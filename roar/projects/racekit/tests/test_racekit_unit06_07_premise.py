"""The Unit 6 and Unit 7 premises (plan roar-006 U6.1-U6.4, U7.1-U7.9), raced with the reference
submissions in the session's shared parallel pool (``_speed_premise.py``, ``_premise.race_all``).

Every gate the plan routes here is asserted in full; the milestones assert a trimmed subset. The pins
come from the probes (``q8.txt``, ``q11.txt``, ``q18.txt``-``q21.txt``), reproduced to the bit by the
shipped agents; a miss means stop, amend and re-gate, never a silent re-pin.

Tolerances (the plan's Gates header): times, medians and quoted spreads within ±0.05 s; clean/crash
outcomes, spin counts and per-seed collision lists exact; max |offset| within ±0.01 m where quoted;
noise-aware comparisons strict (``racekit.measure.noise_aware_better``). A race is *clean* when it
finishes with 0 collisions and its max |offset| on driving rows is at most 2 m.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from _speed_premise import (
    ACCEPTED,
    EDGE_VECTOR,
    SINGLES,
    U7_GRID_EDGE,
    grid_key,
    grip_key,
    knobs,
)
from racekit.measure import noise_aware_better

TICK = 0.05 + 1e-9
OFFSET_TOL = 0.01 + 1e-9
CLEAN_OFFSET = 2.0  # m: the clean rule's limit on max |offset|
AGENTS = Path(__file__).resolve().parents[1] / "agents"


def _clean(outcome) -> bool:
    return outcome.finished and outcome.collisions == 0 and outcome.max_offset <= CLEAN_OFFSET


def _all_clean(outcomes) -> bool:
    return len(outcomes) > 0 and all(_clean(o) for o in outcomes)


def _times(outcomes):
    return [o.total_time for o in outcomes]


def _median_spread(outcomes):
    times = _times(outcomes)
    return float(np.median(times)), max(times) - min(times)


def _collisions(outcomes):
    return [o.collisions for o in outcomes]


def _assert_clean_row(outcomes, median, spread=None, n=5):
    assert len(outcomes) == n and _all_clean(outcomes), outcomes
    got_median, got_spread = _median_spread(outcomes)
    assert got_median == pytest.approx(median, abs=TICK), outcomes
    if spread is not None:
        assert got_spread == pytest.approx(spread, abs=TICK), outcomes
    assert all(o.spins == 0 for o in outcomes), outcomes


def _assert_one_clean(outcomes, time):
    (outcome,) = outcomes
    assert _clean(outcome) and outcome.spins == 0, outcome
    assert outcome.total_time == pytest.approx(time, abs=TICK), outcome


def _assert_spins(outcomes, spins):
    (outcome,) = outcomes
    assert not outcome.finished and outcome.spins == spins, outcome


# --- Unit 6 ------------------------------------------------------------------------------------------


def test_u6_1_the_unit_5_agent_spins_or_runs_wide_on_the_sliding_cars(speed_premise):
    (spin,) = speed_premise["u6-flat-dynamic-test-circuit"]
    assert (spin.spins, spin.collisions, spin.finished) == (40, 40, False), spin
    (spin,) = speed_premise["u6-flat-carla0-test-circuit"]
    assert (spin.spins, spin.collisions, spin.finished) == (39, 39, False), spin
    (wide,) = speed_premise["u6-flat-dynamic-monza-like"]
    assert (wide.spins, wide.collisions, wide.finished) == (0, 23, False), wide
    _assert_one_clean(speed_premise["u6-flat-dynamic-oval"], 216.50)


U6_DYNAMIC = {  # A_LAT: a clean time, or ("spins", the spin count)
    "test-circuit": {5.0: 433.95, 6.0: 423.70, 7.0: 417.65, 8.0: 413.55, 9.0: 411.05, 9.25: 410.50,
                     9.5: 410.05, 9.75: ("spins", 36), 10.0: ("spins", 37)},
    "monza-like": {5.0: 891.85, 6.0: 881.80, 7.0: 875.70, 8.0: 871.55, 9.0: 868.75, 9.25: 868.15,
                   9.5: ("spins", 11), 9.75: ("spins", 21), 10.0: ("spins", 21)},
}
U6_CARLA0 = {
    "test-circuit": {5.0: 434.70, 6.0: 424.30, 7.0: 418.40, 8.0: ("spins", 19)},
    "monza-like": {5.0: 892.60, 6.0: 882.45, 7.0: 876.30, 8.0: 872.15, 9.0: ("spins", 21)},
}


def _assert_cell(outcomes, pin):
    if isinstance(pin, tuple):
        _assert_spins(outcomes, pin[1])
    else:
        _assert_one_clean(outcomes, pin)


@pytest.mark.parametrize("track", sorted(U6_DYNAMIC))
def test_u6_2_the_cap_is_clean_until_just_under_mu_g(speed_premise, track):
    for a_lat, pin in U6_DYNAMIC[track].items():
        _assert_cell(speed_premise[f"u6-dynamic-{track}-{a_lat}"], pin)


@pytest.mark.parametrize("track", sorted(U6_CARLA0))
def test_u6_3_the_carla_like_edge_is_lower(speed_premise, track):
    for a_lat, pin in U6_CARLA0[track].items():
        _assert_cell(speed_premise[f"u6-carla0-{track}-{a_lat}"], pin)
    # the edge moves down: the last clean A_LAT on carla_like is below DynamicCar()'s
    def edge(table):
        return max(a for a, pin in table.items() if not isinstance(pin, tuple))
    assert edge(U6_CARLA0[track]) < edge(U6_DYNAMIC[track])


U6_REF = {"oval": (216.50, 0.10), "test-circuit": (422.65, 0.30), "monza-like": (880.50, 0.15)}


@pytest.mark.parametrize("track", sorted(U6_REF))
def test_u6_4_the_unit_6_reference_is_clean_on_the_noisy_carla_like_car(speed_premise, track):
    _assert_clean_row(speed_premise[f"u6-ref-{track}"], *U6_REF[track])


# --- Unit 7 ------------------------------------------------------------------------------------------


def test_u7_1_the_lookahead_must_grow_at_45_m_s(speed_premise):
    assert _collisions(speed_premise["u7-ppk-0.3"]) == [10, 9, 8, 9, 10]
    assert _collisions(speed_premise["u7-ppk-0.4"]) == [6, 6, 6, 6, 6]
    reference = speed_premise["u7-ref-test-circuit"][:5]
    assert _all_clean(reference)
    for k in (0.6, 0.7):
        longer = speed_premise[f"u7-ppk-{k}"]
        _assert_clean_row(longer, 304.20, 0.15)
        assert not noise_aware_better(_times(longer), _times(reference))  # not faster than 0.5


U7_LEAD = {  # (A_DEC, A_LAT): the collision lists at 0.15 s; the 0.3 s cell's median and per-seed max |offset|
    (4.0, 5.0): ([6, 5, 6, 6, 5], 303.25, [1.55, 1.55, 1.56, 1.56, 1.57]),
    (6.0, 4.0): ([5, 5, 1, 5, 3], 311.40, [1.47, 1.60, 1.49, 1.49, 1.53]),
}


@pytest.mark.parametrize(("a_dec", "a_lat"), sorted(U7_LEAD))
def test_u7_2_a_short_lead_crashes_at_the_grid_edge(speed_premise, a_dec, a_lat):
    collisions, median, max_offsets = U7_LEAD[(a_dec, a_lat)]
    short = speed_premise[f"u7-lead-0.15-{a_dec}-{a_lat}"]
    assert _collisions(short) == collisions
    assert not any(_clean(o) for o in short), short
    lead = speed_premise[grid_key(a_dec, a_lat)]
    _assert_clean_row(lead, median)
    assert [o.max_offset for o in lead] == pytest.approx(max_offsets, abs=OFFSET_TOL)


U7_GRID_LAST_CLEAN = {3.0: 308.45, 4.0: 303.25, 4.5: 303.40, 5.0: 300.90, 6.0: 304.15}  # median, seeds 0-4
U7_GRID_FIRST_UNCLEAN = {3.0: [6, 6], 4.0: [6, 6], 4.5: [1], 5.0: [6, 6], 6.0: [4, 4]}  # collision lists


def test_u7_3_the_clean_edge_falls_as_the_braking_rate_rises(speed_premise):
    medians = {}
    for a_dec, (clean, unclean, _) in U7_GRID_EDGE.items():
        last = speed_premise[grid_key(a_dec, clean)][:5]
        _assert_clean_row(last, U7_GRID_LAST_CLEAN[a_dec])
        medians[(a_dec, clean)] = _median_spread(last)[0]
        first = speed_premise[grid_key(a_dec, unclean)]
        assert _collisions(first) == U7_GRID_FIRST_UNCLEAN[a_dec], first
        assert not any(_clean(o) for o in first), first
    edges = [U7_GRID_EDGE[a_dec][0] for a_dec in sorted(U7_GRID_EDGE)]
    assert edges == sorted(edges, reverse=True) and edges[0] > edges[-1], edges
    assert min(medians, key=medians.get) == (5.0, 4.8), medians  # the fastest clean cell
    assert U7_GRID_EDGE[5.0][0] == 4.8  # the reference's A_LAT 4.6 is one grid step inside it


U7_REF_DETERMINISTIC = {
    "carla0": {"oval": 152.75, "test-circuit": 304.80, "monza-like": 515.45},
    "dynamic": {"oval": 152.15, "test-circuit": 303.45, "monza-like": 514.10},
}


def test_u7_4_the_unit_7_reference(speed_premise):
    _assert_clean_row(speed_premise["u7-ref-test-circuit"], 304.15, 0.20, n=10)
    for track, median, spread, max_offset in (("oval", 152.75, 0.10, 0.81), ("monza-like", 515.10, 0.15, 1.67)):
        outcomes = speed_premise[f"u7-ref-{track}"]
        _assert_clean_row(outcomes, median, spread)
        assert float(np.median([o.max_offset for o in outcomes])) == pytest.approx(max_offset, abs=OFFSET_TOL)
    for car, times in U7_REF_DETERMINISTIC.items():
        for track, time in times.items():
            _assert_one_clean(speed_premise[f"u7-ref-{car}-{track}"], time)


@pytest.mark.parametrize("track", sorted(U6_REF))
def test_u7_5_unit_7_beats_unit_6_beyond_the_noise(speed_premise, track):
    unit_7 = speed_premise[f"u7-ref-{track}"][:5]
    unit_6 = speed_premise[f"u6-ref-{track}"]
    assert _all_clean(unit_7) and _all_clean(unit_6)
    if track == "test-circuit":
        assert _median_spread(unit_7)[0] == pytest.approx(304.15, abs=TICK)
    assert noise_aware_better(_times(unit_7), _times(unit_6))


def test_u7_6_each_knob_alone_is_clean_but_the_stack_is_not(speed_premise):
    for section, knob in enumerate(SINGLES):
        alone = speed_premise[grip_key(knobs(**{f"s{section}": knob}))]
        assert len(alone) == 5 and _all_clean(alone), (section, knob, alone)
    stack = speed_premise[grip_key(SINGLES)]
    assert _collisions(stack) == [23] * 10, stack
    assert not any(_clean(o) for o in stack), stack


U7_SEQUENTIAL_LATER = {2: [0, 0, 0, 0, 18], 3: [0, 18, 0, 0, 18], 4: [0, 0, 0, 0, 18], 5: [0, 0, 0, 0, 18]}


def test_u7_7_the_sequential_pass_and_the_ten_seed_check(speed_premise):
    # section 0: keeps 1.2; 1.3 is unclean
    _assert_clean_row(speed_premise[grip_key(knobs(s0=1.2))], 303.10)
    assert _collisions(speed_premise[grip_key(knobs(s0=1.3))]) == [9, 0, 0, 4, 13]
    # section 1 on top: keeps 1.4 (the edge vector's seeds 0-4); 1.5 is unclean although it was clean alone
    edge = speed_premise[grip_key(EDGE_VECTOR)]
    _assert_clean_row(edge[:5], 298.35)
    assert _collisions(speed_premise[grip_key(knobs(s0=1.2, s1=1.5))]) == [23] * 5
    assert _all_clean(speed_premise[grip_key(knobs(s1=1.5))])
    # sections 2-5: the first step, 1.05, is unclean
    for section, collisions in U7_SEQUENTIAL_LATER.items():
        grip = list(EDGE_VECTOR)
        grip[section] = 1.05
        assert _collisions(speed_premise[grip_key(tuple(grip))]) == collisions, section
    # the ten-seed check of the five-seed result fails on seeds 5 and 8
    assert _collisions(edge) == [0, 0, 0, 0, 0, 18, 0, 0, 18, 0], edge
    assert [seed for seed, o in enumerate(edge) if not _clean(o)] == [5, 8]
    assert [edge[5].max_offset, edge[8].max_offset] == pytest.approx([6.48, 6.38], abs=OFFSET_TOL)
    # one step back on the raised knobs: clean on seeds 0-9
    _assert_clean_row(speed_premise[grip_key(ACCEPTED)], 299.60, 0.15, n=10)


def test_u7_8_per_section_knobs_beat_the_best_global_setting(speed_premise):
    accepted = speed_premise[grip_key(ACCEPTED)]
    reference = speed_premise["u7-ref-test-circuit"]
    best_global = speed_premise[grid_key(5.0, 4.8)]
    _assert_clean_row(accepted, 299.60, 0.15, n=10)
    _assert_clean_row(reference, 304.15, 0.20, n=10)
    _assert_clean_row(best_global, 300.93, 0.20, n=10)
    assert noise_aware_better(_times(accepted), _times(reference))  # with margin
    assert noise_aware_better(_times(accepted), _times(best_global))  # against the edge


# --- fast checks (no shared pool) --------------------------------------------------------------------


def _load_agent(name):
    from racekit.runner import load_submission, shim_installed

    with shim_installed():
        agent_class, _ = load_submission(AGENTS / name)
    return agent_class


@pytest.mark.parametrize("track_name", ["oval", "test-circuit", "monza-like"])
def test_u7_9_the_agents_section_map_is_racekits(track_name):
    from racekit.tracks import grip_sections, load_track

    track = load_track(track_name)
    agent = _load_agent("unit-07.py")(track.waypoints, None)
    assert agent.section == grip_sections(track).tolist()


def _race(agent, constants, track, car, tmp_path):
    from racekit.runner import run_race
    from racekit.variants import write_variant

    submission = AGENTS / agent
    if constants:
        submission = write_variant(submission, tmp_path / f"variant_{agent}",
                                   {name: repr(value) for name, value in constants})
    return run_race(submission, track, car=car, seed=0, max_seconds=1500.0)


def _assert_same_race(first, second):
    assert first.total_time == second.total_time and first.collisions == second.collisions
    assert first.respawn_causes == second.respawn_causes
    assert first.telemetry.dtype == second.telemetry.dtype
    assert first.telemetry.tobytes() == second.telemetry.tobytes()  # identical to the tick


def test_unit_06_flat_races_exactly_like_unit_05(tmp_path):
    from racekit.cars import KinematicCar

    unit_05 = _race("unit-05.py", (), "test-circuit", KinematicCar(jitter=0.05), tmp_path)
    flat = _race("unit-06.py", (("SPEED_MODE", "flat"),), "test-circuit", KinematicCar(jitter=0.05), tmp_path)
    _assert_same_race(unit_05, flat)


def test_unit_07_cap_races_exactly_like_unit_06(tmp_path):
    from racekit.cars import carla_like

    unit_06 = _race("unit-06.py", (), "test-circuit", carla_like(noise=True), tmp_path)
    cap = _race("unit-07.py", (("SPEED_MODE", "cap"), ("TARGET_SPEED", 20.0), ("PP_K", 0.3), ("A_LAT", 6.0)),
                "test-circuit", carla_like(noise=True), tmp_path)
    _assert_same_race(unit_06, cap)
