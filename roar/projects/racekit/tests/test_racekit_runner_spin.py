"""The runner's roar-004 additions (plan roar-004 G4.2): the spin-out major collision,
``respawn_causes``, and ``attach_track`` once per race."""

from __future__ import annotations

import inspect
from typing import ClassVar

import numpy as np
import pytest
from racekit.cars import KinematicCar
from racekit.runner import CONTROL_DT, CRASH_IMPULSE, RESPAWN_HOLD_TICKS, run_race
from racekit.tracks import Track


class _ScriptedCar:
    """A scripted car on a straight: from the start it moves 1 m, then 2 m per tick. It reports a
    spin-out on the ticks in ``spin_ticks`` and steps sideways off the track on ``wall_ticks``
    (ticks counted since the race start, across respawns)."""

    def __init__(self, spin_ticks=(), wall_ticks=()) -> None:
        self.spin_ticks, self.wall_ticks = set(spin_ticks), set(wall_ticks)
        self.calls = 0
        self.attached = []
        self.x = self.y = self.yaw = self.v = 0.0

    def attach_track(self, track):
        self.attached.append(track.name)

    def reset(self, x, y, yaw, v=0.0):
        self.x, self.y, self.yaw, self.v = float(x), float(y), float(yaw), float(v)

    def velocity(self):
        return 40.0, 0.0

    def advance(self, throttle, steer, brake, hand_brake, reverse, dt, substeps):
        self.calls += 1
        self.x += 1.0 if self.x == 0.0 else 2.0
        self.y = 5.0 if self.calls in self.wall_ticks else 0.0

    def spun_out(self):
        return self.calls in self.spin_ticks


class _Recorder:
    """Drives on and records the collision sensor's reading at every step."""

    impulses: ClassVar[list] = []

    def __init__(self, waypoints, vehicle, camera, location, velocity, rpy, occupancy, collision):
        self.vehicle, self.collision, self.location = vehicle, collision, location
        type(self).impulses = []

    async def initialize(self):
        pass

    async def step(self):
        type(self).impulses.append((tuple(self.collision.get_last_gym_observation().tolist()),
                                    tuple(self.location.get_last_gym_observation().tolist())))
        await self.vehicle.apply_action({"throttle": 0.5, "steer": 0.0, "brake": 0.0, "hand_brake": 0.0,
                                         "reverse": 0, "target_gear": 0})


def _straight(n: int = 200) -> Track:
    x = 2.0 * np.arange(n)
    return Track("straight", x, np.zeros(n), np.zeros(n), 1.0)


def test_a_spin_out_respawns_exactly_like_the_wall():
    spin = run_race(_Recorder, _straight(), car=_ScriptedCar(spin_ticks={20}), laps=1, max_seconds=5.0)
    wall = run_race(_Recorder, _straight(), car=_ScriptedCar(wall_ticks={20}), laps=1, max_seconds=5.0)
    assert spin.respawn_causes == ["spin"] and wall.respawn_causes == ["wall"]
    assert spin.collisions == wall.collisions == 1
    assert spin.respawn_times == [pytest.approx(20 * CONTROL_DT)]
    telemetry = spin.telemetry
    held = telemetry["held"] == 1
    assert int(held.sum()) == RESPAWN_HOLD_TICKS
    first_held = int(np.argmax(held))
    assert first_held == 20
    # the start pose, at rest, through the hold
    assert (telemetry["x"][held] == 0.0).all() and (telemetry["v"][held] == 0.0).all()
    # progress resets to 0 when the hold ends: the first row after it is back at the start
    assert telemetry["progress"][first_held - 1] > 10
    assert telemetry["progress"][first_held + RESPAWN_HOLD_TICKS] <= 1
    # same tick count, same progress: the spin's respawn is the wall's
    assert np.array_equal(spin.telemetry["progress"], wall.telemetry["progress"])
    assert np.array_equal(spin.telemetry["held"], wall.telemetry["held"])


def test_a_spin_reports_the_crash_impulse_on_the_first_step_after_the_hold():
    run_race(_Recorder, _straight(), car=_ScriptedCar(spin_ticks={20}), laps=1, max_seconds=5.0)
    impulses = [np.linalg.norm(reading) for reading, _ in _Recorder.impulses]
    assert impulses[20] == pytest.approx(CRASH_IMPULSE)
    assert all(value == 0.0 for k, value in enumerate(impulses) if k != 20)


def test_wall_and_spin_on_the_same_tick_is_a_wall():
    result = run_race(_Recorder, _straight(), car=_ScriptedCar(spin_ticks={20, 60}, wall_ticks={20}),
                      laps=1, max_seconds=6.0)
    assert result.respawn_causes == ["wall", "spin"]
    assert result.collisions == len(result.respawn_times) == 2


def test_attach_track_is_called_once_per_race_even_with_respawns():
    car = _ScriptedCar(spin_ticks={10, 50})
    result = run_race(_Recorder, _straight(), car=car, laps=1, max_seconds=5.0)
    assert result.collisions == 2
    assert car.attached == ["straight"]
    run_race(_Recorder, _straight(), car=car, laps=1, max_seconds=1.0)
    assert car.attached == ["straight", "straight"]


def test_a_car_without_spun_out_or_attach_track_races_as_before():
    """KinematicCar has neither hook; the default car is still KinematicCar."""
    assert inspect.signature(run_race).parameters["car"].default is None
    default = run_race(_Recorder, "oval", laps=1, max_seconds=10.0)
    explicit = run_race(_Recorder, "oval", car=KinematicCar(), laps=1, max_seconds=10.0)
    assert np.array_equal(default.telemetry, explicit.telemetry)
    assert default.respawn_causes == []
