"""Replay a headless turtle program as a compact TikZ figure."""

from __future__ import annotations

import sys

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


def figure_tikz(source: str) -> str:
    """Execute a turtle script with a fresh tracker and return a TikZ picture.

    The caller adds its unit/cell context to any exception when reporting a build failure.
    """
    fake_turtle.reset()
    previous = sys.modules.get("turtle")
    sys.modules["turtle"] = fake_turtle
    try:
        try:
            exec(compile(source, "<turtle figure>", "exec"), {"__name__": "__main__"})  # noqa: S102 - course script replay
        except BaseException as error:
            raise RuntimeError(f"turtle figure replay failed: {error}") from error
    finally:
        if previous is None:
            sys.modules.pop("turtle", None)
        else:
            sys.modules["turtle"] = previous

    traced = fake_turtle.segments()
    coordinates = [(0.0, 0.0)] + [point for x1, y1, x2, y2, _, _ in traced
                                    for point in ((x1, y1), (x2, y2))]
    width = max(x for x, _ in coordinates) - min(x for x, _ in coordinates)
    height = max(y for _, y in coordinates) - min(y for _, y in coordinates)
    lines = [
        # Both limits divide the same scale factor, preserving aspect ratio.
        rf"\pgfmathsetmacro{{\figscale}}{{min(1, 0.8\textwidth/{max(width, 1):.6g}pt, 7cm/{max(height, 1):.6g}pt)}}",
        r"\begin{tikzpicture}[x=1pt,y=1pt,scale=\figscale]",
    ]
    for x1, y1, x2, y2, color, pen_width in traced:
        mapped = SVG_NAMES.get(str(color).lower(), "black")
        lines.append(
            rf"\draw[line width={float(pen_width) * 0.4:.6g}pt, color={mapped}] "
            rf"({x1:.6g},{y1:.6g}) -- ({x2:.6g},{y2:.6g});"
        )
    lines.append(r"\path[draw, line width=0.4pt, color=black] (0,0) circle[radius=2pt];")
    lines.append(r"\end{tikzpicture}")
    return "\n".join(lines)
