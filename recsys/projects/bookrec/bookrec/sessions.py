"""Load the U12 session-log observables: ``series.csv.gz`` and ordered train histories.

Unit 12 (sequence-aware retrieval) is scored on the separate session log ``sessions.csv.gz`` (the
same six-column schema as ``interactions.csv.gz``) with the unchanged
:func:`~bookrec.scoreboard.run_validation_scoreboard`. That scoreboard collapses each reader's train
history into a *set*; a sequence path needs the *order*, which :func:`load_train_sequences` supplies.

Dependency-light (stdlib ``csv`` + ``gzip``), so ``import bookrec`` stays torch/faiss-free.
"""

from __future__ import annotations

import csv
import gzip
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

SERIES_COLUMNS = ("item_id", "series_id", "volume")
SESSION_COLUMNS = ("reader_id", "item_id", "timestamp", "split", "label")


def _open_text(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, mode="rt", encoding="utf-8", newline="")
    return open(path, encoding="utf-8", newline="")


def _int_field(row: dict[str, str], column: str, name: str, line_no: int) -> int:
    raw = (row.get(column) or "").strip()
    try:
        return int(raw)
    except ValueError as error:
        raise ValueError(f"{name} line {line_no}: non-integer {column} {raw!r}") from error


def _check_header(reader: csv.DictReader, required: tuple[str, ...], name: str) -> None:
    header = reader.fieldnames or []
    missing = [column for column in required if column not in header]
    if missing:
        raise ValueError(f"{name} missing required column(s): {missing}")


def load_series(path: str | Path) -> dict[int, tuple[int, int]]:
    """Load a (optionally gzip'd) series CSV into ``{item_id: (series_id, volume)}``.

    Books outside every series have no row (and no key). Requires the ``item_id``, ``series_id``
    and ``volume`` columns; raises on a missing column, a non-integer field, or a book listed twice.
    """
    path = Path(path)
    name = f"series {path.name}"
    series: dict[int, tuple[int, int]] = {}
    with _open_text(path) as handle:
        reader = csv.DictReader(handle)
        _check_header(reader, SERIES_COLUMNS, name)
        for line_no, row in enumerate(reader, start=2):
            item_id = _int_field(row, "item_id", name, line_no)
            if item_id in series:
                raise ValueError(f"{name} line {line_no}: duplicate item_id {item_id}")
            series[item_id] = (
                _int_field(row, "series_id", name, line_no),
                _int_field(row, "volume", name, line_no),
            )
    return series


def ordered_train_histories(rows: Iterable[Mapping[str, Any]]) -> dict[int, list[int]]:
    """Each reader's **ordered** train-positive item list from an iterable of row mappings.

    The ONE ordering implementation shared by :func:`load_train_sequences` and every Unit-12
    sequence path's ``fit``. Rows carry ``reader_id, item_id, timestamp, split, label`` (the U4 keys
    plus ``timestamp``); only ``split == "train"`` **and** ``label == 1`` rows are kept (val/test
    rows and sampled negatives never enter a history). Per reader, items are ordered by
    ``(timestamp, row order)`` — ties at the same timestamp keep the input order. Readers are
    returned in ascending id order; a reader with no train positive has no key. Raises
    :class:`ValueError` when a train-positive row has no ``timestamp`` (an order needs one).
    """
    events: dict[int, list[tuple[int, int, int]]] = {}
    for position, row in enumerate(rows):
        if row["split"] != "train" or int(row["label"]) != 1:
            continue
        if "timestamp" not in row or row["timestamp"] in (None, ""):
            raise ValueError(
                "ordered_train_histories: a train-positive row has no 'timestamp' — sequence "
                "paths need rows with reader_id, item_id, timestamp, split, label"
            )
        events.setdefault(int(row["reader_id"]), []).append(
            (int(row["timestamp"]), position, int(row["item_id"]))
        )
    return {
        reader_id: [item for _, _, item in sorted(events[reader_id])]
        for reader_id in sorted(events)
    }


def _read_session_rows(path: Path) -> list[dict[str, int | str]]:
    """Parse a session-log CSV into typed row mappings (header- and integer-checked)."""
    name = f"sessions {path.name}"
    rows: list[dict[str, int | str]] = []
    with _open_text(path) as handle:
        reader = csv.DictReader(handle)
        _check_header(reader, SESSION_COLUMNS, name)
        for line_no, row in enumerate(reader, start=2):
            rows.append(
                {
                    "reader_id": _int_field(row, "reader_id", name, line_no),
                    "item_id": _int_field(row, "item_id", name, line_no),
                    "timestamp": _int_field(row, "timestamp", name, line_no),
                    "split": row.get("split") or "",
                    "label": _int_field(row, "label", name, line_no),
                }
            )
    return rows


def load_train_sequences(path: str | Path) -> dict[int, list[int]]:
    """Each reader's **ordered** train-positive item list from a session-log CSV.

    Only ``label == 1`` rows of the ``train`` split are kept (val/test are never read into the
    history). Per reader, items are ordered by ``(timestamp, file row order)`` — ties at the same
    timestamp keep the file's order. Readers are returned in ascending id order; a reader with no
    train positive has no key. The ordering is :func:`ordered_train_histories` (one implementation).
    """
    path = Path(path)
    name = f"sessions {path.name}"
    rows: list[dict[str, int | str]] = []
    with _open_text(path) as handle:
        reader = csv.DictReader(handle)
        _check_header(reader, SESSION_COLUMNS, name)
        for line_no, row in enumerate(reader, start=2):
            if row.get("split") != "train" or _int_field(row, "label", name, line_no) != 1:
                continue
            rows.append(
                {
                    "reader_id": _int_field(row, "reader_id", name, line_no),
                    "item_id": _int_field(row, "item_id", name, line_no),
                    "timestamp": _int_field(row, "timestamp", name, line_no),
                    "split": "train",
                    "label": 1,
                }
            )
    return ordered_train_histories(rows)


def first_unseen_val(path: str | Path) -> dict[int, int]:
    """Each reader's time-ordered **first** val positive that is not a train positive.

    The next-item target for next-item hit@k: per reader, the val ``label == 1`` rows ordered by
    ``(timestamp, file row order)``; the first whose item is not among that reader's train
    positives. A reader whose val positives are all re-reads (or who has none) has no key.
    """
    rows = _read_session_rows(Path(path))
    train_items: dict[int, set[int]] = {}
    for reader_id, items in ordered_train_histories(rows).items():
        train_items[reader_id] = set(items)
    val_events: dict[int, list[tuple[int, int, int]]] = {}
    for position, row in enumerate(rows):
        if row["split"] != "val" or int(row["label"]) != 1:
            continue
        val_events.setdefault(int(row["reader_id"]), []).append(
            (int(row["timestamp"]), position, int(row["item_id"]))
        )
    first: dict[int, int] = {}
    for reader_id in sorted(val_events):
        seen = train_items.get(reader_id, set())
        for _, _, item in sorted(val_events[reader_id]):
            if item not in seen:
                first[reader_id] = item
                break
    return first
