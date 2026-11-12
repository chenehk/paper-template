---
name: references
description: Adds and verifies BibTeX entries in refs.bib under the project's citation rules - published venue (conference/journal) whenever one exists, arXiv only for unpublished work, url pointing to the PDF or arXiv page. Use when a page needs a citation, when related-work names new papers, or before an export.
---
You maintain `refs.bib` for a paper written as a Quarto book. Read `CLAUDE.md` first,
especially "Citations", and follow it exactly.

For each paper you are asked to add or check:
1. Find it and open its pages: the venue's proceedings page and PDF if it was
   published, otherwise its arXiv abstract page. Do not write an entry from memory or
   from a search snippet.
2. Decide published vs unpublished. Search for a published version even when you were
   given an arXiv id (title search on the venue sites, Semantic Scholar, DBLP). If one
   exists, cite it, not the preprint.
3. Write the entry: `@inproceedings` / `@article` with the full venue name, year, pages
   when shown, `url` = the PDF on the venue's site, no `doi`; or `@misc` for arXiv with
   `eprint`, `archivePrefix`, `primaryClass`, `url` = the abstract page. Authors as
   printed on the paper. Key `firstauthorYEARword`.
4. Never change an existing key that pages already cite; fix its fields instead.
5. When checking, report per entry: OK, or what is wrong (preprint with a published
   version, missing venue, dead or non-PDF url, wrong year), with the evidence URL.
6. Replace plain-text mentions you were asked to convert with `[@key]`, run
   `tools/refresh.sh`, stage (never commit), and report the keys added or changed.
