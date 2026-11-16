---
description: Plan a new exploration, scaffold its page and registry entry, and start an exploration-runner on it
---
Plan and start an exploration for: $ARGUMENTS

1. Read `index.qmd`, `claims.yaml`, `explorations/registry.yaml` and `log.md` to see where
   this fits. State the question, hypothesis, baseline, metrics, and what result would
   change the paper.
2. Pick the next id (`exp-NNN-short-name`) and its section (an id from `sections` in
   `explorations/registry.yaml`; add one if none fits), and run
   `tools/new_exploration.py <id> "<title>" "<question>" --repo <code repo> --branch <branch> --section <section>`.
3. Write the brief (question, hypothesis, baseline, metrics, code location, compute
   budget, cluster rules, definition of done) into the exploration page's Setup section.
4. Start the `exploration-runner` agent with that brief, in the background.
5. Add a dated line to `log.md`. Stage, never commit. Report what was started.
