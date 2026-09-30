"""Model-free invariant tests for the seeded data substrate (design 011 §6, plan recsys-001).

These assert the *structure* the generator promises — enrichment, skew, leakage-safe splits, cold
partitions, session order, determinism — using only counting and the exposed ground-truth, never a
trained model. Thresholds are generous so they pin the signal without being brittle (NEP-19).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from _common import GENERATED_DIR
from _dataset_fixture import small_config
from gen_catalog import generate_catalog, write_catalog
from gen_interactions import build_dataset, generate_interactions, write_interactions
from slice_books import main as slice_main


def _pair_affinity(dataset, readers: np.ndarray, items: np.ndarray) -> np.ndarray:
    latent = (dataset.catalog.latent[items] * dataset.reader_latent[readers]).sum(axis=1)
    feature = (dataset.catalog.genre_matrix[items] * dataset.reader_prefs[readers]).sum(axis=1)
    return latent + dataset.config.feature_weight * feature


def test_dataset_has_positives_and_all_splits(dataset) -> None:
    assert dataset.labels.sum() > 0
    assert set(np.unique(dataset.splits)) == {"train", "val", "test"}


def test_observed_positives_are_enriched_vs_true_affinity(dataset) -> None:
    rng = np.random.default_rng(0)
    pos = dataset.mask(label=1)
    readers = dataset.reader_ids[pos]
    items = dataset.item_ids[pos]
    negatives = rng.integers(0, dataset.catalog.n_books, size=items.shape[0])
    pos_aff = _pair_affinity(dataset, readers, items)
    neg_aff = _pair_affinity(dataset, readers, negatives)
    auc = float(np.mean(pos_aff > neg_aff))  # AUC of true-affinity ranking positives over randoms
    assert auc > 0.7, auc


def test_interaction_counts_show_popularity_skew(dataset) -> None:
    counts = np.bincount(dataset.item_ids, minlength=dataset.catalog.n_books)
    ordered = np.sort(counts)[::-1]
    top_decile = max(1, len(ordered) // 10)
    share = ordered[:top_decile].sum() / ordered.sum()
    assert share > 0.3, share  # popularity-biased exposure concentrates interactions


def test_per_reader_temporal_splits_are_leakage_free(dataset) -> None:
    checked = 0
    for u in np.unique(dataset.reader_ids):
        rows = dataset.reader_ids == u
        ts = dataset.timestamps[rows]
        sp = dataset.splits[rows]
        have = {name: ts[sp == name] for name in ("train", "val", "test")}
        if not all(len(have[name]) for name in ("train", "val", "test")):
            continue
        assert have["train"].max() < have["val"].min()
        assert have["val"].max() < have["test"].min()
        checked += 1
    assert checked > 0  # at least some warm readers exercise all three splits


def test_cold_partitions_are_disjoint_from_train(dataset) -> None:
    train = dataset.mask(split="train")
    train_items = set(dataset.item_ids[train].tolist())
    train_readers = set(dataset.reader_ids[train].tolist())
    assert train_items.isdisjoint(set(dataset.cold_items.tolist()))
    assert train_readers.isdisjoint(set(dataset.cold_readers.tolist()))


def test_sessions_are_time_ordered(dataset) -> None:
    for u in np.unique(dataset.reader_ids):
        rows = dataset.reader_ids == u
        ts = dataset.timestamps[rows]
        sessions = dataset.session_ids[rows]
        order = np.argsort(sessions, kind="stable")
        assert np.all(np.diff(ts[order]) >= 0)  # timestamps non-decreasing along session order


def test_generation_is_deterministic_under_the_same_seed() -> None:
    config = small_config()
    a = build_dataset(config)
    b = build_dataset(config)
    assert np.array_equal(a.item_ids, b.item_ids)
    assert np.array_equal(a.labels, b.labels)
    assert np.array_equal(a.timestamps, b.timestamps)
    assert np.array_equal(a.splits, b.splits)


def test_written_files_are_byte_identical_across_runs(tmp_path: Path) -> None:
    config = small_config()
    outs = []
    for name in ("a", "b"):
        rng = np.random.default_rng(config.seed)
        catalog = generate_catalog(config, rng)
        inter = generate_interactions(catalog, config, rng)
        out = tmp_path / name
        write_catalog(catalog, out)
        write_interactions(inter, out)
        outs.append(out)
    for fname in ("catalog.csv.gz", "interactions.csv.gz"):
        assert (outs[0] / fname).read_bytes() == (outs[1] / fname).read_bytes()


def test_slice_fails_closed_without_permission(capsys) -> None:
    assert slice_main([]) == 1
    assert "refusing to slice" in capsys.readouterr().err


def test_slice_openlibrary_fallback_writes_normalised_dedup_slice(tmp_path: Path) -> None:
    dump = tmp_path / "ol.jsonl"
    dump.write_text(
        "\n".join(
            [
                json.dumps({"title": "  Dune  ", "author": "Herbert", "subjects": ["sci-fi"]}),
                json.dumps({"title": "Dune", "author": "Herbert", "subjects": ["sci-fi"]}),
                json.dumps({"title": "Emma", "author": "Austen", "isbn": "123"}),
            ]
        ),
        encoding="utf-8",
    )
    out = tmp_path / "out"
    assert slice_main(["--openlibrary", str(dump), "--output", str(out)]) == 0
    manifest = json.loads((out / "books_slice.manifest.json").read_text(encoding="utf-8"))
    assert manifest["rowcounts"]["books_slice"] == 2  # the duplicate Dune row is deduped
    assert manifest["notes"]["promotable"] is False
    assert (out / "books_slice.csv.gz").is_file()


def test_generated_dir_is_gitignored() -> None:
    gitignore = (Path(__file__).resolve().parents[3] / ".gitignore").read_text(encoding="utf-8")
    assert "recsys/data/generated/" in gitignore
    assert GENERATED_DIR.name == "generated"
