"""Unit 3 (recsys-005): the lexical / BM25 content retrieval path.

Verifies the shipped `LexicalRetrievalPath` + `BM25Index` on the recsys-004 keyword text:
the index math (IDF monotone in df; the `b` length-norm and `k1` saturation behave), the path
beating the random floor on the seeded val scoreboard with a stable margin, empty-`seen` → `[]`,
a fit→artifact→load round-trip returning identical recommendations, and registry ownership.
"""

from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path

import numpy as np
import pytest
from bookrec import (
    BM25Index,
    DuplicatePathError,
    LexicalRetrievalPath,
    PathRegistry,
    PopularityRetrievalPath,
    RandomRetrievalPath,
    generated_dir,
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


# --- the lexical path beats the random floor by a stable margin ------------------------------


def test_lexical_beats_random_floor(generated: dict[str, object]) -> None:
    catalog_ids = generated["catalog_ids"]
    cold_readers = generated["cold_readers"]
    interactions_path = generated["interactions_path"]

    lexical = LexicalRetrievalPath(generated["keywords"]).fit(generated["rows"], catalog=catalog_ids)
    random_floor = RandomRetrievalPath(catalog_ids, seed=RANDOM_SEED)

    lexical_result = run_validation_scoreboard(
        lexical, interactions_path, catalog_ids=catalog_ids, k=K, cold_readers=cold_readers
    )
    random_result = run_validation_scoreboard(
        random_floor, interactions_path, catalog_ids=catalog_ids, k=K, cold_readers=cold_readers
    )
    # Direction + stable margin, not a brittle point value (measured ~0.158 vs floor ~0.012, ~13x).
    assert lexical_result.readers == random_result.readers > 0
    assert lexical_result.hit_rate_at_k > 5 * random_result.hit_rate_at_k


def test_lexical_is_deterministic(generated: dict[str, object]) -> None:
    catalog_ids = generated["catalog_ids"]
    kwargs = {"catalog_ids": catalog_ids, "k": K, "cold_readers": generated["cold_readers"]}
    first = run_validation_scoreboard(
        LexicalRetrievalPath(generated["keywords"]).fit(generated["rows"], catalog=catalog_ids),
        generated["interactions_path"],
        **kwargs,
    )
    second = run_validation_scoreboard(
        LexicalRetrievalPath(generated["keywords"]).fit(generated["rows"], catalog=catalog_ids),
        generated["interactions_path"],
        **kwargs,
    )
    assert first == second


# --- contract behaviour ----------------------------------------------------------------------


def test_empty_seen_returns_empty(generated: dict[str, object]) -> None:
    path = LexicalRetrievalPath(generated["keywords"]).fit(generated["rows"])
    assert path.retrieve(0, {"seen": set()}, K) == []
    assert path.retrieve(0, {}, K) == []


def test_retrieve_excludes_seen_and_is_bounded(generated: dict[str, object]) -> None:
    catalog_ids = generated["catalog_ids"]
    path = LexicalRetrievalPath(generated["keywords"]).fit(generated["rows"], catalog=catalog_ids)
    seen = {catalog_ids[0], catalog_ids[1], catalog_ids[2]}
    recs = path.retrieve(0, {"seen": seen}, K)
    assert len(recs) <= K
    assert all(c.item_id not in seen for c in recs)
    assert all(c.provenance == "lexical" for c in recs)


def test_fit_signature_is_protocol_substitutable(generated: dict[str, object]) -> None:
    # fit(interactions, catalog=None) — exactly the RetrievalPath protocol shape.
    path = LexicalRetrievalPath(generated["keywords"])
    same = path.fit(generated["rows"])  # no catalog arg; must work
    assert same is path
    assert path.retrieve(0, {"seen": {generated["catalog_ids"][5]}}, K)  # fitted


def test_fit_artifact_load_round_trip(generated: dict[str, object]) -> None:
    catalog_ids = generated["catalog_ids"]
    rows = generated["rows"]
    original = LexicalRetrievalPath(generated["keywords"]).fit(rows, catalog=catalog_ids)
    restored = LexicalRetrievalPath(generated["keywords"]).load(original.artifact())
    for reader_seed in (3, 11, 42, 128):
        rng = np.random.default_rng(reader_seed)
        seen = set(rng.choice(catalog_ids, size=4, replace=False).tolist())
        a = original.retrieve(reader_seed, {"seen": seen}, K)
        b = restored.retrieve(reader_seed, {"seen": seen}, K)
        assert [c.item_id for c in a] == [c.item_id for c in b]
        assert [c.score for c in a] == [c.score for c in b]
        assert [c.provenance for c in a] == [c.provenance for c in b]


def test_empty_keyword_corpus_raises() -> None:
    with pytest.raises(ValueError):
        LexicalRetrievalPath({})


# --- BM25 index math (tiny hand-checked fixtures) --------------------------------------------


def test_idf_monotone_decreasing_in_df() -> None:
    # "rare" appears in 1 of 4 docs; "common" in all 4. Rare must have the larger IDF.
    docs = {
        0: "rare common",
        1: "common filler",
        2: "common other",
        3: "common thing",
    }
    index = BM25Index(docs)
    assert index.idf[index.vocab["rare"]] > index.idf[index.vocab["common"]]
    assert (index.idf > 0).all()


def test_b_length_normalization_favors_short_docs() -> None:
    # Both docs contain "x" once; doc 1 is much longer. With b=1 the short doc scores higher;
    # with b=0 (no length norm) they tie.
    docs = {0: "x", 1: "x a b c d e f g h i j"}
    query = ["x"]
    normed = BM25Index(docs, b=1.0).score(query)
    flat = BM25Index(docs, b=0.0).score(query)
    assert normed[0] > normed[1]  # short doc wins under length normalization
    assert flat[0] == pytest.approx(flat[1])  # no length norm → tie


def test_k1_saturation_is_monotone_in_k1() -> None:
    # A repeated term: a larger k1 gives a larger (less saturated) tf contribution for tf>1.
    docs = {0: "x x", 1: "y"}
    low = BM25Index(docs, k1=0.3, b=0.0).score(["x"])[0]
    high = BM25Index(docs, k1=5.0, b=0.0).score(["x"])[0]
    assert high > low


def test_k1_zero_is_finite_binary_presence() -> None:
    # k1 -> 0 is the binary-presence limit the unit teaches as a stretch; it must be finite
    # (no 0/0 NaN for docs that lack the query term) and give every matching doc an equal score.
    docs = {0: "x x y", 1: "x z", 2: "q r"}
    scores = BM25Index(docs, k1=0.0, b=0.0).score(["x"])
    assert np.isfinite(scores).all()
    assert scores[0] == pytest.approx(scores[1])  # presence, not count (tf=2 ties tf=1)
    assert scores[0] > 0
    assert scores[2] == pytest.approx(0.0)  # no "x" -> no contribution


def test_index_rejects_bad_params() -> None:
    with pytest.raises(ValueError):
        BM25Index({0: "x"}, k1=-1.0)
    with pytest.raises(ValueError):
        BM25Index({0: "x"}, b=2.0)
    with pytest.raises(ValueError):
        BM25Index({})


# --- registry ownership ----------------------------------------------------------------------


def test_lexical_path_registers_without_collision(generated: dict[str, object]) -> None:
    registry = PathRegistry()
    path = LexicalRetrievalPath(generated["keywords"])
    registry.register(path)
    assert path.artifact_name() == "lexical-v1"
    assert "lexical" in registry
    # coexists with the other paths (distinct names + artifacts)
    registry.register(PopularityRetrievalPath())
    registry.register(RandomRetrievalPath(generated["catalog_ids"], seed=RANDOM_SEED))
    with pytest.raises(DuplicatePathError):
        registry.register(LexicalRetrievalPath(generated["keywords"]))
