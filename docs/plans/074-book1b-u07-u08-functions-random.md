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
- practices: `[import-statement, turtle-basics, turtle-drawing, loop-counter, accumulator, running-total,
  int-type, float-type, error-messages, comment, naming]`
  (Dropped `nested-loops`/`count-by-condition` — no named site; `draw_polygon` is a single loop. Each kept
  tag has a named site in the outline: `loop-counter` (the loops in `is_prime`/`gcd`), `accumulator` (`fib`),
  `running-total` (`sum_to_n` contrasted with the `sum()` builtin), int/float returns, `error-messages` (L1's
  print-vs-return `TypeError … NoneType` reading callback — [sol] r2), comments/names.)

**unit-08-randomness** — `kind: unit`, `title: "Randomness — the random module, dice, and simulation"`, `lessons: 3`
- introduces: `[random-module]`
- requires: `[import-statement, def-function, parameters, return-value, for-loop, range-function, arithmetic,
  comparison, if-statement, boolean, variable, print]`
- practices: `[turtle-basics, turtle-drawing, builtin-functions, running-total, count-by-condition,
  accumulator, int-type, float-type, scope, comment, naming]`

**checkpoint-03-functions-and-randomness** — `kind: checkpoint`, `title: "Checkpoint 3 — Functions & Randomness"`, `lessons: 0.5`
- introduces: `[]`
- requires: `[print, variable, def-function, parameters, return-value, random-module, import-statement,
  type-conversion, for-loop, range-function, while-loop, if-statement, elif-else, comparison, boolean,
  arithmetic, builtin-functions, f-string, string-literal]`
- practices: `[print, variable, def-function, parameters, return-value, scope, builtin-functions, random-module,
  import-statement, type-conversion, for-loop, range-function, while-loop, loop-counter, accumulator,
  running-total, count-by-condition, if-statement, elif-else, comparison, boolean, arithmetic, int-type,
  float-type]`
  (**Strict-scan closure ([sol]/[glm]):** the checkpoint allowed set is `requires ∪ practices`
  (concept_scan.py:934-936; checkpoints get NO fastforward). The seeded-random question's `import random`
  detects BOTH `import-statement` and `random-module`; `int()`/`str()`/`float()` detects `type-conversion`;
  a literal-bearing f-string detects BOTH `f-string` AND `string-literal` (concept_scan.py:14-15,279-285) —
  both are placed in `requires` (the "real prereqs" convention, matching shipped cp01/cp02 which put
  `f-string` in requires) and so are NOT duplicated here. Dropped `break-statement` (no `while … break`
  sentinel). `count_primes(n)` backs `count-by-condition`. **Phase C cp03 pin:** join text with f-strings
  only (NO `+` string-concat) and use NO boolean operators (`and`/`or`) — avoids detecting unlisted
  `string-concat`/`logical-ops` ([glm] r3); the `scope` tag is backed by a define-and-return question whose
  body uses a local name ([fable] r3).)

Closure: every `requires` is introduced ≤ its entry (def-function/parameters/return-value/scope/
builtin-functions in U07; random-module in U08; the rest in U01–U06). U07's turtle `practices` are exactly
U06's introductions (the deferred practice sites promised in plan 073's §6 record) plus earlier loop/number
concepts. **Checkpoints get NO fastforward** (design §5): cp03 uses only concepts introduced ≤ U08. After
this plan: 33 → 39 introduced-once (adds the 6 above; cp03 introduces none).

### Design §6 practice-coverage record
U07/U08's turtle practice sites (`draw_polygon(n, side)`, random walk) are where U06's `import-statement`/
`turtle-basics`/`turtle-drawing` introductions get their promised practice (plan 073 §6). U08 REQUIRES
(core) U07's `def-function`/`parameters`/`return-value` (every simulation is a function) and PRACTICES
`scope`/`builtin-functions`; cp03 then anchors the practice of all five U07 introductions plus `random-module`
(Book-1 checkpoint style). U07's own kept practice tags each have a named site: `loop-counter`
(`is_prime`/`gcd` loops), `accumulator` (`fib`), `running-total` (`sum_to_n` vs the `sum()` builtin), int/float
returns, comments/names. No self-practice: neither unit lists its own introductions in `practices`.

## The function form (U07 on — design §7; the big shift)

Student exercises are stated as "define `f(...)` meeting this spec" with worked sample calls
(`f(3, 74) → …`). `solutions.ipynb` DEFINES the function and asserts it against **several distinct input
cases** (not per-line output). **Random exercises MUST seed with `import random` +
`random.seed(4)` (module style) before the first random use** — `_solution_policy_findings`
(notebooks.py:231-328, run on U08 AND cp03 solutions) requires a preceding `random.seed(4)` (literal int 4)
before the first random attribute and bans `from random import …` (an authoring pin uses seed 4 and nothing else). `notebooks.py` also enforces ≥3 assert-bearing cells notebook-wide; per-exercise
"several distinct cases" is the content-gate authoring rule. NO `input()` in graded/solution cells. Solutions run
top-to-bottom clean; student notebooks stay solution-free with NO executed outputs; every cell has a unique id.

## builtin-functions — the taught facet set (U07)

`builtin-functions` is introduced here, so before U07 nothing beyond `print`/`int`/`float`/`str` was allowed.
Teach exactly this NUMBER-argument set: `max(a, b)` / `min(a, b, c)` on numbers, `sum(range(1, n + 1))`
(contrasted with the hand loop), `abs`, `round` (teacher-notes note the banker's rounding `round(2.5) == 2`),
and `range` as the callable behind `for`. **`sorted` is OMITTED entirely** — `concept_scan.py:451` maps
`sorted`→`list-sort`, which would fail the strict scan (lists are U10). `len` is PREVIEWED in one sentence
only (its natural argument is a list/string → taught in U09), never used in core. NO lists/
strings-as-sequences anywhere in U07 (U09/U10); every example stays on already-taught data (ints, floats, ranges).

## Turtle practice sites (reuse the U06 format — verified by turtle-check)

- **U07 `draw_polygon(n, side)`**: a FUNCTION that draws a regular n-gon (`turtle.left(360 / n)`), shown in a
  no-exec lesson cell + `assets/l*_draw_polygon.py` (module-level style, one terminal `turtle.done()`), and an
  exercise starter `assets/ex*_*.py`. Same hard rules as U06: fake_turtle stub subset only; `360 / n` never
  `//`; closure or `# turtle-check: open-path`; ≥1 pen-down; solutions.ipynb carries NO `import turtle`
  (turtle code in markdown "real program" blocks + `assets/`; companions are headless).
- **U08 random walk**: a turtle whose step/turn is chosen by `random.randint(0, 1)` (→ left/right) — NOT
  `random.choice([…])` (a list literal is U10; if `choice` is used anywhere its argument is a `range(...)`,
  never a list). Carries `# turtle-check: open-path` (a random walk does not close); `import random` +
  `random.seed(4)` before the first random call so the drawn `.py` is deterministic under turtle-check.
- Turtle exercises are EXEMPT from the assert rule (design §7); verified by execution + `turtle-check`.

## Teaching outlines

### U07 Functions (3 lessons, problem-first)
- **L1 — Define & Call (`def-function`, `parameters`, `return-value`).** Genuine hook with a visible payoff:
  a mini "temperature-converter tool" the class calls on several inputs — the point is a function you invoke
  again and again, not a one-off script. `def name(params): … return value`; call it. **The print-vs-return
  trap gets a concrete artifact (design's most-important idea):** a function that only `print`s, then a
  caller doing `total = f(3) + 1` → `TypeError: unsupported operand … NoneType`; students read the error
  (`error-messages` callback) and fix it with `return`. One pinned exercise + a lesson Notice on this.
  Ladder: `square(n)`, `is_even(n)`, `celsius_to_f(c)`.
- **L2 — Functions that Compute (`return-value` deepened + `builtin-functions`).** `is_prime(n)`,
  `gcd(a, b)` (Euclid `while` — `loop-counter`), `fib(n)` (`accumulator`), `sum_to_n(n)` (`running-total`)
  contrasted with `sum(range(1, n + 1))`; then the built-ins `max(a,b)`/`min(a,b,c)`/`sum`/`abs`/`round` as
  named number tools (NO `len`/`sorted`), each contrasted with the hand loop. **`fib` uses a temp variable
  (`nxt = a + b; a = b; b = nxt`), NEVER tuple assignment `a, b = b, a + b`** (multiple/tuple assignment is
  untaught — [fable] r2). The 60-min cut names `gcd` (Euclid, the least intuitive) as the item to defer/stretch.
- **L3 — Scope (`scope`) + the `draw_polygon(n, side)` turtle practice site.** Local vs global names; a
  parameter is a local name; why a function can't see a caller's loop variable; return a result instead of
  reaching out. `draw_polygon(n, side)` is the scope APPLICATION — `n`/`side`/`angle = 360 / n` are local
  names inside the function (turtle practice site; `assets/*.py`, `turtle-check`). Trap: expecting a local
  change to leak out.
60-min cut per lesson noted in teacher-notes.

### U08 Randomness (3 lessons, problem-first)
- **L1 — Chance (`random-module`).** `import random`; `random.randint(a, b)` and `random.choice(range(...))`
  (argument is a `range`, never a list — lists are U10); **`random.seed(4)` for reproducibility** (and why
  tests seed). A dice/coin game that keeps a **cumulative score across rolls** (`running-total` site — [glm] r3).
  (NO `random.random()`/`uniform`/`randrange` — the scanner permits only `seed`/`randint`/`choice`, concept_scan.py:55.)
- **L2 — Simulate & Estimate.** Count outcomes over many trials in a seeded function — a trial tally uses
  the `accumulator` (`total = total + 1`) and `count-by-condition`; report the result with the built-ins
  `round`/`max` (`builtin-functions` site). Then a Monte-Carlo estimate with `randint` on an integer grid,
  motivated by a **picture** (a quarter-circle inside a square: the fraction of random points landing inside
  the quarter-circle ≈ its area ratio π/4, so `×4` gives π — draw it / use the U06 turtle intuition, don't
  leave the `×4` as magic): `x = random.randint(0, 1000)`, `y = random.randint(0, 1000)` (each axis has 1001
  possible values, not a "1000×1000 grid"), count `x*x + y*y <= 1000*1000` (squares + `<=` are U02 math). Teacher-notes state the estimate is CLOSE TO,
  not exactly, π (more trials → closer), so students expect ~3.1, not 3.14159. Everything packaged as seeded functions.
- **L3 — Random Turtle Walk.** The turtle practice site: fixed step + a random left/right turn chosen by
  `random.randint(0, 1)`, `random.seed(4)`, `# turtle-check: open-path`.
60-min cut per lesson noted in teacher-notes.

### Checkpoint 03 (after U08, strict, no turtle, no fastforward)
6–7 VISIBLE `## Question N`. Mix: define-a-function questions (a small `is_prime`/`gcd`-style; a
parameterized formula; a `sum_to_n` running-total function), a `count_primes(n)` count-by-condition
function, an `elif` ladder inside a function, one built-in-function question (`max`/`min`/`sum`/`abs`/`round`
on numbers/ranges), and ONE seeded-random question whose STATEMENT tells the student to call `random.seed(4)`
before their function's first random use (so the blind-solve reproduces the asserted, deterministic value —
matches notebooks.py:323-328). Strict scan: only concepts ≤ U08; NO lists/dicts/strings-as-sequences/
files/classes; built-ins limited to those taught (`print`/`int`/`float`/`str` + the U07 number set, no
`len`/`sorted`). teacher-notes has `## Grading` (naming TWO pass-bar items: *define-and-return* and
*call-and-use-the-result*, mirroring cp02) + the full heading set.

## Value plan
Distinct input cases per exercise/question, distinct from lesson examples and each other (the plan-072/073
value-distinctness rule). List the (function, sample inputs) plan in each unit's + the checkpoint's
teacher-notes so the gate can check.

## Phases

### Phase A — plan-review gate (4-way). No implementation until consensus.
### Phase B — contracts: 3 coverage-map entries (7-key) + 2 unit manifests + 1 checkpoint manifest + 3 syllabus rows; `--book book1b coverage-check` + `prereq-check` GREEN.
### Phase C — statements + assets (Codex): U07 + U08 lesson.ipynb (function form; no-exec turtle demos for the practice sites) + exercises.ipynb + cp03 questions + turtle assets (lN_*/ex*_* .py). Per unit: **≥8 exercises, core ≤7, ≥2 `stretch` Challenge** (the ≥6-heading + ≥2-stretch floor is
notebooks.py:583-587; ≥8/core≤7 is the plans-071–073 house convention — [glm] r2). exN turtle starters are valid CLOSED placeholders (≥1 pen-down), per the U06 rule. Pin: function form (define-a-function specs with worked sample calls); the number-only builtin set (max/min/sum/abs/round, NO len/sorted); module-level turtle + `360 / n` (never `//`) + closure/`# turtle-check: open-path`; random uses ONLY `randint`/`choice(range(...))` (NO `random.random`) and `import random` + `random.seed(4)`.
### Phase D — solutions (SEPARATE fresh Codex): U07/U08 solutions.ipynb (function form: define + assert several distinct cases; NO `import turtle`; ≥3 assert cells; random solutions begin `import random` + `random.seed(4)` before first random use, no `from random import`) + cp03 solutions + turtle `assets/solutions_*.py`; verify `turtle-check` + `exec-solutions`.
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

**[fable] APPROVE WITH NITS; [sol] REJECT; [glm] REJECT.** All blockers are verified tooling-closure facts
(the reviewers cited exact tool lines). Folded ALL of them:
- `[FIXED]` **random API** ([sol]/[fable]): dropped `random.random()`/`uniform`/`randrange` (scanner permits
  only `seed`/`randint`/`choice`, concept_scan.py:55); Monte-Carlo now uses `randint` on an integer grid.
- `[FIXED]` **seed(4)** ([sol]/[glm]/[fable]): pinned `import random` + `random.seed(4)` before first random
  use in all U08/cp03 solutions; banned `from random import` (notebooks.py:231-328).
- `[FIXED]` **cp03 strict-scan closure** ([sol]): added `import-statement` (the random question imports
  random) + `type-conversion` (int/float/str) to cp03 requires+practices; dropped `break-statement`.
- `[FIXED]` **`sorted` removed entirely** ([sol]/[fable]/[glm]): U07 builtins = max/min/sum/abs/round on
  numbers/ranges; `len` previewed only (taught U09); `sorted`→list-sort excluded (concept_scan.py:451).
- `[FIXED]` **U07 metadata backing** ([sol]/[glm]): dropped `nested-loops`/`count-by-condition` from U07
  practices (no site); each kept tag now has a named site (loop-counter/accumulator/running-total via
  is_prime/gcd/fib/sum_to_n).
- `[FIXED]` **`random.choice`** ([fable]/[glm]): argument pinned to `range(...)`, never a list; the walk uses
  `randint(0, 1)` for left/right.
- `[FIXED]` **U07 L2 overload** ([fable]): moved `draw_polygon` to L3 as the scope application.
- `[FIXED]` **print-vs-return trap** ([fable]): pinned a concrete `TypeError: … NoneType` exercise + Notice.
- `[FIXED]` **cp03 shape** ([fable]/[glm]): 6–7 questions; two named pass-bar items in Grading; count_primes
  backs count-by-condition.
- `[FIXED]` **builtin facets** ([fable]): number-arg set only, round(2.5)==2 note, len previewed.
- `[FIXED]` **Phase C exercise floor** ([glm]/[fable]): ≥8 exercises, core ≤7, ≥2 stretch; closed-placeholder
  turtle starters restated.
- `[FIXED]` **§6 record reword** ([glm]): U08 realizes U07 intros via `requires`; U07 named sites listed.
- `[FIXED]` **U07 hook** ([fable]/[glm]): reframed from "refactor" to a genuine tool with a visible payoff.

### Round 2 (2026-09-23) — [self] APPROVE; [fable] APPROVE WITH NITS; [glm] APPROVE WITH NITS; [sol] REJECT.
All 5 round-1 blockers verified resolved by all three externals. [sol] found two more strict-scan-closure
gaps; [glm]/[fable] added non-blocking nits. Folded:
- `[FIXED]` ([sol]) cp03 `f-string` without `string-literal`: literal-bearing f-strings detect BOTH
  (concept_scan.py:14-15,279-285); `string-literal` (and `f-string`) placed in cp03 `requires` in round 3.
- `[FIXED]` ([sol]) U07 `error-messages` missing: L1's print-vs-return `TypeError` reading callback genuinely
  practices it (MANUAL_ONLY concept); added to U07 practices.
- `[FIXED]` ([sol] nit) seed wording corrected (requires a preceding `random.seed(4)`; bans `from random import`).
- `[FIXED]` ([glm]) Phase C citation: ≥6-heading+≥2-stretch is notebooks.py:583-587; ≥8/core≤7 is the
  plans-071–073 convention. `:53`→`:55` allowlist citation.
- `[FIXED]` ([glm]) U08 named sites: `accumulator` (trial tally `total = total + 1`), `builtin-functions`
  (`round`/`max` in the estimate report) named in L2.
- `[FIXED]` ([fable]) `fib` uses a temp var (no tuple assignment `a, b = b, a + b` — untaught); 60-min cut
  names `gcd` as deferrable; Monte-Carlo gets the quarter-circle π/4 picture + "1001 values/axis, not a
  1000×1000 grid"; cp03 seeded question STATEMENT tells the student to `random.seed(4)` first.

### Round 3 (2026-09-23) — [self] APPROVE; [fable] APPROVE; [glm] APPROVE WITH NITS; [sol] REJECT (narrow).
[sol]'s U07 `error-messages` fix confirmed RESOLVED; its one remaining finding: `string-literal` was in cp03
`practices` but not `requires`, mismatching my r2 fold-note ("requires+practices"). Verified the checkpoint
allowed set is `requires ∪ practices` (concept_scan.py:934-936) — so practices-only already closes the scan
(cp01/cp02 ship `string-literal` practices-only and pass). To satisfy [sol] AND [glm]'s "f-string→requires
prereq convention" without cross-field duplication, moved BOTH `f-string` and `string-literal` into cp03
`requires` and removed them from `practices`. [glm] nits folded: fold-note corrected; U08 L1 names the
`running-total` site (cumulative dice score); Phase C cp03 pin added (f-strings only, no `+` concat, no
boolean operators) to avoid unlisted `string-concat`/`logical-ops`; `scope` backed by a define-and-return
question. [fable] note folded (Monte-Carlo estimate ≈ π, not exact).

### Round 4 (2026-09-23) — re-dispatched [sol]/[glm]/[fable].
**CONSENSUS — [self] APPROVE; [sol] APPROVE; [glm] APPROVE; [fable] APPROVE.** All blockers resolved across
4 rounds; no open findings. **Plan-review gate PASSED.** Phase-C authoring note ([fable] r4): put the
"Monte-Carlo ≈ π, not exactly" line in the student-facing L2 prose too, not only teacher-notes.

## Content Review

### Round 1 (2026-09-23) — [self] APPROVE; [glm] APPROVE WITH NITS; [fable] APPROVE WITH NITS; [sol] REJECT.
Blind solves: [fable] 71/71 sample calls match; [glm] 25/25 items match; all tooling (turtle-check,
structure-check, concept-scan, exec-solutions ×3) PASS. One REJECT ([sol], value-distinctness + a fragile
assert). Dispositions (folded):
- `[FIXED]` ([sol] Must Fix) U08 Ex6 Monte-Carlo asserts use exact `==` → tolerance `abs(est-exp) < 1e-9`
  (consistent with "≈ not exact").
- `[FIXED]` ([sol] Must Fix) value-distinctness: varied the reused sample inputs `ticket_cost(4)`,
  `count_heads(12)`, and cp03 `is_prime(2/17)`/`sum_to_n(1/6)` so exercise/checkpoint inputs differ from the
  lesson and each other. ([glm] judged distinctness already held; the change satisfies [sol] at no cost.)
- `[FIXED]` ([sol]/[glm] Should Fix) added a `## Value plan (sample inputs)` inventory to all three
  teacher-notes (the plan promised it).
- `[FIXED]` ([sol]/[fable] Should Fix) U07 scope prose false claim ("a function cannot see a caller's
  variable" — false at module level) reworded to "should take what it needs via parameters"; added the
  concrete `print(angle)` → `NameError` demo in L3; fixed the same claim in teacher-notes' discussion prompt
  (draw_polygon returns `None`).
- `[FIXED]` ([fable] Should Fix) U08 quarter-circle picture was a straight diagonal (implies ×2) → redrawn
  curved + "arc bulges out → ≈78.5% = π/4, so ×4".
- `[FIXED]` ([fable] Should Fix) U07 teacher-notes gained the Jupyter print-vs-return trap (bare last-line
  call displays the value whether it returns or prints).
- `[FIXED]` ([sol] Should Fix) U08 teacher-notes "more trials necessarily closer" → "closer on average, not
  monotonic" (matches the lesson).
- `[FIXED]` ([glm]/[fable]) `solutions_ex7_polygon_tool.py` uses `turtle.left(angle)` and drops the
  student-visible in-function `assert … 1e-6`; the headless companion asserts non-vacuous values.
- `[FIXED]` nits: `len` one-sentence preview (U07 L2); randint-vs-choice + two-arg `round` notes (U08);
  cp03 Q5 shows `"Gold"` quoted, Q2 uses a temp var, redundant top-level seed removed; U07 second 60-min cut.
- `[WONTFIX]` ([sol]/[glm] Nice-to-Have) native-exec sandbox limitation (my ci-local ran native
  exec-solutions ALL GREEN); the "missing checkpoint lesson.ipynb" is a review-scope artifact (checkpoints
  ship `checkpoint.ipynb`, structure-check passes).

### Round 2 (2026-09-23) — CONSENSUS. [self] APPROVE; [sol] APPROVE; [glm] APPROVE WITH NITS; [fable] APPROVE.
All round-1 Must/Should findings verified resolved (blind re-solves match; all tooling PASS). No `[OPEN]`
items. Two residual non-blocking cosmetic nits folded for polish: cp03 Q5 worked-call block now quotes all
four returns (`"Silver"`/`"Bronze"`/`"Keep practicing"`, not just `"Gold"`); the U07 L3 scope demo cell
reframed so `draw_polygon` is clearly defined in context (the `.py`), leaving only the intended
`print(angle)` → `NameError` — ci-local ALL GREEN after both.

**Content-review gate PASSED (4-way consensus).** Proceeding to PR.

## Post-Execution Report

**Status: implemented, ci-local ALL GREEN (2026-09-23). Content-review gate next.**

- **Phase B (contracts):** 3 coverage-map entries (U07/U08/cp03) + 2 unit manifests + 1 checkpoint manifest +
  3 syllabus rows; coverage-check/prereq-check GREEN; 33→39 introduced-once, no dupes, no forward requires.
- **Phase C (statements + assets, Codex ×2):** U07 `lesson.ipynb` (Define & Call + print-vs-return TypeError
  Notice; is_prime/gcd/fib[temp var]/sum_to_n + number builtins; Scope + draw_polygon) + `exercises.ipynb`
  (9, function form, 2 stretch) + assets (l3_draw_polygon, ex7 starter). U08 `lesson.ipynb` (Chance/Simulate
  & Estimate/Random Walk; seed(4); Monte-Carlo π grid ≈3.1 with the quarter-circle picture) + `exercises.ipynb`
  (9) + assets (l3_random_walk [open-path], ex7 starter). cp03 `checkpoint.ipynb` (7 visible Questions,
  function form, seed(4) in the random question statement, scope via define-and-return).
- **Phase D (solutions, SEPARATE fresh Codex ×2):** U07/U08/cp03 `solutions.ipynb` (function form, define +
  assert several distinct cases; NO `import turtle`; 33/38/24 non-vacuous asserts; `random.seed(4)` before
  first random use, no `from random import`) + 2 turtle `solutions_*.py`.
- **Phase E (teacher-notes inline + verification):** teacher-notes for U07/U08/cp03 (full heading sets; cp03
  has `## Grading` with two named pass-bar items). `TMPDIR=/dev/shm bash scripts/ci-local.sh` → **ALL GREEN**
  (registry/lint, unit tests, notebook exec + hygiene, manifest/prereq/coverage/stretch, concept-scan,
  turtle-check, checkpoint questions, PDF, pre-merge-guard). Static audit clean: no `//`/`random.random`/
  tuple-assignment/`len`/`sorted`; module-level turtle; seed 4; random walk open-path.

No deviations from the approved plan.
