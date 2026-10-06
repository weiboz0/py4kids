"""The standalone-cell probe (design 012 D3; plan 101 C, Review Focus 1, 2 and 4)."""

import random
import subprocess
import time
from pathlib import Path

import nbformat
import pytest
from nbformat.v4 import new_code_cell, new_output

from tools.export.probe import ProbeResult, analyse, closure, probe_cells

FIXTURE = Path(__file__).parent / "fixtures" / "site" / "units" / "unit-01-demo"
TIMEOUT = 2


def code(cell_id: str, source: str, out: str | None = None, tags=None):
    cell = new_code_cell(source, id=cell_id)
    if out is not None:
        cell.outputs = [new_output("stream", name="stdout", text=out)]
    if tags:
        cell.metadata["tags"] = tags
    return cell


def git_repo(path: Path, tracked: dict[str, str], untracked: dict[str, str] | None = None) -> Path:
    """An entry dir inside a fresh `git init` repo; only `tracked` files are `git add`ed."""
    entry = path / "unit-01-x"
    entry.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    for name, text in {**tracked, **(untracked or {})}.items():
        (entry / name).parent.mkdir(parents=True, exist_ok=True)
        (entry / name).write_text(text, encoding="utf-8")
    if tracked:
        subprocess.run(["git", "-C", str(path), "add", *[f"unit-01-x/{n}" for n in tracked]],
                       check=True)
    return entry


@pytest.fixture(scope="module")
def fixture_probe():
    cells = nbformat.read(FIXTURE / "lesson.ipynb", as_version=4).cells
    before = sorted(p.relative_to(FIXTURE) for p in FIXTURE.rglob("*"))
    start = time.monotonic()
    results = probe_cells(FIXTURE, cells, timeout_s=TIMEOUT)
    elapsed = time.monotonic() - start
    after = sorted(p.relative_to(FIXTURE) for p in FIXTURE.rglob("*"))
    return results, elapsed, before, after


def test_probe_standalone_and_prelude(fixture_probe):
    results, *_ = fixture_probe
    assert results["c3"] == ProbeResult("standalone", [], [])
    assert results["c2"].status == "prelude"
    assert results["c2"].prelude == ["c1"]
    assert results["c1"].status == "standalone"  # output-free: runs clean, prints nothing
    assert results["c4"].status == "standalone"
    assert results["c9"].status == "standalone"
    assert "c7" not in results and "c8" not in results  # no-exec cells are not probed


def test_probe_tree_unchanged(fixture_probe):
    """Review Focus 1: c4 writes scratch.txt, but only in a temporary copy."""
    _results, _elapsed, before, after = fixture_probe
    assert not (FIXTURE / "scratch.txt").exists()
    assert before == after


def test_probe_hang_and_input(fixture_probe):
    """Review Focus 2: a hang times out, `input()` reads /dev/null and errors, and both finish."""
    results, elapsed, *_ = fixture_probe
    assert results["c5"].status == "timeout"
    assert results["c6"].status == "error"
    assert "EOFError" in results["c6"].detail
    assert elapsed < 2 * TIMEOUT


def test_probe_setup_cells(tmp_path):
    entry = git_repo(tmp_path, {"lesson.ipynb": "{}"})
    roll = random.Random(1).randint(1, 6)
    cells = [
        code("a", "import random"),
        code("b", "import random\nrandom.seed(1)"),
        code("c", "print(random.randint(1, 6))", f"{roll}\n"),
        code("d", "random.seed(1)"),
    ]
    results = probe_cells(entry, cells, timeout_s=10)
    assert results["a"] == ProbeResult("standalone", [], [])
    assert results["b"] == ProbeResult("standalone", [], [])
    assert results["c"].status == "prelude"
    assert results["c"].prelude == ["a", "b"]
    assert results["d"].status == "prelude"  # a bare seed call needs its import
    # `random.randint(…)` in c is a method call on `random` too (it advances the generator).
    assert results["d"].prelude == ["a", "b", "c"]


def test_closure_follows_mutating_calls():
    earlier = [(0, analyse("items = []")), (1, analyse("items.append(4)")),
               (2, analyse("other = 1")), (3, analyse("table = {}\ntable['k'] = 2"))]
    assert closure(analyse("print(items)"), earlier) == [0, 1]
    assert closure(analyse("print(table)"), earlier) == [3]


def test_probe_file_written_by_earlier_cell(tmp_path):
    entry = git_repo(tmp_path, {"lesson.ipynb": "{}"}, untracked={"x.txt": "stale\n"})
    cells = [
        code("A", "with open('x.txt', 'w') as f:\n    f.write('hello\\n')"),
        code("B", "with open('x.txt') as f:\n    print(f.read(), end='')", "hello\n"),
        code("C", "with open('y.txt', 'w') as f:\n    f.write('own\\n')\n"
                  "with open('y.txt') as f:\n    print(f.read(), end='')", "own\n"),
    ]
    results = probe_cells(entry, cells, timeout_s=10)
    assert results["A"].status == "standalone"
    assert results["B"] == ProbeResult("prelude", ["A"], [])  # the stale x.txt is not copied
    assert results["C"] == ProbeResult("standalone", [], [])
    assert (entry / "x.txt").read_text(encoding="utf-8") == "stale\n"
    assert not (entry / "y.txt").exists()


def test_files_tracked_only(tmp_path):
    entry = git_repo(
        tmp_path,
        {"lesson.ipynb": "{}", "data.txt": "1 2 3\n", "assets/table.txt": "t\n",
         "assets/ex1.py": "print(1)\n", "assets/verify/check.txt": "v\n"},
        untracked={"scratch.txt": "junk\n"},
    )
    cells = [code("a", "names = ['data.txt', 'scratch.txt', 'table.txt', 'assets/ex1.py', "
                       "'ex1.py', 'assets/verify/check.txt']\nprint(len(names))", "6\n"),
             code("b", "print(open('data.txt').read().split())", "['1', '2', '3']\n")]
    results = probe_cells(entry, cells, timeout_s=10)
    assert results["a"] == ProbeResult("standalone", [], ["assets/table.txt", "data.txt"])
    assert results["b"] == ProbeResult("standalone", [], ["data.txt"])


def test_probe_is_deterministic(fixture_probe):
    """Review Focus 4: a second probe gives the same results."""
    results, *_ = fixture_probe
    cells = nbformat.read(FIXTURE / "lesson.ipynb", as_version=4).cells
    again = probe_cells(FIXTURE, [c for c in cells if c.id != "c5"], timeout_s=TIMEOUT)
    assert again == {k: v for k, v in results.items() if k != "c5"}
