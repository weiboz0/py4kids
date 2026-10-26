"""Telemetry: the v1 CSV, ``sector_splits`` and the recorder's ``CumulativeProgress`` (plans roar-001
Phase D, roar-002 Phase 1: G3 and the lab-path recordings)."""

from __future__ import annotations

import math

import numpy as np
import pytest
from conftest import STARTER
from racekit.cars import KinematicCar
from racekit.runner import (
    CONTROL_DT,
    RESPAWN_HOLD_TICKS,
    SECTORS_PER_LAP,
    advance_progress,
    load_submission,
    run_race,
    shim_installed,
)
from racekit.telemetry import (
    COLUMNS,
    CumulativeProgress,
    race_meta,
    read_csv,
    sector_splits,
    write_csv,
)
from racekit.tracks import load_track

# --- the v1 CSV ----------------------------------------------------------------------------------


def test_csv_round_trip_with_the_v1_header_and_meta(tmp_path):
    result = run_race(STARTER, "oval", max_seconds=5.0)
    meta = race_meta(result)
    n = len(load_track("oval"))
    assert meta == {"progress_total": 3 * n, "laps": 3, "per_lap": 3, "waypoints_per_lap": n}
    path = write_csv(result.telemetry, tmp_path / "telemetry.csv", meta)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == f"# racekit-telemetry v1 progress_total={3 * n} laps=3 per_lap=3 waypoints_per_lap={n}"
    assert lines[1] == "t,x,y,yaw,v,throttle,steer,brake,progress,offset,held"
    assert COLUMNS == result.telemetry.dtype.names
    assert len(lines) == 2 + result.ticks
    back, back_meta = read_csv(path)
    assert back_meta == meta and all(type(value) is int for value in back_meta.values())
    assert back.dtype == result.telemetry.dtype
    for name in COLUMNS:
        assert np.allclose(back[name], result.telemetry[name], atol=1e-6)
    assert write_csv(back, tmp_path / "again.csv", back_meta).read_bytes() == path.read_bytes()


GOOD_META = "# racekit-telemetry v1 progress_total=30 laps=3 per_lap=3 waypoints_per_lap=10"
HEADER = ",".join(COLUMNS)


@pytest.mark.parametrize(("first", "second", "match"), [
    ("t,x,y", "0,1,2", "line 1 must be"),  # the v0 (headerless-meta) format
    (HEADER, "0.05," * 10 + "0", "line 1 must be"),
    ("# racekit-telemetry v2 progress_total=30 laps=3 per_lap=3 waypoints_per_lap=10", HEADER, "line 1 must be"),
    ("# racekit-telemetry v1 laps=3 progress_total=30 per_lap=3 waypoints_per_lap=10", HEADER, "line 1 must be"),
    (GOOD_META + " extra=1", HEADER, "line 1 must be"),
    (GOOD_META.replace("laps=3", "laps=3.0"), HEADER, "meta laps must be an int"),
    (GOOD_META.replace("per_lap=3", "per_lap=three"), HEADER, "meta per_lap must be an int"),
    (GOOD_META.replace("progress_total=30", "progress_total=-30"), HEADER, "progress_total must be an int"),
    (GOOD_META.replace("progress_total=30", "progress_total=31"), HEADER, "laps × waypoints_per_lap"),
    (GOOD_META, "t,x,y", "header must be"),
])
def test_malformed_headers_and_non_int_meta_are_rejected(tmp_path, first, second, match):
    bad = tmp_path / "bad.csv"
    bad.write_text(f"{first}\n{second}\n", encoding="utf-8")
    with pytest.raises(ValueError, match=match):
        read_csv(bad)


def test_bad_rows_and_bad_meta_on_write_are_rejected(tmp_path):
    short = tmp_path / "short.csv"
    short.write_text(f"{GOOD_META}\n{HEADER}\n0.05,1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="line 3"):
        read_csv(short)
    telemetry = run_race(STARTER, "oval", max_seconds=1.0).telemetry
    meta = {"progress_total": 30, "laps": 3, "per_lap": 3, "waypoints_per_lap": 10}
    with pytest.raises(ValueError, match="columns"):
        write_csv(np.zeros(3, dtype=[("t", "f8")]), tmp_path / "x.csv", meta)
    for bad in ({**meta, "laps": 3.0}, {**meta, "laps": True}, {"progress_total": 30, "laps": 3},
                {**meta, "seed": 0}, {**meta, "waypoints_per_lap": 11}):
        with pytest.raises(ValueError, match="meta"):
            write_csv(telemetry, tmp_path / "x.csv", bad)


# --- sector splits (G3) --------------------------------------------------------------------------


@pytest.mark.parametrize("track", ["oval", "monza-like"])
def test_sector_splits_from_telemetry_equal_the_result_and_a_csv_round_trip(tmp_path, track):
    """G3: computed from the t and progress columns, equal to result.sector_splits to 1e-9, summing
    to total_time, for the result and for the same race written to CSV and read back."""
    result = run_race(STARTER, track, car=KinematicCar(jitter=0.05), seed=0)
    assert result.finished and result.collisions == 0
    splits = sector_splits(result.telemetry, result.progress_total, laps=3, per_lap=3)
    assert splits.shape == (3, SECTORS_PER_LAP) and not np.isnan(splits).any()
    assert np.allclose(splits, result.sector_splits, rtol=0.0, atol=1e-9)
    assert splits.sum() == pytest.approx(result.total_time, abs=1e-9)
    telemetry, meta = read_csv(write_csv(result.telemetry, tmp_path / "run.csv", race_meta(result)))
    from_csv = sector_splits(telemetry, meta["progress_total"], meta["laps"], meta["per_lap"])
    assert np.allclose(from_csv, result.sector_splits, rtol=0.0, atol=1e-9)
    assert from_csv.sum() == pytest.approx(result.total_time, abs=1e-9)


def test_sector_splits_handle_held_rows_and_progress_drops():
    total, laps = 90, 1  # one lap of 90 waypoints, 3 sectors: boundaries 30, 60, 85
    rows = [(0.05 * (i + 1), i * 2) for i in range(20)]  # progress 0..38: sector 1 crossed at 0.80
    rows += [(1.05 + 0.05 * k, 38) for k in range(4)]  # a respawn hold, pre-reset progress
    held = [0] * 20 + [1] * 4
    rows += [(1.30 + 0.05 * i, i * 3) for i in range(31)]  # restart: 0..90
    held += [0] * 31
    telemetry = np.array([(t, p, h) for (t, p), h in zip(rows, held)],
                         dtype=[("t", "f8"), ("progress", "i8"), ("held", "i8")])
    splits = sector_splits(telemetry, total, laps=laps, per_lap=3)
    # the origin is the last held row (t = 1.20); crossings at progress 30 (t=1.80), 60 (2.30), 85 (2.75)
    assert np.allclose(splits, [[0.60, 0.50, 0.45]], atol=1e-9)
    # without the held column: the drop to below 0.1·n restarts the sectors at that row (t = 1.30)
    no_held = telemetry[["t", "progress"]]
    no_held = no_held[telemetry["held"] == 0]
    assert np.allclose(sector_splits(no_held, total, laps=laps, per_lap=3), [[0.50, 0.50, 0.45]], atol=1e-9)
    # a drop that stays above 0.1·n is not a respawn; an unreached sector is NaN
    partial = np.array([(0.05, 40), (0.10, 20), (0.15, 50)], dtype=[("t", "f8"), ("progress", "i8")])
    assert np.isnan(sector_splits(partial, total, laps=laps)[0, 1:]).all()
    assert sector_splits(partial, total, laps=laps)[0, 0] == pytest.approx(0.05)


def test_a_recorded_crash_at_progress_zero_restarts_sector_one_after_the_hold():
    """[sol] B1: the lab recorder's layout (CSV-shaped, progress 0 on its held rows). A crash before
    the first waypoint leaves progress at 0 on both sides, so only the held rows mark the respawn."""
    total, laps = 90, 1  # boundaries 30, 60, 85
    rows = [(0.05 * i, 0, 0) for i in range(10)]  # t = 0.00 .. 0.45: still at progress 0, then a crash
    rows += [(0.05 * (10 + k), 0, 1) for k in range(1, RESPAWN_HOLD_TICKS + 1)]  # hold: t = 0.55 .. 1.50
    rows += [(1.50 + 0.05 * i, 3 * i, 0) for i in range(31)]  # the restart: t = 1.50 .. 3.00, progress 0 .. 90
    csv_shaped = np.array(
        [(t, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, p, 0.0, h) for t, p, h in rows],
        dtype=[(name, "i8" if name in ("progress", "held") else "f8") for name in COLUMNS],
    )
    splits = sector_splits(csv_shaped, total, laps=laps, per_lap=3)
    # sector 1 runs from the end of the hold (t = 1.50) to progress 30 (t = 2.00), not from t = 0
    assert np.allclose(splits, [[0.50, 0.50, 0.45]], atol=1e-9)
    # without the held rows the same recording shows no respawn: the lost time leaks into sector 1
    no_held = csv_shaped[csv_shaped["held"] == 0]
    assert sector_splits(no_held, total, laps=laps, per_lap=3)[0, 0] == pytest.approx(2.00, abs=1e-9)


# --- the recorder (the lab path) -----------------------------------------------------------------


def _starter_class():
    with shim_installed():
        agent_class, _ = load_submission(STARTER)
    return agent_class


# a firm right at full throttle (not full lock: on this car full lock circles on the spot)
STEER_OFF = {"throttle": 1.0, "steer": 0.25, "brake": 0.0, "hand_brake": 0.0, "reverse": 0, "target_gear": 0}


def recording_agent(saboteur=None):
    """The starter plus a lab-style recorder: it tracks its own one-lap waypoint index with the
    runner's forward-window rule, feeds it to CumulativeProgress with the collision sensor's
    impulse, and records one row per step. ``saboteur(agent, progress, t)`` returns True to steer
    off (until the crash)."""

    class Recorder(_starter_class()):
        rows = []  # noqa: RUF012 - the last race's recorded rows
        respawned = []  # noqa: RUF012 - the t of each row the recorder flagged as a respawn

        async def initialize(self):
            await super().initialize()
            points = self.maneuverable_waypoints
            n = len(points)
            order = list(range(1, n)) + [0]  # the runner's lap order: one past the start first
            self.wx = [float(points[i].location[0]) for i in order] * 2
            self.wy = [float(points[i].location[1]) for i in order] * 2
            self.n = n
            self.lap_index = 0
            self.last = tuple(float(v) for v in self.location_sensor.get_last_gym_observation()[:2])
            self.recorder = CumulativeProgress(n)
            self.tick = 0
            self.crashed = False
            Recorder.rows = []
            Recorder.respawned = []

        async def step(self):
            impulse = self.collision_sensor.get_last_gym_observation()
            location = self.location_sensor.get_last_gym_observation()
            x, y = float(location[0]), float(location[1])
            if math.sqrt(sum(float(c) ** 2 for c in impulse)) > CumulativeProgress.RESPAWN_IMPULSE:
                self.tick += RESPAWN_HOLD_TICKS  # the hold ticks the agent was not called for
                self.lap_index, self.last, self.crashed = 0, (x, y), True
            self.lap_index = advance_progress(self.wx, self.wy, self.lap_index, self.last[0], self.last[1], x, y)
            self.lap_index %= self.n
            self.last = (x, y)
            progress = self.recorder.update(self.lap_index, impulse)
            t = self.tick * CONTROL_DT
            if self.recorder.respawned:
                Recorder.respawned.append(t)
            await super().step()
            if saboteur is not None and not self.crashed and saboteur(self, progress, t):
                await self.vehicle.apply_action(STEER_OFF)
            action = self.vehicle.last_action
            Recorder.rows.append((t, x, y, 0.0, 0.0, action["throttle"], action["steer"], action["brake"],
                                  progress, 0.0, 0))
            self.tick += 1

    return Recorder


def _recorded(agent) -> np.ndarray:
    from racekit.telemetry import TELEMETRY_DTYPE

    return np.array(agent.rows, dtype=TELEMETRY_DTYPE)


def _matches_runner_on_every_observed_non_held_row(recorded, result):
    runner = {round(float(t), 6): int(p) for t, p, h in zip(result.telemetry["t"], result.telemetry["progress"],
                                                             result.telemetry["held"]) if not h}
    seen = {round(float(t), 6): int(p) for t, p in zip(recorded["t"], recorded["progress"])}
    for t, progress in seen.items():
        if t in runner:
            assert progress == runner[t], t
    # the recorder never observes a crash tick (the car is already back at the start) nor the finish
    unseen = sorted(set(runner) - set(seen))
    expected = sorted(round(r, 6) for r in result.respawn_times)
    if result.finished:
        expected.append(round(result.total_time, 6))
    assert unseen == expected


def test_a_recorded_three_lap_csv_gives_the_result_splits_within_a_tick(tmp_path):
    agent = recording_agent()
    result = run_race(agent, "oval", car=KinematicCar(jitter=0.05), seed=1)
    assert result.finished and result.collisions == 0
    recorded = _recorded(agent)
    _matches_runner_on_every_observed_non_held_row(recorded, result)
    meta = race_meta(result)
    telemetry, meta = read_csv(write_csv(recorded, tmp_path / "lab.csv", meta))
    assert np.all(np.diff(telemetry["progress"]) >= 0)
    # a recorder never sees the finishing tick: the last sector is open unless finished=True
    assert np.isnan(sector_splits(telemetry, meta["progress_total"], meta["laps"], meta["per_lap"])[-1, -1])
    splits = sector_splits(telemetry, meta["progress_total"], meta["laps"], meta["per_lap"], finished=True)
    assert np.abs(splits - result.sector_splits).max() <= CONTROL_DT + 1e-9


def test_a_recorded_crash_resets_once_and_restarts_the_splits(tmp_path):
    agent = recording_agent(saboteur=lambda self, progress, t: t >= 60.0)
    result = run_race(agent, "oval", car=KinematicCar(), seed=0)
    assert result.finished and result.collisions == 1
    recorded = _recorded(agent)
    _matches_runner_on_every_observed_non_held_row(recorded, result)
    telemetry, meta = read_csv(write_csv(recorded, tmp_path / "crash.csv", race_meta(result)))
    steps = np.diff(telemetry["progress"])
    assert int((steps < 0).sum()) == 1  # monotone apart from exactly one reset ...
    reset = int(np.argmax(steps < 0)) + 1
    assert telemetry["progress"][reset] < 0.1 * meta["waypoints_per_lap"]  # ... to the start
    assert agent.respawned == [float(telemetry["t"][reset])]
    splits = sector_splits(telemetry, meta["progress_total"], meta["laps"], meta["per_lap"], finished=True)
    # the restarted race: the splits run from the end of the hold, as the runner's do
    assert np.abs(splits - result.sector_splits).max() <= CONTROL_DT + 1e-9
    assert splits.sum() == pytest.approx(result.total_time - result.respawn_times[0] - 1.0, abs=1e-9)


def test_a_crash_near_the_start_after_a_lap_resets_the_recorder_to_zero(tmp_path):
    """Steering off within 15 m of the start in lap 2: the progress jump is small, so only the
    explicit collision signal can tell it from driving on; the recorder resets to 0."""
    track = load_track("oval")
    n = len(track)
    spacing = track.length / n

    def near_start_in_lap_two(agent, progress, t):
        return n <= progress < 2 * n and (progress - n) * spacing <= 15.0

    agent = recording_agent(saboteur=near_start_in_lap_two)
    result = run_race(agent, track, car=KinematicCar(), seed=0)
    assert result.collisions == 1
    crash_progress = int(result.telemetry["progress"][result.telemetry["t"] == result.respawn_times[0]][0])
    assert n <= crash_progress < n + 0.1 * n  # a crash near the start line, after a completed lap
    recorded = _recorded(agent)
    _matches_runner_on_every_observed_non_held_row(recorded, result)
    reset = int(np.argmax(np.diff(recorded["progress"]) < 0)) + 1
    assert recorded["progress"][reset - 1] >= n and recorded["progress"][reset] == 0
    assert agent.respawned == [float(recorded["t"][reset])]


def test_cumulative_progress_wraps_and_resets():
    recorder = CumulativeProgress(100)
    quiet = (0.0, 0.0, 0.0)
    assert [recorder.update(i, quiet) for i in (0, 50, 95, 99, 2, 40)] == [0, 50, 95, 99, 102, 140]
    assert recorder.update(97, quiet) == 197 and recorder.update(3, quiet) == 203
    assert recorder.update(5, (0.0, -1000.0, 0.0)) == 5 and recorder.respawned
    assert recorder.update(6, quiet) == 6 and not recorder.respawned
    assert recorder.update(7, (60.0, 60.0, 60.0)) == 7 and recorder.respawned  # |impulse| ≈ 104 > 100
    assert recorder.update(8, (50.0, 50.0, 0.0)) == 8 and not recorder.respawned  # ≈ 71: a bump only
    with pytest.raises(ValueError):
        CumulativeProgress(0)


# --- the sensor log (plan roar-004 G4.7) -----------------------------------------------------------


def _log_rows():
    rng = np.random.default_rng(5)
    rows = []
    for k in range(50):
        values = rng.normal(size=8)
        rows.append((k * 0.05, *values[:5], abs(values[5]) % 1.0, float(np.clip(values[6], -1, 1)), 0.0))
    rows.append((50 * 0.05 + 1.0, -1e-9, 0.0, -0.0, 1.0, 2.0, 0.5, -0.5, 1.0))
    return rows


LOG_META = {"track": "monza-like", "seed": 0, "noise": 0.1, "kind": "race"}


def test_the_sensor_log_round_trips(tmp_path):
    from racekit.telemetry import LOG_COLUMNS, log_array, read_log_csv, write_log_csv

    path = write_log_csv(_log_rows(), tmp_path / "log.csv", LOG_META)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "# racekit-log v1 track=monza-like seed=0 noise=0.1 kind=race"
    assert lines[1] == ",".join(LOG_COLUMNS) == "t,x,y,yaw,vx,vy,throttle,steer,brake"
    assert "-0.000000" not in path.read_text(encoding="utf-8")
    log, meta = read_log_csv(path)
    assert meta == LOG_META and log.dtype.names == LOG_COLUMNS and log.size == 51
    assert np.allclose(log.view((np.float64, 9)), log_array(_log_rows()).view((np.float64, 9)), atol=5e-7)
    again = write_log_csv(log, tmp_path / "again.csv", meta)
    assert again.read_bytes() == path.read_bytes()


@pytest.mark.parametrize("meta", [
    {"track": "monza like", "seed": 0, "noise": 0.1, "kind": "race"},
    {"track": "monza-like", "seed": -1, "noise": 0.1, "kind": "race"},
    {"track": "monza-like", "seed": 0, "noise": -0.1, "kind": "race"},
    {"track": "monza-like", "seed": 0, "noise": 0.1},
    {"track": "monza-like", "seed": True, "noise": 0.1, "kind": "race"},
])
def test_the_sensor_log_writer_validates_its_meta(tmp_path, meta):
    from racekit.telemetry import write_log_csv

    with pytest.raises(ValueError):
        write_log_csv(_log_rows(), tmp_path / "log.csv", meta)


@pytest.mark.parametrize(("first", "header", "row"), [
    ("# racekit-telemetry v1 progress_total=3 laps=1 per_lap=3 waypoints_per_lap=3", None, None),
    ("# racekit-log v1 track=oval seed=x noise=0.1 kind=race", None, None),
    (None, "t,x,y,yaw,v,throttle,steer,brake", None),
    (None, None, "0.0,1.0"),
])
def test_the_sensor_log_reader_validates_its_input(tmp_path, first, header, row):
    from racekit.telemetry import read_log_csv

    lines = [first or "# racekit-log v1 track=oval seed=0 noise=0.1 kind=steady",
             header or "t,x,y,yaw,vx,vy,throttle,steer,brake", row or "0,0,0,0,0,0,0,0,0"]
    path = tmp_path / "bad.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValueError):
        read_log_csv(path)
