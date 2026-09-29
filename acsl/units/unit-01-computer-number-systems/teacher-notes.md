# Teacher Notes — Unit 01: Computer Number Systems

## Goals

Students learn ACSL's first Contest 1 category.
By the end they can:

- read place value in bases 2, 8, 10 and 16, and convert any base to decimal by expanded notation;
- convert decimal to any base by repeated division, and between 2, 8 and 16 by grouping 3 or 4 binary digits;
- add, subtract, and multiply by a single digit in another base, carrying or borrowing the base, not 10;
- compare values written in different bases, and read hex RGB colours such as `#7FBF3F`;
- count the 1s in a binary number;
- convert with hand-written Python loops, and only then use the `int(text, base)` shortcut;
- *(Intermediate and above)* convert fractions in bases 2, 8 and 16 (0.101₂ = 5/8), by hand.

The hook, "Three Friends, One Number?", shows three cards (101101₂, 55₈, 2D₁₆) that turn out to be the same number, 45, plus a colour puzzle. Lesson 1 resolves both.

## Pacing

Budget: three lessons of 60–90 minutes, before the Contest 1 window opens (Oct 19, 2026).

- **Lesson 1, the Elementary section.** It contains no code for students to run, so an Elementary-only group can do this lesson alone.
  - Keep place value and expanded notation slow and visual (a place-value chart on the board).
  - Do the grouping shortcut both ways, then add/subtract with carries in base 2 and base 16.
  - Close with RGB colours; students like mixing a colour from hex digits.
  - Exercises 1–9 are the Elementary mock test (30 minutes).
- **Lesson 2, Junior and above.**
  - Repeated division (write the remainders bottom-up).
  - Larger conversions, a "mystery base" example, and multiplying by one digit.
  - Then the conversion as a Python loop with a `DIGITS` string, including the edge case 0.
- **Lesson 3, Junior and above.**
  - `to_decimal` / `to_base` as functions, then the `int(text, base)` shortcut.
  - End with the Intermediate fractions section: the places after the point are ½, ¼, ⅛, … in base 2.
- **Exercises:** 1–9 Elementary; 10–16 Junior (short answers plus two programs); 17–21 Intermediate/Senior, with 20–21 as Challenges.

**60-minute cut:** keep expanded notation, grouping and repeated division; move RGB colours and single-digit multiplication to homework.

## Common mistakes

- Confusing digit value with place value: the 3 in 37₈ is worth 24, not 3.
- Reading the remainders top-down after repeated division; they must be read from the last remainder to the first.
- Grouping from the left instead of from the right, which gives a wrong leading group.
- Carrying 10 instead of the base when adding in base 8 or 16.
- Writing hex digits 10–15 as "10"–"15" instead of A–F, or in lowercase in an answer.
- Treating a fraction in base 2 like a decimal fraction (0.1₂ is one half, not one tenth).

## Discussion prompts

- Why do computers use base 2, and why do programmers like base 16 for writing it?
- Why does grouping 3 binary digits give an octal digit, but 4 give a hex digit?
- Is there a base where the number 10 means ten? What does "10" mean in every base?
- Can every decimal fraction be written exactly in base 2? Try 0.1.

## Differentiation

- **Elementary:** Lesson 1 and Exercises 1–9 are the whole Contest 1 path; skip Lessons 2–3.
- **Junior:** all lessons except the fractions section; Exercises 1–16.
- **Intermediate and Senior:** everything, including fractions and the mystery-base Challenge.
- **Classroom:** the short-answer items at Junior and Intermediate level (no programming).
- **Support:** a printed chart of powers of 2, 8 and 16, and a hex digit table. Check each conversion by converting back.
- **Extension:** convert between two unusual bases (e.g. base 5 to base 7) without going through decimal, then explain why the route through decimal is usually easier.
