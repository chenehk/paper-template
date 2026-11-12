#!/usr/bin/env bash
# Bring template changes (agents, commands, tools, templates) into this project.
# Shows a diff first; only applies with --apply. Never touches project content.
set -e
tmpl=${TEMPLATE:-/work/hdd/bbjs/sjin2/papers/paper-template}
cd "$(dirname "$0")/.."
paths=".claude/agents .claude/commands tools _templates"
for p in $paths; do diff -ru "$p" "$tmpl/$p" || true; done
if [ "${1:-}" = "--apply" ]; then
    for p in $paths; do mkdir -p "$p"; cp -r "$tmpl/$p/." "$p/"; done
    git -C "$tmpl" rev-parse HEAD > .template-version 2>/dev/null || true
    echo "applied; review with git diff, then stage"
fi
