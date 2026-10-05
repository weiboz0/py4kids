"""The Unit 1 frozen-validation scoreboard and seeded random retrieval floor.

Unit 6 extends this module additively: :func:`run_validation_scoreboard` gains a ``split=`` param
(so Checkpoint A can score the sealed ``test`` holdout once) and reports precision@k / NDCG@k
alongside hit-rate / recall; :func:`run_blended_scoreboard` evaluates a *calibrated weighted blend*
of several paths (the first blended recommender) with hit@k and catalog coverage.
"""

from __future__ import annotations

import csv
import gzip
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from bookrec.blend import blend
from bookrec.diversity import catalog_coverage
from bookrec.evaluate import hit_rate_at_k, ndcg_at_k, precision_at_k, recall_at_k
from bookrec.protocol import BaseRetrievalPath, Candidate
from bookrec.rank import rank


class RandomRetrievalPath(BaseRetrievalPath):
    """A seeded baseline that samples candidates uniformly from unseen catalog items."""

    def __init__(self, item_ids: Iterable[int], seed: int = 0) -> None:
        super().__init__(name="random", version="1", _fitted=True)
        self.seed = seed
        self._items = tuple(sorted(set(item_ids)))
        if any(not isinstance(item_id, int) or isinstance(item_id, bool) for item_id in self._items):
            raise TypeError("random baseline item ids must be stable ints")
        self._rng = np.random.default_rng(self.seed)

    def fit(self, interactions: Any, catalog: Any | None = None) -> RandomRetrievalPath:
        del interactions, catalog
        return self

    def load(self, artifact: Any) -> RandomRetrievalPath:
        del artifact
        return self

    def retrieve(self, query: Any, context: Any, k: int) -> list[Candidate]:
        del query
        if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
            raise ValueError(f"k must be a positive int, got {k!r}")
        seen = set(context.get("seen", ())) if isinstance(context, Mapping) else set()
        unseen = [item_id for item_id in self._items if item_id not in seen]
        count = min(k, len(unseen))
        chosen = self._rng.choice(unseen, size=count, replace=False).tolist() if unseen else []
        candidates = [Candidate(int(item_id), 1.0, self.name) for item_id in chosen]
        return self._finish(candidates, k)


@dataclass(frozen=True)
class ScoreboardResult:
    """Aggregate evaluation metrics and the number of eligible readers.

    ``hit_rate_at_k`` / ``recall_at_k`` are the Unit-1 metrics; ``precision_at_k`` / ``ndcg_at_k``
    are the Unit-6 rank-position-aware additions (default ``0.0`` so any older positional
    construction stays valid).
    """

    readers: int
    hit_rate_at_k: float
    recall_at_k: float
    precision_at_k: float = 0.0
    ndcg_at_k: float = 0.0


@dataclass(frozen=True)
class BlendedScoreboardResult:
    """Aggregate metrics for a calibrated weighted blend of several retrieval paths."""

    readers: int
    hit_rate_at_k: float
    catalog_coverage: float


def _open_interactions(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, mode="rt", encoding="utf-8", newline="")
    return open(path, encoding="utf-8", newline="")


def _seen_and_relevant(
    interactions_path: str | Path,
    known_items: set[int],
    split: str,
) -> tuple[dict[int, set[int]], dict[int, set[int]]]:
    """Read positive train items (the seen set) and positive ``split`` items (the relevant set).

    Shared by both scoreboards. The seen set is always the train positives; the relevant set is the
    positives of the requested ``split`` (``"val"`` or ``"test"``). Only ``label == 1`` rows whose
    item is in ``known_items`` are counted; everything else is leakage/noise and skipped.
    """
    seen_by_reader: dict[int, set[int]] = defaultdict(set)
    target_by_reader: dict[int, set[int]] = defaultdict(set)
    with _open_interactions(Path(interactions_path)) as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            reader_id = int(row["reader_id"])
            item_id = int(row["item_id"])
            if item_id not in known_items or int(row["label"]) != 1:
                continue
            if row["split"] == "train":
                seen_by_reader[reader_id].add(item_id)
            elif row["split"] == split:
                target_by_reader[reader_id].add(item_id)
    return seen_by_reader, target_by_reader


def run_validation_scoreboard(
    path: Any,
    interactions_path: str | Path,
    *,
    catalog_ids: Iterable[int],
    k: int,
    cold_readers: Iterable[int] = (),
    split: str = "val",
) -> ScoreboardResult:
    """Evaluate a retrieval path on the positive rows of one held-out ``split``.

    ``split`` defaults to ``"val"`` (the frozen validation holdout); ``"test"`` is permitted so
    Checkpoint A can score the sealed test holdout **once** — the SAME cold-reader exclusion applies
    to both. Readers with no unseen positive item in the split, and declared ``cold_readers``, are
    excluded. Positive training items form the seen set and are removed from both recommendations
    and relevance before scoring: a re-read is not a recommendation. Reports hit-rate, recall,
    precision and NDCG at ``k``.
    """
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        raise ValueError(f"k must be a positive int, got {k!r}")
    if split not in ("val", "test"):
        raise ValueError(f"split must be 'val' or 'test', got {split!r}")
    known_items = set(catalog_ids)
    cold = set(cold_readers)
    seen_by_reader, target_by_reader = _seen_and_relevant(interactions_path, known_items, split)

    hits: list[float] = []
    recalls: list[float] = []
    precisions: list[float] = []
    ndcgs: list[float] = []
    for reader_id in sorted(target_by_reader):
        seen = seen_by_reader[reader_id]
        relevant = target_by_reader[reader_id] - seen
        if reader_id in cold or not relevant:
            continue
        candidates = path.retrieve(reader_id, {"seen": seen}, k)
        recommendations = rank(candidates, n=k, exclude=seen)
        hits.append(hit_rate_at_k(recommendations, relevant, k))
        recalls.append(recall_at_k(recommendations, relevant, k))
        precisions.append(precision_at_k(recommendations, relevant, k))
        ndcgs.append(ndcg_at_k(recommendations, relevant, k))
    readers = len(hits)
    return ScoreboardResult(
        readers=readers,
        hit_rate_at_k=sum(hits) / readers if readers else 0.0,
        recall_at_k=sum(recalls) / readers if readers else 0.0,
        precision_at_k=sum(precisions) / readers if readers else 0.0,
        ndcg_at_k=sum(ndcgs) / readers if readers else 0.0,
    )


def run_blended_scoreboard(
    paths: Mapping[str, Any],
    interactions_path: str | Path,
    *,
    catalog_ids: Iterable[int],
    k: int,
    pool: int,
    weights: Mapping[str, float] | None = None,
    cold_readers: Iterable[int] = (),
    split: str = "val",
) -> BlendedScoreboardResult:
    """Evaluate a calibrated weighted blend of several paths — the first blended recommender.

    For every eligible reader: each path in ``paths`` retrieves a per-path pool of ``pool``
    candidates; :func:`~bookrec.blend.blend` calibrates each path to ``[0, 1]`` and takes the
    ``weights``-weighted union; :func:`~bookrec.rank.rank` drops the reader's seen items and keeps
    the top ``k``. Returns mean hit@k and catalog coverage (the fraction of the catalog that appears
    in at least one reader's top-k). ``weights`` must name exactly the blended ``paths`` (the
    :func:`~bookrec.blend.blend` contract); omit it for an equal-weight blend. The reader eligibility
    and seen/relevant construction match :func:`run_validation_scoreboard` exactly, so a single-path
    blend reproduces that path's hit@k. Deterministic given fitted paths.
    """
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        raise ValueError(f"k must be a positive int, got {k!r}")
    if not isinstance(pool, int) or isinstance(pool, bool) or pool <= 0:
        raise ValueError(f"pool must be a positive int, got {pool!r}")
    if split not in ("val", "test"):
        raise ValueError(f"split must be 'val' or 'test', got {split!r}")
    if not paths:
        raise ValueError("run_blended_scoreboard needs at least one path")
    known_items = set(catalog_ids)
    cold = set(cold_readers)
    seen_by_reader, target_by_reader = _seen_and_relevant(interactions_path, known_items, split)

    hits: list[float] = []
    rec_lists: list[list[int]] = []
    for reader_id in sorted(target_by_reader):
        seen = seen_by_reader[reader_id]
        relevant = target_by_reader[reader_id] - seen
        if reader_id in cold or not relevant:
            continue
        per_path = {
            name: path.retrieve(reader_id, {"seen": seen}, pool) for name, path in paths.items()
        }
        blended = blend(per_path, weights=weights)
        recommendations = rank(blended, n=k, exclude=seen)
        hits.append(hit_rate_at_k(recommendations, relevant, k))
        rec_lists.append([c.item_id for c in recommendations])
    readers = len(hits)
    return BlendedScoreboardResult(
        readers=readers,
        hit_rate_at_k=sum(hits) / readers if readers else 0.0,
        catalog_coverage=catalog_coverage(rec_lists, known_items),
    )
