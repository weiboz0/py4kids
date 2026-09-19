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
Exercises 1–8 form the in-class path; the labelled More Practice Exercises 9–11 are homework; the
**Algorithm Extension** (Exercises 12–23) is optional enrichment; and Exercises 24–25 remain optional Challenges.

- **Lesson 1 — save to a file (file-write, with-statement) (60–90 min).**
  Open on the hook: a game that forgets everything when you close it is no fun.
  25 min: the file-write ladder (`with open("savegame.txt", "w") as f: f.write(one line)` → a loop writing several scores → a mixed `settings.txt`).
  Explain `with` opens the file and closes it automatically; `\n` is the invisible end-of-line; `str(...)` because files hold TEXT.
  In class, complete Exercises 1 and 4.
  60-MINUTE CUT: complete Exercise 1; begin Exercise 4 next lesson.
- **Lesson 2 — read a file back (file-read) (60–90 min).**
  Open on the thread: yesterday we saved; today we load.
  25 min: the file-read ladder (`f.read()` whole file → `for line in f:` print each → `.strip()` a clean line → rebuild a list with `int()` + `.append()`).
  Stress that `savegame.txt` holds ONLY scores so every line turns back into an integer.
  In class, complete Exercises 2–3, including the required loaded-data f-string in Exercise 3. The load-into-a-list transform-each rep is now Exercise 12 in the Algorithm Extension.
- **Lesson 3 — package the loader (60–90 min).**
  **Put it together:** first read `settings.txt` as text and run both paths of the name search in Exercise 5, then wrap the saver and loader in the helper functions from Exercise 6.
  Complete the fixed-score branch in Exercise 7 and finish with the `FileNotFoundError` study in Exercise 8: save first, then load.
  60-MINUTE CUT: Exercises 5–6 are the core; guide Exercises 7–8 together as the final short closing pair.

Homework More Practice: Exercise 9 proves that a second `"w"` save replaces instead of duplicates, Exercise 10 repeats dictionary save/load through functions, and Exercise 11 repeats a parameterized score loader. The transform-each, running-total, linear-search, find-extreme, and filter reappearances now live in the **Algorithm Extension** (Exercises 12–16), run as time permits: Exercise 13 retrieves running-total over file lines and Exercise 14 retrieves **linear-search** by scanning saved names one line at a time, stopping when the target is found.
Exercise 15 retrieves the **find-extreme** best-so-far scan directly over stripped, converted file
lines; students keep only `best_score`, build no list, and do not use `max()`.
Exercise 16 retrieves **filter-into-list** after the Lesson-2 line loader: students scan saved score
lines, convert each line, test it against a threshold, and append only passing scores to a new list.
Its variation axis is the file-line source rather than an in-memory list.
`error-messages` has one in-class student-authored code repetition rather than three because Exercise 8 turns its diagnosed `FileNotFoundError` into a real save-before-load repair, while deliberately staging more failing loads would be artificial and would not add useful file practice.
The exercises notebook is designed to run top-to-bottom once; Exercise 10 intentionally replaces Ada's `settings.txt` profile with Mina's, so rerunning Exercise 5 afterward changes its result.

## Algorithm Extension (enrichment)

The unit's algorithm track sits in a labelled **`## Algorithm Extension`** section at the end of the
notebook (design 002 v8). It gathers the five pattern reps — transform-each (Ex 12, load lines→ints),
running-total (Ex 13, sum the saves), linear-search (Ex 14, find a name and stop early), find-extreme
(Ex 15, highest by scanning), filter-into-list (Ex 16, load only the high scores) — then seven new
**unmarked** drills (Ex 17–23). Exercises 24–25 remain the optional stretch Challenges. The pattern beats
are named in class; every exercise here (Ex 12–23) is routed as time-permitting / homework /
differentiation.

The five relocated file-reading exercises each **re-save the file they read first** (savegame.txt, or
settings.txt for the linear-search drill) so they run independently of exercise order (the notebook is otherwise stateful). The seven new drills work on an
**inline list** of already-loaded scores (the file-reading skill is exercised by the relocated reps and
the core), keeping each drill self-contained and single-pass:

- **Ex 17** count boss-level saves (≥ 1000 → 2), **Ex 18** average of the saves (2825 ÷ 4 = 706.25),
  **Ex 19** lowest save (argmin, seed from the FIRST score — `0` is safe as a *max* seed for positive scores, e.g. Ex 15, but fatal as a *min* seed, since 0 would always win → 450), **Ex 20** which save holds my score
  (position search + `break` → 2), **Ex 23** first save ≥ target (search + `break` → 725).
- **Ex 21 & Ex 22** are the **same list ([300, 450, 725, 1350]), opposite-boundary** pair ÷ 1000: Ex 21
  *checks before adding* (2 fit, total 750); Ex 22 *adds then checks* (3 added, total 1475, tipping save
  725). Run them back-to-back.

Long-form accumulation (`x = x + …`) throughout — Book 1 does not teach `+=`.

## Common mistakes

- Forgetting `"\n"`, so every value lands on one line and the loader reads one giant number.
- Forgetting `.strip()` before `int()`, so `int("850\n")` — actually Python tolerates the newline
  here, but a stray space would break it; strip to be safe and to teach the habit.
- Using append mode `"a"` instead of `"w"`, so the file GROWS every time you run — always re-save
  the whole list with `"w"`; Exercise 9 makes the unchanged first and second file contents visible with `print(...)`.
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
- Fast finishers: Challenges 24–25 — compare the core explicit scan with a list-building
  `max()` route, then load, append, and re-save a new high. Saving two score files and loading
  whichever the player picks is a good no-new-concepts extension.
- Middle tier: Exercises 9–11 provide extra save/load repetitions before the Challenges.
