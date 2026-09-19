# Plan 048 — Loop-Drill Inventory (bounded, authoritative)

Consolidated from the [fable] (~89 proposals + the "until-threshold" matrix supplement) and [sol] (36
proposals) advisory reviews (2026-09-18), deduplicated and **bounded**. This is the authoritative source
the plan-048 unit slices draw from; each slice finalizes its unit's exact list (exact data + expected
outputs) at slice start and records it in the PR.

**Rules for every drill here (from plan 048 Global Constraints):**
- Single-pass, linear. Lives in the unit's `## Algorithm Extension` section (H2, matches `## Challenge`);
  algo exercises are core `## Exercise N` (the highest-numbered), before the unit's Challenge cells.
- **UNMARKED** — these are extra-practice reps, NOT new tagged pattern loci (no `<!-- pattern: id -->`).
  Their Spotlight/prose may still ask "which pattern is this?" but they add no marker and no
  `practices` technique tag. (The 7 patterns already meet their ≥3 spiral from plan 047.)
- Prereq-clean per unit; scanner-derived regular-concept `practices` adds only under the General Rule
  (introduced ≤ unit, not in the unit's `introduces`). Enabling concepts listed per drill.
- No `for`/`range`/list in u04 (deliberate — u04's lesson is `while`-only; `for`/`range` are u03 so they
  are closure-legal but excluded by choice). No `list`/`string-index` in u05 (data from `range`/formulae).
  No `len` before u07 (use a manual counter). Forbid `ord`/`chr` everywhere (unregistered AND undetected
  by concept-scan — u06 letter values come only from the lesson's `range(26)` alphabet-position scan).
  No `.split()`, `sum`/`sorted`/`abs`/`round`/`.count()`/`.index()`/`enumerate`, no `None`/`continue`,
  no tuples/multi-return/comprehensions. `min`/max by scan seed from the first item (never `best = 0`).
  No literal `input(` in any solution cell; `input()`-driven drills are `no-exec`.

## Per-unit caps (bounds total new volume ≈ 50 core drills; "full lightest-units fill")

| Unit | cap | tier | notes |
|---|---|---|---|
| u02 number-detective | 0 new | — | relocation only (stays lean) |
| u04 quiz-show | ≤7 | in-class + hw | `while`-only, fixed/typed values |
| u05 function-factory | ≤9 | in-class + hw | all packaged as functions; lightest unit |
| u06 secret-codes | ≤8 | in-class + hw | character scans; letter values via the alphabet scan |
| u07 high-score-hall | ≤6 | **More-Practice** | already 16 core — watch the >2× cells guardrail |
| u08 word-wizard | ≤5 | **More-Practice** | already 16 core |
| u09 save-point | ≤7 | in-class + hw | file-line loops, no list |
| u10 pet-simulator | ≤9 | in-class + hw | object loops; richest untapped |

## A. The "until-threshold" matrix ([fable] exact datasets) — one loop, running total + a stop-rule

Four cells per placement, all on the SAME dataset so the only visible difference is **check-before-add
(`<=`, "fits")** vs **add-then-check (`>`, "tips", name the tipping item)**:
- **S-fit** total that fits (≤X) · **S-tip** total when it first exceeds X · **C-fit** how many fit ·
  **C-tip** how many until it first exceeds X.

| Unit · items | X | S-fit | C-fit | S-tip (tipping item) | C-tip |
|---|---|---|---|---|---|
| u04 · scores 4,6,5,7,3 (via `if/elif` on `round_number` in a `while`) | 12 | 10 | 2 | 15 (round 3 = 5) | 3 |
| u05 · sizes 10+i*5 → 10,15,20,25,30 (in a function) | 60 | 45 | 3 | 70 (25) | 4 |
| u06 · letter-values of "secret" (from the range(26) scan) 19,5,3,18,5,20 | 30 | 27 (print `message[:count]` → "sec") | 3 | 45 ("r") | 4 |
| u07 · waiting [300,450,275,600] (Ex13's list) | 1000 | 750 | 2 | 1025 (275) | 3 |
| u08 · word lengths of owl,dragon,cat,wizard,sun | 12 | 12 (exact hit → proves `<=`) | 3 | 18 (wizard) | 4 |
| u09 · savegame lines 300,450,725,1350 (no list) | 1000 | 750 | 2 | 1475 (725) | 3 |
| u10 · Buddy hunger 8, snacks 2,4,3,5 (total runs DOWN) | floor 0 | hunger 2 (look-ahead before feed) | 2 | hunger −1 (snack 3) | 3 |

Run each with a huge X so the loop ends naturally ("all fit" / tipping item stays "none") — the edge
that teaches "loop finished" vs "loop broke". **Neighbours** (same skeleton, different done-yet): just-
reaching (`>=` vs `>`), until a sentinel value in the data, until the first item failing a test
(streak/prefix), until the first N that pass, two-condition stop (`and`/`or`). Distribute across u04–u10.

## B. Per-unit drill lists (candidates; slice picks up to the cap)

### u04 quiz-show (≤7; `while`-only, no list)
1. Two-counter count (correct vs wrong via `if/elif/else`) — count. [core]
2. Conditional sum "total only passing rounds" (`if score>=5: total+=score`) — sum. [core]
3. Signed accumulate "points and penalties" (+2 / −1) — sum. [core]
4. Opening streak length (`break` on first wrong) — count-with-early-exit. [core]
5. Matrix S-fit + C-fit (scores 4,6,5,7,3 / X=12). [core]
6. Matrix S-tip + C-tip (same data). [core]
7. True user-sentinel "add scores until 0" (`no-exec`). [hw]

### u05 function-factory (≤9; functions; no list/string-index)
1. `count_bonus_stamps(n)` — count multiples of 3. [core] (adds if-statement, comparison)
2. `total_even_stamps(n)` — conditional sum. [core]
3. `stamps_in_triangle(rows)` — sum the counter (1+2+…). [core]
4. `average_side(n)` — sum then /n. [hw]
5. `stamps_that_fit(limit)` / `width_used(limit)` — matrix fit (count / sum). [core]
6. `stamps_to_pass(limit)` / `width_when_passed(limit)` — matrix tip. [core] (adds break-statement)
7. `stamps_to_reach(target)` — sentinel-in-function (`while`). [core] (adds while-loop)
8. `count_jumbo_stamps(n, threshold)` — parameterized conditional count. [hw]
9. `total_ribbon(n, start, growth)` — parameterized conditional sum. [hw]

### u06 secret-codes (≤8; character scans; letter values via alphabet scan)
1. `count_letter(message, letter)` — count (function). [core]
2. Letters / spaces / marks — three counters (`if/elif/else`). [core]
3. Find first vowel — index search via manual counter + `break`. [core]
4. Boolean "contains a digit?" search. [core]
5. Star the vowels — map-with-branch into a new string. [core]
6. Letter-value sum of a word (values from the range(26) scan) — sum. [core]
7. Matrix fit+tip (letter-values of "secret" / 30; count doubles as slice index). [core]
8. Count digits ≥ 5 in a code (membership + convert + threshold). [hw] (adds type-conversion)

### u07 high-score-hall (≤6; More-Practice tier)
1. Rookie by name — argmin (first scanned MIN in the book). [More-Practice]
2. Best + worst in one pass. [More-Practice]
3. Count-then-average the passers (zero-count guard). [More-Practice]
4. "What place would I be?" — count `> my_score`, rank = count+1. [More-Practice]
5. Position/boolean search over the board (index vs `in`). [More-Practice]
6. Matrix over the waiting list [300,450,275,600]/1000 + the `≥`-vs-`>` boundary drill. [More-Practice]

### u08 word-wizard (≤5; More-Practice tier)
1. Total of the tally (sum dict values) — sum. [More-Practice]
2. Rarest word — argmin over items. [More-Practice]
3. Known vs unknown — two-counter count. [More-Practice]
4. First unknown word — search for a non-member (`break`). [More-Practice]
5. Matrix over word-lengths / 12 (exact-hit boundary). [More-Practice]

### u09 save-point (≤7; file lines, no list)
1. Count boss-level saves (`>=1000`) — count. [core]
2. Count-then-average the save file (no `len`). [core]
3. Lowest saved score by scanning — argmin + init gotcha. [core]
4. Which line holds my score? — line-number search (`loop-counter`). [core]
5. First save ≥ target — threshold search. [hw]
6. Matrix over lines 300,450,725,1350 / 1000. [core]
7. Filter-and-re-save (write passers straight to a file, no list). [hw]

### u10 pet-simulator (≤9; object loops)
1. Count the hungry pets (`hunger>6`) — count. [core]
2. Team hunger total — sum. [core]
3. Find a pet by name (`break`, not-found via `found` flag) — search. [core]
4. Roster of names — map objects→strings. [core]
5. Hungriest / least-hungry pet — max & argmin over objects. [core]
6. Mood tally (`counts[mood]=…` from `status()`) — tally-by-key. [hw]
7. Matrix "feed until budget" (downward total; look-ahead before `feed`). [core]
8. Feed every hungry pet — filter-driven action (no list). [hw]
9. Cheer up the saddest pet — argmin feeds a sentinel loop. [hw]

## Provenance
Every item above appears in the [fable] and/or [sol] advisory reviews (2026-09-18); both verified each
against `coverage-map.yaml` + unit manifests/lessons for prereq closure. The matrix datasets/answers are
[fable]'s. This file is the bounded selection; the full advisory discussion (gap table, closure analysis,
rollout notes) is summarized in plan 048's Appendix.
