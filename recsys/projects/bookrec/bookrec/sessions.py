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
from pathlib import Path

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


def load_train_sequences(path: str | Path) -> dict[int, list[int]]:
    """Each reader's **ordered** train-positive item list from a session-log CSV.

    Only ``label == 1`` rows of the ``train`` split are kept (val/test are never read into the
    history). Per reader, items are ordered by ``(timestamp, file row order)`` — ties at the same
    timestamp keep the file's order. Readers are returned in ascending id order; a reader with no
    train positive has no key.
    """
    path = Path(path)
    name = f"sessions {path.name}"
    events: dict[int, list[tuple[int, int, int]]] = {}
    with _open_text(path) as handle:
        reader = csv.DictReader(handle)
        _check_header(reader, SESSION_COLUMNS, name)
        for line_no, row in enumerate(reader, start=2):
            if row.get("split") != "train" or _int_field(row, "label", name, line_no) != 1:
                continue
            reader_id = _int_field(row, "reader_id", name, line_no)
            timestamp = _int_field(row, "timestamp", name, line_no)
            item_id = _int_field(row, "item_id", name, line_no)
            events.setdefault(reader_id, []).append((timestamp, line_no, item_id))
    return {
        reader_id: [item for _, _, item in sorted(events[reader_id])]
        for reader_id in sorted(events)
    }
