"""The Unit 8 and Unit 9 gates (plan roar-008 U8.1-U8.5, U9.1-U9.6): system identification, and the
racing line.

The races run in the session's shared parallel pool (``_line_premise.py``, ``_premise.race_all``):
41 jobs, 141 races, all on ``carla_like(noise=True)``, race seeds 0-4 unless a job says otherwise,
capped at 450 s on a ``test-circuit`` track and 900 s on ``monza-like`` (the grip probes: one lap,
300 s, seed 0). The lines are solved once per session (``_line_solver.py``, QR + ``bvls``; U9.1 is
race-free). The tracks are loaded by their literal generated names: the carla-like car's hidden grip
is keyed to the track name, so a rename changes the car and invalidates every pin. The pins come
from the probes (``p6``-``p9``, ``p19``-``p26``); a miss means stop, amend and re-gate, never a
silent re-pin.

U8.2 compares the probe's estimates with the car's hidden grip table: this routed test may, student
material never does.

Tolerances: medians and quoted spreads within ±0.05 s (one tick). A race is *clean* when it finishes
with 0 collisions and its max cross-track error from **its own line** on driving rows is at most 2 m
(for a centreline race that is the max |offset|); an unclean cell is asserted only "not clean", never
a collision count (that count depends on the time cap). The equivalences are asserted to the tick: the
same total time and byte-identical telemetry.
"""

from __future__ import annotations

import numpy as np
import pytest
from _line_premise import (
    BASE,
    CHECKPOINT,
    LINE_TRACKS,
    LOCAL_TRACKS,
    MEASURED_MU_G,
    MONZA,
    PROBE_TRACKS,
    TRAINING,
    U7_66,
    U7_66_CHECKPOINT,
    U8_054,
    U8_70_MONZA,
    U8_MONZA_EDGE,
    U8_NO_MU,
    U8_REFERENCE,
    U9_NO_LINE,
    U9_REFERENCE,
    centre_key,
    line_key,
    line_premise_jobs,
    local_key,
    probe_key,
)
from _line_solver import PIN, curvature_and_length, line_offsets, line_points
from conftest import RACEKIT
from racekit import _truth
from racekit.check_submission import check_submission
from racekit.sysid_data import LOGS, load_log, log_path
from racekit.telemetry import read_log_csv
from racekit.tracks import load_track

TICK = 0.05 + 1e-9
CLEAN_ERROR = 2.0  # m: the clean rule's limit on the max cross-track error from the race's own line
G = 9.81
AGENTS = RACEKIT / "agents"
CHECKPOINT_A_MEDIAN = 310.80  # s: Checkpoint A's pinned race on the checkpoint track (plan roar-007)
CHECKPOINT_A_SPREAD = 0.20  # s: its pinned spread


def _clean(outcome) -> bool:
    return outcome.finished and outcome.collisions == 0 and outcome.line_error <= CLEAN_ERROR


def _all_clean(outcomes) -> bool:
    return len(outcomes) == 5 and all(_clean(o) for o in outcomes)


def _median(outcomes) -> float:
    return float(np.median([o.total_time for o in outcomes]))


def _spread(outcomes) -> float:
    times = [o.total_time for o in outcomes]
    return max(times) - min(times)


def _assert_clean_row(outcomes, median):
    assert _all_clean(outcomes), outcomes
    assert _median(outcomes) == pytest.approx(median, abs=TICK), outcomes


def _assert_not_clean(outcomes):
    assert len(outcomes) == 5 and not _all_clean(outcomes), outcomes


def _assert_same_race(first, second):
    assert len(first) == len(second) == 1
    assert first[0].total_time == second[0].total_time and first[0].collisions == second[0].collisions
    assert first[0].digest == second[0].digest  # identical telemetry, to the tick


def _load_agent(name):
    from racekit.runner import load_submission, shim_installed

    with shim_installed():
        agent_class, _ = load_submission(AGENTS / name)
    return agent_class


def _module_constant(name, constant):
    import ast

    tree = ast.parse((AGENTS / name).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == constant for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"{constant} not in {name}")


def test_the_job_list_is_the_plans_141_races(line_controls):
    jobs = line_premise_jobs(line_controls)
    assert len(jobs) == 41
    assert sum(len(job.seeds) for job in jobs.values()) == 141
    assert sum(len(job.seeds) for job in jobs.values() if job.track == MONZA) == 31
    assert all(job.car == "carla" for job in jobs.values())
    for key, job in jobs.items():
        if key.startswith("probe-"):
            assert job.laps == 1 and job.max_seconds == 300.0 and job.seeds == (0,)
        else:
            assert job.laps is None and job.max_seconds == (900.0 if job.track == MONZA else 450.0)
    # the literal track names (the hidden grip is keyed to them)
    assert TRAINING == ("test-circuit", "test-circuit-seed1", "test-circuit-seed2", "test-circuit-seed3",
                        "test-circuit-seed4")
    assert CHECKPOINT == "test-circuit-seed2026" and MONZA == "monza-like"
    # on test-circuit the agents race their shipped MU_G and (global) LINE_CONTROL
    for key, job in jobs.items():
        if job.track == BASE:
            constants = dict(job.constants)
            assert constants.get("MU_G") is None, key
            assert constants.get("LINE_CONTROL") is None or key == local_key(BASE, 0.5), key


def test_the_agents_ship_test_circuits_measured_values():
    for name in ("unit-08.py", "unit-09.py"):
        assert _module_constant(name, "MU_G") == MEASURED_MU_G[BASE]
    assert _module_constant("unit-08.py", "MU_FRACTION") == 0.56
    assert _module_constant("unit-09.py", "MU_FRACTION") == 0.54
    assert _module_constant("unit-09.py", "LINE_STEP") == 10


# --- U8.1: the committed logs, through racekit.sysid_data ------------------------------------------------


@pytest.mark.parametrize("name", LOGS)
def test_u8_1_the_loader_returns_the_logs(name):
    if not log_path(name).is_file():
        pytest.fail(f"{log_path(name)} is missing; run "
                    "`PYTHONHASHSEED=0 uv run --group roar python roar/data/generate.py`")
    log, meta = load_log(name)
    expected_log, expected_meta = read_log_csv(log_path(name))
    assert meta == expected_meta and np.array_equal(log, expected_log)


def test_u8_1_the_longitudinal_fit_through_the_loader():
    # roar-004's G4.6 assertions (test_racekit_sysid_premise.py, which also reads through load_log)
    from test_racekit_sysid_premise import _longitudinal_fit

    log, meta = load_log("monza-like-seed0.csv")
    assert meta["kind"] == "race"
    rms = {lag: _longitudinal_fit(log, lag)[1] for lag in (0, 1, 2)}
    assert min(rms, key=rms.get) == 1, rms
    (a_throttle, a_brake, c_drag), _ = _longitudinal_fit(log, 1)
    assert abs(a_brake / _truth.A_BRAKE - 1.0) <= 0.05, a_brake
    assert abs(c_drag / _truth.C_DRAG - 1.0) <= 0.10, c_drag
    assert abs(a_throttle / _truth.A_THROTTLE - 1.0) <= 0.10, a_throttle


# --- U8.2: the grip probe ---------------------------------------------------------------------------------


@pytest.mark.parametrize("track", PROBE_TRACKS)
def test_u8_2_the_probes_reproduce_the_measured_grip(line_premise, track):
    for section in range(6):
        (outcome,) = line_premise[probe_key(track, section)]
        rows, estimate = outcome.sections[section]
        assert rows > 20 and estimate is not None, (section, rows)
        assert round(estimate, 2) == pytest.approx(MEASURED_MU_G[track][section], abs=1e-9), (section, estimate)


def test_u8_2_every_test_circuit_probe_slid_and_its_estimates_are_near_mu_g(line_premise):
    mu_g = np.array(_truth.grip_table(BASE)) * G
    for section in range(6):
        (outcome,) = line_premise[probe_key(BASE, section)]
        assert outcome.collisions >= 1, section  # the probe lost grip: the estimate is an estimate
        ratio = outcome.sections[section][1] / mu_g[section]
        assert 0.97 <= ratio <= 1.02, (section, ratio)


def test_u8_2_monza_section_0_never_slid_so_it_is_a_lower_bound(line_premise):
    mu_g = np.array(_truth.grip_table(MONZA)) * G
    for section in range(1, 6):
        (outcome,) = line_premise[probe_key(MONZA, section)]
        ratio = outcome.sections[section][1] / mu_g[section]
        assert 0.95 <= ratio <= 1.02, (section, ratio)
    (start,) = line_premise[probe_key(MONZA, 0)]
    assert start.collisions == 0, start
    assert start.sections[0][1] / mu_g[0] < 0.8, start.sections[0]


# --- U8.3: the steering gain ------------------------------------------------------------------------------


def test_u8_3_at_70_degrees_the_measured_mu_planner_is_not_clean_on_monza(line_premise):
    _assert_not_clean(line_premise[U8_70_MONZA])


def test_u8_3_at_66_degrees_it_is_clean_on_monza_through_0_62(line_premise):
    _assert_clean_row(line_premise[U8_MONZA_EDGE], 497.90)


def test_u8_3_the_steering_gain_does_not_cure_the_unit_7_reference_on_seed2026(line_premise):
    _assert_not_clean(line_premise[U7_66_CHECKPOINT])


# --- U8.4: the transfer -----------------------------------------------------------------------------------


def test_u8_4_0_58_is_clean_on_the_training_family(line_premise):
    for track, median in zip(TRAINING, (299.30, 295.15, 294.35, 294.75, 295.80)):
        _assert_clean_row(line_premise[centre_key(track, 0.58)], median)


def test_u8_4_0_60_is_not_clean_on_seed4(line_premise):
    _assert_not_clean(line_premise[centre_key("test-circuit-seed4", 0.6)])


def test_u8_4_the_frozen_0_56_transfers_and_beats_checkpoint_a(line_premise):
    outcomes = line_premise[centre_key(CHECKPOINT, 0.56)]
    _assert_clean_row(outcomes, 303.30)
    spread = max(_spread(outcomes), CHECKPOINT_A_SPREAD)
    assert _median(outcomes) + 3 * spread < CHECKPOINT_A_MEDIAN


# --- U8.5: the reference ----------------------------------------------------------------------------------


def test_u8_5_the_unit_8_reference(line_premise):
    _assert_clean_row(line_premise[U8_REFERENCE], 301.95)


def test_u8_5_without_mu_g_unit_8_races_exactly_like_unit_7_at_66_degrees(line_premise):
    _assert_same_race(line_premise[U8_NO_MU], line_premise[U7_66])


def test_u8_check_submission_passes_on_unit_08():
    # the isolated Python 3.8 run covers every file in agents/ (test_racekit_check_submission.py)
    report = check_submission(AGENTS / "unit-08.py")
    assert report.ok, str(report)


# --- U9.1: the line is valid (race-free) ------------------------------------------------------------------


@pytest.mark.parametrize("track_name", LINE_TRACKS)
def test_u9_1_the_line_is_inside_the_margin_pinned_at_the_start_and_smoother(line_controls, track_name):
    track = load_track(track_name)
    n = len(track)
    for kind in ("global", "local") if track_name in LOCAL_TRACKS else ("global",):
        offsets = line_offsets(line_controls[(track_name, kind)], n)
        assert len(line_controls[(track_name, kind)]) == n // 10
        assert np.all(np.abs(offsets) <= track.half_width - 2.5 + 1e-9), kind
        assert np.abs(offsets[:PIN]).max() <= 1e-9 and np.abs(offsets[n - PIN:]).max() <= 1e-9, kind
        centre = curvature_and_length(track.x, track.y)
        line = curvature_and_length(*line_points(track.x, track.y, offsets))
        assert line[0] < centre[0] and line[1] < centre[1], (kind, centre, line)


def test_u9_1_what_the_line_changes(line_controls):
    for name, centre, line in (("test-circuit", (0.2880, 2661.7, 18.0), (0.2326, 2636.2, 15.2)),
                               ("monza-like", (0.2421, 5714.5, 25.0), (0.1428, 5684.7, 28.3))):
        track = load_track(name)
        offsets = line_offsets(line_controls[(name, "global")], len(track))
        got_centre = curvature_and_length(track.x, track.y)
        got_line = curvature_and_length(*line_points(track.x, track.y, offsets))
        assert got_centre[0] == pytest.approx(centre[0], abs=5e-5) and got_line[0] == pytest.approx(line[0], abs=0.002)
        assert got_centre[1] == pytest.approx(centre[1], abs=0.05) and got_line[1] == pytest.approx(line[1], abs=0.05)
        assert got_centre[2] == pytest.approx(centre[2], abs=0.05) and got_line[2] == pytest.approx(line[2], abs=0.05)


def test_u9_1_the_shipped_line_re_solves_and_the_agent_rebuilds_it(line_controls):
    track = load_track(BASE)
    n = len(track)
    shipped = _module_constant("unit-09.py", "LINE_CONTROL")
    assert len(shipped) == n // 10
    solved = line_offsets(line_controls[(BASE, "global")], n)
    assert np.abs(line_offsets(shipped, n) - solved).max() <= 1e-6
    # the agent's own B-spline evaluation (numpy only) is the solver's basis
    agent = _load_agent("unit-09.py")(track.waypoints, None)
    assert np.abs(np.array(agent.offsets) - line_offsets(shipped, n)).max() <= 1e-12
    x, y = line_points(track.x, track.y, line_offsets(shipped, n))
    assert np.abs(np.array(agent.xs) - x).max() <= 1e-9 and np.abs(np.array(agent.ys) - y).max() <= 1e-9


# --- U9.2: the same f -------------------------------------------------------------------------------------


def test_u9_2_on_test_circuit_the_line_buys_25_s_at_the_same_f(line_premise):
    _assert_clean_row(line_premise[U9_REFERENCE], 279.60)
    _assert_clean_row(line_premise[centre_key(BASE, 0.54)], 304.70)


def test_u9_2_on_monza_the_line_beats_local_widening_beats_the_centreline(line_premise):
    _assert_clean_row(line_premise[line_key(MONZA, 0.6)], 473.45)
    _assert_clean_row(line_premise[local_key(MONZA, 0.6)], 487.55)
    _assert_clean_row(line_premise[centre_key(MONZA, 0.6)], 500.70)


# --- U9.3: a new line breaks the tuning ------------------------------------------------------------------


def test_u9_3_unit_8s_edge_is_not_clean_with_the_line(line_premise):
    _assert_not_clean(line_premise[line_key("test-circuit-seed4", 0.58)])
    # ... while on the centreline 0.58 is clean on all five training tracks (U8.4)
    assert all(_all_clean(line_premise[centre_key(track, 0.58)]) for track in TRAINING)


# --- U9.4: the family and the transfer --------------------------------------------------------------------


def test_u9_4_unit_8s_frozen_0_56_stays_clean_with_the_line(line_premise):
    for track, median in zip(TRAINING, (277.10, 273.80, 273.05, 273.25, 273.45)):
        _assert_clean_row(line_premise[line_key(track, 0.56)], median)


def test_u9_4_the_retuned_0_54_transfers_and_0_58_does_not(line_premise):
    _assert_clean_row(line_premise[line_key(CHECKPOINT, 0.54)], 282.05)
    _assert_not_clean(line_premise[line_key(CHECKPOINT, 0.58)])


# --- U9.5: local widening loses on test-circuit ------------------------------------------------------------


def test_u9_5_local_widening_is_not_clean_on_test_circuit(line_premise):
    _assert_not_clean(line_premise[local_key(BASE, 0.5)])


# --- U9.6: the reference ----------------------------------------------------------------------------------


def test_u9_6_the_unit_9_reference(line_premise):
    _assert_clean_row(line_premise[U9_REFERENCE], 279.60)


def test_u9_6_without_a_line_unit_9_races_exactly_like_unit_8_at_0_54(line_premise):
    _assert_same_race(line_premise[U9_NO_LINE], line_premise[U8_054])


def test_u9_check_submission_passes_on_unit_09():
    report = check_submission(AGENTS / "unit-09.py")
    assert report.ok, str(report)
