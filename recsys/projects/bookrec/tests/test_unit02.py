"""Unit 2 tests (plan recsys-003): the popularity count path, weighted rating, and bias metrics.

Directions are asserted on the committed seed (not brittle exact values). The measured numbers on
this seed (k=10, cold readers excluded, 368 scored readers, 2000-item catalog, head = top 200):
popularity-count hit@10 ≈ 0.1196 vs random floor ≈ 0.0136; popularity coverage ≈ 0.007 vs random
≈ 0.84; popularity head-share = 1.0 vs random ≈ 0.10.
"""

from __future__ import annotations

import csv
import gzip
import json
from collections import defaultdict
from itertools import pairwise
from pathlib import Path

import numpy as np
import pytest
from bookrec import (
    PathRegistry,
    PopularityRetrievalPath,
    RandomRetrievalPath,
    catalog_coverage,
    generated_dir,
    head_ids_from_counts,
    head_share,
    load_catalog,
    rank,
    run_validation_scoreboard,
    weighted_rating,
)

K = 10
RANDOM_SEED = 0


def _read_rows(path: Path) -> list[dict[str, object]]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        return [
            {
                "reader_id": int(row["reader_id"]),
                "item_id": int(row["item_id"]),
                "split": row["split"],
                "label": int(row["label"]),
            }
            for row in csv.DictReader(handle)
        ]


@pytest.fixture(scope="module")
def generated() -> dict[str, object]:
    gen = generated_dir()
    catalog_ids = sorted(load_catalog(gen / "catalog.csv.gz"))
    cold = json.loads((gen / "cold_partitions.json").read_text())
    return {
        "interactions_path": gen / "interactions.csv.gz",
        "catalog_ids": catalog_ids,
        "cold_readers": cold["cold_readers"],
        "rows": _read_rows(gen / "interactions.csv.gz"),
    }


# --- the count path beats the random floor ---------------------------------------------------


def test_count_path_hit_rate_far_exceeds_random_floor(generated: dict[str, object]) -> None:
    catalog_ids = generated["catalog_ids"]
    cold_readers = generated["cold_readers"]
    interactions_path = generated["interactions_path"]

    pop = PopularityRetrievalPath().fit(generated["rows"], catalog=catalog_ids)
    random_floor = RandomRetrievalPath(catalog_ids, seed=RANDOM_SEED)

    pop_result = run_validation_scoreboard(
        pop, interactions_path, catalog_ids=catalog_ids, k=K, cold_readers=cold_readers
    )
    random_result = run_validation_scoreboard(
        random_floor, interactions_path, catalog_ids=catalog_ids, k=K, cold_readers=cold_readers
    )

    # Direction, not brittle exact values: count path ~0.12, random floor ~0.014.
    assert pop_result.readers == random_result.readers > 0
    assert pop_result.hit_rate_at_k > 0.05
    assert pop_result.hit_rate_at_k > 5 * random_result.hit_rate_at_k


def test_scoreboard_is_deterministic(generated: dict[str, object]) -> None:
    catalog_ids = generated["catalog_ids"]
    first = run_validation_scoreboard(
        PopularityRetrievalPath().fit(generated["rows"], catalog=catalog_ids),
        generated["interactions_path"],
        catalog_ids=catalog_ids,
        k=K,
        cold_readers=generated["cold_readers"],
    )
    second = run_validation_scoreboard(
        PopularityRetrievalPath().fit(generated["rows"], catalog=catalog_ids),
        generated["interactions_path"],
        catalog_ids=catalog_ids,
        k=K,
        cold_readers=generated["cold_readers"],
    )
    assert first == second


# --- leakage safety: only positive train rows count ------------------------------------------


def test_fit_counts_only_positive_train_rows() -> None:
    rows = [
        {"reader_id": 0, "item_id": 1, "split": "train", "label": 1},
        {"reader_id": 1, "item_id": 1, "split": "train", "label": 1},
        {"reader_id": 2, "item_id": 2, "split": "train", "label": 1},
    ]
    path = PopularityRetrievalPath().fit(rows)
    assert path.counts == {1: 2, 2: 1}


def test_val_test_and_negative_rows_do_not_change_counts() -> None:
    train_positives = [
        {"reader_id": 0, "item_id": 1, "split": "train", "label": 1},
        {"reader_id": 1, "item_id": 1, "split": "train", "label": 1},
        {"reader_id": 2, "item_id": 2, "split": "train", "label": 1},
    ]
    leakage = [
        {"reader_id": 3, "item_id": 1, "split": "val", "label": 1},  # val row
        {"reader_id": 4, "item_id": 2, "split": "test", "label": 1},  # sealed test row
        {"reader_id": 5, "item_id": 1, "split": "train", "label": 0},  # train negative
        {"reader_id": 6, "item_id": 9, "split": "val", "label": 1},  # val-only item
    ]
    clean = PopularityRetrievalPath().fit(train_positives).counts
    with_leakage = PopularityRetrievalPath().fit(train_positives + leakage).counts
    assert with_leakage == clean == {1: 2, 2: 1}


def test_fit_raises_on_no_train_positives() -> None:
    with pytest.raises(ValueError, match="no positive train"):
        PopularityRetrievalPath().fit(
            [{"reader_id": 0, "item_id": 1, "split": "val", "label": 1}]
        )


def test_retrieve_is_reader_independent_and_excludes_seen() -> None:
    rows = [
        {"reader_id": 0, "item_id": 1, "split": "train", "label": 1},
        {"reader_id": 0, "item_id": 1, "split": "train", "label": 1},
        {"reader_id": 0, "item_id": 2, "split": "train", "label": 1},
        {"reader_id": 0, "item_id": 3, "split": "train", "label": 1},
    ]
    path = PopularityRetrievalPath().fit(rows)  # counts: 1->2, 2->1, 3->1
    reader_a = [c.item_id for c in path.retrieve("alice", {"seen": set()}, k=3)]
    reader_b = [c.item_id for c in path.retrieve("bob", {"seen": set()}, k=3)]
    assert reader_a == reader_b == [1, 2, 3]  # same ranking for every query
    excluded = [c.item_id for c in path.retrieve("alice", {"seen": {1}}, k=3)]
    assert 1 not in excluded and excluded == [2, 3]


def test_load_round_trips_the_fitted_artifact() -> None:
    rows = [
        {"reader_id": 0, "item_id": 7, "split": "train", "label": 1},
        {"reader_id": 1, "item_id": 7, "split": "train", "label": 1},
        {"reader_id": 2, "item_id": 8, "split": "train", "label": 1},
    ]
    fitted = PopularityRetrievalPath().fit(rows)
    restored = PopularityRetrievalPath().load(fitted.artifact())
    assert restored.counts == fitted.counts
    assert [c.item_id for c in restored.retrieve(None, {}, k=2)] == [7, 8]


# --- weighted (Bayesian-shrinkage) rating ----------------------------------------------------


def test_weighted_rating_reverses_thin_evidence_at_default_m() -> None:
    # 3-of-3 (rate 1.0, thin) vs 9000-of-10000 (rate 0.9, deep evidence). With a realistic low
    # global rate, shrinkage pulls the thin item down below the deep one at the default m=10.
    positives = np.array([3, 9000])
    exposures = np.array([3, 10000])
    scores = weighted_rating(positives, exposures, global_rate=0.2)
    assert scores[0] < scores[1]  # the 3/3 book scores BELOW the 9000/10000 book


def test_weighted_rating_m_to_zero_recovers_the_raw_rate() -> None:
    positives = np.array([3.0, 9000.0, 0.0])
    exposures = np.array([3.0, 10000.0, 5.0])
    scores = weighted_rating(positives, exposures, m=0.0, global_rate=0.2)
    np.testing.assert_allclose(scores, positives / exposures)


def test_weighted_rating_contracts_toward_C_as_m_grows() -> None:
    positives = np.array([3, 1, 9000, 40])
    exposures = np.array([3, 10, 10000, 50])
    c = 0.2
    distances = [
        float(np.max(np.abs(weighted_rating(positives, exposures, m=m, global_rate=c) - c)))
        for m in (0.0, 1.0, 10.0, 100.0, 1000.0)
    ]
    # Strictly contracting toward C (do NOT assert exact ties at finite m).
    assert all(later < earlier for earlier, later in pairwise(distances))


def test_weighted_rating_handles_zero_exposure_safely() -> None:
    scores = weighted_rating(np.array([0, 5]), np.array([0, 10]), m=10.0, global_rate=0.3)
    assert np.isfinite(scores).all()
    assert scores[0] == pytest.approx(0.3)  # v==0 -> the global rate C


def test_weighted_rating_default_global_rate_shows_no_reversal() -> None:
    # With the default global_rate=None the shrink target is the pair's OWN C = 9003/10003 ~ 0.90,
    # which is NOT below R2=0.9, so the thin 3/3 item scores slightly ABOVE the deep 9000/10000 one.
    # That is why the reversal test must pass an explicit low global_rate (0.2 < R2).
    positives = np.array([3, 9000])
    exposures = np.array([3, 10000])
    scores = weighted_rating(positives, exposures)  # global_rate=None -> C ~ 0.90
    assert scores[0] > scores[1]  # NO reversal at the pair's own high C


def test_weighted_rating_zero_m_is_valid() -> None:
    scores = weighted_rating(np.array([3.0, 0.0]), np.array([3.0, 5.0]), m=0.0, global_rate=0.2)
    np.testing.assert_allclose(scores, np.array([1.0, 0.0]))  # m==0 -> raw rate


def test_weighted_rating_rejects_negative_m() -> None:
    with pytest.raises(ValueError, match="m must be >= 0"):
        weighted_rating(np.array([1, 2]), np.array([2, 4]), m=-1.0, global_rate=0.2)


def test_weighted_rating_rejects_non_finite_m() -> None:
    with pytest.raises(TypeError, match="m must be finite"):
        weighted_rating(np.array([1, 2]), np.array([2, 4]), m=float("inf"), global_rate=0.2)


def test_weighted_rating_rejects_negative_exposures() -> None:
    with pytest.raises(ValueError, match="exposures must be >= 0"):
        weighted_rating(np.array([1, 2]), np.array([2, -4]), global_rate=0.2)


def test_weighted_rating_rejects_negative_positives() -> None:
    with pytest.raises(ValueError, match="positives must be >= 0"):
        weighted_rating(np.array([-1, 2]), np.array([2, 4]), global_rate=0.2)


def test_weighted_rating_rejects_positives_exceeding_exposures() -> None:
    with pytest.raises(ValueError, match="positives must be <= exposures"):
        weighted_rating(np.array([5, 2]), np.array([3, 4]), global_rate=0.2)


def test_weighted_rating_rejects_non_finite_counts() -> None:
    with pytest.raises(TypeError, match="must be finite"):
        weighted_rating(np.array([float("nan"), 2.0]), np.array([3.0, 4.0]), global_rate=0.2)


def test_weighted_rating_rejects_out_of_range_global_rate() -> None:
    with pytest.raises(ValueError, match=r"global_rate must be in \[0, 1\]"):
        weighted_rating(np.array([3, 9000]), np.array([3, 10000]), global_rate=2.0)
    with pytest.raises(ValueError, match=r"global_rate must be in \[0, 1\]"):
        weighted_rating(np.array([3, 9000]), np.array([3, 10000]), global_rate=-0.1)


def test_weighted_rating_rejects_non_finite_global_rate() -> None:
    with pytest.raises(TypeError, match="global_rate must be finite"):
        weighted_rating(np.array([3, 9000]), np.array([3, 10000]), global_rate=float("nan"))


# --- popularity-bias metrics: coverage and head-share ----------------------------------------


def _recommendations(path: object, generated: dict[str, object]) -> list[list[object]]:
    """Reproduce the scoreboard's scored-reader set and collect each one's top-k list."""
    catalog_ids = set(generated["catalog_ids"])
    cold = set(generated["cold_readers"])
    seen_by: dict[int, set[int]] = defaultdict(set)
    val_by: dict[int, set[int]] = defaultdict(set)
    for row in generated["rows"]:
        if row["item_id"] not in catalog_ids or row["label"] != 1:
            continue
        if row["split"] == "train":
            seen_by[row["reader_id"]].add(row["item_id"])
        elif row["split"] == "val":
            val_by[row["reader_id"]].add(row["item_id"])
    recommendations = []
    for reader_id in sorted(val_by):
        seen = seen_by[reader_id]
        if reader_id in cold or not (val_by[reader_id] - seen):
            continue
        candidates = path.retrieve(reader_id, {"seen": seen}, K)
        recommendations.append(rank(candidates, n=K, exclude=seen))
    return recommendations


def test_popularity_coverage_is_far_below_random_coverage(generated: dict[str, object]) -> None:
    catalog_ids = generated["catalog_ids"]
    pop = PopularityRetrievalPath().fit(generated["rows"], catalog=catalog_ids)
    random_floor = RandomRetrievalPath(catalog_ids, seed=RANDOM_SEED)

    head = head_ids_from_counts(pop.counts, catalog_ids, fraction=0.10)
    assert len(head) == 200  # ceil(0.10 * 2000)

    pop_recs = _recommendations(pop, generated)
    random_recs = _recommendations(random_floor, generated)

    pop_coverage = catalog_coverage(pop_recs, catalog_ids)
    random_coverage = catalog_coverage(random_recs, catalog_ids)
    pop_head = head_share(pop_recs, head)
    random_head = head_share(random_recs, head)

    for value in (pop_coverage, random_coverage, pop_head, random_head):
        assert 0.0 <= value <= 1.0
    # The popularity "winner" serves almost none of the catalog (bias): ~0.007 vs ~0.84.
    assert pop_coverage < 0.05
    assert pop_coverage < 0.1 * random_coverage
    # Every popularity slot is a head item; the random floor spreads over the tail.
    assert pop_head == pytest.approx(1.0)
    assert random_head < pop_head


def test_coverage_and_head_share_edge_cases() -> None:
    assert catalog_coverage([], [1, 2, 3]) == 0.0
    assert catalog_coverage([[1, 2]], []) == 0.0
    assert head_share([], [1]) == 0.0
    assert catalog_coverage([[1, 1], [1]], [1, 2]) == pytest.approx(0.5)
    assert head_share([[1, 2], [3, 4]], {1, 2}) == pytest.approx(0.5)


# --- registry integration --------------------------------------------------------------------


def test_popularity_path_registers_without_collision() -> None:
    registry = PathRegistry()
    path = PopularityRetrievalPath()
    registry.register(path)
    assert path.artifact_name() == "popularity-v1"
    assert "popularity" in registry
    assert registry.get("popularity") is path
