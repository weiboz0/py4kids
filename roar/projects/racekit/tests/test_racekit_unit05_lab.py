"""The Unit 5 lab's recorder and its stale-row rule, raced on racekit (plan roar-005 U5.6).

The Unit 1 lab's recorder (its ``# lab-recorder:`` cell and parameters cell), with the one-line
``offset`` change exactly as the Unit 5 lab's ``diff`` block shows it, is spliced into a copy of
``agents/unit-05.py`` with the three wiring lines of the Unit 1 lab. Two races:

* ``oval`` with jitter 0: the recorded ``offset`` (the agent's own ``self.cross_track_error``,
  measured at the start of a tick) equals racekit's telemetry ``offset`` one row earlier (the state
  after the previous tick; the Unit 2 milestone's alignment) within 1e-4 m;
* a respawning race ([fable] N10): ``STEERING = "pid"``, ``TARGET_SPEED = 30.0``, ``test-circuit``,
  ``KinematicCar(jitter=0.05, lag_ticks=2)``, seed 0, ``max_seconds=400``: exactly 41 collisions, and
  the lab's ``driving_rows`` (taken from the shipped notebook) drops exactly the held rows and the
  first row after each hold run.
"""

from __future__ import annotations

import json
import re

import numpy as np
import pytest
from conftest import RACEKIT, REPO
from racekit.cars import KinematicCar
from racekit.check_submission import check_submission
from racekit.runner import RESPAWN_HOLD_TICKS, run_race
from racekit.telemetry import read_csv
from racekit.variants import write_variant

UNIT_01_LAB = REPO / "roar" / "units" / "unit-01-the-race-and-baseline" / "labs" / "real-sim.ipynb"
UNIT_05_LAB = REPO / "roar" / "units" / "unit-05-geometric-steering" / "labs" / "real-sim.ipynb"
UNIT_05 = RACEKIT / "agents" / "unit-05.py"
MARKER = "# lab-recorder:"
WIRING = (  # the Unit 1 lab's wiring lines, each after the line of the agent it follows
    ("        self.current_index = self.nearest_index(location)\n", "        self.start_recording()\n"),
    ("        self.current_index = self.advance_index(location)\n", "        self.reanchor_after_respawn()\n"),
)
RECORD_CALL = "        self.record(location, yaw, speed, throttle, steer, brake)\n"
APPLY = "        await self.vehicle.apply_action({\n"
OFFSET_TOL = 1e-4  # m: the recorder writes six decimals


def _cells(path):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    return [(cell["cell_type"], "".join(cell["source"])) for cell in notebook["cells"]]


def _once(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, old
    return text.replace(old, new)


def _offset_change():
    """The (old, new) line of the Unit 5 lab's one ``diff`` block."""
    blocks = [block for kind, source in _cells(UNIT_05_LAB) if kind == "markdown"
              for block in re.findall(r"```diff\n(.*?)```", source, flags=re.DOTALL)]
    assert len(blocks) == 1, "the Unit 5 lab shows exactly one diff block"
    removed = [line[1:] for line in blocks[0].splitlines() if line.startswith("-")]
    added = [line[1:] for line in blocks[0].splitlines() if line.startswith("+")]
    assert len(removed) == 1 and len(added) == 1, "the recorder change is one line"
    assert "self.cross_track_error" in added[0]
    return removed[0] + "\n", added[0] + "\n"


def recorder_source(agent: str) -> str:
    """``agent`` with the Unit 1 recorder, as changed by the Unit 5 lab, pasted and wired in."""
    code = [source for kind, source in _cells(UNIT_01_LAB) if kind == "code"]
    recorders = [source for source in code if source.startswith(MARKER)]
    assert len(recorders) == 1
    old, new = _offset_change()
    recorder = _once(recorders[0], old, new)
    top, methods = recorder.split("# --- inside the existing class", 1)
    methods = methods.split("class RoarCompetitionSolution:\n", 1)[1]
    parameters = code[0]  # lab-check pins the first code cell as the parameters cell
    source = _once(agent, "import roar_py_interface\n", "import roar_py_interface\n\n" + parameters + "\n\n" + top)
    for after, line in WIRING:
        source = _once(source, after, after + line)
    source = _once(source, APPLY, RECORD_CALL + APPLY)
    return _once(source, "    async def initialize(self)", methods.rstrip() + "\n\n    async def initialize(self)")


def driving_rows():
    """The lab's exclusion rule, executed from the shipped notebook's analysis cell."""
    code = [source for kind, source in _cells(UNIT_05_LAB) if kind == "code"]
    defining = [source for source in code if "def driving_rows(" in source]
    assert len(defining) == 1
    tree_source = defining[0]
    start = tree_source.index("def driving_rows(")
    end = tree_source.index("\n\n\n", start)
    namespace = {"np": np}
    exec(compile(tree_source[start:end], str(UNIT_05_LAB), "exec"), namespace)  # noqa: S102 - the shipped code
    return namespace["driving_rows"]


@pytest.fixture
def recorder(tmp_path, monkeypatch):
    """The spliced Unit 5 submission's path and its CSV path (``ROAR_LAB_CSV`` points at it)."""
    path = tmp_path / "submission.py"
    path.write_text(recorder_source(UNIT_05.read_text(encoding="utf-8")), encoding="utf-8")
    csv_path = tmp_path / "recording.csv"
    monkeypatch.setenv("ROAR_LAB_CSV", str(csv_path))
    return path, csv_path


def test_the_recorded_offset_is_racekits_offset_one_row_earlier(recorder):
    path, csv_path = recorder
    report = check_submission(path)
    assert report.ok, report.findings
    result = run_race(path, "oval", car=KinematicCar(jitter=0.0))
    assert result.finished and result.collisions == 0
    assert result.total_time == pytest.approx(216.35, abs=0.05 + 1e-9)  # U5.2: recording changes nothing
    recorded, _ = read_csv(csv_path)
    racekit = result.telemetry
    assert len(recorded) == len(racekit)
    assert np.allclose(recorded["t"][1:], racekit["t"][:-1], rtol=0.0, atol=1e-9)
    gap = np.abs(recorded["offset"][1:] - racekit["offset"][:-1])
    assert gap.max() <= OFFSET_TOL, gap.max()
    assert np.abs(recorded["offset"]).max() > 0.001  # the column is the measurement, not Unit 1's zeros


def test_the_stale_row_rule_on_a_respawning_race(recorder, tmp_path):
    path, csv_path = recorder
    respawning = write_variant(path, tmp_path / "respawning.py", {"STEERING": '"pid"', "TARGET_SPEED": "30.0"})
    result = run_race(respawning, "test-circuit", car=KinematicCar(jitter=0.05, lag_ticks=2), seed=0,
                      max_seconds=400.0)
    assert result.collisions == 41 and not result.finished, result
    telemetry, meta = read_csv(csv_path)
    held = telemetry["held"] == 1
    starts = [row for row in np.nonzero(held)[0] if row == 0 or not held[row - 1]]
    assert len(starts) == 41  # one hold run per collision, each written by the recorder
    runs_ends = [row for row in np.nonzero(held)[0] if row + 1 == len(held) or not held[row + 1]]
    assert all(end - start + 1 == RESPAWN_HOLD_TICKS for start, end in zip(starts, runs_ends))
    first_after = {end + 1 for end in runs_ends if end + 1 < len(held)}

    keep, stale = driving_rows()(telemetry, meta["waypoints_per_lap"])
    dropped = set(np.nonzero(~keep)[0])
    assert set(stale) == first_after  # exactly the first row after each hold run
    assert dropped == set(np.nonzero(held)[0]) | first_after
    assert not held[sorted(first_after)].any() and (telemetry["progress"][sorted(first_after)] == 0).all()


def test_without_held_rows_the_rule_drops_the_progress_drop_row():
    telemetry = np.zeros(8, dtype=[("held", "i8"), ("progress", "i8")])
    telemetry["progress"] = [5, 6, 900, 950, 3, 4, 5, 6]  # a respawn after row 3 (n = 1000)
    keep, stale = driving_rows()(telemetry, 1000)
    assert stale == [4] and list(np.nonzero(~keep)[0]) == [4]
    lap_wrap = np.zeros(4, dtype=[("held", "i8"), ("progress", "i8")])
    lap_wrap["progress"] = [998, 999, 1000, 1001]  # cumulative progress never drops at a lap wrap
    keep, stale = driving_rows()(lap_wrap, 1000)
    assert stale == [] and keep.all()
