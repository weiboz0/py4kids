"""Verification helper for unit 12: ACSL graph theory.

Used only by ``verify`` cells in ``solutions.ipynb`` (and ``tests/test_acsl_eval_graph.py``).

A graph is read from its edge text pasted verbatim: braces, commas and whitespace are layout,
and each remaining item is two vertex letters followed by an optional weight (``AB``, ``AB3``).
Every function that reads edge text takes ``vertices=None, directed=False``; vertices are always
taken in alphabetical order.

- ``matrix`` / ``matrix_power`` / ``count_paths``: adjacency matrix (1 per edge, weights ignored),
  its powers, and walks of a given length (entries of ``M^p``).
- ``simple_paths``: simple paths from a vertex, optionally filtered by length and end.
- ``cycles``: through ``start`` (undirected: both directions), or each cycle once from its
  smallest vertex, or (``both_directions=True``) in both directions as the Elementary doc counts.
- ``degrees``, ``components`` (undirected only), ``traversable`` (Euler's rule), ``cheapest``
  (least weight over all simple paths, by listing).

Canonical text: a path or cycle is its vertex letters run together; lists are sorted.
"""

from __future__ import annotations

import re

_ITEM = re.compile(r"^([A-Za-z])([A-Za-z])(\d*)$")


def _parse(edges: str) -> list[tuple[str, str, int | None]]:
    items = edges.replace("{", " ").replace("}", " ").replace(",", " ").split()
    parsed = []
    for item in items:
        match = _ITEM.match(item)
        if not match:
            raise ValueError(f"bad edge {item!r}")
        weight = int(match.group(3)) if match.group(3) else None
        parsed.append((match.group(1), match.group(2), weight))
    return parsed


def _graph(edges: str, vertices, directed: bool):
    """Return (sorted vertex list, adjacency dict vertex -> {neighbour: weight})."""
    parsed = _parse(edges)
    names = set(vertices or "")
    for a, b, _ in parsed:
        names.add(a)
        names.add(b)
    order = sorted(names)
    adj: dict[str, dict[str, int | None]] = {v: {} for v in order}
    for a, b, w in parsed:
        adj[a][b] = w
        if not directed:
            adj[b][a] = w
    return order, adj


def matrix(edges, vertices=None, directed=False) -> list[list[int]]:
    order, adj = _graph(edges, vertices, directed)
    return [[1 if b in adj[a] else 0 for b in order] for a in order]


def _multiply(x: list[list[int]], y: list[list[int]]) -> list[list[int]]:
    n = len(x)
    return [[sum(x[i][k] * y[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def matrix_power(M: list[list[int]], p: int) -> list[list[int]]:
    if p < 1:
        raise ValueError("p must be at least 1")
    result = [row[:] for row in M]
    for _ in range(p - 1):
        result = _multiply(result, M)
    return result


def count_paths(edges, start, end, length, vertices=None, directed=False) -> int:
    order = sorted(set(vertices or "") | {c for a, b, _ in _parse(edges) for c in (a, b)})
    power = matrix_power(matrix(edges, vertices, directed), length)
    return power[order.index(start)][order.index(end)]


def _all_simple(adj, start):
    """Every simple path (as a vertex list) from ``start`` with at least one edge."""
    found = []

    def walk(path):
        for nxt in sorted(adj[path[-1]]):
            if nxt not in path:
                path.append(nxt)
                found.append(list(path))
                walk(path)
                path.pop()

    walk([start])
    return found


def simple_paths(edges, start, length=None, end=None, vertices=None, directed=False) -> list[str]:
    _, adj = _graph(edges, vertices, directed)
    result = []
    for path in _all_simple(adj, start):
        if length is not None and len(path) - 1 != length:
            continue
        if end is not None and path[-1] != end:
            continue
        result.append("".join(path))
    return sorted(result)


def _cycles_from(adj, start, directed, allowed=None):
    """Cycles through ``start`` written from it, in every direction the edges allow."""
    smallest = 2 if directed else 3
    found = []
    for path in _all_simple(adj, start):
        if allowed is not None and any(v not in allowed for v in path):
            continue
        if len(path) >= smallest and start in adj[path[-1]]:
            found.append("".join(path) + start)
    return found


def cycles(edges, start=None, both_directions=False, vertices=None, directed=False) -> list[str]:
    order, adj = _graph(edges, vertices, directed)
    if start is not None:
        return sorted(_cycles_from(adj, start, directed))
    result = []
    for i, v in enumerate(order):
        for cycle in _cycles_from(adj, v, directed, allowed=set(order[i:])):
            if directed or both_directions or cycle[1] < cycle[-2]:
                result.append(cycle)
    return sorted(result)


def degrees(edges, vertices=None, directed=False) -> dict[str, int]:
    order, _ = _graph(edges, vertices, directed)
    count = {v: 0 for v in order}
    for a, b, _ in _parse(edges):
        count[a] += 1
        count[b] += 1
    return count


def _components(order, adj) -> list[set[str]]:
    seen: set[str] = set()
    pieces = []
    for v in order:
        if v in seen:
            continue
        piece = {v}
        stack = [v]
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if w not in piece:
                    piece.add(w)
                    stack.append(w)
        seen |= piece
        pieces.append(piece)
    return pieces


def components(edges, vertices=None, directed=False) -> int:
    if directed:
        raise ValueError("components is for undirected graphs only")
    order, adj = _graph(edges, vertices, directed)
    return len(_components(order, adj))


def traversable(edges, vertices=None, directed=False) -> bool:
    if directed:
        raise ValueError("traversable is for undirected graphs only")
    order, adj = _graph(edges, vertices, directed)
    pieces = [p for p in _components(order, adj) if any(adj[v] for v in p)]
    odd = sum(1 for d in degrees(edges, vertices).values() if d % 2)
    return len(pieces) <= 1 and odd in (0, 2)


def cheapest(edges, start, end, vertices=None, directed=False) -> int:
    _, adj = _graph(edges, vertices, directed)
    best = None
    for path in _all_simple(adj, start):
        if path[-1] != end:
            continue
        total = sum(adj[a][b] for a, b in zip(path, path[1:]))
        if best is None or total < best:
            best = total
    if best is None:
        raise ValueError(f"no path from {start} to {end}")
    return best
