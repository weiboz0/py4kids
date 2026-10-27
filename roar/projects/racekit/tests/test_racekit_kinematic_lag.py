"""``KinematicCar(lag_ticks=N)``: the actuator-delay FIFO (plan roar-005 Phase A, taught in Unit 5).

``lag_ticks=0`` must be the lag-free car to the bit (every earlier pin rides on it); a lag of N
delays (throttle, steer, brake) by N control ticks through the same FIFO as ``DynamicCar``'s, with
the jitter drawn first (at command time), ``hand_brake``/``reverse`` immediate, and ``reset`` (a
respawn) refilling the queue with zero actions.
"""

from __future__ import annotations

import math
import random

import pytest
from racekit.cars import KinematicCar
from racekit.runner import run_race


def _old_advance(car, throttle, steer, brake, hand_brake, reverse, dt, substeps):
    """A frozen copy of ``KinematicCar.advance`` before roar-005 (the lag-free reference)."""
    if car.jitter != 0.0:
        gauss = car._rng.gauss
        throttle = min(1.0, max(0.0, throttle + gauss(0.0, car.jitter)))
        steer = min(1.0, max(-1.0, steer + gauss(0.0, car.jitter)))
    tan_delta = math.tan(-steer * car.max_steer)
    k_yaw = tan_delta / car.wheelbase
    drive = car.a_throttle * throttle * (-1.0 if reverse >= 0.5 else 1.0)
    braking = car.a_brake * max(brake, 1.0 if hand_brake >= 0.5 else 0.0)
    c = car.c_drag
    h = dt / substeps
    x, y, yaw, v = car.x, car.y, car.yaw, car.v
    cos, sin = math.cos, math.sin

    def accel(speed):
        a = drive - c * speed * abs(speed)
        if speed > 0.0:
            a -= braking
        elif speed < 0.0:
            a += braking
        return a

    for _ in range(substeps):
        v_old = v
        if car.integrator == "euler":
            x += h * v * cos(yaw)
            y += h * v * sin(yaw)
            yaw += h * v * k_yaw
            v += h * accel(v)
        else:
            k1x, k1y, k1w, k1v = v * cos(yaw), v * sin(yaw), v * k_yaw, accel(v)
            v2, w2 = v + 0.5 * h * k1v, yaw + 0.5 * h * k1w
            k2x, k2y, k2w, k2v = v2 * cos(w2), v2 * sin(w2), v2 * k_yaw, accel(v2)
            v3, w3 = v + 0.5 * h * k2v, yaw + 0.5 * h * k2w
            k3x, k3y, k3w, k3v = v3 * cos(w3), v3 * sin(w3), v3 * k_yaw, accel(v3)
            v4, w4 = v + h * k3v, yaw + h * k3w
            k4x, k4y, k4w, k4v = v4 * cos(w4), v4 * sin(w4), v4 * k_yaw, accel(v4)
            s = h / 6.0
            x += s * (k1x + 2.0 * k2x + 2.0 * k3x + k4x)
            y += s * (k1y + 2.0 * k2y + 2.0 * k3y + k4y)
            yaw += s * (k1w + 2.0 * k2w + 2.0 * k3w + k4w)
            v += s * (k1v + 2.0 * k2v + 2.0 * k3v + k4v)
        if braking > 0.0:
            crossed_zero = (v_old > 0.0 > v) or (v_old < 0.0 < v)
            held_at_rest = v_old == 0.0 and abs(drive) <= braking
            if crossed_zero or held_at_rest:
                v = 0.0
    car.x, car.y, car.v = x, y, v
    car.yaw = (yaw + math.pi) % (2.0 * math.pi) - math.pi


class _OldKinematicCar(KinematicCar):
    def advance(self, throttle, steer, brake, hand_brake, reverse, dt, substeps):
        _old_advance(self, throttle, steer, brake, hand_brake, reverse, dt, substeps)


def _fuzz_actions(seed: int, count: int = 400):
    rng = random.Random(seed)
    actions = []
    for _ in range(count):
        actions.append((
            rng.choice([0.0, 1.0, rng.random()]),
            rng.choice([-1.0, 1.0, rng.uniform(-1.0, 1.0)]),
            rng.choice([0.0, 0.0, 1.0, rng.random()]),
            1.0 if rng.random() < 0.05 else 0.0,  # hand_brake
            1.0 if rng.random() < 0.1 else 0.0,  # reverse
        ))
    return actions


def _drive(car, actions, seed=0, start_v=5.0):
    car.seed(seed)
    car.reset(0.0, 0.0, 0.3, start_v)
    states = []
    for throttle, steer, brake, hand_brake, reverse in actions:
        car.advance(throttle, steer, brake, hand_brake, reverse, 0.05, 10)
        states.append((car.x, car.y, car.yaw, car.v))
    return states


@pytest.mark.parametrize("jitter", [0.0, 0.05, 0.3])
@pytest.mark.parametrize("integrator", ["rk4", "euler"])
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_lag_zero_is_bit_identical_to_the_lag_free_car(jitter, integrator, seed):
    actions = _fuzz_actions(seed)
    new = _drive(KinematicCar(jitter=jitter, integrator=integrator, lag_ticks=0), actions, seed=seed)
    old = _drive(_OldKinematicCar(jitter=jitter, integrator=integrator), actions, seed=seed)
    assert new == old  # exact float equality, every tick
    default = _drive(KinematicCar(jitter=jitter, integrator=integrator), actions, seed=seed)
    assert default == old


@pytest.mark.parametrize("lag", [1, 2, 3])
def test_lag_k_first_changes_the_state_on_tick_k_plus_1(lag):
    car = KinematicCar(lag_ticks=lag)
    rest = KinematicCar()
    car.reset(0.0, 0.0, 0.0, 0.0)
    rest.reset(0.0, 0.0, 0.0, 0.0)
    # tick 1 commands full throttle and full steer; the car stays at rest (zero queued actions)
    # for the first `lag` ticks and moves on tick lag + 1
    for tick in range(1, lag + 3):
        car.advance(1.0, 0.5, 0.0, 0.0, 0.0, 0.05, 10)
        rest.advance(0.0, 0.0, 0.0, 0.0, 0.0, 0.05, 10)
        moved = (car.x, car.y, car.yaw, car.v) != (rest.x, rest.y, rest.yaw, rest.v)
        assert moved == (tick >= lag + 1), (tick, car.v)


@pytest.mark.parametrize("lag", [1, 2, 4])
def test_lag_k_equals_the_lag_free_car_fed_the_delayed_actions(lag):
    actions = _fuzz_actions(7)
    actions = [(t, s, b, 0.0, 0.0) for t, s, b, _, _ in actions]  # hand_brake/reverse act immediately
    lagged = _drive(KinematicCar(lag_ticks=lag), actions)
    delayed = [(0.0, 0.0, 0.0, 0.0, 0.0)] * lag + actions[:-lag]
    assert lagged == _drive(KinematicCar(), delayed)


def test_hand_brake_and_reverse_act_immediately():
    lagged, free = KinematicCar(lag_ticks=3), KinematicCar()
    for car in (lagged, free):
        car.reset(0.0, 0.0, 0.0, 10.0)
    for car in (lagged, free):  # coast with the hand brake: no queued action is involved
        car.advance(0.0, 0.0, 0.0, 1.0, 0.0, 0.05, 10)
    assert lagged.v == free.v < 10.0
    for car in (lagged, free):
        car.reset(0.0, 0.0, 0.0, 0.0)
    for _ in range(3):  # queue three forward full-throttle commands (the lagged car has not moved)
        lagged.advance(1.0, 0.0, 0.0, 0.0, 0.0, 0.05, 10)
    assert lagged.v == 0.0
    lagged.advance(0.0, 0.0, 0.0, 0.0, 1.0, 0.05, 10)  # the first one acts, reversed by this tick's flag
    free.advance(1.0, 0.0, 0.0, 0.0, 1.0, 0.05, 10)
    assert lagged.v == free.v < 0.0


def test_jitter_is_drawn_first_then_queued():
    """The jitter draw order is unchanged (throttle then steer, every tick, at command time) and
    the jittered action is what the FIFO delays."""
    sigma, lag = 0.2, 2
    actions = [(t, s, b) for t, s, b, _, _ in _fuzz_actions(3, 200)]
    stream = random.Random(9)
    jittered = []
    for throttle, steer, brake in actions:
        jt = min(1.0, max(0.0, throttle + stream.gauss(0.0, sigma)))
        js = min(1.0, max(-1.0, steer + stream.gauss(0.0, sigma)))
        jittered.append((jt, js, brake))
    car = KinematicCar(jitter=sigma, lag_ticks=lag)
    car.seed(9)
    car.reset(0.0, 0.0, 0.0, 8.0)
    reference = KinematicCar()
    reference.reset(0.0, 0.0, 0.0, 8.0)
    applied = [(0.0, 0.0, 0.0)] * lag + jittered[:-lag]
    for command, action in zip(actions, applied):
        car.advance(*command, 0.0, 0.0, 0.05, 10)
        reference.advance(*action, 0.0, 0.0, 0.05, 10)
        assert (car.x, car.y, car.yaw, car.v) == (reference.x, reference.y, reference.yaw, reference.v)


def test_reset_refills_the_queue_with_zero_actions():
    car = KinematicCar(lag_ticks=2)
    assert list(car.queue) == [(0.0, 0.0, 0.0)] * 2
    car.reset(0.0, 0.0, 0.0, 0.0)
    car.advance(1.0, 0.3, 0.0, 0.0, 0.0, 0.05, 10)
    car.advance(0.5, -0.3, 0.2, 0.0, 0.0, 0.05, 10)
    assert list(car.queue) == [(1.0, 0.3, 0.0), (0.5, -0.3, 0.2)]
    car.reset(5.0, 5.0, 1.0, 0.0)
    assert list(car.queue) == [(0.0, 0.0, 0.0)] * 2
    car.advance(1.0, 0.0, 0.0, 0.0, 0.0, 0.05, 10)  # the discarded commands never act
    assert (car.x, car.y, car.v) == (5.0, 5.0, 0.0)
    assert len(KinematicCar().queue) == 0


class _RecordingCar(KinematicCar):
    """Records the queue just before and just after every reset (the race start and respawns)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resets = []

    def reset(self, x, y, yaw, v=0.0):
        before = list(self.queue)
        super().reset(x, y, yaw, v)
        self.resets.append((before, list(self.queue)))


class _IntoTheWall:
    """Full throttle, a steady right turn (a radius of about 20 m): it leaves the track within seconds, again and again."""

    def __init__(self, waypoints, vehicle, *sensors):
        self.vehicle = vehicle

    async def initialize(self):
        pass

    async def step(self):
        await self.vehicle.apply_action({"throttle": 1.0, "steer": 0.2, "brake": 0.0, "hand_brake": 0.0,
                                         "reverse": 0, "target_gear": 0})


def test_a_respawn_mid_race_drains_the_queue():
    car = _RecordingCar(lag_ticks=2)
    result = run_race(_IntoTheWall, "oval", car=car, max_seconds=20.0)
    assert result.collisions >= 2, result.collisions
    assert len(car.resets) == 1 + result.collisions  # the race start, then one per respawn
    for before, after in car.resets[1:]:
        assert before == [(1.0, 0.2, 0.0)] * 2  # the commands queued when it crashed ...
        assert after == [(0.0, 0.0, 0.0)] * 2  # ... are discarded by the respawn


@pytest.mark.parametrize("bad", [-1, 1.5, True, -0.5])
def test_bad_lag_ticks_raises(bad):
    with pytest.raises(ValueError):
        KinematicCar(lag_ticks=bad)


def test_lag_ticks_accepts_an_integral_value():
    assert KinematicCar(lag_ticks=2.0).lag_ticks == 2
    assert KinematicCar().lag_ticks == 0
