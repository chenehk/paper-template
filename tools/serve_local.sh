#!/usr/bin/env bash
# Serve a clone of this site on a laptop and open it in the browser.
# Usage: tools/serve_local.sh [port]    (needs Quarto: brew install --cask quarto)
set -e
cd "$(dirname "$0")/.."
port=${1:-4747}
command -v quarto >/dev/null || { echo "quarto not found; on macOS: brew install --cask quarto" >&2; exit 1; }
git pull --ff-only --quiet || echo "warning: could not fast-forward; serving the local copy" >&2
quarto render --to html --quiet
exec quarto preview --port "$port"
