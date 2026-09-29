# Plan 092 — The ACSL book: foundation, season map, and the Foundations unit

**Goal:** Register *Contest Python: ACSL* (`acsl/`) as a book organized by the ACSL contest season, marked by division.
This plan adds the tooling the season structure needs and ships its first unit, **ACSL Foundations**.
Contests 1–4 follow in plans 093–096; the USACO trim follows in 097 (design 009 §3).

**Spec:** designs 008 and 009. User decisions, 2026-09-28/29:
- "separate the cp book into acsl and usaco"
- "for ACSL, we will cover all levels in one book, but mark concepts by level"
- ACSL prerequisites: "New ACSL foundations unit"
- Mock contests: "Replace and move" (applied in plan 097)
- "organize them by acsl units, so that students can follow the contest schedule in a competition season"

## Survey (2026-09-29)

- **`usaco-bronze` dependencies:** the ACSL-flavoured units (02 Boolean logic, 11 number systems/bitwise, 12 binary trees) need concepts introduced only by USACO units: `input-parse` and `str-split` (U01), `tuple` (U04), `complete-search` (U05), `recursion` (U09). USACO's graphs unit needs `deque` (U10).
  - A straight move therefore breaks prerequisite closure both ways.
  - Design 009 replaces it: ACSL is written fresh by contest, shared ids use `peers`, and USACO is trimmed last (097).
- **ACSL schedule:** from the acsl.org Study Materials, retrieved 2026-09-29; the design 009 D2 table.
  - The 2026–27 contest windows open in Oct, Jan, Feb and Mar (acsl.org Schedule).
  - Junior, Intermediate and Senior each have a 6-question short-answer test plus one programming problem; Elementary has a 6-question non-programming test on one category; Classroom has 10 non-programming questions.
- **Registry:**
  - `tuple` (feature, data-structures), `str-split` (feature, io), `input-parse` (technique, io) and `complete-search` (technique, search) exist in `usaco-bronze/curriculum/concepts.yaml`.
  - `global_concept_uniqueness_findings` allows a shared id only for variant pairs.

## Phase A — Design (inline)

`docs/designs/009-acsl-book.md` (this branch). Design 008 gets a one-line pointer: "D3–D4 refined by design 009".

## Phase B — ACSL Foundations unit: lesson and statements (Opus subagent)

Unit `acsl/units/unit-00-acsl-foundations/`. The manifest's `acsl:` block is `{contest: 0, category: Foundations, divisions: [junior, intermediate, senior]}`; Elementary has no programming, so Foundations starts at Junior.

- **Hook first:** a real ACSL-style programming problem in the opening cell. For example, read a line of numbers and report something about it. The unit then builds the skills to solve it.
- **Lessons (3):**
  1. **How ACSL works:**
     - the season and the divisions
     - short-answer vs programming, exact answers
     - reading a contest problem statement
     - running a `.py` solver with input
  2. **Reading contest input:**
     - `input()` for one line and several lines
     - `split()`
     - `int`/`float` conversion
     - fixed-count and "until 0" reading (a sentinel from the Python books)
  3. **Tuples and complete search:**
     - pairs and triples as tuples
     - unpacking
     - trying every candidate with nested loops
     - counting and choosing the best
- **Exercises:** at least 12, with the `stretch` Challenge tier, in two kinds (design 009 D4):
  - **Programming:** stdin `.py` solvers under the judge contract. Each has a sample fixture plus at least one edge fixture.
  - **Short-answer:** a question with one exact answer.
  - Every exercise carries exactly one division tag (`acsl-junior` / `acsl-intermediate` / `acsl-senior`).
- **Concepts:**
  - introduces (shared with `usaco-bronze` via `peers`, with identical registry entries): `input-parse`, `str-split`, `tuple`, `complete-search`
  - requires: Python-book concepts only (`python-projects` ids)
  - no USACO-only ids
- **Content is ACSL-flavoured and original.** No USACO notebook is copied.
- **Teacher notes** (inline, active session): goals, pacing, how to use the book through a season (the contest windows), the division path, common mistakes.

## Phase C — Solutions (Opus subagent, separate fresh session)

- **Programming items:** each gets a solver `assets/exN.py` plus fixtures under `assets/exN/`, and passes `judge-check`.
- **Short-answer items:** in `solutions.ipynb`, a cell computes the answer with Python and `assert`s the exact printed answer.
- **Lesson companion assets** as the judge contract requires.

## Phase D — Tooling and registration (Opus subagent)

- **D1 `peers`:**
  - `books.yaml` gets `peers:` (symmetric, validated).
  - `global_concept_uniqueness_findings` lets peers each introduce a shared id when the `concepts.yaml` entries (name, category, `kind`, including absence) are identical. It fails on drift, and fails if a book `requires` an id that only its peer introduces.
  - Tests cover all of this.
- **D2 Register `acsl`:**
  - `books.yaml`: id `acsl`, title "Contest Python: ACSL", subtitle "From Elementary to Senior, one contest at a time", `depends_on: [python-projects]`, `peers: [usaco-bronze]`, `judge: true`. `usaco-bronze` gets `peers: [acsl]`.
  - Folder skeleton:
    - `acsl/syllabus.md`: the whole season map. Contest 0–4 parts, one row per planned unit, with its category and divisions; units after Foundations marked *planned (plan 09N)*. It also includes a "Following the season" section with the contest windows.
    - `acsl/curriculum/concepts.yaml`, `coverage-map.yaml`, `season.yaml` (D2 table, with source URL and retrieval date).
    - `acsl/docs/README.md`
    - `acsl/checkpoints/` and `acsl/projects/` as the tools require (empty until 093).
  - The `test_book_ids` guard and `tests/test_books.py` learn `acsl`.
- **D3 `acsl-check`**, registered in `tools/checks.py` and wired into `ci-local` for books with an `acsl` season file (a registry flag `acsl: true`):
  - manifest `acsl:` block valid against `season.yaml`
  - unit order follows the season
  - exactly one division tag per exercise, never below the unit's lowest division
  - a contest part has its practice checkpoint once any of its units ship
  - Tests for each failure.
- **D4 Short-answer items:**
  - `structure-check` / `cell-lint` / `judge-check` accept an exercise with no stdin solver when its statement is marked short-answer (a `short-answer` cell tag) and its solution has an asserting answer cell.
  - `exec-solutions` runs those cells.
  - Tests.
- **D5 CI:** `ci-local` runs every per-book check for `acsl` (registry-driven); `pre-merge-guard` learns the new root.

## Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN, including for `acsl`: structure, hygiene, noexec, cell-lint, exec-solutions, exec-lessons, manifest, prereq, coverage, concept-scan, stretch, judge-check, source-policy and `acsl-check`.
2. `prereq-check` and `coverage-check` pass for `acsl` and for `usaco-bronze` separately; the global concept check passes with the four shared ids.
3. Mutation tests fail as designed:
   - a division tag below the unit's minimum
   - a missing tag
   - an unknown category
   - out-of-season order
   - peer registry drift
   - requiring a peer-only id
4. Blind solve in the content gate: reviewers solve Foundations exercises from the statements alone.
5. Post-execution report.

## Out of scope

- Contests 1–4 units and practice checkpoints (093–096).
- Any `usaco-bronze` change, including the trim and mock-contest replace-and-move (097).
- ACSL publication (PDF editions).
- Level badges in print (they come with publication).

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- The verification phase is named. Scope is one unit plus infrastructure, and project-first holds (hook cell first).
- Watch items:
  - Shared concept entries must be byte-identical to USACO's.
  - `acsl-check` must not block `usaco-bronze`.
  - The short-answer genre must still be machine-verified (no free-text answers without an assert).
  - The season file records its source and date, because ACSL lists change yearly.
- `[glm]` skipped: user decision 2026-09-28, "Skip GLM until further notice".

## Content Review
_(filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
