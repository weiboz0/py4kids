# Teacher Notes — Unit 15: Assembly Language

## Goals

Students learn the Intermediate and Senior third Contest 4 category: ACSL's assembly language.
By the end they can:

- read a line as `LABEL OPCODE LOC`, knowing the first word is a label only when it is not an opcode;
- trace the accumulator `ACC`, which starts at 0, and memory through `DC`, `LOAD`, `STORE`, `ADD`, `SUB`, `MULT`, `DIV` and `END`;
- use immediate data (`=5`), which only `LOAD`, `ADD`, `SUB`, `MULT` and `DIV` allow;
- apply `DIV` as ACC ÷ LOC, rounding **toward zero** (`-7` ÷ `2` is `-3`), unlike ACSL's `int`, which rounds down;
- follow branches (`BE`, `BG`, `BL`, `BU`), loops built from them, `READ` and `PRINT`;
- say what a program computes in general (the wiki's `N!` sample style);
- translate small programs to Python, and (Senior) write an interpreter with a dict for memory and a table of labels.

The hook is "The Robot With One Pocket": a robot stacking tins in a triangle runs a program that sums 1 to N. With `N DC 4` the answer is 10, and 5050 for N = 100.

## Pacing

Budget: three lessons of 60–90 minutes in the Contest 4 window.

- **Lesson 1.**
  - The shape of a line, the first opcodes and immediate data.
  - `DIV` rounding toward zero, and how big a number can be.
  - A traced program (the wiki's `TEMP` = −9 sample), then the same work in Python.
- **Lesson 2.**
  - Branches and compare-by-subtracting; `READ` and `PRINT`, which create labels.
  - A forward branch, a countdown loop, and the wiki's `N!` sample, including why N = 0 never stops.
  - The same loops in Python.
- **Lesson 3.**
  - What does the program compute? Checking edge cases (a product that works only when B ≥ 1).
  - Senior: an assembly interpreter in Python, then back to the robot.
- **Exercises:** 18 items. Exercises 1–11 are Intermediate (programs 4, 10 and 11); 12–18 are Senior (program 16; 17–18 are Challenges, 17 the full interpreter).

**60-minute cut:** keep the opcodes, `DIV` and one loop; set the interpreter as reading and Exercise 17 as a take-home project.

## Common mistakes

- Treating the first word of `LOAD B` as a label.
- Using floor for `DIV` on a negative result; ACSL keeps the integer part, so it rounds toward zero.
- Forgetting that `ACC` starts at 0, or that `STORE` does not change `ACC`.
- Using immediate data with `STORE` or a branch; only `LOAD`, `ADD`, `SUB`, `MULT` and `DIV` allow it.
- Reading `BG` as "greater than or equal"; it branches only when `ACC` > 0.
- Stopping a trace too early in a loop, or missing the last `PRINT`.

## Discussion prompts

- Why does a computer need an accumulator at all?
- How can you test "is X bigger than Y?" with only `SUB` and a branch?
- The `N!` program never stops for N = 0. How would you fix it?
- How does the Lesson 3 interpreter find where a branch should jump?

## Differentiation

- **Intermediate:** Lessons 1–3 without the Senior interpreter section; Exercises 1–11.
- **Senior:** the whole unit, including Exercises 12–18.
- **Junior:** not part of the Junior path (Junior's Contest 4 has What Does This Program Do? – Strings instead). Keen Juniors can try Lesson 1.
- **Classroom:** Classroom's Contest 4 includes Assembly Language, so do the short-answer items at Intermediate level.
- **Elementary:** not part of the Elementary path.
- **Support:** a printed trace table with columns for the line, `ACC`, and each memory label.
- **Extension:** write an assembly program that prints the digits of a number in reverse, then run it in the Exercise 17 interpreter.

## A note on the 1,000,000 rule

ACSL says `ADD`, `SUB`, `MULT` and `READ` work "modulo 1,000,000" but gives no example for negative results.
The book keeps the sign and the last six digits, and says in the lesson that this is its own convention.
No exercise depends on it: every value stays within ±999,999, and no program divides by zero.
