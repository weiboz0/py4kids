"""`py4kids-tools export | classify | site-check` (design 012; plan 101 E)."""

import importlib.util
import json
from pathlib import Path

import nbformat
import pytest

from tools.cli import main
from tools.export import answers

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "site_demo_book", Path(__file__).parent / "fixtures" / "site" / "demo_book.py")
demo_book = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(demo_book)


@pytest.fixture
def site_root(tmp_path):
    answers.clear_caches()
    return demo_book.build_site_root(tmp_path / "root")


def tree(directory: Path) -> dict[str, bytes]:
    return {path.relative_to(directory).as_posix(): path.read_bytes()
            for path in sorted(directory.rglob("*")) if path.is_file()}


@pytest.mark.parametrize("command", [["export"], ["classify"], ["site-check"]])
def test_cli_refuses_non_site_book(command, capsys):
    assert main(["--book", "recsys", *command]) == 2
    assert capsys.readouterr().err.strip() == \
        "usage: recsys is not a site book (books.yaml site: true)"
    assert main([*command, "--book", "recsys"]) == 2


def test_cli_export_both_orders(site_root, tmp_path, capsys):
    one, two = tmp_path / "one", tmp_path / "two"
    assert main(["--root", str(site_root), "export", "--book", "demo", "--out", str(one)]) == 0
    assert main(["--root", str(site_root), "--book", "demo", "export", "--out", str(two)]) == 0
    assert tree(one) == tree(two)
    out = capsys.readouterr().out
    assert "export: demo:" in out and "sha256:" in out
    assert not (site_root / "site" / "ids" / "demo.json").exists()


def test_cli_export_default_out_and_ledger(site_root):
    assert main(["--root", str(site_root), "--book", "demo", "export", "--update-ledger",
                 "--release", "v9"]) == 0
    book = json.loads((site_root / "site" / "content" / "demo" / "book.json").read_text())
    assert book["release"]["tag"] == "v9"
    ledger = json.loads((site_root / "site" / "ids" / "demo.json").read_text())
    assert ledger == sorted(ledger) and len(ledger) == len(set(ledger))
    assert "demo/unit-01-demo/exercises/u1e01" in ledger
    assert "demo/back-matter/glossary/print" in ledger
    assert "demo/unit-01-demo/lesson/l1c2#predict" in ledger


def test_cli_export_failure_exit_1(site_root, capsys):
    path = site_root / "demo" / "units" / "unit-02-more" / "lesson.ipynb"
    data = json.loads(path.read_text())
    del data["cells"][0]["id"]
    data["nbformat_minor"] = 4
    path.write_text(json.dumps(data))
    assert main(["--root", str(site_root), "--book", "demo", "export"]) == 1
    assert "cell 0 has no id" in capsys.readouterr().out


def test_cli_classify(site_root, capsys):
    assert main(["--root", str(site_root), "--book", "demo", "classify", "--unit", "unit-01-demo"]) == 0
    rows = [line.split("\t") for line in capsys.readouterr().out.strip().splitlines()]
    assert all(len(row) == 4 for row in rows)
    assert all(row[0].startswith("demo/unit-01-demo/exercises/") for row in rows)
    assert rows[0][:3] == ["demo/unit-01-demo/exercises/u1e01", "fixtures", ""]
    assert main(["--root", str(site_root), "--book", "demo", "classify", "--apply",
                 "--unit", "unit-01-demo"]) == 0
    capsys.readouterr()
    answers.clear_caches()
    assert main(["--root", str(site_root), "classify", "--book", "demo", "--unit", "unit-01-demo"]) == 0
    rows = [line.split("\t") for line in capsys.readouterr().out.strip().splitlines()]
    assert all(row[1] == row[2] for row in rows)
    exercises = nbformat.read(site_root / "demo/units/unit-01-demo/exercises.ipynb", as_version=4)
    assert "check-fixtures" in exercises.cells[1].metadata["tags"]


def test_cli_site_check(site_root, capsys):
    assert main(["--root", str(site_root), "--book", "demo", "site-check"]) == 0
    out = capsys.readouterr().out
    assert "INFO: demo: classification proposed" in out
    assert "site-check: PASS" in out


def test_cli_site_check_fails_on_probe_error(tmp_path, capsys):
    answers.clear_caches()
    boom = demo_book.code("boom", "print(1 / 0)")
    root = demo_book.build_site_root(tmp_path / "root", extra_lesson_cells=[boom])
    assert main(["--root", str(root), "site-check", "--book", "demo"]) == 1
    assert "FAIL: demo/unit-01-demo/lesson/boom: lesson probe error" in capsys.readouterr().out


def test_cli_site_check_fails_an_also_check_entry_not_in_the_statement(site_root, capsys):
    """plan 102 Phase 0: an `also_check` entry copied from a solution is a site-check FAIL."""
    path = site_root / "demo" / "units" / "unit-01-demo" / "exercises.ipynb"
    notebook = nbformat.read(path, as_version=4)
    heading = next(cell for cell in notebook.cells if cell.get("id") == "u1e07")
    heading.metadata["also_check"] = ["return n * 2"]
    nbformat.write(notebook, path)
    assert main(["--root", str(site_root), "--book", "demo", "site-check"]) == 1
    assert ("FAIL: demo/unit-01-demo/exercises/u1e07: metadata.also_check entry is not in the "
            "statement: 'return n * 2'") in capsys.readouterr().out
