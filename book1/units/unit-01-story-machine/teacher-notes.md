# Teacher Notes — Unit 01: Mad-Libs Story Machine

## Goals

Students leave able to run a Python program, print text, read simple error messages without panic, store words in named variables, collect input, and assemble text with f-strings.
Success looks like: every student runs a Mad-Libs machine they modified themselves, and nobody freezes when a red traceback appears.

## Pacing

Budget: three lessons of 60–90 minutes (this is the heaviest introduction load of the year at the most fragile point). Each concept is taught as a short **worked-example ladder** — a minimal example, then one small twist, then a realistic use — with a one-line *Notice* after each rung naming the single new thing. The lesson-count is advisory: pull in as many rungs as the class has time for; the ladders exist so students generalize a concept rather than copy one line.

- **Lesson 1 — run-program, print, string-literal, comment, error-messages (60–90 min).**
  Open on the project thread: run the finished Mad-Libs machine live and let the class shout the words.
  10 min: what a program is; running a notebook cell (run-program).
  30 min: the print ladder (one line → several lines → a blank line) and the string-literal ladder (double quotes → single quotes → punctuation is text) — students make each rung their own.
  15 min: the comment ladder (a note line → a comment at the end of a line).
  20 min: DELIBERATELY break a line (unclosed quote) and read the traceback together (error-messages); the message is a clue, not a scolding.
- **Lesson 2 — variable, naming, input (60–90 min).**
  Open on the thread: yesterday's story was fixed; today the machine remembers and asks for the words.
  25 min: the variable ladder (save + show → two variables → reassigning replaces the value).
  20 min: the naming ladder (a descriptive name → underscores for multiple words → exact-same-spelling), spiced with bad-name comedy (`x`, `thing2`, `myAwesomeDogName`).
  20 min: the input ladder (prompt + show → reuse the reply → two questions) — each rung is teacher-run (it waits for typing).
- **Lesson 3 — string-concat, f-string, and the Story Machine (60–90 min).**
  25 min: the concatenation ladder (`+` two pieces → join several → spaces must be added by hand).
  25 min: the f-string ladder (one `{name}` → several `{names}` → the same name twice) as the nicer way.
  Rest: finish the personal Mad-Libs machine; exercises.
  60-MINUTE CUT (any lesson): teach rungs 1–2 of each ladder live and leave rung 3 as a "try it" — the *Notice* lines let students self-serve the last rung.

Practices reappearance (none — this is the first unit; every concept here is practiced in units 02–04 and checkpoint 01).

## Common mistakes

- Unclosed or mismatched quotes (the year's most common lesson-1 error — treat it as a traceback-reading rehearsal, not a failure).
- `Print` vs `print` (case matters; NameError).
- Typing a variable name differently at use site than at assignment (NameError — connect to naming conventions).
- Forgetting quotes around literals, or quoting variable names inside f-string braces.
- Expecting `input()` to continue by itself — students must press Enter.

## Discussion prompts

- Who "reads" your program — the computer, or the next human? Why do comments exist if the computer ignores them?
- Why might `dog_name` be a better label than `x`? When would short names be fine?
- The error message pointed at the wrong-looking line — how did it still help us?

## Differentiation

- Strugglers: pair-program lesson 2's machine; provide the story skeleton with blanks so only variables/input remain.
- Fast finishers: the Challenge exercises (multi-paragraph story reusing variables; emoji-art title) — stretch previews nothing untaught, it just goes bigger.
- Absent students: lesson 1 can be caught up in 20 minutes with a partner before lesson 2; nothing else depends on the broken-line ritual except courage.
