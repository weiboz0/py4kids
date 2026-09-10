# Teacher Notes — Unit 09: Save Point

## Goals

Students leave able to make a program REMEMBER things between runs by using files: WRITE data with
`with open(name, "w") as f: f.write(...)`, READ it back with `with open(name) as f:` (either
`f.read()` for the whole file or `for line in f:` line-by-line), and rebuild game state — a list of
high scores, a few settings — from what was saved. This is the first unit where data outlives the
program. Success looks like: every student saves scores to a file, closes and re-opens the
notebook, and loads the same scores back.

## Pacing

Budget: three lessons of 60–90 minutes.
Each concept is a short **worked-example ladder** (minimal → one step up → real save system, with a *Notice* per rung); the lesson-count is advisory.
`with-statement` is co-taught (it wraps every file operation); the only string method is `.strip()`.
The write rungs must run before the read rungs (the read rungs load the file the write rungs saved).
Exercises 1–9 form the in-class path; the labelled More Practice Exercises 10–12 are homework, and Exercises 13–14 remain optional Challenges.

- **Lesson 1 — save to a file (file-write, with-statement) (60–90 min).**
  Open on the hook: a game that forgets everything when you close it is no fun.
  25 min: the file-write ladder (`with open("savegame.txt", "w") as f: f.write(one line)` → a loop writing several scores → a mixed `settings.txt`).
  Explain `with` opens the file and closes it automatically; `\n` is the invisible end-of-line; `str(...)` because files hold TEXT.
  In class, complete Exercises 1 and 5.
  60-MINUTE CUT: complete Exercise 1; begin Exercise 5 next lesson.
- **Lesson 2 — read a file back (file-read) (60–90 min).**
  Open on the thread: yesterday we saved; today we load.
  25 min: the file-read ladder (`f.read()` whole file → `for line in f:` print each → `.strip()` a clean line → rebuild a list with `int()` + `.append()`).
  Stress that `savegame.txt` holds ONLY scores so every line turns back into an integer.
  In class, complete Exercises 2–4, including the required loaded-data f-string in Exercise 4.
- **Lesson 3 — package the loader (60–90 min).**
  **Put it together:** first read `settings.txt` as text and run both paths of the name search in Exercise 6, then wrap the saver and loader in the helper functions from Exercise 7.
  Complete the fixed-score branch in Exercise 8 and finish with the `FileNotFoundError` study in Exercise 9: save first, then load.
  60-MINUTE CUT: Exercises 6–7 are the core; guide Exercises 8–9 together as the final short closing pair.

Homework More Practice: Exercise 10 proves that a second `"w"` save replaces instead of duplicates, Exercise 11 repeats dictionary save/load through functions, and Exercise 12 repeats a parameterized score loader.
`error-messages` has one in-class study repetition rather than three because deliberately staging multiple failing loads would be artificial and would not add useful file practice.

## Common mistakes

- Forgetting `"\n"`, so every value lands on one line and the loader reads one giant number.
- Forgetting `.strip()` before `int()`, so `int("850\n")` — actually Python tolerates the newline
  here, but a stray space would break it; strip to be safe and to teach the habit.
- Using append mode `"a"` instead of `"w"`, so the file GROWS every time you run — always re-save
  the whole list with `"w"`; Exercise 10 makes the unchanged first and second file contents visible with `print(...)`.
- Reading a file that was never saved → `FileNotFoundError`; save before you load (the Lesson-3
  bug beat).
- `int()`-parsing the settings file (which holds words) → `ValueError`; read settings as TEXT and
  search it with `in`, never `int()`.
- Forgetting `with`, leaving the file open — always use `with open(...) as f:`.

## Discussion prompts

- Where does a saved file live after the program ends? Why is that different from a variable?
- Why do we keep scores and settings in separate files instead of one? (Numbers vs words.)
- What could go wrong if two players share one save file?

## Differentiation

- Strugglers: give the write code and have them only do the READ half (open, loop, print) — seeing
  their own saved scores load back is a satisfying win.
- Fast finishers: Exercises 13–14 — highest-saved-score (load then `max`) and add-a-new-high
  (load, append, re-save). Saving two score files and loading whichever the player picks is a good
  no-new-concepts extension.
- Middle tier: Exercises 10–12 provide extra save/load repetitions before the Challenges.
