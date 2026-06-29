Compile the manuscript markdown to Word (docx) with bibliography.

Target: $ARGUMENTS (default: both EN and JA)

For EN:
```
cd /Users/koreedatatsuya/research/lincs_glyco_2nd_paper/manuscript && pandoc FULL_MANUSCRIPT_DRAFT_EN.md -o FULL_MANUSCRIPT_DRAFT_EN.docx --from markdown --to docx --citeproc --bibliography=refs/lincs_glyco_2nd_paper.bib --csl=nature.csl
```

For JA:
```
cd /Users/koreedatatsuya/research/lincs_glyco_2nd_paper/manuscript && pandoc FULL_MANUSCRIPT_DRAFT_JA.md -o FULL_MANUSCRIPT_DRAFT_JA.docx --from markdown --to docx --citeproc --bibliography=refs/lincs_glyco_2nd_paper.bib --csl=nature.csl
```

If $ARGUMENTS is "EN", compile EN only. If "JA", compile JA only. Otherwise compile both.
After compilation, open the generated docx file(s).
