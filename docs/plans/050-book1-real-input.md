# Plan 050 — Book 1 Real-Input Norm (hybrid stdin form + realistic data)

**Goal:** Make Book-1 examples and exercises stop looking "fake." Two norms, course-wide:
1. **Hybrid stdin form (Option A, user-chosen).** Every complete teaching example (each lesson section's
   "put it together") and every exercise keeps its **executable fixed-data** form (runs live, students
   see output) AND gains ONE consistent **`no-exec` `input()`-reading "real program"** form — the
   finished-program shape that reads its data from input. Uses `input()` (introduced u01), **NOT**
   `sys.stdin` (that is Book 2). `no-exec` because an `input()` cell is interactive (the `INTERACTIVE`
   rule in `tools/notebooks.py` forces it).
2. **Realistic exec data (user-directed).** The culminating "put it together" cells and the exercises use
   realistic, non-trivial datasets — no `n = 3`, no 2-element lists. Handling depends on list availability
   (user chose **(i)**):
   - **u07–u10 (lists taught from u07):** realistic FIXED lists (≈6–8 elements, real variety, ties where
     apt) directly in the exec cells.
   - **u01–u06 (no `list` yet):** a realistic *fixed* dataset would need an ugly N-branch `if/elif` just to
     store N values, which reads MORE fake — so the exec cell keeps a **modest** fixed dataset and the
     **`input()` real-program form carries the realism** (it handles arbitrary input size naturally).
     The tiny one-increment build-up rungs (R1 = one update, R2 = +one) **stay minimal** — realism
     applies to the put-it-together and exercises, never the graduated build-up rungs (that would break
     the plans 031–035 / 049 one-increment pedagogy that cleared its gates).

**Non-goal / explicitly NOT this plan:** Book-2-style `sys.stdin.read()` + subprocess `judge-check` over
`.in`/`.out` (that was the rejected "full stdin-first" option — it would make every teaching cell
`no-exec` and lose executable worked examples). Book 1 stays a notebook course with **executable
worked examples**; the stdin realism is the *added* `no-exec` real-program form + realistic exec data.

**Architecture (per complete task):**
- **Lesson "put it together"** (each L-section and each Algorithm-Extension home): keep the executable
  fixed-data version (with realistic data per the rule above), then add a `no-exec` `input()` real-program
  cell + a `**Notice:**` framing it as "the finished program reads its data with `input()`; display-only,
  run it yourself." The tiny build-up rungs are untouched.
- **Exercises:** the reference **solution reads `input()`** (a real program) on a realistic sample; a
  small **executable fixed-data check cell** demonstrates/verifies the logic runs (since the `input()`
  solution itself is `no-exec`). Student answer cells stay empty. Exercise statements say the program
  reads its input (values, one per line / as prompted) and prints the result.
- **Prereq closure:** `input()`/`int()`/`str()` are u01; every real-program form uses only concepts ≤ its
  unit (no `sys`, no `.split()` unless taught, no list before u07). The `input()` cell is `no-exec`
  (INTERACTIVE), so `exec-lessons`/`exec-solutions` never run it — no hang.
- **No metadata churn:** no `introduces`/`requires` change; a scanner-forced regular-concept `practices`
  add only under the General Rule (expected rare); pattern markers/§3 untouched (this is orthogonal to
  the algorithm-pattern thread — it adds a real-program form + realistic data, no locus change).

**Spec:** new **`docs/designs/003-book1-real-input.md`** (committed in Phase A) — the authority for the two
norms + the per-unit realistic-data recipe + the `no-exec` real-program convention; plus
`tools/notebooks.py` (the `INTERACTIVE`/`no-exec` + exec-lessons/exec-solutions semantics that must stay
green), and the plans 031–035 / 047–049 worked-example + Algorithm-Extension conventions this builds on.

## Global Constraints

- **`input()` idiom only** for reading input (u01-native); NEVER `sys.stdin` / `sys.stdin.read()` in Book 1.
- **Every `input()`-reading cell is `no-exec`-tagged** (INTERACTIVE); executable cells are `input`-free
  fixed data. So `exec-lessons`/`exec-solutions` still run clean.
- **Realistic data** on put-it-together + exercises; **build-up rungs stay minimal**; list-less units use
  Handling (i).
- **Executable worked examples preserved** — the fixed-data ladders (031–035, 049) are NOT converted to
  `no-exec`; the real-program form is ADDED alongside.
- Prereq-closure per unit; no `introduces`/`requires`/marker/§3 change; General-Rule `practices` add only
  if scanner-forced. Branch `feature/plan-050-…`; no commits while a `[sol]` review is in flight;
  `GH_TOKEN=$(cat .gh-token)`; run `ci-local` FOREGROUND (`TMPDIR=/dev/shm bash scripts/ci-local.sh`).
- **Do not touch** Book 2; governance files; the algorithm-pattern markers/loci.

## Out of scope

- Book-2-style subprocess judging / `.in`-`.out` fixtures / `judge-check` for Book 1 (rejected option).
- Converting existing executable teaching cells to `no-exec`.
- New algorithm patterns; checkpoints/projects **content redesign** (they get the same norm applied, but
  no new questions).

## Phases

Dispatch per AGENTS.md. **Pilot one unit fully first** (like the Book-2 migration), prove the norm + CI,
then roll out. Each slice keeps `ci-local` GREEN and `main` valid.

### Phase A — Design 003 + conventions + CI-safety probe (docs, ships first)
1. Write `docs/designs/003-book1-real-input.md`: the two norms; the `input()`-`no-exec` real-program
   convention; the realistic-data recipe (u07–u10 fixed lists; u01–u06 Handling (i)); the per-unit
   closure notes; the acceptance bar (reached unit-by-unit as slices merge).
2. Probe (throwaway, reverted): add a `no-exec` `input()` cell + a realistic fixed-data exec cell to a
   unit and confirm `exec-lessons`/`exec-solutions`/`hygiene`/`cell-lint`/`noexec-check`/`concept-scan`/
   `structure-check` all stay green (the `input()` cell must be stripped by INTERACTIVE→no-exec; the
   realistic exec cell must run). Ship tooling tolerance + fault fixtures only if a check needs it;
   expected: none.
- **Acceptance (A):** design 003 committed; probe green; no tooling change (or it ships fault-tested).

### Phase B — PILOT: u04 quiz-show (full unit)
Apply both norms to u04 end-to-end: each L-section put-it-together and each Algorithm-Extension home
put-it-together gains a `no-exec` `input()` real-program form (+ Notice); the executable put-it-togethers
use realistic-but-modest fixed data (u04 is list-less → Handling (i)); each u04 exercise gets an
`input()`-reading reference solution + a realistic fixed-data check, statement reworded to "reads its
input." Build-up rungs untouched; markers/§3 untouched. 4-way content gate; ci-local GREEN.

### Phases C–… — rollout (one plan per 1–2 units / the checkpoints / the projects)
u01–u03, u05, u06 (list-less, Handling (i)); u07–u10 (realistic fixed lists); the 4 checkpoints; the 2
projects. Each a slice through both gates; sequence to avoid churn. (Enumerated in design 003 §rollout.)

### Phase V — Verification (named, mandatory)
`uv run pytest -q` green; `scripts/ci-local.sh` ALL GREEN (exec-lessons/exec-solutions run the fixed-data
cells; no-exec `input()` cells stripped; hygiene/cell-lint/noexec/concept-scan/structure/PDF + pre-merge
guard). **Pedagogy (reviewer-enforced):** every complete task has an executable fixed-data form AND a
`no-exec` `input()` real-program form; put-it-together + exercise data is realistic (no `n=3`/2-element
lists) where the unit's closure allows; build-up rungs stay one-increment; no `sys.stdin`; Book 2 green.
**Acceptance:** design 003; the norm applied to every in-scope entry (unit-by-unit); ci-local ALL GREEN;
`pre-merge-guard --pr` OK; plan-review + per-PR content-review 4-way consensus.

## Plan Review

_(4-way gate — pending dispatch.)_

## Content Review

_(pending per slice.)_

## Post-Execution Report

_(pending.)_
