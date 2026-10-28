"""The committed sensor logs for system identification (Unit 8; plan roar-008, design 013 §5).

``roar/data/generate.py`` records two logs of the carla-like car in the sensor-log format
(``racekit.telemetry.read_log_csv``): what the driver observed and commanded each step, never the
car's state. They live in ``roar/data/generated/sysid/`` (``RACEKIT_SYSID_DIR`` overrides it, as
``RACEKIT_TRACKS_DIR`` does for the tracks)::

    from racekit.sysid_data import LOGS, load_log
    log, meta = load_log("monza-like-seed0.csv")

* ``monza-like-seed0.csv`` (``kind=race``): a full race on ``monza-like``, for the longitudinal map;
* ``oval-steady-seed0.csv`` (``kind=steady``): one lap of ``oval`` at a steady 15 m/s, for the
  steering gain.

numpy only (through ``read_log_csv``); Python 3.8-compatible.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np

from .telemetry import read_log_csv

LOGS = ("monza-like-seed0.csv", "oval-steady-seed0.csv")
# roar/projects/racekit/racekit/sysid_data.py -> roar/data/generated/sysid
_DEFAULT_DIR = Path(__file__).resolve().parents[3] / "data" / "generated" / "sysid"


def sysid_dir() -> Path:
    """Where the generated logs live (``RACEKIT_SYSID_DIR`` overrides the in-repo default)."""
    override = os.environ.get("RACEKIT_SYSID_DIR")
    return Path(override) if override else _DEFAULT_DIR


def log_path(name: str) -> Path:
    """The path of one committed log, by its name in ``LOGS``."""
    if name not in LOGS:
        raise ValueError(f"unknown sensor log {name!r}; the logs are {', '.join(LOGS)}")
    return sysid_dir() / name


def load_log(name: str) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Read one committed log: ``(log, meta)`` exactly as ``read_log_csv`` returns them."""
    path = log_path(name)
    if not path.is_file():
        raise FileNotFoundError(
            f"no sensor log at {path}; run `PYTHONHASHSEED=0 uv run --group roar python roar/data/generate.py`"
        )
    return read_log_csv(path)
