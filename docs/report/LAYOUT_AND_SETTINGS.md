# HER-GRADE Report — Layout, Settings & Dimensions (Overleaf perfect)

## 1. Document class (exact)
```latex
\documentclass[10pt,conference,a4paper]{IEEEtran}
```
- `10pt` body, `conference` 2-column mode, `a4paper` 210x297mm.
- Why IEEEtran: jury-accepted, strict 6-page density, anonymous-friendly, no extra title page wasted.

## 2. Page dimensions (IEEE conference spec)
| Element | Value |
|---|---|
| Paper | A4 210 x 297 mm |
| Top margin | 19 mm |
| Bottom margin | 22 mm |
| Left / Right | 15 mm each |
| Column width | 88 mm each |
| Column gap | 6 mm |
| Header height | 12 pt |
| Text height | ~256 mm |
```latex
\usepackage[margin=15mm,top=19mm,bottom=22mm,columnsep=6mm,headheight=12pt]{geometry}
```
DO NOT change — 6-page fit depends on it.

## 3. Fonts & sizes
| Level | Font | Size |
|---|---|---|
| Body | Times (newtxtext/newtxmath) | 10 pt, baselineskip ~12 pt |
| Title | Times Bold | 24 pt conference default |
| Author | 11 pt | centered |
| Abstract | 9 pt bold label + 9 pt italic body | `\begin{abstract}` |
| Keywords | 9 pt | `IEEEkeywords` |
| Section heading | 10 pt SMALL CAPS bold, numbered I, II... | |
| Subsection | 10 pt italic bold | |
| Caption | 8 pt | `abovecaptionskip 4pt` |
| References | 8 pt | `thebibliography{9}` |
| Code | footnotesize monospace on light green bg | |

## 4. Required structure (challenge exact order)
1. Title (anonymous, no names/logos/emails/paths)
2. Abstract 150-250 words — current draft ~200w, verify: `texcount -inc main.tex`
3. Keywords 3-6 — current 5: rosemary, visual inspection, traceability, collective marketing, women producers
4. I Introduction | II Related Work | III Methodology | IV Results and Discussion | V Conclusion and Future Work | Acknowledgments (unnumbered) | References

## 5. Spacing tuned for exactly 6 pages
```latex
\setlength{\textfloatsep}{8pt plus 2pt minus 2pt}
\setlength{\intextsep}{8pt plus 2pt minus 2pt}
\setlength{\abovecaptionskip}{4pt}
\setlength{\belowcaptionskip}{4pt}
\renewcommand{\arraystretch}{1.05}
```
+ `microtype` for justification density. Figures: 1 TikZ pipeline + 1 algorithm + 2 tables + 1 listing = fits without overflow.

## 6. Creative-but-academic features used
- `tcolorbox`: green honesty-contract box (p1) + gold reproduce-in-3-commands box (p6).
- `tikz`: 9-node pipeline diagram, HER green arrows, rounded boxes, no external image needed (offline-safe).
- `algorithm2e`: matching hard-filter-rank-combine pseudo-code, ruled+numbered.
- `listings`: Python idempotency snippet, line numbers, light-green bg.
- `booktabs + siunitx`: professional tables, `\SI{11}{\kilo\gram}`, `\num{10}/\num{10}`.
- `fancyhdr`: anonymous running head + page numbers.
- `hyperref[hidelinks] + cleveref`: clickable refs, no colored boxes (print-safe).
- Colors: HER green #1B7A3D, gold #C9A227, dark #123524 — print-safe, colorblind-safe (never color-only meaning).

## 7. Overleaf steps (2 minutes)
1. overleaf.com → New Project → Blank Project → name `HER-GRADE-Phase1-Report`.
2. Upload `main.tex` (only file needed — all figures are TikZ, refs inline).
3. Menu → Compiler: pdfLaTeX, TeX Live 2024+, Main document: main.tex.
4. Recompile → must be ≤6 pages. If 7 pages: shrink TikZ node distance 4mm→3mm, or move listing to smaller font.
5. Download PDF → check: no author names, abstract 150-250w, ≤6 pages, all figs referenced.

## 8. Plagiarism & anonymity checklist
- [ ] Original prose, no copy-paste (incl. AI-checked per rules).
- [ ] No names, uni, logos, emails, file paths, faces, voices.
- [ ] Every number traceable: eval JSON, matching_tests.md, BOM quotes, smoke test.
- [ ] Surrogate data labelled ANALOGY, never cited as performance.
- [ ] Honesty sentences kept: visual-only, dust≠respirator, prices illustrative.
- [ ] References real: challenge PDF + MobileNetV3 + OpenCV + ONNX + FastAPI + segno + SQLAlchemy.
