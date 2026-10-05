"""Check-kind classification: proposals, tags and `apply_proposals` (plan 101 D, design 012 D4)."""

import importlib.util
from pathlib import Path

import nbformat
import pytest

from tools.export import answers
from tools.export.classify import (
    KINDS,
    PREDICT,
    TAG,
    apply_proposals,
    classification_rows,
    confirmed_kind,
    item_kind,
    propose_kind,
    tag_findings,
)
from tools.export.items import entry_content

_spec = importlib.util.spec_from_file_location(
    "site_demo_book", Path(__file__).parent / "fixtures" / "site" / "demo_book.py")
demo_book = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(demo_book)


@pytest.fixture
def demo(tmp_path):
    answers.clear_caches()
    return demo_book.build_demo_root(tmp_path / "root")


def items_of(root, folder, entry, kind):
    return entry_content(root, "demo", root / "demo" / folder / entry, kind).items


def test_kinds_and_tags():
    assert KINDS == ("fixtures", "answer", "asserts", "expected-output", "predict", "self-check")
    assert TAG == {"fixtures": "check-fixtures", "answer": "check-answer",
                   "asserts": "check-asserts", "expected-output": "check-expected-output",
                   "predict": "check-predict", "self-check": "check-self"}


def test_propose_each_kind(demo):
    unit = items_of(demo, "units", "unit-01-demo", "unit")
    proposed = {item.label: propose_kind(demo, "demo", item) for item in unit}
    assert proposed["Exercise 1"] == ("fixtures", "solver assets/ex1.py with 2 fixture pair(s)")
    assert proposed["Exercise 2"] == ("answer", "short-answer tag")
    assert proposed["Exercise 3"] == ("predict", "the statement asks what the program prints")
    assert proposed["Exercise 4"] == ("asserts", "2 portable top-level assert(s)")  # `double` in the starter
    assert proposed["Exercise 5"] == ("expected-output",
                                      "the solution prints the same output on two runs")
    assert proposed["Exercise 6"] == ("self-check", "the solution or starter calls input()")
    assert proposed["Challenge 1"][0] == "asserts"  # `triple` is bound in the starter

    more = {item.number: item for item in items_of(demo, "units", "unit-02-more", "unit")}
    # Not portable: `my_list` is the student's own choice; the run is fixed, so expected-output.
    kind = propose_kind(demo, "demo", more[1])[0]
    assert kind == "expected-output"
    # Variable-portable: the statement names `total`.
    assert propose_kind(demo, "demo", more[2])[0] == "asserts"
    # Builtins need no binding: `len(names)` with `names` named in the statement.
    assert propose_kind(demo, "demo", more[3])[0] == "asserts"
    # A trace statement whose program prints nothing falls through.
    assert propose_kind(demo, "demo", more[5]) == (
        "self-check", "trace program prints nothing; the solution prints nothing")
    # Unseeded random is never expected-output.
    assert propose_kind(demo, "demo", more[6]) == (
        "self-check", "the solution uses random without seed()")

    checkpoint = items_of(demo, "checkpoints", "checkpoint-01-demo", "checkpoint")
    assert [propose_kind(demo, "demo", i)[0] for i in checkpoint] == ["answer", "asserts"]
    problems = items_of(demo, "projects", "project-01-demo", "project")
    assert [propose_kind(demo, "demo", i)[0] for i in problems] == ["asserts", "asserts"]
    milestones = items_of(demo, "projects", "project-02-demo", "project")
    assert [propose_kind(demo, "demo", i) for i in milestones] == [
        ("self-check", "no matching solution section"),
        ("expected-output", "the solution prints the same output on two runs")]


def test_non_portable_assert_reason(demo):
    more = {item.number: item for item in items_of(demo, "units", "unit-02-more", "unit")}
    assert answers.asserts_portability(more[1]) == (
        False, "asserts test the solution's own choices (my_list)")
    path = demo / "demo/units/unit-02-more/solutions.ipynb"
    notebook = nbformat.read(path, as_version=4)
    notebook.cells[2].source = "my_list = [3, 1, 2]\nassert my_list == [3, 1, 2]"  # silent now
    nbformat.write(notebook, path)
    answers.clear_caches()
    more = {item.number: item for item in items_of(demo, "units", "unit-02-more", "unit")}
    assert propose_kind(demo, "demo", more[1]) == (
        "self-check", "asserts test the solution's own choices (my_list); the solution prints nothing")


def test_predict_not_trace_by_hand(demo):
    more = {item.number: item for item in items_of(demo, "units", "unit-02-more", "unit")}
    item = more[4]
    assert PREDICT.search(item.statement_source) is None  # "trace their counter values by hand"
    assert propose_kind(demo, "demo", item)[0] != "predict"
    assert PREDICT.search("What does this code print?")
    assert PREDICT.search("Predict the output of the loop.")
    assert PREDICT.search("Trace this code and write what it shows.")
    assert not PREDICT.search("Trace the turtle's path on paper.")


def test_tag_findings(demo):
    path = demo / "demo/units/unit-01-demo/exercises.ipynb"
    notebook = nbformat.read(path, as_version=4)
    notebook.cells[1].metadata["tags"] = ["check-fixtures", "check-answer"]
    notebook.cells[2].metadata["tags"] = ["check-self"]  # Exercise 1's starter: a body cell
    notebook.cells[3].metadata["tags"] = ["short-answer", "check-bogus"]
    nbformat.write(notebook, path)
    items = items_of(demo, "units", "unit-01-demo", "unit")
    assert tag_findings(items[0]) == [
        "FAIL: demo/unit-01-demo/exercises/u1e01: more than one check-* tag: check-fixtures, check-answer",
        ("FAIL: demo/unit-01-demo/exercises/u1e01: check-self on a non-heading cell (u1e02); "
         "check-* tags go on the item's heading cell")]
    assert tag_findings(items[1]) == ["FAIL: demo/unit-01-demo/exercises/u1e03: unknown check tag check-bogus"]
    assert tag_findings(items[2]) == []
    assert confirmed_kind(items[0]) == "fixtures"
    assert confirmed_kind(items[1]) is None


def test_confirmed_tag_wins(demo):
    path = demo / "demo/units/unit-01-demo/exercises.ipynb"
    notebook = nbformat.read(path, as_version=4)
    notebook.cells[9].metadata["tags"] = ["check-self"]  # Exercise 5 would be expected-output
    nbformat.write(notebook, path)
    item = items_of(demo, "units", "unit-01-demo", "unit")[4]
    assert item_kind(demo, "demo", item) == ("self-check", "confirmed by check-self")
    assert answers.check_data(demo, "demo", item, "self-check")["confirmed"] is True


def test_classification_rows(demo):
    rows = classification_rows(demo, "demo", "unit-01-demo")
    assert rows[0] == ("demo/unit-01-demo/exercises/u1e01", "fixtures", "",
                       "solver assets/ex1.py with 2 fixture pair(s)")
    assert len(rows) == 7
    with pytest.raises(ValueError, match="no syllabus entry"):
        classification_rows(demo, "demo", "unit-99-missing")


def _snapshot(path: Path):
    notebook = nbformat.read(path, as_version=4)
    return [(c.id, c.cell_type, c.source, c.get("outputs")) for c in notebook.cells]


def test_apply_proposals_roundtrip(demo):
    paths = sorted((demo / "demo").rglob("*.ipynb"))
    before = {path: _snapshot(path) for path in paths}
    changed = apply_proposals(demo, "demo")
    assert "demo/unit-01-demo/exercises/u1e01" in changed
    assert len(changed) == 7 + 6 + 2 + 2 + 2
    unit = items_of(demo, "units", "unit-01-demo", "unit")
    assert [c.metadata.get("tags") for c in [i.heading_cell for i in unit]] == [
        ["check-fixtures"], ["short-answer", "check-answer"], ["check-predict"],
        ["check-asserts"], ["check-expected-output"], ["check-self"], ["stretch", "check-asserts"]]
    assert [confirmed_kind(i) for i in unit][:2] == ["fixtures", "answer"]
    # Ids, sources and outputs are unchanged; only tags were added.
    assert {path: _snapshot(path) for path in paths} == before
    more = nbformat.read(demo / "demo/units/unit-02-more/exercises.ipynb", as_version=4)
    assert more.cells[-1].outputs[0]["text"] == "4\n"
    # A second apply changes nothing.
    texts = {path: path.read_text(encoding="utf-8") for path in paths}
    assert apply_proposals(demo, "demo") == []
    assert {path: path.read_text(encoding="utf-8") for path in paths} == texts


def test_apply_proposals_one_entry(demo):
    changed = apply_proposals(demo, "demo", "checkpoint-01-demo")
    assert changed == ["demo/checkpoint-01-demo/checkpoint/c1c01",
                       "demo/checkpoint-01-demo/checkpoint/c1c02"]
