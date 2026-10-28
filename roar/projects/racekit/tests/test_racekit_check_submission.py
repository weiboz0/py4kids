"""``check_submission`` and the Python 3.8 compatibility of racekit itself (plan roar-001 Phase D)."""

from __future__ import annotations

import ast
import re
import subprocess
import textwrap

import pytest
from conftest import CONSTRUCTOR, RACEKIT, REPO, STARTER
from racekit.check_submission import (
    check_submission,
    deny_list_findings,
    import_findings,
    main,
    py38_stdlib,
    shape_findings,
)

STEP = '''
async def initialize(self):
    pass

async def step(self):
    await self.vehicle.apply_action({"throttle": 0.3, "steer": 0.0, "brake": 0.0,
                                     "hand_brake": 0.0, "reverse": 0})
'''


def _findings(source: str):
    return deny_list_findings(ast.parse(textwrap.dedent(source), feature_version=(3, 8)))


def test_the_starter_passes(capsys):
    report = check_submission(STARTER)
    assert report.ok, str(report)
    assert report.race.finished and report.race.collisions == 0
    assert report.step_p99_ms <= 5.0
    assert main([str(STARTER)]) == 0
    out = capsys.readouterr().out
    assert "PASS" in out and "python=" in out


def test_py38_stdlib_list_is_exhaustive_and_header_documented():
    names = py38_stdlib()
    for name in ("operator", "contextlib", "asyncio", "math", "typing", "test", "idlelib", "tkinter",
                 "__future__", "dataclasses", "functools", "itertools", "collections", "statistics"):
        assert name in names
    for name in ("numpy", "scipy", "graphlib", "zoneinfo", "tomllib", "site-packages"):
        assert name not in names
    header = [line for line in (RACEKIT / "racekit/contract/py38_stdlib.txt").read_text().splitlines()
              if line.startswith("#")]
    text = "\n".join(header)
    assert "uv run --no-project --python 3.8 python -c" in text
    assert re.search(r"Interpreter: CPython 3\.8\.\d+", text)
    assert f"{len(names)} names in all" in text
    assert len(names) > 250


@pytest.mark.parametrize(("source", "reason"), [
    ("x = 'abc'.removeprefix('a')", "removeprefix"),
    ("x = 'abc'.removesuffix('c')", "removesuffix"),
    ("import functools\n@functools.cache\ndef f():\n    return 1", "functools.cache"),
    ("import functools as ft\n@ft.cache\ndef f():\n    return 1", "functools.cache"),
    ("from functools import cache", "functools.cache"),
    ("import math\nx = math.lcm(2, 3)", "math.lcm"),
    ("from itertools import pairwise", "itertools.pairwise"),
    ("x = (5).bit_count()", "bit_count"),
    ("x = list(zip([1], [2], strict=True))", "strict="),
    ("x = {'a': 1} | {'b': 2}", "dict | dict"),
    ("d = {}\nd |= {'b': 2}", "on a dict"),
    ("import numpy as np\nx = np.trapezoid([1, 2])", "trapezoid"),
    ("ok = isinstance(1, int | float)", "runtime `X | Y`"),
    ("x = list[int]", "at runtime"),
    ("def f(x: int | None) -> None:\n    pass", "`X | Y` annotation"),
    ("def f(x) -> list[int]:\n    return [x]", "in an annotation"),
    ("y: dict[str, int] = {}", "in an annotation"),
    ("def f(x: 'list[int]'):\n    pass", "in an annotation"),
    ("a = {'x': 1}\nb = dict(y=2)\nc = a | b", "dict | dict"),
    ("from typing import Dict\ndef f(a: Dict[str, int], b):\n    a |= b", "on a dict"),
    ("a = {k: 1 for k in 'ab'}\nb: dict = {}\nb |= a", "on a dict"),
    ("import math\nx = math.nextafter(1.0, 2.0)", "math.nextafter"),
    ("import random\nx = random.randbytes(4)", "random.randbytes"),
    ("from statistics import correlation", "statistics.correlation"),
    ("import statistics\nx = statistics.covariance([1, 2], [3, 4])", "statistics.covariance"),
    ("from typing import Optional\nT = Optional[int] | None", "runtime `X | Y`"),
    ("import typing\nT = typing.List[int] | None", "runtime `X | Y`"),
])
def test_deny_list_catches_each_form(source, reason):
    findings = _findings(source)
    assert findings and any(reason in finding for finding in findings), findings


def test_attribute_denials_say_they_are_by_name():
    findings = _findings("class S:\n    def removeprefix(self):\n        pass\nS().removeprefix()\n")
    assert findings and all("flagged by attribute name" in finding for finding in findings)


def test_deny_list_allows_3_8_forms():
    assert _findings('''
        from __future__ import annotations
        from typing import Dict, List, Optional, Union
        import numpy as np

        def f(x: Optional[int], y: Union[int, float]) -> List[int]:
            merged = {**{"a": 1}, **{"b": 2}}
            flags = 0b101 | 0b010
            values: Dict[str, int] = dict(merged)
            return [x or 0, int(y), flags, len(values), int(np.trapz([1, 2]))]
    ''') == []


def test_import_allow_list():
    tree = ast.parse("import os, json\nimport numpy as np\nfrom collections import deque\n"
                     "import roar_py_interface\nfrom roar_py_interface import RoarPyWaypoint\n")
    assert import_findings(tree) == []
    for bad in ("import scipy", "from scipy import optimize", "import pandas", "from . import helper",
                "import graphlib", "import racekit",
                "import importlib\nm = importlib.import_module('scipy')",
                "from importlib import import_module\nm = import_module('json')",
                "m = __import__('scipy')"):
        assert import_findings(ast.parse(bad)), bad
    dynamic = import_findings(ast.parse("m = __import__('json')"))
    assert dynamic and "dynamic import" in dynamic[0]


def test_shape_findings():
    good = ast.parse("class RoarCompetitionSolution:\n" + CONSTRUCTOR + textwrap.indent(STEP, "    "))
    assert shape_findings(good) == []
    assert shape_findings(ast.parse("class Other:\n    pass\n")) == ["no top-level class RoarCompetitionSolution"]


@pytest.mark.parametrize(("body", "constructor", "header", "expected"), [
    ("async def initialize(self):\n    match 1:\n        case 1:\n            pass\n" + STEP.split("async def initialize(self):\n    pass\n")[1],
     None, None, "parse: not valid Python 3.8"),
    (STEP + "\ndef helper(self):\n    return 'x'.removeprefix('x')\n", None, None, "removeprefix"),
    (STEP + "\ndef helper(self, x: int | None):\n    return x\n", None, None, "`X | Y` annotation"),
    (STEP, None, "import scipy\nimport roar_py_interface\n\n\n", "import 'scipy' is not allowed"),
    (STEP, "    def __init__(self, waypoints, vehicle):\n        self.vehicle = vehicle\n", None,
     "__init__ must take"),
    (STEP.replace("async def initialize", "def initialize"), None, None, "initialize must be `async def`"),
    (STEP.replace("async def step", "def step"), None, None, "step must be `async def`"),
    (STEP.replace("async def initialize(self):\n    pass\n", ""), None, None, "has no initialize() method"),
    (STEP.replace('"throttle": 0.3', '"throttle": 1.7'), None, None, "invalid action"),
    (STEP.replace("await self.vehicle", "1 / 0\n    await self.vehicle"), None, None,
     "the race raised ZeroDivisionError"),
])
def test_negative_submissions_fail_with_the_right_reason(write_submission, body, constructor, header, expected):
    kwargs = {}
    if constructor is not None:
        kwargs["constructor"] = constructor
    if header is not None:
        kwargs["header"] = header
    path = write_submission(body, **kwargs)
    report = check_submission(path, max_seconds=5.0)
    assert not report.ok
    assert any(expected in finding for finding in report.findings), str(report)


def test_a_valid_agent_that_never_finishes_fails(write_submission):
    path = write_submission(STEP.replace('"throttle": 0.3', '"throttle": 0.0'))
    report = check_submission(path, max_seconds=5.0)
    assert not report.ok
    assert report.findings == [
        f"race: the race did not finish within 5.0 s: progress 0 of the required {report.race.progress_required}"
    ]


def test_the_report_says_the_ast_stage_is_not_a_proof():
    text = str(check_submission(STARTER))
    assert "deny-list, not a proof" in text and "isolated 3.8 run" in text


def test_a_slow_step_fails_the_p99_budget(write_submission):
    path = write_submission(STEP.replace("await self.vehicle", "time.sleep(0.008)\n    await self.vehicle"),
                            header="import time\n\nimport roar_py_interface\n\n\n")
    report = check_submission(path, max_seconds=6.0)
    assert not report.ok
    assert any("exceeds the 5.0 ms budget" in finding for finding in report.findings), str(report)
    assert report.step_p99_ms > 5.0


def test_failed_static_stages_skip_the_race(write_submission):
    path = write_submission(STEP, header="import scipy\n\n\n")
    report = check_submission(path)
    assert report.race is None and report.skipped == ["race"]
    assert main([str(path)]) == 1


def _racekit_modules():
    return sorted((RACEKIT / "racekit").glob("*.py"))


@pytest.mark.parametrize("path", _racekit_modules(), ids=lambda path: path.name)
def test_every_racekit_module_is_python_3_8(path):
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, feature_version=(3, 8))
    assert deny_list_findings(tree) == []
    first = next(node for node in tree.body if not (
        isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
    ))
    assert isinstance(first, ast.ImportFrom) and first.module == "__future__", path.name
    assert [alias.name for alias in first.names] == ["annotations"]


def _top_level_modules(nodes):
    found = set()
    for node in nodes:
        if isinstance(node, ast.Import):
            found |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.add(node.module.split(".")[0])
    return found


def test_racekit_core_imports_numpy_only():
    """Module-level imports are numpy and the 3.8 standard library only; matplotlib is imported
    lazily, inside the functions of the analysis module ``plots`` only."""
    module_level = set()
    lazy = {}
    for path in _racekit_modules():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        module_level |= _top_level_modules(tree.body)
        nested = _top_level_modules(ast.walk(tree)) - _top_level_modules(tree.body) - py38_stdlib() - {"numpy"}
        if nested:
            lazy[path.name] = nested
    assert module_level - py38_stdlib() == {"numpy"}
    assert lazy == {"plots.py": {"matplotlib"}}


AGENTS = sorted((RACEKIT / "agents").glob("*.py"))


def test_unit_01_is_the_starter_copied():
    assert (RACEKIT / "agents" / "unit-01.py").read_bytes() == STARTER.read_bytes()
    assert {"starter.py", "unit-01.py"} <= {path.name for path in AGENTS}


@pytest.mark.slow
@pytest.mark.parametrize("agent", AGENTS, ids=lambda path: path.name)
def test_isolated_python_3_8_check_submission_run(agent):
    """The isolated 3.8 run (design 013 §4.1), for every reference submission in ``agents/``.
    Needs uv's managed CPython 3.8: if it cannot be fetched, this test FAILS rather than skips."""
    command = [
        "uv", "run", "--no-project", "--python", "3.8",
        "--with", "numpy<1.25", "--with", "scipy<1.11", "--with-editable", "roar/projects/racekit",
        "python", "-m", "racekit.check_submission", agent.relative_to(REPO).as_posix(),
    ]
    run = subprocess.run(command, cwd=REPO, capture_output=True, text=True, timeout=600, check=False)
    assert run.returncode == 0, run.stdout + run.stderr
    match = re.search(r"python=(\d+)\.(\d+)\.\d+ numpy=(\d+)\.(\d+)", run.stdout)
    assert match, run.stdout
    assert (int(match.group(1)), int(match.group(2))) == (3, 8)
    assert (int(match.group(3)), int(match.group(4))) < (1, 25)
    assert "PASS" in run.stdout
    assert not (REPO / "roar/projects/racekit/uv.lock").exists()


# The 3.8 smoke race (plan roar-004 G4.9): one lap of `oval` on carla_like(noise=True), which exercises
# DynamicCar, racekit._truth, the section grip, attach_track and the per-tick spin-out check.
SMOKE_RACE = '''\
import math, platform
import numpy as np
from racekit.cars import DynamicCar, carla_like
from racekit.runner import run_race

class Gentle:
    def __init__(self, waypoints, vehicle, camera, location, velocity, rpy, occupancy, collision):
        self.points = np.array([w.location[:2] for w in waypoints], dtype=float)
        self.vehicle, self.location, self.velocity, self.rpy = vehicle, location, velocity, rpy
        self.index = 0

    async def initialize(self):
        pass

    async def step(self):
        here = np.asarray(self.location.get_last_gym_observation()[:2], dtype=float)
        yaw = float(self.rpy.get_last_gym_observation()[2])
        speed = float(np.linalg.norm(self.velocity.get_last_gym_observation()))
        n = len(self.points)
        window = [(self.index + k) % n for k in range(20)]
        self.index = min(window, key=lambda i: float(np.sum((self.points[i] - here) ** 2)))
        ahead = self.points[(self.index + 5) % n] - here
        alpha = math.atan2(ahead[1], ahead[0]) - yaw
        alpha = (alpha + math.pi) % (2 * math.pi) - math.pi
        delta = math.atan2(2 * 2.875 * math.sin(alpha), float(np.hypot(*ahead)))
        command = 0.2 * (12.0 - speed)
        await self.vehicle.apply_action({"throttle": min(1.0, max(0.0, command)),
                                         "steer": min(1.0, max(-1.0, -delta / math.radians(70.0))),
                                         "brake": min(1.0, max(0.0, -command)), "hand_brake": 0.0,
                                         "reverse": 0, "target_gear": 0})

car = carla_like(noise=True)
result = run_race(Gentle, "oval", car=car, laps=1, max_seconds=300.0, seed=0)
assert isinstance(car, DynamicCar) and car.per_section and len(set(car.mu)) == 6
assert result.finished and result.collisions == 0 and result.respawn_causes == [], result
car.reset(0.0, 0.0, 0.0, 0.0)
car.vx, car.vy = 10.0, 6.0  # |beta| = 31 degrees at 11.7 m/s
assert car.spun_out()
print("python=%s numpy=%s %r" % (platform.python_version(), np.__version__, result))
'''


@pytest.mark.slow
def test_isolated_python_3_8_dynamic_car_smoke_race(tmp_path):
    script = tmp_path / "smoke_race.py"
    script.write_text(SMOKE_RACE, encoding="utf-8")
    command = [
        "uv", "run", "--no-project", "--python", "3.8",
        "--with", "numpy<1.25", "--with-editable", "roar/projects/racekit",
        "python", str(script),
    ]
    run = subprocess.run(command, cwd=REPO, capture_output=True, text=True, timeout=600, check=False)
    assert run.returncode == 0, run.stdout + run.stderr
    match = re.search(r"python=(\d+)\.(\d+)\.\d+ numpy=(\d+)\.(\d+)", run.stdout)
    assert match, run.stdout
    assert (int(match.group(1)), int(match.group(2))) == (3, 8)
    assert (int(match.group(3)), int(match.group(4))) < (1, 25)
    assert "finished" in run.stdout and "0 collisions" in run.stdout
    assert not (REPO / "roar/projects/racekit/uv.lock").exists()
