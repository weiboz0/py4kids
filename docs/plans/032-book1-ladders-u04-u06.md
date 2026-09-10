# Plan 032 — Book 1 Worked-Example Ladders: U04 + U06 (rollout batch 1)

**Goal:** Apply the proven worked-example-ladder standard (plan 031) to U04 (Quiz Show) and U06 (Secret
Codes), so each newly-introduced concept gets a graduated ladder instead of a single example.

**Architecture:** Identical approach to the plan-031 pilot (merged, PR #32): each introduced concept becomes a
minimal → one-step-up → realistic ladder with a one-line `**Notice:**` per rung; completeness + gradual
pacing (exactly one increment per rung) is the bar; rung count follows difficulty; reused concepts get a
one-line recap. Lesson-only change; concepts/exercises/solutions/checkpoints unchanged; `lessons` counts are
advisory (book1 budget ceiling already `[28, 44]`). The ladder standard is defined in
`docs/plans/031-book1-worked-examples.md` ("## The worked-example ladder standard") — this plan applies it.

**Tech stack:** Jupyter lesson notebooks; `tools/`; `scripts/ci-local.sh`.

**Spec:** `docs/designs/000-project-design.md` + the plan-031 standard.

## Global Constraints (inherited from plan 031; the closure specifics that matter here)

- **Closure is law (reviewer-enforced; concept-scan is unit-level).** A rung uses only concepts taught by its
  point in the unit's lesson ORDER. Per-unit specifics:
  - **U04 Quiz Show** introduces `accumulator, logical-ops, conditional-nesting, break-statement`; its concept
    union is `if-statement, elif-else, while-loop, comparison, input, f-string, arithmetic, int-type, variable`
    (requires) + `boolean, type-conversion, loop-counter, error-messages, string-literal` (practices).
    **`accumulator` IS introduced here**, so counting loops are finally LEGAL in U04 (contrast to U02's
    counter-free loops). **CRITICAL closure fact: `for-loop` and `range-function` are NOT in U04's union** (and
    are AST-detected by concept-scan) — so **U04 loop rungs must be `while`-based with a counter**
    (`questions_asked = questions_asked + 1`), NEVER `for i in range(...)`. Also NO `string-slice` (AST-detected,
    not in U04). Respect intra-unit order (a `logical-ops` rung must not use `break`/nesting taught later).
  - **U06 Secret Codes** introduces `string-index, string-slice, string-methods, in-operator`; union includes
    `for-loop, string-concat, def-function, parameters, return-value, range-function, accumulator, loop-counter,
    nested-loops` etc. Order within the unit: index → slice → methods → `in`. **A `string-methods` rung may use
    ONLY the four methods the unit teaches: `.strip()`, `.lower()`, `.upper()`, `.replace()`** (chaining them is
    fine) — any other method reds concept-scan's untaught-method check. The reverse slice `[::-1]` IS taught
    (fold it into the slice ladder as its realistic rung).
- **Execution:** `exec-lessons` runs every non-`no-exec` code cell in one kernel; prefer executable rungs with
  literal values; tag `no-exec` any rung using `input()` or demonstrating an error. (U04 uses `input()` — its
  accumulator/break game rungs that read input are `no-exec`, like U02.)
- **Concepts unchanged:** U04/U06 `manifest.concepts` (introduces/requires/practices) and coverage-map entries
  stay identical EXCEPT the `lessons` count. Exercises/solutions/checkpoints untouched. Each lesson still opens
  project-first.
- **House style:** allowed Book-1 constructs only (nothing used before its unit/position); unique cell ids; no
  stored outputs; `**Notice:**` markdown lines; teacher-notes `## Pacing` blocks == the new `lessons` count.

## Out of scope

- U03, U05 (turtle units — final rollout batch, plan 035), U07–U10 (batches 2–3).
- Any change to the concept set, exercises, solutions, checkpoints.
- **Verification-phase note:** ships reworked unit lessons WITH a named verification phase (Phase C).

## Phases

### Phase A — U04 "Quiz Show" lesson ladders

Rework `book1/units/unit-04-quiz-show/lesson.ipynb`: graduated ladders for `accumulator` (set a total at 0 →
add one → add again to see it grow → count with a **`while`-loop + counter**, NO `for`/`range`), `logical-ops`
(`and` → `or` → `not` → a combined rule — fixes a real gap: `not` currently has no code cell), `conditional-
nesting` (an `if` inside an `if` → an inner `elif`/`else` → a realistic locked-follow-up gate — ≥3 rungs, it is beginner-hard), `break-statement` (leave a `while` loop
early → with a condition → in the sudden-death game). Each rung adds exactly one increment. Executable rungs
with literal values where possible; `no-exec` for `input()`-driven game rungs. Set `manifest.yaml` `lessons: 3`
and update teacher-notes `## Pacing` to 3 lessons.

### Phase B — U06 "Secret Codes" lesson ladders

Rework `book1/units/unit-06-secret-codes/lesson.ipynb`: ladders for `string-index` (one index → another
position → negative index → index in a loop), `string-slice` (one increment per rung: `[a:b]` → `[:b]` →
`[a:]` → `[::-1]` reverse), `string-methods` (`.lower()` → `.upper()` → `.strip()` → `.replace(old,new)` →
chained in a transform — ONLY these four), `in-operator` (membership test → in an `if` condition → inside a
`for` loop over the string). Respect order index → slice → methods → `in`. Executable rungs with literal
strings preferred. Set `manifest.yaml` `lessons: 3` and update teacher-notes `## Pacing` to 3 lessons.

### Phase C — map/syllabus + Verification (named verification phase)

- `book1/curriculum/coverage-map.yaml`: set U04 `lessons: 3`, U06 `lessons: 3` (= their manifests; book1 total
  34 → 36, ≤ the `[28, 44]` ceiling). `book1/syllabus.md`: update the U04/U06 arc-table `Lessons` cells and
  the "~34 lessons"/"summing to 34 — 26 unit lessons"/"~32–34 class sessions" figures (→ 36, 28 unit lessons).
- `scripts/ci-local.sh` ALL GREEN: `exec-lessons` (every non-`no-exec` rung runs clean), `concept-scan`
  (no used-but-unlisted / untaught method — **watch: in U04, NO `for`/`range`/`string-slice` AND NO string
  `+` at all (`string-concat` is NOT in U04's union — use f-strings for output); in U06, only `.strip`/
  `.lower`/`.upper`/`.replace` in methods rungs, and string `+` is fine there (`string-concat` is a U06
  require)**),
  `coverage`/`prereq` (concepts unchanged → stable), `lesson-budget` (≤ 44), manifest==map, structure/hygiene/
  noexec, PDF build, pre-merge guard.
- **Closure + completeness/gradual audit (primary content-review duty):** no rung uses a later-in-unit or
  untaught concept or method; each ladder is complete + one-increment-per-rung; Notices accurate; lessons
  open project-first; and the numbered `## Pacing` blocks equal the new `lessons` count (manual — tooling only checks heading presence).

## Post-Execution Report

**Shipped:** worked-example ladders for U04 (Quiz Show) and U06 (Secret Codes) — rollout batch 1 of the
plan-031 standard.

**U04** `lesson.ipynb` 15 → 36 cells (15 code, 2 `no-exec`), 3 lesson sections (accumulator+logical-ops →
conditional-nesting → break+SUDDEN DEATH). Ladders: accumulator 4 rungs (set→add→add→while-loop counter→two
accumulators), logical-ops 4 (`and`→`or`→`not`→combined — fixes the prior gap where `not` had no code cell),
conditional-nesting 3 (if-in-if→inner if/else→locked follow-up), break 3 (fixed point→on a condition→sudden
death). **All loop rungs are `while`+counter (accumulator legal in U04); NO `for`/`range`/`string-slice`; all
output via f-strings (no string `+`, since `string-concat` is not in U04's union).** teacher-notes → 3
lessons; manifest `lessons: 3`.

**U06** `lesson.ipynb` 27 → 49 cells (21 code, 2 `no-exec`), 3 lesson sections (index/slice/methods →
ATBASH decode + `in` → Caesar encoder). Ladders: string-index 4 (`[0]`→more→`[-1]`→in a loop), string-slice 4
(one-increment `[1:4]`→`[:2]`→`[2:]`→`[::-1]`), string-methods 5 (`.lower`→`.upper`→`.strip`→`.replace`→
chained — **only these four taught methods**), in-operator 3 (membership→False cases→inside a loop). The
ATBASH/Caesar game cells are preserved as the realistic rungs.

**Phase C / verification:** `ci-local.sh` ALL GREEN. coverage-map U04/U06 `lessons: 3` (= manifests; book1
total 34 → 36 ≤ 44); syllabus arc-table + figures updated (28 unit lessons, 36 total). concept-scan clean
(no for/range/slice/string-`+` in U04; only the four methods in U06; no unknown methods); exec-lessons runs
every non-`no-exec` rung clean; closure audit clean. Concepts/exercises/solutions/checkpoints unchanged.

**Deviations:** none.

## Plan Review

### Round 1 (2026-09-09, HEAD 8f5bb22) — [fable] AWN · [glm] REJECT · [sol] pending

Both externals verified the accumulator-legitimacy (genuinely introduced in U04 → counting loops legal),
U06's order (index→slice→methods→`in`) and its exactly-four taught methods, and metadata stability. They
converge on one blocking error + nits:

1. `[FIXED]` **[glm REJECT B1 = fable Nit 1] U04 closure set wrong** — the plan listed `for-loop`/
   `range-function` in U04's available set, but neither is in U04's manifest union (both AST-detected) → a
   `for i in range(...)` rung would red concept-scan with no permitted fix (concepts frozen). → Corrected:
   U04 loop rungs are **`while` + counter only** (accumulator legal here), NO `for`/`range`, and NO
   `string-slice` (also AST-detected, not in U04). Phase C concept-scan watch updated.
2. `[FIXED]` **[glm/fable] enumerate U06's taught methods** — named `.strip/.lower/.upper/.replace` in Global
   Constraints (the only four; any other method reds concept-scan) and stated `[::-1]` IS taught (folded into
   the slice ladder).
3. `[FIXED]` **[glm] string-slice rung bundled `[a:]`+`[:b]`** (two-increment — sol-precedent reject). → Split
   the slice ladder to one increment per rung (`[a:b]` → `[:b]` → `[a:]` → `[::-1]`).
4. `[FIXED]` **[fable/glm] pin the lessons count** — U04/U06 → 3 each (total 36 ≤ 44); Phase C updates the
   syllabus figures.
5. `[WONTFIX-cosmetic] [glm] `loop-counter` is in U04 practices not requires` — corrected the wording to cite
   U04's union (requires + practices) rather than mislabeling.

[fable] APPROVE WITH NITS (no blocking); [glm] REJECT on B1 (now fixed). Re-confirming [glm]; [sol] pending.

### Round 2 (2026-09-09, HEAD 7fa2264) — [glm] AWN · [sol] APPROVE · CONSENSUS

[glm] re-confirm: **APPROVE WITH NITS** (B1 verified resolved against the tooling; 2 editorial nits applied —
the Phase-C watch note's U04 string-`+` inversion → corrected to "NO string `+` in U04, use f-strings", and
the syllabus "26 unit lessons" sub-figure). [sol] on the fixed HEAD: **APPROVE** (no blocking; confirmed
while-only/no-for-range/no-slice for U04, the four U06 methods + order, one-increment slice split, metadata +
budget + Phase C all sound). Also applied [sol]'s notes: conditional-nesting → ≥3 rungs (beginner-hard), and a
`## Pacing`-blocks==lessons manual check in Phase C.

**CONSENSUS — plan-review gate CLOSED:** [self] APPROVE · [fable] APPROVE WITH NITS · [glm] APPROVE WITH NITS
· [sol] APPROVE. Cleared for implementation.

## Content Review

### Round 1 (2026-09-09, HEAD e884e1a) — [self] APPROVE · [glm] AWN · [fable] AWN · [sol] REJECT

All reviewers AST-verified closure (U04 zero for/range/slice/string-`+`; U06 only the four methods, order
index→slice→methods→`in`), executed non-`no-exec` rungs clean, and confirmed conventions. [glm] and [fable]
judged completeness + gradual pacing MET and APPROVED WITH NITS; [sol] REJECTed on two pacing jumps. Findings:

1. `[FIXED]` **[sol, blocking] U04 conditional-nesting realistic rung jumped too hard** (cell 25 inner if/else
   → the full locked-follow-up game adds equality tests + two accumulators + outer else + output at once). →
   Added a bridge rung (nesting + one scoring step) and framed the full game as "put it together", so the
   increment is one step. (Aligns with the user's gradual-pacing priority.)
2. `[FIXED]` **[sol, blocking] U04 break realistic rung jumped too hard** (cell 32 conditional break → full
   SUDDEN DEATH with inputs + if/elif/else dispatch + tally). → Added a bridge rung (break when an
   accumulator hits a target, executable) and framed the full game as the application.
3. `[FIXED]` **[sol nit / glm nit1 / fable nit1] U06 in-loop Notice over-claimed** "shift a letter, copy a
   mark" when the rung only labels characters. → Reworded to "tests each character — here it just labels
   them; the real cipher will use that test to shift/copy."
4. `[FIXED]` **[glm nit1 / fable nit1] U06 teacher-notes "Lesson-2 bug" stale** → "Lesson-3 bug".
5. `[FIXED]` **[glm nit2] syllabus ladder parenthetical** now names U04/U06 (plans 031–032).
6. `[FIXED]` **[fable nit2] U04 logical-ops combined-rung Notice** tightened ("use `and` for a real rule").
7. `[WONTFIX]` **[fable nit3] U06 ATBASH loop uses direct string iteration** vs the index ladder's range walk
   — PRE-EXISTING (3 occurrences before the rework), not a plan-032 regression; future errata/polish.
8. `[N/A]` **[sol] "ci-local FAIL"** — a SANDBOX artifact in sol's clone (Jupyter socket `PermissionError:
   Operation not permitted`); the real `ci-local.sh` runs ALL GREEN (CI_EXIT=0) here and [glm]/[fable]
   executed every rung clean. Not a repo defect.

U04 now 42 cells (2 bridge rungs added); all book1 checks PASS. Re-running ci-local + re-dispatching [sol].

### Round 2 — [sol] APPROVE · CONSENSUS

[sol] re-review: both pacing bridges CONFIRMED FIXED (U04 nesting cells 27/29 scoring bridge + "put
together" framing; break cells 37/39 accumulator-target bridge → full SUDDEN DEATH application), U06 Notice
accurate, closure/methods/exec/conventions all re-confirmed. **APPROVE.**

**CONSENSUS — content-review gate CLOSED:** [self] APPROVE · [glm] APPROVE WITH NITS · [fable] APPROVE WITH
NITS · [sol] APPROVE. Completeness + gradual pacing confirmed MET by all four; closure clean; all findings
`[FIXED]` (one pre-existing observation `[WONTFIX]`). `ci-local.sh` ALL GREEN. Cleared for PR.
