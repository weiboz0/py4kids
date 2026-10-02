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
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence

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
