# Plan 095 — ACSL Contest 3: Boolean Algebra, Data Structures, WDTPD – Arrays, FSAs and Regular Expressions

**Goal:** Ship the Contest 3 part of *Contest Python: ACSL*: one unit per Contest 3 category, then the Contest 3 practice checkpoint.
This is the study block for the third contest window (Feb 1 – Apr 11, 2027).

**Spec:** design 009 and the roadmap row for 095. User decision, 2026-09-29: "continue with plan 093 on autopilot and all other contest followed".
Conventions and lessons carried over from plans 093–094:
- canonical short-answer text; one-line WDTPD outputs
- the ACSL dialect of unit 03: `int` = floor, inclusive substrings, inclusive `FOR`, arrays `A(3)` and `A(r, c)`
- `.pop`, `.index`, `.count`, `.find` and `.join` banned in contest code; the stack-plus-`top` idiom of unit 04
- tested verify helpers in `assets/verify/`, with pre-written test files the helper authors do not edit
- an Elementary lesson with no code the student runs; the checkpoint's student page lists every path, Classroom included; timing lines apply only to the paths they name
- fixtures for every boundary rule a statement states (plan 094's shift-clamp lesson)
- per-entry `requires` boundaries; registry before authoring; coverage map and syllabus after, reconciled
- teacher notes inline; separate solutions sessions; blind solves in the gate

## Survey (2026-09-29, main at 7e55168)

- **`season.yaml` Contest 3 units:**
  - Boolean Algebra — elementary, junior, intermediate, senior
  - Data Structures — junior, intermediate, senior
  - WDTPD – Arrays — junior
  - FSAs and Regular Expressions — intermediate, senior
- **ACSL papers** (6 short-answer questions each):
  - Junior: Boolean Algebra, Data Structures, What Does This Program Do? – Arrays
  - Intermediate and Senior: Boolean Algebra, Data Structures, FSAs and Regular Expressions
  - Elementary: Elementary Boolean Algebra
  - Classroom: Boolean Algebra, FSAs and Regular Expressions, Data Structures
- **Shared id** with USACO (identical entry): `boolean-algebra` (technique, techniques), introduced by USACO unit 02.
  `code-tracing`, `acsl-pseudocode`, `grid-2d` and `postfix-eval` (the stack idiom) already exist in `acsl`.
  USACO's `tree-traversal` (technique, data-structures) is on ACSL's Data Structures page too, and unit 09 introduces it as a shared id.
- **Official scope** (retrieved 2026-09-29):
  - *Elementary Boolean Algebra* (ACSL's Elementary doc): 2 variables `A` and `B`; `~` NOT, `*` AND, `+` OR; precedence NOT, AND, OR, left to right; `1` TRUE and `0` FALSE.
    Five question types: truth evaluation of a statement, truth tables, simplification with the laws, counting the ordered pairs that make an expression true, and equivalence by truth table.
    Includes De Morgan's laws, tautologies, and the commutative, associative and distributive properties.
  - *Boolean Algebra* (ACSL wiki): NOT (overbar), AND (juxtaposition or `·`), OR `+`, XOR `⊕`, XNOR `⊙`. Precedence: NOT; AND; XOR and XNOR; OR.
    The laws are commutative, associative, idempotent, annihilator, identity, complement, absorptive, distributive, De Morgan, double negation, and the XOR/XNOR identities.
    Question types: simplify (the wiki: "the fewest number of operators"), and find the ordered tuples that make an expression true.
    Wiki samples: one expression simplifies to `A`; another has solutions `(1,0)` and `(1,1)`.
  - *Data Structures* (ACSL wiki): stacks (LIFO) and queues (FIFO) with `PUSH(x)` and `POP()` (`POP` of an empty structure gives `NIL`); binary search trees with inorder, preorder and postorder traversals and a deletion rule; priority queues as heaps (min-heaps in its examples; "a max-heap is also possible").
    - A BST puts **duplicates as if less than their equal key** (to the left). The root has depth 0.
    - The internal path length is the sum of the depths of all nodes; external nodes are the empty attachment points; the external path length is the sum of their depths.
    - Min-heap: every node ≤ its children, no gaps, built by inserting one item at a time. Removing the root moves the bottom-most, right-most item to the root and swaps it down with the smaller child.
    - BST deletion of `p` with parent `f`: no children, delete `p`; one child, it becomes `f`'s child; two children, the left child `l` takes `p`'s place and the right subtree `r` is attached to the `l` tree (as the right child of `l`'s right-most node, where BST order puts it).
    - Wiki samples: stack `Z` = `-2`; the min-heap of `PROGRAMMING` has bottom row `RORN`; the BST of `PROGRAM` has internal path length `12`.
  - *FSAs and Regular Expressions* (ACSL wiki): states, one initial state, final (double-circled) states, labelled transitions.
    - Regular expressions use concatenation, union `|` (or `U`), and Kleene star `*`, with precedence star, then concatenation, then union.
    - The extended syntax is `?`, `+`, `.`, `[abc]`, `[^abc]`, `[a-z]`, and `()`; `λ` is the empty string.
    - The identities include `(a*)* = a*`, `aa* = a*a`, `aa* U λ = a*`, `a(b U c) = ab U ac`, `a(ba)* = (ab)*a`, and `(a U b)* = (a*b*)* = a*(ba*)*`.
    - Question types: FSA to regular expression, simplification, equivalence, and which strings are accepted.
    - Wiki samples: `00*1*1U11*0*0` accepts `0000001111111` and `10`; `[A-D]*[a-d]*[0-9]` accepts `ABCD8`, `abcd5`, `ABcd9`, `DCCBBBaaaa5`; `Hi?g+h+[^a-ceiou]` accepts `HigghhhC`, `Highd`, `HgggggghX`.

## Shared rules for this plan

**Verification helpers.** Evaluators that check answers live in `acsl/units/<unit>/assets/verify/`, with plan 094's recipe (`sys.path.insert(0, "assets/verify")`, then `import`; `__pycache__/` git-ignored):
- `bool_eval.py` (unit 08) parses the book's Boolean notation (below), `~~A` included. Its interface:
  - `evaluate(expr, values) -> int`, where `values` maps each variable to 0 or 1
  - `solutions(expr, value=1) -> str`: the canonical tuple list of the rows where `expr` equals `value` (`"(1,0), (1,1)"`), or `NONE`
  - `count(expr, value=1) -> int`
  - `equivalent(a, b) -> bool`, by full truth table
  - `minimal_sops(expr) -> list[str]`: **every** minimal sum of products (fewest terms, then fewest literals), in canonical text, found by brute force over prime-implicant covers (2 to 4 variables); a tautology gives `["1"]` and a contradiction `["0"]`
  - `column(expr) -> str`: the truth-table result column (canonical form below)
- `ds_eval.py` (unit 09). Its interface:
  - `run(script, kind) -> dict`: runs a script on a `"stack"` or a `"queue"`, one statement per list item. The statements are:
    - `PUSH(e)`
    - `POP()`
    - `V = POP()`, where `V` is a one-letter capital variable

    `e` is an integer, a variable assigned earlier, or `a op b` with `op` one of `+ - *` over those; any other bare word (such as `A` never assigned, or `CAT`) is pushed as a letter/word value.
    It returns `{"popped": [...], "vars": {...}}`: every popped value in order (`"NIL"` when empty) and the final variables. The wiki sample gives `vars["Z"] == -2`.
  - `bst(keys) -> dict`, where `keys` is a list inserted in order (a word is passed as `list("PROGRAM")`). The report has these fields:
    - `depths: list[int]`, the depth of each inserted node in insertion order, so duplicates stay distinct
    - `ipl`, `epl`, `external`, `leaves`, `height: int`: the internal and external path lengths, the external-node count, the leaf count, and the greatest depth
    - `leaf_keys`, `inorder`, `preorder`, `postorder: str`, in canonical row text (leaves left to right)
  - `bst_delete(keys, key) -> dict`: the same report, minus `depths`, after inserting `keys` and then deleting the **shallowest** node holding `key` by ACSL's rule (below)
  - `heap(keys, kind="min") -> list[str]`: the rows of a heap built by insertion, top row first, in canonical text
  - `heap_pop(keys, kind="min") -> list[str]`: the rows after removing the root by ACSL's rule
- `fsa_eval.py` (unit 11). Its interface:
  - `accepts(pattern, s) -> bool`: translates an ACSL regular expression and then uses Python's `re.fullmatch`. The translation is token by token: outside a `[...]` class, `U` is union and becomes `|`, and `λ` becomes an empty group `()`, so a quantifier after it stays valid; inside a class, `U` and `λ` are literal characters, while the class operators keep their meaning (`[A-D]` is a range, `[^a-ceiou]` a negated class). Items never use `U` or `λ` as a literal symbol outside a class.
  - `run_dfa(table, start, finals, s) -> bool`, where `table` maps `(state, symbol)` to a state and a missing entry rejects
  - `same_language(p, q, alphabet, max_len) -> bool`, which compares acceptance on every string up to `max_len`

The pre-written tests pin these signatures in their docstrings, so verify cells can be written in parallel with the evaluators.

Verify cells are exempt from `source-policy` and `concept-scan`, so `fsa_eval.py` may use `re`; student code never does.
Each evaluator must pass its **pre-written** test file before any answer is trusted:
- `tests/test_acsl_eval_bool.py`
- `tests/test_acsl_eval_ds.py`
- `tests/test_acsl_eval_fsa.py`

A verify cell's expression string is byte-identical to the statement's.

**The book's Boolean notation**, which all items and answers use:
- `~` NOT, applying to the variable or bracket right after it (`~A`, `~(A + B)`)
- `*` AND, `+` OR, `⊕` XOR, `⊙` XNOR, with a single space around every binary operator
- `1` and `0` for TRUE and FALSE in expressions; double negation `~~A` is allowed
- precedence as ACSL's: `~`; `*`; `⊕` and `⊙`; `+`

The Elementary doc uses the same symbols. The Junior lesson shows the wiki's overbar and juxtaposition forms and translates them, so students can read real papers.
Contest books build no PDF yet (ACSL publication is out of scope), so `⊙`, like unit 05's `⊕`, needs only to display in the notebooks.

**Stack, queue, tree and heap idioms for student code** (still no `.pop`, `.index`, `.count`, `.find`, `.join`, list slices or `collections`):
- **stack:** unit 04's list plus `top` count
- **queue:** a list plus a `head` index; `PUSH` appends, `POP` reads `queue[head]` and adds 1 to `head`, and the queue is empty when `head == len(queue)`
- **BST:** parallel lists `key`, `left` and `right`, with `-1` for "no child"; insertion walks from the root with a `while` loop
- **min-heap:** a list with an unused slot 0, so the children of position `i` are `2i` and `2i + 1`; insertion appends and then swaps upward while the parent is larger
- **FSA:** a dict from `(state, symbol)` tuples to states, or nested dicts

These map to `list-*`, `dict-*` and `tuple` ids that are already registered.

**Per-entry concept boundaries:**
- Units 08, 09 and 11 require only *Python by Projects* and Foundations ids, with these additions:
  - Unit 09 also requires `postfix-eval` (unit 04, the stack idiom) and `recursion` (unit 02, for traversals).
  - Unit 11 also requires `recursion` (unit 02), which its matcher uses, and it lists `dict-literal`, `dict-access` and `tuple` for its FSA tables.
- Unit 10 also practises `code-tracing`, `acsl-pseudocode` and `grid-2d` (unit 03), and **introduces nothing** (`introduces: []`).
- The checkpoint is strict over *Python by Projects* plus units 00–11. Its author writes from these specs; A2 re-checks every id against the units' final manifests.

**Canonical answer text** (plan 093–094 rules, plus the rules below):
- **Boolean values and counts:** `1`, `0`, or a bare integer count. An Elementary item that asks whether a *statement* (such as `3 + 4 > 6 AND 7 - 2 > 6`) is true answers `TRUE` or `FALSE`, as the Elementary doc does.
- **Satisfying tuples:** values in alphabetical order of the variables, `(A,B)` with no inner spaces, in ascending binary order, separated by `, `: `(1,0), (1,1)`. Three variables give `(A,B,C)` triples.
- **Simplified expressions:** a sum of products in the book's notation. Within a term, literals go in alphabetical order of their variable (`~A * B`, not `B * ~A`).
  Terms are ordered by comparing their literal lists position by position: the earlier variable first, then `X` before `~X` for the same variable, and a term that runs out first goes first (`A * B + ~A * C`, not `~A * C + A * B`).
  `0` and `1` stand alone. No XOR or XNOR appears in a simplified answer.
  Every simplify item's statement says "as a sum of products".
  Every simplify item's verify cell asserts that `bool_eval` finds **exactly one** minimal sum of products for the original expression, and that the answer text equals it. An item whose minimal form is not unique is rewritten.
- **Data structures:**
  - popped values as integers or letters
  - `NIL` for an empty `POP`
  - a heap or tree row, or a traversal, as its letters or numbers in order, with letters run together (`RORN`) and numbers separated by single spaces
  - the position of an item in a heap as its 1-based array index (the root is 1)
- **Truth tables:** the result column as a string of `0`s and `1`s, rows in ascending binary order of the variables (`00, 01, 10, 11` for `A, B`): `~A + B` is `1101`. `bool_eval.column(expr) -> str` gives it.
  - path lengths, depths and counts as bare integers
- **Option lists** (accepted strings, tautologies, equivalent expressions): items label their options with capital letters `A`, `B`, `C`, …, and the answer is the chosen labels in that order, separated by `, ` (`A, E`); `NONE` when none qualify.
- **Regular-expression answers** are judged as option choices (which expression is equivalent / describes the FSA), never as free text. The lesson still has students *write* expressions for FSAs, and the teacher notes say real papers grade free text.

## The entries (all under `acsl/`)

Unit conventions:
- a project-first hook and 3 lessons
- **at least 14 exercises**, mixing programming items (judged line-exact) and short-answer items (`**Answer:**` line and a top-level `verify` assert)
- a heading ladder tag plus a visible division line on every exercise
- at least 2 `stretch` Challenges
- ACSL-style statements

### `unit-08-boolean-algebra` — Boolean Algebra

- **Divisions:** elementary, junior, intermediate, senior. **Introduces:** `boolean-algebra`.
- **Non-programming hook.**
- **Lesson 1 is the Elementary section**, with no code the student runs. It follows the official Elementary doc:
  - 2 variables, `~ * +`, `1` and `0`, precedence and brackets
  - the doc's skills: evaluate a statement (`TRUE`/`FALSE`, including arithmetic comparisons), build a truth table, simplify with the laws (De Morgan and the basic identities), list or count the ordered pairs that make an expression true or false, test equivalence by truth table, and pick the tautology or the equivalent expression from options
  - the book lists pairs in ascending order; the lesson says ACSL accepts any order (its doc lists them descending)
  - ≥ 6 contiguous `acsl-elementary` short-answer items open the exercises, before any other tag.
    **Exercises 1–6 are the Elementary mock test**: one per skill (evaluate, truth table, simplify, count pairs, equivalence) plus a second simplify item. Any further Elementary items come after them as extra practice.
- **Junior and above:**
  - 3 variables; the full list of laws; XOR and XNOR with their identities
  - the wiki's overbar/juxtaposition notation translated to the book's
  - simplification by the laws; finding all satisfying tuples
  - Python: `and`, `or`, `not`, and `!=` as XOR on 0/1 values, with a truth-table loop that counts or lists the solutions
- **Intermediate and above:** longer simplifications, nested negations, and 4-variable tuple counts.

### `unit-09-data-structures` — Data Structures

- **Divisions:** junior, intermediate, senior. **Introduces:** the ACSL-only `acsl-data-structures` ("Stacks, queues, BSTs and heaps (ACSL conventions)", technique, data-structures) and the shared `tree-traversal`.
- **Requires** also `recursion` (unit 02, for traversals) and `postfix-eval` (unit 04's stack idiom); the heap uses `//` (`arithmetic`) and a tuple swap (`tuple`).
- **Rules from ACSL's page:** stacks and queues with `PUSH`/`POP` (`NIL` when empty); BSTs with duplicates to the left; depth, internal/external path length and external nodes; heaps built by insertion (min-heaps, and max-heaps when an item says so), and root removal.
- **Junior:** stack and queue traces; building a BST from a word or list and reading its depths, leaves and internal path length.
- **Intermediate and above:** inorder, preorder and postorder traversals; external path length and external-node counts; min-heaps and max-heaps (rows, the bottom row, the position of an item); mixed `PUSH`/`POP` scripts with arithmetic on popped values, as in the wiki sample.
- **Senior:** BST deletion and heap root removal by ACSL's rules, then a report on the new tree (for example its internal path length).
- **Python:** the idioms above, used to build what the statements describe and print it.
- **Out:** balanced trees, and heap deletion of anything but the root (not on ACSL's page).

### `unit-10-wdtpd-arrays` — What Does This Program Do? – Arrays

- **Divisions:** junior. **Introduces:** none; it practises `code-tracing`, `acsl-pseudocode` and `grid-2d`.
- **Constructs:**
  - 1D arrays `A(i)`, starting at 1 or 0 as the program states
  - 2D arrays `A(r, c)`
  - loops that fill, shift, swap, reverse, sum, count and find extremes
  - arrays indexed by computed positions (`A(i + 1)`, `A(n - i)`)
  - nested loops over grids, rows and diagonals
- **Out:** string traversal (Contest 4).
- At least one third of items are in pseudocode, and every short-answer item has one-line output.
- *(Intermediate and Senior met arrays in unit 03; the teacher notes suggest this unit as array drill only.)*

### `unit-11-fsas-regular-expressions` — FSAs and Regular Expressions

- **Divisions:** intermediate, senior. **Introduces:** the ACSL-only `fsa-regex` ("Finite state automata and regular expressions", technique, techniques).
- **FSAs** are shown as transition tables (states × symbols, with the initial state and final states marked) and, where helpful, a text diagram. Reading an FSA: which strings it accepts, and which regular expression describes it.
- **Regular expressions:**
  - the three basic operations and their precedence
  - `λ`; the identities list, used to test equivalence
  - the extended syntax (`?`, `+`, `.`, classes, negated classes, ranges)
  - "which strings are accepted" items in the wiki's option-list form
- **Python:** a DFA simulator from a table read from input, and a hand-written matcher for one-character patterns with `?`, `+` and `*` (with recursion). The student never uses `re`.
- **Out:** NFA-to-DFA conversion, and minimisation.

### `checkpoint-03-contest-3-practice` — Practice (contest 3)

- **Divisions:** junior, intermediate, senior. **9 questions:**
  - Q1–Q2 Boolean Algebra, `acsl-junior` (Q2 the harder: satisfying tuples)
  - Q3–Q4 Data Structures, `acsl-junior` (one stack/queue item, one BST item)
  - Q5–Q6 WDTPD – Arrays, `acsl-junior`, at least one in pseudocode
  - Q7–Q8 FSAs and Regular Expressions, `acsl-intermediate` (one FSA item, one regular-expression item)
  - Q9 the single `acsl-junior` programming problem, last, on Junior Contest 3 material (Boolean Algebra, a stack or queue, a BST, or arrays), with the sample plus ≥ 4 hidden-style fixtures
- **Paths:**
  - Junior: Q1–Q6 + Q9
  - Intermediate and Senior: Q1–Q4, Q7–Q8 + Q9
  - Classroom (its Contest 3 categories are Boolean Algebra, FSAs and Regular Expressions, and Data Structures): Q1–Q4 + Q7–Q8, with Q5–Q6 optional extra
  - Elementary: unit 08's Exercises 1–6, as 6 questions in 30 minutes
- The student page lists every path, and Q9's timing line names only the programming paths.
- **Teacher notes:** Grading in ACSL's format (6 short answers in 30 minutes; the programming problem scored on its test data).

## Phase A1 — Registry and tooling, before authoring

- **Inline:** `acsl/curriculum/concepts.yaml` gains `boolean-algebra` and `tree-traversal` (byte-identical to USACO's) and the ACSL-only `acsl-data-structures` and `fsa-regex`.
- **Opus tooling subagent:** **pre-written evaluator tests** (expected values from the ACSL wiki and the Elementary doc, one file per evaluator; each imports its evaluator from the unit's `assets/verify/` and skips until that module exists):
  - `tests/test_acsl_eval_bool.py`:
    - the wiki's two samples: equivalence to `A`, and the solutions `(1,0), (1,1)`
    - the Elementary doc's `~(A + ~B) + ~A * B` equivalent to `~A * B`
    - precedence cases for `~`, `*`, `⊕`/`⊙` and `+`, left to right on ties
    - De Morgan, and each XOR/XNOR identity
    - `~~A`; `solutions(expr, 0)` for the rows that are false
    - `column` for 2 and 3 variables; `minimal_sops` on a 2-variable input, a tautology (`["1"]`) and a contradiction (`["0"]`)
    - the three traversals of the wiki's tree from `A M E R I C A N`: inorder `AACEIMNR`, preorder `AAMECIRN`, postorder `ACIENRMA`
    - canonical tuple order for 2 and 3 variables, and counts
    - minimal sums of products: `A * B + ~A * C` has exactly one (itself, the consensus term dropped); `A * ~B + ~A * B + B * ~C + ~B * C`, whose minimal forms tie, returns more than one; the wiki sample 1 gives exactly `A`; canonical term order
  - `tests/test_acsl_eval_ds.py`:
    - the wiki's three samples: `run(["PUSH(3)", "PUSH(6)", "PUSH(8)", "Y = POP()", "X = POP()", "PUSH(X-Y)", "Z = POP()"], "stack")["vars"]["Z"] == -2`; the `PROGRAMMING` min-heap's last row `RORN`; the `PROGRAM` BST's `ipl` `12`
    - duplicate keys: `depths` for `list("AMERICAN")` keeps both `A` nodes; `bst_delete` removes the shallower one
    - `NIL` on an empty `POP`, for a stack and for a queue
    - a duplicate going left
    - depth, height, leaves, the external node count (= n + 1) and the external path length on a hand-checked tree
    - heap rows for a numeric list
    - max-heap rows; heap root removal
    - BST deletion for a leaf, a one-child node and a two-child node
  - `tests/test_acsl_eval_fsa.py`:
    - the wiki's three "accepted" samples, with every listed option accepted or rejected as the wiki states
    - token-by-token translation: `aUb` is a union, `[TUV]` keeps `U` literal, `[A-D]` and `[^a-ceiou]` keep their range and negation, `(λUa)b` and `λ*` stay valid and match as ACSL means
    - each wiki identity checked with `same_language` over the alphabet `{a, b, c}` on all strings up to length 5
    - a DFA table run, a missing transition rejecting

## Phase B — Lessons and statements (Opus subagents in parallel, one per entry, each owning only its folder)

Each unit folder gets `lesson.ipynb`, `exercises.ipynb` (statements, with `**Your answer:** _(write your answer here)_` placeholders for short answers; no answers and no verify cells), `manifest.yaml`, and `assets/` with the programming fixtures (`exN/k.in|out`); the checkpoint gets `checkpoint.ipynb`, `manifest.yaml` and `assets/q9/`. Teacher notes come in Phase D. The worked `**Answer:**` lines, the verify cells and the programming solutions go in `solutions.ipynb` in Phase C.

## Phase C — Solutions (Opus subagents, separate fresh sessions, one per entry)

- Solved from the statements only.
- The unit 08, 09 and 11 solutions sessions each write their `assets/verify/*_eval.py`, which must pass its pre-written test file. They do not edit that file.

## Phase A2 — Coverage and syllabus, after authoring (inline)

Coverage-map entries in season order (units 08, 09, 10, 11, then the checkpoint), reconciled against the manifests. Syllabus rows in the check's form.

## Phase D — Teacher notes (inline)

Five `teacher-notes.md` files, with the required headings and Grading for the checkpoint. They cover:
- division paths, including unit 10 as array drill for Intermediate/Senior and the Elementary mock test at 6 in 30
- the canonical answer forms
- the ACSL rules students most often get wrong: duplicates left, depth from 0, min-heap insertion order, and regex precedence
- the book's sum-of-products answers versus ACSL's "fewest operators" (a paper may expect `~(A + B)` where the book writes `~A * ~B`)

## Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN, in a solo run on the final commit.
2. The global concept check passes with the shared `boolean-algebra`. The three pre-written evaluator test files pass, with no skips, on the ACSL wiki and Elementary-doc samples.
3. A script reports the actual question ids and tags for each checkpoint path:
   - Junior: Q1–Q6 + Q9
   - Intermediate/Senior: Q1–Q4, Q7–Q8 + Q9
   - Classroom: Q1–Q4, Q7–Q8

   It also checks that unit 08 has ≥ 6 contiguous `acsl-elementary` items before any other tag, and that Exercises 1–6 are all `acsl-elementary` short-answer items.
4. Blind solves: reviewers solve all 8 checkpoint short answers and at least 3 items per unit.
5. Post-execution report.

## Out of scope

- Contest 4 (096).
- The USACO trim (097).
- ACSL publication.

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- **N1 (folded):** the term order for simplified answers had no tie-break between `X` and `~X`. It now compares literal lists (earlier variable, then `X` before `~X`, then the shorter term), and simplified answers never use XOR or XNOR.
- **N2 (folded):** tuple values follow the alphabetical order of the variables.
- **N3 (folded):** Q9 must use Junior material, because FSAs are Intermediate+.

### Round 1 — verdicts and fold

- `[sol]` **REJECT**, 4 findings, all folded:
  1. The simplify contract did not prove minimality or uniqueness. `bool_eval.minimal_sops` now returns every minimal sum of products (fewest terms, then fewest literals); each simplify verify cell asserts exactly one, equal to the answer; the ordering example is now `A * B + ~A * C`; tests cover a unique case and a tied (cyclic) case.
  2. The regex translation is token by token (`U` literal inside classes; `λ` → `()`), with tests for literals, classes and quantified `λ`.
  3. Unit 11 requires `recursion` (unit 02) and lists `dict-literal`, `dict-access`, `tuple`.
  4. The Elementary mock is Exercises 1–6 (one per skill plus a second simplify), checked in Phase E.
- `[fable]` **APPROVE WITH NITS**, 14 findings, all folded:
  1. Traversals and BST deletion *are* on ACSL's page (verified). Unit 09 now introduces the shared `tree-traversal` (Intermediate+), with ACSL's deletion rule and heap root removal (Senior), and matching `ds_eval` functions and tests.
  2. = `[sol]` 3.
  3. = `[sol]` 1.
  4. Simplify statements say "as a sum of products", and the teacher notes cover ACSL's "fewest operators".
  5. Elementary skills now include statement truth (`TRUE`/`FALSE`), pairs for false, and tautology/equivalence options; option labels are capital letters.
  6. = `[sol]` 2, plus the identity alphabet `{a, b, c}` up to length 5 and the DFA table interface.
  7. The evaluator interfaces are named in the plan and pinned in the test docstrings.
  8–14. `~~A`; max-heaps; heap position as a 1-based index; students still write regular expressions; the Phase B file set; unit 09's `arithmetic`/`tuple`/`recursion` requires; a lesson note that ACSL accepts any pair order.
- The plan otherwise follows plan 094's shape and its lessons: tested helpers with pre-written tests, a code-free Elementary lesson, every path listed on the student page, and boundary fixtures.

### Round 2 — verdicts and fold

- `[fable]` **APPROVE WITH NITS**. It verified every round-1 fold (deletion, heap removal, the traversal strings, the interfaces, `λ → ()`, and the `minimal_sops` claims by brute force).
  - N1 (must fold) = `[sol]` 1: `exercises.ipynb` holds statements and `**Your answer:**` placeholders only; the answers, verify cells and solutions go in `solutions.ipynb` (Phase C), where the tools exempt verify cells.
  - N2: truth tables have a canonical result-column form and `bool_eval.column`.
  - N3: `minimal_sops` returns `["1"]` or `["0"]` for a tautology or a contradiction, and works for 2 variables.
  - N4: the wording is tidied.
- `[sol]` **REJECT**, 4 findings, all folded:
  1. = `[fable]` N1.
  2. `ds_eval.run` now takes assignments and `PUSH(a op b)`, and returns popped values plus variables; the wiki `Z = -2` sample is written out as a test.
  3. The BST report has typed fields; `depths` is in insertion order, so duplicates stay distinct; deletion removes the shallowest matching node.
  4. Inside a class, only `U` and `λ` are literal; ranges and negation keep their meaning, with tests.

## Content Review

## Post-Execution Report
_(filled before merge.)_
