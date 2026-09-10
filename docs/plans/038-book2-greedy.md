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
complexity note). No new tooling. The per-entry `assets/` switch flips U06 to the new model; all
other entries stay unchanged.

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
  sort keys only** (`sorted(seq, key=named_fn)` / `list.sort(reverse=True)`), NEVER a lambda
  (reviewer-enforced). No banned scanner-blind construct (the shipped solvers already use `i = i + 1`,
  named keys, no comprehension/ternary/`[x]*n`/`+=` — `source-policy` enforces it mechanically).
- **Lesson solver PIDs:** `l1`–`l4` (`manifest.lessons` stays 2 → `judge-check` derives `l1`,`l2` as
  expected; `l3`,`l4` are reserved-stem solvers, judged + fixture-required + mirrored). Exercise
  solvers `ex1`–`ex9`. Each solver ≥2 non-vacuous fixtures (from the shipped mutation-hardened
  asserts + crafted edges).
- Lesson opens project-first (festival-scheduling hook). Early ladder + counterexample rungs are
  EXECUTABLE on literal data (run under `exec-lessons`); the four full solvers are `no-exec` cells
  mirroring `l1`–`l4.py`. `manifest.lessons` unchanged (2); coverage-map unchanged.

## Phases

### Phase A — assets: 13 stdin `.py` solvers + fixtures

`book2/units/unit-06-greedy/assets/`: transform each shipped `solve()` (4 lesson + 9 exercise) into a
direct stdin `.py` (`import sys; data = sys.stdin.read(); …; print(ans)` — no `solve()` wrapper),
preserving the verified body. Fixtures `assets/<pid>/<k>.in`+`<k>.out` from each solver's asserts
(≥2 each; verify a plausibly-wrong greedy — wrong sort key, `>`-vs-`>=` boundary — fails ≥1 fixture,
per the content-gate non-vacuous bar).

### Phase B — lesson + solutions + docs

- `lesson.ipynb`: the L1/L2 ladders above with executable literal-data rungs + the two executable
  counterexample rungs, one-line `**Notice:**` per rung, the four full solvers as `no-exec` "Put it
  together" cells mirroring `l1`–`l4.py` + run lines, `**Complexity:**` notes; keep the exchange-
  argument prose.
- `solutions.ipynb`: all-`no-exec` display mirroring each `exN.py`, with a one-line `**Notice:**`
  explanation per exercise (the local choice + sort key + the edge its fixtures pin).
- `exercises.ipynb`: rewrite the intro cell off the retired `solve(data)` wording to the stdin/stdout
  form (statements otherwise unchanged).
- `teacher-notes.md`: pacing re-synced to the ladders + the two counterexamples (stays 2 lessons);
  keep the 5 unit headings.

### Phase C — Verification (named verification phase)

`scripts/ci-local.sh` ALL GREEN: `judge-check` (all 13 U06 solvers pass ≥2 fixtures; `l1`,`l2`
expected-present; mirrors match), `source-policy` (U06 clean; named-key-only, no banned construct),
`exec-lessons` (ladder + counterexample rungs run; solver cells `no-exec`), `concept-scan` (U06 union
+ stdin set), coverage/prereq, manifest==map, structure/hygiene/cell-lint/noexec/stretch, Book-1 PDF,
pre-merge-guard. Un-migrated entries stay GREEN on the old path. **Content-review audit:** greedy
solvers correct + fixtures non-vacuous (mutation-kill a wrong sort key / boundary); each ladder rung
one-increment with a Notice; BOTH counterexample rungs present and correct (start-key < end-key; coin
`[1,3,4]`/`6` greedy=3 vs optimal=2); project-first; `## Pacing` == 2 lessons.

## Out of scope

- Any other unit/checkpoint/capstone (later rollout). Tooling (settled in plan 036). Governance files.
- **Verification-phase note:** ships a reworked unit WITH a named verification phase (Phase C).

## Post-Execution Report

_(filled at Phase C)_

## Plan Review

_(4-way plan-review gate — consensus before implementation)_

## Content Review

_(4-way content-review gate — consensus before PR)_
