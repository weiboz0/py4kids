# Plan 018 — Book 2 Unit 01 "Reading the Input" + practice-completeness fix

**Goal:** Ship Book-2 `unit-01-reading-the-input` — the first content unit, which establishes the
binding `solve(data:str)->str` judge contract and the Book-2 problem-set pattern — and first land the
practice-completeness deferral fix so authoring a unit does not red the whole-book coverage-check.

**Architecture:** Phase A: refine `practice_findings` to gate on the CAPSTONE being authored, not any
entry (carry-forward from plan 017). Phase B: author U01 (lesson/exercises/solutions/teacher-notes/
manifest) on the `solve(data)` contract; wire U01's per-entry checks into ci-local. Phase C: verify.

**Spec:** `docs/designs/001-book2-algorithms.md` (§3 solve contract, §4 unit anatomy, §7 U01);
`book2/syllabus.md`; `book2/curriculum/coverage-map.yaml` (the U01 entry); plan 017 (the cross-book
tooling + two-tier registry + the two content-plan carry-forwards); Book-1 plan 004 (first-units
precedent). Book-1 content conventions transfer (5-heading unit teacher-notes, ≥6 exercises with ≥2
`stretch`, manifest map-equal, no executed outputs in student notebooks).

## Global Constraints

- **Practice-completeness fix (Phase A, tooling — carry-forward from plan 017 gate):**
  `practice_findings` currently enforces "every concept practiced before the capstone" whenever ANY
  entry dir exists (`has_authored_entry = any(...)`). That reds coverage-check the moment U01 lands
  (only U01's concepts are authored). Refine it to enforce only when the **capstone entry is
  authored** (its dir exists) — practice-completeness is a whole-arc property, meaningful only when
  the arc is complete. Book 1 UNCHANGED (its capstone `project-02-grand-adventure` dir exists →
  still enforced → still PASS). Book 2 defers until its final plan (the capstone lands). Add a test:
  a dependent-book fixture with a unit authored but NO capstone dir → no practice-completeness
  finding; with the capstone dir authored + incomplete pre-capstone practices → the finding fires.
  Book-1 regression byte-identical.
- **The `solve(data:str)->str` contract (binding, design §3):** every reference solution in
  `solutions.ipynb` is a pure function `solve(data: str) -> str` — parsing inside, NO `input()` in any
  executable cell. Verified by inline asserts token-compared: `assert solve(SAMPLE_IN).split() ==
  EXPECTED.split()`, against the sample **plus ≥1 crafted edge/larger case per problem** (non-vacuous;
  a wrong solution fails — content gate mutation-checks). The real-submission wrapper
  (`import sys; print(solve(sys.stdin.read()))`) appears ONLY in a `no-exec`-tagged cell or teacher
  note, never CI-run. Deterministic (no `random`).
- **Unit anatomy (design §4; Book-1 conventions):** `lesson.ipynb` opens on the motivating problem
  (too-slow/naive → the technique), teaches, works one problem end-to-end; `exercises.ipynb` = a
  laddered PROBLEM SET (≥8 problems, each: statement + constraints + sample input/output; ≥2
  `stretch`-tagged as "Challenge"); `solutions.ipynb` = reference `solve` functions + the non-vacuous
  asserts (mirror `## Exercise N` / `## Problem N` headings, unique cell ids, no executed outputs);
  `teacher-notes.md` = FIVE `##` headings (`## Goals`, `## Pacing`, `## Common mistakes`,
  `## Discussion prompts`, `## Differentiation`) and states each problem's intended Big-O; student
  notebooks carry NO solutions and NO executed outputs.
- **U01 concept scope (closure + two-tier):** U01 `introduces` `input-parse`, `str-split`, `grid-2d`
  (per the map; `input-parse`/`grid-2d` are TECHNIQUES, `str-split` a FEATURE). It may USE any Book-1
  baseline concept (for-loop, list-append, type-conversion, int-type, string-methods, def-function,
  etc.) — all in the baseline. It may NOT use any not-yet-introduced Book-2 concept (no sets, tuples,
  sorted-key, recursion, binary-search, …). `concept-scan --book book2` over U01 must be clean: the
  only FEATURE it introduces/uses is `str-split` (`.split`), which is in U01's union; Book-1 features
  are baseline-allowed. Manifest map-equal; `practices` amended from the actual content
  (`practices ∩ introduces` empty — so U01 does NOT practice input-parse/str-split/grid-2d; it
  practices the Book-1 concepts it exercises).
- **CI-safety:** `solutions.ipynb` executes headless + input-free (the CI executor runs it; solve()
  functions + asserts only). Any sample input is an in-cell string literal or a committed small
  fixture — NO reading real stdin. No scratch files needed (input is a string arg).
- **ci-local wiring:** with U01 authored, ADD Book-2 per-entry checks for the content that now
  exists — `manifest-check`/`structure-check`/`hygiene-check`/`cell-lint`/`exec-solutions`/
  `noexec-check`/`stretch-check` for `--book book2` (these iterate only existing entry dirs, so they
  cover U01 and are inert for unauthored entries). Keep the map-level checks. (Confirm each per-entry
  check tolerates a partially-authored book — if any require ALL map entries to have dirs, scope
  them or defer, as plan 017 did for the map-level split.) **VERIFIED (2026-09-07):** all seven
  per-entry checks already PASS on the content-less Book 2 — they iterate EXISTING dirs, so a
  partially-authored book is fine; the "requires all map entries to have dirs" risk does not
  materialize.
- Process (standing): no commits while a `[sol]` review is in flight; branch before drafting; codex
  prompts name the in-process execution fallback and avoid bare CLI-flag-like tokens; SEPARATE codex
  sessions for exercise STATEMENTS vs blind SOLUTIONS.

## Out of scope

U01 only (U02–U05 + CP1 are later Term-1 plans). Out of scope: any other Book-2 unit content; the
capstone; a shared "sample judge" tools/ helper (inline asserts suffice for now); the scanner-profile
authoring rules for U04 set-methods / U10 `.pop` (those bind their own unit plans); PDF handout tuning.

## Phases

Dispatch per AGENTS.md: the practice-completeness fix via codex (tooling); U01 exercise/lesson
STATEMENTS via codex; the blind SOLUTIONS via a SEPARATE codex session; teacher notes inline;
manifest + ci-local wiring inline.

### Phase A — practice-completeness capstone-gating fix (codex)

1. In `tools/curriculum.py` `practice_findings`, replace `has_authored_entry = any(entry dir exists)`
   with `capstone_authored = (capstone entry's dir exists)`; enforce the pre-capstone-coverage rule
   only when `capstone_authored`.
2. Tests: dependent-book fixture with a unit dir but no capstone dir → NO practice finding; with the
   capstone dir + incomplete pre-capstone practices → the finding fires; Book-1 unchanged.
- Acceptance (A): `ruff` clean; `pytest` green (incl. new tests); Book-1 prereq/coverage/concept-scan
  byte-identical; `--book book2 coverage-check` still PASS (no content yet → deferred).

### Phase B — U01 content (codex statements + blind solutions; inline manifest + wiring)

Blueprint (motivating problem → technique → laddered problem set; the `solve(data)` contract):
- **Motivating problem (lesson):** "read `N`, then `N` integers; print their sum and max" from the
  input string — naive vs clean parsing; introduce `solve(data)->str`.
- **Techniques taught:** `data.split()` / `line.split()`, `int(...)` conversion, reading `N` then `N`
  values, reading a grid (`R C` then `R` rows) into a list-of-lists (`grid-2d`); building the output
  string; the submission wrapper shown in a `no-exec` cell.
- **Problem set (exercises, ≥8, laddered, ≥2 `stretch`):** sum/stats of N numbers; count values above
  a threshold; per-line sums; find a value's position; row/column sums of a grid; a small
  transform-and-print; `stretch`: a two-part parse (a header line + a variable body), a grid corner/
  border task.
- **Solutions:** each a `solve(data:str)->str`; asserts against the given sample PLUS a crafted edge
  case (empty/N=0, single element, all-equal, a 1×K or K×1 grid) — non-vacuous; token-compared.
- **manifest.yaml** map-equal: `introduces: [input-parse, str-split, grid-2d]`; `requires` = the
  Book-1 baseline concepts U01 leans on; `practices` = the Book-1 concepts U01 actually exercises
  (scanner-derived; `practices ∩ introduces` empty). Amend the map entry's `practices` to match.
- **teacher-notes.md**: five headings; each problem's intended Big-O; the `solve` contract rationale;
  common parse mistakes (off-by-one on N, forgetting `int()`, trailing whitespace, `.split()` on an
  empty line).
- **ci-local**: add the Book-2 per-entry checks (they now have U01 to check).

### Phase C — Verification (NAMED, mandatory)

Mechanical: `ruff` clean; `pytest` green; `--book book2` `manifest-check`/`structure-check`/
`hygiene-check`/`cell-lint`/`noexec-check`/`stretch-check`/`exec-solutions`/`prereq-check`/
`coverage-check`/`concept-scan` all PASS (U01 content clean; `concept-scan` sees only `str-split` +
baseline features; no not-yet-taught Book-2 feature); solutions execute headless input-free with
non-vacuous sample+edge asserts; manifest map-equal; Book-1 byte-identical; full `ci-local.sh` ALL
GREEN (both books). Reviewer duties (both gates): blind-solve the problem set from the statements;
confirm every `solve` is a pure `str->str` with NO `input()`, asserts sample+edge non-vacuous
(mutation-test); closure (only U01 concepts + Book-1 baseline — NO sets/tuples/sorted-key/recursion/
etc.); the practice-completeness fix is correct + Book-1-safe; teacher-notes state each Big-O.

**Acceptance criteria:** practice-completeness fix shipped + tested + Book-1-safe; U01 complete
(lesson/exercises/solutions/teacher-notes/manifest); `solve(data)` contract honored; ci-local ALL
GREEN with Book-2 per-entry checks wired; plan-review + content-review 4-way consensus.

---

## Plan Review

### Review 1 — [self] (2026-09-07)
APPROVE. Plan opens with the plan-017 carry-forward (practice-completeness gated on capstone-authored,
not any-authored) — the correct semantics (whole-arc property, checked when the arc is complete),
Book-1-safe (its capstone dir exists → unchanged), and it unblocks incremental unit authoring. U01
establishes the binding `solve(data)->str` contract + the Book-2 problem-set pattern that every later
unit inherits, with non-vacuous sample+edge asserts (the Book-1 vacuous-assert discipline carried
over). Closure is tight: U01 introduces `input-parse`/`str-split`/`grid-2d` and may lean only on the
Book-1 baseline — `concept-scan` will enforce `str-split` (the one new feature) and the two-tier
model keeps `input-parse`/`grid-2d` reviewer-enforced. Phase C is the named verification phase; the
per-entry ci-local wiring is scoped to now-authored content. Risk to watch at the gate: a per-entry
check that assumes every map entry has a dir (would fail on the still-unauthored U02–capstone) — the
plan flags confirming each tolerates a partially-authored book.
