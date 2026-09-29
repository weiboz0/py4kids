# Teacher Notes — Unit 03: What Does This Program Do? – Branching

## Goals

Students learn ACSL's third Contest 1 category: reading a short program and writing its exact output.
By the end they can:

- read ACSL pseudocode and translate it to Python using the dialect table:
  - `/` is real division; `^` is `**`
  - `!`, `&&`, `||` are `not`, `and`, `or`
  - `abs`
  - ACSL `int(x)` is the greatest integer ≤ x, which is **`math.floor(x)`, not Python's `int()`**
  - `sqrt` is `math.sqrt`
- trace a program with a **trace table**, one row per step, and write the one printed line exactly;
- follow `if`/`elif`/`else` chains (only the first true branch runs), separate `IF`s (each one is tested), nested decisions, and `and`-before-`or` precedence;
- *(Intermediate and above; Contest 1 covers all constructs for these divisions)* trace `FOR` loops (which include their end value, with steps up and down), `WHILE` loops, 1D arrays starting at 1, **2D arrays** `A(r, c)` as grids, and strings;
- use ACSL's substring rules, which are **not** Python slices: `S[:n]` is the first n characters, `S[n:]` is the **last** n, and `S[a:b]` is positions a **through** b.

The hook is a Junior branching question in pseudocode, with a = 26 and b = 9. The answer is 15; Lesson 1 translates the program and Lesson 2 traces it by hand.

## Pacing

Budget: three lessons of 60–90 minutes, the last unit before the Contest 1 practice.

- **Lesson 1: reading pseudocode.**
  - Build the dialect table with the class, and do one demo per row.
  - Spend extra time on `int(-1.5)`: ACSL and `math.floor` give −2, Python's `int()` gives −1.
  - Also on `6 / 3` printing `2.0` in Python.
- **Lesson 2: tracing branches.**
  - Trace-table drills on the hook, then chains versus separate `IF`s, nesting, and digit arithmetic with `//` and `%`.
- **Lesson 3 (Intermediate and above): loops, arrays, grids, strings.**
  - Show `FOR i = 1 TO 10 STEP 3` becoming `range(1, 11, 3)`.
  - A 2D grid as a list of rows (`grid[r][c]`).
  - The ACSL substring table next to Python slices.
- **Exercises:** 1–7 Junior (mostly short-answer, with one predict-then-verify program), 8–16 Intermediate, 17–18 Challenges. At least one third of the items are in pseudocode.

**60-minute cut:** keep the dialect table, the trace-table method and `if`/`elif` chains. Juniors can skip Lesson 3; for Intermediate students, move strings to homework.

## Common mistakes

- Using Python's `int()` for ACSL `int` on a negative number (truncates instead of flooring).
- Reading ACSL substrings as Python slices: `S[4:]` in ACSL is the **last** four characters, and `S[2:6]` includes position 6.
- Continuing down an `elif` chain after a branch was already true, or skipping a later separate `IF` because an earlier one was true.
- Stopping a `FOR` loop one step early (ACSL `FOR` includes its end value).
- Starting arrays at the wrong index; the program states whether it starts at 0 or 1.
- Writing extra spaces or text in the answer; `OUTPUT x, y` is one line with single spaces.
- Forgetting that `/` gives a decimal (`7 / 2` is `3.5`).

## Discussion prompts

- Why does ACSL use its own pseudocode instead of one real language?
- Which rows of the dialect table are most likely to trick you in a contest, and how will you remember them?
- When a trace gets long, how do you keep from losing track? What goes in each column of your trace table?
- How is an `elif` chain different from several separate `if`s? Invent an input where they give different answers.

## Differentiation

- **Junior:** Lessons 1–2 and Exercises 1–7. The Junior Contest 1 category is Branching.
- **Intermediate and Senior:** everything; Lesson 3 is essential, because their Contest 1 draws on all constructs.
- **Classroom:** the short-answer items at Junior and Intermediate level.
- **Elementary:** not part of the Elementary path (WDTPD is not an Elementary category).
- **Support:** a printed dialect table and a blank trace-table sheet. Have students trace first, then check with Python.
- **Extension:** write a pseudocode program whose output changes if you confuse ACSL `int` with Python `int`, or ACSL substrings with Python slices; swap with a partner.
