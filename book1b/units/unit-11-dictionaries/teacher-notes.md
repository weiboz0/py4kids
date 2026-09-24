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
  `d.get(key, default)`); add/update with `d[key] = value`, then the new rung that updates a stored number
  (`counts["blue"] = counts["blue"] + 1`). The first code cell is now split: the literal and a printed
  dictionary first, then one `d[key]` read, then the function. A lookup table (Roman values, levels) and a
  `no-exec` cell that reads a Roman symbol and looks it up.
- **Lesson 2 — Loop over a Dictionary (`dict-loop`).** `for key in d`, then the new rung showing that keys
  come back **in the order they were added** (`"zinc"`, `"iron"`, `"neon"`) — the rule Letter Tally Chart
  relies on; `for key, value in d.items()` ("two
  loop names, one per pair"); `keys()`/`values()`; sum the values; find the key with the largest value
  (`find-extreme` over `items()` — assume a unique maximum, or "ties → the first key wins"). A `no-exec` cell
  reads `n` records `name score` into a dictionary and totals them.
- **Lesson 3 — Build Maps from Data.** A frequency tally with the missing-key idiom
  (`if k in d: d[k] = d[k] + 1` / `else: d[k] = 1`, or `d.get(k, 0) + 1`); group-by-first-letter (`word[0]`,
  each value a LIST built with the explicit `if letter in d: d[letter].append(w)` / `else: d[letter] = [w]`);
  new rungs tally the letters of one word and show that two dictionaries are equal when they hold the same
  pairs (`==`, order-independent); a sorted leaderboard and a keys-passing-a-test filter; then **Read
  records** (`"Rin 12".split()`, `int(parts[1])`) with `no-exec` cells that tally a typed line of words and
  read `n` records.

**60-minute cut:** in Lesson 3 keep the frequency tally live; group-by (dict of lists, Ex6 First-Letter
Shelves) is the reach — under the cut, move Ex6 to the fast-finisher tier and teach it only if time allows.

## Exercises — core vs. More Practice vs. challenge

28 exercises, all in the function form.

- **Core (1–10):** Planet Day Lookup, Safe Snack Count, Supply Total, Busiest Station, Case-Folding Word
  Tally, First-Letter Shelves, Sorted Score Board, plus **Morse Encoder** (8: `NOTE` → `-. --- - .`),
  **Roman Numeral Value** (9: `XLII` → 42, `LXIX` → 69) and **Letter Tally Chart** (10: `papaya` →
  `p ##` / `a ###` / `y #`). Exercises 8–10 require a purpose comment.
- **More Practice (11–24)**, grouped by genre:
  - *Encoding:* Invert a Dictionary, Word Translator (`a red hen` → `a rojo gallina`).
  - *Tallies & reports:* Anagram by Tally, Most Frequent Letter (`bookkeeper` → `e`), Vote Percentages
    (75.0 / 25.0), Group by Length, Scores from Records (`Rin 12` / `Oto 7` / `Rin 5` → Rin 17).
  - *Lookups & filters:* Price Lookup Total (18), Alphabetical Keys, Low Stock, Missing Prices.
  - *Number theory & validation:* Luhn Check Digit (`79927398713` → valid).
  - *Debug & predict:* Fix the KeyError (`KeyError: 'screws'` → `get`), Predict the Update
    (`{'a': 6, 'b': 2}`).
- **Challenges (25–28, `stretch`):** Qualifying Players, Word Winner Report, Morse Decoder (`- . -.` →
  `TEN`), Report Card (averages per name, names sorted).

**Real versions.** Every exercise except Fix the KeyError and Predict the Update has a real program: words
arrive on one line (`split`), records as `n` then `n` lines `name value`.

## Common mistakes

- `d[key]` on a missing key raises `KeyError` — use `d.get(key, default)` or check `key in d` first.
- Thinking `key in d` checks values — it checks KEYS only.
- The tally trap: `d[k] = d[k] + 1` on a first-seen key is a `KeyError` — handle the missing key
  (`if k in d … else d[k] = 1`, or `d.get(k, 0) + 1`).
- The group-by trap: `d.get(letter, []).append(w)` appends to a throwaway list (the word vanishes) — use the
  explicit `if letter in d: d[letter].append(w) / else: d[letter] = [w]`.
- Case folding: `"Cloud"` and `"cloud"` are different keys unless you `lower()` first.
- Most-common on ties: pin a unique winner or the "first key wins" rule, or the answer is ambiguous.
- Record lines: `parts[1]` is text — convert with `int(parts[1])` before adding.
- Inverting a dictionary with repeated values silently keeps only the last key — Invert a Dictionary
  promises unique values.
- Expecting a dictionary to come back sorted — it keeps insertion order; sort a list of keys when order
  matters (Alphabetical Keys, Report Card).

## Discussion prompts

- When is `d.get(key, 0)` better than `d[key]`? What does the second argument do?
- Why does `key in d` look at keys and not values? How would you check whether a value is present?
- In a tally, why does the very first time you see a key need special handling?
- Which is easier to read for counting: `if k in d … else …` or `d.get(k, 0) + 1`? Why?

## Differentiation

- Strugglers: Core 1–3 and 5 (lookup, `get`, sum, a tally); give the loop and have them write the update line.
- Fast finishers: the encoding and report More Practice, then the Challenges (the Morse Decoder inverts the
  encoder's table); then extend the tally to also report the
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
- Ex25 (stretch) `qualifiers`: `({"Ana":16,"Bo":7,"Cy":12},10)`→`["Ana","Cy"]`.
- Ex26 (stretch) `word_winner`: `["Red","blue","red"]`→`"red: 2"`; `["owl","fox","FOX","fox"]`→`"fox: 3"`.
- New exercises 8–28: fixtures as in the exercise statements (plan 083's tables), grep-distinct from
  shipped Book 1b content.

## More Practice ideas (design 006 D9 genres)

- **Encoding:** a phone keypad map (`"abc" → 2` …) that turns a word into digits.
- **Data report:** from `n` records `city temperature`, print each city's highest reading.
- **Validation:** check that every key in an order exists in a price table before totalling.
