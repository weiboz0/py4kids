"""The Unit 4 and Unit 5 premises (plan roar-005 U4.2-U4.4, U5.2-U5.5), raced with the reference
submissions in the session's shared parallel pool (``_agent_premise.py``, ``_premise.race_all``).

Every multi-seed claim of the plan's Gates is asserted here in full; the milestones assert a
trimmed subset. The pins come from the probes (``p6_full.txt``, ``p7.txt``), reproduced to the bit
by the shipped agents and ``KinematicCar(lag_ticks=...)``; a miss means stop, amend and re-gate,
never a silent re-pin.

Tolerances (the plan's Gates header): deterministic times and jittered median times within one
tick (±0.05 s); RMS |offset| (medians and ranges) within ±0.0005 m and max |offset| within ±0.005 m;
clean/crash outcomes and per-seed collision lists exact; every noise-aware comparison strict.
"""

from __future__ import annotations

import numpy as np
import pytest
from _agent_premise import LOOKAHEADS, TRACKS
from racekit.measure import noise_aware_better

TICK = 0.05 + 1e-9
RMS_TOL = 0.0005 + 1e-9
MAX_TOL = 0.005 + 1e-9


def _clean(outcomes):
    return len(outcomes) > 0 and all(o.finished and o.collisions == 0 for o in outcomes)


def _rms(outcomes):
    """(median, range) of the per-seed RMS |offset|."""
    values = [o.rms for o in outcomes]
    return float(np.median(values)), max(values) - min(values)


def _times(outcomes):
    """(median, spread) of the per-seed race times."""
    values = [o.total_time for o in outcomes]
    return float(np.median(values)), max(values) - min(values)


def _collisions(outcomes):
    return [o.collisions for o in outcomes]


# --- U4.2 / U5.2: the reference submissions, jitter 0 ------------------------------------------------

EXACT = {  # track: (time, RMS, max |offset|)
    "u4": {"oval": (216.35, 0.0034, 0.009), "test-circuit": (400.55, 0.0139, 0.136),
           "monza-like": (858.45, 0.0112, 0.153)},
    "u5": {"oval": (216.35, 0.0035, None), "test-circuit": (400.50, 0.0193, None),
           "monza-like": (858.45, 0.0157, None)},
}


@pytest.mark.parametrize("track", TRACKS)
@pytest.mark.parametrize("name", sorted(EXACT))
def test_u4_2_u5_2_the_reference_submissions_race_the_pinned_times(agent_premise, name, track):
    (outcome,) = agent_premise[f"{name}-exact-{track}"]
    time, rms, max_offset = EXACT[name][track]
    assert outcome.finished and outcome.collisions == 0, outcome
    assert outcome.total_time == pytest.approx(time, abs=TICK), outcome
    assert outcome.rms == pytest.approx(rms, abs=RMS_TOL), outcome
    if max_offset is not None:
        assert outcome.max_offset == pytest.approx(max_offset, abs=MAX_TOL), outcome


@pytest.mark.parametrize("track", TRACKS)
def test_u5_2_steering_pid_races_exactly_like_unit_04(agent_premise, track):
    assert agent_premise[f"u5-pid-exact-{track}"] == agent_premise[f"u4-exact-{track}"]


# --- U4.3: the scorecard (jitter 0.05, seeds 0-4) ------------------------------------------------------

SCORECARD = {  # track: (RMS median, range, time median, spread) for Unit 4, then the starter
    "u4": {"oval": (0.1041, 0.0062, 216.40, 0.05), "test-circuit": (0.1048, 0.0050, 400.60, 0.10),
           "monza-like": (0.1029, 0.0042, 858.55, 0.00)},
    "starter": {"oval": (0.1397, 0.0099, 220.75, 0.35), "test-circuit": (0.1586, 0.0055, 407.50, 0.65),
                "monza-like": (0.1416, 0.0040, 870.50, 0.45)},
}


def _assert_row(outcomes, rms_median, rms_range, time_median=None, time_spread=None):
    assert len(outcomes) == 5 and _clean(outcomes), outcomes
    median, spread = _rms(outcomes)
    assert median == pytest.approx(rms_median, abs=RMS_TOL), (median, outcomes)
    if rms_range is not None:
        assert spread == pytest.approx(rms_range, abs=RMS_TOL), (spread, outcomes)
    if time_median is not None:
        times_median, times_spread = _times(outcomes)
        assert times_median == pytest.approx(time_median, abs=TICK), outcomes
        if time_spread is not None:
            assert times_spread == pytest.approx(time_spread, abs=TICK), outcomes


@pytest.mark.parametrize("track", TRACKS)
def test_u4_3_unit_04_beats_the_starter_beyond_the_noise(agent_premise, track):
    unit_04, starter = agent_premise[f"u4-{track}"], agent_premise[f"starter-{track}"]
    _assert_row(unit_04, *SCORECARD["u4"][track])
    _assert_row(starter, *SCORECARD["starter"][track])
    (u4_median, u4_range), (st_median, st_range) = _rms(unit_04), _rms(starter)
    assert st_median - u4_median > max(u4_range, st_range)  # the RMS gap exceeds the larger range
    assert noise_aware_better([o.total_time for o in unit_04], [o.total_time for o in starter])


# --- U4.4: the ablations --------------------------------------------------------------------------------

NO_FEEDFORWARD = {"oval": 0.1327, "test-circuit": 0.1794, "monza-like": 0.1374}


@pytest.mark.parametrize("track", TRACKS)
def test_u4_4_without_the_feedforward_the_rms_is_worse(agent_premise, track):
    no_ff = agent_premise[f"u4-noff-{track}"]
    _assert_row(no_ff, NO_FEEDFORWARD[track], None)
    assert _rms(no_ff)[0] > _rms(agent_premise[f"u4-{track}"])[0]
    if track == "test-circuit":  # worse than the starter there
        assert _rms(no_ff)[0] > _rms(agent_premise[f"starter-{track}"])[0]


def test_u4_4_without_the_d_term_every_seed_crashes(agent_premise):
    no_d = agent_premise["u4-nod-test-circuit"]
    assert _collisions(no_d) == [30, 32, 31, 29, 30], no_d
    assert not any(o.finished for o in no_d)


# --- U5.3: pure pursuit and Stanley at 20 m/s (lag 0) -----------------------------------------------------

PURSUIT_20 = {"oval": (0.1422, 0.0107), "test-circuit": (0.1481, 0.0050), "monza-like": (0.1445, 0.0022)}
STANLEY_20 = {"oval": 0.0987, "test-circuit": 0.1043, "monza-like": 0.0981}


@pytest.mark.parametrize("track", TRACKS)
def test_u5_3_pursuit_does_not_beat_unit_04_without_delay(agent_premise, track):
    pursuit, stanley = agent_premise[f"pursuit-{track}"], agent_premise[f"stanley-{track}"]
    _assert_row(pursuit, *PURSUIT_20[track])
    _assert_row(stanley, STANLEY_20[track], None)
    assert _rms(pursuit)[0] > _rms(agent_premise[f"u4-{track}"])[0]


# --- U5.4: the delay study (test-circuit, 30 m/s, jitter 0.05, max_seconds=400) -------------------------

LAG_0 = {"pd": (0.1295, 0.0060), "stanley": (0.1582, 0.0139), "pursuit": (0.3097, 0.0153),
         "starter": (0.2346, 0.0167), "detuned": (0.3538, 0.0280)}


@pytest.mark.parametrize("name", sorted(LAG_0))
def test_u5_4_lag_0_every_controller_is_clean(agent_premise, name):
    outcomes = agent_premise[f"delay-{name}-lag0"]
    assert _collisions(outcomes) == [0, 0, 0, 0, 0], outcomes
    _assert_row(outcomes, *LAG_0[name])


def test_u5_4_lag_2_the_tight_controllers_crash_on_every_seed(agent_premise):
    assert _collisions(agent_premise["delay-pd-lag2"]) == [41, 42, 43, 43, 40]
    assert _collisions(agent_premise["delay-stanley-lag2"]) == [20, 16, 16, 17, 20]
    starter = agent_premise["delay-starter-lag2"]  # does not finish inside the cap
    assert _collisions(starter) == [0, 1, 0, 0, 0] and not any(o.finished for o in starter), starter


def test_u5_4_lag_2_pursuit_and_the_detuned_pd_are_clean(agent_premise):
    pursuit, detuned = agent_premise["delay-pursuit-lag2"], agent_premise["delay-detuned-lag2"]
    _assert_row(pursuit, 0.4526, 0.0234, 269.70, 0.20)
    _assert_row(detuned, 0.5149, 0.0376, 269.70, 0.15)


def test_u5_4_the_gate(agent_premise):
    # at lag 2 pure pursuit beats the detuned PD beyond both ranges ...
    (p_median, p_range), (d_median, d_range) = (_rms(agent_premise["delay-pursuit-lag2"]),
                                                _rms(agent_premise["delay-detuned-lag2"]))
    assert d_median - p_median > max(p_range, d_range)
    # ... and at lag 0 Unit 4's PD beats pure pursuit beyond both ranges
    (pd_median, pd_range), (p0_median, p0_range) = (_rms(agent_premise["delay-pd-lag0"]),
                                                    _rms(agent_premise["delay-pursuit-lag0"]))
    assert p0_median - pd_median > max(pd_range, p0_range)
    # the tight laws collide on every seed at lag 2; pure pursuit is clean 5/5
    for name in ("pd", "stanley"):
        assert all(o.collisions > 0 for o in agent_premise[f"delay-{name}-lag2"])
    assert _clean(agent_premise["delay-pursuit-lag2"])


# --- U5.5: the lookahead sweep ------------------------------------------------------------------------

SWEEP = {0: {0.2: 0.1800, 0.3: 0.3097, 0.4: 0.4656, 0.5: 0.6477},
         2: {0.2: 1.2972, 0.3: 0.4526, 0.4: 0.5625, 0.5: 0.7203}}


def _sweep(agent_premise, k, lag):
    return agent_premise[f"delay-pursuit-lag{lag}" if k == 0.3 else f"sweep-{k}-lag{lag}"]


@pytest.mark.parametrize("lag", sorted(SWEEP))
def test_u5_5_the_best_lookahead_grows_with_the_delay(agent_premise, lag):
    medians = {}
    for k in LOOKAHEADS:
        outcomes = _sweep(agent_premise, k, lag)
        _assert_row(outcomes, SWEEP[lag][k], None)
        medians[k] = _rms(outcomes)[0]
    assert min(medians, key=medians.get) == (0.2 if lag == 0 else 0.3), medians
    if lag == 2:  # the short lookahead weaves
        _assert_row(_sweep(agent_premise, 0.2, 2), SWEEP[2][0.2], None, 292.35, 5.75)
