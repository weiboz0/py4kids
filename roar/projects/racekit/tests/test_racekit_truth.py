"""The carla-like car's grip: the public section rule and the hard-pinned μ tables (plan roar-004)."""

from __future__ import annotations

import numpy as np
import pytest
from racekit import _truth
from racekit.tracks import GRIP_SECTIONS, TRACK_NAMES, grip_sections, load_track

# Drawn with random.Random seeded from sha256("racekit-grip:" + name), uniform in [0.78, 1.05],
# rounded to 3 decimals (plan roar-004 "Probe evidence"). Hard-pinned: a change is a re-gate.
PINNED_MU = {
    "oval": (0.930, 1.001, 0.802, 0.975, 1.024, 0.880),
    "test-circuit": (0.817, 1.002, 0.886, 0.816, 0.849, 0.838),
    "monza-like": (0.836, 0.941, 0.951, 0.940, 0.996, 0.819),
}


@pytest.mark.parametrize("name", TRACK_NAMES)
def test_the_named_tracks_mu_tables_are_pinned(name):
    assert _truth.grip_table(name) == PINNED_MU[name]


def test_any_track_name_gets_a_reproducible_table_in_range():
    table = _truth.grip_table("checkpoint-seed-7")
    assert table == _truth.grip_table("checkpoint-seed-7") != _truth.grip_table("checkpoint-seed-8")
    assert len(table) == GRIP_SECTIONS == 6
    assert all(0.78 <= mu <= 1.05 and round(mu, 3) == mu for mu in table)


@pytest.mark.parametrize("name", TRACK_NAMES)
def test_grip_sections_are_equal_arc_length_sixths_from_the_start(name):
    track = load_track(name)
    sections = grip_sections(track)
    assert sections.shape == (len(track),) and sections[0] == 0 and sections[-1] == GRIP_SECTIONS - 1
    assert (np.diff(sections) >= 0).all() and set(sections.tolist()) == set(range(GRIP_SECTIONS))
    lengths = [np.ptp(track.s[sections == i]) for i in range(GRIP_SECTIONS)]
    assert max(lengths) - min(lengths) <= 2.1 * 2  # equal to within about a waypoint spacing each end
    for i in range(1, GRIP_SECTIONS):
        first = int(np.argmax(sections == i))
        assert track.s[first - 1] < i * track.length / GRIP_SECTIONS <= track.s[first]
