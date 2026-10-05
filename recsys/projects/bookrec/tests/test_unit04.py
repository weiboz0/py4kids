"""Unit 4 (recsys-006): item-item co-occurrence collaborative filtering.

Verifies the shipped `ItemItemRetrievalPath` + `item_item_cosine` on the recsys-004 interaction
log: the first **collaborative** path clearing the recoverability harness's two-part gate on the
seeded val scoreboard (hit@10 >= 1.3x popularity AND >= popularity + 0.03) **and** beating the
Unit-3 lexical path; a tiny hand-checked co-occurrence/cosine fixture; leakage safety (the fitted
similarity is bit-identical with or without val/test rows, and a val-folded "leaky" fit scores
wildly higher); the contract behaviour (empty / out-of-index `seen`, exclude-seen, bound); a
fit->artifact->load round-trip returning identical recommendations; registry ownership; and the
honest `n_neighbors`-cap *degradation* on this data.
"""

from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path

import numpy as np
import pytest
from bookrec import (
    DuplicatePathError,
    ItemItemRetrievalPath,
    LexicalRetrievalPath,
    PathRegistry,
    PopularityRetrievalPath,
    RandomRetrievalPath,
    generated_dir,
    item_item_cosine,
    load_catalog,
    load_keywords,
    run_validation_scoreboard,
)

K = 10
RANDOM_SEED = 0


def _read_rows(path: Path) -> list[dict[str, object]]:
    with gzip.open(path, mode="rt", encoding="utf-8", newline="") as handle:
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
        "keywords": load_keywords(gen / "keywords.csv.gz"),
        "rows": _read_rows(gen / "interactions.csv.gz"),
    }


def _hit_rate(path: object, generated: dict[str, object]) -> float:
    return run_validation_scoreboard(
        path,
        generated["interactions_path"],
        catalog_ids=generated["catalog_ids"],
        k=K,
        cold_readers=generated["cold_readers"],
    ).hit_rate_at_k


# --- the decisive win: CF clears the harness two-part gate AND beats lexical ------------------


def test_cf_clears_harness_gate_and_beats_popularity_and_lexical(
    generated: dict[str, object],
) -> None:
    catalog_ids = generated["catalog_ids"]
    rows = generated["rows"]

    cf = ItemItemRetrievalPath().fit(rows, catalog=catalog_ids)
    popularity = PopularityRetrievalPath().fit(rows, catalog=catalog_ids)
    lexical = LexicalRetrievalPath(generated["keywords"]).fit(rows, catalog=catalog_ids)

    cf_hit = _hit_rate(cf, generated)
    pop_hit = _hit_rate(popularity, generated)
    lex_hit = _hit_rate(lexical, generated)

    # Harness two-part margin over popularity (measured CF ~0.252 vs pop ~0.108, lexical ~0.158):
    # a ratio floor AND an absolute floor, so neither a tiny-but-high-ratio nor a large-but-flat
    # number can sneak through. CF is the first path to beat BOTH popularity AND the content path.
    assert pop_hit > 0 and lex_hit > 0
    assert cf_hit >= 1.3 * pop_hit
    assert cf_hit >= pop_hit + 0.03
    assert cf_hit > lex_hit


def test_cf_is_deterministic(generated: dict[str, object]) -> None:
    catalog_ids = generated["catalog_ids"]
    rows = generated["rows"]
    first = _hit_rate(ItemItemRetrievalPath().fit(rows, catalog=catalog_ids), generated)
    second = _hit_rate(ItemItemRetrievalPath().fit(rows, catalog=catalog_ids), generated)
    assert first == second


# --- tiny hand-checked co-occurrence / cosine fixture ----------------------------------------


def _train_pos(reader_id: int, item_id: int) -> dict[str, object]:
    return {"reader_id": reader_id, "item_id": item_id, "split": "train", "label": 1}


def test_tiny_cooccurrence_cosine_fixture() -> None:
    # Readers 0 and 1 both read items 100 and 101 (identical columns -> cosine 1.0); reader 2 reads
    # only item 102 (shares no reader with 100/101 -> cosine 0). The diagonal is zeroed.
    rows = [
        _train_pos(0, 100),
        _train_pos(0, 101),
        _train_pos(1, 100),
        _train_pos(1, 101),
        _train_pos(2, 102),
    ]
    path = ItemItemRetrievalPath().fit(rows)
    sim = path.similarity  # item ids sorted: [100, 101, 102]
    i100, i101, i102 = 0, 1, 2
    assert sim[i100, i101] == pytest.approx(1.0)  # co-read by the same readers
    assert sim[i101, i100] == pytest.approx(1.0)  # symmetric (uncapped)
    assert sim[i100, i102] == pytest.approx(0.0)  # no shared reader
    assert sim[i100, i100] == 0.0  # diagonal zeroed
    assert sim[i101, i101] == 0.0
    assert sim[i102, i102] == 0.0

    # retrieval: a reader who read 100 is recommended its twin 101 first.
    recs = path.retrieve(0, {"seen": {100}}, 3)
    assert recs[0].item_id == 101
    assert recs[0].provenance == "item-item"


def test_item_item_cosine_matches_hand_computation() -> None:
    # incidence columns: 100=[1,1,0], 101=[1,1,0], 102=[0,0,1].
    incidence = np.array([[1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    sim = item_item_cosine(incidence)
    assert np.allclose(np.diag(sim), 0.0)
    assert sim[0, 1] == pytest.approx(1.0)
    assert sim[0, 2] == pytest.approx(0.0)
    assert np.allclose(sim, sim.T)  # cosine is symmetric


# --- leakage safety --------------------------------------------------------------------------


def test_similarity_is_bit_identical_without_val_test_rows(generated: dict[str, object]) -> None:
    catalog_ids = generated["catalog_ids"]
    all_rows = generated["rows"]
    train_only = [row for row in all_rows if row["split"] == "train"]
    assert len(train_only) < len(all_rows)  # there really are val/test rows to drop

    full = ItemItemRetrievalPath().fit(all_rows, catalog=catalog_ids)
    trained = ItemItemRetrievalPath().fit(train_only, catalog=catalog_ids)
    # val/test rows and label==0 rows never touch the similarity: bit-identical, not merely close.
    assert np.array_equal(full.similarity, trained.similarity)


def test_leaky_fit_scores_dramatically_higher(generated: dict[str, object]) -> None:
    catalog_ids = generated["catalog_ids"]
    rows = generated["rows"]
    honest_hit = _hit_rate(ItemItemRetrievalPath().fit(rows, catalog=catalog_ids), generated)

    # A "leaky" fit that folds the val positives into the training incidence can recover the
    # held-out answer directly -> hit@10 jumps to a too-good-to-be-true ~0.96 (measured 0.964).
    leaky_rows = [
        dict(row, split="train") if (row["split"] == "val" and row["label"] == 1) else row
        for row in rows
    ]
    leaky_hit = _hit_rate(ItemItemRetrievalPath().fit(leaky_rows, catalog=catalog_ids), generated)
    assert leaky_hit > 0.5
    assert leaky_hit > 3 * honest_hit  # vivid: leakage is not a small wobble


# --- contract behaviour ----------------------------------------------------------------------


def test_empty_seen_returns_empty(generated: dict[str, object]) -> None:
    path = ItemItemRetrievalPath().fit(generated["rows"], catalog=generated["catalog_ids"])
    assert path.retrieve(0, {"seen": set()}, K) == []
    assert path.retrieve(0, {}, K) == []


def test_seen_item_not_in_index_is_skipped_no_keyerror() -> None:
    # Only items 100/101/102 are in the fitted index. A seen id of 999 (absent) must be skipped,
    # never raise KeyError. With one indexed + one absent seen item, retrieval still works.
    rows = [_train_pos(0, 100), _train_pos(0, 101), _train_pos(1, 100), _train_pos(1, 101)]
    path = ItemItemRetrievalPath().fit(rows)
    recs = path.retrieve(0, {"seen": {100, 999}}, K)  # 999 absent -> skipped
    assert [c.item_id for c in recs] == [101]
    assert path.retrieve(0, {"seen": {999}}, K) == []  # only-absent -> no signal -> []


def test_no_neighbour_history_returns_empty_coverage_ceiling() -> None:
    # Coverage ceiling (enforced): readers 0 and 1 co-read 100/101; reader 2 reads only 102, which
    # shares no reader with the others -> 102's similarity column is all-zero. A reader whose whole
    # history is {102} has NO positive-score candidate, so retrieve returns [] rather than handing
    # back zero-score filler items. An empty seen likewise returns [].
    rows = [
        _train_pos(0, 100),
        _train_pos(0, 101),
        _train_pos(1, 100),
        _train_pos(1, 101),
        _train_pos(2, 102),
    ]
    path = ItemItemRetrievalPath().fit(rows)
    assert path.retrieve(0, {"seen": {102}}, 10) == []  # only neighbourless item seen -> []
    assert path.retrieve(0, {"seen": set()}, 10) == []


def test_retrieve_excludes_seen_and_is_bounded(generated: dict[str, object]) -> None:
    catalog_ids = generated["catalog_ids"]
    path = ItemItemRetrievalPath().fit(generated["rows"], catalog=catalog_ids)
    seen = {catalog_ids[0], catalog_ids[1], catalog_ids[2]}
    recs = path.retrieve(0, {"seen": seen}, K)
    assert len(recs) <= K
    assert all(c.item_id not in seen for c in recs)
    assert all(c.provenance == "item-item" for c in recs)


def test_fit_signature_is_protocol_substitutable(generated: dict[str, object]) -> None:
    # fit(interactions, catalog=None) — exactly the RetrievalPath protocol shape (no catalog arg).
    path = ItemItemRetrievalPath()
    same = path.fit(generated["rows"])
    assert same is path
    # Seed with an item that HAS train positives AND a real co-occurrence neighbour (a reader who
    # co-read >=2 books), so the coverage-ceiling retrieve returns a NON-EMPTY, positive-score
    # result — not the vacuous `is not None` check that a no-positives item would pass trivially.
    reader_items: dict[int, set[int]] = {}
    for row in generated["rows"]:
        if row["split"] == "train" and row["label"] == 1:
            reader_items.setdefault(int(row["reader_id"]), set()).add(int(row["item_id"]))
    seen_item = next(next(iter(items)) for items in reader_items.values() if len(items) >= 2)
    recs = path.retrieve(0, {"seen": {seen_item}}, K)
    assert recs  # a real neighbour exists -> non-empty
    assert all(c.score > 0 for c in recs)


def test_fit_raises_on_no_train_positives() -> None:
    with pytest.raises(ValueError):
        ItemItemRetrievalPath().fit([{"reader_id": 0, "item_id": 1, "split": "val", "label": 1}])


def test_fit_artifact_load_round_trip(generated: dict[str, object]) -> None:
    catalog_ids = generated["catalog_ids"]
    rows = generated["rows"]
    original = ItemItemRetrievalPath().fit(rows, catalog=catalog_ids)
    restored = ItemItemRetrievalPath().load(original.artifact())
    for reader_seed in (3, 11, 42, 128):
        rng = np.random.default_rng(reader_seed)
        seen = set(rng.choice(catalog_ids, size=4, replace=False).tolist())
        a = original.retrieve(reader_seed, {"seen": seen}, K)
        b = restored.retrieve(reader_seed, {"seen": seen}, K)
        assert [c.item_id for c in a] == [c.item_id for c in b]
        assert [c.score for c in a] == [c.score for c in b]
        assert [c.provenance for c in a] == [c.provenance for c in b]
    # load copies arrays, never aliases the artifact's.
    artifact = original.artifact()
    loaded = ItemItemRetrievalPath().load(artifact)
    artifact["similarity"][0, 0] = 123.0
    assert loaded.similarity[0, 0] != 123.0


def test_load_rejects_malformed_similarity_shape(generated: dict[str, object]) -> None:
    # load must validate the restored similarity against len(item_ids): a non-square matrix (or any
    # shape != (n_items, n_items)) is a corrupt artifact and raises ValueError, not a silent load.
    original = ItemItemRetrievalPath().fit(generated["rows"], catalog=generated["catalog_ids"])
    artifact = original.artifact()
    artifact["similarity"] = artifact["similarity"][:-1]  # (n-1, n) — no longer square vs item_ids
    with pytest.raises(ValueError):
        ItemItemRetrievalPath().load(artifact)


# --- registry ownership ----------------------------------------------------------------------


def test_cf_path_registers_without_collision(generated: dict[str, object]) -> None:
    registry = PathRegistry()
    path = ItemItemRetrievalPath()
    registry.register(path)
    assert path.artifact_name() == "item-item-v1"
    assert "item-item" in registry
    # coexists with the other shipped paths (distinct names + artifacts).
    registry.register(RandomRetrievalPath(generated["catalog_ids"], seed=RANDOM_SEED))
    registry.register(PopularityRetrievalPath())
    registry.register(LexicalRetrievalPath(generated["keywords"]))
    with pytest.raises(DuplicatePathError):
        registry.register(ItemItemRetrievalPath())


# --- honest n_neighbors-cap degradation ------------------------------------------------------


def test_small_neighbor_cap_lowers_hit_rate(generated: dict[str, object]) -> None:
    catalog_ids = generated["catalog_ids"]
    rows = generated["rows"]
    uncapped = _hit_rate(ItemItemRetrievalPath().fit(rows, catalog=catalog_ids), generated)
    capped = _hit_rate(
        ItemItemRetrievalPath(n_neighbors=10).fit(rows, catalog=catalog_ids), generated
    )
    # On THIS data a small neighbourhood cap DEGRADES the score (measured ~0.142 < ~0.252):
    # the unit teaches the uncapped default honestly. Capping must not raise it.
    assert capped < uncapped
    assert ItemItemRetrievalPath(n_neighbors=10).fit(rows, catalog=catalog_ids).n_neighbors == 10


def test_rejects_bad_n_neighbors() -> None:
    with pytest.raises(ValueError):
        ItemItemRetrievalPath(n_neighbors=0)
    with pytest.raises(ValueError):
        ItemItemRetrievalPath(n_neighbors=-5)
