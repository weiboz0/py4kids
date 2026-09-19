# Teacher Notes — Unit 07: High-Score Hall of Fame

## Goals

Students leave able to use a LIST as a container that holds many values at once — build one
with `[...]`, read items by position (`scores[0]`, `scores[-1]`), grow it with `.append()`,
walk it with a `for` loop, measure it with `len`/`max`/`min`, and rank it with `.sort()` — and
to assemble these into a working arcade leaderboard that crowns a champion.
This is the first unit where one variable holds a whole collection, not a single value.
Success looks like: every student builds a scores list, sorts it top-first, and prints a
numbered "Place N: score" hall of fame.
Exercises 1–6 form the in-class path; the labelled More Practice Exercises 7–9 are homework after
Lesson 3; the **Algorithm Extension** (Exercises 10–22 — the seven pattern reps plus six loop drills) is
optional enrichment, with only the find-extreme and filter naming Spotlights read in class (each Spotlight
is now followed by a short worked-example ladder — code rungs + Notices → a put-it-together — that is part
of the same time-permitting/homework enrichment, not required in-class); and the
Challenges remain optional stretch work.

## Pacing

Budget: three lessons of 60–90 minutes. Each concept is a short **worked-example ladder** (minimal → one step up → real board use, with a *Notice* per rung); the lesson-count is advisory. Closure note: this unit's built-ins are exactly `len`/`max`/`min` (an accumulator gives the total, NOT `sum`), and sorting uses `.sort()` / `.sort(reverse=True)`; builtins are taught in Lesson 1, before sorting in Lesson 2.

- **Lesson 1 — lists hold many scores (list-literal, list-index, list-append, list-loop, builtin-functions) (60–90 min).**
  Open on the hook: a messy scrap of paper full of scores — how would a program keep them?
  15 min: the list ladder (`[]` → a few items → the scores list) and the index ladder (`[0]` → another → `[-1]`).
  15 min: the append ladder (append one → again → append in a loop) and the list-loop ladder (print each → accumulate a total). Call a `range(len(...))` walk "entry #1, #2…" (POSITION), NOT "place"/"rank" — ranking comes after sorting. Naming them "places" before sorting is the trap.
  Immediately after the append ladder, teach the **Keep the ones that pass
  (filter)** spotlight: a person can glance through a pile and keep the qualifying cards, but a
  program must check one score at a time and append each passing score to a new list. Do a 2-minute
  unplugged trace: sort a pile of score cards, keeping only the cards that pass the threshold in a
  new pile. The **filter** pattern's home is Exercise 16 in the closing Algorithm Extension — name it in class from this Spotlight, and run Exercise 16 as time permits.
  20 min: the builtins ladder (`len` → `max` → `min`) plus `average = total / len(scores)` (a decimal — a float).
  Immediately after the indexed list scan and `max` beat, teach the **Find the best (max / argmax)**
  spotlight: `max` keeps only the number, while an explicit scan can keep both `best_score` and
  `best_name`. Do a 2-minute unplugged trace: hold up height cards one at a time and have students
  keep the tallest seen so far **and whose card it is**. The **find-extreme** pattern's home is
  Exercise 15 in the closing Algorithm Extension — name it in class from this Spotlight while the scan is
  fresh, and run Exercise 15 as time permits.
  The running-total reuse (now Exercise 10 in the Algorithm Extension) rides this list-loop accumulate
  beat — run it as time permits too. Reserve Exercise 2 for Lesson 2
  because it sorts, and reserve Exercises 1 and 3 for Lesson 3 because they use membership and
  deliberate traceback reading.
  60-MINUTE CUT: teach ladder rungs 1–2; leave the last rung as a "try it".
- **Lesson 2 — rank the hall and crown a champion (list-sort; helpers) (60–90 min).**
  Open on the thread: yesterday we LISTED scores; today we RANK them.
  20 min: the sort ladder (`.sort()` low→high → `.sort(reverse=True)` top-first → print with a `board_line` helper). Emphasize `.sort()` changes the list IN PLACE and returns `None` (contrast Unit 06's string rebuild).
  20 min: `add_score` appends then re-sorts so the hall stays ranked.
  After the sort and helper ladders, use Exercises 2, 4, and 5 in class. Exercise 4's
  interactive cell stays `no-exec`; students run it themselves and supply a score.
- **Lesson 3 — polish the hall (tiers, membership, a doubling threshold) (60–90 min).**
  20 min: a gold/silver/bronze tier with `if`/`elif`/`else`; guard a duplicate with `if score in scores`.
  15 min: a `while` loop doubling a qualifying threshold; then the deliberate `IndexError` (`scores[len(scores)]`) — read the traceback together.
  After tiers, membership, `while`, and the deliberate traceback have all been taught, use
  Exercises 1, 3, and 6 in class. Exercise 3's first blank cell is `no-exec`: students
  deliberately produce the `IndexError` only with the teacher, read its final line, and then
  write the safe `scores[-1]` fix in the following cell. Exercise 6 is also interactive and
  remains `no-exec`.
  Assign the labelled More Practice Exercises 7–9 as homework only after Lesson 3: ascending
  sort and input report (7), `.sort()` returning `None` (8), and a second list-processing `while`
  loop (9). The count-by-condition, transform-each, sentinel-loop, and linear-search reappearances
  now live in the Algorithm Extension (Exercises 11, 12, 13, 14) — see below; the naming beats ride
  the lessons but their exercises run as time permits. Thus no exercise is allocated before its concepts
  have appeared in the lesson sequence.

## Common mistakes

- Calling `.sort()` and expecting it to hand back a sorted list: `best = scores.sort()` sets
  `best` to `None`. `.sort()` rearranges the list in place; just use `scores` afterward.
- Forgetting `reverse=True`, so the "top" of the board is actually the lowest score.
- Off-the-end indexing: `scores[len(scores)]` is an IndexError — valid positions run `0` to
  `len(scores) - 1`. This is the planned Lesson-3 bug; read the traceback together.
  The expected final line is `IndexError: list index out of range`.
- Off-by-one on the numbered board: humans count from 1, so print `position + 1`, not
  `position`.
- Adding a score to a ranked board and forgetting to re-sort, so the new score sits at the
  bottom no matter how big it is — `.append()` always adds to the END.
- Updating `best_score` but forgetting `best_name`, so the winning number and player no longer
  belong together. In Exercise 15, update both from the same position.
- Seeding a minimum (or maximum) at `0` in the scan drills — `rookie_score = 0` makes 0 always
  "win" and returns the wrong player. Seed from the FIRST score/name instead (Exercises 15, 17, 18).
- Mixing champion names into the score list. Exercise 12 keeps a cleaned name list separate so
  every list has one clear job.
- Appending every score instead of only scores that pass the threshold. In Exercise 16, the
  `.append()` belongs inside the qualifying `if`, and the original score list stays unchanged.

## Discussion prompts

- A list lets one name hold many values. Where else in a game would a list help (lives,
  inventory, level names)?
- Why does `.sort()` change the list instead of giving back a new one? When is changing-in-place
  handy, and when is it surprising?
- Which parts of the hall belong in the score list, and which information should stay in its
  own list for now?

## Differentiation

- Strugglers: give the leaderboard `scores` list pre-built and have them only `.append()` and
  `.sort(reverse=True)` it; reading `max`/`min` off a ready list is a satisfying win on its own.
- Fast finishers: the Challenge exercises — sort-then-top-three and merge-two-boards (append the
  second list's scores in one loop, then a single re-sort). Extending the tier ladder with a
  fourth "legend" tier is a good no-new-concepts stretch.
- Middle tier: the add-my-score exercise (append + re-sort + return) before the Challenges.

## Exercise split and count note

- **In class:** Exercises 1–6. The find-extreme and filter naming Spotlights are read in Lesson 1
  (immediately after the `max` contrast and the append ladder), but their home exercises now live in the
  Algorithm Extension.
- **Homework / More Practice:** Exercises 7–9, assigned only after Lesson 3.
- **Algorithm Extension (enrichment):** Exercises 10–22 — the seven relocated pattern exercises
  (running-total, count-by-condition, transform-each, sentinel-loop, linear-search, find-extreme,
  filter-into-list) plus six new unmarked loop drills; routed as time-permitting / homework /
  differentiation (see the Algorithm Extension section below).
- **Optional stretch:** Challenge 1 and Challenge 2.

The deliberate traceback in Exercise 3 is the unit's one genuine `error-messages` authoring
rep. It has a justified peripheral count exemption: repeatedly staging raising list accesses
would be artificial, while traceback reading is practiced again across later units. The raising
cell is tagged `no-exec`, and students fix it in a separate safe cell.

## Algorithm Extension (enrichment)

The unit's algorithm track sits in a labelled **`## Algorithm Extension`** section at the end of the
notebook (design 002 v8). It gathers the seven pattern reps — running-total (Ex 10), count-by-condition
(Ex 11), transform-each (Ex 12), sentinel-loop (Ex 13), linear-search (Ex 14), the **find-extreme** home
(Ex 15, champion by name), and the **filter-into-list** home (Ex 16, keep only the qualifying scores) —
then six new **unmarked** list drills (Ex 17–22). Only the find-extreme and filter naming Spotlights are
read in class (Lesson 1); every exercise here (Ex 10–22) is routed as time-permitting / homework /
differentiation and never gates the core board build.

Every drill loops over a real list (`len`/`max`/`min`/`.append()` available; accumulate totals with a
loop — no `sum`):

- **Ex 17** rookie by name (argmin, keep `rookie_name`+`rookie_score` → "Zoe"/650), **Ex 18** best & worst
  in one pass (1050 / 720), **Ex 19** average of the passers with a zero-count guard (3 passers → 900.0),
  **Ex 20** "what place would I be?" (count scores above mine, rank = count + 1 → place 3).
- **Ex 21 & Ex 22** are the **same list ([300, 450, 275, 600]), opposite-boundary** pair ÷ budget 1000:
  Ex 21 *checks before adding* (2 fit, total 750); Ex 22 *adds then checks* (3 added, total 1025, tipping
  wait 275). Run them back-to-back so students feel where the check sits relative to the add.

These are extra reps of patterns students have met; being the broadest-core unit, they are routed mostly
to More-Practice/homework so the in-class core stays the board build.
