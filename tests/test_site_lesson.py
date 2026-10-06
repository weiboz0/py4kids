"""Lesson blocks and concept attribution (design 012 D3, D6, D8; plan 101 C)."""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import nbformat
import pytest
from jsonschema import Draft202012Validator

from tools.books import book_path, books_with_flag
from tools.export import lesson as lesson_module
from tools.export.cards import predict_cards
from tools.export.concepts import book_registry, cell_concepts, concept_override
from tools.export.ids import item_key
from tools.export.lesson import lesson_dirs, lesson_export, markdown_parts
from tools.publish import markdown_blocks
from tools.turtle_figure import turtle_segments

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = Path(__file__).parent / "fixtures" / "site" / "units" / "unit-01-demo"
SCHEMA = json.loads((ROOT / "tools/export/schema/bundle.schema.json").read_text(encoding="utf-8"))
BOOK = "python-projects"  # the fixture's concept registry
KEY = f"{BOOK}/unit-01-demo/lesson"


def block_validator() -> Draft202012Validator:
    return Draft202012Validator(SCHEMA).evolve(schema=SCHEMA["$defs"]["block"])


@pytest.fixture(scope="module")
def registry():
    return book_registry(ROOT, BOOK)


@pytest.fixture(scope="module")
def fixture_lesson(registry):
    return lesson_export(ROOT, BOOK, FIXTURE, timeout_s=2, registry=registry)


def by_key(lesson):
    return {block["key"]: block for block in lesson.blocks}


def test_blocks_types_and_keys(fixture_lesson):
    blocks = by_key(fixture_lesson)
    assert fixture_lesson.title == "Unit 1 — Demo"
    assert blocks[f"{KEY}/m0"]["type"] == "opener"
    assert blocks[f"{KEY}/m1"]["type"] == "goals"
    assert blocks[f"{KEY}/m1"]["md"] == "- Print a value.\n- Store a value in a variable."
    assert (blocks[f"{KEY}/m2"]["type"], blocks[f"{KEY}/m2#2"]["type"]) == ("prose", "prose")
    assert blocks[f"{KEY}/m2"]["md"] == "### First heading\n\nSome words."
    assert blocks[f"{KEY}/m2#2"]["md"] == "### Second heading\n\nMore words."
    assert f"{KEY}/m2#3" not in blocks
    assert blocks[f"{KEY}/m3"]["type"] == "notice"
    assert blocks[f"{KEY}/m3"]["md"] == "The file `scratch.txt` holds one letter.\n\nThat is all it holds."
    assert blocks[f"{KEY}/c7"]["type"] == "error-demo"
    assert blocks[f"{KEY}/c8"]["type"] == "turtle-figure"
    assert len(blocks[f"{KEY}/c8"]["figure"]) == 4
    assert blocks[f"{KEY}/c3"]["type"] == "code"
    assert blocks[f"{KEY}/c3"]["output"] == "hi\n"
    assert "output" not in blocks[f"{KEY}/c1"]
    assert blocks[f"{KEY}/c2"]["probe"] == "prelude"
    assert blocks[f"{KEY}/c2"]["prelude"] == [f"{KEY}/c1"]
    assert blocks[f"{KEY}/c2"]["needs_prelude"] is True
    assert blocks[f"{KEY}/c3"]["needs_prelude"] is False
    # error and timeout never reach the bundle: the block says null, Lesson.probes keeps the status
    assert blocks[f"{KEY}/c5"]["probe"] is None and blocks[f"{KEY}/c6"]["probe"] is None
    assert fixture_lesson.probes[f"{KEY}/c5"].status == "timeout"
    assert fixture_lesson.probes[f"{KEY}/c6"].status == "error"
    assert blocks[f"{KEY}/c7"]["probe"] is None
    program = blocks[f"{KEY}/m4#asset:demo.py"]
    assert program["type"] == "program"
    assert program["files"] == ["files/unit-01-demo/assets/demo.py"]
    order = [block["key"] for block in fixture_lesson.blocks]
    assert order.index(f"{KEY}/m4") < order.index(f"{KEY}/m4#asset:demo.py")
    assert order == sorted(order, key=order.index)  # cell order
    assert len(order) == len(set(order))


def test_fixture_blocks_validate(fixture_lesson):
    validator = block_validator()
    for block in fixture_lesson.blocks:
        assert not list(validator.iter_errors(block)), block["key"]


def test_turtle_segments_square():
    segments = turtle_segments("import turtle\nfor _ in range(4):\n    turtle.forward(50)\n"
                               "    turtle.left(90)\n")
    assert [(s["x1"], s["y1"], s["x2"], s["y2"]) for s in segments] == [
        (0.0, 0.0, 50.0, 0.0), (50.0, 0.0, 50.0, 50.0), (50.0, 50.0, 0.0, 50.0),
        (0.0, 50.0, 0.0, 0.0)]
    assert {(s["color"], s["width"]) for s in segments} == {("black", 1.0)}


@pytest.mark.parametrize("book, entry", [
    ("python-concepts", "unit-01-output-and-variables"),
    ("acsl", "unit-12-graph-theory"),
])
def test_lesson_opener_real(book, entry):
    entry_dir = book_path(ROOT, book) / "units" / entry
    cell0 = nbformat.read(entry_dir / "lesson.ipynb", as_version=4).cells[0]
    lesson = lesson_export(ROOT, book, entry_dir, probe=False)
    h1 = cell0.source.splitlines()[0]
    assert lesson.title == h1.removeprefix("# ")  # as render_chapter derives it
    assert not any(h1 in block.get("md", "") for block in lesson.blocks)
    hook = re.sub(r"^# [^\n]*\n*", "", cell0.source).strip()  # render_chapter's opener body
    openers = [block for block in lesson.blocks if block["type"] == "opener"]
    assert len(openers) == 1
    assert openers[0]["key"] == item_key(book, entry, "lesson", cell0.id)
    assert openers[0]["md"] == hook
    assert lesson.blocks[0] is openers[0]
    first_heading = re.search(r"(?m)^#{2,6} ", hook)
    if first_heading is None:  # a heading-free hook: also markdown_blocks(first=True)'s panel
        rendered = markdown_blocks(cell0.source, first=True)
        panel = re.search(r"::: \{\.opener\}\n(.*?)\n:::\n", rendered, re.DOTALL)
        assert panel and panel[1] == hook
    else:
        assert entry == "unit-12-graph-theory"  # a hook that opens with a heading


def test_unknown_route_fails(monkeypatch, registry):
    monkeypatch.setattr(lesson_module, "route_code", lambda cell, stdin_note=True: ("weird", ""))
    with pytest.raises(ValueError, match="weird"):
        lesson_export(ROOT, BOOK, FIXTURE, probe=False, registry=registry)


def test_concept_override_unregistered_fails(tmp_path, registry):
    entry = tmp_path / "units" / "unit-01-demo"
    shutil.copytree(FIXTURE, entry)
    nb = nbformat.read(entry / "lesson.ipynb", as_version=4)
    by_id = {cell.id: cell for cell in nb.cells}
    by_id["c3"].metadata["concepts"] = ["not-a-concept", "print"]
    by_id["m2"].metadata["concepts"] = ["variable"]
    nbformat.write(nb, entry / "lesson.ipynb")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    lesson = lesson_export(ROOT, BOOK, entry, probe=False, registry=registry)
    assert lesson.findings == [f"FAIL: {KEY}/c3: unregistered concept not-a-concept"]
    blocks = by_key(lesson)
    assert blocks[f"{KEY}/c3"]["concepts"] == ["print"]  # the override, registered ids only
    assert blocks[f"{KEY}/m2"]["concepts"] == blocks[f"{KEY}/m2#2"]["concepts"] == ["variable"]
    # An item heading cell (Phase D reads it through the same helper):
    heading_key = item_key(BOOK, "unit-01-demo", "exercises", "e1")
    ids, findings = concept_override(heading_key, {"concepts": ["not-a-concept"]}, registry.ids)
    assert (ids, findings) == ([], [f"FAIL: {heading_key}: unregistered concept not-a-concept"])
    assert concept_override(heading_key, {}, registry.ids) == (None, [])
    assert concept_override(heading_key, {"concepts": "print"}, registry.ids)[1] == [
        f"FAIL: {heading_key}: metadata.concepts must be a list of concept ids"]


def test_cell_concepts(registry):
    names = {concept["id"]: concept["name"].lower() for concept in registry.concepts}

    def ids(fragment: str) -> set[str]:
        return {cid for cid, name in names.items() if fragment in name}

    found = set(cell_concepts(registry.profile, registry.ids, "for i in range(3):\n    print(i)\n"))
    assert ids("for loops") and ids("for loops") <= found
    assert ids("range") and ids("range") <= found
    assert ids("printing") and ids("printing") <= found
    assert found <= registry.ids
    assert cell_concepts(registry.profile, registry.ids, "print(1 +") == []


def test_markdown_parts_notice_grouping():
    parts = markdown_parts("Intro words.\n\nNotice: one.\n\nmore notice.\n\n### Next\n\nBody.")
    assert parts == [("prose", "Intro words."), ("notice", "One.\n\nmore notice."),
                     ("prose", "### Next\n\nBody.")]
    assert markdown_parts("### Recap\n\n- a\n- b") == [("recap", "- a\n- b")]


def test_lesson_dirs_real():
    for book in books_with_flag(ROOT, "site"):
        dirs = lesson_dirs(ROOT, book)
        assert dirs and all((d / "lesson.ipynb").is_file() for d in dirs)


def git_status() -> str:
    return subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--ignored"],
                          capture_output=True, text=True, check=True).stdout


def test_real_lessons_probed_validate():
    """Every real lesson, probed: every block and predict card validates against `$defs.block` /
    `$defs.card`, no probe errors or times out, and the repo tree gains no file (Review Focus 1)."""
    before = git_status()
    blocks_v = block_validator()
    cards_v = Draft202012Validator(SCHEMA).evolve(schema=SCHEMA["$defs"]["card"])
    broken = []
    for book in books_with_flag(ROOT, "site"):
        registry = book_registry(ROOT, book)
        for entry_dir in lesson_dirs(ROOT, book):
            lesson = lesson_export(ROOT, book, entry_dir, registry=registry)
            assert lesson.findings == []
            broken += [(key, r.status, r.detail) for key, r in lesson.probes.items()
                       if r.status in ("error", "timeout")]
            for block in lesson.blocks:
                errors = [e.message for e in blocks_v.iter_errors(block)]
                assert not errors, (block["key"], errors)
            for card in predict_cards(lesson.blocks):
                assert not list(cards_v.iter_errors(card)), card["key"]
    assert broken == []
    assert git_status() == before


DUMP = """
import json, sys
from pathlib import Path
from tools.export.lesson import lesson_export
lesson = lesson_export(Path('.'), sys.argv[1], Path(sys.argv[2]))
print(json.dumps([lesson.title, lesson.blocks], sort_keys=True))
"""


def test_lesson_deterministic_across_hashseed():
    """Review Focus 4: the same blocks under two PYTHONHASHSEEDs (a file-writing lesson)."""
    runs = []
    for seed in ("1", "2"):
        env = {**os.environ, "PYTHONHASHSEED": seed}
        runs.append(subprocess.run(
            [sys.executable, "-c", DUMP, "python-concepts", "python-concepts/units/unit-12-files"],
            cwd=ROOT, env=env, capture_output=True, text=True, check=True).stdout)
    assert runs[0] == runs[1]
    assert '"probe": "prelude"' in runs[0]
