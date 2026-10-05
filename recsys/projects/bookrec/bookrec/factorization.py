"""Unit 5: matrix factorization — the latent-factor retrieval path (design 011 §6/§8).

The Part-1 -> Part-2 hinge. Where Unit 4's item-item CF reads co-occurrence off the log directly,
matrix factorization **learns** a low-dimensional factor (embedding) per reader and per book so that
``sigmoid(P_u . Q_i)`` approximates "reader ``u`` liked book ``i``". The learned reader/item factors
ARE embeddings scored by a dot product -- the exact shape Unit 8's neural two-tower will learn -- so
MF is the latent generalization of co-occurrence: on this data it is **on par with item-item CF**
(about 0.25-0.26 hit@10 vs CF's ~0.25, within noise over 500 readers), while beating the lexical
content path and popularity by wide margins.

Two ideas live here:

- the **latent-factor model** ``P Q^T`` (readers x factors, books x factors); a reader's score for a
  book is the dot product of their factors.
- :class:`MatrixFactorizationPath` -- a :class:`~bookrec.protocol.BaseRetrievalPath` that trains
  ``P`` / ``Q`` by **full-batch, per-entity-averaged gradient descent on a logistic
  implicit-feedback loss** with L2 regularization. PORTED from the recoverability harness's
  ``_learned_mf`` scorer (the harness takes dense generator-sized reader/item index arrays; this
  package has no generator object, so the logic is ported and the index arrays are built from the
  row-mapping log instead).

**Implicit feedback + sampled negatives.** A read/like is a positive; there are no negative
*ratings*. Training pairs the observed **train positives** (label 1) with ``n_negatives`` negatives
sampled **per train-positive interaction** from each reader's *unobserved complement* (a draw that
collides with one of that reader's own observed positives is resampled). These complement negatives
-- NOT the log's ``label == 0`` exposure negatives, which carry the taste signal and collapse MF to
the random floor -- are what make MF work (the Unit-5 lesson measures both).

**Item universe = the full catalog.** Every catalog item gets an initialized ``Q`` row, so retrieval
can score any item (broader candidate reach than CF's hard-zero cold column). **Readers = those with
>= 1 train positive**: only they get a learned ``P`` row. A cold reader (0 train positives) has no
factor -> ``retrieve`` returns ``[]``; a cold *item* does get a ``Q`` row, but with no positive
signal it is shaped only by negative gradient (pushed to a low score) -- the real cold-item fix is
Unit 9's features.

**Leakage safety.** Only ``split == "train"`` positives enter training; val/test rows and
``label == 0`` rows never touch ``P`` / ``Q`` (the fitted factors are identical with or without
them). Training is deterministic under ``seed`` (seeded factor init + seeded negative sampling). The
package stays **numpy-only** (no pandas, no torch -- torch begins Unit 8).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import numpy as np

from bookrec.protocol import BaseRetrievalPath, Candidate


def _positive_int(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} must be a positive int, got {value!r}")
    return value


def _positive_float(value: object, name: str) -> float:
    number = float(value)  # type: ignore[arg-type]
    if not np.isfinite(number) or number <= 0.0:
        raise ValueError(f"{name} must be a positive finite number, got {value!r}")
    return number


class MatrixFactorizationPath(BaseRetrievalPath):
    """Latent-factor retrieval: learn reader/book factors so ``sigmoid(P_u . Q_i) ~= liked``.

    Reader-dependent and **collaborative** -- the factors are learned from the interaction log, not
    the catalog text. :meth:`fit` trains ``P`` / ``Q`` by full-batch, per-entity-averaged gradient
    descent on a logistic implicit-feedback loss with L2 regularization; :meth:`retrieve` scores a
    fitted reader's whole catalog by ``P[reader] . Q^T`` and returns the top ``k`` unseen items.

    The constructor defaults are **pinned** to the configuration measured on the shipped data
    (``n_factors=32, n_epochs=300, learning_rate=0.5, reg=0.05, n_negatives=10``): below ~300 epochs
    MF silently drops under the lexical path, so these are NOT "small/few" -- do not shrink them.
    """

    def __init__(
        self,
        *,
        n_factors: int = 32,
        n_epochs: int = 300,
        learning_rate: float = 0.5,
        reg: float = 0.05,
        n_negatives: int = 10,
        seed: int = 0,
        name: str = "mf",
        version: str = "1",
    ) -> None:
        super().__init__(name=name, version=version)
        self.n_factors = _positive_int(n_factors, "n_factors")
        self.n_epochs = _positive_int(n_epochs, "n_epochs")
        self.learning_rate = _positive_float(learning_rate, "learning_rate")
        self.reg = _positive_float(reg, "reg")
        self.n_negatives = _positive_int(n_negatives, "n_negatives")
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise TypeError(f"seed must be an int, got {seed!r}")
        self.seed = seed
        self._reader_ids: list[int] = []
        self._item_ids: list[int] = []
        self._reader_of: dict[int, int] = {}
        self._row_of: dict[int, int] = {}
        self._p: np.ndarray | None = None
        self._q: np.ndarray | None = None

    # ----------------------------------------------------------------------------- training
    def _accumulate(self, index: np.ndarray, weighted: np.ndarray, size: int) -> np.ndarray:
        """Per-entity gradient sum via per-column ``bincount`` (far faster than ``np.add.at``)."""
        out = np.empty((size, weighted.shape[1]))
        for d in range(weighted.shape[1]):
            out[:, d] = np.bincount(index, weights=weighted[:, d], minlength=size)
        return out

    def _train(
        self, pos_readers: np.ndarray, pos_items: np.ndarray, n_readers: int, n_books: int
    ) -> tuple[np.ndarray, np.ndarray]:
        """Full-batch, per-entity-averaged gradient descent on the logistic implicit-feedback loss.

        PORTS ``_reference_recommenders._learned_mf`` exactly: seeded factor init, ``n_negatives``
        complement negatives sampled **per train-positive** (resampling collisions with that
        reader's own positives), a logistic loss over positives + sampled negatives, and a step that
        divides each entity's summed gradient by its interaction count, with L2 regularization.
        """
        rng = np.random.default_rng(self.seed)
        p = rng.normal(0.0, 0.1, size=(n_readers, self.n_factors))
        q = rng.normal(0.0, 0.1, size=(n_books, self.n_factors))
        n_pos = pos_readers.shape[0]
        neg_readers = np.repeat(pos_readers, self.n_negatives)
        neg_items = rng.integers(0, n_books, size=n_pos * self.n_negatives)
        # Sample negatives from each reader's UNOBSERVED complement: resample any draw that collides
        # with one of that reader's observed positives so no "negative" is actually a known positive.
        observed = set(zip(pos_readers.tolist(), pos_items.tolist()))
        neg_reader_list = neg_readers.tolist()
        pending = [
            j for j in range(neg_items.shape[0]) if (neg_reader_list[j], int(neg_items[j])) in observed
        ]
        while pending:
            neg_items[pending] = rng.integers(0, n_books, size=len(pending))
            pending = [j for j in pending if (neg_reader_list[j], int(neg_items[j])) in observed]
        u_idx = np.concatenate([pos_readers, neg_readers])
        i_idx = np.concatenate([pos_items, neg_items])
        y = np.concatenate([np.ones(n_pos), np.zeros(n_pos * self.n_negatives)])
        count_u = np.maximum(np.bincount(u_idx, minlength=n_readers), 1)[:, None]
        count_i = np.maximum(np.bincount(i_idx, minlength=n_books), 1)[:, None]
        for _ in range(self.n_epochs):
            scores = (p[u_idx] * q[i_idx]).sum(axis=1)
            err = y - 1.0 / (1.0 + np.exp(-scores))
            grad_p = self._accumulate(u_idx, err[:, None] * q[i_idx], n_readers)
            grad_q = self._accumulate(i_idx, err[:, None] * p[u_idx], n_books)
            p += self.learning_rate * (grad_p / count_u - self.reg * p)
            q += self.learning_rate * (grad_q / count_i - self.reg * q)
        return p, q

    def fit(
        self, interactions: Iterable[Mapping[str, Any]], catalog: Any | None = None
    ) -> MatrixFactorizationPath:
        """Train ``P`` / ``Q`` from the **train positives** of a row-mapping interaction log.

        ``interactions`` is an **iterable of row mappings** with keys
        ``reader_id, item_id, split, label`` (the shape ``DataFrame.to_dict("records")`` and the
        generator's own rows both satisfy -- no pandas import, exactly like
        :meth:`~bookrec.popularity.PopularityRetrievalPath.fit`). Only rows with ``split == "train"``
        **and** ``label == 1`` are training positives; val/test rows and ``label == 0`` rows never
        touch ``P`` / ``Q`` (leakage safety -- the factors are bit-identical with or without them).

        The **item universe** is ``catalog`` when given (every catalog item gets an initialized
        ``Q`` row, so retrieval can score the whole catalog), else the train-positive items.
        **Readers** are those with >= 1 train positive (only they get a learned ``P`` row). Training
        is deterministic under ``seed``. Raises :class:`ValueError` on an empty fit (no train
        positives).
        """
        known = sorted({int(item_id) for item_id in catalog}) if catalog is not None else None
        known_set = set(known) if known is not None else None
        pos_pairs: list[tuple[int, int]] = []
        for row in interactions:
            if row["split"] != "train" or int(row["label"]) != 1:
                continue
            item_id = int(row["item_id"])
            if known_set is not None and item_id not in known_set:
                continue
            pos_pairs.append((int(row["reader_id"]), item_id))
        if not pos_pairs:
            raise ValueError(
                "MatrixFactorizationPath.fit found no positive train interactions to train from"
            )
        item_ids = known if known is not None else sorted({item for _, item in pos_pairs})
        row_of = {item: idx for idx, item in enumerate(item_ids)}
        reader_ids = sorted({reader for reader, _ in pos_pairs})
        reader_of = {reader: idx for idx, reader in enumerate(reader_ids)}
        pos_readers = np.array([reader_of[reader] for reader, _ in pos_pairs], dtype=np.int64)
        pos_items = np.array([row_of[item] for _, item in pos_pairs], dtype=np.int64)
        p, q = self._train(pos_readers, pos_items, len(reader_ids), len(item_ids))
        self._reader_ids = reader_ids
        self._item_ids = item_ids
        self._reader_of = reader_of
        self._row_of = row_of
        self._p = p
        self._q = q
        self._fitted = True
        return self

    # --------------------------------------------------------------------------- persistence
    def load(self, artifact: Mapping[str, Any]) -> MatrixFactorizationPath:
        """Restore a fitted path from its :meth:`artifact` state (arrays copied, never aliased)."""
        state = dict(artifact)
        reader_ids = [int(r) for r in state["reader_ids"]]
        item_ids = [int(i) for i in state["item_ids"]]
        p = np.array(state["P"], dtype=float)
        q = np.array(state["Q"], dtype=float)
        if p.shape != (len(reader_ids), q.shape[1]):
            raise ValueError(
                f"MatrixFactorizationPath.load: P shape {p.shape} does not match "
                f"({len(reader_ids)}, n_factors) for the restored reader_ids"
            )
        if q.shape != (len(item_ids), p.shape[1]):
            raise ValueError(
                f"MatrixFactorizationPath.load: Q shape {q.shape} does not match "
                f"({len(item_ids)}, n_factors) for the restored item_ids"
            )
        params = dict(state.get("params", {}))
        for key in ("n_factors", "n_epochs", "n_negatives", "seed"):
            if key in params:
                setattr(self, key, int(params[key]))
        for key in ("learning_rate", "reg"):
            if key in params:
                setattr(self, key, float(params[key]))
        self._reader_ids = reader_ids
        self._item_ids = item_ids
        self._reader_of = {reader: idx for idx, reader in enumerate(reader_ids)}
        self._row_of = {item: idx for idx, item in enumerate(item_ids)}
        self._p = p
        self._q = q
        self._fitted = True
        return self

    def artifact(self) -> dict[str, Any]:
        """The fitted state this path owns and versions (``P``, ``Q``, ids, hyperparameters)."""
        if self._p is None or self._q is None:
            raise RuntimeError("MatrixFactorizationPath.artifact before fit/load")
        return {
            "P": self._p.copy(),
            "Q": self._q.copy(),
            "reader_ids": list(self._reader_ids),
            "item_ids": list(self._item_ids),
            "params": {
                "n_factors": self.n_factors,
                "n_epochs": self.n_epochs,
                "learning_rate": self.learning_rate,
                "reg": self.reg,
                "n_negatives": self.n_negatives,
                "seed": self.seed,
            },
        }

    @property
    def reader_factors(self) -> np.ndarray:
        """A copy of the learned reader factor matrix ``P`` (readers x factors)."""
        if self._p is None:
            raise RuntimeError("MatrixFactorizationPath.reader_factors before fit/load")
        return self._p.copy()

    @property
    def item_factors(self) -> np.ndarray:
        """A copy of the learned item factor matrix ``Q`` (items x factors)."""
        if self._q is None:
            raise RuntimeError("MatrixFactorizationPath.item_factors before fit/load")
        return self._q.copy()

    # ------------------------------------------------------------------------------ retrieval
    def retrieve(self, query: Any, context: Any, k: int) -> list[Candidate]:
        """Top ``k`` unseen books for a fitted reader by ``P[reader] . Q^T`` over the whole catalog.

        The reader is identified by ``query`` (the reader id). A reader **with** a learned factor is
        scored over all catalog items **regardless of whether** ``context["seen"]`` is empty -- MF
        does not build its query from ``seen`` (``seen`` is used only to *exclude* already-read books
        from the result, so an empty ``seen`` excludes nothing and still returns ``k`` recs). Only a
        reader with **no learned factor** (unknown / cold -- 0 train positives) returns ``[]``.
        """
        if self._p is None or self._q is None:
            raise RuntimeError("MatrixFactorizationPath.retrieve before fit/load")
        if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
            raise ValueError(f"k must be a positive int, got {k!r}")
        try:
            reader_id = int(query)
        except (TypeError, ValueError):
            return []
        row = self._reader_of.get(reader_id)
        if row is None:  # no learned factor -> cold/unknown reader
            return []
        seen = set(context.get("seen", ())) if isinstance(context, Mapping) else set()
        scores = self._p[row] @ self._q.T
        candidates = [
            Candidate(item_id, float(scores[col]), self.name)
            for col, item_id in enumerate(self._item_ids)
            if item_id not in seen
        ]
        return self._finish(candidates, k)
