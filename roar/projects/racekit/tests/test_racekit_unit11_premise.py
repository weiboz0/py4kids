"""The Unit 11 gates (plan roar-010 U11.2-U11.9): robustness.

The races run in the session's shared parallel pool (``_robust_premise.py``, ``_premise.race_all``):
218 races on ``carla_like(noise=True, perturb=k)`` (car ``k`` of the perturbed family; training cars
k = 0-23, held-out cars k = 24-47, race seed k mod 5), plus the lag-2 and the unperturbed car (race
seed 0), all capped at 700 s, every one with ``MPC_BUDGET_MS = None`` (no wall clock in a gate race).
U11.7a and the constants are race-free (scripted sensors). U11.1 (the family) is
``test_racekit_perturb.py``.

A race is *clean* when it finishes with 0 collisions and its max error from **its own line** on
driving rows is at most 2 m. A race not finished counts at the 700 s cap in a mean. The equivalence
is asserted to the tick (byte-identical telemetry). The pins come from the probes (q7-q11) and were
confirmed by the Phase A re-run; a miss means stop, amend and re-gate, never a silent re-pin.

U11.3's remainder is systematically *shorter* than the fresh twin (remainder - twin < 0, by 0.4-0.7 s
in the probe): the speed loop's PI integral survives the restart (``_robust_premise``'s docstring has
the measurement). The gate's tolerance is 1.0 s, and the lesson says "t + 1 s, to within a second".
"""

from __future__ import annotations

import ast
import asyncio
import math
import sys

import numpy as np
import pytest
from _robust_premise import (
    CAP,
    EQUIVALENCE_CARS,
    FALLBACK_SCALE,
    FRACTIONS,
    HELD_OUT_CARS,
    LAG2_U10,
    LAG2_U11,
    NOMINAL_U10,
    NOMINAL_U11,
    TRAINING_CARS,
    TRANSFER_CARS,
    TWIN_CARS,
    robust_premise_jobs,
    transfer_key,
    twin_key,
    u10_key,
    u11_key,
    warn_key,
)
from conftest import RACEKIT
from racekit.check_submission import check_submission
from racekit.tracks import load_track

CLEAN_ERROR = 2.0
AGENTS = RACEKIT / "agents"
HOLD_S = 1.0  # the respawn hold
U11_3_TOLERANCE = 1.0  # s


def _clean(outcome) -> bool:
    return outcome.finished and outcome.collisions == 0 and outcome.line_error <= CLEAN_ERROR


def _capped(outcome) -> float:
    return outcome.total_time if outcome.finished else CAP


def _one(premise, key):
    (outcome,) = premise[key]
    return outcome


def _row(premise, key_of, cars):
    return {k: _one(premise, key_of(k)) for k in cars}


def _mean(outcomes) -> float:
    return float(np.mean([_capped(o) for o in outcomes]))


def _assigned(name, constant):
    tree = ast.parse((AGENTS / name).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == constant for t in node.targets):
            return node.value
    raise AssertionError(f"{constant} not in {name}")


def _module_constant(name, constant):
    return ast.literal_eval(_assigned(name, constant))


def test_the_job_list_is_the_plans_218_races(line_controls):
    jobs = robust_premise_jobs(line_controls)
    assert sum(len(job.seeds) for job in jobs.values()) == len(jobs) == 218
    for key, job in jobs.items():
        assert job.max_seconds == CAP and dict(job.constants)["MPC_BUDGET_MS"] is None, key
        if job.perturb is not None and job.track == "test-circuit":
            assert job.seeds == (job.perturb % 5,), key
        else:
            assert job.seeds == (0,), key
    assert TRAINING_CARS == tuple(range(24)) and HELD_OUT_CARS == tuple(range(24, 48))
    assert jobs[LAG2_U10].lag_ticks == jobs[LAG2_U11].lag_ticks == 2
    assert dict(jobs[twin_key(8)].constants)["MU_FRACTION"] == 0.58 * 0.86


def test_the_agent_ships_the_plans_constants():
    expected = {"STEERING": "mpc", "MU_FRACTION": 0.54, "MPC_BUDGET_MS": 5.0, "MPC_LAG": 1,
                "RESPAWN_IMPULSE": 100.0, "REFRACTORY_TICKS": 40, "FALLBACK_STEERING": "pursuit",
                "FALLBACK_SCALE": 0.86, "WARN_BETA_DEG": 8.0, "WARN_ERROR_M": 1.6, "WARN_MIN_SPEED": 5.0,
                "WARN_FALLBACK": False}
    for constant, value in expected.items():
        assert _module_constant("unit-11.py", constant) == value, constant
    assert FALLBACK_SCALE == _module_constant("unit-11.py", "FALLBACK_SCALE")
    # everything else Unit 10 planned with is Unit 10's
    for constant in ("MU_G", "LINE_CONTROL", "MAX_STEER", "A_DEC", "A_ACC", "PP_K", "MPC_HORIZON", "MPC_Q_E",
                     "MPC_Q_PSI", "MPC_R_DU", "MPC_MIN_HORIZON"):
        assert ast.dump(_assigned("unit-11.py", constant)) == ast.dump(_assigned("unit-10.py", constant)), constant


# --- U11.2: the hook --------------------------------------------------------------------------------------


def test_u11_2_unit_10_crashes_and_crash_loops_on_the_training_family(robust_premise):
    row = _row(robust_premise, lambda k: u10_key(0.58, k), TRAINING_CARS)
    assert any(not _clean(o) for o in row.values()), row
    loops = [k for k, o in row.items() if o.collisions >= 3 and not o.finished]
    assert loops, row


# --- U11.3: respawn economics -----------------------------------------------------------------------------


def test_u11_3_a_restart_is_a_fresh_race(robust_premise):
    races = _row(robust_premise, lambda k: u11_key(0.58, k), TRAINING_CARS + HELD_OUT_CARS)
    once = tuple(k for k, o in races.items() if o.collisions == 1 and o.finished)
    assert len(once) >= 3, once
    assert once == TWIN_CARS, once  # every qualifying race has its fresh twin
    for k in once:
        crashed, twin = races[k], _one(robust_premise, twin_key(k))
        assert twin.finished and twin.collisions == 0, (k, twin)
        remainder = crashed.total_time - crashed.respawn_times[0] - HOLD_S
        assert abs(remainder - twin.total_time) <= U11_3_TOLERANCE, (k, remainder, twin.total_time)


# --- U11.4: the robust fraction ---------------------------------------------------------------------------


def test_u11_4_0_54_is_the_robust_fraction(robust_premise):
    rows = {value: _row(robust_premise, lambda k, v=value: u10_key(v, k), TRAINING_CARS) for value in FRACTIONS}
    assert not all(_clean(o) for o in rows[0.56].values()), rows[0.56]
    assert all(_clean(o) for o in rows[0.54].values()), rows[0.54]
    means = {value: _mean(row.values()) for value, row in rows.items()}
    assert min(means, key=means.get) == 0.54, means


# --- U11.5: the fallback ----------------------------------------------------------------------------------


def test_u11_5_with_the_fallback_every_race_finishes_with_at_most_one_collision(robust_premise):
    races = _row(robust_premise, lambda k: u11_key(0.58, k), TRAINING_CARS + HELD_OUT_CARS)
    for k, o in races.items():
        assert o.finished and o.collisions <= 1, (k, o)
        assert o.respawns == o.collisions, (k, o)  # one respawn handled per collision


def test_u11_5_on_the_lag_2_car_only_the_fallback_finishes(robust_premise):
    unit10, unit11 = _one(robust_premise, LAG2_U10), _one(robust_premise, LAG2_U11)
    assert not unit10.finished, unit10
    assert unit11.finished and unit11.collisions == 1 and unit11.mode == "fallback", unit11


# --- U11.6: the gate (design §6) --------------------------------------------------------------------------


def test_u11_6_unit_11_is_clean_on_every_held_out_perturbation(robust_premise):
    row = _row(robust_premise, lambda k: u11_key(0.54, k), HELD_OUT_CARS)
    assert all(_clean(o) for o in row.values()), {k: o for k, o in row.items() if not _clean(o)}


# --- U11.7: equivalence -----------------------------------------------------------------------------------


def test_u11_7_with_no_respawn_unit_11_races_exactly_like_unit_10(robust_premise):
    pairs = [(NOMINAL_U11, NOMINAL_U10)] + [(u11_key(0.54, k), u10_key(0.54, k)) for k in EQUIVALENCE_CARS]
    for eleven, ten in pairs:
        a, b = _one(robust_premise, eleven), _one(robust_premise, ten)
        assert a.collisions == 0 and a.respawns == 0 and a.mode == "primary", (eleven, a)
        assert a.total_time == b.total_time and a.digest == b.digest, (eleven, a, b)


# --- U11.7a: the handler, on scripted sensors -------------------------------------------------------------


class _Sensor:
    def __init__(self, value):
        self.set(value)

    def set(self, value):
        self.value = np.asarray(value, dtype=float)

    def get_last_gym_observation(self):
        return self.value


class _Vehicle:
    def __init__(self):
        self.actions = []

    async def apply_action(self, action):
        self.actions.append(action)


def _load(name, **constants):
    """A fresh load of ``agents/<name>`` (its own module), with module constants changed."""
    from racekit.runner import load_submission, shim_installed

    with shim_installed():
        agent_class, module_name = load_submission(AGENTS / name)
    module = sys.modules.pop(module_name)
    for constant, value in constants.items():
        setattr(module, constant, value)
    return agent_class, module


def _rig(agent_class, track, location, yaw, velocity, impulse=(0.0, 0.0, 0.0)):
    vehicle = _Vehicle()
    sensors = {"location": _Sensor(location), "rpy": _Sensor((0.0, 0.0, yaw)), "velocity": _Sensor(velocity),
               "collision": _Sensor(impulse)}
    agent = agent_class(track.waypoints, vehicle, None, sensors["location"], sensors["velocity"], sensors["rpy"],
                        None, sensors["collision"])
    return agent, vehicle, sensors


def _line_pose(agent, index, offset):
    """A point ``offset`` m left of the agent's line at ``index``, and the line's heading there."""
    count = len(agent.xs)
    j = (index + 1) % count
    heading = math.atan2(agent.ys[j] - agent.ys[index], agent.xs[j] - agent.xs[index])
    return (agent.xs[index] - offset * math.sin(heading), agent.ys[index] + offset * math.cos(heading), 0.0), heading


def test_u11_7a_a_warning_is_counted_and_changes_nothing():
    track = load_track("test-circuit")
    eleven, _ = _load("unit-11.py", MPC_BUDGET_MS=None)
    ten, _ = _load("unit-10.py", MPC_BUDGET_MS=None, MU_FRACTION=0.54)
    probe, _, _ = _rig(eleven, track, (0.0, 0.0, 0.0), 0.0, (0.0, 0.0, 0.0))
    location, heading = _line_pose(probe, 400, 2.0)
    slip = heading + math.radians(10.0)  # the velocity 10 deg left of the heading: beta = 10 deg
    velocity = (20.0 * math.cos(slip), 20.0 * math.sin(slip), 0.0)
    a, a_vehicle, _ = _rig(eleven, track, location, heading, velocity)
    b, b_vehicle, _ = _rig(ten, track, location, heading, velocity)

    async def drive():
        await a.initialize()
        await b.initialize()
        for step in range(1, 4):
            await a.step()
            await b.step()
            assert a.beta == pytest.approx(10.0, abs=1e-9) and abs(a.cross_track_error) > 1.6
            assert a.warnings == step and a.mode == "primary"
            assert a_vehicle.actions[-1] == b_vehicle.actions[-1]
            assert a.current_index == b.current_index and a.mpc_last == b.mpc_last

    asyncio.run(drive())


def test_u11_7a_no_warning_at_or_below_the_minimum_speed():
    track = load_track("test-circuit")
    eleven, _ = _load("unit-11.py", MPC_BUDGET_MS=None)
    probe, _, _ = _rig(eleven, track, (0.0, 0.0, 0.0), 0.0, (0.0, 0.0, 0.0))
    location, heading = _line_pose(probe, 400, 2.0)
    slip = heading + math.radians(10.0)
    agent, _, _ = _rig(eleven, track, location, heading, (5.0 * math.cos(slip), 5.0 * math.sin(slip), 0.0))

    async def drive():
        await agent.initialize()
        await agent.step()

    asyncio.run(drive())
    assert agent.warnings == 0 and agent.beta == pytest.approx(10.0, abs=1e-9)


CRASH = (0.0, -1000.0, 0.0)  # racekit's impulse after a major collision
QUIET = (0.0, 0.0, 0.0)


def test_u11_7a_a_carla_respawn_keeps_the_index_then_re_anchors_on_the_start():
    track = load_track("test-circuit")
    eleven, module = _load("unit-11.py", MPC_BUDGET_MS=None)
    probe, _, _ = _rig(eleven, track, (0.0, 0.0, 0.0), 0.0, (0.0, 0.0, 0.0))
    crash_pose, heading = _line_pose(probe, 600, 0.5)
    moving = (30.0 * math.cos(heading), 30.0 * math.sin(heading), 0.0)
    agent, _, sensors = _rig(eleven, track, crash_pose, heading, moving)
    start_x, start_y, start_yaw = track.start_pose()
    anchored = []
    nearest = agent.nearest_index

    def spy(location):
        anchored.append(tuple(float(v) for v in location[:2]))
        return nearest(location)

    async def drive():
        await agent.initialize()
        for _ in range(3):
            await agent.step()
        index = agent.current_index
        assert 595 <= index <= 605 and agent.respawns == 0 and agent.mode == "primary"
        agent.nearest_index = spy
        # CARLA's first step after the hold: the impulse, with the stale crash pose and velocity
        sensors["collision"].set(CRASH)
        await agent.step()
        assert agent.respawns == 1 and agent.mode == "fallback" and agent.reanchor
        assert agent.current_index == index and anchored == []  # the stale pose is not trusted
        assert agent.mpc_queue == [0.0] * module.MPC_LAG and agent.mpc_last == 0.0 and agent.plan is None
        assert agent.limit_scale == FALLBACK_SCALE
        # the next step: the start pose at rest (the impulse may still be reported)
        sensors["location"].set((start_x, start_y, 0.0))
        sensors["rpy"].set((0.0, 0.0, start_yaw))
        sensors["velocity"].set((0.0, 0.0, 0.0))
        await agent.step()
        assert anchored == [(start_x, start_y)] and not agent.reanchor
        assert agent.current_index == nearest((start_x, start_y, 0.0))
        assert agent.respawns == 1

    asyncio.run(drive())


def test_u11_7a_a_repeated_reading_is_one_respawn_and_the_refractory_window():
    track = load_track("test-circuit")
    eleven, module = _load("unit-11.py", MPC_BUDGET_MS=None)
    start_x, start_y, start_yaw = track.start_pose()
    agent, _, sensors = _rig(eleven, track, (start_x, start_y, 0.0), start_yaw, (0.0, 0.0, 0.0))
    assert module.REFRACTORY_TICKS == 40

    async def drive():
        await agent.initialize()
        await agent.step()  # step 1, quiet
        sensors["collision"].set(CRASH)
        for _ in range(10):  # steps 2-11: one reading, repeated
            await agent.step()
        assert agent.respawns == 1 and agent.respawn_tick == 2
        sensors["collision"].set(QUIET)
        for _ in range(9):  # steps 12-20
            await agent.step()
        sensors["collision"].set(CRASH)  # a new impulse at step 21, inside the window
        await agent.step()
        assert agent.respawns == 1
        sensors["collision"].set(QUIET)
        while agent.ticks < 41:  # steps 22-41
            await agent.step()
        sensors["collision"].set(CRASH)  # a new impulse at step 42: 40 steps after step 2
        await agent.step()
        assert agent.respawns == 2 and agent.respawn_tick == 42
        assert agent.limit_scale == pytest.approx(FALLBACK_SCALE ** 2, rel=1e-15)

    asyncio.run(drive())


def test_u11_7a_check_submission_passes_on_unit_11():
    # the routed suite runs tests serially, so this timing is outside any pool
    report = check_submission(AGENTS / "unit-11.py")
    assert report.ok, str(report)


# --- U11.8: transfer (a finding) --------------------------------------------------------------------------


def test_u11_8_the_margin_does_not_transfer_to_seed2026(robust_premise):
    row = _row(robust_premise, transfer_key, TRANSFER_CARS)
    assert any(not _clean(o) for o in row.values()), row
    assert any(_clean(o) for o in row.values()), row


# --- U11.9: warnings as a trigger (the negative result) ---------------------------------------------------


def test_u11_9_falling_back_on_a_warning_does_not_help(robust_premise):
    plain = _row(robust_premise, lambda k: u11_key(0.58, k), TRAINING_CARS)
    warned = _row(robust_premise, warn_key, TRAINING_CARS)
    crashed = [k for k, o in plain.items() if o.collisions]
    assert crashed, plain
    for k in crashed:
        assert warned[k].collisions >= 1, (k, warned[k])
    assert _mean(warned.values()) >= _mean(plain.values()), (_mean(warned.values()), _mean(plain.values()))
