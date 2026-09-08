# Plan 024 — Book 2 CP2 "Mock Contest 2"

**Goal:** Ship `checkpoint-02-mock-contest-2` — the second timed mock contest, assessing Term-2
(U06 Greedy, U07 Simulation, U08 Prefix Sums, on the U01–U05 foundation) — on the `solve(data:str)->str`
contract, following the shipped CP1 checkpoint pattern.

**Architecture:** A checkpoint entry (`checkpoint.ipynb` + `solutions.ipynb` + `teacher-notes.md` +
`manifest.yaml`). `checkpoint.ipynb` opens with contest framing (time budget + rules), then 6 timed
`## Question N` problems that collectively exercise the Term-2 techniques — two greedy (sort-then-sweep),
two simulation (step-by-step state / grid), two prefix-sum (1D range query + 2D sub-rectangle) — each with
an EMPTY student code cell. `solutions.ipynb` mirrors the `## Question N` headings with pure `solve(data)`
references and non-vacuous asserts. Introduces nothing; requires the U06–U08 techniques it assesses (plus
the earlier introduces its solutions genuinely use); practices the Book-1 concepts its solutions use.

**Tech Stack:** Jupyter notebooks (nbformat), `tools/` checks, `scripts/ci-local.sh`,
`py4kids-tools --book book2`; Python 3 stdlib only.

**Spec:** `docs/designs/001-book2-algorithms.md` (§7 CP2). NOTE: the design's contest-realism prose is
stale — §1 says "2–3 problems", but the shipped tooling (`checkpoint_question_findings`) requires 6–8, and
CP1 shipped 6; the ~35–45 min budget derives from `lessons: 0.5` + the CP1 precedent, not a design §8 time
budget (§8 is annual pacing). `book2/syllabus.md`;
`book2/curriculum/coverage-map.yaml` (`checkpoint-02-mock-contest-2` entry); the shipped
`book2/checkpoints/checkpoint-01-mock-contest-1/` (the exact checkpoint pattern) and plan 021 (CP1 — all
its gate lessons transfer); plans 022/023 (U06–U08) and their content-gate lessons.

## Global Constraints

Copied from the design + registry + the CP1/U06–U08 gate lessons; every task's requirements include this.

- **Contract:** every reference solution is a pure `solve(data: str) -> str`; ZERO `input()` in any
  executable cell. The `import sys; print(solve(sys.stdin.read()))` wrapper is shown ONLY as a **markdown
  fenced block** in `checkpoint.ipynb` or in teacher-notes — **NEVER as a code cell** (checkpoint code cells
  are ruff-linted with NO `no-exec` exemption — that exemption is `kind=="unit"` only — so a wrapper code
  cell's undefined `solve` fails cell-lint with F821), and NEVER in solutions.ipynb (which both cell-lints
  AND executes — a wrapper there fails twice). Deterministic. Every cell has an `id`.
- **Checkpoint structure (structure-check):** required files exactly `manifest.yaml`, `checkpoint.ipynb`,
  `solutions.ipynb`, `teacher-notes.md`. Problem headings are `## Question N` (NOT `## Exercise`) — **6–8,
  numbered sequentially 1..N** (this plan uses exactly 6). Student code cells are EMPTY (`''`). Checkpoints
  have NO stretch tier (a stretch tag is a FAIL). teacher-notes has exactly SIX headings — the five unit
  headings `## Goals`/`## Pacing`/`## Common mistakes`/`## Discussion prompts`/`## Differentiation` PLUS
  `## Grading` (points per question + total, and the time budget).
- **Closure (same scanner + reviewer rules as U06–U08):** only Book-1 + U01–U08 concepts. set-ops ONLY via
  `.add`/`.discard` on a `{…}`/`set()` var in-cell, or `-`; **NOT `.remove`** (scanner silently credits it,
  U04 taught only `.add`/`.discard`); NEVER `&|^`; NEVER `.union`/`.intersection`/`.difference`.
  `sorted(seq, key=named_fn)` (NO lambda). greedy/simulation/prefix-sum/binary-search/complete-search all
  allowed (≤U08). **NO not-yet-taught concept: no recursion/backtracking (U09), no `deque`/`.pop` (U10), no
  comprehension/genexps (U09), no bitwise-ops/base-conversion (U11), no `tree-traversal` (U12), no
  graph traversal / `bfs`/`dfs`/`flood-fill`/`graph-repr` (U13 — the most realistic slip for a grid-
  simulation question quietly becoming connected-components/flood-fill), no converging two-pointer (U14).** **NO
  scanner-blind untaught surface: no list-repetition `[x]*n` (build with while/append), no chained
  comparison `a<=b<c` (use `b>=a and b<c`).** NO untaught methods (.join/.splitlines/.index/.count/.find/
  .pop). Allowed builtins ONLY `{len,min,max,sorted,sum,abs,round}` — NO `all`/`any`/`enumerate`/`zip`/
  `reversed`/`map`/`filter`. **Enforcement:** concept-scan + ad-hoc `detect()` for premature FEATURES +
  untaught methods; an **AST check** (`ast.Compare` len(ops)>1; `ast.BinOp` Mult with a list operand) plus
  grep for `.remove`/banned-builtins for the scanner-blind slips. concept-scan `--book book2` clean.
- **Two-tier metadata (a checkpoint ASSESSES its concepts):** `introduces: []`. `requires:` = EVERY U01–U08
  introduced concept the solutions USE (`greedy`/`simulation`/`prefix-sum` plus, if genuinely used,
  `input-parse`/`str-split`/`sorted-key`/`tuple`/`set-*`/`grid-2d`/`binary-search`/`complete-search`/
  `complexity`/`boolean-algebra`) — trim any not used. `practices:` = `(used) − requires − introduces −
  wrapper-artifacts (file-read, import-statement)` = ONLY the Book-1 concepts the solutions use; NO U01–U08
  introduce appears in `practices`. `requires ∩ practices = ∅`; manifest == coverage-map exactly;
  `lessons: 0.5`.
- **Non-vacuous asserts (the U06–U08 mutation categories):** every reference solution carries the sample
  assert PLUS crafted edge cases killing the technique's signature mutants — greedy: wrong sort key /
  no-sort / decisive-last-after-sort / tie boundary; simulation: off-by-one on the last step / boundary /
  wrong-order-of-update / termination; prefix-sum: the ±1 prefix index / 2D inclusion-exclusion sign-or-term
  / single & full range / decisive-last-cell. Decisive values placed last (and last-after-sort).
- **Assessment integrity:** every problem solvable with ONLY U01–U08 material (prereq closure); the six
  collectively cover the term (2 greedy, 2 simulation, 2 prefix-sum); contest-appropriate difficulty for a
  timed sitting (no stretch tier). **Every output is an INTEGER or plain string — never a float.**

## Out of scope

- No new unit/technique/feature (introduces empty); no tooling change.
- **Verification is NOT out of scope:** Phase B is the named verification phase (blind-solve + mutation +
  full ci-local + 4-way content gate).

---

## Phases

### Phase A — checkpoint.ipynb + solutions.ipynb + teacher-notes + manifest

**Files:**
- Create: `book2/checkpoints/checkpoint-02-mock-contest-2/{checkpoint,solutions}.ipynb`,
  `teacher-notes.md`, `manifest.yaml`
- Modify: `book2/curriculum/coverage-map.yaml` (fill the CP2 entry's `requires` to the assessed set +
  `practices` to Book-1 used — both mirror the manifest since manifest==map)

**Interfaces:**
- Consumes: U01–U08 introduced concepts + Book-1.
- Produces: nothing (assessment leaf).

- [ ] **A1 — checkpoint.ipynb.** Opening markdown: contest title, the ~35–45 min time budget (matching
  `lessons: 0.5`), rules (each `solve(data)` reads the whole input string; the submission wrapper is shown
  as a markdown fenced block, NOT a code cell), and a points-table pointer. Then EXACTLY 6 `## Question N`
  (sequential 1..6), each: title (### …), one-paragraph statement, `### Constraints`, `### Sample Input`,
  `### Sample Output` (```text fences), then an EMPTY code cell. **Fixed six-question allocation (exactly
  2 greedy / 2 simulation / 2 prefix-sum — pinned, no alternatives):**
  - **Q1 greedy** — interval scheduling / max non-overlapping (sort by end, then sweep).
  - **Q2 simulation** — grid robot / bounded walk following a command string (clamp/stop at walls).
  - **Q3 prefix-sum (1D)** — answer many range-sum (or range-count) queries via a cumulative array.
  - **Q4 greedy** — a different-key greedy: fewest-coins (canonical denominations) or max-items-under-budget
    (sort by cost, take cheapest).
  - **Q5 simulation** — tick-by-tick state update (a bounded counter/resource, or an event sequence
    processed by index-walk — no `.pop`/`deque`).
  - **Q6 prefix-sum (2D)** — sum/aggregate a sub-rectangle of a grid via the four-term inclusion-exclusion
    formula.
  Integer/plain-string outputs; decisive values last / last-after-sort.
- [ ] **A2 — solutions.ipynb (FRESH author, blind).** Mirror `## Question N`; pure `solve(data)`;
  scanner-clean forms (greedy via `sorted(key=named_fn)`+sweep; simulation via bounded loops, no `.pop`/
  recursion; prefix-sum via while/append build + the ±1 / 2D inclusion-exclusion formula; NO list-repetition,
  NO chained comparison, NO `.remove`, NO converging two-pointer). Non-vacuous asserts per the mutation
  categories above. Every cell has an `id`.
- [ ] **A3 — teacher-notes.md.** The SIX headings incl `## Grading` (points per question + total, ~35–45 min
  budget); `## Pacing` frames the single timed 0.5-lesson sitting; a per-question Big-O line; which Term-2
  technique each question assesses. May carry the submission-wrapper snippet (allowed in `.md`).
- [ ] **A4 — manifest.yaml + map.** `introduces: []`; `lessons: 0.5`; `requires:` = the genuinely-assessed
  U01–U08 introduces (greedy/simulation/prefix-sum + those actually used); `practices:` = `used − requires −
  introduces − wrapper-artifacts` (Book-1 concepts only, incl. `dict-access` via `.get`/`[]` if used);
  `requires ∩ practices = ∅`; manifest == map. Derive from an ad-hoc `detect()` over both notebooks;
  hand-add scanner-invisible used concepts.

### Phase B — Verification (named verification phase)

- [ ] **B1 — blind-solve + mutation self-check** on both notebooks (greedy/simulation/prefix-sum mutation
  categories — every mutant fails an assert; every pristine solver passes; cap binary-search/while mutants).
  Confirm each assessed U06–U08 technique is genuinely exercised; run the AST closure check (no chained
  comparison / list-repetition) + grep (`.remove`/banned builtins). Fix any vacuous assert.
- [ ] **B2 — full `scripts/ci-local.sh` ALL GREEN both books** (foreground / subshell-to-scratchpad-log —
  ci-local cleans `/dev/shm`).
- [ ] **B3 — commit Phase A+B** on `feature/plan-024-book2-cp2`.
- [ ] **B4 — 4-way content-review gate** ([self]/[sol]/[glm]/[fable], read-only, HEAD-pinned): blind-solve
  all 6; mutation sweep (categories above); closure (AST check for chained-comparison/list-repetition; no
  `.remove`/premature technique/untaught builtin); `## Question N` 6–8 sequential, empty student cells,
  wrapper markdown-only (cell-lint clean); teacher-notes six headings incl `## Grading`; manifest==map,
  `requires` = assessed set (each genuinely used), `practices` Book-1-only; each problem prereq-closed to
  U01–U08; the six collectively cover Term-2 (≥2 each greedy/simulation/prefix-sum). Resolve every `[OPEN]`;
  re-verify in round-2 before consensus.
- [ ] **B5 — commit content-gate fixes, write the post-execution report**, re-run full `ci-local.sh` ALL
  GREEN — all precede the PR.
- [ ] **B6 — PR** → `pre-merge-guard.sh --pr` OK → squash-merge → delete branch → update memory.

## Post-Execution Report

_(filled at Phase B)_

## Plan Review

### Round 1 (2026-09-08, HEAD a12e71a) — [self] APPROVE · [glm]/[fable] APPROVE-WITH-NITS · [sol] REJECT
All three external reviewers verified the checkpoint STRUCTURE correct against `tools/notebooks.py` (files,
`## Question N` 6–8 sequential, six teacher-note headings incl `## Grading`, no stretch, the wrapper-code-
cell F821 rule) and the closure/metadata carried correctly from CP1 + U06–U08. One blocker + convergent
nits folded (no architecture change):
- **[FIXED] BLOCKER (sol; glm+fable as nit) — the six questions were not concretely pinned.** A1 used
  generic shapes with Q5/Q6 "OR"-alternatives + a "mixed problem", which could diverge from the declared
  2-greedy/2-simulation/2-prefix-sum split. Replaced with a **fixed pinned allocation**: Q1 greedy (interval
  scheduling), Q2 simulation (grid walk), Q3 prefix-sum 1D (range queries), Q4 greedy (coins/budget), Q5
  simulation (tick state), Q6 prefix-sum 2D (sub-rectangle inclusion-exclusion) — no alternatives.
- **[FIXED] nit (fable) — B4/closure ban omitted U13.** Added `tree-traversal` (U12) and `bfs`/`dfs`/
  `flood-fill`/`graph-repr` (U13) to the premature bans — the realistic slip for a grid-simulation question
  becoming flood-fill/connected-components.
- **[FIXED] nit (fable) — wrapper wording.** Added explicit "NEVER in solutions.ipynb" (it both cell-lints
  and executes there).
- **[FIXED] nit (sol) — stale §8 citation.** Corrected the Spec: the ~35–45 min budget derives from
  `lessons: 0.5` + CP1, not a design §8 time budget; noted design §1's "2–3 problems" prose is stale vs the
  tooling's 6–8.
No reviewer found a wrong structure claim or closure hole. Round-2 (sol, focused) dispatched at the revised
HEAD to confirm the pin; glm + fable round-1 approvals stand (the edits only tightened what they approved).

### Round 2 — [self] APPROVE; [sol] focused re-check dispatched, pending
Consensus recorded here once sol confirms the pin (glm/fable round-1 APPROVE-WITH-NITS stand); no `[OPEN]`
blocker remains before implementation.

## Content Review

_(4-way content-review gate — findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`, all resolve before merge)_
