"""The Unit 12 gates (plan roar-012 U12.0-U12.8): tuning against race time.

Two session pools (``_tuning_premise.py``, ``_premise.race_all``): the test track's six Unit 8 grip
probes on ``test-circuit-seed2028`` (U12.0, the ``tuning_test_track`` fixture, with the track's line
solved once), then the gate races (``tuning_premise``): 109 races of ``agents/unit-11.py``,
``agents/unit-12.py`` and settings of ``unit-11.py`` (the speed search's, the one-track search's, the
dead knobs, ``A_DEC = 6.0``), each distinct race once, plus U12.1's determinism re-race, on the nominal
``carla_like(noise=True)`` or the perturbed car ``carla_like(noise=True, perturb=k)``, 3 laps unless
said, capped at 700 s, every one with ``MPC_BUDGET_MS = None`` (no wall clock in a gate race).
``check_submission`` runs outside any pool (the routed suite runs tests serially). U12.0's geometry
pins are ``roar/data/tests/test_gen_tracks.py``.

The three kinds of track: the **training** tracks (``test-circuit``, ``test-circuit-seed1`` ...
``seed4``: the search's objective), the **validation** track ``test-circuit-seed2026`` (never in the
objective, but the speed search's failure there changed it) and the **test** track
``test-circuit-seed2028`` (its seed fixed before it was built or probed; raced only by the gate).

A race is *clean* when it finishes with 0 collisions and its max error from **its own line** on
driving rows is at most 2 m. Race times are pinned to a tick (0.05 s). The pins come from the probes
(p1-p9); a miss means stop, amend and re-gate, never a silent re-pin.
"""

from __future__ import annotations

import ast

import numpy as np
import pytest
from _checkpoint_b_premise import lowest_grip_cars
from _line_premise import BASE, TRAINING
from _tuning_premise import (
    A_DEC_6,
    DEAD_KNOBS,
    HELD_OUT_CARS,
    KNOB_LAPS,
    LOW_GRIP_CARS,
    MU_060,
    OBJECTIVE_SEEDS,
    OVERFIT_SETTING,
    RERACE_TAG,
    SEEDS5,
    SHIPPED_11,
    SHIPPED_12,
    SPEED_SETTING,
    TEST,
    TEST_MU_G,
    U11,
    U12,
    VALIDATION,
    objective_keys,
    probe_key,
    race_key,
    tuning_jobs,
)
from conftest import RACEKIT
from racekit.check_submission import check_submission
from racekit.measure import noise_aware_better

TICK = 0.05 + 1e-9
MU_TOL = 0.005 + 1e-9  # the probe estimates are pinned after rounding to 0.01
CLEAN_ERROR = 2.0  # m: the clean rule's limit on the line error
CAP = 700.0
AGENTS = RACEKIT / "agents"
POOLED_RACES = 109  # the distinct gate races (U12.1's re-race included; U12.0's six probes are separate)

# U12.0: the test track (probe p9)
TEST_LINE_VALUES = 131
PROBE_SECTION_0_TIME = 108.90
# U12.1: unit-11's 3-lap spread on the validation track, race seeds 0-4 (p1/p4: 0.15)
NOISE_SPREAD = 0.25
# U12.2: one lap of test-circuit, race seed 0 (p8)
KNOB_TIME = 96.40
MU_060_TIME = 93.95
KNOB_GAIN = 0.25  # s: MU_FRACTION 0.60 is faster than this
# U12.3: the one-track search's gain on its own track (p5: 279.65 -> 265.55 / 265.50)
OVERFIT_GAIN = 10.0
# U12.4: the speed search's gain on the training family, per race seed (p3/p8: about 49 s)
SPEED_GAIN = 40.0
# U12.5a: the validation track (p4)
VALIDATION_MEDIANS = {U12: 280.65, U11: 282.00}
# U12.5: the test track (p9)
TEST_MEDIANS = {U12: 269.65, U11: 271.05}
# U12.6: the crash-aware objective's per-replicate sums (p8)
OBJECTIVE_SUMS = {U12: (2215.35, 2215.25), U11: (2224.90, 2224.35)}
# U12.7: the cost on the held-out perturbed cars (p4: 20 of 24 clean)
HELD_OUT_MIN_CLEAN = 20
HELD_OUT_MAX_ERROR = 2.6  # m: every held-out race that is not clean stays within this
MODULE_CONSTANTS = 48  # U12.8: the hook's count (the State / Action type aliases excluded)


def _clean(outcome) -> bool:
    return outcome.finished and outcome.collisions == 0 and outcome.line_error <= CLEAN_ERROR


def _one(premise, key):
    (outcome,) = premise[key]
    return outcome


def _races(premise, setting, track, seeds=SEEDS5):
    return [_one(premise, race_key(setting, track, seed)) for seed in seeds]


def _times(outcomes):
    return [round(o.total_time, 2) for o in outcomes]


def _median(outcomes) -> float:
    return float(np.median([o.total_time for o in outcomes]))


def _spread(outcomes) -> float:
    times = [o.total_time for o in outcomes]
    return max(times) - min(times)


def _objective_sums(premise, setting):
    return [sum(_one(premise, key).total_time for key in objective_keys(setting, replicate))
            for replicate in range(len(OBJECTIVE_SEEDS))]


def _assigned(name, constant):
    tree = ast.parse((AGENTS / name).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == constant for t in node.targets):
            return node.value
    raise AssertionError(f"{constant} not in {name}")


def _module_constant(name, constant):
    return ast.literal_eval(_assigned(name, constant))


def test_the_job_list_is_the_plans_pooled_races(line_controls):
    jobs = tuning_jobs(line_controls, (0.0,) * TEST_LINE_VALUES)
    assert sum(len(job.seeds) for job in jobs.values()) == len(jobs) == POOLED_RACES
    # each distinct race once, except U12.1's tagged twin
    distinct = {job for job in jobs.values()}
    assert len(distinct) == POOLED_RACES - 1
    twin = race_key(SHIPPED_12, TEST, 0)
    assert jobs[twin] == jobs[f"{twin}|{RERACE_TAG}"]
    for key, job in jobs.items():
        assert job.track != "test-circuit-seed2027" and (job.perturb is None or job.perturb < 1000), key
        assert job.max_seconds == CAP and dict(job.constants)["MPC_BUDGET_MS"] is None, key
        assert job.laps == (KNOB_LAPS if key.endswith(f"|L{KNOB_LAPS}") else None), key
        if job.track == BASE:
            assert "LINE_CONTROL" not in dict(job.constants), key  # the shipped line, as shipped
        else:
            assert "LINE_CONTROL" in dict(job.constants) and "MU_G" in dict(job.constants), key


def test_the_low_grip_cars_are_unit_11s_three_lowest_grip_training_cars():
    assert lowest_grip_cars() == LOW_GRIP_CARS == (16, 18, 8)


# --- U12.0: the test track -----------------------------------------------------------------------------


def test_u12_0_the_test_track_line_and_grip(tuning_test_track):
    assert len(tuning_test_track.line) == TEST_LINE_VALUES
    measured = []
    for section in range(6):
        (outcome,) = tuning_test_track.probes[probe_key(section)]
        count, estimate = outcome.sections[section]
        assert estimate is not None, (section, count)
        measured.append(estimate)
        if section == 0:
            # it never slid: a lower bound
            assert outcome.finished and outcome.collisions == 0, outcome
            assert outcome.total_time == pytest.approx(PROBE_SECTION_0_TIME, abs=TICK), outcome
        else:
            # the car slid: the estimate is a measurement
            assert not outcome.finished and outcome.collisions >= 1, (section, outcome)
    print(f"\nU12.0: probes {[round(v, 2) for v in measured]} (pinned {TEST_MU_G}); collisions "
          f"{[tuning_test_track.probes[probe_key(s)][0].collisions for s in range(6)]}")
    assert [round(value, 2) for value in measured] == pytest.approx(TEST_MU_G, abs=MU_TOL), measured


# --- U12.1: determinism and noise -----------------------------------------------------------------------


def test_u12_1_the_same_seed_is_the_same_race(tuning_premise):
    twin = _one(tuning_premise, race_key(SHIPPED_12, TEST, 0))
    again = _one(tuning_premise, race_key(SHIPPED_12, TEST, 0, tag=RERACE_TAG))
    assert again.digest == twin.digest and again.total_time == twin.total_time, (twin, again)


def test_u12_1_the_noise_on_the_validation_track(tuning_premise):
    row = _races(tuning_premise, SHIPPED_11, VALIDATION)
    print(f"\nU12.1: unit-11 on {VALIDATION}: times {_times(row)} spread {_spread(row):.2f}")
    assert _spread(row) <= NOISE_SPREAD + 1e-9, _times(row)


# --- U12.2: the knob map ---------------------------------------------------------------------------------


def test_u12_2_dead_knobs_race_identically_and_mu_fraction_does_not(tuning_premise):
    shipped = _one(tuning_premise, race_key(SHIPPED_11, BASE, 0, laps=KNOB_LAPS))
    assert shipped.total_time == pytest.approx(KNOB_TIME, abs=TICK), shipped
    for setting in DEAD_KNOBS:
        outcome = _one(tuning_premise, race_key(setting, BASE, 0, laps=KNOB_LAPS))
        assert outcome.digest == shipped.digest, (setting.label, outcome)  # identical telemetry
        assert outcome.total_time == shipped.total_time, (setting.label, outcome)
    live = _one(tuning_premise, race_key(MU_060, BASE, 0, laps=KNOB_LAPS))
    print(f"\nU12.2: shipped {shipped.total_time:.2f}, MU_FRACTION 0.60 {live.total_time:.2f}")
    assert shipped.total_time - live.total_time > KNOB_GAIN, (shipped, live)
    assert live.total_time == pytest.approx(MU_060_TIME, abs=TICK), live
    assert live.digest != shipped.digest


# --- U12.3: overfitting -----------------------------------------------------------------------------------


def test_u12_3_tuned_on_one_track_it_crashes_on_the_validation_track(tuning_premise):
    own = _races(tuning_premise, OVERFIT_SETTING, BASE, OBJECTIVE_SEEDS)
    shipped = _races(tuning_premise, SHIPPED_11, BASE, OBJECTIVE_SEEDS)
    elsewhere = _races(tuning_premise, OVERFIT_SETTING, VALIDATION, SEEDS5[:3])
    print(f"\nU12.3: overfit on {BASE} {_times(own)} vs unit-11 {_times(shipped)}; on {VALIDATION} "
          f"{_times(elsewhere)} collisions {[o.collisions for o in elsewhere]} "
          f"line errors {[round(o.line_error, 2) for o in elsewhere]}")
    assert all(_clean(o) for o in own), own
    for tuned, base in zip(own, shipped):
        assert base.total_time - tuned.total_time > OVERFIT_GAIN, (tuned, base)
    assert not any(_clean(o) for o in elsewhere), elsewhere


# --- U12.4: the speed search's result ---------------------------------------------------------------------


def test_u12_4_the_speed_setting_wins_the_training_family_and_crashes_on_validation(tuning_premise):
    sums = {}
    for setting in (SPEED_SETTING, SHIPPED_11):
        per_seed = []
        for seed in OBJECTIVE_SEEDS:
            races = [_one(tuning_premise, race_key(setting, track, seed)) for track in TRAINING]
            assert all(_clean(o) for o in races), (setting.label, seed, races)
            per_seed.append(sum(o.total_time for o in races))
        sums[setting.label] = per_seed
    validation = _races(tuning_premise, SPEED_SETTING, VALIDATION)
    print(f"\nU12.4: training per-seed sums speed {[round(s, 2) for s in sums['speed']]} unit-11 "
          f"{[round(s, 2) for s in sums['u11']]}; on {VALIDATION} {_times(validation)} clean "
          f"{sum(_clean(o) for o in validation)}/5 max line error {max(o.line_error for o in validation):.2f}")
    for speed, base in zip(sums["speed"], sums["u11"]):
        assert base - speed > SPEED_GAIN, sums
    assert not any(_clean(o) for o in validation), validation


# --- U12.5a: the validation track -------------------------------------------------------------------------


def test_u12_5a_unit_12_on_the_validation_track(tuning_premise):
    rows = {agent: _races(tuning_premise, setting, VALIDATION)
            for agent, setting in ((U12, SHIPPED_12), (U11, SHIPPED_11))}
    for agent, row in rows.items():
        print(f"\nU12.5a: {agent} on {VALIDATION}: {_times(row)} median {_median(row):.2f} spread "
              f"{_spread(row):.2f} max line error {max(o.line_error for o in row):.2f}")
        assert all(_clean(o) for o in row), (agent, row)
        assert _median(row) == pytest.approx(VALIDATION_MEDIANS[agent], abs=TICK), (agent, _times(row))


# --- U12.5: the gate (design §6), on the test track --------------------------------------------------------


def test_u12_5_the_tuned_agent_beats_the_hand_tuned_one_on_the_test_track(tuning_premise):
    rows = {agent: _races(tuning_premise, setting, TEST)
            for agent, setting in ((U12, SHIPPED_12), (U11, SHIPPED_11))}
    speed = _races(tuning_premise, SPEED_SETTING, TEST)
    for agent, row in rows.items():
        print(f"\nU12.5: {agent} on {TEST}: {_times(row)} median {_median(row):.2f} spread "
              f"{_spread(row):.2f} max line error {max(o.line_error for o in row):.2f}")
        assert all(_clean(o) for o in row), (agent, row)
        assert _median(row) == pytest.approx(TEST_MEDIANS[agent], abs=TICK), (agent, _times(row))
    print(f"U12.5: the speed setting on {TEST}: {_times(speed)} clean {sum(_clean(o) for o in speed)}/5")
    times = {agent: [o.total_time for o in row] for agent, row in rows.items()}
    assert noise_aware_better(times[U12], times[U11]), times
    assert not all(_clean(o) for o in speed), speed


# --- U12.6: the crash-aware verdict -------------------------------------------------------------------------


def test_u12_6_the_crash_aware_objective_accepts_a_dec_5_5(tuning_premise):
    sums = {}
    for agent, setting in ((U12, SHIPPED_12), (U11, SHIPPED_11)):
        races = [_one(tuning_premise, key) for replicate in range(len(OBJECTIVE_SEEDS))
                 for key in objective_keys(setting, replicate)]
        assert len(races) == 16 and all(_clean(o) for o in races), (agent, races)
        sums[agent] = _objective_sums(tuning_premise, setting)
    print(f"\nU12.6: per-replicate sums unit-12 {[round(s, 2) for s in sums[U12]]} unit-11 "
          f"{[round(s, 2) for s in sums[U11]]}")
    assert noise_aware_better(sums[U12], sums[U11]), sums
    for agent, pinned in OBJECTIVE_SUMS.items():
        assert sums[agent] == pytest.approx(pinned, abs=TICK), (agent, sums[agent])


def test_u12_6_a_dec_6_0_is_not_clean_on_car_16_so_5_5_is_the_edge(tuning_premise):
    races = [_one(tuning_premise, race_key(A_DEC_6, BASE, (16 + replicate) % 5, perturb=16))
             for replicate in range(len(OBJECTIVE_SEEDS))]
    print(f"\nU12.6: A_DEC 6.0 on car 16: times {_times(races)} collisions {[o.collisions for o in races]} "
          f"line errors {[round(o.line_error, 2) for o in races]}")
    assert not any(_clean(o) for o in races), races


# --- U12.7: the cost ----------------------------------------------------------------------------------------


def test_u12_7_the_cost_on_the_held_out_perturbed_cars(tuning_premise):
    row = {k: _one(tuning_premise, race_key(SHIPPED_12, BASE, k % 5, perturb=k)) for k in HELD_OUT_CARS}
    assert all(o.finished and o.collisions == 0 for o in row.values()), row
    unclean = {k: round(o.line_error, 3) for k, o in row.items() if not _clean(o)}
    nearest = max((o.line_error, k) for k, o in row.items() if _clean(o))  # the clean car closest to 2 m
    print(f"\nU12.7: not clean {unclean} (p4: k = 24, 29, 32, 35); clean {len(row) - len(unclean)}/24; "
          f"the clean car nearest the rule k = {nearest[1]} at {nearest[0]:.3f} m")
    # The not-clean set is reported, not asserted: k = 24 sits 11 mm over the 2 m rule (p4: 2.011 m), and
    # the nearest clean car, k = 43, is 14 cm inside it, so a tick of noise could move either across it.
    assert len(row) - len(unclean) >= HELD_OUT_MIN_CLEAN, unclean
    assert len(unclean) >= 1, unclean
    assert all(error <= HELD_OUT_MAX_ERROR for error in unclean.values()), unclean


def test_u12_7_the_validation_line_error_is_reported(tuning_premise):
    errors = {agent: max(o.line_error for o in _races(tuning_premise, setting, VALIDATION))
              for agent, setting in ((U12, SHIPPED_12), (U11, SHIPPED_11))}
    # reported, not asserted (p4: 1.76 m vs 1.20 m)
    print(f"\nU12.7: max line error on {VALIDATION}: unit-12 {errors[U12]:.2f} m, unit-11 {errors[U11]:.2f} m")


# --- U12.8: equivalence -------------------------------------------------------------------------------------


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


def test_u12_8_unit_12_is_unit_11_with_a_dec_5_5():
    ours, theirs = _module_parts(U12), _module_parts(U11)
    changed = {key for key in set(ours[0]) | set(theirs[0]) if ours[0].get(key) != theirs[0].get(key)}
    assert changed == {"A_DEC"}, changed
    assert _module_constant(U12, "A_DEC") == 5.5 and _module_constant(U11, "A_DEC") == 5.0
    assert _module_constant(U12, "MPC_BUDGET_MS") == 5.0  # the shipped file keeps the timing
    assert ours[1] == theirs[1]  # every function and class, byte-identical as AST
    assert ours[2] == theirs[2]  # the docstring and the imports
    for parts in (ours, theirs):
        constants = [key for key in parts[0] if key not in ("State", "Action")]
        assert len(constants) == MODULE_CONSTANTS, len(constants)
        assert all(key.isupper() for key in constants), constants


def test_check_submission_passes_on_unit_12():
    # the routed suite runs tests serially, so this timing is outside any pool
    report = check_submission(AGENTS / U12)
    print(f"\ncheck_submission({U12}): {report}")
    assert report.ok, str(report)
