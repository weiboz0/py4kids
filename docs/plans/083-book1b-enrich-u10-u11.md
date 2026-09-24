# Plan 083 — Book 1b enrichment: Units 10–11 (Lists, Dictionaries)

**Goal:** Apply design 006 (D3–D9) to U10–U11: split the dense first list cell into single-idea rungs,
teach the widened list methods (`insert`/`pop`/`remove`/`index`, plan 079), negative indexes and
slices on lists, **multi-number `split` parsing** (the U10 input idiom), **nested-list grids**, and
give both units varied exercise sets (grids & boards, statistics, sorting by hand, bar charts, Morse,
Roman numerals, check digits, record parsing, tally histograms).

**Spec:** `docs/designs/006-book1b-enrichment.md` (D3 as amended; D4 U10/U11 art; D5; D9 U10/U11
genres); U10–U11 audit (2026-09-24, this plan's author, from the shipped notebooks).
Conventions are those of plans 080–082 (lead-in rule, binding numbering, values tables, depth rule,
fence parity with executed fences, bare-`input()` fences, pinned repairs, metadata deltas).

## Dependencies

Stacked on plans 081 (U05 negative `range` step) and 082 (U09 teaches `split`, `join`, `[::-1]`);
implementation starts only after 082 merges. If 082 were abandoned, U10 rung 4 would have to teach
`split`/`join` itself — the plan would be re-gated.

## Global constraints

- **Function form** (U07 on): every exercise defines the named function(s); the solution asserts
  several distinct cases; the real program (fence) reads stdin with bare `input()`, calls the
  function, prints the result.
- **U10 toolkit:** everything through U09, plus list literals, indexing (positive and negative),
  assignment through an index (`scores[1] = 5`), slices on lists (incl. `[::-1]`, the only step),
  `len`/`sum`/`min`/`max`/`sorted`, `.sort()` (no arguments), `append`, `insert`, `pop` (with and
  without an index), `remove`, `index`, `in`/`not in` on lists, `" ".join(list_of_strings)`,
  **lists of lists** (`grid[r][c]`), and `line.split()` with subscripting (`parts[0]`) and
  `int(...)` per piece.
  Never: `enumerate`, `zip`, tuple assignment or unpacking (swaps use a temporary variable),
  comprehensions, `list(...)`, `count`, `copy`, `reverse()`, `sort(key=…)`/`reverse=True`, dicts
  (U11), `global`.
- **U11 toolkit:** U10 plus dict literals (`{}` included), `d[key]` read/assign, `in` on a dict,
  `get`, `keys`/`values`/`items`, `for key, value in d.items():` (design 006's existing carve-out —
  the only two-name loop header), `len(d)`, dict values that are lists, and `d1 == d2` (taught by a
  new rung). Never: `del`, `pop` on a dict, `setdefault`, `sorted(d)`, dict comprehensions,
  `defaultdict`/`Counter`.
- **ASCII art:** functions RETURN the picture as one string with `"\n"` between rows (built as a list
  of row strings joined with `"\n".join(rows)` — join is taught in U09, lists in U10); asserted
  exactly; no trailing spaces; `.` filler where a gap is needed.
- **Grids** are lists of strings (`["*..", "...", ".*."]`, read with `grid[r][c]`) or lists of lists of
  numbers; a grid function returning a grid returns a new list of row strings.
- **Lead-in rule:** a lead-in sentence always sits directly above the code it introduces; every new
  rung gets its own lead-in and a short Notice.
- **Contract lines:** every exercise ends with exactly one `**Real version:**` or `**No real
  version:**` line. Real programs read lists as **one line of space-separated values** (`parts =
  input().split()`, then a loop appending `int(part)`) and grids as **one row per line** after a first
  line holding the row count. No-real cases: repair/predict exercises only.
- **Repairs** pin the broken code (shown as a `no-exec` cell or text), its exact error line, and the
  repaired output.
- **Values:** every new fixture below is grepped against shipped Book 1b content (Phase E); the
  author already replaced `banana`, `Ana`/`Bo`, `pear`, `cocoa`, `apple`, `fig`, `kite`, `north`, `Dee`,
  `cat` and `drum` (all shipped elsewhere in Book 1b), and no exercise reuses a lesson rung's values.
- **Counting rule (as plans 080–082):** scanner closure reads code cells only; the **D7 depth audit counts
  distinct exercises from the solutions' stand-in code AND their executed real-program fences** (a fence
  is a rep only for the concepts it actually uses; `input` and the reading-side `type-conversion` reps
  come from fences, since solution code cells may never call `input()`). f-string and comment reps are
  pinned in stand-in code. Phase E prints the per-concept table from this combined audit.
- **A concept used by fewer than 3 exercises goes in `requires`, not `practices`** (plan 081's rule for
  U06), so the honesty scan never meets an undeclared concept.

## U10 — Lists

**Rungs (lesson):**
1. **Split the dense first cell.** `u10l003` currently teaches a list literal, a function, `append`
   (before its section) and index 0 at once. Replace it with rungs, each with its own lead-in.
   `u10l002` is split: its literal sentences ("A **list** keeps several values in order… commas
   separate its items") stay as rung (a)'s lead-in; its index sentence ("An index reaches one
   position: index `0` is the first position") moves above rung (b).
   (a) `scores = [3, 1, 2]` / `print(scores)` (a literal); (b) `print(scores[0])` (index 0);
   (c) `print(scores[-1])` (a negative index counts from the end, as in U09 strings);
   (d) `print(len(scores))`; (e) `scores[1] = 5` / `print(scores)` (change one item through its
   index). The old `u10l003`/`u10l004` pair moves, rewritten without `append`
   (`first_score(scores)` only), to the end of the section as the function rung. `u10l004`'s `append`
   sentence moves to the `append` section (`u10l008`).
2. **After `u10l010` (append section): a new section "Change a list in place"** — one method per rung:
   `insert(0, value)`; `pop()` returns and removes the last item; `pop(0)` the first; `remove(value)`
   removes the first match; `.index(value)` finds a position — plus a Notice that `remove`/`index`
   raise `ValueError` when the value is missing, so guard with `in`.
3. **Slices on lists:** two rungs — `print(scores[1:3])` (a slice is a new list), then
   `print(scores[::-1])` (a new reversed list; the original is unchanged) — placed after the position loop (`u10l011`–`u10l013`) and before rung 4's new section.
4. **New section at the end of Lesson 1: "Read several numbers on one line"** — rungs:
   `line = "7 3 8"` / `parts = line.split()` / `print(parts)` (a list of strings); `print(int(parts[0])
   + int(parts[1]))` → 10; then a loop that appends `int(part)` for every piece into `numbers`; then
   `print("-".join(parts))` → `7-3-8` (**`join` over a list of strings** — U09 joined the letters of one
   string; now the pieces come from a list).
   Then two `no-exec` real-input cells: `parts = input().split()` → numbers → `print(sum(numbers))`;
   and "read `n`, then `n` lines" appending `int(input())`.
5. **New section before `u10l046` (put it together): "Lists inside lists: a grid"** — rungs:
   `grid = [[1, 1, 0], [0, 1, 1]]` / `print(grid[1])`; `print(grid[1][0])` (row, then column);
   a nested loop that builds one row string per inner list and appends it to `rows`, then
   `print("\n".join(rows))` (a picture returned as one string — the form every ASCII-art exercise uses);
   a list of strings as a picture
   (`board = ["#..", ".#.", "..#"]`, `print(board[2][2])`); then a `no-exec` cell reading a grid (first
   line the row count, then one row per line). The `u10l046` lead-in stays above `u10l047`.
6. **Lesson 2 real-input cell (D3: one per lesson — U10 has three lessons: L1 rung 4's two cells, L2
   this cell, L3 rung 5's grid-reading cell; Phase E counts 3/3):** a `no-exec` cell after the `sorted` section reads
   one line of numbers and prints them in order.

**Shipped text to rewrite:** `u10e001` intro ("Core work is Exercises 1–7. Exercises 8–9 are optional
Challenges" → the new partition); `u10e002` ("Build new lists with `append` inside a loop" → "…with
`append` (or change them in place with the Lesson 1 methods when a spec says so)"); teacher-notes
lines 39–40 ("only `append`/`sort` list methods are used") and 49 (the untaught-method mistake —
`insert`/`remove`/`pop`/`index` are now taught; `count` stays untaught). Phase D rewrites the whole U10
teacher-notes: Goals (5–11: in-place methods, slices, `split` parsing, grids), Lesson 1 pacing (17–19:
the new sections), the Challenge count (71) and the **Value plan** (75–88) listing every new fixture.

**New exercises** (C = core, MP = More Practice, S = Challenge):

| title | kind | fixture → exact result | genre |
|---|---|---|---|
| Numbers on One Line | C | `parse_numbers("4 9 2 15")` → `[4, 9, 2, 15]`, `parse_numbers("-3 0")` → `[-3, 0]` (split, loop, `int`, `append`; purpose comment required) | parsing |
| Second Largest | C | `second_largest([7, 19, 4, 19, 12])` → 12 (the largest value strictly below `max`: seed `best = min(numbers)`, then keep any value that is `< top` and `> best`), `([5, 3])` → 3 (with only two distinct values the answer is the smaller one — not a bug); lists hold at least two distinct values; real program prints `Second largest: 12` (f-string; purpose comment required) | searching |
| Rotate a List | C | `rotate_left([3, 8, 1, 6])` → `[8, 1, 6, 3]` via `numbers.append(numbers.pop(0))`; returns the same (changed) list (purpose comment required) | sequences |
| Median | MP | `median([9, 2, 7, 4, 5])` → 5; `median([8, 3, 6, 1])` → 4.5 (`sorted`, middle index `len // 2`; odd length returns the middle item itself — the int `5`, not `5.0`; even length averages the two middles); the stand-in and real program print `f"Median: {m}"` → `Median: 5` | statistics |
| Mode | MP | `mode([4, 2, 4, 7, 2, 4])` → 4 — for each value, an inner loop counts equal items; strict `>` keeps the first most-common value (no `count`) | statistics |
| Remove Duplicates | MP | `dedupe([5, 3, 5, 8, 3, 1])` → `[5, 3, 8, 1]` (`not in` the result, keep first appearance) | filtering |
| Reverse in Place | MP | `reverse_in_place([6, 1, 9, 4])` → `[4, 9, 1, 6]` — two indexes `left`/`right` moving inward in a `while left < right` loop, swapping through a temporary variable (no slices, no `reverse()`) | sorting & two pointers |
| Top Three | MP | `top_three([14, 3, 27, 9, 18, 21])` → `[27, 21, 18]` (`sorted`, then indexes `-1`, `-2`, `-3`) | sorting |
| Queue at the Counter | MP | `after_rush(["Ada", "Ben", "Cal"])` → append `"Fay"`, serve with `pop(0)`, `insert(0, "Eve")`, `remove("Cal")` → `['Eve', 'Ben', 'Fay']`; real reads the three names on one line | simulation, list methods |
| Find the Seat | MP | `seat_of(["Kim", "Lu", "Max"], "Lu")` → 1, `(…, "Zed")` → -1 (`.index` guarded by `in`) | searching |
| Bar Chart | MP | `bar_chart(["Mon", "Tue", "Wed"], [3, 5, 2])` → `"Mon ###\nTue #####\nWed ##"` (index loop over two parallel lists; each row `f"{labels[i]} " + "#" * values[i]`) | ASCII art, data report |
| Grid Printer | MP | `grid_text([[1, 0, 1], [0, 1, 0]])` → `"#.#\n.#."` (1 → `#`, 0 → `.`; nested loops, one row string per inner list) | ASCII art, grids |
| Tic-Tac-Toe Winner | MP | board = 3 strings: `winner(["XOX", "OXO", "OOX"])` → `"X"` (diagonal), `(["OOO", "XX.", "X.."])` → `"O"`, `(["XOX", "XOO", "OXX"])` → `"none"`; checks 3 rows, 3 columns, 2 diagonals by building each line as a 3-character string | grid & board |
| Magic Square Check | MP | `is_magic([[2, 7, 6], [9, 5, 1], [4, 3, 8]])` → True, `([[1, 2, 3], [4, 5, 6], [7, 8, 9]])` → False — every row, column and both diagonals sum to the first row's total (hand-written running totals for columns/diagonals) | grid & board |
| Running Maximum | MP | `running_max([3, 7, 2, 9, 4])` → `[3, 7, 7, 9, 9]` (best seeded from `numbers[0]`) | find-extreme |
| Fix the Index Error | MP | broken: `scores = [8, 5, 6]` / `print(scores[3])` → `IndexError: list index out of range`; repaired `print(scores[-1])` → `6` (No real version) | debug & repair |
| Fix the Missing Value | MP | broken: `numbers = [4, 5]` / `numbers.remove(7)` / `print(numbers)` → `ValueError: list.remove(x): x not in list`; repaired with `if 7 in numbers:` guard → prints `[4, 5]` (No real version) | debug & repair |
| Smallest Gap | MP | `smallest_gap([15, 3, 9, 22, 11])` → 2 (sort a copy with `sorted`, compare neighbours by index, seed from the first gap) | sorting, find-extreme |
| Is It Sorted? | MP | `is_sorted([2, 5, 5, 9])` → True, `([4, 1, 6])` → False (`numbers == sorted(numbers)`) | sorting |
| Long Words | MP | `long_words(["sled", "umbrella", "sky", "lantern"], 5)` → `['umbrella', 'lantern']` (`len(word) >= minimum`) | filtering, text |
| Common Elements | MP | `common([3, 8, 5, 12], [5, 3, 7])` → `[3, 5]` (order of the first list) | filtering |
| Class Average | MP | `average_of([12, 15, 9, 20])` → 14.0 with a hand-written total loop (no `sum`); the stand-in and real program (reads `n` then `n` lines) print `f"Average: {average}"` → `Average: 14.0` | statistics |
| Fix the String Sum | MP | broken: `parts = "4 5".split()` / `print(sum(parts))` → `TypeError: unsupported operand type(s) for +: 'int' and 'str'`; repaired: a loop appends `int(part)` to `numbers`, then `print(sum(numbers))` → `9` (No real version) | debug & repair, parsing |
| Challenge: Vertical Bar Chart | S | `vertical_bars([2, 4, 1])` → `".#.\n.#.\n##.\n###"` (`top = max(values)`; `for i in range(top):` with `level = top - i`; `#` when the value reaches the level, else `.`) | ASCII art |
| Challenge: Minesweeper Counts | S | `mine_counts(["*..", "...", ".*."])` → `['*10', '221', '1*1']` (each non-mine cell becomes its count of the 8 neighbours holding `*`; bounds checked with `0 <= r < rows` chained comparisons) | grid & board |
| Challenge: Game of Life Step | S | `life_step(["...", "###", "..."])` → `['.#.', '.#.', '.#.']` (live cell survives with 2 or 3 live neighbours; dead cell with exactly 3 becomes live) | grid & board, simulation |
| Challenge: Selection Sort | S | `selection_sort([29, 10, 14, 37, 13])` → `[10, 13, 14, 29, 37]` by hand (for each position find the smallest remaining position, swap through a temporary variable; no `sort`/`sorted`) | sorting |
| Challenge: Statistics Report | S | `stats_report([6, 2, 9, 2, 5])` → `"mean 4.8 median 5 mode 2"` — calls the student's own `median` and `mode` helpers (composition) and builds the line with an f-string | statistics |

## U11 — Dictionaries

**Rungs (lesson):**
1. **Before `u11l003`:** split the literal from the function — `vote_counts = {"blue": 3, "gold": 2,
   "green": 1}` / `print(vote_counts)`; then `print(vote_counts["blue"])`; then the existing
   function cell. `u11l002`'s explanation stays as the first rung's lead-in; each rung gets its own
   lead-in.
2. **In "Add or update a pair" (after `u11l012`):** a rung `counts = {"blue": 3}` / `counts["blue"] =
   counts["blue"] + 1` / `print(counts)` — updating a stored number, the step the frequency map
   (`u11l032`) relies on.
3. **In "Build a frequency map" (after `u11l033`):** a rung that tallies the letters of one word
   (`for ch in "melon":` → five keys, each 1) — the tally over a string, before the `get` shortcut.
4. **New rung after `u11l035`:** `print(tally_with_get(["a", "b"]) == {"b": 1, "a": 1})` → `True` —
   two dictionaries are equal when they hold the same pairs, whatever the order.
5. **In "Loop through the keys" (after `u11l019`):** a rung that builds `order = {}` by adding
   `"zinc"`, then `"iron"`, then `"gold"` and loops over it — the keys come back **in the order they
   were added** (the rule Letter Tally Chart relies on).
6. **D3 — one real-input `no-exec` cell per lesson:** L1 reads a Roman symbol (`I`, `V` or `X`) and looks
   it up in `u11l015`'s table; L2 reads a minimum and prints the players at or above it; L3's two cells
   are in rung 7.
7. **New section before `u11l044`: "Read records"** — `record = "Rin 12"` / `parts = record.split()`
   / `scores[parts[0]] = int(parts[1])`; then two `no-exec` real-input cells: read one line of words
   and tally it; read `n`, then `n` lines of `name score`.

**Shipped text to rewrite:** `u11e001` intro (new partition); `u11e002` ("The calls supply every input"
→ "The calls supply every input; each Real version reads the same values with `input()`"); `u11l039`
("A list may hold other lists" → "…as in Unit 10's grids"); teacher-notes Goals, pacing, "the two
Challenges" (line 62) and the **Value plan** (66–79) listing every new fixture.

**New exercises:**

| title | kind | fixture → exact result | genre |
|---|---|---|---|
| Morse Encoder | C | code table `{"A": ".-", "E": ".", "N": "-.", "O": "---", "S": "...", "T": "-"}` given in the spec; `to_morse("NOTE")` → `"-. --- - ."`, `to_morse("SOS")` → `"... --- ..."` (a list of codes, then `" ".join`) | encoding |
| Roman Numeral Value | C | values `{"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}`; `roman_to_int("XLII")` → 42, `("LXIX")` → 69 (subtract a value that is smaller than the next one) | sequences & bases |
| Letter Tally Chart | C | `tally_chart("papaya")` → `"p ##\na ###\ny #"` (rows in first-appearance order — taught by U11 rung 5; each row `f"{ch} " + "#" * count`) | ASCII art, tallies |
| Invert a Dictionary | MP | `invert({"cold": "C", "warm": "W", "hot": "H"})` → `{'C': 'cold', 'W': 'warm', 'H': 'hot'}` (values are unique) | encoding |
| Anagram by Tally | MP | `is_anagram("listen", "silent")` → True, `("cider", "crumb")` → False (two tallies compared with `==`) | text |
| Price Lookup Total | MP | `cart_total({"pen": 3, "pad": 5, "ink": 12}, ["pen", "ink", "pen"])` → 18; real reads the item names on one line | aggregation |
| Luhn Check Digit | MP | `luhn_valid("79927398713")` → True, `("79927398710")` → False (from the right, double every second digit, subtract 9 when over 9, total % 10 == 0) | number theory, validation |
| Scores from Records | MP | `parse_records(["Rin 12", "Oto 7", "Rin 5"])` → `{'Rin': 17, 'Oto': 7}` (`split`, `int(parts[1])`, add to an existing key); real reads `n` then `n` record lines | parsing, aggregation |
| Group by Length | MP | `group_by_length(["elk", "lynx", "yak", "hare", "gnu"])` → `{3: ['elk', 'yak', 'gnu'], 4: ['lynx', 'hare']}` (the explicit membership form from `u11l037`) | grouping |
| Most Frequent Letter | MP | `top_letter("bookkeeper")` → `"e"` (tally, then a strict find-extreme scan) | tallies, find-extreme |
| Vote Percentages | MP | `percentages({"yes": 6, "no": 2})` → `{'yes': 75.0, 'no': 25.0}` (`count / total * 100`, total by a loop) | statistics, data report |
| Word Translator | MP | `translate("a red hen", {"red": "rojo", "hen": "gallina"})` → `"a rojo gallina"` (`get(word, word)` keeps unknown words) | encoding, text |
| Fix the KeyError | MP | broken: `stock = {"nails": 40}` / `print(stock["screws"])` → `KeyError: 'screws'`; repaired `print(stock.get("screws", 0))` → `0` (No real version) | debug & repair |
| Predict the Update | MP | predict: `d = {"a": 1}` / `d["a"] = d["a"] + 5` / `d["b"] = 2` / `print(d)` → `{'a': 6, 'b': 2}` (No real version) | tracing |
| Alphabetical Keys | MP | `sorted_keys({"quince": 4, "lime": 9, "date": 2})` → `['date', 'lime', 'quince']` (append each key, then `.sort()`) | sorting |
| Low Stock | MP | `low_stock({"bolts": 3, "gears": 12, "springs": 1}, 5)` → `['bolts', 'springs']` (keys whose value is below the limit) | filtering, data report |
| Missing Prices | MP | `missing_prices({"pen": 3, "pad": 5}, ["pad", "cap", "pen", "mug"])` → `['cap', 'mug']` (items not `in` the price table) | filtering |
| Challenge: Morse Decoder | S | same code table; invert it, then `from_morse("- . -.")` → `"TEN"` | encoding |
| Challenge: Report Card | S | `report_card({"Pax": [70, 75, 80], "Juno": [90, 80]})` → `"Juno 85.0\nPax 75.0"` (names collected and `.sort()`ed; average per name; rows `f"{name} {average}"` joined with `"\n"`) | data report |

## Binding final exercise order (Challenges last; `More Practice: ` prefix)

- **U10 (37):** 1–7 existing core · 8 Numbers on One Line · 9 Second Largest · 10 Rotate a List ·
  11–30 MP: Median, Mode, Remove Duplicates, Reverse in Place, Top Three, Queue at the Counter, Find the
  Seat, Bar Chart, Grid Printer, Tic-Tac-Toe Winner, Magic Square Check, Running Maximum, Fix the Index
  Error, Fix the Missing Value, Fix the String Sum, Smallest Gap, Is It Sorted?, Long Words, Common
  Elements, Class Average · 31–37 Challenges: Keep Approved Values (was 8), Longest Word Position (was 9), Vertical Bar
  Chart, Minesweeper Counts, Game of Life Step, Selection Sort, Statistics Report.
- **U11 (28):** 1–7 existing core · 8 Morse Encoder · 9 Roman Numeral Value · 10 Letter Tally Chart ·
  11–24 MP: Invert a Dictionary, Anagram by Tally, Price Lookup Total, Luhn Check Digit, Scores from
  Records, Group by Length, Most Frequent Letter, Vote Percentages, Word Translator, Fix the KeyError,
  Predict the Update, Alphabetical Keys, Low Stock, Missing Prices · 25–28 Challenges: Qualifying Players (was 8), Word Winner Report (was 9), Morse
  Decoder, Report Card.

No real version: U10 Fix the Index Error, Fix the Missing Value, Fix the String Sum (U10 Ex 4 "Repair the In-Place Sorter" is
a write-the-function spec, so it gets a real program that reads one line of numbers);
U11 Fix the KeyError, Predict the Update. Every other exercise (existing ones included) gets a real
program.

## Depth (D7: introduced ≥5, practiced ≥3; Phase E prints the full table)

- **U10 introduces:** `list-literal`, `list-index`, `list-append`, `list-loop` — each ≥15 (nearly every
  exercise); `list-sort` 6 (Ex 4, Median, Top Three, Smallest Gap, Is It Sorted?, Statistics Report);
  `find-extreme` 6 (Ex 5, Longest Word Position, Second Largest, Running Maximum, Mode, Smallest Gap);
  `filter-into-list` 5 (Ex 7, Keep Approved Values, Remove Duplicates, Long Words, Common Elements).
- **U10 practices:** `builtin-functions` ≥10; `in-operator` 5 (Keep Approved Values, Remove
  Duplicates, Common Elements, Find the Seat, Fix the Missing Value); `accumulator`/`running-total` ≥3
  (Ex 6, Magic Square Check, Class Average); `count-by-condition` 3 (Mode, Minesweeper Counts, Game of
  Life Step); `f-string` 3 (stand-in code of Bar Chart, Median, Class Average — plus Statistics Report);
  `error-messages` 3 (Fix the Index Error, Fix the Missing Value, Fix the String Sum);
  `float-type` 3 (Median, Class Average, Statistics Report); `loop-counter` 3 (Mode's inner `count`, Minesweeper Counts' and Game of Life
  Step's neighbour counts); `comment` 3 (purpose comments in the Ex 8–10 stand-ins, counted in solutions.ipynb); `int-type`,
  `naming` ≥3.
- **U11 introduces:** `dict-literal` ≥12, `dict-access` ≥12, `dict-loop` ≥8 (every tally/report
  exercise).
- **U11 practices** (reps pinned in the specs): `list-literal`/`list-append` ≥5; `list-sort` 3 (Ex 7
  Sorted Score Board, Alphabetical Keys, Report Card's sorted names); `filter-into-list` 3 (Qualifying
  Players, Low Stock, Missing Prices); `string-methods` 4 (Ex 5 `lower`, Word Winner Report `lower`,
  Scores from Records `split`, Word Translator `split`/`join`); `string-index` 3 (Ex 6 `word[0]`, Roman
  Numeral Value `s[i]`, Luhn Check Digit `s[i]`); `find-extreme` 3 (Ex 4, Word Winner Report, Most
  Frequent Letter); `count-by-condition` 3 (the conditional tally increments of Ex 5, Letter Tally
  Chart, Most Frequent Letter); `accumulator` ≥3 (Ex 3, Price Lookup Total, Luhn Check Digit, Vote
  Percentages); `f-string` 3 (Word Winner Report, Report Card rows `f"{name} {average}"`, Letter Tally
  Chart's rows); `builtin-functions` ≥3; `comment` 3 (purpose comments
  required in Ex 8–10); `int-type`/`naming` ≥3.

## Metadata deltas (manifest + coverage-map, identically; confirmed by Phase E's honesty scan)

Rule: `practices` gains a concept only with ≥3 named reps; a concept used by fewer goes in `requires`.

- **U10 `practices` +=** `input`, `type-conversion` (every real program's fence; stand-ins: Numbers on One
  Line, Fix the String Sum), `string-methods` (`split`: Numbers on One Line, Fix the String Sum, Queue at
  the Counter's fence; `join`: Bar Chart, Grid Printer, Vertical Bar Chart), `string-index` (Tic-Tac-Toe Winner,
  Minesweeper Counts, Game of Life Step), `string-concat` (Bar Chart, Grid Printer, Vertical Bar Chart,
  Minesweeper Counts), `nested-loops` (Mode, Grid Printer, Minesweeper Counts, Game of Life Step,
  Selection Sort), `error-messages` (the three repairs). (`float-type` is already a shipped U10 practice,
  not a delta — Median, Class Average and Statistics Report keep it honest.) **U10 `requires` +=** `while-loop` (Reverse in Place only), `logical-ops`
  (Minesweeper bounds only if the scanner sees `and`), `string-slice` (lesson slices; no exercise needs
  one).
- **U11 `practices` +=** `input`, `type-conversion` (every real program; Scores from Records, Luhn
  Check Digit). **U11 `requires` +=** `float-type` (Vote Percentages, Report Card — two reps),
  `error-messages` (Fix the KeyError — one rep), `string-concat` (Letter Tally Chart's `"#" * count`
  rows — one rep).
- Phase E's depth audit enforces D7 for **every** added `practices` concept, and its lesson audit
  enforces D3's one real-input `no-exec` cell per lesson.

## Phases

- **Phase B (Codex gpt-6-sol ×2, direct `codex exec` in the main checkout):** lesson rungs + `no-exec`
  input cells + exercise statements with starters holding the worked-sample given values.
- **Phase C (Codex ×2, separate fresh sessions):** solutions — stand-ins + asserts, real-program fences
  (bare `input()`) with Sample input / Expected output.
- **Phase D (inline):** teacher-notes (pacing incl. 60-minute cuts; core/MP/challenge partition with
  values; common mistakes: `pop` vs `remove` arguments, `remove`/`index` `ValueError`, aliasing when a
  function changes its input list, `grid[c][r]` swapped, `sort()` returns `None`, dict `KeyError`;
  D9 genre notes), metadata deltas.
- **Phase E — VERIFICATION (audits first, ci-local last):** toolkit AST audit of every cell and fence
  (per-unit allow-lists above; no `enumerate`/`zip`/tuple targets except the U11 `items()` carve-out;
  no step other than `-1`); exercise-contract + fence-parity audit (every fence EXECUTED with its pinned
  Sample input; stdout == Expected output == the stand-in's printed lines); fixture grep of every new
  value against shipped Book 1b content; value-use audit; manifest ↔ coverage-map diff + honesty scan;
  depth + genre tables (D9 ≥4 per unit); `scripts/ci-local.sh` ALL GREEN; post-execution report.

## Out of scope

U12–U13, checkpoints, syllabus refresh (plan 084); tooling.

## Plan Review

### Round 1 — verdicts

- `[sol]` **REJECT** — D3 needs a real-input cell in every lesson; deltas without 3 reps (`string-slice`,
  `while-loop`, `error-messages`, U11 `float-type`); `u10l002` explains index 0 above the literal rung;
  slice rung carries two ideas; fixture collisions (`cocoa`, `Dee`, `cat`, `apple`, `fig`, `kite`);
  `u11e002` and dictionary order.
- `[fable]` **REJECT** — unstated dependency on 082/081; collisions (`cocoa`, `apple`, `kite`, `north`);
  Grid Printer and Numbers on One Line copy lesson values; incomplete rewrite list (U10/U11 teacher-notes
  Goals/pacing/Value plan, `u11e002`, `u11l039`); nits: string immutability untaught, f-string/comment
  reps must be in stand-in code, Second Largest two-value note, Median int.
- `[glm]` **REJECT** (reviewed the pre-fold draft 7ccba24) — delta tags without 3 reps (`string-slice`,
  `while-loop`, `error-messages`, `logical-ops`, `elif-else`, U11 `float-type`/`error-messages`);
  `join` over a list never taught; U11 omits `string-concat`; nits: dependency, Luhn without a negative
  step, rung 3/4 order, `loop-counter` reps unnamed.

### Round 1 — fold

- `[FIXED]` `## Dependencies` added; Vertical Bar Chart pinned to `range(top)` + `level = top - i`.
- `[FIXED]` D3: U10 L2 and U11 L1/L2 real-input cells added (one per lesson in both units).
- `[FIXED]` deltas: explicit ≥3-reps rule; under-used concepts moved to `requires`; third U10 repair
  **Fix the String Sum** (`TypeError`; U10 → 37).
- `[FIXED]` ladder: `u10l002` split (literal vs index sentences); slices are two rungs; the
  "strings cannot change" clause dropped.
- `[FIXED]` fixtures: `papaya`, `melon`, `sled`, `cold/warm/hot`, `a red hen`, `quince/lime/date`;
  lesson values changed (`"7 3 8"`, `[[1, 1, 0], [0, 1, 1]]`) so no exercise copies a rung.
- `[FIXED]` rewrite list: `u11e002`, `u11l039`, U10/U11 teacher-notes Goals/pacing/Challenge
  counts/Value plans; dictionary insertion order taught by a new U11 rung before Letter Tally Chart.
- `[FIXED]` ([glm]) `join` over a list taught by two rungs (`"-".join(parts)`, `"\n".join(rows)`);
  U11 `string-concat` → `requires`; `loop-counter` reps named; slices placed before rung 4; delta tags
  were already moved to `requires` by the [sol]/[fable] fold; Luhn indexes `s[len(s) - 1 - i]` (no step).
- `[FIXED]` f-string reps pinned in stand-in code (Bar Chart, Median, Class Average; Letter Tally Chart,
  Report Card, Word Winner); comment reps counted in solutions; Second Largest and Median notes.

### Round 1 — `[self]` APPROVE WITH NITS

- Every fixture recomputed by running reference code (scratch script); `banana`, `Ana`/`Bo` and `pear`
  collisions with shipped Book 1b replaced before review.
- Nits folded before dispatch: U10 Ex 4 is a write-the-function spec, so it keeps a real program;
  Second Largest pins its seed (`best = min(numbers)`, no `None`).
- Watch items for reviewers: U10 grows 9 → 37 and U11 9 → 28 (volume is the standing preference);
  list slices scan as `string-slice` (a practices delta, not a new concept).

### Round 2 — [fable] APPROVE WITH NITS (folded)

- `[FIXED]` Vertical Bar Chart `[2, 4, 1]` → `".#.\n.#.\n##.\n###"` (no longer copies `u10l003`'s
  `[3, 1, 2]`); Anagram's false case `("cider", "crumb")` (`robot` is a checkpoint-04 fixture); U11 L1
  real-input cell reads a Roman symbol (planets belong to U11 Ex 1); U10 D3 count stated (3 lessons,
  3/3); U11 rungs renumbered 1–7 in order; cosmetics (duplicate `loop-counter`, `float-type` already
  practised, genre cells, the `[self]` count).

### Round 2 — [sol] REJECT (folded)

- `[FIXED]` counting rule stated once: closure from code cells; D7 depth from stand-ins **plus executed
  fences** (the source of the `input` reps); Phase E prints the combined table.
- `[FIXED]` Class Average's `n`-then-`n`-lines input is not a `split` rep (Queue at the Counter's fence
  is); `float-type` is noted as a shipped practice, not a delta.

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
