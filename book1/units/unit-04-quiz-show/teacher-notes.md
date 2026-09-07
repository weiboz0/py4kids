# Teacher Notes — Unit 04: Quiz Show

## Goals

Students leave able to keep a running score with the accumulator pattern, combine
conditions with `and`/`or`, nest a conditional inside another for follow-up questions,
and end a loop early with `break`.
Success looks like: every student hosts a quiz whose score, streak bonus, and
sudden-death round they built and can explain.

## Pacing

Budget: two lessons of 60–90 minutes.

- **Lesson 1 — accumulator, logical-ops (60–90 min).**
  Open on the project thread: the teacher hosts a three-question quiz against the class,
  keeping score on the board — today the machine takes over the scoring.
  20 min: the straight-line three-question quiz (input, int(), if/elif — all owned since unit 02).
  20 min: `score = score + 1` — name the ACCUMULATOR pattern out loud; add a visible
  `questions_asked` counter (counting arrived with unit 03's loops; today it counts
  the game the class actually cares about).
  25 min: the streak bonus — right answer AND streak alive earns double; `and`, `or`, and
  `not` all arrive here — the bonus rule needs `and`, and `not on_streak` powers the
  coasting-penalty (exercise 7). All three logical operators are genuinely taught.
  Rest: exercises 1–3.
  60-MINUTE CUT: drop the `or` variant (it returns in exercise 2); the accumulator
  and one `and` are the non-negotiable core.
- **Lesson 2 — conditional-nesting, break-statement (60–90 min).**
  Open on the thread: yesterday's quiz was fair; finals are dramatic.
  20 min: the follow-up question — a bonus part asked ONLY if part one was right
  (an `if` inside an `if`; indent together, trace on the board).
  30 min: SUDDEN DEATH — a `while` loop over `questions_asked` dispatching three
  hard-coded questions through an if/elif chain; one wrong answer and `break` ends the
  round on the spot. Let the drama sell the statement.
  Rest: exercises; play each other's shows.
  60-MINUTE CUT: build sudden death with two questions instead of three; the remix
  exercise restores the third.

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
