"""Subprocess judge for Book-2 stdin-first solutions (Plan 036).

A reference solution is a real contest script in an entry's ``assets/`` dir that reads stdin and
prints stdout. ``judge_findings`` runs each solver against committed ``<pid>/<k>.in`` fixtures and
token-compares stdout to ``<pid>/<k>.out``.  Modeled on :func:`tools.fake_turtle.turtle_findings`.

BOOK-SCOPED to ``book2``: returns ``[]`` for any other book (the "assets/ + .py" new-model detector
is indistinguishable from Book-1 turtle assets).  This is an intentional documented no-op, not the
fail-closed-on-missing-root convention used by the notebook checks.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from tools.notebooks import (
    EXERCISE_HEADING,
    PROBLEM_HEADING,
    QUESTION_HEADING,
    _fail,
    _markdown_heading_occurrences,
    _strip_markdown_fences,
    code_cells,
    content_dirs,
    read_nb,
    tags,
)

JUDGE_TIMEOUT_S = 30
REPO_ROOT = Path(__file__).resolve().parents[1]
SOLVER_STEM = re.compile(r"^(?:l|ex|q|p)\d+$")
_LESSON_ASSET = re.compile(r"assets/(l\d+)\.py")
_NUM = re.compile(r"\d+")


def _referenced_lesson_pids(notebook) -> set[str]:
    """Lesson-solver PIDs the lesson.ipynb references (assets/lN.py, filtered to the l\\d+ stem)."""
    pids: set[str] = set()
    for cell in notebook.cells:
        pids.update(_LESSON_ASSET.findall(cell.source))
    return pids


def _norm_ws(source: str) -> str:
    """Modulo-whitespace: per-line trailing strip + trailing blank-line strip (no full collapse)."""
    lines = [line.rstrip() for line in source.splitlines()]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def _heading_numbers(notebook, pattern) -> list[int]:
    return [
        int(_NUM.search(heading).group())
        for heading, _index in _markdown_heading_occurrences(notebook, pattern)
    ]


def _expected_pids(entry_dir: Path, kind: str) -> set[str]:
    """Derive the set of expected solver stems from headings / manifest (end-unanchored patterns)."""
    pids: set[str] = set()
    if kind == "unit":
        exercises = entry_dir / "exercises.ipynb"
        if exercises.is_file():
            pids |= {f"ex{n}" for n in _heading_numbers(read_nb(exercises), EXERCISE_HEADING)}
        # Lesson solvers: the manifest floor (l1..l{manifest.lessons}) UNION every lesson solver the
        # lesson references (assets/lN.py) — so a unit with more solvers than lessons (e.g. U06's four)
        # still fails closed on a referenced-but-missing lN.py.
        lessons = _manifest_lessons(entry_dir)
        pids |= {f"l{n}" for n in range(1, lessons + 1)}
        lesson_nb = entry_dir / "lesson.ipynb"
        if lesson_nb.is_file():
            pids |= _referenced_lesson_pids(read_nb(lesson_nb))
    elif kind == "checkpoint":
        checkpoint = entry_dir / "checkpoint.ipynb"
        if checkpoint.is_file():
            pids |= {f"q{n}" for n in _heading_numbers(read_nb(checkpoint), QUESTION_HEADING)}
    elif kind == "project":
        brief = entry_dir / "brief.ipynb"
        if brief.is_file():
            pids |= {f"p{n}" for n in _heading_numbers(read_nb(brief), PROBLEM_HEADING)}
    return pids


def _manifest_lessons(entry_dir: Path) -> int:
    import yaml

    manifest_path = entry_dir / "manifest.yaml"
    if not manifest_path.is_file():
        return 0
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if isinstance(manifest, dict) and isinstance(manifest.get("lessons"), int):
        return manifest["lessons"]
    return 0


def _fixture_pairs(fx_dir: Path, scope: str, stem: str, findings: list[str]):
    pairs = []
    if fx_dir.is_dir():
        for inp in sorted(fx_dir.glob("*.in")):
            outp = inp.with_suffix(".out")
            if outp.is_file():
                pairs.append((inp, outp))
            else:
                findings.append(_fail(scope, f"{stem}: {inp.name} has no matching .out"))
        for outp in sorted(fx_dir.glob("*.out")):
            if not outp.with_suffix(".in").is_file():
                findings.append(_fail(scope, f"{stem}: {outp.name} has no matching .in"))
    return pairs


def _run_case(script: Path, inp: Path, outp: Path, scope: str, stem: str) -> str | None:
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            input=inp.read_text(encoding="utf-8"),
            text=True,
            capture_output=True,
            timeout=JUDGE_TIMEOUT_S,
            cwd=REPO_ROOT,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return _fail(scope, f"{stem}.py exceeded {JUDGE_TIMEOUT_S}s on {inp.name}")
    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "error"
        return _fail(scope, f"{stem}.py failed on {inp.name}: {detail}")
    if result.stdout.strip() == "":
        return _fail(scope, f"{stem}.py produced no output on {inp.name}")
    if result.stdout.split() != outp.read_text(encoding="utf-8").split():
        return _fail(scope, f"{stem}.py wrong output on {inp.name}")
    return None


def _mirror_source(entry_dir: Path, kind: str, stem: str) -> str | None:
    """Return the display-cell source that must mirror <stem>.py, or None if no cell is located."""
    if stem.startswith("l"):
        lesson = entry_dir / "lesson.ipynb"
        if not lesson.is_file():
            return None
        target = _norm_ws((entry_dir / "assets" / f"{stem}.py").read_text(encoding="utf-8"))
        for cell in code_cells(read_nb(lesson)):
            if "no-exec" in tags(cell) and _norm_ws(cell.source) == target:
                return cell.source  # a matching mirror exists
        return None
    # exN / qN / pN: the code cell under the matching heading in solutions.ipynb
    heading = {"e": "## Exercise", "q": "## Question", "p": "## Problem"}[stem[0]]
    number = _NUM.search(stem).group()
    sol = entry_dir / "solutions.ipynb"
    if not sol.is_file():
        return None
    notebook = read_nb(sol)
    cells = notebook.cells
    pattern = re.compile(rf"^{re.escape(heading)} {number}\b", re.MULTILINE)
    for i, cell in enumerate(cells):
        if cell.cell_type == "markdown" and pattern.search(_strip_markdown_fences(cell.source)):
            for later in cells[i + 1 :]:
                if later.cell_type == "markdown" and re.search(
                    rf"^{re.escape(heading)} \d+\b", _strip_markdown_fences(later.source), re.MULTILINE
                ):
                    break
                if later.cell_type == "code":
                    return later.source
            return None
    return None


def judge_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    if book != "book2":
        return []  # intentional no-op outside book2 (see module docstring)
    entries, findings = content_dirs(root, book, unit)
    if findings:
        return findings
    for entry_dir, kind in entries:
        assets = entry_dir / "assets"
        if not assets.is_dir():
            continue  # not yet migrated to the stdin model; partial-book tolerant
        scope = entry_dir.name
        scripts = {p.stem: p for p in sorted(assets.glob("*.py"))}
        expected = _expected_pids(entry_dir, kind)
        for pid in sorted(expected):
            if pid not in scripts:
                findings.append(_fail(scope, f"missing solver {pid}.py"))
        # every solver (expected, or a reserved (l|ex|q|p)N stem) is judged + mirrored; others helpers
        for stem, script in scripts.items():
            if not (stem in expected or SOLVER_STEM.match(stem)):
                continue  # helper module: source-policy-scanned elsewhere, not run here
            pairs = _fixture_pairs(assets / stem, scope, stem, findings)
            if len(pairs) < 2:
                findings.append(_fail(scope, f"{stem}.py needs >=2 fixture pairs (has {len(pairs)})"))
            for inp, outp in pairs:
                problem = _run_case(script, inp, outp, scope, stem)
                if problem:
                    findings.append(problem)
            mirror = _mirror_source(entry_dir, kind, stem)
            if mirror is None or _norm_ws(mirror) != _norm_ws(script.read_text(encoding="utf-8")):
                findings.append(_fail(scope, f"{stem}.py has no mirroring display cell (drift?)"))
        # orphan fixture dirs with no matching .py
        for sub in sorted(p for p in assets.iterdir() if p.is_dir()):
            if sub.name not in scripts:
                findings.append(_fail(scope, f"fixture dir {sub.name}/ has no {sub.name}.py"))
    return findings
