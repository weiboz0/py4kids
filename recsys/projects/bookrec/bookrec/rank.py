"""Order a merged candidate pool into the final recommendations.

The foundation ranker is score-order with a deterministic id tie-break and an optional
``exclude`` set (items the reader has already seen). A learned reranker replaces the ordering
key in a later unit without changing this signature.
"""

from __future__ import annotations

from collections.abc import Iterable

from bookrec.protocol import Candidate, order_candidates


def rank(
    candidates: Iterable[Candidate],
    n: int | None = None,
    exclude: Iterable[int] | None = None,
) -> list[Candidate]:
    """Return the top ``n`` candidates (all, if ``n`` is None) after dropping ``exclude`` ids.

    Ordering is score descending, ties broken by ascending item id (deterministic).
    """
    blocked = set(exclude or ())
    kept = [c for c in candidates if c.item_id not in blocked]
    ordered = order_candidates(kept)
    if n is None:
        return ordered
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        raise ValueError(f"n must be a non-negative int or None, got {n!r}")
    return ordered[:n]
