# Teacher Notes — Unit 09: Save Point

## Goals

Students leave able to make a program REMEMBER things between runs by using files: WRITE data with
`with open(name, "w") as f: f.write(...)`, READ it back with `with open(name) as f:` (either
`f.read()` for the whole file or `for line in f:` line-by-line), and rebuild game state — a list of
high scores, a few settings — from what was saved. This is the first unit where data outlives the
program. Success looks like: every student saves scores to a file, closes and re-opens the
notebook, and loads the same scores back.

## Pacing

Budget: two lessons of 60–90 minutes.

- **Lesson 1 — save to a file (file-write, with-statement) (60–90 min).**
  Open on the hook: a game that forgets everything when you close it is no fun.
  15 min: `with open("savegame.txt", "w") as f:` and `f.write(...)`; explain `with` opens the file
  and closes it automatically when the block ends.
  15 min: the `"\n"` newline — it is the invisible "end of line" character; write one score per line
  with `for score in scores: f.write(str(score) + "\n")`. Without `"\n"`, every value runs together
  on one line. `str(...)` is needed because you can only write TEXT to a file, not a raw number.
  20 min: save a few settings as TEXT to `settings.txt` — the player's name, volume, difficulty —
  one per line.
  60-MINUTE CUT: drop the settings file; saving the score list is the core.
- **Lesson 2 — load from a file (file-read) (60–90 min).**
  Open on the thread: yesterday we saved; today we load it back.
  15 min: read the whole file with `f.read()` and print it.
  20 min: rebuild the score list line-by-line — `loaded = []` then `for line in f:
  loaded.append(int(line.strip()))`. `.strip()` removes the trailing newline; `int(...)` turns the
  text back into a number (this is why `savegame.txt` holds ONLY scores — every line must be a
  number). A `load_scores(filename)` helper returns the list.
  15 min: read `settings.txt` as TEXT and search it with membership — `if "Ada" in info: ...`. We do
  NOT `int()` the settings file, because it holds words, not just numbers.
  10 min: the deliberate bug — open a file that was never saved → `FileNotFoundError`. Read the
  traceback together; the fix is to SAVE before you LOAD.
  60-MINUTE CUT: skip the settings read; the score round-trip is the non-negotiable core.

Two separate files on purpose: `savegame.txt` is numbers only (so `int()` never chokes), and
`settings.txt` is words (read by membership, never `int()`-parsed). Mixing a name into the scores
file would crash the loader — a good thing to name explicitly.

Practices reappearance: `for-loop` walks both a list (`for score in scores`) and a file
(`for line in f`); `list-literal`/`list-append`/`list-loop` build and rebuild the score list;
`type-conversion` (`str` to save, `int` to load) and `string-concat` (`+ "\n"`) shape each line;
`string-methods` (`.strip()`) trims the newline; `dict-literal`/`dict-access` supply the settings;
`in-operator`/`if-statement` search the settings text; `builtin-functions` (`len`, `max`) measure
the loaded list; `print`/`f-string`/`variable`/`string-literal`/`int-type` throughout;
`error-messages` is the FileNotFoundError beat; `input` is practiced only in the save-my-score
exercise PROMPT (the executable cells are input-free so the notebooks run in class). All return in
unit 10 and the capstone.

## Common mistakes

- Forgetting `"\n"`, so every value lands on one line and the loader reads one giant number.
- Forgetting `.strip()` before `int()`, so `int("850\n")` — actually Python tolerates the newline
  here, but a stray space would break it; strip to be safe and to teach the habit.
- Using append mode `"a"` instead of `"w"`, so the file GROWS every time you run — always re-save
  the whole list with `"w"`.
- Reading a file that was never saved → `FileNotFoundError`; save before you load (the Lesson-2
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
- Fast finishers: the Challenge exercises — highest-saved-score (load then `max`) and add-a-new-high
  (load, append, re-save). Saving TWO score files and loading whichever the player picks is a good
  no-new-concepts extension.
- Middle tier: the save-then-load round-trip via the helper functions before the Challenges.
