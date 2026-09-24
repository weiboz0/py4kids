# Teacher Notes — Project 1: Algorithm Challenge

The non-themed, end-of-book capstone: an integrative problem set that pulls together the whole year —
number algorithms, list processing and searching, text/tallies, file I/O, and a small class.
It is the visible year-end goal students work toward.
It introduces nothing new; every problem reuses concepts already taught and practiced in Units 01–13.
Eleven problems sit in four milestones; each is function/class form, checked by calling it on fixed
inputs. Problems 4 and 5 are Challenges (rendered "Challenge") — reach work, not required for a pass.

## Goals

Students demonstrate that they can pick the right tool for an unfamiliar problem and assemble a correct,
tested solution end to end — the payoff of a year of practice.
Success looks like: a student reads a spec, writes a function/class that reproduces the worked sample,
and can explain WHY their loop/condition/data structure fits (a prime test needs a nested loop; a tally
needs a dict; a round-trip needs `with open`).
The four milestones map to the year's arcs: **Numbers** (`nth_prime`, `reverse_digits`), **Lists &
searching** (`top_three`, `merge_sorted`, `binary_search`), **Text, tallies & files**
(`count_substring`, `word_counts_from_file`, `most_common_word`, `group_by_parity`), and **Objects &
pipelines** (`RunningTally`, `running_totals_to_file`).

## Pacing

Budget: **two lessons of 60–90 minutes** (it is a project, not a checkpoint — collaboration and
iteration are encouraged). Suggested split:

- **Lesson 1 — Milestones 1–2** (numbers, then lists/searching). Warm up on `nth_prime`/`reverse_digits`,
  then the list algorithms; leave `merge_sorted`/`binary_search` (Challenges) for fast finishers or a
  whole-class walkthrough.
- **Lesson 2 — Milestones 3–4** (text/tallies/files, then the class + the file pipeline). The file
  problems reuse the Unit 12 self-contained pattern (write the scratch file, then read it); `RunningTally`
  reuses Unit 13's class shape.

Every file problem writes its own scratch `.txt` before reading it, so a cell runs the same way every
time; the scratch files are git-ignored.

## Common mistakes

- **`nth_prime`:** counting composites, or an off-by-one on the k-th prime; forgetting that 2 is prime
  (the inner `range(2, candidate)` is empty for candidate 2, so the flag stays True).
- **`reverse_digits`:** losing trailing zeros the wrong way — `reverse_digits(1200)` is `21`, not `0021`;
  the arithmetic build handles it because leading zeros never enter an int.
- **`top_three`:** trying to reverse a list with a tool we haven't taught — sort ascending with
  `sorted(...)` and read the last three by index; no `.copy()`, no `[::-1]`.
- **`merge_sorted`:** forgetting to drain the leftover tail of the longer list after one side runs out.
- **`binary_search`:** an infinite loop from not moving `lo`/`hi` past `mid`; returning a boolean instead
  of the index (or `-1`).
- **`count_substring`:** stopping the scan too early — the last start index is `len(text) - len(part)`;
  and counting OVERLAPS (`"aaaa"`/`"aa"` is 3, not 2).
- **File problems:** reading before writing; using string `+` to build a line instead of an f-string;
  forgetting `int(line.strip())` when a saved line must become a number.
- **`RunningTally`:** calling `highest()`/`describe()` before any `add` (`max([])` raises); forgetting
  `self`. Inside `describe`, call the methods with parentheses (`self.total()`/`self.highest()`) or the
  helpers (`sum(self.values)`/`max(self.values)`) — a bare `{self.total}` in the f-string prints a
  bound-method, and a bare `{total}` is a `NameError`.
- **Dict problems:** reaching for `for k, v in d.items()` (multiple assignment) — use `for key in d:` and
  `counts[key]`/`.get`.

## Discussion prompts

- Which problems needed a **dictionary**, and why was a dict better than two parallel lists?
- `merge_sorted` and `binary_search` both rely on the input already being **sorted** — what breaks if it
  is not, and how would you check?
- `count_substring` counts overlaps. When would you WANT non-overlapping counts instead, and how would
  the loop change?
- `RunningTally` bundles data (`self.values`) with behavior (`add`/`total`/`describe`). When is an object
  clearer than passing a list around to separate functions?
- Which of your solutions would still be correct on a much larger input, and which would get slow?

## Differentiation

- **Strugglers:** prioritize Milestone 1 + the non-Challenge list/tally problems (`top_three`,
  `word_counts_from_file`, `group_by_parity`); give the class skeleton for `RunningTally` and have them
  write one method.
- **Fast finishers:** the two Challenges (`merge_sorted`, `binary_search`), then extend `most_common_word`
  to return the top TWO, or make `RunningTally` also track the lowest value.
- **Middle tier:** rewrite `running_totals_to_file` to also return the grand total, or add a second
  `RunningTally` and compare two tallies.

## Rubric

Each problem is scored on: (1) correct function/class name and signature, (2) reproduces the worked
sample and passes the reference asserts on the fixed inputs, (3) stays within the taught toolkit (no
untaught methods/constructs). A capstone "pass" is **7 of the 9 core problems** correct, including at
least one from each of Milestones 1, 3, and 4 (numbers, a file/tally, and the class). The two Challenges
(P4/P5) are bonus — a full-marks project has them too. Partial credit: a function with the right shape
but one wrong branch or an off-by-one earns half; a class whose `__init__`/attributes are right but a
method is wrong earns half.

## Value plan (sample inputs)

Every fixture below is distinct across problems and audited against shipped Book 1b content
(`possession`/`cocoon`/`larch`/`maple`/`birch`/`cedar`/`wren`/`finch`/`kite`/`yoyo`/`seal`/`crane`/
`heron`/`ibis`/`koi` are all fresh). File problems write their own git-ignored scratch files.

- **P1 `nth_prime`:** 1→2, 5→11, 10→29 (+3→5).
- **P2 `reverse_digits`:** 1234→4321, 1200→21, 0→0 (+507→705).
- **P3 `top_three`:** [4,9,1,7,3]→[9,7,4], [5,5,2,8]→[8,5,5], [10,20,30]→[30,20,10].
- **P4 `merge_sorted` (Challenge):** [1,4,6]+[2,3,5]→[1,2,3,4,5,6], []+[2,9]→[2,9], [3,8,9]+[]→[3,8,9] (+[2,6,6]+[6,10]→[2,6,6,6,10], a duplicate-handling case).
- **P5 `binary_search` (Challenge):** ([1,3,5,7,9],7)→3, (…,4)→-1, ([2,4,6,8,10,12],2)→0 (+…,12→5).
- **P6 `count_substring`:** ("cocoon","co")→2, ("aaaa","aa")→3, ("possession","ss")→2.
- **P7 `word_counts_from_file`** (scratch `p7_words.txt`/`p7b_words.txt`/`p7c_words.txt`):
  fern/moss/fern/larch/moss/fern→{"fern":3,"moss":2,"larch":1}; maple/birch/maple/cedar→{"maple":2,
  "birch":1,"cedar":1}; wren×3/finch→{"wren":3,"finch":1}.
- **P8 `most_common_word`** (scratch `p8_words.txt`/`p8b_words.txt`/`p8c_words.txt`):
  kite×3/yoyo×2→"kite"; seal/crane×3/seal→"crane"; heron/ibis×2/koi→"ibis".
- **P9 `group_by_parity`:** [1,2,3,4]→{"even":[2,4],"odd":[1,3]}, [0,7,10]→{"even":[0,10],"odd":[7]},
  []→{"even":[],"odd":[]}.
- **P10 `RunningTally`:** add(5)→1, add(9)→2, add(0)→3; total()→14, highest()→9,
  describe()→"3 values, total 14, highest 9"; a second instance stays independent.
- **P11 `running_totals_to_file`** (scratch `p11_in.txt`/`p11_out.txt`, plus `p11b_*`/`p11c_*`):
  [5,3,2]→[5,8,10] (file "5\n8\n10\n"); [10,-4,6]→[10,6,12]; [0,12,8,1]→[0,12,20,21].
