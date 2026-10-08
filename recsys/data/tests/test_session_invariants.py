"""Invariants for the U12 series + session log (plan recsys-014 Phase C; ``gen_sessions.py``).

Schemas; a leakage-free per-reader ``train < val < test`` split by timestamp; strictly increasing
session times; no cold item ever exposed; well-formed series (one series per book, contiguous
volumes ``1..L``, one author, ``series_len_min <= L <= series_len_max``, ``(year, item_id)``
order); byte-identical regeneration; and the ``DatasetConfig.__post_init__`` knob validation.

Most checks run on a small in-memory config; the last test re-checks the CI-generated files on disk
(skipped when the generated directory is absent).
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from dataclasses import replace
from itertools import pairwise
from pathlib import Path

import numpy as np
import pytest
from _common import GENERATED_DIR, DatasetConfig
from _dataset_fixture import small_config
from _reference_recommenders import ordered_positive_sequences, ordered_train_sequences
from gen_catalog import generate_catalog
from gen_interactions import build_dataset
from gen_sessions import (
    SERIES_COLUMNS,
    SESSION_COLUMNS,
    generate_series,
    generate_sessions,
    write_series,
    write_sessions,
)


def _session_config() -> DatasetConfig:
    return replace(small_config(), session_n_readers=150)


@pytest.fixture(scope="module")
def world():
    """(config, catalog, cold_items, series, session log) for the small session config."""
    config = _session_config()
    inter = build_dataset(config)
    series = generate_series(inter.catalog, config)
    log = generate_sessions(inter.catalog, series, inter.cold_items, config)
    return config, inter.catalog, inter.cold_items, series, log


def _read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with gzip.open(path, mode="rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def _assert_series_well_formed(item_ids, series_ids, volumes, author_ids, years, lo, hi) -> None:
    assert len(set(item_ids)) == len(item_ids), "a book appears in more than one series row"
    members: dict[int, list[tuple[int, int]]] = {}
    for item, sid, vol in zip(item_ids, series_ids, volumes):
        members.setdefault(int(sid), []).append((int(vol), int(item)))
    assert sorted(members) == list(range(len(members))), "series ids are not 0..n-1"
    for sid, rows in members.items():
        rows.sort()
        vols = [v for v, _ in rows]
        books = [b for _, b in rows]
        assert vols == list(range(1, len(rows) + 1)), (sid, vols)
        assert lo <= len(rows) <= hi, (sid, len(rows))
        assert len({int(author_ids[b]) for b in books}) == 1, (sid, books)
        keys = [(int(years[b]), b) for b in books]
        assert keys == sorted(keys), (sid, keys)


def _assert_session_log_invariants(reader_ids, timestamps, session_ids, splits) -> None:
    order_ok = 0
    for u in np.unique(reader_ids):
        rows = np.nonzero(reader_ids == u)[0]
        ts, sess, sp = timestamps[rows], session_ids[rows], splits[rows]
        # File order is event order: timestamps and session ids never go backwards.
        assert np.all(np.diff(ts) >= 0) and np.all(np.diff(sess) >= 0), u
        # Sessions are strictly time-separated: each session ends before the next one starts.
        uniq = np.unique(sess)
        for a, b in pairwise(uniq):
            assert ts[sess == a].max() < ts[sess == b].min(), (u, a, b)
        have = {name: ts[sp == name] for name in ("train", "val", "test")}
        assert all(len(have[name]) for name in have), (u, {k: len(v) for k, v in have.items()})
        assert have["train"].max() < have["val"].min(), u
        assert have["val"].max() < have["test"].min(), u
        # A split never interleaves: once a reader leaves train it never returns to it.
        rank = np.array([{"train": 0, "val": 1, "test": 2}[s] for s in sp])
        assert np.all(np.diff(rank) >= 0), u
        order_ok += 1
    assert order_ok > 0


# ---------------------------------------------------------------------------------------- schemas
def test_written_schemas_and_manifest_checksums(world, tmp_path: Path) -> None:
    _, _, _, series, log = world
    series_manifest = write_series(series, tmp_path)
    session_manifest = write_sessions(log, tmp_path)
    series_header, series_rows = _read_rows(tmp_path / "series.csv.gz")
    session_header, session_rows = _read_rows(tmp_path / "sessions.csv.gz")
    assert series_header == SERIES_COLUMNS == ["item_id", "series_id", "volume"]
    assert session_header == SESSION_COLUMNS
    assert SESSION_COLUMNS == ["reader_id", "item_id", "session_id", "timestamp", "split", "label"]
    assert len(series_rows) == series.item_ids.shape[0]
    assert len(session_rows) == log.n_events
    assert {row["split"] for row in session_rows} == {"train", "val", "test"}
    assert {row["label"] for row in session_rows} == {"0", "1"}
    for manifest in (series_manifest, session_manifest):
        for name, digest in manifest.checksums.items():
            assert hashlib.sha256((tmp_path / name).read_bytes()).hexdigest() == digest


# -------------------------------------------------------------------------------------- sessions
def test_session_splits_are_leakage_free_and_time_ordered(world) -> None:
    _, _, _, _, log = world
    _assert_session_log_invariants(log.reader_ids, log.timestamps, log.session_ids, log.splits)
    assert log.reader_ids.max() < log.config.session_n_readers


def test_no_cold_item_is_ever_exposed(world) -> None:
    _, _, cold_items, _, log = world
    assert cold_items.size > 0
    assert set(log.item_ids.tolist()).isdisjoint(set(cold_items.tolist()))


def test_ordered_train_sequences_follow_the_goal3_key(world, tmp_path: Path) -> None:
    _, _, _, _, log = world
    write_sessions(log, tmp_path)
    loaded = ordered_train_sequences(tmp_path / "sessions.csv.gz")
    train, _ = ordered_positive_sequences(
        log.reader_ids, log.item_ids, log.timestamps, log.splits, log.labels
    )
    assert loaded == train
    for u, seq in loaded.items():
        rows = np.nonzero((log.reader_ids == u) & (log.labels == 1) & (log.splits == "train"))[0]
        assert seq == log.item_ids[rows].tolist()  # file order == (timestamp, row) order


# ---------------------------------------------------------------------------------------- series
def test_series_are_well_formed(world) -> None:
    config, catalog, _, series, _ = world
    assert series.item_ids.size > 0
    _assert_series_well_formed(
        series.item_ids.tolist(),
        series.series_ids.tolist(),
        series.volumes.tolist(),
        catalog.author_ids,
        catalog.years,
        config.series_len_min,
        config.series_len_max,
    )


def test_series_ignores_the_session_seed() -> None:
    config = _session_config()
    catalog = generate_catalog(config, np.random.default_rng(config.seed))
    a = generate_series(catalog, config)
    b = generate_series(catalog, replace(config, session_seed=7))
    assert np.array_equal(a.item_ids, b.item_ids) and np.array_equal(a.volumes, b.volumes)


# ---------------------------------------------------------------------------------- determinism
def _write_small_world(out_dir: Path, config: DatasetConfig) -> None:
    inter = build_dataset(config)
    series = generate_series(inter.catalog, config)
    write_series(series, out_dir)
    write_sessions(generate_sessions(inter.catalog, series, inter.cold_items, config), out_dir)


def test_series_and_sessions_regenerate_byte_identically(tmp_path: Path) -> None:
    config = _session_config()
    _write_small_world(tmp_path / "a", config)
    _write_small_world(tmp_path / "b", config)
    for name in ("series.csv.gz", "sessions.csv.gz"):
        assert (tmp_path / "a" / name).read_bytes() == (tmp_path / "b" / name).read_bytes()


def test_session_seed_varies_only_the_session_log(world) -> None:
    config, catalog, cold_items, series, log = world
    other = generate_sessions(catalog, series, cold_items, replace(config, session_seed=99))
    assert not (other.n_events == log.n_events and np.array_equal(other.item_ids, log.item_ids)), (
        "session_seed should re-draw the session log"
    )


# ---------------------------------------------------------------------------------- validation
@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"series_fraction": 0.0}, "series_fraction"),
        ({"series_fraction": 1.0}, "series_fraction"),
        ({"series_len_min": 1}, "series lengths"),
        ({"series_len_min": 6, "series_len_max": 5}, "series lengths"),
        ({"session_n_readers": 0}, "session_n_readers"),
        ({"session_mean_sessions": 0.0}, "session_mean_sessions"),
        ({"session_min_sessions": 2}, "session_min_sessions"),
        ({"session_max_items": 0}, "session_max_items"),
        ({"session_negatives_per_positive": -1}, "session_negatives_per_positive"),
        ({"session_series_window": 0}, "session_series_window"),
        ({"session_series_follow_prob": 1.5}, "session_series_follow_prob"),
        ({"session_author_decay": -0.1}, "session_author_decay"),
        ({"session_mood_persist": 2.0}, "session_mood_persist"),
        ({"session_series_accept": -1.0}, "session_series_accept"),
        ({"session_author_bump": -1.0}, "session_author_bump"),
        ({"session_mood_boost": -0.5}, "session_mood_boost"),
    ],
)
def test_invalid_series_and_session_knobs_are_rejected(overrides: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        DatasetConfig(**overrides)


def test_effective_session_seed_defaults_to_the_committed_seed() -> None:
    assert DatasetConfig().effective_session_seed == DatasetConfig().seed
    assert DatasetConfig(session_seed=3).effective_session_seed == 3


# ------------------------------------------------------------------------- CI-generated on disk
def test_ci_generated_series_and_sessions_satisfy_invariants() -> None:
    if not GENERATED_DIR.is_dir():
        pytest.skip("CI-generated artifacts are absent; run gen_catalog.py and gen_interactions.py")
    names = ("catalog.csv.gz", "cold_partitions.json", "series.csv.gz", "sessions.csv.gz")
    missing = [n for n in names if not (GENERATED_DIR / n).is_file()]
    assert not missing, f"generated directory is incomplete (missing: {', '.join(missing)})"
    config = DatasetConfig()

    _, catalog_rows = _read_rows(GENERATED_DIR / "catalog.csv.gz")
    authors = {int(r["item_id"]): int(r["author_id"]) for r in catalog_rows}
    years = {int(r["item_id"]): int(r["year"]) for r in catalog_rows}

    header, series_rows = _read_rows(GENERATED_DIR / "series.csv.gz")
    assert header == SERIES_COLUMNS
    _assert_series_well_formed(
        [int(r["item_id"]) for r in series_rows],
        [int(r["series_id"]) for r in series_rows],
        [int(r["volume"]) for r in series_rows],
        authors,
        years,
        config.series_len_min,
        config.series_len_max,
    )

    header, rows = _read_rows(GENERATED_DIR / "sessions.csv.gz")
    assert header == SESSION_COLUMNS
    reader_ids = np.array([int(r["reader_id"]) for r in rows], dtype=np.int64)
    item_ids = np.array([int(r["item_id"]) for r in rows], dtype=np.int64)
    timestamps = np.array([int(r["timestamp"]) for r in rows], dtype=np.int64)
    session_ids = np.array([int(r["session_id"]) for r in rows], dtype=np.int64)
    splits = np.array([r["split"] for r in rows], dtype="<U5")
    assert len(np.unique(reader_ids)) == config.session_n_readers
    _assert_session_log_invariants(reader_ids, timestamps, session_ids, splits)

    cold = json.loads((GENERATED_DIR / "cold_partitions.json").read_text(encoding="utf-8"))
    assert set(item_ids.tolist()).isdisjoint(set(cold["cold_items"]))
