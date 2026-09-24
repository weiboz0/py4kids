import ast
from pathlib import Path

import nbformat
import pytest
import yaml

from tools.concept_scan import concept_scan_findings, detect, scanner_profile

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


@pytest.mark.parametrize(
    ("source", "concept"),
    [
        ("value.split()", "string-methods"),
        ("value.join(parts)", "string-methods"),
        ("value.isdigit()", "string-methods"),
        ("value.isalpha()", "string-methods"),
        ("value.find(needle)", "string-methods"),
        ("value.startswith(prefix)", "string-methods"),
        ("value.endswith(suffix)", "string-methods"),
        ("values.pop()", "list-append"),
        ("values.insert(0, item)", "list-append"),
        ("values.remove(item)", "list-append"),
        ("values.index(item)", "list-index"),
        ("for item in values:\n    continue", "break-statement"),
    ],
)
def test_book1_profile_detects_every_widened_method(source, concept):
    concepts = [
        {"id": concept_id}
        for concept_id in (
            "break-statement",
            "list-append",
            "list-index",
            "string-methods",
        )
    ]
    profile = scanner_profile(concepts)

    used, untaught = detect(
        ast.parse(source),
        registered_concepts={row["id"] for row in concepts},
        profile=profile,
    )

    assert concept in used
    assert untaught == set()


def test_book1_profile_split_ignores_book2_registered_concept():
    profile = scanner_profile([{"id": "string-methods"}])

    used, untaught = detect(
        ast.parse("value.split()"),
        registered_concepts={"string-methods", "str-split"},
        profile=profile,
    )

    assert "string-methods" in used
    assert "str-split" not in used
    assert untaught == set()


def test_book1_declared_book2_split_uses_str_split():
    profile = scanner_profile([{"id": "string-methods"}, {"id": "str-split"}])

    used, untaught = detect(
        ast.parse("value.split()"),
        registered_concepts={"string-methods", "str-split"},
        profile=profile,
    )

    assert "str-split" in used
    assert "string-methods" not in used
    assert untaught == set()


def test_book2_profile_keeps_split_as_str_split():
    profile = scanner_profile([{"id": "str-split"}])

    used, untaught = detect(
        ast.parse("value.split()"),
        registered_concepts={"str-split"},
        profile=profile,
    )

    assert used == {"str-split"}
    assert untaught == set()


@pytest.mark.parametrize(
    "method",
    ["insert", "isalpha", "startswith", "pop", "index", "join"],
)
def test_book2_profile_keeps_widened_methods_untaught(method):
    profile = scanner_profile([{"id": "str-split"}])

    used, untaught = detect(
        ast.parse(f"value.{method}()"),
        registered_concepts={"str-split"},
        profile=profile,
    )

    assert used == set()
    assert untaught == {method}


def test_known_set_remove_maps_only_to_set_ops():
    profile = scanner_profile([{"id": "set-ops"}])

    used, untaught = detect(
        ast.parse("values = set()\nvalues.remove(item)"),
        registered_concepts={"list-append", "set-ops"},
        profile=profile,
    )

    assert used == {"set-ops"}
    assert "list-append" not in used
    assert untaught == set()


@pytest.mark.parametrize("method", ["count", "title", "extend"])
def test_book1_profile_keeps_unwidened_methods_out_of_new_concepts(method):
    profile = scanner_profile([{"id": "string-methods"}])

    used, untaught = detect(
        ast.parse(f"value.{method}()"),
        registered_concepts={"list-append", "list-index", "string-methods"},
        profile=profile,
    )

    assert used.isdisjoint({"list-append", "list-index", "string-methods"})
    if method == "title":
        # `title` remains globally known as a turtle method; widening must not
        # misattribute it to the string-methods concept.
        assert untaught == set()
    else:
        assert untaught == {method}


def _write_strict_checkpoint(root: Path, source: str) -> None:
    curriculum = root / "book1/curriculum"
    checkpoint = root / "book1/checkpoints/checkpoint-01-fixture"
    curriculum.mkdir(parents=True)
    checkpoint.mkdir(parents=True)
    concept_ids = [
        "break-statement",
        "list-append",
        "list-index",
        "string-methods",
        "while-loop",
    ]
    (curriculum / "concepts.yaml").write_text(
        yaml.safe_dump(
            {
                "concepts_version": 1,
                "concepts": [
                    {"id": concept_id, "name": concept_id, "category": "control"}
                    for concept_id in concept_ids
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (curriculum / "coverage-map.yaml").write_text(
        yaml.safe_dump(
            {
                "map_version": 1,
                "entries": [
                    {
                        "id": "checkpoint-01-fixture",
                        "kind": "checkpoint",
                        "title": "Strict checkpoint fixture",
                        "lessons": 1,
                        "introduces": [],
                        "requires": ["while-loop"],
                        "practices": [],
                    }
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    nbformat.write(
        nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(source)]),
        checkpoint / "checkpoint.ipynb",
    )


@pytest.mark.parametrize(
    ("source", "missing"),
    [
        ("position = values.index(3)", "list-index"),
        ("while ready:\n    continue", "break-statement"),
        ("words = value.split()", "string-methods"),
        ("last = values.pop()", "list-append"),
    ],
)
def test_strict_checkpoint_reports_each_widened_concept(tmp_path, source, missing):
    _write_strict_checkpoint(tmp_path, source)

    assert concept_scan_findings(tmp_path, "book1") == [
        f"FAIL: checkpoint-01-fixture: used-but-unlisted concept {missing}"
    ]
