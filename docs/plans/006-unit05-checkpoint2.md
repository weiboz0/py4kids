# Plan 006 — Unit 05 + Checkpoint 02 Implementation Plan

**Goal:** Ship `unit-05-function-factory` (functions — the Term 2 capstone concept) and `checkpoint-02-loops-and-functions`, closing the loops-and-functions teaching block so project 01 (Arcade Night) has all its prerequisites.

**Architecture:** Both follow the established pipelines — unit per plan 004, checkpoint per plan 005. Unit 05 introduces functions but `requires` turtle-basics/turtle-drawing, so it carries `assets/*.py` turtle scripts per D-005. TWO fixes ride along (gate round 1): (a) one map amendment — checkpoint-02's `practices` gains the foundational substrate it was missing (a plan-002 under-specification: it listed the headline loops/functions/turtle concepts but omitted `print`/`variable`/`comparison`/etc. that every question uses, where checkpoint-01 correctly carries them); (b) one small tooling change so `layout_findings` fail-closes on missing turtle assets when turtle is REQUIRED, not only when introduced.

**Spec:** `book1/curriculum/coverage-map.yaml` (binding); plan 004 unit conventions; plan 005 checkpoint conventions; D-001, D-005.

## Global Constraints

- All plan-004 unit Global Constraints apply to unit 05; all plan-005 checkpoint conventions
  apply to checkpoint 02 (map-equal manifests; `## Question N` 6–8 sequential; broken
  snippets in markdown fences; no stretch/solutions in the checkpoint; six teacher-notes
  headings incl. `## Grading`; solution bans/seed/≥3 non-vacuous asserts; hook-first for
  the unit; per-lesson concept allocation; commit trailers).
- Turtle-in-checkpoint rule (binding, new — checkpoints can't run turtle, D-005): any
  checkpoint question touching `turtle-basics`/`turtle-drawing` is TRACE/PREDICT style —
  the student reads a turtle snippet shown in a MARKDOWN FENCE and answers about what it
  draws (shape, count, closure); no turtle code cell in the checkpoint, no execution. Its
  SOLUTION is still a CODE CELL (the mirror check requires code under every question,
  fable #1) but holds only plain values, e.g. `answer = "pentagon"` + a non-vacuous
  `assert`; it imports no turtle (the GUI-import ban is tooling-enforced).
- Coverage-map amendment (EXACTLY this, gate round-1 blocker sol #3): append to
  `checkpoint-02-loops-and-functions.practices` the substrate its questions use —
  `print, variable, comparison, arithmetic, if-statement, elif-else, boolean, int-type,
  loop-counter, f-string` — all introduced by units 01–03, so closure holds; verified
  green against every curriculum invariant. Nothing else in the map changes; the
  checkpoint manifest carries the amended list.
- Unit 05 turtle assets follow D-005 + the plan-003 turtle conventions (closure to a
  multiple of 360°, `# turtle-check: open-path` opt-out). CORRECTION (sol #5): `turtle-check`
  globs and EXECUTES every `assets/*.py` including `assets/solutions_*.py`, so the solution
  turtle scripts MUST close per the convention too — the blind solution author is told this.
- Process (standing): no commits while a `[sol]` review is in flight; codex content-gate
  prompts name the in-process fallback and avoid bare CLI-flag-like tokens.

## Out of scope

Content plan → Phase D is the mandatory named verification phase. In scope (gate round 1):
ONE tooling change (the turtle-asset fail-close in Phase A.1) and ONE map amendment
(checkpoint-02 substrate, Phase A.2). Out of scope: project 01 and units 06+ (later plans);
PDF handouts for the checkpoint; any OTHER tooling change or map edit beyond those two.

## Phases

Dispatch per AGENTS.md: unit-05 lesson/exercises + checkpoint-02 questions + turtle asset
scripts via codex GPT-5.6-sol; solutions (unit + checkpoint) via a SEPARATE blind codex
session on finished statements only; teacher/grading notes inline; manifests inline.

### Phase A — tooling fail-close + map amendment (codex tooling / inline)

1. **Tooling (codex, sol #4):** `layout_findings` currently enforces `assets/` existence +
   reference resolution + `py_compile` only when the manifest INTRODUCES `turtle-basics`.
   Change the guard to fire when `turtle-basics` is in `introduces ∪ requires ∪ practices`,
   so a turtle-REQUIRING unit with missing/unreferenced assets fails closed. Reword the
   finding message from "introduces turtle but has no assets/" to "uses turtle but has no
   assets/" (it now fires for require/practice too — fable round-2 nit). Add a one-fault
   fixture (turtle-requiring unit, assets dir removed → FAIL). Parity verified by fable:
   real book1 unchanged (unit-03 introduces → still green; non-turtle units not triggered),
   synthetic turtle-in-requires unit newly caught.
2. **Map amendment (inline):** apply the checkpoint-02 practices amendment (Global
   Constraints); full curriculum suite green with the amendment alone before any content.
- **Acceptance:** `uv run pytest -q` green (new fixture passes; existing unchanged);
  `ci-local.sh` ALL GREEN with the amended map and the tooling change.

### Phase A′ — manifests (inline, land with content)

`book1/units/unit-05-function-factory/manifest.yaml` and
`book1/checkpoints/checkpoint-02-loops-and-functions/manifest.yaml`, both map-equal
(checkpoint carries the amended practices). Land each in the same commit as its complete
directory (no manifest-only intermediate — plan-005 discipline).
- **Acceptance:** each manifest is map-equal (`manifest-check` passes for its scope) and lands
  only in the commit that also carries its directory's complete file set (repo stays green
  at every commit).

### Phase B — unit-05-function-factory content (3 lessons)

Blueprint (introduces def-function, parameters, return-value, scope; requires turtle +
for-loop + variable + f-string; practices range-function, loop-counter, arithmetic,
nested-loops, float-type):
- Hook: a greeting-card + turtle-stamp FACTORY — stamp the same shape or card many times
  without copy-pasting; functions are the machine that makes machines.
- Lesson 1 (def-function, parameters): `def greeting_card(name):` — the same card for any
  name; parameters are the blanks the factory fills. A turtle `stamp` function drawing a
  shape at the current spot, called in `for side in range(sides)` (practices range-function
  AND loop-counter — the loop variable sets each stamp's size/position, so its VALUE is
  used, not just the repetition). Turtle work runs as `assets/l1_cards.py` (D-005).
  60-min cut targets the turtle-stamp application, never the core `def`/`parameters`.
- Lesson 2 (return-value): functions that hand something BACK — `area(w, h)` returns a
  number to use in a message; a `polygon_points(n)` helper returns the turn angle
  `360 / n` (practices float-type, arithmetic) used by the drawing script `assets/l2_shapes.py`.
- Lesson 3 (scope): local vs global — why a name inside a function doesn't leak out;
  a nested-loops turtle pattern factory (`assets/l3_stamps.py`, practices nested-loops)
  where each call is self-contained. A deliberate scope bug + traceback moment.
- Turtle-asset API constraint (glm round-2 #3): `turtle-check` runs every `assets/*.py`
  under the plan-003 FAKE-turtle stub, whose surface is only forward/backward/left/right/
  penup/pendown/pensize/pencolor/color/speed/bgcolor/Screen/done/exitonclick/Turtle —
  scripts must use ONLY these (no `write`/`goto`/`textinput`/`setpos`, which AttributeError
  under the stub); the `# turtle-check: open-path` opt-out waives ONLY closure, so the
  ≥1-pen-down and <10000-move bounds still apply. The greeting-card visual is drawn with
  pen strokes, not `turtle.write`.
- Notebooks carry the reasoning, predict-the-output for functions, and turtle predictions
  (turtle cells tagged `no-exec` or shown as markdown; nothing imports turtle in notebooks);
  `exercises.ipynb` ≥6 core + ≥2 stretch (write-a-function, fix-the-parameter,
  return-vs-print, scope-trace, design-a-stamp; stretch: a function with two parameters
  making a name-badge, a recursive-free "flower" stamp calling a petal function in a loop).
- Solutions: function/return/scope answers execute headless, input-free (assigned sample
  values, stated inline), non-vacuous asserts; turtle answers as `assets/solutions_*.py`
  which ALSO run under turtle-check and must close per convention.
- Teacher notes: five headings, per-lesson allocation (L1 def+params, L2 return, L3 scope),
  60-min cut points (L1 cut = the turtle stamp; differentiation protects the applied part),
  differentiation; common mistakes (print vs return, forgetting the parameter, expecting a
  local name outside, calling before defining).
- **Acceptance:** unit suite green (layout+assets, hygiene, structure, no-exec, turtle-check
  on l1/l2/l3 + solutions scripts, teacher-notes headings); solutions execute with asserts.

### Phase C — checkpoint-02-loops-and-functions content

Blueprint (practices for-loop, range-function, while-loop, accumulator, logical-ops,
conditional-nesting, def-function, parameters, return-value, scope, turtle-basics,
turtle-drawing — units 03–05 material):
- 8 questions (sequential 1..8, ceiling), ~35–45 min, all within the AMENDED
  practices ∪ requires. EVERY amended practices concept must appear in ≥1 named question
  (glm round-2 #2 — a practice with no question is a decorative map claim), pinned thus:
  Q1 trace a `for`/`range` loop's output (for-loop, range-function, loop-counter, print,
  int-type); Q2 complete a `while` accumulator (while-loop, accumulator, comparison,
  arithmetic, variable); Q3 write a small function with a parameter that returns an
  `f-string` greeting (def-function, parameters, return-value, f-string); Q4 return-vs-print
  judgment (return-value, print); Q5 scope trace (scope, def-function, variable); Q6 a
  logical-ops/nesting condition with a full `if`/`elif`/`else` ladder (logical-ops,
  conditional-nesting, if-statement, elif-else, boolean, comparison); Q7 TURTLE
  TRACE/PREDICT (read `for i in range(5): forward(...); right(72)` in a markdown fence →
  "a pentagon", no execution; solution is a plain-value code cell); Q8 build-it — a SCORING
  function only (def-function, parameters, accumulator, if-statement), NO draw option
  (sol #2: a draw option would be turtle production, violating trace/predict-only).
- Teacher notes + `## Grading`: per-question intent, partial reads, re-teach signal
  (functions are the hard idea — ≥1/3 missing the write-a-function or return question →
  revisit before project 01 leans on functions).
- **Acceptance:** checkpoint suite green (question count/sequence, no stretch/solutions,
  mirrored solutions + asserts, six teacher-notes headings); solutions execute headless.

### Phase D — Verification (NAMED, mandatory)

Mechanical: full pytest green; `ci-local.sh` ALL GREEN (unit-05 turtle-check on its assets;
checkpoint-02 through the checkpoint checks); solutions execute with non-vacuous asserts;
manifests map-equal; turtle assets close per convention.
Reviewer duties: blind-solve all questions/exercises; cumulative closure (unit 05 uses only
≤unit-05 concepts; checkpoint uses only its practices ∪ requires — the turtle question is
trace-only); solutions non-vacuous/complete; grading usable; timing; hook-first; the
turtle-in-checkpoint question is genuinely trace/predict with no execution dependency.

**Acceptance criteria:** both directories complete; `uv run pytest -q` green; ci-local ALL
GREEN (incl. the tooling fail-close fixture and amended map); content gate 4-way consensus.

---

## Plan Review

### Review 1 — [self] (2026-09-06)
- **Verdict**: APPROVE — reuses shipped pipelines; turtle-in-checkpoint resolved via trace/predict.

### Review 2 — [fable] (2026-09-06)
- **Verdict**: APPROVE WITH NITS (tooling traced live)
1. `[OPEN]` (Medium) Turtle-trace checkpoint solution must be a CODE cell (plain values, no turtle import) — the mirror check requires code under every question; prose-only fails.
2. `[OPEN]` (Medium) Unit-05 has turtle in `requires` not `introduces`, so `layout_findings` won't auto-enforce `assets/` existence/references — make it a Phase-D reviewer duty (or fix tooling).
3. `[OPEN]` (Nit) `range-function` practice only implicit — make it explicit.
4. `[OPEN]` (Nit) L1 is heaviest — target the 60-min cut at the turtle-stamp, not the core `def`.
5. `[OPEN]` (Nit) State solutions are input-free.
6. `[OPEN]` (Nit) Add pytest-green to acceptance criteria.

### Review 3 — [sol] (2026-09-06)
- **Verdict**: REJECT
1. `[OPEN]` (Major) `range-function` under-specified (= fable #3); loop-counter effect unstated.
2. `[OPEN]` (Blocker) Build-it offers "draws OR scores" — the draw option violates the trace/predict-only turtle rule.
3. `[OPEN]` (Blocker) Checkpoint-02 concept boundary: "return-vs-print" assesses `print`, and the for/range trace touches `print`/`loop-counter`, none in checkpoint-02's union. (Verified: checkpoint-02's practices omit the entire foundational substrate that checkpoint-01 carries — a plan-002 under-specification.)
4. `[OPEN]` (Blocker) Unit-05 turtle assets not fail-closed — `layout_findings` enforces assets only when turtle is INTRODUCED; unit-05 requires it, so missing assets pass. (= fable #2, but a tooling gap to close, not just a reviewer duty.)
5. `[OPEN]` (Major) Plan wrongly says `assets/solutions_*.py` are compile-checked not executed — `turtle_findings` globs and executes ALL `assets/*.py`, so solution scripts must close per convention.
6. `[OPEN]` (Major) Phases A–C have no phase-local acceptance criteria.

### Revision 2 resolutions (2026-09-06) — applied for sol + fable (glm r1 timed out, reviews rev2 fresh)
- sol 1 / fable 3 `[FIXED]`: `range-function` explicit (`for side in range(sides)`) and loop-counter's value-use stated.
- sol 2 `[FIXED]`: build-it is SCORING-ONLY; the draw option removed.
- sol 3 `[FIXED]`: map amendment adds the foundational substrate to checkpoint-02 practices (10 concepts, all ≤ unit 03); verified green against every curriculum invariant; Phase A applies it before content.
- sol 4 / fable 2 `[FIXED]`: tooling change — `layout_findings` asset enforcement fires for turtle in introduces ∪ requires ∪ practices; one-fault fixture added (Phase A).
- sol 5 `[FIXED]`: plan corrected — `assets/solutions_*.py` ARE executed by turtle-check and must close; blind author told.
- sol 6 `[FIXED]`: per-phase acceptance blocks added (A, A′, B, C); pytest-green added to final acceptance (fable #6).
- fable 1 `[FIXED]`: turtle-checkpoint solution is a plain-value CODE cell (not prose).
- fable 4 `[FIXED]`: L1 60-min cut targets the turtle stamp, not the core def.
- fable 5 `[FIXED]`: solutions stated input-free.

### Round 2 (2026-09-06)
- **[sol]**: REJECT — all 5 substantive items verified Clean; two stale-doc issues only.
  1. `[FIXED]` Phase A′ lacked an acceptance block. → added.
  2. `[FIXED]` `## Out of scope` still excluded "tooling change"/"map edit" that Phase A performs. → reworded to "beyond the two round-1 fixes".
- **[fable]**: APPROVE WITH NITS — prototyped the amendment + tooling change live (unit-03 stays green, no over-trigger, unit-05 enforced); all 8 questions within the amended union.
  1. `[FIXED]` Fail message "introduces turtle" should read "uses turtle" (fires for require/practice now). → reworded in Phase A.1.
- **[glm]**: APPROVE WITH NITS — re-verified amendment + tooling in /tmp.
  1. `[FIXED]` Out-of-scope self-contradiction (= sol r2 #2).
  2. `[FIXED]` Not every amended practices concept was pinned to a question (f-string/int-type/elif-else implicit). → binding rule added; all 10 pinned to Q1–Q8.
  3. `[FIXED]` Warn the codex author that turtle-check uses the fake-turtle stub (limited API; open-path waives only closure). → Phase B API-constraint note added.

### Round 3 (2026-09-06)
- **[sol]**: APPROVE — both doc fixes confirmed; rev3 delta (concept pinning, wording, API note) introduced no contradiction.

### Gate result (2026-09-06)
- `[self]` APPROVE · `[sol]` APPROVE (round 3) · `[glm]` APPROVE WITH NITS · `[fable]` APPROVE WITH NITS.
- Full consensus, no `[OPEN]` items — **gate PASSED; approval to implement.**

## Content Review

### Review 1 — [self] (2026-09-06)
- **Verdict**: APPROVE — concept sweep clean (brace hits are f-strings); hook opens the lesson; 279 tests, ci-local ALL GREEN.

### Review 2 — [fable] (2026-09-06)
- **Verdict**: APPROVE WITH NITS (no blockers)
- Blind-solved all 6 core + 2 Challenge exercises and all 8 questions — zero discrepancies; verified every amended-practices concept appears in ≥1 question (glm's decorative-claim concern, mapping listed); all six turtle assets close; tooling fail-close verified non-over-triggering.
1. `[FIXED]` Challenge-2 `petal(size)` solution is a non-drawing stub — add a one-line "plan stub" comment. → added.
2. `[WONTFIX]` Q6 solution refactors the shown print-in-branches into a `door_message` variable for the mirror assert — harmless, differs slightly from the literal snippet. → intentional (the assert needs a value to check); the reasoning is identical.

### Review 3 — [glm] (2026-09-06)
- **Verdict**: APPROVE WITH NITS (no blockers) — zero blind-solve discrepancies; closure, Q7 rule, tooling fail-close all verified clean.
1. `[FIXED]` (Should Fix) Checkpoint Q2 "write the two repaired lines" reads as an un-runnable fragment. → reworded to "rewrite the whole program … filling in both blanks so it runs".
2. `[FIXED]` (Nice to Have) Unit Ex3 had no concrete sample number. → "(For example, double the number 7.)" added.

### Review 4 — [sol] (2026-09-06)
- **Verdict**: REJECT
1. `[FIXED]` (Blocker) Challenge-2 `petal()` draws nothing, so the promised flower has no real drawing (the asset drew a stamp_gallery, not a flower). → added a genuinely-drawing `flower()`/`petal_shape()` to `assets/solutions_l3.py` (turtle-check PASS, closes); the notebook stub now points at it and explains the count-only headless check.
2. `[FIXED]` (Major) Checkpoint grading Q3/Q8 accepted `print` where the questions require `return`. → both tightened to require the returned value; partial credit named as the return-vs-print gap.
3. `[FIXED]` (Minor) Turtle fail-close practices-branch had no regression test. → `_practices_turtle_missing_assets` fixture added alongside the requires one.
4. `[FIXED]` (Nit) Unit Ex4 solution didn't state the float/whole-number prediction. → solution now says "FLOAT (20.0), because 2.5 is a float".
- Blind-solve: no checkpoint discrepancies; the two unit divergences (Ex6 blank values, Challenge-2 drawing) both trace to the under-constrained plan prompt, resolved by finding 1.

## Post-Execution Report

(written before shipping.)
