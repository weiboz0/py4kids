# Book 1 Algorithm-Pattern Reuse Ledger

Source of record for plan 047 (design 002 v7). Derived from the plan's "Appendix — Reuse ledger",
normalized for tooling (exact registry ids in the enabling-concepts column; `H`/`→` prose prefixes
dropped) — same 28 loci, actions, and counts. The content gate checks marked exercises against it.
**No ≤16 exercise-count ceiling** (design §7 v7): "resulting core" is informative pacing data, not a cap.
New/adapt headings are planned authoring targets (content gate confirms embodiment).

**Baseline core/stretch audited 2026-09-18:** u02 8 core / 2 Challenge · u04 10/2 · u05 11/2 · u06 11/2 ·
u07 13/2 · u08 14/2 · u09 12/2 · u10 12/2. Project-01 has no `stretch` cells (milestones only).
(Per-unit `stretch`-tagged *cell* totals vary — u02 5, u04 5, u05 6, u06 6, u07 5, u08 4, u09 4, u10 4 —
because a Challenge exercise is ≥2 tagged cells; the invariant tracked here is **≥2 Challenge exercises**.)

## Per-locus ledger

| pattern | entry | exercise heading | now | action | enabling concepts | slice |
|---|---|---|---|---|---|---|
| running-total | u04 (home) | *new* "Running total: add the round scores" (`while`-based, no list) | new core | new | accumulator (u04 co-intro), arithmetic (u02) | C |
| running-total | u05 | "Exercise 7" `total_card_borders(n)` | core | reuse | — | C |
| running-total | u07 | "Exercise 4 / Total and Average" | core | reuse | — | C |
| running-total | u09 | *new* "Sum the saved scores" (read-and-sum) | new core | new | accumulator, arithmetic (scanner-derived on u09), file-read (u09) | C |
| count-by-condition | u04 (home) | *new/adapt* "Count the correct answers" (`while`-based, no list) | new core | new | comparison (u02), if-statement (u02) | D |
| count-by-condition | u06 | *new* "Count the vowels" (count-matches) | new core | new | in-operator (u06), comparison | D |
| count-by-condition | u07 | "Exercise 5 / Award a Score Tier" | core | reuse | — | D |
| count-by-condition | u08 | "Exercise 5: Count the Words" (tally-by-key) | core | reuse | — | D |
| find-extreme | u07 (home) | *new* "Champion by name" (best_name+best_score) | new core | new | list-loop (u07), comparison | G |
| find-extreme | u08 | "Exercise 6: Most Common Word" | core | reuse | — | G |
| find-extreme | u09 | *new* "Highest score by scanning" (best-so-far, no `max()`) | new core | new | comparison (scanner-derived on u09) | G |
| find-extreme | u10 | "Exercise 13: Happiest Pet" + `best_pet` | stretch | promote | — | G (+1 u10 Challenge replacement) |
| linear-search | u06 (home) | lesson `for … range(26)` scan + home ex adds `break` | new/adapt core | new/adapt | for-loop (u03), break-statement (u04), in-operator (u06), comparison | F |
| linear-search | u07 | *new* "Find the first over the bar, stop early" | new core | new | break-statement (scanner-derived on u07) | F |
| linear-search | u08 | "Challenge 1: Reverse Lookup" → "Exercise 15" + `break` | stretch | promote | break-statement (scanner-derived on u08) | F (+1 u08 Challenge replacement) |
| linear-search | u09 | *new* "Find a name in the save file" | new core | new | break-statement (scanner-derived on u09) | F |
| transform-each | u06 (home) | *new/adapt* "Do the same to each character" (new string) | new core | new/adapt | for-loop (u03), string-methods (u06) | E |
| transform-each | u07 | "Exercise 6 / Tidy the Champion Names" | core | reuse | — | E |
| transform-each | u08 | "Exercise 10: Translate a List" | core | reuse | — | E |
| transform-each | u09 | "Exercise 3: Load Scores into a List" (line→int) | core | reuse | — | E |
| filter-into-list | u07 (home) | *new* "Keep only the qualifying scores" | new core | new | list-append (u07), comparison | H |
| filter-into-list | u08 | *new* "Keep only the long words" (Exercise 16) | new core | new | list-append, comparison, builtin-functions (`len`, scanner-derived on u08) | H |
| filter-into-list | u09 | *new* "Load only the high scores" | new core | new | list-append, comparison, file-read | H |
| filter-into-list | u10 | *new* "List the happy pets" | new core | new | list-append, comparison | H |
| sentinel-loop | u02 (home) | "Exercise 3" while-until-guessed game | core | reuse-as-home | while-loop (u02), comparison (u02) | B |
| sentinel-loop | project-01 | M1 `while choice != "q"` menu | core | reuse | — | B |
| sentinel-loop | u07 | "Exercise 12: Double the Qualifying Threshold" (`while`, true sentinel) | core | reuse | — | B |
| sentinel-loop | u10 | "Exercise 14: Play Until Happy" (`while happiness<10`) | stretch | promote | — | B (+1 u10 Challenge replacement) |

## Resulting per-unit core count (projected, informative — not a cap)

Challenge column = Challenge-*exercise* count (each ≥2 `stretch`-tagged cells → always ≥ the
`notebooks.py:538` CI floor of ≥2 tagged cells). Replacements added in the promoting slice.

| unit | baseline core | +new core | resulting core | Challenge exercises after |
|---|---|---|---|---|
| u02 | 8 | 0 (sentinel home = reuse Ex3) | 8 | 2 (unchanged) |
| u04 | 10 | +2 (running-total + count homes, `while`-based, no list) +7 (plan-048 unmarked drills, Ex13–19) | 19 | 2 (unchanged) |
| u05 | 11 | 0 (reuse Ex7) +9 (plan-048 unmarked function drills, Ex12–20) | 20 | 2 (unchanged) |
| u06 | 11 | +2 (count-matches new; linear-search & transform-each homes) | 13 | 2 (unchanged) |
| u07 | 13 | +3 (find-extreme home, filter home, loop+break) | 16 | 2 (unchanged) |
| u08 | 14 | +2 (reverse-lookup promote→core Ex15, filter new Ex16) | 16 | 2 − 1 + 1 = 2 |
| u09 | 12 | +4 (read-and-sum, best-so-far, find-in-file, filter — all new) | 16 | 2 (unchanged) |
| u10 | 12 | +3 (Ex13 promote, Ex14 promote, filter new) | 15 | 2 − 2 + 2 = 2 |

**Plan-048 Algorithm Extension (unmarked reps).** Each pattern-hosting unit's algo exercises are
relocated into a closing `## Algorithm Extension` section and joined by extra **unmarked** loop-mastery
drills (no `<!-- pattern: id -->` marker, no new technique `practices` tag, no new §3 locus). The
"resulting core" above grows by each unit's drill count as its slice lands; per-unit caps and datasets
live in `docs/proposals/048-loop-drill-inventory.md`. Landed so far: **u04 +7 (Ex13–19)** — two-counter
tally, conditional sum, signed accumulate, opening streak, and the until-threshold matrix pair
(check-before-add / add-then-check on 4,6,5,7,3 ÷ 12) + a sentinel drill. **u05 +9 (Ex12–20)** — all
function-packaged: count/sum/triangle/average, the matrix pair (sizes 10..30 ÷ 60), a `while` sentinel
(`stamps_to_reach`), and two parameterized drills (scanner-derived `practices` added under the General
Rule: `if-statement`, `elif-else`, `comparison`, `while-loop`, `break-statement` — all introduced ≤ u05).

## Invariants proven

- **Spiral ≥3 core non-checkpoint reappearances** (home excluded): running-total u05/u07/u09;
  count-by-condition u06/u07/u08; find-extreme u08/u09/u10; linear-search u07/u08/u09;
  transform-each u07/u08/u09; filter-into-list u08/u09/u10; sentinel-loop project-01/u07/u10.
- **Stretch:** every touched unit keeps ≥2 Challenge exercises at every merge.
- **Scanner-derived `practices`** (exact registry ids, all closure-clean, under the General Rule):
  `break-statement` (intro u04) → u06/u07/u08/u09; `accumulator` (u04) + `arithmetic` (u02) → u09;
  `comparison` (u02) → u09; `builtin-functions` (u07) → u08.
