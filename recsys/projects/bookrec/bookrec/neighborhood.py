"""Unit 4: neighborhood collaborative filtering — item-item co-occurrence (design 011 §6/§8).

The first **collaborative** retrieval path: it reads *who-read-what* from the interaction log
rather than the catalog text, and it is the first path to beat **both** popularity and the Unit-3
content/lexical path (a decisive ~2.3x popularity / ~1.6x lexical on the committed seed; Unit 3's
lexical already modestly edged popularity ~1.46x — CF is the first to beat both).

Two ideas live here:

- :func:`item_item_cosine` — build an item x item **cosine co-occurrence** similarity from a binary
  reader x item incidence of **train positives only**: two books are similar when the same readers
  engaged both. PORTED from the recoverability harness's ``_item_item_cf`` scorer (the harness
  takes a dense generator-sized reader x item matrix; this package has no generator object, so the
  logic is ported and the matrix is built from the row-mapping log instead).
- :class:`ItemItemRetrievalPath` — a :class:`~bookrec.protocol.BaseRetrievalPath` that fits that
  similarity from the log and, for a reader, scores every candidate by the **summed similarity to
  the books the reader has read** (``context["seen"]``) — *k*-nearest-neighbour retrieval over the
  item-similarity matrix. An ``n_neighbors`` cap is **optional and defaults to uncapped**: on this
  data an uncapped neighbourhood is best and a small cap *degrades* (taught honestly).

**Implicit feedback.** A read/like is a positive; there are no negative *ratings*. The log's
``label == 0`` rows are exposure-sampled negatives (exposed-not-liked) standing in for the
unobserved — but the co-occurrence path uses **positives only** (``split == "train"`` and
``label == 1``) and ranks the full catalog (no negative sampling; that arrives in Unit 5 MF).

**Leakage safety.** Only train positives enter the similarity; val/test rows and ``label == 0``
rows never touch it — folding val positives into ``fit`` would let the path "recover" the held-out
answer and score far too high. The package stays numpy-only (no pandas import).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import numpy as np

from bookrec.protocol import BaseRetrievalPath, Candidate


def item_item_cosine(incidence: np.ndarray) -> np.ndarray:
    """Cosine item x item co-occurrence similarity from a binary reader x item incidence matrix.

    PORTED from the recoverability harness ``_item_item_cf``: ``sim[i, j]`` is the cosine over the
    reader columns who co-engaged items ``i`` and ``j`` (``incidence[r, i] == 1.0`` iff reader ``r``
    has a train positive for item ``i``), with a **zeroed diagonal** so an item is never its own
    neighbour. An item nobody read is an all-zero column: its norm is clamped to ``1e-9`` so it gets
    an all-zero similarity row/column — the CF **coverage ceiling** — not a divide-by-zero.
    """
    incidence = np.asarray(incidence, dtype=float)
    norms = np.sqrt((incidence**2).sum(axis=0))
    sim = (incidence.T @ incidence) / np.maximum(np.outer(norms, norms), 1e-9)
    np.fill_diagonal(sim, 0.0)
    return sim


def _cap_neighbors(similarity: np.ndarray, n_neighbors: int) -> np.ndarray:
    """Keep each item's top-``n_neighbors`` neighbours (largest similarity), zero the rest.

    The *k*-nearest-neighbour restriction of the similarity matrix. On this data it *degrades* the
    scoreboard (an uncapped neighbourhood is best), which the unit teaches honestly; the default is
    uncapped (``n_neighbors=None``), so this is only reached when a cap is requested.
    """
    n_items = similarity.shape[0]
    if n_neighbors >= n_items:
        return similarity.copy()
    capped = np.zeros_like(similarity)
    # Per row, keep the n_neighbors columns with the largest similarity (the diagonal is already
    # zero, so a well-connected item never keeps itself over a real neighbour).
    keep = np.argsort(-similarity, axis=1)[:, :n_neighbors]
    rows = np.arange(n_items)[:, None]
    capped[rows, keep] = similarity[rows, keep]
    return capped


class ItemItemRetrievalPath(BaseRetrievalPath):
    """Item-item co-occurrence CF: recommend books similar to the ones a reader has read.

    Reader-dependent and **collaborative** — the similarity comes from the interaction log, not the
    catalog text. :meth:`fit` builds an item x item cosine similarity from the **train positives**;
    :meth:`retrieve` scores each candidate by the summed similarity to ``context["seen"]`` and
    returns the top ``k`` unseen items.
    """

    def __init__(
        self, *, n_neighbors: int | None = None, name: str = "item-item", version: str = "1"
    ) -> None:
        super().__init__(name=name, version=version)
        if n_neighbors is not None and (
            not isinstance(n_neighbors, int)
            or isinstance(n_neighbors, bool)
            or n_neighbors <= 0
        ):
            raise ValueError(f"n_neighbors must be a positive int or None, got {n_neighbors!r}")
        self.n_neighbors = n_neighbors
        self._item_ids: list[int] = []
        self._row_of: dict[int, int] = {}
        self._similarity: np.ndarray | None = None

    def fit(
        self, interactions: Iterable[Mapping[str, Any]], catalog: Any | None = None
    ) -> ItemItemRetrievalPath:
        """Build the item x item co-occurrence similarity from the **train positives**.

        ``interactions`` is an **iterable of row mappings** with keys
        ``reader_id, item_id, split, label`` (the shape ``DataFrame.to_dict("records")`` and the
        generator's own rows both satisfy — no pandas import, exactly like
        :meth:`~bookrec.popularity.PopularityRetrievalPath.fit`). Only rows with ``split == "train"``
        **and** ``label == 1`` enter the incidence; val/test rows and ``label == 0`` rows are
        leakage and are skipped in code (so the fitted similarity is bit-identical with or without
        them). The **item universe** is ``catalog`` when given, else the train-positive items
        (precedence: catalog if provided, else train items); readers are indexed from the train
        rows themselves. Raises :class:`ValueError` on an empty fit (no train positives).
        """
        known = {int(item_id) for item_id in catalog} if catalog is not None else None
        positives: set[tuple[int, int]] = set()
        for row in interactions:
            if row["split"] != "train" or int(row["label"]) != 1:
                continue
            item_id = int(row["item_id"])
            if known is not None and item_id not in known:
                continue
            positives.add((int(row["reader_id"]), item_id))
        if not positives:
            raise ValueError(
                "ItemItemRetrievalPath.fit found no positive train interactions to build from"
            )
        # Item universe: catalog if provided, else the train-positive items.
        item_ids = sorted(known) if known is not None else sorted({item for _, item in positives})
        row_of = {item: idx for idx, item in enumerate(item_ids)}
        # Index readers in a deterministic (sorted) order so the incidence — and therefore the
        # floating-point cosine summation — is fully determined by the positives, not input order.
        reader_ids = sorted({reader for reader, _ in positives})
        reader_of = {reader: idx for idx, reader in enumerate(reader_ids)}
        incidence = np.zeros((len(reader_ids), len(item_ids)), dtype=float)
        for reader, item_id in positives:
            incidence[reader_of[reader], row_of[item_id]] = 1.0
        similarity = item_item_cosine(incidence)
        if self.n_neighbors is not None:
            similarity = _cap_neighbors(similarity, self.n_neighbors)
        self._item_ids = item_ids
        self._row_of = row_of
        self._similarity = similarity
        self._fitted = True
        return self

    def load(self, artifact: Mapping[str, Any]) -> ItemItemRetrievalPath:
        """Restore a fitted path from its :meth:`artifact` state (arrays copied, never aliased).

        The artifact is the source of truth for the fitted state (item ids, similarity,
        ``n_neighbors``); ``name``/``version`` remain the path's identity.
        """
        state = dict(artifact)
        item_ids = [int(i) for i in state["item_ids"]]
        self._item_ids = item_ids
        self._row_of = {item: idx for idx, item in enumerate(item_ids)}
        self._similarity = np.array(state["similarity"], dtype=float)
        if "n_neighbors" in state:
            self.n_neighbors = state["n_neighbors"]
        self._fitted = True
        return self

    def artifact(self) -> dict[str, Any]:
        """The concrete fitted state this path owns and versions (item ids, similarity, cap)."""
        if self._similarity is None:
            raise RuntimeError("ItemItemRetrievalPath.artifact before fit/load")
        return {
            "item_ids": list(self._item_ids),
            "similarity": self._similarity.copy(),
            "n_neighbors": self.n_neighbors,
        }

    @property
    def similarity(self) -> np.ndarray:
        """A copy of the fitted item x item similarity matrix."""
        if self._similarity is None:
            raise RuntimeError("ItemItemRetrievalPath.similarity before fit/load")
        return self._similarity.copy()

    def retrieve(self, query: Any, context: Any, k: int) -> list[Candidate]:
        """Top ``k`` unseen books by summed similarity to the reader's ``context["seen"]`` items.

        *k*-nearest-neighbour retrieval: a candidate's score is the sum of its similarity to every
        seen book. ``seen`` items absent from the fitted index are skipped (no ``KeyError`` on a
        hand-built context); an empty ``seen`` — or a ``seen`` with no indexed item — returns ``[]``.
        Seen books are excluded from the recommendations (a re-read is not a recommendation).
        """
        del query  # the reader is identified through context["seen"], not the query id
        if self._similarity is None:
            raise RuntimeError("ItemItemRetrievalPath.retrieve before fit/load")
        if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
            raise ValueError(f"k must be a positive int, got {k!r}")
        seen = set(context.get("seen", ())) if isinstance(context, Mapping) else set()
        seen_cols = [self._row_of[item_id] for item_id in seen if item_id in self._row_of]
        if not seen_cols:
            return []
        scores = self._similarity[:, seen_cols].sum(axis=1)
        candidates = [
            Candidate(item_id, float(scores[row]), self.name)
            for row, item_id in enumerate(self._item_ids)
            if item_id not in seen
        ]
        return self._finish(candidates, k)
