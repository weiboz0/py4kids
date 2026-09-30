# Glossary

**Adjacency list** — A way to store a graph: a dictionary that maps each node to a list of its neighbours; an undirected edge is added in both directions. *(Unit 13)*
<!-- concept: graph-repr; index: adjacency list; graph -->

**Backtracking** — Building an answer one choice at a time: try a choice, recurse on the rest, then undo the choice before trying the next, so that every valid answer is counted. *(Unit 9)*
<!-- concept: backtracking; index: undo -->

**Base conversion** — Writing a number in another base, such as binary (base 2) or hexadecimal (base 16): repeated `% base` and `// base` give the digits from the right, and `value = value * base + digit` reads them back. *(Unit 11)*
<!-- concept: base-conversion; index: hexadecimal; base 16 -->

**Binary search** — Finding a target in a sorted list by checking the middle and keeping only the half that could hold it, so it takes about `O(log n)` steps; it can also search over the answer, such as the smallest capacity that works. *(Unit 5)*
<!-- concept: binary-search; index: lower bound; search over the answer -->

**Bitmask** — An integer whose bits mark a subset: bit `i` set means item `i` is included, so the masks `0` to `(1 << n) - 1` list every subset of `n` items. *(Unit 11)*
<!-- concept: bitmask; index: masks; mask -->

**Bitwise operators** — Operators that work on the bits (binary digits) of integers: `&` (and), `|` (or), `^` (exclusive or), `~` (not), and the shifts `<<` and `>>`. *(Unit 11)*
<!-- concept: bitwise-ops; index: bitwise; bits; bit -->

**Boolean algebra** — The rules for combining `True` and `False` with `and`, `or`, and `not`, such as De Morgan's laws: `not (a and b)` equals `(not a) or (not b)`. *(Unit 2)*
<!-- concept: boolean-algebra; index: Boolean logic; truth table; De Morgan -->

**Breadth-first search** — Exploring a graph or grid layer by layer from a start, with a `deque` as a queue; the first time it reaches a place is along a shortest path. *(Unit 13)*
<!-- concept: bfs; index: BFS -->

**Code tracing** — Following a program line by line on paper, keeping track of each variable, to predict exactly what it prints before running it. *(Unit 2)*
<!-- concept: code-tracing; index: tracing; trace -->

**Complete search** — Trying every allowed choice, such as every pair or every triple, and keeping the ones that work; it is always correct, but fast enough only when N is small. *(Unit 5)*
<!-- concept: complete-search; index: brute force; every combination -->

**Depth-first search** — Exploring as deep as possible before backing up, usually by recursing into each unvisited neighbour; afterwards the `visited` set holds every node reachable from the start. *(Unit 13)*
<!-- concept: dfs; index: DFS -->

**Deque** — `deque()` from `collections` is a double-ended queue: a stack with `appendleft`, `popleft`, and `stack[0]` (newest first), or a queue with `append` and `popleft` (oldest first). *(Unit 10)*
<!-- concept: deque; index: `deque`; stack; queue -->

**Flood fill** — Marking every open cell connected to a start cell by recursing into its four neighbours, skipping walls, edges, and cells already visited; it measures one region, and repeated fills count the regions. *(Unit 13)*
<!-- concept: flood-fill; index: flood-fill; region -->

**GCD** — The greatest common divisor: the largest number that divides both `a` and `b`. Euclid's algorithm repeats `a, b = b, a % b` until `b` is 0; then `a // gcd * b` is the least common multiple. *(Unit 11)*
<!-- concept: gcd; index: Euclid; greatest common divisor -->

**Greedy algorithm** — An algorithm that takes the locally best choice at each step, often after sorting by the right key; an exchange argument shows why it is safe, and a counterexample shows when it fails. *(Unit 6)*
<!-- concept: greedy; index: greedy; exchange argument -->

**Grid** — A table of rows and columns stored as a list of lists; `grid[r][c]` is the value in row `r`, column `c`. *(Unit 1)*
<!-- concept: grid-2d; index: list of lists; list-of-lists -->

**Modular arithmetic** — Working with remainders: taking `% m` after every multiplication keeps the numbers small without changing the final remainder. *(Unit 11)*
<!-- concept: modular-arithmetic; index: modular; modulo -->

**Parsing input** — Turning the input text into the numbers and words a program needs, usually by splitting it into tokens and converting each one in order. *(Unit 1)*
<!-- concept: input-parse; index: parsing; parse; parses -->

**Postfix evaluation** — Working out an expression whose operators come after their two values, such as `8 3 -`: push each number on a stack, and at each operator pop the right value, then the left, and push the result. *(Unit 10)*
<!-- concept: postfix-eval; index: postfix -->

**Prefix sum** — A list `pre` in which `pre[i]` is the total of the first `i` values, with `pre[0] = 0`, so any range total is one subtraction: `pre[right + 1] - pre[left]`; a prefix grid does the same for rectangles. *(Unit 8)*
<!-- concept: prefix-sum; index: prefix array; prefix grid; cumulative totals -->

**Recursion** — A function calling itself on a smaller version of the same problem, with a base case that stops the calls. *(Unit 9)*
<!-- concept: recursion; index: recursive; base case -->

**Set literal** — Braces around values, such as `{"Ava", "Bo"}`, make a set: a collection that keeps each distinct value once and answers `in` quickly; `set()` makes an empty one. *(Unit 4)*
<!-- concept: set-literal; index: sets; distinct values -->

**Set operations** — `.add` and `.discard` put a value into a set or take it out; the union holds the values in either set, the intersection the values in both, and `first - second` the values only in the first. *(Unit 4)*
<!-- concept: set-ops; index: membership; union; intersection -->

**Sieve of Eratosthenes** — A way to find every prime up to N: mark every number as prime, then for each prime `p` mark `p*p`, `p*p + p`, … as not prime; the numbers still marked are the primes. *(Unit 11)*
<!-- concept: sieve; index: sieve; primes -->

**Simulation** — Solving a problem by following its rules exactly, step by step and in order, while tracking the changing state and guarding every edge. *(Unit 7)*
<!-- concept: simulation; index: simulate; ad hoc -->

**Sort key** — `sorted(items, key=by_score)` orders items by the value that a named key function returns; return a negated field to put the largest first, or a tuple such as `(-score, name)` to break ties. *(Unit 4)*
<!-- concept: sorted-key; index: key function; compound key -->

**Splitting text** — `.split()` breaks text on every run of spaces and newlines into a list of string tokens, such as `"3\n4 9"` into `['3', '4', '9']`. *(Unit 1)*
<!-- concept: str-split; index: `.split`; tokens -->

**Time complexity** — How fast a program's work grows with the input size N, written in Big-O form such as `O(n)`, `O(n log n)`, or `O(n²)`; with the constraints, it tells you whether a plan is fast enough. *(Unit 3)*
<!-- concept: complexity; index: complexity; growth -->

**Tree traversal** — Visiting every node of a binary tree in a fixed order: pre-order visits a node before its left and right subtrees, in-order between them, and post-order after them. *(Unit 12)*
<!-- concept: tree-traversal; index: binary tree; pre-order; traversal -->

**Tuple** — An ordered group of values in parentheses, such as `("Ava", 8)`, that keeps one record's fields together; `name, score = record` unpacks it into separate variables. *(Unit 4)*
<!-- concept: tuple; index: tuples -->

**Two pointers** — Two indices that each move only one way through a list, so the whole scan is `O(n)`: converging pointers find a pair in a sorted list, and a sliding window grows on the right and shrinks on the left. *(Unit 14)*
<!-- concept: two-pointers; index: pointers; sliding window -->
