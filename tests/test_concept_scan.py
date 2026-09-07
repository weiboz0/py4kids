import ast
from pathlib import Path

import nbformat
import yaml

from tools.concept_scan import concept_scan_findings, detect

REPO = Path(__file__).resolve().parents[1]


def test_class_body_method_is_not_def_function():
    used, _ = detect(ast.parse("class Pet:\n    def feed(self):\n        pass\n"))

    assert "methods" in used
    assert "def-function" not in used


def test_module_level_function_is_def_function():
    used, _ = detect(ast.parse("def greet():\n    pass\n"))

    assert "def-function" in used


def test_function_nested_in_method_is_def_function():
    source = "class Pet:\n    def feed(self):\n        def helper():\n            pass\n"
    used, _ = detect(ast.parse(source))

    assert "def-function" in used


def test_f_string_literal_text_is_string_literal():
    used, _ = detect(ast.parse('message = f"Hello, {name}!"'))

    assert "f-string" in used
    assert "string-literal" in used


def test_real_book_has_no_used_but_unlisted_concepts():
    assert concept_scan_findings(REPO, "book1") == []


def test_unlisted_concept_produces_one_finding(tmp_path):
    curriculum = tmp_path / "book1/curriculum"
    entry_dir = tmp_path / "book1/units/unit-01-fixture"
    curriculum.mkdir(parents=True)
    entry_dir.mkdir(parents=True)
    coverage_map = {
        "map_version": 1,
        "entries": [
            {
                "id": "unit-01-fixture",
                "kind": "unit",
                "title": "Fixture",
                "lessons": 1,
                "introduces": [],
                "requires": [],
                "practices": [],
            }
        ],
    }
    (curriculum / "coverage-map.yaml").write_text(
        yaml.safe_dump(coverage_map, sort_keys=False), encoding="utf-8"
    )
    nbformat.write(
        nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("total = 1 + 2")]),
        entry_dir / "lesson.ipynb",
    )

    assert concept_scan_findings(tmp_path, "book1") == [
        "FAIL: unit-01-fixture: used-but-unlisted concept arithmetic"
    ]
