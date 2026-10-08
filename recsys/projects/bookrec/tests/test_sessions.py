"""Tests for the U12 session-log loaders ``bookrec.load_series`` / ``bookrec.load_train_sequences``
(plan recsys-014 Phase D): the ordering key, the train-positive filter, the error contracts, and a
round-trip of the CI-generated ``series.csv.gz`` / ``sessions.csv.gz`` that cross-checks the loader
against the data suite's recoverability-harness loader (the same Goal-3 ordering key).
"""

from __future__ import annotations

import gzip
import sys
from pathlib import Path

import pytest
from bookrec import generated_dir, load_series, load_train_sequences

_DATA_DIR = str(Path(__file__).resolve().parents[3] / "data")
if _DATA_DIR not in sys.path:
    sys.path.insert(0, _DATA_DIR)

from _common import DatasetConfig
from _reference_recommenders import ordered_train_sequences

SESSION_HEADER = "reader_id,item_id,session_id,timestamp,split,label\n"


def _write(path: Path, text: str) -> Path:
    if path.suffix == ".gz":
        with gzip.open(path, mode="wt", encoding="utf-8", newline="") as handle:
            handle.write(text)
    else:
        path.write_text(text, encoding="utf-8")
    return path


# ------------------------------------------------------------------------------------ load_series
def test_load_series_maps_item_to_series_and_volume(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "series.csv.gz",
        "item_id,series_id,volume\n7,0,1\n3,0,2\n9,1,1\n4,1,2\n5,1,3\n",
    )
    assert load_series(path) == {7: (0, 1), 3: (0, 2), 9: (1, 1), 4: (1, 2), 5: (1, 3)}


def test_load_series_missing_column_raises(tmp_path: Path) -> None:
    path = _write(tmp_path / "series.csv", "item_id,series_id\n1,0\n")
    with pytest.raises(ValueError, match="missing required column"):
        load_series(path)


def test_load_series_duplicate_item_raises(tmp_path: Path) -> None:
    path = _write(tmp_path / "series.csv", "item_id,series_id,volume\n1,0,1\n1,2,1\n")
    with pytest.raises(ValueError, match="duplicate item_id"):
        load_series(path)


def test_load_series_non_integer_raises(tmp_path: Path) -> None:
    path = _write(tmp_path / "series.csv", "item_id,series_id,volume\n1,0,one\n")
    with pytest.raises(ValueError, match="non-integer volume"):
        load_series(path)


# --------------------------------------------------------------------------- load_train_sequences
def test_train_sequences_are_ordered_by_timestamp_then_file_row(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "sessions.csv",
        SESSION_HEADER
        + "2,50,0,10,train,1\n"
        + "1,30,1,20,train,1\n"  # reader 1: later timestamp, listed first
        + "1,10,0,5,train,1\n"
        + "1,11,0,5,train,0\n"  # a negative: never in the history
        + "1,12,0,7,train,1\n"  # same-timestamp tie with the next row: file order wins
        + "1,13,0,7,train,1\n"
        + "1,40,2,30,val,1\n"  # val / test positives are never history
        + "1,41,3,40,test,1\n"
        + "3,60,2,30,val,1\n",  # a reader with no train positive has no key
    )
    sequences = load_train_sequences(path)
    assert sequences == {1: [10, 12, 13, 30], 2: [50]}
    assert list(sequences) == [1, 2]


def test_train_sequences_missing_column_raises(tmp_path: Path) -> None:
    path = _write(tmp_path / "sessions.csv", "reader_id,item_id,split,label\n0,1,train,1\n")
    with pytest.raises(ValueError, match="missing required column"):
        load_train_sequences(path)


def test_train_sequences_non_integer_raises(tmp_path: Path) -> None:
    path = _write(tmp_path / "sessions.csv", SESSION_HEADER + "0,1,0,soon,train,1\n")
    with pytest.raises(ValueError, match="non-integer timestamp"):
        load_train_sequences(path)


# -------------------------------------------------------------------- CI-generated round-trip
def test_generated_session_log_round_trips() -> None:
    config = DatasetConfig()
    data = generated_dir()
    sequences = load_train_sequences(data / "sessions.csv.gz")
    # Same Goal-3 ordering key as the data suite's recoverability harness.
    assert sequences == ordered_train_sequences(data / "sessions.csv.gz")
    assert 0 < len(sequences) <= config.session_n_readers
    assert all(0 <= item < config.n_books for seq in sequences.values() for item in seq)

    series = load_series(data / "series.csv.gz")
    assert series
    volumes: dict[int, list[int]] = {}
    for series_id, volume in series.values():
        volumes.setdefault(series_id, []).append(volume)
    for vols in volumes.values():
        assert sorted(vols) == list(range(1, len(vols) + 1))
        assert config.series_len_min <= len(vols) <= config.series_len_max
