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
  base-conversion, bitwise-ops, bitmask, gcd, sieve, modular-arithmetic, tree-traversal]` (**bitmask added**
  vs the current map), PLUS any earlier introduce genuinely used (`input-parse`/`str-split`/`complete-search`
  /`grid-2d`/… — trim to those actually used). `practices:` = `(used) − requires − introduces −
  wrapper-artifacts (file-read, import-statement)` = the Book-1 + earlier-Book-2 concepts the solutions use;
  NO U09–U12 introduce appears in `practices`. `requires ∩ practices = ∅`; manifest == coverage-map exactly
  (incl. list order); `lessons: 0.5`.
- **Non-vacuous asserts (the U09–U12 mutation categories):** each reference solution carries the sample
  assert PLUS crafted edge cases killing the technique's signature mutants — backtracking: the base case
  (empty/no-solution → correct empty answer), a must-undo path, a decisive-last choice; deque/postfix: the
  LIFO order, an empty-stack/unbalanced edge, a decisive-last token; base-conversion: a decisive last digit/
  bit + a 0/power boundary; bitwise/bitmask: `&` vs `|` vs `^` differ, empty+full mask, finite-width `~`;
  gcd: coprime(→1)/one-divides/equal; sieve: the PRIME-SQUARE boundary (e.g. bound 49); modular: a
  brute-force-checkable case + a wrong-operand / missing-final-`%M` mutant (NO reduce-midway-vs-end assert —
  impossible in Python); tree-traversal: single node, left-only & right-only skew, a pre/in/post-
  distinguishing tree (graded traversal output PRE/POST-order so `sorted()` can't shortcut). Decisive values
  last / last-after-sort.
- **Assessment integrity:** every problem solvable with ONLY ≤ U12 material (prereq closure); the seven
  collectively cover Term-3 (see A1); contest-appropriate difficulty for a timed sitting (no stretch tier).
  **Every output is an INTEGER or plain string — never a float.**

## Out of scope

- No new unit/technique/feature (introduces empty); no tooling change.
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
  - **Q1 — recursion + backtracking + modular-arithmetic (U09/U11):** count the arrangements/subsets meeting
    a stated rule via a recursive backtracking search, and report the count **modulo `M`** (the count can be
    large; reduce as you go). Small N bound.
  - **Q2 — deque + postfix-eval (U10):** evaluate a valid space-separated postfix (RPN) expression with a
    `deque` used as a stack (`appendleft`/`popleft`, never `.pop`); integer result.
  - **Q3 — base-conversion (U11):** convert a value between decimal and a stated base (binary or hex) BY
    HAND; a decisive last digit and a boundary (0 / a power) in the asserts.
  - **Q4 — bitwise-ops + bitmask (U11):** enumerate subsets of a small set via `range(1<<n)` + `mask&(1<<i)`
    and report a count/selection (the empty and full masks both exercised).
  - **Q5 — gcd (U11):** GCD/LCM over a list (iterative Euclid; `a // gcd * b`; the zero/coprime/equal edges).
  - **Q6 — sieve (U11):** count primes ≤ N (or the nth prime) via a sieve built with while/append, crossing
    off from `p*p`; a sample whose bound is a prime square (e.g. 49).
  - **Q7 — tree-traversal (U12):** over a binary tree given as parallel arrays (root index, `-1` sentinel
    base-cased with `== -1`), produce a PRE- or POST-order output or a recursive aggregation (height/leaf/
    sum) — NOT in-order (so `sorted()` can't shortcut); single-node + skew in the asserts.
  Integer/plain-string outputs; decisive values last; multi-item output assembled one concat per statement.
- [ ] **A2 — solutions.ipynb (FRESH author, blind).** Mirror `## Question N`; pure `solve(data)`;
  scanner-clean forms — recursion/backtracking with pop-free undo (`path + [choice]` or `path[:]=path[:-1]`,
  never `path=path[:-1]`/`del`/`.pop`); deque stack via `appendleft`/`popleft`; base-conversion/gcd/sieve by
  hand (NO `bin`/`hex`/`format`/`:b`/`int(x,base)`/`math`/3-arg `pow`/`divmod`); finite-width `~` masked;
  tree recursion over arrays (NO class, NO `sorted()`-traversal); multi-item output one concat per statement;
  NO comprehension/`+=`/list-or-str-repetition/chained-comparison/`.remove`/banned-builtins. Non-vacuous
  asserts per the mutation categories above. Every cell has an `id`; NO stored outputs.
- [ ] **A3 — teacher-notes.md.** The SIX headings incl `## Grading` (points per question + total, ~40–50 min
  budget); `## Pacing` frames the single timed 0.5-lesson sitting; a per-question Big-O line; which Term-3
  unit/technique each question assesses. May carry the submission-wrapper snippet (allowed in `.md`).
- [ ] **A4 — manifest.yaml + map.** `introduces: []`; `lessons: 0.5`; `requires:` = the genuinely-assessed
  U09–U12 introduces (the 11-concept target set, incl. `bitmask`, trimmed to those actually used) + earlier
  introduces used; `practices:` = `used − requires − introduces − wrapper-artifacts` (Book-1 + earlier-Book-2
  concepts, incl. `dict-access` if used); `requires ∩ practices = ∅`; manifest == map (incl. order). Derive
  from an ad-hoc `detect()` over both notebooks; hand-add scanner-invisible used concepts (techniques).

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

## Content Review

_(4-way content-review gate — findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`, all resolve before merge)_
