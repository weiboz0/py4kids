"""The dynamic car's analytic checks (plan roar-004 G4.1; design 013 §7.1).

The thresholds are the plan's pins, measured on the immutable freeze of the prototype
(``dyn_af442a6f.py``); every spin check calls the car's own ``spun_out()``.
"""

from __future__ import annotations

import math
import random

import numpy as np
import pytest
from racekit import cars
from racekit.cars import SPIN_MIN_SPEED, Car, DynamicCar, KinematicCar, carla_like
from racekit.runner import run_race

G = 9.81
DT = 0.05


def _tick(car, throttle=0.0, steer=0.0, brake=0.0, reverse=0.0, dt=DT, substeps=10):
    car.advance(throttle, steer, brake, 0.0, reverse, dt, substeps)


def _accel_ratio(car, before, mu):
    """|Δv_world| / (dt · μg) over the last tick."""
    after = car.velocity()
    return math.hypot(after[0] - before[0], after[1] - before[1]) / DT / (mu * G)


def test_dynamic_car_satisfies_the_car_protocol_and_defaults():
    car: Car = DynamicCar()
    for name in ("reset", "advance", "velocity", "seed", "spun_out", "attach_track"):
        assert callable(getattr(car, name))
    assert (car.mass, car.yaw_inertia, car.lf, car.wheelbase) == (1845.0, 2900.0, 1.40, 2.875)
    assert car.max_steer == pytest.approx(math.radians(70.0))
    assert (car.a_throttle, car.a_brake, car.c_drag, car.mu, car.lag_ticks) == (6.0, 8.0, 4e-4, 1.0, 1)
    assert (car.v_kin_lo, car.v_kin_hi, SPIN_MIN_SPEED) == (1.0, 2.0, 5.0)
    assert car.spin_beta == pytest.approx(math.radians(25.0))
    with pytest.raises(ValueError):
        DynamicCar(mu=[1.0, 1.0])
    with pytest.raises(ValueError):
        DynamicCar(jitter=-0.1)


# --- the steady circle, longitudinal map and integrator order --------------------------------------


def test_steady_circle_radius_is_wheelbase_over_tan_delta():
    """8 m/s at steer 0.02: the steady radius v / r is within 3% of L / tan δ."""
    car = DynamicCar(lag_ticks=0, c_drag=0.0)
    car.reset(0.0, 0.0, 0.0, 8.0)
    car.delta = -0.02 * car.max_steer
    for _ in range(400):  # 20 s, holding 8 m/s with a little throttle
        _tick(car, throttle=max(0.0, 0.5 * (8.0 - car.v)), steer=0.02)
    radius = math.hypot(car.vx, car.vy) / abs(car.r)
    expected = car.wheelbase / math.tan(0.02 * car.max_steer)
    assert abs(radius - expected) <= 0.03 * expected
    assert car.r < 0.0  # a positive steer turns right


def test_straight_full_throttle_matches_the_longitudinal_map():
    """Below the traction limit, dv/dt = a_T − c·v|v| (analytic tanh solution) to 1e-3 m/s over 2 s."""
    car = DynamicCar(lag_ticks=0)
    v0 = 10.0
    car.reset(0.0, 0.0, 0.0, v0)
    a, c = car.a_throttle, car.c_drag
    terminal, rate = math.sqrt(a / c), math.sqrt(a * c)
    worst = 0.0
    for k in range(1, 41):
        _tick(car, throttle=1.0)
        exact = terminal * math.tanh(rate * k * DT + math.atanh(v0 / terminal))
        worst = max(worst, abs(car.v - exact))
        assert car.vy == 0.0 and car.r == 0.0
    assert worst <= 1e-3


def _manoeuvre(substeps: int):
    car = DynamicCar(lag_ticks=0)
    car.reset(0.0, 0.0, 0.0, 15.0)
    car.delta = -0.03 * car.max_steer  # the wheel starts at its target
    for _ in range(40):  # 2 s
        _tick(car, throttle=0.3, steer=0.03, substeps=substeps)
    return np.array([car.x, car.y, car.yaw, car.vx, car.vy, car.r])


def test_rk4_order_halving_the_substep_shrinks_the_error_by_at_least_12():
    cars._force_log = log = []
    try:
        reference = _manoeuvre(1280)
    finally:
        cars._force_log = None
    # no tyre saturated: |F_y| stays well below each axle's friction-circle limit
    assert max(max(abs(fyf) / fmf, abs(fyr) / fmr) for _, fyf, fmf, _, fyr, fmr in log) < 0.8
    errors = [np.max(np.abs(_manoeuvre(n) - reference)) for n in (2, 4, 8)]
    ratios = [errors[0] / errors[1], errors[1] / errors[2]]
    assert all(ratio >= 12.0 for ratio in ratios), (errors, ratios)


# --- the friction circle ---------------------------------------------------------------------------


def test_friction_circle_holds_at_every_stage_in_a_random_action_fuzz():
    """A regression guard (true by construction): √(F_x² + F_y²) ≤ μF_z + 1e-9 per axle."""
    rng = random.Random(2024)
    cars._force_log = log = []
    try:
        for _ in range(500):
            mu = rng.choice([0.78, 0.9, 1.0])
            car = DynamicCar(mu=mu, lag_ticks=rng.choice([0, 1, 2]))
            car.reset(0.0, 0.0, rng.uniform(-3.0, 3.0), rng.uniform(0.0, 45.0))
            car.vy, car.r = rng.uniform(-2.0, 2.0), rng.uniform(-1.0, 1.0)
            for _ in range(4):
                _tick(car, rng.uniform(0, 1), rng.uniform(-1, 1), rng.choice([0.0, rng.uniform(0, 1)]),
                      reverse=rng.choice([0.0, 0.0, 0.0, 1.0]))
    finally:
        cars._force_log = None
    assert len(log) > 500 * 4 * 10 * 4 * 0.5
    for fx_f, fy_f, fmax_f, fx_r, fy_r, fmax_r in log:
        assert math.hypot(fx_f, fy_f) <= fmax_f + 1e-9
        assert math.hypot(fx_r, fy_r) <= fmax_r + 1e-9


def test_per_tick_acceleration_stays_within_mu_g_over_a_clean_limit_lap(limit_laps):
    """A completed, clean test-circuit lap on the carla-like car at the Unit 7 combined grip (the
    fastest clean setting, near the grip limit): every tick above 5 m/s stays within 1.02 μg."""
    clean, _ = limit_laps
    result, ratios = clean
    assert result.finished and result.collisions == 0, result
    assert ratios.size > 1000
    assert float(ratios.max()) <= 1.02


def test_per_tick_acceleration_stays_within_mu_g_in_an_over_the_limit_run(limit_laps):
    """An over-the-limit run with respawns (a_lat 8 against μg ≈ 8–9.8): sliding, spinning and
    wall-hitting states stay within 1.02 μg too (probe max 0.992). It never completes a lap."""
    _, crashing = limit_laps
    result, ratios = crashing
    assert result.collisions > 0
    assert ratios.size > 500
    assert float(ratios.max()) <= 1.02


def _recorded_race(driver, seed, max_seconds):
    car = carla_like(noise=True)
    ratios = []
    advance = car.advance

    def recording(*args):
        vx0, vy0 = car.velocity()
        speed0 = abs(car.vx)
        advance(*args)
        vx1, vy1 = car.velocity()
        if speed0 > 5.0:
            ratios.append(math.hypot(vx1 - vx0, vy1 - vy0) / DT / (car.mu_now * G))

    car.advance = recording
    result = run_race(driver, "test-circuit", car=car, max_seconds=max_seconds, seed=seed, laps=1)
    return result, np.array(ratios)


@pytest.fixture(scope="module")
def limit_laps():
    from _premise import UNIT7_BEST_GLOBAL, UNIT7_COMBINED
    from drivers import pure_pursuit

    clean = _recorded_race(pure_pursuit(45.0, UNIT7_BEST_GLOBAL, UNIT7_COMBINED, 6.0, 150), 0, 300.0)
    crashing = _recorded_race(pure_pursuit(45.0, 8.0, None, 6.0, 150), 1, 150.0)
    return clean, crashing


# --- the brake stop --------------------------------------------------------------------------------


@pytest.mark.parametrize("v0", [0.005, 0.01, 0.03, 0.2, 1.0, 5.0])
def test_full_brake_stops_exactly_and_never_reverses(v0):
    car = DynamicCar()
    car.reset(0.0, 0.0, 0.0, v0)
    for _ in range(20):
        _tick(car, brake=1.0)
        assert car.vx >= 0.0
    assert car.v == 0.0 and car.vx == 0.0 and car.vy == 0.0


def test_throttle_against_the_brake_is_not_an_early_snap():
    """Full throttle and full brake from 0.05 m/s: the net 2 m/s² takes at least 3 substeps."""
    car = DynamicCar(lag_ticks=0)
    car.reset(0.0, 0.0, 0.0, 0.05)
    substeps = 0
    while car.v != 0.0:
        car.advance(1.0, 0.0, 1.0, 0.0, 0.0, DT / 10, 1)  # one substep per call
        substeps += 1
        assert substeps < 100
    assert substeps >= 3


def test_partial_throttle_against_full_brake_reaches_rest():
    car = DynamicCar()
    car.reset(0.0, 0.0, 0.0, 5.0)
    for _ in range(40):  # 2 s
        _tick(car, throttle=0.75, brake=1.0)
    assert car.v == 0.0


# --- low speed -------------------------------------------------------------------------------------

LOW_ACTIONS = [(1, 1.0, 0, 0), (1, 0.5, 0, 0), (0.3, 1.0, 0, 0), (0, 1.0, 1, 0), (0, 0, 1, 0), (0, 0.5, 1, 0),
               (0.5, -1.0, 0.3, 0), (1, 0, 1, 1), (1, 1.0, 1, 1), (0.5, 0, 1, 0)]


@pytest.mark.parametrize("lag", [0, 1])
@pytest.mark.parametrize("preset", [False, True], ids=["ramped-wheel", "settled-wheel"])
def test_low_speed_acceleration_stays_within_mu_g(lag, preset):
    """μ ∈ {0.78, 1}, nine starting speeds, the ten actions, 3 s each (probe worst 1.000)."""
    worst = 0.0
    for mu in (0.78, 1.0):
        for v0 in (0.0, 0.06, 0.4, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0):
            for throttle, steer, brake, reverse in LOW_ACTIONS:
                car = DynamicCar(mu=mu, lag_ticks=lag)
                car.reset(0.0, 0.0, 0.0, v0)
                if preset:
                    car.delta = -steer * car.max_steer
                for _ in range(60):
                    before = car.velocity()
                    _tick(car, throttle, steer, brake, reverse)
                    worst = max(worst, _accel_ratio(car, before, mu))
    assert worst <= 1.02


def test_lateral_state_fuzz_stays_within_mu_g():
    """3,000 seeded low-speed sliding states with random actions, 10 ticks each (probe 1.000)."""
    rng = random.Random(7)
    worst = 0.0
    for _ in range(3000):
        mu = rng.choice([0.78, 0.9, 1.0])
        vx, vy, r = rng.uniform(-0.5, 3.0), rng.uniform(-1.5, 1.5), rng.uniform(-4.0, 4.0)
        throttle, steer = rng.choice([0, 0.3, 1]), rng.uniform(-1, 1)
        brake, reverse = rng.choice([0, 0.5, 1]), rng.choice([0, 0, 1])
        car = DynamicCar(mu=mu, lag_ticks=0)
        car.reset(0.0, 0.0, rng.uniform(-3.0, 3.0), 0.0)
        car.vx, car.vy, car.r = vx, vy, r
        car.delta = -steer * car.max_steer
        for _ in range(10):
            before = car.velocity()
            _tick(car, throttle, steer, brake, reverse)
            worst = max(worst, _accel_ratio(car, before, mu))
    assert worst <= 1.02


def test_the_sol_round_4_counterexample_is_inside_the_bound():
    car = DynamicCar(mu=0.78, lag_ticks=0)
    car.reset(0.0, 0.0, 0.0, 0.0)
    car.vx, car.vy, car.r = 0.2, -0.49, -3.0
    car.delta = car.max_steer
    before = car.velocity()
    _tick(car, 0.0, -1.0, 1.0)
    assert _accel_ratio(car, before, 0.78) <= 1.0


@pytest.mark.parametrize("steer", [0.0, 0.5, 1.0])
def test_from_rest_the_car_never_backs_up_and_accelerates_monotonically(steer):
    car = DynamicCar()
    car.reset(0.0, 0.0, 0.0, 0.0)
    previous = 0.0
    for _ in range(80):  # 4 s at throttle 0.3
        _tick(car, throttle=0.3, steer=steer)
        assert car.vx >= 0.0
        if abs(car.vx) < 1.0:
            assert car.vx >= previous - 1e-12
        assert not car.spun_out()
        previous = car.vx


@pytest.mark.parametrize(("steer", "bound"), [(0.5, 0.1), (1.0, 0.4)])
def test_low_speed_sideslip_relaxes_to_the_kinematic_value(steer, bound):
    """While |vx| < 1 m/s and after 0.5 s, |vy − l_r·vx·tan δ / L| is within the relaxation-lag bound
    (probe 0.062 half lock, 0.308 full lock); the window must not be empty."""
    car = DynamicCar()
    car.reset(0.0, 0.0, 0.0, 0.0)
    window = []
    for k in range(80):
        _tick(car, throttle=0.3, steer=steer)
        if abs(car.vx) < 1.0 and k >= 10:
            window.append(abs(car.vy - car.lr * car.vx * math.tan(car.delta) / car.wheelbase))
    assert window, "the low-speed window is empty"
    assert max(window) <= bound


# --- lag and steering rate -------------------------------------------------------------------------


@pytest.mark.parametrize("lag", [0, 1, 2])
def test_a_throttle_step_first_changes_vx_on_tick_lag_plus_one(lag):
    stepped, coasting = DynamicCar(lag_ticks=lag), DynamicCar(lag_ticks=lag)
    for car in (stepped, coasting):
        car.reset(0.0, 0.0, 0.0, 10.0)
    first = None
    for tick in range(1, 6):
        _tick(stepped, throttle=1.0)
        _tick(coasting, throttle=0.0)
        if first is None and stepped.vx != coasting.vx:
            first = tick
    assert first == lag + 1


def test_the_steering_rate_limit_is_respected():
    car = DynamicCar(lag_ticks=0)
    car.reset(0.0, 0.0, 0.0, 10.0)
    per_tick = car.steer_rate * DT
    previous = car.delta
    reached = None
    for tick in range(1, 13):
        _tick(car, steer=-1.0 if tick <= 6 else 1.0)
        assert abs(car.delta - previous) <= per_tick + 1e-12
        if reached is None and car.delta == pytest.approx(car.max_steer):
            reached = tick
        previous = car.delta
    # 70° at 360°/s is 0.194 s: four ticks
    assert reached == 4


# --- spin-out --------------------------------------------------------------------------------------


def _spins(v0, script, car=None):
    car = car or DynamicCar()
    car.reset(0.0, 0.0, 0.0, v0)
    tripped = False
    for throttle, steer, brake, ticks in script:
        for _ in range(ticks):
            _tick(car, throttle, steer, brake)
            tripped |= car.spun_out()
    return tripped


def test_spin_out_trips_on_real_spins():
    assert _spins(40.0, [(0.0, 1.0, 1.0, 20)])  # 40 m/s, full lock and full brake for 1 s
    assert _spins(0.0, [(1.0, 1.0, 0.0, 80)])  # power oversteer: full throttle at full lock from rest


def test_spin_out_never_trips_on_legitimate_turns():
    assert not _spins(15.0, [(0.03, 0.0307, 0.0, 120)])  # a steady 15 m/s, 0.3 g circle (R ≈ 76 m, speed held)
    for v0 in (5.0, 6.0, 8.0, 10.0):  # full lock at throttle 0.3 for 4 s
        assert not _spins(v0, [(0.3, 1.0, 0.0, 80)]), v0
    # a held full lock or a half-lock L/R/L at 40 m/s understeers
    assert not _spins(40.0, [(0.0, 0.5, 0.0, 8), (0.0, -0.5, 0.0, 8), (0.0, 0.5, 0.0, 8)])


def test_spun_out_needs_speed_above_the_threshold():
    car = DynamicCar()
    car.reset(0.0, 0.0, 0.0, 0.0)
    car.vx, car.vy = 3.0, 3.0  # β = 45° but ‖v‖ = 4.24 m/s
    assert not car.spun_out()
    car.vx, car.vy = 4.0, 4.0  # 5.66 m/s
    assert car.spun_out()


# --- grip and noise --------------------------------------------------------------------------------


def test_a_per_section_car_without_a_track_raises():
    car = DynamicCar(mu=[0.9, 1.0, 0.8, 1.0, 0.95, 0.85])
    assert car.per_section
    with pytest.raises(RuntimeError, match="attach_track"):
        _tick(car, throttle=1.0)
    with pytest.raises(RuntimeError, match="attach_track"):
        _tick(carla_like(), throttle=1.0)
    assert not DynamicCar().per_section


def test_jitter_draws_throttle_then_steer_whenever_either_sigma_is_set():
    for jitter, steer_jitter in ((0.2, 0.0), (0.0, 0.05), (0.2, 0.05)):
        noisy, reference = DynamicCar(jitter=jitter, steer_jitter=steer_jitter), DynamicCar()
        noisy.seed(11)
        stream = random.Random(11)
        for car in (noisy, reference):
            car.reset(0.0, 0.0, 0.0, 10.0)
        for throttle, steer, brake in [(0.6, 0.05, 0.0), (1.0, -1.0, 0.0), (0.0, 0.2, 0.7)] * 10:
            expected_throttle = min(1.0, max(0.0, throttle + stream.gauss(0, jitter)))
            expected_steer = min(1.0, max(-1.0, steer + stream.gauss(0, steer_jitter)))
            _tick(noisy, throttle, steer, brake)
            _tick(reference, expected_throttle, expected_steer, brake)
            assert (noisy.x, noisy.y, noisy.yaw, noisy.vx, noisy.vy, noisy.r) == (
                reference.x, reference.y, reference.yaw, reference.vx, reference.vy, reference.r)


def test_no_jitter_draws_no_random_number(monkeypatch):
    class Raising:
        def __getattr__(self, name):
            raise AssertionError(f"no jitter, yet a random number was drawn ({name})")

    car = DynamicCar()
    car._rng = Raising()
    car.reset(0.0, 0.0, 0.0, 5.0)
    for _ in range(10):
        _tick(car, 0.5, 0.1)


def test_kinematic_car_is_unchanged_by_this_plan():
    """The default car stays the kinematic bicycle, with no dynamic-car attributes."""
    car = KinematicCar()
    assert not hasattr(car, "attach_track") and not hasattr(car, "spun_out")
