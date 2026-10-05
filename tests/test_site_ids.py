"""Global keys, uniqueness and the id ledger (design 012 D3; plan 101 B)."""

import json

import nbformat
import pytest

from tools.export.ids import (
    card_key,
    concept_card_key,
    continuity_findings,
    duplicate_key_findings,
    item_key,
    load_ledger,
    missing_id_findings,
    write_ledger,
)


def test_item_key_format():
    assert item_key("acsl", "unit-12-graph-theory", "lesson", "a1b2") == (
        "acsl/unit-12-graph-theory/lesson/a1b2"
    )
    assert item_key("acsl", "unit-12-graph-theory", "lesson", "a1b2", 2) == (
        "acsl/unit-12-graph-theory/lesson/a1b2#2"
    )
    assert item_key("b", "project-01-x", "brief", "c9", None) == "b/project-01-x/brief/c9"


@pytest.mark.parametrize(
    "parts",
    [
        ("", "unit-01", "lesson", "c1"),
        ("b", "unit-01", "lesson", ""),
        ("b", "unit/01", "lesson", "c1"),
        ("b", "unit-01", "lesson", "c#1"),
    ],
)
def test_item_key_rejects_bad_parts(parts):
    with pytest.raises(ValueError):
        item_key(*parts)


def test_item_key_rejects_bad_part_number():
    with pytest.raises(ValueError):
        item_key("b", "unit-01", "lesson", "c1", 0)


def test_card_keys():
    block = item_key("b", "unit-01-x", "lesson", "c3")
    assert card_key(block) == "b/unit-01-x/lesson/c3#predict"
    assert card_key(block) != block
    assert concept_card_key("acsl", "bfs") == "acsl/back-matter/glossary/bfs"


def test_duplicates_reported_once_each():
    keys = ["b/u/lesson/c1", "b/u/lesson/c2", "b/u/lesson/c1", "b/u/lesson/c1",
            "b/u/exercises/e1", "b/u/exercises/e1"]
    assert duplicate_key_findings(keys) == [
        "FAIL: duplicate id: b/u/exercises/e1 (2 times)",
        "FAIL: duplicate id: b/u/lesson/c1 (3 times)",
    ]
    assert duplicate_key_findings(iter(["a/b/c/d", "a/b/c/d#2"])) == []


def _notebook(tmp_path, cells):
    nb = nbformat.v4.new_notebook()
    nb.cells = cells
    path = tmp_path / "lesson.ipynb"
    nbformat.write(nb, path)
    return path


def test_missing_id_findings(tmp_path):
    path = _notebook(tmp_path, [nbformat.v4.new_markdown_cell("# T"),
                                nbformat.v4.new_code_cell("x = 1")])
    assert missing_id_findings(path) == []
    raw = json.loads(path.read_text(encoding="utf-8"))
    del raw["cells"][1]["id"]
    raw["cells"][0]["id"] = ""
    path.write_text(json.dumps(raw), encoding="utf-8")
    assert missing_id_findings(path) == [
        f"FAIL: {path}: cell 0 has no id",
        f"FAIL: {path}: cell 1 has no id",
    ]


def test_ledger_roundtrip(tmp_path):
    assert load_ledger(tmp_path, "b") == set()
    write_ledger(tmp_path, "b", ["b/u/lesson/c2", "b/u/lesson/c1", "b/u/lesson/c1"])
    path = tmp_path / "site" / "ids" / "b.json"
    assert path.read_text(encoding="utf-8") == '[\n "b/u/lesson/c1",\n "b/u/lesson/c2"\n]\n'
    assert load_ledger(tmp_path, "b") == {"b/u/lesson/c1", "b/u/lesson/c2"}


def test_continuity(tmp_path):
    write_ledger(tmp_path, "b", ["b/u/lesson/kept", "b/u/lesson/gone", "b/u/lesson/old"])
    (tmp_path / "site" / "ids" / "b-retired.yaml").write_text(
        'b/u/lesson/old: "retired"\n', encoding="utf-8"
    )
    keys = ["b/u/lesson/kept", "b/u/lesson/new"]  # a new key passes
    assert continuity_findings(tmp_path, "b", keys) == [
        (
            "FAIL: b: id vanished since the ledger: b/u/lesson/gone "
            '(map it in site/ids/b-retired.yaml as `b/u/lesson/gone: <new key or "retired">`)'
        )
    ]
    (tmp_path / "site" / "ids" / "b-retired.yaml").write_text(
        'b/u/lesson/old: retired\nb/u/lesson/gone: b/u/lesson/new\n', encoding="utf-8"
    )
    assert continuity_findings(tmp_path, "b", keys) == []


def test_continuity_without_ledger_passes(tmp_path):
    assert continuity_findings(tmp_path, "b", ["b/u/lesson/c1"]) == []


def test_continuity_mapping_target_must_exist(tmp_path):
    write_ledger(tmp_path, "b", ["b/u/lesson/gone"])
    (tmp_path / "site" / "ids" / "b-retired.yaml").write_text(
        "b/u/lesson/gone: b/u/lesson/typo\n", encoding="utf-8"
    )
    assert continuity_findings(tmp_path, "b", ["b/u/lesson/new"]) == [
        (
            "FAIL: b: site/ids/b-retired.yaml maps b/u/lesson/gone to b/u/lesson/typo, "
            "which is not in the bundle"
        )
    ]


def test_continuity_bad_retired_file(tmp_path):
    write_ledger(tmp_path, "b", ["b/u/lesson/gone"])
    (tmp_path / "site" / "ids" / "b-retired.yaml").write_text("- a\n- b\n", encoding="utf-8")
    assert continuity_findings(tmp_path, "b", []) == [
        "FAIL: b: site/ids/b-retired.yaml must be a mapping of old key to new key or \"retired\""
    ]
