"""CI-generated-dataset validation (design 011 §6/§9, plan recsys-001 Phase E).

The invariant suite in ``test_invariants.py`` checks the in-memory generator objects. This module
closes the gap flagged in content review: it writes the DEFAULT dataset to disk, loads the catalog
back through the *shipped* ``bookrec.load_catalog`` loader, re-parses the interaction CSV with the
stdlib, and re-asserts the leakage-free temporal split + cold-partition-disjoint invariants on the
ON-DISK bytes — not just the in-memory arrays. Fully deterministic (one seeded numpy stream).

Runs in the routed ``uv run --group recsys pytest recsys/`` step, where ``bookrec`` is installed.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from _common import GENERATED_DIR
from bookrec import load_catalog

CATALOG_COLUMNS = ["item_id", "title", "author_id", "genres", "year"]
KEYWORD_COLUMNS = ["item_id", "keywords"]
INTERACTION_COLUMNS = ["reader_id", "item_id", "session_id", "timestamp", "split", "label"]


def _read_interactions(path: Path):
    readers: list[int] = []
    items: list[int] = []
    timestamps: list[int] = []
    splits: list[str] = []
    with gzip.open(path, mode="rt", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            readers.append(int(row["reader_id"]))
            items.append(int(row["item_id"]))
            timestamps.append(int(row["timestamp"]))
            splits.append(row["split"])
    return (
        np.array(readers, dtype=np.int64),
        np.array(items, dtype=np.int64),
        np.array(timestamps, dtype=np.int64),
        np.array(splits, dtype="<U5"),
    )


def _require_generated_dir() -> Path:
    if not GENERATED_DIR.is_dir():
        pytest.skip(
            "CI-generated artifacts are absent; run gen_catalog.py and gen_interactions.py first"
        )
    required = {
        "catalog.csv.gz",
        "keywords.csv.gz",
        "interactions.csv.gz",
        "cold_partitions.json",
        "checksums.json",
    }
    missing = sorted(name for name in required if not (GENERATED_DIR / name).is_file())
    assert not missing, (
        "generated directory is incomplete; run both generators "
        f"(missing: {', '.join(missing)})"
    )
    return GENERATED_DIR


def _read_header(path: Path) -> list[str]:
    with gzip.open(path, mode="rt", encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle))


def test_ci_generated_artifacts_have_expected_schema_and_checksums() -> None:
    generated_dir = _require_generated_dir()
    assert _read_header(generated_dir / "catalog.csv.gz") == CATALOG_COLUMNS
    assert _read_header(generated_dir / "keywords.csv.gz") == KEYWORD_COLUMNS
    assert _read_header(generated_dir / "interactions.csv.gz") == INTERACTION_COLUMNS

    manifest = json.loads((generated_dir / "checksums.json").read_text(encoding="utf-8"))
    assert set(manifest) == {
        "catalog.csv.gz",
        "keywords.csv.gz",
        "interactions.csv.gz",
        "cold_partitions.json",
    }
    for name, expected in manifest.items():
        actual = hashlib.sha256((generated_dir / name).read_bytes()).hexdigest()
        assert actual == expected


def test_ci_generated_artifacts_satisfy_split_and_cold_partition_invariants() -> None:
    generated_dir = _require_generated_dir()

    # 1) The catalog loads via the shipped bookrec loader from the written CSV bytes.
    loaded = load_catalog(generated_dir / "catalog.csv.gz")
    assert len(loaded) > 0

    # 2) Re-parse the interactions CSV and re-assert invariants on the ON-DISK data.
    reader_ids, item_ids, timestamps, splits = _read_interactions(
        generated_dir / "interactions.csv.gz"
    )
    assert set(np.unique(splits)) == {"train", "val", "test"}
    assert set(item_ids.tolist()) <= set(loaded)

    # Leakage-free temporal split per warm reader: train < val < test by event time.
    checked = 0
    for u in np.unique(reader_ids):
        rows = reader_ids == u
        ts = timestamps[rows]
        sp = splits[rows]
        have = {name: ts[sp == name] for name in ("train", "val", "test")}
        if not all(len(have[name]) for name in ("train", "val", "test")):
            continue
        assert have["train"].max() < have["val"].min()
        assert have["val"].max() < have["test"].min()
        checked += 1
    assert checked > 0

    # Cold partitions disjoint from train, using persisted metadata from the same CLI run.
    cold = json.loads((generated_dir / "cold_partitions.json").read_text(encoding="utf-8"))
    assert set(cold) == {"cold_items", "cold_readers"}
    train = splits == "train"
    assert set(item_ids[train].tolist()).isdisjoint(set(cold["cold_items"]))
    assert set(reader_ids[train].tolist()).isdisjoint(set(cold["cold_readers"]))
