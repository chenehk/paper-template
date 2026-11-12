# Paper template

A research project written as a Quarto book, run by Claude Code agents: the main
session orchestrates; sub-agents run experiments, track jobs, cover related work and
review. Conventions are in `CLAUDE.md`.

## Start a project

```bash
cp -r /work/hdd/bbjs/sjin2/papers/paper-template /work/hdd/bbjs/sjin2/papers/<project>
cd /work/hdd/bbjs/sjin2/papers/<project>
rm -rf .git && git init && git -C ../paper-template rev-parse HEAD > .template-version
# edit _quarto.yml (title, author) and tools/clusters.yaml (accounts, limits)
```

Then, in a Claude Code session in that directory: write the problem in `intro.qmd`
and the Introduction summary in `index.qmd`, and use

| Command | What it does |
|---|---|
| `/new-experiment <idea>` | plans an experiment, scaffolds its page and registry entry, starts an experiment-runner |
| `/schedule` | one scheduler pass: submit queued jobs, refresh states, summarise |
| `/fold-results <id>` | folds a finished experiment into the paper, method and related work |
| `/add-related <topic>` | related-work agent covers a topic, with verified BibTeX |
| `/check-paper` | reviewer checks claims, numbers, links and builds |
| `/export-latex` | renders the paper with an uploaded LaTeX template, zipped for Overleaf |

## View

```bash
tools/preview.sh 4747        # on the server (fails if the port is taken)
ssh -L 4747:localhost:4747 <that login node>   # on your machine, then open http://localhost:4747
```

Or serve a clone on your own machine (pulls first, opens the browser):

```bash
git clone <this repo> && cd <it> && tools/serve_local.sh
```

## How jobs are tracked

Each job runs inside `tools/run_job.sh`, which appends started / finished / failed /
terminated events to `experiments/<id>/events.jsonl`, so jobs report for themselves.
`tools/scheduler.py` is stateless: a pass reads the registry, those events and Slurm,
submits what fits within `tools/clusters.yaml` limits, requeues retryable failures, and
writes `status.qmd` and `.scheduler/inbox.md`. It runs only inside a session (`once`,
or `wait` with a timeout). No polling loop outlives a session: Slurm `scrontab` is
disabled on Delta/DeltaAI, and compute nodes cannot ssh to the DeltaAI login node.

## Update a project from the template

`tools/update_from_template.sh` shows the diff of agents, commands, tools and
templates; `--apply` copies them and records the template commit.

## Layout

See the table in `CLAUDE.md`.
