# Research paper project: conventions

This repository is a paper written as a Quarto book. The code lives in other
repositories; experiment pages link to a branch and commit there. Every agent
working here reads this file first.

## Layout

| Path | What | Owner |
|---|---|---|
| `index.qmd` | the paper: Abstract, Introduction, Related work, Method, Experiments, Conclusion. Each section is a short summary that links to its detail pages. | orchestrator |
| `intro.qmd` (+ more pages) | problem statement and motivation in full | orchestrator |
| `related/*.qmd` | related work, one page per topic | related-work agent |
| `method/*.qmd` | method, one page per component | orchestrator |
| `experiments/<id>/index.qmd` | one page per experiment | that experiment's runner |
| `web/part-links.html` | makes each sidebar part title open its section of the Paper page | orchestrator |
| `experiments/<id>/results.json` | every number the experiment reports | that experiment's runner |
| `experiments/<id>/tables/*.md`, `figs/` | generated from `results.json`; never hand-edited | `tools/make_tables.py` |
| `experiments/registry.yaml` | experiments, their jobs, code branch and commit | orchestrator + scheduler |
| `experiments/<id>/events.jsonl` | job events written by `tools/run_job.sh` | jobs themselves |
| `refs.bib` | citations; only papers an agent actually opened (rules below) | references agent |
| `references.qmd` | the References page every citation links to; generated from `refs.bib` | (generated) |
| `claims.yaml` | each claim in `index.qmd` -> experiment id and result key | orchestrator |
| `log.md` | dated decisions | orchestrator |
| `status.qmd`, `.scheduler/` | generated status board and scheduler state (git-ignored) | scheduler |

## Site structure

The sidebar has two levels: **Paper** (`index.qmd`), then the parts **Introduction**,
**Related work**, **Method**, **Experiments** and **Obsolete experiments**, each listing
its pages. Clicking a
part title opens the matching section of the Paper page (`#sec-paper-intro`,
`#sec-paper-related`, `#sec-paper-method`, `#sec-paper-experiments`), via
`web/part-links.html`. A new page must be added under its part in `_quarto.yml`
(experiment pages are added by `tools/sync_chapters.py`). When an experiment fails or
is superseded, set its registry status to `obsolete` and add a "Why it failed" section
and a lesson to its page; `sync_chapters.py` then moves it from Experiments to Obsolete
experiments. Its folder (results, raw files) stays.

## Citations

Cite with `[@key]` anywhere; the citation links to its entry on the References page,
and the entry links to the paper. Every entry in `refs.bib` must satisfy:

- **Opened, not remembered:** the agent that adds it opened the paper's page.
- **Published version first:** if the paper appeared at a conference or in a journal,
  the entry is `@inproceedings` (with `booktitle`, e.g. "Proc. Interspeech 2021") or
  `@article` (with `journal`, `volume`, `number`), `year`, `pages` when known, and
  `url` = the PDF on the venue's site (ACL Anthology, ISCA Archive, PMLR, OpenReview,
  IEEE Xplore, ...). No `doi` field: the citation style would show the DOI instead of
  the PDF link.
- **arXiv only if unpublished:** `@misc` with `eprint`, `archivePrefix = {arXiv}`,
  `primaryClass`, and `url` = `https://arxiv.org/abs/<id>`. Re-check for a published
  version before every export.
- **Keys:** `firstauthorYEARword`, lower case (e.g. `graves2006ctc`); never reuse a key
  for a different paper.

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
- **related-work**: finds and reads papers, writes `related/` pages and cites with `[@key]`.
- **references**: adds and verifies `refs.bib` entries under the citation rules.
- **paper-reviewer**: checks claims, numbers, links and the LaTeX build; reports only.

## Commands (see `.claude/commands/`)

`/new-experiment`, `/schedule`, `/fold-results`, `/add-related`, `/check-refs`,
`/check-paper`, `/export-latex`.

## Keeping the site current

`tools/preview.sh` re-renders a page whose `.qmd` changed when it is next opened.
It does not see changes to included tables, `results.json`, the chapter list or
`_quarto.yml`: whoever makes such a change runs `tools/refresh.sh` (tables, chapters,
full render) as the last step of their task. Run only one preview per project; two
previews on one project interfere.

## Viewing

`tools/preview.sh [port]` serves the site on the server; forward it with
`ssh -L <port>:localhost:<port> <login node>` and open `http://localhost:<port>`.
