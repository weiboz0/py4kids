"""The answer model: canonical texts, hashes, asserts, fixtures, odd answers (plan 101 D, design 012 D5)."""

import importlib.util
import json
import re
from pathlib import Path

import nbformat
import pytest

from tools.books import book_path, publication_config
from tools.export import answers
from tools.export.items import entry_content, export_item
from tools.export.normalise import answer_hash
from tools.publish import answer_key, entries, group_title, item_groups, student_answer_text

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "site_demo_book", Path(__file__).parent / "fixtures" / "site" / "demo_book.py")
demo_book = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(demo_book)


@pytest.fixture
def demo(tmp_path):
    answers.clear_caches()
    return demo_book.build_demo_root(tmp_path / "root")


def unit_items(root, entry="unit-01-demo"):
    return {i.label: i for i in entry_content(root, "demo", root / "demo/units" / entry, "unit").items}


# --- odd answers ---------------------------------------------------------------------------


def _appendix_slices(entry: Path, lesson_heading: str | None) -> dict[int, str]:
    """Each odd exercise's text in the Student Book appendix (`answer_key(..., 'student')`)."""
    notebook = nbformat.read(entry / "exercises.ipynb", as_version=4)
    items = [{"number": g["number"], "title": group_title(g, "Exercise")}
             for g in item_groups(notebook.cells, "Exercise")[1]]
    appendix = answer_key(entry, "unit", items, "student", lesson_heading)
    unit = int(re.search(r"unit-(\d+)", entry.name)[1])
    heading = re.compile(rf"^### Unit {unit}, Exercise (\d+)\b.*\n\n```\{{=latex\}}\n\\label\{{ans:"
                         rf"{re.escape(entry.name)}:\d+\}}\n```(?:\n\n|\n?$)", re.MULTILINE)
    marks = list(heading.finditer(appendix))
    slices = {}
    for index, mark in enumerate(marks):
        end = marks[index + 1].start() if index + 1 < len(marks) else len(appendix)
        slices[int(mark[1])] = appendix[mark.end():end].rstrip("\n").removesuffix("\n")
    assert len(marks) == sum(1 for item in items if item["number"] % 2), entry.name
    return slices


@pytest.mark.parametrize("book", ["python-projects", "python-concepts", "usaco-bronze", "acsl"])
def test_odd_answer_equals_appendix(book):
    lesson_heading = publication_config(ROOT, book).lesson_heading
    checked = 0
    for entry_id, entry in entries(book_path(ROOT, book), "student"):
        if not entry_id.startswith("unit-"):
            continue
        slices = _appendix_slices(entry, lesson_heading)
        for item in entry_content(ROOT, book, entry, "unit").items:
            fields = answers.answer_fields(ROOT, book, item)
            if item.kind == "unit" and item.number % 2:
                text = student_answer_text(entry, item.number, lesson_heading)
                assert text == slices[item.number], item.key
                assert fields == {"answer_visibility": "after-attempt", "answer_md": text}
                checked += 1
            else:
                assert fields == {"answer_visibility": "none"}, item.key
    assert checked > 0


def test_student_answer_text_only_odd(demo):
    entry = demo / "demo/units/unit-01-demo"
    assert "The loop prints 0, 2 and 4." in student_answer_text(entry, 3, None)
    with pytest.raises(ValueError, match="missing solution Exercise 4"):
        student_answer_text(entry, 4, None)


def test_answer_fields(demo):
    unit = unit_items(demo)
    assert answers.answer_fields(demo, "demo", unit["Exercise 1"])["answer_visibility"] == "after-attempt"
    assert answers.answer_fields(demo, "demo", unit["Exercise 2"]) == {"answer_visibility": "none"}
    assert answers.answer_fields(demo, "demo", unit["Challenge 1"]) == {"answer_visibility": "none"}
    checkpoint = entry_content(demo, "demo", demo / "demo/checkpoints/checkpoint-01-demo",
                               "checkpoint").items
    assert answers.answer_fields(demo, "demo", checkpoint[0]) == {"answer_visibility": "none"}


# --- hidden items --------------------------------------------------------------------------


def test_hidden_items_ship_hash_only(demo):
    item = unit_items(demo)["Exercise 2"]
    exported = export_item(demo, "demo", item)
    check = exported.data["check"]
    assert check == {"kind": "answer", "hash": answer_hash(item.key, "ZEBRA", case="insensitive"),
                     "answer_format": {"case": "insensitive", "hint": "one word"},
                     "turtle": False, "confirmed": False}
    dumped = json.dumps(exported.data)
    assert "zebra" not in dumped.casefold()
    assert "answer_md" not in exported.data
    # Hidden predict and expected-output texts ship as hashes too.
    for label, canonical in (("Exercise 3", "0\n2\n4\n"), ("Exercise 5", "1\n2\n3\ndone\n")):
        data = export_item(demo, "demo", unit_items(demo)[label]).data
        fmt = data["check"]["answer_format"]
        assert data["check"]["hash"] == answer_hash(data["key"], canonical, case=fmt["case"])
    checkpoint = entry_content(demo, "demo", demo / "demo/checkpoints/checkpoint-01-demo",
                               "checkpoint").items
    data = export_item(demo, "demo", checkpoint[0]).data
    assert data["check"]["hash"] == answer_hash(data["key"], "8", case="sensitive")
    assert "eight" not in json.dumps(data)


def test_asserts_ship_no_function_body(demo):
    item = unit_items(demo)["Exercise 4"]
    check = answers.check_data(demo, "demo", item, "asserts")
    assert check == {"kind": "asserts", "source": "assert double(3) == 6\nassert double(0) == 0",
                     "functions": ["double"], "turtle": False, "confirmed": False}
    data = export_item(demo, "demo", item).data
    assert "return n * 2" not in json.dumps(data)
    more = {i.number: i for i in entry_content(demo, "demo", demo / "demo/units/unit-02-more",
                                               "unit").items}
    assert answers.asserts_check(more[3]) == ("assert len(names) == 3", [])
    with pytest.raises(ValueError, match="check-asserts: asserts test the solution's own choices"):
        answers.check_data(demo, "demo", more[1], "asserts")


def test_answer_line_exactly_one(demo):
    path = demo / "demo/units/unit-01-demo/solutions.ipynb"
    notebook = nbformat.read(path, as_version=4)
    notebook.cells[4].source += "\n\n**Answer:** `HORSE`"
    nbformat.write(notebook, path)
    item = unit_items(demo)["Exercise 2"]
    with pytest.raises(ValueError, match=r"FAIL: demo/unit-01-demo/exercises/u1e03: expected exactly "
                                         r"one \*\*Answer:\*\* line in the solution, found 2"):
        answers.check_data(demo, "demo", item, "answer")


# --- fixtures ------------------------------------------------------------------------------


def test_fixture_sample_and_budget(demo):
    item = unit_items(demo)["Exercise 1"]
    assert answers.sample_input(item.statement_source) == "3\n"  # the fence after the prose
    check = answers.check_data(demo, "demo", item, "fixtures")
    assert check == {
        "kind": "fixtures",
        "cases": [
            {"n": 1, "in_file": "files/unit-01-demo/fixtures/ex1/1.in",
             "out_file": "files/unit-01-demo/fixtures/ex1/1.out", "sample": True},
            {"n": 2, "in_file": "files/unit-01-demo/fixtures/ex1/2.in",
             "out_file": "files/unit-01-demo/fixtures/ex1/2.out", "sample": False}],
        "match": "token", "over_budget": [], "turtle": False, "confirmed": False}
    assert [path for path, _ in answers.fixture_files(demo, "demo", item)] == [
        "files/unit-01-demo/fixtures/ex1/1.in", "files/unit-01-demo/fixtures/ex1/1.out",
        "files/unit-01-demo/fixtures/ex1/2.in", "files/unit-01-demo/fixtures/ex1/2.out"]

    fixtures = demo / "demo/units/unit-01-demo/assets/ex1"
    (fixtures / "1.in").write_text("4\n", encoding="utf-8")  # no pair matches the sample now
    (fixtures / "1.out").write_text("8\n", encoding="utf-8")
    (fixtures / "10.in").write_text("1" * 150_000 + "\n", encoding="utf-8")  # a 200 KB pair
    (fixtures / "10.out").write_text("2" * 50_000 + "\n", encoding="utf-8")
    check = answers.check_data(demo, "demo", item, "fixtures")
    assert [case["n"] for case in check["cases"]] == [1, 2, 10]  # numeric order
    assert not any(case["sample"] for case in check["cases"])
    assert check["over_budget"] == [10]
    assert answers.check_notes(demo, "demo", item, "fixtures") == [
        "fixtures: no pair matches the statement's Sample Input",
        "fixtures: case 10 over the 130 KB budget"]


def test_fixture_match_line_for_acsl_books(demo):
    books = demo / "books.yaml"
    books.write_text(books.read_text(encoding="utf-8") + "  acsl: true\n", encoding="utf-8")
    item = unit_items(demo)["Exercise 1"]
    assert answers.check_data(demo, "demo", item, "fixtures")["match"] == "line"


def test_sample_input_forms():
    assert answers.sample_input("### Sample Input\n\n```\n1 2\n```\n") == "1 2\n"
    assert answers.sample_input("### Sample Input 1\n\nFirst:\n\n```text\na\n```\n\n"
                                "### Sample Input 2\n\n```text\nb\n```") == "a\n"
    assert answers.sample_input("### Sample Input\n\nNone shown.\n\n### Sample Output\n\n```\n1\n```") is None
    assert answers.sample_input("No sample here.") is None


def test_real_sample_after_prose():
    """ACSL unit 15 Exercise 17's Sample Input fence follows prose; a pair matches it."""
    entry = ROOT / "acsl/units/unit-15-assembly-language"
    item = next(i for i in entry_content(ROOT, "acsl", entry, "unit").items if i.number == 17)
    assert answers.sample_input(item.statement_source) is not None
    check = answers.check_data(ROOT, "acsl", item, "fixtures")
    assert sum(case["sample"] for case in check["cases"]) == 1
    assert check["match"] == "line"


# --- answer formats --------------------------------------------------------------------------


def test_answer_format_override_and_derivation(demo):
    unit = unit_items(demo)
    assert answers.answer_format(unit["Exercise 2"], "ZEBRA") == (
        {"case": "insensitive", "hint": "one word"}, [])
    assert answers.derive_answer_format("  42 \n") == {"case": "sensitive", "hint": "a number"}
    assert answers.derive_answer_format("-3.5") == {"case": "sensitive", "hint": "a number"}
    assert answers.derive_answer_format("13 8 3") == {"case": "sensitive", "hint": "one line"}
    assert answers.derive_answer_format("0\n2\n4\n") == {"case": "sensitive", "hint": "several lines"}
    assert answers.answer_format(unit["Exercise 3"], "0\n2\n4\n") == (
        {"case": "sensitive", "hint": "several lines"}, [])
    assert answers.answer_format(unit["Exercise 5"], "1\n2\n3\ndone\n") == (
        {"case": "sensitive", "hint": "several lines"}, ["answer_format: derived (letters)"])
    unit["Exercise 3"].heading_cell.metadata["answer_format"] = {"case": "loud", "hint": "x"}
    with pytest.raises(ValueError, match="metadata.answer_format must be"):
        answers.answer_format(unit["Exercise 3"], "0")


def test_self_check_requirements(demo):
    unit = unit_items(demo)
    assert answers.check_data(demo, "demo", unit["Exercise 6"], "self-check")["requirements"] == [
        "asks for a name with input()", "prints a greeting that uses the name"]
    requirements, notes = answers.self_check_requirements(unit["Exercise 4"])
    assert requirements == ["Write double(n) so it returns twice n."]
    assert notes == ["self-check: no list in the statement"]
    unit["Exercise 4"].heading_cell.metadata["requirements"] = ["defines double", "returns 2n"]
    assert answers.self_check_requirements(unit["Exercise 4"]) == (["defines double", "returns 2n"], [])


# --- sandboxed runs ----------------------------------------------------------------------------


def test_runs_use_tracked_files_only(demo):
    entry = demo / "demo/units/unit-01-demo"
    (entry / "scratch.txt").write_text("untracked\n", encoding="utf-8")
    probe = ("import os\nprint(os.path.exists('scratch.txt'), os.path.exists('assets/ex1.py'))\n"
             "open('written.txt', 'w').write('x')\nimport sys\nprint(repr(sys.stdin.read()))\n"
             "print(os.environ['PYTHONHASHSEED'])")
    result = answers.run_python(entry, probe)
    assert result.status == "ok"
    assert result.stdout == "False True\n''\n0\n"
    assert not (entry / "written.txt").exists()
    slow = answers.run_python(entry, "import time\ntime.sleep(5)", timeout_s=0.5)
    assert slow.status == "timeout"


# --- the hidden corpora (Phase F) ----------------------------------------------------------------


def test_hidden_corpora_accessors(demo):
    cells = answers.solution_code_cells(demo, "demo")
    solution_cells = sum(
        sum(1 for c in nbformat.read(path, as_version=4).cells if c.cell_type == "code")
        for path in (demo / "demo").rglob("solutions.ipynb"))
    assert len(cells) == solution_cells
    by_origin = {c.origin: c for c in cells}
    odd = by_origin["demo/units/unit-01-demo/solutions.ipynb#u1s07"]
    assert (odd.item, odd.released) == ("Exercise 3", True)
    even = by_origin["demo/units/unit-01-demo/solutions.ipynb#u1s09"]
    assert (even.item, even.released) == ("Exercise 4", False)
    assert by_origin["demo/units/unit-01-demo/solutions.ipynb#u1s16"].item == "Challenge 1"
    assert by_origin["demo/projects/project-02-demo/solutions.ipynb#p2s02"].item == "Lucky Guess"

    files = {f.origin: f for f in answers.solution_asset_files(demo, "demo")}
    assert files["demo/units/unit-01-demo/assets/ex1.py"].released is True
    assert "demo/units/unit-01-demo/assets/count_helper.py" not in files

    paragraphs = answers.solution_markdown_paragraphs(demo, "demo")
    assert any(p.text == "Zebras have black and white stripes." and not p.released for p in paragraphs)

    canon = answers.canonical_texts(demo, "demo")
    assert canon["demo/unit-01-demo/exercises/u1e03"] == ("answer", "ZEBRA", "insensitive")
    assert canon["demo/unit-01-demo/exercises/u1e05"] == ("predict", "0\n2\n4\n", "sensitive")
    assert canon["demo/checkpoint-01-demo/checkpoint/c1c01"] == ("answer", "8", "sensitive")
    released = answers.released_answers(demo, "demo")
    assert set(released) == {"demo/unit-01-demo/exercises/u1e01", "demo/unit-01-demo/exercises/u1e05",
                             "demo/unit-01-demo/exercises/u1e09", "demo/unit-02-more/exercises/u2e01",
                             "demo/unit-02-more/exercises/u2e05", "demo/unit-02-more/exercises/u2e09"}
    asserts = answers.shipped_asserts(demo, "demo")
    assert asserts["demo/unit-01-demo/exercises/u1e07"] == "assert double(3) == 6\nassert double(0) == 0"
