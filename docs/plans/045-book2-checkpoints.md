# Plan 045 — Migrate Book-2 Checkpoints CP1–CP4 to stdin-first

**Goal:** Migrate all four Book-2 checkpoints (CP1–CP4, 26 questions total) from the
`solve(data:str)->str` inline-assert contract to the **stdin-first, subprocess-judged** model,
matching the 14 already-migrated units.

**Architecture:** Each question's reference solution becomes a real `.py` in the checkpoint's
`assets/` reading `sys.stdin` and printing stdout, judged by `tools/judge.py` against committed
`assets/<pid>/<k>.in` / `<k>.out` fixtures (≥2 per solver, non-vacuous). `solutions.ipynb` becomes
all-`no-exec` cells **byte-identical** to each `.py`. `checkpoint.ipynb` intro + question statements
are rewritten off `solve(data)` to the stdin/stdout contract (student code cells stay empty). Shipped
solver **logic is preserved** — only the I/O contract transforms (top-level `return X` → `print(X)`,
AST-scoped so nested helpers are untouched; multi-return solvers hand-written flat).

**Tech Stack:** Python 3.12, `uv`, `tools/judge.py` (`judge-check`), `tools/source_policy.py`
(`source-policy`), `tools/concept_scan.py`, `scripts/ci-local.sh`. Implementation uses **temporary,
uncommitted** scratchpad builders `build_cp.py` (same machinery as the unit migrations' `build_uNN.py`)
— they live outside the repo tree and are never committed; only the generated content ships.

**Spec:** `docs/designs/001-book2-algorithms.md` §3/§4 (stdin-first judge contract) + the checkpoint
conventions in `tools/notebooks.py` (PID `qN` from `## Question N`; 6–8 sequential questions; NO
stretch tier; teacher-notes six headings incl `## Grading`; submission wrapper markdown-only —
cell-lint's no-exec exemption is `kind=='unit'` ONLY, so a wrapper code cell reds F821).

## Global Constraints

- **PID convention:** `qN` per `## Question N`. CP1/CP2 have 6 questions; CP3/CP4 have 7.
- **Closure (preserved from each shipped solver, no new constructs):** pinned builtins only
  `{len,min,max,sorted,sum,abs,round,input,print,range,int,str,set}`; NO comprehension / ternary /
  `+=` / chained-compare / `[x]*n` / lambda / class / `nonlocal` / `global` / `del` /
  banned methods `{pop,join,index,count,find}`. `deque` FIFO/stack uses `append`/`appendleft`/
  `popleft`/`[0]` (never bare `.pop`). Grid bounds non-chained (`0 <= r and r < rows`). Recursion is
  preserved EXACTLY as shipped — no `nonlocal`/`global` is introduced; where a shipped nested helper
  (CP3 Q1's `count_arrangements`, CP4 Q1's `fill`) already closes over a captured list/set, that is
  left verbatim (this is an I/O-only migration, NOT a rewrite to argument-passing). These are the SAME
  rules as the units each checkpoint assesses; the migration is an I/O transform, never a logic change.
- **No stretch tier** in any `checkpoint.ipynb` (a stretch tag is a checkpoint FAIL).
- **Submission wrapper markdown-only** (fenced block in the intro or teacher-notes), never a code cell.
- **Fixtures:** ≥2 per solver, non-vacuous; every `.out` recomputed by running the pristine stdin
  solver on the `.in` (exact, one line per printed line); drop any empty-stdout fixture (judge FAILs
  empty stdout); dedupe inputs.
- **Manifests unchanged** (map-equal; checkpoints introduce nothing; every assessed Book-2 technique
  is still exercised by its question's solver, so no `practices`/`requires` entry is removed). NOTE:
  the `return-value` practice is technically retired at the OUTER `solve()` level by the migration,
  but each checkpoint still uses `return-value` inside a shipped nested helper (except possibly CP4,
  where it becomes list-but-unused — allowed, `concept-scan` never flags listed-but-unused). Manifests
  therefore stay byte-identical. `is_stdin_model_entry` waives `exec-solutions`/solution-policy per
  entry once `assets/` with `.py` exists.

## File Structure (per checkpoint CPn)

- Create: `book2/checkpoints/checkpoint-0n-.../assets/qK.py` (K = 1..6/7) + `assets/qK/<j>.in`/`.out`.
- Modify: `book2/checkpoints/checkpoint-0n-.../solutions.ipynb` — each `def solve`+asserts cell → a
  `no-exec` cell byte-identical to `qK.py`; per-question `**Notice:**` describing that solver.
- Modify: `book2/checkpoints/checkpoint-0n-.../checkpoint.ipynb` — intro rewritten off `solve(data)`
  to the stdin/stdout contract (markdown wrapper); question statements swept `return`→`print`
  (whole-word, case-insensitive), repairing any legitimate function-return / named-key prose.
- Modify: `book2/checkpoints/checkpoint-0n-.../teacher-notes.md` — reword every `solve`/`return`
  token (whole-word case-insensitive zero, `## Grading` retained); keep the six headings.

## Multi-return / nested-helper inventory (hand-write flat vs AST-scoped)

- **Multi-return (hand-write flat — guard chain → `if/else`; loop-return → found-flag):**
  CP1 Q2 (`is_open` → `if/else` print), CP3 Q3, CP4 Q2, CP4 Q3 (also nested), CP4 Q4.
- **Nested helper (AST-scoped `to_stdin` converts only solve's OWN top-level return; the helper's
  returns are left intact):** CP1 Q4 (`rank_key`, sort-key), CP2 Q1 (`end_time`, sort-key), CP3 Q1
  (`count_arrangements`, recursive), CP3 Q5 (`gcd`, recursive), CP3 Q7 (`walk`, recursive), CP4 Q1
  (`fill`, recursive), CP4 Q3 (`walk`, recursive). _(Corrected per the plan-review gate — CP2/CP3's
  helper is in Q1, not Q2; CP1 Q4 / CP2 Q1 are sort-keys, not recursive. A1 routes both mechanical
  and nested through the same AST-scoped conversion, so the classification only steers reviewer
  attention — it never changes the transform.)_
- **Mechanical (single top-level return):** all remaining questions.

## Tasks / Phases

### Phase A — Build (per checkpoint via `scratchpad/build_cpN.py`)

- [ ] A1: For each checkpoint, read the ORIGINAL `solve()`+asserts from the current committed
  `solutions.ipynb`; `to_stdin` each mechanical/nested solver (import-aware; AST-scoped return
  conversion); hand-write the 5 multi-return solvers flat (I/O-preserving).
- [ ] A2: Extract fixtures from the asserts (handle both `solve(IN)==OUT` and `.split()==.split()`
  forms); recompute every `.out` by running the pristine `.py` on the actual `.in` **file** (never
  from the assert literal — CP4's assert inputs lack a trailing newline, so materialize the `.in`,
  then compute the `.out` from it); dedupe; drop empty-stdout; ensure ≥2 non-vacuous per solver.
  **Named vacuous-fixture hotspots (add a crafted witness, verified sole-killer in B2):**
  - **CP4 Q7** (graph reachability) — shipped asserts survive an undirected mutant (`adj[v].append(u)`);
    add a directedness witness, e.g. `3 1 1\n2 1` → `1` (mutant → `1 2`).
  - **CP4 Q2** (BFS) — shipped asserts survive a no-op `visited.add`; add a visited-discipline witness
    (a cycle with an unreachable target, or a grid where the unmarked BFS diverges), and a FIFO witness.
  - **CP3 Q4** (subset-sum) — 4 of 5 asserts output `"1"`; add a decisive `"0"`/different-value case.
  - **CP4 Q3 / Q4** (YES/NO outputs) — cover BOTH YES and NO with a distinguishing case each.
- [ ] A3: Write `assets/qK.py` + fixtures; rebuild `solutions.ipynb` = no-exec byte-identical mirrors
  (`mirror(pysrc)=pysrc.splitlines(keepends=True)`) + per-question `**Notice:**` derived from the
  ACTUAL solver algorithm.
- [ ] A4: Rewrite `checkpoint.ipynb` intro off `solve(data)` (stdin/stdout contract, markdown
  wrapper); sweep question statements `return`→`print`; repair legitimate return/named-key prose.
- [ ] A5: Sweep `teacher-notes.md` (`solve`/`return` tokens; keep `## Grading` + the six headings;
  re-sync any grading/Big-O prose to the stdin shape).

### Phase B — Verification (REQUIRED)

- [ ] B1: Subprocess-run every `qK.py` against every fixture; confirm stdout matches `.out` exactly.
- [ ] B2: Mutation-test each non-vacuous witness (confirm it kills the intended mutant, e.g. a
  boundary flip, wrong aggregate, FIFO→LIFO, no-sort) — each new witness must be the sole killer.
- [ ] B3: Confirm all no-exec mirrors byte-identical to their `.py`; every question sample I/O in
  `checkpoint.ipynb` re-run through its solver matches.
- [ ] B4: AST closure audit over all `assets/*.py` (no banned construct; pinned builtins only).
- [ ] B5: Contract sweep — zero whole-word `return`/`returns`/`returned`/bare `solve` in
  `checkpoint.ipynb` statements or `teacher-notes.md` (except a sanctioned intro wrapper mention);
  no stretch tag; no `def solve`/wrapper code cell anywhere; **all 26 student answer cells remain
  empty** (source is `[]`).
- [ ] B6: **Metadata byte-preservation** — scoped `git diff` shows the four `manifest.yaml` and
  `book2/curriculum/coverage-map.yaml` are UNCHANGED (the "manifests unchanged" rule proven by diff,
  not just by map-equal CI).
- [ ] B7: `bash scripts/ci-local.sh` → ALL GREEN, exit 0 (`judge-check`, `source-policy`,
  `cell-lint`, `noexec`, `concept-scan`, `prereq`, `coverage`, `manifest`, `structure`, `hygiene`,
  `stretch`, `exec-solutions` waived per stdin entry, pre-merge-guard). Each checkpoint flips ATOMICALLY
  — `judge-check` fails any expected `qN` lacking a solver once `assets/` exists, so all of a
  checkpoint's questions land in the same commit.

### Phase C — Post-execution report + gates

- [ ] C1: Write the post-execution report in this plan file.
- [ ] C2: 4-way content-review gate (per `docs/content-review-gate.md`) — all four reviewers
  blind-solve all 26 questions; findings organized per-checkpoint (CP1…CP4) so `[OPEN]` items stay
  tractable; resolve all `[OPEN]`.
- [ ] C3: PR → `pre-merge-guard --pr` → squash-merge.

## Out of scope

- No tooling changes (`tools/`, `scripts/`) — the stdin infra + judge already ship on main.
- No manifest/concept-map changes; no new questions; no logic changes to any solver.
- The project-03 capstone is a SEPARATE follow-up plan (next batch after this one).

## Plan Review

### Round 1 (HEAD db3ed32) — 4-way consensus: all four APPROVE / APPROVE WITH NITS ✅

- **[self] APPROVE** — phasing sound; named Phase B verification; multi-return set (CP1 Q2, CP3 Q3,
  CP4 Q2/Q3/Q4) matches the AST scan; checkpoint conventions (`## Question N` 6–8, no stretch,
  markdown-only wrapper, `## Grading`, manifests unchanged) correct; scope (4 CPs, 26 Qs, no ladders)
  appropriate for one plan.
- **[sol] APPROVE WITH NITS** — no blockers. Nits: nested-helper inventory factually wrong (below);
  add an explicit "all 26 student cells remain empty" check; verify manifest/coverage-map byte
  preservation via scoped `git diff`; clarify `build_cp.py` is a temporary uncommitted helper.
- **[glm] APPROVE WITH NITS** — no blockers. Nits: same nested-helper correction; name the vacuous
  witnesses (CP4 Q7 directedness `3 1 1\n2 1`→`1`; CP4 Q2 visited-discipline); soften the
  mutable-state constraint (CP3 Q1 closes over `used`); note `return-value` retired with the outer
  `solve()`; state the content gate blind-solves all 26; note atomic per-checkpoint flip.
- **[fable] APPROVE WITH NITS** — no blockers. Multi-return set verified EXACT. Nits: same
  nested-helper correction (CP2 Q1/CP3 Q1, soften "recursive"); flag CP3 Q4 / CP4 Q3–Q4 as
  vacuous-fixture hotspots; footnote CP4's no-trailing-newline assert inputs (materialize `.in`,
  compute `.out` from the file).

**Fixes applied (HEAD → next commit), all non-blocking nits:** nested-helper inventory corrected to
CP1 Q4 / CP2 Q1 / CP3 Q1,Q5,Q7 / CP4 Q1,Q3 (+ "sort-key" vs "recursive" labels); named vacuous-fixture
hotspots + witnesses added to A2/B2 (CP4 Q7, CP4 Q2, CP3 Q4, CP4 Q3/Q4); mutable-state constraint
softened to "preserved verbatim, no `nonlocal` introduced"; B5 adds empty-student-cell check; B6 adds
manifest/coverage-map byte-diff; B7 notes atomic flip; `build_cp.py` marked temporary/uncommitted;
`return-value` retirement + blind-solve-all-26 noted.

**Gate CLOSED — 4-way consensus, no blockers.** Cleared for Phase A implementation.

## Content Review

_(pending)_

## Post-Execution Report

_(pending)_
