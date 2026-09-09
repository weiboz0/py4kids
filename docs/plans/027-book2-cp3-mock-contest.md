# Plan 027 — Book 2 CP3 "Mock Contest 3"

> **For agentic workers:** run the full usaaio lifecycle (plan-review gate → Phase A → ci-local →
> content-review gate → PR → pre-merge-guard → squash-merge). Steps use checkbox syntax.

**Goal:** Ship `checkpoint-03-mock-contest-3` — the third timed mock contest, assessing Term-3 (U09
Recursion & Backtracking, U10 Stacks/Queues/Deques, U11 Number Systems/Bitwise/Number-Theory, U12 Binary
Trees, on the U01–U08 foundation) — on the `solve(data:str)->str` contract, following the shipped CP1/CP2
checkpoint pattern.

**Architecture:** A checkpoint entry (`checkpoint.ipynb` + `solutions.ipynb` + `teacher-notes.md` +
`manifest.yaml`). `checkpoint.ipynb` opens with contest framing (time budget + rules), then **7** timed
`## Question N` problems on the fixed allocation pinned in A1, each with an EMPTY student code cell.
`solutions.ipynb` mirrors the `## Question N` headings with pure `solve(data)` references and non-vacuous
asserts. Introduces nothing; requires the U09–U12 techniques it assesses (plus earlier introduces its
solutions genuinely use); practices the Book-1 + earlier-Book-2 concepts its solutions use.

**Tech Stack:** Jupyter notebooks (nbformat), `tools/` checks, `scripts/ci-local.sh`,
`py4kids-tools --book book2`; Python 3 stdlib only (no imports — deque is `from collections import deque`).

**Spec:** `docs/designs/001-book2-algorithms.md` (§7 Term-3 / CP3). NOTE: the design's contest-realism prose
is stale — §1 says "2–3 problems", but the shipped tooling (`checkpoint_question_findings`) requires 6–8, and
CP1/CP2 shipped 6; the ~40–50 min budget derives from `lessons: 0.5` + the CP1/CP2 precedent. `book2/
syllabus.md`; `book2/curriculum/coverage-map.yaml` (`checkpoint-03-mock-contest-3` entry — **its `requires`
currently OMITS `bitmask`; this plan ADDS it** so CP3 assesses U11's full concept set); the shipped
`book2/checkpoints/checkpoint-01-mock-contest-1/` and `-02-mock-contest-2/` (the exact pattern); plans 025
(U09/U10) and 026 (U11/U12) and all their content-gate lessons.

## Global Constraints

Copied from the design + registry + the CP1/CP2/U09–U12 gate lessons; every task's requirements include this.

- **Contract:** every reference solution is a pure `solve(data: str) -> str`; ZERO `input()` in any
  executable cell. The `import sys; print(solve(sys.stdin.read()))` wrapper is shown ONLY as a **markdown
  fenced block** in `checkpoint.ipynb` or teacher-notes — **NEVER as a code cell** (checkpoint code cells are
  ruff-linted with NO `no-exec` exemption — that exemption is `kind=="unit"` only — so a wrapper code cell's
  undefined `solve` fails cell-lint F821), and NEVER in solutions.ipynb (which both cell-lints AND executes).
  Deterministic. Every cell has an `id`.
- **Checkpoint structure (structure-check):** required files exactly `manifest.yaml`, `checkpoint.ipynb`,
  `solutions.ipynb`, `teacher-notes.md`. Problem headings are `## Question N` (NOT `## Exercise`) — **6–8,
  numbered sequentially 1..N** (this plan uses exactly 7). Student code cells are EMPTY (`''`). Checkpoints
  have NO stretch tier (a stretch tag is a FAIL). teacher-notes has exactly SIX headings — the five unit
  headings `## Goals`/`## Pacing`/`## Common mistakes`/`## Discussion prompts`/`## Differentiation` PLUS
  `## Grading` (points per question + total, and the time budget).
- **Closure — Term-3 material is now LEGAL; later material still BANNED.** Legal (≤ U12): recursion +
  backtracking (U09 — a named self-calling function is fine here); `deque` via `from collections import
  deque` with `.appendleft`/`.popleft`/`.append` and peek `stack[0]` (U10) + postfix-eval; `bitwise-ops`
  `& | ^ ~ << >>` (U11) with finite-width `~` masked `((1<<w)-1)`; base-conversion BY HAND; `bitmask`
  (`range(1<<n)`); iterative or recursive `gcd`; `sieve` (while/append, cross from `p*p`); modular-arithmetic
  (reduce-as-you-go); `tree-traversal` (recursion over parallel-array/dict trees, NO class); plus all
  ≤ U08 techniques. **STILL BANNED (not yet taught): NO `bfs`/`dfs`/`flood-fill`/`graph-repr` (U13 — a grid/
  tree question must not become a general graph traversal), NO converging `two-pointers`/sliding-window
  (U14).** **ALWAYS BANNED (course-wide): NO `.pop()`** (untaught — a stack is a `deque` `appendleft`+
  `popleft`); **NO `comprehension`** (dropped from Book 2 — concept-scan CANNOT catch it, so AST-check
  `ListComp`/`SetComp`/`DictComp`/`GeneratorExp`); **NO augmented assignment `+=`/`-=`/… (untaught — use
  `x = x + …`)**; NO `del`; NO list/string repetition `[x]*n`/`'0'*n` (build with while/append); NO chained
  comparison `a<=b<c` (use `b>=a and b<c`); set-ops via `.add`/`.discard`/`-` only (NEVER `.remove`/`&|^`-on-
  sets/`.union`/`.intersection`/`.difference`); NO untaught methods (`.join`/`.splitlines`/`.index`/`.count`/
  `.find`/`.pop`/`.bit_length`/`.bit_count`); NO base/number-theory shortcuts (`bin`/`hex`/`oct`/`format`/
  `int(x,base)`/f-string base format-specs `:b`/`:x`/`:X`/`:o` case-insensitive/`0b`/`0x`/`0o` literals
  either case/3-arg `pow(a,b,m)`/`divmod`/`math.*`); NO `sorted()`/`.sort` used to PRODUCE a tree traversal.
  Allowed builtins ONLY `{len,min,max,sorted,sum,abs,round}` — NO `all`/`any`/`enumerate`/`zip`/`reversed`/
  `map`/`filter`. **Output assembly:** `.join` banned → build multi-item output ONE concat per statement
  (`result = result + piece`; CPython in-place-optimizes this to O(n); the multi-concat `result = result +
  a + " " + b` form is O(n²) — the 439 s U11-Ex6 trap — so NEVER use it). concept-scan `--book book2` clean.
- **Enforcement split:** concept-scan + ad-hoc `detect()` for premature FEATURES (`graph-repr`/`two-pointers`
  are techniques — reviewer-enforced; `deque`/`recursion`/`bitwise-ops`/`tuple` are detected and must be
  LISTED) + untaught methods; an **AST check** for comprehensions (`ListComp`/`SetComp`/`DictComp`/
  `GeneratorExp`), augmented-assignment (`ast.AugAssign`), list/str-repetition (`ast.BinOp` Mult with a
  List **or Str** operand), chained comparison (`ast.Compare` len(ops)>1), f-string base format-specs
  (`FormattedValue.format_spec`); plus a **grep (code cells only, case-insensitive where noted)** for
  `\.pop\(`, `\.remove\(`, `\bdel\b`, `\.join\(`, `itertools`, `Counter`, `\bmath\b`, `from math`, `\bbin\(`,
  `\bhex\(`, `\boct\(`, `\bformat\(`, `\bpow\(`, `\bdivmod\(`, `\.bit_length`, `\.bit_count`, `0[bxo]` literal,
  the banned builtins, and `sorted`/`\.sort` in any traversal-output solution.
- **Two-tier metadata (a checkpoint ASSESSES its concepts):** `introduces: []`. `requires:` = EVERY U09–U12
  introduced concept the solutions USE — target set `[recursion, backtracking, deque, postfix-eval,
  base-conversion, bitwise-ops, bitmask, gcd, sieve, tree-traversal]` (10 concepts: **`bitmask` added** vs
  the current map, **`modular-arithmetic` removed** — not assessed, see Out of scope), PLUS any earlier
  introduce genuinely used (`input-parse`/`str-split`/`complete-search`/… — trim to those actually used).
  All 10 target concepts are used by the A1 allocation (Q1 recursion+backtracking, Q2 deque+postfix-eval,
  Q3 base-conversion, Q4 bitwise-ops+bitmask, Q5 gcd, Q6 sieve, Q7 tree-traversal); if a `detect()` trim
  would drop any of the 10, that is an A1-allocation bug to fix, not a metadata adjustment. `practices:` =
  `(used) − requires − introduces − wrapper-artifacts (file-read, import-statement)` = the Book-1 +
  earlier-Book-2 concepts the solutions use; NO U09–U12 introduce appears in `practices`.
  `requires ∩ practices = ∅`; manifest == coverage-map exactly (incl. list order); `lessons: 0.5`.
- **Non-vacuous asserts — each question's signature mutant (matched to its PINNED solver, per [sol]#3):**
  Q1 recursion/backtracking — the no-solution base case (e.g. `N` forcing a dead end → `0`), a path that
  must be un-marked before the next branch (a missing un-mark over-prunes → wrong count), a decisive-last
  value. Q2 postfix — operand ORDER for `-` (`5 3 -` → `2`, a swapped-operand mutant gives `-2`) and a
  decisive-last `+` token (no empty-stack edge: input is guaranteed valid). Q3 base-conversion — a decisive
  last bit, `0` (→ `"0"`), and an exact power of two. Q4 bitwise/bitmask — the EMPTY mask (sum 0) and the
  FULL mask both counted, and a mid-subset being the unique match (the bitwise witness is the `mask&(1<<i)`
  membership test). Q5 gcd — coprime (→ GCD 1), one value dividing another, all-equal. Q6 sieve — the
  PRIME-SQUARE boundary `N = 49` killing the `p*p` `<`-vs-`<=` mutant. Q7 tree-traversal — a single node, a
  left-only and a right-only skew, and a tree whose pre-order ≠ its values sorted (kills a `sorted()`
  shortcut). Decisive values last / last-after-sort.
- **Assessment integrity:** every problem solvable with ONLY ≤ U12 material (prereq closure); the seven
  collectively cover Term-3 — U09 (Q1), U10 (Q2), U11 (Q3 base-conversion, Q4 bitwise+bitmask, Q5 gcd, Q6
  sieve — 5 of U11's 6 techniques; modular-arithmetic excluded, see Out of scope), U12 (Q7); contest-
  appropriate difficulty for a timed sitting (no stretch tier). **Every output is an INTEGER or plain string
  — never a float.**

## Out of scope

- No new unit/technique/feature (introduces empty); no tooling change.
- **`modular-arithmetic` is intentionally NOT assessed by CP3 (removed from the map's CP3 `requires`).**
  Rationale: genuinely assessing modular-arithmetic's "reduce-as-you-go" core needs a dedicated problem whose
  UNREDUCED value is infeasible while the reduced computation stays fast (a power/factorial mod M) — a
  backtracking-count-mod-M (the natural fold into Q1) cannot, because the search visits ≥1 state per counted
  item so the count and the search cost scale together (plan-gate [sol]#2). Adding a dedicated 8th question
  worsens the already-tight ~40–50 min feasibility ([sol]#4/[fable]#4/[glm]#2). modular-arithmetic is taught
  and practiced in U11, and is **not a prerequisite of the capstone** (`project-03` requires does not list
  it), so omitting it from CP3 breaks no downstream closure. CP3 still assesses 5 of U11's 6 techniques
  (base-conversion, bitwise-ops, bitmask, gcd, sieve).
- **Verification is NOT out of scope:** Phase B is the named verification phase (blind-solve + mutation +
  full ci-local + 4-way content gate).

---

## Phases

### Phase A — checkpoint.ipynb + solutions.ipynb + teacher-notes + manifest

**Files:** Create `book2/checkpoints/checkpoint-03-mock-contest-3/{checkpoint,solutions}.ipynb`,
`teacher-notes.md`, `manifest.yaml`; Modify `book2/curriculum/coverage-map.yaml` (CP3 entry `requires` =
assessed set incl. `bitmask` + `practices` = used earlier concepts — both mirror the manifest).

**Interfaces:** Consumes U01–U12 introduced concepts + Book-1. Produces nothing (assessment leaf).

- [ ] **A1 — checkpoint.ipynb.** Opening markdown: contest title, the ~40–50 min time budget (matching
  `lessons: 0.5`), rules (each `solve(data)` reads the whole input string; the submission wrapper is shown as
  a markdown fenced block, NOT a code cell), a points-table pointer. Then EXACTLY 7 `## Question N`
  (sequential 1..7), each: `### <title>`, one-paragraph statement, `### Constraints`, `### Sample Input`,
  `### Sample Output` (```text fences), then an EMPTY code cell. **Fixed seven-question allocation (pinned to
  ONE concrete problem each — NO "or"/alternatives, per the sol plan-gate lesson):**
  - **Q1 — recursion + backtracking (U09):** count the number of ways to arrange all `N` distinct given
    values in a row so that **no two adjacent values differ by exactly 1** (a spaced-permutation count).
    Solve with a recursive backtracking search that marks a chosen value in a boolean `used[]`, recurses,
    and **un-marks it on return** (the undo is the point — a choose/skip subset search would NOT exercise
    backtracking). Output the integer count. `1 <= N <= 9`.
  - **Q2 — deque + postfix-eval (U10):** evaluate a valid space-separated postfix (RPN) expression with the
    operators `+ - *` using a `deque` as a stack (`appendleft` push, `popleft` pop — never `.pop`); output
    the integer result. (Input is guaranteed valid, so there is no empty-stack edge — the decisive mutants
    are operand order for `-` and a decisive-last `+` token.)
  - **Q3 — base-conversion (U11):** read a non-negative decimal integer and output its **binary** (base-2)
    representation, computed BY HAND (repeated `% 2` / `// 2`, digits assembled by `+` concat) — no
    `bin`/`format`/`:b`. Asserts pin a decisive last bit, `0`, and an exact power of two.
  - **Q4 — bitwise-ops + bitmask (U11):** given `N` item weights and a target `T`, count the subsets whose
    total equals `T` by enumerating every mask in `range(1 << N)` and testing membership with
    `mask & (1 << i)`. Output the integer count. `1 <= N <= 18`. Asserts exercise the empty mask (sum 0) and
    the full mask, and a mid-subset being the unique match. (Bitwise witnesses are `<<` and `&`, matching the
    solver; `|`/`^`/`~` are not used here.)
  - **Q5 — gcd (U11):** read `N` positive integers and output two space-separated values: the GCD of all of
    them and the LCM of all of them, computed with iterative Euclid (`while b != 0: a, b = b, a % b`) and
    `lcm = a // gcd * b`. Asserts cover coprime (GCD 1), one value dividing another, and all-equal.
  - **Q6 — sieve (U11):** read `N` and output the count of primes `p` with `2 <= p <= N`, using a Sieve of
    Eratosthenes whose boolean array is built with `while`/`append` (never `[False]*n`) and which crosses off
    multiples starting at `p*p`. One sample uses `N = 49` (= 7²) to pin the `p*p` `<=` boundary.
  - **Q7 — tree-traversal (U12):** over a binary tree given as parallel arrays (`N`, a root index, then
    `value left right` per node with `-1` for "no child", base-cased with `== -1` before indexing), output
    the **pre-order** traversal of the values, space-separated, via a recursive walk (NO class, NO `sorted()`
    — the sample tree's pre-order differs from its sorted order). Asserts cover a single node, a left-only
    and a right-only skew, and a tree whose pre-order ≠ its values sorted.
  Integer/plain-string outputs; decisive values last; multi-item output assembled ONE concat per statement
  (`result = result + piece` — never the O(n²) `result = result + a + " " + b` form).

  **modular-arithmetic is intentionally NOT assessed in CP3** — see `## Out of scope` for the rationale.
- [ ] **A2 — solutions.ipynb (FRESH author, blind).** Mirror `## Question N`; pure `solve(data)`;
  scanner-clean forms — recursion/backtracking with pop-free undo (`path + [choice]` or `path[:]=path[:-1]`,
  never `path=path[:-1]`/`del`/`.pop`); deque stack via `appendleft`/`popleft`; base-conversion/gcd/sieve by
  hand (NO `bin`/`hex`/`format`/`:b`/`int(x,base)`/`math`/3-arg `pow`/`divmod`); finite-width `~` masked;
  tree recursion over arrays (NO class, NO `sorted()`-traversal); multi-item output one concat per statement;
  NO comprehension/`+=`/list-or-str-repetition/chained-comparison/`.remove`/banned-builtins. Non-vacuous
  asserts per the mutation categories above. Every cell has an `id`; NO stored outputs.
- [ ] **A3 — teacher-notes.md.** The SIX headings incl `## Grading` (points per question + total, ~40–50 min
  budget); `## Pacing` frames the single timed 0.5-lesson sitting and — matching the CP1/CP2 teacher-notes
  posture — states students are **not expected to finish all seven**: bank the surest questions first, and
  the grading rewards partial completion (a student who solves 5 cleanly passes). Flag **Q1** (recursive
  backtracking) as the heaviest. A per-question Big-O line; which Term-3 unit/technique each question
  assesses. May carry the submission-wrapper snippet (allowed in `.md`).
- [ ] **A4 — manifest.yaml + map.** `introduces: []`; `lessons: 0.5`; `requires:` = the genuinely-assessed
  U09–U12 introduces — the **10-concept target set** `[recursion, backtracking, deque, postfix-eval,
  base-conversion, bitwise-ops, bitmask, gcd, sieve, tree-traversal]` (bitmask added, modular-arithmetic
  removed vs the current map) + earlier introduces genuinely used; `practices:` = `used − requires −
  introduces − wrapper-artifacts` (Book-1 + earlier-Book-2 concepts, incl. `dict-access` if used);
  `requires ∩ practices = ∅`; manifest == map (incl. order). Derive from an ad-hoc `detect()` over both
  notebooks; hand-add scanner-invisible used concepts (techniques). If `detect()` shows any of the 10 target
  concepts is NOT used, fix the A1 allocation (do not silently drop it from `requires`).

### Phase B — Verification (named verification phase)

- [ ] **B1 — blind-solve + mutation self-check** on both notebooks (the U09–U12 mutation categories above —
  every mutant fails an assert; every pristine solver passes). Run each `solve()` on its stated Sample I/O
  and confirm a match. Confirm each assessed U09–U12 technique is genuinely exercised; run the AST closure
  check (comprehension/`+=`/chained-comparison/list-or-str-repetition/format-spec) + grep (`.pop`/`.remove`/
  `del`/`.join`/base-modular-shortcuts/banned-builtins/`sorted`-in-traversal). Fix any vacuous assert by
  adding crafted asserts (pristine-pass + mutant-kill), never by changing a correct solver.
- [ ] **B2 — full `scripts/ci-local.sh` ALL GREEN both books** (orphan-kill first; foreground
  `TMPDIR=/dev/shm … > SCRATCHPAD/log`; log NOT in /dev/shm; no `| head`/`| tail`).
- [ ] **B3 — commit Phase A+B** on `feature/plan-027-book2-cp3`.
- [ ] **B4 — 4-way content-review gate** ([self]/[sol]/[glm]/[fable], read-only, HEAD-pinned): blind-solve
  all 7; mutation sweep (categories above); closure (AST + grep as in B1); `## Question N` 6–8 sequential,
  empty student cells, wrapper markdown-only (cell-lint clean); teacher-notes six headings incl `## Grading`;
  manifest==map, `requires` = assessed set (each genuinely used, `bitmask` included), `practices`
  Book-1/earlier-Book-2 only; each problem prereq-closed to ≤ U12; the seven collectively cover Term-3.
  Resolve every `[OPEN]`; re-verify in round-2 before consensus. (Note: `opencode`/[glm] has been flaky —
  may return a placeholder then re-notify async; re-dispatch if it yields a non-verdict.)
- [ ] **B5 — commit content-gate fixes, write the post-execution report**, re-run full `ci-local.sh` ALL
  GREEN — all precede the PR.
- [ ] **B6 — PR** → `pre-merge-guard.sh --pr` OK → squash-merge → delete branch → update memory.

## Post-Execution Report

_(filled at Phase B)_

## Plan Review

_(4-way plan-review gate — consensus before any implementation)_

### Round 1 (2026-09-09, HEAD 6766776) — [self] APPROVE · [fable] APPROVE WITH NITS · [glm] APPROVE WITH NITS · [sol] REJECT

Conventions/metadata-shape/closure/verification-phase confirmed sound by all four. Blocking + should-fix
findings (all addressed in the Round-2 revision at HEAD below):
1. `[FIXED]` [sol#1 = fable#1 = glm#3] A1 claimed "pin ONE concrete problem each" but 5 of 7 slots carried
   "or"/alternatives (Q1 arrangements/subsets, Q3 binary/hex, Q4 count/selection, Q6 prime-count/nth-prime,
   Q7 traversal/aggregation). → every slot now pinned to ONE concrete problem (Q1 spaced-permutation count,
   Q3 decimal→binary, Q4 subset-sum count, Q5 GCD+LCM, Q6 count primes ≤N, Q7 pre-order).
2. `[FIXED]` [sol#2, fable#2] Q1 folding modular-arithmetic was a FAKE assessment — a backtracking count
   can't force reduce-as-you-go (count and search cost scale together), and choose/skip subset-counting
   needs no undo so `backtracking` went unexercised. → Q1 is now a **spaced-permutation count with `used[]`
   mark/un-mark** (genuine backtracking undo); **modular-arithmetic dropped** from the assessed set (honest
   `requires`; rationale in Out of scope — it needs a dedicated power/factorial-mod problem and is not a
   capstone prereq).
3. `[FIXED]` [sol#3] Mandated mutants didn't match the (unpinned) solvers. → per-question signature mutants
   now match each PINNED solver (Q2 operand-order/decisive-`+`, no empty-stack since input is valid; Q4 `&`/
   `<<` witnesses only; Q6 prime-square `N=49`; Q7 pre-order ≠ sorted).
4. `[FIXED]` [sol#4 = fable#4 = glm#2] 7 dense problems in ~40–50 min feasibility risk. → A3 now states the
   CP1/CP2 partial-credit posture ("not expected to finish all seven; bank the surest; 5 clean passes") and
   flags Q1 as heaviest. Kept at 7 (within the 6–8 tooling bound; each question single-focus).
5. `[FIXED]` [fable#3] pin Q1's (N, M) so count > M. → moot: modular dropped; Q1 outputs a plain integer
   count (`N ≤ 9`).
6. `[FIXED]` [fable#5] A4 "trim to used" could shrink the assessed set. → A4 now says any of the 10 target
   concepts showing unused is an A1-allocation bug to fix, not a metadata trim.
7. `[noted]` [glm#4] adding `bitmask` is correct/prereq-closed (map omits it; U11 introduces it).

- **[self] Round 2 — APPROVE** (revision addresses every Must/Should above; design now honest + pinned).
- **[sol]/[glm]/[fable] Round 2 — _pending_**

## Content Review

_(4-way content-review gate — findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`, all resolve before merge)_
