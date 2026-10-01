"""Model-free invariant tests for the seeded data substrate (design 011 §6, plan recsys-001).

These assert the *structure* the generator promises — enrichment, skew, leakage-safe splits, cold
partitions, session order, determinism — using only counting and the exposed ground-truth, never a
trained model. Thresholds are generous so they pin the signal without being brittle (NEP-19).
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
import slice_books
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


def _attestation(path: Path, *, license_line: str, extra: str = "") -> Path:
    path.write_text(
        f"source: books-mirror\n{license_line}\nconfirmed_by: tester\ndate: 2026-09-30\n{extra}",
        encoding="utf-8",
    )
    return path


def test_slice_refuses_non_permissive_license(tmp_path: Path, capsys) -> None:
    att = _attestation(tmp_path / "att.yaml", license_line="license: unknown")
    out = tmp_path / "out"
    assert slice_main(["--attestation", str(att), "--dsn", "db://x", "--output", str(out)]) == 1
    assert "not in the permissive allowlist" in capsys.readouterr().err
    assert not out.exists()


def test_slice_refuses_missing_license(tmp_path: Path, capsys) -> None:
    att = tmp_path / "att.yaml"
    att.write_text("source: books-mirror\nconfirmed_by: tester\ndate: 2026-09-30\n", "utf-8")
    out = tmp_path / "out"
    assert slice_main(["--attestation", str(att), "--dsn", "db://x", "--output", str(out)]) == 1
    assert "attestation must record" in capsys.readouterr().err
    assert not out.exists()


def test_slice_permissive_license_takes_the_db_path(tmp_path: Path, monkeypatch) -> None:
    att = _attestation(tmp_path / "att.yaml", license_line="license: CC0")
    monkeypatch.setattr(
        slice_books,
        "_rows_from_postgres",
        lambda dsn, limit: [
            {"item_id": 0, "title": "Dune", "author": "Herbert", "subjects": "sci-fi", "isbn": "1"},
        ],
    )
    out = tmp_path / "out"
    code = slice_main(["--attestation", str(att), "--dsn", "db://x", "--output", str(out)])
    assert code == 0
    manifest = json.loads((out / "books_slice.manifest.json").read_text(encoding="utf-8"))
    assert manifest["source"] == "postgres:books-mirror"
    assert manifest["notes"]["license"] == "CC0"
    assert manifest["rowcounts"]["books_slice"] == 1


@pytest.mark.parametrize("license_value", ["unknown", "ISBNdb"])
def test_slice_permissive_flag_cannot_override_license_allowlist(
    tmp_path: Path, monkeypatch, license_value: str
) -> None:
    att = _attestation(
        tmp_path / "att.yaml",
        license_line=f"license: {license_value}",
        extra="permissive: true\n",
    )

    def unexpected_db_call(dsn, limit):
        pytest.fail("non-allowlisted attestation reached the PostgreSQL layer")

    monkeypatch.setattr(slice_books, "_rows_from_postgres", unexpected_db_call)
    out = tmp_path / "out"
    assert slice_main(["--attestation", str(att), "--dsn", "db://x", "--output", str(out)]) == 1
    assert not out.exists()


def test_popularity_exposure_weight_changes_exposure_skew() -> None:
    base = small_config()
    flat = build_dataset(replace(base, popularity_exposure_weight=0.0))
    sharp = build_dataset(replace(base, popularity_exposure_weight=3.0))

    def top_decile_share(dataset) -> float:
        counts = np.bincount(dataset.item_ids, minlength=dataset.catalog.n_books)
        ordered = np.sort(counts)[::-1]
        top = max(1, len(ordered) // 10)
        return float(ordered[:top].sum() / ordered.sum())

    # weight=0 flattens exposure toward uniform; weight=3 sharpens the popular head.
    assert top_decile_share(sharp) > top_decile_share(flat)


def test_generated_dir_is_gitignored() -> None:
    gitignore = (Path(__file__).resolve().parents[3] / ".gitignore").read_text(encoding="utf-8")
    assert "recsys/data/generated/" in gitignore
    assert GENERATED_DIR.name == "generated"
