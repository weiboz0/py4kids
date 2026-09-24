# Teacher Notes — Checkpoint 01: Foundations

## Goals

A short, un-themed mixed assessment proving Units 01–03: output & variables, numbers & arithmetic
(including `//`/`%`, float output, and text↔number conversion), and decisions (`if`/`elif`/`else`,
`and`/`or`/`not`). It introduces nothing new and assesses only what has been taught. Students work solo;
it is solution-free like a unit's exercises.

The checkpoint is deliberately **pre-function and pre-loop**: every question is solvable with
straight-line code — NO loops, NO lists, NO self-referential reassignment (`x = x + …`), and no
built-ins beyond `print`/`int`/`float`/`str`. (Those ideas arrive in Unit 04+.)

## Pacing

Budget: half a lesson (~30–45 minutes). Hand it out after Unit 03. Let students attempt all seven
questions in order (Q1–Q4 are the gentle output/number items; Q5–Q7 are the decision/logic/traceback
items). Reserve the last 10 minutes to read Q7's traceback together as a class if time is tight.
The seven questions and the concept each targets:
1. **Name Card** — output + variables + f-string (U01).
2. **Labeled Item** — a single labeled line built with `+` string concatenation (U01).
3. **Hours and Minutes** — `//` and `%` on a given number of minutes (U02).
4. **Converted Average** — `int()` on typed values, `/` → a float shown exactly (U02).
5. **Ordered Score Ladder** — an `if`/`elif`/`else` ladder only correct top-down (U03).
6. **Range and Entry Test** — an `and`/`or` condition that prints `Entry approved` / `Entry denied`
   (U02 comparison + U03 logic).
7. **Read the Final Traceback Line** — read a broken snippet's traceback and name the error *type* on
   its final line (U01–U02 `error-messages`).

## Real-version notes (design 006, plan 084)

Each question now ends with an ungraded **Real version** note (CP01 Q7, a traceback-reading question,
says **No real version**). Graded answers still use the fixed given values and never call `input()`; the
solutions notebook shows each real program — the same work reading stdin with a bare `input()`, the way a
contest problem does — with a sample input and its expected output. Use one or two as a warm-up after the
checkpoint, typing the sample input live.

## Common mistakes

- `/` printing `10.0` where a student expected `10` (Q4) — `/` always gives a float.
- Ordering the Q5 `elif` ladder broad-test-first, so the verdict is wrong.
- `=` vs `==` inside a condition.
- On Q7, reading the *first* line of the traceback instead of the final error line.
- Byte-exact output: capitals, spaces, punctuation, and the float `.0`/`.5` all count.

## Discussion prompts

- Which question felt hardest, and which concept did it test?
- Why must the Q5 ladder test the highest band first?
- What does the final line of a traceback tell you that the earlier lines do not?

## Grading

Pass = at least 5 of 7 correct, with Q3 (int math) and Q5 (elif ordering) among them — those two are the
load-bearing U02/U03 skills. Key each question to its concept (see Pacing). Full marks require byte-exact
output. Partial credit: award Q5 if the branches are right but the order is off, and note the fix.

## Differentiation

- Strugglers: allow Q1–Q4 (output/numbers) as the pass bar; treat Q5–Q7 as reach.
- Fast finishers: ask them to add a second correct `elif` branch to Q5 or a second condition to Q6.
