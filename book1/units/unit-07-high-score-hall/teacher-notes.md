# Teacher Notes — Unit 07: High-Score Hall of Fame

## Goals

Students leave able to use a LIST as a container that holds many values at once — build one
with `[...]`, read items by position (`scores[0]`, `scores[-1]`), grow it with `.append()`,
walk it with a `for` loop, measure it with `len`/`max`/`min`, and rank it with `.sort()` — and
to assemble these into a working arcade leaderboard that crowns a champion.
This is the first unit where one variable holds a whole collection, not a single value.
Success looks like: every student builds a scores list, sorts it top-first, and prints a
numbered "Place N: score" hall of fame.

## Pacing

Budget: three lessons of 60–90 minutes. Each concept is a short **worked-example ladder** (minimal → one step up → real board use, with a *Notice* per rung); the lesson-count is advisory. Closure note: this unit's built-ins are exactly `len`/`max`/`min` (an accumulator gives the total, NOT `sum`), and sorting is `.sort()` / `.sort(reverse=True)` only (never `sorted()`); builtins are taught in Lesson 1, before sorting in Lesson 2.

- **Lesson 1 — lists hold many scores (list-literal, list-index, list-append, list-loop, builtin-functions) (60–90 min).**
  Open on the hook: a messy scrap of paper full of scores — how would a program keep them?
  15 min: the list ladder (`[]` → a few items → the scores list) and the index ladder (`[0]` → another → `[-1]`).
  15 min: the append ladder (append one → again → append in a loop) and the list-loop ladder (print each → accumulate a total). Call a `range(len(...))` walk "entry #1, #2…" (POSITION), NOT "place"/"rank" — ranking comes after sorting. Naming them "places" before sorting is the trap.
  20 min: the builtins ladder (`len` → `max` → `min`) plus `average = total / len(scores)` (a decimal — a float).
  60-MINUTE CUT: teach ladder rungs 1–2; leave the last rung as a "try it".
- **Lesson 2 — rank the hall and crown a champion (list-sort; helpers) (60–90 min).**
  Open on the thread: yesterday we LISTED scores; today we RANK them.
  20 min: the sort ladder (`.sort()` low→high → `.sort(reverse=True)` top-first → print with a `board_line` helper). Emphasize `.sort()` changes the list IN PLACE and returns `None` (contrast Unit 06's string rebuild).
  20 min: `add_score` appends then re-sorts so the hall stays ranked.
  Rest: ranking exercises.
- **Lesson 3 — polish the hall (tiers, membership, a doubling threshold) (60–90 min).**
  20 min: a gold/silver/bronze tier with `if`/`elif`/`else`; guard a duplicate with `if score in scores`.
  15 min: a `while` loop doubling a qualifying threshold; then the deliberate `IndexError` (`scores[len(scores)]`) — read the traceback together.
  Rest: exercises; play with each other's halls.

## Common mistakes

- Calling `.sort()` and expecting it to hand back a sorted list: `best = scores.sort()` sets
  `best` to `None`. `.sort()` rearranges the list in place; just use `scores` afterward.
- Forgetting `reverse=True`, so the "top" of the board is actually the lowest score.
- Off-the-end indexing: `scores[len(scores)]` is an IndexError — valid positions run `0` to
  `len(scores) - 1`. This is the planned Lesson-3 bug; read the traceback together.
- Off-by-one on the numbered board: humans count from 1, so print `position + 1`, not
  `position`.
- Adding a score to a ranked board and forgetting to re-sort, so the new score sits at the
  bottom no matter how big it is — `.append()` always adds to the END.
- Expecting the champion-name string demo (now in the exercises, not the lesson)
  dictionaries, Unit 08).

## Discussion prompts

- A list lets one name hold many values. Where else in a game would a list help (lives,
  inventory, level names)?
- Why does `.sort()` change the list instead of giving back a new one? When is changing-in-place
  handy, and when is it surprising?
- If we wanted each score to remember WHOSE it is, what would we need that a plain list can't do?
  (Seeds the dictionary idea for Unit 08.)

## Differentiation

- Strugglers: give the leaderboard `scores` list pre-built and have them only `.append()` and
  `.sort(reverse=True)` it; reading `max`/`min` off a ready list is a satisfying win on its own.
- Fast finishers: the Challenge exercises — sort-then-top-three and merge-two-boards (append the
  second list's scores in one loop, then a single re-sort). Extending the tier ladder with a
  fourth "legend" tier is a good no-new-concepts stretch.
- Middle tier: the add-my-score exercise (append + re-sort + return) before the Challenges.
