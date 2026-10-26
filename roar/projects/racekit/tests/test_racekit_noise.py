"""Noise on the carla-like car (plan roar-004 G4.4) and the carla-like car's construction."""

from __future__ import annotations

import numpy as np
import pytest
from drivers import pure_pursuit
from racekit import _truth
from racekit.cars import DynamicCar, carla_like
from racekit.runner import run_race

SPREAD_BAND = (0.15, 0.6)  # s: 3–12 ticks around the probe's 0.25 s (5 ticks)


def test_g4_4_throttle_noise_spreads_clean_runs_within_the_band(premise):
    outcomes = premise["noise-monza-3.5"]
    assert len(outcomes) == 5
    assert all(o.finished and o.collisions == 0 for o in outcomes), outcomes
    times = [o.total_time for o in outcomes]
    spread = max(times) - min(times)
    assert SPREAD_BAND[0] <= spread <= SPREAD_BAND[1], times


def _oval_lap(car, seed):
    return run_race(pure_pursuit(45.0, 3.5, None, 6.0, 150), "oval", car=car, laps=1, seed=seed)


def test_g4_4_noise_false_is_deterministic_and_seeds_repeat():
    quiet = [_oval_lap(carla_like(noise=False), seed) for seed in (0, 3)]
    assert quiet[0].total_time == quiet[1].total_time
    assert np.array_equal(quiet[0].telemetry, quiet[1].telemetry)
    noisy = [_oval_lap(carla_like(noise=True), seed) for seed in (3, 3, 4)]
    assert np.array_equal(noisy[0].telemetry, noisy[1].telemetry)
    assert not np.array_equal(noisy[0].telemetry, noisy[2].telemetry)
    assert not np.array_equal(noisy[0].telemetry, quiet[0].telemetry)


def test_carla_like_is_a_configured_dynamic_car_with_throttle_only_noise():
    quiet, noisy = carla_like(), carla_like(noise=True)
    assert type(quiet) is DynamicCar and type(noisy) is DynamicCar
    assert quiet.jitter == 0.0 and noisy.jitter == _truth.NOISE_SIGMA == 0.1
    assert quiet.steer_jitter == noisy.steer_jitter == 0.0
    assert quiet.per_section
    defaults = DynamicCar()
    # the parameters Unit 8 identifies differ from the public defaults; mass, L and lag are shared
    for name in ("max_steer", "a_throttle", "a_brake", "c_drag"):
        assert getattr(quiet, name) != getattr(defaults, name), name
    for name in ("mass", "wheelbase", "lag_ticks"):
        assert getattr(quiet, name) == getattr(defaults, name), name


def test_carla_like_takes_its_grip_from_the_track_it_races():
    car = carla_like()
    run_race(pure_pursuit(20.0), "oval", car=car, laps=1, max_seconds=30.0)
    assert car.mu == _truth.grip_table("oval")
    run_race(pure_pursuit(20.0), "test-circuit", car=car, laps=1, max_seconds=5.0)
    assert car.mu == _truth.grip_table("test-circuit")
    assert 0.78 <= min(car.mu) and max(car.mu) <= 1.05
    with pytest.raises(RuntimeError):
        carla_like().advance(0.5, 0.0, 0.0, 0.0, 0.0, 0.05, 10)
