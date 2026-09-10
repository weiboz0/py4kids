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
  - **U04 Quiz Show** introduces `accumulator, logical-ops, conditional-nesting, break-statement` and requires
    U02/U03 concepts (`if/elif/else, while-loop, comparison, input, f-string, arithmetic, int-type, variable,
    for-loop, range-function, loop-counter`). **`accumulator` IS introduced here**, so counting loops
    (`score = score + 1`) are finally LEGAL in U04 — a deliberate contrast to U02's counter-free loops; its
    ladder may use them freely. Respect intra-unit order (a `logical-ops` rung must not use `break` if break
    is taught later, etc.).
  - **U06 Secret Codes** introduces `string-index, string-slice, string-methods, in-operator` and requires
    `for-loop, string-concat, def-function, parameters, return-value` (+ practices many). Order within the
    unit: index → slice → methods → `in` (confirm against the notebook). A `string-methods` rung may use ONLY
    methods the unit actually teaches (read the lesson to enumerate them — do not introduce an untaught
    method; untaught methods red concept-scan).
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

Rework `book1/units/unit-04-quiz-show/lesson.ipynb`: graduated ladders for `accumulator` (a core loop idea —
4+ rungs: set a total → add inside a loop → the running score → combine with a counter), `logical-ops`
(`and` → `or` → `not`, and combined), `conditional-nesting` (an `if` inside an `if` → a realistic gate),
`break-statement` (leave a loop early → with a condition → in the quiz game). Respect intra-unit order;
executable rungs where possible, `no-exec` for `input()`-driven game rungs. Update teacher-notes `## Pacing`
to the new lesson count and set `manifest.yaml` `lessons:` accordingly (current 2 → propose 3; confirm at
authoring by the ladder volume).

### Phase B — U06 "Secret Codes" lesson ladders

Rework `book1/units/unit-06-secret-codes/lesson.ipynb`: ladders for `string-index` (one index → negative
index → index in a loop), `string-slice` (4 rungs: `[a:b]` → `[a:]`/`[:b]` → step/reverse if taught →
realistic), `string-methods` (one taught method → another → chained/in a transform — ONLY methods the unit
teaches), `in-operator` (membership test → in a condition → in a loop/filter). Respect order index → slice →
methods → `in`. Executable rungs with literal strings preferred. Update teacher-notes `## Pacing` + manifest
`lessons:` (current → +1 as volume warrants).

### Phase C — map/syllabus + Verification (named verification phase)

- `book1/curriculum/coverage-map.yaml`: set U04/U06 `lessons` = their manifests; `book1/syllabus.md` arc-table
  `Lessons` cells updated (prose budget line already says "advisory"; adjust the total if it names a figure).
  Confirm the new book1 total stays ≤ 44 (the ceiling already raised in plan 031).
- `scripts/ci-local.sh` ALL GREEN: `exec-lessons` (every non-`no-exec` rung runs clean), `concept-scan`
  (no used-but-unlisted / untaught method — watch U06 string methods and any `+` in a numeric context),
  `coverage`/`prereq` (concepts unchanged → stable), `lesson-budget` (≤ 44), manifest==map, structure/hygiene/
  noexec, PDF build, pre-merge guard.
- **Closure + completeness/gradual audit (primary content-review duty):** no rung uses a later-in-unit or
  untaught concept or method; each ladder is complete + one-increment-per-rung; Notices accurate; lessons
  open project-first.

## Post-Execution Report

_(filled at Phase C)_

## Plan Review

_(4-way plan-review gate — consensus before any implementation)_

## Content Review

_(4-way content-review gate — consensus before PR)_
