"""``racekit.plots`` smoke tests on the Agg backend (plan roar-002 Phase 1)."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # after selecting the backend
import pytest
from conftest import STARTER
from racekit.plots import plot_speed_map, plot_telemetry, plot_track
from racekit.runner import run_race


@pytest.fixture(scope="module")
def race():
    return run_race(STARTER, "oval", max_seconds=20.0)


def test_plot_track(tmp_path):
    ax = plot_track("oval")
    assert ax.get_title() == "oval" and len(ax.lines) == 4  # two edges, the centreline, the start
    ax.figure.savefig(tmp_path / "track.png")
    plt.close("all")


def test_plot_telemetry(race, tmp_path):
    ax = plot_telemetry(race.telemetry)
    assert len(ax.lines) == 1 and ax.get_xlabel() == "t (s)"
    _, ax = plt.subplots()
    assert plot_telemetry(race.telemetry, ("throttle", "steer"), ax=ax) is ax and len(ax.lines) == 2
    with pytest.raises(ValueError, match="column"):
        plot_telemetry(race.telemetry, ("speed",))
    ax.figure.savefig(tmp_path / "telemetry.png")
    plt.close("all")


def test_plot_speed_map(race, tmp_path):
    ax = plot_speed_map(race.telemetry, track="oval")
    assert len(ax.collections) == 1 and len(ax.figure.axes) == 2  # the scatter and its colorbar
    plot_speed_map(race.telemetry).figure.savefig(tmp_path / "speed.png")
    plt.close("all")
