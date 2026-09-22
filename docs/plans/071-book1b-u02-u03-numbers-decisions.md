# Plan 071 — Book 1b Units 02 (Numbers & Arithmetic) + 03 (Decisions)

**Origin:** Book 1b buildout (standing directive 2026-09-22, "full book 1b implementation").
**Design:** `docs/designs/005-book1b-concept-first.md` §3 (unit table), §5 (fastforward), §7 (mini-CP form).
**Template:** Unit 01 (`book1b/units/unit-01-output-and-variables/`, plan 070) — clone its shape exactly.

## Scope

Author two adjacent concept-family units, each cloning the U01 template (problem-first lesson;
mini-CP pre-function exercises; per-line-assert solutions mirroring the student form; teacher-notes with
core/extra/Challenge partition; ≥2 Challenge exercises; solution-free student notebooks; no `input()` in
solutions code). Both are pre-function (no `def` until U07). Add each unit's coverage-map entry + syllabus
arc-table row + manifest. Book 1b stays `buildout: true`.

## Coverage-map entries (the contract)

**unit-02-numbers-and-arithmetic** — `lessons: 3`
- introduces: `[int-type, float-type, arithmetic, type-conversion, boolean, comparison]`
- requires: `[print, variable, input, f-string]`
- practices: `[string-literal, naming, comment, error-messages, run-program, string-concat]`

**unit-03-decisions** — `lessons: 3`
- introduces: `[logical-ops, if-statement, elif-else, conditional-nesting]`
- requires: `[boolean, comparison, arithmetic, variable, print]`
- practices: `[int-type, type-conversion, f-string, string-literal, input, naming]`

Closure (strict over `requires`): U02 requires ⊆ U01; U03 requires ⊆ U01∪U02 (`comparison`/`boolean`/
`arithmetic` are U02). No entry practices its own introductions. `prereq-check` (fastforward) validates
`requires` only; `coverage-check` validates the rest.

## Problem backgrounds (mini-CP, simple; design §3)

- **U02 (numbers as math):** even/odd via `n % 2 == 0`, digit extraction (`//`, `%`), sum/average of a
  few given numbers, unit conversion (minutes→h:m), rounding/`//` change-making, compare two numbers →
  a boolean verdict, `int()`/`float()` conversions from given text. Fastforward is available but light.
- **U03 (branching):** classify a given value — leap-year test (`and`/`or`/`not`), triangle type from
  three sides, letter grade from a score, sign of a number, in-range check, smallest-of-three (nested
  `if`), a simple FizzBuzz-for-one-number. Given values → exact printed verdict.

Exercises favor volume (no cap); ≥2 Challenge each; core/extra/Challenge partition documented in
teacher-notes so a lesson still fits 60–90 min. Repair/error exercises (if any) show the literal fix.

## Phases

### Phase A — plan-review gate (4-way). No implementation until consensus.

### Phase B — contracts
`book1b/curriculum/coverage-map.yaml` (append the two entries), `book1b/syllabus.md` (append two
arc-table rows in map order), and a `manifest.yaml` per unit. `python -m tools.cli --book book1b
coverage-check` + `prereq-check` GREEN.

### Phase C — statements (Codex, gpt-5.6-sol): each unit's `lesson.ipynb` + `exercises.ipynb`
Problem-first lesson (opening cell = a real problem, not drill; per-concept worked-example ladders;
a deliberate broken/fixed traceback beat reusing `error-messages`). Exercises: ≥8 each, mini-CP
pre-function form, ≥2 `stretch` Challenge, no solutions/outputs/"Solution" headings, no `input()` in code.

### Phase D — solutions (SEPARATE fresh Codex, gpt-5.6-sol): each unit's `solutions.ipynb`
House form: capture each output line in a named variable, print it, assert it (repair exercises show the
literal fix, assert separately). Mirror every `## Exercise N`. Runs clean; no `input()` in code.

### Phase E — teacher-notes (inline) + verification
`teacher-notes.md` per unit (goals, 60–90 min pacing, core/extra/Challenge partition, common mistakes,
discussion prompts, differentiation). **Verification:** full `TMPDIR=/dev/shm bash scripts/ci-local.sh`
ALL GREEN across the three books; both units' `exec-solutions` clean + asserts pass; exercises
solution-free/output-free; ≥2 stretch each; opening cells are problems. Scope allowlist = this plan +
the two `book1b/units/unit-0{2,3}-*/` trees + `book1b/curriculum/coverage-map.yaml` + `book1b/syllabus.md`.

## Out of scope

- U04–U13, checkpoints, Algorithm Challenge — later plans (072+).
- No tooling changes (plan 070 shipped them); no Book 1/Book 2 changes; no governance-file edits.
- Not an erratum. **Verification phase:** Phase E is the named verification phase (units → required).

## Plan Review

### Round 1 (2026-09-22) — [self] inline; [sol]/[glm]/[fable] dispatched parallel.

#### [self] — **APPROVE.**
Closure verified in listed order: U02 `requires` ⊆ U01 introduces; U03 `requires` (`boolean`/`comparison`/
`arithmetic`/`variable`/`print`) ⊆ U01∪U02. Neither entry practices its own introductions; all practices
are earlier concepts. All 62 catalog concepts stay introduced-once (U02 adds the 6 numbers/compare, U03
the 4 control ids; consistent with design 005 §3 incl. `comparison`→U02). Both units are pre-function
(no `def`) and clone the U01 template (problem-first, mini-CP, house solution form). Phase E is the named
verification phase (units → required). No tooling/governance/Book-1/2 changes. No open blockers.

_(Awaiting [sol] / [glm] (volcengine-plan/glm-5.3) / [fable].)_

## Content Review

_(4-way content-review gate — filled before PR.)_

## Post-Execution Report

_(Filled before shipping.)_
