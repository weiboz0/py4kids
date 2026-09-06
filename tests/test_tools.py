import copy
import os
from pathlib import Path

import nbformat
import pytest
import yaml

from tools import cli
from tools.checks import CHECKS
from tools.curriculum import map_schema_findings

REPO = Path(__file__).resolve().parents[1]
CHECK_NAMES = (
    "manifest-check",
    "hygiene-check",
    "structure-check",
    "noexec-check",
    "exec-solutions",
    "exec-lessons",
    "cell-lint",
    "turtle-check",
    "prereq-check",
    "coverage-check",
    "stretch-check",
)
REAL_BOOK_EXEC_CHECKS = {"exec-solutions", "exec-lessons"}


def _write_yaml(path, data):
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _read_nb(path):
    return nbformat.read(path, as_version=4)


def _write_nb(path, notebook):
    nbformat.write(notebook, path)


@pytest.fixture
def valid_root(tmp_path):
    """Build an all-green registry root with one complete prefix unit."""
    book = tmp_path / "book1"
    (book / "curriculum").mkdir(parents=True)
    (book / "units").mkdir()
    concept_ids = ["turtle-basics", *(f"concept-{index:02d}" for index in range(39))]
    concepts = {
        "concepts_version": 1,
        "concepts": [
            {"id": concept, "name": f"Concept {index}", "category": "graphics"}
            for index, concept in enumerate(concept_ids)
        ],
    }
    entries = []
    for index in range(8):
        introduced = concept_ids[index * 5 : (index + 1) * 5]
        entries.append(
            {
                "id": f"unit-{index + 1:02d}-fixture",
                "kind": "unit",
                "title": f"Fixture unit {index + 1}",
                "lessons": 3,
                "introduces": introduced,
                "requires": [] if index == 0 else [concept_ids[0]],
                "practices": [] if index == 0 else concept_ids[: index * 5],
            }
        )
    entries.append(
        {
            "id": "checkpoint-01-fixture",
            "kind": "checkpoint",
            "title": "Fixture checkpoint",
            "lessons": 1,
            "introduces": [],
            "requires": [concept_ids[0]],
            "practices": list(concept_ids),
        }
    )
    entries.append(
        {
            "id": "project-02-grand-adventure",
            "kind": "project",
            "title": "Fixture capstone",
            "lessons": 5,
            "introduces": [],
            "requires": [concept_ids[0]],
            "practices": list(concept_ids),
        }
    )
    _write_yaml(book / "curriculum/concepts.yaml", concepts)
    _write_yaml(book / "curriculum/coverage-map.yaml", {"map_version": 1, "entries": entries})
    syllabus_rows = "\n".join(
        f"| `{entry['id']}` | {entry['kind']} | {entry['lessons']:g} |" for entry in entries
    )
    (book / "syllabus.md").write_text(syllabus_rows + "\n", encoding="utf-8")
    unit = book / "units/unit-01-story-machine"
    unit.mkdir()
    entries[0]["id"] = unit.name
    _write_yaml(book / "curriculum/coverage-map.yaml", {"map_version": 1, "entries": entries})
    (book / "syllabus.md").write_text(
        "\n".join(
            f"| `{entry['id']}` | {entry['kind']} | {entry['lessons']:g} |" for entry in entries
        )
        + "\n",
        encoding="utf-8",
    )
    _write_yaml(
        unit / "manifest.yaml",
        {
            "id": unit.name,
            "kind": "unit",
            "blueprint_version": 1,
            "lessons": 3,
            "concepts": {
                "introduces": concept_ids[:5],
                "requires": [],
                "practices": [],
            },
            "provenance": "original",
        },
    )
    lesson = nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_markdown_cell("# Project hook"),
            nbformat.v4.new_code_cell("value = 1"),
            nbformat.v4.new_code_cell(
                "name = input('teacher demo: ')", metadata={"tags": ["no-exec"]}
            ),
            nbformat.v4.new_code_cell("assert value == 1"),
        ]
    )
    _write_nb(unit / "lesson.ipynb", lesson)
    exercises = []
    solutions = []
    for index in range(1, 7):
        metadata = {"tags": ["stretch"]} if index >= 5 else {}
        exercises.append(
            nbformat.v4.new_markdown_cell(
                f"Exercise prompt.\n## Exercise {index}\nDo the work.", metadata=metadata
            )
        )
        exercises.append(nbformat.v4.new_code_cell(""))
        solutions.append(nbformat.v4.new_markdown_cell(f"Answer notes.\n## Exercise {index}"))
        solutions.append(nbformat.v4.new_code_cell(f"answer_{index} = {index}"))
        if index <= 4:
            solutions.append(nbformat.v4.new_code_cell(f"assert answer_{index} == {index}"))
    exercises.append(nbformat.v4.new_markdown_cell("This is not a ## Exercise 99 heading."))
    _write_nb(unit / "exercises.ipynb", nbformat.v4.new_notebook(cells=exercises))
    _write_nb(unit / "solutions.ipynb", nbformat.v4.new_notebook(cells=solutions))
    (unit / "teacher-notes.md").write_text(
        "## Goals\nGoal.\n## Pacing\n60 minutes.\n## Common mistakes\nMistake.\n"
        "## Discussion prompts\nPrompt.\n## Differentiation\nSupport.\n",
        encoding="utf-8",
    )
    assets = unit / "assets"
    assets.mkdir()
    (assets / "closed.py").write_text(
        "import turtle\nfor _ in range(4):\n    turtle.forward(10)\n    turtle.right(90)\n"
        "turtle.done()\n",
        encoding="utf-8",
    )
    return tmp_path


def _run(root, check, capsys, unit=None):
    args = ["--root", str(root), "--book", "book1"]
    if unit:
        args += ["--unit", unit]
    args.append(check)
    code = cli.main(args)
    return code, capsys.readouterr().out


def test_cli_check_registry_is_exact():
    assert tuple(CHECKS) == CHECK_NAMES


def test_cli_exit_codes(valid_root, capsys):
    code, output = _run(valid_root, "manifest-check", capsys)
    assert code == 0
    assert output == "manifest-check: PASS\n"
    assert cli.main(["--book", "book1", "not-a-check"]) == 2


@pytest.mark.parametrize("check", CHECK_NAMES)
def test_generated_baseline_passes_each_check(valid_root, check, capsys):
    code, output = _run(valid_root, check, capsys)
    assert code == 0, output


@pytest.mark.parametrize("check", CHECK_NAMES)
def test_real_book_passes_each_check(check, capsys):
    if _skip_exec_in_ci("real-book", check):
        pytest.skip("real-book notebook execution is authoritative in CI step 3")
    code, output = _run(REPO, check, capsys)
    assert code == 0, output


def _skip_exec_in_ci(scope, check):
    return (
        os.environ.get("PY4KIDS_CI") == "1"
        and scope == "real-book"
        and check in REAL_BOOK_EXEC_CHECKS
    )


def test_ci_mode_skips_only_real_book_execution(monkeypatch):
    monkeypatch.setenv("PY4KIDS_CI", "1")
    skipped = {
        (scope, check)
        for scope in ("real-book", "generated", "negative")
        for check in CHECK_NAMES
        if _skip_exec_in_ci(scope, check)
    }
    assert skipped == {("real-book", check) for check in REAL_BOOK_EXEC_CHECKS}


def _unit(root):
    return root / "book1/units/unit-01-story-machine"


def _manifest(root):
    path = _unit(root) / "manifest.yaml"
    return path, yaml.safe_load(path.read_text(encoding="utf-8"))


def _map(root):
    path = root / "book1/curriculum/coverage-map.yaml"
    return path, yaml.safe_load(path.read_text(encoding="utf-8"))


def _concepts(root):
    path = root / "book1/curriculum/concepts.yaml"
    return path, yaml.safe_load(path.read_text(encoding="utf-8"))


def _notebook(root, name):
    path = _unit(root) / name
    return path, _read_nb(path)


def _remove_required(root, name):
    (_unit(root) / name).unlink()


def _missing_assets(root):
    for path in (_unit(root) / "assets").iterdir():
        path.unlink()
    (_unit(root) / "assets").rmdir()


def _missing_asset_reference(root):
    path, nb = _notebook(root, "lesson.ipynb")
    nb.cells.append(nbformat.v4.new_markdown_cell("Run `assets/missing.py`."))
    _write_nb(path, nb)


def _noncompiling_asset(root):
    (_unit(root) / "assets/closed.py").write_text("if True print('broken')\n", encoding="utf-8")


def _exercise_heading_floor(root):
    path, nb = _notebook(root, "exercises.ipynb")
    removed = False
    for cell in nb.cells:
        if cell.cell_type == "markdown" and "## Exercise " in cell.source and not removed:
            cell.source = cell.source.replace("## Exercise ", "## Activity ", 1)
            removed = True
    _write_nb(path, nb)


def _stretch_floor(root):
    path, nb = _notebook(root, "exercises.ipynb")
    for cell in nb.cells:
        cell.metadata["tags"] = [t for t in cell.metadata.get("tags", []) if t != "stretch"]
    _write_nb(path, nb)


def _missing_solution_heading(root):
    path, nb = _notebook(root, "solutions.ipynb")
    for cell in nb.cells:
        if cell.cell_type == "markdown" and "## Exercise 1" in cell.source:
            cell.source = cell.source.replace("## Exercise 1", "## Answer 1")
            break
    _write_nb(path, nb)


def _solution_heading_without_code(root):
    path, nb = _notebook(root, "solutions.ipynb")
    start = next(
        i
        for i, cell in enumerate(nb.cells)
        if cell.cell_type == "markdown" and "## Exercise 1" in cell.source
    )
    end = next(
        i
        for i, cell in enumerate(nb.cells[start + 1 :], start + 1)
        if cell.cell_type == "markdown" and "## Exercise 2" in cell.source
    )
    nb.cells[start + 1 : end] = [c for c in nb.cells[start + 1 : end] if c.cell_type != "code"]
    _write_nb(path, nb)


def _assert_floor(root):
    path, nb = _notebook(root, "solutions.ipynb")
    kept = 0
    for cell in nb.cells:
        if cell.cell_type == "code" and "assert" in cell.source:
            kept += 1
            if kept > 2:
                cell.source = cell.source.replace("assert", "# removed check", 1)
    _write_nb(path, nb)


def _add_solution_code(root, source):
    path, nb = _notebook(root, "solutions.ipynb")
    nb.cells.append(nbformat.v4.new_code_cell(source))
    _write_nb(path, nb)


def _input_ban(root):
    _add_solution_code(root, "name = input ('name? ')")


def _gui_ban(root):
    _add_solution_code(root, "value = 1\nimport tkinter")


def _gui_from_turtle_ban(root):
    _add_solution_code(root, "if True:\n    from  turtle   import Turtle")


def _random_import_ban(root):
    _add_solution_code(root, "if True:\n    from  random   import randint")


def _random_seed_missing(root):
    _add_solution_code(root, "import random\nvalue = random.randint(1, 3)")


def _random_seed_late(root):
    _add_solution_code(root, "import random\nvalue = random.randint(1, 3)\nrandom.seed(4)")


def _notes_heading(root, heading):
    path = _unit(root) / "teacher-notes.md"
    path.write_text(
        path.read_text(encoding="utf-8").replace(heading, "## Removed", 1),
        encoding="utf-8",
    )


def _prefix_gap(root):
    source = _unit(root)
    destination = root / "book1/units/unit-03-turtle-art-studio"
    source.rename(destination)
    path, manifest = (
        destination / "manifest.yaml",
        yaml.safe_load((destination / "manifest.yaml").read_text(encoding="utf-8")),
    )
    manifest["id"] = destination.name
    _write_yaml(path, manifest)


STRUCTURE_CASES = [
    *(
        (
            f"required-{name}",
            lambda root, name=name: _remove_required(root, name),
            f"missing {name}",
        )
        for name in (
            "manifest.yaml",
            "lesson.ipynb",
            "exercises.ipynb",
            "solutions.ipynb",
            "teacher-notes.md",
        )
    ),
    ("turtle-assets", _missing_assets, "introduces turtle but has no assets/"),
    ("asset-reference", _missing_asset_reference, "references missing assets/missing.py"),
    ("asset-compile", _noncompiling_asset, "asset closed.py does not compile"),
    ("exercise-floor", _exercise_heading_floor, "5 exercise headings (<6)"),
    ("stretch-floor", _stretch_floor, "0 stretch-tagged cells (<2)"),
    ("solution-mirror", _missing_solution_heading, "solutions missing '## Exercise 1'"),
    (
        "solution-code",
        _solution_heading_without_code,
        "solutions: no code under '## Exercise 1'",
    ),
    ("assert-floor", _assert_floor, "solutions need >=3 assert cells"),
    ("input-ban", _input_ban, "solutions call input()"),
    ("gui-ban", _gui_ban, "solutions import a GUI"),
    ("gui-from-turtle-ban", _gui_from_turtle_ban, "solutions import a GUI"),
    ("random-import-ban", _random_import_ban, "solutions use 'from random import'"),
    (
        "random-seed",
        _random_seed_missing,
        "solutions use random without random.seed(4)",
    ),
    (
        "random-seed-order",
        _random_seed_late,
        "solutions: random.seed(4) must precede first use",
    ),
    *(
        (
            "notes-" + h.lower().replace(" ", "-"),
            lambda root, h=h: _notes_heading(root, h),
            f"teacher notes missing '{h}'",
        )
        for h in (
            "## Goals",
            "## Pacing",
            "## Common mistakes",
            "## Discussion prompts",
            "## Differentiation",
        )
    ),
    ("unit-prefix", _prefix_gap, "unit directories are not the coverage-map prefix"),
]


@pytest.mark.parametrize(
    "_name,mutate,expected",
    STRUCTURE_CASES,
    ids=lambda value: value if isinstance(value, str) else None,
)
def test_structure_one_fault(valid_root, capsys, _name, mutate, expected):
    mutate(valid_root)
    code, output = _run(valid_root, "structure-check", capsys)
    assert code == 1
    lines = [line for line in output.splitlines() if line.startswith("FAIL:")]
    if expected.startswith("unit directories"):
        expected_lines = [f"FAIL: book1: {expected}"]
    else:
        expected_lines = [f"FAIL: unit-01-story-machine: {expected}"]
    assert lines == expected_lines


def test_asset_compile_does_not_write_pycache(valid_root, capsys):
    code, output = _run(valid_root, "structure-check", capsys)
    assert code == 0, output
    assert not (_unit(valid_root) / "assets/__pycache__").exists()


def _manifest_mutation(root, key, value):
    path, data = _manifest(root)
    data[key] = value
    _write_yaml(path, data)


def _manifest_keys(root):
    path, data = _manifest(root)
    data["extra"] = True
    _write_yaml(path, data)


def _manifest_concept_keys(root):
    path, data = _manifest(root)
    data["concepts"]["extra"] = []
    _write_yaml(path, data)


def _manifest_map_field(root, field):
    path, data = _manifest(root)
    if field == "lessons":
        data[field] += 1
    else:
        data["concepts"][field] = list(data["concepts"][field]) + ["float-type"]
    _write_yaml(path, data)


MANIFEST_CASES = [
    ("keys", _manifest_keys, "manifest keys"),
    ("kind", lambda r: _manifest_mutation(r, "kind", "project"), "kind must be unit"),
    (
        "blueprint",
        lambda r: _manifest_mutation(r, "blueprint_version", 2),
        "blueprint_version must be 1",
    ),
    (
        "provenance",
        lambda r: _manifest_mutation(r, "provenance", "unknown"),
        "provenance must be original",
    ),
    ("id", lambda r: _manifest_mutation(r, "id", "unit-99-wrong"), "id does not match directory"),
    ("concept-keys", _manifest_concept_keys, "concept keys"),
    *(
        (
            "map-" + field,
            lambda root, field=field: _manifest_map_field(root, field),
            f"{field} differs from coverage map",
        )
        for field in ("lessons", "introduces", "requires", "practices")
    ),
]


@pytest.mark.parametrize("_name,mutate,expected", MANIFEST_CASES)
def test_manifest_one_fault(valid_root, capsys, _name, mutate, expected):
    mutate(valid_root)
    code, output = _run(valid_root, "manifest-check", capsys)
    assert code == 1
    assert output.count("FAIL:") == 1
    assert f"FAIL: unit-01-story-machine: {expected}" in output


def test_manifest_missing_map_entry(valid_root, capsys):
    path, data = _map(valid_root)
    data["entries"][0]["id"] = "unit-01-renamed"
    _write_yaml(path, data)
    code, output = _run(valid_root, "manifest-check", capsys)
    assert code == 1
    assert output == "FAIL: unit-01-story-machine: not in coverage map\n"


@pytest.mark.parametrize("source", ["null\n", "[]\n"])
def test_manifest_scalar_or_null_returns_finding(valid_root, capsys, source):
    (_unit(valid_root) / "manifest.yaml").write_text(source, encoding="utf-8")
    code, output = _run(valid_root, "manifest-check", capsys)
    assert code == 1
    assert output == "FAIL: unit-01-story-machine: manifest must be a mapping\n"


def test_manifest_null_concepts_returns_finding(valid_root, capsys):
    path, manifest = _manifest(valid_root)
    manifest["concepts"] = None
    _write_yaml(path, manifest)
    code, output = _run(valid_root, "manifest-check", capsys)
    assert code == 1
    assert output == "FAIL: unit-01-story-machine: manifest concepts must be a mapping\n"


@pytest.mark.parametrize("entry_id", [[], {}])
def test_manifest_unhashable_coverage_map_id_returns_finding(valid_root, capsys, entry_id):
    path, data = _map(valid_root)
    data["entries"][0]["id"] = entry_id
    _write_yaml(path, data)
    code, output = _run(valid_root, "manifest-check", capsys)
    assert code == 1
    assert output == "FAIL: book1: coverage-map entry 0 id must be a string\n"


def test_manifest_concept_list_members_must_be_ids(valid_root, capsys):
    path, manifest = _manifest(valid_root)
    manifest["concepts"]["introduces"].append({})
    _write_yaml(path, manifest)
    code, output = _run(valid_root, "manifest-check", capsys)
    assert code == 1
    assert output == (
        "FAIL: unit-01-story-machine: manifest concepts.introduces must be a list of ids\n"
    )


def test_hygiene_output_one_fault(valid_root, capsys):
    path, nb = _notebook(valid_root, "exercises.ipynb")
    cell = next(c for c in nb.cells if c.cell_type == "code")
    cell.outputs = [nbformat.v4.new_output("stream", name="stdout", text="leak\n")]
    _write_nb(path, nb)
    code, output = _run(valid_root, "hygiene-check", capsys)
    assert code == 1
    assert "has outputs" in output
    assert output.count("FAIL:") == 1


def test_hygiene_execution_count_one_fault(valid_root, capsys):
    path, nb = _notebook(valid_root, "exercises.ipynb")
    next(c for c in nb.cells if c.cell_type == "code").execution_count = 1
    _write_nb(path, nb)
    code, output = _run(valid_root, "hygiene-check", capsys)
    assert code == 1
    assert "is executed" in output
    assert output.count("FAIL:") == 1


@pytest.mark.parametrize(
    "heading",
    ["Prior student text.\n## Solution", "Prior student text.\n#Solution"],
)
def test_hygiene_solution_heading_one_fault(valid_root, capsys, heading):
    path, nb = _notebook(valid_root, "exercises.ipynb")
    nb.cells.append(nbformat.v4.new_markdown_cell(heading))
    _write_nb(path, nb)
    code, output = _run(valid_root, "hygiene-check", capsys)
    assert code == 1
    assert output == "FAIL: unit-01-story-machine: exercises contain a solution heading\n"


def test_noexec_opening_one_fault(valid_root, capsys):
    path, nb = _notebook(valid_root, "lesson.ipynb")
    nb.cells[0] = nbformat.v4.new_code_cell("x = 1")
    _write_nb(path, nb)
    code, output = _run(valid_root, "noexec-check", capsys)
    assert code == 1
    assert "lesson must open with non-empty markdown" in output
    assert output.count("FAIL:") == 1


def test_noexec_empty_lesson_one_fault(valid_root, capsys):
    path, nb = _notebook(valid_root, "lesson.ipynb")
    nb.cells = []
    _write_nb(path, nb)
    code, output = _run(valid_root, "noexec-check", capsys)
    assert code == 1
    assert output == "FAIL: unit-01-story-machine: lesson is empty\n"


def test_noexec_empty_first_markdown_one_fault(valid_root, capsys):
    path, nb = _notebook(valid_root, "lesson.ipynb")
    nb.cells[0].source = ""
    _write_nb(path, nb)
    code, output = _run(valid_root, "noexec-check", capsys)
    assert code == 1
    assert "lesson must open with non-empty markdown" in output
    assert output.count("FAIL:") == 1


@pytest.mark.parametrize(
    "source",
    [
        "input ('name? ')",
        "value = 1\nimport tkinter",
        "if True:\n    from  turtle   import Turtle",
    ],
)
def test_noexec_tag_one_fault(valid_root, capsys, source):
    path, nb = _notebook(valid_root, "lesson.ipynb")
    nb.cells.append(nbformat.v4.new_code_cell(source))
    _write_nb(path, nb)
    code, output = _run(valid_root, "noexec-check", capsys)
    assert code == 1
    assert output == (
        "FAIL: unit-01-story-machine: lesson code cell 3 is interactive/GUI but not no-exec\n"
    )


def test_input_identifier_is_not_treated_as_input_call(valid_root, capsys):
    _add_solution_code(
        valid_root,
        "def myinput():\n    return 'safe'\n\nanswer = myinput()",
    )
    code, output = _run(valid_root, "structure-check", capsys)
    assert code == 0, output


def test_cell_lint_one_fault_and_noexec_exemption(valid_root, capsys):
    path, nb = _notebook(valid_root, "lesson.ipynb")
    nb.cells.append(nbformat.v4.new_code_cell("print(undefined_lint_name)"))
    nb.cells.append(
        nbformat.v4.new_code_cell("print(undefined_teacher_demo)", metadata={"tags": ["no-exec"]})
    )
    _write_nb(path, nb)
    code, output = _run(valid_root, "cell-lint", capsys)
    assert code == 1
    assert "undefined_lint_name" in output
    assert "undefined_teacher_demo" not in output
    assert "lesson.ipynb cell" in output


def test_cell_lint_ignores_magic_lines(valid_root, capsys):
    path, nb = _notebook(valid_root, "lesson.ipynb")
    nb.cells.append(nbformat.v4.new_code_cell("%time value\n!echo classroom\nassert value == 1"))
    _write_nb(path, nb)
    code, output = _run(valid_root, "cell-lint", capsys)
    assert code == 0, output


def test_cell_lint_checks_syntax_before_cells_are_concatenated(valid_root, capsys):
    path, nb = _notebook(valid_root, "lesson.ipynb")
    nb.cells.append(nbformat.v4.new_code_cell("repaired_only_by_concat = ("))
    nb.cells.append(nbformat.v4.new_code_cell("1)"))
    _write_nb(path, nb)
    code, output = _run(valid_root, "cell-lint", capsys)
    assert code == 1
    assert "lesson.ipynb cell 4: syntax error" in output
    assert "lesson.ipynb cell 5: syntax error" in output
    assert output.count("FAIL:") == 2


def test_exec_solutions_one_fault(valid_root, capsys):
    _add_solution_code(valid_root, "assert False, 'fixture failure'")
    code, output = _run(valid_root, "exec-solutions", capsys)
    assert code == 1
    assert "solutions.ipynb execution failed" in output
    assert "fixture failure" in output


def test_exec_lessons_drops_noexec_and_exposes_dependency(valid_root, capsys):
    path, nb = _notebook(valid_root, "lesson.ipynb")
    nb.cells.append(nbformat.v4.new_code_cell("teacher_state = 3", metadata={"tags": ["no-exec"]}))
    nb.cells.append(nbformat.v4.new_code_cell("assert teacher_state == 3"))
    _write_nb(path, nb)
    code, output = _run(valid_root, "exec-lessons", capsys)
    assert code == 1
    assert "lesson.ipynb execution failed" in output
    assert "teacher_state" in output


def _turtle_script(root, source):
    (_unit(root) / "assets/closed.py").write_text(source, encoding="utf-8")


TURTLE_CASES = [
    ("closure", "import turtle\nturtle.forward(10)\n", "path does not close"),
    (
        "heading-closure",
        "import turtle\nturtle.forward(10)\nturtle.backward(10)\nturtle.right(45)\n",
        "path does not close",
    ),
    (
        "pen-down",
        "# turtle-check: open-path\nimport turtle\nturtle.penup()\nturtle.forward(10)\n",
        "no pen-down move",
    ),
    (
        "move-bound",
        "# turtle-check: open-path\nimport turtle\nfor _ in range(10000):\n    turtle.forward(1)\n",
        "10000 moves (must be <10000)",
    ),
]
# A 20-second sleep fixture is intentionally omitted; the real subprocess enforces the timeout.


@pytest.mark.parametrize("_name,source,expected", TURTLE_CASES)
def test_turtle_one_fault(valid_root, capsys, _name, source, expected):
    _turtle_script(valid_root, source)
    code, output = _run(valid_root, "turtle-check", capsys)
    assert code == 1
    assert expected in output
    assert output.count("FAIL:") == 1


def test_turtle_open_path_waives_only_closure(valid_root, capsys):
    _turtle_script(
        valid_root,
        "# turtle-check: open-path\nimport turtle\nturtle.forward(10)\nturtle.right(45)\n",
    )
    code, output = _run(valid_root, "turtle-check", capsys)
    assert code == 0
    assert output == "turtle-check: PASS\n"


def test_turtle_open_path_does_not_waive_pen_floor(valid_root, capsys):
    _turtle_script(
        valid_root,
        "# turtle-check: open-path\nimport turtle\nturtle.penup()\nturtle.forward(10)\n",
    )
    code, output = _run(valid_root, "turtle-check", capsys)
    assert code == 1
    assert output.count("FAIL:") == 1
    assert "no pen-down move" in output


def test_turtle_open_path_text_inside_string_does_not_waive_closure(valid_root, capsys):
    _turtle_script(
        valid_root,
        'import turtle\nmarker = "# turtle-check: open-path"\nturtle.forward(10)\n',
    )
    code, output = _run(valid_root, "turtle-check", capsys)
    assert code == 1
    assert output.count("FAIL:") == 1
    assert "path does not close" in output


def _coverage_version(root, key):
    path = root / f"book1/curriculum/{key}.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["concepts_version" if key == "concepts" else "map_version"] = 2
    _write_yaml(path, data)


def _few_concepts(root):
    path, data = _concepts(root)
    data["concepts"] = data["concepts"][:39]
    _write_yaml(path, data)


def _concept_mutation(root, mutation):
    path, data = _concepts(root)
    mutation(data["concepts"])
    _write_yaml(path, data)


def _map_mutation(root, mutation):
    path, data = _map(root)
    mutation(data["entries"])
    _write_yaml(path, data)


def _replace_concept_id(root, replacement):
    concepts_path, concepts = _concepts(root)
    old = concepts["concepts"][1]["id"]
    concepts["concepts"][1]["id"] = replacement
    _write_yaml(concepts_path, concepts)
    map_path, coverage = _map(root)
    for entry in coverage["entries"]:
        for field in ("introduces", "requires", "practices"):
            entry[field] = [replacement if value == old else value for value in entry[field]]
    _write_yaml(map_path, coverage)


def _remove_precapstone_practice(root):
    path, data = _map(root)
    for entry in data["entries"]:
        if entry["id"] != "project-02-grand-adventure":
            entry["practices"] = [
                concept for concept in entry["practices"] if concept != "concept-00"
            ]
    _write_yaml(path, data)


def _break_first_syllabus_row(root):
    path = root / "book1/syllabus.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("| unit | 3 |", "| unit | 9 |", 1), encoding="utf-8")


def _duplicate_field(root, field):
    path, data = _map(root)
    entry = data["entries"][1]
    entry[field].append(entry[field][0])
    _write_yaml(path, data)


MALFORMED_CURRICULUM_CASES = [
    ("concepts.yaml", "null\n", "concepts.yaml must be a mapping"),
    (
        "concepts.yaml",
        "concepts_version: 1\nconcepts: null\n",
        "concepts must be a list",
    ),
    (
        "concepts.yaml",
        "concepts_version: 1\nconcepts: [null]\n",
        "concept entry 0 must be a mapping",
    ),
    ("coverage-map.yaml", "null\n", "coverage-map.yaml must be a mapping"),
    (
        "coverage-map.yaml",
        "map_version: 1\nentries: null\n",
        "coverage-map entries must be a list",
    ),
    (
        "coverage-map.yaml",
        "map_version: 1\nentries: [null]\n",
        "coverage-map entry 0 must be a mapping",
    ),
]


@pytest.mark.parametrize("filename,source,expected", MALFORMED_CURRICULUM_CASES)
def test_malformed_curriculum_types_return_findings(
    valid_root, capsys, filename, source, expected
):
    path = valid_root / "book1/curriculum" / filename
    path.write_text(source, encoding="utf-8")
    code, output = _run(valid_root, "coverage-check", capsys)
    assert code == 1
    assert output == f"FAIL: book1: {expected}\n"


def _invalid_lessons(root, value):
    path, data = _map(root)
    data["entries"][0]["lessons"] = value
    if isinstance(value, (int, float)):
        data["entries"][-1]["lessons"] += 3 - value
    _write_yaml(path, data)


def _introduce_twice(root):
    path, data = _map(root)
    repeated = data["entries"][0]["introduces"][0]
    data["entries"][1]["introduces"].append(repeated)
    data["entries"][1]["practices"].remove(repeated)
    _write_yaml(path, data)


def _never_introduce(root):
    path, data = _map(root)
    removed = data["entries"][0]["introduces"].pop()
    checkpoint = next(entry for entry in data["entries"] if entry["kind"] == "checkpoint")
    checkpoint["practices"].remove(removed)
    _write_yaml(path, data)


COVERAGE_CASES = [
    ("concept-version", lambda r: _coverage_version(r, "concepts"), "concepts_version must be 1"),
    ("concept-count", _few_concepts, "concept registry has fewer than 40 concepts"),
    (
        "concept-ids",
        lambda r: _concept_mutation(r, lambda cs: cs.append(copy.deepcopy(cs[0]))),
        "duplicate concept ids",
    ),
    (
        "concept-keys",
        lambda r: _concept_mutation(r, lambda cs: cs[0].update(extra=True)),
        "bad concept keys",
    ),
    (
        "concept-category",
        lambda r: _concept_mutation(r, lambda cs: cs[0].update(category="unknown")),
        "unknown category",
    ),
    ("concept-kebab", lambda r: _replace_concept_id(r, "Not Kebab"), "non-kebab concept id"),
    ("map-version", lambda r: _coverage_version(r, "coverage-map"), "map_version must be 1"),
    (
        "map-duplicate",
        lambda r: _map_mutation(r, lambda es: es[1].update(id=es[0]["id"])),
        "duplicate entry ids",
    ),
    ("map-keys", lambda r: _map_mutation(r, lambda es: es[0].update(extra=True)), "bad entry keys"),
    ("map-id", lambda r: _map_mutation(r, lambda es: es[0].update(id="bad")), "bad entry id"),
    (
        "map-kind",
        lambda r: _map_mutation(r, lambda es: es[0].update(kind="lesson")),
        "bad entry id",
    ),
    (
        "map-lessons",
        lambda r: _invalid_lessons(r, 0),
        "lessons must be positive",
    ),
    (
        "map-lessons-type",
        lambda r: _invalid_lessons(r, "three"),
        "lessons must be positive",
    ),
    ("budget", lambda r: _map_mutation(r, lambda es: es[0].update(lessons=20)), "lesson budget"),
    (
        "unknown-introduces",
        lambda r: _map_mutation(r, lambda es: es[0]["introduces"].append("unknown")),
        "introduces references unknown concepts",
    ),
    (
        "unknown-requires",
        lambda r: _map_mutation(r, lambda es: es[1]["requires"].append("unknown")),
        "requires references unknown concepts",
    ),
    (
        "unknown-practices",
        lambda r: _map_mutation(r, lambda es: es[-1]["practices"].append("unknown")),
        "practices references unknown concepts",
    ),
    (
        "introduced-twice",
        _introduce_twice,
        "concept introduced twice",
    ),
    (
        "never-introduced",
        _never_introduce,
        "never introduced",
    ),
    (
        "own-practice",
        lambda r: _map_mutation(r, lambda es: es[0]["practices"].append(es[0]["introduces"][0])),
        "practices its own introductions",
    ),
    (
        "introduces-duplicates",
        lambda r: _duplicate_field(r, "introduces"),
        "introduces has duplicates",
    ),
    ("requires-duplicates", lambda r: _duplicate_field(r, "requires"), "requires has duplicates"),
    (
        "practices-duplicates",
        lambda r: _duplicate_field(r, "practices"),
        "practices has duplicates",
    ),
    ("pre-capstone", _remove_precapstone_practice, "only the capstone practices"),
    ("syllabus-row", _break_first_syllabus_row, "syllabus table missing/incorrect row"),
    (
        "syllabus-extra",
        lambda r: (r / "book1/syllabus.md").write_text(
            (r / "book1/syllabus.md").read_text(encoding="utf-8")
            + "\n| 17 | `unit-99-extra` | unit | 1 | Extra |\n",
            encoding="utf-8",
        ),
        "stale/extra syllabus rows",
    ),
]


@pytest.mark.parametrize("_name,mutate,expected", COVERAGE_CASES)
def test_coverage_one_fault(valid_root, capsys, _name, mutate, expected):
    mutate(valid_root)
    code, output = _run(valid_root, "coverage-check", capsys)
    assert code == 1
    assert expected in output
    expected_count = 2 if _name in {"introduces-duplicates", "unknown-introduces"} else 1
    assert output.count("FAIL:") == expected_count
    if _name == "unknown-introduces":
        assert "never introduced: []" in output
    if _name == "introduces-duplicates":
        assert "concept introduced twice" in output


def test_syllabus_order_one_fault(valid_root, capsys):
    path = valid_root / "book1/syllabus.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    lines[0], lines[1] = lines[1], lines[0]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    code, output = _run(valid_root, "coverage-check", capsys)
    assert code == 1
    assert "syllabus table order differs" in output


def test_checkpoint_introduces_one_fault(valid_root, capsys):
    path, data = _map(valid_root)
    last_unit = next(entry for entry in data["entries"] if entry["id"] == "unit-08-fixture")
    checkpoint = next(entry for entry in data["entries"] if entry["kind"] == "checkpoint")
    moved = last_unit["introduces"].pop()
    checkpoint["introduces"].append(moved)
    checkpoint["practices"].remove(moved)
    data["entries"][1]["practices"].append(moved)
    _write_yaml(path, data)
    code, output = _run(valid_root, "coverage-check", capsys)
    assert code == 1
    assert output == "FAIL: book1: checkpoint-01-fixture introduces concepts\n"


def test_checkpoint_assesses_untaught_one_fault(valid_root, capsys):
    path, data = _map(valid_root)
    checkpoint = data["entries"].pop(-2)
    data["entries"].insert(1, checkpoint)
    _write_yaml(path, data)
    code, output = _run(valid_root, "coverage-check", capsys)
    assert code == 1
    assert output.count("FAIL:") == 1
    assert "checkpoint-01-fixture assesses untaught concepts" in output


def test_stretch_floor_has_bound_cli_home(valid_root, capsys):
    _stretch_floor(valid_root)
    code, output = _run(valid_root, "stretch-check", capsys)
    assert code == 1
    assert output == "FAIL: unit-01-story-machine: 0 stretch-tagged cells (<2)\n"


def test_bool_lessons_preserves_legacy_numeric_contract(valid_root):
    path, data = _map(valid_root)
    data["entries"][0]["lessons"] = True
    _write_yaml(path, data)
    assert map_schema_findings(valid_root, "book1") == []


def test_unit_narrowing_accepts_existing_unit(valid_root, capsys):
    code, output = _run(valid_root, "structure-check", capsys, unit="unit-01-story-machine")
    assert code == 0
    assert output == "structure-check: PASS\n"


def test_prereq_closure_one_fault(valid_root, capsys):
    path, data = _map(valid_root)
    data["entries"][0]["requires"].append("concept-00")
    _write_yaml(path, data)
    code, output = _run(valid_root, "prereq-check", capsys)
    assert code == 1
    assert output == (
        "FAIL: book1: unit-01-story-machine uses concepts not yet introduced: ['concept-00']\n"
    )


def test_practice_closure_one_fault(valid_root, capsys):
    path, data = _map(valid_root)
    data["entries"][0]["practices"].append("concept-00")
    _write_yaml(path, data)
    code, output = _run(valid_root, "prereq-check", capsys)
    assert code == 1
    assert output == (
        "FAIL: book1: unit-01-story-machine uses concepts not yet introduced: ['concept-00']\n"
    )


def test_unit_narrowing(valid_root, capsys):
    _remove_required(valid_root, "teacher-notes.md")
    code, output = _run(valid_root, "structure-check", capsys, unit="unit-99-absent")
    assert code == 1
    assert output == "FAIL: unit-99-absent: unit directory does not exist\n"


def test_ci_local_has_exact_six_real_steps():
    text = (REPO / "scripts/ci-local.sh").read_text(encoding="utf-8")
    assert text.count('step "') == 6
    assert "SKIP (plan" not in text
    assert "export PY4KIDS_CI=1" in text
    commands = [
        "hygiene-check",
        "structure-check",
        "noexec-check",
        "cell-lint",
        "exec-solutions",
        "exec-lessons",
        "manifest-check",
        "prereq-check",
        "coverage-check",
        "stretch-check",
        "turtle-check",
    ]
    positions = [text.index(command) for command in commands]
    assert positions == sorted(positions)
    assert "bash scripts/build-pdf.sh --book book1" in text


def test_pdf_builder_contract():
    text = (REPO / "scripts/build-pdf.sh").read_text(encoding="utf-8")
    config = text.index("JUPYTER_CONFIG_DIR")
    convert = text.index("jupyter nbconvert")
    assert config < convert
    assert "mktemp -d" in text
    assert '--output "$unit_id"' in text
    assert "--pdf-engine=xelatex" in text
    assert "build/handouts" in text
