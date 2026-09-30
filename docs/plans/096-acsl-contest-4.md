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
    - traversability: every edge used once without lifting the pencil, possible only when 0 or 2 vertices have odd degree
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
- `graph_eval.py` (unit 12). Its interface:
  - `parse(edges, directed=False)` reads an edge string like `"AB AC BC AD DB"` (space-separated pairs; a weighted edge is `AB3`).
    It returns `(vertices, adjacency)`, with vertices in alphabetical order.
  - `matrix(edges, directed=False) -> list[list[int]]`, rows and columns in alphabetical vertex order
  - `matrix_power(M, p) -> list[list[int]]`
  - `count_paths(edges, start, end, length, directed=False) -> int`: walks with repeats allowed, as `M^p` counts them
  - `simple_paths(edges, start, length, directed=False) -> list[str]`: every simple path of `length` edges from `start`, as vertex strings in alphabetical order
  - `cycles(edges, directed=False, start=None) -> list[str]`: with `start`, every cycle through `start` written from it, in each direction, in alphabetical order (the Elementary doc's form).
    Without `start`, each cycle once, written from its alphabetically smallest vertex, going the direction whose second vertex is smaller for an undirected graph.
  - `degrees(edges) -> dict`, `traversable(edges) -> bool`, `components(edges) -> int`
- `circuit_eval.py` (unit 13). A circuit is a **netlist**: one gate per line, `NAME = GATE(input, input)`, with `GATE` one of `BUFFER NOT AND NAND OR NOR XOR XNOR`; inputs are the circuit's variables `A`–`D` or earlier gate names; the last line's gate is the output.
  - `evaluate(netlist, values) -> int`
  - `solutions(netlist, value=1) -> str`: the canonical tuple list, as `bool_eval.solutions`
  - `count(netlist, value=1) -> int`
  - `to_expression(netlist) -> str`: the circuit as an expression in the book's Boolean notation, where `NAND(x, y)` is `~(x * y)`, and so on
  - Simplifying reuses unit 08's `bool_eval.minimal_sops`; verify cells import it from `../unit-08-boolean-algebra/assets/verify`.
- `asm_eval.py` (unit 15):
  - `run(program, inputs=()) -> dict` runs an ACSL assembly program, given as text with one instruction per line.
    It returns `{"memory": {label: value}, "printed": [values], "acc": [ACC after each ACC-changing instruction]}`.
  - The semantics are exactly the wiki's:
    - `ADD`, `SUB` and `MULT` results are reduced modulo 1,000,000 as the wiki states. The A1 test author reads the wiki's exact wording (and any worked example) and pins the rule for negative results in the test docstring; items avoid results beyond ±999,999 unless an item is about the rule itself.
    - `DIV` keeps the signed integer part, rounding toward zero. `DIV` is the one place ACSL rounds toward zero, not floor.
    - `READ` takes the next input.
    - Branches jump to a label; `END` stops.
    - A `STORE` to a label with no `DC` creates it.
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
- **Unit 13** introduces the ACSL-only `logic-gates` ("Logic gates and circuits", technique, techniques). It requires `boolean-algebra` (unit 08).
- **Unit 14** introduces nothing (`introduces: []`); it practises `code-tracing` and `acsl-pseudocode`.
- **Unit 15** introduces the ACSL-only `acsl-assembly` ("ACSL assembly language", technique, techniques). It requires `dict-*`, `str-split` and `input-parse`.
- **The checkpoint** is strict over *Python by Projects* plus units 00–15.

**Canonical answer text** (plans 093–095, plus these):
- **Paths and cycles:** vertex strings with no separators (`CADB`), listed in alphabetical order and separated by `, `; counts as bare integers. Each counting item states in words what counts (a walk that may repeat vertices, a simple path, a cycle counted once, or a cycle in each direction from a named vertex).
- **Matrices:** an item asks for one entry or a row sum as an integer, never a whole matrix.
- **Yes/no** (for example traversable): `YES` or `NO`.
- **Circuits:** tuples and counts as in unit 08; simplified expressions as unit 08's unique minimal sum of products, with `0` and `1` standing alone.
- **Assembly:** the value in a named location, or the printed values in order separated by single spaces.
- **Option lists:** capital letters as in plan 095.

## The entries (all under `acsl/`)

Unit conventions:
- a project-first hook with a title no other unit uses, and 3 lessons
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
- **Junior:** two and three inputs, up to about 4 gates. **Intermediate and above:** four inputs, deeper circuits, XNOR chains. **Senior:** building a given function from NAND gates only (answered as a count or an option choice).
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
    - its six cycles from A (`ABCA, ABDA, ACBA, ACBDA, ADBA, ADBCA`), and the same graph's cycles counted once each
    - the wiki's matrix-power sample (1 path of length 2 from A to C; 3 of length 4)
    - traversability with 0, 2 and 4 odd vertices; components; a directed cycle count; weighted parsing
  - `tests/test_acsl_eval_circuit.py`:
    - the wiki's three samples (`(1,1,0)` the only FALSE triple; 10 TRUE rows; simplifies to `0`), transcribed from the wiki's diagrams into netlists
    - every gate's truth table
    - `to_expression` agreeing with `evaluate` on every row
  - `tests/test_acsl_eval_asm.py`:
    - the wiki's two samples (`TEMP` = −9 with the `ACC` trace −2, −6, 2, −1, −9; `N!` for several `N`)
    - each opcode, including immediate data, `DIV` toward zero for negatives, the modulo rule on overflow, each branch, `READ`/`PRINT`, and the step limit
- Each file imports its evaluator from the unit's `assets/verify/` and skips until it exists.

## Phase B — Lessons and statements (Opus subagents in parallel, one per entry, each owning only its folder)

Each unit folder gets `lesson.ipynb`, `exercises.ipynb` (statements with placeholders only), `manifest.yaml`, and `assets/` (lesson mirrors, reference solvers, and fixtures `exN/k.in|out`). The checkpoint gets `checkpoint.ipynb`, `manifest.yaml` and `assets/q9/`. Each author reports its intended answers for a blind cross-check without writing them into any file.

## Phase C — Solutions (Opus subagents, separate fresh sessions, one per entry)

- Solved from the statements only; mirrors byte-identical to `assets/exN.py`.
- The unit 12, 13 and 15 sessions write their `assets/verify/*_eval.py`, which must pass the pre-written test file. They do not edit that file.
- Verify cells call the tested helpers.

## Phase A2 — Coverage and syllabus, after authoring (inline)

Coverage-map entries in season order (units 12–15, then the checkpoint), reconciled against the manifests. Syllabus rows replace the "planned" rows.

## Phase D — Teacher notes (inline)

Five `teacher-notes.md` files with the required headings, and Grading for the checkpoint. They cover division paths (unit 14 as string drill for Intermediate/Senior; the Elementary mock test), the canonical forms, and the traps: substrings versus slices, `DIV` toward zero, walks versus simple paths, and cycles counted once versus in each direction.

## Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN, in a solo run on the final commit.
2. The three pre-written evaluator test files pass with no skips.
3. A script reports the checkpoint paths by question tags (Junior Q1–Q6 + Q9; Intermediate/Senior Q1–Q4, Q7–Q8 + Q9; Classroom Q1–Q4, Q7–Q8). It also checks that unit 12's Exercises 1–6 are `acsl-elementary` short-answer items, contiguous before any other tag.
4. Blind solves: reviewers solve all 8 checkpoint short answers and at least 3 items per unit.
5. Post-execution report.

## Out of scope

- The USACO trim (097). The user asked to be consulted before it.
- ACSL publication (PDF build for contest books).

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- **N1 (folded):** the assembly modulo rule for negative results was stated from memory. A1 now pins it from the wiki's wording, and items stay inside ±999,999 unless the rule is the point.
- The plan carries every plan 095 lesson forward: helpers pinned by pre-written tests, checkpoints importing them, a placeholder-only `exercises.ipynb`, unique hook titles, no checkpoint repeats, and stated counting rules for paths and cycles.

## Content Review

## Post-Execution Report
_(filled before merge.)_
