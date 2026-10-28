"""The perturbed carla-like family (plan roar-010 U11.1; design 013 §4.4 v4.9).

``carla_like(perturb=k)`` multiplies the car's mass and yaw inertia, steering gain, throttle and brake
authority, drag and every section's grip by ``perturbation_factors(k)``, drawn from
``random.Random(f"perturb:{k}")``, one ``uniform`` per factor in ``PERTURBATION_FAMILY``'s order (the
probe's draw exactly, so the probe outcomes carry over). ``perturb=None`` is today's car to the bit;
``lag_ticks`` replaces the lag on its own.
"""

from __future__ import annotations

import hashlib

import pytest
from conftest import RACEKIT
from racekit import _truth
from racekit.cars import PERTURBATION_FAMILY, DynamicCar, carla_like, perturbation_factors
from racekit.runner import run_race

ORDER = ("grip", "steering", "throttle", "brake", "mass", "drag")
RANGES = {"grip": (0.92, 1.00), "steering": (0.95, 1.05), "throttle": (0.90, 1.10), "brake": (0.90, 1.05),
          "mass": (0.95, 1.10), "drag": (0.90, 1.10)}
# k = 0's factors, as the probe (pk.py) drew them: a change of salt or order is a re-gate
K0 = {"grip": 0.9772982538664562, "steering": 1.0330433154877583, "throttle": 0.9764160702539033,
      "brake": 0.9251899711729277, "mass": 1.0359238348007391, "drag": 0.9773829726255534}
AGENT = RACEKIT / "agents" / "unit-09.py"  # pure pursuit: a quick full-speed driver


def _todays_car(noise: bool, lag_ticks: int = _truth.LAG_TICKS) -> DynamicCar:
    """``carla_like`` as it was before roar-010."""
    car = DynamicCar(
        mass=_truth.MASS, yaw_inertia=_truth.YAW_INERTIA, lf=_truth.LF, wheelbase=_truth.WHEELBASE,
        max_steer=_truth.MAX_STEER, a_throttle=_truth.A_THROTTLE, a_brake=_truth.A_BRAKE,
        c_drag=_truth.C_DRAG, tyre_b=_truth.TYRE_B, tyre_c=_truth.TYRE_C, lag_ticks=lag_ticks,
        jitter=_truth.NOISE_SIGMA if noise else 0.0,
    )
    car._grip_table = _truth.grip_table
    return car


def _race(car, laps=1):
    result = run_race(AGENT, "test-circuit", car=car, seed=2, laps=laps)
    return result, hashlib.sha256(result.telemetry.tobytes() + repr(result.respawn_causes).encode()).hexdigest()


def test_the_family_is_published_in_the_draw_order():
    assert tuple(PERTURBATION_FAMILY) == ORDER
    assert dict(PERTURBATION_FAMILY) == RANGES
    with pytest.raises(TypeError):
        PERTURBATION_FAMILY["grip"] = (1.0, 1.0)  # read-only


def test_k_0_is_pinned_and_the_draw_is_deterministic():
    assert perturbation_factors(0) == K0
    assert tuple(perturbation_factors(0)) == ORDER
    for k in (0, 7, 23, 47, 999):
        assert perturbation_factors(k) == perturbation_factors(k)
    assert perturbation_factors(1) != perturbation_factors(0)


def test_every_factor_is_inside_its_range_for_k_0_to_999():
    for k in range(1000):
        factors = perturbation_factors(k)
        assert tuple(factors) == ORDER, k
        for name, (low, high) in RANGES.items():
            assert low <= factors[name] <= high, (k, name, factors[name])


@pytest.mark.parametrize("bad", (True, 1.0, "3", None))
def test_k_must_be_an_int(bad):
    with pytest.raises(TypeError):
        perturbation_factors(bad)


def test_a_perturbed_car_has_its_factors():
    for k in (0, 8, 41):
        f = perturbation_factors(k)
        car = carla_like(perturb=k)
        assert car.mass == _truth.MASS * f["mass"] and car.yaw_inertia == _truth.YAW_INERTIA * f["mass"]
        assert car.max_steer == _truth.MAX_STEER * f["steering"]
        assert car.a_throttle == _truth.A_THROTTLE * f["throttle"] and car.a_brake == _truth.A_BRAKE * f["brake"]
        assert car.c_drag == _truth.C_DRAG * f["drag"]
        assert car._grip_table("test-circuit") == tuple(mu * f["grip"] for mu in _truth.grip_table("test-circuit"))
        # not perturbed: the geometry, the tyre shape, the lag and the noise
        assert (car.lf, car.wheelbase, car.tyre_b, car.tyre_c) == (_truth.LF, _truth.WHEELBASE, _truth.TYRE_B,
                                                                  _truth.TYRE_C)
        assert car.lag_ticks == _truth.LAG_TICKS and car.jitter == 0.0
        assert carla_like(noise=True, perturb=k).jitter == _truth.NOISE_SIGMA


@pytest.mark.parametrize("noise", (False, True))
def test_perturb_none_races_exactly_like_todays_car(noise):
    today, today_digest = _race(_todays_car(noise))
    for car in (carla_like(noise=noise), carla_like(noise=noise, perturb=None, lag_ticks=None)):
        result, digest = _race(car)
        assert result.total_time == today.total_time and digest == today_digest
    assert today.finished


def test_a_perturbed_car_races_differently():
    _, today = _race(_todays_car(True))
    _, perturbed = _race(carla_like(noise=True, perturb=0))
    _, again = _race(carla_like(noise=True, perturb=0))
    assert perturbed != today and perturbed == again


def test_lag_ticks_replaces_the_lag_alone():
    for k in (None, 5):
        base, lagged = carla_like(perturb=k), carla_like(perturb=k, lag_ticks=2)
        assert lagged.lag_ticks == 2 and base.lag_ticks == _truth.LAG_TICKS
        assert len(lagged.queue) == 2
        for name in ("mass", "yaw_inertia", "max_steer", "a_throttle", "a_brake", "c_drag", "jitter"):
            assert getattr(lagged, name) == getattr(base, name), name
    _, lag2 = _race(carla_like(noise=True, lag_ticks=2))
    _, by_hand = _race(_todays_car(True, lag_ticks=2))
    assert lag2 == by_hand
    assert carla_like(lag_ticks=0).lag_ticks == 0


@pytest.mark.parametrize("bad", (-1, 1.5, True))
def test_lag_ticks_must_be_an_int_at_least_0(bad):
    with pytest.raises(ValueError, match="lag_ticks"):
        carla_like(lag_ticks=bad)
