# Plan 097 — Publication tooling for every book

**Goal:** Make the publication pipeline (the publisher, the audit, the theme, and the handout and syllabus build) work for every book, with no change to *Python, Concept by Concept*'s generated content.
This is design 010's first rollout step. Plans 098–100 then author each book's content and turn on its `publication` flag.

**Spec:** design 010 (D1–D5), which extends design 007.
User decisions, 2026-09-30: "all books should have pdfs"; the same four editions for every book; goals/recap panels everywhere; a short unnumbered contest setup chapter.
The read-only gap survey (2026-09-30) is summarised in design 010 §1.

## Survey (2026-09-30, main at 996bb19)

- **The publisher** (`tools/publish.py`, 983 lines):
  - `EDITIONS` holds the four profiles.
  - `build()` reads fixed front-matter names, a mandatory numbered `docs/unit-00-getting-set-up.md`, `back-matter/glossary.md` and `quick-reference.md`.
  - `entries()` parses syllabus rows `| \`unit-…\` |`, but *Python by Projects* has a leading `| # |` column, which it does not parse.
  - `render_items` / `group_title` skip each item's heading cell (lines 389–394, 439). That is harmless in python-concepts, where all 345 heading cells are heading-only, but it drops the statement in:
    - *Python by Projects*: 132/180 exercises and 23/31 questions
    - *USACO Bronze*: 127/127 and 26/26
    - *ACSL*: 324/324 and 35/35
  - Answers print `verify` cells as code plus Check lines (lines 287–326, 535–544), and markdown answers are not passed through `markdown_blocks`.
  - `solution_assets` knows only `solutions_ex*.py`, and `allowed_source` admits every `units/*/assets/*.py` to student editions (line 154), which would include the contest solutions `exN.py`.
  - The projects' running header is fixed to "Algorithm Challenge" (line 585). `PYTHON_INDEX_NAMES` is Python-book specific.
- **The audit** (`tools/publish_audit.py`, 878 lines) hard-codes python-concepts values:
  - `ERROR_IDS` / `HANG_IDS` (lines 38–40)
  - `PRINT_REQUIRED_STARTERS` (line 50)
  - the unit-06 turtle try-its and the 21 Teacher's Edition drawings (lines 371, 812)
  - the banned phrases (lines 41–48)
  - answers beginning at "Unit 1, Exercise 1" (lines 69–75)
  - unit 0 read as the setup chapter (lines 439–445)
- **The theme** (`tools/publish_theme/panels.lua`, lines 90–91, 111–112) wraps only arrows, Greek, U+25B8 and U+2610 in `\fallbackfont`, and only in `Str` / `Code`, not in code blocks.
  An ACSL trial render reported missing `⊕` (×40), `⊙` (×30), subscripts `₀–₈` (~140), `✓ ✗` and `⌊ ⌋`.
- **Handouts and syllabi** (`scripts/build-pdf.sh`) build with Latin Modern via `xelatex -quiet`, and drop missing glyphs silently:
  - a unit 05 handout lost its `⊕`
  - a unit 01 handout lost 29 subscripts
  - a syllabus lost `≥`

  `ci-local.sh` step 5 skips `judge` books. A trial build of both contest books worked, apart from the glyphs.

## Phases

### Phase A — Baseline and per-book config (D1)

1. Before any code change, capture python-concepts' generated Quarto projects for all four editions (every `.qmd` and `inventory.json`) and its `publish-audit` findings into a baseline under `build/` (git-ignored).
   The regression test compares against a checked-in digest (`tests/data/python-concepts-publish-digest.json`, SHA-256 per generated file per edition).
2. Add `<book>/publication.yaml` with a schema, loaded and validated by `tools/books.py`. It holds:
   - `setup:` — `source`, `teacher_notes`, and `numbered` (bool): the title is "Unit 0 — Getting Set Up" when numbered, and "Getting Set Up" otherwise
   - `project_headers:` — a map from project id to header text
   - `audit:` — the per-book expectations:
     - `error_demo_ids`, `hang_demo_ids`, `print_required_starters`
     - `turtle_tryits: {unit_id: count}` and `teacher_turtle_drawings`
     - `phrase_exemptions: {phrase: reason}`
     - `goals_recap: required`, required for every book by user decision
   - `index_names:` — the Python names the index recognises

   Every python-concepts constant moves into `python-concepts/publication.yaml` unchanged.
   `publish` and `publish-audit` read the config, and `build-book.sh` refuses a `publication: true` book that has no valid config.
3. The regression test passes: the digest is identical for all four editions, and the audit findings are unchanged.
   Phase B may change python-concepts output only where D2/D3 require it (for example, answer markdown now passing through `markdown_blocks`). Each such change is listed file by file with its reason, the digest is updated in the same commit, and the rendered pages are compared in the content gate. Phase A itself changes nothing.

### Phase B — Rendering and answers for every book (D2, D3)

- **Items:**
  - Statements come from the heading cell as well as the following cells.
  - The title is the first `###` heading that is not one of the structural subsections: `Input`, `Output`, `Constraints`, `Sample Input`, `Sample Output`, `Example`.
  - Structural subsections become unnumbered run-in subheads; sample I/O prints as code blocks.
  - `_Division: X and above._` prints as a division tag; the `**Your answer:**` placeholder prints nothing.
- **Syllabus:** `entries()` accepts an optional leading `| # |` column.
- **Setup chapter:** it follows `publication.yaml` (numbered or not). A book whose own Unit 0 is a real unit (ACSL Foundations) keeps that as Unit 0. The audit's outline parser identifies the setup chapter by id, never by the number 0.
- **Answers:**
  - Short-answer items print their worked markdown (through `markdown_blocks`) and their `**Answer:**` line.
  - `verify`-tagged cells are never printed.
  - Judge programming items print `assets/exN.py` as a listing.
  - The answers-start check accepts the book's first unit number.
- **Source boundary:** `assets/exN.py`, `assets/q*.py` and `assets/verify/**` are solution sources, outside every student allowlist except through `student_answer_sources`. `allowed_source` and the leak guard are extended to match.
- **Project running headers** come from `publication.yaml`.

### Phase C — Glyphs and the handout/syllabus build (D4, D5)

- `panels.lua` wraps the D4 ranges in `\fallbackfont`, in prose, inline code and code blocks (the code-block path uses a listings/fvextra escape, or a font with fallback).
- A handout template for nbconvert and a pandoc template for syllabi use the book fonts plus the fallback.
- **The missing-glyph check:** a small tool, `tools/pdf_glyphs.py`, scans a LaTeX log for `Missing character` and fails. It runs for every handout and syllabus build. The book audit already has this check, now with the wider fallback.
- `ci-local.sh` step 5 builds handouts and the syllabus for **every** book (the `judge` gate goes).

### Phase D — Unit tests

Fixture books under `tmp_path`:
- (a) a python-concepts-style item
- (b) a heading-body item (*Python by Projects* style)
- (c) a judge programming item with Input/Output/Constraints/Sample sections and a `_Division:_` line
- (d) a short-answer item with a `**Your answer:**` placeholder, and a solution containing a `verify` cell and an `**Answer:**` line

The tests cover:
- the statement is present
- the title is correct
- subheads, the division tag, and no placeholder
- the answer shows the `**Answer:**` text and no `verify` code
- `exN.py` absent from student editions except the odd answers
- the setup chapter numbered and unnumbered
- config validation errors
- the missing-glyph check on a crafted log
- the regression digest

## Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN in a solo run on the final commit. That run builds handouts and syllabi for all four books, with no missing glyphs, and python-concepts' four editions as before.
2. The python-concepts regression digest is identical for all four editions, and its audit findings are unchanged.
3. **Trial report (not a gate).** In a scratch copy, flag *Python by Projects*, *USACO Bronze* and *ACSL* `publication: true` with stub front and back matter, and build one edition each. Report for each book:
   - the page count
   - that sampled statements are present (Exercise 1 of a contest unit)
   - that there are 0 missing glyphs
   - the remaining audit findings, which are the content plans' to-do list
4. Post-execution report.

## Out of scope

- Per-book content (front and back matter, glossary, setup chapters, goals/recap panels, lesson outputs, leak and phrase fixes) → plans 098–100.
- Flagging any new book `publication: true` → plans 098–100.
- The GitHub Release → after plan 100.
- This is a tooling-only plan; it ships no units, projects or checkpoints.

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- **N1 (folded):** a strict byte-identical guard would block Phase B's intended fixes where they touch python-concepts (answer markdown). Phase A stays byte-identical; Phase B's python-concepts diffs are listed, justified and rendered for review, and the digest is updated deliberately.
- Tooling-only exemption: the plan ships no units, projects or checkpoints. It states this in Out of scope and still names Phase E.

## Content Review

## Post-Execution Report
_(filled before merge.)_
