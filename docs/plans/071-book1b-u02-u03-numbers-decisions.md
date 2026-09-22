# Plan 071 — Book 1b Units 02 (Numbers & Arithmetic) + 03 (Decisions) + Checkpoint 01

**Origin:** Book 1b buildout (standing directive 2026-09-22, "full book 1b implementation").
**Design:** `docs/designs/005-book1b-concept-first.md` §3 (unit table + checkpoint boundaries), §5
(fastforward + U02 forward-tag convention), §6 (per-plan practice-coverage rule), §7 (mini-CP form).
**Template:** Unit 01 (`book1b/units/unit-01-output-and-variables/`, plan 070) — clone its shape exactly.

## Scope

Author two adjacent pre-function concept-family units **and their checkpoint** (U03 is a checkpoint
boundary, design §3; the rollout requires the checkpoint "where due", design §11 / [sol]+[glm] r1):
- **U02 — Numbers & Arithmetic**, **U03 — Decisions**, **checkpoint-01 — Foundations** (assesses U01–U03).

Each unit clones the U01 template (problem-first lesson; mini-CP pre-function exercises; per-line-assert
solutions in the house form; teacher-notes with core/extra/Challenge partition; ≥2 Challenge; solution-free
student notebooks; no `input()` in graded cells). Book 1b stays `buildout: true`.

## Coverage-map entries (the contract)

**unit-02-numbers-and-arithmetic** — `lessons: 3`
- introduces: `[int-type, float-type, arithmetic, type-conversion, boolean, comparison]`
- requires: `[print, variable, input, f-string]`
- practices: `[string-literal, naming, comment, error-messages, run-program, string-concat, for-loop, range-function, accumulator]`
  - **`for-loop`/`range-function`/`accumulator` are the deliberate FORWARD tags** (design §5: U02 is the
    first unit to demonstrate the forward-reaching `practices:` convention — its own example is "a small
    loop inside a numbers-unit problem"). U02's lesson carries ONE **boxed "Peek ahead — not needed for
    the exercises"** example that sums `range(1, 101)` into a running `total` (expected `5050`) — a case
    where writing it out by hand is visibly absurd, so the loop earns its keep ([fable] r2). It uses
    `for` + `range` + the accumulator idiom (`total = total + n`), all honestly tagged; it is lesson-only
    (NOT a core exercise; [fable] r1 #7 keeps `if`/loops out of U02 core), carries a one-line English
    gloss ("for each number `n` from 1 to 100, add it to `total`"), and students never modify it
    (teacher-notes: "read it aloud, don't teach it"). This makes the shipped U01 pointer true.

**unit-03-decisions** — `lessons: 3`
- introduces: `[logical-ops, if-statement, elif-else, conditional-nesting]`
- requires: `[boolean, comparison, arithmetic, variable, print]`
- practices: `[int-type, type-conversion, float-type, f-string, string-literal, naming, input]`

**checkpoint-01-foundations** — `kind: checkpoint`, `lessons: 0.5`
- introduces: `[]`
- requires: `[print, variable, if-statement, comparison, arithmetic]`
- practices: `[print, variable, comparison, boolean, arithmetic, int-type, float-type, type-conversion,
  if-statement, elif-else, logical-ops, conditional-nesting, f-string, string-literal, string-concat,
  naming, comment, run-program, error-messages, input]`
  - The checkpoint is where the FOUNDATIONAL concepts (`print`/`variable`/`comparison`/`boolean`/
    `arithmetic`/the control ids) get their `practices:` tag — exactly how Book 1's checkpoints anchor
    coverage. Checkpoints stay STRICT (fastforward does not apply): every practiced id is introduced by
    U01–U03, so `checkpoint_findings` passes.

Closure (strict over `requires`): U02 requires ⊆ U01; U03 requires ⊆ U01∪U02; checkpoint requires ⊆
U01–U03. No entry practices its own introductions. `prereq-check` (fastforward) validates `requires`
only; `coverage-check` (which runs `checkpoint_findings`) validates the rest.

### Design §6 practice-coverage record (manual, per-plan)

After U01–U03 + checkpoint-01, every concept introduced through U03 is practiced at least once (the
checkpoint's `practices:` covers the foundational io/data/control ids; U02/U03 practices cover the
string/number reinforcers; `for-loop` is a forward tag, not yet due). Concepts introduced *after* U03
(loops, functions, strings, collections, files, oop) are practiced by their own later units/plans; the
capstone practice-coverage anchor stays dormant until the Algorithm Challenge (still `buildout: true`).

## Authoring guardrails (Phase C/D) — folded from plan-review [fable]/[glm] r1

**U02 (numbers):**
- **No `round`/`min`/`max`/`abs`/`sum`/`len`** ([fable] #1/#3/r2, [glm] #3): all are `builtin-functions`
  (U07) in the scanner's `BUILTINS`; fastforward won't flag them in a unit, so the *plan* forbids them.
  Rounding/change = integer `//` and `%`; "distance"/sign = subtraction + comparison; the peek-ahead sum
  uses the accumulator idiom (`total = total + n`), never `sum(...)`.
- **Pin float output** ([fable] #2): expected output shows exactly what Python prints — `10 / 2` → `5.0`,
  `(3+4+5)/3` → `4.0`, `7/2` → `3.5`. Choose given values that land on `.0`/`.5`; never `1/3` or
  `0.1+0.2`; NO `:.2f` format specs. A **Notice** pins "`/` always gives a float, `//` gives an int".
- **`//` and `%` on non-negative operands only** ([fable] #3); negatives appear only in comparison/sign
  exercises. **Opening hook** = minutes→h:m (`135 // 60`, `135 % 60`) or digit-splitting — never "here is `int`".
- **Traceback beat** ([fable] #4): `print("Age: " + 12)` → `TypeError: can only concatenate str … to str`,
  fixed with `str()` / f-string; pair with `"3" + "4"` → `"34"` vs `3 + 4` → `7` (motivates `int()` on
  given text, e.g. `age_text = "12"`).
- **Keep `if` out of core** ([fable] #7): "compare two numbers" PRINTS the boolean
  (`print(a > b)` / `f"Is {n} even? {n % 2 == 0}"`), never an `if`; the boxed `for`-loop peek-ahead
  (using `for` + `range` + accumulator, all tagged) is the only forward reach in U02 and is lesson-only.
- Digit exercises state the operand range ("a two-digit number"); `int("12")` samples show the quotes ([fable] #10).

**U03 (decisions):**
- **Traceback beat** ([fable] #5): `if score = 90:` → `SyntaxError` (`=` vs `==`), fixed to `==`.
- **elif ordering** ([fable] #5): grade ladder top-down (`>= 90` first), triangle equilateral-before-isosceles;
  ≥1 exercise whose expected output is only correct with the right `elif` order + a Notice on why.
- **In-range** via `x >= 0 and x <= 10` (logical-ops' job); chained `0 <= x <= 10` only as a Notice.
- **Leap year** ([fable] #6): parenthesized `(year % 4 == 0 and year % 100 != 0) or year % 400 == 0`,
  pre-explained ("divisible by 4, except centuries, except every 400"), samples 1900/2000/2024; opener
  tests a single given year (pre-loop; separate `if`s if several).
- **input try-it** ([glm] #4): reuse the U01 Ex8 pattern — a fenced "try `input()` yourself" markdown
  snippet + a fixed-value stand-in in the graded cell.

**Both / checkpoint:** core ≤7 exercises per unit ([fable] #9), design §3 "logic puzzles" go in Challenge
only; each teacher-notes carries a "60-MINUTE CUT" line (U01 precedent). The **try-it / fixed-value
stand-in pattern applies wherever a lesson shows `input()` live**; no `input()` in ANY graded or solution
code cell (both units) ([glm] r2). The checkpoint is un-themed, mixes U01–U03, assesses only introduced
concepts, and is solution-free like a unit's exercises. **Checkpoint strict-scan traps** ([fable] r2 —
checkpoints keep the strict per-entry allowed set, NOT the fastforward unit allowance): checkpoint code
uses **no self-referential reassignment (`x = x + …`, `+=` → `accumulator`), no loops, no lists, and no
builtins beyond `print`/`int`/`float`/`str`**. **Checkpoint mix** ([fable] r2): 6–8 problems with a
declared balance — ≈2 U01 (output / f-string / variables), 2–3 U02 (arithmetic / type-conversion /
float-output), 2–3 U03 (incl. one order-sensitive `elif` ladder and one `and`/`or` range test), plus one
traceback-reading item — so the checkpoint genuinely exercises every id it claims to practice, and the
grading notes key each problem to its concept(s).

## Phases

### Phase A — plan-review gate (4-way). No implementation until consensus.

### Phase B — contracts
Append the three entries to `book1b/curriculum/coverage-map.yaml`; add three `syllabus.md` arc-table rows
(map order); create `manifest.yaml` per unit + the checkpoint. `--book book1b coverage-check` +
`prereq-check` GREEN.

### Phase C — statements (Codex, gpt-5.6-sol)
Per unit: `lesson.ipynb` + `exercises.ipynb` (problem-first, worked-example ladders, the named traceback
beats, ≥8 mini-CP pre-function exercises, ≥2 `stretch` Challenge, no solutions/outputs/"Solution"
headings, no `input()` in code). Checkpoint: `checkpoint.ipynb` (student-facing mixed U01–U03 problems,
no solutions/outputs). Follow every Authoring guardrail above.

### Phase D — solutions (SEPARATE fresh Codex, gpt-5.6-sol)
`solutions.ipynb` per unit AND for the checkpoint, house form (capture line → print → assert; repair
exercises show the literal fix). Mirror every `## Exercise N`; runs clean; no `input()` in code.

### Phase E — teacher-notes (inline) + verification
`teacher-notes.md` per unit (checkpoint gets grading notes): goals, 60–90 min pacing + 60-MINUTE CUT,
core/extra/Challenge partition, common mistakes, discussion prompts, differentiation. **Verification:**
full `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN across the three books; both units' + the
checkpoint's `exec-solutions` clean + asserts pass; exercises/checkpoint solution-free/output-free; ≥2
stretch per unit; opening cells are problems; the U02 `for`-loop peek-ahead executes. Scope allowlist =
this plan + `book1b/units/unit-0{2,3}-*/` + `book1b/checkpoints/checkpoint-01-foundations/` +
`book1b/curriculum/coverage-map.yaml` + `book1b/syllabus.md`.

## Out of scope

- U04–U13, the later checkpoints, and the Algorithm Challenge — later plans (072+).
- No tooling changes (plan 070 shipped them); no Book 1/Book 2 changes; no governance-file edits.
- Not an erratum. **Verification phase:** Phase E is the named verification phase (units + checkpoint → required).

## Plan Review

### Round 1 (2026-09-22) — [self] APPROVE (see below); [sol] REJECT; [glm] REJECT; [fable] APPROVE WITH NITS.

#### [self] round 1 — APPROVE (superseded by the round-1 folds: the original draft omitted the U02
forward tag, the post-U03 checkpoint, and the authoring guardrails; all now folded).

#### [sol] round 1 — **REJECT**, both blockers FOLDED:
1. U02 must demonstrate the forward-reaching `practices:` convention (design §5) → U02 `practices` now
   includes `for-loop` (a lesson-only peek-ahead sum), making the shipped U01 pointer true.
2. Post-U03 checkpoint deferred though U03 is a checkpoint boundary → **checkpoint-01-foundations added to
   this plan's scope**. (Closure/partition/template all PASS per [sol].)

#### [glm] round 1 — **REJECT**, both blockers FOLDED (tooling verified GREEN + mutation-tested by [glm]):
1. Same U02 forward-tag blocker → `for-loop` forward tag added.
2. Design §6 per-plan practice-coverage absent + U03 under-tags → checkpoint-01 now carries the
   foundational-concept `practices:`; the **§6 practice-coverage record** above is added. Nits folded:
   "rounding" disambiguated (`//`/`%`, no builtins); input try-it pattern pinned (guardrails).

#### [fable] round 1 — **APPROVE WITH NITS**, all 10 guardrails FOLDED into "Authoring guardrails" above
(no builtins; float output pinned; `//`/`%` non-negative; named U02/U03 traceback beats; elif ordering;
leap-year formula; `if` out of U02 core; practice bookkeeping via the checkpoint; core ≤7 + 60-min cut;
mini-CP wording).

### Round 2 (2026-09-22) — revised with the checkpoint, the `for-loop` forward tag, the §6 record, and
the authoring guardrails.
- **[sol]** — **APPROVE WITH NITS.** Both blockers verified resolved (forward tag legal/lesson-only;
  checkpoint schema-correct + strict + §6 record satisfies design). Nits FOLDED: dropped the non-existent
  `checkpoint-check`; the summing peek also uses `accumulator` → tagged (`for-loop`/`range-function`/
  `accumulator`) and wording fixed.
- **[glm]** (volcengine-plan/glm-5.3) — **APPROVE WITH NITS.** Verified GREEN + mutation-tested (forward
  tag in `requires` → FAIL; checkpoint practicing an untaught id → FAIL; non-empty checkpoint introduces
  → FAIL). Nits FOLDED: `checkpoint-check` wording; input try-it clause broadened to Phase C.
- **[fable]** — **APPROVE WITH NITS.** All 10 round-1 guardrails confirmed captured. Nits FOLDED: builtin
  ban extended to `sum`/`len`; peek-ahead made to "earn its keep" (sum `range(1,101)`→5050, boxed, gloss,
  read-aloud) with honest tags; checkpoint strict-scan traps + 6–8 declared-mix guidance added.

### Plan-review outcome: **FULL 4-way consensus** — [self] APPROVE · [sol]/[glm]/[fable] APPROVE WITH NITS,
all nits folded, no open blockers. Two rounds (round 1 = 2× REJECT on the U02 forward-tag + missing
checkpoint/§6; round 2 clean). Gate CLOSED → implementation (Phases B–E).

## Content Review

Scope: U02 + U03 + checkpoint-01 content (lessons/exercises/solutions/checkpoint/teacher-notes/manifests).
Commit 82503a0. Tooling unchanged since plan 070 (no code review needed this round).

### Review 1 — [self] (2026-09-22) — **APPROVE.**
Verified via full `ci-local.sh` ALL GREEN (three books) — `exec-solutions` passes, so every exercise's
per-line asserts hold (correctness) and `exec-lessons` runs both lessons incl. the 5050 peek-ahead.
Structural audit: U02 10 exercises / 6 stretch; U03 10 / 6; checkpoint 7 `## Question` (in 6–8);
solutions mirror all headings (10/10/7) with a non-vacuous assert each; no `input()` in any graded/
solution code; no executed outputs; no "Solution" headings; every cell has an id. Guardrails honored:
U02 opens on h:m, prints Booleans (no `if` in core), TypeError beat present, floats shown as `5.0`, the
`for`-loop peek is boxed/lesson-only with `for`/`range`/`accumulator` tagged; U03 has the `=`→`==` beat
and the order-sensitive Medal Ladder; checkpoint is strict (no loops/lists/accumulator/builtins beyond
print/int/float/str). Openings are problems, not drill. No open [self] findings.

_(Awaiting [sol] / [glm] (volcengine-plan/glm-5.3) / [fable].)_

## Post-Execution Report

_(Filled before shipping.)_
