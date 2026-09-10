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
  = every additional concept the solutions use (scanner-derived: `grid-2d`, and the Book-1 features), filled
  after authoring so `concept-scan` passes (used ⊆ requires ∪ practices).
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
6 milestone rounds**, pinned. The concept→problem map below covers all 17 required concepts, each with a
genuine home:

- **M1 Warmups** (P1, P2).
  - **P1 "Checkpoint Ledger"** (`input-parse`, `prefix-sum`): first line `N`, then `N` integers, then `Q`,
    then `Q` queries `l r` (1-indexed inclusive). Answer each query with a prefix-sum range total; output the
    `Q` answers space-separated. Assert distinguishes a prefix off-by-one (correct = `pre[r] - pre[l-1]`).
    Complexity O(N + Q).
  - **P2 "Warehouse Robot"** (`simulation`, `grid-2d`): first line `R C`, then `sr sc`, then a move string of
    `U/D/L/R`; the robot ignores a move that would leave the `R×C` grid; output the final `r c`. Assert
    distinguishes a missing bounds guard (off-grid) and a wall at the edge. Complexity O(len(moves)).
- **M2 Search & Pointers** (P3, P4).
  - **P3 "Split the Load"** (`binary-search`, `greedy`): minimize the maximum truck load — binary-search on
    the answer, with a greedy left-to-right packing feasibility check that counts trucks and tests ≤ `K`.
    Assert distinguishes a lo/hi boundary slip and a "fits exactly" tie. Complexity O(N log(sum)).
  - **P4 "Perfect Pair"** (`two-pointers`, `sorted-key`): `N` records each `(skill, name-index)`; after
    `sorted(key=named_fn)` (sort by skill), use converging two pointers to find whether two DIFFERENT players'
    skills sum to exactly `T` — output `YES`/`NO`. Assert distinguishes a wrong-pointer move, a self-pair
    (`lo == hi`), and a wrong sort key. Complexity O(N log N).
- **M3 Graphs & Grids** (P5, P6).
  - **P5 "Evacuation Route"** (`graph-repr`, `bfs`, `deque`, `grid-2d`, `set-literal`): fewest 4-neighbour
    steps from `S` to `T` on an `R×C` grid with `#` walls, `-1` if unreachable; deque FIFO
    (`append`/`popleft`, `while len(queue) > 0`), `visited = {start}` (a `{...}` set literal). Assert includes
    a FIFO-witness (a grid where a LIFO stack overshoots) and an unreachable case. Complexity O(R·C).
  - **P6 "Flood the Basin"** (`flood-fill`, `recursion`): the size of the LARGEST 4-connected region of `#` in
    a grid; recursive flood-fill with a `visited` set. Assert distinguishes an 8-neighbour merge and a
    single-cell region. Complexity O(R·C), `R·C ≤ 400`.
- **M4 Recursion & Backtracking** (P7).
  - **P7 "Exact Change"** (`recursion`, `backtracking`, `complete-search`): count the subsets of `N` coin
    values summing to exactly `T`, via include/exclude recursion (try→recurse→undo). Assert distinguishes an
    include-only (no-backtrack) mutant and a wrong empty-target base case (`T=0` → 1). Complexity O(2^N),
    `N ≤ 20`.
- **M5 Trees** (P8).
  - **P8 "Team Roster"** (`tree-traversal`, `dfs`, `recursion`): a rooted binary tree as parallel arrays
    (`left[i]`, `right[i]`, `label[i]`, `-1` child sentinel); return the PRE-order label sequence,
    space-separated. Assert distinguishes pre- vs post-order and the `-1` sentinel base case (guarded with
    `== -1` before indexing). Complexity O(N).
- **M6 "Make it yours".** No new required problem — an extension round (see the brief).

Concept coverage (all 17 `requires`): input-parse→P1, prefix-sum→P1, simulation→P2, binary-search→P3,
greedy→P3, two-pointers→P4, sorted-key→P4, graph-repr→P5, bfs→P5, deque→P5, set-literal→P5, grid-2d→P2/P5/P6
(a `practices` concept), flood-fill→P6, recursion→P6/P7/P8, backtracking→P7, complete-search→P7,
tree-traversal→P8, dfs→P8. Before finalizing, run an ad-hoc `detect()` over the solution cells to confirm the
AST-features are genuinely used, and reviewer-check the techniques.

### Phase B — Author `brief.ipynb` + `teacher-notes.md` + `manifest.yaml`

- **`brief.ipynb`:** intro (contest rules + the `solve` contract + a markdown-only submission wrapper), then
  **6 sequential `## Milestone N`** rounds. M1–M5 present their problems (statement + sample I/O +
  constraints + the intended technique named), each with an EMPTY student code cell (no solutions). **M6
  "## Make it yours"** — extension ideas (add a problem, tighten a bound, optimize a solve). A
  **`## Requirements`** checklist (all 8 problems pass their samples under the `solve` contract; within the
  time budget). No `## Solution`/solution heading anywhere in the brief.
- **`teacher-notes.md`:** `## Goals`, `## Pacing` (3 lessons — a timed contest sitting + review),
  `## Common mistakes`, `## Discussion prompts`, `## Differentiation`, **`## Rubric`** (per-problem credit +
  the per-problem Big-O table + the signature mutant each problem's asserts kill).
- **`manifest.yaml`:** `id: project-03-mock-contest`, `kind: project`, `lessons: 3`, `introduces: []`,
  `requires:` the 17 techniques (already in the map), `practices:` the scanner-derived set (`grid-2d` +
  Book-1 features actually used). Update the `project-03-mock-contest` map entry's `practices` to match
  (manifest == map as sorted lists).

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

_(filled at Phase C)_

## Plan Review

_(4-way plan-review gate — consensus before any implementation)_

## Content Review

_(4-way content-review gate — consensus before PR)_
