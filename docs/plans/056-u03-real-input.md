# Plan 056 — u03 turtle-art-studio: full real-input treatment (compute-and-print arm)

**Status:** PLAN-REVIEW GATE CLOSED (4-way consensus, round 3) — implementation pending.
**Type:** Content — apply the full treatment to `unit-03-turtle-art-studio`.
**Branch:** `feature/plan-056-u03-real-input`. **Base:** main @ 580ddf2.

## Motivation

Rollout slice 6 (design 003 §7 — list-less units). u03 teaches turtle drawing via `for`/`range`/nested-loops,
and is the **hardest fit** for the norm: its lesson is 12 `no-exec` turtle DRAWINGS (0 compute capstones) and
the turtle drawing itself lives in separate `assets/*.py` files (structure-check-validated, **out of the
notebook real-input scope**). Treatment is decided by a **per-exercise audit, not a uniform rule** (design
003 **v4** authority): each exercise is classified by what it grades —
- **reads-nothing / generator → exempt** (design §1/§8 v4): the lesson's all-drawing capstones, the
  fix-the-error literal-count repairs (Ex3/Ex6), the predict-the-counters twins (Ex8/Ch1), the on-paper
  color-string task (Ch2), and the prediction-TABLE halves of Ex2/Ex4 — no real-form.
- **read-and-compute** (the remainder — Ex1/Ex5/Ex7/Ex10, Ex9, and the compute-authoring halves of Ex2/Ex4):
  the solution cell reads its shape parameter (`input(...)`, wrapped in `int()` when numeric) then runs the
  unchanged compute + `print`.

Because the lesson is all-drawing, u03's real-forms live **entirely in `solutions.ipynb` markdown** (the cp01
pattern) — **no lesson change, no metadata add** (§5/§8 v4 reads-nothing exemption). Authorities: design 003
**v4** (§1/§8 exemption, §5 per-unit audit, §2/§3 u01–u06 arm, §6); merged pilots u02/u04 (read-and-compute)
+ u01 + cp01 (solutions-markdown-only). Recurring audits baked in.

## No lesson change, no metadata change (corrected after round 1)

u03's lesson is **all turtle-DRAWING** (12 `no-exec` cells, 0 executable compute cells; the sole "put it
together" is the spirograph drawing) → there is **no compute capstone to pair with a lesson `input()` form**.
So u03's real-input treatment lives **entirely in `solutions.ipynb` markdown real-forms + exercise-statement
cues** (the cp01 pattern, adapted for a unit). Consequences:
- **NO lesson.ipynb change** (all-drawing lesson; turtle drawings are the reads-nothing/generator class).
- **NO metadata change.** No u03 CODE cell uses `input`/`int(input())` (markdown real-forms are invisible to
  concept-scan / prereq / coverage). So the design-§5 `input` add is NOT triggered for u03. **design 003 §5 is
  amended (v4)** to make the add per-unit-audit-contingent; u03 gets none. (`int-type`/`type-conversion` are
  `never_flag` and only appear in markdown anyway.)

## The treatment (read-and-compute, solutions-markdown-only)

1. **Real-input forms:** `solutions.ipynb` markdown fenced real-forms beside the fixed-data asserted twins;
   exercise STATEMENTS get `**Real version:**` cues (non-exempt) / `**No real version:**` notes (exempt).
2. **No data growth.** Shape params (`n=7`, `side_count=4`) are realistic (design 003 §3 u01–u06 arm).
3. **CP-light naming — none.** `n`, `side_count`, `shape_count`, `side_length`, `angle` are clean. Keep verbatim.
4. **No numbered prompts.** Real-forms read the shape parameter(s) up front — **one read per parameter, all up
   front** ("How many sides? " / "How many shapes? "), then the unchanged loop; no `{i+1}` indices.
5. **Read the parameter with `input(...)`, wrapped in `int()` only when numeric.** Numeric shape params
   (`n`, `side_count`, `shape_count`) → `int(input(...))` (int/type-conversion are u02, prereq-valid; markdown
   so not scanned); a STRING param (Ex7's `color_name`) → plain `input(...)`, no `int()`. Real-forms add only
   this to the existing `for`/`range`/arithmetic/`print`/f-string. **NO `if`/comparison/list/while/sys.stdin**
   (u03 has none; the only comparisons — and any `or`/BoolOp, e.g. `assert side_number != 0 or pen_size == 1`
   in the Ex1/Ex5/Ex7/Ex8 twins — appear ONLY inside `assert` lines, which stay in the twins). Turtle
   `assets/*.py` files are NOT touched.

## Per-exercise SHAPE table

| Shape | Exercises | Real-form + statement treatment |
|---|---|---|
| **exempt** | Ex3 + Ex6 (**fix-the-error** — the graded task is fixing the literal loop count [`range(3)`→`range(4)`, etc.], unrelated to input; reading dissolves the repair — the u01-Ex2/3 class, NOT u02-Ex4 where `int(input)` WAS the fix), Ex8 + Challenge 1 (**predict-the-counters** — the twin hardcodes the counter list as a string literal `"0, 1, 2, 3, 4, 5, 6"`, which a read of `n` would break), Challenge 2 (**on-paper/reads-nothing** — six fixed `turtle.color(...)` strings, no numeric param), and the **prediction/trace TABLE halves** of Ex2/Ex4 | NO real-form for the exempt part; `**No real version:**` statement note (with the one-line rationale) |
| **read-and-compute** (fixed shape param → read it) | Ex1, Ex5, Ex7, Ex10, Ex9 (**+ a declared print `print(drawn_sides, travel_moves)` added to its twin** so §6(b) has a result line — sol 19 is currently assert-only; expected result line **`16 4`** on the fixed data; the markdown twin must mirror this exact print + line), and the **compute-authoring halves of Ex2 + Ex4** (`n=7` loop print / nested `shape_count`/`side_count` print) | markdown real-form reads its shape parameter with `input(...)` (wrapped in `int()` when numeric — Ex7's `color_name` is a STRING → plain `input(...)`, no `int()`) then the unchanged compute+print; statement `**Real version:**` cue (Ex9's statement is script-only → its cue anchors to the twin: "**Real version:** — see the solution", naming `print(drawn_sides, travel_moves)`) |

(Ex2/Ex4 are hybrids: the prediction TABLE is exempt; the separate compute-authoring program is read-and-compute.
The `**No real version:**` note for Ex3/Ex6 records that they are literal-count repairs.)

## Phases
### Phase A — apply to u03 (exercises + solutions ONLY; + design 003 §5)
- **NO lesson.ipynb change; NO manifest/coverage-map change** (see above).
- **exercises.ipynb:** `**Real version:**` cues on Ex1/Ex5/Ex7/Ex9/Ex10; `**No real version:**` notes on
  Ex3/Ex6/Ex8/Ch1/Ch2. **Ex2/Ex4 are hybrids → carry BOTH, each half-labeled** so the authoring cue isn't
  skipped: `**Real version:** … for the program` (the compute-authoring half) + `**No real version:** … for
  the prediction table` (the predict-table half).
- **solutions.ipynb:** markdown read-and-compute real-forms per the SHAPE table; add the one declared print to
  Ex9's twin (so it has a result line).
- **design 003 §5** amended to v4 (per-unit-audit-contingent input add; u03 gets none) — done in this plan.
- No growth, no rename, no numbered prompts, **no teacher-notes change**. Fenced real-forms must not contain a
  `## Exercise <digit>` line.

### Phase B — verification
- `ast.parse` + piped-run every read-and-compute real-form; result line == fixed-data twin modulo `input()`
  prompt text (standard §6(a–c); one up-front read per parameter, then the unchanged loop/print). Ex9's twin
  gains a print → re-run it under `exec-solutions`.
- CLOSURE AST scan: only `input`/`int`/`for`/`range`/arithmetic/`print`/f-string in real-forms; NO
  `if`/list/while/`sys.stdin`; **comparisons AND `or`/BoolOp appear only inside `assert` lines** (e.g.
  `assert side_number != 0 or pen_size == 1`) — record so the scan doesn't false-alarm on the twins.
- 0 `input()` in solutions CODE cells; ≥3 non-vacuous assert cells; no fenced `## Exercise <digit>` line.
- `scripts/ci-local.sh` ALL GREEN (prereq/coverage/concept-scan unaffected — no metadata change).

## Out of scope
- Any Book-1 entry other than u03 (rollout continues per design 003 §7). **design 003 §5 amended → v4** (in
  scope, this plan). Turtle `assets/*.py` drawing files (separate artifact). No lesson change, no metadata add,
  no data growth. Phase B present.

## Plan Review

### Round 1 (2026-09-19) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.
#### [self] (2026-09-19)
- **Verdict**: APPROVE
- Uniform read-and-compute (every solutions cell is compute-and-print with a fixed shape param; turtle drawing
  in assets/*.py, out of scope); metadata refinement `practices:[input,int-type,type-conversion]` (int(input)
  needs u02 int concepts; prereq-valid); closure clean (no if/compare/list/while — u03 has none); SHAPE (exempt
  predict Ex2/Ex4; read-and-compute the rest + Challenges); lesson audit (compute capstones → input real-forms;
  turtle-drawing no-exec = reads-nothing class; rungs exempt); no growth/rename/numbered-prompts; Phase B present.
#### [sol] (2026-09-19)
- **Verdict**: REJECT
1. `[OPEN]` Must Fix: structural premise too coarse — sol 6 (Ex3) + sol 19 (Ex9) don't print; sol 25 (Ch2) has
   no numeric shape param; Ex3/Ex6 loop over LITERALS (int(input) would be inert). Re-survey per-cell.
2. `[OPEN]` Must Fix: Ex2/Ex4 tables are exempt, but each statement ALSO requires a separate headless program
   (sol 4/8 compute+print from fixed counts) — that coding portion needs a real-form.
3. `[OPEN]` Must Fix: Ex3/Ex6 are fix-the-error (repair literal loop bounds) — reading removes the graded repair
   → exempt (No real version), unlike u02 Ex4 where int(input) IS the fix.
4. `[OPEN]` Must Fix: lesson audit targets a nonexistent compute capstone — the sole "Put it together" (cell 38)
   is itself a no-exec turtle DRAWING → reads-nothing generator → REMOVE the proposed lesson input-form.
5. `[OPEN]` Must Fix: Ch2 (conceptual color-command strings, no n/side_count/shape_count) → exempt, not
   read-and-compute.

#### [glm] (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: REJECT
1. `[OPEN]` Must Fix: lesson-audit phantom — lesson has ZERO executable cells (all 12 no-exec drawings; capstone
   38 is a drawing). Fix to "all-drawing → NO lesson input() cell; input practice lands in exercises/solutions
   real-forms" OR scope creating a compute twin.
2. `[OPEN]` Must Fix: Ch2 → exempt reads-nothing (no numeric param; six fixed color strings).
3. `[OPEN]` Should Fix: Ex2/Ex4 are hybrids (predict table + compute-authoring half) — the authoring half needs
   a real-form (read-and-compute scoped to it); the u04-Ex6 pure-predict precedent doesn't cover hybrids.
4. `[OPEN]` Should Fix: Ex3/Ex9 print nothing → §6(b) parity vacuous; add a minimal print or document. (glm view:
   Ex3/Ex6 read-and-compute is defensible — starters run clean with wrong counts, not a traceback debug.)
5. `[OPEN]` Should Fix: design §5 — the 3-concept set + §5's "u03 gets a lesson input() cell" premise is
   falsified by the corrected audit; the practices add (if any) anchors on exercises/solutions real-forms.
   Metadata verified prereq-valid + in sync + no technique trip.
6. `[OPEN]` Nice: treatment §4 "reads ONE parameter" contradicts two-param exercises; Phase B "lesson no-exec
   form" moot; teacher-notes silent.

### Round 1 — outcome: REJECT (3 of 4). Fixed → round 2.
**Round 1 responses (plan revised):**
- → [FIXED] Lesson phantom ([sol]#4/[glm]#1/[fable]#1): **NO lesson change** — lesson is all-drawing;
  input practice via solutions markdown real-forms (the cp01 pattern). Both-forms audit removed.
- → [FIXED] Metadata ([sol]#? /[glm]#5/[fable]#5): **NO metadata add** — no u03 code cell uses input (markdown
  real-forms invisible to concept-scan); **design 003 §5 amended** to drop u03 from the lesson-input-cell add set
  (u03 is markdown-only). int-type/type-conversion are never_flag anyway.
- → [FIXED] Ch2 → exempt reads-nothing ([sol]#5/[glm]#2/[fable]#4).
- → [FIXED] Ex2/Ex4 → read-and-compute scoped to the authoring half; the prediction/trace TABLE stays exempt
  ([sol]#2/[glm]#3; [fable]#7 noted the inconsistency).
- → [FIXED] Ex3/Ex6 → EXEMPT (fix-the-error: the graded task is fixing the literal count, unrelated to input —
  the u01-Ex2/3 class, NOT u02-Ex4 where int(input) WAS the fix) ([sol]#3/[fable]#2; glm#4 minority
  read-and-compute noted — flagged for round 2).
- → [FIXED] Ex9 → read-and-compute with a declared one-line print added to its twin (so §6(b) has a result line).
- → [FIXED] Ex8/Ch1 → exempt (predict-the-counters, hardcoded counter-string literal).
- → [FIXED] Nits: treatment §4 reworded ("one read per parameter, all up front"); Phase B lesson-form line
  removed; teacher-notes "no change" stated; assert-line comparisons recorded for the closure scan.
Re-dispatching round 2 (lesson/metadata dropped; §5 amended; SHAPE reclassified materially).

#### [fable] (2026-09-19)
- **Verdict**: REJECT — treatment shape (read-and-compute, assets out of scope, int(input) closure) right, but
  structural premises wrong in two decision-level places.
1. `[OPEN]` Must Fix: lesson audit row 1 targets a nonexistent cell — all 12 lesson code cells are no-exec
   turtle drawings, the sole "Put it together" (cell 38) is the spirograph. Either name a real target — the L2
   polygon capstone (cell 24/27) or L3 spirograph (38) as a `no-exec` `input()` turtle form reading `n` (oracle:
   fake_turtle stub, compare computed `angle`; Notice handles the "lives in assets" promise) — OR keep the
   lesson untouched and drop the "input add is lesson-driven" claim (then the add is pedagogical-only, since
   concept-scan needs a lesson input() CODE cell to see it).
2. `[OPEN]` Must Fix: Ex3 (sol 6) + Ex9 (sol 19) have NO print (assert-only) — no §6(b) result line. Ex3 = exempt
   (fix-the-error). Ex6 same (repair dissolves the bug). Ex9 = add one print to the twin (declared edit) or exempt.
3. `[OPEN]` Should Fix: Ex8 + Ch1 twins hardcode the counter list as a string literal ("0, 1, 2, 3, 4, 5, 6") —
   reading `n` breaks it → exempt (predict-the-counters) or rewrite the twin.
4. `[OPEN]` Must Fix: Ch2 misclassified — no shape param (six literal color strings, on-paper) → exempt.
5. `[OPEN]` Nice: metadata — int-type/type-conversion are `never_flag` → the 3-set add is pedagogical (coverage
   honesty), NOT CI-forced; only `input` is CI-relevant, and only if a lesson `no-exec` input() CODE cell exists
   (ties to #1). State the 3-set is pedagogical.
6. `[OPEN]` Nice: closure confirmed (no if/while/list; only assert-line comparisons — record so Phase B doesn't
   false-alarm).
7. `[OPEN]` Nice: Ex2/Ex4 exemptions defensible (predict-without-running framing; fixed n=7 per the comment) —
   note the inconsistency with Ex5/Ex10 in the exempt note.
8. `[OPEN]` Should Fix: Phase B must name the turtle-form oracle (#1) + any twin edits re-run under exec-solutions.

### Round 2 (2026-09-19) — re-review after fixes (0619a62)
#### [self] round 2 (2026-09-19)
- **Verdict**: APPROVE — solutions-markdown-only (no lesson/metadata change) + design 003 §5→v4 resolve the
  phantom-lesson + metadata Must-Fixes; SHAPE reclassified (exempt Ex3/Ex6/Ex8/Ch1/Ch2 + Ex2/Ex4 tables;
  read-and-compute Ex1/Ex5/Ex7/Ex10/Ex9[+print] + Ex2/Ex4 authoring halves). No open blocker.
#### [sol] round 2 (2026-09-19)
- **Verdict**: REJECT
1. `[OPEN]` Must Fix: design-003 consistency — §5 (v4) now says u03 gets no lesson-input/metadata, but §7 still
   lists "input add: u03" and §8 still requires every complete task (incl. lesson cell 38 spirograph capstone)
   to have a lesson input() form. Reconcile §7 + **codify the reads-nothing/generator exemption in §1/§8**.
2. `[OPEN]` Must Fix: plan Motivation (lines 10–15) still says "every solution cell prints / uniform
   read-and-compute / design v3" — contradicts the corrected SHAPE. Rewrite to the per-exercise audit + v4.
3. `[OPEN]` Should Fix: Ex9's "one declared print" must pin the exact `print(...)` + expected result line (§6b).

### Round 2 — outcome: REJECT (1 of 4, [sol]); [glm]/[fable] APPROVE-WITH-NITS (Ex3/Ex6 exempt now consensus).
Fixed → round 3.
**Round 2 responses (plan + design revised):**
- → [FIXED] [sol]#1 (design consistency): **design 003 amended** — §1/§8 codify the **reads-nothing/generator
  exemption** (turtle drawing / generator / countdown / fixed printed card have no real-program form; the
  both-forms rule applies only to input-shaped tasks); §7 rollout `input`-add notes reconciled to defer to the
  §5 per-unit audit (u03 gets none); header + v4 revision entry updated. u03's cell-38 spirograph capstone is
  now explicitly exempt (all-drawing), so no lesson input form is required.
- → [FIXED] [sol]#2 (Motivation): rewrote lines 9–15 to the **per-exercise audit + v4** authority — dropped
  "every solution cell prints", "uniform read-and-compute", and the v3 citation.
- → [FIXED] [sol]#3 / [fable]#2 (Ex9 pin): pinned the exact declared print `print(drawn_sides, travel_moves)`
  and expected result line **`16 4`** in the SHAPE table; the markdown twin must mirror both.
- → [FIXED] [glm] Nice (Ex2/Ex4 half-labeled cues): Phase A now specifies BOTH cues, each labeled by half
  ("… for the program" / "… for the prediction table").
- → [FIXED] [fable]#1 (Ex7 string param): treatment §5 reworded — `input(...)` wrapped in `int()` only when
  numeric; Ex7's `color_name` is a STRING → plain `input(...)`.
- → [FIXED] [fable]#3 (closure-scan note): extended to "comparisons AND `or`/BoolOp only inside `assert` lines".
Re-dispatching round 3 ([sol] only; [glm]/[fable] already APPROVE-WITH-NITS with nits folded).

#### [glm] round 2 (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: APPROVE WITH NITS — all round-1 findings resolved; §5 v4 sound; **accepts Ex3/Ex6 exempt and
  withdraws its round-1 read-and-compute minority view** (the graded repair is the literal count; a read
  dissolves it; u01-Ex2/3 class). No new blocker.
1. `[OPEN]` Nice: Ex2/Ex4 hybrid statements carry BOTH a `**Real version:**` cue (authoring half) and a
   `**No real version:**` note (prediction-table half) — word each to name its half ("…for the prediction
   table" / "…for the program") so a student doesn't skip the authoring cue.

#### [fable] round 2 (2026-09-19)
- **Verdict**: APPROVE WITH NITS — all 8 round-1 findings verified resolved; §5 v4 sound (no governance file
  touched); Ex9 declared print sound (result line `16 4`). 3 plan-wording Nice (fold):
1. `[OPEN]` Nice: Ex7's `color_name` is a STRING → real-form reads it with plain `input(...)` (not `int()`);
   clarify treatment §5 ("read the parameter with `input(...)`, wrapped in `int()` only when numeric").
2. `[OPEN]` Nice: Ex9 statement is script-only → its cue anchors to the twin ("— see the solution") + name the
   declared print (e.g. `print(drawn_sides, travel_moves)`) so Phase B's expected line is unambiguous.
3. `[OPEN]` Nice: extend the closure-scan note to "comparisons AND `or`/BoolOp only inside `assert` lines"
   (Ex1/Ex5/Ex7/Ex8 twins carry `assert side_number != 0 or pen_size == 1`).

### Round 3 (2026-09-19) — [sol] re-review after round-2 fixes (1a710bb)
#### [sol] round 3 (2026-09-19)
- **Verdict**: APPROVE — no remaining Must/Should. Design consistency resolved (003 §1/§7/§8/§9 v4; cell 38
  exempt turtle drawing); Motivation matches the SHAPE table and cites v4; Ex9 pin exact (sol 19:
  `shape_count=4`,`side_count=4` → `drawn_sides=16`,`travel_moves=4` → result `16 4`). Classification,
  solutions-markdown-only form, no lesson/metadata/data-growth change, Phase B all intact.

### Round 3 — outcome: **PLAN-REVIEW GATE CLOSED** — 4-way consensus:
[self] APPROVE · [sol] APPROVE · [glm] APPROVE WITH NITS (folded) · [fable] APPROVE WITH NITS (folded). No open blockers.

## Content Review
_(pending — 4-way, post-implementation.)_

## Post-Execution Report
_(pending.)_
