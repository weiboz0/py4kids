"""The Unit 8 premise on the generated sensor logs (plan roar-004 G4.6).

The logs are ``roar/data/generate.py`` step 2's (``generated/sysid/``): what a driver observed and
commanded, never the car's state. This plan does **not** establish per-section μ identification
(roar-008's probe); the μ check here is a consistency bound only.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from conftest import DATA
from racekit import _truth
from racekit.telemetry import read_log_csv
from racekit.tracks import GRIP_SECTIONS, grip_sections, load_track

DT = 0.05
G = 9.81
SYSID = DATA / "generated" / "sysid"


def _log(name):
    path = SYSID / name
    if not path.is_file():
        pytest.fail(f"{path} is missing; run `PYTHONHASHSEED=0 uv run --group roar python roar/data/generate.py`")
    return read_log_csv(path)


def _segments(log):
    """Respawn-free runs of rows: a clock gap larger than one control tick is a respawn."""
    breaks = np.where(np.abs(np.diff(log["t"]) - DT) > 1e-6)[0] + 1
    return np.split(np.arange(log.size), breaks)


def _longitudinal_fit(log, lag):
    """Least squares of dv/dt = a_T·throttle − a_B·brake − c·v|v| between consecutive observations,
    with the commanded action lagged ``lag`` steps; returns ((a_T, a_B, c), residual RMS)."""
    speed = np.hypot(log["vx"], log["vy"])
    rows, rates = [], []
    for segment in _segments(log):
        k = segment[lag:-1]  # observation k -> k + 1 is driven by the action commanded at k - lag
        v0, v1 = speed[k], speed[k + 1]
        mean = 0.5 * (v0 + v1)
        rows.append(np.column_stack([log["throttle"][k - lag], -log["brake"][k - lag], -mean * np.abs(mean)]))
        rates.append((v1 - v0) / DT)
    a, b = np.vstack(rows), np.concatenate(rates)
    coef = np.linalg.lstsq(a, b, rcond=None)[0]
    return coef, float(np.sqrt(np.mean((a @ coef - b) ** 2)))


@pytest.fixture(scope="module")
def race_log():
    log, meta = _log("monza-like-seed0.csv")
    assert meta["kind"] == "race" and meta["track"] == "monza-like"
    return log


def test_g4_6_the_lagged_fit_has_its_residual_minimum_at_lag_1(race_log):
    rms = {lag: _longitudinal_fit(race_log, lag)[1] for lag in (0, 1, 2)}
    assert min(rms, key=rms.get) == 1, rms  # probe 0.569 / 0.436 / 0.537 (seed 3)


def test_g4_6_the_longitudinal_map_is_recovered(race_log):
    (a_throttle, a_brake, c_drag), _ = _longitudinal_fit(race_log, 1)
    assert abs(a_brake / _truth.A_BRAKE - 1.0) <= 0.05, a_brake
    assert abs(c_drag / _truth.C_DRAG - 1.0) <= 0.10, c_drag
    assert abs(a_throttle / _truth.A_THROTTLE - 1.0) <= 0.10, a_throttle


def test_g4_6_the_steady_log_gives_the_steering_gain():
    log, meta = _log("oval-steady-seed0.csv")
    assert meta["kind"] == "steady"
    yaw = np.unwrap(log["yaw"])
    body_speed = log["vx"] * np.cos(log["yaw"]) + log["vy"] * np.sin(log["yaw"])
    rate = np.diff(yaw) / DT  # over observation k -> k + 1
    speed = 0.5 * (body_speed[:-1] + body_speed[1:])
    applied = np.r_[0.0, log["steer"][:-2]]  # the steer commanded at k - 1 (one tick of lag)
    rolling = np.array([applied[max(0, k - 10):k + 1].std() for k in range(applied.size)])
    steady = (speed > 5.0) & (np.abs(applied) > 0.005) & (rolling < 0.002)
    assert steady.sum() >= 100
    gain = np.linalg.lstsq((-applied[steady])[:, None], np.arctan(rate[steady] * 2.875 / speed[steady]),
                           rcond=None)[0][0]
    assert abs(math.degrees(gain) / 66.0 - 1.0) <= 0.03, math.degrees(gain)  # probe 65.94° at 15 m/s


def test_g4_6_section_lateral_acceleration_is_bounded_by_mu_g(race_log):
    """A consistency check only: per respawn-free segment, drop 10 rows at each end, keep body speed
    > 5 m/s; the 98th percentile of |a_y| (central differences of the world velocity, on the body
    y axis) is ≤ 1.02·μ·g in every section with at least 20 such rows."""
    track = load_track("monza-like")
    sections = grip_sections(track)
    mu = np.array(_truth.grip_table("monza-like"))
    lateral = [[] for _ in range(GRIP_SECTIONS)]
    for segment in _segments(race_log):
        log = race_log[segment]
        ax, ay = np.gradient(log["vx"], DT), np.gradient(log["vy"], DT)
        a_y = -ax * np.sin(log["yaw"]) + ay * np.cos(log["yaw"])
        body_speed = log["vx"] * np.cos(log["yaw"]) + log["vy"] * np.sin(log["yaw"])
        hint = track.locate(log["x"][0], log["y"][0])[0]
        section = []
        for x, y in zip(log["x"].tolist(), log["y"].tolist()):
            hint = track.nearest(x, y, hint)[0]
            section.append(sections[hint])
        section = np.array(section)
        keep = body_speed > 5.0
        keep[:10] = False
        keep[-10:] = False
        for i in range(GRIP_SECTIONS):
            lateral[i].extend(np.abs(a_y[keep & (section == i)]).tolist())
    checked = 0
    for i in range(GRIP_SECTIONS):
        if len(lateral[i]) >= 20:
            checked += 1
            assert np.percentile(lateral[i], 98) <= 1.02 * mu[i] * G, i
    assert checked >= 3
