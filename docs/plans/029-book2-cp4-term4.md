# Plan 029 — Book 2 CP4 "Mock Contest 4" (Term-4 finale) + CP1–3 practices errata

**Goal:** Add a fourth mock-contest checkpoint (CP4) after U14 covering Term 4 (grids/graphs +
two-pointers), and correct the CP1–3 manifests so every Book-2 concept has a pre-capstone practice home —
unblocking the practice-completeness gate for the capstone (plan 030).

**Architecture:** A timed Term-4 checkpoint mirroring CP1–CP3 (`## Question N`, 6–8 sequential, no stretch,
solutions run clean, teacher-notes with a `## Grading` heading). Plus a metadata errata: the Book-2 concepts
each of CP1/CP2/CP3 genuinely exercises move from `requires` into `practices` (matching Book 1, where
checkpoints are the practice homes — CP03 practices=25, CP04=33). CP4 additionally practices the three
stragglers no term checkpoint currently exercises (`set-literal`, `modular-arithmetic`, `code-tracing`).

**Tech stack:** Python `solve(data:str)->str` judge contract; `tools/` verification; `scripts/ci-local.sh`.

**Spec / design:** `docs/designs/001-book2-algorithms.md` (§7 amended by this plan: 14 units + **4**
mock-contest checkpoints + capstone). This plan edits a design doc — permitted within the plan lifecycle
(design docs are not on the human-review governance list).

## Global Constraints

- **Judge contract:** every reference solution is a pure `solve(data: str) -> str`; ZERO `input()` in any
  executable cell; the submission wrapper (`import sys; print(solve(sys.stdin.read()))`) appears ONLY as a
  MARKDOWN fenced block or in teacher-notes — NEVER a code cell (cell-lint's no-exec exemption is
  `kind=="unit"` only, so a wrapper code cell reds F821 on undefined `solve`). Deterministic; integer/string
  output only (no floats); every cell a unique id; no stored outputs; student `checkpoint.ipynb` cells empty.
- **Checkpoint conventions (verified vs `tools/notebooks.py`):** files = `manifest.yaml` /
  `checkpoint.ipynb` / `solutions.ipynb` / `teacher-notes.md`; headings `## Question N` (regex
  `^## Question \d+`), **6–8 sequential**; NO stretch tier (a `stretch` tag is a FAIL); teacher-notes needs
  SIX headings = the 5 unit headings + `## Grading`; concept-scan + closure run over BOTH
  `checkpoint.ipynb` and `solutions.ipynb`, exec-solutions over `solutions.ipynb` only, `checkpoint.ipynb`
  never executed. `manifest` must equal the map entry (introduces/requires/practices).
- **Checkpoint metadata (CORRECTED — this is the errata):** a checkpoint's `practices` holds the concepts
  its questions genuinely EXERCISE (Book-2 concepts introduced by earlier units + Book-1 concepts);
  `requires` holds only the direct structural parsing prerequisites (kept small, per Book 1). `introduces`
  is empty. `practices ∩ introduces` must be empty (trivially, no introduces). Every `requires`/`practices`
  id must be already-taught by the checkpoint's map position.
- **Closure at Term 4 (everything ≤ U14 is legal):** all of U01–U14's concepts may be used. STILL banned
  everywhere (scanner-blind → grep/AST, not concept-scan): `nonlocal`/`global`, `.pop()`, `.index`,
  `.setdefault`, `+=` (use `x = x + …`), comprehensions (ListComp/SetComp/DictComp/GeneratorExp — detector
  is INERT since comprehension was dropped), `del`, `.join`, `.union`/`.intersection`/`.difference`,
  `.remove`, chained comparison (`a<=b<c`), bare-container truthiness (`while queue:` → `while len(queue)>0`),
  list/str repetition (`[x]*n`, `'0'*n`), base/number shortcuts (`bin`/`hex`/`oct`/`format`/`int(x,base)`/
  f-string `:b`/`:x`/`0x`/`0b`/`0o`/3-arg `pow`/`divmod`/`.bit_length`/`.bit_count`), `defaultdict`/`heapq`/
  `queue`/`functools`/`itertools`/`Counter`/`math`/`sys.setrecursionlimit`. Allowed builtins ONLY
  {len, min, max, sorted, sum, abs, round}.
- **Idiom reminders:** adjacency-list = plain dict (`if u not in adj: adj[u] = []`); BFS = deque FIFO
  (`append` enqueue / `popleft` dequeue, `while len(queue) > 0`); DFS/flood-fill = recursion with `visited`
  set PASSED AS ARGUMENT; 4-neighbour; recursive-grid inputs capped R·C ≤ 400; converging two-pointers on a
  SORTED list; sliding window with an INCREMENTAL running sum on NON-NEGATIVE values; output built with ONE
  concat per statement (`result = result + piece`) — never `result + a + " " + b` (O(n²)); modular reduction
  enforced by INPUT SIZE (counts that overflow without reducing) + a brute-force cross-check, never by a
  reduce-midway-vs-end assert (impossible with Python's exact ints).

## Out of scope

- The capstone `project-03-mock-contest` itself — plan 030. This plan only makes its practice-completeness
  gate satisfiable (CP4 + CP1–3 errata bring `pre_capstone ⊇ all 31 Book-2 concepts`).
- Any change to U01–U14 lesson/exercise/solution CONTENT. CP1–3 changes are manifest + map metadata only
  (the questions already exercise these concepts; only their field placement is corrected).
- Changing the `practice_findings` tooling. The gap is closed by content (CP4) + metadata (errata), not by
  weakening the check — the check keeps its "reinforce every concept before the capstone" intent intact.
- **Verification-phase exemption:** N/A — this plan ships a checkpoint (CP4) WITH a named verification phase
  (Phase C). The CP1–3 errata is metadata-only and is verified by the same phase (coverage/manifest checks).

## Phases

### Phase A — CP1–3 practices errata (metadata only)

For each of CP1, CP2, CP3, in BOTH `book2/checkpoints/<cp>/manifest.yaml` AND the matching
`book2/curriculum/coverage-map.yaml` entry (kept byte-equal), move the Book-2 concepts the checkpoint's
questions genuinely exercise from `requires` into `practices`, leaving `requires` = the small parsing
prerequisites. Target Book-2 concepts to appear in each checkpoint's `practices`:

- **CP1** (Term 1): `grid-2d, boolean-algebra, complexity, set-ops, sorted-key, binary-search,
  complete-search, tuple` (+ existing Book-1 practices; `input-parse`/`str-split` stay listed).
- **CP2** (Term 2): `greedy, simulation, prefix-sum` (+ carried Term-1 concepts its questions reuse:
  `grid-2d, sorted-key, input-parse, str-split, tuple`).
- **CP3** (Term 3): `recursion, backtracking, deque, postfix-eval, base-conversion, bitwise-ops, bitmask,
  gcd, sieve, tree-traversal` (+ `complete-search, input-parse, str-split, tuple`).

`requires` after the move: the structural parsing prereqs only (`input-parse, str-split`, plus `grid-2d`
where a grid is parsed). Re-run coverage/manifest checks; each CP's `practices ⊆ seen` at its position
holds (all listed concepts are introduced by earlier units).

### Phase B — CP4 "Mock Contest 4" (Term-4 finale) authoring

Create `book2/checkpoints/checkpoint-04-mock-contest-4/` with `manifest.yaml`, `checkpoint.ipynb`
(student, empty cells, `## Question N`), `solutions.ipynb` (blind, pure `solve()`, ≥1 distinguishing
assert per question incl. mutation-hardened graph/window witnesses), `teacher-notes.md` (six headings incl.
`## Grading`, per-question Big-O, pacing). `lessons: 0.5`.

**7 questions** assessing Term 4 and picking up the three stragglers:
1. **Grid flood-fill count** (flood-fill, graph-repr as grid) — count/size regions; recursion + `visited`.
2. **Fewest-steps BFS** (bfs) — deque FIFO shortest path on a grid; FIFO-witness assert (a LIFO mutant
   returns a longer distance).
3. **Graph connectivity DFS** (dfs, graph-repr) — adjacency-list dict, recursion with `visited` arg.
4. **Converging two-pointers** (two-pointers) — pair/closest on a sorted list.
5. **Sliding window** (two-pointers) — longest/shortest window, incremental running sum, non-negative.
6. **Path-count mod 1e9+7** (modular-arithmetic + graph-repr/recursion) — count paths in a small DAG/grid,
   output mod 1000000007; input sized so the unreduced count is infeasible → genuine reduce-as-you-go;
   brute-force cross-check on small inputs; uses a `{...}` `visited`/seen **set-literal**.
7. **Trace-the-traversal** (code-tracing + set-literal) — given a short BFS/DFS routine and input, predict
   its printed output; a `{...}` set literal appears in the traced code and the solver.

**CP4 manifest:** `introduces: []`;
`requires: [graph-repr, bfs, dfs, flood-fill, two-pointers, input-parse, str-split, grid-2d]`;
`practices: [graph-repr, bfs, dfs, flood-fill, two-pointers, set-literal, modular-arithmetic, code-tracing,
recursion, deque, sorted-key, input-parse, str-split, grid-2d, tuple, <Book-1 concepts exercised>]`.
(The five Term-4 concepts appear in BOTH requires and practices — allowed; `practices` is what the
gate counts. `set-literal`/`modular-arithmetic`/`code-tracing` are the stragglers CP4 exists to home.)

Add the CP4 row to `book2/curriculum/coverage-map.yaml` (after U14, before `project-03-mock-contest`) and to
`book2/<...>/syllabus.md` (in map order) — `syllabus_findings` checks the table row + order.

### Phase C — Verification (named verification phase)

- `scripts/ci-local.sh` ALL GREEN: registry+lint, notebook execution+hygiene, manifest/prereq/coverage/
  stretch, concept-scan (over CP4 checkpoint.ipynb + solutions.ipynb), PDF build (book1-only), pre-merge
  guard.
- Coverage-check specifics to confirm: CP1–3 + CP4 manifests equal their map entries; `practice_findings`
  is still DEFERRED (capstone dir absent) so it does not fire here — but assert directly that
  `pre_capstone ⊇ all 31 Book-2 concepts` via an ad-hoc script (so plan 030's capstone will pass).
- Execute `solutions.ipynb` in a real kernel; every assert holds; run each `solve()` on its STATED sample.
- AST-grep CP4 for the always-banned scanner-blind traps (nonlocal/global, `.pop(`, `.index`, `+=`,
  comprehensions, chained comparison, bare truthiness, base shortcuts, banned imports); confirm modular
  reduction is size-enforced + brute-checked; confirm FIFO/sort mutation-witness asserts kill their mutants.

## Post-Execution Report

_(filled at Phase C)_

## Plan Review

_(4-way plan-review gate — consensus before any implementation)_

## Content Review

_(4-way content-review gate — consensus before PR)_
