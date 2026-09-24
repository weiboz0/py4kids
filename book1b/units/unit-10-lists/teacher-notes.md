# Teacher Notes — Unit 10: Lists

## Goals

Students leave able to build and process a list: write a literal (`[3, 1, 2]`), read an item by index
(`nums[0]`, `nums[-1]`), change an item through its index, grow and change a list (`append`, `insert`,
`pop`, `remove`, `index`), slice it (`nums[1:3]`, `nums[::-1]`), compare two lists with `==`, parse several
numbers typed on one line (`input().split()` + `int`), read a grid stored as a list of lists
(`grid[r][c]`), loop over it two ways (`for x in nums` and `for i in range(len(nums))`),
order it (`nums.sort()` in place vs `sorted(nums)` for a new list), find an extreme by hand, and filter items
into a new list.
Success looks like: every student writes a function that builds a new list with `append` in a loop, and one
that scans a list to find the best item (or its position).
Function form throughout; built-ins `len`/`min`/`max`/`sum`/`sorted` are available now (for lists).

## Pacing

Budget: three lessons of 60–90 minutes.

- **Lesson 1 — Build and Read (`list-literal`, `list-index`, `list-append`, `list-loop`).** The old dense
  first cell is now a ladder: a literal, index 0, a negative index, `len`, changing one item through its
  index, then the function rung. The value loop and `len`/`sum`; `append`; the new **"Change a list in
  place"** rungs — `insert(0, x)`, `pop()`, `pop(0)`, `remove(x)`, `.index(x)` (Notice: `remove`/`index`
  raise `ValueError` when the value is missing, so guard with `in`); the index loop; **slices**
  (`nums[1:3]`, `nums[::-1]`) and **list equality** (`[1, 2] == [2, 1]` is False — order matters). Then
  **read several numbers on one line**: `"7 3 8".split()` is a list of strings, `int(parts[0])`, a loop that
  converts every piece, and `"-".join(parts)` (join over a list). Two `no-exec` cells read a line of numbers
  and read `n` then `n` lines.
- **Lesson 2 — Order and Choose (`list-sort`, `find-extreme`).** `nums.sort()` sorts in place and **returns
  `None`** (teach the `scores = nums.sort()` → `None` trap — the list twin of print-vs-return); `sorted(nums)`
  returns a new list and leaves the original alone. `min`/`max`/`sum` builtins vs a hand-written
  **find-extreme** loop seeded `best = nums[0]` (NOT `0` — it breaks on all-negative data); the loop earns
  its keep as **argmax** (position of the max, or the longest word — `max(key=…)` is not taught). A `no-exec`
  cell reads a line of numbers and prints them sorted.
- **Lesson 3 — Filter and Combine (`filter-into-list`).** Build a new list of items passing a test with
  `append` inside an `if` in a loop (NOT a comprehension); **prefix sums** (append a running total each step);
  then the new **grid** section — `grid[1]` (a row), `grid[1][0]` (row, then column), a nested loop that
  builds one row string per inner list and `"\n".join(rows)`, a list of strings as a picture, and a
  `no-exec` cell that reads a row count and then the rows; put it together (keep the above-average scores,
  using `sum`/`len` for the average).

**60-minute cut:** Lesson 1 is the densest — teach the literal/index/`append` rungs and the one-line
parsing live, and hand the in-place methods over as a worksheet (each is one line). Lesson 3's prefix-sums
build can wait; keep filtering (the headline technique) and the first two grid rungs.

## Exercises — core vs. More Practice vs. challenge

37 exercises, all in the function form; every extreme/average spec states the list has at least one item;
lists are built with loops (never comprehensions).

- **Core (1–10):** Score Snapshot, Scale Every Score, Round-to-Round Changes, Repair the In-Place Sorter,
  Winning Position (argmax), Progress Totals (prefix sums), Above the Team Average, plus **Numbers on One
  Line** (8: `"4 9 2 15"` → `[4, 9, 2, 15]`), **Second Largest** (9: → 12) and **Rotate a List** (10:
  `append(pop(0))`). Exercises 8–10 require a purpose comment.
- **More Practice (11–30)**, grouped by genre:
  - *Statistics:* Median (5; 4.5), Mode (4), Class Average (`Average: 14.0`).
  - *Searching & sorting:* Remove Duplicates, Reverse in Place (two pointers, `while left < right`), Top
    Three, Find the Seat (`.index` guarded by `in`), Running Maximum, Smallest Gap, Is It Sorted? (list `==`),
    Long Words, Common Elements.
  - *Simulation:* Queue at the Counter (`append`, `pop(0)`, `insert`, `remove` → `['Eve', 'Ben', 'Fay']`).
  - *ASCII art & grids:* Bar Chart, Grid Printer, Tic-Tac-Toe Winner, Magic Square Check.
  - *Debug & repair:* Fix the Index Error (`IndexError: list index out of range`), Fix the Missing Value
    (`ValueError: list.remove(x): x not in list`), Fix the String Sum (`TypeError` — split pieces are
    strings).
- **Challenges (31–37, `stretch`):** Keep Approved Values, Longest Word Position, Vertical Bar Chart,
  Minesweeper Counts, Game of Life Step, Selection Sort, Statistics Report.

**Real versions.** Every exercise except the three Fix exercises has a real program. List inputs arrive as
one line of values (`input().split()` + an `int` loop) or as `n` then `n` lines; grids as a row count then
one row per line.

## Common mistakes

- `scores = nums.sort()` sets `scores` to `None` (sort is in place) — use `sorted(nums)` when you need a
  value back.
- Seeding a find-extreme with `best = 0` instead of `best = nums[0]` (wrong on all-negative lists).
- Off-by-one with `range(len(nums))`; mixing the value loop and the index loop when you need the position.
- Modifying `nums` while looping over it, or expecting `sorted(nums)` to change `nums` (it does not).
- Reaching for `count` or a comprehension — neither is taught; count and build with a loop.
- `pop()` vs `pop(0)` vs `remove(value)`: `pop` takes a POSITION (and returns the item), `remove` takes a
  VALUE; `remove`/`index` raise `ValueError` when the value is missing — guard with `in`.
- Forgetting that `split()` gives strings: `sum(parts)` fails with a `TypeError`; convert each piece first.
- Swapping row and column in `grid[r][c]`; checking a neighbour outside the grid (use `0 <= r < rows`).
- A function that changes the list it was given (`rotate_left`, `reverse_in_place`) changes the caller's
  list too — say so in the spec, as these do.
- **Silent wraparound in round-to-round changes:** writing `for i in range(len(scores))` instead of
  `range(1, len(scores))` makes `scores[i] - scores[i-1]` compute `scores[0] - scores[-1]` on the first pass
  — no error, just a wrong extra value, because `-1` wraps to the last item (exactly the negative index U09
  taught). Start the range at 1.
- Using `//` for an average (`sum(nums) // len(nums)`) drops the fraction — use `/` for the true average in
  "above the average".

## Discussion prompts

- When do you want `nums.sort()` (change the list) and when `sorted(nums)` (keep the original)? Why does
  `nums.sort()` return `None`?
- `min`/`max` give the value — how do you get the *position* of the biggest, or the longest word? Why does
  the hand loop earn its place next to the built-ins?
- Why seed `best = nums[0]` and not `0`?
- In "above the average", why must you compute the average before the filtering loop, not inside it?

## Differentiation

- Strugglers: Core 1–3 and 5 (build/read, scale, differences, argmax); give the loop and have them add the
  `append` or the comparison.
- Fast finishers: the grid and statistics More Practice, then the Challenges (Minesweeper and the Game of
  Life are favourites); then combine — sort the kept list, or
  return both the max and its position.
- Middle tier: rewrite a `min`/`max` call as the hand-written find-extreme loop and confirm identical results.

## Value plan (sample inputs)

Each exercise uses list inputs distinct from the lesson examples and each other (mixed lists with negatives,
single-item and empty lists, some/all/none passing a filter); the solution notebook asserts several distinct
cases per function.
- Ex1 `score_snapshot`: `[6,9,4]`, `[12]`, `[-2,5,1,3]`.
- Ex2 `scaled_scores`: `([3,7,2],4)`, `([-2,5,0],3)`, `([],9)`.
- Ex3 `round_changes`: `[5,9,8,14]`, `[20,15,10]`, `[7]`.
- Ex4 `sort_in_place`: `[8,3,6]`, `[-1,-7,-4]`, `[5,5,2]`.
- Ex5 `position_of_largest`: `[14,22,17]`, `[-8,-3,-10]`, `[9,12,12,4]`.
- Ex6 `progress_totals`: `[4,6,3]`, `[10,0,5,2]`, `[]`.
- Ex7 `above_average`: `[9,15,12,20]`, `[4,4,4]`, `[-6,-2,-4]`.
- Ex31 (stretch) `keep_approved`: `([7,2,7,5],[2,5])`, `([3,3,8],[3,9])`, `([4,6],[1,2])`.
- Ex32 (stretch) `position_of_longest`: `["owl","panther","fox"]`, `["kiwi","apricot","fig"]`, `["sun","map","key"]`.
- New exercises 8–37: fixtures as in the exercise statements (plan 083's tables), grep-distinct from shipped
  Book 1b content.

## More Practice ideas (design 006 D9 genres)

- **Grid & board:** count the `#` cells in each column of a list-of-strings map.
- **Statistics:** the range (max − min) and how many values lie above the median.
- **Games:** a "Connect Three" check on one row of a board string.
