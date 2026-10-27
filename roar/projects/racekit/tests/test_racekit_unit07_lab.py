"""The Unit 7 lab's section sidecar and its per-section analysis, raced on racekit (plan roar-006 U7.10).

The Unit 1 lab's recorder (its ``# lab-recorder:`` cell and parameters cell), with Unit 5's one-line
``offset`` change exactly as the Unit 5 lab's ``diff`` block shows it, and the Unit 7 lab's sidecar
writer (its ``# lab-sidecar:`` cell) with its wiring line, are spliced into a copy of
``agents/unit-07.py``. The analysis functions are executed from the shipped Unit 7 lab.

* ``oval`` on ``carla_like(noise=True)``, seed 0: the sidecar equals ``grip_sections(load_track("oval"))``
  (the race starts on waypoint 0), and the analysis maps every driving row to the section of the
  waypoint the agent was at when it wrote that row;
* the sidecar writer called directly with a shifted start (``start_index`` 10 and n - 3): line k is the
  section of waypoint (start_index + k) mod n, and a row on the lap wrap and a row in lap 2 map to
  the right waypoint's section;
* without a sidecar the analysis falls back to six equal progress slices, and says so.
"""

from __future__ import annotations

import json
import re
import sys

import numpy as np
import pytest
from conftest import RACEKIT, REPO
from racekit.cars import carla_like
from racekit.check_submission import check_submission
from racekit.runner import load_submission, run_race, shim_installed
from racekit.telemetry import read_csv
from racekit.tracks import grip_sections, load_track

UNIT_01_LAB = REPO / "roar" / "units" / "unit-01-the-race-and-baseline" / "labs" / "real-sim.ipynb"
UNIT_05_LAB = REPO / "roar" / "units" / "unit-05-geometric-steering" / "labs" / "real-sim.ipynb"
UNIT_07_LAB = REPO / "roar" / "units" / "unit-07-speed-planning" / "labs" / "real-sim.ipynb"
UNIT_07 = RACEKIT / "agents" / "unit-07.py"
RECORDER_MARKER = "# lab-recorder:"
SIDECAR_MARKER = "# lab-sidecar:"
START_RECORDING = "        self.start_recording()\n"
SIDECAR_CALL = "        write_section_sidecar(TELEMETRY_PATH, self.section, self.start_index)\n"
WIRING = (  # the Unit 1 lab's wiring lines and the Unit 7 lab's, each after the line it follows
    ("        self.current_index = self.nearest_index(location)\n", START_RECORDING + SIDECAR_CALL),
    ("        self.current_index = self.advance_index(location)\n", "        self.reanchor_after_respawn()\n"),
)
RECORD_CALL = "        self.record(location, yaw, speed, throttle, steer, brake)\n"
APPLY = "        await self.vehicle.apply_action({\n"


def _cells(path):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    return [(cell["cell_type"], "".join(cell["source"])) for cell in notebook["cells"]]


def _once(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, old
    return text.replace(old, new)


def _code_starting_with(path, marker):
    found = [source for kind, source in _cells(path) if kind == "code" and source.startswith(marker)]
    assert len(found) == 1, (path.name, marker)
    return found[0]


def _offset_change():
    """The (old, new) line of the Unit 5 lab's one ``diff`` block (the change the Unit 7 lab reuses)."""
    blocks = [block for kind, source in _cells(UNIT_05_LAB) if kind == "markdown"
              for block in re.findall(r"```diff\n(.*?)```", source, flags=re.DOTALL)]
    assert len(blocks) == 1
    removed = [line[1:] for line in blocks[0].splitlines() if line.startswith("-")]
    added = [line[1:] for line in blocks[0].splitlines() if line.startswith("+")]
    assert len(removed) == 1 and len(added) == 1 and "self.cross_track_error" in added[0]
    return removed[0] + "\n", added[0] + "\n"


def _sidecar_source() -> str:
    return _code_starting_with(UNIT_07_LAB, SIDECAR_MARKER)


def _lab_functions():
    """The Unit 7 lab's analysis functions, executed from the shipped notebook's analysis cell."""
    code = [source for kind, source in _cells(UNIT_07_LAB) if kind == "code"]
    defining = [source for source in code if "def load_sections(" in source]
    assert len(defining) == 1
    source = defining[0]
    start = source.index("def driving_rows(")
    end = source.index("\n\n\ndef section_table(", start)
    namespace = {"np": np, "SECTIONS": 6}
    exec(compile(source[start:end], str(UNIT_07_LAB), "exec"), namespace)  # noqa: S102 - the shipped code
    return namespace


def _sidecar_writer():
    namespace = {}
    exec(compile(_sidecar_source(), str(UNIT_07_LAB), "exec"), namespace)  # noqa: S102 - the shipped code
    return namespace["write_section_sidecar"]


def recorder_source(agent: str) -> str:
    """``agent`` with the Unit 1 recorder, Unit 5's change and the Unit 7 sidecar pasted and wired in."""
    # the Unit 7 lab's markdown shows the new wiring line once, right after start_recording()
    shown = [source for kind, source in _cells(UNIT_07_LAB) if kind == "markdown" and SIDECAR_CALL.strip() in source]
    assert len(shown) == 1 and shown[0].count(SIDECAR_CALL.strip()) == 1
    assert shown[0].index("self.start_recording()") < shown[0].index(SIDECAR_CALL.strip())

    code = [source for kind, source in _cells(UNIT_01_LAB) if kind == "code"]
    old, new = _offset_change()
    recorder = _once(_code_starting_with(UNIT_01_LAB, RECORDER_MARKER), old, new)
    top, methods = recorder.split("# --- inside the existing class", 1)
    methods = methods.split("class RoarCompetitionSolution:\n", 1)[1]
    parameters = code[0]  # lab-check pins the first code cell as the parameters cell
    module_top = parameters + "\n\n" + top + "\n\n" + _sidecar_source() + "\n\n"
    source = _once(agent, "import roar_py_interface\n", "import roar_py_interface\n\n" + module_top)
    for after, lines in WIRING:
        source = _once(source, after, after + lines)
    source = _once(source, APPLY, RECORD_CALL + APPLY)
    return _once(source, "    async def initialize(self)", methods.rstrip() + "\n\n    async def initialize(self)")


@pytest.fixture
def recorder(tmp_path, monkeypatch):
    """The spliced Unit 7 submission's path and its CSV path (``ROAR_LAB_CSV`` points at it)."""
    path = tmp_path / "submission.py"
    path.write_text(recorder_source(UNIT_07.read_text(encoding="utf-8")), encoding="utf-8")
    csv_path = tmp_path / "recording.csv"
    monkeypatch.setenv("ROAR_LAB_CSV", str(csv_path))
    return path, csv_path


def test_the_sidecar_and_the_analysis_on_an_oval_race(recorder):
    path, csv_path = recorder
    report = check_submission(path)
    assert report.ok, report.findings
    with shim_installed():
        agent_class, module_name = load_submission(path)
    indices = []

    class Watched(agent_class):  # the waypoint the agent was at when it wrote each row
        async def step(self):
            await super().step()
            indices.append(self.current_index)

    try:
        result = run_race(Watched, "oval", car=carla_like(noise=True), seed=0, max_seconds=600.0)
    finally:
        sys.modules.pop(module_name, None)
    assert result.finished and result.collisions == 0, result
    assert result.total_time == pytest.approx(152.70, abs=0.05 + 1e-9)  # recording changes nothing

    grip = grip_sections(load_track("oval")).tolist()
    sidecar = [int(line) for line in csv_path.with_name(csv_path.name + ".sections.txt").read_text().split()]
    assert sidecar == grip  # the race starts on waypoint 0, so progress order is waypoint order

    lab = _lab_functions()
    telemetry, meta = read_csv(csv_path)
    n = meta["waypoints_per_lap"]
    sections, from_sidecar = lab["load_sections"](str(csv_path), n)
    assert from_sidecar and sections == grip
    assert len(telemetry) == len(indices)  # one row per step, no hold rows on a clean race
    keep, stale = lab["driving_rows"](telemetry, n)
    driving = np.nonzero(keep)[0]
    assert len(driving) == len(telemetry) and stale == []
    mapped = lab["row_sections"](telemetry["progress"], sections)
    expected = np.array([grip[index] for index in indices])
    assert np.array_equal(mapped[driving], expected[driving])
    assert set(expected.tolist()) == set(range(6))  # every section was driven
    assert int(telemetry["progress"].max()) >= 2 * n  # the rows include laps 2 and 3


@pytest.mark.parametrize("shift", [10, -3])
def test_the_sidecar_is_written_in_progress_order(tmp_path, shift):
    grip = grip_sections(load_track("oval")).tolist()
    n = len(grip)
    start = shift % n  # 10, and n - 3
    csv_path = tmp_path / "recording.csv"
    _sidecar_writer()(str(csv_path), grip, start)
    sidecar = [int(line) for line in csv_path.with_name(csv_path.name + ".sections.txt").read_text().split()]
    assert sidecar == [grip[(start + k) % n] for k in range(n)]  # the rotation
    assert sidecar != grip

    lab = _lab_functions()
    sections, from_sidecar = lab["load_sections"](str(csv_path), n)
    assert from_sidecar and sections == sidecar
    rows = {  # progress: the waypoint the recorder was at
        0: start,
        n - start - 1: n - 1,  # the last waypoint of the lap ...
        n - start: 0,  # ... and the lap wrap: waypoint 0, section 0
        n + 7: (start + 7) % n,  # lap 2
        2 * n + n // 2: (start + n // 2) % n,  # lap 3
    }
    mapped = lab["row_sections"](np.array(list(rows)), sections)
    assert mapped.tolist() == [grip[waypoint] for waypoint in rows.values()]
    assert mapped[2] == 0 and mapped[1] == 5


def test_without_a_sidecar_the_analysis_uses_equal_progress_slices(tmp_path):
    lab = _lab_functions()
    sections, from_sidecar = lab["load_sections"](str(tmp_path / "no-such-recording"), 12)
    assert not from_sidecar and sections == [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
