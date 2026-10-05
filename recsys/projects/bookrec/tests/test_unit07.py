"""Unit 7 (recsys-009): the semantic GloVe-embedding content retrieval path.

Verifies, on the committed GloVe subset + the seeded recsys-004 keyword text:

- the committed subset loads and matches its sidecar sha256 (and is the publish-safe < 1 MB size);
- hand-checkable :func:`book_embedding` / cosine behaviour (mean pooling, L2-norm, OOV skip, zero
  safety) on a tiny fixture;
- the path clears the random floor and sits in the measured band vs lexical
  (``semantic_hit > 5 x floor`` AND ``0.5 x lexical <= semantic <= 1.1 x lexical``);
- determinism, empty-``seen`` -> ``[]``, a fit->artifact->load round-trip returning identical recs,
  registry ownership as ``semantic-v1``;
- quantitative complementarity (lexical-vs-semantic top-10 overlap is low);
- numpy-only (no gensim / torch imported under ``bookrec/``).
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pytest
from bookrec import (
    DuplicatePathError,
    GloveSubset,
    LexicalRetrievalPath,
    PathRegistry,
    RandomRetrievalPath,
    SemanticEmbeddingRetrievalPath,
    book_embedding,
    generated_dir,
    load_catalog,
    load_glove_subset,
    load_keywords,
    run_validation_scoreboard,
)

K = 10
RANDOM_SEED = 0
GLOVE_DIR = Path(__file__).resolve().parents[3] / "data" / "glove"


def _read_rows(path: Path) -> list[dict[str, object]]:
    with gzip.open(path, mode="rt", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


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
def glove() -> GloveSubset:
    return load_glove_subset()


# --- the committed artifact: integrity + shape ----------------------------------------------


def test_committed_subset_matches_sidecar_sha256_and_is_small() -> None:
    npy_path = GLOVE_DIR / "glove_subset.npy"
    sidecar = json.loads((GLOVE_DIR / "glove_subset.json").read_text(encoding="utf-8"))
    data = npy_path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == sidecar["sha256"]
    assert len(data) < 1_000_000  # publish-safe cap (measured ~0.12 MB)
    assert sidecar["dim"] == 100
    assert sidecar["missing"] == ["starfall"]  # the single OOV vocab word


def test_subset_loads_with_expected_shape_and_coverage(glove: GloveSubset) -> None:
    assert glove.matrix.shape == (len(glove.tokens), glove.dim) == (608, 100)
    # 607/608 covered; the one missing token is a zero row and skipped at pooling.
    assert glove.missing == ["starfall"]
    assert np.allclose(glove.vector("starfall"), 0.0)
    assert glove.vector("dragon") is not None
    assert glove.vector("not_a_real_token") is None


# --- hand-checkable embedding / cosine math --------------------------------------------------


def _toy_glove() -> GloveSubset:
    # Two orthogonal unit axes plus one zero (OOV-like) row, dim=2 for hand arithmetic.
    matrix = np.array([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]], dtype=np.float32)
    tokens = ["east", "north", "void"]
    return GloveSubset(matrix, {t: i for i, t in enumerate(tokens)}, tokens, 2, ["void"])


def test_book_embedding_is_mean_pooled_and_l2_normalized() -> None:
    g = _toy_glove()
    # mean of east=(1,0) and north=(0,1) is (0.5,0.5); L2-normalized -> (1/sqrt2, 1/sqrt2).
    emb = book_embedding(["east", "north"], g)
    assert emb == pytest.approx([1 / np.sqrt(2), 1 / np.sqrt(2)], abs=1e-6)
    assert float(np.linalg.norm(emb)) == pytest.approx(1.0, abs=1e-6)
    # a single token normalizes to itself (already unit length).
    assert book_embedding(["east"], g) == pytest.approx([1.0, 0.0], abs=1e-6)


def test_book_embedding_skips_oov_and_is_zero_safe() -> None:
    g = _toy_glove()
    # "void" is a zero row; "missing" is out of vocabulary -> both skipped, only "east" counts.
    assert book_embedding(["east", "void", "missing"], g) == pytest.approx([1.0, 0.0], abs=1e-6)
    # all-OOV / all-zero -> safe zero vector (no NaN), so cosine against it is 0.
    zero = book_embedding(["void", "missing"], g)
    assert zero.shape == (2,)
    assert np.allclose(zero, 0.0)


def test_retrieve_cosine_on_toy_fixture() -> None:
    g = _toy_glove()
    keywords = {0: "east", 1: "north", 2: "east north", 3: "void"}
    path = SemanticEmbeddingRetrievalPath(keywords, g).fit(None, catalog=[0, 1, 2, 3])
    # Reader has seen book 0 (pure east). Book 2 (east+north, 45deg) outranks book 1 (north, 90deg);
    # book 3 (zero embedding) scores 0. Book 0 is excluded (seen).
    recs = path.retrieve(0, {"seen": {0}}, K)
    assert [c.item_id for c in recs] == [2, 1, 3]
    assert recs[0].score == pytest.approx(1 / np.sqrt(2), abs=1e-6)  # cos45
    assert recs[1].score == pytest.approx(0.0, abs=1e-6)  # cos90
    assert recs[2].score == pytest.approx(0.0, abs=1e-6)  # zero embedding
    assert all(c.provenance == "semantic" for c in recs)


# --- the floor + measured band (direction + band, like test_unit03) --------------------------


def test_semantic_clears_floor_and_sits_in_measured_band(generated: dict[str, object], glove) -> None:
    catalog_ids = generated["catalog_ids"]
    cold = generated["cold_readers"]
    interactions = generated["interactions_path"]

    semantic = SemanticEmbeddingRetrievalPath(generated["keywords"], glove).fit(
        generated["rows"], catalog=catalog_ids
    )
    lexical = LexicalRetrievalPath(generated["keywords"]).fit(generated["rows"], catalog=catalog_ids)
    floor = RandomRetrievalPath(catalog_ids, seed=RANDOM_SEED)

    sem = run_validation_scoreboard(semantic, interactions, catalog_ids=catalog_ids, k=K, cold_readers=cold)
    lex = run_validation_scoreboard(lexical, interactions, catalog_ids=catalog_ids, k=K, cold_readers=cold)
    rnd = run_validation_scoreboard(floor, interactions, catalog_ids=catalog_ids, k=K, cold_readers=cold)

    assert sem.readers == lex.readers == rnd.readers == 500
    # Above the floor (measured ~0.102 vs ~0.012, ~8.5x):
    assert sem.hit_rate_at_k > 5 * rnd.hit_rate_at_k
    # Below lexical but same order of magnitude (measured ~0.102 vs ~0.158):
    assert 0.5 * lex.hit_rate_at_k <= sem.hit_rate_at_k <= 1.1 * lex.hit_rate_at_k


def test_semantic_is_deterministic(generated: dict[str, object], glove) -> None:
    catalog_ids = generated["catalog_ids"]
    kwargs = {"catalog_ids": catalog_ids, "k": K, "cold_readers": generated["cold_readers"]}
    first = run_validation_scoreboard(
        SemanticEmbeddingRetrievalPath(generated["keywords"], glove).fit(generated["rows"], catalog=catalog_ids),
        generated["interactions_path"],
        **kwargs,
    )
    second = run_validation_scoreboard(
        SemanticEmbeddingRetrievalPath(generated["keywords"], glove).fit(generated["rows"], catalog=catalog_ids),
        generated["interactions_path"],
        **kwargs,
    )
    assert first == second


# --- quantitative complementarity (binds the lesson's "complementary" claim) -----------------


def test_lexical_vs_semantic_overlap_is_low(generated: dict[str, object], glove) -> None:
    catalog_ids = generated["catalog_ids"]
    semantic = SemanticEmbeddingRetrievalPath(generated["keywords"], glove).fit(
        generated["rows"], catalog=catalog_ids
    )
    lexical = LexicalRetrievalPath(generated["keywords"]).fit(generated["rows"], catalog=catalog_ids)

    seen_by: dict[int, set[int]] = defaultdict(set)
    target_by: dict[int, set[int]] = defaultdict(set)
    known = set(catalog_ids)
    for row in generated["rows"]:
        rid, iid = int(row["reader_id"]), int(row["item_id"])
        if iid not in known or int(row["label"]) != 1:
            continue
        if row["split"] == "train":
            seen_by[rid].add(iid)
        elif row["split"] == "val":
            target_by[rid].add(iid)

    cold = set(generated["cold_readers"])
    fractions: list[float] = []
    for rid in sorted(target_by):
        seen = seen_by[rid]
        if rid in cold or not (target_by[rid] - seen):
            continue
        s = {c.item_id for c in semantic.retrieve(rid, {"seen": seen}, K)}
        lx = {c.item_id for c in lexical.retrieve(rid, {"seen": seen}, K)}
        if s and lx:
            fractions.append(len(s & lx) / K)
    overlap = float(np.mean(fractions))
    # Measured ~0.22: the two paths largely surface DIFFERENT books -> complementary, not redundant.
    assert 0.0 < overlap < 0.4


# --- contract behaviour ----------------------------------------------------------------------


def test_empty_seen_returns_empty(generated: dict[str, object], glove) -> None:
    path = SemanticEmbeddingRetrievalPath(generated["keywords"], glove).fit(generated["rows"])
    assert path.retrieve(0, {"seen": set()}, K) == []
    assert path.retrieve(0, {}, K) == []


def test_retrieve_excludes_seen_and_is_bounded(generated: dict[str, object], glove) -> None:
    catalog_ids = generated["catalog_ids"]
    path = SemanticEmbeddingRetrievalPath(generated["keywords"], glove).fit(
        generated["rows"], catalog=catalog_ids
    )
    seen = {catalog_ids[0], catalog_ids[1], catalog_ids[2]}
    recs = path.retrieve(0, {"seen": seen}, K)
    assert len(recs) <= K
    assert all(c.item_id not in seen for c in recs)
    assert all(c.provenance == "semantic" for c in recs)


def test_fit_signature_is_protocol_substitutable(generated: dict[str, object], glove) -> None:
    path = SemanticEmbeddingRetrievalPath(generated["keywords"], glove)
    same = path.fit(generated["rows"])  # no catalog arg; must work
    assert same is path
    assert path.retrieve(0, {"seen": {generated["catalog_ids"][5]}}, K)  # fitted


def test_fit_artifact_load_round_trip(generated: dict[str, object], glove) -> None:
    catalog_ids = generated["catalog_ids"]
    rows = generated["rows"]
    original = SemanticEmbeddingRetrievalPath(generated["keywords"], glove).fit(rows, catalog=catalog_ids)
    restored = SemanticEmbeddingRetrievalPath(generated["keywords"], glove).load(original.artifact())
    for reader_seed in (3, 11, 42, 128):
        rng = np.random.default_rng(reader_seed)
        seen = set(rng.choice(catalog_ids, size=4, replace=False).tolist())
        a = original.retrieve(reader_seed, {"seen": seen}, K)
        b = restored.retrieve(reader_seed, {"seen": seen}, K)
        assert [c.item_id for c in a] == [c.item_id for c in b]
        assert [c.score for c in a] == [c.score for c in b]
        assert [c.provenance for c in a] == [c.provenance for c in b]


def test_empty_keyword_corpus_raises(glove) -> None:
    with pytest.raises(ValueError):
        SemanticEmbeddingRetrievalPath({}, glove)


# --- registry ownership ----------------------------------------------------------------------


def test_semantic_path_registers_as_semantic_v1(generated: dict[str, object], glove) -> None:
    registry = PathRegistry()
    path = SemanticEmbeddingRetrievalPath(generated["keywords"], glove)
    registry.register(path)
    assert path.artifact_name() == "semantic-v1"
    assert "semantic" in registry
    registry.register(LexicalRetrievalPath(generated["keywords"]))  # distinct name + artifact
    with pytest.raises(DuplicatePathError):
        registry.register(SemanticEmbeddingRetrievalPath(generated["keywords"], glove))


# --- numpy-only: no heavy ML stack imported under bookrec/ -----------------------------------


def test_bookrec_imports_no_gensim_or_torch() -> None:
    bookrec_dir = Path(__file__).resolve().parents[1] / "bookrec"
    for source in bookrec_dir.rglob("*.py"):
        text = source.read_text(encoding="utf-8")
        for forbidden in ("import gensim", "import torch", "from gensim", "from torch"):
            assert forbidden not in text, f"{source.name} imports a forbidden ML stack: {forbidden}"
