# Teacher Notes — Unit 12: Graph Theory

## Goals

Students learn ACSL's first Contest 4 category, which every division takes.
By the end they can:

- read a graph from its vertex and edge sets (`{AB, AC, BC}`), find degrees, and check the handshake rule (the degrees add up to twice the number of edges);
- list simple paths of a given length, or between two vertices, and count them;
- find cycles, and count them by the rule the question states;
- decide whether a graph can be drawn in one stroke: it must be one connected piece with 0 or 2 odd vertices;
- count the edges of a complete graph;
- (Junior and above) read directed graphs and adjacency matrices, count walks of length p with `M^p`, count components, and use trees (N − 1 edges) and forests;
- (Intermediate and above) find the cheapest path in a small weighted graph by listing, count spanning trees, and recognise DAGs;
- in Python, build an adjacency matrix, multiply matrices with three nested loops, and list simple paths with recursion.

The hook is "The Park Keeper's Rounds", with no code: one park graph and three questions. Can the keeper rake every path once? How many jogging loops pass through A? How many 3-minute dog walks are there? Lesson 1 answers the first two, and Lesson 2 the third with `M^3`.

## Pacing

Budget: three lessons of 60–90 minutes, early in the Contest 4 window (Mar 1 – May 23, 2027).

- **Lesson 1, the Elementary section.** It contains no code for students to run.
  - Vertex and edge sets, degree and the handshake check.
  - Simple paths of a given length, paths between two vertices, and counting paths of length 2 (a path and its reverse count as two).
  - Cycles, counted in each direction as the Elementary doc does, and cycles through one vertex.
  - Complete graphs, then traversability, including the two-triangles trap and Königsberg.
  - Exercises 1–6 are the Elementary mock test (6 questions in 30 minutes); 7–9 are extra Elementary practice.
- **Lesson 2, Junior and above.**
  - Directed graphs; cycles counted **once**, with the difference from Lesson 1 stated plainly; 2-cycles; the wiki's sample.
  - The adjacency matrix, `M^2` and `M^3` as row-times-column products, and the park's dog walks.
  - Components, trees and forests.
  - The Intermediate section: the cheapest path by listing, spanning trees, DAGs, and `M^4` with a self-loop.
- **Lesson 3, Junior and above.**
  - Graphs in Python: positions of letters, a matrix as a list of lists, and degrees.
  - Multiplying matrices with three nested loops, and listing simple paths with recursion.
- **Exercises:** 26 items. Exercises 1–9 are Elementary; 10–18 are Junior (programs 17 and 18); 19–23 are Intermediate (program 23); and 24–26 are Senior (25–26 are Challenges; 26 is a program).

**60-minute cut:** keep paths, cycles, traversability and the adjacency matrix with `M^2`; set trees, forests and the Python lesson as reading plus Exercises 12 and 15.

## Common mistakes

- **Counting cycles by the wrong rule.** ACSL's two sources disagree:
  - The Elementary doc counts each undirected cycle in **both directions** (its sample graph has 6 cycles).
  - The Junior+ wiki counts each cycle **once** ("HEGH and EHGE are different ways to identify the same cycle").

  Every item in this book says which rule applies, so teach students to read that line first.
- **Mixing up walks and simple paths.** `M^p` counts walks, which may revisit vertices. The Elementary doc's "paths of length 2" are simple paths, and its sample graph has 12 of them against 22 walks.
- **Traversability.** Checking only the odd-vertex count and forgetting that the graph must be connected; two separate triangles cannot be drawn in one stroke.
- **Directed edges.** Reading `AB` both ways in a directed graph.
- **Matrix products.** Multiplying entry by entry instead of row times column.
- **Complete graphs.** Forgetting to halve the handshake count: `n(n − 1) / 2`.

## Discussion prompts

- Why must the degrees always add up to an even number?
- Why can't a graph with 4 odd vertices be drawn in one stroke?
- What does an entry of `M^2` count, and why does row-times-column count it?
- Where do graphs appear in real life (maps, networks, friendships)?

## Differentiation

- **Elementary:** Lesson 1 and Exercises 1–9 are the whole Contest 4 path; Exercises 1–6 are the mock test.
- **Junior:** Lessons 1–3 without the Intermediate section; Exercises 1–18.
- **Intermediate and Senior:** everything, including the Challenges.
- **Classroom:** Classroom's Contest 4 includes Graph Theory, so do the short-answer items at Junior and Intermediate level.
- **Support:** printed graph drawings for each edge set, and a blank matrix grid with labelled rows and columns.
- **Extension:** find a graph with 5 vertices where `M^2` has a 3 on its diagonal, and explain what that 3 counts.

## Answer forms

- Traversability items answer `YES` or `NO`, not the Elementary doc's "starting and ending vertices" form.
- Path and cycle lists are vertex strings in alphabetical order, separated by `, `.
