"""Unit 8 (recsys-010): the two-tower model — MF re-expressed as a learned neural retriever.

Verifies the shipped `TwoTowerRetrievalPath` (PyTorch, torch imported lazily inside `fit`) on the
recsys-004 interaction log at the **pinned** config
(`embedding_dim=32, n_epochs=60, learning_rate=0.01, n_negatives=10, batch_size=256,
weight_decay=1e-4, seed=0`):

- the two-tower is the **best path in the book so far** — MF is fit live IN-TEST at the same seed /
  val split and `mf_hit` is read live (never a hard-coded 0.276), and the two-tower clears
  `tt_hit >= mf_hit - 0.03` AND `tt_hit >= 1.2 x pop` AND `tt_hit >= pop + 0.03` AND
  `tt_hit >= lexical` on the seeded val scoreboard (seed 0, k=10, 60 cold readers excluded).
  Measured seed-0 two-tower ~0.34 vs MF 0.276, CF 0.252, lexical 0.158, pop 0.108;
- CPU determinism per design 011 §184 (tolerance / ranking, NOT exact-float as the gate): two
  seeded fits give identical top-k ranking + `np.allclose` embeddings (with `np.array_equal` as a
  CPU bonus assertion);
- BPR training reduces the pairwise loss (a hand-checkable tiny fixture); leakage safety (val/test
  rows never touch the towers); the retrieve contract (a KNOWN reader with empty `seen` still
  returns k recs, stale `seen` ids are ignored, an UNKNOWN reader -> []); a fit->artifact->load
  round-trip returning identical recommendations **without importing torch**; and registry
  ownership (`two-tower-v1`).
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
    MatrixFactorizationPath,
    PathRegistry,
    PopularityRetrievalPath,
    RandomRetrievalPath,
    TwoTowerRetrievalPath,
    generated_dir,
    load_catalog,
    load_keywords,
    run_validation_scoreboard,
)

K = 10
SEED = 0  # pinned: seed-0 two-tower ~0.34 hit@10 on the shipped data (> MF 0.276 > CF 0.252)


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


@pytest.fixture(scope="module")
def fitted_tt(generated: dict[str, object]) -> TwoTowerRetrievalPath:
    # Trained ONCE at the pinned config and shared across tests (one full fit, not one per test).
    return TwoTowerRetrievalPath(seed=SEED).fit(
        generated["rows"], catalog=generated["catalog_ids"]
    )


# --- the decisive win: the two-tower is the book's best path, clearing the MF-bound gate --------


def test_two_tower_is_best_path_and_clears_mf_gate(
    generated: dict[str, object], fitted_tt: TwoTowerRetrievalPath
) -> None:
    catalog_ids = generated["catalog_ids"]
    rows = generated["rows"]

    # Fit MF live at the SAME seed/val split and read mf_hit live (never a hard-coded 0.276), so the
    # MF-bound gate stays measure-bound if the generator seed ever changes.
    mf = MatrixFactorizationPath(seed=SEED).fit(rows, catalog=catalog_ids)
    pop = PopularityRetrievalPath().fit(rows, catalog=catalog_ids)
    lexical = LexicalRetrievalPath(generated["keywords"]).fit(rows, catalog=catalog_ids)

    tt_hit = _hit_rate(fitted_tt, generated)
    mf_hit = _hit_rate(mf, generated)
    pop_hit = _hit_rate(pop, generated)
    lex_hit = _hit_rate(lexical, generated)

    # Measured (seed 0): pop 0.108, lexical 0.158, MF 0.276, two-tower ~0.34 (the new best). The
    # SAME reader.book dot product as MF, but the pairwise BPR ranking objective + Adam + weight
    # decay win on top-k. The 0.03 MF tolerance (as in Unit 5) is cleared with wide room; an
    # unregularized (weight_decay=0) path would overfit below CF and correctly FAIL `tt >= mf-0.03`.
    assert pop_hit > 0 and lex_hit > 0
    assert tt_hit >= mf_hit - 0.03
    assert tt_hit >= 1.2 * pop_hit
    assert tt_hit >= pop_hit + 0.03
    assert tt_hit >= lex_hit


def test_two_tower_is_deterministic(
    generated: dict[str, object], fitted_tt: TwoTowerRetrievalPath
) -> None:
    catalog_ids = generated["catalog_ids"]
    rows = generated["rows"]
    # A second independently-constructed fit at the same seed/config. Design 011 §184: the GATE is
    # tolerance/ranking-based (identical top-k ranking + allclose embeddings), NEVER exact-float.
    other = TwoTowerRetrievalPath(seed=SEED).fit(rows, catalog=catalog_ids)

    assert np.allclose(fitted_tt.reader_embeddings, other.reader_embeddings)
    assert np.allclose(fitted_tt.item_embeddings, other.item_embeddings)
    # Identical top-k RANKING for several fitted readers (the behavioural reproducibility gate).
    reader_ids = fitted_tt.artifact()["reader_ids"]
    for reader_id in (reader_ids[0], reader_ids[len(reader_ids) // 2], reader_ids[-1]):
        a = [c.item_id for c in fitted_tt.retrieve(reader_id, {"seen": set()}, K)]
        b = [c.item_id for c in other.retrieve(reader_id, {"seen": set()}, K)]
        assert a == b
    # Bonus (not the gate): seeded init + seeded sampling are bit-identical on CPU here.
    assert np.array_equal(fitted_tt.reader_embeddings, other.reader_embeddings)
    assert np.array_equal(fitted_tt.item_embeddings, other.item_embeddings)


# --- a tiny hand-checkable BPR step reduces the pairwise loss --------------------------------


def _train_pos(reader_id: int, item_id: int) -> dict[str, object]:
    return {"reader_id": reader_id, "item_id": item_id, "split": "train", "label": 1}


def _bpr_loss(
    path: TwoTowerRetrievalPath, triples: list[tuple[int, int, int]]
) -> float:
    """Mean ``-log sigmoid(s_pos - s_neg)`` over (reader, positive, negative) triples (lower=better)."""
    art = path.artifact()
    readers, items = art["reader_embeddings"], art["item_embeddings"]
    reader_of = {r: i for i, r in enumerate(art["reader_ids"])}
    row_of = {it: i for i, it in enumerate(art["item_ids"])}
    losses = []
    for reader_id, pos_id, neg_id in triples:
        s_pos = float(readers[reader_of[reader_id]] @ items[row_of[pos_id]])
        s_neg = float(readers[reader_of[reader_id]] @ items[row_of[neg_id]])
        diff = s_pos - s_neg
        # -log sigmoid(diff) = log(1 + exp(-diff)), via logaddexp for numerical safety.
        losses.append(float(np.logaddexp(0.0, -diff)))
    return float(np.mean(losses))


def test_bpr_training_reduces_the_pairwise_loss() -> None:
    # Two taste clusters: readers 0-2 read books 10/11/12, readers 3-5 read books 20/21/22. BPR must
    # push each reader's positives ABOVE a cross-cluster negative, so the pairwise loss over
    # (reader, own-positive, other-cluster-item) triples FALLS as training proceeds. Deterministic.
    pairs = [(r, it) for r in (0, 1, 2) for it in (10, 11, 12)]
    pairs += [(r, it) for r in (3, 4, 5) for it in (20, 21, 22)]
    rows = [_train_pos(r, it) for r, it in pairs]
    catalog = [10, 11, 12, 20, 21, 22]
    # Hand-checkable triples: cluster-A readers' positives vs a cluster-B book, and vice versa.
    triples = [(r, it, 20) for r in (0, 1, 2) for it in (10, 11, 12)]
    triples += [(r, it, 10) for r in (3, 4, 5) for it in (20, 21, 22)]

    barely = TwoTowerRetrievalPath(n_epochs=1, seed=SEED).fit(rows, catalog=catalog)
    trained = TwoTowerRetrievalPath(n_epochs=60, seed=SEED).fit(rows, catalog=catalog)

    assert _bpr_loss(trained, triples) < _bpr_loss(barely, triples)
    # The recorded per-epoch loss also falls from first epoch to last (same descent, observed live).
    assert trained.loss_history[-1] < trained.loss_history[0]
    # After training, each reader scores its own cluster's book above the other cluster's.
    art = trained.artifact()
    readers, items = art["reader_embeddings"], art["item_embeddings"]
    reader_of = {r: i for i, r in enumerate(art["reader_ids"])}
    row_of = {it: i for i, it in enumerate(art["item_ids"])}
    s_pos = float(readers[reader_of[0]] @ items[row_of[10]])
    s_neg = float(readers[reader_of[0]] @ items[row_of[20]])
    assert s_pos > s_neg


def test_fit_terminates_when_a_reader_covers_the_whole_catalog() -> None:
    # Regression: a reader whose positives cover EVERY catalog item has an empty unobserved
    # complement, so its BPR triples are dropped (the collision-resampling loop must never spin
    # forever). Reader 0 covers all four books; reader 1 covers two. fit() returns quickly and
    # still learns an embedding for both readers.
    catalog = [10, 11, 12, 13]
    rows = [_train_pos(0, it) for it in catalog] + [_train_pos(1, 10), _train_pos(1, 11)]
    path = TwoTowerRetrievalPath(n_epochs=5, seed=SEED).fit(rows, catalog=catalog)
    reader_ids = set(path.artifact()["reader_ids"])
    assert {0, 1} <= reader_ids
    recs = path.retrieve(1, {"seen": []}, 3)
    assert len(recs) == 3


# --- leakage safety --------------------------------------------------------------------------


def test_embeddings_are_bit_identical_without_val_test_rows(generated: dict[str, object]) -> None:
    catalog_ids = generated["catalog_ids"]
    all_rows = generated["rows"]
    train_only = [row for row in all_rows if row["split"] == "train"]
    assert len(train_only) < len(all_rows)  # there really are val/test rows to drop

    # A reduced-epoch config keeps this cheap; leakage is structural (which rows become positives),
    # so it holds at any config. val/test rows and label==0 rows never touch the towers.
    full = TwoTowerRetrievalPath(n_epochs=5, seed=SEED).fit(all_rows, catalog=catalog_ids)
    trained = TwoTowerRetrievalPath(n_epochs=5, seed=SEED).fit(train_only, catalog=catalog_ids)
    assert np.array_equal(full.reader_embeddings, trained.reader_embeddings)
    assert np.array_equal(full.item_embeddings, trained.item_embeddings)


# --- retrieve contract -----------------------------------------------------------------------


def test_known_reader_with_empty_seen_still_returns_k(
    generated: dict[str, object], fitted_tt: TwoTowerRetrievalPath
) -> None:
    # The two-tower does not build its query from `seen`: a fitted reader is scored by
    # reader_emb . item_emb^T over the whole catalog regardless of whether `seen` is empty.
    reader_id = fitted_tt.artifact()["reader_ids"][0]
    recs = fitted_tt.retrieve(reader_id, {"seen": set()}, K)
    assert len(recs) == K
    assert all(c.provenance == "two-tower" for c in recs)
    assert recs == fitted_tt.retrieve(reader_id, {}, K)  # missing `seen` behaves like empty seen


def test_stale_seen_id_absent_from_catalog_is_ignored(
    generated: dict[str, object], fitted_tt: TwoTowerRetrievalPath
) -> None:
    # A `seen` id that is not in the catalog is simply ignored (not an error), as in Unit 5's MF.
    reader_id = fitted_tt.artifact()["reader_ids"][0]
    stale = max(generated["catalog_ids"]) + 10_000
    recs = fitted_tt.retrieve(reader_id, {"seen": {stale}}, K)
    assert len(recs) == K  # the stale id excludes nothing real
    assert recs == fitted_tt.retrieve(reader_id, {"seen": set()}, K)


def test_unknown_reader_returns_empty(fitted_tt: TwoTowerRetrievalPath) -> None:
    # A reader with no learned embedding (0 train positives / never seen in fit) -> [], not a crash.
    known = set(fitted_tt.artifact()["reader_ids"])
    unknown = next(r for r in range(10_000_000) if r not in known)
    assert fitted_tt.retrieve(unknown, {"seen": set()}, K) == []
    assert fitted_tt.retrieve(unknown, {"seen": {1, 2, 3}}, K) == []


def test_retrieve_excludes_seen_and_is_bounded(
    generated: dict[str, object], fitted_tt: TwoTowerRetrievalPath
) -> None:
    catalog_ids = generated["catalog_ids"]
    reader_id = fitted_tt.artifact()["reader_ids"][0]
    seen = {catalog_ids[0], catalog_ids[1], catalog_ids[2]}
    recs = fitted_tt.retrieve(reader_id, {"seen": seen}, K)
    assert len(recs) == K
    assert all(c.item_id not in seen for c in recs)
    assert all(c.provenance == "two-tower" for c in recs)


def test_fit_signature_is_protocol_substitutable(generated: dict[str, object]) -> None:
    # fit(interactions, catalog=None) — exactly the RetrievalPath protocol shape. Without a catalog,
    # the item universe falls back to the train-positive items, and a fitted reader still scores.
    path = TwoTowerRetrievalPath(n_epochs=5, seed=SEED)
    same = path.fit(generated["rows"])
    assert same is path
    reader_id = path.artifact()["reader_ids"][0]
    assert path.retrieve(reader_id, {"seen": set()}, K)


def test_fit_raises_on_no_train_positives() -> None:
    with pytest.raises(ValueError):
        TwoTowerRetrievalPath().fit([{"reader_id": 0, "item_id": 1, "split": "val", "label": 1}])


# --- artifact round-trip (torch-free load) ---------------------------------------------------


def test_fit_artifact_load_round_trip_without_torch(
    generated: dict[str, object], fitted_tt: TwoTowerRetrievalPath
) -> None:
    catalog_ids = generated["catalog_ids"]
    restored = TwoTowerRetrievalPath().load(fitted_tt.artifact())
    reader_ids = fitted_tt.artifact()["reader_ids"]
    for reader_seed in (3, 11, 42, 128):
        rng = np.random.default_rng(reader_seed)
        reader_id = reader_ids[int(rng.integers(0, len(reader_ids)))]
        seen = set(rng.choice(catalog_ids, size=4, replace=False).tolist())
        a = fitted_tt.retrieve(reader_id, {"seen": seen}, K)
        b = restored.retrieve(reader_id, {"seen": seen}, K)
        assert [c.item_id for c in a] == [c.item_id for c in b]
        assert [c.score for c in a] == [c.score for c in b]
        assert [c.provenance for c in a] == [c.provenance for c in b]
    # load copies arrays, never aliases the artifact's.
    artifact = fitted_tt.artifact()
    loaded = TwoTowerRetrievalPath().load(artifact)
    artifact["reader_embeddings"][0, 0] = 123.0
    assert loaded.reader_embeddings[0, 0] != 123.0


def test_load_rejects_malformed_embedding_shape(fitted_tt: TwoTowerRetrievalPath) -> None:
    artifact = fitted_tt.artifact()
    artifact["reader_embeddings"] = artifact["reader_embeddings"][:-1]  # one fewer row than ids
    with pytest.raises(ValueError):
        TwoTowerRetrievalPath().load(artifact)


# --- registry ownership + hyperparameter validation ------------------------------------------


def test_two_tower_registers_as_two_tower_v1(generated: dict[str, object]) -> None:
    registry = PathRegistry()
    path = TwoTowerRetrievalPath()
    registry.register(path)
    assert path.artifact_name() == "two-tower-v1"
    assert "two-tower" in registry
    # coexists with the other shipped paths (distinct names + artifacts).
    registry.register(RandomRetrievalPath(generated["catalog_ids"], seed=SEED))
    registry.register(PopularityRetrievalPath())
    registry.register(LexicalRetrievalPath(generated["keywords"]))
    registry.register(ItemItemRetrievalPath())
    registry.register(MatrixFactorizationPath())
    with pytest.raises(DuplicatePathError):
        registry.register(TwoTowerRetrievalPath())


def test_rejects_bad_hyperparameters() -> None:
    for kwargs in (
        {"embedding_dim": 0},
        {"n_epochs": -1},
        {"learning_rate": 0.0},
        {"n_negatives": 0},
        {"batch_size": 0},
        {"weight_decay": -0.1},  # negative is invalid...
    ):
        with pytest.raises(ValueError):
            TwoTowerRetrievalPath(**kwargs)
    # ...but weight_decay=0 is a VALID (overfitting-demo) config, not an error.
    assert TwoTowerRetrievalPath(weight_decay=0.0).weight_decay == 0.0
    with pytest.raises(TypeError):
        TwoTowerRetrievalPath(seed="x")  # type: ignore[arg-type]
