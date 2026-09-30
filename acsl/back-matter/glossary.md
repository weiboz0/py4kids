# Glossary

**ACSL pseudocode** — The small programming language of ACSL's *What Does This Program Do?* questions, with `INPUT`, `OUTPUT`, `IF … THEN … END IF`, `FOR … NEXT` and `WHILE … END WHILE`; its `int(x)` rounds down, its `FOR` includes the end value, and its substrings are not Python slices. *(Unit 3)*
<!-- concept: acsl-pseudocode; index: pseudocode -->

**Assembly language** — ACSL's made-up low-level language: each line has an optional label, an opcode such as `LOAD`, `ADD` or `BG`, and a location; every calculation happens in one accumulator, `ACC`, and `DIV` rounds toward zero. *(Unit 15)*
<!-- concept: acsl-assembly; index: accumulator; opcode -->

**Base conversion** — Writing a number in another base, such as binary (base 2) or hexadecimal (base 16): repeated `% base` and `// base` give the digits from the right, and `value = value * base + digit` reads them back. *(Unit 1)*
<!-- concept: base-conversion; index: hexadecimal; base 16 -->

**Bit-string flicking** — Changing a row of bits with `NOT`, `AND`, `OR` and `XOR`, the shifts `LSHIFT-x` and `RSHIFT-x` (bits fall off and zeros come in), and the circulates `LCIRC-x` and `RCIRC-x` (bits wrap around); `NOT` goes first and `OR` last. *(Unit 5)*
<!-- concept: bitwise-ops; index: bit string; circulate -->

**Boolean algebra** — Working with values that are 1 (TRUE) or 0 (FALSE), written `~A` (NOT), `A * B` (AND), `A + B` (OR), `A ⊕ B` (XOR) and `A ⊙ B` (XNOR); laws such as De Morgan's `~(A + B) = ~A * ~B` simplify an expression. *(Unit 8)*
<!-- concept: boolean-algebra; index: truth table; De Morgan; tautology -->

**Code tracing** — Following a program line by line on paper, keeping track of each variable, to predict exactly what it prints before running it. *(Unit 3)*
<!-- concept: code-tracing; index: tracing; trace -->

**Complete search** — Trying every allowed choice, such as every pair or every triple, and keeping the ones that work; it is always correct, but fast enough only when N is small. *(Unit 0)*
<!-- concept: complete-search; index: brute force -->

**Data structures** — The structures of ACSL's Contest 3: a stack (`POP` takes the newest item), a queue (`POP` takes the oldest), a binary search tree (an equal key goes left), and a heap (a min-heap: every node is at most its children; a max-heap the reverse). *(Unit 9)*
<!-- concept: acsl-data-structures; index: stack; queue; binary search tree; heap -->

**Finite state automaton** — A machine of states and transitions that reads a string one symbol at a time and accepts it when it ends in a final state; a regular expression describes the same kind of set of strings. *(Unit 11)*
<!-- concept: fsa-regex; index: FSA; regular expression -->

**Graph** — Vertices joined by edges, written as two sets such as `{A, B, C}` and `{AB, BC}`; an adjacency matrix `M` has a 1 for each edge, and `M²` counts the paths of length 2. *(Unit 12)*
<!-- concept: acsl-graph-theory; index: vertex; adjacency matrix; cycle -->

**Grid** — A table of rows and columns stored as a list of lists; `grid[r][c]` is the value in row `r`, column `c`. *(Unit 3)*
<!-- concept: grid-2d; index: list of lists; 2D array -->

**LISP** — A language whose statements are lists, such as `(ADD 2 3)`: the function comes first, the innermost lists are worked out first, a quote `'` keeps a list as it is, and `CAR`, `CDR` and `CONS` take lists apart and build them. *(Unit 7)*
<!-- concept: lisp-eval; index: atom -->

**Logic gate** — A circuit part that turns one or two input signals, each 0 or 1, into one output: BUFFER, NOT, AND, NAND, OR, NOR, XOR or XNOR; a netlist lists a circuit's gates, one per line. *(Unit 13)*
<!-- concept: logic-gates; index: gate; netlist; circuit -->

**Parsing input** — Turning the input text into the numbers and words a program needs, usually by splitting it into tokens and converting each one in order. *(Unit 0)*
<!-- concept: input-parse; index: contest input -->

**Postfix evaluation** — Working out an expression whose operators come after their two values, such as `8 3 -`: push each number on a stack, and at each operator pop the right value, then the left, and push the result. *(Unit 4)*
<!-- concept: postfix-eval; index: postfix -->

**Recursion** — A function calling itself on a smaller version of the same problem, with a base case that stops the calls. *(Unit 2)*
<!-- concept: recursion; index: recursive; base case -->

**Splitting text** — `.split()` breaks text on every run of spaces and newlines into a list of string tokens, such as `"3\n4 9"` into `['3', '4', '9']`. *(Unit 0)*
<!-- concept: str-split; index: `.split` -->

**Tree traversal** — Visiting every node of a binary tree in a fixed order: preorder visits a node before its left and right subtrees, inorder between them, and postorder after them. *(Unit 9)*
<!-- concept: tree-traversal; index: traversal; preorder; inorder -->

**Tuple** — An ordered group of values in parentheses, such as `("Ava", 8)`, that keeps one record's fields together; `name, score = record` unpacks it into separate variables. *(Unit 0)*
<!-- concept: tuple; index: tuples -->
