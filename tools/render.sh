#!/usr/bin/env bash
# Re-render into _site/, which tools/preview.sh serves.
#   tools/render.sh page.qmd [...]   render just those pages
#   tools/render.sh                  full refresh (tools/refresh.sh)
# Renders take a lock, so overlapping requests run one after another.
set -e
cd "$(dirname "$0")/.."
[ $# -eq 0 ] && exec tools/refresh.sh
. tools/activate_quarto.sh
exec 9>.render.lock
flock 9
for f in "$@"; do
    [ -f "$f" ] || continue
    start=$(date +%s)
    quarto render "$f" --to html --quiet 2>&1 | grep -iE "warn|error" || true
    echo "rendered $f in $(( $(date +%s) - start ))s at $(date +%T)"
done
