"""The Unit 1 frozen-validation scoreboard and seeded random retrieval floor."""

from __future__ import annotations

import csv
import gzip
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from bookrec.evaluate import hit_rate_at_k, recall_at_k
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
    """Aggregate validation metrics and the number of eligible readers."""

    readers: int
    hit_rate_at_k: float
    recall_at_k: float


def _open_interactions(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, mode="rt", encoding="utf-8", newline="")
    return open(path, encoding="utf-8", newline="")


def run_validation_scoreboard(
    path: Any,
    interactions_path: str | Path,
    *,
    catalog_ids: Iterable[int],
    k: int,
    cold_readers: Iterable[int] = (),
) -> ScoreboardResult:
    """Evaluate a retrieval path on positive ``val`` rows, never on sealed ``test`` rows.

    Readers with no positive validation item and declared cold readers are excluded. Positive
    training items form the seen set and are removed with :func:`bookrec.rank.rank` before scoring.
    """
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        raise ValueError(f"k must be a positive int, got {k!r}")
    known_items = set(catalog_ids)
    cold = set(cold_readers)
    seen_by_reader: dict[int, set[int]] = defaultdict(set)
    val_by_reader: dict[int, set[int]] = defaultdict(set)
    with _open_interactions(Path(interactions_path)) as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            reader_id = int(row["reader_id"])
            item_id = int(row["item_id"])
            if item_id not in known_items or int(row["label"]) != 1:
                continue
            if row["split"] == "train":
                seen_by_reader[reader_id].add(item_id)
            elif row["split"] == "val":
                val_by_reader[reader_id].add(item_id)

    hits: list[float] = []
    recalls: list[float] = []
    for reader_id in sorted(val_by_reader):
        relevant = val_by_reader[reader_id]
        if reader_id in cold or not relevant:
            continue
        seen = seen_by_reader[reader_id]
        candidates = path.retrieve(reader_id, {"seen": seen}, k)
        recommendations = rank(candidates, n=k, exclude=seen)
        hits.append(hit_rate_at_k(recommendations, relevant, k))
        recalls.append(recall_at_k(recommendations, relevant, k))
    readers = len(hits)
    return ScoreboardResult(
        readers=readers,
        hit_rate_at_k=sum(hits) / readers if readers else 0.0,
        recall_at_k=sum(recalls) / readers if readers else 0.0,
    )
