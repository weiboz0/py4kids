"""Telemetry CSV export and import with a fixed column schema (design 013 §4.2, §7.2).

The same format carries the real-simulator lab sample later, so a student's CARLA log and a
racekit log are analysed by the same code.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Union

import numpy as np

from .runner import TELEMETRY_DTYPE

COLUMNS = TELEMETRY_DTYPE.names  # ("t", "x", "y", "yaw", "v", "throttle", "steer", "brake", "progress", "offset")
FLOAT_FORMAT = "{:.6f}"


def write_csv(telemetry: np.ndarray, path: Union[str, Path]) -> Path:
    """Write telemetry rows to ``path`` with the fixed header and six-decimal floats."""
    path = Path(path)
    if telemetry.dtype.names != COLUMNS:
        raise ValueError(f"telemetry columns must be {COLUMNS}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(COLUMNS)
        for row in telemetry:
            writer.writerow([
                str(int(row[name])) if name == "progress" else FLOAT_FORMAT.format(float(row[name]))
                for name in COLUMNS
            ])
    return path


def read_csv(path: Union[str, Path]) -> np.ndarray:
    """Read a telemetry CSV; the header must be exactly the schema's columns, in order."""
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        if header is None or tuple(header) != COLUMNS:
            raise ValueError(f"telemetry CSV header must be {','.join(COLUMNS)}")
        rows = []
        for number, record in enumerate(reader, start=2):
            if len(record) != len(COLUMNS):
                raise ValueError(f"line {number}: expected {len(COLUMNS)} fields, got {len(record)}")
            rows.append(tuple(int(value) if name == "progress" else float(value)
                              for name, value in zip(COLUMNS, record)))
    return np.array(rows, dtype=TELEMETRY_DTYPE) if rows else np.zeros(0, TELEMETRY_DTYPE)
