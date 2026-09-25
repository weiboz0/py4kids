# Plan 085 — Book 1b publication: stored lesson outputs, typeset Student Book and Teacher's Edition

**Goal:** Implement design 007 for Book 1b: every executable lesson cell carries its verified expected
output; a builder turns the notebooks and teacher notes into two typeset PDF books (Student Book and
Teacher's Edition) with publishable layout — no notebook framing; turtle programs appear as drawn
figures.

**Spec:** `docs/designs/007-book-publication.md` (D1–D6; user decisions 2026-09-24: keep `.ipynb` as the
source, two editions, Book 1b first). Spike (2026-09-24, throwaway): Quarto 1.6.42 rendered a real U05
lesson + teacher notes to a `scrbook` PDF with executed outputs once `no-exec` cells were marked
`eval: false`.

## Global constraints

- Sources are never modified by the builder; it writes only under `book1b/build/publish/` (gitignored).
  Committed publication inputs (front matter) live in `book1b/front-matter/` — a different name from the
  build folder on purpose.
- No new Python dependencies (Quarto, pandoc, TeX Live with KOMA/tcolorbox/TikZ and the fonts are
  already installed); the builder uses the standard library + `nbformat` + `pyyaml`.
- Stored lesson outputs are **stdout stream text only**. An executable lesson cell that produces any other
  output — a `stderr` stream, `execute_result`, `display_data` or an error — fails `fill-outputs` with
  `FAIL: <unit>: lesson code cell <id> produced non-stdout output (<kind>)`. A cell that prints nothing
  stores the empty output list, which is valid. Execution counts are cleared; cell/notebook metadata are
  left untouched so diffs stay limited to `outputs`. (Measured by [fable]: 287 executable cells, 283
  stdout-only + 4 silent, none with other output; longest 27 lines, widest 44 characters.)
- Exercise, checkpoint and brief notebooks keep the existing hygiene rule (no outputs).
- **Student Book source allowlist:** the student edition reads only `lesson.ipynb`, `exercises.ipynb`,
  `checkpoint.ipynb`, `brief.ipynb`, non-solution unit assets (`assets/*.py` whose name does not start
  with `solutions_`), project data files, `syllabus.md` and `front-matter/`. It never opens
  `teacher-notes.md`, `solutions.ipynb` or `assets/solutions_*.py` (enforced in code by one allowlist
  function and verified by tests, see Phase E).
- Tags: this plan adds two new cell tags to `no-exec` lesson cells — **`error-demo`** (9 cells of
  deliberately broken code) and **`hang-demo`** (1 infinite loop) — enumerated by id in Phase C; they are
  the only source edits besides stored outputs.

## Phase A — Tooling: stored outputs and turtle traces (Codex gpt-6-sol)

- `tools/notebooks.py` + `tools/cli.py` (registered like the existing checks): `fill-outputs --book B
  [--unit U]` executes each `lesson.ipynb` with the CI executor (cwd = unit folder, `no-exec` cells
  skipped, in order) and stores, per executable cell, the complete output list (one `stream`/`stdout`
  output, or `[]`), `execution_count: null`. `lesson-outputs-check --book B` re-executes and compares each
  executable cell's full output list with the stored list; findings:
  `… lesson code cell <id> output is stale` (lists differ), `… produced non-stdout output (<kind>)`, and
  `… no-exec cell has stored output` (a `no-exec` cell must store none). Running `fill-outputs` twice
  must leave the notebook byte-identical (tested). Scratch files written by lessons stay git-ignored.
- `tools/fake_turtle.py`: the tracker also records **segments** `(x1, y1, x2, y2, color, width)` for every
  pen-down move, the current pen colour (`pencolor`/`color` first argument, a name string) and width
  (`pensize`, default 1); `reset()` clears them; a new `segments()` returns a list copy. `Screen()`,
  `bgcolor`, `speed`, `done`, `exitonclick` stay no-ops. Existing `state()` keys and `turtle-check`
  behaviour are unchanged.
- `tools/turtle_figure.py`: `figure_tikz(source: str) -> str` runs one turtle script in a fresh
  namespace with `sys.modules["turtle"]` bound to `fake_turtle` after `reset()` (so every figure has a
  fresh tracker), then emits a `tikzpicture`: each segment as `\draw[line width=<w*0.4>pt,
  color=<Name>]` in svgnames colours (a fixed name map — `royalblue` → `RoyalBlue`, unknown names →
  `black`); the drawing is scaled uniformly so its larger side is at most 0.8 `\textwidth` and 7 cm tall;
  a start marker (small open circle at the origin) is drawn; open paths need no special handling. Any
  exception or an unsupported turtle call fails the build with `FAIL: <unit>: turtle figure for cell <id>:
  <error>`.
- `scripts/ci-local.sh`: add `lesson-outputs-check` to the notebook stage (Book 1b; other books report
  `SKIP (plan NNN)` until their plans fill outputs).
- Tests: fill→check round trip on a fixture notebook; idempotence (fill twice → identical bytes); stale
  output detected; silent cell accepted with `[]`; `no-exec` skipped and must stay output-free; stderr and
  rich output rejected; segments for a square (4 segments, closed, colour and width recorded), a pen-up
  travel (no segment), `reset()` clearing segments; `figure_tikz` on a square (4 `\draw` lines) and on a
  script calling an unsupported method (fails); `turtle-check` results unchanged on Book 1b.

## Phase B — Tooling: the publisher (Codex gpt-6-sol)

`tools/publish.py` + `py4kids-tools publish --book book1b --edition student|teacher` +
`scripts/build-book.sh --book book1b` (both editions). It writes a Quarto book project to
`book1b/build/publish/<edition>/` and renders `Book1b-Student.pdf` / `Book1b-Teacher.pdf`. Quarto never
executes code (`execute: enabled: false`); the `.qmd` reader disables `tex_math_dollars` (prose uses `$`).

**Chapter order:** front matter → the syllabus's shipped-entries table order (13 units; checkpoints after
Units 03, 05, 08, 11, 13; the Algorithm Challenge last), one chapter per entry; chapter short titles for
running heads come from the unit's H1 without the leading "Unit NN —" and are capped at 32 characters.

**Markdown handling (all entries):** each markdown cell is split into paragraphs; a paragraph that matches `^(\*\*Notice:\*\*|Notice:)` (bold or plain — U12 uses
the plain form 15 times) or a heading of level 3+ containing the word `Notice` (e.g. `### Notice: …`,
`### Contrast Notice …`) becomes a `::: {.notice}` panel holding that
paragraph and any directly following paragraphs of the same cell until the next heading. Other bold
lead-ins (`**One twist:**`, `**Realistic:**`, `**Check yourself:**`, `**Try real input:**`, …) pass
through unchanged as prose. The notebook H1 becomes the chapter title; the paragraphs that follow the H1
**in the same cell** (the hook) become the `::: {.opener}`; the next cell continues as normal content.

**Lessons:** code cells → fenced `python` block, then the stored output (if non-empty) in
`::: {.output}`. `no-exec` cells, routed by a fixed precedence: tagged `error-demo` → `::: {.errordemo}` "Read
the error" (code only; the explanation stays in the following markdown); tagged `hang-demo` →
`::: {.hangdemo}` "Watch out: this never stops" (code only); code that imports `turtle` → the code as a
"Program" listing followed by the TikZ figure; code that calls `input(` → `::: {.tryit}` "Try it
yourself" (code, no output); anything else (e.g. `u07l034a`, an excerpt of a real program) →
`::: {.program}` "Program excerpt". A lesson paragraph naming `assets/<name>.py` for a file that exists and is
not a `solutions_` asset gets that asset listed as code (once per chapter, in a `::: {.program}` block
with its path as caption) and, if it imports `turtle`, its figure.

**Units — exercises:** cells are grouped per exercise: the `## Exercise N` cell starts a group; the next
`### Title` cell gives the title (rendered "Exercise N — Title", Challenges "Challenge — Title" with a
Challenge badge when any cell of the group is tagged `stretch`) **and the rest of that cell — the
statement — follows the title unchanged**; the remaining markdown and code cells of the group follow in
order. The `**Real version:**` / `**No real version:**` line becomes a
`::: {.realprog}` note, reworded in the Student Book to "Real program: … — your teacher's edition has the
full program." Starter code cells always print as a "Starter" code block (instruction comments stay
visible); in the Student Book each exercise ends with a ruled answer area (four lines; eight for
Challenges — reduced from six/twelve during the Phase D page review to keep the Student Book near 460
pages). Statements naming `assets/exN_*.py` list that starter asset as code.

**Checkpoints:** the same grouping keyed on `## Question N` + `### Title`; no Challenge badges.

**Algorithm Challenge (`brief.ipynb`):** `## Milestone N` → a section; `### Problem N` / `### Problem N —
Challenge` → a problem group (Challenge badge from the `stretch` tag on the markdown cell); every data file
a problem names (e.g. `p7_words.txt`, `p11_in.txt`) that exists in the project folder is printed after
the problem in a `::: {.datafile}` block with its file name.

**Teacher's Edition additions (teacher edition only — the only code path that opens teacher sources):**
- after each chapter opener, the entry's `teacher-notes.md` inside a breakable `::: {.teacher}` panel:
  the file's H1 is dropped and remaining headings shift down two levels; development jargon is removed by
  a fixed substitution list (`(design 006 D9 genres)`, `design 006 D3`, `(plan 0NN)` references, "for CI"
  asides) and `60-MINUTE CUT` becomes "60-minute cut";
- after each exercise set / checkpoint / problem set, an **Answer key** section: for each item in order,
  its label in the entry's own terms — "Exercise N — Title" (units), "Question N — Title" (checkpoints),
  "Problem N" (the brief) — matched to the solutions notebook's `## Exercise N` / `## Question N` /
  `## Problem N` headings, then the solution code cells with lines consisting only of `assert …`
  removed and a note "(checked by the course's test suite)" when any were removed; then the real program
  and its sample input/output from the markdown fence; U06–U08 turtle exercises list the
  `assets/solutions_exN*.py` program and its figure; solution notebooks' "Note for teachers … CI" preface
  cells are skipped. The Algorithm Challenge's teacher notes and answer key follow the same rules.

**Theme** (`tools/publish_theme/`: `_quarto.yml` template, `theme.tex`, `panels.lua` filter mapping the
div classes to tcolorbox environments): KOMA `scrbook`, 7 × 10 in, Atkinson Hyperlegible body with a
**fallback font for arrows and other missing glyphs** (DejaVu Sans for U+2190–21FF and any character
Atkinson lacks, via `\newfontfamily` + a Unicode-range map), Fira Mono code, panels for Output (grey,
labelled "Output"), Notice, Try it yourself, Read the error, Program, Challenge, Real program, Data file
and Teacher (all breakable); unit openers on recto pages; running heads (chapter short title / section);
long code lines wrap with a marker.

**Front matter** (`book1b/front-matter/`, Markdown, authored inline in Phase D): title page, "How to use
this book", "For teachers" (Teacher's Edition only).

**Tests:** transform unit tests on fixture cells — paragraph-level Notice inside a mixed cell, in all
three forms (bold, plain `Notice:` from a U12 fixture, `### … Notice …` heading); opener;
stored output preserved and empty output omitted; `error-demo` / turtle / input `no-exec` routing; asset
listing; exercise grouping with a stretch group and the Real line (both editions' wording); checkpoint
and brief grouping incl. a data file; teacher panel heading shift and jargon removal; answer-key
assert stripping. **Boundary tests:** the student build's allowlist function rejects `teacher-notes.md`,
`solutions.ipynb` and `assets/solutions_*.py`; a sentinel test plants unique marker strings in a fixture
entry's teacher notes, solutions notebook and solution asset and asserts they appear in the teacher
project and **not** in any file of the student project nor in the student PDF's extracted text.

## Phase C — Populate stored lesson outputs (run the tool)

Tag these `no-exec` lesson cells (the complete list — every lesson `no-exec` cell that neither reads
input nor imports `turtle`, except the program excerpt `u07l034a`):
`error-demo` — U01 `9442d5582e1f` (unclosed quote), `25129fdd9963` (misspelled name),
`dcec5192b293` (missing `+`); U02 `u02l029` (`"Age: " + 12`), `u02l079` (`int("abc")`); U03 `u03l010`
(`if score = 90:`); U04 `u04l022` (`total` before assignment); U07 `u07l009` (`f(3) + 1`); U13 `u13l009`
(lost `self`). `hang-demo` — U04 `u04l012` (the counter never changes). The Phase E audit re-derives this
list from the notebooks and fails on any difference. Run `fill-outputs --book book1b`; review the diff (outputs + the tags only;
287 executable lesson cells across 13 units); `lesson-outputs-check` PASS; `hygiene-check` unchanged.

## Phase D — Front matter and typography polish (inline)

Write the front matter (title page text, how-to-use, teacher preface). Render both editions and review
sampled pages as images (unit opener, a lesson spread, an exercise page with a Challenge, a turtle figure
page, a teacher panel, an answer-key page, a checkpoint page); iterate the theme until: no overfull lines
or code overflowing the text block, no orphaned panel headers, figures fit the page, running heads
correct.

## Phase E — VERIFICATION

1. Unit tests (Phases A–B) pass, including the boundary sentinel tests.
2. `lesson-outputs-check` PASS for Book 1b (and `fill-outputs` idempotent); `hygiene-check`,
   `turtle-check` and `structure-check` still pass.
3. **Completeness audit** (a script over the generated projects and the PDFs' extracted text): for each
   edition, the ordered list of chapter identifiers equals the syllabus order (13 units, 5 checkpoints,
   the Algorithm Challenge); per unit the count and order of "Exercise N" titles equals `exercises.ipynb`,
   per checkpoint the Question count, per brief the Problem count; for every chapter, the builder writes
   a typed block inventory (source cell id → rendered kind: code+output, errordemo, hangdemo, tryit,
   program, figure, starter, asset listing) and the audit checks that every source code cell id appears
   exactly once, in source order, with the kind its routing rule requires; the Teacher's Edition has one Answer key
   per exercise set / checkpoint / problem set covering every exercise number; the Student Book has none.
4. **Render log audit:** no `Missing character` lines; overfull hbox warnings ≤ 5 per edition, none wider
   than 10 pt; no `In [` / `Out[` strings in either PDF's text.
5. A Notice audit: the number of Notice panels per chapter equals the number of source paragraphs /
   headings matching the Notice rule (all 13 lessons; U12's plain form included).
6. Rendered-page review (sampled pages as images: a U12 page with a plain-form Notice, unit opener, lesson spread, turtle figure, error demo,
   exercise with Challenge, teacher panel, answer key, checkpoint, Algorithm Challenge data file) recorded
   in the plan.
7. `scripts/ci-local.sh` ALL GREEN (now including `lesson-outputs-check` and both book renders); the full
   CI duration before and after is recorded in the post-execution report.
8. Post-execution report.

## Out of scope

Book 1 and Book 2 editions (later plans); HTML/e-book output; Markdown migration or jupytext pairing
(design 007 D1 — the notebooks remain the single source of truth); changing any lesson or exercise wording
(only stored outputs and the `error-demo` / `hang-demo` tags are added). Real-book furniture not in v1: index, glossary,
figure/listing numbering and cross-references, cover art, colophon/copyright page, print trim/bleed and
PDF/X export — the v1 books are classroom-publishable, not press-ready.

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- Grounded in a spike (real U05 lesson + notes rendered by Quarto) and a survey: 287 executable lesson
  cells, all `no-exec` turtle cells hold complete scripts (so figures can be replayed), no matplotlib (so
  figures are TikZ), full TeX Live with the needed packages and fonts.
- Watch items for reviewers: output determinism (seeded randomness, file cells), the Student Book's
  no-solution guarantee, and whether emitting `.qmd` (instead of rendering `.ipynb` directly) is the
  right control point.

### Round 1 — verdicts

- `[glm]` APPROVE WITH NITS — stderr outputs, `reset()` clearing segments, failing figure replay,
  no-solution test granularity, front-matter vs build path names.
- `[fable]` APPROVE WITH NITS (verified 287 cells: 283 stdout + 4 silent) — must-fix spec gaps: 11
  deliberate-error `no-exec` cells are not "Try it yourself"; Atkinson Hyperlegible lacks arrow glyphs
  (254 uses); Algorithm Challenge transform and data files; U06 asset-based answer key; comment-only
  starters must stay visible; teacher-notes headings/jargon/breakable panels; answer-key asserts and the
  Student Book's "see the solution" wording; nits on lead-ins, `$` math, running-head titles, missing book
  furniture.
- `[sol]` **REJECT** — Notice detection at paragraph level and grouping rules for all three entry types;
  reproducible turtle replay (fresh tracker, styles, window calls, scaling, failures) and lesson asset
  listing; an enforceable Student Book source boundary with sentinel tests; completeness checks by counts
  and order; silent-cell comparison; CI time.

### Round 1 — fold

- `[FIXED]` all of the above: the Global constraints, Phase A, Phase B, Phase C and Phase E were
  rewritten — stdout-only rule with explicit failure kinds and silent cells; idempotence test; turtle
  segments/styles/reset and `turtle_figure.py` with scaling and failure behaviour; paragraph-level Notice;
  grouping rules for exercises, checkpoints and the brief (data files printed); `error-demo` tag for the 11
  error cells; lesson and exercise asset listing; starter blocks always printed plus answer areas; teacher
  panels with heading shift, jargon removal, breakable; answer keys with asserts stripped and U06 asset
  solutions; a source allowlist with sentinel tests on project files and PDF text; a fallback font for
  missing glyphs and a `Missing character` log check; completeness audit by ordered counts; CI duration
  recorded; `front-matter/` path; out-of-scope book furniture listed.

### Round 2 — [sol] REJECT (folded)

- `[FIXED]` the opener is the paragraphs after the H1 in the same cell; the exercise statement that
  shares the `### Title` cell is kept.
- `[FIXED]` completeness uses a typed block inventory keyed by source cell id; answer-key labels follow
  each entry type (Exercise / Question / Problem).
- `[FIXED]` the tagged cells are enumerated by id (9 `error-demo`, 1 `hang-demo` for the infinite loop
  with a "this never stops" panel); `u07l034a` routes to "Program excerpt"; routing precedence fixed.

### Round 3 — [sol] REJECT (folded)

- `[FIXED]` the Notice rule covers all three source forms found by a survey of every lesson paragraph
  (262 bold `**Notice:**`, 15 plain `Notice:` in U12, 4 headings containing `Notice`); a U12 fixture test, a
  per-chapter Notice-count audit and a U12 page in the rendered review were added.

### Round 4 — CONSENSUS

- `[sol]` APPROVE WITH NITS (r4) — Notice forms, fixture and audit verified; nits folded (exact Notice
  counts 262/15/4; out-of-scope names both new tags).
- `[fable]` APPROVE WITH NITS (r1, folded) · `[glm]` APPROVE WITH NITS (r1, folded) · `[self]` APPROVE
  WITH NITS.

**Consensus reached — implementation starts.**

## Content Review

### Round 1 — verdicts (HEAD b9bf2a5; PDF snapshots of polish round 3)

- `[self]` APPROVE WITH NITS — three rounds of rendered-page review folded (numbering, callouts, framed
  code + output, turtle figure clipping, TOC kind labels, duplicate asset listings, orphaned labels);
  `ci-local.sh` ALL GREEN with both book renders (1709 s).
- `[fable]` **REJECT** — U06 asset-reference line swallowed the following `##` headings (TOC/outline lost
  Lessons 2–3 and Exercises); stranded Challenge headings; answer rules colliding with the Starter box;
  turtle answer keys printing the test harness; Real-program wording fragments; mixed heading fonts.
  Fidelity, leak and stored-output checks clean.
- `[glm]` **REJECT** — the same U06 corruption (literal `##`/`:::` in both PDFs); answer areas 4/8 vs
  the plan's 6/12; Challenge title form; suggested a literal-artefact audit.
- `[sol]` **REJECT** — the same U06 corruption; answer-area count vs the plan.

### Round 1 — fold

- `[FIXED]` every emitted block ends with a blank line and blocks join with a blank line; the audit now
  rejects literal Markdown/Quarto artefacts in PDF text and checks source `##` headings reach the outline
  (U06 now lists Lessons 1–3 and Exercises); regression test added.
- `[FIXED]` exercise/question/problem headings keep with their body; answer rules start clear of the
  Starter box and never orphan; turtle answer keys drop harness cells and show the solution program +
  figure; Real-program notes are full sentences ("… (not graded)." for checkpoints) and "no real
  program" notes say so without pointing to the Teacher's Edition; headings use Atkinson Hyperlegible;
  Challenges render "Challenge — Title" with an "Exercise N" badge.
- `[FIXED]` plan text now records the 4/8 answer-line counts (reduced during Phase D to keep the Student
  Book near 460–500 pages).

### Round 2 — CONSENSUS

- `[sol]` APPROVE WITH NITS (r2) — no artefacts, U06 outline complete, plan records 4/8 lines; nit folded
  (Real-program notes capitalised in both editions).
- `[fable]` APPROVE WITH NITS (r2) — all six round-1 items verified on rendered pages; nits folded: the
  U12 `## Challenge` section note now introduces the next exercise instead of joining Exercise 24; the
  checkpoint no-real note says "for this question". Recorded as follow-ups (not blocking): keep-together
  page growth (≈36 pages; answer areas could split after the Starter), one answer-key "Expected output"
  label orphaned at a page foot, and the doubled label on U06's "Contrast Notice" heading.
- `[glm]` APPROVE WITH NITS (r2) — nits recorded: "Lesson One" vs "Lesson 1" naming (source wording, out
  of this plan's scope) and the U03 PDF bookmark dropping inline code (`if`).
- `[self]` APPROVE WITH NITS.

**Consensus reached.**

## Post-Execution Report

**Status: implemented; audits clean (2026-09-25).**

- **Phase A (Codex gpt-6-sol):** `fill-outputs` / `lesson-outputs-check` (stdout-only, silent cells `[]`,
  idempotent), `fake_turtle` segment/style recording, `tools/turtle_figure.py` (TikZ, padded, centred,
  captioned); `lesson-outputs-check` in ci-local (Book 1 and Book 2 SKIP until plan 086).
- **Phase C:** 287 executable lesson cells in the 13 Book 1b lessons now store their verified outputs; 9
  `error-demo` + 1 `hang-demo` tags. The notebook diffs contain only outputs and those tags (verified by
  all three reviewers).
- **Phase B (Codex):** `tools/publish.py` (notebook → `.qmd`, paragraph-level Notice, routing, grouping
  for exercises / checkpoint questions / brief problems with data files, teacher panels, answer keys, a
  single source-allowlist gate), the Quarto theme (`tools/publish_theme/`), `scripts/build-book.sh`,
  `tools/publish_audit.py` (chapter order, per-item counts, typed block inventory, Notice counts, answer-key
  coverage, tag re-derivation, render-log and literal-artefact checks, student/teacher boundary sentinels).
- **Phase D:** front matter written (`book1b/front-matter/`); four rounds of rendered-page review and
  layout polish (numbering, unit/checkpoint labels, framed code + attached Output, light callouts, turtle
  figure bounds, running heads, keep-together rules, answer areas 4/8 lines).
- **Result:** Student Book 496 pages, Teacher's Edition ≈860 pages; `publish-audit` PASS (19 chapters,
  391 items per edition, 0 overfull boxes, no missing glyphs, no notebook or Markdown artefacts); 29
  publication tests; `scripts/ci-local.sh` ALL GREEN in 1709 s with both book renders (previous runs,
  before the book build, took roughly 20 minutes).
- **Follow-ups (not blocking):** page growth from keep-together rules; an orphaned answer-key label; the
  U06 "Contrast Notice" double label; U03 bookmark inline code; "Lesson One" vs "Lesson 1" source
  naming; Book 1 and Book 2 editions (later plans).
