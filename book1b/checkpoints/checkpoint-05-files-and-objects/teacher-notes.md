# Teacher Notes — Checkpoint 05: Files & Objects

## Goals

The mandatory final checkpoint, proving Units 01–13, with the load on the two most recent units: file I/O
(save/load, `with`, line-by-line reading and searching) and objects (a class with `__init__`, attributes, and
methods). It is the only assessment of U12's and U13's concepts before the end-of-book Algorithm Challenge.
It introduces nothing new. Students work solo; every question is in the function/class form, checked by
calling it on fixed inputs. File questions are SELF-CONTAINED (they write their file before reading it) and
use git-ignored scratch names.

The checkpoint stays strict: **no inheritance, no dunder methods beyond `__init__`, no decorators; no
comprehensions, no `math`/`import`; file methods limited to read/readlines/readline/write/close; text joined
with f-strings (no `+`); search lines with `==` (no `in`); no `while`/`range`/`sorted`/`and`/`or`.**

## Pacing

Budget: **45–60 minutes** (heavier than earlier checkpoints — file setup + class definitions). Hand out after
Unit 13. The seven questions and their targets:
1. **Score File Round Trip** (`save_scores`/`load_scores`) — `file-write`+`file-read`+`with` (U12). *Pass-bar (round-trip).*
2. **Load a Score Summary** (`score_summary`) — load numbers, report `[total, highest, strong_count]`
   (`strong_count` = how many scores are ≥ 15) (U12 stats).
3. **Find the First Matching Team** (`find_team`) — `linear-search` over lines with `==` (U12).
4. **Make a Point** (`Point`) — a class with `__init__` + attributes; construct and read (U13).
5. **Rectangle Report** — an `area()` method + a `describe()` f-string method (U13 methods).
6. **Counter Award Band** (`Counter.award_band`) — an `elif` ladder method on an attribute (U03/U13).
7. **Save a Labeled Rectangle** — a class whose method saves itself to a file + a `string-slice`
   (`short_code`) of an attribute — ties U12 + U13 (U12+U13). *Pass-bar (class-with-a-method).*

## Real-version notes (design 006, plan 084)

Each question now ends with an ungraded **Real version** note (CP01 Q7, a traceback-reading question,
says **No real version**). Graded answers still use the fixed given values and never call `input()`; the
solutions notebook shows each real program — the same work reading stdin with a bare `input()`, the way a
contest problem does — with a sample input and its expected output. Use one or two as a warm-up after the
checkpoint, typing the sample input live.

## Common mistakes

- Reading a file before it is written — each file question writes its own file first.
- `int(line.strip())` forgotten (a read line is a string with a newline).
- Forgetting `self` in a method or attribute reference.
- Q3: returning after the loop instead of inside it; using `target in text` instead of the line-by-line `==`
  search the question asks for.
- Reaching for `math.sqrt`, a comprehension, `__str__`, `+`-joined text, or `and`/`or` — none are needed.

## Discussion prompts

- Which questions save AND load (round-trip), and why does loading usually return a new value or object?
- In Q4/Q5, what does each `Point`/`Rectangle` remember, and what does a method compute from it?
- In Q7, how does an object save itself, and how is `short_code` a slice rather than a single character?

## Grading

Pass = at least 5 of 7 correct, with **Q1 (file round-trip)** and **Q7 (class with a method that saves
itself)** among them — those are the load-bearing Files and Objects skills. Key each question to its
concept(s) above. Full marks require the exact returned values for the fixed inputs. Partial credit: award a
class whose `__init__`/attributes are right but a method is wrong at half; award a save/load pair that writes
correctly but mis-parses on load at half (note the `int(line.strip())` fix).

## Differentiation

- Strugglers: prioritize Q1–Q2 and Q4–Q5 — the round-trip, a summary, a class, and a method; treat Q3/Q6/Q7
  as reach.
- Fast finishers: after Q7, ask them to add a `load` function that rebuilds the labeled rectangle from its
  saved file and confirms the round-trip.

## Value plan (sample inputs)

- Q1 `save_scores([14,27,31],"q1_scores.txt")`→"q1_scores.txt"; `load_scores(...)`→[14,27,31].
- Q2 `score_summary("q2_scores.txt")` over `[12,19,7,19]`→[57,19,2] (`[total, highest, strong_count]`; two
  scores are ≥ 15). Q3 `find_team(...,"Otter")`→"Found Otter";
  `"Lynx"`→"No team named Lynx".
- Q4 `Point(6,2)` and `Point(-3,8)` — read `.x`/`.y`; `first.x = 10` leaves `second.x` at -3 (identity).
  Q5 `poster.area()`→24, `poster.describe()`→"8 by 3 has area 24" (`Rectangle(8,3)`).
- Q6 `Counter(12).award_band()`→"gold", `Counter(7)`→"silver", `Counter(2)`→"bronze"; `Counter(12).reached_goal()`→True, `Counter(7)`→False.
- Q7 `sign.short_code()`→"NW" (`code` "NW-17"); `sign.save("q7_rectangle.txt")` writes `"NW-17\n9\n4\n"` (save round-trip).
