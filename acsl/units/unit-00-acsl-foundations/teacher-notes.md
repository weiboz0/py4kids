# Teacher Notes — Unit 00: ACSL Foundations

## Goals

This unit gets a student who has finished a Python fundamentals book ready for ACSL's programming problems and its exact-answer style.
By the end, students should be able to:

- describe the ACSL season (four contests, each with its own categories), the divisions, and the difference between short-answer and programming questions;
- read a contest problem statement: task, input format, output format, sample, limits;
- run a `.py` solver from a terminal, typing the input or feeding a fixture file with `<`;
- read contest input with `input()` and `split()`, convert tokens with `int()`, and read a fixed count of values or read until a `0` sentinel;
- store pairs and triples as tuples, unpack them, and loop over a list of tuples;
- solve small problems by complete search: try every candidate or every pair (`range(i + 1, n)`), count the ones that work, and keep the best;
- trace a short program by hand and write its exact output, the core skill behind every "What Does This Program Do?" question.

The unit opens with **Pairs That Make the Target**: count the pairs of cards that add to a target, and print the first such pair.
Lesson 3's `assets/l3.py` solves it, so students see the whole path from reading the input to the searched answer.

Every exercise carries a division tag on its heading: Junior, Intermediate or Senior.
Short-answer items (tagged `short-answer`) ask for one exact output; the solutions show a worked trace and a machine-checked answer.

## Pacing

Budget: three lessons of 60–90 minutes.

- **Lesson 1 — How ACSL works (about 60 minutes).**
  - Walk through the season map in the syllabus.
  - Point out this year's contest windows. Contest 1 opens in October, so this unit fits September and early October.
  - Explain the divisions and the division tags.
  - Hand-trace one short program together before anyone types.
  - Run `assets/l1.py` twice: once typing the input, once with `< assets/l1/1.in`. Expect to walk the room for the terminal step.
- **Lesson 2 — Reading contest input.**
  - Most errors this term come from input handling, so give this lesson its full time.
  - Do the `"40" + "2"` trap live: `42` versus `402`.
  - Finish with the until-0 reader `assets/l2.py`.
- **Lesson 3 — Tuples and complete search.**
  - Start with tuples and unpacking, then "try every candidate" (`3x + 5y = 31`), then every pair with `range(i + 1, n)`.
  - Close by solving the opening hook with `assets/l3.py`, including its `NONE` edge case.
- **Exercises.** Exercises 1–7 and 10 are the Junior core. Exercises 8, 9 and 11–13 add Intermediate items. Exercises 14–15 are Challenges (Intermediate and Senior). Programming items are good homework; short-answer items work well as five-minute warm-ups in later lessons.

**60-minute cut:** keep Lesson 1's terminal run and Lesson 2's fixed-count and sentinel readers. Move the tuple swap and the edge-test discussion in Lesson 3 to homework reading.

## Common mistakes

- Adding strings instead of numbers: `input()` returns text, so `"40" + "2"` is `402`. Convert every number token with `int()` before doing arithmetic.
- Reading the wrong number of lines. When the first line says how many values follow, students often read one line too many or too few. Have them trace the reader against the sample input line by line.
- Printing extra words or spaces ("The answer is 42", a trailing space, a blank line). ACSL compares output exactly; print only what the output format asks for.
- Counting each pair twice in a pair search: `range(n)` inside `range(n)` counts `(i, j)` and `(j, i)`, and even `(i, i)`. The inner loop starts at `i + 1`.
- Forgetting the "no answer" case, such as `NONE` in the hook. Always check what to print when nothing matches.
- Trying to change a tuple (`point[0] = 5`). Tuples cannot be changed; build a new one instead.
- Writing a short answer that is almost right: `3 2 7` versus `3, 2, 7`. The expected answer is the exact printed text.

## Discussion prompts

- Why does ACSL require the exact output text instead of accepting "anything that means the same"?
- A friend's solution passes the sample but fails the hidden tests. What kinds of input should you try on your own program before you submit?
- When is "try every possibility" fast enough, and when would it be too slow? Think about 10 values, then 1,000, then 1,000,000.
- Why might a problem store a point as a tuple `(x, y)` instead of two separate lists?
- How is tracing a program by hand like being the computer? What do you need to write down to avoid mistakes?

## Differentiation

**Division paths through the book:**

- **Junior** students do every `acsl-junior` item here, then follow the Contest 1–4 parts in season order.
- **Intermediate** and **Senior** students also do the items tagged at their level. Before Contest 1, they should also work the Contest 1 "What Does This Program Do?" section that traces loops, arrays and strings, because their Contest 1 covers all constructs.
- **Elementary** students skip this unit (the Elementary contest has no programming) and start at Contest 1's Computer Number Systems unit.
- **Classroom** students need only the short-answer skills: Lesson 1's tracing, and the short-answer items at Junior and Intermediate level.

**Support:**
- Pair students for the terminal steps in Lesson 1.
- Give a printed "reader template" (read N, then N values) for Lesson 2.
- For complete search, have students first list every candidate on paper for a tiny case (three or four values) before writing the loops.

**Extension:**
- The Challenges (14 Making Change, 15 Triangle Sticks) stretch complete search to more than two nested choices.
- Ask fast finishers to write a second fixture that would catch a wrong solution to an exercise they solved. This is the habit ACSL programming rewards.
