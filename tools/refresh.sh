#!/usr/bin/env bash
# Rebuild everything derived: tables from results.json, chapter lists from the
# registry, then a full render. Run after writing results, adding or retiring an
# experiment, or editing _quarto.yml. A running preview serves the new pages.
set -e
cd "$(dirname "$0")/.."
. tools/activate_quarto.sh
/usr/bin/python3 tools/make_tables.py
/usr/bin/python3 tools/sync_chapters.py
quarto render --to html 2>&1 | grep -iE "warn|error" || true
echo "refreshed $(date -Is)"
