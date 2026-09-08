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
  (`import sys; print(solve(sys.stdin.read()))`) appears ONLY in a `no-exec`-tagged cell of
  `lesson.ipynb` or in `teacher-notes.md` markdown — **NEVER in `solutions.ipynb`** (fable-5/glm-5):
  `exec-solutions` runs ALL solution cells regardless of the `no-exec` tag (that tag is stripped only
  for `lesson.ipynb`), so a wrapper there would `sys.stdin.read()` → hang-to-timeout. Deterministic:
  NO `random` anywhere (the exec policy would tolerate a seeded `random`, so "no random" is
  reviewer/content-gate-enforced — mutation-checked at the gate) — glm-6c.
- **Untaught methods (scanner-enforced — fable-6/glm-6b):** the only string/list method taught by U01
  is `.split` (via `str-split`); the Book-2 scanner profile adds only `split` (+ Book-1's taught
  methods). So U01 content must NOT use `.join`, `.splitlines`, `.index`, `.count`, `.find`, etc. —
  build output with concatenation/f-strings/loops, and find a position with a manual loop. (This is
  good pedagogy and the scanner enforces it — the same guard that nearly caught `.index` in Book-1
  unit-06.) The codex authoring prompts MUST state this.
- **Unit anatomy (design §4; Book-1 conventions):** `lesson.ipynb` opens on the motivating problem
  (too-slow/naive → the technique), teaches, works one problem end-to-end; `exercises.ipynb` = a
  laddered PROBLEM SET (≥8 problems, each: statement + constraints + sample input/output; ≥2
  `stretch`-tagged as "Challenge"); `solutions.ipynb` = reference `solve` functions + the non-vacuous
  asserts; **headings are `## Exercise N` in BOTH `exercises.ipynb` and `solutions.ipynb`** —
  `structure-check`/`stretch-check` count the `^## Exercise \d+` regex, so framing items as "problems"
  in the PROSE is fine but the HEADINGS stay `## Exercise N` (`## Problem N` is reserved for
  checkpoint/mock-contest files) — glm-4. Unique cell ids, no executed outputs; `teacher-notes.md` =
  FIVE `##` headings (`## Goals`, `## Pacing`, `## Common mistakes`, `## Discussion prompts`,
  `## Differentiation`) and states each exercise's intended Big-O; student notebooks carry NO
  solutions and NO executed outputs. (NOTE: design-001 §4 says "six headings incl. `## Rubric`" for
  units — that is a design-doc slip; the tooling + Book-1 convention give UNITS five headings
  (`## Rubric` is projects-only, `## Grading` checkpoints-only). The plan follows the tooling;
  design-001 §4 gets an errata note — fable-7/glm-observation.)
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
  **`exec-lessons`** (fable-4/glm-5 — else U01's `lesson.ipynb` is never EXECUTED, only regex-linted,
  and a runtime error or the `sys.stdin.read()` wrapper would slip CI; the wrapper cell MUST be
  `no-exec`-tagged so `exec-lessons` strips it rather than hanging)/`noexec-check`/`stretch-check` for
  `--book book2` (these iterate only existing entry dirs, so they
  cover U01 and are inert for unauthored entries). Keep the map-level checks. (Confirm each per-entry
  check tolerates a partially-authored book — if any require ALL map entries to have dirs, scope
  them or defer, as plan 017 did for the map-level split.) **VERIFIED (2026-09-07):** all eight
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
   only when `capstone_authored`. **Guard `capstone_id is None`** (a finale-less map) →
   `capstone_authored = False` (do NOT dereference `book_dir/"projects"/None`) — glm-3/fable-2. Leave
   the per-entry overlap/duplicate checks (`curriculum.py:250-262`) UNCONDITIONAL (map-level
   discipline, not dir-gated) — the fix touches ONLY the `:280` pre-capstone rule (glm-1).
2. **UPDATE the two EXISTING tests that encode the OLD gating (glm-2 — else pytest reds on the first
   run):** `test_practice_completeness_reactivates_when_content_exists` and
   `test_dependency_practices_do_not_expand_own_completeness_set` currently author only a unit dir and
   assert the finding fires; under capstone-gating that finding no longer fires. Re-point them to also
   author the capstone fixture dir (`<book>/projects/project-03-fixture` or the fixture's capstone id)
   so they keep asserting the finding.
3. ADD tests: a dependent-book fixture with a unit dir but NO capstone dir → NO practice finding;
   with the capstone dir + incomplete pre-capstone practices → the finding fires; a finale-less map →
   no crash (capstone_authored False); Book-1 unchanged.
- Acceptance (A): `ruff` clean; `pytest` green (incl. updated + new tests); **Book-1 byte-identical
  by the named procedure (sol-1):** capture `--book book1 prereq-check`/`coverage-check`/`concept-scan`
  stdout+exit BEFORE the change (or from `main`) and AFTER, and diff them equal; `--book book2
  coverage-check` still PASS (no content yet → deferred).

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
  Book-1 baseline concepts U01 GENUINELY uses (scanner/content-derived) — **TRIM `file-read` and
  `with-statement`** from the current map entry (glm-6a: pure `solve(data)` problems read a string
  arg, never files); keep e.g. `for-loop`/`string-methods`/`type-conversion`/`int-type`/`list-literal`/
  `list-append`/`def-function`/`parameters`/`return-value`/`print`. `practices` = the Book-1 concepts
  U01 actually exercises (scanner-derived; `practices ∩ introduces` empty, so NOT input-parse/
  str-split/grid-2d). Amend BOTH the map entry (`requires` trim + `practices`) AND the manifest to
  match (map == manifest).
- **teacher-notes.md**: five headings; each problem's intended Big-O; the `solve` contract rationale;
  common parse mistakes (off-by-one on N, forgetting `int()`, trailing whitespace, `.split()` on an
  empty line).
- **ci-local**: add the Book-2 per-entry checks (they now have U01 to check).

### Phase C — Verification (NAMED, mandatory)

Mechanical: `ruff` clean; `pytest` green; `--book book2` `manifest-check`/`structure-check`/
`hygiene-check`/`cell-lint`/`noexec-check`/`stretch-check`/`exec-solutions`/`exec-lessons`/
`prereq-check`/`coverage-check`/`concept-scan` all PASS (U01 content clean; `concept-scan` sees only `str-split` +
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

### Reviews 2–3 — [fable] / [glm] (2026-09-07) → APPROVE WITH NITS, reconciled
Both verified the Phase-A fix correct + Book-1-safe against `curriculum.py:247-282`, the solve
contract airtight (CI bans `input()` in solutions), closure tight, and the "per-entry checks tolerate
a partial book" claim EMPIRICALLY true (all eight pass on content-less Book 2). NITS, all folded in:
- **[FIXED] (glm-2, critical) two EXISTING tests encode the OLD gating** → Phase A.2 re-points them
  to author the capstone fixture dir (else pytest reds on the first Phase-A run).
- **[FIXED] (glm-4, critical) `## Exercise N` headings** → `structure`/`stretch-check` count
  `^## Exercise \d+`; exercises keep `## Exercise N` headings (problems framing in prose only).
- **[FIXED] (fable-2/glm-3) `capstone_id is None` guard** → `capstone_authored=False`.
- **[FIXED] (fable-4/glm-5) add `exec-lessons`** to the wiring; wrapper cell `no-exec`-tagged.
- **[FIXED] (fable-5/glm-5) wrapper only in lesson `no-exec` / teacher-notes**, never `solutions.ipynb`.
- **[FIXED] (fable-6/glm-6b) untaught methods** (`.join`/`.splitlines`/`.index`/`.count`) — authoring
  uses loops/concat only.
- **[FIXED] (glm-6a) trim U01 `requires`** (`file-read`/`with-statement`) to genuinely-used.
- **[FIXED] (glm-6c) no random** — reviewer/content-gate mutation-checked.
- **[FIXED] (fable-7/glm) design-001 §4 heading slip** — units are 5 headings, not 6; errata-note it.

### Carry-forwards (DEFERRED — recorded, NOT plan-018's to fix; distinct from any `[OPEN]` gate item)
- **[DEFERRED → Term-4/capstone plan] `two-pointers`@U14 has no pre-capstone practice home
  (fable-3, corrected per sol-3):** `two-pointers` is introduced by U14, the LAST pre-capstone entry;
  since no entry may practice its own introductions nor a not-yet-introduced concept, NO pre-capstone
  entry can legally practice `two-pointers` → when the capstone dir lands, `practice_findings` fires
  "only the capstone practices: [two-pointers, …]" unavoidably. (Correction: U13's graph concepts CAN
  be practiced by U14, which comes after U13 — only `two-pointers`, U14's own introduction, is
  strictly homeless.) Book 1 escaped this because checkpoint-04 sat between its last unit and the
  capstone. FIX in the Term-4 plan: add a 4th mock-contest checkpoint AFTER U14 (before the capstone)
  that practices U14's `two-pointers` (and can double as U13/U14 review), or otherwise restructure.
  (Phase-A semantics stay correct — "must fire at the end" is by design.)
- **[DEFERRED → design maintenance] design-001 §4** says units carry six teacher-notes headings incl.
  `## Rubric`; tooling + convention give units FIVE. Errata note (governance-light doc edit).

### Reconciliation (2026-09-07) — sol re-dispatched on round-2
fable + glm APPROVE WITH NITS (no blockers); all nits folded above. The round-1 sol review HUNG (a
known codex-sol failure mode — its subagent stalled ~33 min; two ORPHANED codex tasks from earlier
sessions were also cleaned up); stopped it and re-dispatched a FRESH sol on the reconciled plan for
round-2. Round-2 to all three on the revised HEAD.

**Round-2: CONSENSUS REACHED — 4-way, no open blockers.** [self] APPROVE · [fable] APPROVE (traced
the re-pointed tests stay non-vacuous) · [glm] APPROVE · [sol] APPROVE WITH NITS. sol's three nits,
all folded: (1) named the Book-1 byte-identical capture-and-compare procedure in Phase-A acceptance;
(2) added `exec-lessons` to the Phase-C command list + fixed the seven→EIGHT per-entry count; (3)
corrected the U13/U14 carry-forward (U14 CAN practice U13's concepts — only `two-pointers` is
strictly homeless). Carry-forwards retagged `[DEFERRED]` (glm) so they don't read as `[OPEN]` gate
blockers. Plan-review gate CLOSED. Proceeding to implementation (Phase A).