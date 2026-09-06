# Teacher Notes — Unit 02: Number Detective

## Goals

Students leave able to work with integers and arithmetic, convert typed input with `int()`, import and use `random.randint`, compare values, branch with `if`/`elif`/`else`, and loop with `while` — combined into a guessing game they built.
Success looks like: every student's game loops until the correct guess, and students can explain WHY the loop stops.

## Pacing

Budget: three lessons of 60–90 minutes.
Ten concepts land here — the year's joint-heaviest unit — so each lesson carries a fixed allocation and the exercise set stays short.

- **Lesson 1 — int-type, arithmetic, type-conversion, import-statement, random-module (60–90 min).**
  Open on the project thread: the teacher's computer picks a secret number; the class tries to find it by shouting — chaos motivates a smarter way.
  20 min: integers and arithmetic (including `//` and `%` as party tricks).
  15 min: `input()` gives text — `int()` fixes it (bridge from unit 01).
  25 min: `import random`, `random.randint` — every student's machine picks a secret.
  Rest: dice-roller exercise.
- **Lesson 2 — boolean, comparison, if-statement, elif-else (60–90 min).**
  Open on the thread: the machine has a secret; today it learns to answer one guess.
  20 min: comparisons and True/False.
  30 min: the one-guess detective — `if`/`elif`/`else` gives "too high / too low / got it!".
  Rest: higher-or-lower exercises.
- **Lesson 3 — while-loop (60–90 min).**
  Open on the thread: one guess isn't a game; loop until correct.
  25 min: `while guess != secret` — the full game.
  20 min: deliberate-bug debugging session (practices error-messages): the forgotten-`int()` bug lives in the exercises; the `=`-for-`==` bug is TEACHER-IMPROVISED — type `while guess = secret:` live, let the SyntaxError land, and read it together (it is not in the notebooks by design).
  Rest: play; hand-tally guess counts for the paper leaderboard.

DELIBERATE OMISSION: there is NO guess counter in this unit — `loop-counter` is introduced in unit 03 (coverage-map contract).
Students tally their guesses on paper and the class keeps a hand-written leaderboard; tell them the machine learns to count next unit.

Practices reappearance: string-literal/naming/comment are exercised throughout the game's messages and code style; run-program and error-messages get the lesson-3 debugging session; all five reappear in checkpoint 01.

## Common mistakes

- Comparing text to numbers: forgetting `int()` around `input()` (TypeError — a planned traceback-reading moment).
- `=` where `==` was meant (SyntaxError inside `if`/`while` — read it together).
- `elif` chains ordered so "too high" swallows "got it".
- Infinite loops from asking for input OUTSIDE the loop body — teach "the loop must be able to change its answer".
- `random.randint(1, 10)` bounds confusion (both ends inclusive).

## Discussion prompts

- Why does the game need `while` and not just many `if`s?
- What's the smartest first guess for 1–100, and why? (Seeds the halving idea without teaching algorithms.)
- Is the computer "thinking" when it picks a random number?

## Differentiation

- Strugglers: provide the lesson-2 detective as a fill-in-the-branches skeleton; pair for lesson 3.
- Fast finishers: Challenge exercises — "hot/cold" distance hints (arithmetic + comparison only) and computer-guesses-your-number (halving narrative, no counters).
- The 1–1000 range remix is a good middle-tier extension before the Challenges.
