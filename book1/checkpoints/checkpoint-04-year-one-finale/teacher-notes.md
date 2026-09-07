# Teacher Notes — Checkpoint 04: Year One Finale

## Goals

This checkpoint confirms that students can bring Book 1's two biggest skills together: OBJECTS and FILES.
Students define a class, initialize attributes, update object state through a method, write and reload a simple save file, sort loaded data, walk a dictionary, and guard a missing-key lookup.
Nothing new is introduced; every question uses only skills taught in Book 1 Units 01–10.

## Pacing

Budget: 35–40 minutes (the hardest checkpoint because it combines files and OOP).
Q1–Q2 assess object construction and behavior, Q3–Q5 form a save-load-rank sequence, and Q6–Q8 assess dictionary iteration and safe membership checks.
RUN IN ORDER: Q3 writes `finale.txt` before Q4 reads it.
Running Q4 first raises `FileNotFoundError`.
Budget the most time for Q2 and the Q3–Q5 sequence.

## Common mistakes

- Forgetting `self` in the constructor, method parameters, or attribute assignments.
- Expecting `.sort()` to return the sorted list even though it rearranges the list in place and returns `None`.
- Forgetting `.strip()` before converting a file line with `int()`.
- Treating a `KeyError` as unavoidable instead of using a membership guard.
- Typing an attribute name differently when setting it and when reading it.
- Running Q4 or Q5 out of order before the earlier cell has created the needed file or list.

## Discussion prompts

- What information belongs inside a hero object, and what information belongs in a save file?
- Why does a method need `self` to change one particular object's state?
- What does the final line of a traceback tell you that the earlier lines do not?

## Differentiation

- A struggling student can complete Q1, Q3, Q6, and Q7 first, then return to the method and file-loading questions.
- For Q2, prompt the student to trace the health attribute before and after the method call without supplying code.
- For Q3–Q4, show a three-line sample text file and ask what one loop pass sees, without revealing the implementation.
- A fast finisher can explain aloud why a membership guard prevents the Q8 crash, but should not add tools beyond Units 01–10.

## Grading

40 points total, 5 points per question.
Full credit requires correct, runnable code that follows the requested Book 1 approach.
Partial credit is available for a sound structure with one local syntax, naming, conversion, or ordering mistake.
Do not award credit for replacing the assessed approach with tools outside Units 01–10, including `max`, `len`, `.split()`, or `.get()`.

- **Q1 — define a class (5):** constructor and `self` use (2), both required attributes (1), object creation (1), and both requested prints (1).
- **Q2 — add a method (5):** complete stand-alone class (1), correct method signature and `self` use (1), state update (1), returned new state (1), and call plus print (1).
- **Q3 — write a save file (5):** given list (1), write-mode `with` block (2), loop over scores (1), and one integer per line (1).
- **Q4 — load the save file (5):** empty destination list (1), read-mode `with` block (1), direct file loop (1), cleaned integer conversion and append (1), and requested print (1).
- **Q5 — rank the scores (5):** in-place descending sort (3) and top item read by index and printed (2); partial credit for a correct ascending sort followed by an incorrect top-item choice.
- **Q6 — walk an inventory (5):** given dictionary (1), `.items()` pair loop (3), and both parts of each pair printed (1).
- **Q7 — check the inventory (5):** sword membership result printed (2), shield membership branch (2), and safe present/missing behavior (1).
- **Q8 — fix the bug (5):** identifies the traceback's final line as the clue (1), uses a membership guard (2), and provides safe present and missing branches (2).

A student scoring at least 28/40 (70%) is solid on the Book 1 finale skills.
Below that, revisit object state in Q1–Q2 and the write-then-read sequence in Q3–Q4 first.
