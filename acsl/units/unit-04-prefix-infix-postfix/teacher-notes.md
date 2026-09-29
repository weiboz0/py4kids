# Teacher Notes — Unit 04: Prefix/Infix/Postfix Notation

## Goals

Students learn ACSL's first Contest 2 category.
By the end they can:

- read infix, prefix (Polish) and postfix (Reverse Polish) expressions, with the operators `+ - * /` and `↑` (the Elementary paper writes `^`);
- evaluate postfix left to right and prefix by scanning, then with a stack by hand;
- convert infix to prefix or postfix by fully bracketing, never reordering operands and keeping equal precedence left to right;
- convert directly between prefix and postfix;
- write a Python postfix evaluator using a list stack with a tracked `top` (no `.pop`).

The hook, "The Calculator With No Brackets", shows a calculator that computes `6 8 4 2 - / +` = 10 with no brackets, plus a left-to-right argument (`8 - 3 - 2`).

## Pacing

Budget: three lessons of 60–90 minutes, early in the Contest 2 window (Jan 4 – Feb 28, 2027).

- **Lesson 1, the Elementary section.** It contains no code for students to run.
  - Elementary limits: single digits, division only by 1 or 2, powers only 1 or 2.
  - Do all five Elementary skills on the board: evaluate postfix, evaluate prefix, infix→prefix, infix→postfix, prefix↔postfix.
  - Exercises 1–9 are the Elementary mock test: 6 questions in 30 minutes from this set.
- **Lesson 2, Junior and above.**
  - Letters and multi-digit operands, and `↑` in the precedence order.
  - The square-bracket method for converting directly between prefix and postfix.
  - Stack evaluation by hand, with a table.
- **Lesson 3, Junior and above.**
  - The Python evaluator and the canonical way to print results (whole numbers as integers, otherwise a terminating decimal).
  - Prefix evaluation reading right to left.
  - The Intermediate section on long expressions and non-whole answers. Expression trees are an optional aside, not assessed.
- **Exercises:** 1–9 Elementary; 10–17 Junior (including two stack-calculator programs); 18–21 Intermediate; 22–23 Senior Challenges.

**60-minute cut:** keep fully bracketed conversion and stack evaluation; move direct prefix↔postfix conversion to homework.

## Common mistakes

- Reordering operands (`- 5 3` is 2, not −2); the operands keep their left-to-right order in every notation.
- Treating equal precedence right to left: `8 - 3 - 2` is `(8 - 3) - 2`.
- In prefix evaluation with a stack, reading right to left but then taking the two operands in the wrong order. The first operand popped is the **left** operand.
- Writing answers with extra or missing spaces; answers are single-space-separated tokens.
- Printing `69.0` instead of `69` (whole results are written as integers).

## Discussion prompts

- Why don't prefix and postfix need brackets at all?
- Which notation is easiest for a computer, and why do stack-based calculators use postfix?
- How can you check a conversion quickly? Try converting it back.
- Where might you have seen Reverse Polish notation before?

## Differentiation

- **Elementary:** Lesson 1 and Exercises 1–9 are the whole Contest 2 path.
- **Junior:** Lessons 1–3 without the Intermediate section; Exercises 1–17.
- **Intermediate and Senior:** everything, including the Challenges.
- **Classroom:** the short-answer items at Junior and Intermediate level.
- **Support:** a printed precedence ladder (`↑`, then `* /`, then `+ -`, with ties left to right) and a blank stack table.
- **Extension:** students write an infix expression whose prefix and postfix forms look identical in token order except for the operators, then challenge a partner.
