"""Unit 9: the **feature tower** — a two-tower whose item side is built from content (design 011 §8).

Unit 8's :class:`~bookrec.two_tower.TwoTowerRetrievalPath` gives every catalog item a bare learned
per-id :class:`torch.nn.Embedding` row. That row is only informative for an item the training log
has *interacted with*: a **cold item** (zero train positives) never appears as a positive, and under
Unit 8's uniform-over-the-full-catalog negative sampler it is only ever sampled as a **negative**, so
its id row is pushed down and the item is buried (measured cold-coverage exactly 0). The ID-only
two-tower and item-item CF therefore reach cold items at ~0.

The **feature tower** keeps the two-tower's reader-tower / item-tower dot-product model but rebuilds
the **item tower from what the book IS**, combining four signals to the shared ``embedding_dim``:

- a learned per-id :class:`torch.nn.Embedding` (the Unit-8 collaborative row);
- a learned **genre** embedding, mean-pooled over the book's genres;
- a learned **author** embedding;
- a learned :class:`torch.nn.Linear` **projection of the book's Unit-7 GloVe keyword vector**.

The reader tower stays a bare id embedding; the score is still ``reader_emb . item_emb``. Because the
genre / author / GloVe-projection parameters are shared across all books and trained from the **warm**
items, a cold book inherits a sensible vector from its features even though its own id row only ever
receives negative gradients — so the feature tower is the **first learned-taste / collaborative path to surface cold items
while holding near the book's best warm hit** (a warm/cold *compromise*, not dominance: content paths
like Unit 7 already serve cold items freely, they just ignore the interaction log).

**The decisive design choice is the negative pool.** 41% of the catalog is zero-train, so Unit 8's
``negative_pool="full"`` sampler (uniform over the whole catalog) makes a cold item negatives-only and
the tower suppresses it hard — not categorically (full-catalog still surfaces 39 of the 818 cold books),
but features can only weakly counter an item's own negative gradient. The
shipped default ``negative_pool="warm"`` draws negatives **only from the train-positive (warm) item
universe**, so a cold item is never a negative and its features place it. ``negative_pool="hard"``
(popularity-weighted over the same warm universe) is the **ablation** knob — measured it *trades* warm
accuracy for cold reach rather than sharpening both, and it risks sampling a true (unobserved)
positive as a negative. ``"full"`` is kept to teach the failure mode (it reproduces Unit 8's sampler
on the feature architecture: cold reach collapses and warm sags).

**Determinism / torch isolation (design 011 §7, exactly Unit 8's contract).** torch is imported
**lazily, inside** :meth:`fit` **only**; training seeds :func:`torch.manual_seed`, enables
:func:`torch.use_deterministic_algorithms` and pins :func:`torch.set_num_threads` to 1, **saving and
restoring** the last two process-global knobs in a ``finally`` block. :meth:`fit` composes the FULL
item tower once at the end and stores it — together with the reader tower — as plain **numpy**
matrices, so :meth:`retrieve`, :meth:`load` and :meth:`artifact` never import torch and never need to
re-compose the towers. The determinism gate is tolerance / ranking based (identical top-k ranking +
``allclose``), never exact-float.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
from typing import Any

import numpy as np

from bookrec.catalog import Book
from bookrec.embeddings import GloveSubset, book_embedding
from bookrec.lexical import tokenize
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


def _book_genres(book: Book) -> list[str]:
    """The book's genre tokens, parsed from the catalog's ``;``-joined ``genres`` field."""
    raw = str(book.fields.get("genres", "")) if isinstance(book.fields, Mapping) else ""
    return [g for g in (part.strip() for part in raw.split(";")) if g]


def _book_author(book: Book) -> str:
    """The book's author id as a stable string key (the catalog's ``author_id`` field)."""
    return str(book.fields.get("author_id", "")) if isinstance(book.fields, Mapping) else ""


class FeatureTowerRetrievalPath(BaseRetrievalPath):
    """Two-tower retrieval whose item tower is built from id + genre + author + GloVe features.

    Features arrive through the **constructor** (exactly like
    :class:`~bookrec.embeddings.SemanticEmbeddingRetrievalPath`): the catalog ``Book`` records (for
    genre / author), the per-book keyword text and the GloVe subset (for the keyword vector). That
    keeps ``fit(interactions, catalog=None)`` at the exact :class:`~bookrec.protocol.RetrievalPath`
    signature — ``catalog`` is an iterable of item **ids**, never ``Book`` records.

    :meth:`fit` trains the reader tower and the feature item tower by **BPR** (Adam + weight decay,
    torch imported lazily here); it composes the full item tower once and stores it with the reader
    tower as **numpy** matrices, so :meth:`retrieve` / :meth:`load` / :meth:`artifact` are torch-free.
    Every catalog item — cold items included — gets a feature-based row, so retrieval can surface a
    book with zero interaction history.
    """

    def __init__(
        self,
        catalog_books: Mapping[int, Book] | Iterable[Book],
        keywords: Mapping[int, str],
        glove: GloveSubset,
        *,
        embedding_dim: int = 32,
        n_epochs: int = 40,
        learning_rate: float = 0.01,
        n_negatives: int = 10,
        batch_size: int = 256,
        weight_decay: float = 1e-4,
        negative_pool: str = "warm",
        seed: int = 0,
        name: str = "feature-tower",
        version: str = "1",
    ) -> None:
        super().__init__(name=name, version=version)
        if isinstance(catalog_books, Mapping):
            books = {int(i): b for i, b in catalog_books.items()}
        else:
            books = {int(b.item_id): b for b in catalog_books}
        if not books:
            raise ValueError("FeatureTowerRetrievalPath needs a non-empty catalog of books")
        if not keywords:
            raise ValueError("FeatureTowerRetrievalPath needs a non-empty keyword corpus")
        self._books: dict[int, Book] = books
        self._keywords: dict[int, str] = {int(i): str(text) for i, text in keywords.items()}
        self._glove = glove
        self.embedding_dim = _positive_int(embedding_dim, "embedding_dim")
        self.n_epochs = _positive_int(n_epochs, "n_epochs")
        self.learning_rate = _positive_float(learning_rate, "learning_rate")
        self.n_negatives = _positive_int(n_negatives, "n_negatives")
        self.batch_size = _positive_int(batch_size, "batch_size")
        # weight_decay = 0 is a VALID (overfitting-demo) config, so it is non-negative, not positive.
        self.weight_decay = _nonnegative_float(weight_decay, "weight_decay")
        if negative_pool not in ("warm", "full", "hard"):
            raise ValueError(
                f"negative_pool must be 'warm' (train-positive universe), 'full' (the whole "
                f"catalog, Unit 8's sampler / failure mode) or 'hard' (popularity-weighted over "
                f"the warm universe), got {negative_pool!r}"
            )
        self.negative_pool = negative_pool
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise TypeError(f"seed must be an int, got {seed!r}")
        self.seed = seed
        self._reader_ids: list[int] = []
        self._item_ids: list[int] = []
        self._reader_of: dict[int, int] = {}
        self._row_of: dict[int, int] = {}
        self._reader_matrix: np.ndarray | None = None  # (n_readers, dim) float32
        self._item_matrix: np.ndarray | None = None  # (n_books, dim) float32 — COMPOSED tower
        self._loss_history: list[float] = []

    # --------------------------------------------------------------------------- feature tables
    def _feature_tables(
        self, item_ids: list[int]
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
        """Build the per-item feature tables (genre multi-hot, author index, GloVe keyword matrix).

        Returns ``(genre_multihot, author_row, glove_matrix, n_authors)``. The genre and author
        vocabularies are derived from the catalog books themselves (sorted for determinism), so the
        module never imports the dataset generator.
        """
        genre_vocab = sorted({g for i in item_ids for g in _book_genres(self._books[i])})
        author_vocab = sorted({_book_author(self._books[i]) for i in item_ids})
        genre_index = {g: j for j, g in enumerate(genre_vocab)}
        author_index = {a: j for j, a in enumerate(author_vocab)}

        n_items = len(item_ids)
        genre_multihot = np.zeros((n_items, max(1, len(genre_vocab))), dtype=np.float32)
        author_row = np.zeros(n_items, dtype=np.int64)
        glove_matrix = np.zeros((n_items, self._glove.dim), dtype=np.float32)
        for row, item_id in enumerate(item_ids):
            book = self._books[item_id]
            for g in _book_genres(book):
                genre_multihot[row, genre_index[g]] = 1.0
            author_row[row] = author_index[_book_author(book)]
            glove_matrix[row] = book_embedding(
                tokenize(self._keywords.get(item_id, "")), self._glove
            )
        return genre_multihot, author_row, glove_matrix, max(1, len(author_vocab))

    # ----------------------------------------------------------------------------- training
    def fit(
        self, interactions: Iterable[Mapping[str, Any]], catalog: Any | None = None
    ) -> FeatureTowerRetrievalPath:
        """Train the reader tower + feature item tower by BPR from the log's **train positives**.

        ``interactions`` is an iterable of row mappings (``reader_id, item_id, split, label``); only
        ``split == "train"`` **and** ``label == 1`` rows are training positives (leakage safety).
        ``catalog`` (optional) is an iterable of item **ids** restricting the item universe to known
        items that have a catalog ``Book`` record; without it the universe is every constructor book
        (so cold items are present and get a feature row). **Readers** are those with >= 1 train
        positive. **Negatives** are drawn from the train-positive (warm) universe per
        :attr:`negative_pool`. torch is imported here (the only place this module needs it); training
        is deterministic under ``seed``. Raises :class:`ValueError` on an empty fit.
        """
        import torch  # LAZY: torch is needed only to train; retrieve/load/artifact stay torch-free.

        if catalog is not None:
            known = {int(item_id) for item_id in catalog}
            item_ids = sorted(i for i in self._books if i in known)
        else:
            item_ids = sorted(self._books)
        if not item_ids:
            raise ValueError("FeatureTowerRetrievalPath.fit: no catalog books to build a tower from")
        item_set = set(item_ids)
        row_of = {item: idx for idx, item in enumerate(item_ids)}
        n_books = len(item_ids)

        pos_pairs: list[tuple[int, int]] = []
        reader_positives: dict[int, set[int]] = defaultdict(set)
        item_pos_count = np.zeros(n_books, dtype=np.float64)
        for row in interactions:
            if row["split"] != "train" or int(row["label"]) != 1:
                continue
            item_id = int(row["item_id"])
            if item_id not in item_set:
                continue
            reader_id = int(row["reader_id"])
            pos_pairs.append((reader_id, item_id))
            reader_positives[reader_id].add(item_id)
            item_pos_count[row_of[item_id]] += 1.0
        if not pos_pairs:
            raise ValueError(
                "FeatureTowerRetrievalPath.fit found no positive train interactions to train from"
            )
        reader_ids = sorted(reader_positives)
        reader_of = {reader: idx for idx, reader in enumerate(reader_ids)}
        n_readers = len(reader_ids)

        # The WARM universe: the rows that have >= 1 train positive. Cold items (zero train positives)
        # are DELIBERATELY excluded from the "warm"/"hard" negative pools so their features can place
        # them; "full" uses the whole catalog (Unit 8's sampler / the taught failure mode).
        warm_rows = np.flatnonzero(item_pos_count > 0).astype(np.int64)
        if warm_rows.size == 0:  # pragma: no cover - guarded by the no-positives check above
            raise ValueError("FeatureTowerRetrievalPath.fit: no warm items to sample negatives from")
        if self.negative_pool == "full":
            pool_rows = np.arange(n_books, dtype=np.int64)
            pool_probs = None
        elif self.negative_pool == "hard":  # popularity-weighted over the warm universe
            pool_rows = warm_rows
            pool_weights = item_pos_count[warm_rows]
            pool_probs = pool_weights / pool_weights.sum()
        else:  # "warm": uniform over the warm universe
            pool_rows = warm_rows
            pool_probs = None

        pos_r = np.array([reader_of[r] for r, _ in pos_pairs], dtype=np.int64)
        pos_i = np.array([row_of[i] for _, i in pos_pairs], dtype=np.int64)

        # A reader whose positives cover the WHOLE negative pool has no legal negative, so its BPR
        # triples are dropped (inert on the shipped data; guards tiny fixtures from a spin-forever
        # collision loop — exactly Unit 8's guard, generalised to the chosen pool).
        pool_set = set(pool_rows.tolist())
        full_coverage = {
            reader_of[r]
            for r, items in reader_positives.items()
            if pool_set.issubset({row_of[i] for i in items})
        }
        triple_r = np.repeat(pos_r, self.n_negatives)
        triple_pos = np.repeat(pos_i, self.n_negatives)
        if full_coverage:
            keep = np.array([r not in full_coverage for r in triple_r.tolist()])
            triple_r = triple_r[keep]
            triple_pos = triple_pos[keep]
        n_triples = int(triple_r.shape[0])
        if n_triples == 0:
            raise ValueError(
                "FeatureTowerRetrievalPath.fit: every reader covers the whole warm universe, so no "
                "sampled negative exists to form a BPR triple"
            )
        observed_codes = np.array(
            sorted({reader_of[r] * n_books + row_of[it] for r, it in pos_pairs}), dtype=np.int64
        )

        genre_multihot, author_row, glove_matrix, n_authors = self._feature_tables(item_ids)
        n_genres = genre_multihot.shape[1]

        rng = np.random.default_rng(self.seed)

        def _sample_negatives(size: int) -> np.ndarray:
            if pool_probs is not None:
                return rng.choice(pool_rows, size=size, p=pool_probs)
            return pool_rows[rng.integers(0, pool_rows.size, size=size)]

        # Save the PROCESS-GLOBAL determinism knobs and restore them in finally (Unit 8's contract).
        prev_deterministic = torch.are_deterministic_algorithms_enabled()
        prev_threads = torch.get_num_threads()
        try:
            torch.use_deterministic_algorithms(True)
            torch.set_num_threads(1)
            torch.manual_seed(self.seed)

            reader_tower = torch.nn.Embedding(n_readers, self.embedding_dim)
            item_id_tower = torch.nn.Embedding(n_books, self.embedding_dim)
            genre_tower = torch.nn.Embedding(n_genres, self.embedding_dim)
            author_tower = torch.nn.Embedding(n_authors, self.embedding_dim)
            glove_proj = torch.nn.Linear(self._glove.dim, self.embedding_dim)
            for emb in (reader_tower, item_id_tower, genre_tower, author_tower):
                torch.nn.init.normal_(emb.weight, mean=0.0, std=0.1)
            torch.nn.init.normal_(glove_proj.weight, mean=0.0, std=0.1)
            torch.nn.init.zeros_(glove_proj.bias)

            genre_mh_t = torch.from_numpy(genre_multihot)  # (n_books, n_genres)
            genre_counts_t = torch.from_numpy(
                np.maximum(genre_multihot.sum(axis=1, keepdims=True), 1.0).astype(np.float32)
            )
            author_row_t = torch.from_numpy(author_row)  # (n_books,) long
            glove_t = torch.from_numpy(glove_matrix)  # (n_books, glove_dim)

            def item_vectors(rows: torch.Tensor) -> torch.Tensor:
                """Compose the item tower for the given item rows: id + genre + author + GloVe."""
                id_vec = item_id_tower(rows)
                genre_vec = (genre_mh_t[rows] @ genre_tower.weight) / genre_counts_t[rows]
                author_vec = author_tower(author_row_t[rows])
                glove_vec = glove_proj(glove_t[rows])
                return id_vec + genre_vec + author_vec + glove_vec

            optimizer = torch.optim.Adam(
                list(reader_tower.parameters())
                + list(item_id_tower.parameters())
                + list(genre_tower.parameters())
                + list(author_tower.parameters())
                + list(glove_proj.parameters()),
                lr=self.learning_rate,
                weight_decay=self.weight_decay,
            )

            self._loss_history = []
            for _ in range(self.n_epochs):
                neg = _sample_negatives(n_triples)
                collide = np.isin(triple_r * n_books + neg, observed_codes)
                while collide.any():
                    neg[collide] = _sample_negatives(int(collide.sum()))
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
                    s_pos = (reader_vec * item_vectors(bp)).sum(dim=1)
                    s_neg = (reader_vec * item_vectors(bn)).sum(dim=1)
                    loss = -torch.nn.functional.logsigmoid(s_pos - s_neg).mean()
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    epoch_loss += loss.item()
                    n_batches += 1
                self._loss_history.append(epoch_loss / n_batches)

            # Compose the FULL item tower ONCE and store it as numpy — retrieve/load/artifact then
            # need neither torch nor the sub-embeddings (the composed matrix IS the item tower).
            with torch.no_grad():
                all_rows = torch.arange(n_books)
                item_matrix = item_vectors(all_rows).detach().numpy().astype(np.float32).copy()
            reader_matrix = reader_tower.weight.detach().numpy().astype(np.float32).copy()
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
    def load(self, artifact: Mapping[str, Any]) -> FeatureTowerRetrievalPath:
        """Restore a fitted path from its :meth:`artifact` state (numpy only — never imports torch).

        The matrices are copied (never aliased) so a later mutation of the artifact dict cannot reach
        into the loaded path.
        """
        state = dict(artifact)
        reader_ids = [int(r) for r in state["reader_ids"]]
        item_ids = [int(i) for i in state["item_ids"]]
        reader_matrix = np.array(state["reader_embeddings"], dtype=np.float32)
        item_matrix = np.array(state["item_embeddings"], dtype=np.float32)
        if reader_matrix.shape != (len(reader_ids), item_matrix.shape[1]):
            raise ValueError(
                f"FeatureTowerRetrievalPath.load: reader-embedding shape {reader_matrix.shape} "
                f"does not match ({len(reader_ids)}, embedding_dim) for the restored reader_ids"
            )
        if item_matrix.shape != (len(item_ids), reader_matrix.shape[1]):
            raise ValueError(
                f"FeatureTowerRetrievalPath.load: item-embedding shape {item_matrix.shape} does not "
                f"match ({len(item_ids)}, embedding_dim) for the restored item_ids"
            )
        params = dict(state.get("params", {}))
        for key in ("embedding_dim", "n_epochs", "n_negatives", "batch_size", "seed"):
            if key in params:
                setattr(self, key, int(params[key]))
        for key in ("learning_rate", "weight_decay"):
            if key in params:
                setattr(self, key, float(params[key]))
        if "negative_pool" in params:
            self.negative_pool = str(params["negative_pool"])
        self._reader_ids = reader_ids
        self._item_ids = item_ids
        self._reader_of = {reader: idx for idx, reader in enumerate(reader_ids)}
        self._row_of = {item: idx for idx, item in enumerate(item_ids)}
        self._reader_matrix = reader_matrix
        self._item_matrix = item_matrix
        self._fitted = True
        return self

    def artifact(self) -> dict[str, Any]:
        """The fitted state this path owns and versions: the COMPOSED numpy towers + ids + params.

        Numpy only — ``item_embeddings`` is the already-composed item tower (id + genre + author +
        GloVe), so a restored path runs :meth:`retrieve` without importing torch or re-composing.
        """
        if self._reader_matrix is None or self._item_matrix is None:
            raise RuntimeError("FeatureTowerRetrievalPath.artifact before fit/load")
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
                "negative_pool": self.negative_pool,
                "seed": self.seed,
            },
        }

    @property
    def reader_embeddings(self) -> np.ndarray:
        """A copy of the learned reader-tower matrix (readers x embedding_dim)."""
        if self._reader_matrix is None:
            raise RuntimeError("FeatureTowerRetrievalPath.reader_embeddings before fit/load")
        return self._reader_matrix.copy()

    @property
    def item_embeddings(self) -> np.ndarray:
        """A copy of the COMPOSED item-tower matrix (items x embedding_dim)."""
        if self._item_matrix is None:
            raise RuntimeError("FeatureTowerRetrievalPath.item_embeddings before fit/load")
        return self._item_matrix.copy()

    @property
    def loss_history(self) -> list[float]:
        """Mean BPR loss per epoch from the last :meth:`fit` (empty after :meth:`load`)."""
        return list(self._loss_history)

    # ------------------------------------------------------------------------------ retrieval
    def retrieve(self, query: Any, context: Any, k: int) -> list[Candidate]:
        """Top ``k`` unseen books for a fitted reader by ``reader_emb . item_emb^T`` (torch-free).

        Scored with the **numpy** composed towers stored at fit — no torch import. A fitted reader is
        scored over ALL catalog items (cold items included — they carry a feature-based row)
        regardless of whether ``context["seen"]`` is empty; ``seen`` only excludes already-read books,
        and stale ``seen`` ids absent from the catalog are ignored. A reader with no learned embedding
        (unknown / cold reader, 0 train positives) returns ``[]``.
        """
        if self._reader_matrix is None or self._item_matrix is None:
            raise RuntimeError("FeatureTowerRetrievalPath.retrieve before fit/load")
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
