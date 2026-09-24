# Teacher Notes — Checkpoint 04: Dictionaries & Collections

## Goals

A short mixed assessment proving Units 01–11, with the load on dictionaries: building and reading a lookup
map, safe access with `d.get(default)`, frequency tallies with the missing-key idiom, looping over `items()`,
and finding the most common key — over a recap of lists, functions, and `elif` lookups.
It introduces nothing new and assesses only what has been taught. Students work solo; every question is in the
function form, checked by calling it on fixed inputs.

The checkpoint stays strict: **no `ord`/`chr`, no comprehensions, no `collections`/`defaultdict`, dict methods
limited to `items`/`keys`/`values`/`get`, list methods to `append`/`sort`**; text is joined with f-strings
(no `+`), no boolean operators, and no `range`/`sorted`/slices are needed.

## Pacing

Budget: half a lesson (~30–45 minutes). Hand out after Unit 11. The seven questions and their targets:
1. **Build a Trail Lookup** (`trail_distance`) — build/read a dict (U11). *Pass-bar (build-and-read).*
2. **Default Locker Count** (`locker_count`) — `d.get(key, 0)` with a default (U11).
3. **Color Frequency Tally** (`color_counts`) — the missing-key tally idiom (U11). *Pass-bar (tally).*
4. **Inventory Total** (`inventory_total`) — sum values over `items()`/`values()` (U11).
5. **Most Common Choice** (`most_common`) — `find-extreme` over items, unique winner (U10/U11).
6. **Level Lookup Message** (`level_message`) — an `elif`/lookup returning an f-string (U03/U11).
7. **First-Word Report** (`first_word_report`) — tally a list of words AND read `words[0]` by position, then
   report `"word: n of total"` (U10 list-index + U11 tally).

## Real-version notes (design 006, plan 084)

Each question now ends with an ungraded **Real version** note (CP01 Q7, a traceback-reading question,
says **No real version**). Graded answers still use the fixed given values and never call `input()`; the
solutions notebook shows each real program — the same work reading stdin with a bare `input()`, the way a
contest problem does — with a sample input and its expected output. Use one or two as a warm-up after the
checkpoint, typing the sample input live.

## Common mistakes

- `d[key]` on a missing key raises `KeyError` — use `d.get(key, 0)` (Q2) or check `key in d`.
- The tally trap (Q3): the first time a key appears, `d[k] = d[k] + 1` fails — handle the missing key first.
- Q5 most-common: comparing values but returning the value instead of the key; ties (the inputs have a clear
  winner — say so).
- Q6: forgetting the input is a string key (`"3"`), or an `elif` order that returns the wrong band.
- Q7: reading `words[0]` after the list might be empty (the spec guarantees at least one word); miscounting
  the total.
- Reaching for a comprehension, `range`, `sorted`, `+` text join, or `and`/`or` — none are needed here.

## Discussion prompts

- When does `d.get(key, 0)` save you from a `KeyError`, and what does the `0` mean?
- In the frequency tally, why does the first sighting of a key need different handling from later ones?
- In Q7, how do you read the first word specifically, and how is that different from looping over all words?

## Grading

Pass = at least 5 of 7 correct, with **Q1 (build-and-read a dict)** and **Q3 (tally with the missing-key
idiom)** among them — those are the load-bearing dictionary skills. Key each question to its concept(s) above.
Full marks require the exact returned values for the fixed inputs. Partial credit: award a tally whose logic
is right but that `KeyError`s on the first key at half (note the missing-key fix); `d.get`-with-default (Q2)
is a good partial-credit discriminator.

## Differentiation

- Strugglers: prioritize Q1–Q4 — build/read, `get`-default, the tally, and the total; treat Q5/Q6/Q7 as reach.
- Fast finishers: after Q7, ask them to also report the LEAST common colour from Q3's tally (another
  find-extreme with a flipped comparison).

## Value plan (sample inputs)

- Q1 `trail_distance`: `"Creek"`→3, `"Lake"`→8.
- Q2 `locker_count`: `({"balls":6,"cones":9},"cones")`→9, `(…,"bibs")`→0.
- Q3 `color_counts`: `["red","blue","red"]`→`{"red":2,"blue":1}`; `["gold","gold","green","gold"]`→`{"gold":3,"green":1}`.
- Q4 `inventory_total`: `{"notebooks":4,"pencils":10,"erasers":3}`→17, `{"folders":8}`→8.
- Q5 `most_common`: `{"robot":5,"rocket":8,"maze":3}`→"rocket", `{"sun":1,"moon":4}`→"moon".
- Q6 `level_message`: `"3"`→"Gold: 10", `"2"`→"Silver: 7".
- Q7 `first_word_report`: `["map","star","map"]`→`"map: 2 of 3"`; `["red","blue","green","red"]`→`"red: 2 of 4"`.
