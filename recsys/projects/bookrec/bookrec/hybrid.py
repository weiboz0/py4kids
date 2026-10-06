"""Unit 10: hybrid retrieval — fusing a sparse (BM25) and a dense (two-tower) path (design 011 §8).

Unit 3's :class:`~bookrec.lexical.LexicalRetrievalPath` retrieves by **lexical** keyword overlap
(BM25); Unit 8's :class:`~bookrec.two_tower.TwoTowerRetrievalPath` retrieves by a **learned dense**
embedding dot product. They surface largely *different* books — lexical catches an on-the-nose
keyword match the dense tower ranks low, the dense tower catches a taste match no keyword shares.
:class:`HybridRetrievalPath` **fuses** the two candidate lists, extending Unit 6's score-blending
precedent (:func:`~bookrec.scoreboard.run_blended_scoreboard`) to a two-path sparse+dense hybrid.

Two fusion methods:

- ``"weighted"`` (the default) — each path's scores are **min-max normalised** over its own pool
  (so the paths are comparable), then fused ``weight * dense + (1 - weight) * sparse``. The default
  ``weight = 0.7`` is **dense-heavy** (the dense tower is the stronger path here).
- ``"rrf"`` — **reciprocal-rank fusion**: an item scores ``weight / (k0 + rank_dense) +
  (1 - weight) / (k0 + rank_sparse)`` (``k0 = 60``), using only *rank*, not raw score.

**Honest framing (design 011 §8, measured).** Hybrid is **not** a free win: the dense tower
dominates, and only a *tuned, dense-heavy* weighted fusion gives a **small** lift — on this data
``pool=50, weight=0.7`` edges the two-tower on both hit@10 (~0.362 vs 0.340) and catalog coverage
(~0.192 vs 0.177), but the gain is small, weight-sensitive (equal weights **hurt**) and RRF loses to
the two-tower alone. So the hybrid is a *modest, tuning-dependent complement*, not a new best.

Both sub-paths are **already fit** (supplied at construction); fusion is pure numpy over their
candidate lists, so this module imports neither torch nor faiss.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from bookrec.protocol import BaseRetrievalPath, Candidate, calibrate_scores


def _positive_int(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} must be a positive int, got {value!r}")
    return value


def _unit_float(value: object, name: str) -> float:
    number = float(value)  # type: ignore[arg-type]
    if not 0.0 <= number <= 1.0:
        raise ValueError(f"{name} must be in [0, 1], got {value!r}")
    return number


class HybridRetrievalPath(BaseRetrievalPath):
    """Fuse a sparse (BM25) and a dense (two-tower) path's candidates into one ranked list.

    ``sparse_path`` and ``dense_path`` are **already-fit** retrieval paths supplied at construction
    (exactly like Unit 9's feature-constructor pattern). :meth:`retrieve` asks **each** path for its
    top ``pool`` candidates (each path excludes ``context["seen"]`` in its own ``retrieve``, so the
    pools are over-fetched past ``seen``), fuses them by :attr:`method`, and returns the top ``k``.

    ``weight`` is the **dense** path's weight (``1 - weight`` goes to the sparse path); it must be in
    ``[0, 1]``. ``method`` is ``"weighted"`` (min-max-normalised weighted sum, the default) or
    ``"rrf"`` (reciprocal-rank fusion, ``k0 = 60``). The default ``pool = 50, weight = 0.7`` is the
    measured sweet spot. Deterministic; an empty / unknown query yields whatever the sub-paths yield.
    """

    def __init__(
        self,
        sparse_path: Any,
        dense_path: Any,
        weight: float = 0.7,
        pool: int = 50,
        method: str = "weighted",
        *,
        rrf_k0: int = 60,
        name: str = "hybrid",
        version: str = "1",
    ) -> None:
        super().__init__(name=name, version=version)
        if method not in ("weighted", "rrf"):
            raise ValueError(
                f"method must be 'weighted' (min-max weighted sum) or 'rrf' "
                f"(reciprocal-rank fusion), got {method!r}"
            )
        self._sparse = sparse_path
        self._dense = dense_path
        self.weight = _unit_float(weight, "weight")
        self.pool = _positive_int(pool, "pool")
        self.method = method
        self.rrf_k0 = _positive_int(rrf_k0, "rrf_k0")

    def fit(self, interactions: Any, catalog: Any | None = None) -> HybridRetrievalPath:
        """Both sub-paths are already fit, so this is a no-op that keeps the protocol signature.

        ``interactions`` / ``catalog`` are ignored (the sparse and dense paths are trained in their
        own ``fit``). Returns ``self`` so a hybrid is substitutable wherever a fitted path is used.
        """
        del interactions, catalog
        self._fitted = True
        return self

    def load(self, artifact: Mapping[str, Any]) -> HybridRetrievalPath:
        """Restore the fusion hyperparameters from :meth:`artifact`.

        The sub-paths are the construction-provided fitted components (like a lexical path's keyword
        corpus), so the artifact owns only the fusion state (``weight`` / ``pool`` / ``method`` /
        ``rrf_k0``); a loaded hybrid over the same sub-paths retrieves identically to the original.
        """
        params = dict(dict(artifact).get("params", {}))
        if "weight" in params:
            self.weight = _unit_float(params["weight"], "weight")
        if "pool" in params:
            self.pool = _positive_int(int(params["pool"]), "pool")
        if "method" in params:
            if params["method"] not in ("weighted", "rrf"):
                raise ValueError(f"method must be 'weighted' or 'rrf', got {params['method']!r}")
            self.method = str(params["method"])
        if "rrf_k0" in params:
            self.rrf_k0 = _positive_int(int(params["rrf_k0"]), "rrf_k0")
        self._fitted = True
        return self

    def artifact(self) -> dict[str, Any]:
        """The fusion hyperparameters this path owns and versions (the sub-paths own their own)."""
        return {
            "params": {
                "weight": self.weight,
                "pool": self.pool,
                "method": self.method,
                "rrf_k0": self.rrf_k0,
            }
        }

    def retrieve(self, query: Any, context: Any, k: int) -> list[Candidate]:
        """Top ``k`` books from fusing the sparse and dense paths' top-``pool`` candidates.

        Each sub-path retrieves ``pool`` candidates (already excluding ``seen``); the two pools are
        fused by :attr:`method` over their union and the top ``k`` are returned. ``seen`` items are
        excluded defensively as well. Deterministic (the base class's score-then-id tie-break).
        """
        if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
            raise ValueError(f"k must be a positive int, got {k!r}")
        seen = set(context.get("seen", ())) if isinstance(context, Mapping) else set()
        sparse_c = self._sparse.retrieve(query, context, self.pool)
        dense_c = self._dense.retrieve(query, context, self.pool)
        if self.method == "rrf":
            fused = self._fuse_rrf(sparse_c, dense_c)
        else:
            fused = self._fuse_weighted(sparse_c, dense_c)
        candidates = [
            Candidate(item_id, score, self.name)
            for item_id, score in fused.items()
            if item_id not in seen
        ]
        return self._finish(candidates, k)

    def _fuse_weighted(
        self, sparse_c: list[Candidate], dense_c: list[Candidate]
    ) -> dict[int, float]:
        """Min-max normalise each path's pool, then ``weight*dense + (1-weight)*sparse`` over the union."""
        dense_norm = {c.item_id: c.score for c in calibrate_scores(dense_c)}
        sparse_norm = {c.item_id: c.score for c in calibrate_scores(sparse_c)}
        fused: dict[int, float] = {}
        for item_id in set(dense_norm) | set(sparse_norm):
            fused[item_id] = (
                self.weight * dense_norm.get(item_id, 0.0)
                + (1.0 - self.weight) * sparse_norm.get(item_id, 0.0)
            )
        return fused

    def _fuse_rrf(
        self, sparse_c: list[Candidate], dense_c: list[Candidate]
    ) -> dict[int, float]:
        """Weighted reciprocal-rank fusion: ``w/(k0+rank_dense) + (1-w)/(k0+rank_sparse)`` (1-based rank)."""
        dense_rank = {c.item_id: r for r, c in enumerate(dense_c, start=1)}
        sparse_rank = {c.item_id: r for r, c in enumerate(sparse_c, start=1)}
        fused: dict[int, float] = {}
        for item_id in set(dense_rank) | set(sparse_rank):
            score = 0.0
            if item_id in dense_rank:
                score += self.weight / (self.rrf_k0 + dense_rank[item_id])
            if item_id in sparse_rank:
                score += (1.0 - self.weight) / (self.rrf_k0 + sparse_rank[item_id])
            fused[item_id] = score
        return fused
