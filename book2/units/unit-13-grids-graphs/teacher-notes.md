# Teacher Notes — Unit 13: Grids, Graphs & Traversal

## Goals

By the end of this unit students can:

- Walk a **2D grid** by its four neighbours (up/down/left/right) with correct bounds checks
  (`0 <= r and r < rows`).
- Represent an explicit **graph as an adjacency-list dict** `{node: [neighbours]}` (NO class), add an
  undirected edge to BOTH endpoints, and read a node's degree as `len(adj[node])`.
- **Flood-fill** a connected region, marking a `visited` set, and count / size regions.
- Run **BFS** for fewest-steps shortest paths — a `deque` used as a FIFO queue (`append` to enqueue,
  `popleft` to dequeue), a `visited` set, and a distance that grows one layer at a time.
- Run **DFS** for reachability — recursion with the `visited` set **passed as an argument** (never
  `nonlocal`).

A grid IS a graph (each cell a node, each step an edge); the same visited-guarded traversal answers
"connected?", "how many regions?", and "fewest steps?".

## Pacing

Three 60–90 minute lessons, with the CORE exercises assigned per lesson (stretches are optional homework):

**Lesson 1 — Grids & adjacency-list graphs.** Four-neighbour iteration + bounds; build an adjacency-list
dict (plain dict, `if u not in adj: adj[u] = []` then append; undirected edge on both endpoints); degree.
Class works **Exercise 1 (Friendship Degrees)**.

**Lesson 2 — Flood-fill & BFS.** Recursive flood-fill with a visited set; then BFS shortest-steps with a
`deque` FIFO queue (`while len(queue) > 0`), visited, and a per-cell distance. Stress the FIFO order — a LIFO
stack gives wrong distances. Class works **Exercises 2, 3, 4** (Paint One Room; Count the Islands; Fewest
Maze Steps).

**Lesson 3 — DFS reachability.** Recursive DFS with visited passed as an argument; connectivity / components.
Class works **Exercises 5, 6, 7** (Emergency Exit; Can the Message Travel?; Separate Networks). Assign the
stretch problems (8 Largest Meadow, 9 Farthest Delivery) as extension.

## Common mistakes

- **Forgetting `visited`** — a traversal without it loops forever (BFS) or hits `RecursionError` (DFS/
  flood-fill on a cycle). Mark a node visited when you first reach it.
- **BFS with a LIFO stack** — using `appendleft`+`popleft` (a stack) instead of `append`+`popleft` (a FIFO
  queue) returns wrong shortest-step counts. BFS needs FIFO.
- **Diagonal vs 4-neighbour** — these problems are 4-neighbour; adding diagonals merges regions that should
  be separate.
- **`arr[-1]` / off-grid** — check `0 <= r and r < rows` and `0 <= c and c < cols` BEFORE indexing the grid.
- **Mutating the grid while iterating it** — mark visited in a separate set (or carefully), don't corrupt the
  structure mid-walk.
- **Reaching for `.pop` / `nonlocal` / `defaultdict`** — all untaught here: removal is `.popleft`, DFS passes
  `visited` as an argument, and the adjacency dict is a plain dict with an `if u not in adj` pre-check.

## Discussion prompts

- Why does BFS (a FIFO queue) give the *fewest* steps while DFS does not? Trace both on a small grid.
- A grid and an adjacency-list graph look different but use the same traversal. What is the "node" and what is
  the "edge" in each?
- In flood-fill, why must you mark a cell visited the moment you enter it, not when you leave it?
- For "count the islands", why does each un-visited land cell start exactly one new region?

## Differentiation

- **More support:** give the four-neighbour offset list and the BFS-queue / recursive-DFS skeletons; pre-write
  the grid/graph parsing for Exercises 1–4.
- **More challenge:** the stretch problems (8 Largest Meadow — largest region; 9 Farthest Delivery — the
  maximum BFS distance) combine a traversal with a max; ask students to state the Big-O and the worst-case
  recursion depth.
- **Extension:** ask fast finishers to explain why BFS and DFS are both O(V+E), and when a recursive DFS would
  exceed Python's recursion limit (a long snake-like region).

### Concept → core-exercise coverage

- **graph-repr** → Ex 1 (Friendship Degrees), Ex 6 (Can the Message Travel?), Ex 7 (Separate Networks)
- **flood-fill** → Ex 2 (Paint One Room), Ex 3 (Count the Islands)
- **bfs** → Ex 4 (Fewest Maze Steps)
- **dfs** → Ex 5 (Emergency Exit), Ex 6 (Can the Message Travel?)

(Stretch: Ex 8 Largest Meadow — flood-fill; Ex 9 Farthest Delivery — BFS.)

### Big-O per exercise

1. Friendship Degrees — O(V + E) to build the adjacency list, O(1) per degree query.
2. Paint One Room — O(cells) (one flood-fill over the region).
3. Count the Islands — O(R·C) (each cell visited once across all fills).
4. Fewest Maze Steps — O(R·C) BFS (each cell enqueued once).
5. Emergency Exit — O(R·C) DFS/BFS reachability.
6. Can the Message Travel? — O(V + E) DFS reachability on the graph.
7. Separate Networks — O(V + E) (count components via repeated traversal).
8. Largest Meadow *(stretch)* — O(R·C) (flood-fill every region, track the max).
9. Farthest Delivery *(stretch)* — O(V + E) BFS from the source, take the max distance.
