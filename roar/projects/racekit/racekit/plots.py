"""Telemetry and track plots (plan roar-002; design 013 §4.2).

matplotlib is imported lazily inside each function, so ``import racekit.plots`` needs numpy only
and racekit's core never imports matplotlib. Each function draws on ``ax`` (a new figure when it
is None) and returns the axes, so a notebook can add titles, labels or more lines with plain
``ax`` calls.
"""

from __future__ import annotations

from typing import Any, Optional, Sequence, Union

import numpy as np

from .tracks import Track, load_track


def _axes(ax: Any, figsize: Any) -> Any:
    if ax is not None:
        return ax
    import matplotlib.pyplot as plt

    _, ax = plt.subplots(figsize=figsize)
    return ax


def plot_track(track: Union[str, Track], ax: Optional[Any] = None, show_start: bool = True) -> Any:
    """The track from above: the centreline (dashed), both edges, and the start (a marker)."""
    track = load_track(track)
    ax = _axes(ax, (7, 6))
    nx, ny = -np.sin(track.yaw), np.cos(track.yaw)  # the left-pointing normal
    closed = np.r_[np.arange(len(track)), 0]
    for side in (1.0, -1.0):
        ax.plot((track.x + side * track.half_width * nx)[closed], (track.y + side * track.half_width * ny)[closed],
                color="0.35", linewidth=1.0)
    ax.plot(track.x[closed], track.y[closed], color="0.6", linewidth=0.8, linestyle="--")
    if show_start:
        x, y, _ = track.start_pose()
        ax.plot([x], [y], marker="o", color="tab:green", linestyle="none", label="start")
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(track.name)
    return ax


def plot_telemetry(telemetry: np.ndarray, columns: Sequence[str] = ("v",), ax: Optional[Any] = None) -> Any:
    """Telemetry columns against time ``t``, one line per column (held rows included)."""
    names = telemetry.dtype.names or ()
    missing = [column for column in columns if column not in names]
    if missing:
        raise ValueError(f"no telemetry column(s) {missing}; the columns are {names}")
    ax = _axes(ax, (9, 3.5))
    for column in columns:
        ax.plot(telemetry["t"], telemetry[column], label=column, linewidth=1.0)
    ax.set_xlabel("t (s)")
    ax.set_ylabel(", ".join(columns))
    if len(columns) > 1:
        ax.legend()
    ax.grid(True, alpha=0.3)
    return ax


def plot_speed_map(
    telemetry: np.ndarray, track: Optional[Union[str, Track]] = None, ax: Optional[Any] = None,
) -> Any:
    """The driven path from above, coloured by speed ``v`` (m/s), over the track when given."""
    ax = plot_track(track, ax=ax) if track is not None else _axes(ax, (7, 6))
    points = ax.scatter(telemetry["x"], telemetry["y"], c=telemetry["v"], s=2, cmap="viridis")
    ax.figure.colorbar(points, ax=ax, label="v (m/s)")
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    return ax
