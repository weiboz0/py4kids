"""The Unit 6 and Unit 7 premises (plan roar-004 G4.3, G4.5), raced with the data-side driver
(``roar/data/drivers.py``) in the session's shared parallel pool (``_premise.py``).

The plan's probe values (frozen prototype ``dyn_af442a6f.py``, reproduced on the shipped code) are
quoted beside each gate; a miss means stop, amend and re-gate, never a silent re-pin.
"""

from __future__ import annotations

import numpy as np
from _premise import (
    UNIT7_GRID_CLEAN,
    UNIT7_GRID_UNCLEAN,
    UNIT7_GRID_UNCLEAN_SEEDS,
    UNIT7_STACK_SEEDS,
    unit7_singles,
)


def _clean(outcomes):
    return all(o.finished and o.collisions == 0 for o in outcomes)


def _median_spread(outcomes):
    times = [o.total_time for o in outcomes]
    return float(np.median(times)), max(times) - min(times)


# --- G4.3: the Unit 6 premise on DynamicCar() defaults ---------------------------------------------


def test_g4_3_a_flat_20_m_s_runs_wide_on_test_circuit(premise):
    (flat,) = premise["u6-flat-dynamic"]
    assert not flat.finished and flat.collisions >= 5, flat  # probe: 16 collisions in 1500 s
    assert flat.spins == 0  # it runs wide at the tight corners; it does not spin


def test_g4_3_the_curvature_limited_speed_finishes_clean(premise):
    (limited,) = premise["u6-limited-dynamic"]
    assert limited.finished and limited.collisions == 0 and limited.spins == 0, limited  # probe 413.70 s


def test_g4_3_the_flat_driver_is_clean_on_the_kinematic_car(premise):
    (kinematic,) = premise["u6-flat-kinematic"]
    assert kinematic.finished and kinematic.collisions == 0, kinematic


# --- G4.5: the Unit 7 premise (carla_like(noise=True), test-circuit, seeds 0–4) --------------------


def test_g4_5_global_3_7_is_the_fastest_clean_global_on_the_grid(premise):
    medians = {}
    for a_lat in UNIT7_GRID_CLEAN:
        outcomes = premise[f"u7-global-{a_lat}"]
        assert len(outcomes) == 5 and _clean(outcomes), (a_lat, outcomes)
        medians[a_lat] = _median_spread(outcomes)[0]
    # probe medians 327.40 / 325.05 / 323.05 s
    assert medians[3.7] < medians[3.6] < medians[3.5], medians
    for a_lat in UNIT7_GRID_UNCLEAN:  # probe: collisions on 4/5, 5/5 and 5/5 seeds
        outcomes = premise[f"u7-global-{a_lat}"]
        assert len(outcomes) == 5, (a_lat, outcomes)
        colliding = tuple(seed for seed, o in enumerate(outcomes) if o.collisions > 0)
        assert colliding == UNIT7_GRID_UNCLEAN_SEEDS[a_lat], (a_lat, outcomes)


def test_g4_5_section_grip_beats_the_best_global_beyond_the_noise(premise):
    combined, best = premise["u7-combined"], premise["u7-global-3.7"]
    assert len(combined) == 5 and _clean(combined), combined
    median_combined, spread_combined = _median_spread(combined)  # probe 313.50 s, spread 0.45 s
    median_best, spread_best = _median_spread(best)  # probe 323.05 s, spread 0.40 s
    gain = median_best - median_combined  # probe 9.55 s
    assert gain > max(spread_combined, spread_best), (gain, spread_combined, spread_best)
    assert gain >= 5.0, gain


def test_g4_5_knobs_clean_alone_can_crash_when_stacked(premise):
    singles = list(unit7_singles())
    assert [section for section, _ in singles] == [0, 1, 2, 3, 5]
    for section, _ in singles:  # probe medians 325.35 / 321.30 / 323.60 / 324.95 / 325.25 s
        outcomes = premise[f"u7-single-{section}"]
        assert len(outcomes) == 5 and _clean(outcomes), (section, outcomes)
    assert _clean(premise["u7-global-3.5"])  # the base itself (section 4's ×1)
    stack = premise["u7-stack"]
    assert len(stack) == 5 and not _clean(stack), stack
    assert tuple(seed for seed, o in enumerate(stack) if o.collisions > 0) == UNIT7_STACK_SEEDS, stack
