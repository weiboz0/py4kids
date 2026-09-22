# Teacher Notes — Unit 01: Output & Variables

## Goals

Students leave able to run a program, print output, write comments, use string literals, store values
in well-named variables, read a value from the keyboard with `input()`, join text with `+` and with
f-strings, and read a Python error message when something breaks.
Success looks like: every student changes three saved values and watches the whole "fact card" reprint
itself correctly, and can point to where each value is stored.

This is the first unit of the concept-first edition, so it is also where students learn the shape of a
Book 1b exercise: read the **Specification**, look at the **worked sample** (given values → expected
output), and make your cell produce that exact output.

## Pacing

Budget: three lessons of 60–90 minutes. Ten concepts land here — the year's joint-heaviest introduction
load — so each is taught as a short **worked-example ladder** (minimal → one twist → realistic, with a
*Notice* line per rung). The lesson-count is advisory; take as many rungs per sitting as time allows.

- **Lesson 1 — Make Output Appear (run-program, print, comment, string-literal).**
  Open on the project thread: the club needs a tidy fact card for its welcome board (the lesson's
  opening cell). Today, just make text appear.
  Run a first program; `print(...)`; add a `#` comment for a human reader; quote strings and see what
  quotes do and don't show. Keep it to output only — nothing is saved yet.
- **Lesson 2 — Save Values (variable, naming, input).**
  Thread: the card should change when the details change, so we must *save* the details.
  Assign values to variables; choose clear names (`favorite_color`, not `x`); read one value from the
  keyboard with `input()`. Show that a good name is documentation.
  Note on `input()`: demonstrate it live/typed. In the exercises and solutions the "given values"
  stand in for typing, so those cells never call `input()` — that is the house convention.
- **Lesson 3 — Assemble the Card (string-concat, f-string, error-messages).**
  Thread: put the saved details together into the card.
  Build a line with `+` (and notice you must join text to text), then rebuild it more readably with an
  f-string. Finish with the **deliberate broken/fixed** cell: run the broken version, read the traceback
  together, name the fix. End on the **Final build** — the whole card assembled from the saved values.

60-MINUTE CUT (any lesson): teach rungs 1–2 of each ladder live and leave the last rung as a "try it";
the *Notice* lines let students self-serve it.

## Exercises — core vs. extra vs. challenge

The bank is intentionally large (12 exercises); it is partitioned so a single lesson still fits 60–90 min:
- **Core (Exercises 1–6):** every student completes these in class — they exercise all ten concepts on
  the fact-card family of problems (welcome sign, labeled card, keyboard-filled card).
- **Extra practice (Exercises 7–10):** variety for fast finishers or homework.
- **Challenges (Exercises 11–12):** optional stretch; no core exercise depends on them.

Every exercise uses the **pre-function form** — given fixed values, produce an exact output — because
functions are not taught until Unit 07.
(Book 1b allows *fastforward*: examples may reach ahead to a not-yet-taught idea when a problem needs it.
Unit 01 barely needs it; **Unit 02 is where the forward-reaching `practices:` tagging convention is first
demonstrated** — no forward tags are needed here.)

## Common mistakes

- Forgetting the quotes around a string literal (`NameError`) — a planned traceback-reading moment.
- Joining text to a non-string with `+` (`TypeError`) — everything in a `+` chain must be text.
- Vague variable names (`a`, `thing`) that make the card code unreadable a week later.
- Expecting `#` comments to appear in the output — they are for humans, not the program.
- Overwriting a saved value by accident and wondering why the card changed.
- Mismatched capitals/spaces vs. the expected output — read the worked sample character by character.

## Discussion prompts

- Why store the name in a variable instead of typing it straight into the `print`?
- What does a comment give you that the code alone does not?
- When is an f-string clearer than joining with `+`? When might `+` be fine?
- A traceback looks scary — what are the two most useful pieces of information in it?

## Differentiation

- Strugglers: give the fact-card code with the values blanked out and have them fill in and run it —
  seeing the card change from their own values is the win.
- Fast finishers: Extra practice (7–10), then the Challenges (11–12).
- Middle tier: rewrite one `+`-joined line as an f-string and confirm identical output.
