# Teacher Notes — Unit 04: Quiz Show

## Goals

Students leave able to keep a running score with the accumulator pattern, combine
conditions with `and`/`or`/`not`, store boolean results, nest a conditional inside
another for follow-up questions, convert numeric input, and end a loop early with `break`.
Success looks like: every student hosts a quiz whose score, streak bonus, and
sudden-death round they built and can explain, including why a chosen condition uses
`and`, `or`, or `not`.

## Pacing

Budget: three lessons of 60–90 minutes. Each concept is taught as a short **worked-example ladder** (minimal → one step up → real game use, with a *Notice* line per rung); the lesson-count is advisory. Closure note for authors: U04 counting loops are `while`+counter (counting is legal here — `accumulator` is introduced — but `for`/`range` are NOT in this unit; output uses f-strings, not string `+`).

- **Lesson 1 — accumulator, logical-ops (60–90 min).**
  Open on the project thread: the teacher hosts a three-question quiz against the class,
  keeping score on the board — today the machine takes over the scoring.
  25 min: the accumulator ladder (`score = score + 1` once → again → inside a `while` loop → two accumulators, score + `asked`). Name the ACCUMULATOR pattern out loud.
  25 min: the logical-ops ladder (`and` → `or` → `not` → a combined streak-bonus rule). All three operators are genuinely taught, each on its own rung.
  Rest: the full opening round + exercises 1–2. NAME the two patterns (running total, counting by condition) from their Spotlights in the closing **Algorithm Extension** lesson section here, while the accumulator is fresh — just the one-line hook each, so every student has met the name. Each Spotlight is now followed by a short **worked-example ladder** (code rungs + Notices → a put-it-together); those ladders, like Exercises 11–12, are **enrichment** (walk through them time-permitting / as homework, not required in-class) so the 60–90 min budget is unchanged — see the Algorithm Extension note below.
  Before Exercise 11 (running total), run a 2-minute unplugged trace: announce three round scores, have students add each score on their fingers, and say the new total-so-far after every round.
  Before Exercise 12 (counting by condition), run a second 2-minute unplugged trace: ask three yes/no questions, have classmates raise a hand when the answer is yes, and bump one visible counter for each raised hand.
  60-MINUTE CUT: teach ladder rungs 1–2 live, leave the last rung as a "try it".
- **Lesson 2 — conditional-nesting (60–90 min).**
  Open on the thread: finals are dramatic — a follow-up unlocks only when part one is right.
  25 min: the nesting ladder (an `if` inside an `if` → an inner `if`/`else` → the realistic locked-follow-up gate). Indent together; trace on the board.
  Rest: exercise 3 and a partner trace of each nested branch.
- **Lesson 3 — break-statement + SUDDEN DEATH (60–90 min).**
  Open on the thread: one wrong answer ends everything.
  25 min: the `break` ladder (leave a `while` loop at a fixed point → break on a wrong-answer condition → the full SUDDEN DEATH round with an `if`/`elif`/`else` dispatch). Let the drama sell the statement.
  Rest: exercises 4–7; play each other's shows.
  60-MINUTE CUT: build sudden death with two questions instead of three; the remix exercise restores the third.

Practices reappearance: boolean and type-conversion run through every scoring check
(`int(input(...))`, True/False talk); loop-counter drives sudden death's dispatch and
the lightning-round Challenge; error-messages gets a deliberate debugging moment in
exercise 5. All four reappear in checkpoint 02.

Running-total route: name the pattern in class from the lesson Spotlight; Exercise 11 is its home in the Algorithm Extension (run as time permits). Retrieve it inside a function in Unit 05 exercise 11, retrieve it over a list in Unit 07 exercise 10, then assign Unit 09 exercise 13 after the file-reading lesson to transfer the same total-so-far update to saved-score lines.

Count-by-condition route: name the pattern in class from the lesson Spotlight; Exercise 12 is its home in the Algorithm Extension (run as time permits). Retrieve it over characters in Unit 06 exercise 12, retrieve it over a score list in Unit 07 exercise 11, then use Unit 08 exercise 12 to show the tally-by-key variation: one count per word in a dictionary.

## Exercise allocation

- **In class:** exercises 1–2 after the accumulator/logical-ops ladder, exercise 3
  after conditional nesting, and exercises 4–7 after the `break` ladder. The running-total and
  count-by-condition homes now sit in the **Algorithm Extension** (Exercises 11–12); name both
  patterns in class from the lesson Spotlights and run Exercises 11–12 as time permits.
  This in-class path reps every Unit 04 `introduces`/`practices` concept at least once,
  except `running-total` and `count-by-condition`, whose homes now live in the
  Algorithm Extension (Exercises 11–12) — named in class, practised there.
- **Homework / More Practice:** exercises 8–10 after Lesson 3; review them at the
  opening of the next meeting.
- **Algorithm Extension (enrichment):** Exercises 11–19 — the two pattern homes plus seven
  unmarked loop drills; routed as time-permitting / homework / differentiation (see below), never
  gating the core quiz build.
- **Optional stretch:** the two Challenges remain fast-finisher work and do not
  supply any required mastery repetition.

Count exemption: `error-messages` has one genuine authoring repetition in exercise 5; staging three artificial crashes would displace more useful quiz-building practice.

## Algorithm Extension (enrichment)

Exercises 11–19 form the unit's **Algorithm Extension** — an explicitly-labelled, end-of-notebook
enrichment block, routed as time-permitting / homework / differentiation (design 002 v8); it never
gates the core quiz build. Every drill keeps Unit 04's closure: a `while`+counter loop that picks each
value with an `if`/`elif`/`else` chain (no `for`/`range`/list), output via f-strings.

- **Ex 11 running total** and **Ex 12 counting by condition** — the two pattern homes (named in the
  lesson Spotlights).
- **Ex 13** two-counter tally (correct vs wrong), **Ex 14** conditional sum (add only rounds ≥ 5, → 18),
  **Ex 15** signed accumulate (+2 / −1, → 4), **Ex 16** opening streak (`break` at the first wrong, → 3).
- **Ex 17 & Ex 18** are the deliberate **same-data, opposite-boundary** pair on scores 4, 6, 5, 7, 3 /
  budget 12: Ex 17 *checks before adding* (the total that fits, 10, and how many fit, 2); Ex 18 *adds
  then checks* (the tipping total, 15, and that the 3rd score — 5 — tips it). Run them back-to-back so
  students feel `<=`-before-add versus `>`-after-add on identical data.
- **Ex 19** (homework, interactive) sums typed scores until the player enters 0 — the sentinel-stop
  variation; its cell is `no-exec`.

These are extra reps of patterns students have already met; assign as many as time allows — the point is
repeated, low-stakes exposure to the same loop shapes.

## Common mistakes

- Resetting the accumulator inside the loop (`score = 0` in the body) — score stays 0 or 1;
  trace it and move the line up.
- `and` where `or` was meant (and vice versa) in the bonus rule — truth-table the bonus
  on the board with class examples, then have students say both accepted spellings in
  exercise 8 before they write the `or` expression.
- Nesting by wishful thinking: the follow-up `if` not indented under its parent, so it
  always runs. Show both indentations side by side.
- `break` outside any loop (SyntaxError — a planned traceback-reading moment) and
  `break` ending the WHOLE show when only the round should end.
- Forgetting `int()` on a numeric answer, so `"7" == 7` is False and a right answer
  scores wrong — this is exercise 5's deliberate bug.
- Updating a counter only on the correct-answer path, which can trap the player in a
  retry loop; trace attempts 1, 2, and 3 on paper.

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
