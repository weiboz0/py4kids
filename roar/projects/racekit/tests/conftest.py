"""Shared helpers for the racekit suite (plan roar-001 Phase D).

The suite races on the generated tracks; CI regenerates them first (ci-local's routed step runs
``roar/data/generate.py`` before ``pytest roar``).
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest
from racekit.tracks import TRACK_NAMES, tracks_dir

RACEKIT = Path(__file__).resolve().parents[1]
REPO = RACEKIT.parents[2]
STARTER = RACEKIT / "agents" / "starter.py"
DATA = REPO / "roar" / "data"
# the data-side driver module (roar/data/drivers.py, plan roar-004) is imported by the premise tests
if str(DATA) not in sys.path:
    sys.path.insert(0, str(DATA))

from gen_tracks import SEEDED_NAMES  # the seeded checkpoint tracks (plan roar-007)

SUBMISSION_HEADER = '''\
from __future__ import annotations

import math

import numpy as np
import roar_py_interface


'''
CONSTRUCTOR = '''\
    def __init__(self, maneuverable_waypoints, vehicle, camera_sensor=None, location_sensor=None,
                 velocity_sensor=None, rpy_sensor=None, occupancy_map_sensor=None,
                 collision_sensor=None):
        self.waypoints = maneuverable_waypoints
        self.vehicle = vehicle
        self.location_sensor = location_sensor
        self.velocity_sensor = velocity_sensor
        self.rpy_sensor = rpy_sensor
        self.collision_sensor = collision_sensor
'''


@pytest.fixture(scope="session", autouse=True)
def generated_tracks():
    missing = [name for name in TRACK_NAMES + SEEDED_NAMES if not (tracks_dir() / f"{name}.npz").is_file()]
    if missing:
        pytest.fail(
            f"generated tracks missing ({missing}); run "
            "`PYTHONHASHSEED=0 uv run --group roar python roar/data/generate.py` first"
        )


@pytest.fixture
def write_submission(tmp_path):
    """Write a submission file; ``body`` is the class body after the standard constructor."""

    def write(body: str, name: str = "submission.py", header: str = SUBMISSION_HEADER,
              constructor: str = CONSTRUCTOR, folder: Path | None = None) -> Path:
        target = (folder or tmp_path) / name
        target.parent.mkdir(parents=True, exist_ok=True)
        source = header + "class RoarCompetitionSolution:\n" + constructor + textwrap.indent(
            textwrap.dedent(body), "    "
        )
        target.write_text(source, encoding="utf-8")
        return target

    return write


@pytest.fixture(scope="session")
def premise():
    """The premise races (plan roar-004 G4.3–G4.5), raced once per session in parallel."""
    from _premise import premise_jobs, race_all

    return race_all(premise_jobs())


@pytest.fixture(scope="session")
def agent_premise():
    """The Unit 4 / Unit 5 premise races (plan roar-005), raced once per session in parallel."""
    from _agent_premise import race_agent_premise

    return race_agent_premise()


@pytest.fixture(scope="session")
def speed_premise():
    """The Unit 6 / Unit 7 premise races (plan roar-006), raced once per session in parallel."""
    from _speed_premise import race_speed_premise

    return race_speed_premise()


@pytest.fixture(scope="session")
def checkpoint_a():
    """Checkpoint A's gate races (plan roar-007 CP.2-CP.4), raced once per session in parallel."""
    from _checkpoint_premise import race_checkpoint_a

    return race_checkpoint_a()


@pytest.fixture(scope="session")
def line_controls():
    """The Unit 9 lines' control values (plan roar-008 U9.1), solved once per session in parallel."""
    from _line_premise import solve_lines

    return solve_lines()


@pytest.fixture(scope="session")
def line_premise(line_controls):
    """The Unit 8-9 gate races (plan roar-008 U8.2-U8.5, U9.2-U9.6), raced once per session in parallel."""
    from _line_premise import race_line_premise

    return race_line_premise(line_controls)


@pytest.fixture(scope="session")
def mpc_premise(line_controls):
    """The Unit 10 gate races (plan roar-009 U10.2-U10.8), raced once per session in parallel."""
    from _mpc_premise import race_mpc_premise

    return race_mpc_premise(line_controls)


@pytest.fixture(scope="session")
def robust_premise(line_controls):
    """The Unit 11 gate races (plan roar-010 U11.2-U11.9), raced once per session in parallel."""
    from _robust_premise import race_robust_premise

    return race_robust_premise(line_controls)


@pytest.fixture(scope="session")
def race_day_line():
    """Checkpoint B's race-day line (plan roar-011), solved once per session."""
    from _checkpoint_b_premise import solve_race_day_line

    return solve_race_day_line()


@pytest.fixture(scope="session")
def checkpoint_b_premise(line_controls, race_day_line):
    """Checkpoint B's pooled gate races (plan roar-011 CPB.2-CPB.5), raced once per session in parallel."""
    from _checkpoint_b_premise import race_checkpoint_b

    return race_checkpoint_b(line_controls, race_day_line)


@pytest.fixture(scope="session")
def tuning_test_track():
    """Unit 12's test track (plan roar-012 U12.0): its line, solved once, and its six grip probes,
    raced once per session in parallel."""
    from _tuning_premise import measure_test_track

    return measure_test_track()


@pytest.fixture(scope="session")
def tuning_premise(line_controls, tuning_test_track):
    """The Unit 12 gate races (plan roar-012 U12.1-U12.7), raced once per session in parallel."""
    from _tuning_premise import race_tuning_premise

    return race_tuning_premise(line_controls, tuning_test_track)


@pytest.fixture(scope="session")
def race_day_premise():
    """The Unit 13 gate races (plan roar-013 U13.1-U13.5), raced once per session in parallel."""
    from _race_day_premise import race_race_day_premise

    return race_race_day_premise()
