#!/usr/bin/env bash
# Rebuild everything derived: tables from results.json, chapter lists from the
# registry, then a full render. Run after writing results, adding or retiring an
# exploration, or editing _quarto.yml. tools/preview.sh serves the result.
set -e
cd "$(dirname "$0")/.."
exec 9>.render.lock
flock 9
. tools/activate_quarto.sh
/usr/bin/python3 tools/make_tables.py
/usr/bin/python3 tools/sync_chapters.py
command -v dot >/dev/null && tools/render_diagrams.sh
quarto render --to html 2>&1 | grep -iE "warn|error" || true
echo "refreshed $(date -Is)"
