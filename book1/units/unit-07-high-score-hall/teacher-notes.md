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

Budget: two lessons of 60–90 minutes.

- **Lesson 1 — lists hold many scores (list-literal, list-index, list-append, list-loop,
  builtin-functions) (60–90 min).**
  Open on the hook: a messy scrap of paper full of scores — how would a program keep them?
  15 min: a list is one variable holding many scores — `scores = [1200, 850, 990, 1500]`;
  first and last with `scores[0]` / `scores[-1]`.
  15 min: grow the board with `scores.append(1310)`; walk it with `for score in scores`.
  15 min: a numbered board over the list AS ENTERED — `for position in range(len(scores))`.
  Call these "entry #1, #2…" (POSITION in the list), NOT "place" or "rank" — ranking comes in
  Lesson 2 after we sort. Naming them "places" before sorting is the trap to avoid.
  20 min: measure it — `len` (how many), `max` (the champion), `min` (the rookie); a running
  `total` accumulator and `average = total / len(scores)` (note the average is a decimal —
  a float — even when the scores are whole numbers).
  60-MINUTE CUT: drop the average beat; build/index/append/loop/`max`/`min` are the core.
- **Lesson 2 — rank the hall and crown a champion (list-sort; helpers + tiers) (60–90 min).**
  Open on the thread: yesterday we LISTED scores; today we RANK them and crown the champion.
  10 min: capture `champion = max(scores)` first, then `scores.sort()` (low→high) and
  `scores.sort(reverse=True)` (top-first). Emphasize `.sort()` changes the list IN PLACE — it
  does NOT return a new list (contrast Unit 06, where you REBUILD a string rather than change
  it). This is the unit's key mental-model beat.
  20 min: a `board_line(place, score)` helper (`return "Place " + str(place) + ": " +
  str(score)`) printed over the SORTED list — now the numbers really are places/ranks. An
  `add_score(scores, new_score)` helper that appends AND re-sorts, so the hall stays ranked
  after every addition.
  15 min: tier ranking with `if score >= 1000: … elif score >= 500: … else:` →
  gold/silver/bronze; an already-on-the-board guard `if new_score in scores`.
  10 min: the qualifying-threshold `while` loop (`threshold` doubles each round until it passes
  the champion) and the deliberate off-the-end bug `scores[len(scores)]` — read the IndexError
  traceback together (valid positions are `0` to `len(scores) - 1`).
  60-MINUTE CUT: skip the while-loop threshold demo; sort + board_line + tiers are the core.

Note on the champion's NAME: Lesson 2 cleans a single scalar name
(`winner = "  ada lovelace  ".strip().upper()`) purely to practice string methods. Say plainly
that this name is an ILLUSTRATION and is NOT linked to any particular score — pairing a name to
a score needs a dictionary, which arrives in Unit 08. Keeping one list of numbers is a
deliberate simplification, not an oversight.

Practices reappearance: `print`/`f-string` run through every "show the board" step;
`arithmetic` is the running total and `position + 1`; `int-type` is the scores themselves;
`range-function`/`loop-counter` drive the numbered board; `if-statement`/`elif-else`/
`comparison` are the tiers; `string-concat`/`type-conversion` build the `board_line` label;
`float-type` is the average; `string-methods` cleans the winner name; `in-operator` is the
already-on-the-board guard; `while-loop`/`accumulator` carry over; `error-messages` is the
IndexError beat. `input` is practiced through the "add-my-score" exercise PROMPT only — the
executable cells stay input-free so the notebooks run start-to-finish in class without waiting
on typed input; students see `input()` in the exercise text and the reference solution uses a
fixed sample score instead. All of these return in Unit 08's word games and the capstone.

## Common mistakes

- Calling `.sort()` and expecting it to hand back a sorted list: `best = scores.sort()` sets
  `best` to `None`. `.sort()` rearranges the list in place; just use `scores` afterward.
- Forgetting `reverse=True`, so the "top" of the board is actually the lowest score.
- Off-the-end indexing: `scores[len(scores)]` is an IndexError — valid positions run `0` to
  `len(scores) - 1`. This is the planned Lesson-2 bug; read the traceback together.
- Off-by-one on the numbered board: humans count from 1, so print `position + 1`, not
  `position`.
- Adding a score to a ranked board and forgetting to re-sort, so the new score sits at the
  bottom no matter how big it is — `.append()` always adds to the END.
- Expecting the illustrative `winner` name to be tied to a score — it isn't yet (that needs
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
