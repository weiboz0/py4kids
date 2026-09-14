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
(`source-policy`), `tools/concept_scan.py`, `scripts/ci-local.sh`. Reusable scratchpad builders
`build_cpN.py` (same machinery as `build_uNN.py`).

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
  `popleft`/`[0]` (never bare `.pop`). Recursion passes mutable state as an argument. Grid bounds
  non-chained (`0 <= r and r < rows`). These are the SAME rules as the units each checkpoint assesses;
  the migration is an I/O transform, never a logic change.
- **No stretch tier** in any `checkpoint.ipynb` (a stretch tag is a checkpoint FAIL).
- **Submission wrapper markdown-only** (fenced block in the intro or teacher-notes), never a code cell.
- **Fixtures:** ≥2 per solver, non-vacuous; every `.out` recomputed by running the pristine stdin
  solver on the `.in` (exact, one line per printed line); drop any empty-stdout fixture (judge FAILs
  empty stdout); dedupe inputs.
- **Manifests unchanged** (map-equal; checkpoints introduce nothing; the stdin migration does not
  change assessed concepts). `is_stdin_model_entry` waives `exec-solutions`/solution-policy per entry
  once `assets/` with `.py` exists.

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
- **Nested recursive helper (AST-scoped `to_stdin` converts only solve's OWN top-level return):**
  CP1 Q4, CP2 Q2, CP3 Q2, CP3 Q5, CP3 Q7, CP4 Q1, CP4 Q3.
- **Mechanical (single top-level return):** all remaining questions.

## Tasks / Phases

### Phase A — Build (per checkpoint via `scratchpad/build_cpN.py`)

- [ ] A1: For each checkpoint, read the ORIGINAL `solve()`+asserts from the current committed
  `solutions.ipynb`; `to_stdin` each mechanical/nested solver (import-aware; AST-scoped return
  conversion); hand-write the 5 multi-return solvers flat (I/O-preserving).
- [ ] A2: Extract fixtures from the asserts (handle both `solve(IN)==OUT` and `.split()==.split()`
  forms); recompute every `.out` by running the pristine `.py`; dedupe; drop empty-stdout; ensure
  ≥2 non-vacuous per solver (add a crafted mutation-witness where the asserts are vacuous).
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
  no stretch tag; no `def solve`/wrapper code cell anywhere.
- [ ] B6: `bash scripts/ci-local.sh` → ALL GREEN, exit 0 (`judge-check`, `source-policy`,
  `cell-lint`, `noexec`, `concept-scan`, `prereq`, `coverage`, `manifest`, `structure`, `hygiene`,
  `stretch`, `exec-solutions` waived per stdin entry, pre-merge-guard).

### Phase C — Post-execution report + gates

- [ ] C1: Write the post-execution report in this plan file.
- [ ] C2: 4-way content-review gate (per `docs/content-review-gate.md`); resolve all `[OPEN]`.
- [ ] C3: PR → `pre-merge-guard --pr` → squash-merge.

## Out of scope

- No tooling changes (`tools/`, `scripts/`) — the stdin infra + judge already ship on main.
- No manifest/concept-map changes; no new questions; no logic changes to any solver.
- The project-03 capstone is a SEPARATE follow-up plan (next batch after this one).

## Plan Review

_(4-way gate — pending dispatch.)_

## Content Review

_(pending)_

## Post-Execution Report

_(pending)_
