# Plan 023 — Book 2 U08 "Prefix Sums"

**Goal:** Ship the final Term-2 unit — `unit-08-prefix-sums` (introduces the TECHNIQUE `prefix-sum`) — on
the `solve(data:str)->str` contract, following the established Book-2 technique-unit pattern (U02/U03/U05/
U06/U07).

**Architecture:** One unit, the standard Book-2 set (lesson/exercises/solutions/teacher-notes/manifest).
`prefix-sum` is a reviewer-enforced **technique** (scanner-invisible): a precomputed cumulative-sum array
that answers a range-sum query in O(1) after O(n) build, extended to a 2D grid with the inclusion-exclusion
formula. Graded exercises are `solve(data)` problems that REQUIRE the prefix-sum shape (many range queries,
or a 2D sub-rectangle sum, where recomputing each answer would be too slow). Wire into ci-local via the
existing Book-2 per-entry block.

**Tech Stack:** Jupyter notebooks (nbformat), `tools/` checks, `scripts/ci-local.sh`,
`py4kids-tools --book book2`; Python 3 stdlib only.

**Spec:** `docs/designs/001-book2-algorithms.md` (§4 unit anatomy, §5 two-tier concepts, §7 U08: "1D
cumulative sums for O(1) range queries → 2D on a grid"); `book2/syllabus.md`; `book2/curriculum/
coverage-map.yaml` (U08 entry); plans 018–022 (the shipped Book-2 unit pattern — all closure rules
transfer); the plan-019..022 content-gate lessons (mutation categories; `.remove` ban; untaught-builtin
ban; scanner-blind untaught surface — list-repetition `[x]*n`, chained comparison `a<=b<c`; one-directional
concept-scan; cell IDs required).

## Global Constraints

Copied from the design + registry + prior-gate lessons; every task's requirements include this section.

- **Contract:** every reference solution is a pure `solve(data: str) -> str`; ZERO `input()` in any
  executable cell; the submission wrapper `import sys; print(solve(sys.stdin.read()))` appears ONLY in a
  `no-exec`-tagged LESSON cell (units get the `kind=="unit"` cell-lint exemption) or in teacher-notes;
  NEVER in solutions.ipynb. Deterministic. Student code cells are EMPTY (`''`). **Every notebook cell has
  an `id`** (codex authors sometimes omit them → nbformat warning; add via uuid if missing).
- **New concept is a TECHNIQUE (scanner-invisible):** `prefix-sum` is reviewer-enforced — genuinely taught
  in the lesson/teacher-notes and USED by the exercises; it is U08's `introduces`, never its own practice.
  Earlier techniques used (e.g. `input-parse`, `grid-2d`, `complexity`) are hand-listed in practices/requires.
- **Closure (same scanner rules as U02–U07):** only Book-1 + U01–U07 concepts + `prefix-sum`. If sets are
  used: `.add`/`.discard` on a `{…}`/`set()` var in-cell, or `-`; **NOT `.remove`**; NEVER `&|^`; NEVER
  `.union`/`.intersection`/`.difference`. `sorted(seq, key=named_fn)` (NO lambda). binary-search, fixed-depth
  nested-loop complete-search, greedy, simulation all allowed (≤U07). **NO not-yet-taught concept: no
  recursion/backtracking (U09), no `deque`/`.pop` (U10), no `comprehension`/generator expressions (U09), no
  `bitwise-ops`/`base-conversion` (U11), no converging two-pointer (U14).** **NO scanner-blind untaught
  surface: no list-repetition `[x] * n` (build with a while/append loop), no chained comparison `a <= b < c`
  (use `b >= a and b < c`).** NO untaught methods (.join/.splitlines/.index/.count/.find/.pop). Allowed
  builtins ONLY `{len,min,max,sorted,sum,abs,round}` — NO `all`/`any`/`enumerate`/`zip`/`reversed`/`map`/
  `filter`. **Enforcement split:** concept-scan + ad-hoc `detect()` catch premature FEATURES + untaught
  methods; `.remove`, the banned builtins, list-repetition, and chained comparisons are scanner-BLIND →
  enforce by **grep + reviewer read**. concept-scan `--book book2` clean.
- **Two-tier `practices` (plan-020 formula):** `practices = (detected ∪ manually-listed used) − requires −
  introduces − wrapper-artifacts (file-read, import-statement)` — a concept in `requires` never appears in
  `practices`. So `str-split` (feature, if used) + earlier techniques used-and-not-in-requires (`input-parse`,
  `complexity`) + Book-1 concepts used. `requires ∩ practices = ∅`, `practices ∩ introduces = ∅`; manifest
  == coverage-map exactly. Derive from ad-hoc `detect()`; hand-add scanner-invisible used concepts.
- **Rich, laddered problem set:** ≥ 8 `## Exercise N` (tooling counts `^## Exercise \d+`), each with Sample
  Input / Sample Output / Constraints; ≥ 2 cell-tagged `stretch` (heading "Challenge"). **Every output is
  an INTEGER or plain string — never a float.** Non-vacuous asserts: sample + crafted edge cases killing
  the prefix-sum-specific mutants — **off-by-one on the prefix index** (`pre[i]` vs `pre[i-1]`, inclusive
  vs exclusive range endpoints), the **2D inclusion-exclusion formula** (`+pre[r2][c2] -pre[r1-1][c2]
  -pre[r2][c1-1] +pre[r1-1][c1-1]` — a wrong sign or a dropped/miscornered term), a **single-element or
  full-array range**, and a query whose decisive cells are at the **last row/column / array end**. Place
  the decisive value last.
- **teacher-notes:** exactly the five heading strings `## Goals`/`## Pacing`/`## Common mistakes`/
  `## Discussion prompts`/`## Differentiation`; a per-exercise Big-O line (build O(n) or O(R·C), each query
  O(1)); a pacing plan covering both lessons (L1 1D prefix sums + range queries; L2 2D grid prefix sums).

## Out of scope

- No new feature or tooling change; no checkpoint (CP2 is plan 024, assesses U06–U08).
- **Verification is NOT out of scope:** **Phase B** is the named verification phase (blind-solve + mutation +
  full ci-local + 4-way content gate).

---

## Phases

### Phase A — U08 "Prefix Sums" (2 lessons)

**Files:**
- Create: `book2/units/unit-08-prefix-sums/{lesson,exercises,solutions}.ipynb`, `teacher-notes.md`,
  `manifest.yaml`
- Modify: `book2/curriculum/coverage-map.yaml` (fill the U08 entry's `practices` + trim `requires` to used —
  both mirror the manifest since manifest==map)

**Interfaces:**
- Consumes: Book-1 (list, for-loop, accumulator, nested-loops) + U01 `grid-2d`/`input-parse`.
- Produces: technique `prefix-sum` (prereq for CP2 and later units).

- [ ] **A1 — lesson.ipynb.** Contest hook (e.g. "answer many range-sum queries over a big array fast", then
  "sum any sub-rectangle of a grid"). Teach: (1) build the 1D prefix array `pre[0]=0`, `pre[i]=pre[i-1]+a[i-1]`,
  and answer `sum(l..r) = pre[r+1]-pre[l]` in O(1); stress the index convention and the off-by-one; (2) the
  2D grid prefix sum and the inclusion-exclusion rectangle formula, with a hand-traced small example. Runnable
  `solve(data)` cells (integer outputs, scanner-clean — build arrays with while/append, no `[x]*n`); one
  `no-exec` wrapper cell.
- [ ] **A2 — exercises.ipynb.** ≥ 8 `## Exercise N` `solve(data)` problems that REQUIRE prefix sums
  (constraints make per-query recomputation too slow, or a 2D sub-rectangle sum is asked): many 1D range-sum
  queries, count-in-range via prefix counts, max/target range using cumulative sums, 2D sub-rectangle sum,
  count/aggregate over a grid region, longest/best window whose running total meets a bound. All problems
  are solvable with plain 1D/2D prefix-sum reasoning as taught in A1 — do NOT introduce a difference-array
  or any un-taught trick (taught-before-assessed is law). ≥ 2 `stretch`. EMPTY
  student cells; Sample I/O + Constraints; INTEGER outputs; decisive cells at the last position / last
  row-column. Statements unambiguous.
- [ ] **A3 — solutions.ipynb (FRESH author, blind).** Mirror `## Exercise N`; pure `solve(data)`; build
  prefix arrays with while/append (no list-repetition, no chained comparison); 2D uses the inclusion-
  exclusion formula. Non-vacuous asserts incl. off-by-one on the prefix index, a wrong-sign/dropped-term 2D
  formula mutant, single-element and full-range queries, and a decisive-last-cell case.
- [ ] **A4 — teacher-notes.md.** Five exact headings; per-exercise Big-O (O(n)/O(R·C) build, O(1) per query);
  2-lesson pacing (L1 1D; L2 2D); common mistakes (the ±1 index convention; the 2D inclusion-exclusion signs;
  querying before building).
- [ ] **A5 — manifest.yaml + map.** `introduces: [prefix-sum]`; `requires:` = genuinely-used prereqs (the
  map seeds `list-literal`/`list-append`/`for-loop`/`loop-counter`/`accumulator`/`grid-2d`/`nested-loops`);
  `practices:` = `used − requires − introduces − wrapper-artifacts` (Book-1 concepts + `str-split` +
  `input-parse` if not in requires); `requires ∩ practices = ∅`, `practices ∩ introduces = ∅`; `lessons: 2`;
  manifest == map.
- [ ] **A6 — verify U08 in isolation:** all `--book book2` checks PASS; concept-scan clean (ad-hoc `detect()`
  shows no premature FEATURE). For the scanner-blind slips, run an **AST check** over every code cell (more
  robust than grep): flag any `ast.Compare` with `len(node.ops) > 1` (chained comparison) and any
  `ast.BinOp` with `ast.Mult` where either operand is a list (`ast.List`) — i.e. list-repetition; also grep
  `.remove(` and the banned builtins (`all`/`any`/`enumerate`/`zip`/`reversed`/`map`/`filter`). Confirm
  prefix-sum is genuinely taught + used.

### Phase B — Verification (named verification phase)

- [ ] **B1 — blind-solve + mutation self-check** (off-by-one prefix index, 2D formula sign/term, single/full
  range, decisive-last — every mutant fails an assert; every pristine solver passes). Confirm prefix-sum
  genuinely taught + exercised; no premature concept. Fix any vacuous assert.
- [ ] **B2 — full `scripts/ci-local.sh` ALL GREEN both books** (run in the foreground with a long timeout —
  the PDF build is environmentally flaky in background).
- [ ] **B3 — commit Phase A+B** on `feature/plan-023-book2-u08`.
- [ ] **B4 — 4-way content-review gate** ([self]/[sol]/[glm]/[fable], read-only, HEAD-pinned): blind-solve;
  mutation sweep (categories above, esp. the ±1 prefix index and the 2D inclusion-exclusion formula);
  per-technique TAUGHT checklist (1D build/query · off-by-one convention · 2D grid prefix · inclusion-
  exclusion); technique metadata + prematurity (prefix-sum introduced not premature; NO recursion/`deque`/
  `.pop`/comprehension/two-pointer/`.remove`/list-repetition/chained-comparison/untaught-builtin); solution
  shape matches Big-O; manifest==map; structure; cell IDs present. Resolve every `[OPEN]`; re-verify in
  round-2 before consensus.
- [ ] **B5 — commit content-gate fixes, write the post-execution report**, re-run full `ci-local.sh` ALL
  GREEN — all precede the PR.
- [ ] **B6 — PR** → `pre-merge-guard.sh --pr` OK → squash-merge → delete branch → update memory.

## Post-Execution Report (2026-09-08)

**Delivered:** `unit-08-prefix-sums` — the final Term-2 unit — on the `solve(data:str)->str` contract.
- **Phase A** — lesson (2 lessons: 1D prefix build + O(1) range query with the ±1 convention; 2D grid
  prefix + the four-term inclusion-exclusion formula) + 9 integer-output exercises (2 stretch): 1D range
  totals/counts/target/max, 2D sub-rectangle sums/region-count/max, and two stretch window problems.
  Statements + fresh blind solutions authored by separate codex sessions; teacher-notes + manifest inline.
  AST-verified NO list-repetition `[x]*n` and NO chained comparison `a<=b<c` (the two closure slips from
  plan 022), no `.remove`/`.pop`/floats, all cells have IDs. `practices = used − requires − introduces −
  wrapper-artifacts`; manifest==map. Committed 0f63ac2.
- **Phase B** — verification. Full `scripts/ci-local.sh` ALL GREEN both books. 4-way content gate: round 1
  confirmed all 9 solvers correct (fable 3,600 differential trials; sol/glm blind) with every ±1-index and
  2D inclusion-exclusion mutant killed and AST closure clean, but flagged 5 documentation/metadata items
  (Ex9 no-window guarantee, Ex9 Big-O O(n)→O(n²), Ex9 name, Ex4 extension wording, unused `for-loop`
  require) — all fixed with NO solution change (solutions byte-identical), round 2 unanimous APPROVE.
  Fixes committed 7e4ce45.

**Verification note:** the full ci-local's PDF-build step is environmentally flaky (xelatex) and background
wrappers get SIGTERM'd — run it in the foreground (piped to `tail`, or a subshell writing a scratchpad log
outside `/dev/shm`, which ci-local cleans). All per-entry content checks were green throughout.

**Term 2 units (U06–U08) all done.** Next: CP2 Mock Contest 2 (plan 024, assesses greedy/simulation/
prefix-sum). Then Term 3 (U09–U12 + CP3), Term 4 (U13–U14 + capstone + CP4). Carry-forwards unchanged
(CP4 after U14; audit every technique's pre-capstone practice home). Future cleanup: add cell IDs to the
U02/U04/U05 solution notebooks.

## Plan Review

### Round 1 (2026-09-08, HEAD dbdbc0f) — CONSENSUS: [self] APPROVE · [glm]/[fable]/[sol] APPROVE-WITH-NITS
No closure hole and no blocker from any reviewer. All three independently verified against `concept_scan.py`
that the closure boundary is correct — the premature list (recursion/backtracking U09, deque/`.pop` U10,
comprehension U09, bitwise-ops/base-conversion U11, two-pointer U14) and the scanner-BLIND bans (`.remove`
silently set-credited, bare-name builtins unreported, list-repetition reads as arithmetic, chained comparison
collapses to `comparison`) are right and correctly assigned to grep/AST + review (with `.pop` correctly
scanner-caught via the unknown-method path). Two-tier practices, mutation focus (±1 prefix index + 2D
inclusion-exclusion), integer-only outputs, and Phase B verification all PASS. Non-blocking nits folded:
- **[FIXED] (all three) stale "Phase C" label** in Out of scope → Phase B.
- **[FIXED] (glm+fable) difference-array exercise** not covered by the lesson/checklist → removed from A2
  (replaced with a running-total-window prefix-sum problem); A2 now states taught-before-assessed explicitly.
- **[FIXED] (fable) A6 scanner-blind check hardened** — replaced under-inclusive greps with an AST check
  (`ast.Compare len(ops)>1` for chained comparison; `ast.BinOp` Mult with a list operand for list-repetition),
  the same method the plan-022 remediation used.

**Plan-review gate CLOSED — 4-way consensus, zero blockers. Cleared for implementation (Phase A).**

## Content Review

### Round 1 (2026-09-08, HEAD 0f63ac2) — [self] APPROVE · [glm]/[fable] APPROVE-WITH-NITS · [sol] REJECT
All reviewers confirmed the SOLUTIONS correct and the SUITE strong: blind-solved 9/9 (fable 3,600 differential
trials 0 mismatch); the ±1 prefix-index and 2D inclusion-exclusion mutants all killed (fable 38/38
non-equivalent, sol 39/39, glm 31/31 — the only survivors were provably-equivalent `pre=[0]→[1]` seed
mutants, a constant offset that cancels in every `pre[r+1]-pre[l]`); AST closure clean (0 chained
comparisons, 0 list-repetitions, no premature/banned surface); per-technique TAUGHT checklist ✓; all cells
have IDs. Every finding was documentation/metadata/statement-level (none touched solution correctness or
closure) — all fixed:
- **[FIXED] Ex9 (glm+fable+sol) — undefined no-qualifying-window result.** Inputs may have no window with
  total ≤ B (reference returns 0, pinned by its assert but unstated). Added to the statement: "If no
  non-empty window has a total at most `B`, return `0`."
- **[FIXED] Ex9 teacher-notes Big-O (fable+sol) — said O(n)** but the reference (and the statement) enumerate
  all O(n²) windows; an O(n) solve would need the U14 two-pointer (premature). Corrected to "O(n²) after an
  O(n) prefix build".
- **[FIXED] Ex9 name (glm+fable+sol)** — teacher-notes said "Longest Affordable Streak"; the exercise is
  "Longest Low-Total Streak". Aligned everywhere.
- **[FIXED] Ex4 teacher-notes extension (fable) — factually wrong** (max over ALL ranges ≠ max over the
  *reported* ranges). Reworded to loop-sum-each-reported-range (O(Q·n)) vs the prefix-sum version.
- **[FIXED] `for-loop` unused require (fable+sol)** — no `ast.For` anywhere (all loops are `while`). Trimmed
  from `requires` in both manifest and map.
No solution logic changed. All 11 book2 checks re-PASS.

### Round 2 (2026-09-08, HEAD 7e4ce45) — CONSENSUS: [self] · [fable] · [glm] APPROVE, [sol] APPROVE WITH NITS
All five round-1 doc/metadata findings confirmed resolved by all reviewers; the solutions notebook is
**byte-identical** to the round-1-approved version (git blob + SHA-256 match; diff touches only the Ex9
markdown cell, teacher-notes, manifest, and map), so the ±1 and 2D inclusion-exclusion asserts still kill
all 39 mutants (re-confirmed). exec-solutions (real kernel) / concept-scan / manifest-check / prereq-check
PASS; AST closure re-scan clean (0 chained comparisons, 0 list-repetitions, 0 for-loops). sol's lone "nit"
is only the sandbox Jupyter-socket block (handled via its input-free fallback, 9/9). **Content-review gate
CLOSED — zero open blockers, cleared for PR.**
