"""The evaluation scoreboard: top-k retrieval metrics over a held-out relevant set.

These are the U1 metrics (design 011 §8) plus the Unit-6 rank-position-aware metrics
(:func:`precision_at_k`, :func:`ndcg_at_k`). Every metric takes a ranked id list and a set of
relevant ids and is a pure, deterministic function. (Beyond-accuracy metrics — coverage, diversity,
novelty — live in :mod:`bookrec.diversity`.)
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence

from bookrec.protocol import Candidate


def _ranked_ids(recommendations: Sequence[Candidate] | Sequence[int]) -> list[int]:
    """Item ids in ranked order, **de-duplicated** (first occurrence kept).

    A well-formed recommendation list never repeats an item (``blend``/``rank`` de-duplicate by id),
    so on real recommendations this is a no-op. The de-dup guards the metrics against a *malformed*
    input: without it a repeated relevant id earns relevance credit twice, pushing precision@k and
    NDCG@k above their documented ``[0, 1]`` range (e.g. ``ndcg_at_k([1, 1], {1}, 2)`` → 1.63).
    """
    seen: set[int] = set()
    ids: list[int] = []
    for item in recommendations:
        item_id = item.item_id if isinstance(item, Candidate) else int(item)
        if item_id not in seen:
            seen.add(item_id)
            ids.append(item_id)
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


def precision_at_k(
    recommendations: Sequence[Candidate] | Sequence[int],
    relevant: Iterable[int],
    k: int,
) -> float:
    """Fraction of the top-``k`` slots that are relevant: ``|top_k ∩ relevant| / k``.

    Unlike :func:`hit_rate_at_k` (which saturates at the first relevant hit), precision rewards
    packing *more* of the top ``k`` with relevant items. The denominator is always ``k`` (the
    standard precision@k convention), so a short recommendation list — e.g. after ``exclude`` drops
    seen items — is still scored against the full ``k`` budget. Defined as ``0.0`` when ``relevant``
    is empty (no relevant items ⇒ no precision to earn). Pure and deterministic.
    """
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        raise ValueError(f"k must be a positive int, got {k!r}")
    relevant_set = set(relevant)
    if not relevant_set:
        return 0.0
    top = _ranked_ids(recommendations)[:k]
    hits = sum(1 for item_id in top if item_id in relevant_set)
    return hits / k


def ndcg_at_k(
    recommendations: Sequence[Candidate] | Sequence[int],
    relevant: Iterable[int],
    k: int,
) -> float:
    """Normalized discounted cumulative gain at ``k`` with **binary** gain (relevant = 1, else 0).

    A relevant item at 1-based rank ``r`` in the top ``k`` contributes ``1 / log2(r + 1)``, so
    putting the right book *higher* scores more (rank 1 → ``1.0``, rank 2 → ``1/log2 3 ≈ 0.631``,
    …). The DCG is normalized by the ideal DCG (IDCG) — the DCG of the best possible ordering, which
    front-loads ``min(|relevant|, k)`` relevant items — so the result lands in ``[0, 1]``. Defined
    as ``0.0`` when ``relevant`` is empty (IDCG would be 0). Pure and deterministic.
    """
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        raise ValueError(f"k must be a positive int, got {k!r}")
    relevant_set = set(relevant)
    if not relevant_set:
        return 0.0
    top = _ranked_ids(recommendations)[:k]
    dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank, item_id in enumerate(top, start=1)
        if item_id in relevant_set
    )
    ideal_hits = min(len(relevant_set), k)
    idcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
    return dcg / idcg if idcg > 0 else 0.0


def mean_hit_rate_at_k(
    per_query: Iterable[tuple[Sequence[Candidate] | Sequence[int], Iterable[int]]],
    k: int,
) -> float:
    """Average :func:`hit_rate_at_k` over ``(recommendations, relevant)`` pairs (0.0 if empty)."""
    rows = list(per_query)
    if not rows:
        return 0.0
    return sum(hit_rate_at_k(recs, rel, k) for recs, rel in rows) / len(rows)
