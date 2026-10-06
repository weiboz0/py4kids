"""Unit 8: the two-tower model — MF re-expressed as a learned neural retriever (design 011 §6/§8).

The second Part-2 unit and the **first PyTorch unit**. Unit 5's :class:`MatrixFactorizationPath`
learned a reader factor ``P_u`` and a book factor ``Q_i`` by full-batch numpy gradient descent on a
**pointwise logistic** loss. The two-tower keeps *exactly* that latent dot-product model — a reader
embedding tower and a book embedding tower whose dot product scores a match — but **re-expresses it
as a learned neural network**: the towers are :class:`torch.nn.Embedding` layers trained by autograd
with the **Adam** optimizer over mini-batches, under a **pairwise ranking** objective instead.

Two ideas live here:

- the **two-tower / dual-encoder** architecture: ``score(reader, book) = reader_emb . book_emb``
  — the same embedding dot product as MF, GloVe cosine (Unit 7) and the whole embedding-retrieval
  family, now *learned neurally*;
- :class:`TwoTowerRetrievalPath` — a :class:`~bookrec.protocol.BaseRetrievalPath` trained by **BPR**
  (Bayesian Personalized Ranking): the pairwise implicit-feedback loss
  ``-log sigmoid(s_pos - s_neg)`` over ``(reader, train-positive, sampled-negative)`` triples, with
  Adam + L2 weight decay.

**Why a ranking objective, and why weight decay.** On this data the two-tower is the **best path in
the book so far** (measured hit@10 ~0.340 vs MF 0.276 vs CF 0.252) — but **only when regularized**.
The same reader.book dot product is MF's; what changed is the *objective and optimizer* (pairwise
BPR + Adam mini-batches + weight decay vs MF's pointwise logistic full-batch gradient descent), and
the ranking objective wins on top-k. With ``weight_decay = 0`` the BPR loss collapses toward 0
(the model memorizes the train pairs) and val hit@10 drops to ~0.144 (below CF and lexical) — the
hand-delivered overfitting lesson. The constructor default ``weight_decay = 1e-4`` is REQUIRED.

**Implicit feedback + sampled negatives.** A read/like is a positive; there are no negative
*ratings*. Each **train positive** is paired with ``n_negatives`` negatives sampled (numpy RNG) from
that reader's **unobserved complement** — a draw that collides with one of the reader's own observed
positives is resampled — exactly as Unit 5's MF samples negatives. BPR then pushes the positive's
score above each sampled negative's.

**Item universe = the full catalog.** Every catalog item gets a learned item-embedding row (so
retrieval can score any book). **Readers = those with >= 1 train positive** (only they get a learned
reader-embedding row); a reader with no learned embedding (unknown / cold) retrieves ``[]``.

**Leakage safety.** Only ``split == "train"`` positives enter training; val/test rows and
``label == 0`` rows never touch the towers (the fitted embeddings are identical with or without
them).

**Determinism (design 011 §7).** Training seeds :func:`torch.manual_seed` (embedding init) and a
numpy RNG (negative sampling / shuffling), enables :func:`torch.use_deterministic_algorithms` and
pins :func:`torch.set_num_threads` to 1 — so two seeded fits are reproducible (identical top-k
ranking + ``allclose`` embeddings; bit-identical on CPU). Those last two calls mutate **process
state**, so :meth:`fit` **saves and restores** their previous values in a ``finally`` block (it must
not leave later notebook cells silently single-threaded / in deterministic mode).

**torch is imported LAZILY, inside** :meth:`fit` **only** — this module has NO top-level
``import torch``. Training needs torch; :meth:`retrieve`, :meth:`load` and :meth:`artifact` operate
on the **numpy** embedding matrices stored at fit, so importing ``bookrec`` and calling those three
never imports torch (proven by an import-blocked-subprocess test). torch begins — and stays
confined to training in — this unit.
"""

from __future__ import annotations

from collections import defaultdict
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


def _nonnegative_float(value: object, name: str) -> float:
    number = float(value)  # type: ignore[arg-type]
    if not np.isfinite(number) or number < 0.0:
        raise ValueError(f"{name} must be a non-negative finite number, got {value!r}")
    return number


class TwoTowerRetrievalPath(BaseRetrievalPath):
    """Two-tower / dual-encoder retrieval: learn reader/book embeddings so ``reader . book`` ranks.

    Reader-dependent and **collaborative** — the towers are learned from the interaction log, not
    the catalog text. :meth:`fit` trains a reader :class:`torch.nn.Embedding` tower and a book
    tower by **BPR** (pairwise ranking) with Adam + weight decay (torch, lazily imported here);
    :meth:`retrieve` scores a fitted reader's whole catalog by ``reader_emb . book_emb^T`` using the
    **numpy** embeddings stored at fit (torch-free) and returns the top ``k`` unseen items.

    The constructor defaults are **pinned** to the configuration measured on the shipped data
    (``embedding_dim=32, n_epochs=60, learning_rate=0.01, n_negatives=10, batch_size=256,
    weight_decay=1e-4, seed=0``): at ``weight_decay=1e-4`` the two-tower reaches hit@10 ~0.340 (the
    book's best), while ``weight_decay=0`` overfits below CF. ``weight_decay`` may be 0 (the taught
    overfitting demo); every other hyperparameter is strictly positive.
    """

    def __init__(
        self,
        *,
        embedding_dim: int = 32,
        n_epochs: int = 60,
        learning_rate: float = 0.01,
        n_negatives: int = 10,
        batch_size: int = 256,
        weight_decay: float = 1e-4,
        seed: int = 0,
        name: str = "two-tower",
        version: str = "1",
    ) -> None:
        super().__init__(name=name, version=version)
        self.embedding_dim = _positive_int(embedding_dim, "embedding_dim")
        self.n_epochs = _positive_int(n_epochs, "n_epochs")
        self.learning_rate = _positive_float(learning_rate, "learning_rate")
        self.n_negatives = _positive_int(n_negatives, "n_negatives")
        self.batch_size = _positive_int(batch_size, "batch_size")
        # weight_decay = 0 is a VALID (overfitting-demo) config, so it is non-negative, not positive.
        self.weight_decay = _nonnegative_float(weight_decay, "weight_decay")
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise TypeError(f"seed must be an int, got {seed!r}")
        self.seed = seed
        self._reader_ids: list[int] = []
        self._item_ids: list[int] = []
        self._reader_of: dict[int, int] = {}
        self._row_of: dict[int, int] = {}
        self._reader_matrix: np.ndarray | None = None  # (n_readers, dim) float32
        self._item_matrix: np.ndarray | None = None  # (n_books, dim) float32
        self._loss_history: list[float] = []  # mean BPR loss per epoch (via loss.item())

    # ----------------------------------------------------------------------------- training
    def fit(
        self, interactions: Iterable[Mapping[str, Any]], catalog: Any | None = None
    ) -> TwoTowerRetrievalPath:
        """Train the reader/book embedding towers by BPR from the log's **train positives**.

        ``interactions`` is an **iterable of row mappings** with keys
        ``reader_id, item_id, split, label`` (the shape ``DataFrame.to_dict("records")`` and the
        generator's own rows both satisfy — no pandas import, exactly like
        :meth:`~bookrec.factorization.MatrixFactorizationPath.fit`). Only rows with
        ``split == "train"`` **and** ``label == 1`` are training positives; val/test rows and
        ``label == 0`` rows never touch the towers (leakage safety).

        The **item universe** is ``catalog`` when given (every catalog item gets a learned
        item-embedding row, so retrieval can score the whole catalog), else the train-positive
        items. **Readers** are those with >= 1 train positive (only they get a learned
        reader-embedding row). torch is **imported here** (the only place this module needs it);
        training is deterministic under ``seed``. Raises :class:`ValueError` on an empty fit.
        """
        import torch  # LAZY: torch is needed only to train; retrieve/load/artifact stay torch-free.

        known = sorted({int(item_id) for item_id in catalog}) if catalog is not None else None
        known_set = set(known) if known is not None else None
        pos_pairs: list[tuple[int, int]] = []
        reader_positives: dict[int, set[int]] = defaultdict(set)
        for row in interactions:
            if row["split"] != "train" or int(row["label"]) != 1:
                continue
            item_id = int(row["item_id"])
            if known_set is not None and item_id not in known_set:
                continue
            reader_id = int(row["reader_id"])
            pos_pairs.append((reader_id, item_id))
            reader_positives[reader_id].add(item_id)
        if not pos_pairs:
            raise ValueError(
                "TwoTowerRetrievalPath.fit found no positive train interactions to train from"
            )
        item_ids = known if known is not None else sorted({item for _, item in pos_pairs})
        row_of = {item: idx for idx, item in enumerate(item_ids)}
        reader_ids = sorted(reader_positives)
        reader_of = {reader: idx for idx, reader in enumerate(reader_ids)}
        n_readers, n_books = len(reader_ids), len(item_ids)

        # Positive triples (row-index space); negatives are drawn fresh each epoch below.
        pos_r = np.array([reader_of[reader] for reader, _ in pos_pairs], dtype=np.int64)
        pos_i = np.array([row_of[item] for _, item in pos_pairs], dtype=np.int64)

        # Each positive spawns ``n_negatives`` BPR triples. A reader whose observed positives cover
        # the WHOLE catalog has an empty unobserved complement and can supply no negative, so its
        # triples are dropped (inert on the shipped data; guards the tiny test fixtures from an
        # endless collision-resampling loop — exactly MF's guard).
        full_coverage = {reader_of[r] for r, items in reader_positives.items() if len(items) >= n_books}
        triple_r = np.repeat(pos_r, self.n_negatives)
        triple_pos = np.repeat(pos_i, self.n_negatives)
        if full_coverage:
            keep = np.array([r not in full_coverage for r in triple_r.tolist()])
            triple_r = triple_r[keep]
            triple_pos = triple_pos[keep]
        n_triples = int(triple_r.shape[0])
        if n_triples == 0:
            raise ValueError(
                "TwoTowerRetrievalPath.fit: every reader covers the whole catalog, so no "
                "sampled negative exists to form a BPR triple"
            )
        # Observed (reader_row, item_row) pairs encoded as single ints for fast collision tests.
        observed_codes = np.array(
            sorted({reader_of[r] * n_books + row_of[it] for r, it in pos_pairs}), dtype=np.int64
        )

        rng = np.random.default_rng(self.seed)

        # Save the PROCESS-GLOBAL determinism knobs and restore them when fit returns, so a later
        # notebook cell is not silently left single-threaded / in deterministic-algorithm mode.
        prev_deterministic = torch.are_deterministic_algorithms_enabled()
        prev_threads = torch.get_num_threads()
        try:
            torch.use_deterministic_algorithms(True)
            torch.set_num_threads(1)
            torch.manual_seed(self.seed)

            reader_tower = torch.nn.Embedding(n_readers, self.embedding_dim)
            item_tower = torch.nn.Embedding(n_books, self.embedding_dim)
            # Small seeded init keeps initial scores near 0 (sigmoid unsaturated), like MF's 0.1 std.
            torch.nn.init.normal_(reader_tower.weight, mean=0.0, std=0.1)
            torch.nn.init.normal_(item_tower.weight, mean=0.0, std=0.1)
            optimizer = torch.optim.Adam(
                list(reader_tower.parameters()) + list(item_tower.parameters()),
                lr=self.learning_rate,
                weight_decay=self.weight_decay,
            )

            self._loss_history = []
            for _ in range(self.n_epochs):
                # Resample this epoch's negatives from each reader's unobserved complement, then
                # resample any collision with one of that reader's observed positives.
                neg = rng.integers(0, n_books, size=n_triples)
                collide = np.isin(triple_r * n_books + neg, observed_codes)
                while collide.any():
                    neg[collide] = rng.integers(0, n_books, size=int(collide.sum()))
                    collide = np.isin(triple_r * n_books + neg, observed_codes)
                perm = rng.permutation(n_triples)
                readers_t = torch.from_numpy(triple_r[perm])
                pos_t = torch.from_numpy(triple_pos[perm])
                neg_t = torch.from_numpy(neg[perm])

                epoch_loss = 0.0
                n_batches = 0
                for start in range(0, n_triples, self.batch_size):
                    br = readers_t[start : start + self.batch_size]
                    bp = pos_t[start : start + self.batch_size]
                    bn = neg_t[start : start + self.batch_size]
                    reader_vec = reader_tower(br)
                    s_pos = (reader_vec * item_tower(bp)).sum(dim=1)
                    s_neg = (reader_vec * item_tower(bn)).sum(dim=1)
                    loss = -torch.nn.functional.logsigmoid(s_pos - s_neg).mean()
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    epoch_loss += loss.item()  # .item(), not float(loss) (avoids the grad-tensor warning)
                    n_batches += 1
                self._loss_history.append(epoch_loss / n_batches)

            reader_matrix = reader_tower.weight.detach().numpy().astype(np.float32).copy()
            item_matrix = item_tower.weight.detach().numpy().astype(np.float32).copy()
        finally:
            torch.use_deterministic_algorithms(prev_deterministic)
            torch.set_num_threads(prev_threads)

        self._reader_ids = reader_ids
        self._item_ids = item_ids
        self._reader_of = reader_of
        self._row_of = row_of
        self._reader_matrix = reader_matrix
        self._item_matrix = item_matrix
        self._fitted = True
        return self

    # --------------------------------------------------------------------------- persistence
    def load(self, artifact: Mapping[str, Any]) -> TwoTowerRetrievalPath:
        """Restore a fitted path from its :meth:`artifact` state (numpy only — never imports torch).

        The embedding matrices are copied (never aliased) so a later mutation of the artifact dict
        cannot reach into the loaded path.
        """
        state = dict(artifact)
        reader_ids = [int(r) for r in state["reader_ids"]]
        item_ids = [int(i) for i in state["item_ids"]]
        reader_matrix = np.array(state["reader_embeddings"], dtype=np.float32)
        item_matrix = np.array(state["item_embeddings"], dtype=np.float32)
        if reader_matrix.shape != (len(reader_ids), item_matrix.shape[1]):
            raise ValueError(
                f"TwoTowerRetrievalPath.load: reader-embedding shape {reader_matrix.shape} does "
                f"not match ({len(reader_ids)}, embedding_dim) for the restored reader_ids"
            )
        if item_matrix.shape != (len(item_ids), reader_matrix.shape[1]):
            raise ValueError(
                f"TwoTowerRetrievalPath.load: item-embedding shape {item_matrix.shape} does not "
                f"match ({len(item_ids)}, embedding_dim) for the restored item_ids"
            )
        params = dict(state.get("params", {}))
        for key in ("embedding_dim", "n_epochs", "n_negatives", "batch_size", "seed"):
            if key in params:
                setattr(self, key, int(params[key]))
        for key in ("learning_rate", "weight_decay"):
            if key in params:
                setattr(self, key, float(params[key]))
        self._reader_ids = reader_ids
        self._item_ids = item_ids
        self._reader_of = {reader: idx for idx, reader in enumerate(reader_ids)}
        self._row_of = {item: idx for idx, item in enumerate(item_ids)}
        self._reader_matrix = reader_matrix
        self._item_matrix = item_matrix
        self._fitted = True
        return self

    def artifact(self) -> dict[str, Any]:
        """The fitted state this path owns and versions (embedding matrices, ids, hyperparameters).

        Numpy only — a restored path runs :meth:`retrieve` without ever importing torch.
        """
        if self._reader_matrix is None or self._item_matrix is None:
            raise RuntimeError("TwoTowerRetrievalPath.artifact before fit/load")
        return {
            "reader_embeddings": self._reader_matrix.copy(),
            "item_embeddings": self._item_matrix.copy(),
            "reader_ids": list(self._reader_ids),
            "item_ids": list(self._item_ids),
            "params": {
                "embedding_dim": self.embedding_dim,
                "n_epochs": self.n_epochs,
                "learning_rate": self.learning_rate,
                "n_negatives": self.n_negatives,
                "batch_size": self.batch_size,
                "weight_decay": self.weight_decay,
                "seed": self.seed,
            },
        }

    @property
    def reader_embeddings(self) -> np.ndarray:
        """A copy of the learned reader-embedding matrix (readers x embedding_dim)."""
        if self._reader_matrix is None:
            raise RuntimeError("TwoTowerRetrievalPath.reader_embeddings before fit/load")
        return self._reader_matrix.copy()

    @property
    def item_embeddings(self) -> np.ndarray:
        """A copy of the learned item-embedding matrix (items x embedding_dim)."""
        if self._item_matrix is None:
            raise RuntimeError("TwoTowerRetrievalPath.item_embeddings before fit/load")
        return self._item_matrix.copy()

    @property
    def loss_history(self) -> list[float]:
        """Mean BPR loss per epoch from the last :meth:`fit` (empty after :meth:`load`)."""
        return list(self._loss_history)

    # ------------------------------------------------------------------------------ retrieval
    def retrieve(self, query: Any, context: Any, k: int) -> list[Candidate]:
        """Top ``k`` unseen books for a fitted reader by ``reader_emb . item_emb^T`` (torch-free).

        Scored with the **numpy** embeddings stored at fit — no torch import. A reader **with** a
        learned embedding is scored over all catalog items **regardless of whether**
        ``context["seen"]`` is empty (the score does not depend on ``seen``; ``seen`` only *excludes*
        already-read books, and stale ``seen`` ids absent from the catalog are simply ignored, as in
        Unit 5's MF). Only a reader with **no learned embedding** (unknown / cold — 0 train
        positives) returns ``[]``.
        """
        if self._reader_matrix is None or self._item_matrix is None:
            raise RuntimeError("TwoTowerRetrievalPath.retrieve before fit/load")
        if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
            raise ValueError(f"k must be a positive int, got {k!r}")
        try:
            reader_id = int(query)
        except (TypeError, ValueError):
            return []
        row = self._reader_of.get(reader_id)
        if row is None:  # no learned embedding -> cold/unknown reader
            return []
        seen = set(context.get("seen", ())) if isinstance(context, Mapping) else set()
        scores = self._reader_matrix[row] @ self._item_matrix.T
        candidates = [
            Candidate(item_id, float(scores[col]), self.name)
            for col, item_id in enumerate(self._item_ids)
            if item_id not in seen
        ]
        return self._finish(candidates, k)
