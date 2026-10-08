"""Items of the site export: units, challenges, checkpoints, problems and milestones (plan 101 D)."""

import importlib.util
import json
from pathlib import Path

import nbformat
import pytest
from jsonschema import Draft202012Validator

from tools.books import book_path, books_with_flag
from tools.export import answers
from tools.export.items import (
    EntryContent,
    Item,
    _Context,
    _side_block,
    _statement_md,
    entry_content,
    entry_items,
    export_item,
    item_concept_findings,
)
from tools.publish import entries

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "tools/export/schema/bundle.schema.json").read_text(encoding="utf-8"))
_spec = importlib.util.spec_from_file_location(
    "site_demo_book", Path(__file__).parent / "fixtures" / "site" / "demo_book.py")
demo_book = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(demo_book)


def validator(definition: str) -> Draft202012Validator:
    return Draft202012Validator(SCHEMA).evolve(schema=SCHEMA["$defs"][definition])


@pytest.fixture
def demo(tmp_path):
    answers.clear_caches()
    return demo_book.build_demo_root(tmp_path / "root")


def content(root, entry):
    kind = "unit" if entry.startswith("unit-") else (
        "checkpoint" if entry.startswith("checkpoint-") else "project")
    folder = {"unit": "units", "checkpoint": "checkpoints", "project": "projects"}[kind]
    return entry_content(root, "demo", root / "demo" / folder / entry, kind)


def kind_of(entry_id: str) -> str:
    return "unit" if entry_id.startswith("unit-") else (
        "checkpoint" if entry_id.startswith("checkpoint-") else "project")


def test_items_keys_and_kinds(demo):
    unit = content(demo, "unit-01-demo")
    assert isinstance(unit, EntryContent)
    assert [(i.key, i.kind, i.number, i.label) for i in unit.items] == [
        ("demo/unit-01-demo/exercises/u1e01", "unit", 1, "Exercise 1"),
        ("demo/unit-01-demo/exercises/u1e03", "unit", 2, "Exercise 2"),
        ("demo/unit-01-demo/exercises/u1e05", "unit", 3, "Exercise 3"),
        ("demo/unit-01-demo/exercises/u1e07", "unit", 4, "Exercise 4"),
        ("demo/unit-01-demo/exercises/u1e09", "unit", 5, "Exercise 5"),
        ("demo/unit-01-demo/exercises/u1e11", "unit", 6, "Exercise 6"),
        ("demo/unit-01-demo/exercises/u1e14", "challenge", 1, "Challenge 1"),
    ]
    assert [i.title for i in unit.items] == [
        "Doubler", "Stripes", "Loop Trace", "Double It", "Count Up", "Greeter", "Triple It"]
    challenge = unit.items[-1]
    assert challenge.stretch and challenge.mode == "challenge"
    # The challenge section's lead-in cell is the first challenge's `before`, not intro.
    assert [b["key"] for b in challenge.before] == ["demo/unit-01-demo/exercises/u1e13"]
    assert [b["key"] for b in unit.intro] == ["demo/unit-01-demo/exercises/u1e00"]
    assert unit.intro[0]["md"].strip() == "Work through every exercise."  # the H1 goes
    assert unit.outro == []
    assert entry_items(demo, "demo", demo / "demo/units/unit-01-demo", "unit")[0].key == unit.items[0].key

    checkpoint = content(demo, "checkpoint-01-demo")
    assert [(i.key, i.kind, i.label) for i in checkpoint.items] == [
        ("demo/checkpoint-01-demo/checkpoint/c1c01", "checkpoint", "Question 1"),
        ("demo/checkpoint-01-demo/checkpoint/c1c02", "checkpoint", "Question 2")]

    problems = content(demo, "project-01-demo")
    assert [(i.key, i.kind, i.label, i.title) for i in problems.items] == [
        ("demo/project-01-demo/brief/p1b02", "project", "Problem 1", "Adder"),
        ("demo/project-01-demo/brief/p1b05", "project", "Problem 2", "Shouter")]
    assert [b["key"] for b in problems.items[0].before] == ["demo/project-01-demo/brief/p1b01"]
    assert [b["key"] for b in problems.items[1].before] == ["demo/project-01-demo/brief/p1b04"]
    assert [b["key"] for b in problems.outro] == ["demo/project-01-demo/brief/p1b07",
                                                  "demo/project-01-demo/brief/p1b08"]
    assert "Make it yours" in problems.outro[0]["md"]
    assert all("Make it yours" not in i.statement_md for i in problems.items)

    # The milestone fallback: a project without Problem headings.
    milestones = content(demo, "project-02-demo")
    assert [(i.key, i.label, i.title, i.mode) for i in milestones.items] == [
        ("demo/project-02-demo/brief/p2b01", "Milestone 1", "Lucky Guess", "milestone"),
        ("demo/project-02-demo/brief/p2b03", "Milestone 2", "Scoreboard", "milestone")]
    assert milestones.items[0].solution_group is None  # named `## Lucky Guess` section only
    assert milestones.items[1].solution_group is not None
    assert any("no matching solution section" in note for note in milestones.items[0].notes)
    assert [b["key"] for b in milestones.outro] == ["demo/project-02-demo/brief/p2b05"]


def test_statement_has_no_placeholder_or_starter_panel(demo):
    unit = content(demo, "unit-01-demo")
    by_number = {i.number: i for i in unit.items if i.kind == "unit"}
    assert "Your answer" not in by_number[2].statement_md
    assert "Which animal has black and white stripes?" in by_number[2].statement_md
    for item in unit.items:
        assert "{.starter}" not in item.statement_md
        assert "## Exercise" not in item.statement_md
    assert by_number[4].starter == "def double(n):\n    pass"
    assert by_number[1].starter == ""
    # Structural sections become run-in subheads, as in print.
    assert "**Sample Input.** The program reads one line:" in by_number[1].statement_md
    # A challenge's leading **Challenge:** goes (its heading says so already).
    assert unit.items[-1].statement_md.startswith("Write `triple(n)`.")


def test_item_fields(demo):
    unit = content(demo, "unit-01-demo")
    by_number = {i.number: i for i in unit.items if i.kind == "unit"}
    assert by_number[5].files == ["files/unit-01-demo/assets/count_helper.py"]
    assert by_number[1].files == []  # a solution source is never an item file
    assert by_number[2].division == [] and by_number[2].stretch is False
    assert "def-function" in by_number[4].concepts
    assert set(by_number[4].concepts) <= {"print", "for-loop", "def-function", "variable",
                                          "range-function"}


def test_concept_override_and_findings(demo):
    path = demo / "demo/units/unit-01-demo/exercises.ipynb"
    notebook = nbformat.read(path, as_version=4)
    notebook.cells[1].metadata["concepts"] = ["print", "not-a-concept"]
    nbformat.write(notebook, path)
    items = content(demo, "unit-01-demo").items
    assert items[0].concepts == ["print", "not-a-concept"]
    assert item_concept_findings(demo, "demo", items) == [
        "FAIL: demo/unit-01-demo/exercises/u1e01: unregistered concept not-a-concept"]


def test_division_ids(demo):
    path = demo / "demo/units/unit-01-demo/exercises.ipynb"
    notebook = nbformat.read(path, as_version=4)
    notebook.cells[1].source = notebook.cells[1].source.replace(
        "### Doubler", "_Division: Junior and above._\n\n### Doubler")
    nbformat.write(notebook, path)
    item = content(demo, "unit-01-demo").items[0]
    assert item.division == ["junior"]
    assert "Division" not in item.statement_md


def _cell_keys(book: str, entry_id: str, path: Path) -> set[str]:
    notebook = nbformat.read(path, as_version=4)
    return {f"{book}/{entry_id}/{path.stem}/{cell.id}" for cell in notebook.cells}


def assert_every_cell_placed(book: str, entry_id: str, entry_dir: Path, result: EntryContent):
    path = entry_dir / f"{result.items[0].notebook if result.items else 'exercises'}.ipynb"
    keys = [key for key, _ in result.placement]
    assert len(keys) == len(set(keys)), f"{entry_id}: a cell lands twice"
    bases = {key.split("#")[0] for key in keys}
    assert bases == _cell_keys(book, entry_id, path), entry_id
    # Every block key and item key is one of the placed keys, once.
    shown = [b["key"] for b in result.intro + result.outro] + [
        key for item in result.items for key in [item.key] + [b["key"] for b in item.before]]
    assert len(shown) == len(set(shown))
    assert set(shown) <= set(keys)


def test_every_statement_cell_exported_fixture(demo):
    for entry_id, entry_dir in entries(demo / "demo", "teacher"):
        assert_every_cell_placed("demo", entry_id, entry_dir,
                                 entry_content(demo, "demo", entry_dir, kind_of(entry_id)))


@pytest.mark.parametrize("book", ["python-projects", "python-concepts", "usaco-bronze", "acsl"])
def test_every_statement_cell_exported(book):
    assert book in books_with_flag(ROOT, "site")
    for entry_id, entry_dir in entries(book_path(ROOT, book), "teacher"):
        result = entry_content(ROOT, book, entry_dir, kind_of(entry_id))
        assert result.items, entry_id
        assert_every_cell_placed(book, entry_id, entry_dir, result)


def test_project_partition_real():
    concepts = entry_content(ROOT, "python-concepts",
                             ROOT / "python-concepts/projects/project-01-algorithm-challenge", "project")
    by_number = {item.number: item for item in concepts.items}
    prefix = "python-concepts/project-01-algorithm-challenge/brief/"
    assert prefix + "p01b002" in [b["key"] for b in by_number[1].before]
    assert prefix + "p01b007" in [b["key"] for b in by_number[3].before]
    assert [b["key"] for b in concepts.outro] == [prefix + "p01b028", prefix + "p01b029"]
    usaco = entry_content(ROOT, "usaco-bronze",
                          ROOT / "usaco-bronze/projects/project-03-mock-contest", "project")
    prefix = "usaco-bronze/project-03-mock-contest/brief/"
    assert prefix + "27a38ec3" in [b["key"] for b in usaco.items[0].before]
    assert usaco.items[0].number == 1
    assert [b["key"] for b in usaco.outro] == [prefix + "219d2b81", prefix + "ff8f4935"]
    for item in [*concepts.items, *usaco.items]:
        assert "Make it yours" not in item.statement_md


def test_fixture_items_validate(demo):
    item_schema = validator("item")
    for entry_id, entry_dir in entries(demo / "demo", "teacher"):
        result = entry_content(demo, "demo", entry_dir, kind_of(entry_id))
        for block in result.intro + result.outro:
            assert not list(validator("side_block").iter_errors(block)), block
        for item in result.items:
            data = export_item(demo, "demo", item).data
            errors = [e.message for e in item_schema.iter_errors(data)]
            assert not errors, (item.key, errors)


@pytest.mark.parametrize("book", ["python-projects", "python-concepts", "usaco-bronze", "acsl"])
def test_real_items_validate(book):
    """Every real-book item, with its check data and answer fields, is a schema `item`."""
    item_schema = validator("item")
    side = validator("side_block")
    for entry_id, entry_dir in entries(book_path(ROOT, book), "teacher"):
        result = entry_content(ROOT, book, entry_dir, kind_of(entry_id))
        for block in result.intro + result.outro:
            assert not list(side.iter_errors(block)), block["key"]
        for item in result.items:
            assert isinstance(item, Item)
            data = export_item(ROOT, book, item).data
            errors = [e.message for e in item_schema.iter_errors(data)]
            assert not errors, (item.key, errors[:3])


FENCED = """Trace the class below.

```python
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self, amount):
        self.count = self.count + amount


c = Counter()
```

Then answer."""


def _ctx(kind: str = "unit") -> _Context:
    return _Context(root=ROOT, book="demo", entry_dir=ROOT / "demo" / "unit-01-demo", kind=kind,
                    stem="exercises", lesson_heading=None, placement=[])


def _fence(md: str) -> str:
    return md[md.index("```python"):md.index("```", md.index("```python") + 3) + 3]


def test_statement_keeps_fenced_code_verbatim():
    """A blank line inside a code fence never strips the next line's indentation (plan 102)."""
    cell = nbformat.v4.new_markdown_cell("## Exercise 1\n\n" + FENCED)
    md = _statement_md(_ctx(), [cell], None, False)
    assert _fence(md) == _fence(FENCED)
    assert "Trace the class below." in md and md.rstrip().endswith("Then answer.")


def test_side_block_keeps_fenced_code_verbatim():
    """Intro, `before` and outro prose blocks keep a fenced block verbatim too."""
    cell = nbformat.v4.new_markdown_cell(FENCED)
    for kind in ("unit", "project"):
        block = _side_block(_ctx(kind), cell, "demo/unit-01-demo/exercises/x")
        assert _fence(block["md"]) == _fence(FENCED)


def test_real_statement_keeps_method_indentation():
    """python-concepts u13e066: the `increment` method stays indented inside its class (plan 102)."""
    entry_dir = next((book_path(ROOT, "python-concepts") / "units").glob("unit-13-*"))
    items = {i.key.rsplit("/", 1)[1]: i for i in entry_content(
        ROOT, "python-concepts", entry_dir, "unit").items}
    md = items["u13e066"].statement_md
    assert "\n    def increment(self, amount):\n" in _fence(md)
    assert "\ndef increment" not in md
