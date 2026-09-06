# Plan 003 — Verification Tooling Implementation Plan

**Goal:** Replace every `SKIP (plan 003)` in `scripts/ci-local.sh` with a real check: a `tools/` package + `py4kids-tools` CLI providing notebook execution (solutions AND lessons), student hygiene, notebook-cell lint, headless turtle verification, manifest/curriculum checks, and a PDF handout build.

**Architecture:** `tools/` grows focused modules (`notebooks.py`, `curriculum.py`, `fake_turtle.py`, `checks/`, `cli.py`) exposing pure functions; `tests/test_book1_units.py` and `tests/test_book1_curriculum.py` are refactored into thin wrappers importing the same functions (single source of truth; pytest keeps covering them); `cli.py` exposes each check as `py4kids-tools --book <id> <check>` for ci-local. PDF build uses the system toolchain verified present (nbconvert→xelatex for notebooks, pandoc for markdown) — no new Python dependencies.

**Spec:** `docs/designs/000-project-design.md` §4; plan 004 post-execution follow-ups; plan 002 follow-up (checks promoted from pytest).

## Global Constraints

- This plan takes the RESERVED number 003 (see plan 004 Global Constraints — the ci-local SKIP markers and TODO have always pointed here).
- Behavior parity is law: the promoted checks must enforce EXACTLY the rules the interim tests enforce today (patterns per-line `re.MULTILINE`; seed-ordering; cumulative closure; scaffolding exemption; the five teacher-notes headings; `## Exercise N` floors) — any tightening or loosening is a gate finding.
- Existing rules stay recorded where they are (plan 004 Global Constraints); tools docstrings reference them rather than restating divergent copies.
- Notebook-cell lint is critical-only: ruff `--select E9,F63,F7,F82` (syntax errors, undefined names) on extracted code cells — kid-facing style is NOT policed.
- Runtime budget: full `ci-local.sh` stays under 3 minutes on this machine with the three existing units.
- Every commit appends the two mandated trailer lines (exact text in plan 002 §Global Constraints).

## Out of scope

This is a tooling-only plan: it ships no units, projects, or checkpoints, so the named-verification-phase rule for content plans does not apply (exemption per design §5).
Verification here is: the tools' own pytest suite (including negative fixtures), behavior-parity green runs on the shipped units, and a fully SKIP-free `ci-local.sh` ALL GREEN.
Also out of scope: checkpoint/project check variants (no such content exists yet — the unit checks are written so plan 005+ extends kinds, not rewrites), overlap scan, Book 2 anything, solution-notebook PDF rendering (teacher handouts are the exercises).

## Phases

Dispatch: tools/scripts implementation via `codex:codex-rescue` (GPT-5.6-sol, write-capable) per AGENTS.md; plan/orchestration/review handling inline; trivial fixes inline.

### Phase A — package layout, CLI skeleton, fixtures (TDD)

**Files:** `tools/{__init__.py,cli.py,notebooks.py,curriculum.py,fake_turtle.py}`, `tools/checks/__init__.py`, `tests/test_tools.py`, `tests/fixtures/broken-unit/` (a deliberately invalid unit: executed output in exercises, missing stretch tag, solutions missing a heading + calling input(), lesson GUI cell untagged, manifest key drift, a non-compiling asset, a turtle script that doesn't close its turn).
- `pyproject.toml` gains `[project.scripts] py4kids-tools = "tools.cli:main"`.
- CLI contract: `py4kids-tools --book book1 <check>` where `<check>` ∈
  `manifest-check | hygiene-check | structure-check | noexec-check | exec-solutions |
  exec-lessons | cell-lint | turtle-check | prereq-check | coverage-check | stretch-check`;
  exit 0 = pass, 1 = findings (printed one per line as `FAIL: <unit>: <detail>`), 2 = usage.
  `--unit <id>` optionally narrows unit-scoped checks.
- TDD: `tests/test_tools.py` asserts each check passes on the real `book1` AND fails with
  the expected `FAIL:` lines on the broken fixture (negative coverage for every check).

### Phase B — notebook checks promoted into tools

`tools/notebooks.py` re-homes the logic of `tests/test_book1_units.py` as pure functions
returning finding lists (empty = pass): layout+assets(py_compile), manifest/map agreement,
student hygiene, exercise structure, solutions structure + pattern bans + seed ordering,
lesson no-exec tagging, teacher-notes headings. `tests/test_book1_units.py` becomes thin
wrappers asserting `findings == []` per unit (same pytest ids, same skip guard, same
all-three-units check).
New capabilities beyond parity:
1. **exec-lessons**: execute `lesson.ipynb` headless via nbclient AFTER dropping cells
   tagged `no-exec` (design §4's lesson-execution promise; plan 004 reviewer duty 7
   mechanized). Convention clarification this implies (binding, consistent with plan 004's
   intent): untagged lesson cells must not depend on state created by `no-exec` cells —
   if drop-and-run breaks an untagged cell, that is a content defect in the lesson, not a
   tooling false positive. The three shipped lessons must pass; if one does not, fix the
   lesson (smallest edit preserving pedagogy) and ledger it.
2. **cell-lint**: extract code cells (skipping `no-exec` cells and `%`/`!` magic lines)
   from every notebook into per-notebook temp files; run ruff `--select E9,F63,F7,F82`
   `--no-cache`; findings map back to notebook + cell index.
3. **exec-solutions**: the nbclient execution moves here from the test file (tests call it).

### Phase C — headless turtle verification

`tools/fake_turtle.py`: a recording stub implementing the turtle API surface the assets
use (`forward`, `backward`, `left`, `right`, `penup`, `pendown`, `pensize`, `pencolor`,
`color`, `speed`, `bgcolor`, `Screen`/`done`/`exitonclick` as no-ops, `Turtle` class) —
recording (moves, total_turn).
`turtle-check`: for each `assets/*.py`, inject the stub as `sys.modules["turtle"]` in a
fresh subprocess, execute the script, assert: completes within 20s, ≥1 drawing move,
< 10000 moves, and |total_turn| is a multiple of 360° within 1e-6 (closure law — squares
360, stars 720, rosettes 360; a script failing this is drawing garbage).
The broken fixture's non-closing script must FAIL this check.

### Phase D — curriculum checks promoted into tools

`tools/curriculum.py` re-homes `tests/test_book1_curriculum.py` logic (registry schema,
map schema/ids/budget, referenced-concepts-exist, introduced-exactly-once, cumulative
prereq closure over requires ∪ practices, pre-capstone practice coverage, checkpoint
rules, syllabus table match) as functions; the test file becomes thin wrappers.
CLI: `prereq-check`, `coverage-check` (map-level), `stretch-check` (unit-level ≥2
stretch tags), `manifest-check` (unit manifests vs map).

### Phase E — PDF build + ci-local rewrite

1. `scripts/build-pdf.sh --book book1`: for each unit, nbconvert `exercises.ipynb`
   `--to pdf` (xelatex) into `book1/build/handouts/<unit>.pdf`; `pandoc book1/syllabus.md
   -o book1/build/syllabus.pdf`. Fails on any missing/empty output. `book1/build/` stays
   gitignored (add `build/` already covered by root .gitignore — verify).
2. `scripts/ci-local.sh` rewrite — six steps, ZERO SKIP lines:
   1/6 registry + lint (unchanged) · 2/6 pytest (unchanged) ·
   3/6 notebooks: `exec-solutions`, `exec-lessons`, `hygiene-check`, `cell-lint` ·
   4/6 curriculum: `manifest-check`, `prereq-check`, `coverage-check`, `stretch-check`,
   `structure-check`, `noexec-check`, `turtle-check` ·
   5/6 `build-pdf.sh --book book1` · 6/6 pre-merge guard (unchanged).

### Phase F — Verification (tooling-only; exemption above)

1. `uv run pytest -q` — full suite green (tools tests + refactored wrappers + books).
2. Negative coverage: every check fails on `tests/fixtures/broken-unit` with its expected
   `FAIL:` line (asserted by `tests/test_tools.py`).
3. Behavior parity: refactored unit/curriculum wrappers pass on the shipped three units
   with NO check regressions (same pass set as pre-refactor).
4. `bash scripts/ci-local.sh` — ALL GREEN, zero `SKIP` occurrences
   (`! grep -q "SKIP (plan" scripts/ci-local.sh` and the run output), under 3 minutes.
5. PDFs exist, non-empty, open-able (`pdfinfo` or file-size + `%PDF` magic check).

**Acceptance criteria:** all six ci-local steps real and green; parity proven; negative
fixtures covered; runtime < 3 min; `tests/fixtures/` excluded from unit discovery
(the broken unit must not fail the real suite — fixture path lives outside `book1/`).

---

## Plan Review

(4-way gate verdicts land here.)

## Content Review

(pre-PR gate findings land here.)

## Post-Execution Report

(written before shipping.)
