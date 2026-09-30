# Quick Reference

Use this as a reminder after you have met an idea in its unit.
Short answers are worked by hand, so most of this card is ACSL's notation and its traps.
Every programming answer reads its input with `input()` and prints exactly the answer, with nothing extra.

## Reading contest input · Unit 0

```python
parts = input().split()     # one line, split into pieces
n = int(parts[0])           # a piece is text: convert it
name = parts[1]             # keep a word as a string

values = []
for piece in input().split():   # N values on one line
    values.append(int(piece))

count = 0
value = int(input())        # read before the loop ...
while value != 0:           # ... until the 0 that ends the input
    count = count + 1
    value = int(input())    # ... and again at the end of the loop
```

A tuple keeps two values together: `best = (a, b)`, and `a, b = best` unpacks it.
To try every pair of positions once, start the inner loop at `i + 1`.

## Number bases · Unit 1

| Base | Digits | Place values, from the right |
|---|---|---|
| 2 | 0 1 | 1, 2, 4, 8, 16, 32, … |
| 8 | 0 to 7 | 1, 8, 64, 512, … |
| 16 | 0 to 9, A to F | 1, 16, 256, 4096, … |

- 101101₂ means base 2; a number with no base written is in base 10. A = 10, B = 11, …, F = 15.
- To base 10: multiply each digit by its place value and add.
- From base 10: divide by the base again and again, and read the remainders from the last to the first.
- 2 ↔ 8 ↔ 16: one octal digit is 3 bits and one hex digit is 4 bits; group the bits from the **right** (after a point, from the point to the right).
- Adding in base b, a column that reaches b carries 1; a borrowed 1 is worth b.
- A colour `#RRGGBB` holds red, green and blue, two hex digits each, from 00 to FF (255).
- In Python, `int("2D", 16)` is 45; to go from base 10, write the repeated division yourself.

## Recursive functions · Unit 2

```text
f(x) = { f(x - 3) + x      if x > 10
       { 2 * x - 5         if x <= 10
```

- Use the one row whose condition is true; `otherwise` means no row above fits.
- `x mod 3` is the remainder, `floor(x / 2)` rounds down, and `abs(x)` drops the sign.
- Call table: go down, writing what each call turns into, until a base case; then fill in the values coming back up.

## ACSL pseudocode · Unit 3

| ACSL | Python | Watch out |
|---|---|---|
| `/` | `/` | real division: `7 / 2` is `3.5` |
| `int(x)` | `math.floor(x)` | rounds **down**: `int(-3.7)` is `-4` |
| `int(a / b)` | `a // b` | for whole numbers `a` and `b` |
| `^` or `↑` | `**` | `2 ^ 5` is 32 |
| `sqrt(x)` | `math.sqrt(x)` | gives a float |
| `ELSE IF` | `elif` | only the first true branch runs |
| `A(3)`, `A(r, c)` | `A[3]`, `A[r][c]` | round brackets for arrays |

ACSL's `!`, `&&` and `||` are Python's `not`, `and` and `or`; write `not (…)` with brackets.
ACSL's order: `!`, then `^`, then `*`, `/` and `%`, then `+` and `-`, then the comparisons, then `&&`, and `||` last.
Python puts `not` after the comparisons, so add brackets when you translate.

`FOR` **includes** its end value; `range` stops one step before its end:

| ACSL | Python | Values |
|---|---|---|
| `FOR k = 1 TO 9 STEP 2` | `range(1, 10, 2)` | 1, 3, 5, 7, 9 |
| `FOR k = 20 TO 2 STEP -6` | `range(20, 1, -6)` | 20, 14, 8, 2 |

Substrings, with positions from 0, for `S = "ELEPHANT"`:

| ACSL | Means | Gives | Python |
|---|---|---|---|
| `S[:n]` | the **first** n characters | `S[:2]` is `EL` | `S[:n]` |
| `S[n:]` | the **last** n characters | `S[3:]` is `ANT` | `S[len(S) - n:]` |
| `S[a:b]` | positions a **through** b | `S[1:3]` is `LEP` | `S[a:b + 1]` |

When a question shows Python, use Python's rules; when it shows ACSL pseudocode, use ACSL's.

## Prefix, infix and postfix · Unit 4

| Notation | `3 + 4` is written |
|---|---|
| infix | `3 + 4` |
| prefix | `+ 3 4` |
| postfix | `3 4 +` |

- Infix order (PEMDAS): brackets, then `↑`, then `*` and `/`, then `+` and `-`; the same level goes left to right.
- Infix to prefix or postfix: fully bracket, keep the operands in order, and move each operator in front of or after its two operands, inside out.
- Postfix with a stack: push each operand; at an operator pop the **right** value, then the left, and push *left operator right*.
- Prefix with a stack: read from the right; the first value popped is the **left** one.
- Write a whole answer with no decimal point, and any other answer as a decimal, such as `15.5`.

## Bit-string flicking · Unit 5

| Operator | What it does |
|---|---|
| `NOT` (`~`) | flips every bit |
| `AND` (`&`) | 1 where both bits are 1 |
| `OR` | 1 where at least one bit is 1 |
| `XOR` (`⊕`) | 1 where the bits differ |
| `LSHIFT-x`, `RSHIFT-x` | move x places; the bits that fall off are lost, and zeros come in |
| `LCIRC-x`, `RCIRC-x` | move x places; the bits that fall off come back in at the other end |

Order, first to last: brackets, `NOT`, then the shifts and circulates, then `AND`, then `XOR`, then `OR`.
Two-string operators of the same level go left to right; one-string operators go right to left, the one nearest the string first.

- A shorter string is padded with 0s on the **left**; write every bit of the answer.
- Circulating n bits by n places changes nothing, so only the count `% n` matters.
- Solving for x: write x as letters, `abcde`, push them through, and line them up with the answer; a letter that never meets the answer is free (0 or 1).
- In Python, on whole numbers of n bits with `mask = 2 ** n - 1`: `a & b`, `a | b`, `a ^ b` (XOR), `(a << k) & mask`, `a >> k`, and `NOT a` as `a ^ mask`.

## Loops in pseudocode · Unit 6

- A `FOR` loop that runs makes `int((end - start) / step) + 1` passes; one whose start is already past its end makes none.
- `WHILE` tests at the top, before each pass, never in the middle.
- In a running maximum, `>` keeps the **first** of equal values and `>=` keeps the **last**.
- `n % 10` is the last digit of `n`, and `int(n / 10)` removes it.

## LISP · Unit 7

| Statement | Value |
|---|---|
| `(ADD 1 4 2)`, `(MULT 2 3 4)` | 7, 24 (any number of arguments) |
| `(SUB 3 10)`, `(DIV 30 4)` | -7, 7.5 |
| `(SQUARE 3)`, `(EXP 2 4)` | 9, 16 |
| `(EQ 2 2)`, `(POS 0)`, `(NEG -7)` | `true`, `NIL`, `true` |
| `(CAR '(A B C))` | `A`, the first item |
| `(CDR '(A B C))` | `(B C)`, the list without its first item |
| `(CONS 'A '(B C))` | `(A B C)` |
| `(REVERSE '((1 2) 3))` | `(3 (1 2))` |
| `(ATOM 'A)`, `(ATOM '(A))` | `true`, `NIL` |
| `(SETQ X 5)`, `(SET 'X 5)` | 5, and `X` now holds 5 |
| `(EVAL '(ADD 3 4))` | 7 |
| `(DEF F (L) (CAR L))` | defines `F`; `DEFUN` is the same |

- Work from the innermost list outwards. `+`, `-`, `*` and `/` may stand for `ADD`, `SUB`, `MULT` and `DIV`.
- `CADR` is `(CAR (CDR x))`: do the letters between `C` and `R` from right to left.
- `()` is `NIL`, and so is the `CDR` of a one-item list.

## Boolean algebra · Unit 8

| This book | ACSL paper | Meaning |
|---|---|---|
| `~A` | $\overline{A}$ | NOT |
| `A * B` | $AB$ | AND |
| `A + B` | $A + B$ | OR |
| `A ⊕ B` | $A \oplus B$ | XOR: 1 when different |
| `A ⊙ B` | $A \odot B$ | XNOR: 1 when the same |

Order, first to last: brackets, `~`, `*`, then `⊕` and `⊙`, then `+`; the same level goes left to right.
A long bar is a bracket: $\overline{AB}$ is `~(A * B)`, but $\overline{A}\,\overline{B}$ is `~A * ~B`.

- De Morgan: `~(A + B) = ~A * ~B` and `~(A * B) = ~A + ~B`.
- Absorption: `A + A * B = A`, `A * (A + B) = A`, and `A + ~A * B = A + B`.
- Also `A + ~A = 1`, `A * ~A = 0`, `A + 1 = 1`, `(A + B) * (A + C) = A + B * C`, and `A ⊕ B = A * ~B + ~A * B`.
- Truth-table rows count up in binary: `00`, `01`, `10`, `11`.
- Write tuples as `(0,1), (1,0)`, or `NONE`; write a simplified answer as a sum of products, letters in alphabetical order, a plain letter before its `~` form.
- In Python, for 0s and 1s: `not a`, `a and b`, `a or b`, `a != b` (XOR) and `a == b` (XNOR), with brackets round both sides of `!=` and `==`.

## Data structures · Unit 9

| Structure | `PUSH(x)` | `X = POP()` |
|---|---|---|
| stack | puts x on the top | takes the top item (the newest) |
| queue | puts x at the back | takes the front item (the oldest) |

`POP()` on an empty stack or queue gives `NIL`.

- Binary search tree: a key **less than or equal to** a node goes left, a larger key goes right, so a duplicate goes left.
- The root has depth **0**; the internal path length is the sum of all the depths.
- A tree of n nodes has n + 1 external nodes, and external path length = internal path length + 2n.
- Preorder: node, left, right. Inorder: left, node, right (sorted order in a BST). Postorder: left, right, node.
- Min-heap: each node is at most its children, and the rows fill from the left. Insert at the next free place, then swap up while smaller than the parent.
- Heap positions from 1: the children of i are 2i and 2i + 1, and its parent is `i // 2`.
- Delete the root: move the last item to the root, then swap down with the smaller child while larger than it.

## Arrays · Unit 10

- `A(1) = 4, A(2) = 9` fills boxes from the left; use the positions the program uses.
- An array that starts at `A(1)` becomes a Python list with an unused `0` at position 0.
- In n boxes, `A(n + 1 - i)` is the mirror of box i.
- In a square grid of size n, the main diagonal is `A(i, i)` and the other diagonal is `A(i, n + 1 - i)`.
- Swap with a helper: `t = A(i)`, `A(i) = A(j)`, `A(j) = t`.

## FSAs and regular expressions · Unit 11

- An FSA table: `→` marks the initial state, `(final)` each final state, and `—` a missing move, which rejects the string.
- Only the state at the end matters. `λ` is the empty string.
- Order: star `*`, then concatenation, then union `|` (also written `U`). So `ab*` is `a(b*)`, and `a|bc` is `a|(bc)`.

| Symbol | Matches |
|---|---|
| `x*` | zero or more `x` |
| `x+` | one or more `x` |
| `x?` | zero or one `x` |
| `.` | any one character |
| `[abc]`, `[a-z]` | one character listed, or in the range |
| `[^abc]` | one character **not** listed |

One string that fits one expression and not the other shows that two expressions are not equivalent.

## Graph theory · Unit 12

- The degrees add up to twice the number of edges.
- A path's length is its number of edges; a simple path repeats no vertex.
- **Counting cycles:** the Elementary division counts each cycle once in **each direction**; Junior, Intermediate and Senior count it **once**. `ABDA` and `BDAB` are always the same cycle.
- An undirected cycle has at least 3 vertices; in a directed graph `ABA` is a cycle when `AB` and `BA` are both edges.
- A complete graph with V vertices has V × (V − 1) ÷ 2 edges.
- Traversable: one connected piece, and 0 or 2 vertices of odd degree (start at one, finish at the other).
- Adjacency matrix: row `i`, column `j` is 1 for an edge from `i` to `j`. Entry (i, j) of `M^p` counts the paths of length p, which may repeat vertices.
- A tree with N vertices has N − 1 edges; a forest with N vertices and E edges is N − E trees.
- `AB3` is an edge of weight 3; the cost of a path is the total of its weights.

## Digital electronics · Unit 13

| Gate | Output is 1 when | Expression |
|---|---|---|
| BUFFER | the input is 1 | `A` |
| NOT | the input is 0 | `~A` |
| AND | both inputs are 1 | `A * B` |
| NAND | not both are 1 | `~(A * B)` |
| OR | at least one is 1 | `A + B` |
| NOR | both are 0 | `~(A + B)` |
| XOR | the inputs differ | `A ⊕ B` |
| XNOR | the inputs are the same | `A ⊙ B` |

```text
INPUTS A B C
p = NAND(A, B)
out = OR(p, C)
```

- A netlist's first line names the inputs; each other line is one gate, after the gates that feed it; the last line is the output.
- A bubble on a gate's picture means NOT.
- Every input on the `INPUTS` line is a column of the truth table, even if no gate uses it.
- NAND alone can build anything: `NOT(A)` is `NAND(A, A)`, and `OR(A, B)` is `NAND(NAND(A, A), NAND(B, B))`.

## Strings in pseudocode · Unit 14

- `S[:n]` and `S[n:]` have n characters, and `S[a:b]` has b − a + 1; `S[j:j]` is one character.
- Walk every position with `FOR j = 0 TO len(S) - 1`.
- `T = T + S[j]` copies in order; `R = S[j] + R` builds the reverse.
- `+` joins with no space, and a space is a character.
- `<` and `>` compare capital letters by their order in the alphabet.

## Assembly language · Unit 15

| Opcode | What it does |
|---|---|
| `DC` | the label names a location holding `LOC` |
| `LOAD`, `STORE` | copy `LOC` into `ACC`; copy `ACC` into `LOC` |
| `ADD`, `SUB`, `MULT` | `ACC` becomes `ACC` + `LOC`, − `LOC`, × `LOC` |
| `DIV` | `ACC` ÷ `LOC`, rounded **toward zero** |
| `BE`, `BG`, `BL` | jump to the label `LOC` if `ACC` = 0, > 0, < 0 |
| `BU` | always jump |
| `READ`, `PRINT` | read a number into `LOC`; print `LOC` |
| `END` | stop |

- A line is `LABEL OPCODE LOC`; the label is optional, and `ACC` starts at 0.
- `=5` is immediate data, the number 5 itself; `STORE` never takes it.
- `-7 DIV 2` is `-3`, not `-4`.
- `ADD`, `SUB` and `MULT` work modulo 1,000,000.
- A branch never changes `ACC`; to compare X and Y, work out X − Y and branch on its sign.
