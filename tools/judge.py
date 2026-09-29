"""Subprocess judge for stdin-first contest solutions (Plan 036).

A reference solution is a real contest script in an entry's ``assets/`` dir that reads stdin and
prints stdout. ``judge_findings`` runs each solver against committed ``<pid>/<k>.in`` fixtures and
compares stdout to ``<pid>/<k>.out``: token-compared (whitespace-split) by default, and
line-exact in ``acsl`` books (design 009 D4; see :func:`outputs_match`).  Modeled on :func:`tools.fake_turtle.turtle_findings`.

BOOK-SCOPED to books with the ``judge: true`` flag in ``books.yaml``: returns ``[]`` for any other
book (the "assets/ + .py" new-model detector is indistinguishable from turtle assets in the Python
books).  This is an intentional documented no-op, not the
fail-closed-on-missing-root convention used by the notebook checks.

Short-answer items (design 009 D4): an ``## Exercise N`` / ``## Question N`` heading cell tagged
``short-answer`` needs no solver. Its solution section instead ends its worked answer with exactly
one ``**Answer:** `<text>` `` line and has >= 1 live ``verify`` code cell asserting
``str(<computed>) == "<text>"`` with that same literal as a TOP-LEVEL statement of the cell
(checked here statically; ``exec-solutions`` executes it). Every entry of an ``acsl`` book is on the stdin model, with or without ``assets/``.
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

from tools.books import book_flag
from tools.notebooks import (
    EXERCISE_HEADING,
    PROBLEM_HEADING,
    QUESTION_HEADING,
    _fail,
    _markdown_heading_occurrences,
    _strip_markdown_fences,
    code_cells,
    content_dirs,
    is_tautology,
    read_nb,
    tags,
)

JUDGE_TIMEOUT_S = 30
REPO_ROOT = Path(__file__).resolve().parents[1]
SOLVER_STEM = re.compile(r"^(?:l|ex|q|p)\d+$")
_LESSON_ASSET = re.compile(r"assets/(l\d+)\.py")
_NUM = re.compile(r"\d+")
SHORT_ANSWER_TAG = "short-answer"
VERIFY_TAG = "verify"
# assets/<this>/ holds verify-cell evaluator modules (plan 094); judge-check ignores it.
VERIFY_ASSETS_DIR = "verify"
# The one machine-readable answer line of a short-answer worked solution.
ANSWER_LINE = re.compile(r"^\*\*Answer:\*\* `([^`\n]+)`[ \t]*$", re.MULTILINE)
ANSWER_MARK = re.compile(r"^[ \t]*\*\*Answer", re.MULTILINE)


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


def _item_headings(notebook, pattern) -> list[tuple[int, list[str]]]:
    """(item number, heading-cell tags) for each ``## Exercise N`` / ``## Question N`` heading."""
    return [
        (int(_NUM.search(heading).group()), list(tags(notebook.cells[index])))
        for heading, index in _markdown_heading_occurrences(notebook, pattern)
    ]


def short_answer_items(entry_dir: Path, kind: str) -> set[int]:
    """Item numbers whose heading cell is tagged ``short-answer`` (units: exercises; checkpoints)."""
    source = {"unit": "exercises.ipynb", "checkpoint": "checkpoint.ipynb"}.get(kind)
    pattern = {"unit": EXERCISE_HEADING, "checkpoint": QUESTION_HEADING}.get(kind)
    if source is None or not (entry_dir / source).is_file():
        return set()
    return {
        number
        for number, cell_tags in _item_headings(read_nb(entry_dir / source), pattern)
        if SHORT_ANSWER_TAG in cell_tags
    }


def _expected_pids(entry_dir: Path, kind: str) -> set[str]:
    """Derive the set of expected solver stems from headings / manifest (end-unanchored patterns).

    Short-answer items (heading cell tagged ``short-answer``) need no solver.
    """
    pids: set[str] = set()
    short = short_answer_items(entry_dir, kind)
    if kind == "unit":
        exercises = entry_dir / "exercises.ipynb"
        if exercises.is_file():
            pids |= {
                f"ex{n}"
                for n in _heading_numbers(read_nb(exercises), EXERCISE_HEADING)
                if n not in short
            }
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
            pids |= {
                f"q{n}"
                for n in _heading_numbers(read_nb(checkpoint), QUESTION_HEADING)
                if n not in short
            }
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


def _output_lines(text: str) -> list[str]:
    lines = [line.rstrip() for line in text.splitlines()]
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def outputs_match(actual: str, expected: str, *, line_exact: bool) -> bool:
    """Judge comparison. Token mode (usaco-bronze's contract) compares whitespace-split tokens.

    Line-exact mode (``acsl`` books, design 009 D4) compares line by line after stripping trailing
    whitespace on each line and ignoring trailing empty lines; everything else must match, so a
    required single line ``15 10 4`` does not accept ``15\n10\n4``.
    """
    if line_exact:
        return _output_lines(actual) == _output_lines(expected)
    return actual.split() == expected.split()


def _run_case(script: Path, inp: Path, outp: Path, scope: str, stem: str,
              line_exact: bool = False) -> str | None:
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
    if not outputs_match(result.stdout, outp.read_text(encoding="utf-8"), line_exact=line_exact):
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


def _section_cells(notebook, heading: str, number: int) -> list | None:
    """The heading cell plus every cell up to the next same-kind heading, or None if absent."""
    this = re.compile(rf"^{re.escape(heading)} {number}\b", re.MULTILINE)
    any_item = re.compile(rf"^{re.escape(heading)} \d+\b", re.MULTILINE)
    cells = notebook.cells
    for index, cell in enumerate(cells):
        if cell.cell_type == "markdown" and this.search(_strip_markdown_fences(cell.source)):
            section = [cell]
            for later in cells[index + 1 :]:
                if later.cell_type == "markdown" and any_item.search(
                    _strip_markdown_fences(later.source)
                ):
                    break
                section.append(later)
            return section
    return None


def verify_literals(source: str) -> list[str]:
    """Literals of every non-vacuous TOP-LEVEL ``assert str(<computed>) == "<text>"`` in a cell.

    Only statements of the module body count: an assert nested in ``if``/``for``/``while``/
    ``try``/``with``/``def``/``class`` may never run (``if False:``, an uncalled ``def``) or be
    swallowed (``try: ... except``), so it proves nothing about the answer.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    literals = []
    for node in tree.body:
        if not isinstance(node, ast.Assert) or is_tautology(node.test):
            continue
        test = node.test
        if not (
            isinstance(test, ast.Compare)
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Eq)
            and isinstance(test.comparators[0], ast.Constant)
            and isinstance(test.comparators[0].value, str)
        ):
            continue
        left = test.left
        if (
            isinstance(left, ast.Call)
            and isinstance(left.func, ast.Name)
            and left.func.id == "str"
            and len(left.args) == 1
            and not left.keywords
            and not isinstance(left.args[0], ast.Constant)  # str("7") == "7" proves nothing
        ):
            literals.append(test.comparators[0].value)
    return literals


def short_answer_findings(entry_dir: Path, kind: str) -> list[str]:
    """The design 009 D4 rule for every short-answer item of a unit or checkpoint."""
    items = short_answer_items(entry_dir, kind)
    if not items:
        return []
    scope = entry_dir.name
    heading = {"unit": "## Exercise", "checkpoint": "## Question"}[kind]
    label = heading.removeprefix("## ")
    solutions = entry_dir / "solutions.ipynb"
    if not solutions.is_file():
        return [_fail(scope, "missing solutions.ipynb for short-answer items")]
    notebook = read_nb(solutions)
    findings = []
    for number in sorted(items):
        item = f"{label} {number}"
        section = _section_cells(notebook, heading, number)
        if section is None:
            findings.append(_fail(scope, f"{item}: short-answer item has no solution section"))
            continue
        markdown = "\n".join(
            _strip_markdown_fences(cell.source) for cell in section if cell.cell_type == "markdown"
        )
        marks = ANSWER_MARK.findall(markdown)
        answers = ANSWER_LINE.findall(markdown)
        if len(marks) != 1 or len(answers) != 1:
            findings.append(
                _fail(
                    scope,
                    f"{item}: short-answer solution needs exactly one '**Answer:** `<text>`' "
                    f"line (found {len(answers)} well-formed of {len(marks)})",
                )
            )
            continue
        answer = answers[0]
        verify_cells = [
            cell
            for cell in section
            if cell.cell_type == "code"
            and VERIFY_TAG in tags(cell)
            and "no-exec" not in tags(cell)
        ]
        if not verify_cells:
            findings.append(
                _fail(scope, f"{item}: short-answer solution has no executed 'verify' cell")
            )
            continue
        literals = [value for cell in verify_cells for value in verify_literals(cell.source)]
        if answer not in literals:
            findings.append(
                _fail(
                    scope,
                    f"{item}: no non-vacuous verify assert str(...) == {answer!r} "
                    f"matching the **Answer:** line (verify literals: {literals})",
                )
            )
    return findings


def judge_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    if not book_flag(root, book, "judge"):
        return []  # intentional no-op outside judge books (see module docstring)
    acsl_book = book_flag(root, book, "acsl")
    entries, findings = content_dirs(root, book, unit)
    if findings:
        return findings
    for entry_dir, kind in entries:
        assets = entry_dir / "assets"
        if not assets.is_dir() and not acsl_book:
            continue  # not yet migrated to the stdin model; partial-book tolerant
        scope = entry_dir.name
        scripts = (
            {p.stem: p for p in sorted(assets.glob("*.py"))} if assets.is_dir() else {}
        )
        expected = _expected_pids(entry_dir, kind)
        for pid in sorted(expected):
            if pid not in scripts:
                findings.append(_fail(scope, f"missing solver {pid}.py"))
        prefix = {"unit": "ex", "checkpoint": "q"}.get(kind)
        for number in sorted(short_answer_items(entry_dir, kind)):
            if f"{prefix}{number}" in scripts:
                findings.append(
                    _fail(
                        scope,
                        f"{prefix}{number} is tagged short-answer but has solver "
                        f"{prefix}{number}.py (an item is exactly one kind)",
                    )
                )
        findings.extend(short_answer_findings(entry_dir, kind))
        if not assets.is_dir():
            continue
        # every solver (expected, or a reserved (l|ex|q|p)N stem) is judged + mirrored; others helpers
        for stem, script in scripts.items():
            if not (stem in expected or SOLVER_STEM.match(stem)):
                continue  # helper module: source-policy-scanned elsewhere, not run here
            pairs = _fixture_pairs(assets / stem, scope, stem, findings)
            if len(pairs) < 2:
                findings.append(_fail(scope, f"{stem}.py needs >=2 fixture pairs (has {len(pairs)})"))
            for inp, outp in pairs:
                problem = _run_case(script, inp, outp, scope, stem, line_exact=acsl_book)
                if problem:
                    findings.append(problem)
            mirror = _mirror_source(entry_dir, kind, stem)
            if mirror is None or _norm_ws(mirror) != _norm_ws(script.read_text(encoding="utf-8")):
                findings.append(_fail(scope, f"{stem}.py has no mirroring display cell (drift?)"))
        # orphan fixture dirs with no matching .py; assets/verify/ holds answer-checking evaluators
        # imported by verify cells (plan 094), not fixtures, so it is exempt
        for sub in sorted(p for p in assets.iterdir() if p.is_dir()):
            if sub.name == VERIFY_ASSETS_DIR:
                continue
            if sub.name not in scripts:
                findings.append(_fail(scope, f"fixture dir {sub.name}/ has no {sub.name}.py"))
    return findings
