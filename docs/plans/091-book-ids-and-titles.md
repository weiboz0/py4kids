# Plan 091 — Rename the books: level-named ids and proper titles

**Goal:** Replace `book1` / `book1b` / `book2` with `python-projects` / `python-concepts` / `usaco-bronze` everywhere they are live.
Give every book a title from `books.yaml` that student-facing pages and PDF names use.
Split and new ACSL content come in plans 092+.

**Spec:** design 008 (D1, D2, D4 step 1). User decisions, 2026-09-28:
- "we should name these books properly, now we have 3 books, 2 of them are python introduction, 1 is for basic competitive programming. I want to separate the cp book into acsl and usaco"
- "option 2 but with proper naming, usaco book just covers beginning concepts, we may have more advanced books"
- Title set "Python / Contest series"
- Folder ids "Level-named ids"
- "for ACSL, we will cover all levels in one book, but mark concepts by level" (the ACSL book is `acsl`; plan 092)

## Survey (2026-09-28)

- **`tools/`, `tests/` and `scripts/`:** about 750 literal references to `book1` (493), `book2` (142) and `book1b` (111), in about 25 files. Examples:
  - `EXPECTED_BOOK1B` in `tools/turtle_real.py`
  - `book_id == 'book1b'` branches in `tools/publish_audit.py`
  - `--book book1b` in `scripts/ci-local.sh`
  - the `Book1b-*` PDF names
- **`books.yaml`:** three entries. `book1b` is `variant_of: book1`; `book2` has `depends_on: [book1]`.
- **Content:** 23 files carry 30 mentions of "Book 1", "Book 1b" or "Book 2" (syllabi, front matter, `docs/README.md` files, some lessons and teacher notes). The publication subtitle is "Book 1b — Year 1".
- **Governance:** AGENTS.md lines 50–51 name `book1/` and `book2/` ("Year 2: OOP, algorithms…" is also stale). The other governance files have none.
- **Docs:** 96 files under `docs/` mention the old ids. Nearly all are historical plans, designs and reviews (kept); design 000 §1 and live READMEs are current-state and get updated.

## Phase A — Design (inline)

Add `docs/designs/008-book-series-naming.md` (this branch).

## Phase B — Rename and titles (Opus subagent, one session; mechanical)

- **B1 Move folders:** `git mv book1 python-projects`, `git mv book1b python-concepts`, `git mv book2 usaco-bronze`.
- **B2 `books.yaml`:**
  - Rename the ids and roots; `variant_of: python-projects`; `depends_on: [python-projects]` for `usaco-bronze`.
  - Add `title` and `subtitle` to each entry:
    - `python-projects`: "Python by Projects" / "Learn Python by building things"
    - `python-concepts`: "Python, Concept by Concept" / "Learn Python one idea at a time"
    - `usaco-bronze`: "Contest Python: USACO Bronze" / "Algorithms for your first programming contests"
  - Bump `books_version`. The registry check validates the new fields.
- **B3 Tools, tests, scripts:**
  - Replace live id literals with the new ids.
  - Where a title or a book-specific switch is needed, read it from `books.yaml` (`title`, `subtitle`) or name the feature it tests. For example, `EXPECTED_BOOK1B` becomes `EXPECTED_PYTHON_CONCEPTS`, and the publication feature switch moves from `book_id == 'book1b'` to a `books.yaml` `publication: true` flag.
  - Book-qualified prerequisite syntax (if any, e.g. `book1:x`) is migrated consistently. Registry contracts keep working.
- **B4 Publication:**
  - `_quarto.yml` title and subtitle come from `books.yaml` (`@TITLE@`, `@SUBTITLE@`); the edition page drops "Book 1b — Year 1".
  - PDF names follow the pattern `output/<id>/<id>-<edition>.pdf`, e.g. `python-concepts-student-print.pdf`, `python-concepts-answer-key.pdf`.
  - Handouts and syllabi go under `output/<id>/`. `output/README.md` is updated.
- **B5 Content wording:**
  - Every student- and teacher-facing "Book 1", "Book 1b" or "Book 2" in live content becomes the book's title, e.g. "Python, Concept by Concept"; "the Year 1 book" where a generic reference reads better.
  - Syllabus headings become "# <Title> — Syllabus".
  - Teacher notes that compare the two intro books name them by title.
  - No other content change.
- **B6 Current-state docs:**
  - AGENTS.md "Project Structure": the new roots and titles, and the contest split noted as planned. This is a governance edit, explicitly requested by the user's renaming decision.
  - Design 000 §1 tree note.
  - `README.md`, if present.
  - Historical docs are not edited.
- **B7 Local state:** the git-ignored scratch paths in `.gitignore` (e.g. `book1/units/unit-09-…/savegame.txt`) move to the new paths.

## Phase C — Solutions

None.

## Phase D — Verification tooling (same subagent)

- A test (`tests/test_book_ids.py`) fails if a live file uses an old id as a path or `--book` value.
  - Scope: `tools/`, `tests/`, `scripts/`, `books.yaml`, `AGENTS.md`, and every file under the three book roots.
  - Excluded: `docs/plans/`, `docs/designs/`, `docs/reviews/` and `ERRATA.md` (historical).
- A test fails if student-facing content says "Book 1b" (or "Book 1" / "Book 2" as a book name).

## Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN under the new ids (every per-book check, both handout builds, all four Python-concepts editions, `publish-audit`).
2. `output/python-projects/`, `output/python-concepts/` and `output/usaco-bronze/` hold the expected PDFs. No old `output/book*` folder remains after a clean rebuild, and `git status` has no PDFs.
3. `git grep -nw 'book1\|book1b\|book2'` outside the historical scope returns nothing. `git log --follow` works through a moved file.
4. Rendered-page review: the Python, Concept by Concept title page and edition page (new subtitle), and a syllabus heading.
5. Post-execution report with the id mapping and page counts (unchanged).

## Out of scope

- Splitting USACO/ACSL (plan 092) and new ACSL units (093+).
- Rewriting historical plans, designs, reviews and errata.
- Any curriculum content change beyond book names.

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- The verification phase is named. Mechanical scope, with a grep-based guard test against regressions.
- Watch items:
  - Scratch paths in `.gitignore` must move too.
  - Book-qualified prerequisite ids, if any exist, must keep resolving.
  - `pre-merge-guard` id checks must use the new roots.
  - Titles must never leak ids onto student pages.

## Content Review
_(filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
