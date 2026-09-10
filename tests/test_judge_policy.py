"""Tests for the Plan-036 stdin judge + source-policy checkers."""

from pathlib import Path

import nbformat
import pytest
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

import tools.judge as judge_mod
from tools.judge import judge_findings
from tools.source_policy import source_policy_findings

REPO = Path(__file__).resolve().parents[1]


def _nb(path, *cells):
    notebook = new_notebook()
    notebook.cells = list(cells)
    nbformat.write(notebook, path)


def _book2(tmp_path):
    root = tmp_path
    for sub in ("units", "checkpoints", "projects"):
        (root / "book2" / sub).mkdir(parents=True)
    return root


def _unit(root, name="unit-01-x", lessons=0):
    d = root / "book2" / "units" / name
    (d / "assets").mkdir(parents=True)
    (d / "manifest.yaml").write_text(f"id: {name}\nkind: unit\nlessons: {lessons}\n")
    return d


def _solver_entry(root, *, solver="ex1", code="print(sum(int(x) for x in __import__('sys').stdin.read().split()))"):
    # NOTE: the comprehension above is only for test solvers; source-policy is tested separately.
    d = _unit(root)
    (d / "assets" / f"{solver}.py").write_text(code + "\n")
    fx = d / "assets" / solver
    fx.mkdir()
    (fx / "1.in").write_text("1 2 3\n")
    (fx / "1.out").write_text("6\n")
    (fx / "2.in").write_text("10 20\n")
    (fx / "2.out").write_text("30\n")
    # exercises.ipynb heading derives ex1; solutions.ipynb mirrors the .py under ## Exercise 1
    _nb(d / "exercises.ipynb", new_markdown_cell("## Exercise 1 — sum *(tag)*"))
    _nb(
        d / "solutions.ipynb",
        new_markdown_cell("## Exercise 1 — sum"),
        new_code_cell(code),
    )
    return d


# ---------- judge-check ----------

def test_judge_book1_is_noop(tmp_path):
    _book2(tmp_path)
    assert judge_findings(tmp_path, "book1") == []


def test_judge_pass(tmp_path):
    root = _book2(tmp_path)
    _solver_entry(root)
    assert judge_findings(root, "book2") == []


def test_judge_wrong_output(tmp_path):
    root = _book2(tmp_path)
    _solver_entry(root, code="print(0)")
    assert any("wrong output" in f for f in judge_findings(root, "book2"))


def test_judge_nonzero_exit(tmp_path):
    root = _book2(tmp_path)
    _solver_entry(root, code="import sys; sys.exit(1)")
    assert any("failed on" in f for f in judge_findings(root, "book2"))


def test_judge_timeout(tmp_path, monkeypatch):
    monkeypatch.setattr(judge_mod, "JUDGE_TIMEOUT_S", 1)
    root = _book2(tmp_path)
    _solver_entry(root, code="while True:\n    pass")
    assert any("exceeded" in f for f in judge_findings(root, "book2"))


def test_judge_missing_expected_unit_solver(tmp_path):
    root = _book2(tmp_path)
    d = _unit(root)
    _nb(d / "exercises.ipynb", new_markdown_cell("## Exercise 1\n\n## Exercise 2"))
    _nb(d / "solutions.ipynb", new_markdown_cell("## Exercise 1"))
    (d / "assets" / "ex1.py").write_text("print(1)\n")
    for k in ("1", "2"):
        (d / "assets" / "ex1").mkdir(exist_ok=True)
        (d / "assets" / "ex1" / f"{k}.in").write_text("x\n")
        (d / "assets" / "ex1" / f"{k}.out").write_text("1\n")
    # ex2 is expected (heading) but absent
    assert any("missing solver ex2.py" in f for f in judge_findings(root, "book2"))


def test_judge_missing_project_solver_decorated_heading(tmp_path):
    root = _book2(tmp_path)
    d = root / "book2" / "projects" / "project-01-x"
    (d / "assets").mkdir(parents=True)
    (d / "manifest.yaml").write_text("id: project-01-x\nkind: project\nlessons: 1\n")
    # decorated ### Problem headings — an end-unanchored regex must still derive p1, p2
    _nb(
        d / "brief.ipynb",
        new_markdown_cell("## Milestone 1\n\n### Problem 1 — Ledger *(prefix)*\n\n### Problem 2 — Grid *(sim)*"),
    )
    _nb(d / "solutions.ipynb", new_markdown_cell("## Problem 1"))
    (d / "assets" / "p1.py").write_text("print(1)\n")
    (d / "assets" / "p1").mkdir()
    for k in ("1", "2"):
        (d / "assets" / "p1" / f"{k}.in").write_text("x\n")
        (d / "assets" / "p1" / f"{k}.out").write_text("1\n")
    findings = judge_findings(root, "book2")
    assert any("missing solver p2.py" in f for f in findings)


def test_judge_one_case_fails(tmp_path):
    root = _book2(tmp_path)
    d = _solver_entry(root)
    (d / "assets" / "ex1" / "2.in").unlink()
    (d / "assets" / "ex1" / "2.out").unlink()
    assert any("needs >=2 fixture pairs" in f for f in judge_findings(root, "book2"))


def test_judge_missing_counterpart(tmp_path):
    root = _book2(tmp_path)
    d = _solver_entry(root)
    (d / "assets" / "ex1" / "2.out").unlink()
    assert any("has no matching .out" in f for f in judge_findings(root, "book2"))


def test_judge_orphan_fixture_dir(tmp_path):
    root = _book2(tmp_path)
    d = _solver_entry(root)
    orphan = d / "assets" / "ex9"
    orphan.mkdir()
    (orphan / "1.in").write_text("x\n")
    (orphan / "1.out").write_text("1\n")
    assert any("fixture dir ex9/ has no ex9.py" in f for f in judge_findings(root, "book2"))


def test_judge_second_untested_solver(tmp_path):
    root = _book2(tmp_path)
    d = _solver_entry(root)
    # a second reserved-stem solver with no fixtures must FAIL (never silently a helper)
    (d / "assets" / "ex2.py").write_text("print(1)\n")
    assert any("ex2.py needs >=2 fixture pairs" in f for f in judge_findings(root, "book2"))


def test_judge_referenced_lesson_solver_missing(tmp_path):
    # A lesson that references assets/l3.py with no l3.py present FAILs judge-check (Sol blocker fix).
    root = _book2(tmp_path)
    d = _solver_entry(root)
    _nb(d / "lesson.ipynb", new_markdown_cell("Run `python assets/l3.py < assets/l3/1.in`"))
    assert any("missing solver l3" in f for f in judge_findings(root, "book2"))


def test_judge_present_unreferenced_lesson_solver_no_false_missing(tmp_path):
    # Converse: an l3.py present but unreferenced is judged via the reserved stem, never a false miss.
    root = _book2(tmp_path)
    d = _solver_entry(root)
    (d / "assets" / "l3.py").write_text("print(1)\n")
    fx = d / "assets" / "l3"
    fx.mkdir()
    for k in ("1", "2"):
        (fx / f"{k}.in").write_text("x\n")
        (fx / f"{k}.out").write_text("1\n")
    assert not any("missing solver l3" in f for f in judge_findings(root, "book2"))


def test_judge_helper_not_fixture_required(tmp_path):
    root = _book2(tmp_path)
    d = _solver_entry(root)
    (d / "assets" / "helpers.py").write_text("VALUE = 1\n")  # non-PID stem = helper
    assert judge_findings(root, "book2") == []


def test_judge_mirror_drift(tmp_path):
    root = _book2(tmp_path)
    d = _solver_entry(root)
    # change the .py so no solutions cell mirrors it
    (d / "assets" / "ex1.py").write_text("print(sum(int(x) for x in __import__('sys').stdin.read().split()) + 0)\n")
    assert any("no mirroring display cell" in f for f in judge_findings(root, "book2"))


# ---------- source-policy ----------

def test_source_policy_book1_is_noop(tmp_path):
    _book2(tmp_path)
    assert source_policy_findings(tmp_path, "book1") == []


def test_source_policy_full_current_book2_clean():
    # The mandated full-current-Book-2 clean regression (Sol MAJOR 2).
    assert source_policy_findings(REPO, "book2") == []


@pytest.mark.parametrize(
    "snippet, ban",
    [
        ("a = 1\nb = 2\nc = 3\nprint(0 < a < b)", "chained comparison"),
        ("row = [0] * 5\nprint(row)", "list/str repetition"),
        ("x = 1\nprint(x if x else 0)", "ternary"),
        ("f = lambda a: a\nprint(f(1))", "lambda"),
        ("def f():\n    global g\n    g = 1", "global/nonlocal"),
        ("d = {1: 2}\ndel d[1]", "del"),
        ("x = 0\nx += 1", "augmented"),
        ("ys = [i for i in range(3)]\nprint(ys)", "comprehension"),
        ("import itertools\nprint(0)", "itertools"),
        ("from collections import Counter\nprint(0)", "Counter"),
        ("s = 'a b'\nprint(s.find('a'))", ".find()"),
        ("print(enumerate([1]))", "builtin enumerate"),
    ],
)
def test_source_policy_bans(tmp_path, snippet, ban):
    root = _book2(tmp_path)
    d = _unit(root)
    (d / "assets" / "ex1.py").write_text(snippet + "\n")
    findings = source_policy_findings(root, "book2")
    assert any(ban in f for f in findings), f"expected a '{ban}' finding, got {findings}"


def test_source_policy_clean_sample(tmp_path):
    root = _book2(tmp_path)
    d = _unit(root)
    clean = (
        "import sys\n"
        "def helper(n):\n"
        "    return n\n"
        "data = sys.stdin.read().split()\n"
        "total = 0\n"
        "for token in data:\n"
        "    total = total + int(token)\n"
        "nums = set()\n"
        "nums.add(total)\n"
        "print(helper(total))\n"
    )
    (d / "assets" / "ex1.py").write_text(clean)
    assert source_policy_findings(root, "book2") == []


def test_source_policy_helper_syntax_error_surfaces(tmp_path):
    root = _book2(tmp_path)
    d = _unit(root)
    (d / "assets" / "lib.py").write_text("def broken(:\n")  # non-PID helper, never judged
    assert any("does not parse" in f for f in source_policy_findings(root, "book2"))
