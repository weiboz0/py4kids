"""Unit 1 tests for catalog search, the val scoreboard, and the random floor."""

from __future__ import annotations

import csv
import gzip
from pathlib import Path

import pytest
from bookrec import (
    Book,
    Candidate,
    RandomRetrievalPath,
    generated_dir,
    run_validation_scoreboard,
    search_catalog,
)


def _write_interactions(path: Path, rows: list[tuple[object, ...]]) -> None:
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["reader_id", "item_id", "session_id", "timestamp", "split", "label"])
        writer.writerows(rows)


def test_generated_dir_points_to_regenerated_data() -> None:
    path = generated_dir()

    assert path.name == "generated"
    assert path.parent.name == "data"
    assert (path / "catalog.csv.gz").is_file()


def test_search_catalog_uses_real_schema_attributes_and_text() -> None:
    catalog = {
        2: Book(2, "Python Adventures", {"author_id": "7", "genres": "coding;adventure", "year": "2024"}),
        1: Book(1, "Quiet Stars", {"author_id": "8", "genres": "science;poetry", "year": "2020"}),
        3: Book(3, "Adventure Atlas", {"author_id": "7", "genres": "travel;adventure", "year": "2020"}),
    }

    assert [book.item_id for book in search_catalog(catalog, text="adventure")] == [2, 3]
    assert [book.item_id for book in search_catalog(catalog, author_id=7)] == [2, 3]
    assert [book.item_id for book in search_catalog(catalog, genre="science")] == [1]
    assert [book.item_id for book in search_catalog(catalog, year=2020)] == [1, 3]
    assert [book.item_id for book in search_catalog(catalog, text="atlas", author_id=7)] == [3]


class _FixedPath:
    name = "fixed"
    version = "1"

    def retrieve(self, query: object, context: object, k: int) -> list[Candidate]:
        del query, context, k
        return [
            Candidate(0, 3.0, self.name),  # seen in train
            Candidate(4, 2.0, self.name),  # positive only in sealed test
            Candidate(1, 1.0, self.name),
        ]


class _ReturnedItemsPath:
    name = "returned-items"
    version = "1"

    def __init__(self, *item_ids: int) -> None:
        self.item_ids = item_ids

    def retrieve(self, query: object, context: object, k: int) -> list[Candidate]:
        del query, context
        return [Candidate(item_id, 1.0, self.name) for item_id in self.item_ids[:k]]


def test_scoreboard_uses_val_only_and_excludes_ineligible_readers(tmp_path: Path) -> None:
    interactions = tmp_path / "interactions.csv.gz"
    _write_interactions(
        interactions,
        [
            (10, 0, 0, 1, "train", 1),
            (10, 2, 1, 2, "val", 1),
            (10, 4, 2, 3, "test", 1),
            (11, 1, 0, 1, "train", 1),
            (11, 3, 1, 2, "val", 0),  # no val positive
            (12, 3, 1, 2, "val", 1),  # cold reader
        ],
    )

    result = run_validation_scoreboard(
        _FixedPath(), interactions, catalog_ids=range(5), k=2, cold_readers={12}
    )

    assert result.readers == 1
    assert result.hit_rate_at_k == 0.0  # test item 4 is deliberately not relevant
    assert result.recall_at_k == 0.0


def test_scoreboard_removes_train_val_overlap_from_relevant_denominator(
    tmp_path: Path,
) -> None:
    interactions = tmp_path / "interactions.csv.gz"
    _write_interactions(
        interactions,
        [
            (10, 0, 0, 1, "train", 1),
            (10, 0, 1, 2, "val", 1),  # re-read: seen, not recommendable
            (10, 1, 1, 2, "val", 1),  # genuinely unseen and relevant
        ],
    )

    result = run_validation_scoreboard(
        _ReturnedItemsPath(1), interactions, catalog_ids=range(3), k=1
    )

    assert result.readers == 1
    assert result.hit_rate_at_k == 1.0
    assert result.recall_at_k == 1.0


def test_scoreboard_reports_nonzero_metrics_for_genuine_hit(tmp_path: Path) -> None:
    interactions = tmp_path / "interactions.csv.gz"
    _write_interactions(
        interactions,
        [
            (10, 0, 0, 1, "train", 1),
            (10, 2, 1, 2, "val", 1),
        ],
    )

    result = run_validation_scoreboard(
        _ReturnedItemsPath(2), interactions, catalog_ids=range(3), k=1
    )

    assert result.readers == 1
    assert result.hit_rate_at_k == 1.0
    assert result.recall_at_k == 1.0


def test_random_path_samples_only_unseen_items_and_is_deterministic() -> None:
    first = RandomRetrievalPath(range(10), seed=2026)
    second = RandomRetrievalPath(range(10), seed=2026)

    first_ids = [c.item_id for c in first.retrieve(7, {"seen": {0, 1, 2}}, k=4)]
    second_ids = [c.item_id for c in second.retrieve(7, {"seen": {0, 1, 2}}, k=4)]

    assert first_ids == second_ids
    assert len(first_ids) == len(set(first_ids)) == 4
    assert set(first_ids).isdisjoint({0, 1, 2})


@pytest.mark.parametrize("bad_k", [0, -1, 2.0, True])
def test_random_path_rejects_invalid_k(bad_k: object) -> None:
    with pytest.raises(ValueError, match="positive int"):
        RandomRetrievalPath(range(10), seed=2026).retrieve(
            7, {"seen": set()}, k=bad_k  # type: ignore[arg-type]
        )


def test_random_baseline_empirical_hit_rate_matches_exact_k_over_n() -> None:
    item_ids = range(10)
    seen = {0, 1}
    relevant = 2
    k = 2
    trials = 4000
    hits = 0
    for seed in range(trials):
        candidates = RandomRetrievalPath(item_ids, seed=seed).retrieve(
            99, {"seen": seen}, k=k
        )
        hits += relevant in {candidate.item_id for candidate in candidates}

    empirical = hits / trials
    unseen_count = len(set(item_ids) - seen)
    analytic = k / unseen_count
    assert empirical == pytest.approx(analytic, abs=0.03)
