# HER-GRADE Technical Report — Layout, Settings, Dimensions (Overleaf perfect, 5-6 pages)

## 1. Class (exact, do not change)
```latex
\documentclass[10pt,conference,a4paper]{IEEEtran}
```
- 10pt body, conference 2-column, A4 210x297mm.
- Why IEEEtran conference: densest jury-accepted layout, anonymous title block, no wasted title page, strict float control for exactly 5-6 pages.

## 2. Page geometry — IEEE conference spec
| Element | Value | Notes |
|---|---|---|
| Paper | A4 210 x 297 mm | `a4paper` |
| Top | 19 mm | |
| Bottom | 22 mm | leaves room for page number |
| Left / Right | 15 mm each | |
| Column width | 88 mm each | automatic from class + geometry |
| Column gap | 6 mm | `columnsep=6mm` |
| Header height | 12 pt | `headheight=12pt` avoids fancyhdr warning |
| Text height | ~256 mm | |
```latex
\usepackage[margin=15mm,top=19mm,bottom=22mm,columnsep=6mm,headheight=12pt]{geometry}
```

## 3. Fonts and sizes (Times, print-safe)
| Level | Setting | Size |
|---|---|---|
| Body | newtxtext/newtxmath (Times clone) | 10pt / 12pt leading |
| Title | IEEEtran conference default bold | 24pt, centered, two lines max |
| Author block | IEEEauthorblockN/A | 11pt centered |
| Abstract | `abstract` env, bold label | 9pt, italic body, 225 words (150-250 required) |
| Keywords | `IEEEkeywords` | 9pt, 6 keywords (3-6 required) |
| Section | small caps bold, Roman numerals I..V | 10pt |
| Subsection | italic bold | 10pt |
| Captions | `abovecaptionskip 4pt` | 8pt |
| References | `thebibliography{12}` | 8pt, 11 entries |
| Code | listings footnotesize mono, light-green bg | 8pt |
| running head | fancyhdr italic | footnotesize |

## 4. Required structure (challenge-exact order, professional wording)
1. Title — no Phase label, no names/logos/emails/paths.
2. Abstract 225 words — problem (2-15kg vs 20kg+, drudgery, opacity, dust) -> solution (bench+vision+QR+matching+pricing) -> methods (optics, gating, ONNX, threshold, held-out) -> results (acc/FAR/review, counts, throughput, dust, 10/10 QR, 7/7 matching incl. 11+9=20, pricing, usability) -> limits.
3. Keywords (6): rosemary, visual inspection, traceability, collective marketing, women producers, rural supply chain.
4. I Introduction (field reality Sejnane/Zaghouan + promise + 5 contributions + green contract box).
5. II Related Work (4 baselines + integration-as-innovation + Table 1).
6. III Methodology — 3.1 System overview + Fig.1 TikZ chain; 3.2 Bench mechanics/optics/safety + Table 2 BOM 675-1350 DT; 3.3 Vision gate/infer/decide + Eq.1 + dataset discipline; 3.4 Marketplace match/order/price/trace + Alg.1.
7. IV Results and Discussion — 4.1 Vision held-out + Table 3 + threshold trade; 4.2 Sorting/throughput/dust/QR + Listing 1; 4.3 Matching/pricing/usability (7 tests + smoke + French UI); 4.4 Business/feasibility/impact (payback, ops, risks); 4.5 Failures/limits/honesty.
8. V Conclusion and Future Work — staged calendar roadmap (pilot Oct-Nov 2026, early Dec-Mar, scale-up Apr-Sep 2027) + gold reproduce box.
9. Acknowledgments (unnumbered, anonymised). 10. References (11, all cited).

## 5. Spacing tuned for 5-6 pages
```latex
\setlength{\textfloatsep}{8pt plus 2pt minus 2pt}
\setlength{\intextsep}{8pt plus 2pt minus 2pt}
\setlength{\abovecaptionskip}{4pt}
\setlength{\belowcaptionskip}{4pt}
\renewcommand{\arraystretch}{1.05}
```
+ microtype justification. Float budget: 1 TikZ fig + 1 algorithm + 3 tables + 1 listing + 2 tcolorboxes = ~5.5 pages at ~3900 words. If Overleaf shows 7 pages: set TikZ node distance 3.5->3mm, or `\footnotesize` listing.

## 6. Creative-but-academic features
- tcolorbox green Design-contract (p1) + gold Reproduce-in-3-commands (p6).
- TikZ 9-node pipeline (no external images, offline-safe, vector-sharp).
- algorithm2e ruled matching pseudo-code with inputs/outputs.
- listings Python idempotent ingest + stop-alert path.
- booktabs + siunitx: `\SI{11}{\kilo\gram}`, `\num{10}/\num{10}`, `\ang{20}`.
- fancyhdr anonymous running head + page numbers.
- hyperref[hidelinks] + cleveref (print-safe links).
- Palette: green #1B7A3D, gold #C9A227, dark #123524, bg #F2F6F0 — never color-only meaning.

## 7. Overleaf import (2 min)
1. New Blank Project `HER-GRADE-Report` -> Upload `main.tex` only (figures are TikZ, refs inline).
2. Menu: Compiler pdfLaTeX, TeX Live 2024+, Main document main.tex -> Recompile.
3. Check: pages 5-6, abstract 150-250w (`texcount -inc main.tex`), keywords 3-6, all Fig/Table/Alg/Listing referenced, no author identity, 11/11 cites resolve.
4. Fill Table 3 `---` from `docs/evidence/eval_results.json` after bench run.

## 8. Winning-points map (how this draft takes all 40)
- Problem & social relevance (7): Sejnane/Zaghouan field reality, 2-15kg vs 20kg+, drudgery/dust/intermediaries, women + essential-oil/agro-food chains, ILO/FAO cites.
- Innovation & technical solution (10): integration-as-innovation (bench+gated vision+2 honest outputs+QR+hard-filter matching+pricing), gate equation, Alg.1, grade-mix guard, idempotent log.
- Feasibility/business/impact (8): full BOM 675-1350 DT, payback model, ops/maintenance, offline autonomy, staged calendar roadmap, risks mitigated.
- Technical report (10): exact required order, 225w abstract, 6 keywords, measured results + failures + limits + 11 real refs, original prose.
- Video readiness (5): Fig.1 = shotlist backbone, Listing 1 + reproduce box = demo script.

## 9. Anonymity + originality checklist
- [ ] No names, affiliations, logos, emails, paths, faces, voices.
- [ ] No Phase-1/Phase-2 labels in title/headers (calendar roadmap instead).
- [ ] Every number traceable to eval JSON / matching_tests.md / BOM quotes / smoke test.
- [ ] Surrogate labelled analogy, never cited as performance.
- [ ] Honesty sentences kept on every claim: visual-only, dust!=respirator, prices illustrative.
