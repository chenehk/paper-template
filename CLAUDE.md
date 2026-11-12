# Research paper project: conventions

This repository is a paper written as a Quarto book. The code lives in other
repositories; experiment pages link to a branch and commit there. Every agent
working here reads this file first.

## Layout

| Path | What | Owner |
|---|---|---|
| `index.qmd` | the paper: Abstract, 1 Introduction, 2 Related work, 3 Method, 4 Experiments, 5 Conclusion. Each section is a short summary that links to its detail pages. | orchestrator |
| `intro.qmd` | problem statement and motivation in full | orchestrator |
| `related/*.qmd` | related work, one page per topic | related-work agent |
| `method/*.qmd` | method, one page per component | orchestrator |
| `experiments/<id>/index.qmd` | one page per experiment | that experiment's runner |
| `experiments/<id>/results.json` | every number the experiment reports | that experiment's runner |
| `experiments/<id>/tables/*.md`, `figs/` | generated from `results.json`; never hand-edited | `tools/make_tables.py` |
| `experiments/registry.yaml` | experiments, their jobs, code branch and commit | orchestrator + scheduler |
| `experiments/<id>/events.jsonl` | job events written by `tools/run_job.sh` | jobs themselves |
| `refs.bib` | citations; only papers an agent actually opened | related-work agent |
| `claims.yaml` | each claim in `index.qmd` -> experiment id and result key | orchestrator |
| `log.md` | dated decisions | orchestrator |
| `status.qmd`, `.scheduler/` | generated status board and scheduler state (git-ignored) | scheduler |

## Rules for everyone

- **Never `git commit` or `git push`.** Stage with `git add` and report what is staged.
- **Never retype a number.** Numbers live in `results.json`; pages show them through
  generated tables (`{{< include tables/x.md >}}`) or by quoting the file. The reviewer
  checks every number in prose against `results.json`.
- **Stable IDs, cross-referenced:** sections `{#sec-...}`, tables `{#tbl-...}`, figures
  `{#fig-...}`, citations `[@key]`. Every summary in `index.qmd` ends with links to the
  pages it summarizes, and every detail page links back to the claim it supports.
- **People edit these files too.** Before changing a page, `git diff` it and read it
  again; keep their wording, change only what the task needs. Generated files are the
  only ones that may be overwritten whole.
- **Export-safe:** math in LaTeX syntax, citations as BibTeX keys, figures saved as both
  PDF and PNG (`figs/x.pdf`, `figs/x.png`), no HTML-only elements in `index.qmd`.
- **Unverified things are labelled** ("from memory, not checked", "single seed").
- **Clusters:** real work goes through Slurm (see `tools/clusters.yaml`), never on a login
  node. Never leave a polling loop running past the end of a session; a wait inside a
  turn must be bounded and exit by itself. Check that a job reached a working state,
  not only that it was submitted.

## Agents (see `.claude/agents/`)

- **orchestrator** (the main session): plans, writes briefs, starts sub-agents, folds
  results into `index.qmd`, `method/`, `related/`, keeps `claims.yaml` and `log.md`.
- **experiment-runner**: implements and runs one experiment, writes its page.
- **scheduler**: submits and tracks jobs from `registry.yaml`, writes `status.qmd` and
  `.scheduler/inbox.md`.
- **related-work**: finds and reads papers, writes `related/` and `refs.bib`.
- **paper-reviewer**: checks claims, numbers, links and the LaTeX build; reports only.

## Commands (see `.claude/commands/`)

`/new-experiment`, `/schedule`, `/fold-results`, `/add-related`, `/check-paper`,
`/export-latex`.

## Viewing

`tools/preview.sh [port]` serves the site on the server; forward it with
`ssh -L <port>:localhost:<port> <login node>` and open `http://localhost:<port>`.
