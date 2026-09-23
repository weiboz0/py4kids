# Teacher Notes — Unit 10: Lists

## Goals

Students leave able to build and process a list: write a literal (`[3, 1, 2]`), read an item by index
(`nums[0]`), grow one with `append`, loop over it two ways (`for x in nums` and `for i in range(len(nums))`),
order it (`nums.sort()` in place vs `sorted(nums)` for a new list), find an extreme by hand, and filter items
into a new list.
Success looks like: every student writes a function that builds a new list with `append` in a loop, and one
that scans a list to find the best item (or its position).
Function form throughout; built-ins `len`/`min`/`max`/`sum`/`sorted` are available now (for lists).

## Pacing

Budget: three lessons of 60–90 minutes.

- **Lesson 1 — Build and Read (`list-literal`, `list-index`, `list-append`, `list-loop`).** `[3, 1, 2]`;
  `nums[0]`; `nums.append(x)`; both loop forms — `for x in nums` (value) and `for i in range(len(nums))`
  (index, needed for position work); `len`/`sum`.
- **Lesson 2 — Order and Choose (`list-sort`, `find-extreme`).** `nums.sort()` sorts in place and **returns
  `None`** (teach the `scores = nums.sort()` → `None` trap — the list twin of print-vs-return); `sorted(nums)`
  returns a new list and leaves the original alone. `min`/`max`/`sum` builtins vs a hand-written
  **find-extreme** loop seeded `best = nums[0]` (NOT `0` — it breaks on all-negative data); the loop earns
  its keep as **argmax** (position of the max, or the longest word — `max(key=…)` is not taught).
- **Lesson 3 — Filter and Combine (`filter-into-list`).** Build a new list of items passing a test with
  `append` inside an `if` in a loop (NOT a comprehension); **prefix sums** (append a running total each step);
  put it together (keep the above-average scores, using `sum`/`len` for the average).

**60-minute cut:** Lesson 3's prefix-sums build can wait; keep filtering (it is the headline technique).

## Exercises — core vs. extra vs. challenge

Core (1–7): Score Snapshot (build + `len`/`sum`), Scale Every Score (`transform-each` into a new list),
Round-to-Round Changes (differences via index loop), Repair the In-Place Sorter (the `sort()` → `None`
trap fix), Winning Position (argmax), Progress Totals (prefix sums), Above the Team Average (filter using the
average).
Challenges (8–9, `stretch`): Keep Approved Values (filter-into-list); Longest Word Position (argmax over
strings — the honest reason the index loop beats `max`).
Every extreme/average spec states the list has at least one item. Lists are built with `append` loops, never
comprehensions; only `append`/`sort` list methods are used.

## Common mistakes

- `scores = nums.sort()` sets `scores` to `None` (sort is in place) — use `sorted(nums)` when you need a
  value back.
- Seeding a find-extreme with `best = 0` instead of `best = nums[0]` (wrong on all-negative lists).
- Off-by-one with `range(len(nums))`; mixing the value loop and the index loop when you need the position.
- Modifying `nums` while looping over it, or expecting `sorted(nums)` to change `nums` (it does not).
- Reaching for an untaught method (`insert`/`remove`/`pop`/`index`/`count`) or a comprehension — build with
  `append` in a loop.

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
- Fast finishers: the two Challenges (filter, longest-word position), then combine — sort the kept list, or
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
- Ex8 (stretch) `keep_approved`: `([7,2,7,5],[2,5])`, `([3,3,8],[3,9])`, `([4,6],[1,2])`.
- Ex9 (stretch) `position_of_longest`: `["owl","panther","fox"]`, `["green","blue","gold"]`, `["sun","map","key"]`.
