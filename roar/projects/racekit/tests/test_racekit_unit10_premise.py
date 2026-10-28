"""The Unit 10 gates (plan roar-009 U10.1-U10.8): model predictive control.

The races run in the session's shared parallel pool (``_mpc_premise.py``, ``_premise.race_all``):
16 jobs, 76 races (65 of them MPC), all on ``carla_like(noise=True)``, race seeds 0-4 unless a job
says otherwise, capped at 450 s on a ``test-circuit`` track and 900 s on ``monza-like``. The lines
are solved once per session (the ``line_controls`` fixture). The pursuit sides of U10.2 and U10.5
are roar-008's races, read from the ``line_premise`` fixture, not re-raced. Every MPC race runs the
variant ``MPC_BUDGET_MS = None`` (no wall clock in a gate race), except U10.7's
``MPC_BUDGET_MS = 0.0`` races. U10.1 and the non-finite test are race-free.

Tolerances: medians within ±2 ticks (±0.10 s), the plan's one tolerance. A race is *clean* when it
finishes with 0 collisions and its max cross-track error from **its own line** on driving rows is
at most 2 m; an unclean cell is asserted only "not clean", never a collision count. The equivalence
is asserted to the tick: the same total time and byte-identical telemetry. The pins come from the
probes (``r2``-``r8``, ``c1``) and were confirmed by the Phase A re-run; a miss means stop, amend
and re-gate, never a silent re-pin.
"""

from __future__ import annotations

import ast
import asyncio
import math
import sys

import numpy as np
import pytest
from _line_premise import BASE, CHECKPOINT, MONZA, TRAINING, U9_REFERENCE, line_key
from _mpc_premise import (
    LAG0,
    SEED1,
    SEED4,
    U10_AS_PURSUIT,
    budget0_key,
    is_mpc_job,
    mpc_key,
    mpc_premise_jobs,
    pursuit_key,
)
from conftest import RACEKIT
from racekit.check_submission import check_submission
from racekit.measure import noise_aware_better
from racekit.tracks import load_track

TICKS_2 = 0.10 + 1e-9  # s: the plan's tolerance on a median, two ticks
CLEAN_ERROR = 2.0
AGENTS = RACEKIT / "agents"
U10_2_ERROR = 1.3  # m: U10.2's limit on MPC's max line error at f 0.54


def _clean(outcome) -> bool:
    return outcome.finished and outcome.collisions == 0 and outcome.line_error <= CLEAN_ERROR


def _all_clean(outcomes) -> bool:
    return len(outcomes) == 5 and all(_clean(o) for o in outcomes)


def _times(outcomes):
    return [o.total_time for o in outcomes]


def _median(outcomes) -> float:
    return float(np.median(_times(outcomes)))


def _assert_clean_row(outcomes, median):
    assert _all_clean(outcomes), outcomes
    assert _median(outcomes) == pytest.approx(median, abs=TICKS_2), outcomes


def _assert_none_clean(outcomes):
    assert len(outcomes) == 5 and not any(_clean(o) for o in outcomes), outcomes


def _assert_not_all_clean(outcomes):
    assert len(outcomes) == 5 and not _all_clean(outcomes), outcomes


def _module_constant(name, constant):
    tree = ast.parse((AGENTS / name).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == constant for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"{constant} not in {name}")


@pytest.fixture
def unit10():
    """``agents/unit-10.py`` loaded under the shim: (agent class, module)."""
    from racekit.runner import load_submission, shim_installed

    with shim_installed():
        agent_class, module_name = load_submission(AGENTS / "unit-10.py")
        try:
            yield agent_class, sys.modules[module_name]
        finally:
            sys.modules.pop(module_name, None)


def test_the_job_list_is_the_plans_76_races(line_controls):
    jobs = mpc_premise_jobs(line_controls)
    assert len(jobs) == 16
    assert sum(len(job.seeds) for job in jobs.values()) == 76
    assert sum(len(job.seeds) for job in jobs.values() if is_mpc_job(job)) == 65
    assert all(job.car == "carla" and job.laps is None for job in jobs.values())
    for key, job in jobs.items():
        assert job.max_seconds == (900.0 if job.track == MONZA else 450.0), key
        constants = dict(job.constants)
        if is_mpc_job(job):
            budget = 0.0 if key.startswith("mpc-budget0-") else None
            assert "MPC_BUDGET_MS" in constants and constants["MPC_BUDGET_MS"] == budget, key
        if job.track == BASE:
            assert constants.get("MU_G") is None and constants.get("LINE_CONTROL") is None, key
        else:
            assert constants["LINE_CONTROL"] == line_controls[(job.track, "global")], key
    assert TRAINING == ("test-circuit", "test-circuit-seed1", "test-circuit-seed2", "test-circuit-seed3",
                        "test-circuit-seed4")
    assert CHECKPOINT == "test-circuit-seed2026" and MONZA == "monza-like"


def test_the_agent_ships_the_plans_constants():
    expected = {"STEERING": "mpc", "MPC_HORIZON": 40, "MPC_Q_E": 0.3, "MPC_Q_PSI": 20.0, "MPC_R_DU": 1000.0,
                "MPC_LAG": 1, "MPC_BUDGET_MS": 5.0, "MPC_MIN_HORIZON": 10, "MU_FRACTION": 0.58}
    for constant, value in expected.items():
        assert _module_constant("unit-10.py", constant) == value, constant
    # everything Unit 9 planned with is Unit 9's
    for constant in ("MU_G", "LINE_CONTROL", "LINE_STEP", "MAX_STEER", "A_DEC", "A_ACC", "PP_K"):
        source = (AGENTS / "unit-10.py").read_text(encoding="utf-8")
        assert f"\n{constant} = " in source, constant
    assert _module_constant("unit-10.py", "MU_G") == _module_constant("unit-09.py", "MU_G")
    assert _module_constant("unit-10.py", "LINE_CONTROL") == _module_constant("unit-09.py", "LINE_CONTROL")


# --- U10.1: the solve (race-free) -------------------------------------------------------------------------


def _loop_build(e, psi, a, kappa):
    """G and h built one tick at a time: x_{t+1} = A_t x_t + b_t u_t + c_t."""
    m = len(a)
    G = np.zeros((2 * m, m))
    h = np.zeros(2 * m)
    x = np.array([e, psi])
    cols = np.zeros((2, m))  # the effect of each u so far on the current state
    for t in range(m):
        A = np.array([[1.0, a[t]], [0.0, 1.0]])
        x = A @ x + np.array([0.0, -a[t] * kappa[t]])
        cols = A @ cols
        cols[:, t] = (0.0, a[t])
        G[2 * t:2 * t + 2] = cols
        h[2 * t:2 * t + 2] = x
    return G, h


@pytest.mark.parametrize("m", (39, 20, 10))
def test_u10_1_the_closed_form_equals_the_tick_by_tick_build(unit10, m):
    _, module = unit10
    rng = np.random.default_rng(1000 + m)
    a = 0.05 * rng.uniform(1.0, 45.0, m)
    kappa = rng.uniform(-0.07, 0.07, m)
    e, psi = rng.uniform(-2.0, 2.0), rng.uniform(-0.3, 0.3)
    G, h = module.stack_horizon(e, psi, a, kappa)
    G_loop, h_loop = _loop_build(e, psi, a, kappa)
    assert np.allclose(G, G_loop, rtol=1e-12, atol=1e-12)
    assert np.allclose(h, h_loop, rtol=1e-12, atol=1e-12)
    # and x = G u + h is the model rolled forward
    u = rng.uniform(-0.1, 0.1, m)
    x = G @ u + h
    ee, pp = e, psi
    for t in range(m):
        ee, pp = ee + a[t] * pp, pp + a[t] * (u[t] - kappa[t])
        assert x[2 * t] == pytest.approx(ee, abs=1e-12) and x[2 * t + 1] == pytest.approx(pp, abs=1e-12)


def test_u10_1_on_the_tightest_corner_least_squares_is_within_2_percent_of_scipy(unit10):
    from scipy.optimize import minimize

    agent_class, module = unit10
    track = load_track(BASE)
    agent = agent_class(track.waypoints, None)
    kap = np.array(agent.curvature)
    seg = np.array(agent.segment_length)
    assert abs(kap).max() == pytest.approx(0.0658, abs=5e-5)
    # c1's corner: 20 waypoints before the tightest point, v 18 m/s, e0 0.8 m, psi0 0.05, u_last 0
    i0 = int(np.argmax(np.abs(kap))) - 20
    dt, n, v = 0.05, 40, 18.0
    s = np.cumsum(np.r_[0.0, seg[i0:i0 + 200]])
    kref = np.interp(v * dt * np.arange(1, n + 1), s[:-1], kap[i0:i0 + 200])
    x0, u_last = (0.8, 0.05), 0.0
    q_e, q_psi, r = module.MPC_Q_E, module.MPC_Q_PSI, module.MPC_R_DU

    def cost(u):  # the nonlinear path-frame model
        e, p = x0
        total = 0.0
        for k in range(n):
            e, p = e + dt * v * math.sin(p), p + dt * v * (u[k] - kref[k] * math.cos(p) / (1.0 - kref[k] * e))
            total += q_e * e * e + q_psi * p * p
        return total + r * float(np.sum(np.diff(np.r_[u_last, u]) ** 2))

    G, h = module.stack_horizon(x0[0], x0[1], np.full(n, dt * v), kref)
    u_ls = module.least_squares_plan(G, h, u_last)
    u_max = math.tan(module.MAX_STEER) / module.WHEELBASE
    result = minimize(cost, np.zeros(n), method="SLSQP", bounds=[(-u_max, u_max)] * n,
                      options={"maxiter": 500, "ftol": 1e-12})
    assert result.success, result
    assert cost(u_ls) <= 1.02 * result.fun, (cost(u_ls), result.fun)
    assert np.abs(u_ls - result.x).max() <= 1e-3


# --- U10.2: the same f ------------------------------------------------------------------------------------


def test_u10_2_at_the_same_f_neither_is_noise_aware_better(mpc_premise, line_premise):
    mpc = mpc_premise[mpc_key(BASE, 0.54)]
    pursuit = line_premise[U9_REFERENCE]
    assert _all_clean(mpc) and max(o.line_error for o in mpc) <= U10_2_ERROR, mpc
    assert mpc[0].total_time == pytest.approx(279.65, abs=TICKS_2)  # the probe's seed 0
    assert _all_clean(pursuit)
    assert not noise_aware_better(_times(mpc), _times(pursuit))
    assert not noise_aware_better(_times(pursuit), _times(mpc))


# --- U10.3: the hook --------------------------------------------------------------------------------------


def test_u10_3_at_0_58_pursuit_crashes_on_seed4_and_mpc_is_clean(mpc_premise):
    _assert_none_clean(mpc_premise[pursuit_key(SEED4, 0.58)])
    _assert_clean_row(mpc_premise[mpc_key(SEED4, 0.58)], 271.10)


# --- U10.4: the edge --------------------------------------------------------------------------------------


def test_u10_4_mpc_is_clean_on_the_family_at_0_60(mpc_premise):
    for track, median in zip(TRAINING, (272.40, 269.40, 268.80, 268.75, 268.85)):
        _assert_clean_row(mpc_premise[mpc_key(track, 0.6)], median)


def test_u10_4_mpc_is_not_clean_on_every_seed1_race_at_0_62(mpc_premise):
    _assert_not_all_clean(mpc_premise[mpc_key(SEED1, 0.62)])


# --- U10.5: the transfer ----------------------------------------------------------------------------------


def test_u10_5_the_frozen_0_58_transfers_and_beats_unit_9(mpc_premise, line_premise):
    mpc = mpc_premise[mpc_key(CHECKPOINT, 0.58)]
    pursuit = line_premise[line_key(CHECKPOINT, 0.54)]
    _assert_clean_row(mpc, 276.85)
    assert _median(pursuit) == pytest.approx(282.05, abs=TICKS_2)
    assert noise_aware_better(_times(mpc), _times(pursuit))


# --- U10.6: the lag ---------------------------------------------------------------------------------------


def test_u10_6_without_the_lag_mpc_is_not_clean_at_0_60(mpc_premise):
    _assert_none_clean(mpc_premise[LAG0])


# --- U10.7: the over-budget policy and the budget ---------------------------------------------------------


@pytest.mark.parametrize("track, median", ((SEED4, 271.55), (CHECKPOINT, 277.30)))
def test_u10_7_every_tick_over_budget_shortens_the_horizon_and_stays_clean(mpc_premise, track, median):
    outcomes = mpc_premise[budget0_key(track)]
    _assert_clean_row(outcomes, median)
    for outcome in outcomes:
        # one mpc() call per agent step, one step per driving telemetry row (warm-up included)
        assert outcome.steps == outcome.driving_rows
        assert outcome.over_budget == outcome.steps and outcome.fallbacks == 0, outcome
        assert outcome.horizon == 10
        assert outcome.horizons == ((40, 1), (20, 1), (10, outcome.steps - 2)), outcome.horizons


def test_u10_7_without_timing_the_horizon_stays_40(mpc_premise):
    for outcome in mpc_premise[mpc_key(CHECKPOINT, 0.58)]:
        assert outcome.over_budget == 0 and outcome.fallbacks == 0 and outcome.horizon == 40
        assert outcome.horizons == ((40, outcome.steps),)


def test_u10_7_as_pursuit_unit_10_races_exactly_like_unit_9(mpc_premise, line_premise):
    (first,) = mpc_premise[U10_AS_PURSUIT]
    second = mpc_premise[pursuit_key(SEED4, 0.58)][0]
    assert first.total_time == second.total_time and first.collisions == second.collisions
    assert first.digest == second.digest  # identical telemetry, to the tick
    assert first.horizons == () and first.over_budget == 0
    # ... and like roar-008's race of agents/unit-09.py from its file (the same race, seed 0)
    assert line_premise[line_key(SEED4, 0.58)][0].digest == first.digest


class _Sensor:
    def __init__(self, value):
        self.value = np.asarray(value, dtype=float)

    def get_last_gym_observation(self):
        return self.value


class _Vehicle:
    def __init__(self):
        self.actions = []

    async def apply_action(self, action):
        self.actions.append(action)


def test_u10_7_a_non_finite_plan_applies_the_shifted_last_finite_plan(unit10, monkeypatch):
    agent_class, module = unit10
    monkeypatch.setattr(module, "MPC_BUDGET_MS", None)
    track = load_track(BASE)
    x, y, yaw = track.start_pose()
    vehicle = _Vehicle()
    agent = agent_class(track.waypoints, vehicle, None, _Sensor((x, y, 0.0)),
                        _Sensor((15.0 * math.cos(yaw), 15.0 * math.sin(yaw), 0.0)), _Sensor((0.0, 0.0, yaw)))

    def no_pursuit(*args, **kwargs):
        raise AssertionError("pure pursuit is never used in MPC mode")

    monkeypatch.setattr(agent, "pursuit", no_pursuit)

    def applied_steer(u):
        return float(np.clip(-math.atan(module.WHEELBASE * u) / module.MAX_STEER, -1.0, 1.0))

    async def drive():
        await agent.initialize()
        await agent.step()
        plan = np.array(agent.plan)
        assert agent.fallbacks == 0 and agent.plan_used == 1 and np.all(np.isfinite(plan))
        assert vehicle.actions[-1]["steer"] == applied_steer(plan[0])
        agent.curvature = [math.nan] * len(agent.curvature)  # a non-finite curvature: the plan is NaN
        for used in (1, 2):
            await agent.step()
            assert agent.fallbacks == used
            assert agent.mpc_last == plan[used] and agent.mpc_queue == [plan[used]]
            assert vehicle.actions[-1]["steer"] == applied_steer(plan[used])
            assert math.isfinite(vehicle.actions[-1]["steer"])
        # once the plan is used up, the last command applied
        agent.plan_used = len(agent.plan)
        last = agent.mpc_last
        await agent.step()
        assert agent.fallbacks == 3 and agent.mpc_last == last
        assert vehicle.actions[-1]["steer"] == applied_steer(last)
        assert agent.over_budget == 0 and agent.horizon == 40

    asyncio.run(drive())


def test_u10_7_a_failed_solve_is_a_fallback_too(unit10, monkeypatch):
    agent_class, module = unit10
    monkeypatch.setattr(module, "MPC_BUDGET_MS", None)
    agent = agent_class(load_track(BASE).waypoints, None)
    agent.mpc_command(0.0, 15.0)
    plan = np.array(agent.plan)
    agent.profile = [math.nan] * len(agent.profile)  # a non-finite G: lstsq raises LinAlgError
    delta = agent.mpc_command(0.0, 15.0)
    assert agent.fallbacks == 1 and agent.mpc_last == plan[1]
    assert delta == math.atan(module.WHEELBASE * plan[1])


def test_u10_7_check_submission_passes_on_unit_10():
    # the routed suite runs tests serially, so this timing is outside any pool
    report = check_submission(AGENTS / "unit-10.py")
    assert report.ok, str(report)


# --- U10.8: monza-like ------------------------------------------------------------------------------------


def test_u10_8_on_monza_mpc_is_clean_at_0_64_and_pursuit_is_not(mpc_premise):
    _assert_clean_row(mpc_premise[mpc_key(MONZA, 0.64)], 468.75)
    _assert_not_all_clean(mpc_premise[pursuit_key(MONZA, 0.64)])
