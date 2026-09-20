# Plan 057 — u05 function-factory: full real-input treatment (functions read-and-compute arm)

**Status:** DRAFT — plan-review gate pending.
**Type:** Content — apply the full real-input treatment (design 003 v5) to `unit-05-function-factory`.
**Branch:** `feature/plan-057-u05-real-input`. **Base:** main @ 0111f31.

## Motivation

Rollout slice 7 (design 003 §7 — list-less units). u05 introduces `def`/`parameters`/`return`/`scope`; its
solutions are **functions called with fixed arguments + asserts** (plus a few headless turtle-count
compute-and-print cells: Ex6/Ex9/Ex10, the u03 pattern). Treatment by **per-exercise audit** (design 003 v5):

- **Functions read-and-compute (the norm here):** keep the `def … return` **unchanged**, then reproduce the
  twin's **exact call+print structure** with **one `input(...)` read per distinct fixed VALUE** (a twin that
  calls twice reads both calls' args and prints both results — the u04 20→22 precedent) — a **bare call** for
  functions that PRINT their own output, `print(func(args))` only for return-only functions. Type per value:
  **string → plain `input(...)`**; **int → `int(input(...))`**; **float (e.g. lesson `area(7, 4.5)` / Ex4 `area(8, 2.5)`) →
  `float(input(...))`** (`float-type` is in u05's union). Labeled prompts, no `{i}` index (u05 has no lists).
- **Headless-compute read-and-compute** (Ex6/Ex9/Ex10 — no `def`, fixed shape param → counts): read the
  param(s), then the unchanged compute + print (the u03 arm).
- **Exempt** (design §1/§8 **v5** exemption taxonomy): Ex2/Ex7 (**debug/fix-the-error** — missing-parameter /
  scope repair), Ex5 (**predict/trace** — "trace on paper, predict the exact output"), Challenge 2
  (**reads-nothing/generator** — a written plan + predict of a turtle flower drawing, "do not run turtle here").

**Key per-unit difference from u03:** u05's concept union **includes `if-statement`/`elif-else`/`comparison`/
`while-loop`/`break-statement`** (they appear inside `def` bodies — Ex16/17 `if`, Ex18 `while`). So real-forms
**may legitimately contain if/while/comparison/break** (they are in-union); the closure scan forbids only
`sys.stdin` and any **out-of-union** concept — NOT if/while (contrast u03, which banned them because u03's
union lacked them). Authorities: design 003 **v5** (§1/§8 exemption taxonomy, §5 per-unit audit, §2/§3
list-less arm, §6); merged pilots u02/u04 (list-less read-and-compute) + u03 (headless compute + exemption).

## Metadata change (§5 — input add IS triggered for u05)

Unlike u03 (all-drawing lesson, markdown-only), **u05's lesson gains `no-exec` `input()` CODE cells** (the
per-lesson capstone real-forms, below) → `concept-scan` sees `input()` → the **`practices:[input]` add IS
required**, in sync in BOTH:
- `book1/units/unit-05-function-factory/manifest.yaml` — append `input` to `concepts.practices`.
- `book1/curriculum/coverage-map.yaml` — append `input` to the `unit-05-function-factory` `practices` list.

`input` is category `io` (concepts.yaml) — NOT a technique → cannot trip prereq/practice/technique-spiral.
Its prereq-validity flows from **map-order introduction** — `input` is introduced in u01 (first coverage-map
entry), so `prereq_findings` (ordered `seen` set) passes; it need not be in u05's `requires`-closure (u05's
ancestors are u01/u02/u03). No `introduces`/`requires` change. `int-type`/`type-conversion` are `never_flag`
(MANUAL_ONLY) so `int(input())` is safe; `float-type` is **in u05's union** (not never_flag — harmless here,
no float literals in real-forms) so `float(input())` is prereq-valid.

## Lesson both-forms audit (design §1/§8)

**The lesson's literal `**Put it together:**` moments are the turtle DRAWINGS (cells 11, 18, 25) — asset
excerpts that draw, reading nothing → EXEMPT (design §1 reads-nothing/generator).** Because u05 (unlike u03)
has *executable compute ladders* alongside the drawings, the **top executable rung of each compute ladder**
is treated as that lesson's **compute capstone** and gains a `no-exec` `input()` real-form. (This is the
u05-specific rule the later units u06/u08/u09 will reuse: turtle put-it-togethers exempt; compute capstone
gets the form.) All four compute capstones are already executable (run with fixed args) — none is input-only,
so **no executable twin needs adding**. The real-form mirrors the twin's **exact call+print structure**,
reading **one input per distinct fixed VALUE** (the u04 cells 20→22 precedent — reproduce the FULL output),
+ a `**Notice:**` "(It reads live input, so it does not run here.)", placed AFTER the executable cell:

| Lesson | Compute capstone (by content) | Twin calls | Real-form reads | Idiom / output to mirror |
|---|---|---|---|---|
| L1 (card factory) | `greeting_card(name, message)` (cell currently 9) | 2 calls (Ada/"Well done", Sam/"Happy birthday") | **4 reads** (name+message ×2) | plain `input(...)` ×4; **bare call** (fn PRINTS the card — no `print(...)` wrap); 2 cards of output |
| L2 (return) | `area(w, h)` (cell currently 13) | 1 call (7, 4.5) | **2 reads** (w, h — both float) | `float(input(...))` ×2; return-only → `card_area = area(w, h)` then the unchanged `message = f"The card area is {card_area} square units."` / `print(message)`. Line-for-line the twin (7→read, 4.5→read); EXACT §6c parity, no value-specific label |
| L3 (scope) | `pack_card(name)` (cell 20) | 1 call (Ari) | **1 read** (name) | plain `input(...)`; keep the fn's internal `print(factory_name)` + mirror `print(f"Packed: {first_card}")` |
| Algorithm Extension | `total_stamp_size(number_of_stamps)` (cell 28) | 1 call (3) | **1 read** (int) | `int(input(...))`; keep the twin's intermediate var: `three_stamp_total = total_stamp_size(...)` then `print(three_stamp_total)` (mirror the twin's exact call+print) |

**Build-up rungs (exempt from both-forms):** L1 cells 2/4/7 (`blank_card`, single-param `greeting_card`);
L2 `polygon_points(n)` (cell 15) — its two-shape demo prints value-specific labels ("A square …",
"A seven-sided …") that a general input program can't reproduce, so it stays an executable illustration/rung,
not a real-form capstone (this is why `area`, whose output has no value-specific word, is the L2 compute
capstone). Rungs teach one increment; only the compute capstone per lesson carries both forms (the plans
031–035/049 pedagogy; design §3). Reference cells by CONTENT during implementation — each inserted real-form
shifts the later indices.

## Per-exercise SHAPE table

**Universal real-form rule (per-task call shell):** the markdown real-form is the unchanged `def … return`
(or headless compute), with **one `input(...)` read per distinct fixed VALUE** the twin uses (u04 cells 20→22
precedent), then the **twin's exact call+print structure** — a **bare call** for functions that PRINT their
own output (wrapping in `print(...)` would emit a spurious `None`/duplicate line), `print(func(args))` **only**
for return-only functions; multi-call twins reproduce EVERY call (read each call's distinct args). Typed reads:
string → plain `input(...)`; int → `int(input(...))`; float → `float(input(...))`. Labeled prompts, no `{i}`
index (u05 has no lists). §6b parity compares the **computed-output lines only** (see Phase B).

| Shape | Exercises | Real-form + statement treatment |
|---|---|---|
| **read-and-compute — function** | Ex1 `cheer(name)` [str; **2 calls** Maya/Leo → 2 reads], Ex3 `show_double`/`get_double(number)` [**float** — twin `2.5`→`5.0`; real-form f-string uses `{number}` not the literal], Ex4 `area(w,h)` [**w,h both float** → `8.0*2.5=20.0`], Ex8 `turn_angle(n)`/`angle_message` [int], Ex11 `total_card_borders` [int], Ex12–Ex15 `count_bonus_stamps`/`total_even_stamps`/`stamps_in_triangle`/`average_side` [int; Ex15 returns float], Ex16 `stamps_that_fit`/`width_used(limit)` [int, `if` in body], Ex17 `stamps_to_pass`/`width_when_passed(limit)` [int, `if`], Ex18 `stamps_to_reach(target)` [int, `while`], Ex19 `count_jumbo_stamps(n, threshold)` [2×int], Ex20 `total_ribbon(n, start, growth)` [3×int], Challenge 1 `name_badge(name, club)` [2×str; **2 calls** → 4 reads; fn PRINTS → bare calls] | per the universal rule above; statement `**Real version:**` cue |
| **read-and-compute — headless compute** (no `def`) | Ex6 (`stamp_count` → last_pen_size, side_moves), Ex9 (`rows`,`columns` → stamps_drawn), Ex10 (`bands`,`stamps_per_band` → last_size, stamps_drawn) | read the shape param(s) via `int(input(...))`, then the unchanged compute + `print` (u03 arm); `**Real version:**` cue |
| **exempt — debug/fix-the-error** (design §1 v5 class 2) | Ex2 (`greeting_card` **missing-parameter repair**), Ex7 (`make_label` **scope/`NameError` repair**) — the graded task is the repair; reading `name` does not dissolve it (contrast u02 Ex4, where `int(input())` WAS the fix) | NO real-form; `**No real version:**` note (fix-the-error) |
| **exempt — predict/trace** (design §1 v5 class 3) | Ex5 (`player_label`/scope — "**Trace this code on paper … Predict the exact two output lines**") — reading input would defeat the prediction | NO real-form; `**No real version:**` note (trace-and-predict) |
| **exempt — reads-nothing/generator** (design §1 v5 class 1) | Challenge 2 (`flower`/`petal` — written PLAN + predict of a turtle flower **drawing**, "do not run turtle here"; notebook headless-computes petal COUNT only) | NO real-form; `**No real version:**` note (turtle drawing + predict) |

Notes: Ex3/Ex8/Ex16/Ex17 define TWO functions — the real-form reads the shared input once and mirrors
whatever the twin prints (both, or the primary). Homework Ex19/Ex20 stay read-and-compute (multi-arg labeled
prompts). Enrichment Ex11–Ex20 use small fixed data by design (§3 "small fixed data" drills) — the exec twin's
small data is untouched; the real-form carries arbitrary-count realism via the read.
**Read-and-compute: Ex1, Ex3, Ex4, Ex6, Ex8, Ex9, Ex10, Ex11–Ex20, Challenge 1 (18). Exempt: Ex2, Ex5, Ex7,
Challenge 2 (4).**

## The treatment (functions read-and-compute, hybrid forms)

1. **Real-input forms:** lesson `no-exec` `input()` CODE cells (the 4 capstones) + solutions.ipynb markdown
   fenced real-forms (every read-and-compute exercise). Exercise STATEMENTS get `**Real version:**` cues
   (Ch2 `**No real version:**`).
2. **No data growth / no rename.** Function + parameter names (`cheer`, `area`, `w`, `h`, `n`, `target`,
   `threshold`) are already clean and meaningful — keep verbatim. Fixed args are modest/realistic (§3
   list-less arm). Enrichment drills keep small fixed data.
3. **Per-task call shell (NOT a universal `print(func())`):** the real-form reproduces the twin's EXACT
   call+print structure — **bare call** for print-inside functions, `print(func(args))` only for return-only;
   **one read per distinct fixed VALUE**, so a twin that calls twice reads both call's args and prints both
   results. Typed reads: string → `input(...)`; int → `int(input(...))`; float → `float(input(...))`. Labeled
   prompts (`"Name? "`, `"Message? "`, `"Width? "`, `"Height? "`), **no `{i}` index** (u05 has no lists).
4. **Closure (u05-specific):** real-forms add `input`/`int`/`float` reads to the unchanged def/compute.
   **`if`/`elif`/`comparison`/`while`/`break`/`accumulator`/`running-total`/`string-literal` ARE permitted**
   (all in u05's union — they live inside the def/compute bodies). Forbidden: `sys.stdin`, `list`/`list-append`/
   `list-literal` (not in u05 union), any other out-of-union concept. `input()` lives ONLY in lesson `no-exec`
   cells + solutions markdown (never a solutions CODE cell — solution-policy ban).

## Phases

### Phase A — apply to u05 (lesson + exercises + solutions + metadata + coverage-map)
- **lesson.ipynb:** add a `no-exec` `input()` real-form + `**Notice:**` after each of the compute-capstone
  cells — currently **9, 13, 20, 28** (L2 capstone is `area` at cell **13**, NOT `polygon_points` at 15;
  reference by CONTENT, since indices shift on insert), per the both-forms table. Do NOT alter the executable
  capstones or the build-up rungs (incl. `polygon_points` cell 15).
- **exercises.ipynb:** `**Real version:**` cue on the 18 read-and-compute exercises (Ex1, Ex3, Ex4, Ex6, Ex8,
  Ex9, Ex10, Ex11–Ex20, Challenge 1); `**No real version:**` note (naming the exempt class) on Ex2/Ex7
  (fix-the-error), Ex5 (trace-and-predict), Challenge 2 (turtle-drawing + predict). (Ex4 cue: state both `w`
  and `h` are read with `float(input())`, so `8.0 * 2.5` prints `20.0` — matches the twin's assert. Ex3 cue:
  `number` is read with `float(input())` and the f-string uses `{number}` — do NOT re-quote the literal
  `Doubling 2.5 gives 5.0.` from the statement.)
- **solutions.ipynb:** markdown real-forms per the SHAPE table + per-task call shell (unchanged `def`/compute
  + one read per distinct fixed value + the twin's exact call/print), placed after each exercise's asserted
  twin. NO real-form under Ex2/Ex5/Ex7/Challenge 2. Fenced real-forms must not contain a line starting
  `## Exercise <digit>`.
- **metadata:** append `input` to `practices` in `manifest.yaml` AND `coverage-map.yaml` (in sync).
- **teacher-notes.md:** no change (pedagogy unchanged; real-forms are the established norm).

### Phase B — verification
- `ast.parse` + piped-run every real-form (lesson no-exec + solutions markdown); the **computed-output lines**
  == the paired executable twin's computed-output lines modulo `input()` prompt text (design §6a–c). "Computed
  -output lines" EXCLUDES the twins' pedagogy/CI-explanation sentences + assert-scaffolding prints (u04
  real-forms dropped those). Multi-call twins: read every call's distinct args and reproduce every result.
- CLOSURE AST scan: real-forms use only in-union concepts (input/int/float/def/return/for/while/if/elif/
  comparison/break/range/arithmetic/print/f-string); **NO `sys.stdin`, NO list/list-append**, no other
  out-of-union id.
- Hygiene: 0 `input()` in any solutions CODE cell; ≥3 non-vacuous assert cells; no fenced `## Exercise <digit>`
  line; lesson executable capstones + rungs unchanged.
- Metadata: `manifest.yaml` + `coverage-map.yaml` `input` add is in sync; prereq/coverage/concept-scan/
  technique-spiral GREEN (input is `io`, prereq-valid).
- `scripts/ci-local.sh` ALL GREEN.

## Out of scope
- Any Book-1 entry other than u05 (rollout continues per design 003 §7: u06, u08, u09, u10, cp02–04,
  projects). Turtle `assets/*.py` drawing files (separate artifact). No data growth, no rename. Phase B present.
- **In scope:** design 003 → **v5** (§1/§8 codify the full exemption taxonomy) — done in this plan, to resolve
  the round-1 [glm]/[fable] conflict over whether debug/predict tasks are exempt.
- **Parked errata (NOT fixed here):** exercises cells 27/30 point Ex9/Ex10 at `assets/ex10_*`/`ex11_*` (asset
  numbering off-by-one) — a pre-existing bug unrelated to this slice; log a separate errata entry post-merge.

## Plan Review

### Round 1 (2026-09-19) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.
#### [self] (2026-09-19)
- **Verdict**: APPROVE — with two self-noted watch-points for the gate:
  - Functions read-and-compute pattern (def unchanged + typed reads + call/print) is coherent; verified every
    solutions cell is a function call or headless compute on input-shaped data (Ex6/Ex9/Ex10 no-def compute,
    the u03 arm); float-type in u05 union → `float(input())` valid for `area`. Closure correctly differs from
    u03 (u05 union HAS if/elif/comparison/while/break → allowed in real-forms; only sys.stdin + list forbidden).
    Metadata add correct (lesson gains no-exec input() cells → `input` add to manifest+coverage-map, in sync;
    io category, prereq-valid via u01/u02/u04). Ch2 exempt (drawing+predict); Ex1–20+Ch1 read-and-compute
    (no predict/trace/debug among them — keyword scan confirmed only the two Challenges hit "predict").
  - **Watch-point 1 (both-forms):** L2 has TWO complete function demos — `area` (cell 13) and `polygon_points`
    (cell 15). I designated cell 15 the L2 capstone (real-form) and cell 13 the first-return build-up rung.
    If the gate reads `area` as an independent capstone it also needs a real-form; flagged for reviewer call.
  - **Watch-point 2 (two-function exercises):** Ex3/Ex8/Ex16/Ex17 each define TWO functions — the real-form
    reads the shared input once and mirrors whatever the twin prints (both, or the primary). Implementation
    must match each twin's exact printed lines.

#### [fable] (2026-09-19)
- **Verdict**: APPROVE WITH NITS — direction sound + verified (float-type in union; closure; input-add
  correctly triggered & prereq-valid; Phase B named); 2 Must + 4 Should to fold before Phase A:
1. `[OPEN]` Must: **Ex3 is FLOAT** — `get_double(2.5)` → use `float(input(...))` (int(input) on "2.5" raises);
   twin hardcodes `f"Doubling 2.5 gives …"` → real-form uses `f"Doubling {number} gives …"` (named §6c deviation).
2. `[OPEN]` Must: **`print(func(args))` wrong for print-style functions** — greeting_card (les 9), show_double
   (Ex3), player_label (Ex5→now exempt), name_badge (Ch1) print their own output & return None/print+return →
   wrapping emits a spurious `None`/double line. Rule: real-form mirrors the twin's call pattern EXACTLY;
   `print(func(args))` only for return-only functions.
3. `[OPEN]` Should: **multi-call parity rule** — les 9 calls twice (Ada/Sam), les 15 twice (4,7), Ex1 two names,
   Ch1 two badges. State per cell: real-form reads ONCE → one result, Phase B compares vs the twin's FIRST
   call, Notice explains the "one live card/angle" restructuring (u04 cells 54→56 precedent).
4. `[OPEN]` Should: **capstone labeling** — the lesson's actual `**Put it together:**` cells are the turtle
   DRAWINGS 11/18/25 (reads-nothing → exempt §1). Cells 9/15/20/28 are the top executable rung of each COMPUTE
   ladder → treat as the compute capstone that gains the real-form. State this explicitly (the u06/u08/u09 rule).
5. `[OPEN]` Should: **Ex5 is trace-and-predict → EXEMPT** (cell 14 "Trace on paper … Predict the exact two
   output lines") — the u04-Ex6 / u03-Ex8 class; `**No real version:**` trace-and-predict note (no compute half).
6. `[OPEN]` Should: **Ex2 (missing-param repair) + Ex7 (NameError scope repair) are fix-the-error** — record
   the class rule (reading `name` doesn't dissolve the repair). [self decision pending sol/glm: lean EXEMPT for
   consistency with u01 Ex2/3 + u03 Ex3/6, since the graded task is the repair.]
- Nice: (7) reference lesson cells by content, not shifting index; (8) reuse u04 Notice wording verbatim
  "(It reads live input, so it does not run here.)"; (9) Ex4 cue: both w AND h read `float(input())` (8.0*2.5=20.0);
  (10) PRE-EXISTING/out-of-scope errata: exercises cells 27/30 point Ex9/Ex10 to ex10/ex11 assets (off-by-one).

#### [sol] (2026-09-19)
- **Verdict**: REJECT (converges with [fable]):
1. `[OPEN]` Must: the universal "one read per parameter → `print(func(args))`" recipe breaks §6 parity — must
   specify **per-task call shells**: (a) multi-call twins (les 9 Ada/Sam, les 15 `4`/`7`, Ex1 two names, Ch1
   two badges) — one read-set can't reproduce both calls; (b) print-inside functions (Ex5[now exempt], Ch1) —
   `print(func())` duplicates the returned line; (c) les 15/20 need their labeled output ("A square turns…",
   "Packed: …"), not a bare printed return. Real-form must mirror the twin's exact call+print pattern.
2. `[OPEN]` Must: **Ex3 mistyped `[int]`** → `float(input(...))` (twin uses `2.5`, result `5.0`); float-type in union.
3. `[OPEN]` Should: lesson audit should RECORD the labeled `**Put it together:**` turtle drawings (cells 11/18/25)
   as reads-nothing exemptions (§1/§8), not claim 9/15/20/28 are the only lesson capstones.
- Closure, metadata sync, Ex6/9/10 headless-compute, Ch2 exemption, Phase B otherwise valid.

#### [glm] (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: REJECT (converges with [sol]/[fable]):
1. `[OPEN]` Must: read-count / §6c — several twins call with MULTIPLE distinct fixed values; the u04 precedent
   (cells 20→22: answer_1 AND answer_2 both become reads) is **one read per distinct fixed VALUE**, reproducing
   the FULL output. Fix the both-forms table + SHAPE: les 9 = 4 reads/2 calls; les 15 = 2 reads; Ex1 = 2; Ch1 = 4.
2. `[OPEN]` Must: **Ex3 `[int]`→`[float]`** (twin `2.5`→`5.0`).
3. `[OPEN]` Should: `print(func(args))` fails for print-inside defs (greeting_card/player_label/name_badge) —
   real-form calls BARE / mirrors the twin's call structure.
4. `[OPEN]` Should: codify which twin lines Phase B compares — "result line(s)" = the **computed-output lines**,
   EXCLUDING pedagogy/CI-explanation + assert-scaffolding prints (u04 real-forms dropped explanation lines).
- Nice: (5) prereq gloss imprecise — u04 is NOT in u05's requires-closure (ancestors u01/u02/u03); `input`'s
  prereq-validity flows from **map-order introduction (u01)** per `prereq_findings`; and `float-type` is in-union
  but NOT `never_flag` (MANUAL_ONLY = int-type/type-conversion only) — harmless (no float literals in real-forms).
  (6) closure list should also name `accumulator`/`string-literal` (in u05 practices, appear in Ex11–20).
- **CONFLICT with [fable]#5:** [glm] reads Ex2/Ex5/Ex7 as NOT exempt ("v4 exemption is reads-nothing/generator
  ONLY"); [fable] reads Ex5 as trace-and-predict → exempt. Root cause: the debug + predict/trace exemptions are
  applied-but-uncodified (u01/u02/u03/u04). **Resolution → codify the full exemption taxonomy in design 003 (v5).**
- Verified green: closure, metadata add necessary+sufficient (manifest↔map sync machine-enforced), Ex6/9/10
  headless, cells 9/15/20/28 culminating compute cells + 2/4/7/13 rungs + 11/18/25 turtle-drawing exempt, Phase B.

### Round 1 — outcome: REJECT (3 of 4). Fixed → round 2. **Design 003 amended → v5** (codify exemption taxonomy).
**Round 1 responses (plan + design revised):**
- → [FIXED] Recipe (Must, all 3): rewrote the treatment + both-forms table + SHAPE to **per-task call shells** —
  the real-form mirrors each twin's EXACT call+print structure, reads **one input per distinct fixed VALUE**
  (u04 20→22 precedent), reproduces the FULL output; **bare call** for print-inside functions (`print(func())`
  only for return-only); §6b parity compares **computed-output lines only** (excl. pedagogy/assert prints).
  Explicit per-cell reads: les 9 = 4 reads/2 calls, les 15 = 2/2, Ex1 = 2/2, Ch1 = 4/2.
- → [FIXED] Ex3 `[int]`→`[float]` (Must, all 3): `float(input())`; real-form f-string uses `{number}` not the literal.
- → [FIXED] Ex5 EXEMPT (trace-predict), Ex2/Ex7 EXEMPT (fix-the-error): **design 003 §1/§8 → v5** codifies the
  settled 3-class exemption taxonomy (debug/fix-the-error [unless the fix itself reads input]; predict/trace;
  reads-nothing/generator) applied across u01–u04 — resolving the [glm]/[fable] conflict at the authority level.
- → [FIXED] Lesson audit RECORDS the turtle `**Put it together:**` exemptions (cells 11/18/25, reads-nothing §1).
- → [FIXED] Nits: prereq gloss corrected (map-order/u01; float-type in-union not never_flag); closure list adds
  accumulator/string-literal; Notice wording verbatim; cells referenced by content. Errata (asset off-by-one) parked.
Re-dispatching round 2.

### Round 2 (2026-09-19) — re-review after round-1 fixes (d378e1a)
#### [fable] round 2 (2026-09-19)
- **Verdict**: APPROVE WITH NITS — all 6 round-1 findings resolved, nothing regressed (verified per item vs the
  notebooks + design v5). 4 non-blocking polish, all FOLDED:
1. `[FIXED]` Should: L2 cell-15 real-form would hardcode "square"/"seven-sided" while reading `n`.
   (Genericization was tried, then SUPERSEDED in round 2 by switching the L2 capstone to `area` — see Round 2
   responses; `area` reproduces its output line-for-line with exact parity, no deviation.)
2. `[FIXED]` Nit: Algo-Ext shell keeps the twin's intermediate var (`three_stamp_total = …; print(…)`).
3. `[FIXED]` Nit: version strings — design Status → v5; plan Type → v5.
4. `[FIXED]` Nit: Phase A now spells the Ex3 cue (`number` read with `float(input())`, f-string `{number}`).

#### [sol] round 2 (2026-09-19)
- **Verdict**: REJECT (Ex3 float, exemption taxonomy, 18/4 split, turtle exemptions, closure, metadata all sound):
1. `[OPEN]` Must: Motivation still carries the rejected "one read per parameter → print the result" recipe —
   contradicts the per-task call shell later. Rewrite the Motivation bullet.
2. `[OPEN]` Must: the L2 label genericization (`f"A {n}-sided shape turns …"`) violates §6b exact parity — the
   twin prints "A square …"/"A seven-sided …"; §6 does not authorize the deviation. → **Resolution: switch the
   L2 capstone to `area` (cell 13)** (genericizes with EXACT parity, no value-specific word); `polygon_points`
   (15) → return build-up rung. Removes the deviation entirely (supersedes [fable] R2 Should #1).
3. `[OPEN]` Nit: Motivation line 11 still cites design 003 v4 → v5.

#### [glm] round 2 (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: APPROVE — all 6 round-1 findings verified FIXED against the twins + tooling (read-count, Ex3
  float, bare-call rule, Phase B computed-output-lines, prereq gloss, closure list); the round-1 exemption
  conflict RESOLVED via design v5 (18/4 split cross-checked across all 22 tasks). No open blockers.
  (Reviewed the `polygon_points`-capstone version; the round-2 L2→`area` switch below is strictly cleaner —
  exact parity, no deviation — so it does not reopen anything [glm] flagged.) Cosmetic: design §9 v5 prose
  "u01–u04/u03" — the "/u03" is redundant.

### Round 2 — outcome: REJECT (1 of 4, [sol]); [glm] APPROVE, [fable] APPROVE-WITH-NITS. Fixed → round 3.
**Round 2 responses (plan + design revised):**
- → [FIXED] [sol]#1 (Motivation recipe): rewrote the Motivation "Functions read-and-compute" bullet to the
  per-task call shell (exact call+print structure, one read per distinct fixed VALUE, bare call for print-fns);
  dropped "one read per parameter" / "call and print the result".
- → [FIXED] [sol]#2 (L2 label parity): **switched the L2 compute capstone from `polygon_points` (15) to
  `area` (13)** — `area`'s output `"The card area is {card_area} square units."` genericizes with EXACT §6c
  parity (no value-specific word); `polygon_points` (15) → executable rung (its "square"/"seven-sided" labels
  can't be reproduced by a general input program). This supersedes the [fable] R2 genericization Should.
- → [FIXED] [sol]#3 nit + [fable] R2 #3: version strings → v5 (design Status + plan Type + Motivation).
- → [FIXED] [fable] R2 #1/#2/#4 already folded (L2 now moot; Algo-Ext keeps intermediate var; Ex3 cue spelled).
- → [FIXED] [glm] cosmetic: design §9 v5 "/u03" redundancy trimmed.
Re-dispatching round 3 (L2→area is a both-forms-table change — all three re-verify).

### Round 3 (2026-09-19) — re-verify after round-2 fixes (ba4586e)
#### [fable] round 3 (2026-09-19)
- **Verdict**: APPROVE WITH NITS — L2→area cleanly resolves the label-drift (verified: `area(7,4.5)`→
  `"The card area is 31.5 square units."`, real-form reads w,h floats → identical line, no deviation);
  Motivation now per-task call shell; all R2 nits folded; 18/4 split + taxonomy + closure + Phase B intact.
1. `[FIXED]` Nit: Phase A named stale cells "9, 15, 20, 28" → corrected to 9, **13**, 20, 28 (+ reference-by-content).
2. `[FIXED]` Cosmetic: annotated the [fable] R2 Should #1 record as superseded by the L2→area switch.

#### [sol] round 3 (2026-09-19)
- **Verdict**: REJECT — sole finding: Phase A line 121 still named stale targets "9, 15, 20, 28" (risk of
  adding a real-form to the `polygon_points` rung). The three substantive round-2 fixes otherwise verify
  correctly; 18/4 split, v5 taxonomy, closure, metadata, Phase B intact.
  → `[FIXED]`: Phase A corrected to "9, **13**, 20, 28" + reference-by-content (same fix as [fable] R3 #1;
  reviewed on ba4586e before the fix was applied). Re-confirming [sol] round 4.

#### [glm] round 3 (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: APPROVE WITH NITS — all 4 verification points confirmed (area exact §6c parity; polygon_points
  rung sound; Motivation = per-task call shell; no round-2 regressions). 2 findings, both stale/imprecise:
1. `[FIXED]` Should: Phase A stale "9, **15**, 20, 28" → corrected to "9, 13, 20, 28" (same as [sol]/[fable] R3).
2. `[FIXED]` Nit: Motivation float example "`area`'s `2.5`/`4.5`" imprecise → "lesson `area(7, 4.5)` / Ex4 `area(8, 2.5)`".

#### [sol] round 4 (2026-09-19)
- **Verdict**: REJECT — the round-3 fix had APPENDED the corrected "9, 13, 20, 28" while leaving the stale
  "9, 15, 20, 28" first line, so both appeared. → `[FIXED]`: Phase A rewritten to one clean line "9, 13, 20, 28"
  (the stale text now survives only in these review-record quotes). Re-confirming [sol] round 5.

### Round 3 — outcome: [glm] APPROVE-WITH-NITS, [fable] APPROVE-WITH-NITS (nits folded); [sol] R4 REJECT on a
duplicated-line artifact of the R3 fix, now cleanly corrected. Re-dispatching [sol] round 5 (single-line confirm).

## Content Review
_(pending — 4-way, post-implementation.)_

## Post-Execution Report
_(pending.)_
