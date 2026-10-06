"""Replay a headless turtle program as a compact TikZ figure."""

from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout
from unittest.mock import patch

from tools import fake_turtle

# xcolor's svgnames spellings for colours used by the course's turtle programs.
SVG_NAMES = {
    name.lower(): name for name in (
        "Black", "Blue", "Brown", "Coral", "Crimson", "DarkCyan",
        "DarkGreen", "DarkOrange", "DarkViolet", "DimGray", "ForestGreen",
        "Gold", "Goldenrod", "Gray", "Green", "Magenta", "Maroon",
        "Navy", "Orchid", "Purple", "Red", "RoyalBlue", "SeaGreen",
        "Silver", "SlateGray", "Teal", "Turquoise", "White",
    )
}


def _replay(source: str, stdin: str | None = None) -> list[tuple]:
    """Execute a turtle script with a fresh tracker and return its pen-down segments.

    Each segment is `(x1, y1, x2, y2, color, width)`, as `fake_turtle.segments()` records it.
    """
    fake_turtle.reset()
    if stdin is None:
        stdin = fake_turtle.sample_input(source)
    if stdin is None and fake_turtle.calls_input(source):
        raise RuntimeError("turtle figure replay needs sample input")
    previous = sys.modules.get("turtle")
    sys.modules["turtle"] = fake_turtle
    try:
        try:
            with patch("sys.stdin", io.StringIO(stdin or "")), redirect_stdout(io.StringIO()):
                exec(compile(source, "<turtle figure>", "exec"), {"__name__": "__main__"})  # noqa: S102 - course script replay
        except BaseException as error:
            raise RuntimeError(f"turtle figure replay failed: {error}") from error
    finally:
        if previous is None:
            sys.modules.pop("turtle", None)
        else:
            sys.modules["turtle"] = previous
    return fake_turtle.segments()


def _coordinate(value: float) -> float:
    """A stable JSON number: 6 decimals, and never `-0.0`."""
    rounded = round(float(value), 6)
    return 0.0 if rounded == 0 else rounded


def turtle_segments(source: str, stdin: str | None = None) -> list[dict]:
    """The replay `figure_tikz` draws, returned as data: one dict per pen-down move.

    Each is `{x1, y1, x2, y2, color, width}` (design 012 D3, the bundle's `turtle-figure` block).
    """
    return [
        {"x1": _coordinate(x1), "y1": _coordinate(y1), "x2": _coordinate(x2), "y2": _coordinate(y2),
         "color": str(color) or "black", "width": float(width)}
        for x1, y1, x2, y2, color, width in _replay(source, stdin)
    ]


def figure_tikz(source: str, stdin: str | None = None,
                caption: str = "Drawing made by the program above") -> str:
    """Execute a turtle script with a fresh tracker and return a TikZ picture.

    The caller adds its unit/cell context to any exception when reporting a build failure.
    """
    traced = _replay(source, stdin)
    coordinates = [(0.0, 0.0)] + [point for x1, y1, x2, y2, _, _ in traced
                                    for point in ((x1, y1), (x2, y2))]
    padding = max(2.2, *(float(pen_width) * 0.2 for *_, pen_width in traced)) + 2
    left = min(x for x, _ in coordinates) - padding
    right = max(x for x, _ in coordinates) + padding
    bottom = min(y for _, y in coordinates) - padding
    top = max(y for _, y in coordinates) + padding
    width = right - left
    height = top - bottom
    lines = [
        # Both limits divide the same scale factor, preserving aspect ratio.
        r"\begin{pubfigure}",
        rf"\pgfmathsetmacro{{\figscale}}{{min(2.4, 0.8\textwidth/{max(width, 1):.6g}pt, 7cm/{max(height, 1):.6g}pt)}}",
        r"\begin{tikzpicture}[x=1pt,y=1pt,scale=\figscale]",
        rf"\useasboundingbox ({left:.6f},{bottom:.6f}) rectangle ({right:.6f},{top:.6f});",
    ]
    for x1, y1, x2, y2, color, pen_width in traced:
        mapped = SVG_NAMES.get(str(color).lower(), "black")
        lines.append(
            rf"\draw[line width={float(pen_width) * 0.4:.6g}pt, color={mapped}] "
            rf"({x1:.6g},{y1:.6g}) -- ({x2:.6g},{y2:.6g});"
        )
    lines.append(r"\path[draw, line width=0.4pt, color=black] (0,0) circle[radius=2pt];")
    lines.append(r"\end{tikzpicture}")
    lines.append(r"\par\smallskip{\scriptsize\color{black!60}" + caption + "}")
    lines.append(r"\end{pubfigure}")
    return "\n".join(lines)
