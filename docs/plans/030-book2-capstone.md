# Plan 030 — Book 2 Capstone: project-03 "Grand Mock Contest"

**Goal:** Author the Year-2 capstone — a full timed mock contest integrating the year's techniques — as
`book2/projects/project-03-mock-contest/`, completing Book 2 (the final map entry).

**Architecture:** A `kind: project` entry: `brief.ipynb` (3–6 sequential `## Milestone N` rounds presenting
the contest problems with sample I/O + constraints, a `## Make it yours` extension, and a `## Requirements`
checklist — NO solutions in the brief), `solutions.ipynb` (pure `solve(data:str)->str` per problem with
sample + distinguishing asserts), `teacher-notes.md` (five unit headings + `## Rubric`), `manifest.yaml`.
Problems are genuine contest problems, each combining 2–3 of the year's techniques, collectively exercising
all 17 required concepts. Authoring the project dir ACTIVATES `practice_findings` — already satisfiable
(`pre_capstone` = 31/31 after CP4/plan 029), so the gate passes.

**Tech stack:** Python `solve(data:str)->str` judge contract; `tools/` verification; `scripts/ci-local.sh`.

**Spec / design:** `docs/designs/001-book2-algorithms.md` (§7 "Capstone — Full Mock Contest"; §3–4 the
`solve` contract + contest realism). The `project-03-mock-contest` map entry already exists
(`kind: project`, `lessons: 3`, `requires` = the 17 techniques, `practices: []` — to be filled).

## Global Constraints

- **Judge contract:** every reference is a pure `solve(data: str) -> str`; ZERO `input()` in executable
  cells; the submission wrapper appears ONLY as a MARKDOWN block or in teacher-notes. Deterministic;
  integer/string output only; unique cell ids; no stored outputs.
- **Project structure (verified vs `tools/notebooks.py`):** files = `manifest.yaml` / `brief.ipynb` /
  `solutions.ipynb` / `teacher-notes.md`. `brief.ipynb` needs **3–6 sequential `## Milestone N`** headings, a
  `## Make it yours` heading, a `## Requirements` checklist heading, and MUST NOT contain any solution
  heading (no reference code — starter/empty cells only). `teacher-notes.md` needs the five unit headings +
  **`## Rubric`** (projects use `## Rubric`, NOT `## Grading`). `solutions.ipynb` runs top-to-bottom clean.
- **Concept coverage:** the solutions must GENUINELY exercise all 17 `requires` concepts across the problems
  (`input-parse, complete-search, binary-search, greedy, simulation, prefix-sum, recursion, backtracking,
  deque, graph-repr, bfs, dfs, flood-fill, two-pointers, tree-traversal, sorted-key, set-literal`). `practices`
  = every additional concept the solutions use (scanner-derived), filled after authoring so `concept-scan`
  passes (used ⊆ requires ∪ practices). This will include at least `grid-2d` (P2/P6), `str-split` (parsing),
  `tuple` (records/coordinates), `set-ops` (`visited.add` in BFS/flood-fill), plus the Book-1 features
  actually used (`accumulator, arithmetic, comparison, def-function, elif-else, if-statement, in-operator,
  list-append, list-literal, logical-ops, nested-loops, parameters, return-value, string-concat,
  string-literal, type-conversion, while-loop, for-loop`, etc.) — the exact set is derived from `detect()`.
- **Closure / house rules (everything ≤ U14 is legal):** allowed builtins ONLY
  {len, min, max, sorted, sum, abs, round}. Banned everywhere (scanner-blind → grep/AST): `nonlocal`/`global`,
  `.pop()`, `.index`, `.setdefault`, `+=` (use `x = x + …`), comprehensions, `del`, `.join`,
  `.union`/`.intersection`/`.difference`, `.remove`, chained comparison, bare-container truthiness
  (`while len(x) > 0`), list/str repetition, base/number shortcuts (`bin`/`hex`/`oct`/`format`/`int(x,base)`/
  `:b`/`0x`/3-arg `pow`/`divmod`/`.bit_length`), `defaultdict`/`heapq`/`itertools`/`Counter`/`math`/
  `sys.setrecursionlimit`.
- **Idioms:** adjacency-list = plain dict; BFS = deque FIFO (`append`/`popleft`, `while len(queue) > 0`);
  DFS/flood-fill = recursion with `visited` passed as an argument; tree = parallel arrays / dict with a `-1`
  child sentinel base-cased before indexing; converging two-pointers on a SORTED list; sliding window with an
  incremental running sum on non-negative values; binary-search-on-the-answer with a monotone feasibility
  check; output built one concat per statement. Recursive-grid / recursive-backtracking inputs sized so the
  reference finishes fast at the stated constraints (measure worst case).

## Out of scope

- Any new concept (`introduces: []` — a capstone teaches nothing new).
- Changes to U01–U14 / CP1–CP4 content.
- No CP5 or further checkpoints. This plan is the final Book-2 entry.
- **Verification-phase note:** this plan ships a project WITH a named verification phase (Phase C); not
  exempt.

## Phases

### Phase A — Author `solutions.ipynb` (blind, the reference)

Create `book2/projects/project-03-mock-contest/solutions.ipynb` — one pure `solve(data)` per problem with
sample + crafted distinguishing asserts (each killing a plausible wrong-solution mutant). **8 problems across
5 `## Milestone N` rounds** (M1–M5; the `## Make it yours` extension and `## Requirements` checklist are
SEPARATE brief headings, not milestones). Each problem is a fully-pinned contest contract:

- **M1 Warmups** (P1, P2).
  - **P1 "Checkpoint Ledger"** (`input-parse`, `prefix-sum`). Input: line 1 `N`; line 2 `N` integers
    `a_1..a_N`; line 3 `Q`; then `Q` lines each `l r` (1-indexed, inclusive). Output: the `Q` range sums,
    space-separated on one line. Constraints: `1 ≤ N ≤ 100000`, `1 ≤ Q ≤ 100000`, `0 ≤ a_i ≤ 10^9`,
    `1 ≤ l ≤ r ≤ N`. Reference: `pre[0]=0`, `pre[i]=pre[i-1]+a[i]`; answer `pre[r]-pre[l-1]`. Signature
    mutant: `pre[r]-pre[l]` (off-by-one) — killed by a query with `l = 1`. Complexity O(N + Q).
  - **P2 "Warehouse Robot"** (`simulation`, `grid-2d`). Input: line 1 `R C`; line 2 `sr sc` (0-indexed start);
    line 3 a string of `U/D/L/R`. The robot ignores any move that would leave the `R×C` grid (no walls).
    Output: the final `r c` (space-separated). Constraints: `1 ≤ R, C ≤ 1000`, `0 ≤ sr < R`, `0 ≤ sc < C`,
    `0 ≤ |moves| ≤ 100000`. Signature mutant: missing bounds guard — killed by a move sequence pushing against
    an edge (robot must stay put). Complexity O(|moves|).
- **M2 Search & Pointers** (P3, P4).
  - **P3 "Split the Load"** (`binary-search`, `greedy`). Input: line 1 `N K`; line 2 `N` positive integer
    weights (in order). Split the sequence into at most `K` CONTIGUOUS groups minimizing the maximum group
    sum; output that minimum. Reference: binary-search the cap in `[max(w), sum(w)]`; greedy left-to-right
    feasibility counts the groups a cap needs and tests `≤ K`. Constraints: `1 ≤ K ≤ N ≤ 100000`,
    `1 ≤ w_i ≤ 10^9`. Signature mutant: a wrong feasibility comparison (`< K` instead of `≤ K`, which over-
    tightens the cap → `sum(w)`) — killed by the sample (answer 18, mutant 32); asserts also include a "fits
    exactly" tie. (A `lo=1` init is harmless — the monotone predicate converges regardless — so it is not the
    guarded mutant.) Complexity O(N · log(sum)).
  - **P4 "Perfect Pair"** (`two-pointers`, `sorted-key`). Input: line 1 `N T`; then `N` lines each
    `id skill` (two integers). Store records as `(id, skill)`; sort by skill with a NAMED key
    (`sorted(records, key=skill_of)`, `def skill_of(rec): return rec[1]` — the natural tuple order is by id,
    so the key is genuinely needed); converging two pointers decide whether two DIFFERENT players' skills sum
    to exactly `T`. Output: `YES`/`NO`. Constraints: `2 ≤ N ≤ 100000`, `0 ≤ id ≤ 10^9`, `0 ≤ skill ≤ 10^9`,
    `0 ≤ T ≤ 2·10^9`. Signature mutants: wrong-pointer move (killed by a YES case needing the correct move),
    self-pair `lo == hi` (killed by a NO case where the only exact sum is `2·a[i]`), wrong sort key. Complexity
    O(N log N).
- **M3 Graphs** (P5, P6).
  - **P5 "City Network"** (`graph-repr`, `bfs`, `deque`, `set-literal`). Input: line 1 `N M S T` (nodes
    `1..N`, `M` edges, source `S`, target `T`); then `M` lines each `u v` (an undirected edge). Build an
    ADJACENCY-LIST dict (`if u not in adj: adj[u] = []`, append BOTH directions); BFS from `S` for the fewest
    edges (hops) to `T`, or `-1` if unreachable. deque FIFO (`append`/`popleft`, `while len(queue) > 0`),
    `visited = {S}` (a `{...}` set literal). Output: the hop count or `-1`. Constraints: `1 ≤ N ≤ 100000`,
    `0 ≤ M ≤ 200000`, `1 ≤ S, T ≤ N`. Signature mutants: LIFO (`pop` vs `popleft`) overshoots on a graph where
    a stack takes a longer path; an unreachable case (→ `-1`). Complexity O(N + M). (This is the genuine
    `graph-repr` home — an explicit adjacency list, NOT a grid.)
  - **P6 "Flood the Basin"** (`flood-fill`, `recursion`, `grid-2d`). Input: line 1 `R C`; then `R` rows of
    `#`/`.`. Output: the size of the LARGEST 4-connected region of `#` (0 if none). Reference: recursive
    flood-fill with a `visited` set. Constraints: `1 ≤ R, C`, `R·C ≤ 400` (recursive-grid cap). Signature
    mutants: 8-neighbour merge (killed by a grid with diagonally-touching regions), a single-cell region.
    Complexity O(R·C).
- **M4 Recursion & Backtracking** (P7).
  - **P7 "Seating Plan"** (`recursion`, `backtracking`, `complete-search`). Input: a single line `N`. Count
    the arrangements of people `1..N` in seats `1..N` such that person `p` is NOT in seat `p` (a derangement
    count), computed by GENUINE backtracking over a shared `used` array: for the current seat try each unused
    person `p` with `p != seat`, set `used[p] = 1`, recurse, then RESTORE `used[p] = 0`. Output: the count.
    Constraints: `1 ≤ N ≤ 9` (at most 9! ≈ 3.6·10^5 leaves). Signature mutant: removing the restore
    (`used[p] = 0`) — the shared state stays marked and the count collapses; killed by e.g. `N=3` → `2`
    (mutant → a wrong, smaller value). This is the genuine `backtracking` home (mutable shared choice state
    with mark → recurse → restore). Complexity O(N!).
- **M5 Trees** (P8).
  - **P8 "Team Roster"** (`tree-traversal`, `dfs`, `recursion`). Input: line 1 `N` (nodes `1..N`, node `1` is
    the root); then `N` lines each `label left right` (`left`/`right` are child node ids in `1..N`, or `-1`
    for none). Output: the PRE-order label sequence (root, left subtree, right subtree), space-separated.
    Reference: recursion, base-cased on `child == -1` BEFORE indexing. Constraints: `1 ≤ N ≤ 300` (max depth
    300 < Python's ~1000 recursion limit — safe; `sys.setrecursionlimit` banned), `0 ≤ label ≤ 10^9`, the
    input describes a valid rooted binary tree. Signature mutants: pre- vs post-order (killed by an asymmetric
    tree), a missing `== -1` guard (indexing `arr[-1]` reads the last node). Complexity O(N).

Concept coverage — all 17 `requires`, each with a genuine home: input-parse→P1(+all), prefix-sum→P1,
simulation→P2, binary-search→P3, greedy→P3, two-pointers→P4, sorted-key→P4, **graph-repr→P5 (adjacency
list)**, bfs→P5, deque→P5, set-literal→P5, flood-fill→P6, recursion→P6/P7/P8, **backtracking→P7 (mark/restore
shared state)**, complete-search→P7, tree-traversal→P8, dfs→P8. `grid-2d` (a `practices` concept) →P2/P6.
Before finalizing, run an ad-hoc `detect()` over the solution cells to confirm the AST-features are genuinely
used, and reviewer-check the techniques; verify each signature mutant is killed by a distinguishing assert
(numerically, as in CP4).

### Phase B — Author `brief.ipynb` + `teacher-notes.md` + `manifest.yaml`

- **`brief.ipynb`:** intro (contest rules + the `solve` contract + a markdown-only submission wrapper), then
  **exactly 5 sequential `## Milestone N` headings** (`## Milestone 1` … `## Milestone 5`) — M1–M5 present
  their problems (statement + sample I/O + constraints + the intended technique named), each with an EMPTY
  student code cell (no solutions). Then a SEPARATE, standalone **`## Make it yours`** heading (its own exact
  line — NOT `## Milestone 6`; the validator's `## Make it yours` check needs the exact line) with extension
  ideas (add a problem, tighten a bound, optimize a solve), and a SEPARATE **`## Requirements`** checklist
  (all 8 problems pass their samples under the `solve` contract, within the time budget). No `## Solution`/
  solution heading anywhere in the brief (`project_milestone_findings` fails on any `SOLUTION_HEADING`).
- **`teacher-notes.md`:** `## Goals`, `## Pacing` (3 lessons — a timed contest sitting + review),
  `## Common mistakes`, `## Discussion prompts`, `## Differentiation`, **`## Rubric`** (per-problem credit +
  the per-problem Big-O table + the signature mutant each problem's asserts kill). Projects use `## Rubric`,
  NOT `## Grading`.
- **`manifest.yaml`** (full schema per `MANIFEST_KEYS` — all six keys required):
  ```yaml
  id: project-03-mock-contest
  kind: project
  blueprint_version: 1
  lessons: 3
  provenance: original
  concepts:
    introduces: []
    requires: [<the 17 techniques already in the map>]
    practices: [<scanner-derived: grid-2d, str-split, tuple, set-ops + Book-1 features used>]
  ```
  Update the `project-03-mock-contest` map entry's `practices` to match (manifest == map compared as sorted
  lists; duplicates fail separately).

### Phase C — Verification (named verification phase)

- `scripts/ci-local.sh` ALL GREEN: registry+lint, notebook execution+hygiene, manifest/prereq/coverage/
  stretch, concept-scan, project layout (`## Milestone N` 3–6 sequential, `## Make it yours`,
  `## Requirements`, no solution heading), PDF build (book1-only), pre-merge guard.
- **`practice_findings` NOW ACTIVE** (capstone dir exists): confirm `coverage-check` PASSES (`pre_capstone ⊇
  all 31`) — this is the plan's linchpin.
- Execute `solutions.ipynb` in a real kernel; every assert holds; run each `solve()` on its stated sample.
- Confirm all 17 required concepts are genuinely exercised (AST `detect()` for features; manual for
  techniques); confirm `concept-scan` clean (used ⊆ requires ∪ practices; no untaught methods).
- AST-grep for the always-banned scanner-blind traps; confirm each problem's signature mutant is killed by a
  distinguishing assert (verify numerically, as in CP4).

## Post-Execution Report

**Shipped:** `book2/projects/project-03-mock-contest/` — the Year-2 capstone and the FINAL Book-2 map entry.
With this merged, Book 2 is complete (14 units + 4 checkpoints + capstone).

**Phase A (solutions):** `solutions.ipynb` — 8 pure `solve()` problems, each with sample + distinguishing
asserts. P1 Checkpoint Ledger (prefix-sum), P2 Warehouse Robot (grid simulation), P3 Split the Load
(binary-search-on-answer + greedy), P4 Perfect Pair (converging two-pointers, named `skill_of` key), P5 City
Network (adjacency-list graph BFS, deque FIFO, `visited = {source}` literal), P6 Flood the Basin (recursive
flood-fill), P7 Seating Plan (derangement count via mark→recurse→restore backtracking), P8 Team Roster
(recursive pre-order over parallel arrays with `-1` sentinel).

**Phase B (brief + notes + manifest):** `brief.ipynb` — intro + `solve` contract + markdown-only wrapper,
5 `## Milestone N` rounds (M1–M5) presenting the 8 problems with sample I/O + constraints and empty student
cells, a standalone `## Make it yours` extension round, and a `## Requirements` checklist; NO solutions in the
brief. `teacher-notes.md` — five unit headings + `## Rubric` (per-problem Big-O + signature-bug table).
`manifest.yaml` — full six-key schema; `requires` = the 17 techniques, `practices` = `grid-2d, set-ops,
str-split, tuple` + the Book-1 features (scanner-derived). Map entry `practices` updated to match.

**Phase C (verification):** all book2 checks PASS (coverage, prereq, concept-scan, manifest, structure,
hygiene, cell-lint, noexec, stretch, exec-solutions). **`practice_findings` is now ACTIVE (the capstone dir
exists) and PASSES — `pre_capstone ⊇ all 31 Book-2 concepts`** (the plan's linchpin, proven). Solutions
execute clean; every assert holds. Signature mutants confirmed killed numerically: P1 off-by-one (`5 9 0` vs
`7 13 3`), P2 no-bounds (`2 2` vs `1 1` on `2 2/RRDD`), P4 self-pair (`YES` vs `NO`), P5 LIFO (`4` vs `2` on
the witness graph), P6 8-neighbour (`2` vs `1`), P7 no-restore (`0` vs `2` on `N=3`), P8 post-order
(`4 5 2 3 1` vs `1 2 4 5 3`). concept-scan clean (no unknown methods; all 17 `requires` + `grid-2d` genuinely
used).

**Deviations from plan:** none to scope. `import-statement` (the `from collections import deque` wrapper
artifact) is not listed in `practices` — matching the CP1–CP4 precedent; concept-scan does not flag it.

## Plan Review

### Round 1 (2026-09-09, HEAD fdbd148) — [self] AWN · [fable] AWN · [glm] REJECT · [sol] REJECT

All three externals independently confirmed the project structure/files/headings, the `## Rubric`
convention, and — crucially — the practice-completeness linchpin (`known`=31 ⊆ pre-capstone practices, so the
newly-activated `practice_findings` passes). The REJECTs converge on the graph-repr home + pinning; findings:

1. `[FIXED]` **[glm/fable/sol, blocking] `graph-repr` had no genuine home** — P5 "Evacuation Route" was a
   GRID BFS (neighbours computed inline), never an adjacency list; `graph-repr` (concepts.yaml = "adjacency
   list") was only artificially covered. → **Recast P5 as "City Network": an explicit edge-list input building
   `adj = {}` (`if u not in adj: adj[u] = []`, both directions), BFS shortest-hops S→T.** Genuinely homes
   `graph-repr` + `bfs` + `deque` + `set-literal`; `grid-2d` stays homed by P2 + P6.
2. `[FIXED]` **[sol, blocking] P7's backtracking witness was weak** — "include-only" (drop the skip branch) is
   not a missing-undo mutant, so `backtracking` (mark→recurse→undo) was not genuinely exercised. → **Reframed
   P7 as "Seating Plan": count derangements via GENUINE backtracking over a shared `used` array
   (mark `used[p]=1` → recurse → RESTORE `used[p]=0`).** Verified numerically: N=3 → 2; the no-restore mutant
   → 0 (killed by the `N=3`→`2` assert). Still homes `recursion` + `complete-search`.
3. `[FIXED]` **[all 3] Milestone-count wording was contradictory** ("6 sequential `## Milestone N`" but M6 =
   "Make it yours"; `## Make it yours` is a SEPARATE required heading, not a milestone). → Pinned to **exactly
   5 `## Milestone N` (M1–M5)** carrying P1–P8, plus a standalone `## Make it yours` line and a `##
   Requirements` checklist. 5 ∈ [3,6]; validated against `project_milestone_findings`.
4. `[FIXED]` **[sol, blocking] Problems were not fully pinned** — several lacked exact I/O/constraints (P1/P2/
   P3/P4/P5/P6/P8), P2 referenced a nonexistent "wall", P7 lacked positivity, P8 lacked a depth-safe N cap.
   → Every problem now carries a concrete input/output/constraint contract + a signature mutant; P8 capped
   `N ≤ 300` (depth < recursion limit; `sys.setrecursionlimit` banned); P2's "wall" removed.
5. `[FIXED]` **[sol] `practices` note was incomplete** — the solutions also use `str-split`, `tuple`,
   `set-ops` (detectable features). → Global Constraints + Phase B now list `grid-2d, str-split, tuple,
   set-ops` + the Book-1 features, derived from `detect()`.
6. `[FIXED]` **[sol/glm] Phase B manifest sketch omitted required keys** (`blueprint_version`, `provenance`,
   the nested `concepts:` map). → Phase B now gives the full six-key `MANIFEST_KEYS` schema.

Non-blocking (accepted): [glm] P4's converging two-pointer time budget benefits from bounds (now added).

### Round 2 (2026-09-09, HEAD b5b1ee2) — [fable] APPROVE · [glm] APPROVE WITH NITS · [sol] APPROVE

All three re-verified against the actual tooling: P5 is a genuine adjacency-list graph BFS; P7 is genuine
mark→recurse→restore backtracking (all three independently re-traced the derangement mutant: N=3 → 2,
no-restore → 0); the 5-milestone + `## Make it yours` + `## Requirements` structure validates against
`project_milestone_findings`; all 17 concepts have genuine homes; the practice-completeness linchpin holds
(`known`=31 ⊆ pre-capstone practices union). [sol] APPROVE (all 5 Musts resolved). [glm] two non-blocking
wording nits, folded in: `grid-2d` is genuinely homed by **P6** (a 2D `#`/`.` grid; P2 also operates on grid
bounds) — it is a `practices` concept, not one of the 17, so coverage is unaffected; and `practices` is
"scanner-derived for the AST-features, manual for the technique concepts". [fable] one authoring note: P1's
off-by-one assert needs its `l = 1` case to have `a_1 > 0` (honored at authoring; Phase C mutant-check
catches it).

### CONSENSUS — plan-review gate CLOSED

[self] APPROVE · [fable] APPROVE · [glm] APPROVE WITH NITS · [sol] APPROVE. Full 4-way blocking consensus,
zero open findings. Cleared for implementation (Phases A–C).

## Content Review

### Review 1 — [self] (2026-09-09, HEAD ee61cb0)

**APPROVE.** Verified: all 8 `solve()` execute clean with every assert holding; each signature mutant killed
numerically (P1 off-by-one → `5 9 0` vs `7 13 3`; P2 no-bounds → `2 2` vs `1 1`; P4 self-pair → `YES` vs
`NO`; P5 LIFO → `4` vs `2` on the witness graph `6 6 1 6…`; P6 8-neighbour → `2` vs `1`; P7 no-restore → `0`
vs `2` on `N=3`; P8 post-order → `4 5 2 3 1` vs `1 2 4 5 3`). All 17 required concepts genuinely exercised
(graph-repr = a real adjacency dict in P5; backtracking = mark/restore in P7; complete-search = P7;
sorted-key = named `skill_of` key in P4). concept-scan clean (no unknown methods); all book2 checks +
exec-solutions PASS; **`practice_findings` active and passing (`pre_capstone ⊇ 31`)**. Conventions met (5
`## Milestone N` + `## Make it yours` + `## Requirements`, no solution heading in the brief; teacher-notes 5
headings + `## Rubric`; empty student cells; unique ids; no outputs; markdown-only wrapper).

### Reviews 2–3 — [glm] & [fable] (2026-09-09, HEAD ee61cb0)

Both blind-solved all 8 problems independently ([fable] ~2100 randomized oracle cross-checks; [glm] full
diff) — **all 8 references correct, all samples match**, all specified critical asserts confirmed non-vacuous
by mutant execution, all 17 required concepts genuinely exercised (graph-repr = real adjacency dict in P5,
backtracking = mark/restore in P7, complete-search = P7, sorted-key = named `skill_of` in P4). [glm] APPROVE
WITH NITS. **[fable] REJECT** on two scanner-blind closure violations (correctness itself clean). Findings:

1. `[FIXED]` **[fable, blocking] List repetition** — `used = [0] * (n + 1)` (P7) and `label/left/right =
   [x] * (n + 1)` (P8) are the banned `[x]*n` construct (scanner-blind: `Mult` → "arithmetic"). → Rebuilt all
   four arrays with `while`-loop `append` (as every prior solution does). AST-verified 0 list-repetitions.
2. `[FIXED]` **[fable, blocking] Untaught ternary/`IfExp`** — `moves = lines[2] if len(lines) > 2 else ""`
   (P2) is the only `IfExp` in either book (untaught, scanner-blind). → Replaced with a 3-line `if`
   statement. AST-verified 0 `IfExp`.
3. `[WONTFIX — refuted by measurement] [fable NIT] P1 O(N²) output at N=Q=100000.** Measured the shipped
   one-concat-per-statement idiom at N=Q=100000: **0.10 s** (CPython in-place-optimizes `out = out + x`), so
   the O(N+Q) claim holds; no cap needed. (Fable's ~17 s was a reconstructed-solver artifact.)
4. `[FIXED]` **[glm/fable NIT] teacher-notes typo** "a ret/extension session" → "a retry/extension session".
5. `[FIXED]` **[glm NIT] plan P3 signature-mutant wording** overstated a `lo`-init mutant (harmless) → reworded
   to the real feasibility-comparison mutant the assert actually kills.

Solutions re-executed clean after the closure fixes; all book2 checks PASS. [self] APPROVE stands; [glm]
APPROVE WITH NITS (nits fixed). Awaiting [sol] on the fixed version.
