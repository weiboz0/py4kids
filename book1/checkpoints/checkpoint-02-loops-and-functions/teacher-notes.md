# Teacher Notes — Checkpoint 02: Loops and Functions

## Goals

A half-lesson check on Term 2's core: `for`/`range` and `while` loops, the accumulator
pattern, defining and calling functions, parameters and return values, scope, and reading
a turtle loop well enough to predict the shape.
Success looks like: you know who is shaky on FUNCTIONS specifically before project 01
(Arcade Night) asks students to write their own.

## Pacing

Budget: half a lesson (35–45 min), run inside the session that opens project 01.
5 min: frame it — "loops and functions are the tools you'll build your arcade game with;
show me where you are."
30–40 min: students work the eight questions solo, teacher circulating.
The rest of the session launches project 01.

## Common mistakes

- Q1 (for/range trace): off-by-one on `range(n)` (0..n-1) — a known Term-2 stumble.
- Q2 (while accumulator): resetting the running total inside the loop, or a condition that
  never becomes False.
- Q3/Q4 (functions): confusing `return` with `print` — the unit's central idea; this is the
  question that predicts project-01 readiness.
- Q5 (scope): assuming a name from inside a function is visible outside.
- Q6 (logical/nesting): `and`/`or` swapped, or a follow-up branch not indented under its
  parent.
- Q7 (turtle trace): computing the angle but not connecting 72° × 5 = 360° to "pentagon".

## Discussion prompts

Save for AFTER collection:
- Which is the more powerful idea — loops or functions — and why?
- Q7: how did you know it was a pentagon without running it?

## Differentiation

- Strugglers: Q1–Q5 alone is a complete checkpoint; say so quietly. The turtle-trace (Q7)
  is pure reasoning and works on paper for kids who freeze at a keyboard.
- Fast finishers: no extra questions — a checkpoint is a bounded ask.

## Grading

Manual, per D-002 — a judgment read. Per question:
1. **for/range output trace**: full = exact output including the right number of lines;
   partial = right idea, off-by-one on the count. Off-by-one is a targeted re-show, not a
   re-teach.
2. **while-accumulator completion**: full = a condition that terminates AND the total
   accumulates outside the reset; partial = loops but mis-updates. A never-terminating
   condition is the flag to catch before project 01.
3. **write-a-function-with-parameter**: the question asks the function to RETURN the greeting
   (the caller prints it), so full = correct `def` + parameter used + an f-string greeting
   `return`ed; partial = defines and uses the parameter but `print`s inside instead of
   returning (the exact return-vs-print gap Q4 targets — worth naming to the student).
4. **return-vs-print judgment**: THE load-bearing question. Full = names that `return` hands
   the value back for reuse while `print` only shows it. A wrong answer here predicts
   project-01 struggle — flag those students specifically.
5. **scope trace**: full = correct about what's visible where AND why the local name isn't
   available outside; partial = right answer, no "why".
6. **logical/nesting condition**: full = the correct branch AND correct `and`/`or`/nesting;
   partial = right operator, wrong branch order.
7. **turtle trace/predict**: full = "pentagon" (or five-sided) WITH the 360/5 = 72°
   reasoning; partial = the shape without the angle logic.
8. **build-it scoring function**: the question requires the function to RETURN the score, so
   full = a function that takes the three answers, accumulates with an `if` per answer, and
   `return`s the integer; partial = correct scoring but `print`ed inside instead of returned,
   or scoring done outside a function.

**Re-teach signal:** functions are the hard idea and project 01 leans on them hard. If a
third of the class or more misses Q3 or Q4 (writing a function / return-vs-print), spend
20–30 minutes re-teaching functions before project 01's build — don't let the project be
where the gap first shows.
