# Teacher Notes — Unit 12: Files

## Goals

Students leave able to save data to a text file and read it back: `with open(path, "w") as f: f.write(...)`,
`with open(path, "r") as f: f.read()`, loop lines with `for line in f:` and convert with `int(line.strip())`,
and understand why the `with` statement closes the file for them.
Success looks like: every student writes a `save`/`load` pair that round-trips a list of numbers, and a
function that loads numbers from a file and reports a statistic.
Function form throughout; every file drill is SELF-CONTAINED (it writes the file before reading it), so it
runs the same way every time. Scratch `.txt` files are runtime-only and git-ignored — never commit them.

## Pacing

Budget: three lessons of 60–90 minutes. Hook: save a list of arcade scores, then load them back.

- **Lesson 1 — Save Scores, Then Load Them Back (`file-write`, `file-read`, `with-statement`).**
  `with open(path, "w") as f: f.write(f"{x}\n")`; read the whole file with `with open(path, "r") as f:
  f.read()`. **Motivate `with` with a contrast cell:** `f = open(path); f.write(...); f.close()` — "`with`
  does the `close()` for you, even if you forget or the program crashes."
- **Lesson 2 — Turn Saved Lines into Score Statistics.** `for line in f:` + `int(line.strip())` to load
  numbers; total (`running-total`/`accumulator`), count-by-condition, `min`/`max`/`sum`/`len`, the best
  (`find-extreme`). Seeded functions.
- **Lesson 3 — Save Records and Search a Roster.** Save/load records (one field per line); **transform each
  line** into a cleaned/typed value with an `append` loop; a **linear-search** written as `for line in f: if
  line.strip() == target: return …` (first match or a "not found" message).

**60-minute cut:** Lesson 1 = write + whole-file `read()`; the `for line in f` + `int(line.strip())` loop
opens Lesson 2 (the stats need it anyway).

## Exercises — core vs. extra vs. challenge

Core (1–7): Save/Read Arcade Scores (`score_text_round_trip`), Rebuild the Number List
(`score_list_round_trip`), Total & Count Saved Tickets, Four-Number Summary (`saved_score_summary`), Find the
Saved High Score by Scanning (`highest_saved_score`, find-extreme), Load a Typed Player Record
(transform-each), Search a Saved Roster (`linear-search`).
Challenges (8–9, `stretch`): Prove a Fresh Save Replaces the Old One (overwrite semantics); Find Two
Statistics in One Pass.
Every file drill writes its own per-exercise scratch file (`ex1_scores.txt`, …) before reading — the files
are git-ignored.

## Common mistakes

- Forgetting the file must be WRITTEN before it is read — every drill sets up its own file first.
- Leaving `"\n"` off each written line, so all values run together on one line.
- Forgetting `int(line.strip())` — a line read from a file is a STRING with a trailing newline, not a number.
- Expecting the file to close itself without `with`; or reopening in `"w"` mode (which erases the file) when
  you meant to read.
- Reading the whole file with `.read()` when you need to process line by line (use `for line in f:`).

## Discussion prompts

- What does `with` do at the end of the block, and why does that matter?
- A line read from a file is `"70\n"`. What two steps turn it into the number 70?
- Opening in `"w"` mode erases the file first — when is that what you want, and when is it a bug?
- How is scanning a file for a matching line like the `linear-search` you wrote over a string in Unit 09?

## Differentiation

- Strugglers: Core 1–3 (round-trip a list, total/count); give the `save` function and have them write `load`.
- Fast finishers: the two Challenges (overwrite proof, two-stats-one-pass), then add a "records that don't
  exist" branch to the roster search.
- Middle tier: rewrite the whole-file `.read()` load as a `for line in f:` loop and confirm the same numbers.

## Value plan (sample inputs)

Each exercise writes a distinct per-exercise scratch file and uses distinct data; solutions assert the
round-trip.
- Ex1 `score_text_round_trip`: `([45,70,55],"ex1_scores.txt")`→`"45\n70\n55\n"`; `([120,95],…)`→`"120\n95\n"`.
- Ex2 `score_list_round_trip`: `([18,27,36],…)`→`[18,27,36]`; `([5,105],…)`→`[5,105]`.
- Ex3 total & count saved tickets; Ex4 `saved_score_summary([8,15,11],…)`→`[8,15,34,3]` (min,max,sum,count).
- Ex5 `highest_saved_score([44,81,63],…)`→`81`. Ex6 typed record load; Ex7 roster search (found / not found).
- Ex8 (stretch) overwrite proof; Ex9 (stretch) two statistics in one pass.
