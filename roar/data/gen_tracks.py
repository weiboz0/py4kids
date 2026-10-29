"""Seeded closed race tracks from segment specs (design 013 §4.3; plan roar-001 Phase C).

Library plus CLI. A track is a list of segments:

* ``straight`` (zero curvature);
* ``arc`` (constant curvature ``1/R``, signed: positive turns left);
* ``clothoid`` (curvature linear in arc length, the transition between the two).

Every corner is built as clothoid in, arc, clothoid out, so curvature is continuous everywhere,
including the lap seam. The centreline is integrated by curvature in about 0.1 m steps and closed in
two stages before anything is resampled:

1. one designated arc's angle is scaled so the total turn is exactly ``±2π``;
2. the straight lengths are solved (min-norm least squares) so the endpoint gap is zero, using the
   same discrete integrator, so the remaining gap is float-level; that residual (asserted < 2.5 m)
   is sheared out linearly along the lap. Arcs keep their spec curvature.

The closed centreline is resampled at 2.0 m spacing with a per-waypoint drivable half-width.
``monza-like`` is **inspired by Monza** (public layout facts only); it is not the CARLA map, and no
CARLA map or waypoint data is used anywhere.

The seeded checkpoint tracks (``SEEDED_TRACKS``: ``test-circuit-seed1`` … ``test-circuit-seed4``, the
training family, ``test-circuit-seed2026``, Checkpoint A's checkpoint track, and
``test-circuit-seed2027``, Checkpoint B's race-day track) are ``seeded_spec`` variants of ``test-circuit``,
generated alongside the three named tracks.

CLI: ``python roar/data/gen_tracks.py [--out DIR] [--name NAME ...]`` writes ``<name>.npz`` files
(every track in ``ALL_NAMES`` by default).
The book's single driver, ``roar/data/generate.py``, calls this module and owns the checksums.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import math
import zipfile
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

DS = 0.1  # integration step (m)
SPACING = 2.0  # waypoint spacing (m)
MAX_RESIDUAL_GAP = 2.5  # the shear stage only removes a float-level residual (m)
FIELDS = ("x", "y", "z", "yaw", "half_width", "s", "curvature")
TRACK_NAMES = ("oval", "test-circuit", "monza-like")
# The seeded checkpoint tracks (design 013 §4.3, plan roar-007): (base, seed). Checkpoint A's training
# family is test-circuit seeds 1-4 and its checkpoint track is seed 2026 (fixed before it was probed);
# Checkpoint B's race-day track is seed 2027 (plan roar-011, also fixed before it was probed).
# The names are seeded_spec's ``<base>-seed<seed>``; the carla-like car keys its hidden grip to the
# track name, so renaming one changes the car on it.
SEEDED_TRACKS = (
    ("test-circuit", 1),
    ("test-circuit", 2),
    ("test-circuit", 3),
    ("test-circuit", 4),
    ("test-circuit", 2026),
    ("test-circuit", 2027),
)


@dataclass(frozen=True)
class Segment:
    """One centreline segment. Curvature runs linearly from ``k0`` to ``k1`` over ``length``."""

    kind: str  # "straight" | "arc" | "clothoid"
    length: float
    k0: float = 0.0
    k1: float = 0.0
    half_width: float | None = None  # None: the track default
    designated: bool = False  # the arc whose angle closes the total turn
    label: str = ""

    @property
    def turn(self) -> float:
        return 0.5 * (self.k0 + self.k1) * self.length


@dataclass(frozen=True)
class TrackSpec:
    name: str
    segments: tuple[Segment, ...]
    half_width: float


@dataclass
class Track:
    """A generated, closed track resampled at about ``SPACING`` metres."""

    name: str
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    yaw: np.ndarray
    half_width: np.ndarray
    s: np.ndarray
    curvature: np.ndarray
    length: float
    spec: TrackSpec
    closure: dict

    def arrays(self) -> dict[str, np.ndarray]:
        return {field: getattr(self, field) for field in FIELDS}


# --- spec builders -------------------------------------------------------------------------------


def straight(length: float, half_width: float | None = None, label: str = "") -> list[Segment]:
    return [Segment("straight", float(length), half_width=half_width, label=label)]


def corner(
    radius: float,
    angle_deg: float,
    transition: float = 30.0,
    half_width: float | None = None,
    label: str = "",
    designated: bool = False,
) -> list[Segment]:
    """A corner of total turn ``angle_deg`` (positive = left): clothoid in, arc, clothoid out."""
    k = math.copysign(1.0 / radius, angle_deg)
    total = math.radians(angle_deg)
    arc_turn = total - transition * k  # each clothoid turns transition * k / 2
    if arc_turn * total <= 0:
        raise ValueError(f"{label or 'corner'}: transition {transition} m too long for {angle_deg}°")
    common = {"half_width": half_width, "label": label}
    return [
        Segment("clothoid", transition, 0.0, k, **common),
        Segment("arc", abs(arc_turn) * radius, k, k, designated=designated, **common),
        Segment("clothoid", transition, k, 0.0, **common),
    ]


def oval_spec() -> TrackSpec:
    """Two 300 m straights joined by two 120 m-radius arcs (with clothoid entries and exits)."""
    segments = (
        straight(300.0, label="main straight")
        + corner(120.0, 180.0, 40.0, label="turn 1")
        + straight(300.0, label="back straight")
        + corner(120.0, 180.0, 40.0, label="turn 2", designated=True)
    )
    return TrackSpec("oval", tuple(segments), half_width=7.5)


def test_circuit_spec() -> TrackSpec:
    """About 2.5 km: mixed radii, a chicane and a hairpin (counter-clockwise)."""
    segments = (
        straight(380.0, label="start straight")
        + corner(60.0, 90.0, 30.0, label="turn 1")
        + straight(125.0)
        + corner(35.0, -45.0, 20.0, half_width=5.5, label="chicane right")
        + corner(35.0, 45.0, 20.0, half_width=5.5, label="chicane left")
        + straight(170.0)
        + corner(110.0, 90.0, 40.0, label="turn 4")
        + straight(320.0)
        + corner(50.0, -90.0, 25.0, label="turn 5")
        + straight(95.0)
        + corner(18.0, 180.0, 15.0, half_width=5.5, label="hairpin")
        + straight(330.0)
        + corner(150.0, -30.0, 40.0, label="kink")
        + straight(210.0)
        + corner(70.0, 120.0, 30.0, label="turn 8", designated=True)
        + straight(130.0)
    )
    return TrackSpec("test-circuit", tuple(segments), half_width=6.0)


def monza_like_spec() -> TrackSpec:
    """About 5.8 km, **inspired by Monza** from public layout facts (clockwise, so turns are negative).

    Main straight, the Rettifilo chicane, Curva Grande, the Roggia chicane, the two Lesmo corners,
    the Serraglio, the Ascari chicane, the back straight and the Parabolica. Not the CARLA map.
    """
    segments = (
        straight(1210.0, label="main straight")
        + corner(25.0, -80.0, 15.0, half_width=5.5, label="Rettifilo 1")
        + corner(25.0, 75.0, 15.0, half_width=5.5, label="Rettifilo 2")
        + straight(405.0)
        + corner(400.0, -90.0, 60.0, label="Curva Grande")
        + straight(85.0)
        + corner(30.0, 65.0, 15.0, half_width=5.5, label="Roggia 1")
        + corner(30.0, -65.0, 15.0, half_width=5.5, label="Roggia 2")
        + straight(65.0)
        + corner(85.0, -55.0, 30.0, label="Lesmo 1")
        + straight(60.0)
        + corner(65.0, -40.0, 30.0, label="Lesmo 2")
        + straight(445.0, label="Serraglio")
        + corner(400.0, 15.0, 40.0, label="Serraglio kink")
        + straight(340.0)
        + corner(50.0, -50.0, 20.0, label="Ascari 1")
        + corner(60.0, 70.0, 20.0, label="Ascari 2")
        + corner(70.0, -55.0, 20.0, label="Ascari 3")
        + straight(1105.0, label="back straight")
        + corner(140.0, -150.0, 60.0, label="Parabolica", designated=True)
        + straight(110.0)
    )
    return TrackSpec("monza-like", tuple(segments), half_width=6.0)


SPECS = {"oval": oval_spec, "test-circuit": test_circuit_spec, "monza-like": monza_like_spec}


def seeded_spec(seed: int, base: str = "test-circuit") -> TrackSpec:
    """A reproducible variant of ``base``: every corner's radius and every half-width is perturbed.

    Radii scale by a factor in [0.85, 1.15] per corner (its total turn is kept), and half-widths by a
    factor in [0.9, 1.1] per straight and per corner.
    The design's unseen-for-tuning checkpoint tracks (design 013 §4.3) come from named seeds.
    """
    rng = np.random.default_rng(seed)
    spec = SPECS[base]()
    segments = list(spec.segments)
    out: list[Segment] = []
    i = 0
    while i < len(segments):
        segment = segments[i]
        if segment.kind == "straight":
            width = (segment.half_width or spec.half_width) * float(rng.uniform(0.9, 1.1))
            out.append(replace(segment, half_width=width))
            i += 1
            continue
        # a corner: clothoid in, arc, clothoid out (corner() builds every curved segment this way)
        entry, arc, exit_ = segments[i : i + 3]
        assert entry.kind == "clothoid" and arc.kind == "arc" and exit_.kind == "clothoid"
        radius_scale = float(rng.uniform(0.85, 1.15))
        width = (arc.half_width or spec.half_width) * float(rng.uniform(0.9, 1.1))
        k_new = arc.k0 / radius_scale
        corner_turn = entry.turn + arc.turn + exit_.turn  # kept: only the radius changes
        arc_turn = corner_turn - 0.5 * k_new * (entry.length + exit_.length)
        out += [
            replace(entry, k1=k_new, half_width=width),
            replace(arc, k0=k_new, k1=k_new, length=arc_turn / k_new, half_width=width),
            replace(exit_, k0=k_new, half_width=width),
        ]
        i += 3
    return TrackSpec(seeded_name(base, seed), tuple(out), spec.half_width)


# --- integration and closure ---------------------------------------------------------------------


def _segment_steps(segment: Segment) -> int:
    return max(1, round(segment.length / DS))


def _integrate_segment(segment: Segment, x0: float, y0: float, psi0: float):
    """Integrate one segment in ``n`` equal steps of about ``DS``. Returns node arrays (n + 1)."""
    n = _segment_steps(segment)
    h = segment.length / n
    j = np.arange(n, dtype=np.float64)
    slope = (segment.k1 - segment.k0) / segment.length
    # exact heading at the nodes and the step midpoints for linear curvature
    s_nodes = np.arange(n + 1, dtype=np.float64) * h
    psi_nodes = psi0 + segment.k0 * s_nodes + 0.5 * slope * s_nodes**2
    s_mid = (j + 0.5) * h
    psi_mid = psi0 + segment.k0 * s_mid + 0.5 * slope * s_mid**2
    x = x0 + np.concatenate(([0.0], np.cumsum(h * np.cos(psi_mid))))
    y = y0 + np.concatenate(([0.0], np.cumsum(h * np.sin(psi_mid))))
    kappa = segment.k0 + slope * s_nodes
    return s_nodes, x, y, psi_nodes, kappa


def _segment_displacement(segment: Segment, psi0: float) -> tuple[float, float]:
    if segment.kind == "straight":
        return segment.length * math.cos(psi0), segment.length * math.sin(psi0)
    _, x, y, _, _ = _integrate_segment(segment, 0.0, 0.0, psi0)
    return float(x[-1]), float(y[-1])


def close_spec(spec: TrackSpec) -> tuple[TrackSpec, dict]:
    """Two-stage analytic closure. Returns the closed spec and a record of what changed."""
    segments = list(spec.segments)
    designated = [i for i, seg in enumerate(segments) if seg.designated]
    if len(designated) != 1 or segments[designated[0]].kind != "arc":
        raise ValueError(f"{spec.name}: exactly one designated arc is required")
    # Stage 1: the designated arc's angle makes the total turn exactly ±2π.
    turn = sum(seg.turn for seg in segments)
    target = math.copysign(2.0 * math.pi, turn)
    i = designated[0]
    arc = segments[i]
    new_turn = arc.turn + (target - turn)
    if new_turn * arc.turn <= 0:
        raise ValueError(f"{spec.name}: closing the turn would reverse the designated arc")
    segments[i] = replace(arc, length=new_turn / arc.k0)
    total_turn = sum(seg.turn for seg in segments)
    assert abs(total_turn - target) < 1e-9, (spec.name, total_turn, target)

    # Stage 2: the endpoint gap is linear in the straight lengths (headings do not depend on them).
    psi = 0.0
    fixed = np.zeros(2)
    directions = []
    straights = []
    for index, seg in enumerate(segments):
        if seg.kind == "straight":
            straights.append(index)
            directions.append((math.cos(psi), math.sin(psi)))
            fixed += np.array([seg.length * math.cos(psi), seg.length * math.sin(psi)])
        else:
            fixed += np.array(_segment_displacement(seg, psi))
            psi += seg.turn
    if len(straights) < 2:
        raise ValueError(f"{spec.name}: closure needs at least two straights")
    a = np.array(directions, dtype=np.float64).T  # (2, m): d(gap)/d(length_i)
    gap_before = fixed.copy()
    delta = np.linalg.lstsq(a, -gap_before, rcond=None)[0]  # min-norm change to the straights
    for index, change in zip(straights, delta):
        seg = segments[index]
        new_length = seg.length + float(change)
        if new_length < max(10.0, 0.4 * seg.length):
            raise ValueError(f"{spec.name}: straight {index} would shrink to {new_length:.1f} m")
        segments[index] = replace(seg, length=new_length)
    record = {
        "turn_before_deg": math.degrees(turn),
        "designated_arc_change_deg": math.degrees(target - turn),
        "gap_before_m": float(np.hypot(*gap_before)),
        "max_straight_change_m": float(np.abs(delta).max()),
    }
    return TrackSpec(spec.name, tuple(segments), spec.half_width), record


def _integrate_spec(spec: TrackSpec):
    xs, ys, psis, kappas, ss, widths = [], [], [], [], [], []
    x0 = y0 = psi0 = s0 = 0.0
    for seg in spec.segments:
        s, x, y, psi, kappa = _integrate_segment(seg, x0, y0, psi0)
        width = seg.half_width if seg.half_width is not None else spec.half_width
        # drop each segment's last node: it is the next segment's first node
        xs.append(x[:-1])
        ys.append(y[:-1])
        psis.append(psi[:-1])
        kappas.append(kappa[:-1])
        ss.append(s0 + s[:-1])
        widths.append(np.full(s.size - 1, width))
        x0, y0, psi0, s0 = float(x[-1]), float(y[-1]), float(psi[-1]), s0 + seg.length
    end = (x0, y0, psi0, s0)
    return (np.concatenate(xs), np.concatenate(ys), np.concatenate(psis), np.concatenate(kappas),
            np.concatenate(ss), np.concatenate(widths), end)


def build_track(spec: TrackSpec) -> Track:
    closed, record = close_spec(spec)
    x, y, psi, kappa, s, width, (xe, ye, psie, length) = _integrate_spec(closed)
    residual = math.hypot(xe - x[0], ye - y[0])
    assert residual < MAX_RESIDUAL_GAP, (spec.name, residual)
    # Stage 3: shear only the float-level residual out, linearly in s.
    frac = s / length
    x = x - (xe - x[0]) * frac
    y = y - (ye - y[0]) * frac
    record["residual_gap_m"] = residual
    record["heading_residual_rad"] = float(abs(psie - psi[0] - math.copysign(2 * math.pi, psie)))

    # Resample at about SPACING metres (an integer number of equal steps around the lap).
    n = round(length / SPACING)
    step = length / n
    sq = np.arange(n, dtype=np.float64) * step
    s_closed = np.concatenate((s, [length]))

    def interp(values: np.ndarray, end_value: float) -> np.ndarray:
        return np.interp(sq, s_closed, np.concatenate((values, [end_value])))

    xr = interp(x, x[0])
    yr = interp(y, y[0])
    psir = interp(psi, psie)
    kr = interp(kappa, kappa[0])
    # half-width is piecewise constant per segment: take the segment value at each waypoint
    idx = np.searchsorted(s, sq, side="right") - 1
    wr = width[idx]
    yaw = (psir + math.pi) % (2.0 * math.pi) - math.pi
    return Track(
        name=spec.name,
        x=xr + 0.0,
        y=yr + 0.0,
        z=np.zeros(n),
        yaw=yaw,
        half_width=wr.astype(np.float64),
        s=sq,
        curvature=kr + 0.0,
        length=float(length),
        spec=closed,
        closure=record,
    )


def seeded_track(seed: int, base: str = "test-circuit") -> Track:
    return build_track(seeded_spec(seed, base))


def seeded_name(base: str, seed: int) -> str:
    return f"{base}-seed{seed}"


SEEDED_NAMES = tuple(seeded_name(base, seed) for base, seed in SEEDED_TRACKS)
ALL_NAMES = TRACK_NAMES + SEEDED_NAMES  # every generated track, in the driver's order


def build(name: str) -> Track:
    """Build a named track (``TRACK_NAMES``) or a seeded checkpoint track (``SEEDED_NAMES``)."""
    if name in SPECS:
        return build_track(SPECS[name]())
    for base, seed in SEEDED_TRACKS:
        if name == seeded_name(base, seed):
            return seeded_track(seed, base)
    raise KeyError(f"unknown track {name!r}; expected one of {ALL_NAMES}")


# --- oracles shared by the tests and the driver --------------------------------------------------


def max_ramp_rate(spec: TrackSpec) -> float:
    """The spec's steepest clothoid ramp rate |dκ/ds| (1/m²)."""
    rates = [abs(seg.k1 - seg.k0) / seg.length for seg in spec.segments if seg.kind == "clothoid"]
    return max(rates, default=0.0)


def cyclic_signed_curvature(yaw: np.ndarray, s: np.ndarray, length: float) -> np.ndarray:
    """κ[i] = wrap(yaw[i+1] − yaw[i]) / Δs[i], cyclic (the last entry spans the lap seam)."""
    dyaw = np.diff(np.concatenate((yaw, yaw[:1])))
    dyaw = (dyaw + np.pi) % (2.0 * np.pi) - np.pi
    ds = np.diff(np.concatenate((s, [length])))
    return dyaw / ds


def curvature_jumps(track: Track) -> np.ndarray:
    """|κ[i+1] − κ[i]| for every i, including the last-to-first wrap."""
    kappa = cyclic_signed_curvature(track.yaw, track.s, track.length)
    return np.abs(np.diff(np.concatenate((kappa, kappa[:1]))))


def curvature_is_continuous(track: Track, tol: float = 1e-3) -> bool:
    step = float(np.max(np.diff(np.concatenate((track.s, [track.length])))))
    bound = max_ramp_rate(track.spec) * step + tol
    return bool(np.all(curvature_jumps(track) <= bound))


def self_intersections(x: np.ndarray, y: np.ndarray, stride: int = 3) -> int:
    """Count proper crossings between non-adjacent segments of the downsampled closed polyline."""
    p = np.column_stack((x[::stride], y[::stride]))
    q = np.roll(p, -1, axis=0)
    n = p.shape[0]

    def orient(a, b, c):
        return (b[..., 0] - a[..., 0]) * (c[..., 1] - a[..., 1]) - (b[..., 1] - a[..., 1]) * (
            c[..., 0] - a[..., 0]
        )

    hits = 0
    for i in range(n):
        j = np.arange(i + 2, n)
        j = j[(j + 1) % n != i]
        if j.size == 0:
            continue
        a, b, c, d = p[i], q[i], p[j], q[j]
        crosses = (orient(a, b, c) * orient(a, b, d) < 0) & (orient(c, d, a) * orient(c, d, b) < 0)
        hits += int(crosses.sum())
    return hits


# --- deterministic output ------------------------------------------------------------------------


def content_hash(arrays: dict[str, np.ndarray]) -> str:
    """sha256 over ``np.round(values, 6)`` in the fixed FIELDS order (never raw npz bytes)."""
    digest = hashlib.sha256()
    for field in FIELDS:
        values = np.round(np.asarray(arrays[field], dtype=np.float64), 6) + 0.0  # -0.0 -> 0.0
        digest.update(field.encode("ascii") + b"\0")
        digest.update(np.ascontiguousarray(values, dtype="<f8").tobytes())
    return digest.hexdigest()


def npz_bytes(arrays: dict[str, np.ndarray]) -> bytes:
    """An ``.npz`` archive with pinned zip metadata, so equal arrays give equal bytes."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for field in FIELDS:
            member = io.BytesIO()
            np.lib.format.write_array(
                member, np.ascontiguousarray(arrays[field], dtype="<f8"), allow_pickle=False
            )
            info = zipfile.ZipInfo(f"{field}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o644 << 16
            archive.writestr(info, member.getvalue())
    return buffer.getvalue()


def write_track(track: Track, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{track.name}.npz"
    path.write_bytes(npz_bytes(track.arrays()))
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "generated" / "tracks")
    parser.add_argument("--name", action="append", choices=ALL_NAMES)
    args = parser.parse_args(argv)
    for name in args.name or ALL_NAMES:
        track = build(name)
        path = write_track(track, args.out)
        print(f"{name}: {track.length:.1f} m, {track.x.size} waypoints -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
