"""The capstone gates (plan roar-014 C14.0-C14.1): the reference against the starter made clean.

Every race is on ``monza-like``, the nominal ``carla_like(noise=True)``, 3 laps.

* C14.0: the shipped ``agents/starter.py`` (Unit 1's file, clean on ``KinematicCar``) crash-loops on
  this car: at seed 0, capped at 120 s, it has not finished and has collided at least once.
* C14.1, the gate (design 013 §6, the capstone row): the bar is the starter made clean by its own
  knob, ``TARGET_SPEED = 14.0``, raced at seeds 0-4 capped at 1300 s (``_capstone_premise.py``, the
  ``capstone_premise`` fixture). The capstone's reference ``agents/unit-13.py`` is not raced again:
  its five races are Unit 13's U13.1 races, read from the ``race_day_premise`` fixture. All ten are
  clean at 0 collisions; the bar's times equal the probe record to a tick; ``unit-13.py`` is better
  by Unit 1's rule (``noise_aware_better``) and its median is at least 700 s faster.

A race is *clean* when it finishes with 0 collisions and its max error on driving rows is at most
2 m: from the centreline for the starter (no line in the file), from its own line for ``unit-13.py``.
The pins come from plan roar-014's probes (p3, p9); a miss means stop, amend and re-gate, never a
silent re-pin. No perturbed car (Unit 13's test cars 72-95, the capstone's 96-119, a student's own
120-143) and no sealed car (k >= 1000) is raced by this module.
"""

from __future__ import annotations

import numpy as np
import pytest
from _agent_premise import AgentJob
from _capstone_premise import (
    BAR_CAP,
    BAR_CONSTANTS,
    BAR_SPEED,
    FORBIDDEN,
    NEVER_RACED_CARS,
    SEEDS5,
    STARTER,
    STARTER_CAP,
    STARTER_CAPPED,
    bar_key,
    capstone_jobs,
)
from _line_premise import MONZA, race_line_job
from _race_day_premise import SHIPPED_13, race_key
from racekit.measure import noise_aware_better

TICK = 0.05 + 1e-9
CLEAN_ERROR = 2.0  # m: the clean rule's limit on the error (centreline for the starter, the line for unit-13)
POOLED_RACES = 5
# C14.1: the probe record (p3): the bar's per-seed times, seeds 0-4
BAR_TIMES = (1203.45, 1203.55, 1203.90, 1203.85, 1203.20)
MARGIN = 700.0  # s: the reference's median is at least this much faster than the bar's


def _clean(outcome) -> bool:
    return outcome.finished and outcome.collisions == 0 and outcome.line_error <= CLEAN_ERROR


def _one(premise, key):
    (outcome,) = premise[key]
    return outcome


def _times(outcomes):
    return [round(o.total_time, 2) for o in outcomes]


def test_the_job_list_is_the_plans_pooled_races():
    jobs = capstone_jobs()
    assert sum(len(job.seeds) for job in jobs.values()) == len(jobs) == POOLED_RACES
    assert len(set(jobs.values())) == POOLED_RACES  # each distinct race once
    for seed in SEEDS5:
        job = jobs[bar_key(seed)]
        assert job.agent == STARTER and job.constants == BAR_CONSTANTS and job.seeds == (seed,), job
        assert job.track == MONZA and job.max_seconds == BAR_CAP and job.car == "carla" and job.laps is None, job
    assert dict(BAR_CONSTANTS) == {"TARGET_SPEED": BAR_SPEED}


def test_no_perturbed_or_sealed_car_is_raced_here():
    # every race of this module is an AgentJob on the nominal carla_like(noise=True): AgentJob has no
    # perturbed-car field, so no car k in 72-143 (or k >= 1000) can be built by it
    assert "perturb" not in AgentJob._fields
    for job in [*capstone_jobs().values(), STARTER_CAPPED]:
        assert isinstance(job, AgentJob) and job.car == "carla", job
        assert job.track not in FORBIDDEN, job
    assert (min(NEVER_RACED_CARS), max(NEVER_RACED_CARS)) == (72, 143)


# --- C14.0: the shipped starter does not finish on this car -------------------------------------------------


def test_c14_0_the_shipped_starter_crash_loops_on_monza_like():
    assert STARTER_CAPPED.constants == () and STARTER_CAPPED.max_seconds == STARTER_CAP
    (outcome,) = race_line_job(STARTER_CAPPED)
    print(f"\nC14.0: {STARTER} as shipped on {MONZA}, seed 0, cap {STARTER_CAP:.0f} s: {outcome.total_time:.2f} s, "
          f"finished {outcome.finished}, {outcome.collisions} collision(s), max centreline error "
          f"{outcome.line_error:.3f} m")
    assert not outcome.finished, outcome
    assert outcome.collisions >= 1, outcome


# --- C14.1: the gate ----------------------------------------------------------------------------------------


def test_c14_1_unit_13_beats_the_starter_made_clean(capstone_premise, race_day_premise):
    bar = [_one(capstone_premise, bar_key(seed)) for seed in SEEDS5]
    reference = [_one(race_day_premise, race_key(SHIPPED_13, seed)) for seed in SEEDS5]
    for label, row in (("bar (starter, TARGET_SPEED 14.0)", bar), ("unit-13.py (U13.1's races)", reference)):
        print(f"\nC14.1: {label}: {_times(row)} median {np.median([o.total_time for o in row]):.2f}, "
              f"collisions {sum(o.collisions for o in row)}, max error {max(o.line_error for o in row):.3f} m, "
              f"clean {sum(_clean(o) for o in row)}/5")
    assert all(_clean(o) for o in bar), bar
    assert all(_clean(o) for o in reference), reference
    for seed, outcome, pinned in zip(SEEDS5, bar, BAR_TIMES):
        assert outcome.total_time == pytest.approx(pinned, abs=TICK), (seed, _times(bar))
    bar_times = [o.total_time for o in bar]
    reference_times = [o.total_time for o in reference]
    margin = float(np.median(bar_times) - np.median(reference_times))
    print(f"C14.1: margin {margin:.2f} s (at least {MARGIN:.0f}); "
          f"noise_aware_better {noise_aware_better(reference_times, bar_times)}")
    assert noise_aware_better(reference_times, bar_times), (reference_times, bar_times)
    assert margin >= MARGIN, margin
