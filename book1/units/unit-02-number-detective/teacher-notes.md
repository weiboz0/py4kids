# Teacher Notes — Unit 02: Number Detective

## Goals

Students leave able to work with integers and arithmetic (including `//` and `%`), follow `*`-before-`+` precedence, convert between text and numbers with `int()` and `str()`, import and use `random.randint`, store and print a Boolean value, compare values, branch with `if`/`elif`/`else`, and loop with `while` — combined into a guessing game they built.
Success looks like: every student's game loops until the correct guess, and students can explain WHY the loop stops.

## Pacing

Budget: four lessons of 60–90 minutes. Ten concepts land here — the year's joint-heaviest unit — so each is taught as a short **worked-example ladder** (minimal → one twist → realistic, with a *Notice* line per rung). The beginner-hard ideas (arithmetic, comparison, `if`/`elif`/`else`, `while`) carry an extra rung so no step is a leap. The lesson-count is advisory: take as many rungs per sitting as time allows.

- **Lesson 1 — int-type, arithmetic, type-conversion (60–90 min).**
  Open on the project thread: the teacher's computer picks a secret number; the class tries to find it by shouting — chaos motivates a smarter way.
  15 min: the integer ladder (a whole number → negatives/zero → number vs look-alike text).
  25 min: the arithmetic ladder (`+` → `-`/`*` → on saved numbers → `//` and `%`).
  20 min: the type-conversion ladder (`int("27")` → `str()` → `int(input(...))`, the bridge from unit 01).
  Rest: begin the required Exercise 7 range-width report; finish it at the start of Lesson 2 if needed.
- **Lesson 2 — import-statement, random-module, boolean, comparison (60–90 min).**
  Open on the thread: the machine needs its own secret, and a way to judge a guess.
  20 min: the random ladder (`randint(1,6)` → change the range → save the pick as the secret).
  25 min: the comparison ladder (one `==` → `<` both ways → all four operators → compare saved numbers), with True/False as the boolean answer.
  Rest: complete the required Exercise 8 truth check so students store and print a Boolean before branching on it.
- **Lesson 3 — if-statement, elif-else (60–90 min).**
  Open on the thread: the machine has a secret; today it answers one guess.
  20 min: the `if` ladder (one true branch → a false test does nothing → `if`/`else`).
  25 min: the `elif` ladder (three-way verdict → first-True-wins → the one-guess detective with a real input).
  Rest: higher-or-lower exercises.
- **Lesson 4 — while-loop + debugging (60–90 min).**
  Open on the thread: one guess isn't a game; loop until correct.
  30 min: the `while` ladder (loop until a typed sentinel → loop until the guess matches → add an `if` hint inside → the full random game). Every rung is teacher-run (it waits for typing) and counter-free by design.
  20 min: deliberate-bug debugging session (practices error-messages): the forgotten-`int()` bug is in the lesson's broken/fixed pair; the `=`-for-`==` bug is TEACHER-IMPROVISED — type `while guess = secret:` live, let the SyntaxError land, and read it together.
  Rest: play; hand-tally guess counts for the paper leaderboard.
  60-MINUTE CUT (any lesson): teach rungs 1–2 of each ladder live and leave the last rung as a "try it"; the *Notice* lines let students self-serve it.

DELIBERATE OMISSION: there is NO guess counter in this unit — `loop-counter` is introduced in unit 03 (coverage-map contract).
Students tally their guesses on paper and the class keeps a hand-written leaderboard; tell them the machine learns to count next unit.

Practices reappearance: string-literal/naming/comment are exercised throughout the game's messages and code style; run-program and error-messages get the lesson-4 debugging session; all five reappear in checkpoint 01.

## Common mistakes

- Comparing text to numbers: forgetting `int()` around `input()` (TypeError — a planned traceback-reading moment).
- Expecting `//` to keep a decimal, or using `/` when the midpoint must be a whole number.
- Testing even or odd without comparing the `% 2` remainder to zero.
- Reading `low + high * 2` from left to right instead of doing multiplication first.
- Joining text to an integer without `str()`.
- `=` where `==` was meant (SyntaxError inside `if`/`while` — read it together).
- Putting the words `True` or `False` in quotes instead of storing the Boolean result of a comparison.
- `elif` chains ordered so "too high" swallows "got it".
- Infinite loops from asking for input OUTSIDE the loop body — teach "the loop must be able to change its answer".
- `random.randint(1, 10)` bounds confusion (both ends inclusive).

## Discussion prompts

- Why does the game need `while` and not just many `if`s?
- What extra evidence does the printed Boolean give you before the word verdict appears?
- How would parentheses change the value of `low + high * 2`?
- What's the smartest first guess for 1–100, and why? (Seeds the halving idea without teaching algorithms.)
- Is the computer "thinking" when it picks a random number?

## Differentiation

- Strugglers: provide the lesson-3 one-guess detective as a fill-in-the-branches skeleton; pair for the lesson-4 full game.
- Fast finishers: Challenge exercises — "hot/cold" distance hints (arithmetic + comparison only) and computer-guesses-your-number (halving narrative, no counters).
- The 1–1000 range remix is a good middle-tier extension before the Challenges.
