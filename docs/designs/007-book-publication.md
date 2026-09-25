# Design 007 — Book publication: lesson outputs, a typeset book, and a Teacher's Edition

Status: proposed (2026-09-24).
Extends design 000 §1 ("Jupyter notebooks as source of truth; PDFs are built artifacts") and §4
(PDF build).
First applied to Book 1b (plan 085); Book 1 and Book 2 follow in later plans.

## 1. Purpose

The user asked for four things (2026-09-24):

1. Lesson notebooks should show the **expected result** of every executable cell.
2. A **publishable book** built from the notebooks — real book layout and typography, not a notebook
   print-out.
3. A reasoned decision on whether content should move out of notebooks into a media-agnostic source
   (Markdown), with the PDF book and the lesson notebooks as views of that source.
4. A way to put the **teacher notes** into the printed book.

Today the only PDFs are `nbconvert --to pdf` print-outs of each unit's `exercises.ipynb` (handouts)
plus the syllabus; they carry notebook framing (`In [ ]:` prompts, raw cell boxes) and no lessons.

## 2. Decisions

- **D1 — Notebooks stay the source of truth (user decision, 2026-09-24: "Keep .ipynb").**
  The typeset book is a *view* generated from the notebooks plus the Markdown teacher notes; nothing is
  migrated. Reasoning: Quarto reads `.ipynb` and `.md` side by side, so "content once, many views" does
  not require moving the content; a migration would rewrite ~120 notebooks and 40+ checks keyed on cell
  ids, tags (`no-exec`, `stretch`) and solution cells, and would reverse design 000's founding rule for
  mostly cosmetic gain. If diffing or prose editing of `.ipynb` becomes a real cost later, jupytext
  pairing (a readable `.md` twin of each notebook) is the escape hatch; it is out of scope here.
- **D2 — Lesson notebooks store their outputs.**
  A tool (`py4kids-tools fill-outputs`) executes each `lesson.ipynb` from its unit folder (the CI
  working directory) and saves the outputs into the notebook, with execution counts cleared and no
  run-specific metadata, so diffs stay stable. `no-exec` cells keep no outputs (they read stdin or open a
  turtle window). A new check (`lesson-outputs-check`) re-executes every lesson and fails when a stored
  output differs from what the code prints, or when an executable cell has no stored output — so the
  expected results can never drift. Exercises, checkpoints and briefs keep the existing rule: no
  outputs (they are the student's work). Seeded randomness and self-contained file cells make lesson
  outputs deterministic; the check proves it.
- **D3 — The book is built by Quarto from a generated project.**
  A builder (`py4kids-tools publish --book book1b --edition student|teacher`) writes a Quarto book
  project under `bookN/build/publish/<edition>/` from `books.yaml`, the syllabus order and the unit
  folders, then runs `quarto render` to PDF. The builder transforms copies of the notebooks, never the
  sources:
  - code cells render with their **stored outputs** (Quarto `execute: enabled: false`), so the book
    shows exactly what D2 verified;
  - `no-exec` cells render as code under a "Try it yourself" label, with no output;
  - `**Notice:**` paragraphs become Notice callouts; `stretch` exercises get a Challenge marker; each
    exercise's `**Real version:**` line becomes a small "Real program" note;
  - notebook-only furniture is removed (execution counts, empty starter cells become a short
    "Your turn" answer area in the student edition);
  - turtle assets referenced by lessons render as listings of the `.py` file.
- **D4 — Two editions from the same sources (user decision: "Two editions").**
  - **Student Book:** front matter (title page, how to use this book, table of contents), then for each
    unit in syllabus order: a unit opener (the hook), its lessons, its exercises (core, More Practice,
    Challenge); checkpoints where the syllabus places them; the Algorithm Challenge; no solutions.
  - **Teacher's Edition:** everything in the Student Book, plus at the start of each unit a shaded
    **Teacher panel** holding that unit's `teacher-notes.md` (goals, pacing, common mistakes, discussion
    prompts, differentiation), plus an **answer key** after each exercise set (the solutions notebook's
    solution cells and real programs), and each checkpoint's teacher notes and solutions.
- **D5 — Typography and layout.**
  KOMA-Script `scrbook`, 7 × 10 in trim, a readable humanist body face (Atkinson Hyperlegible — designed
  for legibility), a monospace face with clear 0/O and 1/l (Fira Mono or Cascadia Code), tcolorbox panels
  for Output, Notice, Try it yourself, Challenge, Real program and Teacher; unit openers on recto pages;
  running heads with unit and lesson names; generous code line spacing and no code wider than the text
  block (long lines wrap with a marker). All fonts ship with TeX Live — no external downloads.
- **D6 — Verification.**
  `scripts/ci-local.sh` gains `lesson-outputs-check` and builds both Book 1b editions (the existing
  handout and syllabus PDFs stay). Unit tests cover the builder's transforms (tags → callouts, `no-exec`
  handling, output preservation, teacher-panel insertion, answer-key placement, and that the Student Book
  contains no solution content). Plans applying this design include a rendered-page review in their
  content gate (reviewers look at sampled page images, not only the source).

## 3. Rollout

| plan | scope |
|---|---|
| 085 | Book 1b: `fill-outputs` + `lesson-outputs-check`, stored lesson outputs, the publisher, both editions, typography, CI. |
| later | Book 1 and Book 2 editions (turtle-heavy Book 1 and judged Book 2 assets need their own transforms). |

## 4. Non-goals

- No change to the notebooks' role as the source of truth; no Markdown migration; no jupytext pairing.
- No e-book/HTML edition yet (Quarto can add one later from the same project).
- No change to exercise/checkpoint hygiene (still output-free and solution-free).
