# Teacher Notes — Unit 08: Randomness

## Goals

Students leave able to import and use the `random` module — `random.randint(a, b)` for a whole number in a
range, `random.choice(range(...))` to pick from a range, and `random.seed(4)` to make a random program
reproducible — and to package randomness inside functions that count outcomes and estimate probabilities.
Success looks like: every student writes a seeded function that simulates many trials and reports a count or
a percentage, and can explain why a simulated estimate is close to, but not exactly, the true value.
Randomness is the payoff unit for functions: every simulation here is a function from Unit 07, called many
times.

## Pacing

Budget: three lessons of 60–90 minutes.

- **Lesson 1 — Chance (`random-module`).** `import random`; `random.randint` (inclusive of both ends) and
  `random.choice(range(...))`; **`random.seed(4)`** so a run can be repeated and tested (why every solution
  here seeds). A dice-and-coin game that keeps a cumulative score across rolls.
- **Lesson 2 — Simulate & Estimate.** Count how often an outcome happens over many trials (a running total
  inside a function), report it as a percentage (`round`), then a Monte-Carlo estimate of π: throw random
  points into a square and count how many land inside the quarter-circle (`x*x + y*y <= 1000*1000`); the
  fraction inside is about π/4, so multiply by 4. **The estimate is close to, not exactly, π** (about 3.1,
  not 3.14159) — more trials bring it closer ON AVERAGE, but not monotonically (a larger run can score
  worse than a smaller one). (Each axis has 1001 possible values; it is not a "1000×1000
  grid.")
- **Lesson 3 — Random Turtle Walk.** A turtle that steps forward and turns left or right based on
  `random.randint(0, 1)`, seeded so the drawing is reproducible; run as `assets/*.py` from the terminal
  (an open path — it does not close).

**60-minute cut (any lesson):** in Lesson 2, teach the counting simulation and the percentage report live and
leave the π estimate as a "try it"; it is the least essential and the most math-heavy.

## Exercises — core vs. extra vs. challenge

Core (1–7): Dice Total, Heads Counter, Bonus-Round Score (cumulative), Target Roll Counter
(count-by-condition), Even-Roll Percentage (`round`), Quarter-Circle Estimate (Monte-Carlo), **Rescue-Robot
Random Walk** (the turtle practice site — run it in the terminal).
Challenges (8–9, `stretch`): Highest Twenty-Sided Roll (`max` over trials); Multiples in a Random Range.
Every non-turtle exercise is a **seeded function** (`random.seed(4)` before the first random call) asserted
against its deterministic result; the turtle walk is checked by running it.

## Common mistakes

- Forgetting to seed (or seeding after the first random call), so results are not reproducible and the tests
  do not match — seed with `random.seed(4)` first.
- Assuming `random.randint(1, 6)` excludes 6 — both ends are included.
- Passing a list to `random.choice` — use a `range(...)` (lists come later).
- Expecting a simulated estimate to equal the exact value, or to improve on EVERY increase in trials; more
  trials help on average (and never make it perfectly exact), but the improvement is not monotonic.
- In the random walk: running from the wrong directory, or expecting the drawing to close (it is an open
  path and carries the `# turtle-check: open-path` marker).

## Discussion prompts

- Why does seeding make a random program testable? What would happen to the tests without a fixed seed?
- In the π estimate, why does multiplying the inside-fraction by 4 approximate π? What is the picture?
- Why does running more trials usually give a better estimate but never a perfect one?
- Which of this unit's simulations needed a running total, and which needed a count-by-condition?

## Differentiation

- Strugglers: Core 1–5 (dice/coin counts and a percentage); give the loop and have them add the random call
  and the tally.
- Fast finishers: the π estimate, then the two Challenges, then extend the random walk with a random step
  length (still seeded).
- Middle tier: change the number of trials in a simulation and predict how the estimate's stability changes,
  then confirm.

## Value plan (sample inputs)

- Exercise 1 — `roll_total(rolls)`: `4`, `7`, `10`.
- Exercise 2 — `count_heads(flips)`: `6`, `14`, `20`.
- Exercise 3 — `bonus_score(rounds)`: `5`, `8`, `12`.
- Exercise 4 — `count_targets(trials, target)`: `(12, 3)`, `(30, 6)`, `(50, 1)`.
- Exercise 5 — `even_percent(trials)`: `10`, `25`, `100`.
- Exercise 6 — `estimate_pi(trials)`: `20`, `200`, `2000`.
- Exercise 7 — random-walk real program (no function call): seed `4`, `step = 31`, `move_count = 20`.
- Exercise 8 — `highest_roll(trials)`: `3`, `10`, `30`.
- Exercise 9 — `count_multiples(trials, n)`: `(10, 4)`, `(25, 5)`, `(40, 3)`.
