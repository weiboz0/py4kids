# Plan 072 — Book 1b Units 04 (Loops & Counting) + 05 (For & Range) + Checkpoint 02

**Origin:** Book 1b buildout (standing directive, "full book 1b implementation").
**Design:** `docs/designs/005-book1b-concept-first.md` §3 (unit table + checkpoint boundaries), §5, §6, §7.
**Template:** Units 01–03 (plans 070–071) — clone their shape; follow all authoring guardrails below.

## Scope

Two adjacent pre-function loop units + their checkpoint (U05 is a checkpoint boundary, design §3):
- **U04 — Loops & Counting** (`while`), **U05 — For & Range**, **checkpoint-02 — Loops** (assesses U01–U05).
Book 1b stays `buildout: true`.

## Coverage-map entries (the contract)

**unit-04-loops-and-counting** — `lessons: 3`
- introduces: `[while-loop, break-statement, loop-counter, accumulator, sentinel-loop, running-total, count-by-condition]`
- requires: `[if-statement, comparison, arithmetic, int-type, boolean, variable, print]`
- practices: `[elif-else, f-string, string-literal, naming, comment, error-messages]`

**unit-05-for-and-range** — `lessons: 3`
- introduces: `[for-loop, range-function, nested-loops]`
- requires: `[while-loop, accumulator, loop-counter, arithmetic, comparison, if-statement, variable, print]`
- practices: `[running-total, count-by-condition, accumulator, boolean, elif-else, conditional-nesting,
  break-statement, string-concat, int-type, f-string, string-literal, naming]`

**checkpoint-02-loops** — `kind: checkpoint`, `lessons: 0.5`
- introduces: `[]`
- requires: `[print, variable, while-loop, for-loop, range-function, accumulator, if-statement, comparison, arithmetic, f-string]`
- practices: `[print, variable, while-loop, break-statement, loop-counter, accumulator, running-total,
  count-by-condition, sentinel-loop, for-loop, range-function, nested-loops, if-statement, elif-else,
  comparison, boolean, arithmetic, int-type, f-string, string-literal]`
  - Checkpoints stay STRICT (no fastforward): every id is introduced by U01–U05, so `checkpoint_findings`
    passes. Loops are NOW taught, so checkpoint-02 uses them — but no lists (U10), no builtins (`sum`/`len`, U07).

Closure (strict over `requires`) holds in order; no entry practices its own introductions (U05's
`running-total`/`count-by-condition`/`break-statement`/`accumulator` are U04 introductions, legal). Metadata
is honest to content (every id is genuinely used — see the §6 record + guardrails for where each lands).

### Design §6 practice-coverage record (manual, per-plan)

After U01–U05 + checkpoint-02, every one of the 30 concepts introduced through U05 is practiced ≥ once:
- **`conditional-nesting`** (U03, previously deferred) → **U05** nested-classify exercise (`if` inside `if`
  inside a `for`).
- **`sentinel-loop`** (U04) → **checkpoint-02** "repeat until a computed stop value" question (Collatz-style).
- U04's `while-loop`/`break`/`loop-counter`/`accumulator`/`running-total`/`count-by-condition` → practiced in
  U05 and checkpoint-02. `string-concat` (U01) → U05 row-building (`row = row + "*"`). `logical-ops` (U03),
  `float-type`/`type-conversion` (U02), `input`/`run-program` (U01) remain practiced by earlier
  units/checkpoint-01 (unchanged). U05's `for`/`range`/`nested-loops` → checkpoint-02.
The capstone practice-coverage anchor stays dormant (buildout) until the Algorithm Challenge.

## Key teaching notes

- **U04 is `while`-only** (no `for`/`range`/lists). Counting uses a manual counter
  (`i = 0; while i < n: … ; i = i + 1`). **`accumulator` (`x = x + …`) becomes formally taught / student-
  authored at U04** — it was previewed once in U02's boxed 5050 peek (tagged `accumulator`) but never in
  graded U01–U03 content. **Cash in the continuity:** U04's running-total section points back to the 5050
  peek ("you saw this in Unit 02 — now you write it"), and **U05's first `for` example reproduces the 5050
  sum** as `for n in range(1, 101): total = total + n`.
- The three technique concepts land as ordinary concepts: **sentinel-loop** = "repeat until a *computed*
  stop value" (Collatz until `n == 1`; digit-peel until `n == 0`; double until `> 1000`) and the general
  `while True: … if …: break` shape — **never `input()`-driven, never a list walk** (no collection yet).
  **running-total** (accumulate a sum), **count-by-condition** (count how many pass a test).
- **U05** introduces `for`/`range`/`nested-loops`, reusing accumulation/counting over `range`.

## Authoring guardrails (Phase C/D) — folds plan-review [fable]/[sol]/[glm] r1

- **`+=` decision:** lessons, exercise statements, and solutions use `x = x + 1` ONLY; `+=` appears at most
  as a Notice ("Python also allows `x += 1`"). Before the first loop, U04 shows an explicit **reassignment
  rung**: `count = 0; count = count + 1; print(count)` with a Notice "the right side is computed with the
  OLD value, then saved" — the one conceptual hurdle of the unit.
- **No `sum`/`len`/`min`/`max`/`abs`/`round`** (builtins, U07): sums/counts use the accumulator idiom.
- **Printing:** no `end=` / `sep=` / format specs (`:3`, `:.2f`). Same-line/tabular output is built by
  **string accumulation** — inner loop does `row = row + "*"` (or `row = row + f"{i*j} "`), then `print(row)`
  once after the inner loop (this is also the clearest nested-loop teaching, and makes each row assertable).
  `"*" * i` string-repetition is NOT catalog — use the inner-loop accumulation for core; allow `"*" * i`
  only as a Notice/Challenge shortcut *after* the nested version.
- **House solution form for loop output** (design §7 was locked for straight-line code): prefer exercises
  whose graded output is a **single summary line after the loop** (`Steps: 111`, `Sum: 5050`, `Count: 47`)
  asserted in house form, AND assert the loop **state** (`assert total == 5050`). For multi-line output,
  `line = f"…"; print(line)` inside the loop with in-loop asserts on chosen iterations
  (`if i == 1: assert line == …`, `if i == 5: assert line == …`) plus an iteration-count assert; triangles/
  tables assert the accumulated `row` on the first and last rows. Use only U01–U05 concepts (no list-of-lines).
- **Termination:** every loop terminates; a `while` advances its counter/condition each pass; `while True:`
  only with a guaranteed-reachable `break`. **Deliberate beats:** (a) a `no-exec`-tagged infinite-loop cell
  showing the forgotten `i = i + 1` + a Notice on why it never stops **and how to stop it (Kernel → Interrupt /
  Ctrl-C)** — teacher-notes Common mistakes must carry the interrupt instruction; (b) an off-by-one repair
  (the U03 "Repair" slot): contrast `while i < 5` (0–4) vs `while i <= 5` (0–5); for `range`, a Notice "the
  stop value is not included" + ≥1 exercise whose output only matches with the right bound.
- **`range` forms:** teach `range(n)` (from 0) and `range(a, b)`; 3-arg `range(a, b, step)` Notice/Challenge
  only (evens via `if n % 2 == 0`). **Nested loops:** use `row`/`col` names (not `i`/`j`), a Notice on the
  8-space inner body + the dedent trap (`print(row)` at 4 vs 8 spaces), a Notice that `break` exits only the
  inner loop, and never modify the `for` variable in its body.
- **Concept beats to pin:** factorial initializes `product = 1` (not 0) with a Notice (n ≤ 10);
  GCD-by-subtraction teacher-note intuition ("any common divisor of a and b divides a − b") + a trace for
  (48, 18), positive operands, `%`-Euclid Challenge-only; **primality** (U05) uses a boolean **flag**
  (`is_prime = True; … is_prime = False; break`) taught as a rung with a Notice, and the `range(2, 2)`-empty
  edge for `n == 2`; **digit-sum** (a `while` peeling `n % 10`, `n // 10`) is included as the bridge from U02's
  digit split. **`boolean`** is practiced via the primality flag / a printed comparison; **`elif-else`** via a
  FizzBuzz-over-`range` exercise (U05) and count-by-condition tiers (U04); **`comment`** via commented loop code.
- `//`/`%` non-negative; floats printed exactly; pre-function (no `def`); ≥8 exercises/unit, **core ≤7** +
  extra + ≥2 Challenge; solution-free student notebooks, no outputs, no `input()` in graded code (fenced
  try-it only); unique cell ids; problem-first openings; 60-MINUTE CUT line in each teacher-notes.
- **checkpoint-02 mix** (6–8 questions, declared so grading keys each to its concept(s)): ≈2 U01–U03 recap
  (one `elif` ladder, one `//`/`%` or traceback); **≥1 `while` with a counter or `break`**; **≥1 sentinel
  "repeat-until"** (Collatz-style — backs `sentinel-loop`); **≥1 `for`/`range` running-total**; **≥1
  count-by-condition over a range**; **≥1 nested-loop** (times table via `row` accumulation). Strict (no
  lists/builtins). Grading names the `while`-counter and the `for`-running-total as the pass-bar items.

## Lesson-by-lesson outline (so 7 U04 intros don't all land in L1)

- **U04:** L1 `while` + `loop-counter` + the infinite-loop and off-by-one beats (reassignment rung first);
  L2 `accumulator` → running-total (the 5050 cash-in) → count-by-condition (elif tiers); L3 `break` +
  sentinel (Collatz/`while True`+break) + Final build.
- **U05:** L1 `for`/`range` (reproduce 5050) + `range` bounds Notice; L2 accumulate/count over `range` +
  primality with the flag + `break` + FizzBuzz (elif); L3 nested loops → times table / number triangle
  (row accumulation) + a nested-classify exercise (`conditional-nesting`) + Final build.

## Phases

### Phase A — plan-review gate (4-way). No implementation until consensus.
### Phase B — contracts: append the 3 coverage-map entries + 3 syllabus rows + 3 manifests; `--book book1b coverage-check` + `prereq-check` GREEN.
### Phase C — statements (Codex, gpt-5.6-sol): each unit's lesson+exercises; checkpoint.ipynb. Follow every guardrail + the outline.
### Phase D — solutions (SEPARATE fresh Codex): each unit's + the checkpoint's solutions.ipynb (house form incl. the loop-output adaptation; mirror headings).
### Phase E — teacher-notes (inline) + verification: `teacher-notes.md` per unit + checkpoint grading notes;
full `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN across the three books; exec-solutions/exec-lessons
clean; ≥2 stretch/unit; openings are problems; the 5050 reproductions execute. Scope allowlist = this plan +
the U04/U05 unit trees + `book1b/checkpoints/checkpoint-02-loops/` + coverage-map + syllabus.

## Out of scope

- U06–U13, the later checkpoints, the Algorithm Challenge — plans 073+.
- No tooling/governance/Book-1/Book-2 changes. Not an erratum.
- **Verification phase:** Phase E is the named verification phase (units + checkpoint → required).

## Plan Review

### Round 1 (2026-09-22) — [self] APPROVE; [fable] APPROVE WITH NITS; [sol] REJECT; [glm] REJECT.
All three verified closure/schema/strictness PASS; the REJECTs were the shared §6 practice-coverage gap.
FOLDED:
- **Blocker (§6):** `conditional-nesting` (U03) now practiced in **U05** (nested-classify), `sentinel-loop`
  (U04) in **checkpoint-02** (Collatz "repeat-until"); a **§6 practice-coverage record** section added
  (the omission that REJECTed 071 r1). ([sol]#3, [glm]#1)
- **Metadata honesty:** U05 `requires` += `if-statement`; U05 `practices` += `accumulator`/`conditional-
  nesting`/`string-concat`; U04 `requires` += `boolean` (while-True/flag) and dropped it from practices;
  `elif-else` backed by FizzBuzz (U05) + count tiers (U04); `comment` by commented loop code. ([glm]#2/#3/#4,
  [sol]#2, [fable])
- **Guardrails (all [fable] P1–P3):** the `+=` rule + reassignment rung; no `end=`/`sep=`/format specs +
  string-accumulation rows; `"*"*i` core-forbidden; concrete sentinel definition (no `input()`/lists);
  **house-form adaptation for loop output**; infinite-loop `no-exec` beat + interrupt instruction; off-by-one/
  `range`-bounds rungs; factorial `product=1`, GCD intuition, primality flag + `range(2,2)` edge, digit-sum;
  a **lesson-by-lesson outline**; a **declared checkpoint mix** + concept-keyed grading.
- **Wording:** "accumulator forbidden in U01–U03" → "formally taught / student-authored at U04" (U02's 5050
  peek previewed it). ([sol]#6, [fable])

#### [self] round 1 — APPROVE (superseded by the folds above: original draft omitted the §6 record + the
loop-specific guardrails). Closure/partition were correct.

### Round 2 (2026-09-22) — revised with the §6 record, honest metadata, the full guardrail set, the lesson
outline, and the declared checkpoint mix. Re-dispatching [sol]/[glm]/[fable].
_(Awaiting round-2 verdicts.)_

## Content Review

_(4-way content-review gate — filled before PR.)_

## Post-Execution Report

_(Filled before shipping.)_
