# Teacher Notes — Unit 01: Mad-Libs Story Machine

## Goals

Students leave able to run a Python program, print text, read simple error messages without panic, store words in named variables, collect input, and assemble text with f-strings.
Success looks like: every student runs a Mad-Libs machine they modified themselves, and nobody freezes when a red traceback appears.

## Pacing

Budget: two lessons of 60–90 minutes; this is the heaviest introduction load of the year at the most fragile point, so the exercise set stays short and the pace stays gentle.

- **Lesson 1 — run-program, print, comment, string-literal, error-messages (60–90 min).**
  Open on the project thread: run the finished Mad-Libs machine live and let the class shout the words.
  10 min: what a program is; running a notebook cell (run-program).
  25 min: print and string literals — students make the starter story their own.
  15 min: comments as notes-to-self.
  20 min: DELIBERATELY break a line (unclosed quote, misspelled print) and read the traceback together (error-messages); the message is a clue, not a scolding.
  Buffer: exercises 1–2.
- **Lesson 2 — variable, naming, input, string-concat, f-string (60–90 min).**
  Open on the thread: yesterday's story was fixed; today the machine asks for the words.
  20 min: variables as labeled boxes; naming conventions via bad-name comedy (`x`, `thing2`, `myAwesomeDogName`).
  20 min: input() collects words.
  25 min: assembling the story — concatenation first, then f-strings as the nicer way.
  Rest: exercises; finish the personal Mad-Libs machine.

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
