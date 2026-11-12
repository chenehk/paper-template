---
description: Plan a new experiment, scaffold its page and registry entry, and start an experiment-runner on it
---
Plan and start an experiment for: $ARGUMENTS

1. Read `index.qmd`, `claims.yaml`, `experiments/registry.yaml` and `log.md` to see where
   this fits. State the question, hypothesis, baseline, metrics, and what result would
   change the paper.
2. Pick the next id (`exp-NNN-short-name`) and run
   `tools/new_experiment.py <id> "<title>" "<question>" --repo <code repo> --branch <branch>`.
3. Write the brief (question, hypothesis, baseline, metrics, code location, compute
   budget, cluster rules, definition of done) into the experiment page's Setup section.
4. Start the `experiment-runner` agent with that brief, in the background.
5. Add a dated line to `log.md`. Stage, never commit. Report what was started.
