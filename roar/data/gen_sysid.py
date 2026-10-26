"""Step 2 of the generator: the carla-like car's sensor logs for system identification (plan
roar-004; design 013 §4.3, §6 Unit 8).

A pure-pursuit driver (``drivers.py``) races ``racekit.cars.carla_like(noise=True)`` and records its
own sensor observations and commanded actions every step, as a CARLA recorder would; the log is
written with ``racekit.telemetry.write_log_csv``. Nothing in a log is read from the car's state
directly.

* ``sysid/monza-like-seed0.csv``, ``kind=race``: a full 3-lap race on ``monza-like`` at global
  a_lat 3.5 m/s², a 45 m/s cap and look-ahead braking over 300 m at 6 m/s² (the longitudinal fit
  and the actuator lag);
* ``sysid/oval-steady-seed0.csv``, ``kind=steady``: one lap of ``oval`` at a steady 15 m/s
  (the steering-gain fit, which needs steady steering).

roar-008 may add logs (designed excitation for per-section μ); the checksums are byte-stability
checks, not a frozen contract.
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import numpy as np

SEED = 0
MAX_SECONDS = 1200.0


class LogSpec(NamedTuple):
    name: str  # the output path under generated/
    track: str
    kind: str
    laps: int
    driver: dict


LOGS = (
    LogSpec("sysid/monza-like-seed0.csv", "monza-like", "race", 3,
            {"target_speed": 45.0, "a_lat": 3.5, "a_dec": 6.0, "ahead": 150}),
    LogSpec("sysid/oval-steady-seed0.csv", "oval", "steady", 1, {"target_speed": 15.0}),
)


def record(spec: LogSpec, tracks_dir: Path, seed: int = SEED) -> tuple[np.ndarray, dict]:
    """Race ``spec`` on the carla-like car with noise and return ``(log array, meta)``."""
    from drivers import pure_pursuit
    from racekit import _truth
    from racekit.cars import carla_like
    from racekit.runner import run_race
    from racekit.telemetry import log_array

    driver = pure_pursuit(record=True, **spec.driver)
    result = run_race(driver, tracks_dir / f"{spec.track}.npz", car=carla_like(noise=True),
                      laps=spec.laps, max_seconds=MAX_SECONDS, seed=seed)
    if not (result.finished and result.collisions == 0):
        raise SystemExit(f"FAIL: sysid: {spec.name}: the driver must finish cleanly ({result!r})")
    meta = {"track": spec.track, "seed": seed, "noise": _truth.NOISE_SIGMA, "kind": spec.kind}
    return log_array(driver.last.rows), meta
