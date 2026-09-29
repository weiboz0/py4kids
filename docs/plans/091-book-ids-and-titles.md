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

## Survey (2026-09-28, corrected by round 1)

- **`tools/`, `tests/` and `scripts/`:** about 880 live occurrences of `book1`/`book1b`/`book2` in about 38 files. They include:
  - id literals such as `--book book1b`, `root / 'book1b'` (`tools/publish_audit.py:262`, a latent bug) and `EXPECTED_BOOK1B`
  - **feature switches keyed on ids:**
    - `book == "book2"` means the stdin/judge model: `tools/judge.py`, `tools/source_policy.py`, `tools/notebooks.py`
    - `book == "book1"` means patterns and coverage-map v2: `tools/patterns.py`, `tools/patterns_doc.py`, `tools/concept_scan.py`, `tools/curriculum.py`, `tools/notebooks.py`, and `scripts/build-pdf.sh`
    - `book_id == 'book1b'` means publication: `tools/publish_audit.py`, `tools/publish.py`
  - the **qualified-concept-id regexes** (`tools/curriculum.py:66`, `tools/concept_scan.py:71`), with hard-coded `book1:`/`book2:` ids and the `tests/fixtures/borrowed_tools/**` manifests and notebooks that use them
  - in-test `books.yaml` writers
  - `scripts/ci-local.sh` (pins the id list), `scripts/pre-merge-guard.sh:77` (id tuple), `scripts/build-book.sh` (`book1b`)
- **Publication:**
  - `tools/publish.py` derives the subtitle from the syllabus H1 by regex `(Book … — Year N)` and fails otherwise.
  - `tools/publish_theme/_quarto.yml` hard-codes the title.
  - `tools/publish_theme/theme.tex` hard-codes "Python, Concept by Concept / Book 1b — Year 1" and "(folder book1b/)".
  - `EDITIONS` `output_name`s are `Book1b-*`.
  - `tools/publish_output.py` owns `Book*-*.pdf`.
  - `.gitignore` and `output/README.md` describe `Book*-*.pdf`.
- **`books.yaml`:** three entries with `number:` 1/1/2; `book1b` is `variant_of: book1`; `book2` has `depends_on: [book1]`.
- **Content:** 23 files carry 30 "Book 1/1b/2" mentions (syllabi, front matter, READMEs, a few lessons and teacher notes, USACO teacher-notes H1s and checkpoint headings).
  - Live text also names folders as paths (`cd book1b/units/…`) and links historical designs by file name (`005-book1b-concept-first.md`). Paths change with the rename; design file names stay.
- **Governance and docs:**
  - AGENTS.md lines 50–54 carry the old roots and stale "Year 2: OOP…" wording.
  - `docs/architecture/decisions.md:27` says "Book 1 units 03/05": historical, **not edited**, since it is a governance file.
  - 96 `docs/` files are historical. Design 000 §1 is current-state (it gets a note).
  - `TODO.md` has "Book 1" prose.

## Phase A — Design (inline)

`docs/designs/008-book-series-naming.md` (this branch), amended in round 1:
- file names use the id
- each contest book is independently complete, with concepts duplicated where both need them, so plan 092 passes prereq and coverage per book

## Phase B — Rename, registry and tooling (Opus subagent, one session, in this order)

- **B1 Move folders:** `git mv book1 python-projects`, `git mv book1b python-concepts`, `git mv book2 usaco-bronze`.
- **B2 `books.yaml` (`books_version: 2`):**
  - Rename the ids and roots; `variant_of: python-projects`; `usaco-bronze` `depends_on: [python-projects]`.
  - Add `title` and `subtitle`:
    - `python-projects`: "Python by Projects" / "Learn Python by building things"
    - `python-concepts`: "Python, Concept by Concept" / "Learn Python one idea at a time"
    - `usaco-bronze`: "Contest Python: USACO Bronze" / "Algorithms for your first programming contests"
  - Add **feature flags**, which replace every id-keyed switch, each with a comment in `books.yaml` saying what it controls:
    - `publication: true` (python-concepts): the book-publication pipeline
    - `judge: true` (usaco-bronze): the stdin `.py` solvers and the subprocess judge
    - `patterns: true` (python-projects): the pattern checks **and** the coverage-map v2 / markdown concept scan; do not set it on a new book unless both apply
  - `number:` stays as a series ordinal (1/1/2) and drives nothing new.
  - `tests/test_books.py` checks non-empty `title`/`subtitle`, unique ids equal to `root`, version 2, and flags that are booleans.
- **B3 Tools, tests, scripts:**
  - Replace the id literals.
  - Convert every id-keyed feature switch listed in the Survey to its `books.yaml` flag.
  - Build the qualified-concept-id owner alternation from the registry ids, so hyphenated ids like `usaco-bronze:str-split` work and a future `acsl:` needs no regex edit.
  - Migrate `tests/fixtures/borrowed_tools/**` and all in-test `books.yaml` writers to the new ids.
  - `scripts/ci-local.sh` reads the id list from `books.yaml`.
  - `pre-merge-guard.sh` gets the new ids plus a one-release **transition map** (`book1→python-projects`, `book1b→python-concepts`, `book2→usaco-bronze`) that normalises old path prefixes read from `origin/main` or the worktree, so open branches cut before this merge still collide-check.
  - Test module file names (`tests/test_book1_units.py` …) are renamed to the new ids.
  - Run `pytest` after B3.
- **B4 Publication:**
  - `_quarto.yml` gets `@TITLE@`/`@SUBTITLE@` from `books.yaml`, passed by `build()`.
  - The syllabus-H1 regex is removed; the subtitle comes from `books.yaml`.
  - `theme.tex`'s title verso takes `@TITLE@`, `@SUBTITLE@`, "First edition, 2026", and "(folder <id>/)" from the build; no "Book 1b — Year 1".
  - PDF names are `<id>-<edition>.pdf`. They are derived from `book_id + edition` in one helper, which `build()`, `build-book.sh`, the audit and `publish_output` all use. `publish_output`'s book pattern becomes `<id>-*.pdf`.
  - `output/README.md`, `.gitignore` comments and the tests (`tests/test_publication_editions.py` pinned names and heading) are updated.
- **B5 Content wording (student- and teacher-facing, live files only):**
  - A book *as a book* is named by its title.
  - Syllabus H1: `# <Title> — Syllabus`.
  - USACO teacher-notes H1: `# Teacher Notes — USACO Bronze, Unit NN: <Title>`.
  - Checkpoint H1s drop only the `Book 2 ` prefix, giving `# Checkpoint N — Mock Contest N`; checkpoint 04 is already book-free and stays as is (markdown only; hygiene stays green).
  - Folder paths in instructions become the new folder (`cd python-concepts/units/…`); they are not title-ified.
  - Links to historical design file names stay.
  - **Teacher-notes wording is done inline by the active session**, per AGENTS.md dispatch. The subagent leaves `teacher-notes.md` files alone. Its handoff may report the Phase D guard red **only** on teacher notes; the orchestrator rewords them before E1, and the guard must be green at E1.
- **B6 Current-state docs:**
  - AGENTS.md "Project Structure" lines 50–54 **only**: the new roots and titles, and the contest split planned in design 008. This is a user-requested governance edit and is named in the PR body.
  - Design 000 §1 gets a one-line pointer to design 008.
  - `README.md` and `TODO.md` wording.
  - `docs/architecture/decisions.md` and the other historical docs are untouched.
- **B7 `.gitignore`:** scratch paths move to the new folders; the output-name comments are updated.

## Phase C — Solutions

None.

## Phase D — Guard test (same subagent)

`tests/test_book_ids.py` scans live files and fails on any match of:
- a path segment: `(^|[^-\w])book(1b?|2)/`
- a CLI value: `--book book(1b?|2)\b`
- a quoted id: `['"]book(1b?|2)['"]`
- a qualified id: `book(1b?|2):[a-z]`
- an old output name, case-insensitive: `Book1b-` or `Book[12]-`
- a book name: "Book 1b" / "Book 1" / "Book 2" used as a book name in student- or teacher-facing content

**Live files:** `tools/`, `tests/` (excluding this test's own patterns), `scripts/`, `books.yaml`, `.gitignore`, `output/README.md`, `AGENTS.md` §Project Structure, `README.md`, `TODO.md`, and all files under the three book roots.

**Not flagged:** `-book1b-` inside a `docs/designs|plans/NNN-…` file name, and the historical scope (`docs/plans/`, `docs/designs/`, `docs/reviews/`, `docs/architecture/`, `ERRATA.md`).

**Design 000:** a separate assertion checks that §1 points to design 008.

## Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN under the new ids. This covers the registry, per-book checks, both handout builds, the four python-concepts editions and `publish-audit`.
2. `output/` after a clean rebuild:
   - `output/python-concepts/` holds exactly `python-concepts-{student-print,student,answer-key,teacher}.pdf`, `syllabus.pdf` and `handouts/`.
   - `output/python-projects/` holds `syllabus.pdf`, `patterns.pdf` and `handouts/`.
   - No `output/book*` folder remains, `output/README.md` matches, and `git status` has no PDFs.
3. `pytest tests/test_book_ids.py` PASS (the E3 grep uses the same rules). `git log --follow` works through a moved file.
4. Rendered-page review: the python-concepts title page and title verso (new subtitle, "(folder python-concepts/)"), and a syllabus heading.
5. Post-execution report: the id mapping, unchanged page counts, and a note that open branches must rebase (the transition map covers `pre-merge-guard` for one release).

## Out of scope

- The `peers` concept-sharing exemption (design 008 D3; plan 092 implements and tests it).

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

### Round 1 — verdicts

- `[sol]` **REJECT:**
  - design D3's split would break prerequisite closure (`deque`, `str-split`, complete search)
  - D1 vs B4 file names conflict, and `publish_output` rejects the new names
  - the guard misses qualified ids, `.gitignore` and `output/README.md`
  - the syllabus-H1 parser and the `theme.tex` title-back are unnamed
- `[fable]` **APPROVE WITH NITS:**
  - the file-name contradiction
  - guard precision (live links to historical design file names; code comments)
  - the H1→subtitle coupling and its order
  - qualified-id regexes and fixtures
  - `publish_output` pattern, `build-book.sh`
  - the `publish_audit` `root/'book1b'` bug
  - id-keyed feature switches become flags
  - `theme.tex`
  - registry test and `number:`
  - teacher-notes and checkpoint heading forms
  - the pre-merge-guard transition
  - paths vs titles
  - test file names
  - the AGENTS.md diff scope
- `[glm]` **APPROVE WITH NITS** (opencode-go/glm-5.3):
  - the file-name contradiction
  - `decisions.md:27` is governance (leave historical)
  - AGENTS.md line 54
  - a case-insensitive guard for `Book1b-`
  - `TODO.md`
  - teacher notes inline per AGENTS dispatch

### Round 1 — fold

- `[FIXED]` all findings above:
  - design D1: file names use the id
  - design D3: each contest book is independently complete, with duplicated concepts and a per-book prereq/coverage check in plan 092
  - Survey corrected
  - `books.yaml` feature flags replace id switches
  - a registry-built qualified-id alternation
  - fixtures and in-test registries migrated
  - the pre-merge-guard transition map
  - H1 parser removed; titles from `books.yaml`
  - `theme.tex` placeholders
  - one output-name helper
  - `publish_output` `<id>-*.pdf`
  - explicit heading forms
  - paths vs titles
  - teacher notes inline
  - AGENTS.md lines 50–54 only; `decisions.md` untouched
  - `TODO.md`
  - a precise guard with a case-insensitive old-name rule, reused by E3
  - E2 exact contents

### Round 2 — verdicts and fold

- `[sol]` **REJECT** (r2): the naming, publication, parser, theme and guard blockers are resolved. Remaining: design D3's concept duplication conflicts with the global concept-uniqueness check.
  - `[FIXED]` Design D3 now defines the sharing rule: books declared `peers` may each introduce a shared id, with identical registry entries and no requiring a peer-only id. Plan 092 implements and tests it; it is listed under Out of scope here.
- `[fable]` **APPROVE WITH NITS** (r2), all round-1 items verified.
  - `[FIXED]` The guard runs red on teacher notes until the orchestrator's inline pass; it must be green at E1.
  - `[FIXED]` Checkpoint H1 form: drop the `Book 2 ` prefix only.
  - `[FIXED]` A `books.yaml` comment says what each flag covers (`patterns` includes coverage-map v2).
  - Noted: E1 relies on `tests/test_books.py` to pin the registry.

## Content Review
_(filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
