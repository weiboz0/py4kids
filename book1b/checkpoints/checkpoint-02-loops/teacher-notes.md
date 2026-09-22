# Teacher Notes — Checkpoint 02: Loops

## Goals

A short mixed assessment proving Units 01–05, with the load on the loop concepts: `while` with a counter,
sentinel "repeat-until", `for`/`range` running totals, counting by condition, and nested loops — over a
recap of decisions (`elif`) and integer math (`//`/`%`). It introduces nothing new and assesses only what
has been taught. Students work solo; it is solution-free like a unit's exercises.

Loops ARE allowed now (unlike Checkpoint 01), but the checkpoint stays otherwise strict: **no lists, no
functions, and no built-ins beyond `print`/`int`/`float`/`str`** — sums/counts use the accumulator idiom
(`total = total + n`), never `sum(...)`.

## Pacing

Budget: half a lesson (~30–45 minutes). Hand out after Unit 05. The seven questions and their targets:
1. **Ordered Battery Ladder** — an `if`/`elif`/`else` ladder, only correct top-down (U03 recap).
2. **Cartons and Leftovers** — `//` and `%` on given values (U02 recap).
3. **While-Counter Pass Bar** — a `while` loop with a counter/accumulator (U04). *Pass-bar item.*
4. **Collatz Repeat-Until** — a sentinel `while True: … break` that counts steps to 1 (U04 sentinel + break).
5. **For-Total Pass Bar** — a `for`/`range` running total (U05). *Pass-bar item.*
6. **Count by Condition** — count matches across a range (U04/U05 technique).
7. **Four-by-Four Times Table** — nested loops building each row by string accumulation (U05).

## Common mistakes

- Ordering the Q1 ladder broad-first so the verdict is wrong.
- `range` bounds in Q5/Q6 (`range(1, 5)` gives 1–4); off-by-one in the Q3 `while` counter.
- Forgetting the `break` (Q4) or a wrong stop condition — an accidental infinite loop; know how to interrupt.
- Q7 indentation: the inner `row = row + …` at 8 spaces, `print(row)` at 4.
- Byte-exact output: spaces between table entries, the float `.0`, capitals, punctuation.

## Discussion prompts

- Which question needed a `while` and which needed a `for`? Why?
- How does the Collatz loop (Q4) know when to stop?
- In the times table (Q7), what does the inner loop build before the row is printed?

## Grading

Pass = at least 5 of 7 correct, with **Q3 (while-counter)** and **Q5 (for-total)** among them — those are the
load-bearing loop skills. Key each question to its concept(s) above. Full marks require byte-exact output.
Partial credit: award Q1 if the branches are right but the order is off (note the fix); award Q7 if the row
math is right but the spacing is off.

## Differentiation

- Strugglers: Q1–Q3 (recap + one `while`) as the pass bar; treat Q4–Q7 as reach.
- Fast finishers: ask them to extend Q7 to a 5×5 table or add a running total to Q6.
