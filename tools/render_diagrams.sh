#!/usr/bin/env bash
# web/diagrams/*.dot -> *.svg with Graphviz; the site shows the SVGs as plain images.
set -e
cd "$(dirname "$0")/../web/diagrams"
for f in *.dot; do dot -Tsvg "$f" -o "${f%.dot}.svg"; done
