---
description: Verify every refs.bib entry (published venue first, arXiv only if unpublished, PDF/arXiv links), or add references for named papers
---
Start the `references` agent. $ARGUMENTS
With no arguments: check every entry in `refs.bib` against the citation rules in
`CLAUDE.md` and every `[@key]` in the pages (unknown keys, unused entries). With
paper names or plain-text mentions: add verified entries and convert the mentions to
`[@key]`. Report its findings; do not let it delete entries without asking me.
