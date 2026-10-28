"""Checkpoint A's gates (plan roar-007 CP.2-CP.5): a clean agent on a track it was not tuned for.

The races run in the session's shared parallel pool (``_checkpoint_premise.py``, ``_premise.race_all``):
18 cells x race seeds 0-4 = 90 races, all on ``carla_like(noise=True)`` at ``max_seconds=450``, with
Unit 7's reference settings (A_DEC 5.0, PP_K 0.5, PROFILE_LEAD_S 0.3, GRIP all 1.0) and A_LAT
changed through ``write_variant``. The tracks are loaded by their literal generated names
(``test-circuit``, ``test-circuit-seed1`` ... ``test-circuit-seed4``, ``test-circuit-seed2026``): the
carla-like car's hidden grip is keyed to the track name, so a rename changes the car and invalidates
every pin. The pins come from the probes (``q22``-``q29``); a miss means stop, amend and re-gate,
never a silent re-pin.

Tolerances (Unit 7's): medians and quoted spreads within ±0.05 s, max |offset| within ±0.01 m where
quoted. A race is *clean* when it finishes with 0 collisions and its max |offset| on driving rows is
at most 2 m; an unclean cell is asserted only "not clean", never a collision count (that count
depends on the time cap).
"""

from __future__ import annotations

import numpy as np
import pytest
from _checkpoint_premise import (
    CHECKPOINT,
    CHECKPOINT_RACE,
    TRAINING,
    UNIT_06_RACE,
    cell_key,
    checkpoint_a_jobs,
)
from conftest import RACEKIT
from racekit.check_submission import check_submission

TICK = 0.05 + 1e-9
OFFSET_TOL = 0.01 + 1e-9
CLEAN_OFFSET = 2.0  # m: the clean rule's limit on max |offset|
TARGET = 330.0  # s: Checkpoint A's target median on the checkpoint track
CHECKPOINT_A = RACEKIT / "agents" / "checkpoint-a.py"
UNIT_07 = RACEKIT / "agents" / "unit-07.py"

# CP.3: the family's medians (s) at 4.4 (the edge) and 4.2 (the margin value), in TRAINING's order
FAMILY_EDGE = {4.4: (307.55, 305.40, 307.15, 308.15, 308.05), 4.2: (311.10, 308.75, 310.55, 311.60, 311.55)}


def _clean(outcome) -> bool:
    return outcome.finished and outcome.collisions == 0 and outcome.max_offset <= CLEAN_OFFSET


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


def test_the_job_list_is_the_plans_18_cells_and_90_races():
    jobs = checkpoint_a_jobs()
    assert len(jobs) == 18
    assert sum(len(job.seeds) for job in jobs.values()) == 90
    assert all(job.seeds == (0, 1, 2, 3, 4) for job in jobs.values())
    assert all(job.car == "carla" and job.max_seconds == 450.0 for job in jobs.values())
    # the literal track names (the hidden grip is keyed to them)
    assert TRAINING == ("test-circuit", "test-circuit-seed1", "test-circuit-seed2", "test-circuit-seed3",
                        "test-circuit-seed4")
    assert CHECKPOINT == "test-circuit-seed2026"
    assert {job.track for job in jobs.values()} == set(TRAINING) | {CHECKPOINT}


def test_checkpoint_a_is_unit_07_with_a_lat_4_2():
    """``agents/checkpoint-a.py`` is ``agents/unit-07.py`` with a header comment and A_LAT = 4.2."""
    unit7 = UNIT_07.read_text(encoding="utf-8").splitlines()
    ours = CHECKPOINT_A.read_text(encoding="utf-8").splitlines()
    header = ours[: len(ours) - len(unit7)]
    assert header and all(line.startswith("#") for line in header)
    body = ours[len(header):]
    changed = [(a, b) for a, b in zip(unit7, body) if a != b]
    assert len(body) == len(unit7) and len(changed) == 1, changed
    old, new = changed[0]
    assert old.startswith("A_LAT = 4.6  #") and new == old.replace("A_LAT = 4.6", "A_LAT = 4.2")


# --- CP.2: one track is not enough ------------------------------------------------------------------


def test_cp2_test_circuit_edge_is_4_8_and_the_margin_value_is_4_6(checkpoint_a):
    _assert_clean_row(checkpoint_a[cell_key("test-circuit", 4.8)], 300.90)
    assert not _all_clean(checkpoint_a[cell_key("test-circuit", 5.0)])
    # the margin rule's 4.6 is clean on test-circuit (Unit 7's pin) ...
    _assert_clean_row(checkpoint_a[cell_key("test-circuit", 4.6)], 304.15)


def test_cp2_the_margin_value_is_not_clean_on_training_seed_1(checkpoint_a):
    outcomes = checkpoint_a[cell_key("test-circuit-seed1", 4.6)]
    assert len(outcomes) == 5
    assert [_clean(o) for o in outcomes] == [True, False, True, True, True], outcomes  # race seed 1 fails


# --- CP.3: the family edge ----------------------------------------------------------------------------


@pytest.mark.parametrize("a_lat", (4.4, 4.2))
def test_cp3_clean_on_every_training_track(checkpoint_a, a_lat):
    for track, median in zip(TRAINING, FAMILY_EDGE[a_lat]):
        _assert_clean_row(checkpoint_a[cell_key(track, a_lat)], median)


def test_cp3_4_6_is_not_clean_on_the_family(checkpoint_a):
    # 4.6 is clean on test-circuit but not on seed 1, so the family's edge is 4.4 and the margin rule
    # gives 4.2 (one grid step of 0.2 back)
    assert _all_clean(checkpoint_a[cell_key("test-circuit", 4.6)])
    assert not _all_clean(checkpoint_a[cell_key("test-circuit-seed1", 4.6)])


# --- CP.4: the checkpoint race ------------------------------------------------------------------------


def test_cp4_race_day_is_clean_and_within_the_target(checkpoint_a):
    outcomes = checkpoint_a[CHECKPOINT_RACE]
    _assert_clean_row(outcomes, 310.80)
    assert _spread(outcomes) == pytest.approx(0.20, abs=TICK), outcomes
    worst = max(o.max_offset for o in outcomes)
    assert worst <= CLEAN_OFFSET and worst == pytest.approx(1.44, abs=OFFSET_TOL), outcomes
    assert _median(outcomes) <= TARGET


def test_cp4_the_unit_6_agent_is_clean_but_misses_the_target(checkpoint_a):
    outcomes = checkpoint_a[UNIT_06_RACE]
    _assert_clean_row(outcomes, 420.40)
    assert _median(outcomes) > TARGET


def test_cp4_the_checkpoint_tracks_neighbours_of_the_frozen_value(checkpoint_a):
    _assert_clean_row(checkpoint_a[cell_key(CHECKPOINT, 4.4)], 307.30)
    # Unit 7's single-track value does not survive the checkpoint track
    outcomes = checkpoint_a[cell_key(CHECKPOINT, 4.6)]
    assert len(outcomes) == 5 and not any(_clean(o) for o in outcomes), outcomes  # not clean on any seed


# --- CP.5 -----------------------------------------------------------------------------------------------


def test_cp5_check_submission_passes_on_checkpoint_a():
    # the isolated Python 3.8 run covers every file in agents/ (test_racekit_check_submission.py)
    report = check_submission(CHECKPOINT_A)
    assert report.ok, str(report)
