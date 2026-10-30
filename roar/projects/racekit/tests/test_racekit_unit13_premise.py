"""The Unit 13 gates (plan roar-013 U13.0-U13.6): race day on ``monza-like``.

One session pool (``_race_day_premise.py``, ``_premise.race_all``, the ``race_day_premise`` fixture):
37 races of ``agents/unit-13.py``, settings of it (the one-knob margin M, pursuit steering, section
0's grip at 12.0) and ``agents/unit-07.py``, each distinct race once, all on ``monza-like``, 3 laps,
capped at 900 s, on the nominal ``carla_like(noise=True)`` or a perturbed car
``carla_like(noise=True, perturb=k)`` at race seed ``k mod 5``, every one with
``MPC_BUDGET_MS = None`` (no wall clock in a gate race). U13.0 and U13.0b are race-free;
``check_submission`` (U13.6) runs outside any pool (the routed suite runs tests serially).

The track is known; the car is not. The perturbed family's sets: training cars k = 0-23 (the
re-tune's objective races 16, 18 and 8), validation cars k = 24-71 (the plan's pinned record, never
re-raced here) and the **test** cars k = 72-95 (pre-registered, raced once by probe p11 with the
shipped configuration, and here by U13.2 only).

A race is *clean* when it finishes with 0 collisions and its max error from **its own line** on
driving rows is at most 2 m (``agents/unit-07.py``: from the centreline). Race times are pinned to a
tick (0.05 s). The pins come from the probes (p1-p11); a miss means stop, amend and re-gate, never a
silent re-pin.
"""

from __future__ import annotations

import ast
import sys

import numpy as np
import pytest
from _line_premise import MEASURED_MU_G, MONZA
from _race_day_premise import (
    HIGH_MU,
    HIGH_MU_0,
    MARGIN_CAR,
    PURSUIT,
    PURSUIT_CAR,
    SEEDS5,
    SHIPPED_07,
    SHIPPED_13,
    TEST_CARS,
    U13,
    M,
    race_day_jobs,
    race_key,
    race_seed,
)
from conftest import RACEKIT
from racekit.check_submission import check_submission
from racekit.measure import noise_aware_better

TICK = 0.05 + 1e-9
CLEAN_ERROR = 2.0  # m: the clean rule's limit on the line error
CAP = 900.0
AGENTS = RACEKIT / "agents"
U11 = "unit-11.py"
POOLED_RACES = 37

# U13.0: the six constants that differ from agents/unit-11.py
CHANGED = {"LINE_CONTROL", "MU_G", "MU_FRACTION", "A_DEC", "A_ACC", "MPC_MIN_HORIZON"}
SHIPPED = {"MU_FRACTION": 0.64, "A_DEC": 4.5, "A_ACC": 5.0, "MPC_MIN_HORIZON": 40,
           "MPC_HORIZON": 40, "MPC_BUDGET_MS": 5.0, "STEERING": "mpc"}
LINE_VALUES = 285
LINE_TOL = 1e-9
# U13.1: the gate (p1 / p7)
MEDIANS = {"u13": 468.55, "u07": 515.10}
# U13.2: the test cars (p11, timing on, the shipped configuration)
TEST_MEDIAN = 468.65
P11_TIMES = (467.95, 470.05, 470.85, 469.05, 470.75, 466.50, 469.30, 467.40, 469.70, 469.40, 468.70, 469.85,
             468.95, 467.25, 466.70, 467.30, 469.65, 466.70, 468.60, 470.90, 467.45, 467.75, 467.90, 467.90)
U13_5_ERROR_TOL = 0.0005  # m: the max line error, the same to the probe log's three decimals
STEP_P99_BUDGET_MS = 5.0


def _clean(outcome) -> bool:
    return outcome.finished and outcome.collisions == 0 and outcome.line_error <= CLEAN_ERROR


def _one(premise, key):
    (outcome,) = premise[key]
    return outcome


def _times(outcomes):
    return [round(o.total_time, 2) for o in outcomes]


def _median(outcomes) -> float:
    return float(np.median([o.total_time for o in outcomes]))


def _spread(outcomes) -> float:
    times = [o.total_time for o in outcomes]
    return max(times) - min(times)


def _nominal(premise, setting):
    return [_one(premise, race_key(setting, seed)) for seed in SEEDS5]


def test_the_job_list_is_the_plans_pooled_races():
    jobs = race_day_jobs()
    assert sum(len(job.seeds) for job in jobs.values()) == len(jobs) == POOLED_RACES
    assert len(set(jobs.values())) == POOLED_RACES  # each distinct race once
    for key, job in jobs.items():
        assert job.track == MONZA and job.max_seconds == CAP and job.laps is None, key
        if job.agent == U13:
            assert dict(job.constants)["MPC_BUDGET_MS"] is None, key
            assert "LINE_CONTROL" not in dict(job.constants), key  # the shipped line, as shipped
            assert job.perturb is None or job.perturb in TEST_CARS + (MARGIN_CAR, PURSUIT_CAR), key
            assert job.perturb is None or job.seeds == (race_seed(job.perturb),), key
        else:
            assert job.agent == "unit-07.py" and job.constants == () and job.car == "carla", key


# --- U13.0: the file ---------------------------------------------------------------------------------------


def _module_parts(name):
    tree = ast.parse((AGENTS / name).read_text(encoding="utf-8"))
    assigns, bodies, others = {}, {}, []
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                key = target.id if isinstance(target, ast.Name) else ast.dump(target)
                assigns[key] = ast.dump(node.value)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bodies[node.name] = ast.dump(node)
        else:
            others.append(ast.dump(node))
    return assigns, bodies, others


def _module_constant(name, constant):
    tree = ast.parse((AGENTS / name).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == constant for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"{constant} not in {name}")


def test_u13_0_unit_13_is_unit_11_with_six_constants_changed():
    ours, theirs = _module_parts(U13), _module_parts(U11)
    changed = {key for key in set(ours[0]) | set(theirs[0]) if ours[0].get(key) != theirs[0].get(key)}
    assert changed == CHANGED, changed
    assert ours[1] == theirs[1]  # every function and class, byte-identical as AST
    assert ours[2] == theirs[2]  # the docstring and the imports
    for constant, value in SHIPPED.items():
        assert _module_constant(U13, constant) == value, constant
    assert _module_constant(U13, "MPC_MIN_HORIZON") == _module_constant(U13, "MPC_HORIZON")
    assert _module_constant(U13, "MU_G") == MEASURED_MU_G[MONZA]


def test_u13_0_the_line_is_monza_likes_solved_line(line_controls):
    shipped = _module_constant(U13, "LINE_CONTROL")
    solved = line_controls[(MONZA, "global")]
    assert len(shipped) == len(solved) == LINE_VALUES
    difference = float(np.max(np.abs(np.asarray(shipped) - np.asarray(solved))))
    print(f"\nU13.0: LINE_CONTROL {len(shipped)} values, max |shipped - solved| {difference:.3g} m")
    assert difference <= LINE_TOL, difference


# --- U13.0b: the budget policy cannot cut the horizon (race-free) ----------------------------------------


def test_u13_0b_a_slow_mpc_call_is_counted_and_the_horizon_stays_40(tmp_path):
    from racekit.runner import load_submission, shim_installed
    from racekit.tracks import load_track
    from racekit.variants import write_variant

    variant = write_variant(AGENTS / U13, tmp_path / "unit13_budget0.py", {"MPC_BUDGET_MS": "0.0"})
    with shim_installed():
        agent_class, module_name = load_submission(variant)
        try:
            agent = agent_class(load_track(MONZA).waypoints, None)
            assert agent.horizon == 40 and agent.over_budget == 0
            for call in (1, 2, 3):
                agent.mpc_command(0.0, 15.0)
                assert agent.over_budget == call and agent.horizon == 40, (call, agent.horizon)
        finally:
            sys.modules.pop(module_name, None)
    print(f"\nU13.0b: over_budget {agent.over_budget}, horizon {agent.horizon}")


# --- U13.1: the gate (design §6) --------------------------------------------------------------------------


def test_u13_1_unit_13_beats_unit_07_on_monza_like(race_day_premise):
    rows = {setting.label: _nominal(race_day_premise, setting) for setting in (SHIPPED_13, SHIPPED_07)}
    for label, row in rows.items():
        print(f"\nU13.1: {label} on {MONZA}: {_times(row)} median {_median(row):.2f} spread "
              f"{_spread(row):.2f} max line error {max(o.line_error for o in row):.3f}")
        assert all(_clean(o) for o in row), (label, row)
        assert _median(row) == pytest.approx(MEDIANS[label], abs=TICK), (label, _times(row))
    times = {label: [o.total_time for o in row] for label, row in rows.items()}
    print(f"U13.1: gain {_median(rows['u07']) - _median(rows['u13']):.2f} s")
    assert noise_aware_better(times["u13"], times["u07"]), times


# --- U13.2: N/N on the test cars --------------------------------------------------------------------------


def test_u13_2_unit_13_is_clean_on_every_test_car(race_day_premise):
    row = {k: _one(race_day_premise, race_key(SHIPPED_13, race_seed(k), k)) for k in TEST_CARS}
    times = [round(o.total_time, 2) for o in row.values()]
    matches = sum(abs(t - p) <= TICK for t, p in zip(times, P11_TIMES))
    print(f"\nU13.2: test cars 72-95: clean {sum(_clean(o) for o in row.values())}/24, median "
          f"{_median(list(row.values())):.2f}, max line error {max(o.line_error for o in row.values()):.3f}, "
          f"collisions {sum(o.collisions for o in row.values())}; times {times}; "
          f"equal to p11 (timing on) to a tick on {matches}/24 cars")
    assert all(_clean(o) for o in row.values()), {k: o for k, o in row.items() if not _clean(o)}
    assert _median(list(row.values())) == pytest.approx(TEST_MEDIAN, abs=TICK), times


# --- U13.3: the margin on one knob was not enough ----------------------------------------------------------


def test_u13_3_the_one_knob_margin_is_not_clean_on_car_41(race_day_premise):
    outcome = _one(race_day_premise, race_key(M, race_seed(MARGIN_CAR), MARGIN_CAR))
    print(f"\nU13.3: M (0.64, 5.0, 5.0) on car {MARGIN_CAR}: {outcome.total_time:.2f} s, "
          f"{outcome.collisions} collision(s), max line error {outcome.line_error:.3f} m")
    assert not _clean(outcome), outcome


# --- U13.4: pursuit loses the margin -----------------------------------------------------------------------


def test_u13_4_pursuit_is_not_clean_on_car_34(race_day_premise):
    outcome = _one(race_day_premise, race_key(PURSUIT, race_seed(PURSUIT_CAR), PURSUIT_CAR))
    print(f"\nU13.4: unit-13 with pursuit on car {PURSUIT_CAR}: {outcome.total_time:.2f} s, "
          f"{outcome.collisions} collision(s), max line error {outcome.line_error:.3f} m")
    assert not _clean(outcome), outcome


# --- U13.5: section 0 is not grip-limited ------------------------------------------------------------------


def test_u13_5_section_0s_grip_does_not_change_the_race(race_day_premise):
    shipped = _one(race_day_premise, race_key(SHIPPED_13, 0))
    high = _one(race_day_premise, race_key(HIGH_MU, 0))
    print(f"\nU13.5: MU_G[0] = {HIGH_MU_0}: {high.total_time:.2f} s, max line error {high.line_error:.4f} m; "
          f"shipped: {shipped.total_time:.2f} s, {shipped.line_error:.4f} m; telemetry identical: "
          f"{high.digest == shipped.digest}")
    assert _clean(high), high
    assert high.total_time == pytest.approx(shipped.total_time, abs=TICK), (high, shipped)
    assert high.line_error == pytest.approx(shipped.line_error, abs=U13_5_ERROR_TOL), (high, shipped)


# --- U13.6: check_submission on its own track ------------------------------------------------------------


def test_u13_6_check_submission_passes_on_monza_like():
    # the routed suite runs tests serially, so this timing is outside any pool
    report = check_submission(AGENTS / U13, track=MONZA)
    print(f"\ncheck_submission({U13}, track={MONZA!r}): {report}")
    assert report.ok, str(report)
    assert report.step_p99_ms is not None and report.step_p99_ms <= STEP_P99_BUDGET_MS, report.step_p99_ms
