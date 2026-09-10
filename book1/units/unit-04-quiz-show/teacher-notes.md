# Teacher Notes — Unit 04: Quiz Show

## Goals

Students leave able to keep a running score with the accumulator pattern, combine
conditions with `and`/`or`, nest a conditional inside another for follow-up questions,
and end a loop early with `break`.
Success looks like: every student hosts a quiz whose score, streak bonus, and
sudden-death round they built and can explain.

## Pacing

Budget: three lessons of 60–90 minutes. Each concept is taught as a short **worked-example ladder** (minimal → one step up → real game use, with a *Notice* line per rung); the lesson-count is advisory. Closure note for authors: U04 counting loops are `while`+counter (counting is legal here — `accumulator` is introduced — but `for`/`range` are NOT in this unit; output uses f-strings, not string `+`).

- **Lesson 1 — accumulator, logical-ops (60–90 min).**
  Open on the project thread: the teacher hosts a three-question quiz against the class,
  keeping score on the board — today the machine takes over the scoring.
  25 min: the accumulator ladder (`score = score + 1` once → again → inside a `while` loop → two accumulators, score + `questions_asked`). Name the ACCUMULATOR pattern out loud.
  25 min: the logical-ops ladder (`and` → `or` → `not` → a combined streak-bonus rule). All three operators are genuinely taught, each on its own rung.
  Rest: the full opening round + exercises 1–3.
  60-MINUTE CUT: teach ladder rungs 1–2 live, leave the last rung as a "try it".
- **Lesson 2 — conditional-nesting (60–90 min).**
  Open on the thread: finals are dramatic — a follow-up unlocks only when part one is right.
  25 min: the nesting ladder (an `if` inside an `if` → an inner `if`/`else` → the realistic locked-follow-up gate). Indent together; trace on the board.
  Rest: nesting exercises.
- **Lesson 3 — break-statement + SUDDEN DEATH (60–90 min).**
  Open on the thread: one wrong answer ends everything.
  25 min: the `break` ladder (leave a `while` loop at a fixed point → break on a wrong-answer condition → the full SUDDEN DEATH round with an `if`/`elif`/`else` dispatch). Let the drama sell the statement.
  Rest: exercises; play each other's shows.
  60-MINUTE CUT: build sudden death with two questions instead of three; the remix exercise restores the third.

Practices reappearance: boolean and type-conversion run through every scoring check
(`int(input(...))`, True/False talk); loop-counter drives sudden death's dispatch and
the lightning-round Challenge; error-messages gets a deliberate debugging moment in
exercise 5. All four reappear in checkpoint 02.

## Common mistakes

- Resetting the accumulator inside the loop (`score = 0` in the body) — score stays 0 or 1;
  trace it and move the line up.
- `and` where `or` was meant (and vice versa) in the bonus rule — truth-table the bonus
  on the board with class examples.
- Nesting by wishful thinking: the follow-up `if` not indented under its parent, so it
  always runs. Show both indentations side by side.
- `break` outside any loop (SyntaxError — a planned traceback-reading moment) and
  `break` ending the WHOLE show when only the round should end.
- Forgetting `int()` on a numeric answer, so `"7" == 7` is False and a right answer
  scores wrong — this is exercise 5's deliberate bug.

## Discussion prompts

- Where else in life is there an accumulator? (Loyalty points, XP bars, savings jars.)
- The streak bonus needs `and`. What rule would need `or`? What about `not`?
- Is sudden death FAIR? When is ending early kinder than playing on?

## Differentiation

- Strugglers: ship the lesson-1 quiz as a fill-in-the-scoring skeleton; pair for
  sudden death; the two-question variant is a legitimate finish line.
- Fast finishers: Challenge exercises — double-or-nothing (nested condition on the
  final answer) and the lightning-round countdown (a while + counter counting DOWN,
  nothing new required).
- Middle tier: the category-bonus exercise (one extra nested branch) before Challenges.
