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
    lines.append(r"\par\smallskip{\scriptsize\color{black!60}Drawing made by the program above}")
    lines.append(r"\end{pubfigure}")
    return "\n".join(lines)
