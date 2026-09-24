# Teacher Notes — Unit 01: Output & Variables

## Goals

Students leave able to run a program, print output (one value, several values with commas, and with
`sep=`/`end=`), write comments, use string literals including the escapes `\n`, `\t`, `\"` and
triple-quoted strings, store values in well-named variables, read a value from the keyboard with
`input()`, join text with `+` and with f-strings, and read a Python error message when something breaks.
Success looks like: every student changes three saved values and watches the whole "fact card" reprint
itself correctly, can point to where each value is stored, and can turn a fixed-value program into a
"real program" that reads its values with `input()`.

This is the first unit of the concept-first edition, so it is also where students learn the shape of a
Book 1b exercise: read the **Specification**, look at the **worked sample** (given values → expected
output), make your cell produce that exact output, and then read the **Real version** line — the same
program written to read its input, the way a contest problem does.

## Pacing

Budget: three lessons of 60–90 minutes. Ten concepts land here — the year's joint-heaviest introduction
load — so each is taught as a short **worked-example ladder** (minimal → one twist → realistic, with a
*Notice* line per rung). Every code cell adds **one** new idea. The lesson-count is advisory.

- **Lesson 1 — Make Output Appear (run-program, print, comment, string-literal).**
  Open on the fact-card thread. `print(...)`; then the new **Printing several things** ladder:
  `print("Name:", "Maya")` (a comma adds a space) → `sep=" / "` → `end=""` (one cell, two prints on one
  line). Comments; quotes; the new **Special characters** ladder: `\n`, `\t`, `\"`, then a triple-quoted
  three-line picture. No input yet (Lesson 1 is exempt from the real-input rule).
- **Lesson 2 — Save Values (variable, naming, input).**
  Assign values; choose clear names; then `input()` — the three `no-exec` cells are real programs
  students run at home or with you live (e.g. `name = input("Name: ")`, then `print("Hello,", name)` —
  the comma form, because `+` comes in Lesson 3).
- **Lesson 3 — Assemble the Card (string-concat, f-string, error-messages).**
  `+`, then f-strings; the `no-exec` "real card" cell reads two values and prints one f-string line.
  Finish with the deliberate broken/fixed traceback cells and the **Final build**.

60-MINUTE CUT (any lesson): teach rungs 1–2 of each ladder live and leave the last rung as a "try it";
the *Notice* lines let students self-serve it. In Lesson 1, `sep=`/`end=` and the triple-quoted picture
are the natural "try it" rungs.

## Exercises — core vs. More Practice vs. challenge

20 exercises, partitioned so a single lesson still fits 60–90 minutes:
- **Core (Exercises 1–7 and 12–14)** — the in-class path: output, comments, string literals,
  concatenation, f-strings, a traceback repair (Ex 6), writing your own named variables (Ex 7), plus
  the new **Comma Print** (12, `Club: Origami` / `Room: B12`), **Room Sign** (13, `West Wing, Room 204`
  with `+`) and **Escape Poem** (14, one string with `\n` and `\t`). Exercises 12–14 require a purpose
  comment.
- **Extra practice (Exercises 8–11)** — the original extra set (8 now carries a Real version).
- **More Practice (Exercises 15–18)** — homework / fast finishers: **Predict the Output** (15:
  `A B`, `x-y-z`, `Go!Now`), **Swap Two Values** (16: pear/plum with a temporary variable), **Fix the
  NameError** (17: `Favorite` vs `favorite`, prints `mango`), **Triple-Quote Cat** (18: `=^.^=` /
  `(   )` / ` | |`).
- **Challenges (Exercises 19–20)** — optional: reassignment (Two Member Badges) and a two-bug error hunt.

**Real versions.** Every exercise that takes input ends with a **Real version** line; its solution shows
**The real program** — it reads each value with a bare `input()` (one per line), does the same work and
prints the same lines, with a **Sample input** and **Expected output**. Run one or two of these live: type
the sample input and watch the expected output appear. Repair/predict exercises (6, 15, 17, 20) and
fixed-art exercises (14, 18) say **No real version** instead. Graded solution cells never call `input()`
(the notebook runs automatically in CI); the real programs are for typing in and running by hand.

Every exercise uses the **pre-function form** — given fixed values, produce an exact output — because
functions are not taught until Unit 07. (Book 1b allows *fastforward*; **Unit 02 is where the
forward-reaching `practices:` tagging convention is first demonstrated** — no forward tags are needed here.)

## Common mistakes

- Forgetting the quotes around a string literal (`NameError`) — a planned traceback-reading moment.
- Adding a space in the wrong place (or forgetting one) inside a `+` chain; conversely, adding an extra
  space with the comma form — `print("Name:", name)` already inserts one.
- `end=""` surprises: the next `print` continues on the same line. A bare `print()` ends the line.
- Escapes: `\n` is ONE character (a line break), not two; a single backslash must start a real escape.
- Triple-quoted strings: text placed on the line after the opening `"""` starts with a newline — the
  worked samples start the picture right after the quotes.
- Vague variable names (`a`, `thing`); expecting `#` comments to appear in the output; overwriting a
  saved value by accident.
- Mismatched capitals/spaces vs. the expected output — read the worked sample character by character.

## Discussion prompts

- Why store the name in a variable instead of typing it straight into the `print`?
- When is `print(a, b)` handier than `+`? When is an f-string clearer than both?
- The Real version reads its values with `input()`. What changes in the program, and what stays the same?
- A traceback looks scary — what are the two most useful pieces of information in it?

## Differentiation

- Strugglers: give the fact-card code with the values blanked out and have them fill in and run it;
  Core 12–14 are short and confidence-building.
- Fast finishers: More Practice 15–18, then the Challenges, then type in two of the real programs and run
  them with their own input.
- Middle tier: rewrite one `+`-joined line as an f-string and as a comma `print`, and confirm identical
  output.

## More Practice ideas (design 006 D9 genres — for extra homework)

- **Output & formatting:** a three-line business card using `sep="|"`; a receipt whose total line uses
  `end=""` to stay on the same line as a label.
- **ASCII art:** a rocket or house drawn with one triple-quoted string (no backslashes).
- **Debug & predict:** give three `print` lines with mixed commas/`sep`/`end` and have students predict
  the exact output before running.
- **Input validation (preview):** read a name twice and print both — then discuss what happens if the
  user just presses Enter.
