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
  never executed. `manifest` must equal the map entry — the tool compares each concept list as a SORTED set
  (not byte-for-byte), so element ORDER is normalized but membership must match; duplicate ids are NOT
  collapsed — a repeated concept fails a separate duplicate check (`curriculum.py`).
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
  (Phase D). The CP1–3 errata is metadata-only and is verified by the same phase (coverage/manifest checks).

## Phases

### Phase A — CP1–3 practices errata (metadata only)

For each of CP1, CP2, CP3, in BOTH `book2/checkpoints/<cp>/manifest.yaml` AND the matching
`book2/curriculum/coverage-map.yaml` entry (kept equal as sorted sets), move the Book-2 concepts the checkpoint's
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

### Phase B — Design-001 amendment (§7 and §4)

Edit `docs/designs/001-book2-algorithms.md`:
- **§7 arc:** change "≈14 units + **3** mock-contest checkpoints + capstone" → "**4** mock-contest
  checkpoints"; add a **CP4 — Mock Contest 4** entry to the arc list, positioned after U14 and before the
  capstone, described as the Term-4 finale (grids/graphs + two-pointers).
- **§4 (contest-realism, line 24):** correct the stale "checkpoints are … **2–3 problems**" to match the
  shipped reality and the tooling bound (**6–8 questions**); CP1–CP3 all ship 6–7. The identical stale
  phrase also appears in `book2/syllabus.md` (Assessment-format section, "2–3 problems") — fix it there too
  (done in Phase C alongside the CP4 syllabus row).

### Phase C — CP4 "Mock Contest 4" (Term-4 finale) authoring

Create `book2/checkpoints/checkpoint-04-mock-contest-4/` with `manifest.yaml`, `checkpoint.ipynb`
(student, empty cells, `## Question N`), `solutions.ipynb` (blind, pure `solve()`, ≥1 distinguishing
assert per question incl. mutation-hardened witnesses), `teacher-notes.md` (six headings incl.
`## Grading`, per-question Big-O, pacing). `lessons: 0.5`.

**7 fully-pinned questions** (one concrete contract each — input, output, constraints/ties, intended
complexity, and the signature mutant its asserts must kill):

1. **Count the Islands** (flood-fill; grid-2d, recursion, **set-literal**). Input: line `R C`, then `R`
   rows of `#` (land) / `.` (water). Output: the integer count of 4-connected land regions. Reference:
   recursive flood-fill, `visited` seeded as a `{...}` **set literal** (e.g. `visited = {(r, c)}`), 4-neighbour.
   Constraints: `1 <= R, C`, `R*C <= 400` (recursive-grid cap). Complexity: **O(R·C)** (each cell visited
   once). Signature mutant: 8-neighbour (diagonals) merges regions → wrong count; assert includes a grid
   where two land cells touch only diagonally and must stay separate.
2. **Fewest Steps** (bfs; grid-2d, deque). Input: `R C`, then `R` rows with one `S`, one `T`, `#` walls,
   `.` open. Output: fewest 4-neighbour steps `S`→`T`, or `-1` if unreachable. Reference: deque FIFO
   (`append`/`popleft`, `while len(queue) > 0`), `visited` set, layer distance. Constraints: `R*C <= 2000`
   (iterative BFS, no recursion cap). Complexity: **O(R·C)** (each cell enqueued once). Signature mutant:
   LIFO (`popleft`→`pop`, i.e. a stack) returns a longer distance → a FIFO-witness assert on a grid where a
   stack overshoots.
3. **One Network?** (dfs, graph-repr; recursion). Input: `N M`, then `M` lines `u v` (undirected edges,
   nodes `1..N`). Output: `YES` if every node is reachable from node 1 (one connected component), else `NO`.
   Reference: adjacency-list plain dict (`if u not in adj: adj[u] = []`), recursive DFS with `visited`
   passed as an argument. Constraints: `1 <= N <= 300`, `0 <= M <= 2000`. Complexity: **O(N + M)**.
   Signature mutant: not marking the start visited / counting only direct neighbours → mislabels a
   disconnected graph; assert includes a 2-component graph (→ `NO`) and a connected one (→ `YES`).
4. **Exact Budget Pair** (two-pointers). Input: `N T`, then `N` non-negative integer prices. Output: `YES`
   if some two distinct items sum to EXACTLY `T`, else `NO`. Reference: `sorted()` (plain, numeric — no
   key), converging `lo`/`hi` (sum too small → `lo = lo + 1`; too big → `hi = hi - 1`). Constraints:
   `2 <= N <= 100000`, values fit int. Complexity: **O(N log N)** (the sort) then **O(N)** (the scan).
   Signature mutant: advancing the wrong pointer misses a valid pair; assert includes a case answerable only
   by the correct pointer move, and a no-pair case (→ `NO`).
5. **Longest Affordable Streak** (two-pointers / sliding window). Input: `N K`, then `N` non-negative costs.
   Output: the length of the LONGEST contiguous window with sum `<= K` (0 if none). Reference: grow `right`,
   shrink `left` while `window_sum > K`, running sum maintained incrementally. Constraints: `1 <= N <=
   100000`, non-negative values (stated). Complexity: **O(N)** (each index enters/leaves the window once).
   Signature mutant: never shrinking `left` → over-long window; assert includes an input where an early
   expensive item forces a shrink.
6. **Astronomical Power Modulo M** (modular-arithmetic) — mirrors U11 Ex8 (the genuine reduce-as-you-go
   assessment; NOT a count). Input: `A M E` (non-negative base, positive modulus, non-negative exponent).
   Output: `A**E mod M` as a non-negative integer, via repeated squaring reducing `% M` after every
   multiply/square (`answer = answer * current % M`, `current = current * current % M`,
   `exponent = exponent >> 1`). **3-arg `pow` prohibited**; O(log E) modular multiplications required.
   Constraints: `0 <= A <= 10^18`, `1 <= M <= 10^18`, `0 <= E <= 10^18`. **Enforcement (genuine):** the
   huge-`E` sample (`7 13 1000000000000000000` → `9`, from U11) makes an unreduced `A**E` astronomically
   infeasible to even compute — a no-reduction solution cannot produce output at all, so reduce-as-you-go is
   forced by feasibility, not by a value-differing assert. Complexity: **O(log E)** modular multiplications.
   Asserts: small-`E` correctness cases against a brute `A**E % M` oracle (`2 5 3`→`3`, `20 7 1`→`6`,
   `9 1 0`→`0`, `3 11 0`→`1`, and — crucially — an even/internal-zero-bit exponent `2 5 4`→`1`) PLUS the
   huge-`E` case (`7 13 1000000000000000000`→`9`). Signature mutants and how each is killed — both `% M`
   sites are load-bearing, one by feasibility and one by output value:
   (a) **guard-drop** (`if exponent & 1` removed → always multiply): survives odd/all-ones exponents but is
   killed at small scale by `2 5 4`→`1` (the mutant returns 3, since bits 0 and 1 of E=4 are zero).
   (b) **square-side reduction dropped** (`current = current * current` without `% M`): `current` grows to
   `A**(2^k)` — astronomically large after ~60 doublings — so the huge-`E` case becomes INFEASIBLE to
   compute. This is the feasibility-forced mutant, killed by the huge-`E` assert (a no-reduction solver
   cannot produce output).
   (c) **answer-side reduction dropped** (`answer = answer * current` without `% M`): stays feasible but
   leaves `answer` UNREDUCED, so it is killed BY VALUE — `2 5 3` yields 8 (≠3), and huge-`E` yields a raw
   multi-digit integer (≠9). (There is no separate "final `% M`" — the algorithm keeps `answer` reduced at
   each step, so the answer-side `% M` IS the reduction the small-case value witnesses.)
7. **Trace the Traversal** (code-tracing; **set-literal**). The question markdown SHOWS a short fixed BFS
   routine (reproduced verbatim in the question) that seeds `visited = {start}` (a `{...}` **set literal**),
   uses a deque FIFO, appends a dequeued node's neighbours **in the order they appear in that node's
   adjacency list**, marks each on enqueue, and prints each node as it is dequeued. The student predicts the
   exact printed output. **Pinned input format** (the judge `data` the shown routine consumes): first line
   `N M start` (nodes `1..N`, `M` edges, BFS start node); then `M` lines `u v`, each a **directed** edge
   `u → v`; the adjacency list of each node lists its out-neighbours **in input order** (no sorting), so the
   trace is deterministic. Output: the space-separated node ids in dequeue order. Reference `solve(data)`:
   parse this input and REPRODUCE the shown routine exactly (same `{...}` visited literal, same input-order
   neighbour appends, same FIFO order), returning its printed order — a pure `solve()` per the contract.
   Constraints: `1 <= N <= 30`, `0 <= M <= 200`. Complexity: **O(N + M)**. Signature mutant: reading the
   traversal in LIFO (stack) order yields a different sequence → asserts pin the true FIFO order on a graph
   whose input-order adjacency makes FIFO≠LIFO.

**CP4 manifest:** `introduces: []`;
`requires: [input-parse, str-split, grid-2d]` (structural prerequisites);
`practices: [graph-repr, bfs, dfs, flood-fill, two-pointers, set-literal, modular-arithmetic, code-tracing,
recursion, deque, <Book-1 concepts genuinely exercised>]`.
Notes: `sorted-key` and `tuple` are NOT listed for CP4 (Q4 uses plain numeric `sorted()`; no keyed sort) —
both are already homed by CP1/CP2/CP3, so completeness is unaffected. A concept may appear in both
`requires` and `practices` (permitted by the tooling and used in Book-1 CP03/CP04); the gate counts only
`practices`. The eight concepts CP4 is the sole pre-capstone home for — `graph-repr, bfs, dfs, flood-fill,
two-pointers, set-literal, modular-arithmetic, code-tracing` — each map to a genuine question above.

Add the CP4 row to `book2/curriculum/coverage-map.yaml` (after U14, before `project-03-mock-contest`) and to
`book2/syllabus.md` (in map order) — `syllabus_findings` checks the table row and its order. In the SAME
`book2/syllabus.md` edit, correct the stale "2–3 problems" phrase in the Assessment-format section to "6–8
questions" (paired with the design-001 §4 fix in Phase B). Manifest and map entry are kept equal (the tool
compares each concept list as SORTED lists, not byte-for-byte; duplicate ids fail separately).

### Phase D — Verification (named verification phase)

- `scripts/ci-local.sh` ALL GREEN: registry+lint, notebook execution+hygiene, manifest/prereq/coverage/
  stretch, concept-scan (over CP4 checkpoint.ipynb + solutions.ipynb), PDF build (book1-only), pre-merge
  guard.
- Coverage-check specifics to confirm: CP1–3 + CP4 manifests equal their map entries; `practice_findings`
  is still DEFERRED (capstone dir absent) so it does not fire here — but assert directly that
  `pre_capstone ⊇ all 31 Book-2 concepts` via an ad-hoc script (so plan 030's capstone will pass).
- Execute `solutions.ipynb` in a real kernel; every assert holds; run each `solve()` on its STATED sample.
- AST-grep CP4 for the always-banned scanner-blind traps (nonlocal/global, `.pop(`, `.index`, `+=`,
  comprehensions, chained comparison, bare truthiness, base shortcuts, banned imports).
- **Q6 modular**: confirm the huge-`E` case is present and the reference is O(log E) repeated-squaring with
  `% M` after every multiply/square; confirm no 3-arg `pow`; verify the small-`E` asserts match a brute
  `A**E % M` oracle; verify each mutant dies to the stated witness: guard-drop → `2 5 4`→`1`; square-side
  `% M` drop (`current = current * current`) → the huge-`E` case (infeasible, no output); answer-side
  `% M` drop (`answer = answer * current`) → killed by value on `2 5 3` (→8) and huge-`E` (raw integer).
- **Per-question signature mutants**: confirm each pinned question's asserts kill its named mutant
  (Q1 8-neighbour, Q2 LIFO-overshoot, Q3 disconnected mislabel, Q4 wrong-pointer, Q5 never-shrink,
  Q7 wrong-order trace).
- Confirm `docs/designs/001-book2-algorithms.md` §7 lists CP4 (4 checkpoints) and §4 says 6–8.

## Post-Execution Report

**Shipped:** CP4 "Mock Contest 4" (Term-4 finale checkpoint) + the CP1–3 practices errata + the design-001
§7/§4 and syllabus amendments. This is the 18th of 18 map entries' enabling work — it makes the capstone
(plan 030) authorable; with CP4 merged, Book 2 will be 18/18 once the capstone lands.

**Phase A (errata):** CP1/CP2/CP3 manifests + coverage-map entries rewritten so `requires` holds only the
parsing prerequisites (`input-parse, str-split`) and the assessed Book-2 concepts moved into `practices`
(matching Book 1, where checkpoints are the practice homes). No notebook content changed — the questions
already exercised these concepts; only the metadata field placement was corrected.

**Phase B (design):** `docs/designs/001-book2-algorithms.md` §7 updated to "14 units + **4** mock-contest
checkpoints + capstone" with a CP4 arc entry after U14; §4's stale "2–3 problems" → "6–8 questions". The
same stale phrase in `book2/syllabus.md` was corrected and the Term-4 shape + arc table updated.

**Phase C (CP4):** `book2/checkpoints/checkpoint-04-mock-contest-4/` with `manifest.yaml`, `checkpoint.ipynb`
(7 `## Question N` blocks, empty student cells, markdown-only submission wrapper), `solutions.ipynb` (7 pure
`solve()` with sample + distinguishing asserts), and `teacher-notes.md` (six headings incl. `## Grading`,
per-question Big-O table). 7 questions: Q1 Count the Islands (flood-fill), Q2 Fewest Steps (BFS), Q3 One
Network? (DFS connectivity), Q4 Exact Budget Pair (converging two-pointers), Q5 Longest Affordable Streak
(sliding window), Q6 Astronomical Power Modulo M (modular exponentiation, repeated squaring `% M` each step),
Q7 Trace the Traversal (code-tracing, `{start}` set literal). CP4 `practices` homes the 8 concepts CP1–3
don't reach — `graph-repr, bfs, dfs, flood-fill, two-pointers, set-literal, modular-arithmetic, code-tracing`
— so `pre_capstone ⊇ all 31` (verified).

**Phase D (verification):** `scripts/ci-local.sh` — all book2 checks (prereq, coverage, concept-scan,
manifest, structure, hygiene, cell-lint, noexec, stretch, exec-solutions) PASS; solutions execute clean with
every assert holding; each signature mutant confirmed killed (Q1 8-neighbour→wrong count, Q2 LIFO→8 vs 2,
Q3 disconnected→NO, Q4 wrong-pointer→NO, Q5 never-shrink→5 vs 3, Q6 guard-drop→3 on `2 5 4`, Q7 LIFO→
`1 3 4 2` vs `1 2 3 4`). `pre_capstone ⊇ all 31 Book-2 concepts` asserted directly (`practice_findings`
stays deferred until the capstone dir exists). Q6 authored in the arithmetic form (`% 2 == 1`, `// 2`)
matching U11's shipped solution `u11s0011`, avoiding bitwise-ops/integer-truthiness.

**Deviations from plan:** (1) Q6 uses `% 2 == 1` / `// 2` instead of `& 1` / `>> 1` — equivalent repeated
squaring, matches U11's shipped solution, and avoids listing bitwise-ops. (2) `tuple` and `set-ops` are in
CP4 `practices` after all — the plan dropped `tuple`, but coordinate tuples (`(r, c)`) and `visited.add`
are genuinely used, so the scanner requires them listed; both are also homed elsewhere, so this does not
affect completeness. `sorted-key` stays dropped (Q4 uses plain `sorted()`).

## Plan Review

### Round 1 (2026-09-09, HEAD 5ae3703) — [self] AWN · [fable] AWN · [glm] REJECT · [sol] REJECT

All four independently verified: the 31-concept completeness (`pre_capstone ⊇ known` after Phase A + CP4),
the requires→practices migration safety (breaks no check — `referenced_concepts`/prereq/`checkpoint_findings`/
`practice_findings`/`manifest` all neutral to the move), the checkpoint conventions, and the named
verification phase. The two REJECTs and both AWN sets converge on the same blocking issue (Q6) plus
pinning/wording. Findings and dispositions:

1. `[FIXED]` **[all four, blocking] Q6 was the plan-027 fake-modular trap.** A "small DAG/grid path count,
   input sized so the unreduced count is infeasible" is self-contradictory: under the recursive-grid cap
   (R·C ≤ 400) the exact count is a few-hundred-bit int Python handles instantly, so `% M` at the end always
   passes — reduce-as-you-go is never forced (Python has no int overflow; a reduce-midway-vs-end assert is
   impossible). → **Replaced Q6 with "Astronomical Power Modulo M" (modular exponentiation, A^E mod M, E up
   to 10^18, repeated squaring, 3-arg `pow` banned, O(log E))**, mirroring U11 `u11l0015` + U11 Ex8. This is
   a GENUINE reduce-as-you-go assessment: an unreduced `A**E` at E=10^18 is astronomically infeasible to
   compute, so a no-reduction solution cannot even produce output on the huge-E case. `graph-repr`/
   `recursion` stay covered by Q1/Q3; `set-literal` moves to Q1 (flood-fill `visited = {(r,c)}` literal) and
   Q7 (traced routine's `{...}`).
2. `[FIXED]` **[sol+glm, blocking] Questions were alternatives, not pinned contracts.** Q1 (count/size), Q4
   (pair/closest), Q5 (longest/shortest), Q6 (DAG/grid), Q7 (unspecified routine). → Phase C now pins ONE
   concrete contract per question (input, output, constraints/ties, intended complexity, and the signature
   mutant its asserts kill): Q1 count-of-islands, Q4 exact-pair YES/NO, Q5 longest window ≤ K, Q7 the shown
   fixed BFS routine + exact visit-order output.
3. `[FIXED]` **[sol, blocking] The design-001 §7 amendment wasn't in the implementation phases.** → Added
   **Phase B** (edit §7 to 4 checkpoints + add the CP4 arc entry; also correct §4's stale "2–3 problems" to
   6–8, per [fable] Nit 4). Phase D verifies the design contains CP4.
4. `[FIXED]` **[fable+glm+sol] CP4 practices listed `sorted-key` and `tuple` with no genuine question home**
   (Q4 uses plain numeric `sorted()`). → Dropped both from CP4 `practices`; both remain homed by CP1/CP2/CP3,
   so completeness is unaffected (re-verified 31/31).
5. `[FIXED]` **[fable Nit 3] Q7 mechanics under the judge contract.** → Q7 now states `solve(data)` parses
   the shown routine's input and returns its exact printed visit order (a pure `solve()`); asserts pin the
   true FIFO order on a graph where FIFO≠LIFO.
6. `[FIXED]` **[sol nits] Wording.** `book2/syllabus.md` (not `book2/<...>/syllabus.md`); "sorted-set
   equality" not "byte-equal" for manifest==map; requires/practices overlap acknowledged as permitted
   (Book-1 CP03/CP04) rather than claimed disjoint.

Non-blocking nits noted and accepted (no plan change needed): [fable/glm] CP3 `tuple` and CP2 `sorted-key`
practice claims are thin-but-genuine (each also homed elsewhere) — the content gate will confirm the actual
question exercises them. Round 2 re-review pending on the revised plan.

### Round 2 (2026-09-09, HEAD 5d22de9) — [fable] AWN · [glm] AWN · [sol] REJECT

[fable] and [glm] both re-verified Q6 against the shipped U11 content (independently confirming
`7^(10^18) mod 13 = 9`), ran the actual tooling on a simulated end-state ([glm]: prereq/coverage/manifest/
concept-scan all PASS, 31/31), and confirmed all round-1 fixes. All three converged on one Q6-mutant-prose
nit; [sol] (REJECT) added two more precision findings. Dispositions:

1. `[FIXED]` **[sol/fable/glm] Q6 mutant prose was wrong.** The `if exponent & 1` guard-drop mutant survives
   the four listed small cases (E=3 is `11`, E=1, E=0 — no internal zero bit) and the "omit final `% M`"
   mutant is inert (the algorithm keeps `answer` reduced every step). → Added an internal-zero-bit assert
   `2 5 4`→`1` (guard-drop returns 3 → killed at small scale; verified) and reworded both the Phase C and
   Phase D Q6 text: guard-drop is killed by `2 5 4`; the per-multiply `% M` removal is caught by the huge-`E`
   case (feasibility), and there is no separate "final `% M`".
2. `[FIXED]` **[sol, blocking] Q7 input contract under-specified.** → Q7 now pins the exact format
   (`N M start`; `M` directed edges `u v`; adjacency in input order; BFS prints dequeue order), making the
   trace deterministic.
3. `[FIXED]` **[sol, blocking] "intended complexity" promised but Big-O absent from Q1–Q5/Q7.** → Added an
   explicit Complexity line to every question (Q1/Q2 O(R·C), Q3/Q7 O(N+M), Q4 O(N log N), Q5 O(N),
   Q6 O(log E)).
4. `[FIXED]` **[sol, blocking] §4 "2–3 problems" edit targeted only design-001; the stale phrase is in BOTH
   design-001 line 24 AND `book2/syllabus.md`.** → Phase B fixes design-001 §4; Phase C fixes the same phrase
   in `book2/syllabus.md` alongside the CP4 row.
5. `[FIXED]` **[sol] Wording.** "duplicates are normalized" was false (the tool sorts lists, does not
   dedupe; duplicate ids fail a separate check) → corrected. Stale "(Phase C)" cross-reference → "(Phase D)".

### Round 3 (2026-09-09, HEAD 006d59b) — [glm] APPROVE · [fable] AWN · [sol] REJECT (one shared prose nit)

[glm] APPROVE (no blockers; guard-drop kill re-verified by execution, 31/31 reconfirmed). [fable] and [sol]
both re-ran the Q6 mutants numerically and confirmed findings 1 (§4 both files) and 2 (Q7 pin + Big-O)
RESOLVED, but flagged the SAME residual imprecision in the mutant-(b) prose — [fable] as a non-blocking nit
("no kill-matrix hole"), [sol] as blocking. Both are right about the fix:

- `[FIXED]` **Q6 mutant-(b) prose mis-attributed which `% M` site feasibility catches.** Dropping the
  ANSWER-side `% M` (`answer = answer * current`) stays feasible and is killed BY VALUE (`2 5 3`→8,
  huge-`E`→`50031545098999707`, both ≠ pristine) — NOT by feasibility. The genuinely feasibility-forced
  mutant is dropping the SQUARE-side `% M` (`current = current * current`), which grows `current` to
  `A**(2^k)` (~1.6×10¹⁸ bits at E=10¹⁸ → infeasible) while PASSING small cases. → Reworded Phase C and
  Phase D to name three mutants, each with its correct witness: guard-drop→`2 5 4`, square-side→huge-`E`
  (feasibility), answer-side→small-case value. Verified all three numerically. (Findings 1 and 2 were
  `[FIXED]` in round 2 and re-confirmed RESOLVED by [sol] here.)

### Round 4 (2026-09-09, HEAD f456149) — [sol] APPROVE

[sol] re-ran all three Q6 mutants and confirmed finding 3 resolved: guard-drop `2 5 4`→3, square-side drop
passes small cases but ~1.6×10¹⁸ bits on huge-`E` (feasibility witness), answer-side drop feasible and
value-killed (`2 5 3`→8, huge→`50031545098999707`). "Nothing remains."

### CONSENSUS — plan-review gate CLOSED

[self] APPROVE · [glm] APPROVE · [fable] APPROVE (round-3 AWN; the one nit was fixed in round 4) ·
[sol] APPROVE. Full 4-way blocking consensus, zero open findings. Cleared for implementation (Phases A–D).

## Content Review

### Review 1 — [self] (2026-09-09, HEAD 01d2ed7)

**APPROVE.** Verified: all 7 CP4 solutions execute clean in a real kernel with every assert holding; each
signature mutant is killed by a distinguishing assert (Q1 8-neighbour→1 vs 2 on `2 2\n#.\n.#`; Q2 LIFO→8 vs
2; Q3 disconnected→NO; Q4 wrong-pointer→NO; Q5 never-shrink→5 vs 3; Q6 guard-drop→3 on `2 5 4`, huge-`E`
feasibility; Q7 LIFO→`1 3 4 2` vs `1 2 3 4`). concept-scan clean (no used-but-unlisted, no untaught methods);
all book2 checks + exec-solutions PASS; `pre_capstone ⊇ all 31` verified. Conventions met (7 `## Question N`,
no stretch, six teacher-notes headings incl. `## Grading`, markdown-only wrapper, unique ids, no outputs).
Errata: each concept moved into CP1/CP2/CP3 practices is exactly what those checkpoints' questions assess.

Deviations documented in the post-execution report: Q6 uses `% 2 == 1` / `// 2` (matches U11's shipped
solution `u11s0011`, avoids bitwise-ops/integer-truthiness); `tuple`/`set-ops` remain in CP4 practices
(coordinate tuples + `visited.add` genuinely used); `sorted-key` stays dropped (Q4 uses plain `sorted()`).

### Reviews 2–3 — [glm] & [fable] (2026-09-09, HEAD 01d2ed7) — both APPROVE WITH NITS

Both blind-solved all 7 questions independently ([fable] with 400 randomized cross-checks per question,
brute/`pow` oracles) — **all 7 reference solutions correct, all samples match**, all specified critical
asserts confirmed non-vacuous by mutant execution, house rules clean (AST scans zero hits), and all CP1–3
errata practice claims verified genuinely exercised. No blocking findings. Nits (all `[FIXED]` unless noted):

1. `[FIXED]` **[fable NIT-1] Q3 directed-edge mutant survives** — dropping `adj[v].append(u)` (the common
   "forgot undirected" bug) passed all 4 asserts. → Added `solve("2 1\n2 1") == "YES"` (directed mutant → NO;
   verified).
2. `[FIXED]` **[fable NIT-2] Q4 distinctness untested** — a `while lo <= hi` self-pair mutant and a
   build-set-then-membership mutant survived. → Added `solve("3 8\n1 4 6") == "NO"` (verified kills both).
3. `[FIXED]` **[fable NIT-3] Q5 reset-on-overflow mutant survives** — restart-window-at-current passed all 4
   asserts. → Added `solve("5 9\n2 2 3 3 1") == "4"` (mutant → 3; verified).
4. `[FIXED]` **[fable NIT-4 = glm nit-2] Q7 relied on Q2's `deque` import** (cell order). → Added
   `from collections import deque` to Q7's own solution cell (self-contained).
5. `[FIXED]` **[glm nit-1] CP4 student cells shipped a `def solve(data): … pass` scaffold** vs CP1–3's truly
   EMPTY cells (and the report's "empty student cells" claim). → All 7 `checkpoint.ipynb` student code cells
   emptied to match the shipped convention.
6. `[WONTFIX]` **[glm nit-3] CP3 `tuple` is thin** (exercised only by the Q5 swap `a, b = b, a % b`) — genuine
   and also homed by CP1/CP2; no change (matches the plan-review disposition).

Solutions re-executed clean with the three new asserts; all book2 checks PASS at the patched HEAD.
[self] APPROVE stands. Awaiting [sol] blind-solve on the patched version.
