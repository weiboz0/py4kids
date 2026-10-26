"""The race runner: lifecycle, progress, respawn, finish, sync paths and the shim's lifetime
(plan roar-001 Phase D; design 013 §4.2)."""

from __future__ import annotations

import asyncio
import math
import sys
import time
import types

import numpy as np
import pytest
from conftest import STARTER
from racekit.cars import KinematicCar
from racekit.runner import advance_progress, run_race
from racekit.tracks import load_track

ACTION = {"throttle": 0.0, "steer": 0.0, "brake": 0.0, "hand_brake": 0.0, "reverse": 0}


class Follower:
    """A scripted near-perfect follower: pure pursuit 8 m ahead at a held speed."""

    speed = 15.0

    def __init__(self, maneuverable_waypoints, vehicle, camera_sensor, location_sensor,
                 velocity_sensor, rpy_sensor, occupancy_map_sensor, collision_sensor):
        self.points = np.array([waypoint.location[:2] for waypoint in maneuverable_waypoints])
        self.vehicle = vehicle
        self.location_sensor = location_sensor
        self.velocity_sensor = velocity_sensor
        self.rpy_sensor = rpy_sensor
        self.index = 0
        self.car = KinematicCar()

    async def initialize(self):
        pass

    async def step(self):
        x, y, _ = self.location_sensor.get_last_gym_observation()
        yaw = float(self.rpy_sensor.get_last_gym_observation()[2])
        v = float(np.linalg.norm(self.velocity_sensor.get_last_gym_observation()))
        n = len(self.points)
        window = (self.index + np.arange(20)) % n
        self.index = int(window[np.argmin(np.hypot(*(self.points[window] - (x, y)).T))])
        tx, ty = self.points[(self.index + 4) % n]
        alpha = math.atan2(ty - y, tx - x) - yaw
        alpha = (alpha + math.pi) % (2 * math.pi) - math.pi
        delta = math.atan2(2.0 * self.car.wheelbase * math.sin(alpha), 8.0)
        command = 0.5 * (self.speed - v)
        await self.vehicle.apply_action(dict(
            ACTION, steer=max(-1.0, min(1.0, -delta / self.car.max_steer)),
            throttle=max(0.0, min(1.0, command)), brake=max(0.0, min(1.0, -command)),
        ))


def test_a_scripted_follower_finishes_the_oval_in_the_expected_band():
    track = load_track("oval")
    result = run_race(Follower, track)
    assert result.finished and result.collisions == 0
    ideal = 3 * track.length / Follower.speed  # at the held speed, no acceleration phase
    assert ideal < result.total_time < ideal * 1.03
    assert result.progress_total == 3 * len(track)
    assert result.progress_required == result.progress_total - 5
    assert result.progress >= result.progress_required
    assert np.abs(result.telemetry["offset"]).max() < 1.0


def test_three_lap_finish_detection_and_sector_splits():
    one = run_race(Follower, "oval", laps=1)
    three = run_race(Follower, "oval", laps=3)
    assert one.finished and three.finished
    assert one.progress_total == len(load_track("oval"))
    assert three.progress_total == 3 * len(load_track("oval"))
    assert three.total_time == pytest.approx(3 * one.total_time - 2 * 1.6, abs=2.0)
    assert three.sector_splits.shape == (3, 3) and not np.isnan(three.sector_splits).any()
    assert three.sector_splits.sum() == pytest.approx(three.total_time, abs=1e-9)
    # telemetry: one row per tick with the fixed fields
    assert three.telemetry.dtype.names == (
        "t", "x", "y", "yaw", "v", "throttle", "steer", "brake", "progress", "offset", "held",
    )
    assert not three.telemetry["held"].any()
    assert three.telemetry.shape[0] == three.ticks == round(three.total_time / 0.05)
    assert np.all(np.diff(three.telemetry["progress"]) >= 0)
    assert three.step_ms.shape == (three.ticks,)


def test_the_finish_uses_the_five_waypoint_margin():
    result = run_race(Follower, "oval", laps=1)
    progress = result.telemetry["progress"]
    assert result.finished
    assert progress[-1] + 5 >= result.progress_total  # finished on this tick ...
    assert progress[-2] + 5 < result.progress_total  # ... and not one tick earlier
    assert progress[-1] < result.progress_total - 1  # short of the last waypoint


def test_an_unfinished_race_reports_a_timeout():
    result = run_race(Follower, "oval", max_seconds=10.0)
    assert not result.finished
    assert result.total_time == pytest.approx(10.0)
    assert np.isnan(result.sector_splits[-1, -1])


class DriveOff(Follower):
    """Follows the line, then steers hard left at 6 s: it must leave the track and respawn."""

    impulses = []  # noqa: RUF012 - the collision sensor's reading at every step

    def __init__(self, *args):
        super().__init__(*args)
        self.ticks = 0
        self.collision_sensor = args[-1]

    async def initialize(self):
        DriveOff.impulses = []

    async def step(self):
        self.ticks += 1
        DriveOff.impulses.append(self.collision_sensor.get_last_gym_observation().copy())
        if 120 <= self.ticks < 160:
            await self.vehicle.apply_action(dict(ACTION, throttle=0.5, steer=-1.0))
        else:
            await super().step()


def test_drive_off_respawns_at_the_start_pose_holds_and_resets_progress():
    track = load_track("oval")
    result = run_race(DriveOff, track, max_seconds=60.0)
    assert result.collisions >= 1 and len(result.respawn_times) == result.collisions
    telemetry = result.telemetry
    crash = round(result.respawn_times[0] / 0.05) - 1
    assert telemetry["t"][crash] == pytest.approx(result.respawn_times[0])
    assert abs(telemetry["offset"][crash]) > track.half_width[0]  # it left the drivable width
    assert telemetry["progress"][crash] > 0 and not telemetry["held"][crash]
    # the 20-tick (1.0 s) hold: at the start pose, at rest, the agent not called
    hold = telemetry[crash + 1 : crash + 21]
    start_x, start_y, start_yaw = track.start_pose()
    assert hold["held"].all() and len(hold) == 20
    assert hold["t"][-1] - telemetry["t"][crash] == pytest.approx(1.0)
    assert np.allclose(hold["x"], start_x) and np.allclose(hold["y"], start_y)
    assert np.allclose(hold["yaw"], start_yaw) and not hold["v"].any()
    steps_before = crash + 1  # one agent step per row before the hold
    assert len(DriveOff.impulses) == len(telemetry) - int(telemetry["held"].sum())
    assert result.step_ms.size == len(DriveOff.impulses)
    # right after the hold: progress reset to 0, the car still at the start
    after = telemetry[crash + 21]
    assert not after["held"] and after["progress"] == 0
    assert math.hypot(after["x"] - start_x, after["y"] - start_y) < 0.1
    # the collision sensor reports a major impulse at the first step after the hold, none before
    assert np.linalg.norm(DriveOff.impulses[steps_before]) > 100.0
    assert np.linalg.norm(DriveOff.impulses[steps_before - 1]) == 0.0
    # the sector clock restarts with the race
    assert np.isnan(result.sector_splits).all() or result.sector_splits[0, 0] > 0


class ParkAfterCrash(DriveOff):
    """Drives off once, then brakes for ever after the respawn."""

    async def step(self):
        crashed = any(np.linalg.norm(impulse) > 0 for impulse in DriveOff.impulses)
        if crashed or np.linalg.norm(self.collision_sensor.get_last_gym_observation()) > 0:
            DriveOff.impulses.append(self.collision_sensor.get_last_gym_observation().copy())
            await self.vehicle.apply_action(dict(ACTION, brake=1.0))
        else:
            await super().step()


def test_a_parked_agent_after_a_crash_never_regains_progress():
    result = run_race(ParkAfterCrash, "oval", max_seconds=40.0)
    assert result.collisions == 1 and not result.finished
    crash = round(result.respawn_times[0] / 0.05) - 1
    assert result.telemetry["progress"][crash] > 0
    assert not result.telemetry["progress"][crash + 21 :].any()
    assert result.progress == 0
    assert result.total_time == pytest.approx(40.0)


def test_the_forward_window_ignores_far_ahead_waypoints():
    wx = [2.0 * i for i in range(100)]
    wy = [0.0] * 100
    # the car moved past waypoint 30, far beyond the 15-waypoint window starting at 0
    assert advance_progress(wx, wy, 0, 58.0, 0.0, 61.0, 0.0) == 14
    # within the window, the waypoint closest to the motion segment wins
    assert advance_progress(wx, wy, 0, 15.0, 0.5, 17.0, 0.5) in (8, 9)
    assert advance_progress(wx, wy, 20, 20.0, 0.0, 21.0, 0.0) == 20  # never backwards
    assert advance_progress(wx, wy, 95, 197.0, 0.0, 199.0, 0.0) == 99  # clipped at the end


class Lifecycle:
    calls = []  # noqa: RUF012 - a per-test call log

    def __init__(self, maneuverable_waypoints, vehicle, camera_sensor, location_sensor,
                 velocity_sensor, rpy_sensor, occupancy_map_sensor, collision_sensor):
        Lifecycle.calls.append("init")
        self.vehicle = vehicle

    async def initialize(self):
        Lifecycle.calls.append("initialize")
        self.target = 0.4  # state that step() needs

    async def step(self):
        Lifecycle.calls.append("step")
        await self.vehicle.apply_action(dict(ACTION, throttle=self.target))


def _check_lifecycle():
    calls = Lifecycle.calls
    assert calls[:2] == ["init", "initialize"]
    assert calls.count("initialize") == 1 and calls.count("init") == 1
    assert set(calls[2:]) == {"step"} and len(calls) == 2 + 40


def test_lifecycle_without_a_running_loop():
    Lifecycle.calls = []
    result = run_race(Lifecycle, "oval", max_seconds=2.0)
    _check_lifecycle()
    assert result.telemetry["throttle"][0] == pytest.approx(0.4)


def test_lifecycle_inside_a_running_loop_uses_a_worker_thread():
    Lifecycle.calls = []

    async def notebook_cell():
        asyncio.get_running_loop()  # as in a Jupyter kernel
        return run_race(Lifecycle, "oval", max_seconds=2.0)

    result = asyncio.run(notebook_cell())
    _check_lifecycle()
    assert result.ticks == 40


def test_exceptions_propagate_from_both_paths():
    class Broken(Lifecycle):
        async def step(self):
            raise ZeroDivisionError("boom")

    with pytest.raises(ZeroDivisionError):
        run_race(Broken, "oval", max_seconds=1.0)

    async def cell():
        return run_race(Broken, "oval", max_seconds=1.0)

    with pytest.raises(ZeroDivisionError):
        asyncio.run(cell())


def test_function_local_import_of_the_shim_works(write_submission):
    path = write_submission(
        '''
        async def initialize(self):
            pass

        async def step(self):
            import roar_py_interface as rpi
            assert isinstance(self.vehicle, rpi.RoarPyActor)
            await self.vehicle.apply_action({"throttle": 0.3, "steer": 0.0, "brake": 0.0,
                                             "hand_brake": 0.0, "reverse": 0})
        ''',
        header="from __future__ import annotations\n\n\n",
    )
    assert "roar_py_interface" not in sys.modules
    result = run_race(path, "oval", max_seconds=1.0)
    assert result.ticks == 20
    assert "roar_py_interface" not in sys.modules  # restored afterwards


def test_two_submissions_load_in_one_process_without_collision(write_submission, tmp_path):
    body = '''
    async def initialize(self):
        pass

    async def step(self):
        await self.vehicle.apply_action({"throttle": THROTTLE, "steer": 0.0, "brake": 0.0,
                                         "hand_brake": 0.0, "reverse": 0})
    '''
    slow = write_submission(body, header="import roar_py_interface\nTHROTTLE = 0.2\n\n\n",
                            folder=tmp_path / "a")
    fast = write_submission(body, header="import roar_py_interface\nTHROTTLE = 0.9\n\n\n",
                            folder=tmp_path / "b")
    assert slow.name == fast.name == "submission.py"
    first = run_race(slow, "oval", max_seconds=2.0)
    second = run_race(fast, "oval", max_seconds=2.0)
    third = run_race(slow, "oval", max_seconds=2.0)
    assert first.telemetry["throttle"][-1] == pytest.approx(0.2)
    assert second.telemetry["throttle"][-1] == pytest.approx(0.9)
    assert third.telemetry["throttle"][-1] == pytest.approx(0.2)
    assert not [name for name in sys.modules if name.startswith("racekit_submission_")]


def test_the_runner_refuses_to_shadow_a_real_module(tmp_path, monkeypatch):
    impostor = types.ModuleType("roar_py_interface")
    monkeypatch.setitem(sys.modules, "roar_py_interface", impostor)
    with pytest.raises(RuntimeError, match="already imported"):
        run_race(Lifecycle, "oval", max_seconds=1.0)
    assert sys.modules["roar_py_interface"] is impostor
    monkeypatch.delitem(sys.modules, "roar_py_interface")
    (tmp_path / "roar_py_interface.py").write_text("REAL = True\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    with pytest.raises(RuntimeError, match="installed"):
        run_race(Lifecycle, "oval", max_seconds=1.0)
    assert "roar_py_interface" not in sys.modules


def test_a_file_without_the_solution_class_is_rejected(tmp_path):
    path = tmp_path / "empty.py"
    path.write_text("X = 1\n")
    with pytest.raises(ImportError, match="RoarCompetitionSolution"):
        run_race(path, "oval", max_seconds=1.0)


def test_starter_on_monza_like_informational():
    """Informational timing (printed, never asserted: CI jitter). Also the design's tick estimate."""
    started = time.perf_counter()
    result = run_race(STARTER, "monza-like")
    wall = time.perf_counter() - started
    print(f"\nstarter monza-like: {result!r}; {result.ticks} ticks; "
          f"{wall * 1000.0 / result.ticks:.3f} ms/tick wall; step p99 {result.step_ms_p99():.3f} ms")
    assert result.finished and result.collisions == 0
    assert 15000 < result.ticks < 20000  # design 013 §4.2: about 17,000 ticks at 20 m/s


def test_simulation_is_deterministic():
    first = run_race(STARTER, "test-circuit", laps=1)
    second = run_race(STARTER, "test-circuit", laps=1)
    fields = [name for name in first.telemetry.dtype.names]
    for name in fields:
        assert np.array_equal(first.telemetry[name], second.telemetry[name])
