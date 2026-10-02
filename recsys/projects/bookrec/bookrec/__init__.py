"""bookrec — the cumulative book-recommender package.

This package grows unit by unit across *Applied Python: Recommendation Systems*.
The foundation (plan recsys-001) ships the stable substrate every later unit builds on:

- :class:`~bookrec.protocol.Candidate` and the :class:`~bookrec.protocol.RetrievalPath`
  protocol — the contract every retrieval path implements (stable int ids, ``fit``/``load``,
  ``retrieve(query, context, k)``, deterministic tie-break, calibrated scores, artifact
  ownership/versioning);
- :class:`~bookrec.registry.PathRegistry` — a name→path registry that rejects duplicates;
- :func:`~bookrec.blend.blend` — union + per-path calibrated-score merge;
- :func:`~bookrec.rank.rank` — order a candidate pool into recommendations;
- :func:`~bookrec.evaluate.hit_rate_at_k` and friends — the evaluation scoreboard;
- :func:`~bookrec.catalog.load_catalog` — load the gzip'd-CSV catalog slice.

Unit 2 (plan recsys-003) ships the first real learned/scored retrieval path:
:class:`~bookrec.popularity.PopularityRetrievalPath` (count ranking), the
:func:`~bookrec.popularity.weighted_rating` quality lens, and the popularity-bias metrics
:func:`~bookrec.diversity.catalog_coverage` / :func:`~bookrec.diversity.head_share`. Further real
retrieval paths (BM25, item-item, matrix factorisation, two-tower, …) land in later units.
"""

from __future__ import annotations

from bookrec.blend import blend
from bookrec.catalog import Book, load_catalog
from bookrec.data import generated_dir
from bookrec.diversity import catalog_coverage, head_ids_from_counts, head_share
from bookrec.evaluate import hit_rate_at_k, recall_at_k
from bookrec.popularity import PopularityRetrievalPath, weighted_rating
from bookrec.protocol import (
    Candidate,
    RetrievalPath,
    calibrate_scores,
    order_candidates,
)
from bookrec.rank import rank
from bookrec.registry import DuplicatePathError, PathRegistry
from bookrec.scoreboard import RandomRetrievalPath, ScoreboardResult, run_validation_scoreboard
from bookrec.search import search_catalog

__all__ = [
    "Book",
    "Candidate",
    "DuplicatePathError",
    "PathRegistry",
    "PopularityRetrievalPath",
    "RandomRetrievalPath",
    "RetrievalPath",
    "ScoreboardResult",
    "blend",
    "calibrate_scores",
    "catalog_coverage",
    "generated_dir",
    "head_ids_from_counts",
    "head_share",
    "hit_rate_at_k",
    "load_catalog",
    "order_candidates",
    "rank",
    "recall_at_k",
    "run_validation_scoreboard",
    "search_catalog",
    "weighted_rating",
]
