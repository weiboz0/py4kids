"""Unit 9 (recsys-011): the feature tower + item cold-start, on the recsys-004 interaction log.

Verifies the shipped `FeatureTowerRetrievalPath` (PyTorch, torch imported lazily inside `fit`) at the
Phase-B pinned config (`embedding_dim=32, n_epochs=40, learning_rate=0.01, n_negatives=10,
batch_size=256, weight_decay=1e-4, negative_pool="warm", seed=0`). The feature item tower combines an
id embedding with learned genre / author embeddings and a Linear projection of the Unit-7 GloVe
keyword vector, so a **cold item** (zero train positives) still gets a vector from its features.

The crux is a **validation-safe** metric — cold-item **COVERAGE**: the fraction of the 818 zero-train
items that appear in the top-10 of ANY fitted non-cold reader scored from that reader's TRAIN history
only (no held-out / val dependency — the generator leaves cold items without val positives). Measured
at 40ep / seed 0:

- feature-tower (warm-only negatives, shipped): warm hit@10 **0.298**, cold coverage **0.138**
  (113/818), cold hit@10 0.010 (1/97 incidental-cold-val readers);
- feature-tower (full-catalog negatives): warm 0.338, cold coverage 0.048 (39/818) — cold reach
  collapses because cold items become negatives-only;
- feature-tower (hard / popularity negatives): warm 0.172, cold coverage 0.226 — TRADES warm for cold;
- ID-only two-tower (Unit 8) and item-item CF: cold coverage exactly **0.000** (negative-shaped /
  unseen embeddings).

So the gate is directional and robust: feature-tower cold coverage > 0 AND > the ID-only two-tower's
(0), warm-only cold coverage > full-catalog cold coverage, and warm hit stays near the book's best
(>= 0.28, within 0.06 of the two-tower) — a warm/cold **compromise**, not dominance. Determinism is
tolerance / ranking based (design 011 §184): two seeded fits give identical top-k ranking + allclose
(bit-identical here is a printed bonus, never the gate). torch stays lazy (extended in test_unit07).
"""

from __future__ import annotations

import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pytest
from bookrec import (
    DuplicatePathError,
    FeatureTowerRetrievalPath,
    ItemItemRetrievalPath,
    LexicalRetrievalPath,
    PathRegistry,
    TwoTowerRetrievalPath,
    generated_dir,
    load_catalog,
    load_glove_subset,
    load_keywords,
    run_validation_scoreboard,
)

K = 10
SEED = 0
N_EPOCHS = 40  # Phase-B pinned (re-measured from Unit 8's 60ep; each full fit ~20-27s, << 120s cap)
WARM_GATE = 0.28  # feature-tower warm-only hit@10 measured 0.298 at 40ep; pinned with headroom


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
    catalog = load_catalog(gen / "catalog.csv.gz")
    cold = json.loads((gen / "cold_partitions.json").read_text())
    rows = _read_rows(gen / "interactions.csv.gz")

    # Train seen (per reader), zero-train items (the coverage denominator), and the incidental
    # cold-val cohort — all derived from TRAIN/val positives, no path involved.
    seen_by: dict[int, set[int]] = defaultdict(set)
    val_by: dict[int, set[int]] = defaultdict(set)
    train_pos_items: set[int] = set()
    for row in rows:
        if row["label"] != 1:
            continue
        if row["split"] == "train":
            seen_by[int(row["reader_id"])].add(int(row["item_id"]))
            train_pos_items.add(int(row["item_id"]))
        elif row["split"] == "val":
            val_by[int(row["reader_id"])].add(int(row["item_id"]))
    catalog_ids = sorted(catalog)
    zero_train = set(catalog_ids) - train_pos_items
    return {
        "catalog": catalog,
        "catalog_ids": catalog_ids,
        "keywords": load_keywords(gen / "keywords.csv.gz"),
        "glove": load_glove_subset(),
        "rows": rows,
        "interactions_path": gen / "interactions.csv.gz",
        "cold_readers": cold["cold_readers"],
        "seen_by": seen_by,
        "val_by": val_by,
        "zero_train": zero_train,
    }


def _warm_hit(path: object, generated: dict[str, object]) -> float:
    return run_validation_scoreboard(
        path,
        generated["interactions_path"],
        catalog_ids=generated["catalog_ids"],
        k=K,
        cold_readers=generated["cold_readers"],
    ).hit_rate_at_k


def _fitted_cohort(path: object, generated: dict[str, object]) -> list[int]:
    """ALL fitted non-cold readers (learned embedding, minus designated cold readers)."""
    cold = set(generated["cold_readers"])
    try:  # the two towers expose their fitted reader ids in the artifact
        fitted = [int(r) for r in path.artifact()["reader_ids"]]
    except KeyError:  # item-item CF has no reader embedding -> use the train cohort directly
        fitted = sorted(generated["seen_by"])
    return [r for r in fitted if r not in cold]


def _cold_coverage(path: object, generated: dict[str, object]) -> tuple[float, int]:
    """unique zero-train ids in top-10 / 818, over ALL fitted non-cold readers, TRAIN-only scoring.

    Deliberately NOT the scoreboard's held-out-positive eligible cohort: coverage must not depend on
    which readers happen to have a val positive (the denominator and cohort are validation-free).
    """
    zero_train = generated["zero_train"]
    seen_by = generated["seen_by"]
    surfaced: set[int] = set()
    for reader_id in _fitted_cohort(path, generated):
        for c in path.retrieve(reader_id, {"seen": seen_by[reader_id]}, K):
            if c.item_id in zero_train:
                surfaced.add(c.item_id)
    return len(surfaced) / len(zero_train), len(surfaced)


def _cold_hit_report(path: object, generated: dict[str, object]) -> tuple[float, int]:
    """REPORT-ONLY cold hit@10 on readers with a cold (zero-train) val positive (small-n; not a gate)."""
    zero_train = generated["zero_train"]
    seen_by, val_by = generated["seen_by"], generated["val_by"]
    cold_readers = set(generated["cold_readers"])
    hits: list[float] = []
    for reader_id in sorted(val_by):
        if reader_id in cold_readers:
            continue
        seen = seen_by[reader_id]
        cold_relevant = (val_by[reader_id] - seen) & zero_train
        if not cold_relevant:
            continue
        recs = {c.item_id for c in path.retrieve(reader_id, {"seen": seen}, K)}
        hits.append(1.0 if recs & cold_relevant else 0.0)
    return (sum(hits) / len(hits) if hits else 0.0), len(hits)


@pytest.fixture(scope="module")
def fitted_warm(generated: dict[str, object]) -> FeatureTowerRetrievalPath:
    # One full fit at the pinned warm-only config, shared across tests.
    return FeatureTowerRetrievalPath(
        generated["catalog"], generated["keywords"], generated["glove"],
        n_epochs=N_EPOCHS, negative_pool="warm", seed=SEED,
    ).fit(generated["rows"], catalog=generated["catalog_ids"])


@pytest.fixture(scope="module")
def fitted_id_only(generated: dict[str, object]) -> TwoTowerRetrievalPath:
    # The Unit-8 ID-only two-tower (full-catalog negatives) at its shipped config: the cold baseline.
    return TwoTowerRetrievalPath(seed=SEED).fit(
        generated["rows"], catalog=generated["catalog_ids"]
    )


# --- gate 1: warm hit@10 stays near the book's best (not tanked) ------------------------------


def test_warm_hit_at_10_stays_near_the_best(
    generated: dict[str, object],
    fitted_warm: FeatureTowerRetrievalPath,
    fitted_id_only: TwoTowerRetrievalPath,
) -> None:
    ft_warm = _warm_hit(fitted_warm, generated)
    id_warm = _warm_hit(fitted_id_only, generated)
    print(f"\n[warm hit@10] feature-tower warm={ft_warm:.4f}  ID-only two-tower={id_warm:.4f}")
    # Measured: feature-tower warm-only 0.298, two-tower ~0.340. The feature tower trades a little
    # warm accuracy for cold reach (gate 2) but must NOT tank: >= 0.28 and within 0.06 of the best.
    assert ft_warm >= WARM_GATE
    assert ft_warm >= id_warm - 0.06


# --- gate 2: cold-item COVERAGE (the crux) ----------------------------------------------------


def test_cold_item_coverage_beats_id_only(
    generated: dict[str, object],
    fitted_warm: FeatureTowerRetrievalPath,
    fitted_id_only: TwoTowerRetrievalPath,
) -> None:
    assert len(generated["zero_train"]) == 818  # the validation-free denominator
    ft_cov, ft_n = _cold_coverage(fitted_warm, generated)
    id_cov, id_n = _cold_coverage(fitted_id_only, generated)
    print(f"\n[cold coverage /818] feature-tower warm={ft_cov:.4f} ({ft_n})  ID-only={id_cov:.4f} ({id_n})")
    # ID-only two-tower buries every cold item (negative-shaped id embedding) -> exactly 0.
    assert id_cov == 0.0 and id_n == 0
    # The feature tower surfaces cold items from their features: > 0 AND strictly > the ID-only base.
    assert ft_cov > 0.0
    assert ft_cov > id_cov


def test_item_item_cf_also_has_zero_cold_coverage(generated: dict[str, object]) -> None:
    # The other collaborative baseline: CF gives cold items zero co-occurrence -> coverage 0.
    cf = ItemItemRetrievalPath().fit(generated["rows"], catalog=generated["catalog_ids"])
    cf_cov, cf_n = _cold_coverage(cf, generated)
    print(f"\n[cold coverage /818] item-item CF={cf_cov:.4f} ({cf_n})")
    assert cf_cov == 0.0 and cf_n == 0


# --- report-only: cold hit@10 on the incidental-cold-val readers (NOT a gate) -----------------


def test_cold_hit_at_10_is_reported_and_not_below_id_only(
    generated: dict[str, object],
    fitted_warm: FeatureTowerRetrievalPath,
    fitted_id_only: TwoTowerRetrievalPath,
) -> None:
    ft_hit, ft_readers = _cold_hit_report(fitted_warm, generated)
    id_hit, id_readers = _cold_hit_report(fitted_id_only, generated)
    print(
        f"\n[REPORT-ONLY cold hit@10] feature-tower={ft_hit:.4f} ID-only={id_hit:.4f} "
        f"(n={ft_readers} incidental-cold-val readers)"
    )
    assert ft_readers == id_readers == 97  # the incidental cohort is fixed by the data
    # Small-n and report-only: we only bind that the feature tower is not WORSE than the ID-only base.
    assert ft_hit >= id_hit


# --- gate 3: the negative pool is the mechanism (warm-only vs full-catalog vs hard) ------------


def test_negative_pool_controls_cold_reach(
    generated: dict[str, object], fitted_warm: FeatureTowerRetrievalPath
) -> None:
    rows, catalog_ids = generated["rows"], generated["catalog_ids"]
    common = {"n_epochs": N_EPOCHS, "seed": SEED}

    # warm is the shared shipped fixture; only the two ablations are fit here.
    full = FeatureTowerRetrievalPath(
        generated["catalog"], generated["keywords"], generated["glove"],
        negative_pool="full", **common,
    ).fit(rows, catalog=catalog_ids)
    hard = FeatureTowerRetrievalPath(
        generated["catalog"], generated["keywords"], generated["glove"],
        negative_pool="hard", **common,
    ).fit(rows, catalog=catalog_ids)

    warm_cov, _ = _cold_coverage(fitted_warm, generated)
    full_cov, _ = _cold_coverage(full, generated)
    hard_cov, _ = _cold_coverage(hard, generated)
    warm_hit, full_hit, hard_hit = (
        _warm_hit(fitted_warm, generated), _warm_hit(full, generated), _warm_hit(hard, generated)
    )
    print(
        f"\n[negative pool @40ep] warm: hit={warm_hit:.4f} cov={warm_cov:.4f} | "
        f"full: hit={full_hit:.4f} cov={full_cov:.4f} | hard: hit={hard_hit:.4f} cov={hard_cov:.4f}"
    )
    # THE mechanism: drawing negatives from the full catalog makes the 818 cold items negatives-only,
    # so their coverage collapses vs warm-only (measured 0.138 warm vs 0.048 full).
    assert warm_cov > full_cov
    # hard (popularity-weighted over the warm universe) TRADES warm accuracy for cold reach — it does
    # NOT sharpen both (measured warm 0.172 < 0.298, cov 0.226 > 0.138).
    assert hard_cov > warm_cov
    assert hard_hit < warm_hit


# --- determinism (design 011 §184: ranking + allclose; array_equal is a printed bonus) --------


def test_feature_tower_is_deterministic(
    generated: dict[str, object], fitted_warm: FeatureTowerRetrievalPath
) -> None:
    other = FeatureTowerRetrievalPath(
        generated["catalog"], generated["keywords"], generated["glove"],
        n_epochs=N_EPOCHS, negative_pool="warm", seed=SEED,
    ).fit(generated["rows"], catalog=generated["catalog_ids"])

    assert np.allclose(fitted_warm.reader_embeddings, other.reader_embeddings)
    assert np.allclose(fitted_warm.item_embeddings, other.item_embeddings)
    reader_ids = fitted_warm.artifact()["reader_ids"]
    for reader_id in (reader_ids[0], reader_ids[len(reader_ids) // 2], reader_ids[-1]):
        a = [c.item_id for c in fitted_warm.retrieve(reader_id, {"seen": set()}, K)]
        b = [c.item_id for c in other.retrieve(reader_id, {"seen": set()}, K)]
        assert a == b
    bitwise_identical = bool(
        np.array_equal(fitted_warm.reader_embeddings, other.reader_embeddings)
        and np.array_equal(fitted_warm.item_embeddings, other.item_embeddings)
    )
    print(f"(bonus) seeded feature-tower fits bit-identical on this CPU: {bitwise_identical}")


# --- retrieve contract ------------------------------------------------------------------------


def test_known_reader_with_empty_seen_still_returns_k(
    fitted_warm: FeatureTowerRetrievalPath,
) -> None:
    reader_id = fitted_warm.artifact()["reader_ids"][0]
    recs = fitted_warm.retrieve(reader_id, {"seen": set()}, K)
    assert len(recs) == K
    assert all(c.provenance == "feature-tower" for c in recs)
    assert recs == fitted_warm.retrieve(reader_id, {}, K)  # missing `seen` == empty seen


def test_unknown_reader_returns_empty(fitted_warm: FeatureTowerRetrievalPath) -> None:
    known = set(fitted_warm.artifact()["reader_ids"])
    unknown = next(r for r in range(10_000_000) if r not in known)
    assert fitted_warm.retrieve(unknown, {"seen": set()}, K) == []
    assert fitted_warm.retrieve(unknown, {"seen": {1, 2, 3}}, K) == []


def test_retrieve_excludes_seen_and_is_bounded(
    generated: dict[str, object], fitted_warm: FeatureTowerRetrievalPath
) -> None:
    catalog_ids = generated["catalog_ids"]
    reader_id = fitted_warm.artifact()["reader_ids"][0]
    seen = {catalog_ids[0], catalog_ids[1], catalog_ids[2]}
    recs = fitted_warm.retrieve(reader_id, {"seen": seen}, K)
    assert len(recs) == K
    assert all(c.item_id not in seen for c in recs)


def test_a_cold_item_can_score_above_a_warm_item(
    generated: dict[str, object], fitted_warm: FeatureTowerRetrievalPath
) -> None:
    # A cold (zero-train) item still gets a feature-based row, so SOME fitted reader ranks at least
    # one zero-train item inside its top-10 (coverage > 0 restated as a concrete, item-level claim).
    _, surfaced = _cold_coverage(fitted_warm, generated)
    assert surfaced > 0


def test_fit_signature_is_protocol_substitutable(generated: dict[str, object]) -> None:
    # fit(interactions, catalog=None): without a catalog the item universe is every constructor book.
    path = FeatureTowerRetrievalPath(
        generated["catalog"], generated["keywords"], generated["glove"], n_epochs=2, seed=SEED
    )
    same = path.fit(generated["rows"])
    assert same is path
    reader_id = path.artifact()["reader_ids"][0]
    assert path.retrieve(reader_id, {"seen": set()}, K)


def test_fit_raises_on_no_train_positives(generated: dict[str, object]) -> None:
    path = FeatureTowerRetrievalPath(
        generated["catalog"], generated["keywords"], generated["glove"], n_epochs=2, seed=SEED
    )
    with pytest.raises(ValueError):
        path.fit([{"reader_id": 0, "item_id": 1, "split": "val", "label": 1}])


# --- artifact round-trip (torch-free; composed numpy item matrix) -----------------------------


def test_fit_artifact_load_round_trip_without_torch(
    generated: dict[str, object], fitted_warm: FeatureTowerRetrievalPath
) -> None:
    catalog_ids = generated["catalog_ids"]
    art = fitted_warm.artifact()
    # artifact persists the COMPOSED item matrix (one row per catalog item), not sub-embeddings.
    assert art["item_embeddings"].shape == (len(catalog_ids), fitted_warm.embedding_dim)
    assert art["params"]["negative_pool"] == "warm"

    restored = FeatureTowerRetrievalPath(
        generated["catalog"], generated["keywords"], generated["glove"]
    ).load(art)
    reader_ids = art["reader_ids"]
    for reader_seed in (3, 11, 42, 128):
        rng = np.random.default_rng(reader_seed)
        reader_id = reader_ids[int(rng.integers(0, len(reader_ids)))]
        seen = set(rng.choice(catalog_ids, size=4, replace=False).tolist())
        a = fitted_warm.retrieve(reader_id, {"seen": seen}, K)
        b = restored.retrieve(reader_id, {"seen": seen}, K)
        assert [c.item_id for c in a] == [c.item_id for c in b]
        assert [c.score for c in a] == [c.score for c in b]
        assert [c.provenance for c in a] == [c.provenance for c in b]
    # load copies arrays, never aliases the artifact's.
    art2 = fitted_warm.artifact()
    loaded = FeatureTowerRetrievalPath(
        generated["catalog"], generated["keywords"], generated["glove"]
    ).load(art2)
    art2["item_embeddings"][0, 0] = 123.0
    assert loaded.item_embeddings[0, 0] != 123.0


def test_load_rejects_malformed_embedding_shape(
    generated: dict[str, object], fitted_warm: FeatureTowerRetrievalPath
) -> None:
    art = fitted_warm.artifact()
    art["reader_embeddings"] = art["reader_embeddings"][:-1]  # one fewer row than ids
    with pytest.raises(ValueError):
        FeatureTowerRetrievalPath(
            generated["catalog"], generated["keywords"], generated["glove"]
        ).load(art)


# --- registry ownership + hyperparameter validation ------------------------------------------


def test_feature_tower_registers_as_feature_tower_v1(generated: dict[str, object]) -> None:
    registry = PathRegistry()
    path = FeatureTowerRetrievalPath(
        generated["catalog"], generated["keywords"], generated["glove"]
    )
    registry.register(path)
    assert path.artifact_name() == "feature-tower-v1"
    assert "feature-tower" in registry
    # coexists with the other learned paths (distinct name + artifact).
    registry.register(TwoTowerRetrievalPath())
    registry.register(LexicalRetrievalPath(generated["keywords"]))
    with pytest.raises(DuplicatePathError):
        registry.register(
            FeatureTowerRetrievalPath(
                generated["catalog"], generated["keywords"], generated["glove"]
            )
        )


def test_rejects_bad_hyperparameters(generated: dict[str, object]) -> None:
    books, kw, glove = generated["catalog"], generated["keywords"], generated["glove"]
    for kwargs in (
        {"embedding_dim": 0},
        {"n_epochs": -1},
        {"learning_rate": 0.0},
        {"n_negatives": 0},
        {"batch_size": 0},
        {"weight_decay": -0.1},
        {"negative_pool": "uniform"},  # only warm / full / hard are valid
    ):
        with pytest.raises(ValueError):
            FeatureTowerRetrievalPath(books, kw, glove, **kwargs)
    assert FeatureTowerRetrievalPath(books, kw, glove, weight_decay=0.0).weight_decay == 0.0
    with pytest.raises(TypeError):
        FeatureTowerRetrievalPath(books, kw, glove, seed="x")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        FeatureTowerRetrievalPath({}, kw, glove)  # empty catalog
    with pytest.raises(ValueError):
        FeatureTowerRetrievalPath(books, {}, glove)  # empty keyword corpus
