# Plan 102 Phase D log — acsl

Book: `acsl` (*Contest Python: ACSL*). 359 items: `answer` 287, `fixtures` 72.
Authored in worktree from `feature/plan-102-site-content-confirm` @ 8b07c78.

## Summary

- `classify --apply` tagged all 359 heading cells; every item was then read against its statement.
- Kinds before (proposed): answer 287, fixtures 72. After (confirmed): answer 287, fixtures 72.
- **Retags: none.** Every `check-answer` item is a short-answer question (tag `short-answer`) with exactly one `**Answer:**` line in its solution; every `check-fixtures` item is a stdin program whose statement Sample Input matches fixture pair 1 and whose statement Sample Output equals `1.out` (checked for all 72).
- **Statement edits: none** (Phase D makes no statement edits; acsl has no publish baseline).
- **`whitespace: exact` items: none.** No acsl statement makes a tab, indentation or alignment part of an answer.
- **`also_check`: none.** A short answer has one requirement, the answer itself; the fixtures items' method lines ("translate it into Python", "Predict, then verify") are study advice around an output-verified core.
- **`answer_format` authored on 175 `answer` items:** all 130 multi-token canonicals (59 letter-bearing + 71 digit-only lists; the plan's survey split 90 letter-bearing / 40 digit-only lists, measured here as 59 multi-token letter-bearing + 31 single-token letter-bearing = 90, and 71 digit-only multi-token), all 31 single-token letter-bearing canonicals (so all 90 letter-bearing formats are decided), and 14 single-token digit canonicals whose derived hint "a number" would mislead (bit strings with 0s on the left, a `*` pattern, fractions, a binary point, one single-solution "find all"). The remaining 112 single-token numeric canonicals keep the derived `{case: sensitive, hint: "a number"}`, which is the taught form.
- **Aliases `{"^": "↑"}`: 5 items** (unit-04 e-024, e-026, e-030, e-040; checkpoint-02 d0aca7dc). The plan and brief list a sixth, unit-04 **e-028**, but its statement (`A B C * + D E - /` to prefix) and canonical (`/ + A * B C - D E`) contain no power, so the alias would be dead; it was left off. Its hint is the plain prefix hint. Flagged for the caller.
- Case: `insensitive` only for the 5 hexadecimal items (rule 3). LISP (`true`/`NIL`, lists) stays sensitive: unit 07 fixes the spelling ("write "yes" as `true`", "in the same capital letters as the question"). Boolean expressions stay sensitive: no unit rule makes variable names case-free. Program output stays sensitive.
- Hints never contain their own item's canonical (checked mechanically; single letters and choice sets such as `true`/`NIL`, `YES`/`NO` excepted); example answers come from the lesson or exercise intro text.
- **Concepts:** 125 of 128 unattributed lesson blocks and all 15 unattributed `fixtures` items now carry a `concepts` list (the plan survey counted 1 unattributed item; the export on this branch reports 15, all fixtures; all were attributed). 3 lesson blocks stay on the gap list. Short answers stay exempt (287).
- `site-check --book acsl`: PASS, 0 FAIL, `classification: confirmed`, 0 derived letter formats, 0 unmatched samples.

## Per-unit counts

| entry | items | answer | fixtures | answer_format authored | aliases |
|---|---|---|---|---|---|
| unit-00-acsl-foundations | 15 | 5 | 10 | 5 | 0 |
| unit-01-computer-number-systems | 21 | 18 | 3 | 7 | 0 |
| unit-02-recursive-functions | 16 | 10 | 6 | 0 | 0 |
| unit-03-wdtpd-branching | 18 | 16 | 2 | 10 | 0 |
| checkpoint-01-contest-1-practice | 8 | 7 | 1 | 2 | 0 |
| unit-04-prefix-infix-postfix | 23 | 19 | 4 | 10 | 4 |
| unit-05-bit-string-flicking | 21 | 17 | 4 | 13 | 0 |
| unit-06-wdtpd-looping | 19 | 16 | 3 | 11 | 0 |
| unit-07-lisp | 21 | 17 | 4 | 9 | 0 |
| checkpoint-02-contest-2-practice | 9 | 8 | 1 | 4 | 1 |
| unit-08-boolean-algebra | 27 | 23 | 4 | 17 | 0 |
| unit-09-data-structures | 21 | 16 | 5 | 7 | 0 |
| unit-10-wdtpd-arrays | 19 | 16 | 3 | 15 | 0 |
| unit-11-fsas-regular-expressions | 18 | 15 | 3 | 13 | 0 |
| checkpoint-03-contest-3-practice | 9 | 8 | 1 | 5 | 0 |
| unit-12-graph-theory | 26 | 22 | 4 | 7 | 0 |
| unit-13-digital-electronics | 22 | 17 | 5 | 12 | 0 |
| unit-14-wdtpd-strings | 19 | 16 | 3 | 14 | 0 |
| unit-15-assembly-language | 18 | 13 | 5 | 9 | 0 |
| checkpoint-04-contest-4-practice | 9 | 8 | 1 | 5 | 0 |
| **total** | 359 | 287 | 72 | 175 | 5 |

## Answer-format categories and lesson citations

Each authored format is one of these categories; the item lines below name the category.

### BINFRAC (1 items)

- case `sensitive`, hint: "A base-2 number with a point, such as `0.011`, written without the small base subscript."
- Citation: unit 01 Lesson 3: "0.011₂ → 0.011 → **0.3₈**"; exercise intro: "Write a number in a base without the small base subscript".

### BIT (8 items)

- case `sensitive`, hint: "A bit string at its full length, with the 0s on the left kept (`00110`, not `110`)."
- Citation: unit 05 exercise intro: "Write every bit string at its **full length**, including 0s on the left: `00110`, not `110`."; checkpoint 2: "For a bit string, write every bit, at the full length given in the question."

### BITLIST (6 items)

- case `sensitive`, hint: "Every solution in increasing order, each a bit string at its full length (0s on the left kept: `00110`, not `110`), separated by a comma and a space."
- Citation: unit 05 Lesson: "A list of solutions is written in **increasing order**, as binary numbers, separated by a comma and a space, every string at full length."; exercise intro: "Write every bit string at its **full length**, including 0s on the left: `00110`, not `110`."; checkpoint 2: "For a list of bit strings, write them from smallest to largest, separated by a comma and a space."

### CYCLES (2 items)

- case `sensitive`, hint: "Each cycle as its vertex letters run together, from its start back to its start, the cycles in alphabetical order, separated by a comma and a space, as in `ABCA, ACBA`."
- Citation: unit 12 Lesson 1: "This book lists paths in alphabetical order, separated by a comma and a space."; exercise intro: "A path or a cycle is written as its vertex letters run together, such as `CADB` or `ABDA`." / "A list of paths or cycles is written in alphabetical order, separated by a comma and a space: `CABD, CADB`." Exercise intro (Elementary): "a cycle counts **once in each direction** (`ABCA` and `ACBA` are two cycles)"; statements: "Write each one from `C` back to `C`" / "each written from `A` back to `A`".

### FRAC (2 items)

- case `sensitive`, hint: "A base-10 fraction in lowest terms, written with `/`, such as `5/8`."
- Citation: unit 01 exercise intro: "write fractions in lowest terms, such as `5/8`."

### HEAP (2 items)

- case `sensitive`, hint: "The letters of the bottom row, left to right, run together with no spaces (as in `RORN`)."
- Citation: unit 09 Lesson 3: "The bottom row, left to right, is `RORN`."; exercise intro: "A heap row or a traversal is written as its letters **run together** (`RORN`)".

### HEX (4 items)

- case `insensitive`, hint: "A hexadecimal number: base-16 digits only, with capital letters A–F for the digits after 9 (as in `2D`), no base subscript and no leading zeros. Small letters are accepted too."
- Citation: unit 01 Lesson 1 table: "| 16 | hexadecimal ("hex") | 0 to 9, then A B C D E F |"; unit 01 exercise intro: "Write hex digits as capital letters (`2D`, not `2d`), leave out leading zeros"; checkpoint 1: "write only the digits, with capital letters `A`–`F` for hex digits, no base subscript and no leading zeros." Case-insensitive under rule 3 (hex digits are case-free); capitals stay the taught spelling.

### HEX6 (1 items)

- case `insensitive`, hint: "Six hex digits without the `#`, with capital letters A–F for the digits after 9 (as in `2D`). Small letters are accepted too."
- Citation: as HEX, plus the statement: "Write the answer as its six hex digits, without the `#`." and unit 01 Lesson: "A web colour is written `#RRGGBB`: two hex digits of red, two of green, then two of blue."

### LIST (6 items)

- case `sensitive`, hint: "A LISP list: round brackets, single spaces between items, the same capital letters as the question, and no quote mark, as in `(A (B C) D)`."
- Citation: unit 07 Lesson: "A **list** is some items inside round brackets, separated by spaces: `(23 HELLO 821)`."; exercise intro: "Write a list with single spaces and round brackets, in the same capital letters as the question: `(A (B C) D)`." / "Leave out the quote mark"; checkpoint 2: "For a LISP list, write it in parentheses with single spaces, such as `(A B C)`, using the capital letters the question uses." Case-sensitive: the unit's rule is "the same capital letters as the question".

### OPT_ALPHA (16 items)

- case `sensitive`, hint: "The labels of every option that qualifies, in alphabetical order, separated by a comma and a space, as in `A, C`; `NONE` if no option qualifies."
- case `sensitive`, hint: "The labels of every option that qualifies, in alphabetical order, separated by a comma and a space, as in `B, D`; `NONE` if no option qualifies."
- Citation: units 11/15 exercise intros: "Write the labels of every option that qualifies, in alphabetical order, separated by a comma and a space: `A, C, D`. If no option qualifies, write `NONE`."; checkpoint 3: "write the letters of every option that qualifies, in alphabetical order, separated by a comma and a space, such as `A, E`; write `NONE` if no option qualifies."; taught first in unit 08 Lesson 2 (OPT_ORDER sentence).

### OPT_ORDER (8 items)

- case `sensitive`, hint: "The labels of every correct option, in order, separated by a comma and a space, as in `A, C`; `NONE` if no option is correct."
- case `sensitive`, hint: "The labels of every correct option, in order, separated by a comma and a space, as in `B, D`; `NONE` if no option is correct."
- Citation: unit 08 Lesson 2: "Write the labels of every correct option, in order, separated by a comma and a space, such as `A, C`; write `NONE` if no option is correct."; units 12/13 exercise intros repeat it; unit 13 Lesson: "an option question is answered with the labels of every correct option, in order, such as `A, C`, or `NONE`."

### OUT (59 items)

- case `sensitive`, hint: "Exactly the one line the program outputs: values separated by one space, strings without quotation marks, and letters in the case the program prints them."
- Citation: unit 00 Lesson: "**Notice:** `print` puts one space between the things you give it." / "If the answer should be `3 4`, then `3,4` is wrong, and so is `The answer is 3 4`."; unit 03 Lesson 1: "`OUTPUT x, y` prints both values on one line; in this book, as in Python's `print(x, y)`, they are separated by one space."; unit 14 Lesson: "When an ACSL program outputs several values, as in `OUTPUT P, len(P)`, this book writes them on one line separated by one space, just as Python's `print(P, len(P))` does."; units 06/10/14 exercise intros: "Every program outputs exactly one line; when it outputs several values, they are separated by one space, and strings are written without quotation marks."; checkpoints 1/3/4: "For a program, write exactly the one line it outputs."

### PAIRS (2 items)

- case `sensitive`, hint: "Ordered pairs in counting-up order, with no spaces inside a pair, and a comma and a space between pairs, as in `(0,1), (1,0), (1,1)`; `NONE` if there are none."
- Citation: unit 08 Lesson 1: "This book lists pairs in counting-up order, with no spaces inside a pair, and a comma and a space between pairs: `(0,1), (1,0), (1,1)`." / "If no pair works, the answer is `NONE`."

### PATHS (2 items)

- case `sensitive`, hint: "Each path as its vertex letters run together, the paths in alphabetical order, separated by a comma and a space, as in `CABD, CADB`."
- Citation: unit 12 Lesson 1: "This book lists paths in alphabetical order, separated by a comma and a space."; exercise intro: "A path or a cycle is written as its vertex letters run together, such as `CADB` or `ABDA`." / "A list of paths or cycles is written in alphabetical order, separated by a comma and a space: `CABD, CADB`."

### PATTERN (1 items)

- case `sensitive`, hint: "One pattern at full length, with `*` for each free bit (as in `**110010`)."
- Citation: unit 05 Lesson: "Only if the question asks for it, write all the solutions as **one pattern** with `*` for each free bit, as in `**110010`."

### POP (2 items)

- case `sensitive`, hint: "One value: the letter or number popped, or `NIL` if the structure was empty."
- Citation: unit 09 Lesson 1: "If the stack or queue is **empty**, `POP()` has nothing to take, and the value it gives is **`NIL`**."; exercise intro: "A popped value is a number or a letter, and `NIL` when the stack or queue was empty."

### POST (3 items)

- case `sensitive`, hint: "A postfix expression: one space between tokens (as in `12 3 +`), with the operands kept in their original order."
- Citation: unit 04 Lesson 1: "Tokens (each number or operator) are written with one space between them, so `12 3 +` means twelve plus three."; exercise intro: "Write a prefix or postfix expression with **one space between tokens** (`+ 3 * 4 2`), write powers as `↑`, and never change the order of the operands."; checkpoint 2: "separate the tokens with single spaces and keep the operands in their original order."

### POST+CARET (4 items)

- case `sensitive`, hint: "A postfix expression: one space between tokens (as in `12 3 +`), with the operands kept in their original order. Powers are written `↑`; you may type `^` for `↑`."
- Citation: unit 04 Lesson 1: "Tokens (each number or operator) are written with one space between them, so `12 3 +` means twelve plus three."; exercise intro: "Write a prefix or postfix expression with **one space between tokens** (`+ 3 * 4 2`), write powers as `↑`, and never change the order of the operands."; checkpoint 2: "separate the tokens with single spaces and keep the operands in their original order."
- Alias citation: unit 04 Lesson 1: "Both mean the same thing, and on a keyboard you type it as `^`." / "This book always **answers** with `↑`." -> aliases {"^": "↑"}.

### PRE (3 items)

- case `sensitive`, hint: "A prefix expression: one space between tokens (as in `+ 3 * 4 2`), with the operands kept in their original order."
- Citation: unit 04 Lesson 1: "Tokens (each number or operator) are written with one space between them, so `12 3 +` means twelve plus three."; exercise intro: "Write a prefix or postfix expression with **one space between tokens** (`+ 3 * 4 2`), write powers as `↑`, and never change the order of the operands."; checkpoint 2: "separate the tokens with single spaces and keep the operands in their original order."

### PRE+CARET (1 items)

- case `sensitive`, hint: "A prefix expression: one space between tokens (as in `+ 3 * 4 2`), with the operands kept in their original order. Powers are written `↑`; you may type `^` for `↑`."
- Citation: unit 04 Lesson 1: "Tokens (each number or operator) are written with one space between them, so `12 3 +` means twelve plus three."; exercise intro: "Write a prefix or postfix expression with **one space between tokens** (`+ 3 * 4 2`), write powers as `↑`, and never change the order of the operands."; checkpoint 2: "separate the tokens with single spaces and keep the operands in their original order."
- Alias citation: unit 04 Lesson 1: "Both mean the same thing, and on a keyboard you type it as `^`." / "This book always **answers** with `↑`." -> aliases {"^": "↑"}.

### PRINTED (8 items)

- case `sensitive`, hint: "Every printed number in order, on one line, separated by single spaces, as in `13 8 3`."
- Citation: unit 15 Lesson: "When a question asks what a program prints, this book writes the printed numbers in order, on one line, separated by single spaces: `13 8 3`."; checkpoint 4: "every printed number in order, on one line, separated by single spaces."

### SOP (15 items)

- case `sensitive`, hint: "A sum of products: `~` NOT, `*` AND, `+` OR, with one space around each `*` and `+`; the fewest terms, then the fewest letters; letters in alphabetical order inside each term, and the terms in alphabetical order too, with a plain letter before its `~` form (as in `A * B + ~A * C`); `1` or `0` if it is always TRUE or always FALSE."
- Citation: unit 08 Lesson 2: "Inside a term, write the letters in alphabetical order (`~A * B`, not `B * ~A`); put the terms in alphabetical order too, with a plain letter before its `~` form (`A + ~B`, and `A * B + ~A * ~B`)." / "Use the fewest terms you can, and then the fewest letters." / "If the expression is always TRUE, the answer is `1`; if it is always FALSE, the answer is `0`."; unit 13 Lesson: "The answer is a **sum of products**, exactly as in Unit 8"; checkpoints 3/4: "`~` NOT, `*` AND, `+` OR, with a single space around `*` and `+`." Case-sensitive: no unit rule makes Boolean variable names case-free.

### STATE (1 items)

- case `sensitive`, hint: "A state, written exactly as the table names it (as in `q0`)."
- Citation: unit 11 exercise intro: "Write a state exactly as the table names it (`q1`)".

### TF7 (4 items)

- case `sensitive`, hint: "`true` or `NIL`, spelled as this book writes them: `true` in small letters, `NIL` in capitals."
- Citation: unit 07 Lesson: "ACSL writes "yes" as **`true`** and "no" as **`NIL`**." / "In this book, and on ACSL answer sheets, write `true`."; exercise intro: "Write the empty list, and "no", as `NIL`; write "yes" as `true`." Case-sensitive: the unit fixes the spelling `true` / `NIL`.

### TF8 (1 items)

- case `sensitive`, hint: "`TRUE` or `FALSE`, in capital letters."
- Citation: unit 08 exercise intro: "A statement question is answered `TRUE` or `FALSE`."; Lesson 1: "A **statement** is a sentence that is either TRUE or FALSE."

### TRAV (3 items)

- case `sensitive`, hint: "The letters in the order the traversal visits them, run together with no spaces (as in `RORN`)."
- Citation: unit 09 exercise intro: "A heap row or a traversal is written as its letters **run together** (`RORN`)"; Lesson 2: "- preorder: `AAMECIRN`".

### TRIPLES (4 items)

- case `sensitive`, hint: "Ordered triples in counting-up order, with no spaces inside a triple, and a comma and a space between triples, as in `(0,1,0), (1,1,1)`; `NONE` if there are none."
- Citation: unit 08 exercise intro: "Ordered pairs and triples are written with no spaces inside, in counting-up order, separated by a comma and a space: `(0,1), (1,1)`. Write `NONE` if there are none."; Lesson 1 (pairs sentence above); checkpoint 3: "write each as a bracketed tuple ... with no spaces inside, such as `(1,0,1)`, list them in ascending binary order, and separate them with a comma and a space."

### TUPLES13 (4 items)

- case `sensitive`, hint: "Tuples with the inputs in the order of the `INPUTS` line and no spaces inside, listed in counting-up order with a comma and a space between tuples, as in `(0,1,0), (1,1,1)`; `NONE` if there are none."
- Citation: unit 13 Lesson: "tuples are written with no spaces inside, in counting-up order, separated by a comma and a space: `(0,1,0), (0,1,1)`, or `NONE` if there are none"; exercise intro: "Tuples list the inputs in the order of the `INPUTS` line"; checkpoint 4: "in the order of the `INPUTS` line with no spaces inside ... in ascending binary order, and separate them with a comma and a space; write `NONE` if there are none."

### YESNO (2 items)

- case `sensitive`, hint: "`YES` or `NO`, in capital letters."
- Citation: unit 12 exercise intro: "A yes-or-no question is answered `YES` or `NO`."; statement: "Answer `YES` or `NO`."

## Items (one line each: key, final kind, reason)

### unit-00-acsl-foundations

- `acsl/unit-00-acsl-foundations/exercises/a19d52eb` — answer — Exercise 1: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-00-acsl-foundations/exercises/8a4028a4` — fixtures — Exercise 2 "Letter at a Position": stdin program, sample pair 1 = statement sample.
- `acsl/unit-00-acsl-foundations/exercises/19293a7c` — answer — Exercise 3: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-00-acsl-foundations/exercises/c1650251` — fixtures — Exercise 4 "Spread of the Scores": stdin program, sample pair 1 = statement sample.
- `acsl/unit-00-acsl-foundations/exercises/5d48a286` — fixtures — Exercise 5 "Evens and Odds Until Zero": stdin program, sample pair 1 = statement sample; concepts ['input-parse'].
- `acsl/unit-00-acsl-foundations/exercises/cb202366` — answer — Exercise 6: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-00-acsl-foundations/exercises/18eca952` — fixtures — Exercise 7 "Honor Roll": stdin program, sample pair 1 = statement sample.
- `acsl/unit-00-acsl-foundations/exercises/36167514` — fixtures — Exercise 8 "Lines That End in Zero": stdin program, sample pair 1 = statement sample.
- `acsl/unit-00-acsl-foundations/exercises/7919fee6` — answer — Exercise 9: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-00-acsl-foundations/exercises/1c6142c9` — fixtures — Exercise 10 "Farthest From Home": stdin program, sample pair 1 = statement sample.
- `acsl/unit-00-acsl-foundations/exercises/9fe063e5` — fixtures — Exercise 11 "Out-of-Order Pairs": stdin program, sample pair 1 = statement sample.
- `acsl/unit-00-acsl-foundations/exercises/97e2a653` — answer — Exercise 12: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-00-acsl-foundations/exercises/11f3abc1` — fixtures — Exercise 13 "Best Pair Product": stdin program, sample pair 1 = statement sample.
- `acsl/unit-00-acsl-foundations/exercises/3c8111d7` — fixtures — Exercise 14 "Making Change": stdin program, sample pair 1 = statement sample.
- `acsl/unit-00-acsl-foundations/exercises/e261d5d8` — fixtures — Exercise 15 "Triangle Sticks": stdin program, sample pair 1 = statement sample.

### unit-01-computer-number-systems

- `acsl/unit-01-computer-number-systems/exercises/e-040` — answer — Exercise 1: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-01-computer-number-systems/exercises/e-042` — answer — Exercise 2: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-01-computer-number-systems/exercises/e-044` — answer — Exercise 3: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-01-computer-number-systems/exercises/e-046` — answer — Exercise 4: short answer, one **Answer:** line; answer_format HEX, case insensitive.
- `acsl/unit-01-computer-number-systems/exercises/e-048` — answer — Exercise 5: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-01-computer-number-systems/exercises/e-050` — answer — Exercise 6: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-01-computer-number-systems/exercises/e-052` — answer — Exercise 7: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-01-computer-number-systems/exercises/e-054` — answer — Exercise 8: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-01-computer-number-systems/exercises/e-056` — answer — Exercise 9: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-01-computer-number-systems/exercises/e-058` — answer — Exercise 10: short answer, one **Answer:** line; answer_format HEX, case insensitive.
- `acsl/unit-01-computer-number-systems/exercises/e-060` — answer — Exercise 11: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-01-computer-number-systems/exercises/e-062` — answer — Exercise 12: short answer, one **Answer:** line; answer_format HEX, case insensitive.
- `acsl/unit-01-computer-number-systems/exercises/e-064` — answer — Exercise 13: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-01-computer-number-systems/exercises/e-066` — answer — Exercise 14: short answer, one **Answer:** line; answer_format HEX6, case insensitive.
- `acsl/unit-01-computer-number-systems/exercises/e-068` — fixtures — Exercise 15 "Digits in Another Base": stdin program, sample pair 1 = statement sample.
- `acsl/unit-01-computer-number-systems/exercises/e-070` — fixtures — Exercise 16 "The Biggest Card": stdin program, sample pair 1 = statement sample.
- `acsl/unit-01-computer-number-systems/exercises/e-072` — fixtures — Exercise 17 "Double Palindromes": stdin program, sample pair 1 = statement sample.
- `acsl/unit-01-computer-number-systems/exercises/e-074` — answer — Exercise 18: short answer, one **Answer:** line; answer_format FRAC, case sensitive.
- `acsl/unit-01-computer-number-systems/exercises/e-076` — answer — Exercise 19: short answer, one **Answer:** line; answer_format FRAC, case sensitive.
- `acsl/unit-01-computer-number-systems/exercises/e-078` — answer — Exercise 20: short answer, one **Answer:** line; answer_format BINFRAC, case sensitive.
- `acsl/unit-01-computer-number-systems/exercises/e-080` — answer — Exercise 21: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).

### unit-02-recursive-functions

- `acsl/unit-02-recursive-functions/exercises/75f972fa` — answer — Exercise 1: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-02-recursive-functions/exercises/0ff04372` — answer — Exercise 2: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-02-recursive-functions/exercises/fe9dfebf` — answer — Exercise 3: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-02-recursive-functions/exercises/80863612` — answer — Exercise 4: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-02-recursive-functions/exercises/4001d04c` — fixtures — Exercise 5 "Implement the Definition": stdin program, sample pair 1 = statement sample.
- `acsl/unit-02-recursive-functions/exercises/033f1c90` — answer — Exercise 6: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-02-recursive-functions/exercises/e07cc1a2` — answer — Exercise 7: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-02-recursive-functions/exercises/69eef4bb` — fixtures — Exercise 8 "Three Before": stdin program, sample pair 1 = statement sample.
- `acsl/unit-02-recursive-functions/exercises/63f51404` — fixtures — Exercise 9 "Two Numbers Meet": stdin program, sample pair 1 = statement sample.
- `acsl/unit-02-recursive-functions/exercises/d4d3e97c` — answer — Exercise 10: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-02-recursive-functions/exercises/c3fe911e` — fixtures — Exercise 11 "Ping and Pong": stdin program, sample pair 1 = statement sample; concepts ['recursion'].
- `acsl/unit-02-recursive-functions/exercises/5f23eb55` — answer — Exercise 12: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-02-recursive-functions/exercises/8a598b28` — answer — Exercise 13: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-02-recursive-functions/exercises/a70d36fe` — fixtures — Exercise 14 "Many Questions": stdin program, sample pair 1 = statement sample.
- `acsl/unit-02-recursive-functions/exercises/3151445d` — answer — Exercise 15: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-02-recursive-functions/exercises/16adc68e` — fixtures — Exercise 16 "Value and Calls": stdin program, sample pair 1 = statement sample.

### unit-03-wdtpd-branching

- `acsl/unit-03-wdtpd-branching/exercises/52d47c0a` — answer — Exercise 1: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-03-wdtpd-branching/exercises/0c40ee09` — answer — Exercise 2: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-03-wdtpd-branching/exercises/30181550` — answer — Exercise 3: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-03-wdtpd-branching/exercises/b396abfe` — answer — Exercise 4: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-03-wdtpd-branching/exercises/f16600e9` — answer — Exercise 5: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-03-wdtpd-branching/exercises/8629bc34` — fixtures — Exercise 6 "Parking Fee (predict, then verify)": stdin program, sample pair 1 = statement sample.
- `acsl/unit-03-wdtpd-branching/exercises/27f14698` — answer — Exercise 7: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-03-wdtpd-branching/exercises/a74edd6f` — answer — Exercise 8: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-03-wdtpd-branching/exercises/35c9216d` — answer — Exercise 9: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-03-wdtpd-branching/exercises/0a2a8241` — answer — Exercise 10: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-03-wdtpd-branching/exercises/56c02bd7` — answer — Exercise 11: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-03-wdtpd-branching/exercises/ccbad0f3` — answer — Exercise 12: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-03-wdtpd-branching/exercises/db28ebbe` — answer — Exercise 13: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-03-wdtpd-branching/exercises/d0ccc2d3` — answer — Exercise 14: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-03-wdtpd-branching/exercises/e640753c` — answer — Exercise 15: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-03-wdtpd-branching/exercises/fa8f523d` — fixtures — Exercise 16 "Square Steps (predict, then verify)": stdin program, sample pair 1 = statement sample; concepts ['code-tracing', 'acsl-pseudocode'].
- `acsl/unit-03-wdtpd-branching/exercises/d6b8b0c8` — answer — Exercise 17: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-03-wdtpd-branching/exercises/4bb2c8a5` — answer — Exercise 18: short answer, one **Answer:** line; answer_format OUT, case sensitive.

### checkpoint-01-contest-1-practice

- `acsl/checkpoint-01-contest-1-practice/checkpoint/eeccf748` — answer — Question 1: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/checkpoint-01-contest-1-practice/checkpoint/911be66b` — answer — Question 2: short answer, one **Answer:** line; answer_format HEX, case insensitive.
- `acsl/checkpoint-01-contest-1-practice/checkpoint/ff793770` — answer — Question 3: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/checkpoint-01-contest-1-practice/checkpoint/6465f30e` — answer — Question 4: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/checkpoint-01-contest-1-practice/checkpoint/7c14434b` — answer — Question 5: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/checkpoint-01-contest-1-practice/checkpoint/370fca77` — answer — Question 6: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/checkpoint-01-contest-1-practice/checkpoint/b911f785` — answer — Question 7: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/checkpoint-01-contest-1-practice/checkpoint/e44078f9` — fixtures — Question 8 "One Digit, Repeated": stdin program, sample pair 1 = statement sample; concepts ['base-conversion', 'complete-search'].

### unit-04-prefix-infix-postfix

- `acsl/unit-04-prefix-infix-postfix/exercises/e-002` — answer — Exercise 1: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-04-prefix-infix-postfix/exercises/e-004` — answer — Exercise 2: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-04-prefix-infix-postfix/exercises/e-006` — answer — Exercise 3: short answer, one **Answer:** line; answer_format POST, case sensitive.
- `acsl/unit-04-prefix-infix-postfix/exercises/e-008` — answer — Exercise 4: short answer, one **Answer:** line; answer_format PRE, case sensitive.
- `acsl/unit-04-prefix-infix-postfix/exercises/e-010` — answer — Exercise 5: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-04-prefix-infix-postfix/exercises/e-012` — answer — Exercise 6: short answer, one **Answer:** line; answer_format POST, case sensitive.
- `acsl/unit-04-prefix-infix-postfix/exercises/e-014` — answer — Exercise 7: short answer, one **Answer:** line; answer_format PRE, case sensitive.
- `acsl/unit-04-prefix-infix-postfix/exercises/e-016` — answer — Exercise 8: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-04-prefix-infix-postfix/exercises/e-018` — answer — Exercise 9: short answer, one **Answer:** line; answer_format POST, case sensitive.
- `acsl/unit-04-prefix-infix-postfix/exercises/e-020` — answer — Exercise 10: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-04-prefix-infix-postfix/exercises/e-022` — answer — Exercise 11: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-04-prefix-infix-postfix/exercises/e-024` — answer — Exercise 12: short answer, one **Answer:** line; answer_format PRE+CARET, case sensitive; aliases ^→↑.
- `acsl/unit-04-prefix-infix-postfix/exercises/e-026` — answer — Exercise 13: short answer, one **Answer:** line; answer_format POST+CARET, case sensitive; aliases ^→↑.
- `acsl/unit-04-prefix-infix-postfix/exercises/e-028` — answer — Exercise 14: short answer, one **Answer:** line; answer_format PRE, case sensitive.
- `acsl/unit-04-prefix-infix-postfix/exercises/e-030` — answer — Exercise 15: short answer, one **Answer:** line; answer_format POST+CARET, case sensitive; aliases ^→↑.
- `acsl/unit-04-prefix-infix-postfix/exercises/e-032` — fixtures — Exercise 16 "The Stack Calculator": stdin program, sample pair 1 = statement sample.
- `acsl/unit-04-prefix-infix-postfix/exercises/e-034` — fixtures — Exercise 17 "The Prefix Calculator": stdin program, sample pair 1 = statement sample.
- `acsl/unit-04-prefix-infix-postfix/exercises/e-036` — answer — Exercise 18: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-04-prefix-infix-postfix/exercises/e-038` — answer — Exercise 19: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-04-prefix-infix-postfix/exercises/e-040` — answer — Exercise 20: short answer, one **Answer:** line; answer_format POST+CARET, case sensitive; aliases ^→↑.
- `acsl/unit-04-prefix-infix-postfix/exercises/e-042` — fixtures — Exercise 21 "The Decimal Calculator": stdin program, sample pair 1 = statement sample.
- `acsl/unit-04-prefix-infix-postfix/exercises/e-044` — answer — Exercise 22: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-04-prefix-infix-postfix/exercises/e-046` — fixtures — Exercise 23 "Prefix to Postfix": stdin program, sample pair 1 = statement sample.

### unit-05-bit-string-flicking

- `acsl/unit-05-bit-string-flicking/exercises/e-002` — answer — Exercise 1: short answer, one **Answer:** line; answer_format BIT, case sensitive.
- `acsl/unit-05-bit-string-flicking/exercises/e-004` — answer — Exercise 2: short answer, one **Answer:** line; answer_format BIT, case sensitive.
- `acsl/unit-05-bit-string-flicking/exercises/e-006` — answer — Exercise 3: short answer, one **Answer:** line; answer_format BIT, case sensitive.
- `acsl/unit-05-bit-string-flicking/exercises/e-008` — answer — Exercise 4: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-05-bit-string-flicking/exercises/e-010` — answer — Exercise 5: short answer, one **Answer:** line; answer_format BIT, case sensitive.
- `acsl/unit-05-bit-string-flicking/exercises/e-012` — answer — Exercise 6: short answer, one **Answer:** line; answer_format BIT, case sensitive.
- `acsl/unit-05-bit-string-flicking/exercises/e-014` — answer — Exercise 7: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-05-bit-string-flicking/exercises/e-016` — answer — Exercise 8: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-05-bit-string-flicking/exercises/e-018` — answer — Exercise 9: short answer, one **Answer:** line; answer_format BITLIST, case sensitive.
- `acsl/unit-05-bit-string-flicking/exercises/e-020` — answer — Exercise 10: short answer, one **Answer:** line; answer_format PATTERN, case sensitive.
- `acsl/unit-05-bit-string-flicking/exercises/e-022` — answer — Exercise 11: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-05-bit-string-flicking/exercises/e-024` — answer — Exercise 12: short answer, one **Answer:** line; answer_format BITLIST, case sensitive.
- `acsl/unit-05-bit-string-flicking/exercises/e-026` — fixtures — Exercise 13 "The Cue Sheet": stdin program, sample pair 1 = statement sample.
- `acsl/unit-05-bit-string-flicking/exercises/e-028` — fixtures — Exercise 14 "Unary Chain": stdin program, sample pair 1 = statement sample.
- `acsl/unit-05-bit-string-flicking/exercises/e-030` — answer — Exercise 15: short answer, one **Answer:** line; answer_format BIT, case sensitive.
- `acsl/unit-05-bit-string-flicking/exercises/e-032` — answer — Exercise 16: short answer, one **Answer:** line; answer_format BIT, case sensitive.
- `acsl/unit-05-bit-string-flicking/exercises/e-034` — answer — Exercise 17: short answer, one **Answer:** line; answer_format BITLIST, case sensitive.
- `acsl/unit-05-bit-string-flicking/exercises/e-036` — answer — Exercise 18: short answer, one **Answer:** line; answer_format BITLIST, case sensitive.
- `acsl/unit-05-bit-string-flicking/exercises/e-038` — fixtures — Exercise 19 "Find Every x": stdin program, sample pair 1 = statement sample.
- `acsl/unit-05-bit-string-flicking/exercises/e-040` — answer — Exercise 20: short answer, one **Answer:** line; answer_format BITLIST, case sensitive.
- `acsl/unit-05-bit-string-flicking/exercises/e-042` — fixtures — Exercise 21 "The Whole Expression": stdin program, sample pair 1 = statement sample.

### unit-06-wdtpd-looping

- `acsl/unit-06-wdtpd-looping/exercises/c9aeac8c` — answer — Exercise 1: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-06-wdtpd-looping/exercises/d8eacfd1` — answer — Exercise 2: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-06-wdtpd-looping/exercises/fa934184` — answer — Exercise 3: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-06-wdtpd-looping/exercises/afe7eb96` — answer — Exercise 4: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-06-wdtpd-looping/exercises/9b7f57ab` — answer — Exercise 5: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-06-wdtpd-looping/exercises/5435da91` — answer — Exercise 6: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-06-wdtpd-looping/exercises/93a42355` — fixtures — Exercise 7 "Up and Down to One (predict, then verify)": stdin program, sample pair 1 = statement sample; concepts ['code-tracing', 'acsl-pseudocode'].
- `acsl/unit-06-wdtpd-looping/exercises/d3796d53` — answer — Exercise 8: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-06-wdtpd-looping/exercises/1c8d4cef` — answer — Exercise 9: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-06-wdtpd-looping/exercises/044994d3` — answer — Exercise 10: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-06-wdtpd-looping/exercises/9ccd01ab` — fixtures — Exercise 11 "Biggest Leftover (predict, then verify)": stdin program, sample pair 1 = statement sample.
- `acsl/unit-06-wdtpd-looping/exercises/cce0ac2b` — answer — Exercise 12: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-06-wdtpd-looping/exercises/7d665dc6` — answer — Exercise 13: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-06-wdtpd-looping/exercises/b65b7a35` — answer — Exercise 14: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-06-wdtpd-looping/exercises/e7c1fdf0` — answer — Exercise 15: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-06-wdtpd-looping/exercises/a6114ad2` — answer — Exercise 16: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-06-wdtpd-looping/exercises/60eb1dca` — fixtures — Exercise 17 "Pairs With a Multiple (predict, then verify)": stdin program, sample pair 1 = statement sample.
- `acsl/unit-06-wdtpd-looping/exercises/5290304a` — answer — Exercise 18: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-06-wdtpd-looping/exercises/63d63e74` — answer — Exercise 19: short answer, one **Answer:** line; answer_format OUT, case sensitive.

### unit-07-lisp

- `acsl/unit-07-lisp/exercises/1547cc11` — answer — Exercise 1: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-07-lisp/exercises/4cb4ccdd` — answer — Exercise 2: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-07-lisp/exercises/21b29780` — answer — Exercise 3: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-07-lisp/exercises/77163cb4` — fixtures — Exercise 4 "One-Call Calculator": stdin program, sample pair 1 = statement sample.
- `acsl/unit-07-lisp/exercises/f4178cbb` — answer — Exercise 5: short answer, one **Answer:** line; answer_format TF7, case sensitive.
- `acsl/unit-07-lisp/exercises/6f6abb00` — answer — Exercise 6: short answer, one **Answer:** line; answer_format TF7, case sensitive.
- `acsl/unit-07-lisp/exercises/e3da1150` — answer — Exercise 7: short answer, one **Answer:** line; answer_format TF7, case sensitive.
- `acsl/unit-07-lisp/exercises/fdbb272d` — answer — Exercise 8: short answer, one **Answer:** line; answer_format LIST, case sensitive.
- `acsl/unit-07-lisp/exercises/3ae21c2c` — answer — Exercise 9: short answer, one **Answer:** line; answer_format LIST, case sensitive.
- `acsl/unit-07-lisp/exercises/a390adc3` — answer — Exercise 10: short answer, one **Answer:** line; answer_format LIST, case sensitive.
- `acsl/unit-07-lisp/exercises/01430bfd` — answer — Exercise 11: short answer, one **Answer:** line; answer_format TF7, case sensitive.
- `acsl/unit-07-lisp/exercises/cdfbb60d` — answer — Exercise 12: short answer, one **Answer:** line; answer_format LIST, case sensitive.
- `acsl/unit-07-lisp/exercises/534096c6` — fixtures — Exercise 13 "REVERSE in Python": stdin program, sample pair 1 = statement sample.
- `acsl/unit-07-lisp/exercises/cc0952ba` — fixtures — Exercise 14 "CONS in Python": stdin program, sample pair 1 = statement sample.
- `acsl/unit-07-lisp/exercises/d92ef6da` — answer — Exercise 15: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-07-lisp/exercises/a62d6ba9` — answer — Exercise 16: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-07-lisp/exercises/5e1d6d7b` — answer — Exercise 17: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-07-lisp/exercises/68c7b70a` — answer — Exercise 18: short answer, one **Answer:** line; answer_format LIST, case sensitive.
- `acsl/unit-07-lisp/exercises/1c562367` — answer — Exercise 19: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-07-lisp/exercises/97012381` — fixtures — Exercise 20 "Shortcuts in Python": stdin program, sample pair 1 = statement sample.
- `acsl/unit-07-lisp/exercises/d2c16617` — answer — Exercise 21: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).

### checkpoint-02-contest-2-practice

- `acsl/checkpoint-02-contest-2-practice/checkpoint/d0aca7dc` — answer — Question 1: short answer, one **Answer:** line; answer_format POST+CARET, case sensitive; aliases ^→↑.
- `acsl/checkpoint-02-contest-2-practice/checkpoint/b11dc543` — answer — Question 2: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/checkpoint-02-contest-2-practice/checkpoint/b42c63e3` — answer — Question 3: short answer, one **Answer:** line; answer_format BIT, case sensitive.
- `acsl/checkpoint-02-contest-2-practice/checkpoint/50d44e45` — answer — Question 4: short answer, one **Answer:** line; answer_format BITLIST, case sensitive.
- `acsl/checkpoint-02-contest-2-practice/checkpoint/9e170522` — answer — Question 5: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/checkpoint-02-contest-2-practice/checkpoint/70e953b6` — answer — Question 6: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/checkpoint-02-contest-2-practice/checkpoint/0efef686` — answer — Question 7: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/checkpoint-02-contest-2-practice/checkpoint/7238df4e` — answer — Question 8: short answer, one **Answer:** line; answer_format LIST, case sensitive.
- `acsl/checkpoint-02-contest-2-practice/checkpoint/e48f5127` — fixtures — Question 9 "Brackets Away": stdin program, sample pair 1 = statement sample.

### unit-08-boolean-algebra

- `acsl/unit-08-boolean-algebra/exercises/e-002` — answer — Exercise 1: short answer, one **Answer:** line; answer_format TF8, case sensitive.
- `acsl/unit-08-boolean-algebra/exercises/e-004` — answer — Exercise 2: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-08-boolean-algebra/exercises/e-006` — answer — Exercise 3: short answer, one **Answer:** line; answer_format SOP, case sensitive.
- `acsl/unit-08-boolean-algebra/exercises/e-008` — answer — Exercise 4: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-08-boolean-algebra/exercises/e-010` — answer — Exercise 5: short answer, one **Answer:** line; answer_format OPT_ORDER, case sensitive.
- `acsl/unit-08-boolean-algebra/exercises/e-012` — answer — Exercise 6: short answer, one **Answer:** line; answer_format SOP, case sensitive.
- `acsl/unit-08-boolean-algebra/exercises/e-014` — answer — Exercise 7: short answer, one **Answer:** line; answer_format PAIRS, case sensitive.
- `acsl/unit-08-boolean-algebra/exercises/e-016` — answer — Exercise 8: short answer, one **Answer:** line; answer_format OPT_ORDER, case sensitive.
- `acsl/unit-08-boolean-algebra/exercises/e-018` — answer — Exercise 9: short answer, one **Answer:** line; answer_format PAIRS, case sensitive.
- `acsl/unit-08-boolean-algebra/exercises/e-020` — answer — Exercise 10: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-08-boolean-algebra/exercises/e-022` — answer — Exercise 11: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-08-boolean-algebra/exercises/e-024` — answer — Exercise 12: short answer, one **Answer:** line; answer_format SOP, case sensitive.
- `acsl/unit-08-boolean-algebra/exercises/e-026` — answer — Exercise 13: short answer, one **Answer:** line; answer_format SOP, case sensitive.
- `acsl/unit-08-boolean-algebra/exercises/e-028` — answer — Exercise 14: short answer, one **Answer:** line; answer_format TRIPLES, case sensitive.
- `acsl/unit-08-boolean-algebra/exercises/e-030` — answer — Exercise 15: short answer, one **Answer:** line; answer_format SOP, case sensitive.
- `acsl/unit-08-boolean-algebra/exercises/e-032` — answer — Exercise 16: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-08-boolean-algebra/exercises/e-034` — answer — Exercise 17: short answer, one **Answer:** line; answer_format TRIPLES, case sensitive.
- `acsl/unit-08-boolean-algebra/exercises/e-036` — fixtures — Exercise 18 "From Column to Solutions": stdin program, sample pair 1 = statement sample.
- `acsl/unit-08-boolean-algebra/exercises/e-038` — fixtures — Exercise 19 "The Sum-of-Products Solver": stdin program, sample pair 1 = statement sample.
- `acsl/unit-08-boolean-algebra/exercises/e-040` — answer — Exercise 20: short answer, one **Answer:** line; answer_format SOP, case sensitive.
- `acsl/unit-08-boolean-algebra/exercises/e-042` — answer — Exercise 21: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-08-boolean-algebra/exercises/e-044` — answer — Exercise 22: short answer, one **Answer:** line; answer_format SOP, case sensitive.
- `acsl/unit-08-boolean-algebra/exercises/e-046` — answer — Exercise 23: short answer, one **Answer:** line; answer_format TRIPLES, case sensitive.
- `acsl/unit-08-boolean-algebra/exercises/e-048` — answer — Exercise 24: short answer, one **Answer:** line; answer_format SOP, case sensitive.
- `acsl/unit-08-boolean-algebra/exercises/e-050` — fixtures — Exercise 25 "Order of Operations": stdin program, sample pair 1 = statement sample.
- `acsl/unit-08-boolean-algebra/exercises/e-052` — answer — Exercise 26: short answer, one **Answer:** line; answer_format SOP, case sensitive.
- `acsl/unit-08-boolean-algebra/exercises/e-054` — fixtures — Exercise 27 "Same or Different?": stdin program, sample pair 1 = statement sample.

### unit-09-data-structures

- `acsl/unit-09-data-structures/exercises/e-002` — answer — Exercise 1: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-09-data-structures/exercises/e-004` — answer — Exercise 2: short answer, one **Answer:** line; answer_format POP, case sensitive.
- `acsl/unit-09-data-structures/exercises/e-006` — answer — Exercise 3: short answer, one **Answer:** line; answer_format POP, case sensitive.
- `acsl/unit-09-data-structures/exercises/e-008` — answer — Exercise 4: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-09-data-structures/exercises/e-010` — answer — Exercise 5: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-09-data-structures/exercises/e-012` — answer — Exercise 6: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-09-data-structures/exercises/e-014` — fixtures — Exercise 7 "The Returns Desk": stdin program, sample pair 1 = statement sample.
- `acsl/unit-09-data-structures/exercises/e-016` — fixtures — Exercise 8 "How Deep Is Each Letter?": stdin program, sample pair 1 = statement sample; concepts ['acsl-data-structures'].
- `acsl/unit-09-data-structures/exercises/e-018` — answer — Exercise 9: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-09-data-structures/exercises/e-020` — answer — Exercise 10: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-09-data-structures/exercises/e-022` — answer — Exercise 11: short answer, one **Answer:** line; answer_format TRAV, case sensitive.
- `acsl/unit-09-data-structures/exercises/e-024` — answer — Exercise 12: short answer, one **Answer:** line; answer_format TRAV, case sensitive.
- `acsl/unit-09-data-structures/exercises/e-026` — answer — Exercise 13: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-09-data-structures/exercises/e-028` — answer — Exercise 14: short answer, one **Answer:** line; answer_format HEAP, case sensitive.
- `acsl/unit-09-data-structures/exercises/e-030` — answer — Exercise 15: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-09-data-structures/exercises/e-032` — fixtures — Exercise 16 "Three Walks": stdin program, sample pair 1 = statement sample.
- `acsl/unit-09-data-structures/exercises/e-034` — fixtures — Exercise 17 "Heap Rows": stdin program, sample pair 1 = statement sample.
- `acsl/unit-09-data-structures/exercises/e-036` — answer — Exercise 18: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-09-data-structures/exercises/e-038` — answer — Exercise 19: short answer, one **Answer:** line; answer_format HEAP, case sensitive.
- `acsl/unit-09-data-structures/exercises/e-040` — answer — Exercise 20: short answer, one **Answer:** line; answer_format TRAV, case sensitive.
- `acsl/unit-09-data-structures/exercises/e-042` — fixtures — Exercise 21 "Pruning the Tree": stdin program, sample pair 1 = statement sample.

### unit-10-wdtpd-arrays

- `acsl/unit-10-wdtpd-arrays/exercises/d58a828d` — answer — Exercise 1: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-10-wdtpd-arrays/exercises/c91c1886` — answer — Exercise 2: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-10-wdtpd-arrays/exercises/b7d59c39` — answer — Exercise 3: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-10-wdtpd-arrays/exercises/7c9c0e85` — answer — Exercise 4: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-10-wdtpd-arrays/exercises/b59b6dc0` — answer — Exercise 5: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-10-wdtpd-arrays/exercises/9d9b8421` — answer — Exercise 6: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-10-wdtpd-arrays/exercises/c50d8794` — answer — Exercise 7: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-10-wdtpd-arrays/exercises/63ede1d0` — fixtures — Exercise 8 "Leaders From the Right (predict, then verify)": stdin program, sample pair 1 = statement sample.
- `acsl/unit-10-wdtpd-arrays/exercises/8825c521` — answer — Exercise 9: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-10-wdtpd-arrays/exercises/dd73c17e` — answer — Exercise 10: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-10-wdtpd-arrays/exercises/8e33229f` — answer — Exercise 11: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-10-wdtpd-arrays/exercises/1e554a86` — answer — Exercise 12: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-10-wdtpd-arrays/exercises/59fd0235` — answer — Exercise 13: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-10-wdtpd-arrays/exercises/a55eadbb` — fixtures — Exercise 14 "Frame and Middle (predict, then verify)": stdin program, sample pair 1 = statement sample.
- `acsl/unit-10-wdtpd-arrays/exercises/ed29c57f` — answer — Exercise 15: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-10-wdtpd-arrays/exercises/1ee5e3e7` — answer — Exercise 16: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-10-wdtpd-arrays/exercises/76cd9bb9` — fixtures — Exercise 17 "Pascal's Triangle (predict, then verify)": stdin program, sample pair 1 = statement sample.
- `acsl/unit-10-wdtpd-arrays/exercises/c64b4187` — answer — Exercise 18: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-10-wdtpd-arrays/exercises/d8a8467a` — answer — Exercise 19: short answer, one **Answer:** line; answer_format OUT, case sensitive.

### unit-11-fsas-regular-expressions

- `acsl/unit-11-fsas-regular-expressions/exercises/e2372bb7` — answer — Exercise 1: short answer, one **Answer:** line; answer_format OPT_ALPHA, case sensitive.
- `acsl/unit-11-fsas-regular-expressions/exercises/f86170b6` — answer — Exercise 2: short answer, one **Answer:** line; answer_format STATE, case sensitive.
- `acsl/unit-11-fsas-regular-expressions/exercises/41d2c433` — answer — Exercise 3: short answer, one **Answer:** line; answer_format OPT_ALPHA, case sensitive.
- `acsl/unit-11-fsas-regular-expressions/exercises/4e2439c4` — fixtures — Exercise 4 "FSA Simulator": stdin program, sample pair 1 = statement sample.
- `acsl/unit-11-fsas-regular-expressions/exercises/0927f401` — answer — Exercise 5: short answer, one **Answer:** line; answer_format OPT_ALPHA, case sensitive.
- `acsl/unit-11-fsas-regular-expressions/exercises/f9dc79c0` — answer — Exercise 6: short answer, one **Answer:** line; answer_format OPT_ALPHA, case sensitive.
- `acsl/unit-11-fsas-regular-expressions/exercises/3d25e5ee` — answer — Exercise 7: short answer, one **Answer:** line; answer_format OPT_ALPHA, case sensitive.
- `acsl/unit-11-fsas-regular-expressions/exercises/79f1b71d` — answer — Exercise 8: short answer, one **Answer:** line; answer_format OPT_ALPHA, case sensitive.
- `acsl/unit-11-fsas-regular-expressions/exercises/1228f477` — answer — Exercise 9: short answer, one **Answer:** line; answer_format OPT_ALPHA, case sensitive.
- `acsl/unit-11-fsas-regular-expressions/exercises/e886b066` — answer — Exercise 10: short answer, one **Answer:** line; answer_format OPT_ALPHA, case sensitive.
- `acsl/unit-11-fsas-regular-expressions/exercises/5326950e` — answer — Exercise 11: short answer, one **Answer:** line; answer_format OPT_ALPHA, case sensitive.
- `acsl/unit-11-fsas-regular-expressions/exercises/5f561f5c` — fixtures — Exercise 12 "Pattern Checker": stdin program, sample pair 1 = statement sample.
- `acsl/unit-11-fsas-regular-expressions/exercises/c9c144dc` — answer — Exercise 13: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-11-fsas-regular-expressions/exercises/2359a6b6` — answer — Exercise 14: short answer, one **Answer:** line; answer_format OPT_ALPHA, case sensitive.
- `acsl/unit-11-fsas-regular-expressions/exercises/cf8f9d3b` — answer — Exercise 15: short answer, one **Answer:** line; answer_format OPT_ALPHA, case sensitive.
- `acsl/unit-11-fsas-regular-expressions/exercises/6663196e` — answer — Exercise 16: short answer, one **Answer:** line; answer_format OPT_ALPHA, case sensitive.
- `acsl/unit-11-fsas-regular-expressions/exercises/bc325c67` — fixtures — Exercise 17 "Full Pattern Checker": stdin program, sample pair 1 = statement sample.
- `acsl/unit-11-fsas-regular-expressions/exercises/4e3d07ae` — answer — Exercise 18: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).

### checkpoint-03-contest-3-practice

- `acsl/checkpoint-03-contest-3-practice/checkpoint/d9966078` — answer — Question 1: short answer, one **Answer:** line; answer_format SOP, case sensitive.
- `acsl/checkpoint-03-contest-3-practice/checkpoint/fa5b4f81` — answer — Question 2: short answer, one **Answer:** line; answer_format TRIPLES, case sensitive.
- `acsl/checkpoint-03-contest-3-practice/checkpoint/d00bfa8e` — answer — Question 3: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/checkpoint-03-contest-3-practice/checkpoint/aeca9805` — answer — Question 4: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/checkpoint-03-contest-3-practice/checkpoint/cf4d556b` — answer — Question 5: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/checkpoint-03-contest-3-practice/checkpoint/be6237c2` — answer — Question 6: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/checkpoint-03-contest-3-practice/checkpoint/29e11049` — answer — Question 7: short answer, one **Answer:** line; answer_format OPT_ALPHA, case sensitive.
- `acsl/checkpoint-03-contest-3-practice/checkpoint/594810e5` — answer — Question 8: short answer, one **Answer:** line; answer_format OPT_ALPHA, case sensitive.
- `acsl/checkpoint-03-contest-3-practice/checkpoint/8e43f595` — fixtures — Question 9 "The Counting Line": stdin program, sample pair 1 = statement sample.

### unit-12-graph-theory

- `acsl/unit-12-graph-theory/exercises/e-002` — answer — Exercise 1: short answer, one **Answer:** line; answer_format PATHS, case sensitive.
- `acsl/unit-12-graph-theory/exercises/e-004` — answer — Exercise 2: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-12-graph-theory/exercises/e-006` — answer — Exercise 3: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-12-graph-theory/exercises/e-008` — answer — Exercise 4: short answer, one **Answer:** line; answer_format YESNO, case sensitive.
- `acsl/unit-12-graph-theory/exercises/e-010` — answer — Exercise 5: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-12-graph-theory/exercises/e-012` — answer — Exercise 6: short answer, one **Answer:** line; answer_format PATHS, case sensitive.
- `acsl/unit-12-graph-theory/exercises/e-014` — answer — Exercise 7: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-12-graph-theory/exercises/e-016` — answer — Exercise 8: short answer, one **Answer:** line; answer_format CYCLES, case sensitive.
- `acsl/unit-12-graph-theory/exercises/e-018` — answer — Exercise 9: short answer, one **Answer:** line; answer_format YESNO, case sensitive.
- `acsl/unit-12-graph-theory/exercises/e-020` — answer — Exercise 10: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-12-graph-theory/exercises/e-022` — answer — Exercise 11: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-12-graph-theory/exercises/e-024` — answer — Exercise 12: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-12-graph-theory/exercises/e-026` — answer — Exercise 13: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-12-graph-theory/exercises/e-028` — answer — Exercise 14: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-12-graph-theory/exercises/e-030` — answer — Exercise 15: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-12-graph-theory/exercises/e-032` — answer — Exercise 16: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-12-graph-theory/exercises/e-034` — fixtures — Exercise 17 "The Road Table": stdin program, sample pair 1 = statement sample.
- `acsl/unit-12-graph-theory/exercises/e-036` — fixtures — Exercise 18 "Two Hops and Three": stdin program, sample pair 1 = statement sample.
- `acsl/unit-12-graph-theory/exercises/e-038` — answer — Exercise 19: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-12-graph-theory/exercises/e-040` — answer — Exercise 20: short answer, one **Answer:** line; answer_format OPT_ORDER, case sensitive.
- `acsl/unit-12-graph-theory/exercises/e-042` — answer — Exercise 21: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-12-graph-theory/exercises/e-044` — answer — Exercise 22: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-12-graph-theory/exercises/e-046` — fixtures — Exercise 23 "Cheapest Ride Finder": stdin program, sample pair 1 = statement sample.
- `acsl/unit-12-graph-theory/exercises/e-048` — answer — Exercise 24: short answer, one **Answer:** line; answer_format CYCLES, case sensitive.
- `acsl/unit-12-graph-theory/exercises/e-050` — answer — Exercise 25: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-12-graph-theory/exercises/e-052` — fixtures — Exercise 26 "Round Trips": stdin program, sample pair 1 = statement sample.

### unit-13-digital-electronics

- `acsl/unit-13-digital-electronics/exercises/e-002` — answer — Exercise 1: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-13-digital-electronics/exercises/e-004` — answer — Exercise 2: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-13-digital-electronics/exercises/e-006` — answer — Exercise 3: short answer, one **Answer:** line; answer_format TUPLES13, case sensitive.
- `acsl/unit-13-digital-electronics/exercises/e-008` — answer — Exercise 4: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-13-digital-electronics/exercises/e-010` — answer — Exercise 5: short answer, one **Answer:** line; answer_format OPT_ORDER, case sensitive.
- `acsl/unit-13-digital-electronics/exercises/e-012` — answer — Exercise 6: short answer, one **Answer:** line; answer_format OPT_ORDER, case sensitive.
- `acsl/unit-13-digital-electronics/exercises/e-014` — answer — Exercise 7: short answer, one **Answer:** line; answer_format SOP, case sensitive.
- `acsl/unit-13-digital-electronics/exercises/e-016` — answer — Exercise 8: short answer, one **Answer:** line; answer_format OPT_ORDER, case sensitive.
- `acsl/unit-13-digital-electronics/exercises/e-018` — answer — Exercise 9: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-13-digital-electronics/exercises/e-020` — fixtures — Exercise 10 "Gate by Gate": stdin program, sample pair 1 = statement sample.
- `acsl/unit-13-digital-electronics/exercises/e-022` — fixtures — Exercise 11 "Trace the Circuit": stdin program, sample pair 1 = statement sample.
- `acsl/unit-13-digital-electronics/exercises/e-024` — fixtures — Exercise 12 "The Result Column": stdin program, sample pair 1 = statement sample; concepts ['logic-gates', 'input-parse'].
- `acsl/unit-13-digital-electronics/exercises/e-026` — answer — Exercise 13: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-13-digital-electronics/exercises/e-028` — answer — Exercise 14: short answer, one **Answer:** line; answer_format TUPLES13, case sensitive.
- `acsl/unit-13-digital-electronics/exercises/e-030` — answer — Exercise 15: short answer, one **Answer:** line; answer_format SOP, case sensitive.
- `acsl/unit-13-digital-electronics/exercises/e-032` — answer — Exercise 16: short answer, one **Answer:** line; answer_format SOP, case sensitive.
- `acsl/unit-13-digital-electronics/exercises/e-034` — answer — Exercise 17: short answer, one **Answer:** line; answer_format TUPLES13, case sensitive.
- `acsl/unit-13-digital-electronics/exercises/e-036` — fixtures — Exercise 18 "Every Solution": stdin program, sample pair 1 = statement sample; concepts ['logic-gates', 'input-parse'].
- `acsl/unit-13-digital-electronics/exercises/e-038` — answer — Exercise 19: short answer, one **Answer:** line; answer_format OPT_ORDER, case sensitive.
- `acsl/unit-13-digital-electronics/exercises/e-040` — answer — Exercise 20: short answer, one **Answer:** line; answer_format OPT_ORDER, case sensitive.
- `acsl/unit-13-digital-electronics/exercises/e-042` — answer — Exercise 21: short answer, one **Answer:** line; answer_format SOP, case sensitive.
- `acsl/unit-13-digital-electronics/exercises/e-044` — fixtures — Exercise 22 "Same Circuit?": stdin program, sample pair 1 = statement sample; concepts ['logic-gates', 'input-parse'].

### unit-14-wdtpd-strings

- `acsl/unit-14-wdtpd-strings/exercises/a54da589` — answer — Exercise 1: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-14-wdtpd-strings/exercises/024cedca` — answer — Exercise 2: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-14-wdtpd-strings/exercises/1f485ade` — answer — Exercise 3: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-14-wdtpd-strings/exercises/a7c48e1b` — answer — Exercise 4: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-14-wdtpd-strings/exercises/ac3b3788` — answer — Exercise 5: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-14-wdtpd-strings/exercises/80d8b772` — answer — Exercise 6: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-14-wdtpd-strings/exercises/c604a077` — answer — Exercise 7: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-14-wdtpd-strings/exercises/44940476` — fixtures — Exercise 8 "Vowel Squeeze (predict, then verify)": stdin program, sample pair 1 = statement sample; concepts ['code-tracing', 'acsl-pseudocode'].
- `acsl/unit-14-wdtpd-strings/exercises/494f6d6e` — answer — Exercise 9: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-14-wdtpd-strings/exercises/892676fa` — answer — Exercise 10: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-14-wdtpd-strings/exercises/b7462ec6` — answer — Exercise 11: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-14-wdtpd-strings/exercises/8724e18e` — answer — Exercise 12: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-14-wdtpd-strings/exercises/22ad4d5d` — fixtures — Exercise 13 "Longest Run (predict, then verify)": stdin program, sample pair 1 = statement sample; concepts ['code-tracing', 'acsl-pseudocode'].
- `acsl/unit-14-wdtpd-strings/exercises/c8e717c9` — answer — Exercise 14: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-14-wdtpd-strings/exercises/a960a37a` — answer — Exercise 15: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-14-wdtpd-strings/exercises/6200941c` — answer — Exercise 16: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/unit-14-wdtpd-strings/exercises/04282687` — fixtures — Exercise 17 "Palindrome Sentences (predict, then verify)": stdin program, sample pair 1 = statement sample; concepts ['code-tracing', 'acsl-pseudocode'].
- `acsl/unit-14-wdtpd-strings/exercises/e9797ad7` — answer — Exercise 18: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-14-wdtpd-strings/exercises/73827ea2` — answer — Exercise 19: short answer, one **Answer:** line; answer_format OUT, case sensitive.

### unit-15-assembly-language

- `acsl/unit-15-assembly-language/exercises/83de04e8` — answer — Exercise 1: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-15-assembly-language/exercises/891dbd65` — answer — Exercise 2: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-15-assembly-language/exercises/518903aa` — answer — Exercise 3: short answer, one **Answer:** line; answer_format PRINTED, case sensitive.
- `acsl/unit-15-assembly-language/exercises/2468c666` — fixtures — Exercise 4 "Straight-Line Translator": stdin program, sample pair 1 = statement sample; concepts ['acsl-assembly'].
- `acsl/unit-15-assembly-language/exercises/40bc78e9` — answer — Exercise 5: short answer, one **Answer:** line; answer_format PRINTED, case sensitive.
- `acsl/unit-15-assembly-language/exercises/987a91ab` — answer — Exercise 6: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-15-assembly-language/exercises/a8bb3f09` — answer — Exercise 7: short answer, one **Answer:** line; answer_format PRINTED, case sensitive.
- `acsl/unit-15-assembly-language/exercises/7b738935` — answer — Exercise 8: short answer, one **Answer:** line; answer_format OPT_ALPHA, case sensitive.
- `acsl/unit-15-assembly-language/exercises/e9a45b95` — answer — Exercise 9: short answer, one **Answer:** line; answer_format PRINTED, case sensitive.
- `acsl/unit-15-assembly-language/exercises/6df28308` — fixtures — Exercise 10 "Digit Loop Translator": stdin program, sample pair 1 = statement sample; concepts ['acsl-assembly'].
- `acsl/unit-15-assembly-language/exercises/b9df026e` — fixtures — Exercise 11 "Accumulator Calculator": stdin program, sample pair 1 = statement sample.
- `acsl/unit-15-assembly-language/exercises/06930b7c` — answer — Exercise 12: short answer, one **Answer:** line; answer_format PRINTED, case sensitive.
- `acsl/unit-15-assembly-language/exercises/9c30192d` — answer — Exercise 13: short answer, one **Answer:** line; answer_format OPT_ALPHA, case sensitive.
- `acsl/unit-15-assembly-language/exercises/31700519` — answer — Exercise 14: short answer, one **Answer:** line; answer_format PRINTED, case sensitive.
- `acsl/unit-15-assembly-language/exercises/ff71d45c` — answer — Exercise 15: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/unit-15-assembly-language/exercises/a22bb998` — fixtures — Exercise 16 "Halve or Triple Translator": stdin program, sample pair 1 = statement sample; concepts ['acsl-assembly'].
- `acsl/unit-15-assembly-language/exercises/cd7889f5` — fixtures — Exercise 17 "Assembly Interpreter": stdin program, sample pair 1 = statement sample.
- `acsl/unit-15-assembly-language/exercises/c5ddc410` — answer — Exercise 18: short answer, one **Answer:** line; answer_format PRINTED, case sensitive.

### checkpoint-04-contest-4-practice

- `acsl/checkpoint-04-contest-4-practice/checkpoint/cbbc3277` — answer — Question 1: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/checkpoint-04-contest-4-practice/checkpoint/0b4d4be6` — answer — Question 2: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/checkpoint-04-contest-4-practice/checkpoint/d53f3ad4` — answer — Question 3: short answer, one **Answer:** line; answer_format TUPLES13, case sensitive.
- `acsl/checkpoint-04-contest-4-practice/checkpoint/dba84224` — answer — Question 4: short answer, one **Answer:** line; answer_format SOP, case sensitive.
- `acsl/checkpoint-04-contest-4-practice/checkpoint/ff235aae` — answer — Question 5: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/checkpoint-04-contest-4-practice/checkpoint/4a015c2f` — answer — Question 6: short answer, one **Answer:** line; answer_format OUT, case sensitive.
- `acsl/checkpoint-04-contest-4-practice/checkpoint/64957843` — answer — Question 7: short answer, one **Answer:** line; derived format "a number" kept (single numeric token).
- `acsl/checkpoint-04-contest-4-practice/checkpoint/463de814` — answer — Question 8: short answer, one **Answer:** line; answer_format PRINTED, case sensitive.
- `acsl/checkpoint-04-contest-4-practice/checkpoint/2196753b` — fixtures — Question 9 "What Kind of Route?": stdin program, sample pair 1 = statement sample.

## Concept attributions

Lesson code blocks (cell `metadata.concepts`), 125:

- `acsl/unit-00-acsl-foundations/lesson/7f7067cf`: code-tracing
- `acsl/unit-00-acsl-foundations/lesson/86aa395e`: input-parse
- `acsl/unit-00-acsl-foundations/lesson/b355e980`: input-parse
- `acsl/unit-00-acsl-foundations/lesson/a6bd68cb`: input-parse
- `acsl/unit-00-acsl-foundations/lesson/11fde602`: input-parse
- `acsl/unit-00-acsl-foundations/lesson/be4c280b`: complete-search
- `acsl/unit-01-computer-number-systems/lesson/l-007`: base-conversion
- `acsl/unit-01-computer-number-systems/lesson/l-022`: base-conversion
- `acsl/unit-01-computer-number-systems/lesson/l-024`: base-conversion
- `acsl/unit-01-computer-number-systems/lesson/l-029`: base-conversion
- `acsl/unit-01-computer-number-systems/lesson/l-031`: base-conversion
- `acsl/unit-01-computer-number-systems/lesson/l-033`: base-conversion
- `acsl/unit-02-recursive-functions/lesson/08042017`: recursion
- `acsl/unit-02-recursive-functions/lesson/6c2db999`: recursion
- `acsl/unit-02-recursive-functions/lesson/ed5f7744`: recursion
- `acsl/unit-02-recursive-functions/lesson/a599565e`: recursion
- `acsl/unit-02-recursive-functions/lesson/372991a7`: recursion
- `acsl/unit-03-wdtpd-branching/lesson/dc275b87`: acsl-pseudocode
- `acsl/unit-03-wdtpd-branching/lesson/fd4b60a1`: acsl-pseudocode
- `acsl/unit-03-wdtpd-branching/lesson/66d2a7ba`: acsl-pseudocode
- `acsl/unit-03-wdtpd-branching/lesson/53b49996`: acsl-pseudocode
- `acsl/unit-03-wdtpd-branching/lesson/a24f9c87`: acsl-pseudocode
- `acsl/unit-03-wdtpd-branching/lesson/728d874a`: code-tracing, acsl-pseudocode
- `acsl/unit-03-wdtpd-branching/lesson/b54eeead`: code-tracing
- `acsl/unit-03-wdtpd-branching/lesson/4d0a1989`: code-tracing
- `acsl/unit-03-wdtpd-branching/lesson/eea913ae`: code-tracing
- `acsl/unit-03-wdtpd-branching/lesson/a9007e3c`: code-tracing
- `acsl/unit-03-wdtpd-branching/lesson/f00774c3`: code-tracing
- `acsl/unit-03-wdtpd-branching/lesson/30ef5809`: acsl-pseudocode
- `acsl/unit-03-wdtpd-branching/lesson/52c0d5b1`: code-tracing, acsl-pseudocode
- `acsl/unit-03-wdtpd-branching/lesson/7510fefb`: code-tracing
- `acsl/unit-03-wdtpd-branching/lesson/7e866368`: code-tracing
- `acsl/unit-03-wdtpd-branching/lesson/acf5be75`: grid-2d
- `acsl/unit-03-wdtpd-branching/lesson/74bf5cb1`: grid-2d
- `acsl/unit-03-wdtpd-branching/lesson/ccf2bfa1`: grid-2d
- `acsl/unit-03-wdtpd-branching/lesson/b225759a`: code-tracing, grid-2d
- `acsl/unit-03-wdtpd-branching/lesson/73d8cdb0`: acsl-pseudocode
- `acsl/unit-03-wdtpd-branching/lesson/a3877e83`: code-tracing, acsl-pseudocode
- `acsl/unit-04-prefix-infix-postfix/lesson/l-017`: postfix-eval
- `acsl/unit-05-bit-string-flicking/lesson/l-005`: bitwise-ops
- `acsl/unit-05-bit-string-flicking/lesson/l-007`: bitwise-ops
- `acsl/unit-05-bit-string-flicking/lesson/l-013`: bitwise-ops
- `acsl/unit-05-bit-string-flicking/lesson/l-021`: base-conversion, complete-search
- `acsl/unit-06-wdtpd-looping/lesson/41245c64`: acsl-pseudocode
- `acsl/unit-06-wdtpd-looping/lesson/c460f9b8`: acsl-pseudocode
- `acsl/unit-06-wdtpd-looping/lesson/3cfb8b63`: acsl-pseudocode
- `acsl/unit-06-wdtpd-looping/lesson/cd9bbcbd`: acsl-pseudocode
- `acsl/unit-06-wdtpd-looping/lesson/c1ff4459`: acsl-pseudocode
- `acsl/unit-06-wdtpd-looping/lesson/c12b7027`: acsl-pseudocode
- `acsl/unit-06-wdtpd-looping/lesson/b6884c4c`: code-tracing
- `acsl/unit-06-wdtpd-looping/lesson/668542e0`: code-tracing
- `acsl/unit-06-wdtpd-looping/lesson/4f460b92`: code-tracing
- `acsl/unit-06-wdtpd-looping/lesson/7bf9e0e1`: code-tracing
- `acsl/unit-06-wdtpd-looping/lesson/a59105d3`: code-tracing
- `acsl/unit-06-wdtpd-looping/lesson/4c1a91d5`: code-tracing
- `acsl/unit-06-wdtpd-looping/lesson/ea73ae8e`: code-tracing
- `acsl/unit-06-wdtpd-looping/lesson/a96fdb3b`: code-tracing
- `acsl/unit-06-wdtpd-looping/lesson/07af3e6f`: code-tracing
- `acsl/unit-06-wdtpd-looping/lesson/a34d5115`: code-tracing
- `acsl/unit-06-wdtpd-looping/lesson/4dad4e8a`: code-tracing
- `acsl/unit-06-wdtpd-looping/lesson/2ec93081`: code-tracing
- `acsl/unit-06-wdtpd-looping/lesson/82b1a581`: code-tracing
- `acsl/unit-06-wdtpd-looping/lesson/3c55d367`: code-tracing
- `acsl/unit-06-wdtpd-looping/lesson/96c1853b`: code-tracing
- `acsl/unit-06-wdtpd-looping/lesson/24b8c1ce`: code-tracing, acsl-pseudocode
- `acsl/unit-07-lisp/lesson/347b060a`: lisp-eval
- `acsl/unit-07-lisp/lesson/90b85c65`: lisp-eval
- `acsl/unit-07-lisp/lesson/a63cb374`: lisp-eval
- `acsl/unit-07-lisp/lesson/94a18028`: lisp-eval
- `acsl/unit-07-lisp/lesson/69879cb7`: lisp-eval
- `acsl/unit-07-lisp/lesson/5050c2e0`: lisp-eval
- `acsl/unit-07-lisp/lesson/9e09f7cf`: lisp-eval
- `acsl/unit-08-boolean-algebra/lesson/l-020`: boolean-algebra
- `acsl/unit-08-boolean-algebra/lesson/l-022`: boolean-algebra
- `acsl/unit-08-boolean-algebra/lesson/l-027`: boolean-algebra, complete-search
- `acsl/unit-08-boolean-algebra/lesson/l-029`: boolean-algebra, complete-search
- `acsl/unit-09-data-structures/lesson/l-014`: acsl-data-structures
- `acsl/unit-10-wdtpd-arrays/lesson/c7f0f6fd`: code-tracing, acsl-pseudocode
- `acsl/unit-10-wdtpd-arrays/lesson/1d3d5781`: code-tracing, acsl-pseudocode
- `acsl/unit-10-wdtpd-arrays/lesson/f0af96ed`: code-tracing, acsl-pseudocode
- `acsl/unit-10-wdtpd-arrays/lesson/c22064b3`: code-tracing, acsl-pseudocode
- `acsl/unit-10-wdtpd-arrays/lesson/51a0096d`: code-tracing, acsl-pseudocode
- `acsl/unit-10-wdtpd-arrays/lesson/924225c8`: code-tracing, acsl-pseudocode
- `acsl/unit-10-wdtpd-arrays/lesson/b3f9a7e8`: code-tracing, acsl-pseudocode
- `acsl/unit-10-wdtpd-arrays/lesson/fbd2f115`: code-tracing, acsl-pseudocode
- `acsl/unit-10-wdtpd-arrays/lesson/b8669985`: code-tracing, acsl-pseudocode
- `acsl/unit-10-wdtpd-arrays/lesson/42d85a34`: code-tracing, acsl-pseudocode
- `acsl/unit-10-wdtpd-arrays/lesson/a81bf76a`: code-tracing, acsl-pseudocode
- `acsl/unit-10-wdtpd-arrays/lesson/27912a0a`: code-tracing, grid-2d
- `acsl/unit-10-wdtpd-arrays/lesson/25c72db8`: code-tracing, grid-2d
- `acsl/unit-10-wdtpd-arrays/lesson/efe97826`: code-tracing, grid-2d
- `acsl/unit-10-wdtpd-arrays/lesson/4645a5ca`: code-tracing, grid-2d
- `acsl/unit-10-wdtpd-arrays/lesson/2262ff79`: code-tracing, grid-2d
- `acsl/unit-10-wdtpd-arrays/lesson/e5905a32`: code-tracing, grid-2d
- `acsl/unit-12-graph-theory/lesson/l-013`: acsl-graph-theory
- `acsl/unit-12-graph-theory/lesson/l-020`: acsl-graph-theory, grid-2d
- `acsl/unit-13-digital-electronics/lesson/l-009`: logic-gates
- `acsl/unit-13-digital-electronics/lesson/l-011`: logic-gates
- `acsl/unit-13-digital-electronics/lesson/l-013`: input-parse
- `acsl/unit-13-digital-electronics/lesson/l-015`: logic-gates
- `acsl/unit-13-digital-electronics/lesson/l-019`: logic-gates
- `acsl/unit-14-wdtpd-strings/lesson/a251d7f6`: code-tracing, acsl-pseudocode
- `acsl/unit-14-wdtpd-strings/lesson/1c7545ea`: code-tracing, acsl-pseudocode
- `acsl/unit-14-wdtpd-strings/lesson/d81fa1b3`: code-tracing, acsl-pseudocode
- `acsl/unit-14-wdtpd-strings/lesson/69765ddf`: code-tracing, acsl-pseudocode
- `acsl/unit-14-wdtpd-strings/lesson/486b367c`: code-tracing, acsl-pseudocode
- `acsl/unit-14-wdtpd-strings/lesson/14e80a84`: code-tracing, acsl-pseudocode
- `acsl/unit-14-wdtpd-strings/lesson/7bcd54a0`: code-tracing, acsl-pseudocode
- `acsl/unit-14-wdtpd-strings/lesson/972e6fb4`: code-tracing, acsl-pseudocode
- `acsl/unit-14-wdtpd-strings/lesson/2220bf65`: code-tracing, acsl-pseudocode
- `acsl/unit-14-wdtpd-strings/lesson/f1b971f4`: code-tracing
- `acsl/unit-14-wdtpd-strings/lesson/46953169`: code-tracing
- `acsl/unit-14-wdtpd-strings/lesson/fb3eee90`: code-tracing
- `acsl/unit-14-wdtpd-strings/lesson/2c04c768`: code-tracing
- `acsl/unit-14-wdtpd-strings/lesson/7bf835ad`: code-tracing
- `acsl/unit-14-wdtpd-strings/lesson/7e631a14`: code-tracing
- `acsl/unit-14-wdtpd-strings/lesson/77f9e5cb`: code-tracing
- `acsl/unit-14-wdtpd-strings/lesson/5d948dc7`: code-tracing
- `acsl/unit-14-wdtpd-strings/lesson/5dade76a`: code-tracing
- `acsl/unit-14-wdtpd-strings/lesson/47828fbc`: code-tracing
- `acsl/unit-15-assembly-language/lesson/ee44cc53`: acsl-assembly
- `acsl/unit-15-assembly-language/lesson/d5183c40`: acsl-assembly
- `acsl/unit-15-assembly-language/lesson/2d5905ec`: acsl-assembly
- `acsl/unit-15-assembly-language/lesson/282cff22`: acsl-assembly
- `acsl/unit-15-assembly-language/lesson/b07740f0`: acsl-assembly

Items (heading-cell `metadata.concepts`), 15 `fixtures` items:

- `acsl/unit-00-acsl-foundations/exercises/5d48a286`: input-parse
- `acsl/unit-02-recursive-functions/exercises/c3fe911e`: recursion
- `acsl/unit-03-wdtpd-branching/exercises/fa8f523d`: code-tracing, acsl-pseudocode
- `acsl/checkpoint-01-contest-1-practice/checkpoint/e44078f9`: base-conversion, complete-search
- `acsl/unit-06-wdtpd-looping/exercises/93a42355`: code-tracing, acsl-pseudocode
- `acsl/unit-09-data-structures/exercises/e-016`: acsl-data-structures
- `acsl/unit-13-digital-electronics/exercises/e-024`: logic-gates, input-parse
- `acsl/unit-13-digital-electronics/exercises/e-036`: logic-gates, input-parse
- `acsl/unit-13-digital-electronics/exercises/e-044`: logic-gates, input-parse
- `acsl/unit-14-wdtpd-strings/exercises/44940476`: code-tracing, acsl-pseudocode
- `acsl/unit-14-wdtpd-strings/exercises/22ad4d5d`: code-tracing, acsl-pseudocode
- `acsl/unit-14-wdtpd-strings/exercises/04282687`: code-tracing, acsl-pseudocode
- `acsl/unit-15-assembly-language/exercises/2468c666`: acsl-assembly
- `acsl/unit-15-assembly-language/exercises/6df28308`: acsl-assembly
- `acsl/unit-15-assembly-language/exercises/a22bb998`: acsl-assembly

Reasons in brief: WDTPD units (03, 06, 10, 14) trace programs → `code-tracing`; blocks that translate an ACSL dialect rule (real `/`, `int` as floor, `sqrt`, `abs`, inclusive `FOR`/`STEP`, 1-based arrays, inclusive substrings) add `acsl-pseudocode`; 2D arrays add `grid-2d`. Unit 01 conversions → `base-conversion`; unit 02 blocks evaluate recursive definitions (argument chain, bottom-up table, mutual recursion) → `recursion`; unit 04 stack → `postfix-eval`; unit 05 string bit operations → `bitwise-ops`, the try-all-x listing → `complete-search` + `base-conversion`; unit 07 Python mirrors of LISP evaluations → `lisp-eval`; unit 08 truth tables → `boolean-algebra` (+ `complete-search` when trying every row); unit 09 BST insert → `acsl-data-structures`; unit 12 vertex positions and matrix powers → `acsl-graph-theory` (+ `grid-2d`); unit 13 gate simulators → `logic-gates`, the netlist tokenizer → `input-parse`; unit 15 accumulator simulations → `acsl-assembly`; unit 00 input-reading programs → `input-parse`, the every-pair loop → `complete-search`, the hand-trace demo → `code-tracing`.

## Concept gap list

- `acsl/unit-00-acsl-foundations/lesson/2175b7f0`: `print(3, 4)` / `print("3,4")` exact-output demo: boilerplate, exercises no registered concept (the plan's own example).
- `acsl/unit-00-acsl-foundations/lesson/a0bce68f`: `line = input(); print(line)`: echoes one line, parses nothing; no registered concept.
- `acsl/unit-04-prefix-infix-postfix/lesson/l-025`: `show(value)` prints a whole float without `.0`: answer formatting, not postfix evaluation; no registered concept.


## Independent blind fixture validation (Phase D requirement)

A separate Opus agent wrote its own solver for each of the 72 fixtures items. It worked on a filtered copy holding only the statement notebooks and the fixture directories: no reference solvers and no solution notebooks (verified: 0 `.py` files in the copy). It ran each solver on every pair under line-exact matching.

**Result:** 72 items, **453/453 cases passed, 0 mismatches**. Its one first-run failure was a bug in its own solver; fixing it confirmed the fixture (unit-04 ex16 case 6).

Report: scratchpad `blind-solvers/acsl-report.md` (session-local).

**The e-028 alias:** the plan names e-028 among the `↑` items, but its statement and canonical (`/ + A * B C - D E`) contain no `↑`, so no alias is set there. The five aliased items are e-024, e-026, e-030, e-040 and checkpoint-02 d0aca7dc.
