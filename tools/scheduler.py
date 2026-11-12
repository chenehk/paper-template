#!/usr/bin/env python3
"""Submit and track experiment jobs listed in experiments/registry.yaml.

Stateless: each pass reads the registry, the jobs' own events files and Slurm,
then submits what fits and writes status.qmd and .scheduler/inbox.md.

  scheduler.py once [--dry-run]       one pass
  scheduler.py wait --until working|done [--timeout SEC] [--every SEC]
                                      bounded in-session watch: passes until every
                                      active job reaches the condition, or timeout

Never run `wait` without a timeout; it is meant to live inside one session.
"""
import argparse
import datetime as dt
import fcntl
import json
import os
import re
import shlex
import subprocess
import sys
import time

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REG = os.path.join(ROOT, "experiments", "registry.yaml")
STATE = os.path.join(ROOT, ".scheduler")
ACTIVE = ("submitted", "running", "working")
BANNER = re.compile(r"NCSA|Kerberos|DUO|go\.ncsa|Permanently added|^\s*$")
RETRYABLE = {"TIMEOUT": "timeout", "NODE_FAIL": "node failure", "OUT_OF_MEMORY": "out of memory",
             "PREEMPTED": "preempted"}
OOM_LOG = re.compile(r"CUDA out of memory|OutOfMemoryError|oom-kill", re.I)


def now():
    return dt.datetime.now().isoformat(timespec="seconds")


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f) or {}


def save_registry(reg):
    head = "# Maintained by the orchestrator (what to run) and tools/scheduler.py (job state).\n"
    tmp = REG + ".tmp"
    with open(tmp, "w") as f:
        f.write(head)
        yaml.safe_dump(reg, f, sort_keys=False, allow_unicode=True, width=100)
    os.replace(tmp, REG)


def run(cluster, cmd):
    """Run a shell command on the cluster's submit host (or locally); return stdout lines."""
    host = cluster.get("submit_host")
    argv = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", host, cmd] if host else ["bash", "-lc", cmd]
    p = subprocess.run(argv, capture_output=True, text=True, timeout=120)
    out = [l for l in p.stdout.splitlines() if not BANNER.search(l)]
    if p.returncode != 0:
        err = " ".join(l for l in p.stderr.splitlines() if not BANNER.search(l))
        raise RuntimeError(f"{cmd!r} failed: {err}")
    return out


def inbox(msg):
    with open(os.path.join(STATE, "inbox.md"), "a") as f:
        f.write(f"- {now()} {msg}\n")
    print(msg)


def events(exp_id):
    path = os.path.join(ROOT, "experiments", exp_id, "events.jsonl")
    if not os.path.exists(path):
        return []
    out = []
    for line in open(path):
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out


def emit(exp_id, job, event, **kw):
    path = os.path.join(ROOT, "experiments", exp_id, "events.jsonl")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(dict(t=now(), job=job, event=event, source="scheduler", **kw)) + "\n")


def last_line(path):
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 4096))
            lines = [l for l in f.read().decode(errors="replace").splitlines() if l.strip()]
        return lines[-1][:160] if lines else ""
    except OSError:
        return ""


def log_has(path, pattern):
    try:
        with open(path, errors="replace") as f:
            return re.search(pattern, f.read()) is not None
    except OSError:
        return False


def refresh(reg, clusters, dry):
    """Update job states from Slurm and the jobs' events files."""
    by_cluster = {}
    for e in reg["experiments"]:
        for j in e.get("jobs", []):
            if j.get("state") in ACTIVE and j.get("slurm_id"):
                by_cluster.setdefault(j["cluster"], set()).add(str(j["slurm_id"]))
    sacct = {}
    for cname, ids in by_cluster.items():
        lines = run(clusters[cname], "sacct -n -P -X -o JobID,State,ExitCode -j " + ",".join(sorted(ids)))
        for l in lines:
            jid, st, code = (l.split("|") + ["", ""])[:3]
            sacct[jid] = (st.split()[0] if st else "", code)
    for e in reg["experiments"]:
        evs = events(e["id"])
        for j in e.get("jobs", []):
            if j.get("state") not in ACTIVE:
                continue
            st, _ = sacct.get(str(j.get("slurm_id")), ("", ""))
            mine = [v for v in evs if v.get("job") == j["name"] and str(v.get("slurm_id", "")) in ("", str(j["slurm_id"]))]
            kinds = [v["event"] for v in mine]
            if st in ("RUNNING",) and j["state"] == "submitted":
                j["state"] = "running"
            if j["state"] in ("running", "submitted") and j.get("working_marker") and j.get("log") \
                    and log_has(j["log"], j["working_marker"]):
                j["state"] = "working"
                emit(e["id"], j["name"], "working", slurm_id=j["slurm_id"])
                inbox(f"{e['id']}/{j['name']}: reached a working state (job {j['slurm_id']})")
            if "finished" in kinds:
                j["state"] = "done"
                inbox(f"{e['id']}/{j['name']}: finished")
            elif "failed" in kinds or "terminated" in kinds or st in ("FAILED", "CANCELLED", "TIMEOUT",
                                                                      "NODE_FAIL", "OUT_OF_MEMORY", "PREEMPTED"):
                if st in ("PENDING", "RUNNING") and "terminated" not in kinds and "failed" not in kinds:
                    continue
                reason = RETRYABLE.get(st) or ("out of memory" if j.get("log") and log_has(j["log"], OOM_LOG.pattern) else None)
                if reason and j.get("retries", 0) < j.get("max_retries", 0):
                    j["retries"] = j.get("retries", 0) + 1
                    j["state"] = "queued"
                    inbox(f"{e['id']}/{j['name']}: {reason}; requeued (retry {j['retries']}/{j['max_retries']})")
                else:
                    j["state"] = "failed"
                    why = reason or "error (see log: %s)" % last_line(j.get("log") or "")
                    inbox(f"{e['id']}/{j['name']}: FAILED, {why}")
            elif st == "COMPLETED" and not kinds:
                j["state"] = "done"
        states = [j.get("state") for j in e.get("jobs", [])]
        if states and all(s == "done" for s in states) and e.get("status") != "done":
            e["status"] = "done"
            inbox(f"{e['id']}: all jobs done")
        elif any(s in ACTIVE for s in states) and e.get("status") == "planned":
            e["status"] = "running"


def submit(reg, clusters, dry):
    """Submit queued jobs whose dependencies are done, within partition limits."""
    used = {}
    for e in reg["experiments"]:
        done = {j["name"] for j in e.get("jobs", []) if j.get("state") == "done"}
        ready = [j for j in e.get("jobs", []) if j.get("state", "queued") == "queued"
                 and all(d in done for d in j.get("depends_on", []))]
        groups = {}
        for j in ready:
            groups.setdefault(j.get("group") or j["name"], []).append(j)
        for gname, jobs in groups.items():
            c = clusters[jobs[0]["cluster"]]
            part = jobs[0].get("partition") or c["default_partition"]
            limit = c.get("limits", {}).get(part)
            if limit is not None:
                key = (jobs[0]["cluster"], part)
                if key not in used:
                    user = os.environ.get("USER")
                    used[key] = 0 if dry else len(run(c, f"squeue -h -u {user} -p {part} -o %i"))
                if used[key] >= limit:
                    continue
            script = write_script(e, gname, jobs)
            gpus = sum(int(j.get("gpus", 0)) for j in jobs)
            acct = c.get("account") or (c["account_gpu"] if gpus else c["account_cpu"])
            opts = [f"--account={acct}", f"--partition={part}", f"--cpus-per-task={max(int(j.get('cpus', 1)) for j in jobs) * len(jobs)}",
                    f"--mem={jobs[0].get('mem', '16G')}", f"--time={jobs[0].get('time', '01:00:00')}",
                    f"--job-name={e['id']}-{gname}"[:60], f"--output={os.path.join(STATE, 'logs', e['id'] + '-' + gname + '.out')}"]
            if gpus:
                opts.append(f"--gpus-per-node={gpus}")
            cmd = "sbatch --parsable " + " ".join(shlex.quote(o) for o in opts) + " " + shlex.quote(script)
            if dry:
                print("[dry-run]", cmd)
                continue
            jid = run(c, cmd)[-1].split(";")[0].strip()
            for j in jobs:
                j.update(state="submitted", slurm_id=jid, submitted=now())
                emit(e["id"], j["name"], "submitted", slurm_id=jid, cluster=jobs[0]["cluster"], partition=part)
            if limit is not None:
                used[key] += 1
            inbox(f"{e['id']}/{gname}: submitted as job {jid} ({jobs[0]['cluster']}/{part}, {len(jobs)} job(s))")


def write_script(e, gname, jobs):
    os.makedirs(os.path.join(STATE, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(STATE, "logs"), exist_ok=True)
    ev = os.path.join(ROOT, "experiments", e["id"], "events.jsonl")
    wrapper = os.path.join(ROOT, "tools", "run_job.sh")
    lines = ["#!/usr/bin/env bash", f"# {e['id']} / {gname}: generated by tools/scheduler.py", "pids=()"]
    gpu = 0
    for j in jobs:
        n = int(j.get("gpus", 0))
        dev = ",".join(str(gpu + k) for k in range(n))
        gpu += n
        env = f"CUDA_VISIBLE_DEVICES={dev} " if n else ""
        inner = f"cd {shlex.quote(j['workdir'])} && {j['command']}"
        lines.append(f"{env}{shlex.quote(wrapper)} {shlex.quote(ev)} {shlex.quote(j['name'])} -- {shlex.quote(inner)} &")
        lines.append("pids+=($!)")
    lines += ["rc=0", 'for p in "${pids[@]}"; do wait "$p" || rc=1; done', "exit $rc"]
    path = os.path.join(STATE, "scripts", f"{e['id']}-{gname}.sh")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    os.chmod(path, 0o755)
    return path


def write_status(reg):
    rows = ["| Experiment | Job | Cluster / partition | State | Slurm id | Retries | Last log line |",
            "|---|---|---|---|---|---|---|"]
    for e in reg["experiments"]:
        for j in e.get("jobs", []):
            ll = last_line(j.get("log") or "").replace("|", "\\|") if j.get("state") in ACTIVE else ""
            rows.append(f"| [{e['id']}](experiments/{e['id']}/index.qmd) | {j['name']} | {j['cluster']} / {j.get('partition', '')} "
                        f"| {j.get('state', 'queued')} | {j.get('slurm_id') or ''} | {j.get('retries', 0)} | `{ll}` |")
    with open(os.path.join(ROOT, "status.qmd"), "w") as f:
        f.write(f"# Job status {{.unnumbered}}\n\nUpdated {now()} by `tools/scheduler.py`.\n\n" + "\n".join(rows) + "\n")


def one_pass(dry):
    os.makedirs(STATE, exist_ok=True)
    with open(os.path.join(STATE, "lock"), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        reg = load_yaml(REG)
        reg.setdefault("experiments", [])
        clusters = load_yaml(os.path.join(ROOT, "tools", "clusters.yaml"))
        refresh(reg, clusters, dry)
        submit(reg, clusters, dry)
        if not dry:
            save_registry(reg)
        write_status(reg)
        return reg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("once")
    o.add_argument("--dry-run", action="store_true")
    w = sub.add_parser("wait")
    w.add_argument("--until", choices=["working", "done"], required=True)
    w.add_argument("--timeout", type=int, default=3000)
    w.add_argument("--every", type=int, default=60)
    a = ap.parse_args()
    if a.cmd == "once":
        one_pass(a.dry_run)
        return
    end = time.time() + min(a.timeout, 6 * 3600)
    target = ("working", "done") if a.until == "working" else ("done",)
    while True:
        reg = one_pass(False)
        jobs = [j for e in reg["experiments"] for j in e.get("jobs", [])]
        pending = [j for j in jobs if j.get("state") in ACTIVE + ("queued",) and j.get("state") not in target]
        if not pending:
            print("WAIT_DONE")
            return
        if time.time() > end:
            print(f"WAIT_TIMEOUT ({len(pending)} job(s) not yet {a.until})")
            return
        time.sleep(a.every)


if __name__ == "__main__":
    sys.exit(main())
