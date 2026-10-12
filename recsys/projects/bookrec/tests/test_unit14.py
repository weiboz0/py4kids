"""Unit 14 (recsys-017): the model cache's REQUIRED CHECK + the assembled full system.

``scripts/build_models.py`` fits the expensive models once (seeded) and writes their torch-free
artifacts to ``recsys/data/generated/models/`` (CI rebuilds them from scratch every run, right after
the data generators). This suite is the required check of plan recsys-017 (gates (a), (d), (e), (f)
and the reranker provenance; the structure of (b)/(c)):

- **(a) cache fidelity** — every artifact exists, matches its schema/version (pickle protocol 5,
  ``manifest.json`` with the data hash) and loads torch-free (the ANN rebuild alone needs faiss);
  each loaded model reproduces its pinned val hit@10 within ±0.002 (MF 0.276, two-tower 0.340, warm
  feature tower 0.298 + 113 ± 3 cold items surfaced, ANN 0.340 with recall@10 >= 0.995 vs exact,
  reranker-u11 0.346, SASRec 0.4228 on the session log);
- **determinism** — MF and the two-tower are refit and ``allclose`` to the cache; the ANN is rebuilt
  (identical top-10, recall@10 >= 0.99); every cached model + the full stack keeps rank overlap
  >= 0.9 per reader against a **20-reader independent oracle** (captured once in Phase B from this
  build and cross-checked IDENTICAL against [fable]'s independent probe build before commit);
- **(e)/(f)** — the full stack (8-path pool + learned reranker) 0.356 / 0.203 ± 0.003, the fixed
  8-path blend 0.362 / 0.206 ± 0.003, the Part-1 build 0.306 / 0.333 ± 0.002;
- **(b)/(c) structure** of ``readouts.json`` — exactly the 10 ablation rows + both baselines, signed
  deltas recomputed from each row's declared baseline to 1e-9, finite / in range; the
  beyond-accuracy rows and columns (the probe values are re-asserted ±0.003 as a reproducibility pin);
- **reranker provenance** — a reduced unmutated build and a reduced mutated build (val dropped, test
  relabelled) through the identical ``build_models`` code produce ``allclose`` reranker artifacts;
  the Unit-11 repeat-read ``log_pop`` regression re-asserted on the build's assembly call; both
  cached rerankers carry ``recipe = "u11-holdout-75-25"`` and the profile fraction;
- the additive ``loss_history`` / reranker training log, and its version-compatible load.

A session fixture builds the cache when it is absent or stale, so a bare ``pytest`` is never vacuous.
CPU-deterministic; routed ``--group recsys``.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from bookrec import (
    AnnRetrievalPath,
    FullSystem,
    ModelCache,
    load_book_data,
    load_cached_models,
    reader_hits,
    run_validation_scoreboard,
)
from bookrec.protocol import BaseRetrievalPath, Candidate
from bookrec.rerank import feature_names, split_profile_labels
from bookrec.system import (
    ABLATION_ROWS,
    BEYOND_ACCURACY_COLUMNS,
    BEYOND_ACCURACY_ROWS,
    BUILD_COMMAND,
    CACHE_SCHEMA,
    CACHE_SCHEMA_VERSION,
    FULL8_PATH_NAMES,
    MANIFEST_FILE,
    MODEL_NAMES,
    RERANKER_RECIPE,
    U11_PATH_NAMES,
    BookData,
    check_readouts,
    data_hash,
    file_sha256,
    make_feature_tower,
    make_mf,
    make_sasrec,
    make_two_tower,
    top_k,
)

K = 10
BUILD_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_models.py"


def _load_build_module():
    spec = importlib.util.spec_from_file_location("bookrec_build_models", BUILD_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


build_models = _load_build_module()


# ------------------------------------------------------------------------------------ fixtures
@pytest.fixture(scope="session")
def data() -> BookData:
    return load_book_data()


@pytest.fixture(scope="session")
def cache(data: BookData) -> ModelCache:
    """The model cache — BUILT here when absent or stale (a bare pytest is never vacuous)."""
    try:
        return load_cached_models(data_dir=data.data_dir)
    except (FileNotFoundError, ValueError):
        build_models.build_all()
        return load_cached_models(data_dir=data.data_dir)


@pytest.fixture(scope="module")
def system(cache: ModelCache, data: BookData) -> FullSystem:
    return FullSystem.from_cache(cache, data)


def _val_hit(path, data: BookData) -> float:
    return run_validation_scoreboard(
        path,
        data.interactions_path,
        catalog_ids=data.catalog_ids,
        k=K,
        cold_readers=data.cold_readers,
    ).hit_rate_at_k


# =========================================================================== (a) the artifacts
def test_every_artifact_exists_with_schema_version_and_manifest(cache: ModelCache, data) -> None:
    manifest = json.loads((cache.directory / MANIFEST_FILE).read_text(encoding="utf-8"))
    assert manifest["schema"] == CACHE_SCHEMA
    assert manifest["schema_version"] == CACHE_SCHEMA_VERSION
    assert manifest["pickle_protocol"] == 5
    assert manifest["data_hash"] == data_hash(data.data_dir)
    assert manifest["models"] == list(MODEL_NAMES)
    assert manifest["build_command"] == BUILD_COMMAND
    expected_class = {
        "mf": ("MatrixFactorizationPath", "mf"),
        "two-tower": ("TwoTowerRetrievalPath", "two-tower"),
        "feature-tower": ("FeatureTowerRetrievalPath", "feature-tower"),
        "feature-tower-hard": ("FeatureTowerRetrievalPath", "feature-tower"),
        "ann": ("AnnRetrievalPath", "ann"),
        "reranker-u11": ("NeuralRerankerPath", "reranker"),
        "reranker-full8": ("NeuralRerankerPath", "reranker"),
        "sasrec": ("SasrecRetrievalPath", "sasrec"),
    }
    for name in MODEL_NAMES:
        target = cache.directory / f"{name}.pkl"
        assert target.is_file(), name
        assert target.read_bytes()[:2] == b"\x80\x05", f"{name}: not pickle protocol 5"
        entry = manifest["artifacts"][name]
        assert entry["sha256"] == file_sha256(target), name
        envelope = cache.envelope(name)
        assert (envelope["schema"], envelope["schema_version"]) == (
            CACHE_SCHEMA,
            CACHE_SCHEMA_VERSION,
        )
        assert (envelope["path_class"], envelope["path_name"]) == expected_class[name], name
        assert envelope["path_version"] == entry["path_version"] == "1", name
    assert cache.artifact("feature-tower")["params"]["negative_pool"] == "warm"
    assert cache.artifact("feature-tower-hard")["params"]["negative_pool"] == "hard"
    assert cache.meta("sasrec")["log"] == "sessions"


def test_cache_loads_torch_free_and_ann_needs_only_faiss(cache: ModelCache) -> None:
    script = (
        "import sys\n"
        "sys.modules['torch'] = None\n"
        "sys.modules['faiss'] = None\n"
        "from pathlib import Path\n"
        "from bookrec import (load_cached_models, MatrixFactorizationPath, TwoTowerRetrievalPath,\n"
        "    FeatureTowerRetrievalPath, NeuralRerankerPath, SasrecRetrievalPath, AnnRetrievalPath,\n"
        "    load_book_data)\n"
        f"cache = load_cached_models({str(cache.directory)!r})\n"
        "data = load_book_data()\n"
        "MatrixFactorizationPath().load(cache.artifact('mf'))\n"
        "tt = TwoTowerRetrievalPath().load(cache.artifact('two-tower'))\n"
        "for name in ('feature-tower', 'feature-tower-hard'):\n"
        "    FeatureTowerRetrievalPath(data.catalog, data.keywords, data.glove).load(cache.artifact(name))\n"
        "sas = SasrecRetrievalPath().load(cache.artifact('sasrec'))\n"
        "assert len(sas.loss_history) == sas.n_epochs\n"
        "for name in ('reranker-u11', 'reranker-full8'):\n"
        "    names = cache.meta(name)['path_names']\n"
        "    NeuralRerankerPath({n: tt for n in names}, lambda r: {}, data.catalog,\n"
        "                       path_names=names).load(cache.artifact(name))\n"
        "try:\n"
        "    AnnRetrievalPath(tt).load(cache.artifact('ann'))\n"
        "    raise AssertionError('the ANN load must rebuild HNSW (faiss blocked)')\n"
        "except ImportError:\n"
        "    pass\n"
        "assert sys.modules.get('torch') is None, 'torch was imported'\n"
        "assert sys.modules.get('faiss') is None, 'faiss was imported'\n"
        "print('CACHE_TORCH_FREE_OK')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, f"stdout={result.stdout!r} stderr={result.stderr!r}"
    assert result.stdout.strip().splitlines()[-1] == "CACHE_TORCH_FREE_OK"


def test_missing_cache_names_the_build_command(tmp_path: Path, data: BookData) -> None:
    with pytest.raises(FileNotFoundError) as missing:
        load_cached_models(tmp_path, data_dir=data.data_dir)
    assert BUILD_COMMAND in str(missing.value)


def test_stale_data_hash_is_refused(tmp_path: Path, cache: ModelCache, data: BookData) -> None:
    manifest = json.loads((cache.directory / MANIFEST_FILE).read_text(encoding="utf-8"))
    manifest["data_hash"] = "0" * 64  # the data were regenerated since the build
    (tmp_path / MANIFEST_FILE).write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="different generated data"):
        load_cached_models(tmp_path, data_dir=data.data_dir)


# ======================================================================= the stored training curves
def test_loss_history_is_stored_and_version_compatible(cache: ModelCache, data) -> None:
    for name, make in (
        ("two-tower", make_two_tower),
        ("feature-tower", lambda: make_feature_tower(data, "warm")),
        ("feature-tower-hard", lambda: make_feature_tower(data, "hard")),
        ("sasrec", make_sasrec),
    ):
        art = cache.artifact(name)
        curve = art["loss_history"]
        assert len(curve) == art["params"]["n_epochs"] and curve[-1] < curve[0], name
        assert make().load(art).loss_history == curve, name
        old = {k: v for k, v in art.items() if k != "loss_history"}  # a pre-recsys-017 artifact
        assert make().load(old).loss_history == [], name
    for name in ("reranker-u11", "reranker-full8"):
        log = cache.loss_history(name)
        assert len(log) == cache.artifact(name)["model"]["params"]["epochs"] == 30, name
        assert log[-1] < log[0], name
        assert cache.meta(name)["training_log"] == log, name


# ================================================================== (a) pinned val hits ± 0.002
def test_loaded_models_reproduce_pinned_val_hits(system: FullSystem, data: BookData) -> None:
    pins = {"mf": 0.276, "two-tower": 0.340, "feature-tower": 0.298, "ann": 0.340}
    for name, pin in pins.items():
        assert _val_hit(system.paths[name], data) == pytest.approx(pin, abs=0.002), name
    assert _val_hit(system.reranker_u11, data) == pytest.approx(0.346, abs=0.002)
    hits = reader_hits(system.sasrec, data.sessions_path, catalog_ids=data.catalog_ids, k=K)
    assert len(hits) == 1419
    assert float(np.mean(list(hits.values()))) == pytest.approx(0.4228, abs=0.002)


def test_feature_tower_cold_coverage(system: FullSystem, data: BookData) -> None:
    train_pos: dict[int, set[int]] = {}
    for row in data.rows:
        if row["split"] == "train" and int(row["label"]) == 1:
            train_pos.setdefault(int(row["reader_id"]), set()).add(int(row["item_id"]))
    zero_train = set(data.catalog_ids) - set().union(*train_pos.values())
    ft = system.paths["feature-tower"]
    cold = set(data.cold_readers)
    surfaced: set[int] = set()
    for reader in ft.artifact()["reader_ids"]:
        if reader in cold:
            continue
        for cand in ft.retrieve(reader, {"seen": train_pos.get(reader, set())}, K):
            if cand.item_id in zero_train:
                surfaced.add(cand.item_id)
    assert abs(len(surfaced) - 113) <= 3, len(surfaced)


def test_ann_recall_and_rebuild(system: FullSystem, data: BookData) -> None:
    exact, ann = system.paths["two-tower"], system.paths["ann"]
    rebuilt = AnnRetrievalPath(exact).fit(data.rows, catalog=data.catalog_ids)
    recall, rebuilt_recall, same = [], [], []
    for reader in data.cohort:
        seen = data.seen_by.get(reader, set())
        truth = set(top_k(exact, reader, seen))
        cached_top = top_k(ann, reader, seen)
        rebuilt_top = top_k(rebuilt, reader, seen)
        recall.append(len(truth & set(cached_top)) / K)
        rebuilt_recall.append(len(truth & set(rebuilt_top)) / K)
        same.append(cached_top == rebuilt_top)
    assert np.mean(recall) >= 0.995, np.mean(recall)
    assert np.mean(rebuilt_recall) >= 0.99, np.mean(rebuilt_recall)
    assert all(same), "the HNSW rebuild must serve identical top-10 lists"


# ========================================================================= determinism (cheap refit)
def test_mf_and_two_tower_refit_allclose_to_cache(cache: ModelCache, data: BookData) -> None:
    mf = make_mf().fit(data.rows, catalog=data.catalog_ids).artifact()
    cached = cache.artifact("mf")
    for key in ("P", "Q"):
        np.testing.assert_allclose(mf[key], cached[key], rtol=0, atol=1e-6, err_msg=key)
    assert mf["reader_ids"] == cached["reader_ids"] and mf["item_ids"] == cached["item_ids"]
    tt = make_two_tower().fit(data.rows, catalog=data.catalog_ids).artifact()
    cached = cache.artifact("two-tower")
    for key in ("reader_embeddings", "item_embeddings"):
        np.testing.assert_allclose(tt[key], cached[key], rtol=0, atol=1e-6, err_msg=key)
    np.testing.assert_allclose(tt["loss_history"], cached["loss_history"], rtol=0, atol=1e-6)


# ================================================================ the 20-reader independent oracle
def test_twenty_reader_oracle_rank_overlap(system: FullSystem, data: BookData) -> None:
    assert data.cohort[:20] == ORACLE_MAIN_READERS
    _seen, _rel, s_cohort = data.session_cohort
    assert s_cohort[:20] == ORACLE_SESSION_READERS
    served = {
        "mf": system.paths["mf"],
        "two-tower": system.paths["two-tower"],
        "feature-tower": system.paths["feature-tower"],
        "feature-tower-hard": system.paths["feature-tower-hard"],
        "ann": system.paths["ann"],
        "reranker-u11": system.reranker_u11,
        "full-stack": system.full_stack,
    }
    assert set(ORACLE_TOP10) == {*served, "sasrec"}
    identical = 0
    for name, path in served.items():
        lists = system.top_lists(path, ORACLE_MAIN_READERS)
        for reader, expected in ORACLE_TOP10[name].items():
            overlap = len(set(lists[reader]) & set(expected)) / K
            assert overlap >= 0.9, (name, reader, overlap)
            identical += lists[reader] == expected
    session_lists = system.session_top_lists(ORACLE_SESSION_READERS)
    for reader, expected in ORACLE_TOP10["sasrec"].items():
        overlap = len(set(session_lists[reader]) & set(expected)) / K
        assert overlap >= 0.9, ("sasrec", reader, overlap)
        identical += session_lists[reader] == expected
    print(f"oracle: {identical}/{20 * len(ORACLE_TOP10)} top-10 lists identical")


# ===================================================================== (e)/(f) the assembled system
def test_full_stack_fixed_blend_and_part1_reproduce(system: FullSystem) -> None:
    full = system.evaluate(system.full_stack)
    assert full["hit"] == pytest.approx(0.356, abs=0.003)
    assert full["coverage"] == pytest.approx(0.203, abs=0.003)
    fixed = system.evaluate(system.fixed_blend())
    assert fixed["hit"] == pytest.approx(0.362, abs=0.003)
    assert fixed["coverage"] == pytest.approx(0.206, abs=0.003)
    part1 = system.evaluate(system.part1_build())
    assert part1["hit"] == pytest.approx(0.306, abs=0.002)
    assert part1["coverage"] == pytest.approx(0.333, abs=0.002)
    assert len(system.data.cohort) == 500


# ============================================================ (b)/(c) readouts.json structure
#: The probe's values (plan recsys-017): (Δhit, Δcoverage) per ablation row.
PROBE_DELTAS = {
    "no-reranker": (0.006, 0.0035),
    "exact-two-tower": (-0.002, 0.0),
    "minus-popularity": (0.008, 0.014),
    "minus-lexical": (0.0, -0.031),
    "minus-item-item": (-0.008, -0.014),
    "minus-mf": (-0.008, 0.032),
    "minus-semantic": (-0.004, -0.021),
    "minus-two-tower": (-0.010, 0.015),
    "minus-feature-tower": (0.002, 0.002),
    "minus-hybrid": (-0.006, 0.005),
}


def test_readouts_json_structure(cache: ModelCache) -> None:
    readouts = cache.readouts
    check_readouts(readouts)  # the shared helper the milestone also uses ...
    # ... and an independent restatement of the structural gate here.
    assert readouts["split"] == "val" and readouts["k"] == K and readouts["pool"] == 50
    baselines = readouts["baselines"]
    assert set(baselines) == {"full-stack", "fixed-blend"}
    rows = readouts["ablation"]
    assert len(rows) == 10
    assert [r["row"] for r in rows] == [
        "no-reranker",
        "exact-two-tower",
        *(f"minus-{p}" for p in FULL8_PATH_NAMES),
    ]
    assert [(r["row"], r["kind"], r["baseline"]) for r in rows] == list(ABLATION_ROWS)
    for row in rows:
        expected_base = "full-stack" if row["kind"] == "stage" else "fixed-blend"
        assert row["baseline"] == expected_base
        base = baselines[expected_base]
        for value in (row["hit"], row["coverage"], base["hit"], base["coverage"]):
            assert np.isfinite(value) and 0.0 <= value <= 1.0
        assert abs(row["d_hit"] - (row["hit"] - base["hit"])) <= 1e-9, row["row"]
        assert abs(row["d_coverage"] - (row["coverage"] - base["coverage"])) <= 1e-9, row["row"]
        d_hit, d_cov = PROBE_DELTAS[row["row"]]
        assert row["d_hit"] == pytest.approx(d_hit, abs=0.003), row["row"]
        assert row["d_coverage"] == pytest.approx(d_cov, abs=0.003), row["row"]
    beyond = readouts["beyond_accuracy"]
    assert [r["system"] for r in beyond] == list(BEYOND_ACCURACY_ROWS)
    assert readouts["beyond_accuracy_columns"] == list(BEYOND_ACCURACY_COLUMNS)
    for row in beyond:
        for column in BEYOND_ACCURACY_COLUMNS:
            assert np.isfinite(row[column]), (row["system"], column)
            if column == "novelty":
                assert row[column] > 0.0
            else:
                assert 0.0 <= row[column] <= 1.0, (row["system"], column)
    by_system = {r["system"]: r for r in beyond}
    assert by_system["full-system"]["hit"] == baselines["full-stack"]["hit"]
    assert by_system["best-single-path"]["hit"] == pytest.approx(0.362, abs=0.003)
    assert by_system["part1-build"]["coverage"] == pytest.approx(0.333, abs=0.003)


# =========================================================================== reranker provenance
def test_cached_rerankers_record_the_u11_recipe(cache: ModelCache) -> None:
    for name, names in (("reranker-u11", U11_PATH_NAMES), ("reranker-full8", FULL8_PATH_NAMES)):
        meta = cache.meta(name)
        assert meta["recipe"] == RERANKER_RECIPE == "u11-holdout-75-25"
        assert meta["holdout_frac"] == 0.25 and meta["profile_frac"] == 0.75
        assert tuple(meta["path_names"]) == tuple(names)
        assert meta["n_features"] == 2 * len(names) + 5  # scores + presence + n_paths + 4 content
        art = cache.artifact(name)
        assert art["params"]["leaky"] is False and art["params"]["holdout_frac"] == 0.25
        assert art["feature_names"] == feature_names(names)
        X, y = cache.training_matrix(name)
        assert X.shape == (meta["training_rows"], meta["n_features"]) and set(np.unique(y)) == {
            0.0,
            1.0,
        }


def _reduced_rows(data: BookData, mutated: bool) -> list[dict[str, object]]:
    """The first ~150 readers' rows; ``mutated`` drops val rows and relabels/retimes test rows."""
    keep = sorted({int(r["reader_id"]) for r in data.rows})[:150]
    keep_set = set(keep)
    rows = [dict(r) for r in data.rows if int(r["reader_id"]) in keep_set]
    if not mutated:
        return rows
    out = []
    for row in rows:
        if row["split"] == "val":
            continue  # dropped
        if row["split"] == "test":
            row["label"] = 1 - int(row["label"])  # relabelled
            row["timestamp"] = int(row["timestamp"]) + 10**6
        out.append(row)
    out.append(
        {
            "reader_id": keep[0],
            "item_id": data.catalog_ids[0],
            "session_id": 0,
            "timestamp": 10**9,
            "split": "val",
            "label": 1,
        }
    )  # a bogus val positive
    return out


@pytest.mark.parametrize("kind", ["reranker-u11", "reranker-full8"])
def test_reduced_build_is_invariant_to_val_test_mutation(kind: str, data: BookData) -> None:
    _clean_rr, clean = build_models.build_reranker(
        kind, data, _reduced_rows(data, mutated=False), config=build_models.REDUCED_CONFIG
    )
    _mutated_rr, mutated = build_models.build_reranker(
        kind, data, _reduced_rows(data, mutated=True), config=build_models.REDUCED_CONFIG
    )
    a, b = clean["artifact"], mutated["artifact"]
    for key in ("mu", "sd"):
        np.testing.assert_allclose(a["model"][key], b["model"][key], rtol=0, atol=1e-6)
    for wa, wb in zip(a["model"]["weights"], b["model"]["weights"], strict=True):
        np.testing.assert_allclose(wa, wb, rtol=0, atol=1e-6)
    assert a["counts"] == b["counts"]
    assert a["known_readers"] == b["known_readers"]
    assert a["feature_names"] == b["feature_names"] and a["params"] == b["params"]
    np.testing.assert_array_equal(
        clean["meta"]["training_matrix"]["X"], mutated["meta"]["training_matrix"]["X"]
    )
    np.testing.assert_array_equal(
        clean["meta"]["training_matrix"]["y"], mutated["meta"]["training_matrix"]["y"]
    )
    assert clean["meta"]["recipe"] == mutated["meta"]["recipe"] == RERANKER_RECIPE


class _FixedPath(BaseRetrievalPath):
    """A fixed candidate pool that, like every real path, excludes the reader's seen set."""

    def __init__(self, pool_items: list[int], name: str = "p") -> None:
        super().__init__(name=name, version="1")
        self._pool_items = list(pool_items)
        self._fitted = True

    def fit(self, interactions, catalog=None):
        return self

    def retrieve(self, query, context, k: int) -> list[Candidate]:
        seen = set((context or {}).get("seen", ()))
        items = [i for i in self._pool_items if i not in seen]
        return [Candidate(int(i), float(len(items) - j), self.name) for j, i in enumerate(items)][
            :k
        ]


class _Book:
    def __init__(self) -> None:
        self.fields = {"genres": "fic", "author_id": "auth"}


def test_build_assembly_keeps_repeat_read_holdout_out_of_log_pop() -> None:
    """The Unit-11 leakage regression, re-asserted on ``build_models.assemble_reranker``."""
    rows = [
        {"reader_id": 1, "item_id": 10, "timestamp": 1, "split": "train", "label": 1},
        {"reader_id": 1, "item_id": 10, "timestamp": 2, "split": "train", "label": 1},
        {"reader_id": 1, "item_id": 20, "timestamp": 3, "split": "train", "label": 1},
        {"reader_id": 1, "item_id": 30, "timestamp": 4, "split": "train", "label": 1},
        {"reader_id": 1, "item_id": 10, "timestamp": 5, "split": "train", "label": 1},  # held out
        {"reader_id": 2, "item_id": 40, "timestamp": 1, "split": "train", "label": 1},
        {"reader_id": 2, "item_id": 50, "timestamp": 2, "split": "train", "label": 1},
        {"reader_id": 2, "item_id": 60, "timestamp": 3, "split": "train", "label": 1},
        {"reader_id": 2, "item_id": 10, "timestamp": 4, "split": "train", "label": 1},  # held out
    ]
    profile, labels = split_profile_labels(rows, 0.25)
    assert 10 in profile[1] and labels[1] == {10} and labels[2] == {10}
    pool = [10, 20, 30, 40, 50, 60, 70, 80]
    seen_rows: list[list[dict[str, object]]] = []

    def factory(train_rows):
        seen_rows.append(list(train_rows))
        return {"p": _FixedPath(pool)}

    reranker, X, y = build_models.assemble_reranker(
        {"p": _FixedPath(pool)}, factory, {i: _Book() for i in pool}, rows, ("p",)
    )
    # The profile refit never saw a held-out label event (every occurrence of a label item removed).
    assert len(seen_rows) == 1
    assert not any(r["item_id"] == 10 for r in seen_rows[0])
    positives = np.flatnonzero(y == 1.0)
    assert positives.size == 1  # reader 2's held-out A
    assert X[positives[0], feature_names(("p",)).index("log_pop")] == 0.0
    assert reranker._counts[10] == 4  # serving counts: the unchanged full-train statistic


# ---------------------------------------------------------------------------------------------
# The 20-reader oracle (plan recsys-017 gate (a), v3). Captured ONCE in Phase B from this build
# (first 20 of the sorted main-log val cohort; for SASRec the first 20 of the session-log val
# cohort) and cross-checked against [fable]'s INDEPENDENT probe build (its pickled models, and a
# fresh re-run of probe.py's full-stack recipe): all 160 lists were IDENTICAL before commit.
# ---------------------------------------------------------------------------------------------
ORACLE_MAIN_READERS = [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22]
ORACLE_SESSION_READERS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21]
ORACLE_TOP10: dict[str, dict[int, list[int]]] = {
    "mf": {
        1: [452, 1743, 1415, 1374, 569, 1881, 583, 1425, 925, 1146],
        2: [1110, 92, 1609, 1404, 1284, 956, 666, 517, 877, 1112],
        3: [1404, 1110, 157, 296, 1407, 1586, 651, 399, 1620, 527],
        5: [484, 1568, 1060, 929, 882, 966, 1174, 1743, 727, 583],
        6: [1404, 1620, 890, 1076, 55, 1284, 877, 851, 956, 1276],
        7: [1110, 1404, 727, 1609, 756, 1710, 1425, 569, 527, 1341],
        8: [484, 452, 1774, 1248, 857, 1341, 184, 670, 157, 1380],
        9: [1743, 1620, 517, 583, 890, 1341, 966, 931, 1609, 1813],
        10: [1743, 1341, 925, 1620, 1881, 1813, 890, 1774, 966, 1497],
        11: [452, 1743, 1620, 925, 1415, 1758, 1110, 966, 1497, 37],
        12: [484, 452, 1110, 1404, 1609, 1341, 92, 1284, 1067, 1415],
        14: [1341, 1146, 1415, 883, 1710, 1768, 569, 966, 470, 756],
        15: [1620, 1609, 727, 1710, 55, 452, 1112, 691, 1813, 92],
        16: [1620, 1067, 92, 1076, 877, 890, 1284, 666, 956, 55],
        17: [184, 1248, 183, 452, 484, 157, 1896, 1374, 1404, 1380],
        18: [1110, 1620, 1067, 1076, 1609, 1404, 1710, 92, 517, 890],
        19: [1710, 1568, 929, 756, 1458, 1174, 1957, 588, 1910, 1955],
        20: [756, 484, 929, 1060, 452, 517, 1957, 1174, 588, 1910],
        21: [670, 963, 882, 727, 1710, 1374, 756, 151, 588, 1056],
        22: [1710, 929, 1609, 1404, 756, 1458, 1568, 1620, 890, 1110],
    },
    "two-tower": {
        1: [452, 1497, 818, 1743, 1050, 184, 1248, 1309, 1454, 413],
        2: [1609, 1404, 92, 1110, 1813, 666, 1284, 857, 877, 452],
        3: [1867, 1586, 1925, 1614, 1407, 1521, 1893, 1348, 923, 1240],
        5: [484, 1415, 966, 1774, 37, 1060, 1758, 583, 929, 593],
        6: [1404, 877, 1620, 1769, 851, 890, 1284, 55, 1076, 399],
        7: [1200, 1374, 1348, 1146, 1991, 1765, 924, 1960, 501, 1240],
        8: [448, 184, 1247, 818, 50, 446, 280, 1991, 1421, 1896],
        9: [966, 517, 883, 1743, 931, 1810, 583, 1309, 1774, 413],
        10: [1743, 966, 1497, 1296, 517, 1774, 413, 1762, 37, 1341],
        11: [452, 966, 883, 1415, 1774, 1743, 37, 931, 1497, 583],
        12: [1609, 1404, 92, 666, 1813, 1769, 965, 55, 1364, 1110],
        14: [1341, 966, 1415, 470, 883, 1146, 1309, 517, 1200, 1497],
        15: [756, 1957, 198, 1060, 1629, 265, 1174, 356, 1710, 230],
        16: [92, 1067, 1620, 666, 890, 877, 1813, 1284, 1769, 1276],
        17: [184, 1896, 1248, 50, 1380, 1633, 1016, 482, 418, 183],
        18: [1710, 1060, 929, 756, 265, 666, 1609, 1404, 1910, 1957],
        19: [1710, 756, 1458, 1770, 1568, 929, 1957, 588, 471, 198],
        20: [452, 484, 517, 966, 1060, 1774, 883, 570, 1005, 1758],
        21: [670, 916, 1364, 1708, 963, 1435, 920, 446, 799, 696],
        22: [1710, 1568, 882, 1458, 929, 265, 756, 1957, 471, 1629],
    },
    "feature-tower": {
        1: [452, 505, 240, 855, 1981, 1415, 1743, 387, 107, 395],
        2: [1609, 666, 1284, 857, 1842, 1116, 92, 877, 545, 951],
        3: [1744, 873, 928, 1354, 1006, 84, 1586, 1462, 247, 694],
        5: [882, 1060, 1770, 1606, 230, 1568, 929, 1174, 1746, 712],
        6: [1404, 890, 1620, 1769, 1956, 1112, 1276, 1842, 385, 851],
        7: [180, 448, 1190, 1659, 1374, 1050, 328, 1711, 610, 293],
        8: [328, 1378, 1991, 1625, 1637, 1165, 748, 202, 90, 1823],
        9: [517, 931, 855, 387, 1743, 107, 682, 1679, 883, 413],
        10: [1743, 855, 925, 505, 931, 195, 966, 1810, 1497, 1789],
        11: [452, 855, 1743, 1497, 931, 966, 1415, 107, 925, 387],
        12: [1338, 1333, 1609, 1112, 431, 350, 1769, 1510, 956, 854],
        14: [855, 1497, 517, 583, 240, 1309, 107, 931, 925, 1341],
        15: [1217, 1142, 1640, 756, 427, 672, 1406, 794, 599, 1551],
        16: [1067, 666, 890, 92, 1620, 1769, 1076, 55, 545, 1842],
        17: [184, 1823, 1648, 200, 1896, 418, 1326, 1628, 99, 372],
        18: [1710, 230, 882, 1174, 1210, 265, 929, 756, 454, 1060],
        19: [1710, 1458, 756, 1770, 1174, 1568, 454, 891, 1955, 230],
        20: [230, 413, 1497, 19, 1686, 891, 1572, 669, 481, 387],
        21: [1562, 670, 63, 955, 696, 727, 1051, 1507, 1972, 520],
        22: [1710, 756, 1770, 1174, 1568, 1458, 1955, 882, 1957, 891],
    },
    "feature-tower-hard": {
        1: [116, 298, 1378, 547, 443, 630, 62, 1247, 479, 90],
        2: [109, 1842, 1854, 1116, 1087, 1813, 1112, 1436, 1884, 919],
        3: [873, 1744, 57, 928, 249, 1462, 1877, 247, 1354, 1930],
        5: [1758, 1415, 20, 1627, 855, 570, 93, 37, 1392, 1810],
        6: [877, 851, 1551, 890, 455, 1391, 691, 385, 449, 1916],
        7: [180, 1659, 870, 610, 1308, 1190, 448, 443, 1126, 1522],
        8: [1823, 1648, 1393, 1752, 529, 784, 1624, 1600, 532, 1532],
        9: [1627, 517, 1810, 395, 93, 94, 855, 931, 228, 1611],
        10: [195, 855, 1743, 1774, 107, 1611, 1810, 801, 505, 1679],
        11: [20, 1774, 505, 1679, 94, 931, 883, 1627, 1497, 1611],
        12: [1112, 1094, 771, 1278, 431, 109, 1854, 385, 854, 186],
        14: [505, 855, 228, 1679, 1497, 1774, 1415, 1356, 1611, 413],
        15: [125, 1640, 417, 1217, 1142, 567, 455, 1916, 672, 13],
        16: [1076, 187, 1278, 1701, 1154, 1067, 1842, 688, 1284, 141],
        17: [529, 1823, 1326, 633, 678, 271, 1648, 418, 341, 1532],
        18: [230, 211, 1979, 265, 1910, 882, 663, 1642, 1210, 1519],
        19: [663, 1642, 211, 1519, 1458, 1020, 588, 56, 1241, 1785],
        20: [1572, 883, 195, 1679, 1497, 94, 484, 1743, 1774, 1392],
        21: [963, 670, 955, 643, 1280, 1852, 1361, 540, 615, 1093],
        22: [1174, 912, 756, 1655, 471, 373, 1519, 1770, 1785, 1575],
    },
    "ann": {
        1: [452, 1497, 818, 1743, 1050, 184, 1248, 1309, 1454, 413],
        2: [1609, 1404, 92, 1110, 1813, 666, 1284, 857, 877, 452],
        3: [1867, 1586, 1925, 1614, 1407, 1521, 1893, 1348, 923, 1240],
        5: [484, 1415, 966, 1774, 37, 1060, 1758, 583, 929, 593],
        6: [1404, 877, 1620, 1769, 851, 890, 1284, 55, 1076, 399],
        7: [1200, 1374, 1348, 1146, 1991, 1765, 924, 1960, 501, 1240],
        8: [448, 184, 1247, 818, 50, 446, 280, 1991, 1421, 1896],
        9: [966, 517, 883, 1743, 931, 1810, 583, 1309, 1774, 413],
        10: [1743, 966, 1497, 1296, 517, 1774, 413, 1762, 37, 1341],
        11: [452, 966, 883, 1415, 1774, 1743, 37, 931, 1497, 583],
        12: [1609, 1404, 92, 666, 1813, 1769, 965, 55, 1364, 1110],
        14: [1341, 966, 1415, 470, 883, 1146, 1309, 517, 1200, 1497],
        15: [756, 1957, 198, 1060, 1629, 265, 1174, 356, 1710, 230],
        16: [92, 1067, 1620, 666, 890, 877, 1813, 1284, 1769, 1276],
        17: [184, 1896, 1248, 50, 1380, 1633, 1016, 482, 418, 183],
        18: [1710, 1060, 929, 756, 265, 666, 1609, 1404, 1910, 1957],
        19: [1710, 756, 1458, 1770, 1568, 929, 1957, 588, 471, 198],
        20: [452, 484, 517, 966, 1060, 1774, 883, 570, 1005, 1758],
        21: [670, 916, 1364, 1708, 963, 1435, 920, 446, 799, 696],
        22: [1710, 1568, 882, 1458, 929, 265, 756, 1957, 471, 1629],
    },
    "reranker-u11": {
        1: [452, 1743, 19, 1415, 966, 1247, 818, 1497, 1810, 570],
        2: [1609, 1110, 1404, 92, 1813, 951, 666, 1510, 453, 545],
        3: [1348, 1586, 1521, 1867, 1138, 1006, 873, 1614, 469, 1407],
        5: [484, 1774, 1497, 583, 1415, 1743, 1758, 1810, 1309, 107],
        6: [1404, 1620, 851, 890, 55, 1769, 1076, 399, 877, 965],
        7: [470, 1526, 1765, 1050, 1960, 328, 1146, 1987, 1816, 762],
        8: [446, 818, 1247, 1380, 762, 1378, 448, 1393, 1896, 532],
        9: [583, 1743, 883, 1810, 1774, 931, 1309, 517, 413, 107],
        10: [1743, 1774, 583, 1497, 925, 517, 1762, 1468, 413, 20],
        11: [452, 1743, 883, 1774, 931, 583, 1468, 570, 1415, 925],
        12: [1609, 92, 1110, 1404, 1067, 1510, 965, 440, 55, 1842],
        14: [883, 1415, 517, 583, 1497, 925, 1758, 570, 1468, 931],
        15: [1957, 756, 1568, 1979, 929, 1458, 1060, 265, 1955, 882],
        16: [92, 1067, 1620, 187, 890, 1769, 55, 1076, 399, 666],
        17: [1248, 184, 1628, 1380, 1896, 1633, 418, 50, 1016, 71],
        18: [1710, 1060, 1609, 1110, 1813, 348, 929, 861, 756, 1404],
        19: [1710, 1458, 756, 929, 588, 454, 451, 1568, 230, 210],
        20: [452, 1060, 1497, 1774, 484, 925, 1743, 883, 756, 107],
        21: [670, 1708, 1051, 1364, 1562, 1435, 799, 827, 916, 920],
        22: [1710, 756, 929, 1174, 1910, 178, 1568, 471, 588, 265],
    },
    "full-stack": {
        1: [452, 19, 1415, 925, 966, 1247, 387, 1743, 1309, 517],
        2: [1609, 1404, 92, 1110, 1284, 666, 851, 1112, 877, 545],
        3: [873, 1348, 1586, 1521, 1006, 1407, 469, 1296, 1614, 923],
        5: [484, 1060, 1415, 1309, 1810, 966, 1762, 1356, 929, 583],
        6: [1404, 890, 1620, 851, 877, 861, 965, 1769, 1112, 691],
        7: [328, 1050, 1454, 762, 1816, 470, 1660, 1025, 130, 1190],
        8: [1380, 818, 1637, 1896, 1991, 446, 628, 1247, 328, 1393],
        9: [1743, 583, 966, 883, 1309, 1810, 107, 931, 1774, 517],
        10: [1743, 583, 966, 1497, 1774, 925, 107, 931, 1762, 19],
        11: [452, 1415, 1743, 883, 966, 583, 1774, 925, 931, 1497],
        12: [1609, 1110, 1510, 1067, 1404, 92, 1769, 1284, 965, 666],
        14: [583, 883, 1415, 925, 1497, 517, 966, 931, 1468, 1341],
        15: [756, 1217, 794, 929, 1458, 1710, 1568, 1406, 1957, 265],
        16: [1067, 92, 890, 666, 1620, 877, 861, 965, 55, 1284],
        17: [418, 1896, 184, 1648, 1380, 1823, 1248, 1016, 1633, 200],
        18: [1710, 1060, 877, 1609, 265, 1110, 929, 1404, 756, 1957],
        19: [1710, 1458, 1568, 756, 588, 929, 454, 1910, 1174, 451],
        20: [452, 1774, 1497, 925, 1174, 1060, 484, 891, 19, 413],
        21: [670, 1708, 151, 1051, 963, 916, 799, 1562, 920, 727],
        22: [1710, 1174, 756, 265, 1568, 178, 471, 1910, 588, 451],
    },
    "sasrec": {
        1: [1341, 531, 1768, 1759, 1200, 1137, 163, 470, 637, 1938],
        2: [666, 13, 1609, 1110, 1462, 385, 1344, 861, 1406, 1850],
        3: [1609, 1067, 92, 890, 1404, 1620, 851, 666, 861, 1076],
        4: [591, 962, 692, 669, 1527, 226, 1686, 434, 671, 909],
        5: [929, 1957, 1770, 265, 1060, 230, 882, 373, 1174, 215],
        6: [1067, 890, 1609, 1404, 1620, 851, 1064, 861, 877, 854],
        7: [1146, 1686, 401, 469, 1960, 1569, 226, 639, 1351, 990],
        8: [1217, 13, 794, 826, 1434, 708, 370, 1342, 343, 599],
        9: [1974, 1733, 1562, 1540, 1435, 1399, 1708, 799, 1051, 615],
        10: [1341, 1759, 1146, 1960, 531, 1768, 569, 1137, 1079, 1425],
        11: [163, 1110, 1620, 890, 92, 1404, 1067, 440, 1444, 1701],
        12: [1146, 373, 929, 1568, 531, 1713, 1765, 756, 1768, 215],
        13: [1957, 265, 1568, 756, 1770, 1174, 215, 891, 1370, 1241],
        15: [1466, 1351, 1131, 120, 639, 1819, 226, 962, 941, 49],
        16: [593, 72, 148, 642, 237, 203, 1946, 1162, 340, 881],
        17: [593, 340, 148, 1878, 875, 1478, 72, 631, 1559, 504],
        18: [1710, 1060, 1458, 230, 882, 215, 210, 1174, 198, 891],
        19: [1364, 1637, 1733, 916, 696, 961, 328, 1974, 1562, 1765],
        20: [1341, 1759, 1960, 1200, 884, 1768, 1339, 569, 470, 1429],
        21: [1540, 963, 670, 920, 1733, 799, 1562, 1435, 1852, 1338],
    },
}
