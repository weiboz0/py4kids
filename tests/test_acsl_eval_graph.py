"""Plan 096 A1: pre-written tests for unit 12's graph evaluator (``assets/verify/graph_eval.py``).

The evaluator's author implements this interface and does NOT edit this file.

**Edge text.** Every function that reads a graph takes ``edges`` plus the keyword arguments
``vertices=None, directed=False``.

* ``edges`` is the statement's edge text pasted verbatim. Braces ``{ }``, commas and whitespace
  (newlines included) are layout, so ``"{AB, AC, BC}"``, ``"AB AC BC"`` and ``"AB,AC,BC"`` are the
  same graph. Each remaining item is one edge: two vertex letters, then optionally the edge's
  weight as decimal digits (``AB3``, ``AB12``).
* A vertex is a single letter. A graph uses capitals (``A``-``Z``) or, as in the Elementary
  doc's second sample, lowercase letters (``a``-``e``); "alphabetical" is ordinary string order.
* Undirected (the default): ``AB`` joins A and B both ways. ``directed=True``: ``AB`` goes from
  A to B only.
* A self-loop ``AA`` is allowed and puts 1 on the diagonal of the matrix. Items never use
  self-loops in cycle or traversability questions, and never use repeated edges.
* ``vertices`` is an optional string of vertex letters (``"ABCDE"``) naming every vertex,
  isolated ones included, in any order. Without it the vertices are those appearing in
  ``edges``. Vertices are ALWAYS taken in alphabetical order.

``graph_eval.matrix(edges, vertices=None, directed=False) -> list[list[int]]``
    The adjacency matrix, rows and columns in alphabetical vertex order: entry ``[i][j]`` is 1
    when there is an edge from vertex ``i`` to vertex ``j`` and 0 otherwise, WHATEVER THE
    WEIGHT. An undirected edge sets both ``[i][j]`` and ``[j][i]``.

``graph_eval.matrix_power(M: list[list[int]], p: int) -> list[list[int]]``
    ``M`` multiplied by itself to the power ``p`` (``p >= 1``); ``M`` is not changed.

``graph_eval.count_paths(edges, start, end, length, vertices=None, directed=False) -> int``
    The number of walks from ``start`` to ``end`` of exactly ``length`` edges, vertices and
    edges may repeat: entry ``[start][end]`` of ``M^length``. This is the wiki's "number of
    paths of length p".

``graph_eval.simple_paths(edges, start, length=None, end=None, vertices=None, directed=False) -> list[str]``
    Every simple path (no vertex repeated) that starts at ``start`` and has at least one edge,
    as a string of its vertices (``"CADB"``), sorted alphabetically. With ``length`` only paths
    of exactly ``length`` edges; with ``end`` only paths ending at ``end``; both filters may be
    combined. A directed path follows edge directions.

``graph_eval.cycles(edges, start=None, both_directions=False, vertices=None, directed=False) -> list[str]``
    Cycles, each written as its vertices with the first repeated at the end (``"ABCA"``), the
    list sorted alphabetically. A cycle is simple apart from its equal first and last vertex. It
    has at least 3 distinct vertices in an undirected graph (``ABA`` is NOT a cycle there), and
    at least 2 in a directed graph (``ABA`` when both ``AB`` and ``BA`` exist).

    * **With** ``start``: every cycle through ``start``, written from ``start`` and back to it.
      Undirected: each cycle appears in BOTH directions (the Elementary doc's ``ABCA`` and
      ``ACBA``). Directed: only in the direction its edges allow.
    * **Without** ``start``: each cycle ONCE, written from its alphabetically smallest vertex;
      undirected, in the direction whose second vertex is the smaller one (``ABCA``, not
      ``ACBA``). This is the wiki's counting (Junior and above): "HEGH and EHGE are different
      ways to identify the same cycle". Directed: each directed cycle once, from its smallest
      vertex.
    * ``both_directions=True`` (undirected, without ``start``): each cycle from its smallest
      vertex in BOTH directions. This is the Elementary doc's counting (its sample graph has 6).

``graph_eval.degrees(edges, vertices=None, directed=False) -> dict[str, int]``
    Vertex -> degree, every vertex included (an isolated vertex has 0). Directed: in-degree plus
    out-degree.

``graph_eval.components(edges, vertices=None, directed=False) -> int``
    The number of connected components of an UNDIRECTED graph; an isolated vertex is a
    component of its own. ``directed=True`` raises ``ValueError``.

``graph_eval.traversable(edges, vertices=None, directed=False) -> bool``
    Undirected only. True exactly when every vertex THAT HAS AN EDGE lies in one connected
    component AND 0 or 2 vertices have odd degree (Euler's rule, as the book states it).
    Isolated vertices do not affect the answer.

``graph_eval.cheapest(edges, start, end, vertices=None, directed=False) -> int``
    The least total weight over all simple paths from ``start`` to ``end``, found by listing
    them (weighted graphs only; items always have such a path).

Sources:

* ACSL's Elementary Division "Graph Theory" doc (the Google doc linked from the ACSL
  Elementary page, retrieved 2026-09-29) — its first graph {A, B, C, D} / {AB, AC, BC, AD, DB}
  and its second graph {a, b, c, d, e} / {ab, ad, bc, cd, ae}.
* The ACSL wiki "Graph Theory" page (categories.acsl.org, retrieved 2026-09-29). Its matrix
  sample (Problem 2) exists only as images; the transcriptions are recorded next to the tests.
* Hand-computed values carry their working in comments.

All expected values were re-checked against an independent throwaway implementation (walks by
recursive enumeration rather than matrix products, cycles by DFS from every vertex).
Skips until the module exists.
"""

from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path

import pytest

VERIFY_DIR = Path(__file__).resolve().parents[1] / "acsl/units/unit-12-graph-theory/assets/verify"
sys.path.insert(0, str(VERIFY_DIR))
graph_eval = pytest.importorskip("graph_eval")


def _edge_count(edges: str, **kw) -> int:
    """Undirected edge count via the handshake rule (sum of degrees / 2)."""
    return sum(graph_eval.degrees(edges, **kw).values()) // 2


# ---------------------------------------------------------------- the Elementary doc, graph 1

# "the set of vertices {A, B, C, D} and the set of edges ... {AB, AC, BC, AD, DB}"
ELEM_1 = "{AB, AC, BC, AD, DB}"


def test_elementary_simple_paths_of_length_3_from_c():
    # "The paths are CADB, CABD, CBAD, and CBDA. You cannot go to vertex D first."
    assert graph_eval.simple_paths(ELEM_1, "C", length=3) == ["CABD", "CADB", "CBAD", "CBDA"]


def test_elementary_cycles_from_a_in_both_directions():
    # "ABDA, ADBA, ABCA, ACBA, ACBDA, and ADBCA are all cycles so there are 6 of them"
    six = ["ABCA", "ABDA", "ACBA", "ACBDA", "ADBA", "ADBCA"]
    assert graph_eval.cycles(ELEM_1, start="A") == six


def test_elementary_whole_graph_count_both_directions():
    # Sample problem: "Find the number of different cycles ... Thus, there are 6 cycles".
    # Every cycle of this graph passes through A, its smallest vertex, so the list is the same
    # six strings as from A.
    got = graph_eval.cycles(ELEM_1, both_directions=True)
    assert got == ["ABCA", "ABDA", "ACBA", "ACBDA", "ADBA", "ADBCA"]
    assert len(got) == 6


def test_elementary_graph_counted_once_is_3():
    # A helper canonicalisation case, NOT an Elementary answer: counted once there are 3 cycles
    # (triangles ABC and ABD, square A-C-B-D). Each goes from A toward its smaller neighbour:
    # ABCA (B < C), ABDA (B < D), ACBDA (C < D; the other way is ADBCA).
    assert graph_eval.cycles(ELEM_1) == ["ABCA", "ABDA", "ACBDA"]


def test_elementary_cycles_from_c():
    # Hand: C lies on triangle ABC and square ACBD. From C both ways:
    #   triangle: CABC, CBAC; square (C-A-D-B-C): CADBC, CBDAC.
    assert graph_eval.cycles(ELEM_1, start="C") == ["CABC", "CADBC", "CBAC", "CBDAC"]


def test_elementary_simple_path_examples_b_to_d():
    # Doc: "BD is a path of length 1 while BAD is a path of length 2 from vertex B to vertex D";
    # "BACBD is a path of length 4, but it is not a simple path".
    # Hand: every simple path B..D: BD, BAD, BCAD (B-C-A-D). BACBD repeats B, so is absent.
    got = graph_eval.simple_paths(ELEM_1, "B", end="D")
    assert got == ["BAD", "BCAD", "BD"]
    assert "BACBD" not in got


def test_simple_paths_end_filter():
    # Hand, from C ending at D: CAD, CBD (length 2); CABD, CBAD (length 3).
    assert graph_eval.simple_paths(ELEM_1, "C", end="D") == ["CABD", "CAD", "CBAD", "CBD"]


def test_simple_paths_length_and_end_combined():
    assert graph_eval.simple_paths(ELEM_1, "C", length=3, end="B") == ["CADB"]
    assert graph_eval.simple_paths(ELEM_1, "C", length=2, end="D") == ["CAD", "CBD"]


def test_simple_paths_without_length_lists_every_simple_path():
    # Hand, all simple paths from C with at least one edge:
    #   length 1: CA, CB; length 2: CAB, CAD, CBA, CBD; length 3: CABD, CADB, CBAD, CBDA.
    expected = ["CA", "CAB", "CABD", "CAD", "CADB", "CB", "CBA", "CBAD", "CBD", "CBDA"]
    assert graph_eval.simple_paths(ELEM_1, "C") == expected
    assert graph_eval.simple_paths(ELEM_1, "C", length=None, end=None) == expected


def test_elementary_graph_degrees_and_traversable():
    # A: AB AC AD = 3; B: AB BC DB = 3; C: 2; D: 2. Two odd vertices, connected -> traversable.
    assert graph_eval.degrees(ELEM_1) == {"A": 3, "B": 3, "C": 2, "D": 2}
    assert graph_eval.traversable(ELEM_1) is True


def test_elementary_missing_edges_make_two_pieces():
    # "if edges BC and AC were missing, then there would be 2 unconnected graphs, one with just
    # vertex C and the other with vertices {A, B, D} with the remaining 3 edges."
    assert graph_eval.components("{AB, AD, DB}", vertices="ABCD") == 2
    assert graph_eval.degrees("{AB, AD, DB}", vertices="ABCD")["C"] == 0


# ---------------------------------------------------------------- the Elementary doc, graph 2

# "The set of vertices is {a,b,c,d,e} and the set of edges is {ab,ad,bc,cd,ae}."
ELEM_2 = "{ab,ad,bc,cd,ae}"


def test_elementary_second_graph_cycles():
    # "The only cycles are 'abcda' and 'adcba'." (both-direction counting)
    assert graph_eval.cycles(ELEM_2, both_directions=True) == ["abcda", "adcba"]
    # Counted once (wiki style): from a toward the smaller neighbour b.
    assert graph_eval.cycles(ELEM_2) == ["abcda"]
    # From a, both directions, as the doc's first sample lists cycles from A.
    assert graph_eval.cycles(ELEM_2, start="a") == ["abcda", "adcba"]
    assert graph_eval.cycles(ELEM_2, start="e") == []


def test_elementary_second_graph_simple_paths_b_to_d():
    # "All of the simple paths from vertex 'b' to vertex 'd' are 'bad' and 'bcd'."
    assert graph_eval.simple_paths(ELEM_2, "b", end="d") == ["bad", "bcd"]


def test_elementary_second_graph_twelve_paths_of_length_2():
    # "There are 12 paths of length 2 including 'abc', 'adc', 'bae', 'bad', 'bcd', 'cba',
    # 'cda', 'dae', 'dcb', 'dab', 'eab', and 'ead'." These are SIMPLE paths, from every start.
    doc = ["abc", "adc", "bae", "bad", "bcd", "cba", "cda", "dae", "dcb", "dab", "eab", "ead"]
    got = [p for v in "abcde" for p in graph_eval.simple_paths(ELEM_2, v, length=2)]
    assert sorted(got) == sorted(doc)
    assert len(got) == 12


def test_elementary_second_graph_walks_of_length_2_are_22():
    # The same graph counted as WALKS (M^2) gives 22, not 12: the sum of M^2's entries is the
    # sum of the squared degrees, 3^2 + 2^2 + 2^2 + 2^2 + 1^2 = 22 (a:3 b:2 c:2 d:2 e:1).
    m2 = graph_eval.matrix_power(graph_eval.matrix(ELEM_2), 2)
    assert sum(map(sum, m2)) == 22
    walks = sum(graph_eval.count_paths(ELEM_2, s, e, 2) for s in "abcde" for e in "abcde")
    assert walks == 22


def test_elementary_second_graph_traversable():
    # "This graph is traversable starting with vertex 'a' and ending with vertex 'e' or starting
    # with 'e' and ending with 'a'." a and e are the two odd vertices.
    assert graph_eval.traversable(ELEM_2) is True
    degs = graph_eval.degrees(ELEM_2)
    assert degs == {"a": 3, "b": 2, "c": 2, "d": 2, "e": 1}
    assert sorted(v for v, d in degs.items() if d % 2) == ["a", "e"]


# ---------------------------------------------------------------- complete graphs


def _complete(letters: str) -> str:
    return " ".join(a + b for a, b in combinations(letters, 2))


@pytest.mark.parametrize(
    "letters, edges",
    [
        ("ABCDE", 10),  # doc: pentagon, 5 vertices + 5 diagonals = 10 edges
        ("ABCDEF", 15),  # doc: hexagon, 6 sides + 9 diagonals = 15 edges
        ("ABCDEFGHIJ", 45),  # doc: decagon, 10 vertices + 35 diagonals = 45 edges
    ],
)
def test_complete_graph_edge_counts(letters, edges):
    k = _complete(letters)
    assert _edge_count(k) == edges
    assert graph_eval.matrix(k) == [
        [0 if i == j else 1 for j in range(len(letters))] for i in range(len(letters))
    ]


def test_complete_graphs_traversability():
    # K5: every degree 4 (0 odd) -> YES. K4: every degree 3 (4 odd) -> NO.
    assert graph_eval.traversable(_complete("ABCDE")) is True
    assert graph_eval.traversable(_complete("ABCD")) is False


# ---------------------------------------------------------------- traversability


@pytest.mark.parametrize(
    "edges, vertices, expected",
    [
        ("AB BC CD DA", None, True),  # square: 0 odd
        ("AB BC CD", None, True),  # path: 2 odd (A, D)
        ("AB AC AD AE", None, False),  # star: B C D E odd -> 4 odd
        ("AB BC CA DE EF FD", None, False),  # two disjoint triangles: 0 odd, but 2 pieces
        ("AB BC CA", "ABCD", True),  # isolated D has no edge: no effect
        ("AB BC CD", "ABCDE", True),  # isolated E: still 2 odd, one piece with edges
    ],
)
def test_traversable_rules(edges, vertices, expected):
    assert graph_eval.traversable(edges, vertices=vertices) is expected


def test_isolated_vertex_through_vertices():
    tri = "{AB, BC, CA}"
    assert graph_eval.degrees(tri, vertices="ABCD") == {"A": 2, "B": 2, "C": 2, "D": 0}
    assert graph_eval.components(tri, vertices="ABCD") == 2  # D is its own component
    assert graph_eval.components(tri) == 1
    assert graph_eval.matrix(tri, vertices="ABCD") == [
        [0, 1, 1, 0],
        [1, 0, 1, 0],
        [1, 1, 0, 0],
        [0, 0, 0, 0],
    ]


# ---------------------------------------------------------------- the wiki's undirected example

# Overview: "its set of edges between these vertices {AB, AD, BD, CF, FG, GH, GE, HE}".
# (Source slip: the wiki's vertex set {A, B, C, D, E, F, G} omits H, which its edges use; the
# test lets the edges name the vertices.)
WIKI_UNDIRECTED = "{AB, AD, BD, CF, FG, GH, GE, HE}"


def test_wiki_components():
    # "the graph above has two connected components: {A, B, D} and {C, E, F, G, H}"
    assert graph_eval.components(WIKI_UNDIRECTED) == 2


def test_wiki_cycles_counted_once():
    # "the path HEGH is a cycle ... HEGH and EHGE are different ways to identify the same
    # cycle". Hand: two triangles, ABD and EGH. Once each, from the smallest vertex toward the
    # smaller neighbour: ABDA, EGHE.
    assert graph_eval.cycles(WIKI_UNDIRECTED) == ["ABDA", "EGHE"]
    assert graph_eval.cycles(WIKI_UNDIRECTED, start="H") == ["HEGH", "HGEH"]


def test_wiki_simple_path_example():
    # "FGHE is path from F to E ... FGHEG is not a simple path."
    got = graph_eval.simple_paths(WIKI_UNDIRECTED, "F", end="E")
    assert "FGHE" in got
    assert got == ["FGE", "FGHE"]  # hand: F-G-E and F-G-H-E


def test_undirected_two_vertices_is_not_a_cycle():
    assert graph_eval.cycles("AB") == []
    assert graph_eval.cycles("AB", start="A") == []


# ---------------------------------------------------------------- the wiki's directed examples

# "the set of edges {AB,AD,DA,DB,EG,GE,HG,HE,GF,CF,FC}"
WIKI_DIRECTED = "{AB,AD,DA,DB,EG,GE,HG,HE,GF,CF,FC}"


def test_wiki_directed_path_one_way_only():
    # "There is one directed path from G to C (namely, GFC); however, there are no directed
    # paths from C to G."
    assert graph_eval.simple_paths(WIKI_DIRECTED, "G", end="C", directed=True) == ["GFC"]
    assert graph_eval.simple_paths(WIKI_DIRECTED, "C", end="G", directed=True) == []
    assert graph_eval.count_paths(WIKI_DIRECTED, "G", "C", 2, directed=True) == 1


def test_wiki_directed_example_cycles():
    # Hand: the only directed cycles are the three two-way pairs A<->D, C<->F, E<->G.
    assert graph_eval.cycles(WIKI_DIRECTED, directed=True) == ["ADA", "CFC", "EGE"]


# Problem 1: "the directed graph with vertices {A, B, C, D, E} and edges
# {AB, BA, BC, CD, DC, DB, DE}" -- "the cycles are: ABA, BCDB, and CDC ... there are 3".
WIKI_P1 = "{AB, BA, BC, CD, DC, DB, DE}"


def test_wiki_problem_1_directed_cycle_count():
    got = graph_eval.cycles(WIKI_P1, vertices="ABCDE", directed=True)
    assert got == ["ABA", "BCDB", "CDC"]
    assert len(got) == 3


def test_wiki_problem_1_directed_cycles_with_start():
    # Only the directions the edges allow: from B, BAB and BCDB (B->C->D->B), never BDCB.
    assert graph_eval.cycles(WIKI_P1, start="B", directed=True) == ["BAB", "BCDB"]
    assert graph_eval.cycles(WIKI_P1, start="D", directed=True) == ["DBCD", "DCD"]
    assert graph_eval.cycles(WIKI_P1, start="E", directed=True) == []


def test_directed_two_cycle():
    assert graph_eval.cycles("AB BA", directed=True) == ["ABA"]
    assert graph_eval.cycles("AB BA", start="B", directed=True) == ["BAB"]


def test_directed_triangle_versus_undirected():
    tri = "AB BC CA"
    assert graph_eval.cycles(tri, directed=True) == ["ABCA"]
    assert graph_eval.cycles(tri, start="B", directed=True) == ["BCAB"]
    assert graph_eval.cycles(tri) == ["ABCA"]
    assert graph_eval.cycles(tri, both_directions=True) == ["ABCA", "ACBA"]
    assert graph_eval.cycles(tri, start="B") == ["BACB", "BCAB"]
    assert graph_eval.simple_paths(tri, "A", directed=True) == ["AB", "ABC"]


def test_wiki_problem_1_directed_degrees():
    # in + out. A: out AB, in BA = 2. B: out BA BC, in AB DB = 4. C: out CD, in BC DC = 3.
    # D: out DC DB DE, in CD = 4. E: in DE = 1. Sum 14 = 2 x 7 edges.
    assert graph_eval.degrees(WIKI_P1, directed=True) == {"A": 2, "B": 4, "C": 3, "D": 4, "E": 1}


def test_components_directed_raises():
    with pytest.raises(ValueError):
        graph_eval.components(WIKI_P1, directed=True)


# ---------------------------------------------------------------- adjacency matrices

# The wiki's "Adjacency Matrices" example (images DirectedGraph.png and AdjMatrix.png,
# AdjMatrix2.png). Transcribed drawing: arrows A->B, A->D, B->C, B->D (diagonal), C->B, D->C.
WIKI_ADJ = "AB AD BC BD CB DC"


def test_wiki_adjacency_matrix_example():
    # AdjMatrix.png, right-hand panel.
    m = graph_eval.matrix(WIKI_ADJ, directed=True)
    assert m == [[0, 1, 0, 1], [0, 0, 1, 1], [0, 1, 0, 0], [0, 0, 1, 0]]
    # AdjMatrix2.png: "2 paths of length 2 from A to C (A -> B -> C and A -> D -> C) ...
    # exactly 1 path of length 2 from A to D (A -> B -> D), exactly 1 ... from B to B".
    assert graph_eval.matrix_power(m, 2) == [[0, 0, 2, 1], [0, 1, 1, 0], [0, 0, 1, 1], [0, 1, 0, 0]]
    assert graph_eval.count_paths(WIKI_ADJ, "A", "C", 2, directed=True) == 2
    assert graph_eval.count_paths(WIKI_ADJ, "A", "D", 2, directed=True) == 1
    assert graph_eval.count_paths(WIKI_ADJ, "B", "B", 2, directed=True) == 1


# Problem 2 ("find the total number of different paths from vertex A to vertex C of length 2 or
# 4"). The graph exists only in the wiki's image "graph sample3.svg"; transcription (fetched
# 2026-09-29, rendered and read, and cross-checked against the SVG path data):
#   * vertices A (top left), B (top right), C (bottom)
#   * a self-loop on A with its arrowhead back into A  -> AA
#   * a self-loop on B likewise                         -> BB
#   * the A-C line has arrowheads at BOTH ends          -> AC and CA
#   * the B-C line has one arrowhead, at C              -> BC
# The solution image "matrix_s3.png" confirms it: M = [[1,0,1],[0,1,1],[1,0,0]],
# M^2 = [[2,0,1],[1,1,1],[1,0,1]], M^4 = [[5,0,3],[4,1,3],[3,0,2]].
WIKI_P2 = "AA AC CA BB BC"


def test_wiki_problem_2_matrix_powers():
    m = graph_eval.matrix(WIKI_P2, directed=True)
    assert m == [[1, 0, 1], [0, 1, 1], [1, 0, 0]]
    assert graph_eval.matrix_power(m, 2) == [[2, 0, 1], [1, 1, 1], [1, 0, 1]]
    assert graph_eval.matrix_power(m, 4) == [[5, 0, 3], [4, 1, 3], [3, 0, 2]]
    assert m == [[1, 0, 1], [0, 1, 1], [1, 0, 0]]  # M itself unchanged


def test_wiki_problem_2_path_counts():
    # "There is 1 path of length 2 from A to C ... A -> A -> C."
    assert graph_eval.count_paths(WIKI_P2, "A", "C", 2, directed=True) == 1
    # "There are 3 paths of length 4 ... A->A->A->A->C, A->A->C->A->C, A->C->A->A->C."
    assert graph_eval.count_paths(WIKI_P2, "A", "C", 4, directed=True) == 3


def test_self_loop_on_the_diagonal():
    assert graph_eval.matrix("AA AB", directed=True) == [[1, 1], [0, 0]]
    assert graph_eval.matrix("AA AB") == [[1, 1], [1, 0]]


def test_wiki_problem_3_matrix():
    # "E = {AB, AD, BA, BD, CA, DB, DC}"; the given matrix (image matrix_s4.png) is
    # [[0,1,0,1],[1,0,0,1],[1,0,0,0],[0,1,1,0]].
    got = graph_eval.matrix("{AB, AD, BA, BD, CA, DB, DC}", directed=True)
    assert got == [[0, 1, 0, 1], [1, 0, 0, 1], [1, 0, 0, 0], [0, 1, 1, 0]]


def test_matrix_power_one_is_m():
    m = graph_eval.matrix(ELEM_1)
    assert graph_eval.matrix_power(m, 1) == m


@pytest.mark.parametrize(
    "edges, directed",
    [(ELEM_1, False), (WIKI_P1, True), (WIKI_P2, True), (WIKI_ADJ, True), (ELEM_2, False)],
)
def test_count_paths_matches_matrix_powers(edges, directed):
    m = graph_eval.matrix(edges, directed=directed)
    names = sorted({ch for ch in edges if ch.isalpha()})
    for p in (1, 2, 3, 4):
        mp = graph_eval.matrix_power(m, p)
        for i, s in enumerate(names):
            for j, e in enumerate(names):
                assert graph_eval.count_paths(edges, s, e, p, directed=directed) == mp[i][j]


# ---------------------------------------------------------------- edge-text layout and order


@pytest.mark.parametrize(
    "text",
    ["{AB, AC, BC}", "AB AC BC", "AB,AC,BC", "{AB,AC,BC}", "  { AB ,\n AC,\tBC }  ", "BC AB AC"],
)
def test_edge_text_layout(text):
    assert graph_eval.matrix(text) == [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
    assert graph_eval.degrees(text) == {"A": 2, "B": 2, "C": 2}
    assert graph_eval.cycles(text) == ["ABCA"]


def test_undirected_edge_sets_both_entries_directed_one():
    assert graph_eval.matrix("AB") == [[0, 1], [1, 0]]
    assert graph_eval.matrix("AB", directed=True) == [[0, 1], [0, 0]]
    assert graph_eval.matrix("BA", directed=True) == [[0, 0], [1, 0]]


def test_vertices_always_alphabetical():
    expected = [[0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]]
    assert graph_eval.matrix("DB CA") == expected
    assert graph_eval.matrix("DB CA", vertices="DCBA") == expected
    assert graph_eval.matrix("DB CA", vertices="ABCD") == expected


# ---------------------------------------------------------------- weighted graphs

WEIGHTED = "{AB3, AC1, BC1, BD5, CD2}"


def test_matrix_ignores_weights():
    assert graph_eval.matrix(WEIGHTED) == graph_eval.matrix("{AB, AC, BC, BD, CD}")
    assert graph_eval.matrix(WEIGHTED) == [[0, 1, 1, 0], [1, 0, 1, 1], [1, 1, 0, 1], [0, 1, 1, 0]]


def test_cheapest_small_weighted_graph():
    # Hand, A to D: ACD 1+2 = 3; ABD 3+5 = 8; ABCD 3+1+2 = 6; ACBD 1+1+5 = 7 -> 3.
    assert graph_eval.cheapest(WEIGHTED, "A", "D") == 3
    # A to B: AB 3; ACB 1+1 = 2; ACDB 1+2+5 = 8 -> 2 (cheaper than the direct edge).
    assert graph_eval.cheapest(WEIGHTED, "A", "B") == 2
    # B to D: BD 5; BCD 1+2 = 3; BACD 3+1+2 = 6 -> 3.
    assert graph_eval.cheapest(WEIGHTED, "B", "D") == 3


def test_cheapest_multi_digit_weights():
    # AC 30 direct; ABC 10+15 = 25 -> 25.
    assert graph_eval.cheapest("AB10 BC15 AC30", "A", "C") == 25


def test_cheapest_directed():
    # A to C: AC 5; ABC 2+2 = 4 -> 4. C to B follows directions: CAB 1+2 = 3 (no CB edge).
    edges = "AB2 BC2 AC5 CA1"
    assert graph_eval.cheapest(edges, "A", "C", directed=True) == 4
    assert graph_eval.cheapest(edges, "C", "B", directed=True) == 3
    # Undirected, C to B has the direct edge BC 2.
    assert graph_eval.cheapest("AB2 BC2 AC5", "C", "B") == 2
