#!/usr/bin/env python3
"""Scaffold an experiment: folder, page from the template, results.json, registry entry.

  new_experiment.py exp-004-span-sil "Span <sil>" "Does a span <sil> fix pause-followed offsets?" \
      --repo /path/to/code --branch my-branch
"""
import argparse, os, subprocess, sys
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ap = argparse.ArgumentParser()
ap.add_argument("id"); ap.add_argument("title"); ap.add_argument("question")
ap.add_argument("--repo", required=True); ap.add_argument("--branch", required=True)
a = ap.parse_args()
if not a.id.startswith("exp-"):
    sys.exit("id must start with exp-")
d = os.path.join(ROOT, "experiments", a.id)
if os.path.exists(d):
    sys.exit(f"{d} exists")
try:
    commit = subprocess.run(["git", "-C", a.repo, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
except Exception:
    commit = None
os.makedirs(os.path.join(d, "tables")); os.makedirs(os.path.join(d, "figs"))
sub = {"{{ID}}": a.id, "{{TITLE}}": a.title, "{{QUESTION}}": a.question, "{{CODE_REPO}}": a.repo,
       "{{BRANCH}}": a.branch, "{{COMMIT}}": commit or "unknown"}
for src, dst in (("experiment.qmd", "index.qmd"), ("results.json", "results.json")):
    text = open(os.path.join(ROOT, "templates", src)).read()
    for k, v in sub.items():
        text = text.replace(k, v)
    open(os.path.join(d, dst), "w").write(text)
reg_path = os.path.join(ROOT, "experiments", "registry.yaml")
reg = yaml.safe_load(open(reg_path)) or {}
reg.setdefault("experiments", []).append(dict(id=a.id, title=a.title, question=a.question, status="planned",
                                              code=dict(repo=a.repo, branch=a.branch, commit=commit), claims=[], jobs=[]))
with open(reg_path, "w") as f:
    f.write("# Maintained by the orchestrator (what to run) and tools/scheduler.py (job state).\n")
    yaml.safe_dump(reg, f, sort_keys=False, allow_unicode=True, width=100)
subprocess.run([sys.executable, os.path.join(ROOT, "tools", "make_tables.py"), d], check=True)
subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sync_chapters.py")], check=True)
print(f"created {d}; add jobs to its registry entry, then run tools/scheduler.py once")
