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
nesting` (an `if` inside an `if` → a realistic locked-follow-up gate), `break-statement` (leave a `while` loop
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
  the "~34 lessons"/"summing to 34"/"~32–34 class sessions" figures to 36.
- `scripts/ci-local.sh` ALL GREEN: `exec-lessons` (every non-`no-exec` rung runs clean), `concept-scan`
  (no used-but-unlisted / untaught method — **watch: NO `for`/`range`/`string-slice` in U04; only `.strip`/
  `.lower`/`.upper`/`.replace` in U06 methods rungs; keep a string literal in any strings-context `+`**),
  `coverage`/`prereq` (concepts unchanged → stable), `lesson-budget` (≤ 44), manifest==map, structure/hygiene/
  noexec, PDF build, pre-merge guard.
- **Closure + completeness/gradual audit (primary content-review duty):** no rung uses a later-in-unit or
  untaught concept or method; each ladder is complete + one-increment-per-rung; Notices accurate; lessons
  open project-first.

## Post-Execution Report

_(filled at Phase C)_

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

### Round 2

_(pending — [glm] re-confirm B1; [sol] on the fixed HEAD)_

## Content Review

_(4-way content-review gate — consensus before PR)_
