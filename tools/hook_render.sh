#!/usr/bin/env bash
# PostToolUse hook (.claude/settings.json): after Claude edits a file in this project,
# re-render what it affects in the background; log in .render.log.
root=$(cd "$(dirname "$0")/.." && pwd)
f=$(jq -r '.tool_input.file_path // .tool_input.notebook_path // empty')
case "$f" in "$root"/*) rel=${f#"$root"/} ;; *) exit 0 ;; esac
case "$rel" in
    _site/*|_templates/*|.quarto/*) exit 0 ;;
    *.qmd) args=("$rel") ;;
    _quarto.yml|refs.bib|web/*|*/results.json|*/tables/*.md|*/_overview.md) args=() ;;
    *) exit 0 ;;
esac
nohup setsid "$root/tools/render.sh" "${args[@]}" >> "$root/.render.log" 2>&1 < /dev/null &
exit 0
