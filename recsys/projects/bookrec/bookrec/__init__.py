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

The U12 session-log loaders (plan recsys-014) — :func:`~bookrec.sessions.load_series` and
:func:`~bookrec.sessions.load_train_sequences` (ordered train-positive histories) — are stdlib-only.
"""

from __future__ import annotations

from bookrec.ann import AnnRetrievalPath, HnswIndex
from bookrec.blend import blend
from bookrec.catalog import Book, load_catalog
from bookrec.data import generated_dir
from bookrec.diversity import (
    catalog_coverage,
    head_ids_from_counts,
    head_share,
    intra_list_diversity,
    novelty,
)
from bookrec.embeddings import (
    GloveSubset,
    SemanticEmbeddingRetrievalPath,
    book_embedding,
    load_glove_subset,
)
from bookrec.evaluate import hit_rate_at_k, ndcg_at_k, precision_at_k, recall_at_k
from bookrec.factorization import MatrixFactorizationPath
from bookrec.feature_tower import FeatureTowerRetrievalPath
from bookrec.hybrid import HybridRetrievalPath
from bookrec.keywords import load_keywords
from bookrec.lexical import (
    BM25Index,
    LexicalRetrievalPath,
    cosine_similarity,
    tfidf_matrix,
)
from bookrec.neighborhood import ItemItemRetrievalPath, item_item_cosine
from bookrec.popularity import PopularityRetrievalPath, weighted_rating
from bookrec.protocol import (
    Candidate,
    RetrievalPath,
    calibrate_scores,
    order_candidates,
)
from bookrec.rank import rank
from bookrec.registry import DuplicatePathError, PathRegistry
from bookrec.rerank import NeuralRerankerPath, RerankerModel, rerank
from bookrec.scoreboard import (
    BlendedScoreboardResult,
    RandomRetrievalPath,
    ScoreboardResult,
    run_blended_scoreboard,
    run_validation_scoreboard,
)
from bookrec.search import search_catalog
from bookrec.sessions import load_series, load_train_sequences
from bookrec.two_tower import TwoTowerRetrievalPath

__all__ = [
    "AnnRetrievalPath",
    "BM25Index",
    "BlendedScoreboardResult",
    "Book",
    "Candidate",
    "DuplicatePathError",
    "FeatureTowerRetrievalPath",
    "GloveSubset",
    "HnswIndex",
    "HybridRetrievalPath",
    "ItemItemRetrievalPath",
    "LexicalRetrievalPath",
    "MatrixFactorizationPath",
    "NeuralRerankerPath",
    "PathRegistry",
    "PopularityRetrievalPath",
    "RandomRetrievalPath",
    "RerankerModel",
    "RetrievalPath",
    "ScoreboardResult",
    "SemanticEmbeddingRetrievalPath",
    "TwoTowerRetrievalPath",
    "blend",
    "book_embedding",
    "calibrate_scores",
    "catalog_coverage",
    "cosine_similarity",
    "generated_dir",
    "head_ids_from_counts",
    "head_share",
    "hit_rate_at_k",
    "intra_list_diversity",
    "item_item_cosine",
    "load_catalog",
    "load_glove_subset",
    "load_keywords",
    "load_series",
    "load_train_sequences",
    "ndcg_at_k",
    "novelty",
    "order_candidates",
    "precision_at_k",
    "rank",
    "recall_at_k",
    "rerank",
    "run_blended_scoreboard",
    "run_validation_scoreboard",
    "search_catalog",
    "tfidf_matrix",
    "weighted_rating",
]
