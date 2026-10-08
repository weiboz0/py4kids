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
- no gensim anywhere under ``bookrec/``, and torch is only ever imported **lazily** (inside
  ``two_tower.fit``), never at any module top level — proven by an import-blocked subprocess.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import subprocess
import sys
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
    # Reader has seen item 0 (pure east). Item 2 (east+north, 45deg) outranks item 1 (north, 90deg);
    # item 3 (zero embedding) scores 0. Item 0 is excluded (seen).
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


# --- no gensim; torch only ever LAZY (Unit 8) ------------------------------------------------


def test_bookrec_imports_no_gensim_or_torch_or_faiss() -> None:
    """gensim is banned everywhere under ``bookrec/``; torch **and faiss** may appear ONLY as lazy imports.

    Unit 8 (``two_tower.py``) imports torch **inside** ``fit``; Unit 10 (``ann.py``) imports faiss
    **inside** the HNSW build/search surface — so importing the package and calling the heavy-dep-free
    surface never pulls torch or faiss. This raw-text scan forbids gensim anywhere and forbids any
    **top-level** (unindented) ``import torch`` / ``from torch`` / ``import faiss`` / ``from faiss`` in
    every ``bookrec/*.py`` — including ``two_tower.py`` and ``ann.py`` — while permitting the indented
    lazy imports inside their methods.
    """
    bookrec_dir = Path(__file__).resolve().parents[1] / "bookrec"
    sources = list(bookrec_dir.rglob("*.py"))
    assert (bookrec_dir / "two_tower.py") in sources  # the Unit-8 module is actually scanned
    assert (bookrec_dir / "feature_tower.py") in sources  # the Unit-9 module is actually scanned
    assert (bookrec_dir / "ann.py") in sources  # the Unit-10 ANN module is actually scanned
    assert (bookrec_dir / "hybrid.py") in sources  # the Unit-10 hybrid module is actually scanned
    for source in sources:
        text = source.read_text(encoding="utf-8")
        # gensim is never allowed, in any form, anywhere in the package.
        for forbidden in ("import gensim", "from gensim"):
            assert forbidden not in text, f"{source.name} imports gensim: {forbidden}"
        # torch and faiss are allowed ONLY as lazy (indented) imports; never at module top level.
        for lineno, line in enumerate(text.splitlines(), start=1):
            if line[:1].isspace():
                continue  # indented -> not a top-level statement (the lazy import inside a method)
            stripped = line.strip()
            assert not stripped.startswith(
                ("import torch", "from torch", "import faiss", "from faiss")
            ), f"{source.name}:{lineno} imports torch/faiss at module top level: {stripped!r}"


def test_heavy_dep_free_paths_do_not_import_torch_or_faiss() -> None:
    """Prove the heavy-dep-free surface never imports torch **or faiss**, though uv's ``.venv`` has both.

    uv installs one shared ``.venv`` with both torch and faiss, so merely running the group-free
    suite does NOT prove ``bookrec`` avoids importing them. In a subprocess we plant TWO **sentinels**
    ``sys.modules["torch"] = None`` and ``sys.modules["faiss"] = None`` (so any real ``import torch`` /
    ``import faiss`` would raise), import ``bookrec`` (which imports every unit module, including
    ``ann.py`` / ``hybrid.py``), then exercise the heavy-dep-free surface:

    - the Unit-8 two-tower and Unit-9 feature tower (``load``/``retrieve``/``artifact`` over numpy);
    - the Unit-10 :class:`HybridRetrievalPath` — ``fit``/``retrieve``/``artifact`` are pure numpy over
      its sub-paths' candidates, so a hybrid runs end-to-end with BOTH torch and faiss blocked;
    - constructing a Unit-10 :class:`AnnRetrievalPath` (construction is faiss-free), and confirming its
      faiss use is **confined to the index build**: ``fit`` attempts a lazy ``import faiss`` and raises
      ImportError under the sentinel, which leaves ``sys.modules['faiss']`` as ``None`` (unimported).

    The subprocess finally asserts BOTH sentinels are **untouched** (``sys.modules.get("torch") is
    None`` AND ``sys.modules.get("faiss") is None``): if anything had imported either, the key would
    no longer be ``None``. (``"faiss" not in sys.modules`` would be WRONG — the key EXISTS, mapped to
    None.)
    """
    script = (
        "import sys\n"
        "sys.modules['torch'] = None  # sentinel: a real `import torch` would now raise\n"
        "sys.modules['faiss'] = None  # sentinel: a real `import faiss` would now raise\n"
        "import numpy as np\n"
        "import bookrec  # imports every unit module, including ann.py / hybrid.py\n"
        "from bookrec import (TwoTowerRetrievalPath, FeatureTowerRetrievalPath, Book, GloveSubset,\n"
        "                     LexicalRetrievalPath, HybridRetrievalPath, AnnRetrievalPath)\n"
        "artifact = {\n"
        "    'reader_embeddings': np.zeros((2, 4), dtype=np.float32),\n"
        "    'item_embeddings': np.eye(4, dtype=np.float32)[:3],\n"
        "    'reader_ids': [100, 200],\n"
        "    'item_ids': [10, 20, 30],\n"
        "    'params': {},\n"
        "}\n"
        "artifact['reader_embeddings'][0, 0] = 1.0  # reader 100 points at item 10\n"
        "loaded = TwoTowerRetrievalPath().load(artifact)\n"
        "recs = loaded.retrieve(100, {'seen': set()}, 2)\n"
        "assert [c.item_id for c in recs][0] == 10, recs\n"
        "restored = loaded.artifact()  # artifact() must also be torch-free\n"
        "assert list(restored['item_ids']) == [10, 20, 30], restored\n"
        "# Unit 9's feature tower is torch-free too on load/retrieve/artifact (it stores the\n"
        "# COMPOSED numpy item matrix, so no re-composition and no torch are needed to serve it).\n"
        "books = {i: Book(item_id=i, title=f'b{i}', fields={'genres': 'fantasy', 'author_id': '1'})\n"
        "         for i in (10, 20, 30)}\n"
        "glove = GloveSubset(np.zeros((1, 2), dtype=np.float32), {'foo': 0}, ['foo'], 2, [])\n"
        "ft = FeatureTowerRetrievalPath(books, {10: 'foo', 20: 'foo', 30: 'foo'}, glove).load(artifact)\n"
        "ft_recs = ft.retrieve(100, {'seen': set()}, 2)\n"
        "assert [c.item_id for c in ft_recs][0] == 10, ft_recs\n"
        "assert ft_recs[0].provenance == 'feature-tower'\n"
        "assert list(ft.artifact()['item_ids']) == [10, 20, 30], ft.artifact()\n"
        "# Unit 10's hybrid is pure numpy over its sub-paths -> fit/retrieve/artifact need NO faiss.\n"
        "lex = LexicalRetrievalPath({10: 'dragon magic', 20: 'space rocket', 30: 'ocean deep'}\n"
        "                           ).fit([], catalog=[10, 20, 30])\n"
        "hyb = HybridRetrievalPath(lex, loaded, weight=0.7, pool=5).fit([])\n"
        "h_recs = hyb.retrieve(100, {'seen': {10}}, 2)\n"
        "assert len(h_recs) == 2 and all(c.provenance == 'hybrid' for c in h_recs), h_recs\n"
        "assert hyb.artifact()['params']['method'] == 'weighted', hyb.artifact()\n"
        "# Unit 10's ANN: construction is faiss-free; its faiss use is CONFINED to the index build,\n"
        "# so fit() attempts a lazy `import faiss` and raises ImportError under the sentinel (which\n"
        "# leaves sys.modules['faiss'] as None -- the module was never actually imported).\n"
        "ann = AnnRetrievalPath(loaded)\n"
        "try:\n"
        "    ann.fit([])\n"
        "    raise AssertionError('AnnRetrievalPath.fit must build a faiss index (import blocked)')\n"
        "except ImportError:\n"
        "    pass  # faiss is confined to the HNSW build surface\n"
        "# Unit 11's neural reranker: load/retrieve/artifact are pure numpy over the learned MLP\n"
        "# weights, so a reranker loads and serves end-to-end with BOTH torch and faiss blocked (torch\n"
        "# is confined to RerankerModel.fit). A hand linear model that scores by the two-tower feature.\n"
        "from bookrec import NeuralRerankerPath, RerankerModel, rerank\n"
        "from bookrec.rerank import feature_names\n"
        "names = ['two-tower']\n"
        "fnames = feature_names(names)\n"
        "hand = {\n"
        "    'linear': True,\n"
        "    'mask': np.ones(len(fnames), dtype=bool),\n"
        "    'mu': np.zeros(len(fnames), dtype=np.float32),\n"
        "    'sd': np.ones(len(fnames), dtype=np.float32),\n"
        "    'weights': [np.eye(1, len(fnames), dtype=np.float32), np.zeros(1, dtype=np.float32)],\n"
        "    'params': {'seed': 0},\n"
        "}\n"
        "rr_model = RerankerModel.from_state(hand)  # numpy rebuild, no torch\n"
        "assert float(rr_model.score(np.eye(1, len(fnames), dtype=np.float32))[0]) == 1.0\n"
        "rr_art = {\n"
        "    'model': hand, 'feature_names': fnames, 'path_names': names,\n"
        "    'counts': {10: 1, 20: 1, 30: 1}, 'max_log_pop': 1.0, 'known_readers': [100],\n"
        "    'params': {'pool': 5, 'holdout_frac': 0.25, 'n_negatives': 10, 'leaky': False},\n"
        "}\n"
        "rr = NeuralRerankerPath({'two-tower': loaded}, lambda rows: {'two-tower': loaded}, books,\n"
        "                        pool=5, path_names=names).load(rr_art)\n"
        "rr_recs = rr.retrieve(100, {'seen': set()}, 2)  # builds pool + features + numpy MLP score\n"
        "assert rr_recs and all(c.provenance == 'reranker' for c in rr_recs), rr_recs\n"
        "assert rr.retrieve(999, {'seen': set()}, 2) == []  # unknown reader -> []\n"
        "assert list(rr.artifact()['path_names']) == names  # artifact() is torch-free too\n"
        "assert sys.modules.get('torch') is None, 'something imported torch on the heavy-dep-free path'\n"
        "assert sys.modules.get('faiss') is None, 'something imported faiss on the heavy-dep-free path'\n"
        "print('HEAVY_DEP_FREE_OK')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, f"stdout={result.stdout!r} stderr={result.stderr!r}"
    assert result.stdout.strip().splitlines()[-1] == "HEAVY_DEP_FREE_OK"
