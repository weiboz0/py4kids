"""The kinematic bicycle (plan roar-001 Phase D; design 013 §4.4)."""

from __future__ import annotations

import math
import random

import pytest
from racekit.cars import Car, KinematicCar


def _circle(car: KinematicCar, steer: float, speed: float, seconds: float, dt: float = 0.05):
    car.c_drag = 0.0  # hold the speed exactly (no throttle, no drag)
    car.reset(0.0, 0.0, 0.0, speed)
    points = []
    for _ in range(round(seconds / dt)):
        car.advance(0.0, steer, 0.0, 0.0, 0.0, dt, 10)
        points.append((car.x, car.y))
    return points


@pytest.mark.parametrize("steer", [-0.3, -0.1, 0.05, 0.2])
def test_steady_state_circle_radius_is_wheelbase_over_tan_delta(steer):
    car = KinematicCar()
    points = _circle(car, steer, 12.0, 30.0)
    delta = -steer * car.max_steer
    expected = car.wheelbase / math.tan(abs(delta))
    # the circle is centred on the start's normal, on the turning side
    centre_y = math.copysign(expected, delta)
    radii = [math.hypot(x, y - centre_y) for x, y in points]
    assert max(abs(radius - expected) for radius in radii) <= 0.01 * expected
    # a positive steer turns right (yaw decreasing), as in the official interface
    car.reset(0.0, 0.0, 0.0, 12.0)
    car.advance(0.0, steer, 0.0, 0.0, 0.0, 0.05, 10)
    assert (car.yaw < 0.0) == (steer > 0.0) and (car.y < 0.0) == (steer > 0.0)


def test_rk4_error_is_smaller_than_euler_at_equal_dt():
    errors = {}
    for integrator in ("rk4", "euler"):
        car = KinematicCar(integrator=integrator)
        steer = -0.15
        points = _circle(car, steer, 15.0, 10.0, dt=0.05)
        delta = -steer * car.max_steer
        radius = car.wheelbase / math.tan(delta)
        omega = 15.0 / radius
        t = 10.0
        exact = (radius * math.sin(omega * t), radius * (1.0 - math.cos(omega * t)))
        errors[integrator] = math.hypot(points[-1][0] - exact[0], points[-1][1] - exact[1])
    assert errors["rk4"] < errors["euler"] / 100.0


def test_drag_decelerates_monotonically_and_braking_stops_without_reversing():
    car = KinematicCar()
    car.reset(0.0, 0.0, 0.0, 40.0)
    speeds = [car.v]
    for _ in range(400):
        car.advance(0.0, 0.0, 0.0, 0.0, 0.0, 0.05, 10)
        speeds.append(car.v)
    assert all(later < earlier for earlier, later in zip(speeds, speeds[1:]))
    assert speeds[-1] > 0.0
    car.reset(0.0, 0.0, 0.0, 10.0)
    for _ in range(100):
        car.advance(0.0, 0.0, 1.0, 0.0, 0.0, 0.05, 10)
    assert car.v == 0.0


def test_throttle_accelerates_toward_a_drag_limited_speed_and_reverse_backs_up():
    car = KinematicCar()
    car.reset(0.0, 0.0, 0.0, 0.0)
    for _ in range(2000):
        car.advance(1.0, 0.0, 0.0, 0.0, 0.0, 0.05, 10)
    terminal = math.sqrt(car.a_throttle / car.c_drag)
    assert car.v == pytest.approx(terminal, rel=0.01)
    car.reset(0.0, 0.0, 0.0, 0.0)
    for _ in range(20):
        car.advance(0.5, 0.0, 0.0, 0.0, 1.0, 0.05, 10)
    assert car.v < 0.0 and car.x < 0.0


def test_kinematic_car_satisfies_the_car_protocol():
    car: Car = KinematicCar()
    for name in ("reset", "advance", "velocity"):
        assert callable(getattr(car, name))
    with pytest.raises(ValueError):
        KinematicCar(integrator="leapfrog")


# --- actuator jitter (plan roar-002 Phase 1) -----------------------------------------------------


class _Raising:
    """A stand-in random stream that fails on any draw."""

    def __getattr__(self, name):
        raise AssertionError(f"jitter = 0 must draw no random numbers (called {name})")


def _drive(car: KinematicCar, actions, seed: int = 0):
    car.seed(seed)
    car.reset(0.0, 0.0, 0.0, 10.0)
    states = []
    for throttle, steer, brake in actions:
        car.advance(throttle, steer, brake, 0.0, 0.0, 0.05, 10)
        states.append((car.x, car.y, car.yaw, car.v))
    return states


ACTIONS = [(0.6, 0.05, 0.0), (1.0, -1.0, 0.0), (0.0, 0.2, 0.7), (0.98, 0.99, 0.0)] * 25


def test_jitter_is_seeded_and_deterministic():
    first = _drive(KinematicCar(jitter=0.05), ACTIONS, seed=7)
    again = _drive(KinematicCar(jitter=0.05), ACTIONS, seed=7)
    other = _drive(KinematicCar(jitter=0.05), ACTIONS, seed=8)
    assert first == again and first != other
    clean = _drive(KinematicCar(), ACTIONS)
    assert first != clean
    car = KinematicCar(jitter=0.05)
    car.seed(7)
    restarted = _drive(car, ACTIONS, seed=7)  # seed() restarts the stream
    assert restarted == first


def test_jitter_draws_throttle_then_steer_clipped_and_never_touches_the_brake():
    """The protocol: per tick, throttle + gauss(0, σ) clipped to [0, 1], THEN steer + gauss(0, σ)
    clipped to [-1, 1]; the brake is passed through."""
    sigma = 0.3
    jittered = KinematicCar(jitter=sigma)
    reference = KinematicCar()
    stream = random.Random(11)
    jittered.seed(11)
    jittered.reset(0.0, 0.0, 0.0, 10.0)
    reference.reset(0.0, 0.0, 0.0, 10.0)
    for throttle, steer, brake in ACTIONS:
        expected_throttle = min(1.0, max(0.0, throttle + stream.gauss(0.0, sigma)))
        expected_steer = min(1.0, max(-1.0, steer + stream.gauss(0.0, sigma)))
        jittered.advance(throttle, steer, brake, 0.0, 0.0, 0.05, 10)
        reference.advance(expected_throttle, expected_steer, brake, 0.0, 0.0, 0.05, 10)
        assert (jittered.x, jittered.y, jittered.yaw, jittered.v) == (reference.x, reference.y, reference.yaw,
                                                                         reference.v)


def test_jitter_zero_draws_nothing_and_is_byte_identical():
    car = KinematicCar(jitter=0.0)
    car.seed(5)
    car._rng = _Raising()
    assert _drive_unseeded(car) == _drive_unseeded(KinematicCar())
    with pytest.raises(ValueError):
        KinematicCar(jitter=-0.1)
    with pytest.raises(ValueError):
        KinematicCar(jitter=float("nan"))


def _drive_unseeded(car: KinematicCar):
    car.reset(0.0, 0.0, 0.0, 10.0)
    states = []
    for throttle, steer, brake in ACTIONS:
        car.advance(throttle, steer, brake, 0.0, 0.0, 0.05, 10)
        states.append((car.x, car.y, car.yaw, car.v))
    return states
