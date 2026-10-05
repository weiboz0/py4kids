"""Unit 2: beyond-accuracy popularity-bias metrics — catalog coverage and head-share.

Design 011 §6/§8. A popularity recommender concentrates exposure on a few head items and starves
the tail; these two metrics make that bias visible. Both take ``recommendations`` as an iterable
of per-reader top-k lists (each a sequence of :class:`~bookrec.protocol.Candidate` or of int item
ids) — the SAME scored-reader set the scoreboard used (cold readers already excluded). Small,
seed-free, numpy-free.

- **catalog coverage** — fraction of *unique* catalog items that appear in at least one reader's
  top-k.
- **head-share** — fraction of recommendation *slots* (summed over every scored reader's top-k)
  whose item is in the head set.
- the **head set** is the top ``fraction`` (default 10%) of *catalog* items by train positive
  count: ``ceil(fraction·N)`` items, ties broken by ascending item id (:func:`head_ids_from_counts`).

Unit 6 adds two per-list beyond-accuracy metrics over a *single* reader's top-k:

- **intra-list diversity** — ``1 − mean pairwise similarity`` of the recommended items (higher =
  the list spans more of item space, not near-duplicates).
- **novelty** — the mean self-information ``−log₂ p̂(item)`` of the recommended items, where
  ``p̂`` is an item's share of the train positives (rarer item ⇒ higher novelty).
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any

from bookrec.protocol import Candidate


def _item_id(item: Candidate | int) -> int:
    return item.item_id if isinstance(item, Candidate) else int(item)


def catalog_coverage(
    recommendations: Iterable[Sequence[Candidate | int]],
    catalog_ids: Iterable[int],
) -> float:
    """Fraction of unique catalog items appearing in at least one reader's top-k (``[0, 1]``)."""
    catalog = {int(item_id) for item_id in catalog_ids}
    if not catalog:
        return 0.0
    recommended: set[int] = set()
    for recs in recommendations:
        for item in recs:
            item_id = _item_id(item)
            if item_id in catalog:
                recommended.add(item_id)
    return len(recommended) / len(catalog)


def head_share(
    recommendations: Iterable[Sequence[Candidate | int]],
    head_ids: Iterable[int],
) -> float:
    """Fraction of recommendation slots (summed over readers) whose item is in ``head_ids``."""
    head = {int(item_id) for item_id in head_ids}
    slots = 0
    in_head = 0
    for recs in recommendations:
        for item in recs:
            slots += 1
            if _item_id(item) in head:
                in_head += 1
    return in_head / slots if slots else 0.0


def _pairwise_similarity(similarity: Any, a: int, b: int) -> float:
    """Look up the item–item similarity of ``a`` and ``b`` from a callable or a 2-D structure.

    ``similarity`` is either a callable ``similarity(a, b) -> float`` or anything indexable by item
    id — a nested mapping ``similarity[a][b]``, or a 2-D structure addressed by a tuple
    ``similarity[a, b]`` (e.g. a numpy matrix whose row/column indices *are* item ids). The two
    index forms are tried in turn so the common cases all work without the caller declaring which.
    """
    if callable(similarity):
        return float(similarity(a, b))
    try:
        return float(similarity[a][b])
    except (TypeError, KeyError, IndexError):
        return float(similarity[a, b])


def intra_list_diversity(
    recommendations: Sequence[Candidate | int],
    similarity: Callable[[int, int], float] | Any,
) -> float:
    """``1 − mean pairwise similarity`` over the recommended items (``0.0`` for fewer than 2 items).

    ``recommendations`` is one reader's top-k list (:class:`~bookrec.protocol.Candidate` objects or
    int item ids). ``similarity`` supplies the item–item similarity of every unordered pair — a
    callable ``similarity(a, b)`` or a 2-D lookup indexed by item id (see
    :func:`_pairwise_similarity`). With fewer than two items there are no pairs, so diversity is
    ``0.0`` by convention. Pure and deterministic.
    """
    ids = [item.item_id if isinstance(item, Candidate) else int(item) for item in recommendations]
    n = len(ids)
    if n < 2:
        return 0.0
    total = 0.0
    pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            total += _pairwise_similarity(similarity, ids[i], ids[j])
            pairs += 1
    return 1.0 - total / pairs


def novelty(
    recommendations: Sequence[Candidate | int],
    popularity: Mapping[int, float],
) -> float:
    """Mean self-information ``−log₂ p̂(item)`` of the recommended items (rarer ⇒ more novel).

    ``popularity`` is a ``{item_id: train-positive-count}`` mapping (as from
    :attr:`~bookrec.popularity.PopularityRetrievalPath.counts`); an item's ``p̂`` is its share of
    the total train positives. Items with a zero or missing count have an undefined (infinite)
    self-information, so they are skipped rather than returning ``inf``; the metric is the mean over
    the remaining items. Returns ``0.0`` when nothing can be scored (empty list, empty popularity,
    or every recommended item unseen in train). Pure and deterministic.
    """
    counts = {int(item_id): float(count) for item_id, count in popularity.items()}
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    ids = [item.item_id if isinstance(item, Candidate) else int(item) for item in recommendations]
    informations: list[float] = []
    for item_id in ids:
        count = counts.get(item_id, 0.0)
        if count > 0:
            informations.append(-math.log2(count / total))
    if not informations:
        return 0.0
    return sum(informations) / len(informations)


def head_ids_from_counts(
    counts: Mapping[int, int],
    catalog_ids: Iterable[int],
    *,
    fraction: float = 0.10,
) -> list[int]:
    """The head set: the top ``fraction`` of catalog items by train positive count.

    ``counts`` is a fitted ``{item_id: train-positive-count}`` mapping (as from
    :attr:`~bookrec.popularity.PopularityRetrievalPath.counts`); catalog items absent from it count
    ``0``. Returns ``ceil(fraction·N)`` item ids (``N`` = catalog size), ordered by count
    descending with ties broken by ascending item id, so the set is deterministic.
    """
    if not 0.0 < fraction <= 1.0:
        raise ValueError(f"fraction must be in (0, 1], got {fraction!r}")
    catalog = sorted({int(item_id) for item_id in catalog_ids})
    n = len(catalog)
    if n == 0:
        return []
    size = math.ceil(fraction * n)
    ranked = sorted(catalog, key=lambda item_id: (-counts.get(item_id, 0), item_id))
    return ranked[:size]
