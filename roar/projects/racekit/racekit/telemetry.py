"""Telemetry: sector splits, the recorder's cumulative progress, and the v1 CSV format (design 013
§4.2, §7.2; plan roar-002).

The same format carries the real-simulator lab recording, so a student's CARLA log and a racekit
log are analysed by the same code.

The columns (``COLUMNS``), one row per control tick:

* ``t``: simulated seconds; ``x``, ``y``, ``yaw``, ``v``: the car's state after the tick;
* ``throttle``, ``steer``, ``brake``: the action the agent applied (before any actuator jitter);
* ``progress``: the furthest waypoint reached, **cumulative over the race** (0 … ``progress_total``),
  reset to 0 by a respawn. On ``held`` rows it keeps the **pre-reset** progress: the runner resets
  it when the 1.0 s hold ends, as the official runner does;
* ``offset``: the signed distance from the centreline (left positive);
* ``held``: 1 on the respawn-hold ticks (the agent is not called), else 0.

``offset`` may be all zero in a real-simulator recording. The Unit 1 lab recorder writes the hold
itself: ``RESPAWN_HOLD_TICKS`` rows with ``held`` 1 at the runner's hold times, with progress 0
(``sector_splits`` never reads progress on a held row), then the first row after the hold at the
same time as the last held row. On CARLA the held rows and that first row carry the **crash pose**
(the runner does not read the sensors again after the respawn); racekit's held rows are at the start
pose. Analyses that care about position or speed should skip ``held`` rows.

The v1 CSV starts with one comment line carrying the integer meta, then the column header, then
the rows::

    # racekit-telemetry v1 progress_total=1407 laps=3 per_lap=3 waypoints_per_lap=469
    t,x,y,yaw,v,throttle,steer,brake,progress,offset,held
    0.050000,...

**The sensor log** (plan roar-004; ``write_log_csv`` / ``read_log_csv``) is a separate, smaller
format: what a driver can record about itself every step, as a CARLA recorder would, for system
identification (Unit 8). The columns (``LOG_COLUMNS``), one row per agent step:

* ``t``: the observation time in simulated seconds (the steps' clock, including any 1.0 s respawn
  hold, so a gap larger than one control tick marks a respawn);
* ``x``, ``y`` (location sensor), ``yaw`` (roll-pitch-yaw sensor), ``vx``, ``vy`` (velocimeter,
  **world frame**): the sensor readings the step saw, before its action;
* ``throttle``, ``steer``, ``brake``: the action the step commanded (before any actuator jitter or
  lag).

It follows the v1 CSV conventions (one comment line of meta, the header, six-decimal floats) with
its own meta: the ``track`` name, the race ``seed``, the actuator ``noise`` σ and the log ``kind``::

    # racekit-log v1 track=monza-like seed=0 noise=0.1 kind=race
    t,x,y,yaw,vx,vy,throttle,steer,brake
    0.000000,...
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any, Dict, Tuple, Union

import numpy as np

from .runner import CONTROL_DT, FINISH_MARGIN, SECTORS_PER_LAP, TELEMETRY_DTYPE

COLUMNS = TELEMETRY_DTYPE.names  # t, x, y, yaw, v, throttle, steer, brake, progress, offset, held
INT_COLUMNS = ("progress", "held")
FLOAT_FORMAT = "{:.6f}"
META_KEYS = ("progress_total", "laps", "per_lap", "waypoints_per_lap")
CSV_MAGIC = "# racekit-telemetry v1"
_META_LINE = re.compile(
    r"# racekit-telemetry v1 progress_total=(\S+) laps=(\S+) per_lap=(\S+) waypoints_per_lap=(\S+)"
)


# --- sector splits -------------------------------------------------------------------------------


def sector_splits(
    telemetry: np.ndarray, progress_total: int, laps: int = 3, per_lap: int = 3, finished: bool = False,
) -> np.ndarray:
    """Sector times, shape ``(laps, per_lap)``, from the ``t`` and ``progress`` columns.

    The race's ``progress_total`` waypoints are cut into ``laps × per_lap`` equal sectors; the last
    boundary is the finish line (5 waypoints short of the end). A sector's time runs from the first
    row at or past its start boundary to the first row at or past its end boundary. A sector never
    reached is NaN.

    A respawn restarts the sectors, as the runner does: on ``held`` rows (when the column exists)
    the clock origin moves to that row and the crossings are cleared; without a held row, a drop of
    cumulative progress to below 0.1·n (``n = progress_total / laps``) is a respawn at that row.

    A recorder in the agent never sees the finishing tick (the race ends before the next step), so
    a recording of a finished race has an open last sector: ``finished=True`` closes it one control
    tick after the last row. Never pass it for a race that did not finish.
    """
    if laps < 1 or per_lap < 1 or progress_total < laps:
        raise ValueError("need laps >= 1, per_lap >= 1 and progress_total >= laps")
    count = laps * per_lap
    boundaries = [min(progress_total - FINISH_MARGIN, round(k * progress_total / count)) for k in range(1, count + 1)]
    respawn_below = CumulativeProgress.WRAP_LOW * progress_total / laps
    times = np.asarray(telemetry["t"], dtype=np.float64)
    progress = np.asarray(telemetry["progress"])
    names = telemetry.dtype.names or ()
    held = np.asarray(telemetry["held"]) if "held" in names else np.zeros(times.size, dtype=np.int64)
    origin = 0.0
    crossings = []
    previous = None  # the previous row's progress; None after a held row
    for t, reached, is_held in zip(times.tolist(), progress.tolist(), held.tolist()):
        if is_held:
            origin, crossings, previous = t, [], None
            continue
        if previous is not None and reached < previous and reached < respawn_below:
            origin, crossings = t, []
        previous = reached
        while len(crossings) < count and reached >= boundaries[len(crossings)]:
            crossings.append(t)
    if finished and len(crossings) == count - 1 and times.size:
        crossings.append(float(times[-1]) + CONTROL_DT)
    splits = np.full(count, np.nan)
    start = origin
    for k, crossed in enumerate(crossings):
        splits[k] = crossed - start
        start = crossed
    return splits.reshape(laps, per_lap)


# --- the recorder's cumulative progress ----------------------------------------------------------


class CumulativeProgress:
    """Turn an agent's one-lap waypoint index into cumulative race progress, for a recorder.

    Plain Python with no imports, Python 3.8-safe, so it can be pasted into a submission.
    ``update(lap_index, collision_impulse)`` takes the agent's own index into its one-lap waypoint
    list and the collision sensor's ``impulse_normal`` reading, and returns ``offset + lap_index``:

    * a **respawn** is the explicit collision signal ``|impulse_normal| > 100`` (the official
      runner's major-collision threshold, seen on the first step after the hold): the offset
      resets to 0, wherever the car is, and ``respawned`` is True for that row;
    * otherwise a **lap wrap** (the index going from >= 0.9·n to < 0.1·n) adds n to the offset.
    """

    RESPAWN_IMPULSE = 100.0  # N·s: the official runner's major-collision threshold
    WRAP_HIGH = 0.9
    WRAP_LOW = 0.1

    def __init__(self, n: int) -> None:
        if n < 1:
            raise ValueError("n (waypoints per lap) must be at least 1")
        self.n = n
        self.offset = 0
        self.last_index = None
        self.respawned = False

    def update(self, lap_index: int, collision_impulse) -> int:
        impulse = sum(float(c) * float(c) for c in collision_impulse) ** 0.5
        self.respawned = impulse > self.RESPAWN_IMPULSE
        if self.respawned:
            self.offset = 0
        elif (self.last_index is not None and self.last_index >= self.WRAP_HIGH * self.n
              and lap_index < self.WRAP_LOW * self.n):
            self.offset += self.n
        self.last_index = lap_index
        return self.offset + lap_index


# --- the v1 CSV ----------------------------------------------------------------------------------


def _is_int(value: Any) -> bool:
    return isinstance(value, (int, np.integer)) and not isinstance(value, (bool, np.bool_))


def _checked_meta(meta: Dict[str, Any]) -> Dict[str, int]:
    if not isinstance(meta, dict) or set(meta) != set(META_KEYS):
        raise ValueError(f"telemetry meta keys must be exactly {', '.join(META_KEYS)}")
    for key in META_KEYS:
        if not _is_int(meta[key]) or meta[key] < 1:
            raise ValueError(f"telemetry meta {key} must be a positive int, got {meta[key]!r}")
    checked = {key: int(meta[key]) for key in META_KEYS}
    if checked["progress_total"] != checked["laps"] * checked["waypoints_per_lap"]:
        raise ValueError("telemetry meta progress_total must equal laps × waypoints_per_lap")
    return checked


def race_meta(result: Any) -> Dict[str, int]:
    """The v1 CSV meta for a ``RaceResult``."""
    return {
        "progress_total": int(result.progress_total), "laps": int(result.laps), "per_lap": SECTORS_PER_LAP,
        "waypoints_per_lap": int(result.progress_total) // int(result.laps),
    }


def write_csv(telemetry: np.ndarray, path: Union[str, Path], meta: Dict[str, int]) -> Path:
    """Write the v1 CSV: the meta line, the fixed header, then the rows with six-decimal floats."""
    path = Path(path)
    if telemetry.dtype.names != COLUMNS:
        raise ValueError(f"telemetry columns must be {COLUMNS}")
    checked = _checked_meta(meta)
    with path.open("w", newline="", encoding="utf-8") as handle:
        handle.write(CSV_MAGIC + "".join(f" {key}={checked[key]}" for key in META_KEYS) + "\n")
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(COLUMNS)
        for row in telemetry:
            writer.writerow([
                str(int(row[name])) if name in INT_COLUMNS else FLOAT_FORMAT.format(float(row[name]))
                for name in COLUMNS
            ])
    return path


def read_csv(path: Union[str, Path]) -> Tuple[np.ndarray, Dict[str, int]]:
    """Read a v1 telemetry CSV: ``(telemetry, meta)``. The meta line, its integer values and the
    column header are validated."""
    with Path(path).open(newline="", encoding="utf-8") as handle:
        first = handle.readline().rstrip("\r\n")
        match = _META_LINE.fullmatch(first)
        if match is None:
            raise ValueError(
                f"telemetry CSV line 1 must be '{CSV_MAGIC} progress_total=<int> laps=<int> per_lap=<int> "
                "waypoints_per_lap=<int>'"
            )
        values = {}
        for key, text in zip(META_KEYS, match.groups()):
            if not re.fullmatch(r"[0-9]+", text):
                raise ValueError(f"telemetry CSV meta {key} must be an int, got {text!r}")
            values[key] = int(text)
        meta = _checked_meta(values)
        reader = csv.reader(handle)
        header = next(reader, None)
        if header is None or tuple(header) != COLUMNS:
            raise ValueError(f"telemetry CSV header must be {','.join(COLUMNS)}")
        rows = []
        for number, record in enumerate(reader, start=3):
            if len(record) != len(COLUMNS):
                raise ValueError(f"line {number}: expected {len(COLUMNS)} fields, got {len(record)}")
            rows.append(tuple(int(value) if name in INT_COLUMNS else float(value)
                              for name, value in zip(COLUMNS, record)))
    telemetry = np.array(rows, dtype=TELEMETRY_DTYPE) if rows else np.zeros(0, TELEMETRY_DTYPE)
    return telemetry, meta


# --- the sensor log (plan roar-004) --------------------------------------------------------------

LOG_COLUMNS = ("t", "x", "y", "yaw", "vx", "vy", "throttle", "steer", "brake")
LOG_DTYPE = np.dtype([(name, "f8") for name in LOG_COLUMNS])
LOG_META_KEYS = ("track", "seed", "noise", "kind")
LOG_MAGIC = "# racekit-log v1"
_LOG_META_LINE = re.compile(r"# racekit-log v1 track=(\S+) seed=(\S+) noise=(\S+) kind=(\S+)")
_TOKEN = re.compile(r"[A-Za-z0-9_.-]+")


def _checked_log_meta(meta: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(meta, dict) or set(meta) != set(LOG_META_KEYS):
        raise ValueError(f"log meta keys must be exactly {', '.join(LOG_META_KEYS)}")
    for key in ("track", "kind"):
        if not isinstance(meta[key], str) or not _TOKEN.fullmatch(meta[key]):
            raise ValueError(f"log meta {key} must be a name of letters, digits, '_', '.' or '-'")
    if not _is_int(meta["seed"]) or meta["seed"] < 0:
        raise ValueError(f"log meta seed must be an int >= 0, got {meta['seed']!r}")
    noise = meta["noise"]
    if isinstance(noise, bool) or not isinstance(noise, (int, float)) or not 0.0 <= float(noise) < float("inf"):
        raise ValueError(f"log meta noise must be a finite number >= 0, got {noise!r}")
    return {"track": meta["track"], "seed": int(meta["seed"]), "noise": float(noise), "kind": meta["kind"]}


def log_array(rows: Any) -> np.ndarray:
    """Rows (a sequence of 9-tuples in ``LOG_COLUMNS`` order, or a structured array) as a
    ``LOG_DTYPE`` array."""
    if isinstance(rows, np.ndarray) and rows.dtype.names is not None:
        if rows.dtype.names != LOG_COLUMNS:
            raise ValueError(f"log columns must be {LOG_COLUMNS}")
        return rows.astype(LOG_DTYPE)
    rows = [tuple(float(value) for value in row) for row in rows]
    if any(len(row) != len(LOG_COLUMNS) for row in rows):
        raise ValueError(f"every log row needs {len(LOG_COLUMNS)} values")
    return np.array(rows, dtype=LOG_DTYPE) if rows else np.zeros(0, LOG_DTYPE)


def _log_number(value: float) -> str:
    text = FLOAT_FORMAT.format(value)
    return text[1:] if text == "-" + FLOAT_FORMAT.format(0.0) else text  # no "-0.000000"


def write_log_csv(rows: Any, path: Union[str, Path], meta: Dict[str, Any]) -> Path:
    """Write a sensor log: the meta line, the fixed header, then the rows with six-decimal floats."""
    path = Path(path)
    log = log_array(rows)
    checked = _checked_log_meta(meta)
    with path.open("w", newline="", encoding="utf-8") as handle:
        handle.write(
            f"{LOG_MAGIC} track={checked['track']} seed={checked['seed']} noise={checked['noise']!r} "
            f"kind={checked['kind']}\n"
        )
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(LOG_COLUMNS)
        for row in log.tolist():
            writer.writerow([_log_number(value) for value in row])
    return path


def read_log_csv(path: Union[str, Path]) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Read a sensor log: ``(log, meta)`` with ``log`` a ``LOG_DTYPE`` array. The meta line and
    the header are validated."""
    with Path(path).open(newline="", encoding="utf-8") as handle:
        first = handle.readline().rstrip("\r\n")
        match = _LOG_META_LINE.fullmatch(first)
        if match is None:
            raise ValueError(
                f"log CSV line 1 must be '{LOG_MAGIC} track=<name> seed=<int> noise=<float> kind=<name>'"
            )
        track, seed, noise, kind = match.groups()
        if not re.fullmatch(r"[0-9]+", seed):
            raise ValueError(f"log CSV meta seed must be an int, got {seed!r}")
        try:
            noise_value = float(noise)
        except ValueError:
            raise ValueError(f"log CSV meta noise must be a number, got {noise!r}") from None
        meta = _checked_log_meta({"track": track, "seed": int(seed), "noise": noise_value, "kind": kind})
        reader = csv.reader(handle)
        header = next(reader, None)
        if header is None or tuple(header) != LOG_COLUMNS:
            raise ValueError(f"log CSV header must be {','.join(LOG_COLUMNS)}")
        rows = []
        for number, record in enumerate(reader, start=3):
            if len(record) != len(LOG_COLUMNS):
                raise ValueError(f"line {number}: expected {len(LOG_COLUMNS)} fields, got {len(record)}")
            rows.append(tuple(float(value) for value in record))
    return log_array(rows), meta
