# Teacher notes — Unit 12: Tuning against race time

## Goals

By the end of this unit students can:

- Treat race time as a **black-box objective**: a setting in, a race time (and a clean flag) out, every evaluation costing races.
- Run **coordinate, random and evolution-strategy search** on a race budget, accept a change only when Unit 1's rule says it beats the noise, and reject any setting that is not clean.
- Read a **knob map**: which of the agent's constants move a clean race, which act only after a respawn, and which do nothing at all in the shipped mode.
- Recognise **overfitting**: a search that wins on the tracks it was tuned on and crashes elsewhere, and keep **training, validation and test tracks** apart (a validation track that changes a decision is no longer a test).
- Fix the objective, not the search: add the cars that crash to the objective, and say honestly what the result still costs.
- **Profile** `step()` with `cProfile` and read the result as shares of the time, not as times.
- Avoid the **determinism and rounding traps** (`repr` round-trips, accumulated steps, tick quantisation, timing-on races, dead knobs) and package a tuned agent with its versions written down.

This unit introduces four concepts:
- `black-box-search`;
- `held-out-track-validation`;
- `step-profiling`;
- `determinism-and-packaging`.

`agents/unit-12.py` is `agents/unit-11.py` with one change, `A_DEC` 5.0 → 5.5: the one step a crash-aware coordinate search accepted.
It sits **on the edge** of that search's family: every neighbouring setting except `unit-11.py` itself is not clean, so Unit 11's margin rule would have shipped 5.0.
The unit ships the edge on purpose, to measure what the margin was for.
The book's tests race it: 1.35 s faster than `unit-11.py` on the validation track (`test-circuit-seed2026`), 1.40 s faster on the test track (`test-circuit-seed2028`, 269.65 against 271.05 s, both clean on five seeds), and clean on only 20 of Unit 11's 24 held-out perturbed cars (all 24 finish with 0 collisions; four go just over the 2 m line rule).

## Pacing

Plan for **three 60–90 min sittings**, with Challenges 9–10 as homework.

1. **Sitting 1: the objective and the knobs** (the hook, §1–§2).
   - Hook: count the constants in `unit-11.py` (48), then show the speed search's record: 48.9 s faster over the five training tracks, then not clean on any of five races on `test-circuit-seed2026`.
     Ask before showing the second table: should we ship it?
   - The noise: one track moves 0.05–0.15 s from seed to seed; the five-track sum 0.45–0.80 s.
   - The knob map: six knobs move a clean race by 7–19 s, a few act only by crashing, several do nothing at all.
   - Exercises 1–2.
2. **Sitting 2: searching, and what searching finds** (§3–§4).
   - The live coordinate search (about 90 s of racing, in two cells: start it, then talk through the first evaluations while it runs).
     It stops on its budget at 0.58, not at an optimum; say so.
   - Random search and the evolution strategy from the record: on the same 200 races, 48.9 / 26.0 / 1.6 s.
   - Overfitting: a search on one track, with per-section knobs, gains 14.1 s there and crashes on every other track.
   - Exercises 3–5. The optional policy-gradient part of §3 is for students who want it.
3. **Sitting 3: a better objective, and shipping it** (§5–§7).
   - The crash-aware objective and its ten-row table; the edge and the margin rule (Exercise 6 applies it).
   - Validation on seed2026, then the test track, raced last.
   - Profiling and the traps; the packaging checklist.
   - Exercises 6–8; the milestone (about 70 s of racing plus `check_submission`).

## Common mistakes

- **Accepting a change smaller than the noise.** Two seeds of a five-track sum differ by up to 0.8 s; a 0.3 s "gain" is not one. Use Unit 1's rule on the per-seed sums.
- **Counting a not-clean race at its time.** Random search drew two settings faster than its incumbent that broke the 2 m line rule. Counting them at their time would have accepted them; reject them.
- **Trusting one-lap races for crashes.** One lap ranks settings the same way as three laps, but misses crashes that happen late (`MPC_Q_E = 0.6` is clean on one lap and crashes on three). Confirm a winner at three laps.
- **Using the validation track as the test.** Seed2026 told us the speed search overfits, and we changed the objective because of it. From then on it is a validation track; the honest test is a track nothing has been tuned against, raced once, at the end.
- **Reading "crash-aware" as "safe".** The crash-aware objective is clean on its own 24 training cars and on 20 of 24 held-out cars. It made failures rarer and smaller, not impossible: the same overfitting, one level up.
- **Hand-rounding a tuned constant.** `0.54 + 3 * 0.02` is `0.6000000000000001`; three roundings of one value are three different floats. Same race time, different races. Snap steps to the grid with `round(x, 2)` and write constants with `repr`.
- **Timing a race to compare settings.** With the MPC's time budget on, the same file and seed can give different races. Compare with the timing off; time the file once, with `check_submission`.
- **Reading a profile as a stopwatch.** The shares (the MPC about two thirds of `step()`) are stable; the milliseconds depend on the machine and its load.

## Discussion prompts

- The speed search gained 49 s and lost everything on a new track. What did its family of five tracks not contain?
- Unit 11's margin rule says ship 5.0; this unit ships 5.5. Which would you race on a day when one crash ends your weekend, and which on a day of many practice runs?
- A validation track that changed one decision is spent. How many fresh tracks would you want before race day, and what would you use each for?
- `predict()` takes a fifth of `step()`'s time and nothing reads it. Should a racing agent carry instruments it does not use?

## Differentiation

- **Support:**
  - give the coordinate-search loop and have students write only the acceptance test (Unit 1's rule plus the clean flag);
  - give the ten-row table already sorted and have students find the edge and apply the margin rule.
- **Core:** all non-stretch exercises unaided.
- **Stretch:**
  - Challenge 9, `SPEED_KP`, `SPEED_KI` and `TARGET_SPEED` on a small box, and why those big knobs are fragile;
  - Challenge 10, a policy-gradient tune of one knob against coordinate search on the same race budget;
  - for strong students: design the next objective (which cars, which tracks, how many seeds) and estimate its race cost before running anything.
