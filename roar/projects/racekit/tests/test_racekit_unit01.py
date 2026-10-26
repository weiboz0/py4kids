"""Unit 1's pinned gates on racekit (plan roar-002 Phase 1): the starter's repeated jittered runs
(G1, G2), the deterministic baseline, the saboteur's crash cost (G6) and the collision-first order
on a finishing tick ([fable] N6)."""

from __future__ import annotations

import hashlib

import numpy as np
import pytest
from conftest import RACEKIT
from racekit import cars
from racekit.cars import KinematicCar
from racekit.measure import repeat_races
from racekit.runner import CONTROL_DT, RESPAWN_HOLD_TICKS, load_submission, run_race, shim_installed
from racekit.tracks import Track

UNIT_01 = RACEKIT / "agents" / "unit-01.py"
# The probe's pins (plan roar-002 "Gates"): per-seed times, seeds 0-4, KinematicCar(jitter=0.05).
PINNED = {
    "oval": [220.60, 220.75, 220.75, 220.95, 220.60],
    "monza-like": [870.30, 870.50, 870.70, 870.75, 870.45],
}
DETERMINISTIC_OVAL = 223.50


@pytest.mark.parametrize("track", sorted(PINNED))
def test_g1_g2_the_starter_finishes_clean_with_the_pinned_per_seed_times(track):
    runs = repeat_races(UNIT_01, track, n=5, car_factory=lambda: KinematicCar(jitter=0.05))
    assert runs.all_finished and runs.collisions == 0  # G1
    assert all(result.laps == 3 for result in runs.results)
    assert np.allclose(runs.times, PINNED[track], rtol=0.0, atol=1e-9)  # G2, exactly (tick-quantized)
    assert runs.median == pytest.approx(float(np.median(PINNED[track])), abs=1e-9)
    assert runs.spread == pytest.approx(max(PINNED[track]) - min(PINNED[track]), abs=1e-9)
    # the same seed gives the same race
    again = run_race(UNIT_01, track, car=KinematicCar(jitter=0.05), seed=3) if track == "oval" else None
    if again is not None:
        assert again.total_time == runs.results[3].total_time
        assert np.array_equal(again.telemetry, runs.results[3].telemetry)


def test_g2_jitter_zero_is_the_deterministic_baseline():
    runs = repeat_races(UNIT_01, "oval", n=3, car_factory=lambda: KinematicCar(jitter=0.0))
    assert runs.all_finished and runs.collisions == 0
    assert runs.times.tolist() == pytest.approx([DETERMINISTIC_OVAL] * 3, abs=1e-9)
    assert runs.spread == 0.0


# sha256 over np.round(column, 6) (fixed column order) of the starter's oval race on roar-001's
# KinematicCar (before jitter existed), taken at roar-002's base commit.
ROAR_001_OVAL_TELEMETRY = "2b787d9b65d84e1f8e5770476f6a0c4dc8e1983a239b042f3905683ba6d88da8"


def _rounded_hash(telemetry: np.ndarray) -> str:
    digest = hashlib.sha256()
    for name in telemetry.dtype.names:
        digest.update(np.round(telemetry[name].astype(np.float64), 6).tobytes())
    return digest.hexdigest()


def test_jitter_zero_race_draws_nothing_and_matches_roar_001(monkeypatch):
    class Raising:
        def __getattr__(self, name):
            raise AssertionError(f"jitter = 0 drew a random number ({name})")

    monkeypatch.setattr(cars.random, "Random", lambda *args: Raising())
    result = run_race(UNIT_01, "oval", car=KinematicCar(jitter=0.0), seed=4)
    assert result.total_time == pytest.approx(DETERMINISTIC_OVAL, abs=1e-9)
    assert _rounded_hash(result.telemetry) == ROAR_001_OVAL_TELEMETRY


def _saboteur(crash_at: float):
    """The starter, with a firm right at full throttle from ``crash_at`` seconds until it crashes."""
    with shim_installed():
        starter, _ = load_submission(UNIT_01)

    class Saboteur(starter):
        async def initialize(self):
            await super().initialize()
            self.steps = 0
            self.crashed = False

        async def step(self):
            impulse = self.collision_sensor.get_last_gym_observation()
            if float(np.linalg.norm(impulse)) > 100.0:
                self.crashed = True
            await super().step()
            if not self.crashed and self.steps * CONTROL_DT >= crash_at:
                await self.vehicle.apply_action({"throttle": 1.0, "steer": 0.25, "brake": 0.0,
                                                 "hand_brake": 0.0, "reverse": 0, "target_gear": 0})
            self.steps += 1

    return Saboteur


def test_g6_a_crash_restarts_the_race_with_the_clock_running():
    result = run_race(_saboteur(60.0), "oval", car=KinematicCar(jitter=0.0))
    assert result.finished
    assert len(result.respawn_times) == 1 and result.collisions == 1
    t_crash = result.respawn_times[0]
    assert 60.0 < t_crash < 65.0
    assert abs(result.total_time - (DETERMINISTIC_OVAL + t_crash + 1.0)) <= CONTROL_DT + 1e-9
    telemetry = result.telemetry
    held = telemetry["held"] == 1
    assert int(held.sum()) == RESPAWN_HOLD_TICKS
    first_held = int(np.argmax(held))
    assert telemetry["t"][first_held - 1] == pytest.approx(t_crash)
    # held rows keep the pre-reset progress; the first row after the hold has progress reset to ~0
    assert (telemetry["progress"][held] == telemetry["progress"][first_held - 1]).all()
    after = first_held + RESPAWN_HOLD_TICKS
    assert telemetry["progress"][first_held - 1] > 100 and telemetry["progress"][after] <= 1


class _Straight:
    """A scripted car on a straight: from the start it moves 1 m, then 2 m per tick (half-way
    between waypoints), with a sideways step of ``swerve`` metres on tick ``swerve_tick`` only."""

    def __init__(self, swerve_tick: int = -1, swerve: float = 0.0) -> None:
        self.swerve_tick, self.swerve = swerve_tick, swerve
        self.calls = 0
        self.x = self.y = self.yaw = self.v = 0.0

    def reset(self, x, y, yaw, v=0.0):
        self.x, self.y, self.yaw, self.v = float(x), float(y), float(yaw), float(v)

    def velocity(self):
        return 40.0, 0.0

    def advance(self, throttle, steer, brake, hand_brake, reverse, dt, substeps):
        self.calls += 1
        self.x += 1.0 if self.x == 0.0 else 2.0
        self.y = self.swerve if self.calls == self.swerve_tick else 0.0


class _Idle:
    def __init__(self, waypoints, vehicle, *sensors):
        self.vehicle = vehicle

    async def initialize(self):
        pass

    async def step(self):
        await self.vehicle.apply_action({"throttle": 0.5, "steer": 0.0, "brake": 0.0, "hand_brake": 0.0,
                                         "reverse": 0, "target_gear": 0})


def _straight_track(n: int = 60) -> Track:
    x = 2.0 * np.arange(n)
    return Track("straight", x, np.zeros(n), np.zeros(n), 0.5)


def test_n6_a_tick_that_finishes_and_collides_is_a_collision():
    track = _straight_track()
    clean = run_race(_Idle, track, car=_Straight(), laps=1, max_seconds=20.0)
    assert clean.finished and clean.collisions == 0
    finish_tick = clean.ticks
    swerved = run_race(_Idle, track, car=_Straight(swerve_tick=finish_tick, swerve=0.6), laps=1, max_seconds=20.0)
    # the swerve tick reaches the finish margin AND leaves the 0.5 m half-width: the collision wins
    assert swerved.respawn_times[0] == pytest.approx(finish_tick * CONTROL_DT)
    crash_row = swerved.telemetry[finish_tick - 1]
    assert crash_row["progress"] + 5 >= swerved.progress_total and abs(crash_row["offset"]) > 0.5
    assert swerved.collisions == 1 and swerved.finished  # it then restarts and finishes
    assert swerved.total_time == pytest.approx((2 * finish_tick + RESPAWN_HOLD_TICKS) * CONTROL_DT)
