"""The Unit 9 racing-line solver, test side (plan roar-008 U9.1): the smoothest line on the reduced
problem, solved with QR and ``scipy.optimize.lsq_linear(method="bvls")``, as the Unit 9 notebook
solves it. The shipped submission keeps only the control values and the B-spline evaluation.

The line: waypoint i moves ``n_i`` metres along its left unit normal; ``n = B c`` with ``B`` the
periodic uniform cubic B-spline basis, one control value every ``STEP`` waypoints. The objective is
the sum of squared second differences of the moved points (x and y), linear in ``c``:
``A c + D x0`` with ``A = [D N_x B; D N_y B]``. Bounds: a control value moves only as far as every
waypoint in its support allows (half-width minus ``MARGIN``), and control values whose support
touches the ``PIN`` waypoints either side of the start are 0. "Local" widening also fixes every
control value whose support leaves the windows of ``LOCAL_WINDOW`` waypoints around each centreline
point tighter than ``LOCAL_RADIUS``.
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

STEP = 10  # waypoints per control value
MARGIN = 2.5  # m kept from each edge
PIN = 30  # waypoints either side of the start held on the centreline
LOCAL_RADIUS = 60.0  # m: local widening opens a window around every point tighter than this
LOCAL_WINDOW = 60  # waypoints either side of a tight point
BOUND_SLACK = 1e-12  # the solver's bounds are widened by this (so a pinned value may be +-1e-12)


def menger(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """The signed Menger curvature at every point of a closed polyline."""
    ax, ay, cx, cy = np.roll(x, 1), np.roll(y, 1), np.roll(x, -1), np.roll(y, -1)
    cross = (x - ax) * (cy - ay) - (y - ay) * (cx - ax)
    product = np.hypot(x - ax, y - ay) * np.hypot(cx - x, cy - y) * np.hypot(cx - ax, cy - ay)
    return 2.0 * cross / product


def normals(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """The left unit normal at every waypoint (the chord from i - 1 to i + 1, turned left)."""
    dx, dy = np.roll(x, -1) - np.roll(x, 1), np.roll(y, -1) - np.roll(y, 1)
    h = np.hypot(dx, dy)
    return -dy / h, dx / h


def basis(n: int, step: int = STEP) -> np.ndarray:
    """``B[i, j]``: the weight of control value j at waypoint i (four non-negative weights a row,
    summing to 1), for ``m = n // step`` control values at t = i * m / n."""
    m = n // step
    t = np.arange(n) * m / n
    j = np.floor(t).astype(int)
    u = t - j
    w = np.stack([(1 - u) ** 3, 3 * u ** 3 - 6 * u ** 2 + 4, -3 * u ** 3 + 3 * u ** 2 + 3 * u + 1, u ** 3], 1) / 6
    b = np.zeros((n, m))
    for k in range(4):
        np.add.at(b, (np.arange(n), (j - 1 + k) % m), w[:, k])
    return b


def local_mask(x: np.ndarray, y: np.ndarray, radius: float = LOCAL_RADIUS, window: int = LOCAL_WINDOW) -> np.ndarray:
    """The waypoints local widening may move: within ``window`` of a centreline point whose radius is
    below ``radius``."""
    kappa = np.abs(menger(x, y))
    n = kappa.size
    near = np.zeros(n, bool)
    for i in np.nonzero(kappa > 1.0 / radius)[0]:
        near[np.arange(i - window, i + window + 1) % n] = True
    return near


def solve_control(x, y, half_width, local: Optional[np.ndarray] = None) -> np.ndarray:
    """The smoothest line's control values (QR, then bounded least squares on the m x m problem)."""
    from scipy.optimize import lsq_linear

    x, y = np.asarray(x, float), np.asarray(y, float)
    n = x.size
    nx, ny = normals(x, y)
    b = basis(n)
    m = b.shape[1]

    def second_difference(values):
        return np.roll(values, -1, 0) - 2 * values + np.roll(values, 1, 0)

    a = np.vstack([second_difference(nx[:, None] * b), second_difference(ny[:, None] * b)])
    rhs = -np.concatenate([second_difference(x), second_difference(y)])
    half = np.asarray(half_width, float) - MARGIN
    index = np.arange(n)
    fixed = (index < PIN) | (index >= n - PIN)
    if local is not None:
        fixed = fixed | ~np.asarray(local)
    high = np.array([0.0 if fixed[b[:, j] > 0].any() else half[b[:, j] > 0].min() for j in range(m)])
    q, r = np.linalg.qr(a)
    result = lsq_linear(r, q.T @ rhs, bounds=(-high - BOUND_SLACK, high + BOUND_SLACK), method="bvls")
    return result.x


def solve_track(spec: Tuple[str, str]) -> Tuple[float, ...]:
    """``(track name, "global" or "local")`` -> the line's control values (a process-pool worker)."""
    from racekit.tracks import load_track

    name, kind = spec
    track = load_track(name)
    local = local_mask(track.x, track.y) if kind == "local" else None
    return tuple(float(value) for value in solve_control(track.x, track.y, track.half_width, local))


def line_offsets(control, n: int) -> np.ndarray:
    """The per-waypoint offsets ``B c`` of a line's control values."""
    return basis(n) @ np.asarray(control, float)


def line_points(x, y, offsets) -> Tuple[np.ndarray, np.ndarray]:
    nx, ny = normals(np.asarray(x, float), np.asarray(y, float))
    return x + offsets * nx, y + offsets * ny


def curvature_and_length(x, y) -> Tuple[float, float, float]:
    """(total squared curvature sum kappa^2 ds, lap length, the tightest radius) of a closed line."""
    kappa = menger(x, y)
    ds = np.hypot(np.roll(x, -1) - x, np.roll(y, -1) - y)
    return float(np.sum(kappa ** 2 * ds)), float(ds.sum()), float(1.0 / np.abs(kappa).max())
