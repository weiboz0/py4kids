"""The evaluation scoreboard: top-k retrieval metrics over a held-out relevant set.

These are the U1 metrics (design 011 §8). Deeper metrics (NDCG, calibration, coverage/diversity)
arrive with Unit 6. Every metric takes a ranked id list and a set of relevant ids and is a pure,
deterministic function.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from bookrec.protocol import Candidate


def _ranked_ids(recommendations: Sequence[Candidate] | Sequence[int]) -> list[int]:
    ids: list[int] = []
    for item in recommendations:
        ids.append(item.item_id if isinstance(item, Candidate) else int(item))
    return ids


def hit_rate_at_k(
    recommendations: Sequence[Candidate] | Sequence[int],
    relevant: Iterable[int],
    k: int,
) -> float:
    """Return ``1.0`` if any of the top-``k`` recommendations is relevant, else ``0.0``.

    This is per-query hit-rate (a.k.a. hit@k); average it over queries for the scoreboard number.
    """
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        raise ValueError(f"k must be a positive int, got {k!r}")
    relevant_set = set(relevant)
    top = _ranked_ids(recommendations)[:k]
    return 1.0 if any(item_id in relevant_set for item_id in top) else 0.0


def recall_at_k(
    recommendations: Sequence[Candidate] | Sequence[int],
    relevant: Iterable[int],
    k: int,
) -> float:
    """Fraction of the relevant items that appear in the top ``k`` (``0.0`` if none relevant)."""
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        raise ValueError(f"k must be a positive int, got {k!r}")
    relevant_set = set(relevant)
    if not relevant_set:
        return 0.0
    top = set(_ranked_ids(recommendations)[:k])
    return len(top & relevant_set) / len(relevant_set)


def mean_hit_rate_at_k(
    per_query: Iterable[tuple[Sequence[Candidate] | Sequence[int], Iterable[int]]],
    k: int,
) -> float:
    """Average :func:`hit_rate_at_k` over ``(recommendations, relevant)`` pairs (0.0 if empty)."""
    rows = list(per_query)
    if not rows:
        return 0.0
    return sum(hit_rate_at_k(recs, rel, k) for recs, rel in rows) / len(rows)
