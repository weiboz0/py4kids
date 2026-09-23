# Plan 074 — Book 1b Unit 07 (Functions) + Unit 08 (Randomness) + Checkpoint 03

**Origin:** Book 1b buildout ("full book 1b implementation").
**Design:** `docs/designs/005-book1b-concept-first.md` §3 (U07/U08 rows + checkpoint-after-U08), §5
(fastforward), §6 (coverage), §7 (mini-CP exercises + the **function form** from U07 on + turtle-exempt),
§8 (turtle practice sites run as `.py`).
**Templates:** Book 1b U01–U06 (prose/teacher-notes/checkpoint form); the **U06 turtle format** for the
turtle practice sites (`assets/*.py` + `turtle-check`); Book 1b cp01/cp02 for the checkpoint shape.

## Scope

Two concept-family units + one checkpoint:
- **U07 Functions** — introduces `def-function`, `parameters`, `return-value`, `scope`, `builtin-functions`;
  a `draw_polygon(n, side)` **turtle practice site** (design §3).
- **U08 Randomness** — introduces `random-module`; a turtle **random-walk** practice site (design §3).
- **Checkpoint 03** — after U08 (design §3/§6), un-themed, strict, assesses U01–U08.

This plan flips the solution form: **from U07 on, exercises use the *function form*** (design §7) — the
solution DEFINES the function and asserts it against **several distinct input cases** (fixed seeds where
random), NOT the pre-function per-line-output form used in U01–U06. Book 1b stays `buildout: true`.

## Coverage-map entries (contracts)

**unit-07-functions** — `kind: unit`, `title: "Functions — def, parameters, return, and built-ins"`, `lessons: 3`
- introduces: `[def-function, parameters, return-value, scope, builtin-functions]`
- requires: `[for-loop, range-function, while-loop, arithmetic, comparison, boolean, if-statement, variable, print]`
- practices: `[import-statement, turtle-basics, turtle-drawing, nested-loops, loop-counter, accumulator,
  running-total, count-by-condition, int-type, float-type, comment, naming]`

**unit-08-randomness** — `kind: unit`, `title: "Randomness — the random module, dice, and simulation"`, `lessons: 3`
- introduces: `[random-module]`
- requires: `[import-statement, def-function, parameters, return-value, for-loop, range-function, arithmetic,
  comparison, if-statement, boolean, variable, print]`
- practices: `[turtle-basics, turtle-drawing, builtin-functions, running-total, count-by-condition,
  accumulator, int-type, float-type, scope, comment, naming]`

**checkpoint-03-functions-and-randomness** — `kind: checkpoint`, `title: "Checkpoint 3 — Functions & Randomness"`, `lessons: 0.5`
- introduces: `[]`
- requires: `[print, variable, def-function, parameters, return-value, random-module, for-loop, range-function,
  while-loop, if-statement, elif-else, comparison, boolean, arithmetic, builtin-functions]`
- practices: `[print, variable, def-function, parameters, return-value, scope, builtin-functions, random-module,
  for-loop, range-function, while-loop, break-statement, loop-counter, accumulator, running-total,
  count-by-condition, if-statement, elif-else, comparison, boolean, arithmetic, int-type, float-type, f-string]`

Closure: every `requires` is introduced ≤ its entry (def-function/parameters/return-value/scope/
builtin-functions in U07; random-module in U08; the rest in U01–U06). U07's turtle `practices` are exactly
U06's introductions (the deferred practice sites promised in plan 073's §6 record) plus earlier loop/number
concepts. **Checkpoints get NO fastforward** (design §5): cp03 uses only concepts introduced ≤ U08. After
this plan: 33 → 39 introduced-once (adds the 6 above; cp03 introduces none).

### Design §6 practice-coverage record
U07/U08's turtle practice sites (`draw_polygon(n, side)`, random walk) are where U06's `import-statement`/
`turtle-basics`/`turtle-drawing` introductions get their promised practice (plan 073 §6). U08 practices U07's
`def-function`/`parameters`/`return-value`/`scope`/`builtin-functions` (every simulation is a function).
cp03 anchors the foundational practices for U01–U08 (Book-1 checkpoint style). No self-practice: neither unit
lists its own introductions in `practices`.

## The function form (U07 on — design §7; the big shift)

Student exercises are stated as "define `f(...)` meeting this spec" with worked sample calls
(`f(3, 74) → …`). `solutions.ipynb` DEFINES the function and asserts it against **several distinct input
cases** (not per-line output). Random exercises seed with `random.seed(N)` (fixed) before asserting.
`notebooks.py` still only enforces ≥3 assert-bearing cells notebook-wide; per-exercise "several distinct
cases" is the content-gate authoring rule. NO `input()` in graded/solution cells. Solutions run
top-to-bottom clean; student notebooks stay solution-free with NO executed outputs; every cell has a unique id.

## builtin-functions — teach the FULL facet set (U07)

`builtin-functions` is introduced here, so before U07 nothing beyond `print`/`int`/`float`/`str` was allowed.
Teach the useful set middle-schoolers need going forward: `len`, `range` (as the callable behind `for`),
`min`, `max`, `sum`, `abs`, `round`, `sorted` (preview kept out of core if it needs lists — lists are U10, so
`sorted`/list builtins stay OUT until U10; `min`/`max`/`sum` shown on ranges/loops, not lists). Keep every
core example to already-taught data (ints, floats, ranges) — NO lists/strings-as-sequences (U09/U10).

## Turtle practice sites (reuse the U06 format — verified by turtle-check)

- **U07 `draw_polygon(n, side)`**: a FUNCTION that draws a regular n-gon (`turtle.left(360 / n)`), shown in a
  no-exec lesson cell + `assets/l*_draw_polygon.py` (module-level style, one terminal `turtle.done()`), and an
  exercise starter `assets/ex*_*.py`. Same hard rules as U06: fake_turtle stub subset only; `360 / n` never
  `//`; closure or `# turtle-check: open-path`; ≥1 pen-down; solutions.ipynb carries NO `import turtle`
  (turtle code in markdown "real program" blocks + `assets/`; companions are headless).
- **U08 random walk**: a turtle that turns/steps by `random.randint`/`random.choice` — carries
  `# turtle-check: open-path` (a random walk does not close); fixed `random.seed(N)` so the drawn `.py` is
  deterministic under turtle-check.
- Turtle exercises are EXEMPT from the assert rule (design §7); verified by execution + `turtle-check`.

## Teaching outlines

### U07 Functions (3 lessons, problem-first)
- **L1 — Define & Call (`def-function`, `parameters`, `return-value`).** Hook: "we keep re-writing the same
  `is_prime` check — package it once." `def name(params): … return value`; call it; the difference between
  `print`-ing inside vs `return`-ing a value the caller uses. Ladder: `square(n)`, `is_even(n)`, `celsius_to_f`.
- **L2 — Functions that Compute (`return-value` deepened + `builtin-functions`).** `is_prime(n)`, `gcd(a, b)`
  (Euclid `while`), `fib(n)`; then the built-ins `len`(on a range count)/`min`/`max`/`sum`/`abs`/`round` as
  named tools, contrasted with writing the loop by hand. The `draw_polygon(n, side)` turtle practice site.
- **L3 — Scope (`scope`).** Local vs global names; a parameter is a local name; why a function can't see a
  caller's loop variable; return a result instead of reaching out. Common trap: shadowing / expecting a
  local change to leak out.
60-min cut per lesson noted in teacher-notes.

### U08 Randomness (3 lessons, problem-first)
- **L1 — Chance (`random-module`).** `import random`; `random.randint(a, b)`, `random.random()`,
  `random.choice(seq-of-numbers)`; **`random.seed(N)` for reproducibility** (and why tests seed). Dice/coin.
- **L2 — Simulate & Estimate.** Count outcomes over many trials (running-total/count-by-condition in a
  function); a Monte-Carlo estimate (e.g. fraction of dice rolls that beat a threshold; a π-style estimate
  kept to already-taught math). Everything packaged as seeded functions.
- **L3 — Random Turtle Walk.** The turtle practice site: step + random turn, seeded, `open-path`.
60-min cut per lesson noted in teacher-notes.

### Checkpoint 03 (after U08, strict, no turtle, no fastforward)
6–8 VISIBLE `## Question N`. Mix: define-a-function questions (a small `is_prime`/`gcd`-style; a
parameterized formula; a running-total function), an `elif` ladder inside a function, one built-in-function
question (`min`/`max`/`sum`/`abs`/`round` on a range/loop), and ONE seeded-random question (`random.seed(N)`
then a function whose asserted result is deterministic). Strict scan: only concepts ≤ U08; NO lists/dicts/
strings-as-sequences/files/classes; built-ins limited to those taught (print/int/float/str + the U07 set).
teacher-notes has `## Grading` + the full heading set.

## Value plan
Distinct input cases per exercise/question, distinct from lesson examples and each other (the plan-072/073
value-distinctness rule). List the (function, sample inputs) plan in each unit's + the checkpoint's
teacher-notes so the gate can check.

## Phases

### Phase A — plan-review gate (4-way). No implementation until consensus.
### Phase B — contracts: 3 coverage-map entries (7-key) + 2 unit manifests + 1 checkpoint manifest + 3 syllabus rows; `--book book1b coverage-check` + `prereq-check` GREEN.
### Phase C — statements + assets (Codex): U07 + U08 lesson.ipynb (function form; no-exec turtle demos for the practice sites) + exercises.ipynb + cp03 questions + turtle assets (lN_*/ex*_* .py). Pin: function form, builtin facet set, module-level turtle + `360 / n` + closure/open-path, seeded random.
### Phase D — solutions (SEPARATE fresh Codex): U07/U08 solutions.ipynb (function form: define + assert several distinct cases; NO `import turtle`; ≥3 assert cells; seeded random) + cp03 solutions + turtle `assets/solutions_*.py`; verify `turtle-check` + `exec-solutions`.
### Phase E — teacher-notes (inline, all three) + verification: full `TMPDIR=/dev/shm bash scripts/ci-local.sh`
ALL GREEN (registry/lint, unit tests, notebook exec+hygiene, manifest/prereq/coverage/stretch,
**turtle-check** for the practice sites, **checkpoint_question_findings**, PDF, pre-merge-guard). AST audit of
every turtle `assets/*.py`: module-level only, `360 / n` never `//`, one terminal `turtle.done()`, no
`exitonclick`, closure or `# turtle-check: open-path`. Scope allowlist = this plan + the U07/U08/cp03 trees +
coverage-map + syllabus.

## Out of scope
- U09–U13, cp04, Algorithm Challenge — plans 075+. No tooling/stub extension; no governance/Book-1/2 changes.
- No lists/dicts/strings-as-sequences/files/classes (later units); built-ins limited to the U07 set (no
  list/string builtins until U09/U10).
- **Verification phase:** Phase E is the named verification phase (units + checkpoint → required).

## Plan Review

### Round 1 (2026-09-23)
**[self] APPROVE.** Closure verified: U07 requires ⊆ U01–U05, U08 requires ⊆ U01–U07 (import-statement U06,
def/params/return U07), cp03 requires ⊆ U01–U08; no entry lists its own introductions in `practices`; U07/U08
turtle practices are exactly U06's introductions (the plan-073 §6 deferred sites); cp03 gets no fastforward
and uses only ≤U08 concepts. 33→39 introduced-once, no duplicate introductions. Named verification phase (E)
covers both units + the checkpoint. Function-form + turtle-practice-site + builtin-facet risks are pinned in
Phases C/D.
_(Awaiting [sol]/[glm]/[fable].)_

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(Filled before shipping.)_
