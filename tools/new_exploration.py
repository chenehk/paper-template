#!/usr/bin/env python3
"""Scaffold an exploration: folder, page from the template, results.json, registry entry.

  new_exploration.py exp-004-span-sil "Span <sil>" "Does a span <sil> fix pause-followed offsets?" \
      --repo /path/to/code --branch my-branch [--section <id from the registry's sections>]
"""
import argparse, os, subprocess, sys
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ap = argparse.ArgumentParser()
ap.add_argument("id"); ap.add_argument("title"); ap.add_argument("question")
ap.add_argument("--repo", required=True); ap.add_argument("--branch", required=True)
ap.add_argument("--section", help="id of a section in the registry's `sections` list")
a = ap.parse_args()
if not a.id.startswith("exp-"):
    sys.exit("id must start with exp-")
d = os.path.join(ROOT, "explorations", a.id)
if os.path.exists(d):
    sys.exit(f"{d} exists")
reg_path = os.path.join(ROOT, "explorations", "registry.yaml")
reg = yaml.safe_load(open(reg_path)) or {}
known = [s["id"] for s in reg.get("sections") or []]
if a.section and a.section not in known:
    sys.exit(f"unknown section {a.section!r}; add it to `sections` in {reg_path} first (known: {known})")
try:
    commit = subprocess.run(["git", "-C", a.repo, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
except Exception:
    commit = None
os.makedirs(os.path.join(d, "tables")); os.makedirs(os.path.join(d, "figs"))
sub = {"{{ID}}": a.id, "{{TITLE}}": a.title, "{{QUESTION}}": a.question, "{{CODE_REPO}}": a.repo,
       "{{BRANCH}}": a.branch, "{{COMMIT}}": commit or "unknown"}
for src, dst in (("exploration.qmd", "index.qmd"), ("results.json", "results.json")):
    text = open(os.path.join(ROOT, "_templates", src)).read()
    for k, v in sub.items():
        text = text.replace(k, v)
    open(os.path.join(d, dst), "w").write(text)
entry = dict(id=a.id, title=a.title, question=a.question, status="planned")
if a.section:
    entry["section"] = a.section
entry.update(code=dict(repo=a.repo, branch=a.branch, commit=commit), claims=[], jobs=[])
reg.setdefault("explorations", []).append(entry)
with open(reg_path, "w") as f:
    f.write("# Maintained by the orchestrator (what to run) and tools/scheduler.py (job state).\n")
    yaml.safe_dump(reg, f, sort_keys=False, allow_unicode=True, width=100)
subprocess.run([sys.executable, os.path.join(ROOT, "tools", "make_tables.py"), d], check=True)
subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sync_chapters.py")], check=True)
print(f"created {d}; add jobs to its registry entry, then run tools/scheduler.py once")
