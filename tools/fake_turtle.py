"""Headless recording turtle used by Plan 003 verification."""

from __future__ import annotations

import io
import json
import math
import subprocess
import sys
import tokenize
from pathlib import Path


class _Tracker:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.heading = 0.0
        self.total_heading_change = 0.0
        self.pen_down = True
        self.moves = 0
        self.pen_down_moves = 0
        self.draw_start_x = None
        self.draw_start_y = None

    def move(self, distance: float):
        if self.pen_down and self.draw_start_x is None:
            self.draw_start_x = self.x
            self.draw_start_y = self.y
        radians = math.radians(self.heading)
        self.x += float(distance) * math.cos(radians)
        self.y += float(distance) * math.sin(radians)
        self.moves += 1
        if self.pen_down:
            self.pen_down_moves += 1

    def turn(self, degrees: float):
        self.heading = (self.heading + float(degrees)) % 360.0
        self.total_heading_change += float(degrees)


_tracker = _Tracker()


def reset():
    global _tracker
    _tracker = _Tracker()


def forward(distance):
    _tracker.move(distance)


def backward(distance):
    _tracker.move(-float(distance))


def left(angle):
    _tracker.turn(angle)


def right(angle):
    _tracker.turn(-float(angle))


def penup():
    _tracker.pen_down = False


def pendown():
    _tracker.pen_down = True


def pensize(*_args, **_kwargs):
    return None


def pencolor(*_args, **_kwargs):
    return None


def color(*_args, **_kwargs):
    return None


def speed(*_args, **_kwargs):
    return None


def bgcolor(*_args, **_kwargs):
    return None


def done():
    return None


def exitonclick():
    return None


class _Screen:
    def bgcolor(self, *_args, **_kwargs):
        return None

    def exitonclick(self):
        return None


def Screen():
    return _Screen()


class Turtle:
    forward = staticmethod(forward)
    backward = staticmethod(backward)
    left = staticmethod(left)
    right = staticmethod(right)
    penup = staticmethod(penup)
    pendown = staticmethod(pendown)
    pensize = staticmethod(pensize)
    pencolor = staticmethod(pencolor)
    color = staticmethod(color)
    speed = staticmethod(speed)


def state() -> dict[str, float | int]:
    return {
        "x": _tracker.x,
        "y": _tracker.y,
        "heading": _tracker.heading,
        "total_heading_change": _tracker.total_heading_change,
        "moves": _tracker.moves,
        "pen_down_moves": _tracker.pen_down_moves,
        "draw_start_x": _tracker.draw_start_x,
        "draw_start_y": _tracker.draw_start_y,
    }


def _angular_remainder(value: float) -> float:
    return abs((value + 180.0) % 360.0 - 180.0)


def _has_open_path_comment(source: str) -> bool:
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    return any(
        token.type == tokenize.COMMENT and token.string == "# turtle-check: open-path"
        for token in tokens
    )


def turtle_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    from tools.notebooks import unit_dirs

    units, findings = unit_dirs(root, book, unit)
    if findings:
        return findings
    for unit_dir in units:
        for script in sorted((unit_dir / "assets").glob("*.py")):
            try:
                preamble = (
                    "import json,runpy,sys; import tools.fake_turtle as stub; "
                    "stub.reset(); sys.modules['turtle']=stub; "
                    "runpy.run_path(sys.argv[1], run_name='__main__'); "
                    "print('STATE:'+json.dumps(stub.state(), sort_keys=True))"
                )
                result = subprocess.run(
                    [sys.executable, "-c", preamble, str(script)],
                    cwd=Path(__file__).resolve().parents[1],
                    text=True,
                    capture_output=True,
                    timeout=20,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                findings.append(f"FAIL: {unit_dir.name}: {script.name} exceeded 20s")
                continue
            if result.returncode != 0:
                detail = (
                    result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "error"
                )
                findings.append(f"FAIL: {unit_dir.name}: {script.name} did not complete: {detail}")
                continue
            marker = next(
                (
                    line
                    for line in reversed(result.stdout.splitlines())
                    if line.startswith("STATE:")
                ),
                None,
            )
            if marker is None:
                findings.append(f"FAIL: {unit_dir.name}: {script.name} returned no turtle state")
                continue
            recorded = json.loads(marker.removeprefix("STATE:"))
            if recorded["pen_down_moves"] < 1:
                findings.append(f"FAIL: {unit_dir.name}: {script.name} has no pen-down move")
            if recorded["moves"] >= 10000:
                findings.append(
                    f"FAIL: {unit_dir.name}: {script.name} has {recorded['moves']} moves "
                    "(must be <10000)"
                )
            source = script.read_text(encoding="utf-8")
            if not _has_open_path_comment(source):
                start_x = recorded["draw_start_x"] or 0.0
                start_y = recorded["draw_start_y"] or 0.0
                position_closed = (
                    math.hypot(recorded["x"] - start_x, recorded["y"] - start_y) <= 1e-6
                )
                heading_closed = _angular_remainder(recorded["total_heading_change"]) <= 1e-6
                if not position_closed or not heading_closed:
                    findings.append(
                        f"FAIL: {unit_dir.name}: {script.name} path does not close "
                        f"(position={recorded['x']:.6g},{recorded['y']:.6g}; "
                        f"turn={recorded['total_heading_change']:.6g})"
                    )
    return findings
