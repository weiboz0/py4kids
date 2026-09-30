# Teacher Notes — Checkpoint 01: Contest 1 Practice

## Goals

This is a timed ACSL-style practice for Contest 1, taken after units 01–03.
It checks that students can do each Contest 1 category under contest conditions: Computer Number Systems, Recursive Functions, and What Does This Program Do? – Branching.
It introduces nothing new.

- Q1–Q2: base conversion (hex → octal) and multiplying in hex.
- Q3–Q4: evaluating recursive definitions, including a multiple-recursion definition.
- Q5–Q6: tracing a Python program and an ACSL-pseudocode program to one exact output line.
- Q7 (Intermediate and above): an all-constructs trace, covering a 2D array, a stepped loop, ACSL `int` of a negative number (floor), `sqrt`, `abs`, a `while` loop, `%`, and a substring.
- Q8: the programming problem, One Digit, Repeated. The program reads `N` and searches the bases from 2 upward for the first one in which every digit of `N` is the same, then prints that base, the digit and the number of digits.

## Pacing

The ACSL format has a 30-minute, 6-question short-answer test, and the programming problem is submitted separately within the contest window (acsl.org Divisions page).
Run this practice the same way:

- **Short answers: 30 minutes, pencil only.** ACSL's Junior, Intermediate and Senior short-answer tests are each 6 questions in 30 minutes. Q1–Q6 are that paper. Intermediate and Senior students add Q7 as extra all-constructs practice in the same sitting.
- **Programming: one session (about 60 minutes)** for Q8. Students may test with their own inputs before handing in.
- Go over the answers in the next lesson. Spend the most time on the questions the class missed most, and trace them together on the board.

## Common mistakes

- Q1: regrouping hex → binary → octal from the left instead of from the right, or dropping a leading zero inside a group.
- Q2: carrying 10 instead of 16 when multiplying in hex, or writing the answer in decimal.
- Q3–Q4: stopping at the first base case reached instead of finishing the substitution back up the call table; in Q4, forgetting one of the two recursive calls or the `+ 1`, or using the base case for `n = 4` (it is `n < 4`).
- Q5–Q6: taking an `elif` after an earlier branch was already true; misreading `!`, `&&`, `||` in the pseudocode.
- Q7: using Python-style truncation for ACSL `int(-2.5)` (it is −3, not −2); starting the 2D array at the wrong index; reading the ACSL substring `S[3:5]` as a Python slice (ACSL includes position 5).
- Q8: comparing only the first and last digits (21 is 10101 in base 2, whose ends match, but the answer is 111 in base 4); stopping the search at base 16, although 300 first repeats a digit in base 19; mishandling `N = 1` and `N = 2`, which are single digits.

## Discussion prompts

- Which question took the longest? Was it the method or the arithmetic that slowed you down?
- For Q7, which single construct did you find hardest to trace, and how could you check it quickly during a contest?
- In Q8, what test inputs did you try before handing in? Which one would have caught a program that only compares the end digits, or one that stops at base 16?
- How would you split your 30 minutes across six questions next time?

## Differentiation

- **Junior:** Q1–Q6 plus Q8, a full Junior paper (six short answers and one programming problem).
- **Intermediate and Senior:** all eight questions; Q7 is the all-constructs trace their Contest 1 includes.
- **Classroom:** Q1–Q7 as short-answer practice (no programming). The real Classroom test is 10 questions in 50 minutes, drawn from the Junior, Intermediate and Senior categories.
- **Elementary:** this checkpoint is not for Elementary students. Their Contest 1 mock test is Exercises 1–9 of Unit 01 (Computer Number Systems), done in 30 minutes.
- **Support:** allow a printed dialect table (ACSL pseudocode ↔ Python) and a hex digit chart during a first attempt, then retake without them.
- **Extension:** ask fast finishers to write two more Q8 test cases, one that a wrong program would fail.

## Grading

Score it the way ACSL does:

- **Short answers:** 1 point each, all or nothing. The answer must match exactly: uppercase hex digits, no base prefix, no extra text.
  - The six-question paper (Q1–Q6) totals 6 points, as ACSL's does; record Q7 separately as extra practice for Intermediate and Senior.
- **Programming (Q8):** run the student's program on the ten test files in `assets/q8/`. Report the number of files passed; the sample alone does not earn full credit.
  - ACSL scores its programming problem on its own hidden test data, as published each season on acsl.org.
- Keep a record of each category's points so students can see which Contest 1 category to review before the real contest.
