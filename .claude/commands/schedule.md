---
description: Run one scheduler pass (submit queued jobs, refresh states) and summarise status
---
Run `tools/scheduler.py once` from the paper repository root, then read
`.scheduler/inbox.md` (new lines since the last report) and `status.qmd`.
Report: jobs submitted, jobs that reached a working state, finished, failed (with the
log's last lines), requeued, and what is still queued and why. $ARGUMENTS
