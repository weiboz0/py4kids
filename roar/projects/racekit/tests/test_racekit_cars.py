"""The kinematic bicycle (plan roar-001 Phase D; design 013 §4.4)."""

from __future__ import annotations

import math

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
