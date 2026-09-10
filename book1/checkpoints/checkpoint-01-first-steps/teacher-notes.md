# Teacher Notes — Checkpoint 01: First Steps

## Goals

A low-stakes half-lesson check on everything from units 01–02: printing, strings,
variables, input, string concatenation, f-strings, numbers and conversion,
comparisons, if/elif/else,
the while loop, and reading a traceback without panic.
Success looks like: you know exactly who needs a revisit before unit 03's dense
turtle-and-loops stretch, and every student leaves feeling "I can do this".

## Pacing

Budget: half a lesson (30–45 min), run inside the session that opens unit 03.
5 min: frame it — "show what you've got; this is for ME to teach you better, not a test
with a grade on the fridge."
25–35 min: students work the seven questions solo in the notebook, teacher circulating.
5 min: collect (save-and-close), tease the turtle.
The remaining half-lesson starts unit 03's hook — the spirograph teaser lands better
with the checkpoint's confidence still warm.

## Common mistakes

- Question 1 (fix-the-error): keeping the integer unconverted in the `+` expression, or
  switching to an f-string instead of authoring the requested concatenation; students who
  miss the traceback's type clue need the error-reading ritual re-run, not more syntax.
- Predict-the-output: computing the arithmetic right but dropping the f-string's
  surrounding text.
- The while question: writing `=` for `==` in the condition — note it but grade the
  INTENT; the concept is "the loop needs a condition that can change".
- The build-it: scope creep — some students build the whole guessing game; that's a
  strength signal, not an error.

## Discussion prompts

Save discussion for AFTER collection (answers walk otherwise):
- Which question felt easiest? (It's usually the traceback one — point out how far
  they've come since lesson 1's first red error.)
- What would you add to the detective game if you had an hour?

## Differentiation

- Strugglers: questions 1–4 alone are a legitimate complete checkpoint; say so quietly
  and let them stop there without ceremony.
- Fast finishers: improve the build-it silently (no extra questions to hand out —
  the point of a checkpoint is a bounded ask).

## Grading

Manual, per D-002 — a judgment read, not a point count. Per question:
1. **Fix-the-error** (error-messages, string-concat): full = names the two types AND uses
   `str(clues_found)` in a working `+` concatenation assigned to `clue_message`, then prints
   it; partial = fixes by pattern-matching without citing the message, or uses an f-string
   instead of the requested concatenation. Partial is fine at this stage; note who cited
   the message — they're your future debuggers.
2. **Predict-the-output** (f-string, arithmetic): full = exact string; partial = right
   arithmetic, mangled text. Partial means re-show f-strings in unit 04's scoring, not
   a re-teach.
3. **Write-a-line** (input, int conversion): the `int(input(...))` shape is the whole
   point; missing `int()` here predicts the unit-04 exercise-5 bug — flag those students
   for that moment.
4. **Trace the if/elif chain** (comparison, elif-else): full = right branch AND says why
   the later branch didn't run. The "why" is the understanding.
5. **Complete the while condition**: full = the specific condition `guess != secret`
   (or an equivalent that keeps looping while the guess is wrong AND stops when it's
   right); a condition that can never become False (`while True`-ish) or the wrong
   comparison is the classic miss — catch it before unit 03 leans on loops hard.
6. **Naming/comment judgment**: any defensible answer is full marks; this question
   exists to make style a conversation, not a rule.
7. **Build-it**: full = it RUNS and uses the required shape — a hard-coded secret, one
   `input()` guess, and an `if`/`elif`/`else` giving a too-low / too-high / correct
   verdict; partial = runs but collapses the three-way branch to one check. Elegance is
   not the bar at week five, but the three-way branch is the point of the question.

**Re-teach signal:** if a third of the class or more stumbles on questions 4–5
(branches/loops), spend 20 minutes re-teaching before unit 03's lesson 2 — unit 03
assumes loop confidence. Individual gaps ride along fine; unit 04's quiz project
re-practices everything here.
