# Plan 038 — Book 2 stdin-first: U06 Greedy (paradigm pilot)

**Goal:** Migrate U06 Greedy to the stdin-first, subprocess-judged model established in plan 036, and
apply the worked-example-ladder standard — with the paradigm's key **completeness** element: explicit
**counterexample rungs showing when a greedy rule FAILS** (interval scheduling by the wrong sort key;
greedy coin change on a non-canonical coin system). This is the second pilot (the first, U08, is on
main); the remaining 12 units + 4 checkpoints + capstone follow in rollout plans.

**Architecture:** Exactly the plan-036 contract (`docs/plans/036-book2-stdin-infra-u08.md`, design-001
§3): reference solutions are stdin `.py` in `assets/`, judged by `judge-check` against `.in`/`.out`
fixtures; `solutions.ipynb` is a no-exec display mirroring each `.py`; lessons are graduated ladders
(executable literal-data rungs → full stdin solver "Put it together" + edge/counterexample rung +
complexity note). Two small `tools/` HARDENINGS the pilot exposes (Phase A0): a fail-closed
lesson-PID inventory in `judge-check` and an `ast.Lambda` ban in `source-policy`. The per-entry
`assets/` switch flips U06 to the new model; all other entries stay unchanged.

**Tech stack:** `tools/judge.py` / `tools/source_policy.py` (from plan 036), Jupyter notebooks,
`.in`/`.out` fixtures, `scripts/ci-local.sh`.

## The greedy ladder + completeness (this unit's shape)

**Governing principle (user, 2026-09-10): use ENOUGH worked examples to secure genuine mastery of the
concept — there is NO learning-duration constraint.** Rung and example counts follow what mastery of
greedy needs (the sort-key-is-the-algorithm idea, the exchange-argument "why", and the failure modes),
NOT a lesson budget. `manifest.lessons` is an advisory workload figure; if the ladders warrant it, the
lesson count may grow (state any bump in Phase B and keep manifest == coverage-map). The default here
keeps 2 lessons and adds rungs within them, but completeness wins over brevity.

`greedy` is a TECHNIQUE (reviewer-enforced). U06 keeps 2 lessons with FOUR worked solvers:

- **L1 — Interval scheduling** (`l1.py`): ladder — rung 1 sort events by END time on a tiny literal
  list (Notice: the sort key IS the algorithm) → rung 2 sweep with `last_end`, count non-overlapping
  (Notice: take an event when `start >= last_end`) → **Put it together** the full stdin solver
  (`l1.py`) → **COUNTEREXAMPLE rung** (completeness): on a tiny case, greedy by START time attends
  fewer events than greedy by END time (e.g. `[(0,10),(1,2),(3,4)]` → start-key 1 vs end-key 2), so
  the key matters → complexity `O(n log n)`.
- **L2 — Match the choice to the goal**: the **coin-change** ladder (`l2.py`, largest-coin-first with
  `//`/`%`) + its **COUNTEREXAMPLE rung**: greedy-largest fails on coins `[1,3,4]` for `6` (greedy
  `4+1+1` = 3 coins; optimal `3+3` = 2) → keep the exchange-argument reason. Then **pairing** (`l3.py`,
  sort both lists, pair in order) and **cheapest-first** (`l4.py`, sort ascending, take while budget
  holds) as "Put it together" applications with one-line Notices. Both counterexample rungs are
  EXECUTABLE (compute the worse greedy answer on literal data; state the better answer in the Notice).

## Global Constraints (closure — U06 union + banned surface)

- **U06** introduces `greedy` (technique); requires `sorted-key, list-sort, for-loop, accumulator,
  tuple, comparison`; practices the parsing/house set (`str-split, input-parse, arithmetic, boolean,
  builtin-functions, def-function, if-statement, list-append, list-literal, logical-ops, nested-loops,
  parameters, print, range-function, return-value, string-methods, type-conversion, while-loop`).
- **Allowed builtins in scope:** the pinned `source-policy` set (`len/min/max/sorted/sum/abs/round` +
  `input/print/range/int/str/set`) — U06 uses `sorted`, `abs`, `int`, `str`, `range`, `print`. **Named
  sort keys only** (`sorted(seq, key=named_fn)` / `list.sort(reverse=True)`), NEVER a lambda — now
  **mechanically enforced** by the `ast.Lambda` ban added to `source-policy` in Phase A0. No banned
  scanner-blind construct (the shipped solvers already use `i = i + 1`, named keys, no
  comprehension/ternary/`[x]*n`/`+=` — `source-policy` enforces it mechanically).
- **Lesson solver PIDs:** `l1`–`l4` (U06 has 4 worked lesson solvers across 2 lessons). Phase A0 makes
  `judge-check` derive expected lesson PIDs from the **`assets/lN.py` references in `lesson.ipynb`**
  (∪ `l1..l{manifest.lessons}`), so every referenced lesson solver is **mandatory and fail-closed** (a
  referenced-but-missing `l3.py` FAILs judge-check, not just structure-check — resolves Sol's blocker).
  Exercise solvers `ex1`–`ex9`. Each solver ≥2 non-vacuous fixtures (from the shipped mutation-hardened
  asserts + crafted edges).
- Lesson opens project-first (festival-scheduling hook). Early ladder + counterexample rungs are
  EXECUTABLE on literal data (run under `exec-lessons`); the four full solvers are `no-exec` cells
  mirroring `l1`–`l4.py`. `manifest.lessons` unchanged (2); coverage-map unchanged.

## Phases

### Phase A0 — tooling hardening (two small `tools/` additions the pilot exposes)

1. **`tools/judge.py` — lesson-PID inventory fail-closed (Sol blocker).** In `_expected_pids` for a
   **unit**, derive lesson solver PIDs from the `assets/l\d+\.py` references in `lesson.ipynb`
   (via `ASSET_REF`), UNION `l1..l{manifest.lessons}`. Every referenced lesson solver is then expected
   → a missing `lN.py` FAILs judge-check ("missing solver lN.py"). Add a test: a unit whose lesson
   references `assets/l3.py` with no `l3.py` present FAILs.
2. **`tools/source_policy.py` — mechanical `lambda` ban (glm/fable).** Add `ast.Lambda` → banned
   ("lambda (use a named function)") — a lambda sort key is the likeliest closure slip across the
   rollout, and it is currently scanner-blind. Add a mutation fixture; and re-run the
   **full-current-book2 clean regression** (`source_policy_findings(root,"book2")==[]`) to confirm no
   shipped content uses a lambda before wiring (both externals verified book2 is lambda-free).

Both changes are book-scoped already (judge/source-policy return `[]` for book1); update the affected
`tools/` tests. This is a hardening of the plan-036 tooling that the multi-solver-per-lesson U06 pilot
surfaced — not a re-architecture.

### Phase A — assets: 13 stdin `.py` solvers + fixtures

`book2/units/unit-06-greedy/assets/`: transform each shipped `solve()` (4 lesson + 9 exercise) into a
direct stdin `.py` (`import sys; data = sys.stdin.read(); …; print(ans)` — no `solve()` wrapper),
preserving the verified body. Fixtures `assets/<pid>/<k>.in`+`<k>.out` from each solver's asserts
(≥2 each; verify a plausibly-wrong greedy — wrong sort key, `>`-vs-`>=` boundary — fails ≥1 fixture,
per the content-gate non-vacuous bar).

### Phase B — lesson + solutions + docs

- `lesson.ipynb`: the L1/L2 ladders above with executable literal-data rungs + the two executable
  counterexample rungs, one-line `**Notice:**` per rung, the four full solvers as `no-exec` "Put it
  together" cells mirroring `l1`–`l4.py`, **a `python assets/lN.py < …` run line for EACH of l1–l4**
  (load-bearing — the judge lesson-PID inventory + ASSET_REF both key on these), `**Complexity:**`
  notes; keep the exchange-argument prose. **Delete the old `solve()` submit-wrapper cell** (`import
  sys; print(solve(sys.stdin.read()))`) and its intro prose — the retired contract must not survive
  (fable N4). **Mastery rungs (user principle + fable N2):** give `l3` (pairing) an executable
  literal-data rung that DEMONSTRATES the exchange argument — compute the total distance for a
  crossed pairing vs the sorted (uncrossed) pairing on two tiny lists and show sorted ≤ crossed; give
  `l4` (cheapest-first) an executable budget-sweep rung (sort ascending, take while the running spend
  fits) — so the two thinnest patterns get a real graduated build, not just a solver dump. Also name
  the **equal-end-time tie** as an explicit L1 completeness item (glm).
- `solutions.ipynb`: all-`no-exec` display mirroring each `exN.py`, with a one-line `**Notice:**`
  explanation per exercise (the local choice + sort key + the edge its fixtures pin).
- `exercises.ipynb`: rewrite the intro cell off the retired `solve(data)` wording to the stdin/stdout
  form (statements otherwise unchanged).
- `teacher-notes.md`: pacing re-synced to the ladders + the two counterexamples (stays 2 lessons);
  keep the 5 unit headings.

### Phase C — Verification (named verification phase)

`scripts/ci-local.sh` ALL GREEN: new `tools/` tests (judge lesson-PID fail-closed; source-policy
lambda ban) + the full-book2 source-policy clean regression; `judge-check` (all 13 U06 solvers pass
≥2 fixtures — **l1–l4 all expected via the lesson's `assets/lN.py` references, fail-closed**; mirrors
match), `source-policy` (U06 clean; **lambda now mechanically banned**, named-key-only, no banned
construct), `exec-lessons` (ladder + counterexample + l3/l4 mastery rungs run; solver cells `no-exec`),
`concept-scan` (U06 union + stdin set), coverage/prereq, manifest==map,
structure/hygiene/cell-lint/noexec/stretch, Book-1 PDF, pre-merge-guard. Un-migrated entries stay
GREEN on the old path. **Content-review audit:** all four `assets/l{1..4}.py` run lines present + the
old `solve()` wrapper cell gone (fable N1/N4); greedy solvers correct + fixtures non-vacuous
(mutation-kill a wrong sort key / boundary; counterexample rungs are LESSON cells, never solver
fixtures — glm); each ladder rung one-increment with a Notice (incl. the l3 exchange-demo + l4
budget-sweep mastery rungs); BOTH counterexample rungs present and correct (start-key 1 < end-key 2;
coin `[1,3,4]`/`6` greedy=3 vs optimal=2); the equal-end-time tie named; **no lambda** (now also
machine-checked); project-first; `## Pacing` == 2 lessons.

## Out of scope

- Any other unit/checkpoint/capstone (later rollout). Tooling (settled in plan 036). Governance files.
- **Verification-phase note:** ships a reworked unit WITH a named verification phase (Phase C).

## Post-Execution Report

_(filled at Phase C)_

## Plan Review

### Round 1 (HEAD 14a64fc) — [self] APPROVE

- **Closure ✓** — the shipped U06 solvers (which the migration preserves verbatim, only un-wrapping
  `solve()` → stdin) use `sorted(key=named_fn)` / `list.sort(reverse=True)` (NO lambda), `while`/`for`,
  `tuple`, `comparison`, `accumulator` (`x = x + 1`), `abs`/`//`/`%`, `list-append`, `list-literal` —
  all within U06's union + the allowed builtin set; no banned scanner-blind construct (no comprehension
  /ternary/`[x]*n`/`+=`/chained-compare; ex9 builds its `used` bool list with an append-loop, not
  `[x]*n`). `source-policy` will enforce this mechanically.
- **Counterexamples ✓ (verified)** — greedy-by-start on `[(0,10),(1,2),(3,4)]` attends 1 event vs
  greedy-by-end attends 2; greedy coins `[1,3,4]` for `6` gives `4+1+1`=3 vs optimal `3+3`=2. Both are
  correct and are the paradigm's completeness element.
- **Named verification Phase C** present; mastery principle (no duration constraint) recorded.
- **Watch-item (not blocking):** the l3/l4 lesson solvers are covered only by the reserved-stem rule
  (judged + mirrored if present) — `manifest.lessons=2` makes only l1/l2 "expected", so a *missing*
  l3/l4 wouldn't be flagged. I author all four, so they exist; noting the minor fail-open for the
  content gate / a possible future tooling tweak. Fixtures come from the shipped mutation-hardened
  asserts (non-vacuous); each solver ≥2 with a wrong-key/boundary-killing case.

### Round 1 (HEAD 14a64fc) — [glm] AWN · [fable] AWN · [sol] REJECT

All three verified closure (named keys, no lambda in shipped content, no banned construct), both
counterexamples numerically correct (start-key 1 vs end-key 2; coin `[1,3,4]`/6 greedy 3 vs optimal
2), the named Phase C, and the non-vacuous fixture plan. One blocking finding + nits, all `[FIXED]`:

1. `[FIXED]` **[sol blocker] l3/l4 lesson-PID fail-open** — judge derived only `l1`,`l2` from
   `manifest.lessons`, so omitting `l3.py`/`l4.py` would pass. → **Phase A0**: `judge-check` now
   derives expected lesson PIDs from the `assets/lN.py` references in `lesson.ipynb` (∪
   `l1..manifest.lessons`), making every referenced lesson solver mandatory/fail-closed + a test.
2. `[FIXED]` **[glm/fable] lambda not mechanically enforced** — → **Phase A0**: `ast.Lambda` ban added
   to `source-policy` (+ mutation fixture + full-book2 clean regression, both externals confirmed
   book2 is lambda-free); Global Constraints reworded from "reviewer-enforced" to mechanical.
3. `[FIXED]` **[fable N2 mastery]** `l3`/`l4` were solver-only — added an executable exchange-demo rung
   for `l3` (crossed vs sorted pairing) and a budget-sweep rung for `l4` (user's mastery principle).
4. `[FIXED]` **[fable N4]** delete the old `solve()` submit-wrapper cell (retired contract).
5. `[FIXED]` **[glm/fable] Phase B/C wording** — 4 run lines load-bearing; Phase C reworded (l1–l4
   fail-closed via references; counterexamples are lesson cells not fixtures; equal-end-tie completeness
   item; no-lambda machine-checked); content audit adds the run-lines + wrapper-gone checks.

### Round 2 (HEAD a18fdc8) — re-dispatched to [sol]/[glm]/[fable]

_(awaiting round 2; the l3/l4 fail-open is now closed in judge + a lambda ban added — re-review the two
tooling hardenings)_

## Content Review

_(4-way content-review gate — consensus before PR)_
