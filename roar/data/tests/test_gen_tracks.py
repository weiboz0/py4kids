"""The seeded track generator (plan roar-001 Phase C; design 013 §4.3)."""

from __future__ import annotations

import json
import math
import time

import gen_tracks as g
import generate
import numpy as np
import pytest

LENGTH_WINDOWS = {
    "oval": (1300.0, 1500.0),  # two 300 m straights, two 120 m-radius 180° corners
    "test-circuit": (2300.0, 2800.0),  # "about 2.5 km"
    "monza-like": (5500.0, 6100.0),  # "about 5.8 km"
    # the seeded checkpoint tracks (plan roar-007): variants of test-circuit, so test-circuit's window
    "test-circuit-seed1": (2300.0, 2800.0),
    "test-circuit-seed2": (2300.0, 2800.0),
    "test-circuit-seed3": (2300.0, 2800.0),
    "test-circuit-seed4": (2300.0, 2800.0),
    "test-circuit-seed2026": (2300.0, 2800.0),
    "test-circuit-seed2027": (2300.0, 2800.0),  # Checkpoint B's race-day track (plan roar-011)
}
SEEDS = (1, 2, 3, 7)
# CP.1 (plan roar-007) and CPB.1 (plan roar-011): the seeded checkpoint tracks' file stems, pinned
# literally (the carla-like car's hidden grip is keyed to the track name), and their measured stats:
# (length m, waypoints, min half-width m, tightest radius m)
SEEDED_STATS = {
    "test-circuit-seed1": (2625.6, 1313, 5.10, 17.7),
    "test-circuit-seed2": (2662.0, 1331, 5.01, 18.7),
    "test-circuit-seed3": (2670.4, 1335, 5.13, 20.5),
    "test-circuit-seed4": (2675.0, 1337, 5.14, 17.3),
    "test-circuit-seed2026": (2655.8, 1328, 5.15, 19.8),
    "test-circuit-seed2027": (2631.2, 1316, 5.41, 19.3),  # CPB.1 (plan roar-011)
}


@pytest.fixture(scope="module", params=g.ALL_NAMES)
def track(request):
    return g.build(request.param)


def _wrap(angle):
    return (angle + np.pi) % (2.0 * np.pi) - np.pi


def _seam_step_spec() -> g.TrackSpec:
    """A closed spec whose only curvature jump is +κ → −κ at the lap seam."""
    k = 1.0 / 80.0
    segments = (
        [g.Segment("arc", 0.4 / k, -k, -k), g.Segment("clothoid", 40.0, -k, 0.0)]
        + g.straight(200.0)
        + g.corner(80.0, 120.0, 40.0)
        + g.straight(200.0)
        + g.corner(80.0, 120.0, 40.0)
        + g.straight(200.0)
        + [g.Segment("clothoid", 40.0, 0.0, k), g.Segment("arc", 2.4 / k, k, k, designated=True)]
    )
    return g.TrackSpec("seam-step", tuple(segments), 6.0)


def test_closure_gap_and_heading(track):
    gap = math.hypot(track.x[0] - track.x[-1], track.y[0] - track.y[-1])
    assert gap < 2.5
    assert track.closure["residual_gap_m"] < g.MAX_RESIDUAL_GAP
    chord = math.atan2(track.y[0] - track.y[-1], track.x[0] - track.x[-1])
    mean_yaw = track.yaw[-1] + 0.5 * _wrap(track.yaw[0] - track.yaw[-1])
    assert abs(math.degrees(_wrap(chord - mean_yaw))) < 0.5
    # every track starts on its start straight, so the seam heading step is zero
    assert abs(math.degrees(_wrap(track.yaw[0] - track.yaw[-1]))) < 0.5


def test_total_turn_is_two_pi(track):
    spec_turn = sum(seg.turn for seg in track.spec.segments)
    assert abs(abs(spec_turn) - 2.0 * math.pi) < 1e-9
    steps = _wrap(np.diff(np.concatenate((track.yaw, track.yaw[:1]))))
    assert abs(abs(steps.sum()) - 2.0 * math.pi) < 1e-6


def test_spacing(track):
    chords = np.hypot(np.diff(np.r_[track.x, track.x[0]]), np.diff(np.r_[track.y, track.y[0]]))
    assert chords.min() >= 1.95 and chords.max() <= 2.05
    assert abs(np.diff(np.r_[track.s, track.length]).mean() - g.SPACING) < 0.05


def test_lengths_in_their_windows(track):
    low, high = LENGTH_WINDOWS[track.name]
    assert low <= track.length <= high
    assert track.x.size == track.s.size == round(track.length / g.SPACING)


def test_curvature_continuity_including_the_seam(track):
    assert g.max_ramp_rate(track.spec) > 0
    assert g.curvature_is_continuous(track)
    kappa = g.cyclic_signed_curvature(track.yaw, track.s, track.length)
    step = np.diff(np.concatenate((track.s, [track.length]))).max()
    bound = g.max_ramp_rate(track.spec) * step + 1e-3
    # the explicit oracle, wrap included
    jumps = np.abs(np.diff(np.concatenate((kappa, kappa[:1]))))
    assert jumps[-1] <= bound
    assert np.all(jumps <= bound)


def test_a_seam_curvature_step_fails_the_oracle():
    track = g.build_track(_seam_step_spec())
    assert g.self_intersections(track.x, track.y) == 0
    jumps = g.curvature_jumps(track)
    assert not g.curvature_is_continuous(track)
    assert int(np.argmax(jumps)) == jumps.size - 1  # the only failing jump is the wrap
    assert jumps[-1] == pytest.approx(2.0 / 80.0, rel=0.05)


def test_arc_curvature_matches_the_spec(track):
    kappa = g.cyclic_signed_curvature(track.yaw, track.s, track.length)
    s0 = 0.0
    checked = 0
    for seg in track.spec.segments:
        s1 = s0 + seg.length
        if seg.kind == "arc":
            inside = (track.s >= s0 + 1.0) & (track.s + g.SPACING <= s1 - 1.0)
            if inside.any():
                assert np.allclose(kappa[inside], seg.k0, rtol=0.02), seg.label
                checked += 1
        s0 = s1
    assert checked >= 2


def test_stored_curvature_matches_the_heading(track):
    kappa = g.cyclic_signed_curvature(track.yaw, track.s, track.length)
    # stored curvature is sampled at each waypoint; the heading-difference estimate is a 2 m mean
    assert np.max(np.abs(kappa - track.curvature)) < g.max_ramp_rate(track.spec) * g.SPACING + 1e-3


def test_no_self_intersection(track):
    assert g.self_intersections(track.x, track.y, stride=3) == 0


def test_half_widths_are_positive_and_per_waypoint(track):
    assert track.half_width.shape == track.x.shape
    assert np.all(track.half_width >= 5.0) and np.all(track.half_width <= 8.0)
    assert np.all(track.z == 0.0)


def test_the_seeded_checkpoint_tracks_are_named_literally():
    assert g.SEEDED_NAMES == tuple(SEEDED_STATS)
    assert g.ALL_NAMES == g.TRACK_NAMES + g.SEEDED_NAMES
    assert all(g.build(name).name == name for name in g.SEEDED_NAMES)


@pytest.mark.parametrize("name", tuple(SEEDED_STATS))
def test_the_seeded_checkpoint_tracks_measure_as_probed(name):
    length, waypoints, min_half_width, tightest_radius = SEEDED_STATS[name]
    track = g.build(name)
    assert track.length == pytest.approx(length, abs=0.1)
    assert track.x.size == waypoints
    assert float(track.half_width.min()) == pytest.approx(min_half_width, abs=0.01)
    assert 1.0 / float(np.abs(track.curvature).max()) == pytest.approx(tightest_radius, abs=0.1)
    assert g.curvature_is_continuous(track)
    assert g.self_intersections(track.x, track.y) == 0
    assert np.all(track.half_width >= 5.0) and np.all(track.half_width <= 8.0)


def test_monza_like_is_labelled_inspired_by_monza():
    doc = g.monza_like_spec.__doc__ + g.__doc__
    assert "inspired by Monza" in doc.replace("**", "")
    assert "not the CARLA map" in doc


def test_closure_rejects_a_spec_without_one_designated_arc():
    spec = g.oval_spec()
    undesignated = tuple(
        g.Segment(seg.kind, seg.length, seg.k0, seg.k1, seg.half_width, False, seg.label)
        for seg in spec.segments
    )
    with pytest.raises(ValueError, match="designated"):
        g.close_spec(g.TrackSpec("x", undesignated, 6.0))


def test_two_builds_are_byte_identical():
    for name in g.ALL_NAMES:
        first, second = g.build(name), g.build(name)
        assert g.npz_bytes(first.arrays()) == g.npz_bytes(second.arrays())
        assert g.content_hash(first.arrays()) == g.content_hash(second.arrays())


def test_content_hash_ignores_sub_rounding_noise_but_sees_real_changes():
    arrays = g.build("oval").arrays()
    noisy = {key: value * (1.0 + 1e-15) for key, value in arrays.items()}
    assert g.content_hash(noisy) == g.content_hash(arrays)
    moved = dict(arrays, x=arrays["x"] + 1e-3)
    assert g.content_hash(moved) != g.content_hash(arrays)


def test_seeded_tracks_are_deterministic_and_distinct():
    a, b = g.seeded_track(SEEDS[0]), g.seeded_track(SEEDS[0])
    assert g.npz_bytes(a.arrays()) == g.npz_bytes(b.arrays())
    hashes = {g.content_hash(g.seeded_track(seed).arrays()) for seed in SEEDS}
    assert len(hashes) == len(SEEDS)  # different seeds give different tracks
    assert g.content_hash(a.arrays()) != g.content_hash(g.build("test-circuit").arrays())


@pytest.mark.parametrize("seed", SEEDS)
def test_seeded_tracks_are_valid(seed):
    track = g.seeded_track(seed)
    assert g.curvature_is_continuous(track)
    assert g.self_intersections(track.x, track.y) == 0
    assert abs(abs(sum(seg.turn for seg in track.spec.segments)) - 2.0 * math.pi) < 1e-9
    chords = np.hypot(np.diff(np.r_[track.x, track.x[0]]), np.diff(np.r_[track.y, track.y[0]]))
    assert chords.min() >= 1.95 and chords.max() <= 2.05


def test_driver_generates_twice_identically_within_budget(tmp_path):
    start = time.perf_counter()
    first = generate.generate(tmp_path / "a")
    elapsed = time.perf_counter() - start
    second = generate.generate(tmp_path / "b")
    # design 013 §7.1: total generation (the named and seeded tracks, roar-004's sysid logs and the lab
    # sample) ≤ 1 min
    assert elapsed <= 60.0
    assert first == second
    assert sorted(first) == sorted(
        ["lab/sample_telemetry.csv", "sysid/monza-like-seed0.csv", "sysid/oval-steady-seed0.csv"]
        + [f"tracks/{name}.npz" for name in g.TRACK_NAMES]
        + [
            "tracks/test-circuit-seed1.npz",
            "tracks/test-circuit-seed2.npz",
            "tracks/test-circuit-seed3.npz",
            "tracks/test-circuit-seed4.npz",
            "tracks/test-circuit-seed2026.npz",
            "tracks/test-circuit-seed2027.npz",
        ]
    )
    for path in first:
        assert (tmp_path / "a" / path).read_bytes() == (tmp_path / "b" / path).read_bytes()
    stored = json.loads((tmp_path / "a" / "checksums.json").read_text(encoding="utf-8"))
    assert stored == first
    with np.load(tmp_path / "a" / "tracks" / "oval.npz") as loaded:
        assert tuple(loaded.files) == g.FIELDS


def test_driver_fails_on_a_two_run_mismatch(tmp_path, monkeypatch):
    calls = iter(range(10))

    def unstable(out_dir):
        arrays = g.build("oval").arrays()
        arrays["x"] = arrays["x"] + next(calls)
        return {"tracks/oval.npz": (g.npz_bytes(arrays), g.content_hash(arrays))}

    monkeypatch.setattr(generate, "STEPS", (("tracks", unstable, generate.rehash_track),))
    with pytest.raises(SystemExit, match="disagree"):
        generate.generate(tmp_path)
