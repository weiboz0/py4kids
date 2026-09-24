# Teacher Notes — Unit 12: Files

## Goals

Students leave able to save data to a text file and read it back: `with open(path, "w") as f: f.write(...)`,
`with open(path, "r") as f: f.read()`, add to the end of a file with mode `"a"`, loop lines with
`for line in f:` and convert with `int(line.strip())`, split comma-separated records with `line.split(",")`,
and understand why the `with` statement closes the file for them.
Success looks like: every student writes a `save`/`load` pair that round-trips a list of numbers, and a
function that loads numbers from a file and reports a statistic.
Function form throughout; every file drill is SELF-CONTAINED (it writes the file before reading it), so it
runs the same way every time. Scratch `.txt` files are runtime-only and git-ignored — never commit them.

## Pacing

Budget: three lessons of 60–90 minutes. Hook: save a list of arcade scores, then load them back.

- **Lesson 1 — Save Scores, Then Load Them Back (`file-write`, `file-read`, `with-statement`).**
  The old dense first cell is now four rungs: write ONE line (`f.write("840\n")`), read it back with
  `f.read()`, write several scores in a loop, then put the save and load steps in functions. **Motivate `with` with a contrast cell:** `f = open(path, "w"); f.write(...); f.close()` — "`with`
  does the `close()` for you, even if you forget or the program crashes." (Open in `"w"` mode in the contrast,
  or the `f.write(...)` fails on a read-only handle.) Then **add to the end with `"a"`**: `"w"` starts a fresh
  file, `"a"` keeps what is there (`575` then `905`). A `no-exec` cell reads `n` scores and saves them.
- **Lesson 2 — Turn Saved Lines into Score Statistics.** `for line in f:` + `int(line.strip())` to load
  numbers; then the old four-function cell as four rungs, one idea each: a running total (`2345`), a count
  that reaches a target (`2`), the best so far (`735`), and the built-in statistics
  (`[420, 735, 2345, 4]`). A `no-exec` cell reads a target and counts the saved scores that reach it.
- **Lesson 3 — Save Records and Search a Roster.** Save/load records (one field per line); **transform each
  line** into a cleaned/typed value with an `append` loop; a **linear-search** written as `for line in f: if
  line.strip() == target: return …` (first match or a "not found" message). New rungs before the search:
  one record per line with fields split by commas (`"Mina,4,860".split(",")`), `int(parts[2])`, and a walk
  over a saved file of comma records. A `no-exec` cell reads a name and searches a typed roster.

**60-minute cut:** Lesson 1 = write + whole-file `read()`; the `for line in f` + `int(line.strip())` loop
opens Lesson 2 (the stats need it anyway).

## Exercises — core vs. More Practice vs. challenge

28 exercises, all in the function form; every file drill writes its own per-exercise scratch file before
reading (the files are git-ignored).

- **Core (1–10):** Save a Labeled Score Report, Rebuild the Number List, Total & Count Saved Tickets,
  Four-Number Summary, Find the Saved High Score by Scanning, Summarize a Saved Player Record, Search a Saved
  Roster, plus **Append a Late Score** (8: `[62, 48, 91]`), **Save a Text Map** (9) and **Best Team from
  Records** (10: `Teo`). Exercises 8–10 require a purpose comment.
- **More Practice (11–24)**, grouped by genre:
  - *Text files:* Long Words in a File (4), Longest Saved Line (`fir hollow`), Numbered Lines, Shout Copy,
    Keep the To-Dos.
  - *Reports & statistics:* Average from a File (`Average: 82.0`), Grade Report (`A: 2` …), Chart from a File.
  - *Searching:* First Long Word (`meadow`), Line of a Name (3 / -1).
  - *Persistence:* Event Log (`"w"` then `"a"`).
  - *Debug & predict:* Fix the Missing File (`FileNotFoundError`), Fix the Write Mode
    (`io.UnsupportedOperation: not writable`), Predict the Overwrite (`2` / `3`).
- **Challenges (25–28, `stretch`):** Prove a Fresh Save Replaces the Old One, Find Two Statistics in One
  Pass, Merge Two Score Files, High-Score Table.

**Real versions.** Every exercise except the two Fix exercises and the predict has a real program: it reads
the data from stdin (`n` then `n` lines, or one line of values), saves it to a file, reloads it, and prints.

## Common mistakes

- Forgetting the file must be WRITTEN before it is read — every drill sets up its own file first.
- Leaving `"\n"` off each written line, so all values run together on one line.
- Forgetting `int(line.strip())` — a line read from a file is a STRING with a trailing newline, not a number.
- Expecting the file to close itself without `with`; or reopening in `"w"` mode (which erases the file) when
  you meant to read.
- Reading the whole file with `.read()` when you need to process line by line (use `for line in f:`).
- Mixing up `"w"` and `"a"`: `"w"` erases, `"a"` adds to the end — Event Log needs both, in that order.
- Opening a file in `"r"` mode and calling `write` (`io.UnsupportedOperation: not writable`), or reading a
  file that was never written (`FileNotFoundError`).
- `line.split(",")` keeps the newline on the last field — `strip()` the line first.

## Discussion prompts

- What does `with` do at the end of the block, and why does that matter?
- A line read from a file is `"70\n"`. What two steps turn it into the number 70?
- Opening in `"w"` mode erases the file first — when is that what you want, and when is it a bug?
- How is scanning a file for a matching line like the `linear-search` you wrote over a string in Unit 09?

## Differentiation

- Strugglers: Core 1–3 (round-trip a list, total/count); give the `save` function and have them write `load`.
- Fast finishers: the report and search More Practice, then the Challenges (the High-Score Table is the
  capstone); then add a "records that don't
  exist" branch to the roster search.
- Middle tier: rewrite the whole-file `.read()` load as a `for line in f:` loop and confirm the same numbers.

## Value plan (sample inputs)

Each exercise writes a distinct per-exercise scratch file and uses distinct data; solutions assert the
round-trip.
- Ex1 `score_text_with_header([45,70,55],"ex1_scores.txt")`→`"ARCADE SCORES\n45\n70\n55\n"`; `([120,95],…)`→`"ARCADE SCORES\n120\n95\n"`.
- Ex2 `score_list_round_trip([18,27,36],"ex2_score_list.txt")`→`[18,27,36]`; `([5,105],…)`→`[5,105]`.
- Ex3 `saved_ticket_report([20,35,15],25,"ex3_tickets.txt")`→`[70,1]`; `([9,12,7],20,…)`→`[28,0]` (`[total, count ≥ threshold]`).
- Ex4 `saved_score_summary([8,15,11],"ex4_summary.txt")`→`[8,15,34,3]` (min,max,sum,count); `([50,20],…)`→`[20,50,70,2]`.
- Ex5 `highest_saved_score([44,81,63],"ex5_high_score.txt")`→`81`; `([205,199,201],…)`→`205`.
- Ex6 `player_record_summary("Lina",3,480,"ex6_typed_record.txt")`→`"Lina: level 3, 480 points"`; `("Zoe",1,75,…)`→`"Zoe: level 1, 75 points"`.
- Ex7 `save_and_find_player(["Inez","Kai","Noor"],"Inez","ex7_roster.txt")`→`"Found Inez."`; `…,"Pia",…`→`"Pia was not found."`.
- Ex25 (stretch) `replace_and_load_scores([10,20],[30,40],"ex25_replace.txt")`→`[30,40]` (overwrite proof).
- Ex26 (stretch) `saved_total_and_best([12,30,18],"ex26_combined_stats.txt")`→`[60,30]` (`[total, best]`, one pass).
- New exercises 8–28: fixtures as in the exercise statements (plan 084's tables), grep-distinct from shipped
  Book 1b content.

## More Practice ideas (design 006 D9 genres)

- **Files & persistence:** a to-do list that appends new items and prints them numbered.
- **Data report:** from a saved file of `name,score` lines, print the names above the average.
- **ASCII art:** save a triangle picture to a file, then load it and print it upside down.
