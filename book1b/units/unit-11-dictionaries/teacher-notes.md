# Teacher Notes — Unit 11: Dictionaries

## Goals

Students leave able to use a dictionary as a labelled map: write a literal (`{"gold": 3, …}`), read a value
with `d[key]` and safely with `d.get(key, default)`, add/update with `d[key] = value`, test membership with
`key in d` (which checks KEYS, not values), loop with `for key in d` and `for key, value in d.items()`, and
BUILD maps from data — frequency tallies and group-by.
Success looks like: every student writes a function that builds a tally dictionary from a list, and one that
finds the key with the largest value.
Function form throughout; dict equality is order-independent, so `assert tally(...) == {...}` is clean.

## Pacing

Budget: three lessons of 60–90 minutes. Open with a concrete problem ("given this list of votes, which option
won and by how many?") before the first `{}` — the motivation for a labelled tally.

- **Lesson 1 — Key/Value Maps (`dict-literal`, `dict-access`).** `{}` literals; `d[key]`; `key in d` tests
  KEYS not values (state it); the `KeyError` for a missing key (shown as a written traceback, then the safe
  `d.get(key, default)`); add/update with `d[key] = value`. A lookup table (planet day-length, price list).
- **Lesson 2 — Loop over a Dictionary (`dict-loop`).** `for key in d`; `for key, value in d.items()` ("two
  loop names, one per pair"); `keys()`/`values()`; sum the values; find the key with the largest value
  (`find-extreme` over `items()` — assume a unique maximum, or "ties → the first key wins").
- **Lesson 3 — Build Maps from Data.** A frequency tally with the missing-key idiom
  (`if k in d: d[k] = d[k] + 1` / `else: d[k] = 1`, or `d.get(k, 0) + 1`); group-by-first-letter (`word[0]`,
  each value a LIST built with the explicit `if letter in d: d[letter].append(w)` / `else: d[letter] = [w]`);
  a sorted leaderboard and a keys-passing-a-test filter.

**60-minute cut:** in Lesson 3 keep the frequency tally live; group-by (dict of lists, Ex6 First-Letter
Shelves) is the reach — under the cut, move Ex6 to the fast-finisher tier and teach it only if time allows.

## Exercises — core vs. extra vs. challenge

Core (1–7): Planet Day Lookup (`day_hours`, access), Safe Snack Count (`snack_count`, `get` default),
Supply Total (`total_supplies`, sum values), Busiest Station (`busiest_station`, find-extreme), Case-Folding
Word Tally (`word_counts`, tally + `lower()`), First-Letter Shelves (`shelve_by_first`, group-by), Sorted
Score Board (`score_board`, sort a list of `[value, key]`).
Challenges (8–9, `stretch`): Qualifying Players (`qualifiers`, filter keys into a list); Word Winner Report
(`word_winner`, most-common + f-string report).

## Common mistakes

- `d[key]` on a missing key raises `KeyError` — use `d.get(key, default)` or check `key in d` first.
- Thinking `key in d` checks values — it checks KEYS only.
- The tally trap: `d[k] = d[k] + 1` on a first-seen key is a `KeyError` — handle the missing key
  (`if k in d … else d[k] = 1`, or `d.get(k, 0) + 1`).
- The group-by trap: `d.get(letter, []).append(w)` appends to a throwaway list (the word vanishes) — use the
  explicit `if letter in d: d[letter].append(w) / else: d[letter] = [w]`.
- Case folding: `"Cloud"` and `"cloud"` are different keys unless you `lower()` first.
- Most-common on ties: pin a unique winner or the "first key wins" rule, or the answer is ambiguous.

## Discussion prompts

- When is `d.get(key, 0)` better than `d[key]`? What does the second argument do?
- Why does `key in d` look at keys and not values? How would you check whether a value is present?
- In a tally, why does the very first time you see a key need special handling?
- Which is easier to read for counting: `if k in d … else …` or `d.get(k, 0) + 1`? Why?

## Differentiation

- Strugglers: Core 1–3 and 5 (lookup, `get`, sum, a tally); give the loop and have them write the update line.
- Fast finishers: the two Challenges (filter, word-winner report), then extend the tally to also report the
  most common key.
- Middle tier: rewrite the tally using `d.get(k, 0) + 1` and confirm the same result as the `if k in d` form.

## Value plan (sample inputs)

Each exercise uses inputs distinct from the lesson examples and each other; the solution notebook asserts
several distinct cases (dict equality is order-independent).
- Ex1 `day_hours`: `"Earth"`→24, `"Mars"`→25.
- Ex2 `snack_count`: `({"apple":5,"cracker":8},"apple")`→5, `(…,"banana")`→0.
- Ex3 `total_supplies`: `{"pens":9,"paper":20,"tape":2}`→31, `{"clips":7}`→7.
- Ex4 `busiest_station`: `{"Oak":12,"Pine":19,"Elm":8}`→"Pine", `{"North":4}`→"North", and the tie
  `{"Red":7,"Blue":7,"Gold":3}`→"Red" (first tied key wins).
- Ex5 `word_counts`: `["Cloud","rain","cloud"]`→`{"cloud":2,"rain":1}`; `["GO","go","Go","stop"]`→`{"go":3,"stop":1}`.
- Ex6 `shelve_by_first`: `["cat","crow","dog","camel"]`→`{"c":["cat","crow","camel"],"d":["dog"]}`.
- Ex7 `score_board`: `{"Mia":14,"Leo":9,"Zoe":18}`→`[[9,"Leo"],[14,"Mia"],[18,"Zoe"]]`.
- Ex8 (stretch) `qualifiers`: `({"Ana":16,"Bo":7,"Cy":12},10)`→`["Ana","Cy"]`.
- Ex9 (stretch) `word_winner`: `["Red","blue","red"]`→`"red: 2"`; `["owl","fox","FOX","fox"]`→`"fox: 3"`.
