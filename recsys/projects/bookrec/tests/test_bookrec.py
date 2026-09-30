"""Contract tests for the bookrec foundation (plan recsys-001, design 011 §5)."""

from __future__ import annotations

import gzip
from pathlib import Path

import pytest
from _popularity_fixture import PopularityPath
from bookrec import (
    Candidate,
    DuplicatePathError,
    PathRegistry,
    RetrievalPath,
    blend,
    calibrate_scores,
    hit_rate_at_k,
    load_catalog,
    order_candidates,
    rank,
    recall_at_k,
)
from bookrec.evaluate import mean_hit_rate_at_k

# --- the contract itself ---------------------------------------------------------------------


def test_popularity_path_satisfies_the_retrieval_protocol(popularity: PopularityPath) -> None:
    assert isinstance(popularity, RetrievalPath)


def test_candidate_item_ids_are_stable_ints() -> None:
    with pytest.raises(TypeError):
        Candidate(item_id="10", score=1.0, provenance="x")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        Candidate(item_id=True, score=1.0, provenance="x")  # bools are not stable ids
    assert Candidate(10, 1.0, "x").item_id == 10


def test_retrieve_honours_k_exactly(popularity: PopularityPath) -> None:
    assert len(popularity.retrieve(None, None, k=3)) == 3
    assert len(popularity.retrieve(None, None, k=99)) == 5  # only five distinct items
    for bad in (0, -1, 2.0, True):
        with pytest.raises(ValueError):
            popularity.retrieve(None, None, k=bad)  # type: ignore[arg-type]


def test_retrieve_is_ordered_with_deterministic_id_tie_break(popularity: PopularityPath) -> None:
    ids = [c.item_id for c in popularity.retrieve(None, None, k=5)]
    # 10 (4) > 20 (3) > [30, 40 tie at 2 -> id order] > 50 (1)
    assert ids == [10, 20, 30, 40, 50]


def test_retrieve_carries_path_provenance(popularity: PopularityPath) -> None:
    assert {c.provenance for c in popularity.retrieve(None, None, k=5)} == {"popularity"}


def test_retrieve_before_fit_fails() -> None:
    with pytest.raises(RuntimeError):
        PopularityPath().retrieve(None, None, k=1)


def test_path_owns_one_versioned_artifact() -> None:
    assert PopularityPath(version="2").artifact_name() == "popularity-v2"


# --- score calibration -----------------------------------------------------------------------


def test_calibration_min_max_normalises_into_unit_interval() -> None:
    cands = [Candidate(1, 4.0, "p"), Candidate(2, 2.0, "p"), Candidate(3, 0.0, "p")]
    scores = {c.item_id: c.score for c in calibrate_scores(cands)}
    assert scores == {1: 1.0, 2: 0.5, 3: 0.0}


def test_calibration_of_equal_scores_is_present_but_uninformative() -> None:
    cands = [Candidate(1, 7.0, "p"), Candidate(2, 7.0, "p")]
    assert [c.score for c in calibrate_scores(cands)] == [1.0, 1.0]
    assert calibrate_scores([]) == []


def test_order_candidates_is_pure_and_deterministic() -> None:
    cands = [Candidate(3, 1.0, "p"), Candidate(1, 1.0, "p"), Candidate(2, 2.0, "p")]
    assert [c.item_id for c in order_candidates(cands)] == [2, 1, 3]


# --- registry --------------------------------------------------------------------------------


def test_registry_registers_and_retrieves(popularity: PopularityPath) -> None:
    registry = PathRegistry()
    registry.register(popularity)
    assert "popularity" in registry
    assert registry.get("popularity") is popularity
    assert registry.names() == ["popularity"]
    assert len(registry) == 1


def test_registry_rejects_duplicate_name(popularity: PopularityPath) -> None:
    registry = PathRegistry()
    registry.register(popularity)
    with pytest.raises(DuplicatePathError):
        registry.register(PopularityPath())


def test_registry_rejects_duplicate_artifact_ownership() -> None:
    registry = PathRegistry()
    registry.register(PopularityPath(name="pop-a", version="1"))
    clash = PopularityPath(name="pop-b", version="1")
    clash.artifact_name = lambda: "pop-a-v1"  # type: ignore[method-assign]
    with pytest.raises(DuplicatePathError):
        registry.register(clash)


# --- catalog ---------------------------------------------------------------------------------


def _write_catalog(path: Path, rows: str) -> None:
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        handle.write(rows)


def test_load_catalog_reads_gzipped_csv_with_stable_int_ids(tmp_path: Path) -> None:
    path = tmp_path / "catalog.csv.gz"
    _write_catalog(
        path,
        "item_id,title,author\n10,Dune,Herbert\n20,Emma,Austen\n",
    )
    catalog = load_catalog(path)
    assert set(catalog) == {10, 20}
    assert catalog[10].title == "Dune"
    assert catalog[10].fields["author"] == "Herbert"


def test_load_catalog_rejects_bad_rows(tmp_path: Path) -> None:
    missing = tmp_path / "missing.csv.gz"
    _write_catalog(missing, "item_id,author\n10,Herbert\n")
    with pytest.raises(ValueError, match="missing required column"):
        load_catalog(missing)

    noninteger = tmp_path / "noninteger.csv.gz"
    _write_catalog(noninteger, "item_id,title\nx,Dune\n")
    with pytest.raises(ValueError, match="non-integer item_id"):
        load_catalog(noninteger)

    duplicate = tmp_path / "duplicate.csv.gz"
    _write_catalog(duplicate, "item_id,title\n10,Dune\n10,Emma\n")
    with pytest.raises(ValueError, match="duplicate item_id"):
        load_catalog(duplicate)


# --- blend + rank + evaluate -----------------------------------------------------------------


def test_blend_unions_calibrates_and_records_provenance() -> None:
    per_path = {
        "popularity": [Candidate(10, 100.0, "popularity"), Candidate(20, 50.0, "popularity")],
        "lexical": [Candidate(20, 2.0, "lexical"), Candidate(30, 1.0, "lexical")],
    }
    blended = blend(per_path)
    by_id = {c.item_id: c for c in blended}
    assert set(by_id) == {10, 20, 30}
    # item 20 appears in both paths -> blended provenance names both, sorted
    assert by_id[20].provenance == "lexical+popularity"
    assert by_id[10].provenance == "popularity"
    # calibrated: popularity 10->1.0, 20->0.0; lexical 20->1.0, 30->0.0
    assert by_id[10].score == pytest.approx(1.0)
    assert by_id[20].score == pytest.approx(1.0)
    assert by_id[30].score == pytest.approx(0.0)
    # deterministic order: 10 and 20 tie at 1.0 -> id order, then 30
    assert [c.item_id for c in blended] == [10, 20, 30]


def test_blend_applies_per_path_weights() -> None:
    per_path = {
        "a": [Candidate(1, 1.0, "a"), Candidate(2, 0.0, "a")],
        "b": [Candidate(2, 1.0, "b"), Candidate(3, 0.0, "b")],
    }
    blended = {c.item_id: c.score for c in blend(per_path, weights={"a": 2.0, "b": 0.0})}
    assert blended[1] == pytest.approx(2.0)
    assert blended[2] == pytest.approx(0.0)
    assert blended[3] == pytest.approx(0.0)


def test_rank_excludes_seen_and_bounds_n() -> None:
    pool = [Candidate(10, 0.9, "p"), Candidate(20, 0.8, "p"), Candidate(30, 0.7, "p")]
    ranked = rank(pool, n=2, exclude={20})
    assert [c.item_id for c in ranked] == [10, 30]
    assert [c.item_id for c in rank(pool)] == [10, 20, 30]
    with pytest.raises(ValueError):
        rank(pool, n=-1)


def test_hit_rate_and_recall_at_k(popularity: PopularityPath) -> None:
    recs = popularity.retrieve(None, None, k=5)  # ids [10, 20, 30, 40, 50]
    assert hit_rate_at_k(recs, relevant={40}, k=5) == 1.0
    assert hit_rate_at_k(recs, relevant={40}, k=2) == 0.0
    assert recall_at_k(recs, relevant={10, 40, 999}, k=5) == pytest.approx(2 / 3)
    assert recall_at_k(recs, relevant=set(), k=5) == 0.0
    for bad in (0, -1, 2.5, True):
        with pytest.raises(ValueError):
            hit_rate_at_k(recs, {10}, k=bad)  # type: ignore[arg-type]


def test_mean_hit_rate_over_queries() -> None:
    rows = [([10, 20], {20}), ([30, 40], {99})]
    assert mean_hit_rate_at_k(rows, k=2) == pytest.approx(0.5)
    assert mean_hit_rate_at_k([], k=2) == 0.0


def test_end_to_end_popularity_blend_rank_evaluate(popularity: PopularityPath) -> None:
    registry = PathRegistry()
    registry.register(popularity)
    per_path = {path.name: path.retrieve(None, None, k=5) for path in registry}
    ranked = rank(blend(per_path), n=3, exclude={10})
    ids = [c.item_id for c in ranked]
    assert ids == [20, 30, 40]
    assert hit_rate_at_k(ranked, relevant={30}, k=3) == 1.0
