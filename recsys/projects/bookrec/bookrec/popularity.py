"""Unit 2: the popularity (count) retrieval path and the weighted-rating quality lens.

Design 011 §6/§8. Two distinct ideas live here:

- :class:`PopularityRetrievalPath` ranks catalog items by their **popularity** — the count of
  positive **train** interactions per item. It is reader-independent (the same ranking for every
  query: not yet personalised), the simplest path that reads data, and it really beats Unit 1's
  random floor. Leakage safety is enforced in code: val/test rows and ``label == 0`` rows never
  touch the counts.
- :func:`weighted_rating` is the **weighted / Bayesian-shrinkage** *quality* estimate
  ``(v·R + m·C)/(v + m)``. It is a different lens (quality, not raw popularity): a 3-of-3 book is
  not called better than a 9000-of-10000 book, because the shrinkage pulls a thin-evidence rate
  toward the global rate ``C``. It is id-free and does not tie-break — ordering is the ranker's
  job.

The package is **numpy-only**: ``bookrec`` declares no pandas dependency (see
:mod:`bookrec.catalog`), so :meth:`PopularityRetrievalPath.fit` **duck-types** an iterable of row
mappings — the shape a pandas ``DataFrame.to_dict("records")`` and the generator's own rows both
satisfy — rather than importing pandas.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import numpy as np

from bookrec.protocol import BaseRetrievalPath, Candidate


class PopularityRetrievalPath(BaseRetrievalPath):
    """Rank catalog items by popularity: the count of positive ``train`` interactions per item.

    Reader-independent — :meth:`retrieve` returns the same ranking for every query (popularity is
    not personalisation), honouring ``context["seen"]`` so a re-read is never recommended.
    """

    def __init__(self, name: str = "popularity", version: str = "1") -> None:
        super().__init__(name=name, version=version)
        self._counts: dict[int, int] = {}

    def fit(
        self, interactions: Iterable[Mapping[str, Any]], catalog: Any | None = None
    ) -> PopularityRetrievalPath:
        """Count the positive ``train`` interactions per catalog item.

        ``interactions`` is an **iterable of row mappings** with keys
        ``reader_id, item_id, split, label`` (the shape ``DataFrame.to_dict("records")`` and the
        generator's own rows both satisfy — no pandas import). Only rows with ``split == "train"``
        **and** ``label == 1`` are counted; val/test rows and ``label == 0`` rows are leakage and
        are skipped in code. ``catalog`` (optional, any iterable of item ids) restricts counting to
        known catalog items. Raises :class:`ValueError` on an empty fit (no train positives).
        """
        known = {int(item_id) for item_id in catalog} if catalog is not None else None
        counts: dict[int, int] = {}
        for row in interactions:
            if row["split"] != "train" or int(row["label"]) != 1:
                continue
            item_id = int(row["item_id"])
            if known is not None and item_id not in known:
                continue
            counts[item_id] = counts.get(item_id, 0) + 1
        if not counts:
            raise ValueError(
                "PopularityRetrievalPath.fit found no positive train interactions to count"
            )
        self._counts = counts
        self._fitted = True
        return self

    def load(self, artifact: Mapping[int, int]) -> PopularityRetrievalPath:
        """Restore a fitted path from its ``{item_id: count}`` artifact."""
        counts = {int(key): int(value) for key, value in dict(artifact).items()}
        if not counts:
            raise ValueError("PopularityRetrievalPath.load received an empty artifact")
        self._counts = counts
        self._fitted = True
        return self

    def artifact(self) -> dict[int, int]:
        """The fitted ``{item_id: popularity-count}`` mapping this path owns and versions."""
        return dict(self._counts)

    @property
    def counts(self) -> dict[int, int]:
        """A copy of the fitted per-item popularity counts."""
        return dict(self._counts)

    def retrieve(self, query: Any, context: Any, k: int) -> list[Candidate]:
        """Return the top ``k`` items by popularity count, reader-independent, minus ``seen``."""
        del query  # popularity is reader-independent
        if not self._fitted:
            raise RuntimeError("PopularityRetrievalPath.retrieve before fit/load")
        if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
            raise ValueError(f"k must be a positive int, got {k!r}")
        seen = set(context.get("seen", ())) if isinstance(context, Mapping) else set()
        candidates = [
            Candidate(item_id, float(count), self.name)
            for item_id, count in self._counts.items()
            if item_id not in seen
        ]
        return self._finish(candidates, k)


def weighted_rating(
    positives: Any,
    exposures: Any,
    *,
    m: float = 10.0,
    global_rate: float | None = None,
) -> np.ndarray:
    """The weighted / Bayesian-shrinkage quality score ``(v·R + m·C)/(v + m)``, vectorised.

    For each item: ``R = positives/exposures`` is the item's own positive **rate**, ``v`` is its
    exposure (``= exposures``), ``C`` is the global positive rate ``global_rate`` (default:
    ``sum(positives)/sum(exposures)``), and ``m`` is the prior strength in pseudo-counts.

    This helper is **id-free** and does **not** tie-break: it returns one score per item in input
    order; ordering/tie-breaking is the ranker's job.

    Limits (using the identity ``score = C + v·(R − C)/(v + m)``):

    - ``m → 0`` ⇒ ``score = R`` (the raw rate; no shrinkage).
    - as ``m`` grows every score **contracts toward ``C``** — ``|score − C| = |v·(R − C)|/(v + m)``
      shrinks monotonically. The ranking does *not* collapse to a flat global order at any finite
      ``m`` (it approaches an exposure-weighted ``v·(R − C)`` order); exact all-equal ties arise
      only in the infinite-``m`` limit.

    The default ``m = 10.0`` exhibits the reversal the unit teaches: with a realistic (low) global
    rate, a 3-of-3 item scores **below** a 9000-of-10000 item — thin evidence is not quality.
    ``v == 0`` is handled safely (its score is ``C``).
    """
    v = np.asarray(exposures, dtype=float)
    pos = np.asarray(positives, dtype=float)
    if v.shape != pos.shape:
        raise ValueError(
            f"positives and exposures must have the same shape, got {pos.shape} and {v.shape}"
        )
    if global_rate is None:
        total_v = float(v.sum())
        c = float(pos.sum()) / total_v if total_v > 0 else 0.0
    else:
        c = float(global_rate)
    fill = np.full(v.shape, c, dtype=float)
    rate = np.divide(pos, v, out=fill.copy(), where=v > 0)
    denom = v + m
    numer = v * rate + m * c
    return np.divide(numer, denom, out=fill.copy(), where=denom > 0)
