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
from pathlib import Path

import numpy as np
from _common import DatasetConfig
from bookrec import load_catalog
from gen_catalog import generate_catalog, write_catalog
from gen_interactions import generate_interactions, write_interactions


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


def test_generated_csv_satisfies_invariants_on_disk(tmp_path: Path) -> None:
    # The DEFAULT dataset, generated deterministically from one threaded rng, written to disk.
    config = DatasetConfig()
    rng = np.random.default_rng(config.seed)
    catalog = generate_catalog(config, rng)
    inter = generate_interactions(catalog, config, rng)
    write_catalog(catalog, tmp_path)
    write_interactions(inter, tmp_path)

    # 1) The catalog loads via the shipped bookrec loader from the written CSV bytes.
    loaded = load_catalog(tmp_path / "catalog.csv.gz")
    assert len(loaded) == catalog.n_books
    assert set(loaded) == {int(i) for i in catalog.item_ids}

    # 2) Re-parse the interactions CSV and re-assert invariants on the ON-DISK data.
    reader_ids, item_ids, timestamps, splits = _read_interactions(tmp_path / "interactions.csv.gz")
    assert set(np.unique(splits)) == {"train", "val", "test"}

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

    # Cold partitions disjoint from train (cold ids from the generator, train rows from disk).
    train = splits == "train"
    assert set(item_ids[train].tolist()).isdisjoint(set(inter.cold_items.tolist()))
    assert set(reader_ids[train].tolist()).isdisjoint(set(inter.cold_readers.tolist()))
