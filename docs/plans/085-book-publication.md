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
- No new Python dependencies (Quarto, pandoc, TeX Live with KOMA/tcolorbox/TikZ and the fonts are
  already installed); the builder uses the standard library + `nbformat` + `pyyaml`.
- Stored lesson outputs are **stream text only** (`stdout`); an executable lesson cell whose output would
  be anything else (images, rich display, errors) fails `fill-outputs`. Execution counts are cleared and
  cell/notebook metadata left untouched so diffs stay minimal.
- Exercise, checkpoint and brief notebooks keep the existing hygiene rule (no outputs).
- Student Book contains **no solution content** (verified by a test).

## Phase A — Tooling: stored outputs and turtle traces (Codex gpt-6-sol)

- `tools/notebooks.py` + `tools/cli.py`: `fill-outputs --book B [--unit U]` executes each `lesson.ipynb`
  with the CI executor (cwd = unit folder, `no-exec` cells skipped) and writes each executable cell's
  stdout as a single `stream` output (`name: stdout`), `execution_count: null`; cells printing nothing
  get an empty output list. `lesson-outputs-check --book B` re-executes and fails with
  `FAIL: <unit>: lesson code cell <id> output is stale` / `… has no stored output` /
  `… produced non-stream output`. Scratch files written by lessons stay git-ignored.
- `tools/fake_turtle.py`: record drawn **segments** — `(x1, y1, x2, y2, color, width)` for every pen-down
  move — plus the pen state; expose them via a new `segments()` function. Existing `state()` keys and
  `turtle-check` behaviour are unchanged.
- `scripts/ci-local.sh`: add `lesson-outputs-check` to the notebook stage (Book 1b only until later plans
  fill the other books; the check reports `SKIP (plan NNN)` for books without stored outputs).
- Tests: fill→check round trip on a fixture notebook; stale output detected; `no-exec` skipped; non-stream
  output rejected; segment recording for a square (4 segments, closed) and a pen-up travel (no segment).

## Phase B — Tooling: the publisher (Codex gpt-6-sol)

`tools/publish.py` + `py4kids-tools publish --book book1b --edition student|teacher` +
`scripts/build-book.sh --book book1b` (both editions). It writes a Quarto book project to
`book1b/build/publish/<edition>/` and renders `Book1b-Student.pdf` / `Book1b-Teacher.pdf`.

- **Order:** front matter → for each entry in the syllabus order (units, checkpoints after Units 03, 05, 08,
  11, 13, then the Algorithm Challenge): one Quarto chapter.
- **Notebook → `.qmd` transform** (the builder writes Markdown; Quarto never executes anything):
  - markdown cells pass through; a cell starting `**Notice:**` becomes `::: {.notice}`; the unit's first
    cell (the hook) becomes the chapter opener `::: {.opener}`;
  - code cells become fenced `python` blocks followed by their stored output in `::: {.output}` (omitted
    when empty);
  - `no-exec` cells become `::: {.tryit}` "Try it yourself" blocks (code, no output); a `no-exec` cell whose
    code imports `turtle` is replayed through `fake_turtle` and followed by a **figure** — a TikZ drawing of
    its segments (colours via `xcolor` svgnames, scaled to the text width) — captioned with the script's
    purpose;
  - exercises: heading → "Exercise N — Title"; `stretch` cells → `::: {.challenge}`; the `**Real
    version:**` / `**No real version:**` line → `::: {.realprog}` note; starter code cells → a
    "Starter" code block (Student Book) — empty-comment-only starters render as a ruled answer area;
  - turtle exercise assets named in statements are listed as code.
- **Teacher's Edition additions:** after each unit opener, the unit's `teacher-notes.md` inside
  `::: {.teacher}`; after each exercise set, an **Answer key** section built from `solutions.ipynb`
  (solution code cells and the real-program fences with their sample input/output); checkpoints get
  their teacher notes and solutions the same way.
- **Theme** (`tools/publish_theme/`: `_quarto.yml` template, `theme.tex`, a Lua filter mapping the div
  classes to tcolorbox environments): KOMA `scrbook`, 7 × 10 in, Atkinson Hyperlegible body, Fira Mono
  code, panels for Output (grey, labelled "Output"), Notice, Try it yourself, Challenge, Real program,
  Teacher; unit openers on recto pages; running heads (unit / lesson); code wraps long lines with a marker.
- **Front matter** (`book1b/publish/front-matter/`, Markdown, authored inline in Phase D): title page,
  "How to use this book", "For teachers" (Teacher's Edition only).
- Tests: transform unit tests (Notice → callout, `no-exec` → Try-it without output, stored output
  preserved, stretch → Challenge, Real line → note, turtle cell → figure with N `\draw` segments, teacher
  panel present only in the teacher edition, Student Book `.qmd` contains no text from any
  `solutions.ipynb`); `build-book.sh` smoke test in ci-local.

## Phase C — Populate stored lesson outputs (run the tool)

Run `fill-outputs --book book1b`; review the diff (outputs only; 287 executable lesson cells across 13
units); `lesson-outputs-check` PASS; `hygiene-check` unchanged for exercises.

## Phase D — Front matter and typography polish (inline)

Write the front matter (title page text, how-to-use, teacher preface). Render both editions and review
sampled pages as images (unit opener, a lesson spread, an exercise page with a Challenge, a turtle figure
page, a teacher panel, an answer-key page, a checkpoint page); iterate the theme until: no overfull lines
or code overflowing the text block, no orphaned panel headers, figures fit the page, running heads
correct.

## Phase E — VERIFICATION

1. Unit tests (Phases A–B) pass.
2. `lesson-outputs-check` PASS for Book 1b; `hygiene-check` still passes (exercises output-free).
3. Both editions render; a script checks the PDFs: page count within expected bounds, every unit title
   present in the table of contents, "Answer key" present only in the Teacher's Edition, no `In [` /
   `Out[` strings anywhere, no LaTeX overfull-box warnings above a small threshold in the render log.
4. Rendered-page review (sampled pages as images) recorded in the plan.
5. `scripts/ci-local.sh` ALL GREEN (now including the book build).
6. Post-execution report.

## Out of scope

Book 1 and Book 2 editions (later plans); HTML/e-book output; Markdown migration or jupytext pairing
(design 007 D1); changing any lesson or exercise wording beyond storing outputs.

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- Grounded in a spike (real U05 lesson + notes rendered by Quarto) and a survey: 287 executable lesson
  cells, all `no-exec` turtle cells hold complete scripts (so figures can be replayed), no matplotlib (so
  figures are TikZ), full TeX Live with the needed packages and fonts.
- Watch items for reviewers: output determinism (seeded randomness, file cells), the Student Book's
  no-solution guarantee, and whether emitting `.qmd` (instead of rendering `.ipynb` directly) is the
  right control point.

## Content Review
_(4-way content-review gate — reviewers inspect sampled rendered pages as well as sources.)_

## Post-Execution Report
_(filled before merge.)_
