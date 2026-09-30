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
   - `project_headers:` — a map from project id to header text. The audit's page-header reset rule (`publish_audit.py:307`) is **derived** from these values plus the fixed back-matter names, not from a hard-coded "Algorithm Challenge"
   - `audit:` — the per-book expectations:
     - `error_demo_ids`, `hang_demo_ids`, `print_required_starters`
     - `error_demo_routing_exceptions` (python-concepts: `u07l034a`, now hard-coded at `publish_audit.py:648`)
     - `print_page_target` (python-concepts: 400, a soft warning)
     - `turtle_tryits: {unit_id: count}` and `teacher_turtle_drawings`
     - `phrase_exemptions: [{phrase, sources, reason}]`, where `sources` is a list of source-path globs relative to the book (for example `units/*/lesson.ipynb`). An exempt phrase is allowed only in chapters generated from matching sources, and is still banned everywhere else: front matter, answers, other notebooks.
     - `goals_recap: required`, required for every book by user decision
   - `index_names:` — the Python names the index recognises
   - `lesson_heading:` — the regex for lesson headings

   **Validation (F10, F13):**
   - `setup.teacher_notes` must match the teacher-notes exclusion pattern, and the student allowlist takes the setup source from the config (`STUDENT_SOURCES` no longer hard-codes it).
   - `publish` and `publish-audit` themselves fail loudly when a publication book has no `publication.yaml`. The existing fixture books in `tests/test_publication_editions.py` get a minimal config.

   Every python-concepts constant moves into `python-concepts/publication.yaml` unchanged.
   `publish` and `publish-audit` read the config, and `build-book.sh` refuses a `publication: true` book that has no valid config.
3. **The regression contract:**
   - The pre-change digest is **immutable** (`tests/data/python-concepts-publish-baseline.json`, written once in step 1 and never edited).
   - At the end of Phase A, the generated output equals it exactly.
   - At the end of the plan, the regression test compares the current output with the baseline. It passes only if every differing file is listed in `tests/data/python-concepts-publish-allowed-diffs.yaml` with a reason naming the D2/D3 rule that requires it (for example, answer markdown now passing through `markdown_blocks`).
   - The content gate reviews that list and the rendered pages it affects.
   - The audit findings for python-concepts stay unchanged (all PASS).

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
  - **Checkpoints:** as design 007 amended it, the student editions print no checkpoint answers. The Teacher's Edition prints each checkpoint's answers the same way: short answers from their `**Answer:**` lines; a judge programming question as a listing of its `assets/qN.py`.
  - `verify`-tagged cells are never printed.
  - Judge programming items print **the solution notebook's mirror cell**, which the judge already enforces to be byte-identical to `assets/exN.py` / `qN.py` / `pN.py` (`tools/judge.py:220`). The file is never printed a second time; it is only a boundary object (F2).
  - The answers-start check accepts the book's first unit number.
- **Source boundary:** files matching exactly `^(ex|q|p)\d+\.py$` under `assets/` (unit `exN.py`, checkpoint `qN.py`, project `pN.py`), and `assets/verify/**`, are solution sources. `exN_name.py` starters stay allowed; a test covers both sides (F9). They are outside every student allowlist except through `student_answer_sources`, which reads odd unit `exN.py` only. `allowed_source`, `solution_assets` and the leak guard (`publish_audit.py:264`) are extended to all three kinds. Tests cover the Teacher's Edition rendering checkpoint `qN.py`, and a student edition failing the audit if any `exN.py` / `qN.py` body appears outside the allowed odd answers.
- **Project running headers** come from `publication.yaml`.

- **stdin programs (F1):** a `no-exec` lesson cell that reads `sys.stdin` or `open(0)` is a stdin program. It renders as a "Try it yourself" panel with a line on running it with a sample file, and `_expected_lesson_kind` in the audit mirrors this. This covers USACO's 33 such cells; ACSL's `input()` cells already route to Try it.
- **Lesson headings (F5):** `publication.yaml` gains `lesson_heading` (a regex; python-concepts `^## Lesson\b`). `markdown_blocks`' demotion rule and the audit's lesson checks use it. Plan 098 decides whether to rename *Python by Projects*' `## L1:` headings or configure them.
- **Checkpoint titles (F7):** `render_chapter` strips `# Checkpoint N:` and `# Checkpoint N — ` alike.
- **Titles (F8):** structural subsections match by prefix (`Sample Input 1` is structural). A `### Problem N — Title *(topic)*` heading supplies its own title, with the italic tag dropped from the running head.

### Phase C — Glyphs and the handout/syllabus build (D4, D5)

- **Font fallback (F4):** the theme uses **luaotfload font fallback**, not per-codepoint wrapping. `luaotfload.add_fallback` chains DejaVu Sans and DejaVu Sans Mono, with `RawFeature={fallback=…}` on the main, sans and mono fonts. That covers prose, inline code, code blocks, headings, raw `\chaptermark`, index entries, the TOC and running heads. It applies only to glyphs the primary font lacks, so python-concepts' pages look the same. The old `panels.lua` wrapping is kept only if it is still needed.
- **Handouts and syllabi (F3):** the builds become two steps with a kept log. `nbconvert --to latex` and `pandoc -s -o *.tex` write the source, then `lualatex` runs in a kept `build/` directory, using templates with the book fonts and the same fallback. Today nbconvert and pandoc discard the engine log, so there is nothing to check.
- **The missing-glyph check:** a small tool, `tools/pdf_glyphs.py`, scans the kept LaTeX log for `Missing character` and fails. It runs for every handout and syllabus build. The book audit already has this check, now with the wider fallback.
- `ci-local.sh` step 5 builds handouts and the syllabus for **every** book (the `judge` gate goes).
- **Change-scoped book builds (D7):** `ci-local.sh` renders a publication book's editions only when `git diff origin/main...HEAD` (plus uncommitted changes) touches that book's root, `tools/publish*.py`, `tools/publish_theme/`, `scripts/build-book.sh` or `books.yaml`. `ci-local.sh --all-books` renders every publication book, and it is required before a release. The step prints which books it rendered or skipped, and why. A skip is never silent.

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
- stdin-program routing and its audit mirror; a `## L1:` lesson heading with a configured `lesson_heading`; `# Checkpoint N — Title` stripping; `Sample Input 1` as structural; a `### Problem N — Title *(topic)*` title
- one judge answer printed once (the mirror cell, not the file as well)
- the missing-glyph check on a crafted log
- **a real render fixture:** a minimal Quarto project through the theme (prose, inline code and a code block containing one character from each D4 range) renders with no `Missing character`; likewise a one-cell nbconvert handout and a pandoc syllabus through the new templates. These run in `ci-local.sh` as a slow-marked test.
- the audit with a non-python-concepts project header (a "Mock Contest" header resets as configured)
- a scoped phrase exemption: allowed in a matching lesson, and failing in front matter and in an answer
- the regression digest

## Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN in a solo run on the final commit. That run builds handouts and syllabi for all four books, with no missing glyphs, and python-concepts' four editions as before.
2. The python-concepts regression digest is identical for all four editions, and its audit findings are unchanged.
3. **Trial report (not a gate).** In a scratch copy, flag *Python by Projects*, *USACO Bronze* and *ACSL* `publication: true` with stub front and back matter, and build one edition each. Report for each book:
   - the page count
   - that sampled statements are present (Exercise 1 of a contest unit)
   - that there are 0 missing glyphs
   - the remaining audit findings, which are the content plans' to-do list
4. Post-execution report. It records how the regression baseline is retired: once plan 097 merges, the immutable-baseline test is regenerated only by an explicit command, so later errata to *Python, Concept by Concept* are not blocked (F11).

## Out of scope

- Per-book content (front and back matter, glossary, setup chapters, goals/recap panels, lesson outputs, leak and phrase fixes) → plans 098–100.
- Flagging any new book `publication: true` → plans 098–100.
- For plan 098: *Python by Projects*' `Lesson One` headings (an independence ban, F6), its `## L1:` lesson headings, and checkpoint-01's bold-text title are content fixes (or a scoped exemption / `lesson_heading`) there.
- The GitHub Release → after plan 100.
- This is a tooling-only plan; it ships no units, projects or checkpoints.

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- **N1 (folded):** a strict byte-identical guard would block Phase B's intended fixes where they touch python-concepts (answer markdown). Phase A stays byte-identical; Phase B's python-concepts diffs are listed, justified and rendered for review, and the digest is updated deliberately.
- Tooling-only exemption: the plan ships no units, projects or checkpoints. It states this in Out of scope and still names Phase E.

### Round 1 — verdicts and fold

- `[sol]` **REJECT**, 5 findings, all folded:
  1. The config gains `error_demo_routing_exceptions` and `print_page_target`; the header-reset rule is derived from `project_headers`; tested with a "Mock Contest" header.
  2. Phrase exemptions are scoped by source globs; tested allowed and disallowed.
  3. Checkpoint answers are Teacher's-Edition-only (short answers and `qN.py`); the leak guard covers `exN`/`qN`/`pN`.
  4. One regression contract: an immutable pre-change baseline plus an allowed-diff list with reasons; design 010 is reworded to match.
  5. A real render fixture (book theme, handout, syllabus) with every D4 glyph in prose and code blocks.
- `[fable]` **APPROVE WITH NITS**, 13 findings, all folded:
  - F1: stdin lesson programs get a Try-it route and its audit mirror.
  - F2: judge answers print the judge-enforced mirror cell once.
  - F3: handouts and syllabi keep their LaTeX log (two-step builds, `lualatex`).
  - F4: luaotfload font fallback.
  - F5: `lesson_heading` config.
  - F6: `Lesson One` goes to plan 098.
  - F7: checkpoint titles with ` — `.
  - F8: prefix-structural subheads and `Problem N — Title` titles.
  - F9: the exact solution-file regex.
  - F10: setup teacher notes validated against the exclusion.
  - F11: baseline retirement.
  - F12: the real build cost, recorded in design 010 D7 with change-scoped book builds.
  - F13: config required, with fixture configs.

## Content Review

## Post-Execution Report
_(filled before merge.)_
