---
description: Fold a finished experiment's results back into the paper, method and related work
---
Fold experiment $ARGUMENTS into the paper.

1. Read `experiments/<id>/index.qmd`, its `results.json` and the runner's report.
2. Update `index.qmd`: the Experiments summary (one or two sentences with the key
   numbers, the main table via include if it is a headline result, and a link
   `@sec-<id>`), and the Abstract or Conclusion if the headline changed.
3. Add or update entries in `claims.yaml` for every new claim.
4. If the experiment changes the method (a new component, a changed default), update
   the relevant `method/*.qmd` page and link it to the experiment. If it touches prior
   work, ask the related-work agent for the comparison.
5. `git diff` every file before editing it; keep the author's wording.
6. Run `tools/refresh.sh`, add a line to `log.md`, stage (never commit), and list
   what changed.
