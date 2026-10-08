"""The browser port of ``tools/fake_turtle.py`` (plan 104): a headless recording turtle.

Pyodide ships no tkinter, so the runner installs this module as ``turtle`` for every run whose
source imports turtle (``imports_turtle``). The drawing API and the tracker are a line-for-line
port of ``tools/fake_turtle.py``; ``turtle_rule`` is the three-part rule of its
``turtle_findings`` (at least one pen-down move; fewer than 10,000 moves; a closed path unless
the source carries ``# turtle-check: open-path``), returning verdicts instead of findings.
``tests/test_runner_harness.py`` proves the port draws and judges exactly as the original.
"""

from __future__ import annotations

import io
import math
import re
import tokenize

MAX_MOVES = 10000


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
        self.color = "black"
        self.width = 1
        self.drawn_segments = []

    def move(self, distance: float):
        old_x, old_y = self.x, self.y
        if self.pen_down and self.draw_start_x is None:
            self.draw_start_x = self.x
            self.draw_start_y = self.y
        radians = math.radians(self.heading)
        self.x += float(distance) * math.cos(radians)
        self.y += float(distance) * math.sin(radians)
        self.moves += 1
        if self.pen_down:
            self.pen_down_moves += 1
            self.drawn_segments.append(
                (old_x, old_y, self.x, self.y, self.color, self.width)
            )

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


def pensize(width=None):
    if width is not None:
        _tracker.width = width
    return _tracker.width


def pencolor(value=None):
    if value is not None:
        _tracker.color = value
    return _tracker.color


def color(*values):
    if values:
        _tracker.color = values[0]
    return _tracker.color


def segments():
    return list(_tracker.drawn_segments)


def final_state():
    return (_tracker.x, _tracker.y, _tracker.heading, _tracker.pen_down)


def imports_turtle(source: str) -> bool:
    return re.search(r"(?m)^\s*(?:import turtle\b|from turtle import\b)", source) is not None


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
    try:
        return any(
            token.type == tokenize.COMMENT and token.string == "# turtle-check: open-path"
            for token in tokens
        )
    except (tokenize.TokenError, SyntaxError):
        return False


def turtle_rule(recorded: dict, source: str) -> list[dict]:
    """The three-part rule of ``tools.fake_turtle.turtle_findings`` as named verdicts."""
    verdicts = [
        {
            "name": "turtle: draws",
            "pass": recorded["pen_down_moves"] >= 1,
            "detail": "" if recorded["pen_down_moves"] >= 1 else "no pen-down move",
        },
        {
            "name": "turtle: moves",
            "pass": recorded["moves"] < MAX_MOVES,
            "detail": ""
            if recorded["moves"] < MAX_MOVES
            else f"{recorded['moves']} moves (must be fewer than {MAX_MOVES})",
        },
    ]
    if _has_open_path_comment(source):
        verdicts.append({"name": "turtle: closed path", "pass": True, "detail": "open path allowed"})
        return verdicts
    start_x = recorded["draw_start_x"] or 0.0
    start_y = recorded["draw_start_y"] or 0.0
    position_closed = math.hypot(recorded["x"] - start_x, recorded["y"] - start_y) <= 1e-6
    heading_closed = _angular_remainder(recorded["total_heading_change"]) <= 1e-6
    closed = position_closed and heading_closed
    detail = (
        ""
        if closed
        else (
            f"path does not close (position={recorded['x']:.6g},{recorded['y']:.6g}; "
            f"turn={recorded['total_heading_change']:.6g})"
        )
    )
    verdicts.append({"name": "turtle: closed path", "pass": closed, "detail": detail})
    return verdicts
