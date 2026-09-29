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
  USACO's `tree-traversal` is not in ACSL's Data Structures page and is not used.
- **Official scope** (retrieved 2026-09-29):
  - *Elementary Boolean Algebra* (ACSL's Elementary doc): 2 variables `A` and `B`; `~` NOT, `*` AND, `+` OR; precedence NOT, AND, OR, left to right; `1` TRUE and `0` FALSE.
    Five question types: truth evaluation of a statement, truth tables, simplification with the laws, counting the ordered pairs that make an expression true, and equivalence by truth table.
    Includes De Morgan's laws, tautologies, and the commutative, associative and distributive properties.
  - *Boolean Algebra* (ACSL wiki): NOT (overbar), AND (juxtaposition or `·`), OR `+`, XOR `⊕`, XNOR `⊙`. Precedence: NOT; AND; XOR and XNOR; OR.
    The laws are commutative, associative, idempotent, annihilator, identity, complement, absorptive, distributive, De Morgan, double negation, and the XOR/XNOR identities.
    Question types: simplify, and find the ordered tuples that make an expression true.
    Wiki samples: one expression simplifies to `A`; another has solutions `(1,0)` and `(1,1)`.
  - *Data Structures* (ACSL wiki): stacks (LIFO) and queues (FIFO) with `PUSH(x)` and `POP()` (`POP` of an empty structure gives `NIL`); binary search trees; priority queues as **min-heaps**.
    - A BST puts **duplicates as if less than their equal key** (to the left). The root has depth 0.
    - The internal path length is the sum of the depths of all nodes; external nodes are the empty attachment points; the external path length is the sum of their depths.
    - Min-heap: every node ≤ its children, no gaps, built by inserting one item at a time.
    - Wiki samples: stack `Z` = `-2`; the min-heap of `PROGRAMMING` has bottom row `RORN`; the BST of `PROGRAM` has internal path length `12`.
  - *FSAs and Regular Expressions* (ACSL wiki): states, one initial state, final (double-circled) states, labelled transitions.
    - Regular expressions use concatenation, union `|` (or `U`), and Kleene star `*`, with precedence star, then concatenation, then union.
    - The extended syntax is `?`, `+`, `.`, `[abc]`, `[^abc]`, `[a-z]`, and `()`; `λ` is the empty string.
    - The identities include `(a*)* = a*`, `aa* = a*a`, `aa* U λ = a*`, `a(b U c) = ab U ac`, `a(ba)* = (ab)*a`, and `(a U b)* = (a*b*)* = a*(ba*)*`.
    - Question types: FSA to regular expression, simplification, equivalence, and which strings are accepted.
    - Wiki samples: `00*1*1U11*0*0` accepts `0000001111111` and `10`; `[A-D]*[a-d]*[0-9]` accepts `ABCD8`, `abcd5`, `ABcd9`, `DCCBBBaaaa5`; `Hi?g+h+[^a-ceiou]` accepts `HigghhhC`, `Highd`, `HgggggghX`.

## Shared rules for this plan

**Verification helpers.** Evaluators that check answers live in `acsl/units/<unit>/assets/verify/`, with plan 094's recipe (`sys.path.insert(0, "assets/verify")`, then `import`; `__pycache__/` git-ignored):
- `bool_eval.py` (unit 08): parses the book's Boolean notation (below). It evaluates an expression for given values, lists the satisfying tuples in canonical order, counts them, and tests equivalence by full truth table.
- `ds_eval.py` (unit 09): runs a `PUSH`/`POP` script on a stack or a queue, builds a BST (duplicates left) and reports the depths, internal path length, external node count, external path length, leaves and height, and builds a min-heap by insertion and reports its rows.
- `fsa_eval.py` (unit 11): tests acceptance for ACSL regular expressions (translating `U` to `|` and `λ` to the empty string, then using Python's `re.fullmatch`) and runs a DFA given as a transition table.

Verify cells are exempt from `source-policy` and `concept-scan`, so `fsa_eval.py` may use `re`; student code never does.
Each evaluator must pass its **pre-written** test file before any answer is trusted:
- `tests/test_acsl_eval_bool.py`
- `tests/test_acsl_eval_ds.py`
- `tests/test_acsl_eval_fsa.py`

A verify cell's expression string is byte-identical to the statement's.

**The book's Boolean notation**, which all items and answers use:
- `~` NOT, applying to the variable or bracket right after it (`~A`, `~(A + B)`)
- `*` AND, `+` OR, `⊕` XOR, `⊙` XNOR, with a single space around every binary operator
- `1` and `0` for TRUE and FALSE
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
- Units 08, 09 and 11 require only *Python by Projects* and Foundations ids (plus `postfix-eval` for unit 09's stack idiom).
- Unit 10 also practises `code-tracing`, `acsl-pseudocode` and `grid-2d` (unit 03), and **introduces nothing** (`introduces: []`).
- The checkpoint is strict over *Python by Projects* plus units 00–11. Its author writes from these specs; A2 re-checks every id against the units' final manifests.

**Canonical answer text** (plan 093–094 rules, plus the rules below):
- **Boolean values and counts:** `1`, `0`, or a bare integer count.
- **Satisfying tuples:** `(A,B)` values with no inner spaces, in ascending binary order, separated by `, `: `(1,0), (1,1)`. Three variables give `(A,B,C)` triples.
- **Simplified expressions:** a sum of products in the book's notation, with literals in each term in alphabetical order (`~A * B`, not `B * ~A`). Terms go in alphabetical order of their first variable, and on a tie a shorter term first. `0` and `1` stand alone.
  - Every simplify item's minimal answer must be unique under these rules; the verify cell asserts both the string and truth-table equivalence to the original.
- **Data structures:**
  - popped values as integers or letters
  - `NIL` for an empty `POP`
  - a heap or tree row as its letters or numbers left to right, with letters run together (`RORN`) and numbers separated by single spaces
  - path lengths, depths and counts as bare integers
- **Accepted strings / option lists:** the labels of the accepted options in the order they are listed, separated by `, ` (`A, E` or `1, 2, 3, 7`); `NONE` when none is accepted.
- **Regular-expression answers** are asked as option choices (which expression is equivalent / describes the FSA), never as free text.

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
  - five skills: evaluate a statement, build a truth table, simplify with the laws (De Morgan and the basic identities), count the ordered pairs that make it true, and test equivalence by truth table
  - ≥ 6 contiguous `acsl-elementary` short-answer items open the exercises, before any other tag
- **Junior and above:**
  - 3 variables; the full list of laws; XOR and XNOR with their identities
  - the wiki's overbar/juxtaposition notation translated to the book's
  - simplification by the laws; finding all satisfying tuples
  - Python: `and`, `or`, `not`, and `!=` as XOR on 0/1 values, with a truth-table loop that counts or lists the solutions
- **Intermediate and above:** longer simplifications, nested negations, and 4-variable tuple counts.

### `unit-09-data-structures` — Data Structures

- **Divisions:** junior, intermediate, senior. **Introduces:** the ACSL-only `acsl-data-structures` ("Stacks, queues, BSTs and heaps (ACSL conventions)", technique, data-structures).
- **Rules from ACSL's page:** stacks and queues with `PUSH`/`POP` (`NIL` when empty); BSTs with duplicates to the left; depth, internal/external path length and external nodes; min-heaps built by insertion.
- **Junior:** stack and queue traces; building a BST from a word or list and reading its depths, leaves and internal path length.
- **Intermediate and above:** external path length and external-node counts; min-heaps (rows, the bottom row, the position of an item); mixed `PUSH`/`POP` scripts with arithmetic on popped values, as in the wiki sample.
- **Python:** the idioms above, used to build what the statements describe and print it.
- **Out:** deletion from a BST or a heap, balanced trees, and traversals (not on ACSL's page).

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
- **Python:** a DFA simulator from a table read from input, and a hand-written matcher for one-character patterns with `?`, `+` and `*` (with recursion or loops). The student never uses `re`.
- **Out:** NFA-to-DFA conversion, and minimisation.

### `checkpoint-03-contest-3-practice` — Practice (contest 3)

- **Divisions:** junior, intermediate, senior. **9 questions:**
  - Q1–Q2 Boolean Algebra, `acsl-junior` (Q2 the harder: satisfying tuples)
  - Q3–Q4 Data Structures, `acsl-junior` (one stack/queue item, one BST item)
  - Q5–Q6 WDTPD – Arrays, `acsl-junior`, at least one in pseudocode
  - Q7–Q8 FSAs and Regular Expressions, `acsl-intermediate` (one FSA item, one regular-expression item)
  - Q9 the single `acsl-junior` programming problem, last, on Contest 3 material, with the sample plus ≥ 4 hidden-style fixtures
- **Paths:**
  - Junior: Q1–Q6 + Q9
  - Intermediate and Senior: Q1–Q4, Q7–Q8 + Q9
  - Classroom (its Contest 3 categories are Boolean Algebra, FSAs and Regular Expressions, and Data Structures): Q1–Q4 + Q7–Q8, with Q5–Q6 optional extra
  - Elementary: unit 08's Elementary items, as 6 questions in 30 minutes
- The student page lists every path, and Q9's timing line names only the programming paths.
- **Teacher notes:** Grading in ACSL's format (6 short answers in 30 minutes; the programming problem scored on its test data).

## Phase A1 — Registry and tooling, before authoring

- **Inline:** `acsl/curriculum/concepts.yaml` gains `boolean-algebra` (byte-identical to USACO's) and the ACSL-only `acsl-data-structures` and `fsa-regex`.
- **Opus tooling subagent:** **pre-written evaluator tests** (expected values from the ACSL wiki and the Elementary doc, one file per evaluator; each imports its evaluator from the unit's `assets/verify/` and skips until that module exists):
  - `tests/test_acsl_eval_bool.py`:
    - the wiki's two samples: equivalence to `A`, and the solutions `(1,0), (1,1)`
    - the Elementary doc's `~(A + ~B) + ~A * B` equivalent to `~A * B`
    - precedence cases for `~`, `*`, `⊕`/`⊙` and `+`, left to right on ties
    - De Morgan, and each XOR/XNOR identity
    - canonical tuple order for 2 and 3 variables, and counts
  - `tests/test_acsl_eval_ds.py`:
    - the wiki's three samples (`-2`, `RORN`, `12`)
    - `NIL` on an empty `POP`, for a stack and for a queue
    - a duplicate going left
    - depth, height, leaves, the external node count (= n + 1) and the external path length on a hand-checked tree
    - heap rows for a numeric list
  - `tests/test_acsl_eval_fsa.py`:
    - the wiki's three "accepted" samples, with every listed option accepted or rejected as the wiki states
    - `U` and `λ` translation
    - each wiki identity checked for equal acceptance on all strings up to length 6
    - a DFA table run

## Phase B — Lessons and statements (Opus subagents in parallel, one per entry, each owning only its folder)

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

## Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN, in a solo run on the final commit.
2. The global concept check passes with the shared `boolean-algebra`. The three pre-written evaluator test files pass, with no skips, on the ACSL wiki and Elementary-doc samples.
3. A script reports the actual question ids and tags for each checkpoint path:
   - Junior: Q1–Q6 + Q9
   - Intermediate/Senior: Q1–Q4, Q7–Q8 + Q9
   - Classroom: Q1–Q4, Q7–Q8

   It also checks that unit 08 has ≥ 6 contiguous `acsl-elementary` items before any other tag.
4. Blind solves: reviewers solve all 8 checkpoint short answers and at least 3 items per unit.
5. Post-execution report.

## Out of scope

- Contest 4 (096).
- The USACO trim (097).
- ACSL publication.

## Plan Review

## Content Review

## Post-Execution Report
_(filled before merge.)_
