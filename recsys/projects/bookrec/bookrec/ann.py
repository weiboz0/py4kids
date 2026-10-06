"""Unit 10: approximate nearest-neighbour (ANN) retrieval over a dense path (design 011 §7/§8).

Every dense path so far — Unit 7 semantic cosine, Unit 8 two-tower, Unit 9 feature tower — retrieves
by scoring *all* catalog items by brute force (``reader_emb . item_emb^T`` then an argsort). That is
**linear in the catalog**: fine at 2,000 books, hopeless at a million. This module teaches the
**exact brute-force baseline vs an approximate index** and the **recall/speed trade**:

- :class:`HnswIndex` — a thin wrapper over a FAISS **HNSW** (Hierarchical Navigable Small World)
  graph index built over a dense item matrix. It is built **`IndexHNSWFlat(d, M, METRIC_INNER_PRODUCT)``**
  — inner product, **not** the FAISS default L2 — so it ranks the **same ``reader . item`` dot product**
  the dense paths use (an L2 index would rank differently and recall-vs-exact would be meaningless).
- :class:`AnnRetrievalPath` — a :class:`~bookrec.protocol.BaseRetrievalPath` that wraps an
  already-fit dense path (its item matrix + reader vectors) and answers ``retrieve`` by an
  **approximate** index search instead of the exact full scan. ANN is a **speed** technique that
  *preserves* accuracy (its hit@k matches the exact path); the speed win is **asymptotic** (no
  meaningful speedup at 2,000 items — it shows at tens of thousands).

**Determinism (design 011 §7/§184).** ``faiss.omp_set_num_threads(1)`` is **process-global** — exactly
like :func:`torch.set_num_threads` in :mod:`bookrec.two_tower` — so every FAISS call here **saves and
restores** the previous thread count in a ``finally`` block (via :func:`faiss.omp_get_max_threads`). A
single-threaded HNSW build with a fixed insertion order is reproducible: two builds give **identical**
neighbour ids and ``allclose`` scores. The gate is recall-vs-exact + that reproducibility, **never**
exact neighbour identity against the brute force (ANN is approximate by construction).

**faiss is imported LAZILY, inside the build / search / load surface only** — this module has NO
top-level ``import faiss``. Importing :mod:`bookrec` (and this module) therefore never pulls FAISS;
FAISS is confined to the index operations, exactly as torch is confined to ``two_tower.fit`` (proven
by an import-blocked subprocess test). The **exact brute-force reference** for recall / latency is
simply the wrapped dense path's own numpy ``retrieve`` (argsort over the same item.reader scores).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from bookrec.protocol import BaseRetrievalPath, Candidate


def _positive_int(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} must be a positive int, got {value!r}")
    return value


def _as_item_matrix(items: Any) -> np.ndarray:
    """Coerce an item matrix to a 2-D, C-contiguous ``float32`` array (what FAISS requires)."""
    matrix = np.ascontiguousarray(np.asarray(items, dtype=np.float32))
    if matrix.ndim != 2:
        raise ValueError(f"item matrix must be 2-D (n_items, dim), got shape {matrix.shape}")
    return matrix


class HnswIndex:
    """A thin FAISS HNSW wrapper over a dense item matrix, ranking by **inner product**.

    The index is built ``IndexHNSWFlat(dim, M, faiss.METRIC_INNER_PRODUCT)`` with
    ``efConstruction`` pinned, single-threaded and deterministic. :meth:`search` ranks query vectors
    by the **same ``query . item`` dot product** a dense path's exact scan uses, so recall-vs-exact is
    meaningful. ``faiss`` is imported lazily inside :meth:`_build` / :meth:`search`, and every FAISS
    call saves and restores the process-global thread count in a ``finally`` block.

    The item matrix, aligned item ids and the pinned ``M`` / ``efConstruction`` are retained so
    :meth:`artifact` / :meth:`load` rebuild an identical single-threaded index without depending on
    FAISS at import time.
    """

    def __init__(
        self,
        items: Any,
        ids: Any,
        *,
        m: int = 32,
        ef_construction: int = 200,
    ) -> None:
        matrix = _as_item_matrix(items)
        id_list = [int(i) for i in ids]
        if matrix.shape[0] != len(id_list):
            raise ValueError(
                f"item matrix has {matrix.shape[0]} rows but {len(id_list)} ids were given"
            )
        self.m = _positive_int(m, "m")
        self.ef_construction = _positive_int(ef_construction, "ef_construction")
        self._items = matrix
        self._ids = id_list
        self._dim = int(matrix.shape[1])
        self._index = self._build(matrix)

    def _build(self, items: np.ndarray) -> Any:
        """Build the single-threaded inner-product HNSW index (faiss imported lazily here)."""
        import faiss  # LAZY: FAISS is needed only to build/search; module import stays FAISS-free.

        prev_threads = faiss.omp_get_max_threads()  # process-global, like torch.set_num_threads
        try:
            faiss.omp_set_num_threads(1)
            index = faiss.IndexHNSWFlat(self._dim, self.m, faiss.METRIC_INNER_PRODUCT)
            index.hnsw.efConstruction = self.ef_construction
            index.add(items)
        finally:
            faiss.omp_set_num_threads(prev_threads)
        return index

    def search(self, queries: Any, k: int, efSearch: int = 64) -> tuple[np.ndarray, np.ndarray]:
        """Approximate top-``k`` neighbours of each query row: ``(labels, scores)``.

        ``labels`` are the row positions into the added item matrix (``-1`` pads a row that found
        fewer than ``k`` neighbours); ``scores`` are the inner products FAISS returns, already sorted
        descending. ``efSearch`` is the recall/speed knob — higher explores more of the graph
        (higher recall, slower). Single-threaded and deterministic (thread count restored in
        ``finally``).
        """
        import faiss  # LAZY: confined to the search surface.

        k = _positive_int(k, "k")
        _positive_int(efSearch, "efSearch")
        q = _as_item_matrix(queries)
        prev_threads = faiss.omp_get_max_threads()
        try:
            faiss.omp_set_num_threads(1)
            self._index.hnsw.efSearch = int(efSearch)
            scores, labels = self._index.search(q, k)  # FAISS returns (distances/scores, ids)
        finally:
            faiss.omp_set_num_threads(prev_threads)
        return labels, scores

    @property
    def ids(self) -> list[int]:
        """The item ids aligned to the index rows (a copy)."""
        return list(self._ids)

    @property
    def items(self) -> np.ndarray:
        """A copy of the indexed item matrix (``float32``)."""
        return self._items.copy()

    @property
    def size(self) -> int:
        """The number of indexed items."""
        return len(self._ids)

    def artifact(self) -> dict[str, Any]:
        """The state needed to rebuild an identical single-threaded index (numpy + pinned params)."""
        return {
            "items": self._items.copy(),
            "ids": list(self._ids),
            "m": self.m,
            "ef_construction": self.ef_construction,
        }

    @classmethod
    def load(cls, artifact: Mapping[str, Any]) -> HnswIndex:
        """Rebuild an index from its :meth:`artifact` state (copies the matrix; never aliases it)."""
        state = dict(artifact)
        return cls(
            np.array(state["items"], dtype=np.float32),
            [int(i) for i in state["ids"]],
            m=int(state["m"]),
            ef_construction=int(state["ef_construction"]),
        )


class AnnRetrievalPath(BaseRetrievalPath):
    """Approximate retrieval over an already-fit dense path's item matrix via a FAISS HNSW index.

    The dense source arrives through the **constructor** (exactly like Unit 9's feature-constructor
    pattern) and must already be fit, exposing — through its ``artifact()`` — an item matrix, reader
    vectors and their ids in **one inner-product space** (e.g.
    :class:`~bookrec.two_tower.TwoTowerRetrievalPath`). :meth:`fit` builds the HNSW index over that
    item matrix (keeping the exact ``fit(interactions, catalog=None)`` protocol signature;
    ``interactions`` / ``catalog`` are ignored — the dense source is already trained). :meth:`retrieve`
    scores a reader by its dense vector, **over-fetching ``min(n_items, k + len(seen))``** neighbours
    from the index *before* excluding ``context["seen"]`` (so a heavy reader still gets ``k`` unseen
    recommendations), and returns the top ``k``. An unknown reader (no dense vector) returns ``[]``.

    ANN is a **speed** technique, not an accuracy one: at a high ``efSearch`` its top-``k`` matches
    the exact dense scan's at high recall, so its hit@k equals the exact path's. The exact brute-force
    reference (for recall / latency) is simply the wrapped dense path's own numpy ``retrieve``.
    """

    def __init__(
        self,
        dense_path: Any,
        efSearch: int = 64,
        m: int = 32,
        ef_construction: int = 200,
        *,
        name: str = "ann",
        version: str = "1",
    ) -> None:
        super().__init__(name=name, version=version)
        self._dense = dense_path
        self.efSearch = _positive_int(efSearch, "efSearch")
        self.m = _positive_int(m, "m")
        self.ef_construction = _positive_int(ef_construction, "ef_construction")
        self._index: HnswIndex | None = None
        self._item_ids: list[int] = []
        self._reader_ids: list[int] = []
        self._reader_of: dict[int, int] = {}
        self._reader_matrix: np.ndarray | None = None

    def fit(self, interactions: Any, catalog: Any | None = None) -> AnnRetrievalPath:
        """Build the HNSW index over the (already-fit) dense source's item matrix.

        ``interactions`` / ``catalog`` are ignored (the dense source is trained in its own ``fit``);
        the signature is kept exactly for protocol substitutability. The dense source's item matrix,
        reader matrix and ids are read from its ``artifact()`` (all public), so this path never
        reaches into the dense path's private state.
        """
        del interactions, catalog
        art = self._dense.artifact()
        self._item_ids = [int(i) for i in art["item_ids"]]
        self._reader_ids = [int(r) for r in art["reader_ids"]]
        self._reader_of = {reader: idx for idx, reader in enumerate(self._reader_ids)}
        self._reader_matrix = np.ascontiguousarray(
            np.asarray(art["reader_embeddings"], dtype=np.float32)
        )
        item_matrix = _as_item_matrix(art["item_embeddings"])
        self._index = HnswIndex(
            item_matrix, self._item_ids, m=self.m, ef_construction=self.ef_construction
        )
        self._fitted = True
        return self

    def load(self, artifact: Mapping[str, Any]) -> AnnRetrievalPath:
        """Restore a fitted path from its :meth:`artifact` (rebuilds the index; no dense path needed).

        The index is rebuilt single-threaded from the stored item matrix, so a loaded path serves
        ``retrieve`` identically to the original without the dense source object. Arrays are copied.
        """
        state = dict(artifact)
        self._index = HnswIndex.load(state["index"])
        self._item_ids = [int(i) for i in state["item_ids"]]
        self._reader_ids = [int(r) for r in state["reader_ids"]]
        self._reader_of = {reader: idx for idx, reader in enumerate(self._reader_ids)}
        self._reader_matrix = np.array(state["reader_embeddings"], dtype=np.float32)
        params = dict(state.get("params", {}))
        for key in ("efSearch", "m", "ef_construction"):
            if key in params:
                setattr(self, key, int(params[key]))
        self._fitted = True
        return self

    def artifact(self) -> dict[str, Any]:
        """The fitted state this path owns and versions (the index rebuild state + reader vectors)."""
        if self._index is None or self._reader_matrix is None:
            raise RuntimeError("AnnRetrievalPath.artifact before fit/load")
        return {
            "index": self._index.artifact(),
            "reader_embeddings": self._reader_matrix.copy(),
            "reader_ids": list(self._reader_ids),
            "item_ids": list(self._item_ids),
            "params": {
                "efSearch": self.efSearch,
                "m": self.m,
                "ef_construction": self.ef_construction,
            },
        }

    @property
    def index(self) -> HnswIndex:
        """The fitted :class:`HnswIndex` (for recall / latency measurement)."""
        if self._index is None:
            raise RuntimeError("AnnRetrievalPath.index before fit/load")
        return self._index

    def retrieve(self, query: Any, context: Any, k: int) -> list[Candidate]:
        """Top ``k`` unseen books for a fitted reader by an **approximate** index search.

        Over-fetches ``min(n_items, k + len(seen))`` neighbours from the HNSW index before excluding
        ``context["seen"]`` — so even a reader who has read many of their top neighbours still gets
        ``k`` unseen recommendations (parity with the exact dense scan). A reader with no dense vector
        (unknown / cold) returns ``[]``.
        """
        if self._index is None or self._reader_matrix is None:
            raise RuntimeError("AnnRetrievalPath.retrieve before fit/load")
        if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
            raise ValueError(f"k must be a positive int, got {k!r}")
        try:
            reader_id = int(query)
        except (TypeError, ValueError):
            return []
        row = self._reader_of.get(reader_id)
        if row is None:  # no dense vector -> cold/unknown reader
            return []
        seen = set(context.get("seen", ())) if isinstance(context, Mapping) else set()
        n_items = len(self._item_ids)
        n_fetch = min(n_items, k + len(seen))
        reader_vec = self._reader_matrix[row][np.newaxis, :]
        labels, scores = self._index.search(reader_vec, n_fetch, efSearch=self.efSearch)
        labels, scores = labels[0], scores[0]
        candidates: list[Candidate] = []
        for label, score in zip(labels.tolist(), scores.tolist()):
            if label < 0:  # FAISS pads with -1 when fewer than n_fetch neighbours were found
                continue
            item_id = self._item_ids[label]
            if item_id in seen:
                continue
            candidates.append(Candidate(item_id, float(score), self.name))
        return self._finish(candidates, k)
