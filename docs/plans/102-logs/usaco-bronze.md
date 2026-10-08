# Plan 102 Phase C — usaco-bronze check confirmation log

Book: `usaco-bronze` (*Contest Python: USACO Bronze*).
`classify --apply` proposed `check-fixtures` for all 161 items; every statement was then read in full, unit by unit.
`site.yaml` is now `classification: confirmed`, and `site-check --book usaco-bronze` reports PASS with no `FAIL:`.

## Summary

- Kinds before: fixtures 161 (proposed, untagged). Kinds after: fixtures 161 (confirmed `check-fixtures` tags).
- Retags: none. Every item is a stdin program with fixture pairs, and none is a short answer, trace-only or open-ended item.
- Statement edits (rule 2): none, so no allowed-diffs entries and no baseline revert notes are needed.
- `answer_format`: none authored. Fixture items are matched token-wise by the runner, and no item has a hidden canonical.
- `whitespace: exact` items: none.
- `also_check`: 140 items carry 205 entries, each copied verbatim from the statement (the site-check statement tie passes).
  They hold the method requirements an output check cannot see: required data structures (set, tuple, deque, dictionary, prefix array), required techniques (binary search, recursion, backtracking, BFS/DFS, two pointers, sieve, Euclid, repeated squaring), banned shortcuts (built-in conversion, `pow`, permutation libraries) and stated time bounds (`O(n)`), because the fixture runner has no time limit.
  The 21 items without `also_check` state only input/output rules, all verified by the fixtures.
- Sample check: for all 161 items, the statement's Sample Input equals one fixture `.in` and its Sample Output equals that pair's `.out` (token comparison; `u11e0010`'s Sample 1 is checked; `u10e0004` matches pair 2 and `d887b6c7` pair 3).
- Blind fixture validation is done by a separate agent; its per-item pass counts are recorded in a separate section, not here.

## Per-unit counts (all `fixtures`)

| entry | items |
|---|---|
| unit-01-reading-the-input | 9 |
| unit-02-boolean-logic | 9 |
| unit-03-complexity | 9 |
| unit-04-sets-tuples-sorting | 9 |
| unit-05-searching-complete-search | 9 |
| checkpoint-01-mock-contest-1 | 6 |
| unit-06-greedy | 9 |
| unit-07-simulation | 9 |
| unit-08-prefix-sums | 9 |
| checkpoint-02-mock-contest-2 | 6 |
| unit-09-recursion-backtracking | 9 |
| unit-10-stacks-queues-deques | 9 |
| unit-11-number-systems-bitwise | 10 |
| unit-12-binary-trees | 9 |
| checkpoint-03-mock-contest-3 | 7 |
| unit-13-grids-graphs | 9 |
| unit-14-two-pointers | 9 |
| checkpoint-04-mock-contest-4 | 7 |
| project-03-mock-contest | 8 |
| **total** | **161** |

## Observations (no change made)

- Unit 12 Exercises 1–4, 7 and 8 (`u12e0002`, `u12e0004`, `u12e0006`, `u12e0008`, `u12e0014`, `u12e0016`) give the tree input format (`N root`, then `value left right` per node) only through the notebook intro ("parse the tree into parallel arrays") and the sample, not in the statement.
  This is a statement-completeness issue outside rule 2, so it is left for the content gate. It does not change the check kind.
- `checkpoint-04` `d8ff98c9` ("Trace the Traversal") is worded as a trace, but it is a stdin program with 4 graph fixtures, so it stays `fixtures`.

## Concept attribution (rule 6)

The export listed 59 unattributed lesson code blocks and 1 unattributed item.
51 blocks and the item now carry a cell `concepts` list from usaco-bronze's own registry, and 8 blocks stay on the gap list.

| block / item | concepts |
|---|---|
| lesson `76bb396a` | `input-parse` |
| lesson `ace546cd` | `input-parse` |
| lesson `a28c2965` | `boolean-algebra` |
| lesson `fed78ff8` | `boolean-algebra` |
| lesson `5ad72816` | `boolean-algebra`, `code-tracing` |
| lesson `38163801` | `boolean-algebra` |
| lesson `b561e8a1` | `boolean-algebra` |
| lesson `7a2ef7ce` | `boolean-algebra` |
| lesson `7f29b87c` | `boolean-algebra`, `code-tracing` |
| lesson `1a91ce71` | `boolean-algebra` |
| lesson `777c9480` | `complexity` |
| lesson `76401aa7` | `complexity` |
| lesson `5835e927` | `complexity` |
| lesson `bcd49ff8` | `complexity` |
| lesson `8542e851` | `complexity` |
| lesson `78de945a` | `binary-search` |
| lesson `a56dda10` | `binary-search` |
| lesson `2053ea26` | `complete-search` |
| lesson `cb6280ec` | `complete-search` |
| lesson `e0fcb950` | `complete-search` |
| lesson `53644e6f` | `complete-search` |
| lesson `80f4f190` | `binary-search` |
| lesson `a6df115a` | `greedy` |
| lesson `ad3720d6` | `greedy` |
| lesson `6e4190e5` | `greedy` |
| lesson `e56072c5` | `greedy` |
| lesson `d8ccc7eb` | `greedy` |
| lesson `04556cfe` | `greedy` |
| lesson `139d05b9` | `simulation` |
| lesson `4c23c818` | `simulation` |
| lesson `a0cc08c2` | `simulation` |
| lesson `9be66d98` | `simulation` |
| lesson `5d4b4495` | `prefix-sum` |
| lesson `804f10b0` | `prefix-sum` |
| lesson `458938d1` | `prefix-sum` |
| lesson `6c7bc57d` | `grid-2d`, `prefix-sum` |
| lesson `0c178a37` | `grid-2d`, `prefix-sum` |
| lesson `ca9cf436` | `base-conversion` |
| lesson `e35891dc` | `base-conversion` |
| lesson `7ff6ae81` | `base-conversion` |
| lesson `60ac0a54` | `sieve` |
| lesson `f9bd2ce1` | `sieve` |
| lesson `7c12cd0a` | `sieve` |
| lesson `787c1f74` | `grid-2d` |
| lesson `959bd1ce` | `graph-repr` |
| lesson `2626c9d9` | `two-pointers` |
| lesson `af174007` | `two-pointers` |
| lesson `fb29700b` | `complexity`, `two-pointers` |
| lesson `d7d48e5e` | `two-pointers` |
| lesson `667e0929` | `two-pointers` |
| lesson `67008a3b` | `two-pointers` |
| item `checkpoint-03-mock-contest-3/checkpoint/af15971d` (Twin Prime Pairs) | `sieve` |

Each attribution names what the block's code does: truth tables, De Morgan and short-circuit (`boolean-algebra`), predict-then-run warm-ups (`code-tracing`), operation counting (`complexity`), halving loops (`binary-search`), pair or triple enumeration (`complete-search`), and so on.
A block that only prepares or sets up a later technique is not attributed to that technique.

### Concept gap list

- `usaco-bronze/unit-01-reading-the-input/lesson/b216ef95`: builds a space-separated output string from a literal list (output formatting); no registered output concept
- `usaco-bronze/unit-02-boolean-logic/lesson/807c8619`: counts `yes` answers with an accumulator; no registered concept (accumulator is not in the book registry)
- `usaco-bronze/unit-05-searching-complete-search/lesson/77e9dc4b`: linear search baseline; `binary-search` would pretend, `complete-search` (combinations) does not fit a single scan
- `usaco-bronze/unit-05-searching-complete-search/lesson/15547134`: the days-needed feasibility check for search-over-answer; it neither searches nor uses `greedy` (introduced in unit 06)
- `usaco-bronze/unit-09-recursion-backtracking/lesson/3ca8a84a`: base case `print(int("42"))`; no recursion is exercised
- `usaco-bronze/unit-09-recursion-backtracking/lesson/22038d5b`: parses one `(a+b)` level by index scanning; no recursion is exercised
- `usaco-bronze/unit-12-binary-trees/lesson/0ea3f119`: stores a tree in parallel arrays and reads the root's child; no traversal (only `tree-traversal` is registered)
- `usaco-bronze/unit-12-binary-trees/lesson/29077c2c`: iterative BST search down one path; not a pre/in/post-order traversal and not array binary search

## Items (one line per item)

- `usaco-bronze/unit-01-reading-the-input/exercises/a12d68e0` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 2 pairs; every stated requirement is verified by the output
- `usaco-bronze/unit-01-reading-the-input/exercises/c34f8a02` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; every stated requirement is verified by the output
- `usaco-bronze/unit-01-reading-the-input/exercises/e561ac24` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 2 pairs; every stated requirement is verified by the output
- `usaco-bronze/unit-01-reading-the-input/exercises/0783ce46` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-01-reading-the-input/exercises/29a5e068` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 2 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-01-reading-the-input/exercises/4bc7028a` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 2 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-01-reading-the-input/exercises/6de924ac` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 2 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-01-reading-the-input/exercises/8f0b46ce` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 2 pairs; every stated requirement is verified by the output
- `usaco-bronze/unit-01-reading-the-input/exercises/a12d68e1` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 2 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-02-boolean-logic/exercises/u02e0002` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; every stated requirement is verified by the output
- `usaco-bronze/unit-02-boolean-logic/exercises/u02e0004` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; every stated requirement is verified by the output
- `usaco-bronze/unit-02-boolean-logic/exercises/u02e0006` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 2 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-02-boolean-logic/exercises/u02e0008` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-02-boolean-logic/exercises/u02e0010` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; every stated requirement is verified by the output
- `usaco-bronze/unit-02-boolean-logic/exercises/u02e0012` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; every stated requirement is verified by the output
- `usaco-bronze/unit-02-boolean-logic/exercises/u02e0014` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 2 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-02-boolean-logic/exercises/u02e0016` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-02-boolean-logic/exercises/u02e0018` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 8 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-03-complexity/exercises/917b4c2e` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 2 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-03-complexity/exercises/2cfb6194` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 2 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-03-complexity/exercises/bc5190e4` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 2 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-03-complexity/exercises/f6bd4a18` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-03-complexity/exercises/75ed403b` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-03-complexity/exercises/e8207a3c` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-03-complexity/exercises/961c42fa` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-03-complexity/exercises/da0912bc` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-03-complexity/exercises/439fd0ae` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-04-sets-tuples-sorting/exercises/u04e0002` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-04-sets-tuples-sorting/exercises/u04e0004` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-04-sets-tuples-sorting/exercises/u04e0006` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-04-sets-tuples-sorting/exercises/u04e0008` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-04-sets-tuples-sorting/exercises/u04e0010` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 2 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-04-sets-tuples-sorting/exercises/u04e0012` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-04-sets-tuples-sorting/exercises/u04e0014` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-04-sets-tuples-sorting/exercises/u04e0016` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-04-sets-tuples-sorting/exercises/u04e0018` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-05-searching-complete-search/exercises/u05e0002` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 2 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-05-searching-complete-search/exercises/u05e0004` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 2 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-05-searching-complete-search/exercises/u05e0006` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 2 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-05-searching-complete-search/exercises/u05e0008` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-05-searching-complete-search/exercises/u05e0010` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-05-searching-complete-search/exercises/u05e0012` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-05-searching-complete-search/exercises/u05e0014` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-05-searching-complete-search/exercises/u05e0016` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-05-searching-complete-search/exercises/u05e0018` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-01-mock-contest-1/checkpoint/9ef4724a` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-01-mock-contest-1/checkpoint/26be8659` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-01-mock-contest-1/checkpoint/5ae91411` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-01-mock-contest-1/checkpoint/1d91dcc2` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 6 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-01-mock-contest-1/checkpoint/da215575` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-01-mock-contest-1/checkpoint/4876b88c` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-06-greedy/exercises/u06e0002` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-06-greedy/exercises/u06e0004` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-06-greedy/exercises/u06e0006` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-06-greedy/exercises/u06e0008` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-06-greedy/exercises/u06e0010` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-06-greedy/exercises/u06e0012` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-06-greedy/exercises/u06e0014` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-06-greedy/exercises/u06e0016` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-06-greedy/exercises/u06e0018` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 6 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-07-simulation/exercises/u07e0002` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; every stated requirement is verified by the output
- `usaco-bronze/unit-07-simulation/exercises/u07e0004` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; every stated requirement is verified by the output
- `usaco-bronze/unit-07-simulation/exercises/u07e0006` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-07-simulation/exercises/u07e0008` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; every stated requirement is verified by the output
- `usaco-bronze/unit-07-simulation/exercises/u07e0010` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; every stated requirement is verified by the output
- `usaco-bronze/unit-07-simulation/exercises/u07e0012` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; every stated requirement is verified by the output; simultaneous-update rule is observable in the output, so no also_check
- `usaco-bronze/unit-07-simulation/exercises/u07e0014` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; every stated requirement is verified by the output
- `usaco-bronze/unit-07-simulation/exercises/u07e0016` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 6 pairs; every stated requirement is verified by the output
- `usaco-bronze/unit-07-simulation/exercises/u07e0018` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; every stated requirement is verified by the output
- `usaco-bronze/unit-08-prefix-sums/exercises/u08e0002` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-08-prefix-sums/exercises/u08e0004` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-08-prefix-sums/exercises/u08e0006` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 6 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-08-prefix-sums/exercises/u08e0008` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-08-prefix-sums/exercises/u08e0010` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-08-prefix-sums/exercises/u08e0012` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-08-prefix-sums/exercises/u08e0014` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 6 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-08-prefix-sums/exercises/u08e0016` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-08-prefix-sums/exercises/u08e0018` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-02-mock-contest-2/checkpoint/8011e2c3` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-02-mock-contest-2/checkpoint/4e88d05b` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; every stated requirement is verified by the output; all rules are output-observable
- `usaco-bronze/checkpoint-02-mock-contest-2/checkpoint/c5be4a9e` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-02-mock-contest-2/checkpoint/c818a5c1` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-02-mock-contest-2/checkpoint/c0dde012` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; every stated requirement is verified by the output; all rules are output-observable
- `usaco-bronze/checkpoint-02-mock-contest-2/checkpoint/725de6ca` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 6 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-09-recursion-backtracking/exercises/u09e0002` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-09-recursion-backtracking/exercises/u09e0004` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-09-recursion-backtracking/exercises/u09e0006` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-09-recursion-backtracking/exercises/u09e0008` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-09-recursion-backtracking/exercises/u09e0010` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-09-recursion-backtracking/exercises/u09e0012` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-09-recursion-backtracking/exercises/u09e0014` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-09-recursion-backtracking/exercises/u09e0016` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-09-recursion-backtracking/exercises/u09e0018` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-10-stacks-queues-deques/exercises/u10e0002` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-10-stacks-queues-deques/exercises/u10e0004` — fixtures — stdin program; statement Sample Input/Output = fixture pair 2 (both sides); 6 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-10-stacks-queues-deques/exercises/u10e0006` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-10-stacks-queues-deques/exercises/u10e0008` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-10-stacks-queues-deques/exercises/u10e0010` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 2 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-10-stacks-queues-deques/exercises/u10e0012` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 3 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-10-stacks-queues-deques/exercises/u10e0014` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-10-stacks-queues-deques/exercises/u10e0016` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 3 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-10-stacks-queues-deques/exercises/u10e0018` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-11-number-systems-bitwise/exercises/u11e0002` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-11-number-systems-bitwise/exercises/u11e0004` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-11-number-systems-bitwise/exercises/u11e0006` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; every stated requirement is verified by the output; the `(1 << W) - 1` mask is a specification of the output (non-negative state), verified by it
- `usaco-bronze/unit-11-number-systems-bitwise/exercises/u11e0008` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-11-number-systems-bitwise/exercises/u11e0010` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 7 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-11-number-systems-bitwise/exercises/u11e0012` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-11-number-systems-bitwise/exercises/u11e0014` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-11-number-systems-bitwise/exercises/u11e0016` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-11-number-systems-bitwise/exercises/u11e0018` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-11-number-systems-bitwise/exercises/u11e0020` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-12-binary-trees/exercises/u12e0002` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-12-binary-trees/exercises/u12e0004` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-12-binary-trees/exercises/u12e0006` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-12-binary-trees/exercises/u12e0008` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-12-binary-trees/exercises/u12e0010` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-12-binary-trees/exercises/u12e0012` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 3 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-12-binary-trees/exercises/u12e0014` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-12-binary-trees/exercises/u12e0016` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-12-binary-trees/exercises/u12e0018` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-03-mock-contest-3/checkpoint/8a50ac24` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 6 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-03-mock-contest-3/checkpoint/cbe6b8a4` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 6 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-03-mock-contest-3/checkpoint/0a3a9763` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 9 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-03-mock-contest-3/checkpoint/b2360aa0` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 6 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-03-mock-contest-3/checkpoint/0ef41cdc` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 6 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-03-mock-contest-3/checkpoint/af15971d` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 6 pairs; also_check 1 (method requirement(s) the fixtures cannot verify); concepts ['sieve'] (was unattributed)
- `usaco-bronze/checkpoint-03-mock-contest-3/checkpoint/7a808c98` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 6 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-13-grids-graphs/exercises/u13e0002` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-13-grids-graphs/exercises/u13e0004` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-13-grids-graphs/exercises/u13e0006` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-13-grids-graphs/exercises/u13e0008` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-13-grids-graphs/exercises/u13e0010` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-13-grids-graphs/exercises/u13e0012` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-13-grids-graphs/exercises/u13e0014` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-13-grids-graphs/exercises/u13e0016` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-13-grids-graphs/exercises/u13e0018` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-14-two-pointers/exercises/u14e0002` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-14-two-pointers/exercises/u14e0004` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 3 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-14-two-pointers/exercises/u14e0006` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-14-two-pointers/exercises/u14e0008` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 3 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-14-two-pointers/exercises/u14e0010` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-14-two-pointers/exercises/u14e0012` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-14-two-pointers/exercises/u14e0014` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-14-two-pointers/exercises/u14e0016` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/unit-14-two-pointers/exercises/u14e0018` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-04-mock-contest-4/checkpoint/17f03587` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-04-mock-contest-4/checkpoint/abc7349b` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 6 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-04-mock-contest-4/checkpoint/4772215f` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 6 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-04-mock-contest-4/checkpoint/39a009c8` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 7 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-04-mock-contest-4/checkpoint/543ba2d2` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 6 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-04-mock-contest-4/checkpoint/248a0c70` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 7 pairs; also_check 3 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/checkpoint-04-mock-contest-4/checkpoint/d8ff98c9` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 4 pairs; every stated requirement is verified by the output; "trace" wording, but the student writes a stdin program for the given BFS routine and 4 pairs vary the graph, so fixtures (not predict)
- `usaco-bronze/project-03-mock-contest/brief/8276d4b4` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/project-03-mock-contest/brief/5193569a` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; every stated requirement is verified by the output; all rules are output-observable
- `usaco-bronze/project-03-mock-contest/brief/968bcef7` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/project-03-mock-contest/brief/5016dd6a` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 2 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/project-03-mock-contest/brief/8b7dbe4a` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/project-03-mock-contest/brief/3e299aa5` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/project-03-mock-contest/brief/d887b6c7` — fixtures — stdin program; statement Sample Input/Output = fixture pair 3 (both sides); 4 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)
- `usaco-bronze/project-03-mock-contest/brief/851efc33` — fixtures — stdin program; statement Sample Input/Output = fixture pair 1 (both sides); 5 pairs; also_check 1 (method requirement(s) the fixtures cannot verify)

## Independent blind fixture validation (Phase C requirement)

A separate Opus agent wrote its own solver for each of the 161 items. It worked on a filtered copy holding only the statement notebooks and the fixture directories: no reference solvers and no solution notebooks (verified: 0 `.py` files, 0 solution notebooks in the copy). It ran each solver on every pair with token matching.

**Result:** 161 items, **669/669 cases passed, 0 mismatches**, no timeouts.

Some blind solvers reached the same outputs with a different method than the statement asks for (a set lookup instead of binary search, for example). That confirms why such method requirements are listed in `also_check`: fixtures cannot verify a method.

Report: scratchpad `blind-solvers/usaco-bronze-report.md` (session-local).
