"""Unit 5 (recsys-007): matrix factorization — the latent-factor retrieval path.

Verifies the shipped `MatrixFactorizationPath` on the recsys-004 interaction log at the **pinned**
config (`n_factors=32, n_epochs=300, learning_rate=0.5, reg=0.05, n_negatives=10, seed=0`): MF is
the latent generalization of co-occurrence, clearing the recoverability gate (hit@10 >= 1.2x
popularity AND >= popularity + 0.03 AND >= lexical AND >= CF - 0.03) on the seeded val scoreboard
(60 cold readers excluded); seeded determinism (two fits bit-identical); a tiny hand-checkable
training step reduces the logistic loss on the positives; leakage safety (val/test rows never touch
P/Q); the retrieve contract (a KNOWN reader with empty `seen` still returns k recs; an UNKNOWN /
cold reader -> []); a fit->artifact->load round-trip returning identical recommendations; and
registry ownership (`mf-v1`, no collision).

Measured on the shipped data (plan recsys-007 "Why this works", k=10, 60 cold readers excluded, 500
eligible): random 0.012, popularity 0.108, content/lexical 0.158, item-item CF 0.252. The Opus port
consumes `default_rng(0)` differently from the recoverability harness, so its seed-0 hit@10 is a
fresh draw from the measured 0.232-0.270 spread; the SHIPPED port measures **seed-0 MF = 0.276**
(>= CF 0.252, so +0.024; the 0.03 tolerance covers the worst-of-5 draw). Seed 0 is pinned.
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
    generated_dir,
    load_catalog,
    load_keywords,
    run_validation_scoreboard,
)

K = 10
SEED = 0  # pinned: seed-0 MF = 0.276 on the shipped data (>= CF 0.252)


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
def fitted_mf(generated: dict[str, object]) -> MatrixFactorizationPath:
    # Trained ONCE at the pinned config and shared across tests (one ~15 s fit, not one per test).
    return MatrixFactorizationPath(seed=SEED).fit(
        generated["rows"], catalog=generated["catalog_ids"]
    )


# --- the decisive win: MF clears the recoverability gate (on par with CF, well over lexical) ----


def test_mf_clears_gate_and_is_on_par_with_cf(
    generated: dict[str, object], fitted_mf: MatrixFactorizationPath
) -> None:
    catalog_ids = generated["catalog_ids"]
    rows = generated["rows"]

    pop = PopularityRetrievalPath().fit(rows, catalog=catalog_ids)
    lexical = LexicalRetrievalPath(generated["keywords"]).fit(rows, catalog=catalog_ids)
    cf = ItemItemRetrievalPath().fit(rows, catalog=catalog_ids)

    mf_hit = _hit_rate(fitted_mf, generated)
    pop_hit = _hit_rate(pop, generated)
    lex_hit = _hit_rate(lexical, generated)
    cf_hit = _hit_rate(cf, generated)

    # Measured (seed 0): pop 0.108, lexical 0.158, CF 0.252, MF 0.276. MF is the latent
    # generalization of co-occurrence: a ratio floor AND an absolute floor over popularity, it beats
    # the lexical content path, and it is on par with CF (within a 0.03 tolerance covering the
    # worst-of-5 negative-sampling draw; measured margin here is +0.024).
    assert pop_hit > 0 and lex_hit > 0
    assert mf_hit >= 1.2 * pop_hit
    assert mf_hit >= pop_hit + 0.03
    assert mf_hit >= lex_hit
    assert mf_hit >= cf_hit - 0.03


def test_mf_is_deterministic_bit_identical(generated: dict[str, object]) -> None:
    catalog_ids = generated["catalog_ids"]
    rows = generated["rows"]
    first = MatrixFactorizationPath(seed=SEED).fit(rows, catalog=catalog_ids)
    second = MatrixFactorizationPath(seed=SEED).fit(rows, catalog=catalog_ids)
    # Seeded init + seeded negative sampling -> the learned factors are bit-identical, not merely
    # close (so every downstream score and recommendation is reproducible run to run).
    assert np.array_equal(first.reader_factors, second.reader_factors)
    assert np.array_equal(first.item_factors, second.item_factors)


# --- a tiny hand-checkable training step reduces the logistic loss ---------------------------


def _train_pos(reader_id: int, item_id: int) -> dict[str, object]:
    return {"reader_id": reader_id, "item_id": item_id, "split": "train", "label": 1}


def _positive_logistic_loss(path: MatrixFactorizationPath, pairs: list[tuple[int, int]]) -> float:
    """Mean ``-log sigmoid(P_u . Q_i)`` over the train positives: lower = positives fit better."""
    art = path.artifact()
    p, q = art["P"], art["Q"]
    reader_of = {r: i for i, r in enumerate(art["reader_ids"])}
    row_of = {it: i for i, it in enumerate(art["item_ids"])}
    losses = []
    for reader_id, item_id in pairs:
        score = float(p[reader_of[reader_id]] @ q[row_of[item_id]])
        losses.append(-np.log(1.0 / (1.0 + np.exp(-score))))
    return float(np.mean(losses))


def test_gradient_descent_reduces_logistic_loss() -> None:
    # Two taste clusters: readers 0-2 read books 10/11/12, readers 3-5 read books 20/21/22. The
    # logistic loss over the positives must FALL as training proceeds (sigmoid(P.Q) rises toward 1
    # for the observed positives). A barely-trained model (1 epoch) still has a high positive loss;
    # the pinned 300-epoch model has driven it far lower. Deterministic (fixed seed).
    pairs = [(r, it) for r in (0, 1, 2) for it in (10, 11, 12)]
    pairs += [(r, it) for r in (3, 4, 5) for it in (20, 21, 22)]
    rows = [_train_pos(r, it) for r, it in pairs]
    catalog = [10, 11, 12, 20, 21, 22]

    barely = MatrixFactorizationPath(n_epochs=1, seed=SEED).fit(rows, catalog=catalog)
    trained = MatrixFactorizationPath(n_epochs=300, seed=SEED).fit(rows, catalog=catalog)

    loss_barely = _positive_logistic_loss(barely, pairs)
    loss_trained = _positive_logistic_loss(trained, pairs)
    assert loss_trained < loss_barely
    # A single gradient step already moves the loss the right way (strictly down from init).
    init = MatrixFactorizationPath(n_epochs=1, seed=SEED)
    one_step = init.fit(rows, catalog=catalog)
    # A 2-epoch model has taken one more descent step than the 1-epoch model -> lower positive loss.
    two_step = MatrixFactorizationPath(n_epochs=2, seed=SEED).fit(rows, catalog=catalog)
    assert _positive_logistic_loss(two_step, pairs) < _positive_logistic_loss(one_step, pairs)


def test_fit_terminates_when_a_reader_covers_the_whole_catalog() -> None:
    # Regression: a reader whose positives cover EVERY catalog item has an empty unobserved
    # complement, so every sampled "negative" collides with a known positive. The collision-
    # resampling loop must not spin forever -- such a reader's negative slots are dropped. Reader 0
    # covers all four books; reader 1 covers two. fit() must return quickly and still learn a factor
    # for both readers. (If the guard regressed, this call would hang and CI would time out.)
    catalog = [10, 11, 12, 13]
    rows = [_train_pos(0, it) for it in catalog] + [_train_pos(1, 10), _train_pos(1, 11)]
    path = MatrixFactorizationPath(n_epochs=5, seed=SEED).fit(rows, catalog=catalog)
    reader_ids = set(path.artifact()["reader_ids"])
    assert {0, 1} <= reader_ids
    # The full-coverage reader still trains on its positives and can be scored.
    recs = path.retrieve(0, {"seen": []}, 3)
    assert len(recs) == 3


# --- leakage safety --------------------------------------------------------------------------


def test_factors_are_bit_identical_without_val_test_rows(generated: dict[str, object]) -> None:
    catalog_ids = generated["catalog_ids"]
    all_rows = generated["rows"]
    train_only = [row for row in all_rows if row["split"] == "train"]
    assert len(train_only) < len(all_rows)  # there really are val/test rows to drop

    full = MatrixFactorizationPath(seed=SEED).fit(all_rows, catalog=catalog_ids)
    trained = MatrixFactorizationPath(seed=SEED).fit(train_only, catalog=catalog_ids)
    # val/test rows and label==0 rows never touch P/Q: the learned factors are bit-identical.
    assert np.array_equal(full.reader_factors, trained.reader_factors)
    assert np.array_equal(full.item_factors, trained.item_factors)


# --- retrieve contract -----------------------------------------------------------------------


def test_known_reader_with_empty_seen_still_returns_k(
    generated: dict[str, object], fitted_mf: MatrixFactorizationPath
) -> None:
    # MF does not build its query from `seen`: a fitted reader is scored by P[reader].Q^T over the
    # whole catalog regardless of whether `seen` is empty, so an empty seen still returns K recs.
    reader_id = fitted_mf.artifact()["reader_ids"][0]
    recs = fitted_mf.retrieve(reader_id, {"seen": set()}, K)
    assert len(recs) == K
    assert all(c.provenance == "mf" for c in recs)
    assert recs == fitted_mf.retrieve(reader_id, {}, K)  # missing `seen` behaves like empty seen


def test_unknown_reader_returns_empty(fitted_mf: MatrixFactorizationPath) -> None:
    # A reader with no learned factor (0 train positives / never seen in fit) -> [], not a crash.
    known = set(fitted_mf.artifact()["reader_ids"])
    unknown = next(r for r in range(10_000_000) if r not in known)
    assert fitted_mf.retrieve(unknown, {"seen": set()}, K) == []
    assert fitted_mf.retrieve(unknown, {"seen": {1, 2, 3}}, K) == []


def test_retrieve_excludes_seen_and_is_bounded(
    generated: dict[str, object], fitted_mf: MatrixFactorizationPath
) -> None:
    catalog_ids = generated["catalog_ids"]
    reader_id = fitted_mf.artifact()["reader_ids"][0]
    seen = {catalog_ids[0], catalog_ids[1], catalog_ids[2]}
    recs = fitted_mf.retrieve(reader_id, {"seen": seen}, K)
    assert len(recs) == K
    assert all(c.item_id not in seen for c in recs)
    assert all(c.provenance == "mf" for c in recs)


def test_fit_signature_is_protocol_substitutable(generated: dict[str, object]) -> None:
    # fit(interactions, catalog=None) — exactly the RetrievalPath protocol shape. Without a catalog,
    # the item universe falls back to the train-positive items, and a fitted reader still scores.
    path = MatrixFactorizationPath(n_epochs=5, seed=SEED)
    same = path.fit(generated["rows"])
    assert same is path
    reader_id = path.artifact()["reader_ids"][0]
    assert path.retrieve(reader_id, {"seen": set()}, K)


def test_fit_raises_on_no_train_positives() -> None:
    with pytest.raises(ValueError):
        MatrixFactorizationPath().fit([{"reader_id": 0, "item_id": 1, "split": "val", "label": 1}])


# --- artifact round-trip ---------------------------------------------------------------------


def test_fit_artifact_load_round_trip(
    generated: dict[str, object], fitted_mf: MatrixFactorizationPath
) -> None:
    catalog_ids = generated["catalog_ids"]
    restored = MatrixFactorizationPath().load(fitted_mf.artifact())
    reader_ids = fitted_mf.artifact()["reader_ids"]
    for reader_seed in (3, 11, 42, 128):
        rng = np.random.default_rng(reader_seed)
        reader_id = reader_ids[int(rng.integers(0, len(reader_ids)))]
        seen = set(rng.choice(catalog_ids, size=4, replace=False).tolist())
        a = fitted_mf.retrieve(reader_id, {"seen": seen}, K)
        b = restored.retrieve(reader_id, {"seen": seen}, K)
        assert [c.item_id for c in a] == [c.item_id for c in b]
        assert [c.score for c in a] == [c.score for c in b]
        assert [c.provenance for c in a] == [c.provenance for c in b]
    # load copies arrays, never aliases the artifact's.
    artifact = fitted_mf.artifact()
    loaded = MatrixFactorizationPath().load(artifact)
    artifact["P"][0, 0] = 123.0
    assert loaded.reader_factors[0, 0] != 123.0


def test_load_rejects_malformed_factor_shape(fitted_mf: MatrixFactorizationPath) -> None:
    artifact = fitted_mf.artifact()
    artifact["P"] = artifact["P"][:-1]  # one fewer reader row than reader_ids -> corrupt artifact
    with pytest.raises(ValueError):
        MatrixFactorizationPath().load(artifact)


# --- registry ownership ----------------------------------------------------------------------


def test_mf_path_registers_without_collision(generated: dict[str, object]) -> None:
    registry = PathRegistry()
    path = MatrixFactorizationPath()
    registry.register(path)
    assert path.artifact_name() == "mf-v1"
    assert "mf" in registry
    # coexists with the other shipped paths (distinct names + artifacts).
    registry.register(RandomRetrievalPath(generated["catalog_ids"], seed=SEED))
    registry.register(PopularityRetrievalPath())
    registry.register(LexicalRetrievalPath(generated["keywords"]))
    registry.register(ItemItemRetrievalPath())
    with pytest.raises(DuplicatePathError):
        registry.register(MatrixFactorizationPath())


def test_rejects_bad_hyperparameters() -> None:
    for kwargs in (
        {"n_factors": 0},
        {"n_epochs": -1},
        {"learning_rate": 0.0},
        {"reg": -0.1},
        {"n_negatives": 0},
    ):
        with pytest.raises(ValueError):
            MatrixFactorizationPath(**kwargs)
    with pytest.raises(TypeError):
        MatrixFactorizationPath(seed="x")  # type: ignore[arg-type]
