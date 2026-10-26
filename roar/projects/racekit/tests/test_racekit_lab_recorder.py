"""The Unit 1 lab's recorder, exactly as ``labs/real-sim.ipynb`` prints it, raced on racekit
(roar-002 content gate: [fable] S1, [fable] M1, [sol] B1).

The recorder cell (found by its ``# lab-recorder:`` marker) and the parameters cell are spliced into
a copy of ``agents/unit-01.py`` with the three wiring lines the lab's markdown shows, then raced on
``oval`` with jitter 0: clean, with a saboteur, and with CARLA's stale first post-hold observation.
"""

from __future__ import annotations

import json
import math
import sys

import numpy as np
import pytest
from conftest import RACEKIT, REPO
from racekit.cars import KinematicCar
from racekit.check_submission import check_submission
from racekit.runner import CONTROL_DT, RESPAWN_HOLD_TICKS, load_submission, run_race, shim_installed
from racekit.telemetry import read_csv, sector_splits

LAB = REPO / "roar" / "units" / "unit-01-the-race-and-baseline" / "labs" / "real-sim.ipynb"
UNIT_01 = RACEKIT / "agents" / "unit-01.py"
MARKER = "# lab-recorder:"
DETERMINISTIC_OVAL = 223.50
# the three wiring lines of the lab's markdown, each after the starter line it follows
WIRING = (
    ("        self.current_index = self.nearest_index(location)\n", "        self.start_recording()\n"),
    ("        self.current_index = self.advance_index(location)\n", "        self.reanchor_after_respawn()\n"),
)
RECORD_CALL = "        self.record(location, yaw, speed, throttle, steer, brake)\n"
APPLY = "        await self.vehicle.apply_action({\n"
STEER_OFF = {"throttle": 1.0, "steer": 0.25, "brake": 0.0, "hand_brake": 0.0, "reverse": 0, "target_gear": 0}


def _lab_cells():
    notebook = json.loads(LAB.read_text(encoding="utf-8"))
    return [(cell["cell_type"], "".join(cell["source"])) for cell in notebook["cells"]]


def _once(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, old
    return text.replace(old, new)


def _recorder_agent_source() -> str:
    cells = _lab_cells()
    code = [source for kind, source in cells if kind == "code"]
    recorders = [source for source in code if source.startswith(MARKER)]
    assert len(recorders) == 1, "exactly one lab code cell starts with the recorder marker"
    top, methods = recorders[0].split("# --- inside the existing class", 1)
    methods = methods.split("class RoarCompetitionSolution:\n", 1)[1]
    parameters = code[0]  # lab-check pins the first code cell as the parameters cell
    # the markdown shows the same wiring, in this order
    wiring = [source for kind, source in cells if kind == "markdown" and "self.start_recording()" in source]
    assert len(wiring) == 1
    shown = wiring[0]
    for line in ("self.start_recording()", "self.reanchor_after_respawn()", RECORD_CALL.strip()):
        assert shown.count(line) == 1, line
    assert shown.index("self.advance_index(location)") < shown.index("self.reanchor_after_respawn()")
    assert shown.index(RECORD_CALL.strip()) < shown.index("await self.vehicle.apply_action")

    source = UNIT_01.read_text(encoding="utf-8")
    source = _once(source, "import roar_py_interface\n", "import roar_py_interface\n\n" + parameters + "\n\n" + top)
    for after, line in WIRING:
        source = _once(source, after, after + line)
    source = _once(source, APPLY, RECORD_CALL + APPLY)
    return _once(source, "    async def initialize(self)", methods.rstrip() + "\n\n    async def initialize(self)")


@pytest.fixture
def recorder(tmp_path, monkeypatch):
    """The spliced submission's path and its CSV path (``ROAR_LAB_CSV`` points at it)."""
    path = tmp_path / "submission.py"
    path.write_text(_recorder_agent_source(), encoding="utf-8")
    csv_path = tmp_path / "recording.csv"
    monkeypatch.setenv("ROAR_LAB_CSV", str(csv_path))
    return path, csv_path


class _CrashPoseCar(KinematicCar):
    """A KinematicCar that remembers its pose at each respawn (the pose CARLA keeps reporting)."""

    def reset(self, x, y, yaw, v=0.0):
        if hasattr(self, "x"):
            self.crash_pose = (self.x, self.y, self.yaw, self.v)
        super().reset(x, y, yaw, v)


class _Fixed:
    def __init__(self, value):
        self.value = np.asarray(value, dtype=np.float64)

    def get_last_gym_observation(self):
        return self.value


def _saboteur(path, should_crash, car=None, stale=False, old_reanchor=False):
    """The recorder agent, steering off when ``should_crash(agent)`` until its first respawn.

    ``stale``: on the first step after the hold, the location, rotation and velocity sensors report
    the crash pose, as the pinned CARLA runner does. ``old_reanchor``: the pre-gate re-anchor
    (``nearest_index`` of that step's location), to show the stale step has teeth."""
    with shim_installed():
        agent_class, module_name = load_submission(path)
    sys.modules.pop(module_name, None)  # the class keeps its globals; leave no stray module behind

    class Saboteur(agent_class):
        async def initialize(self):
            await super().initialize()
            self.crashed = False

        def reanchor_after_respawn(self):
            if not old_reanchor:
                return super().reanchor_after_respawn()
            impulse = self.collision_sensor.get_last_gym_observation()
            if float(np.linalg.norm(impulse)) > 100.0:
                self.current_index = self.nearest_index(self.location_sensor.get_last_gym_observation())
            return None

        async def step(self):
            respawn = float(np.linalg.norm(self.collision_sensor.get_last_gym_observation())) > 100.0
            sensors = (self.location_sensor, self.rpy_sensor, self.velocity_sensor)
            if respawn:
                self.crashed = True
                if stale:
                    x, y, yaw, v = car.crash_pose
                    self.location_sensor = _Fixed((x, y, 0.0))
                    self.rpy_sensor = _Fixed((0.0, 0.0, yaw))
                    self.velocity_sensor = _Fixed((v * math.cos(yaw), v * math.sin(yaw), 0.0))
            steer_off = not self.crashed and should_crash(self)
            await super().step()
            self.location_sensor, self.rpy_sensor, self.velocity_sensor = sensors
            if steer_off:
                await self.vehicle.apply_action(STEER_OFF)

    return Saboteur


def _lap_index(agent):
    return (agent.current_index - agent.start_index) % len(agent.maneuverable_waypoints)


def _recorded_splits(csv_path):
    telemetry, meta = read_csv(csv_path)
    splits = sector_splits(telemetry, meta["progress_total"], meta["laps"], meta["per_lap"], finished=True)
    return telemetry, meta, splits


def test_the_pasted_recorder_passes_check_submission_and_records_the_result_splits(recorder):
    path, csv_path = recorder
    report = check_submission(path)
    assert report.ok, report.findings
    result = run_race(path, "oval", car=KinematicCar(jitter=0.0))
    assert result.finished and result.collisions == 0
    assert result.total_time == pytest.approx(DETERMINISTIC_OVAL, abs=1e-9)  # recording changes nothing
    telemetry, meta, splits = _recorded_splits(csv_path)
    assert meta["progress_total"] == result.progress_total
    assert int(telemetry["held"].sum()) == 0
    assert np.all(np.diff(telemetry["progress"]) >= 0)
    assert np.abs(splits - result.sector_splits).max() <= CONTROL_DT + 1e-9


def _assert_one_recorded_respawn(csv_path, result, crash_pose=None):
    telemetry, meta, splits = _recorded_splits(csv_path)
    assert result.finished and result.collisions == 1
    held = telemetry["held"] == 1
    assert int(held.sum()) == RESPAWN_HOLD_TICKS  # [sol] B1: the hold is written into the file
    first = int(np.argmax(held))
    hold = telemetry[first:first + RESPAWN_HOLD_TICKS]
    assert (hold["held"] == 1).all() and (hold["progress"] == 0).all()
    # the hold rows carry the runner's hold times
    runner_hold = result.telemetry["t"][result.telemetry["held"] == 1]
    assert np.allclose(hold["t"], runner_hold, rtol=0.0, atol=1e-9)
    after = telemetry[first + RESPAWN_HOLD_TICKS]
    assert after["held"] == 0 and after["progress"] == 0 and after["t"] == pytest.approx(hold["t"][-1])
    if crash_pose is not None:  # the lab's prose: the first row after the hold has the crash pose
        assert (after["x"], after["y"]) == pytest.approx(crash_pose[:2], abs=1e-6)
    # after the restart the progress never jumps by a lap until the car really completes one
    rest = telemetry["progress"][first + RESPAWN_HOLD_TICKS:]
    assert np.all(np.diff(rest) >= 0) and np.all(np.diff(rest) < 0.5 * meta["waypoints_per_lap"])
    assert np.abs(splits - result.sector_splits).max() <= CONTROL_DT + 1e-9
    assert float(hold["t"][-1]) + splits.sum() == pytest.approx(result.total_time, abs=1e-9)
    return telemetry, meta


def test_a_recorded_crash_writes_the_hold_and_restarts_the_splits(recorder):
    path, csv_path = recorder
    agent = _saboteur(path, lambda self: self.tick * CONTROL_DT >= 60.0)
    result = run_race(agent, "oval", car=KinematicCar(jitter=0.0))
    _assert_one_recorded_respawn(csv_path, result)


def _late_in_lap_one(self):
    n = len(self.maneuverable_waypoints)
    return self.tick * CONTROL_DT > 30.0 and self.progress_tracker.offset == 0 and _lap_index(self) >= 0.93 * n


def test_the_stale_crash_pose_after_a_late_lap_crash_does_not_fake_a_lap(recorder):
    """[fable] M1: on CARLA the first post-hold step sees the impulse with the crash-pose location.
    The recorder resets to its start index without reading it, so no false lap wrap follows."""
    path, csv_path = recorder
    car = _CrashPoseCar(jitter=0.0)
    result = run_race(_saboteur(path, _late_in_lap_one, car=car, stale=True), "oval", car=car)
    _, meta = _assert_one_recorded_respawn(csv_path, result, crash_pose=car.crash_pose)
    n = meta["waypoints_per_lap"]
    crash_row = result.telemetry[np.isclose(result.telemetry["t"], result.respawn_times[0])][0]
    assert 0.9 * n <= crash_row["progress"] < n  # the crash is in the last tenth of lap 1


def test_the_stale_crash_pose_breaks_the_old_nearest_index_reanchor(recorder):
    """The teeth of the M1 test: re-anchoring on the stale location re-finds the crash point, and the
    next steps (at the start) look like a lap wrap."""
    path, csv_path = recorder
    car = _CrashPoseCar(jitter=0.0)
    run_race(_saboteur(path, _late_in_lap_one, car=car, stale=True, old_reanchor=True), "oval", car=car)
    telemetry, meta = read_csv(csv_path)
    first = int(np.argmax(telemetry["held"] == 1))
    rest = telemetry["progress"][first + RESPAWN_HOLD_TICKS:]
    assert rest[0] >= 0.9 * meta["waypoints_per_lap"]  # anchored at the crash point
    # a false lap within a second of the restart (a real lap takes over a minute)
    assert rest[:20].max() >= meta["waypoints_per_lap"]
