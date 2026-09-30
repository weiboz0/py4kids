# Plan 096 — ACSL Contest 4: Graph Theory, Digital Electronics, WDTPD – Strings, Assembly Language

**Goal:** Ship the Contest 4 part of *Contest Python: ACSL*: one unit per Contest 4 category, then the Contest 4 practice checkpoint.
This is the study block for the fourth contest window (Mar 1 – May 23, 2027), and it completes the season.

**Spec:** design 009 and the roadmap row for 096. User decision, 2026-09-29: "continue with plan 093 on autopilot and all other contest followed".
Conventions and lessons carried over from plans 093–095:
- canonical short-answer text; one-line WDTPD outputs
- the ACSL dialect of unit 03 (inclusive substrings `S[:n]`, `S[n:]`, `S[a:b]`; `int` = floor; inclusive `FOR`)
- `.pop`, `.index`, `.count`, `.find` and `.join` banned in contest code
- tested verify helpers in `assets/verify/` with pre-written test files, which pin every interface in their docstrings; the helper authors do not edit them; checkpoints import the units' helpers
- `exercises.ipynb` holds statements and `**Your answer:** _(write your answer here)_` placeholders only; answers, verify cells and solutions go in `solutions.ipynb`
- an Elementary lesson with no code the student runs, with Exercises 1–6 as the Elementary mock test; the checkpoint's student page lists every path, and timing lines name only the paths they apply to
- fixtures for every boundary rule a statement states; answers unique by construction and checked by brute force
- no two hooks share a title; a checkpoint item never repeats a unit item's function or data
- per-entry `requires` boundaries; registry before authoring; coverage map and syllabus after, reconciled
- teacher notes inline; separate solutions sessions; blind solves in the gate

## Survey (2026-09-29, main at 17f7936)

- **`season.yaml` Contest 4 units:**
  - Graph Theory — elementary, junior, intermediate, senior
  - Digital Electronics — junior, intermediate, senior
  - WDTPD – Strings — junior
  - Assembly Language — intermediate, senior
- **ACSL papers** (6 short-answer questions each):
  - Junior: Graph Theory, Digital Electronics, What Does This Program Do? – Strings
  - Intermediate and Senior: Graph Theory, Digital Electronics, Assembly Language
  - Elementary: Elementary Graph Theory
  - Classroom: Graph Theory, Digital Electronics, Assembly Language
- **Registry:** `boolean-algebra` (unit 08), `code-tracing`, `acsl-pseudocode`, `grid-2d`, `complete-search`, `recursion` and `dict-*`/`tuple` already exist.
  USACO's `graph-repr` is named "adjacency list" and ACSL works mainly with adjacency matrices, so it is not shared; the ACSL units introduce ACSL-only ids.
- **Official scope** (retrieved 2026-09-29):
  - *Elementary Graph Theory* (ACSL's Elementary doc):
    - **undirected** graphs only, written as a vertex set `{A, B, C, D}` and an edge set `{AB, AC, BC, AD, DB}`; small graphs of about 4–8 vertices; complete graphs
    - simple paths (no repeated vertex), and paths of a given length (for example "all simple paths of length 3 starting from C": `CADB, CABD, CBAD, CBDA`)
    - cycles (the doc lists 6 cycles of one graph, each in both directions from A: `ABDA, ADBA, ABCA, ACBA, ACBDA, ADBCA`)
    - traversability: every edge used once without lifting the pencil, possible only when 0 or 2 vertices have odd degree (and, as the book states it, only when every vertex with an edge is connected)
    - the number of edges of a complete graph
  - *Graph Theory* (ACSL wiki):
    - vertices, edges written as pairs (`AB`), and undirected, directed and weighted graphs
    - path, simple path, cycle (simple except that the first and last vertex are the same), connected graph and components
    - trees (N − 1 edges), forests, spanning trees and DAGs
    - the adjacency matrix `M`, where the entries of `M^p` count the paths of length `p`
    - question types: count cycles in a directed graph; draw a graph from an edge list or matrix; count paths of a given length with matrix powers
  - *Digital Electronics* (ACSL wiki):
    - gates BUFFER, NOT, AND, NAND, OR, NOR, XOR and XNOR, one or two inputs each, each with a truth table
    - circuits shown as diagrams, and every circuit written as a Boolean expression
    - question types: the input tuples that make a circuit TRUE or FALSE, how many make it TRUE, and simplifying a circuit's expression
    - wiki samples: the only triple making one circuit FALSE is `(1, 1, 0)`; another circuit is TRUE for 10 four-input rows; a third simplifies to `0`
  - *What Does This Program Do? – Strings* (ACSL wiki):
    - `len(S)`, positions from 0, `S[j]`, `S[:n]` (the first n), `S[n:]` (the last n), `S[a:b]` (positions a through b), `+` concatenation, `==`
    - the rest of the pseudocode language, as unit 03 teaches
  - *Assembly Language Programming* (ACSL wiki):
    - lines `LABEL OPCODE LOC`, with an accumulator `ACC` that starts at 0
    - opcodes:
      - `LOAD`, `STORE`
      - `ADD`, `SUB`, `MULT` (modulo 1,000,000), `DIV` (the signed integer part)
      - `BE`, `BG`, `BL` and `BU` (branch if `ACC` = 0, > 0, < 0, always)
      - `READ` and `PRINT`
      - `DC` (a labelled constant), `END`
    - immediate data `=value` for `LOAD`, `ADD`, `SUB`, `MULT` and `DIV`
    - wiki samples: one program leaves `-9` in `TEMP`; another computes `N!`

## Shared rules for this plan

**Verification helpers** in `acsl/units/<unit>/assets/verify/`, with the plan 094–095 recipe:
- `graph_eval.py` (unit 12). Every function that reads edge text takes `edges` and the keyword arguments `vertices=None, directed=False`; `matrix_power` takes a matrix instead.
  - `edges` is the statement's edge text pasted verbatim: braces, commas and whitespace are layout, so `"{AB, AC, BC}"` and `"AB AC BC"` are the same. A weighted edge carries its weight after the pair (`AB3`). For a directed graph `AB` goes from A to B. A self-loop `AA` is allowed and puts 1 on the diagonal; items never use self-loops in cycle or traversability questions.
  - `vertices` is an optional string of vertex letters (`"ABCDE"`) naming every vertex, isolated ones included; without it the vertices are those that appear in `edges`. Vertices are always taken in alphabetical order.
  - `matrix(edges, ...) -> list[list[int]]`: the adjacency matrix in alphabetical vertex order, **1 for an edge and 0 otherwise, whatever the weight**. An undirected edge sets both entries. Items never use repeated edges.
  - `matrix_power(M, p) -> list[list[int]]`
  - `count_paths(edges, start, end, length, ...) -> int`: walks of exactly `length` edges, with repeats allowed, as the entry of `M^length` counts them
  - `simple_paths(edges, start, length=None, end=None, ...) -> list[str]`: every simple path from `start` (of exactly `length` edges when given; ending at `end` when given), as vertex strings, sorted alphabetically
  - `cycles(edges, start=None, both_directions=False, ...) -> list[str]`, sorted alphabetically:
    - **with `start`:** every cycle through `start`, written from `start` and back to it. For an undirected graph each cycle appears in both directions, as in the Elementary doc (`ABCA` and `ACBA`); for a directed graph only in the direction its edges allow.
    - **without `start`:** each cycle once, written from its alphabetically smallest vertex. For an undirected graph it goes the direction whose second vertex is smaller.
    - **`both_directions=True`** (undirected only, without `start`): each cycle written from its smallest vertex in **both** directions, which is how the Elementary doc counts (its sample graph has 6).
    - A cycle has at least 3 distinct vertices in an undirected graph, and at least 2 in a directed one (`ABA` when both `AB` and `BA` exist).
  - `degrees(edges, ...) -> dict` (in-degree plus out-degree for a directed graph), `components(edges, ...) -> int` (**undirected only**, as in the wiki's example; it raises for `directed=True`; isolated vertices count as components). Component items use undirected graphs only
  - `traversable(edges, ...) -> bool` (undirected only): True exactly when every vertex **that has an edge** lies in one connected component, and 0 or 2 vertices have odd degree
  - `cheapest(edges, start, end, ...) -> int`: the least total weight over all simple paths, by listing (weighted graphs only)
- `circuit_eval.py` (unit 13). A circuit is a **netlist**. Its first line is `INPUTS A B C` (the circuit's input variables, in alphabetical order, each one a column of every tuple even if no gate uses it). Then comes one gate per line, `NAME = GATE(input, input)` (one input for `BUFFER` and `NOT`), with `GATE` one of `BUFFER NOT AND NAND OR NOR XOR XNOR`; a gate's inputs are declared inputs or earlier gate names. Gate names are lowercase (`p`, `q`, `out`), so they never collide with the capital inputs `A`–`D`. The last line's gate is the output.
  - `evaluate(netlist, values) -> int`, where `values` is a dict from each declared input to 0 or 1
  - `solutions(netlist, value=1) -> str`: the canonical tuple list over the declared inputs in `INPUTS` order, rows in ascending binary order (`(1,1,0)`), or `NONE`
  - `count(netlist, value=1) -> int`
  - `to_expression(netlist) -> str`: the circuit as an expression in the book's Boolean notation, where `NAND(x, y)` is `~(x * y)`, and so on
  - Simplifying reuses unit 08's `bool_eval.minimal_sops`; verify cells import it from `../unit-08-boolean-algebra/assets/verify`.
- `asm_eval.py` (unit 15):
  - `run(program, inputs=()) -> dict` runs an ACSL assembly program, given as text with one instruction per line.
    It returns `{"memory": {label: value}, "printed": [values], "acc": [ACC after each ACC-changing instruction]}`.
  - The semantics are exactly the wiki's:
    - `ADD`, `SUB`, `MULT` and `READ` keep a value modulo 1,000,000, as the wiki states. The book reads this as keeping the sign and the last six digits: a true result `v` becomes `sign(v) × (|v| mod 1,000,000)`, so `999,999 + 1` is `0` and `−999,999 − 2` is `−1`.
      The wiki gives no negative-overflow example, so this is a **book convention**: the lesson labels it so, and **no item assesses it**. Every value an item's program produces stays within ±999,999.
    - `DIV` divides ACC by LOC ("divided into the contents of the ACC") and keeps the signed integer part, rounding toward zero: `-7` `DIV` `2` is `-3`. This is the one place ACSL rounds toward zero, not floor. Items never divide by zero, and the helper raises if one does.
    - `READ` takes the next input, reduced by the same rule.
    - Branches jump to a label; `END` stops.
    - A `STORE` or `READ` to a label with no `DC` creates it (the wiki's `N!` sample does both).
    - **Line parsing:** tokens are split on whitespace. The first token is a label exactly when it is not an opcode (the wiki forbids opcodes as labels), so `DONE END` is a labelled `END` and `LOAD B` is an unlabelled `LOAD`. Statements show programs as fixed-width code blocks, pasted byte-identical into verify cells.
  - A step limit of 100,000 raises an error rather than looping forever.

Each evaluator must pass its **pre-written** test file (`tests/test_acsl_eval_graph.py`, `tests/test_acsl_eval_circuit.py`, `tests/test_acsl_eval_asm.py`) before any answer is trusted.

**Circuits in text.** Notebooks have no drawn diagrams.
Every circuit appears as a netlist (above), and Lesson 1 of unit 13 also shows an ASCII sketch for small circuits, so students can read a drawn circuit on a real paper.
The wiki's gate symbols are described in words and truth tables.

**Graphs in text.** A graph is given as its edge set in the book's form (`{AB, AC, BC}` in statements; a directed edge `AB` goes from A to B), or as an adjacency matrix with labelled rows and columns.
A small ASCII sketch may accompany it.

**Student code idioms** (source policy unchanged):
- a graph as a dict of neighbour lists, or an adjacency matrix (list of lists, `grid-2d`)
- matrix multiplication with three nested loops
- a circuit simulator with a dict of gate values
- an assembly interpreter (Senior) with a dict for memory and a label table

**Per-entry concept boundaries:**
- **Unit 12** introduces the ACSL-only `acsl-graph-theory` ("Graphs: paths, cycles, degrees and adjacency matrices (ACSL)", technique, graphs). It requires *Python by Projects*, Foundations, `grid-2d` (unit 03) and `recursion` (unit 02).
- **Unit 13** introduces the ACSL-only `logic-gates` ("Logic gates and circuits", technique, techniques). It requires `boolean-algebra` (unit 08) and, for its simulator, `dict-literal`, `dict-access`, `str-split` and `input-parse`.
- **Unit 14** introduces nothing (`introduces: []`); it practises `code-tracing` and `acsl-pseudocode`, and requires `string-index`, `string-slice` and `string-concat`.
- **Unit 15** introduces the ACSL-only `acsl-assembly` ("ACSL assembly language", technique, techniques). It requires `dict-*`, `str-split` and `input-parse`.
- **The checkpoint** is strict over *Python by Projects* plus units 00–15.

**Canonical answer text** (plans 093–095, plus these):
- **Paths and cycles:** vertex strings with no separators (`CADB`), listed in alphabetical order and separated by `, `; counts as bare integers. Each counting item states in words what counts (a walk that may repeat vertices, a simple path, a cycle counted once, or a cycle in each direction).
  - **Elementary** items follow the Elementary doc: an undirected cycle counts in **each direction**, and paths of a given length are **simple** paths in order (its "paths of length 2" count is 12, not the 22 walks of `M^2`).
  - **Junior and above** follow the wiki: a cycle counts **once** ("HEGH and EHGE are different ways to identify the same cycle"), and a directed cycle only in its own direction.
  - `acsl-elementary` items never ask for cycles "counted once".
- **Matrices:** an item asks for one entry or a row sum as an integer, never a whole matrix.
- **Yes/no** (for example traversable): `YES` or `NO`.
- **Circuits:** tuples and counts as in unit 08; simplified expressions as unit 08's unique minimal sum of products, with `0` and `1` standing alone.
- **Assembly:** the value in a named location, or the printed values in order separated by single spaces.
- **Option lists:** capital letters as in plan 095.

## The entries (all under `acsl/`)

Unit conventions:
- a project-first hook with a title no other unit uses, and 3 lessons. The 12 titles already taken are: Pairs That Make the Target; Three Friends, One Number?; The Shrinking Function; What is output?; The Calculator With No Brackets; The Stage Light Board; How far does the ball travel?; The Shuffled Shopping List; The Clubhouse Door; The Library Robot; Who ends up in locker 2?; The Knock Code
- **at least 14 exercises**, mixing programming items (judged line-exact) and short-answer items
- a heading ladder tag plus a visible division line on every exercise
- at least 2 `stretch` Challenges
- ACSL-style statements

### `unit-12-graph-theory` — Graph Theory

- **Divisions:** elementary, junior, intermediate, senior. **Introduces:** `acsl-graph-theory`.
- **Non-programming hook.**
- **Lesson 1 is the Elementary section**, with no code the student runs. It follows the Elementary doc: undirected graphs as vertex and edge sets, degree, simple paths of a given length from a vertex, cycles through a vertex (both directions), traversability by the odd-degree rule, and complete graphs' edge counts.
  - ≥ 6 contiguous `acsl-elementary` short-answer items open the exercises, and **Exercises 1–6 are the Elementary mock test**: paths, cycles, degree, traversability, a complete-graph count, and a second path or cycle item.
- **Junior and above:**
  - directed graphs; the adjacency matrix; counting paths of length 2 and 3 with matrix products
  - counting cycles in a directed graph; connected components; trees and N − 1 edges
  - Python: adjacency lists and matrices, degrees, and matrix multiplication
- **Intermediate and above:** weighted graphs and the cheapest path by listing (small graphs); spanning trees and DAGs; `M^p` for larger `p`.
- **Out:** named shortest-path algorithms and graph search algorithms (USACO's territory); every item is small enough to solve by listing or matrix products.

### `unit-13-digital-electronics` — Digital Electronics

- **Divisions:** junior, intermediate, senior. **Introduces:** `logic-gates`; practises `boolean-algebra`.
- **Scope:** the eight gates and their truth tables; reading a circuit (netlist and ASCII sketch) as a Boolean expression; circuit outputs for given inputs; the tuples that make a circuit TRUE or FALSE; counts; simplifying a circuit's expression to its unique minimal sum of products; NAND and NOR as universal gates.
- **Junior:** two and three inputs, up to about 4 gates. **Intermediate and above:** four inputs, deeper circuits, XNOR chains. **Senior:** building a given function from NAND gates only, answered as an **option choice** (which circuit is equivalent), checked by truth table.
- **Python:** a circuit simulator that reads a netlist from input and prints its truth table, or the count of TRUE rows.

### `unit-14-wdtpd-strings` — What Does This Program Do? – Strings

- **Divisions:** junior. **Introduces:** none; it practises `code-tracing` and `acsl-pseudocode`.
- **Constructs:**
  - `len`, `S[j]`, and the three ACSL substring forms (inclusive, and **not** Python slices)
  - `+` concatenation and `==`
  - loops over characters; building a new string; reversing; counting characters
  - palindromes, and characters compared as letters
- **Out:** arrays (Contest 3) and any function not on the wiki's list.
- At least half of the items are in pseudocode, since the substring rules are the trap, and every short-answer item has one-line output.

### `unit-15-assembly-language` — Assembly Language

- **Divisions:** intermediate, senior. **Introduces:** `acsl-assembly`.
- **Scope:** the wiki's instruction set and semantics exactly (above); tracing `ACC` and memory; loops made with branches; `READ` from given input; `PRINT`; what a program computes in general (the wiki's `N!` sample style, answered as an option choice or a value for a given input).
- **Short-answer items:** the value in a location, what is printed, or which option describes the program.
- **Python:** translating small assembly programs to Python; and (Senior, stretch) an interpreter for the instruction set that reads a program and its input.

### `checkpoint-04-contest-4-practice` — Practice (contest 4)

- **Divisions:** junior, intermediate, senior. **9 questions:**
  - Q1–Q2 Graph Theory, `acsl-junior` (one path or cycle count; one adjacency-matrix item)
  - Q3–Q4 Digital Electronics, `acsl-junior` (one tuple list; one count or simplification)
  - Q5–Q6 WDTPD – Strings, `acsl-junior`, at least one in pseudocode
  - Q7–Q8 Assembly Language, `acsl-intermediate`
  - Q9 the single `acsl-junior` programming problem, last, on Junior Contest 4 material, with the sample plus ≥ 4 hidden-style fixtures
- **Paths:**
  - Junior: Q1–Q6 + Q9
  - Intermediate and Senior: Q1–Q4, Q7–Q8 + Q9
  - Classroom (its Contest 4 categories are Graph Theory, Digital Electronics and Assembly Language): Q1–Q4 + Q7–Q8, with Q5–Q6 optional
  - Elementary: unit 12's Exercises 1–6, as 6 questions in 30 minutes
- The verify cells import the units' tested helpers.
- **Teacher notes:** Grading in ACSL's format, and a closing note on the whole season (the book's last practice).

## Phase A1 — Registry and tooling, before authoring

- **Inline:** `acsl/curriculum/concepts.yaml` gains the ACSL-only `acsl-graph-theory`, `logic-gates` and `acsl-assembly`.
- **Opus tooling subagent: pre-written evaluator tests**, pinning the interfaces above in their docstrings, from the wiki and Elementary doc samples:
  - `tests/test_acsl_eval_graph.py`:
    - the Elementary doc's simple paths from C (`CABD, CADB, CBAD, CBDA`)
    - its six cycles from A (`ABCA, ABDA, ACBA, ACBDA, ADBA, ADBCA`), its whole-graph count of 6 with `both_directions=True`, and 3 without it (a helper canonicalisation case, not an Elementary answer)
    - the doc's second graph, whose two cycles are `abcda` and `adcba` in both-direction counting
    - the wiki's matrix-power sample (1 path of length 2 from A to C; 3 of length 4), with its self-loop. The graph exists only in the wiki's image `graph sample3.svg`, so the A1 author fetches it and records the transcription in a comment
    - the wiki's directed cycle-count sample (`ABA`, `BCDB`, `CDC`: 3)
    - edge text with braces and commas parsing the same as bare pairs
    - `components(..., directed=True)` raising; `simple_paths` with `end` (and with `length=None`) filtering its results
    - traversability with 0, 2 and 4 odd vertices, and two disjoint triangles (0 odd vertices, not traversable); an isolated vertex given through `vertices` (degree 0, its own component, no effect on traversability)
    - directed cycles with and without `start`, including a 2-cycle `ABA`; `matrix` ignoring weights; `cheapest` on a small weighted graph
  - `tests/test_acsl_eval_circuit.py`:
    - the `INPUTS` line setting tuple columns and order, including an input no gate uses
    - the wiki's three samples (`(1,1,0)` the only FALSE triple; 10 TRUE rows; simplifies to `0`), transcribed from the wiki's diagrams into netlists
    - every gate's truth table
    - `to_expression` agreeing with `evaluate` on every row
  - `tests/test_acsl_eval_asm.py`:
    - the wiki's two samples (`TEMP` = −9 with the `ACC` trace −2, −6, 2, −1, −9; `N!` for several `N`)
    - each opcode, including immediate data, `DIV` toward zero for negatives, each branch, `READ`/`PRINT`, and the step limit
    - `READ` and `STORE` creating labels (the `N!` sample); line parsing of `DONE END` versus `LOAD B`; `DIV` operand order and `-7 DIV 2` → `-3`; `DIV` by zero raising
    - the book's modulo rule at the boundaries: `999999 + 1` → `0`, `-999999 - 2` → `-1`, `1000 MULT =1000` → `0`, `-1234 MULT =1000` → `-234000`, and a `READ` of `1000005` → `5`
- Each file imports its evaluator from the unit's `assets/verify/` and skips until it exists.

## Phase B — Lessons and statements (Opus subagents, one per entry, each owning only its folder)

The four unit authors work in parallel. **The checkpoint author starts after them**, reads units 12–15, and chooses items that repeat no unit item's edge set, netlist function or program.

Each unit folder gets `lesson.ipynb`, `exercises.ipynb` (statements with placeholders only), `manifest.yaml`, and `assets/` (lesson mirrors, reference solvers, and fixtures `exN/k.in|out`). The checkpoint gets `checkpoint.ipynb`, `manifest.yaml` and `assets/q9/`. Each author reports its intended answers for a blind cross-check without writing them into any file.

## Phase C — Solutions (Opus subagents, separate fresh sessions, one per entry)

- Solved from the statements only; mirrors byte-identical to `assets/exN.py`.
- The unit 12, 13 and 15 sessions write their `assets/verify/*_eval.py`, which must pass the pre-written test file. They do not edit that file.
- Verify cells call the tested helpers.

## Phase A2 — Coverage and syllabus, after authoring (inline)

Coverage-map entries in season order (units 12–15, then the checkpoint), reconciled against the manifests. Syllabus rows replace the "planned" rows.

## Phase D — Teacher notes (inline)

Five `teacher-notes.md` files with the required headings, and Grading for the checkpoint. They cover division paths (unit 14 as string drill for Intermediate/Senior; the Elementary mock test), the canonical forms, and the traps: substrings versus slices, `DIV` toward zero, walks (`M^p`) versus the Elementary doc's simple paths, and cycles in each direction (Elementary) versus once (the wiki). Unit 12's notes state the Elementary/wiki counting conflict plainly. Unit 15's notes state that the modulo reading for negatives is a book convention.

## Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN, in a solo run on the final commit.
2. The three pre-written evaluator test files pass with no skips.
3. A script reports the checkpoint paths by question tags (Junior Q1–Q6 + Q9; Intermediate/Senior Q1–Q4, Q7–Q8 + Q9; Classroom Q1–Q4, Q7–Q8). It also checks that unit 12's Exercises 1–6 are `acsl-elementary` short-answer items, contiguous before any other tag.
4. De-duplication scripts:
   - hook titles are unique across `acsl/units`
   - no checkpoint item has a unit 12–15 item's edge set, netlist truth column or program text
   - the checkpoint's verify cells import `graph_eval`, `circuit_eval` and `asm_eval` and define no evaluator of their own
5. Blind solves: reviewers solve all 8 checkpoint short answers and at least 3 items per unit.
6. Post-execution report.

## Out of scope

- The USACO trim (097). The user asked to be consulted before it.
- ACSL publication (PDF build for contest books).

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- **N1 (folded; superseded by the round-1 fold):** the assembly modulo rule for negative results was stated from memory. It is now a pinned book convention that no item assesses.
- The plan carries every plan 095 lesson forward: helpers pinned by pre-written tests, checkpoints importing them, a placeholder-only `exercises.ipynb`, unique hook titles, no checkpoint repeats, and stated counting rules for paths and cycles.

### Round 1 — verdicts and fold

- `[sol]` **REJECT**, 4 findings, all folded:
  1. Traversability also requires every vertex with an edge to be connected; tested with two disjoint triangles.
  2. `graph_eval` takes an optional `vertices` string (isolated vertices), `matrix` is 0/1 whatever the weights, and directed cycles run only in their edge direction; tested.
  3. Netlists begin with `INPUTS …`, which fixes tuple columns and order (unused inputs included); `values` is a dict; tested.
  4. The modulo rule (with `READ`) is pinned as a book convention, with boundary tests, and no item assesses it.
- `[fable]` **REJECT**, 3 blockers and 7 nits, all folded:
  1. Cycle counting follows each source: Elementary counts each undirected cycle in both directions (`both_directions=True`; the doc's 6), and Junior+ counts once (the wiki). Elementary items never say "counted once", and the teacher notes state the conflict.
  2. = `[sol]` 4. No item assesses overflow, and items never divide by zero.
  3. `READ` creates labels, line parsing is pinned (a first token is a label only when it is not an opcode), and `DIV` is ACC ÷ LOC, rounding toward zero; tested.
  4. NAND-only construction is option choice only.
  5. The 12 taken hook titles are listed; the checkpoint author starts after the units; Phase E adds de-duplication and helper-import scripts.
  6. Edge text is pasted verbatim (braces and commas are layout).
  7. Self-loops are allowed in matrices but kept out of cycle items; the wiki's image-only matrix sample is to be transcribed by the A1 author.
  8. Gate names are lowercase.
  9. Units 13 and 14 list their Python `requires`.
  10. The Elementary "paths of length 2" count (simple paths, 12) versus `M^2` walks is named in the canonical rules and in Phase D.

### Round 2 — verdicts and fold

- `[fable]` **APPROVE WITH NITS**. It verified every fold against the sources. Its nits are folded: self-loops are allowed in matrices; `matrix_power` is exempt from the edge-text arguments; the `[self]` N1 note is marked superseded; `components` is undirected only; the `MULT` overflow tests have expected values; `simple_paths` takes an optional `length` and `end`.
- `[sol]` **REJECT**, 1 blocker and 1 nit, both folded:
  1. `components` is undirected only (it raises for directed graphs), and component items use undirected graphs.
  2. = `[fable]` nit 2.

### Round 3 — CONSENSUS

- `[sol]` **APPROVE WITH NITS** (r3). Its nit is folded: tests pin that `components` raises for directed graphs, and that `simple_paths` filters by `end`.
- `[fable]` APPROVE WITH NITS (r2; nits folded).
- `[self]` APPROVE WITH NITS (r1; folded, and N1 superseded).
- `[glm]` skipped (user decision 2026-09-28).

## Content Review

## Post-Execution Report
_(filled before merge.)_
