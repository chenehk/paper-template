---
description: Export the paper to LaTeX for Overleaf, using a template the author provides
---
Export the paper to LaTeX. $ARGUMENTS

1. Ask for the LaTeX template (.cls/.sty/example .tex) if it is not given; put it in
   `templates/latex/<name>/`.
2. Run the paper-reviewer first; stop if there are unresolved references or numbers
   that do not match their source.
3. Wrap the template as a Quarto LaTeX format (template partials or a format
   extension) and render the paper chapters with `quarto render --to latex`.
4. Collect the .tex, figures (PDF), .bib and class files into `export/<date>/` and zip
   it for upload to Overleaf. Report any construct that did not translate.
