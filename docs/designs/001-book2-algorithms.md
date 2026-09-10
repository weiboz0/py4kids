# Book 2 — Algorithms & Data Structures (Year 2) Design Spec

**Status:** design, pending user review → then per-plan implementation via the usaaio lifecycle.
**Supersedes** the design-000 §Scope sketch of Book 2 ("OOP, algorithms, data, larger builds"):
per user direction (2026-09-07), Book 2 is **algorithms & data structures for contest preparation**;
**OOP and software-engineering are deferred to a later book.**

## 1. Charter & target

Book 2 turns a Book-1 graduate (one year of Python fundamentals) into a capable entry-level
competitive programmer and ACSL contestant. Concretely it prepares students for:

- **USACO Bronze** (mastery) **→ easy Silver** (exposure), and
- **ACSL** Junior/Intermediate (and the overlapping Senior topics).

**Language:** Python continues (accepted by USACO through Bronze/easy Silver; sufficient for ACSL's
one program). No second language — depth goes into algorithms, not syntax.

**Delivery:** **problem-first** — every unit opens with a motivating contest problem, teaches the
technique that cracks it, then drills a **rich, laddered problem set**. Proficiency-through-volume is
a first-class goal: problem sets are generous (target ~8–15 problems per unit, difficulty-laddered,
`stretch`-tagged hardest), most solved as self-paced homework.

**Contest realism:** checkpoints are **timed mini mock-contests** (6–8 questions, a real time limit,
teacher-run clock); the capstone is a **full mock contest** spanning the year.

**Non-goals (deferred to a later book):** OOP, software engineering, LISP, regular expressions /
finite-state automata, assembly-language programming, digital electronics. These do not serve a
Python algorithms/problem-solving course.

## 2. Prerequisite surface (what Book 1 leaves)

Book 2 may assume, without re-teaching: variables & I/O, arithmetic, strings (index/slice + the
`upper/lower/strip/replace` methods — **not** `.split`), booleans/comparison/logical-ops,
`if/elif/else`, `for`/`while`/`break`/`range`, `loop-counter`/`accumulator`, `nested-loops`,
functions (`def`/params/return/scope), lists (literal/index/append/`.sort`, `len`/`max`/`min`),
dicts (literal/access/`.items`/`.get`), files (`open`/`with`/`for line in f`), `random`, `import`,
and a gentle class intro (Book 1 unit 10 — used only incidentally in Book 2, not built upon).

**Deliberately NOT in Book 1, so Book 2 must teach as enabling machinery:** input parsing (`.split`,
reading `N` then `N` lines, reading a grid), **sets**, **tuples**, `sorted(key=…)`, list
comprehensions (introduced sparingly), **recursion**, 2D grids, and any complexity vocabulary.

## 3. The stdin-first, subprocess-judged contract (binding CI convention)

> **Amended by plan 036 (2026-09-10).** Book 2 originally used a pure-function `solve(data: str) ->
> str` contract verified by inline asserts. The user found the `solve()` wrapper an extra abstraction
> barrier (real contest code reads stdin) and chose a stdin-first re-architecture. **Migration is
> staged, per entry:** an entry is on the NEW model once it ships an `assets/` dir with `.py` solvers;
> until then it stays on the OLD `solve()`+asserts model (still verified by `exec-solutions` + the
> ≥3-assert policy). Both models coexist during the rollout.

The binding contract for a migrated entry:

- **Every reference solution is a real contest `.py` script** in the entry's `assets/` dir: it reads
  the whole input from stdin (`data = sys.stdin.read()` or line-wise `input()`), computes, and
  `print`s the exact output. No `solve()` wrapper is required.
- **Verification is a subprocess judge (`judge-check`):** each solver runs with a committed
  `assets/<pid>/<k>.in` piped to stdin and its stdout **token-compared** (`split()`) to
  `assets/<pid>/<k>.out`. **PIDs**: `exN` (from `## Exercise N`), `qN` (`## Question N`), `pN`
  (`### Problem N`), and lesson solvers `lN` (from `manifest.lessons`).
- **Non-vacuous discipline (carried from Book 1):** **≥2 fixture pairs per solver** — the stated
  sample **plus ≥1 crafted edge/larger case** whose decisive value is boundary/last, so a wrong
  solution fails. Content gates mutation-check this (mutate the `.py`, re-run the fixtures).
- **Lessons** build each algorithm as a graduated worked-example ladder — executable cells on tiny
  literal data → the full stdin solver shown as a **`no-exec` cell mirroring its `.py`** (run as
  `python assets/<pid>.py < assets/<pid>/1.in`) + an edge rung + a complexity note.
- **`solutions.ipynb`** is a teacher-facing, all-`no-exec` display notebook mirroring each solver
  `.py` (drift guarded by `judge-check`'s mirror check).
- **The always-banned, scanner-blind surface** (chained comparison, `[x]*n`, ternary, `+=`,
  comprehensions, `global`/`nonlocal`, `del`, `itertools`/`Counter`, `.pop`/`.join`/…, non-allowlist
  builtins) is mechanically enforced by **`source-policy`** over lesson cells + solver `.py`.
- Determinism is free — **no `random`/seeding**. **Complexity is taught, not CI-enforced** (intended
  Big-O in teacher notes; no CI time limits).

## 4. Content-as-code structure (reuses Book 1's machinery)

Each unit keeps the proven file set so existing tooling transfers: `lesson.ipynb` (opens on the
motivating problem, teaches the technique, works one problem end-to-end), `exercises.ipynb` (the
laddered problem set; each problem: statement, constraints, sample I/O; `stretch` tags on the
hardest), `solutions.ipynb` (on the new model: a `no-exec` display mirroring each `assets/<pid>.py`
reference solver — see §3; on the old model: reference `solve` functions + non-vacuous sample/edge
asserts), `teacher-notes.md` (the **five** `## Goals`/`## Pacing`/`## Common mistakes`/
`## Discussion prompts`/`## Differentiation` headings for a unit — checkpoints add `## Grading`,
projects add `## Rubric`; states each problem's intended complexity, a pacing plan, the motivating
hook, common mistakes, differentiation), and `manifest.yaml` (concept-tagged, map-equal).

- **Checkpoints** = timed mini mock-contests: `## Question N` blocks (student cells empty), a stated
  time limit, teacher-run clock; solutions verify via the §3 contract (new model: `assets/qN.py` +
  fixtures under `judge-check`; old model: the `solve` contract). Same mechanical rules as Book-1
  checkpoints (no solutions in the student file; a deliberate-bug beat, if any, lives in a markdown
  fence).
- **Capstone** = full mock contest (a complete timed mixed problem set) or a student-authored problem
  set with reference solutions + samples. Doubles as the year finale.
- **Recurring warm-up seam:** boolean-algebra drills and "what-does-this-program-do?" code-tracing
  ride as short warm-ups in teacher notes across units (not only their home unit), for ACSL
  short-answer fluency.

## 5. Two-tier concept registry (the honesty about what CI can check)

Book 2 gets its own `concepts.yaml` + `coverage-map.yaml`. Concepts split into two kinds:

- **Language features** — new syntax/builtins: sets (`set-literal`, `set-ops`), tuples, `.split`,
  `sorted(key=…)`, comprehensions, recursion-as-self-call, `deque`, bitwise operators, etc. These
  are **AST-detectable**, so `concept-scan` enforces them exactly as in Book 1.
- **Technique tags** — algorithmic patterns: `complete-search`, `greedy`, `simulation`, `prefix-sum`,
  `binary-search`, `two-pointers`, `backtracking`, `bfs`, `dfs`, `flood-fill`, `graph-repr`,
  `tree-traversal`, `base-conversion`, `sieve`, `gcd`, `modular-arithmetic`, `boolean-algebra`,
  `postfix-eval`, `bitmask`. These are **not** detectable by any AST scanner; they are tracked in the
  coverage-map for **prereq/coverage closure** (a problem may not *require* a technique before it is
  taught) but are **reviewer-enforced, not scanner-enforced** — the same "necessary-not-sufficient"
  line drawn by Book 1's `MANUAL_ONLY`.

Both kinds obey the usual discipline: `introduces`/`requires`/`practices` per entry, cumulative
closure, `practices ∩ introduces` empty, manifest == map.

**No-OOP representations (keeps the "OOP deferred" promise honest).** The structures that would
normally invite a class are represented with plain lists/dicts/tuples instead: a **binary tree** as
parallel arrays or a dict of nodes (e.g. `left[i]`/`right[i]`/`val[i]`, or `{id: {"val":…,
"left":…, "right":…}}`), a **graph** as an adjacency-list dict (`adj[u] -> list of neighbors`), a
**stack/queue** as a list / `collections.deque`. No student-defined classes are required anywhere in
Book 2; the Book-1 class intro is used only incidentally, never built upon.

## 6. Cross-book prerequisite infrastructure (SHIPS FIRST)

> **ERRATA (plan 017, AD-001):** the `book1:for-loop` *namespaced-id* framing in this section is
> SUPERSEDED by a **flat shared namespace** — Book-1 ids stay bare, Book-2 adds globally-unique new
> ids, and a CI check enforces uniqueness across all books. Book 1 already shipped with bare ids and
> total Book-1-precedes-Book-2 ordering makes prefixes unnecessary. Read `book1:X` below as "the
> (bare) Book-1 concept `X`, available to Book 2 as a prerequisite."

`books.yaml` already declares `book2 depends_on book1`, and design-000 mandates **namespaced concept
ids** (`book1:for-loop`) for cross-book contracts. The verification tooling is currently per-book and
must learn cross-book resolution:

- For a book with `depends_on: [book1]`, the tooling seeds the **"already taught" baseline** with the
  full set of Book-1-taught concepts before Book 2's first entry. `prereq-check`, `coverage-check`,
  and `concept-scan` all consume that baseline (a Book-2 entry may `requires:` a `book1:` concept and
  it resolves as satisfied; a Book-2 lesson using a Book-1 language feature is not flagged
  used-but-unlisted).
- Book-2 `concept-scan` needs **per-book constants** — Book 1's `TAUGHT_METHODS`/`BUILTINS`/
  `MANUAL_ONLY` are book1-coupled (flagged in plan 016); Book 2 extends them (e.g. `.split`, set/deque
  methods become taught; the technique tags join `MANUAL_ONLY`).
- **This is the FIRST Book-2 plan (infra, no content),** so closure discipline works from unit 1.
  It ships with tests (cross-book prereq resolves; a Book-2 entry requiring an un-taught `book1:`
  concept still fails; Book-1 features don't false-flag in Book 2).

## 7. The arc (≈14 units + 4 mock-contest checkpoints + capstone)

Closure-safe ordering; every technique builds only on earlier ones.

**Term 1 — Foundations, logic & search**
- **U01 Reading the input** — `.split`, int conversion, "read N then N numbers," read a grid; reading
  real stdin and printing output (the §3 stdin-first contract; pre-migration entries still show the
  `solve(data)` form until re-authored).
- **U02 Boolean logic & algebra** — truth tables, DeMorgan, short-circuit; seeds the recurring
  code-tracing ("what does this do?") warm-ups.
- **U03 Complexity — fast enough?** — counting operations, O(n)/O(n²)/O(log n), will-it-finish.
- **U04 Sets, tuples & sorting** — O(1) membership + dedup, tuples as records/keys, `sorted(key=…)`.
- **U05 Searching & complete search** — linear search, **binary search** on a sorted list, and brute
  force via **fixed-depth nested loops** (all pairs/triples/candidates). NOTE (closure): full
  subset/permutation *generation* is NOT here — it needs recursion (U09) or bitmasks (U11), both
  later; U05's complete search is nested-loop enumeration only. Generating all subsets is taught in
  U09 (recursive) and revisited as bitmasks in U11.
- **CP1 — Mock Contest 1.**

**Term 2 — Greedy, simulation & sums**
- **U06 Greedy** — sort-then-sweep, locally-best choice, informal "why it works."
- **U07 Simulation & ad hoc** — follow the rules, careful state, off-by-one.
- **U08 Prefix sums** — 1D cumulative sums for O(1) range queries → 2D on a grid.
- **CP2 — Mock Contest 2.**

**Term 3 — Recursion, structures & number sense**
- **U09 Recursion & backtracking** — base/recursive case; permutations/subsets; try→recurse→undo.
- **U10 Stacks, queues & deques** — LIFO/FIFO, `deque`, bracket matching, **postfix evaluation**;
  the queue BFS will reuse.
- **U11 Number systems, bitwise & number theory** — base conversion (bin/hex), **bit-string flicking**
  (AND/OR/XOR/NOT/shifts), GCD (Euclid), primes/sieve, modular arithmetic.
- **U12 Binary trees & traversals** — binary trees, BST, pre/in/post-order traversal (recursive,
  building on U09). Trees represented with arrays/dicts, **no class** (§5).
- **CP3 — Mock Contest 3.**

**Term 4 — Graphs & Silver taste** *(the explicit compressible buffer)*
- **U13 Grids, graphs & traversal** — 2D grids, neighbors/bounds; **explicit graphs** as
  adjacency-list dicts (degree, connectivity — §5, no class); **flood fill**, **BFS** shortest-steps
  (reuses U10's `deque`), **DFS** reachability (reuses U09 recursion).
- **U14 Two pointers & sliding window** — sorted two-pointer, window sums/counts.
- **CP4 — Mock Contest 4.** Term-4 finale: grids/graphs (flood-fill, BFS, DFS, adjacency-list graphs) and
  two-pointers/sliding-window, plus the pre-capstone practice home for those concepts (and a modular-power
  problem reprising U11) so every technique is reinforced in a timed contest before the capstone.
- **Capstone — Full Mock Contest.**

## 8. Pacing contract (the scope-vs-time reconciliation)

Book 2 is fuller than Book 1 (~14 units). Honest budget management, stated in the syllabus:

- Several units are **one lesson of teaching + a large self-paced problem set** (the rich problem
  sets are homework, not class time).
- Boolean-algebra and code-tracing partly ride as **recurring warm-ups**, not full class blocks.
- **Term 4 is the explicit compressible buffer:** if the year runs short, U13–U14 shrink to exposure
  and the capstone still stands. Bronze mastery (Terms 1–3) is the non-negotiable core; Silver taste
  is the stretch.
- The syllabus pins per-unit lesson counts the way Book 1's syllabus allocates its 32 workload units.

## 9. Verification & governance (unchanged from Book 1)

- `scripts/ci-local.sh` remains authoritative; Book 2 adds no new gate types, only the cross-book
  infra (§6) and the two-tier registry (§5). `concept-scan` (now in `tools/`) extends to Book 2.
- Every unit/checkpoint/project ships through the full lifecycle: design → 4-way plan-review gate →
  phase implementation → `ci-local` → 4-way content-review gate → post-execution report → PR →
  `pre-merge-guard --pr` → squash-merge.
- **Self-containedness is law**, cross-book: nothing used before taught, counting Book 1 as the
  baseline. Project-first is law: every unit opens with its problem hook.

## 10. Plan sequence (each its own spec→plan→gates cycle)

1. **Book-2 infra** — cross-book prereq resolution + two-tier registry + Book-2 `concepts.yaml`
   skeleton + Book-2 `coverage-map.yaml` skeleton + syllabus. (No content; tooling + registry only.)
2. **Term 1** — U01–U05 + CP1 (likely 2–3 content plans).
3. **Term 2** — U06–U08 + CP2.
4. **Term 3** — U09–U12 + CP3.
5. **Term 4** — U13–U14 + Capstone.

Granularity (one plan per unit vs. per small group) is decided per term at planning time, following
Book-1 practice.

## 11. Open decisions deferred to plan time (not blocking this spec)

- Exact per-unit lesson counts (syllabus, in plan 1).
- Whether list comprehensions get a dedicated micro-lesson or ride inside U04.
- ~~Whether a shared `tools/`-level "sample judge" helper is worth extracting, or inline asserts
  suffice.~~ **RESOLVED (plan 036):** a subprocess judge (`tools/judge.py`) runs stdin `.py` solvers
  against committed `.in`/`.out` fixtures — see the amended §3.
- Final `concepts.yaml` id list (derived + scanner-reconciled per entry, as in Book 1).
