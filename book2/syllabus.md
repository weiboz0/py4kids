# Book 2 — Year 2 Syllabus

Algorithms & data structures for contest preparation: **USACO Bronze (mastery) → easy Silver
(exposure)**, with the overlapping **ACSL** topics folded in. Problem-first: every unit opens with a
motivating contest problem, teaches the technique, then drills a rich, laddered problem set. Python
continues from Book 1; **OOP and software engineering are deferred to a later book**.
Full design: `docs/designs/001-book2-algorithms.md`.

~35 workload lessons of 60–90 minutes across the year (see the pacing contract below). Prerequisites
import from Book 1 (all of Book 1 precedes Book 2; concept ids are a flat shared namespace — Book-1
ids are available as prerequisites without qualification, see `docs/plans/017-book2-infrastructure.md`
AD-001).

## The `solve(data)` judge contract (binding)

Every reference solution is a pure function **`solve(data: str) -> str`**: it takes the entire
problem input as one string and returns the exact output string. Verification is inline asserts,
token-compared (`assert solve(SAMPLE_IN).split() == SAMPLE_OUT.split()`), against the sample **plus
crafted edge/larger cases** (a wrong solution must fail — non-vacuous, as in Book 1). No `input()` in
executable solution cells; the real-submission wrapper (`import sys; print(solve(sys.stdin.read()))`)
is shown but never CI-run. Problems are deterministic (no `random`/seeding). Each problem's intended
Big-O is stated in teacher notes; "fast enough" is taught, not CI-enforced.

## Arc at a glance

| entry | kind | lessons | focus |
|-------|------|---------|-------|
| `unit-01-reading-the-input` | unit | 2 | input parsing, `.split`, grids, the `solve()` contract |
| `unit-02-boolean-logic` | unit | 2 | boolean algebra, truth tables, code-tracing warm-ups |
| `unit-03-complexity` | unit | 1 | counting operations, O(n)/O(n²)/O(log n), fast enough? |
| `unit-04-sets-tuples-sorting` | unit | 2 | sets, tuples, `sorted(key=…)` |
| `unit-05-searching-complete-search` | unit | 3 | linear/binary search, nested-loop complete search |
| `checkpoint-01-mock-contest-1` | checkpoint | 0.5 | Mock Contest 1 (Term 1) |
| `unit-06-greedy` | unit | 2 | greedy: sort-then-sweep |
| `unit-07-simulation` | unit | 2 | simulation & ad hoc |
| `unit-08-prefix-sums` | unit | 2 | 1D → 2D prefix sums |
| `checkpoint-02-mock-contest-2` | checkpoint | 0.5 | Mock Contest 2 (Term 2) |
| `unit-09-recursion-backtracking` | unit | 3 | recursion, backtracking |
| `unit-10-stacks-queues-deques` | unit | 2 | stacks/queues/`deque`, postfix eval |
| `unit-11-number-systems-bitwise` | unit | 3 | bases, bitwise, GCD, sieve, modular arithmetic |
| `unit-12-binary-trees` | unit | 2 | binary trees, BST, traversals |
| `checkpoint-03-mock-contest-3` | checkpoint | 0.5 | Mock Contest 3 (Term 3) |
| `unit-13-grids-graphs` | unit | 3 | grids, graphs, flood fill, BFS/DFS |
| `unit-14-two-pointers` | unit | 2 | two pointers / sliding window |
| `project-03-mock-contest` | project | 3 | Grand Mock Contest (Year-2 capstone) |

## Term shape

- **Term 1 — Foundations, logic & search:** units 01–05, checkpoint 01.
- **Term 2 — Greedy, simulation & sums:** units 06–08, checkpoint 02.
- **Term 3 — Recursion, structures & number sense:** units 09–12, checkpoint 03.
- **Term 4 — Graphs & Silver taste:** units 13–14, the capstone mock contest.

## Assessment format

Checkpoints are **timed mini mock-contests** (2–3 problems, a stated time limit, teacher-run clock),
verified via the `solve` contract; they assess only already-taught techniques and introduce nothing.
The capstone is a **full mock contest** spanning the year (the finale). Problem sets are generous and
difficulty-laddered (target ~8–15 problems/unit, hardest `stretch`-tagged) — proficiency through
volume, mostly solved as self-paced homework.

## Pacing contract (scope vs. time)

Book 2 is fuller than Book 1 (~35 workload lessons). Honest budget management:
- Several units are one lesson of teaching + a large self-paced problem set (problem sets are
  homework, not class time).
- Boolean-algebra and code-tracing partly ride as recurring warm-ups, not full class blocks.
- **Term 4 (units 13–14) is the explicit compressible buffer:** if the year runs short, they shrink
  to exposure and the capstone still stands. Bronze mastery (Terms 1–3) is the non-negotiable core;
  the Silver taste is the stretch.

## Rules this syllabus is bound by

- Nothing is used before it is taught, counting all of Book 1 as the baseline (cross-book closure).
- Project-first: every unit opens with its motivating problem, never concept drill.
- Checkpoints assess only concepts already taught; they introduce nothing.
- No student-defined classes anywhere (OOP deferred): trees use arrays/dicts, graphs use
  adjacency-list dicts.
- The two-tier concept model: language features are machine-checked by `concept-scan`; algorithmic
  techniques are reviewer-enforced for closure.
