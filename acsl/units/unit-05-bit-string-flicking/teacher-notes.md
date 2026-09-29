# Teacher Notes — Unit 05: Bit-String Flicking

## Goals

Students learn ACSL's second Contest 2 category.
By the end they can:

- apply `NOT`/`~`, `AND`/`&`, `OR`/`|` and `XOR`/`⊕` bit by bit, padding a shorter operand with 0s on the left;
- apply `LSHIFT-x` and `RSHIFT-x` (bits fall off, zeros come in) and `LCIRC-x` and `RCIRC-x` (bits wrap around; a count larger than the length is taken mod the length);
- evaluate whole expressions with ACSL's precedence:
  - `NOT` first, then shift/circulate, then `AND`, then `XOR`, then `OR`
  - equal precedence goes left to right; unary operators apply right to left
- solve for an unknown `x`, giving all solutions in ascending order, a count, or a `*` pattern only when asked;
- write the operations in Python on bit strings with hand loops, and recognise the integer operators `& | ^ << >>` with a width mask.

The hook, "The Stage Light Board", uses eight stage lamps (`10110010`) controlled by NOT, mask, shift and circulate buttons. Lesson 2 solves the first puzzle and Lesson 3 the "what did the board show before?" puzzle.

## Pacing

Budget: three lessons of 60–90 minutes in the Contest 2 window.

- **Lesson 1.**
  - Bit strings and width, and the four bitwise operators with a truth table.
  - Padding unequal lengths.
  - Masks that keep, set or flip bits.
- **Lesson 2.**
  - Shifts and circulates, including the mod rule.
  - The precedence ladder and right-to-left unary operators, with one worked example where working strictly left to right gives a wrong answer.
- **Lesson 3.**
  - Solving for x with the letters method, the canonical answer forms, and brute-force search.
  - The Intermediate section on chains of operations.
  - Integer versions with masks.
- **Exercises:** 1–14 Junior (including two programs); 15–19 Intermediate; 20–21 Senior Challenges.

**60-minute cut:** keep the four operators, shifts and circulates, and one-operation solve-for-x; move chained solve-for-x and the integer operators to homework.

## Common mistakes

- Evaluating strictly left to right and ignoring precedence (`AND` before `XOR` before `OR`).
- Applying unary operators left to right: `NOT RSHIFT-1 x` means `NOT (RSHIFT-1 x)`.
- Padding a short operand on the right instead of the left.
- Shifting in 1s, or letting a shift wrap around like a circulate.
- Forgetting to reduce a circulate count mod the length (`LCIRC-11` on 7 bits is `LCIRC-4`).
- Solve-for-x: listing solutions out of ascending order, missing free bits, or giving a `*` pattern when the question asked for a list or count.

## Discussion prompts

- Why is a circulate reversible but a shift not?
- How can one `AND` or `OR` with a mask switch some lamps on or off while leaving the others alone?
- In solve-for-x, why does an `OR` with 1 create free bits, while `XOR` never does?
- Where do computers use masks and shifts in real life? Think of colours, flags and permissions.

## Differentiation

- **Junior:** all lessons except the Intermediate chains section; Exercises 1–14.
- **Intermediate and Senior:** everything, including chains and the Challenges.
- **Classroom:** the short-answer items at Junior and Intermediate level.
- **Elementary:** not part of the Elementary path (Bit-String Flicking is not an Elementary category).
- **Support:** a printed precedence ladder and a column grid for lining up bits; students check each step bit by bit.
- **Extension:** find the bit string x with `(LCIRC-1 x) XOR x` equal to a given pattern, then explain why some patterns have no solution.
