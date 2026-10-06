"""Unit 10 (recsys-012): approximate nearest neighbours (ANN/FAISS) + hybrid retrieval.

Verifies, on the seeded recsys-004 interaction log and the Unit-8 two-tower (seed 0, the shipped
dense source), the two paths this unit ships:

- :class:`~bookrec.ann.AnnRetrievalPath` over a FAISS **HNSW** index built ``METRIC_INNER_PRODUCT``
  so it ranks the SAME ``reader . item`` dot product the two-tower's exact scan uses. ANN is a
  **speed** technique that *preserves* accuracy: at the pinned ``M=32 / efConstruction=200 /
  efSearch=64`` it recovers the exact top-10 at **recall >= 0.98** (measured ~0.9991) and its hit@10
  equals the exact two-tower (measured 0.340, Δ0). The gate is recall-vs-exact + determinism (design
  §184: identical neighbour ids + ``allclose`` scores on two single-thread builds — never exact
  neighbour identity against the brute force), plus a **generous absolute latency ceiling** (< 1 s,
  measured ~18 ms over the cohort), NOT a 2,000-item speedup (the speed win is asymptotic).
- :class:`~bookrec.hybrid.HybridRetrievalPath` fusing BM25 (Unit 3) + the two-tower (Unit 8). The
  honest, measured story: the dense tower dominates and only a *tuned, dense-heavy* weighted fusion
  (``pool=50, weight=0.7``) gives a **small** lift on BOTH hit@10 (~0.362) and coverage (~0.192) —
  gated directionally (``hit >= two_tower.hit - 0.01`` AND ``coverage > two_tower.coverage``), NOT a
  strict ``hybrid > two-tower``. Equal weights HURT and standard RRF loses (recorded, not asserted).

CPU-deterministic; routed ``--group recsys`` (FAISS-cpu). ``faiss`` is only ever imported lazily
inside the index build/search surface (proven by the import-blocked subprocess in test_unit07).
"""

from __future__ import annotations

import csv
import gzip
import json
import time
from pathlib import Path

import numpy as np
import pytest
from bookrec import (
    AnnRetrievalPath,
    DuplicatePathError,
    HnswIndex,
    HybridRetrievalPath,
    LexicalRetrievalPath,
    PathRegistry,
    TwoTowerRetrievalPath,
    generated_dir,
    load_catalog,
    load_keywords,
    run_blended_scoreboard,
    run_validation_scoreboard,
)

K = 10
SEED = 0  # pinned: seed-0 two-tower hit@10 ~0.340 on the shipped data (the dense source ANN indexes)
M = 32
EF_CONSTRUCTION = 200
EF_SEARCH = 64  # pinned: recall@10 vs exact ~0.9991 (>= the 0.98 gate)


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


@pytest.fixture(scope="module")
def fitted_tt(generated: dict[str, object]) -> TwoTowerRetrievalPath:
    # The shipped dense source, trained ONCE at the pinned config and shared across tests.
    return TwoTowerRetrievalPath(seed=SEED).fit(
        generated["rows"], catalog=generated["catalog_ids"]
    )


@pytest.fixture(scope="module")
def dense_matrices(fitted_tt: TwoTowerRetrievalPath) -> dict[str, object]:
    art = fitted_tt.artifact()
    return {
        "item_matrix": np.ascontiguousarray(np.asarray(art["item_embeddings"], dtype=np.float32)),
        "reader_matrix": np.ascontiguousarray(np.asarray(art["reader_embeddings"], dtype=np.float32)),
        "item_ids": [int(i) for i in art["item_ids"]],
        "reader_ids": [int(r) for r in art["reader_ids"]],
    }


@pytest.fixture(scope="module")
def fitted_ann(
    generated: dict[str, object], fitted_tt: TwoTowerRetrievalPath
) -> AnnRetrievalPath:
    return AnnRetrievalPath(fitted_tt, efSearch=EF_SEARCH, m=M, ef_construction=EF_CONSTRUCTION).fit(
        generated["rows"], catalog=generated["catalog_ids"]
    )


def _exact_top_rows(reader_matrix: np.ndarray, item_matrix: np.ndarray, k: int) -> np.ndarray:
    """Exact top-k item ROW indices per reader by inner product (the brute-force reference)."""
    scores = reader_matrix @ item_matrix.T
    return np.argsort(-scores, axis=1)[:, :k]


def _ann_recall(index: HnswIndex, reader_matrix: np.ndarray, exact_top: np.ndarray, ef: int) -> float:
    """Mean per-reader overlap@k between the ANN neighbours and the exact top-k (both in row space)."""
    labels, _ = index.search(reader_matrix, exact_top.shape[1], efSearch=ef)
    k = exact_top.shape[1]
    overlaps = []
    for i in range(reader_matrix.shape[0]):
        ann_rows = {int(x) for x in labels[i] if x >= 0}
        exact_rows = {int(x) for x in exact_top[i]}
        overlaps.append(len(ann_rows & exact_rows) / k)
    return float(np.mean(overlaps))


# --- ANN recall vs exact brute force (the core gate: ANN approximates the exact scan) ---------


def test_ann_recall_at_10_vs_exact_is_high_at_pinned_efsearch(
    dense_matrices: dict[str, object], fitted_ann: AnnRetrievalPath
) -> None:
    reader_matrix = dense_matrices["reader_matrix"]
    item_matrix = dense_matrices["item_matrix"]
    exact_top = _exact_top_rows(reader_matrix, item_matrix, K)
    recall = _ann_recall(fitted_ann.index, reader_matrix, exact_top, EF_SEARCH)
    # Measured ~0.9991 at M=32/efC=200/efSearch=64; the 0.98 gate bites (0.9 would not).
    assert recall >= 0.98


def test_ann_hit_at_10_equals_exact_two_tower(
    generated: dict[str, object],
    fitted_tt: TwoTowerRetrievalPath,
    fitted_ann: AnnRetrievalPath,
) -> None:
    kwargs = {
        "catalog_ids": generated["catalog_ids"],
        "k": K,
        "cold_readers": generated["cold_readers"],
    }
    tt_hit = run_validation_scoreboard(fitted_tt, generated["interactions_path"], **kwargs).hit_rate_at_k
    ann_hit = run_validation_scoreboard(fitted_ann, generated["interactions_path"], **kwargs).hit_rate_at_k
    # ANN is a SPEED technique, not an accuracy one: its hit@10 matches the exact two-tower (Δ0
    # measured). A small tolerance absorbs the handful of readers whose top-10 the approximation reorders.
    assert ann_hit == pytest.approx(tt_hit, abs=0.005)


def test_hnsw_build_is_deterministic(dense_matrices: dict[str, object]) -> None:
    item_matrix = dense_matrices["item_matrix"]
    item_ids = dense_matrices["item_ids"]
    reader_matrix = dense_matrices["reader_matrix"]
    # Two independently-built single-thread indices. Design §184: identical neighbour ids +
    # allclose scores is the gate (NOT exact-float — faiss returns float32 inner products).
    first = HnswIndex(item_matrix, item_ids, m=M, ef_construction=EF_CONSTRUCTION)
    second = HnswIndex(item_matrix, item_ids, m=M, ef_construction=EF_CONSTRUCTION)
    labels_a, scores_a = first.search(reader_matrix, K, efSearch=EF_SEARCH)
    labels_b, scores_b = second.search(reader_matrix, K, efSearch=EF_SEARCH)
    assert np.array_equal(labels_a, labels_b)
    assert np.allclose(scores_a, scores_b)


def test_recall_rises_from_low_to_high_efsearch(dense_matrices: dict[str, object]) -> None:
    reader_matrix = dense_matrices["reader_matrix"]
    item_matrix = dense_matrices["item_matrix"]
    item_ids = dense_matrices["item_ids"]
    index = HnswIndex(item_matrix, item_ids, m=M, ef_construction=EF_CONSTRUCTION)
    exact_top = _exact_top_rows(reader_matrix, item_matrix, K)
    recall_low = _ann_recall(index, reader_matrix, exact_top, ef=8)
    recall_high = _ann_recall(index, reader_matrix, exact_top, ef=128)
    # Endpoints only (NOT strict per-step monotonicity — recall can plateau/tie near 1.0). A tiny
    # tolerance guards against a float tie. Measured ~0.981 (ef=8) -> ~0.9996 (ef=128).
    assert recall_low <= recall_high + 1e-9
    assert recall_low >= 0.9  # even the cheapest search recovers most of the exact top-10


def test_ann_batched_query_latency_under_one_second(
    dense_matrices: dict[str, object], fitted_ann: AnnRetrievalPath
) -> None:
    reader_matrix = dense_matrices["reader_matrix"]
    start = time.perf_counter()
    fitted_ann.index.search(reader_matrix, K, efSearch=EF_SEARCH)
    elapsed = time.perf_counter() - start
    # A GENEROUS absolute ceiling (design §7 requires recall@k + latency), measured ~18 ms over the
    # ~540-reader cohort. NOT a 2,000-item speedup claim: at 2k there is no meaningful speedup; the
    # win is asymptotic (demonstrated on a 20k synthetic index in the lesson/milestone).
    assert elapsed < 1.0


# --- hybrid: a small, tuning-dependent, dense-heavy lift (NOT a free win) ---------------------


def _board(path: object, generated: dict[str, object], pool: int = K):
    """hit@k + catalog coverage via the single-path blended scoreboard (reproduces the path's hit@k)."""
    return run_blended_scoreboard(
        {path.name: path},
        generated["interactions_path"],
        catalog_ids=generated["catalog_ids"],
        k=K,
        pool=pool,
        cold_readers=generated["cold_readers"],
    )


def test_hybrid_lifts_hit_and_coverage_directionally(
    generated: dict[str, object], fitted_tt: TwoTowerRetrievalPath
) -> None:
    rows = generated["rows"]
    catalog_ids = generated["catalog_ids"]
    lexical = LexicalRetrievalPath(generated["keywords"]).fit(rows, catalog=catalog_ids)

    tt_board = _board(fitted_tt, generated)
    hybrid = HybridRetrievalPath(lexical, fitted_tt, weight=0.7, pool=50, method="weighted").fit(rows)
    hybrid_board = _board(hybrid, generated)

    # Directional + measured-safe (NOT strict hybrid > two-tower): the pinned dense-heavy fusion
    # edges the two-tower on BOTH axes (measured hit 0.362 >= 0.340, coverage 0.192 > 0.177), but
    # the gain is small / weight-sensitive / not statistically secure.
    assert hybrid_board.hit_rate_at_k >= tt_board.hit_rate_at_k - 0.01
    assert hybrid_board.catalog_coverage > tt_board.catalog_coverage

    # RECORD (not assert) that equal weights HURT and standard (equal-weight) RRF loses to the
    # two-tower alone — the honest "fusion is not a free win" readout. These are weight-sensitive,
    # so they are printed, never gated.
    equal = _board(
        HybridRetrievalPath(lexical, fitted_tt, weight=0.5, pool=50, method="weighted").fit(rows),
        generated,
    )
    rrf = _board(
        HybridRetrievalPath(lexical, fitted_tt, weight=0.5, pool=50, method="rrf").fit(rows),
        generated,
    )
    print(
        f"\nhybrid readout (hit@10 / coverage): two-tower {tt_board.hit_rate_at_k:.3f}/"
        f"{tt_board.catalog_coverage:.3f} | pinned w0.7 {hybrid_board.hit_rate_at_k:.3f}/"
        f"{hybrid_board.catalog_coverage:.3f} | equal-weights {equal.hit_rate_at_k:.3f}/"
        f"{equal.catalog_coverage:.3f} | RRF {rrf.hit_rate_at_k:.3f}/{rrf.catalog_coverage:.3f}"
    )
    assert equal.hit_rate_at_k < tt_board.hit_rate_at_k  # equal weights measurably HURT hit@10
    assert rrf.hit_rate_at_k < tt_board.hit_rate_at_k  # standard RRF loses to the two-tower alone


# --- contract behaviour: empty-seen, unknown reader, round-trips, registry --------------------


def test_ann_empty_seen_still_returns_k(
    fitted_tt: TwoTowerRetrievalPath, fitted_ann: AnnRetrievalPath
) -> None:
    reader_id = fitted_tt.artifact()["reader_ids"][0]
    recs = fitted_ann.retrieve(reader_id, {"seen": set()}, K)
    assert len(recs) == K
    assert all(c.provenance == "ann" for c in recs)
    assert recs == fitted_ann.retrieve(reader_id, {}, K)  # missing seen == empty seen


def test_ann_over_fetches_past_seen(
    generated: dict[str, object], fitted_tt: TwoTowerRetrievalPath, fitted_ann: AnnRetrievalPath
) -> None:
    # A reader with several seen items still gets k UNSEEN recs (over-fetch k+len(seen) before
    # excluding seen), and the excluded ids never appear.
    reader_id = fitted_tt.artifact()["reader_ids"][0]
    seen = set(generated["catalog_ids"][:25])
    recs = fitted_ann.retrieve(reader_id, {"seen": seen}, K)
    assert len(recs) == K
    assert all(c.item_id not in seen for c in recs)


def test_ann_unknown_reader_returns_empty(fitted_ann: AnnRetrievalPath) -> None:
    known = set(fitted_ann.artifact()["reader_ids"])
    unknown = next(r for r in range(10_000_000) if r not in known)
    assert fitted_ann.retrieve(unknown, {"seen": set()}, K) == []
    assert fitted_ann.retrieve(unknown, {"seen": {1, 2, 3}}, K) == []


def test_ann_fit_artifact_load_round_trip(
    generated: dict[str, object], fitted_tt: TwoTowerRetrievalPath, fitted_ann: AnnRetrievalPath
) -> None:
    catalog_ids = generated["catalog_ids"]
    restored = AnnRetrievalPath(fitted_tt).load(fitted_ann.artifact())
    reader_ids = fitted_ann.artifact()["reader_ids"]
    for reader_seed in (3, 11, 42, 128):
        rng = np.random.default_rng(reader_seed)
        reader_id = reader_ids[int(rng.integers(0, len(reader_ids)))]
        seen = set(rng.choice(catalog_ids, size=4, replace=False).tolist())
        a = fitted_ann.retrieve(reader_id, {"seen": seen}, K)
        b = restored.retrieve(reader_id, {"seen": seen}, K)
        assert [c.item_id for c in a] == [c.item_id for c in b]
        assert [c.score for c in a] == [c.score for c in b]
    # load copies the stored matrix, never aliases the artifact's.
    artifact = fitted_ann.artifact()
    loaded = AnnRetrievalPath(fitted_tt).load(artifact)
    artifact["reader_embeddings"][0, 0] = 123.0
    assert loaded.retrieve(reader_ids[0], {"seen": set()}, K)  # still serves


def test_hybrid_empty_seen_still_returns_k_and_unknown_reader_is_empty(
    generated: dict[str, object], fitted_tt: TwoTowerRetrievalPath
) -> None:
    rows = generated["rows"]
    catalog_ids = generated["catalog_ids"]
    lexical = LexicalRetrievalPath(generated["keywords"]).fit(rows, catalog=catalog_ids)
    hybrid = HybridRetrievalPath(lexical, fitted_tt, weight=0.7, pool=50).fit(rows)
    reader_id = fitted_tt.artifact()["reader_ids"][0]
    # Empty seen: lexical has no profile ([]), but the two-tower still scores -> k fused recs.
    recs = hybrid.retrieve(reader_id, {"seen": set()}, K)
    assert len(recs) == K
    assert all(c.provenance == "hybrid" for c in recs)
    # Unknown reader: both sub-paths return [] -> hybrid returns [].
    known = set(fitted_tt.artifact()["reader_ids"])
    unknown = next(r for r in range(10_000_000) if r not in known)
    assert hybrid.retrieve(unknown, {"seen": set()}, K) == []


def test_hybrid_fit_artifact_load_round_trip(
    generated: dict[str, object], fitted_tt: TwoTowerRetrievalPath
) -> None:
    rows = generated["rows"]
    catalog_ids = generated["catalog_ids"]
    lexical = LexicalRetrievalPath(generated["keywords"]).fit(rows, catalog=catalog_ids)
    original = HybridRetrievalPath(lexical, fitted_tt, weight=0.7, pool=50, method="weighted").fit(rows)
    restored = HybridRetrievalPath(lexical, fitted_tt).load(original.artifact())
    assert (restored.weight, restored.pool, restored.method) == (0.7, 50, "weighted")
    reader_ids = fitted_tt.artifact()["reader_ids"]
    for reader_seed in (5, 17, 99):
        rng = np.random.default_rng(reader_seed)
        reader_id = reader_ids[int(rng.integers(0, len(reader_ids)))]
        seen = set(rng.choice(catalog_ids, size=4, replace=False).tolist())
        a = original.retrieve(reader_id, {"seen": seen}, K)
        b = restored.retrieve(reader_id, {"seen": seen}, K)
        assert [c.item_id for c in a] == [c.item_id for c in b]
        assert [c.score for c in a] == [c.score for c in b]


def test_hybrid_rejects_bad_params(
    generated: dict[str, object], fitted_tt: TwoTowerRetrievalPath
) -> None:
    lexical = LexicalRetrievalPath(generated["keywords"])
    for kwargs in ({"weight": -0.1}, {"weight": 1.5}, {"pool": 0}, {"method": "bogus"}):
        with pytest.raises(ValueError):
            HybridRetrievalPath(lexical, fitted_tt, **kwargs)


def test_ann_and_hybrid_register_as_v1(
    generated: dict[str, object], fitted_tt: TwoTowerRetrievalPath
) -> None:
    lexical = LexicalRetrievalPath(generated["keywords"])
    registry = PathRegistry()
    ann = AnnRetrievalPath(fitted_tt)
    hybrid = HybridRetrievalPath(lexical, fitted_tt)
    registry.register(ann)
    registry.register(hybrid)
    assert ann.artifact_name() == "ann-v1"
    assert hybrid.artifact_name() == "hybrid-v1"
    assert "ann" in registry and "hybrid" in registry
    with pytest.raises(DuplicatePathError):
        registry.register(AnnRetrievalPath(fitted_tt))
