"""Step 2 of the generator: the carla-like sensor logs (plan roar-004 G4.7).

Byte stability across two generations and the ≤ 1 min budget are checked by
``test_gen_tracks.test_driver_generates_twice_identically_within_budget``; this module checks what
the logs contain and that they round-trip through the reader and writer.
"""

from __future__ import annotations

import gen_sysid
import generate
import numpy as np
import pytest
from racekit.runner import CONTROL_DT, RESPAWN_HOLD_TICKS
from racekit.telemetry import LOG_COLUMNS, read_log_csv, write_log_csv

LOGS = {spec.name: spec for spec in gen_sysid.LOGS}


@pytest.fixture(scope="module", params=sorted(LOGS))
def generated_log(request):
    path = generate.GENERATED / request.param
    if not path.is_file():
        pytest.fail(f"{path} is missing; run `PYTHONHASHSEED=0 uv run --group roar python roar/data/generate.py`")
    return LOGS[request.param], path


def test_the_two_logs_are_declared():
    assert sorted(LOGS) == ["sysid/monza-like-seed0.csv", "sysid/oval-steady-seed0.csv"]
    race, steady = LOGS["sysid/monza-like-seed0.csv"], LOGS["sysid/oval-steady-seed0.csv"]
    assert (race.track, race.kind, race.laps) == ("monza-like", "race", 3)
    assert race.driver == {"target_speed": 45.0, "a_lat": 3.5, "a_dec": 6.0, "ahead": 150}
    assert (steady.track, steady.kind, steady.laps, steady.driver) == ("oval", "steady", 1, {"target_speed": 15.0})


def test_a_generated_log_has_its_meta_columns_and_clock(generated_log):
    spec, path = generated_log
    log, meta = read_log_csv(path)
    assert meta == {"track": spec.track, "seed": 0, "noise": 0.1, "kind": spec.kind}
    assert log.dtype.names == LOG_COLUMNS
    assert log.size > 1000
    steps = np.diff(log["t"])
    # one row per agent step: the clock advances one control tick, or a tick plus the respawn hold
    assert np.allclose(steps[np.abs(steps - CONTROL_DT) > 1e-9], (1 + RESPAWN_HOLD_TICKS) * CONTROL_DT)
    assert log["t"][0] == 0.0
    for name in ("throttle", "brake"):
        assert log[name].min() >= 0.0 and log[name].max() <= 1.0
    assert np.abs(log["steer"]).max() <= 1.0


def test_a_generated_log_round_trips_byte_for_byte(generated_log, tmp_path):
    _, path = generated_log
    log, meta = read_log_csv(path)
    again = write_log_csv(log, tmp_path / "again.csv", meta)
    assert again.read_bytes() == path.read_bytes()
    assert generate.rehash_log(path) == generate.rehash_log(again)


def test_the_log_records_sensor_readings_and_commanded_actions():
    """Re-race the steady log: row k + 1's position and velocity are the sensors' (float32) readings
    of the runner's state after tick k, and row k's action is what the runner was given."""
    from drivers import pure_pursuit
    from racekit.cars import carla_like
    from racekit.runner import run_race
    from racekit.tracks import tracks_dir

    spec = LOGS["sysid/oval-steady-seed0.csv"]
    log, _ = gen_sysid.record(spec, tracks_dir())
    driver = pure_pursuit(record=True, **spec.driver)
    result = run_race(driver, "oval", car=carla_like(noise=True), laps=spec.laps, seed=0)
    telemetry = result.telemetry
    assert result.finished and result.collisions == 0
    assert np.array_equal(gen_sysid.record(spec, tracks_dir())[0], log)
    n = log.size - 1
    assert n == telemetry.size - 1  # the race ends before the finishing tick's step
    for name in ("x", "y"):
        assert np.array_equal(log[name][1:], telemetry[name][:n].astype(np.float32).astype(np.float64)), name
    yaw_error = (log["yaw"][1:] - telemetry["yaw"][:n] + np.pi) % (2 * np.pi) - np.pi
    assert np.abs(yaw_error).max() <= 1e-6  # the sensor's float32 reading, wrapped to [-π, π)
    for name in ("throttle", "steer", "brake"):
        assert np.array_equal(log[name], telemetry[name]), name
    speed = np.hypot(log["vx"][1:], log["vy"][1:])
    assert np.allclose(speed, np.abs(telemetry["v"][:n]), atol=1e-4)
