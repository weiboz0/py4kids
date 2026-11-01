"""``lab-check`` and the lab exclusion pin (plan roar-002 Phase 0; design 013 §7.2).

Group-free: the fixture labs are tiny stdlib-only notebooks and a two-row CSV.
"""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import nbformat
import pytest
import yaml
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook
from publication_helpers import write_publication_config

from tools import publish
from tools.export import answers
from tools.export.bundle import export_book
from tools.labs import lab_findings
from tools.notebooks import FLAGGED_MANIFEST_KEYS, MANIFEST_KEYS, manifest_findings

REPO = Path(__file__).resolve().parents[1]
UNIT = "unit-01-race"
PARAMETERS = 'import os\nTELEMETRY_PATH = os.environ.get("ROAR_LAB_CSV", "telemetry.csv")\n'
SETUP = "import carla\nclient = carla.Client('localhost', 2000)\n"
RECORDER = (
    "with open(TELEMETRY_PATH, \"w\") as handle:\n"
    "    handle.write('t,v\\n')\n"
    "with open(TELEMETRY_PATH, 'a') as handle:\n"
    "    handle.write('0.05,1.0\\n')\n"
)
ANALYSIS = (
    "import csv\n"
    "with open(TELEMETRY_PATH, newline='') as handle:\n"
    "    rows = list(csv.reader(handle))\n"
    "assert rows[0] == ['t', 'v'] and len(rows) == 3\n"
)


def _code(source, *cell_tags):
    cell = new_code_cell(source)
    if cell_tags:
        cell.metadata["tags"] = list(cell_tags)
    return cell


def default_cells():
    return [
        new_markdown_cell("# Lab: the real simulator\n\nInstall CARLA; `subprocess` runs the race."),
        _code(PARAMETERS, "parameters"),
        _code(SETUP, "no-exec"),
        _code(RECORDER, "no-exec"),
        _code(ANALYSIS),
    ]


def write_lab(root: Path, cells, book: str = "labbook", unit: str = UNIT) -> Path:
    path = root / book / "units" / unit / "labs" / "real-sim.ipynb"
    path.parent.mkdir(parents=True, exist_ok=True)
    notebook = new_notebook(cells=cells)
    notebook.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nbformat.write(notebook, path)
    return path


def write_manifest(root: Path, book: str, unit: str = UNIT, **extra) -> None:
    unit_dir = root / book / "units" / unit
    unit_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"id": unit, "kind": "unit", "blueprint_version": 1, "lessons": 3,
                "concepts": {"introduces": [], "requires": [], "practices": []},
                "provenance": "original", **extra}
    (unit_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")


@pytest.fixture
def lab_root(tmp_path):
    """A registry with a `labs` book holding one passing lab, and a book without the flag."""
    (tmp_path / "books.yaml").write_text(yaml.safe_dump({"books_version": 2, "books": [
        {"id": "labbook", "number": 1, "root": "labbook", "title": "L", "subtitle": "l",
         "depends_on": [], "labs": True},
        {"id": "plain", "number": 2, "root": "plain", "title": "P", "subtitle": "p", "depends_on": []},
    ]}), encoding="utf-8")
    for book in ("labbook", "plain"):
        curriculum = tmp_path / book / "curriculum"
        curriculum.mkdir(parents=True)
        (curriculum / "coverage-map.yaml").write_text("map_version: 1\nentries: []\n", encoding="utf-8")
    sample = tmp_path / "data" / "generated" / "sample.csv"
    sample.parent.mkdir(parents=True)
    sample.write_text("t,v\n0.05,1.0\n0.10,2.0\n", encoding="utf-8")
    (tmp_path / "labbook" / "curriculum" / "labs.yaml").write_text(
        "sample_csv: data/generated/sample.csv\n", encoding="utf-8")
    write_manifest(tmp_path, "labbook", lab=True)
    write_lab(tmp_path, default_cells())
    (tmp_path / "plain" / "units").mkdir()
    return tmp_path


def test_a_passing_lab_executes_against_the_sample(lab_root):
    assert lab_findings(lab_root, "labbook") == []
    # the executed copy never touches the source notebook
    notebook = nbformat.read(lab_root / "labbook/units" / UNIT / "labs/real-sim.ipynb", as_version=4)
    assert all(cell.execution_count is None for cell in notebook.cells if cell.cell_type == "code")


def test_a_book_without_labs_passes_and_the_real_registry_flags_roar():
    assert lab_findings(REPO, "python-projects") == []
    assert yaml.safe_load((REPO / "books.yaml").read_text(encoding="utf-8"))["books"][-1]["labs"] is True


def test_a_missing_lab_fails(lab_root):
    (lab_root / "labbook/units" / UNIT / "labs/real-sim.ipynb").unlink()
    assert lab_findings(lab_root, "labbook") == [
        f"FAIL: {UNIT}: manifest lab: true but labs/real-sim.ipynb does not exist"]


@pytest.mark.parametrize("parameters", [
    _code(PARAMETERS),  # untagged
    _code('import os\nTELEMETRY_PATH = os.environ.get("ROAR_LAB_CSV", "other.csv")\n', "parameters"),
    _code("TELEMETRY_PATH = 'x'\n", "parameters"),
    # the right expression, then reassigned ([sol] S2): exactly one assignment is allowed
    _code(PARAMETERS + "TELEMETRY_PATH = 'mine.txt'\n", "parameters"),
    _code(PARAMETERS + "TELEMETRY_PATH += '.bak'\n", "parameters"),
    _code(PARAMETERS + "TELEMETRY_PATH, other = 'mine.txt', 1\n", "parameters"),
    _code(PARAMETERS + "if True:\n    TELEMETRY_PATH: str = 'mine.txt'\n", "parameters"),
])
def test_a_missing_parameters_cell_fails(lab_root, parameters):
    cells = default_cells()
    cells[1] = parameters
    write_lab(lab_root, cells)
    findings = lab_findings(lab_root, "labbook")
    assert any("first code cell must be tagged 'parameters'" in finding for finding in findings), findings


def test_a_lab_without_any_parameters_cell_fails(lab_root):
    cells = default_cells()
    del cells[1]
    write_lab(lab_root, cells)
    findings = lab_findings(lab_root, "labbook")
    assert any("first code cell must be tagged 'parameters'" in finding for finding in findings), findings


@pytest.mark.parametrize("source", [
    "TELEMETRY_PATH = 'mine.txt'\n",
    "TELEMETRY_PATH += '.bak'\n",
    "TELEMETRY_PATH: str = 'mine.txt'\n",
    "other, TELEMETRY_PATH = 1, 'mine.txt'\n",
    "[TELEMETRY_PATH, *rest] = ['mine.txt', 2]\n",
    "def where():\n    TELEMETRY_PATH = 'mine.txt'\n    return TELEMETRY_PATH\n",
    "print(TELEMETRY_PATH := 'mine.txt')\n",
])
def test_assigning_telemetry_path_outside_the_parameters_cell_fails(lab_root, source):
    write_lab(lab_root, [*default_cells(), _code(source)])
    findings = lab_findings(lab_root, "labbook")
    assert findings == [(f"FAIL: {UNIT}: lab code cell 4 assigns TELEMETRY_PATH (only the parameters cell may "
                         "set it)")]


def test_reading_telemetry_path_in_other_cells_passes(lab_root):
    write_lab(lab_root, [*default_cells(), _code("name = TELEMETRY_PATH\nprint(name, TELEMETRY_PATH)\n")])
    assert lab_findings(lab_root, "labbook") == []


@pytest.mark.parametrize("source", [
    "import csv\nrows = list(csv.reader(open('telemetry.csv')))\n",
    "path = f'runs/{1}.csv'\n",
])
def test_a_hard_coded_csv_path_fails(lab_root, source):
    write_lab(lab_root, [*default_cells(), _code(source)])
    findings = lab_findings(lab_root, "labbook")
    assert findings == [(f"FAIL: {UNIT}: lab code cell 4 hard-codes a .csv path (use TELEMETRY_PATH from the "
                         "parameters cell)")]


@pytest.mark.parametrize("source", [
    SETUP,
    "import roar_py_carla\n",
    "import subprocess\nsubprocess.run(['python', 'competition_runner.py'])\n",
    "from racekit.cars import carla_like\nimport carla\n",
])
def test_an_untagged_simulator_code_cell_fails(lab_root, source):
    write_lab(lab_root, [*default_cells(), _code(source)])
    findings = lab_findings(lab_root, "labbook")
    assert findings == [(f"FAIL: {UNIT}: lab code cell 4 uses the simulator (carla / competition_runner / "
                         "subprocess) but is not no-exec")]


def test_racekit_carla_like_is_not_the_simulator(lab_root):
    source = "from racekit.cars import carla_like\ncar = carla_like(noise=True)\n"
    lab = write_lab(lab_root, [*default_cells(), _code(source)])
    # racekit is in the roar group only, and this suite is group-free (plan 107). The lab kernel
    # runs in the lab's directory (_execute_lab's resources.metadata.path), so this stand-in
    # resolves first and shadows any installed racekit: the test is about the checker, not racekit.
    stand_in = lab.parent / "racekit"
    stand_in.mkdir()
    (stand_in / "__init__.py").write_text("", encoding="utf-8")
    (stand_in / "cars.py").write_text("def carla_like(noise=False):\n    return noise\n",
                                      encoding="utf-8")
    assert lab_findings(lab_root, "labbook") == []


@pytest.mark.parametrize(("source", "detail"), [
    ("data = open(TELEMETRY_PATH).read()\n", "open() without a mode reads"),
    ("handle = open(TELEMETRY_PATH, 'r')\n", "open() mode 'r' reads"),
    ("handle = open(TELEMETRY_PATH, mode='r+')\n", "open() mode 'r+' reads"),
    ("handle = open(TELEMETRY_PATH, 'w+')\n", "open() mode 'w+' reads"),
    ("handle = open(TELEMETRY_PATH, 'rb')\n", "open() mode 'rb' reads"),
    ("mode = 'w'\nhandle = open(TELEMETRY_PATH, mode)\n", "open() mode is not a literal, so it may read"),
    ("from pathlib import Path\nhandle = Path(TELEMETRY_PATH).open()\n", "open() without a mode reads"),
    ("import io\nhandle = io.open(TELEMETRY_PATH, 'r')\n", "open() mode 'r' reads"),
    ("import pandas\nframe = pandas.read_csv(TELEMETRY_PATH)\n", "read_csv() reads a CSV"),
    ("from racekit.telemetry import read_csv\ntelemetry, meta = read_csv(TELEMETRY_PATH)\n",
     "read_csv() reads a CSV"),
    ("import numpy\nrows = numpy.load_csv(TELEMETRY_PATH)\n", "load_csv() reads a CSV"),
])
def test_a_read_in_a_no_exec_cell_fails(lab_root, source, detail):
    write_lab(lab_root, [*default_cells(), _code(source, "no-exec")])
    assert lab_findings(lab_root, "labbook") == [
        f"FAIL: {UNIT}: lab code cell 4 is no-exec and must only write: {detail}"]


@pytest.mark.parametrize("source", [
    "handle = open(TELEMETRY_PATH, 'x')\n",
    "handle = open(TELEMETRY_PATH, mode='ab')\n",
    "from pathlib import Path\nhandle = Path(TELEMETRY_PATH).open('w')\n",
])
def test_write_only_opens_in_a_no_exec_cell_pass(lab_root, source):
    write_lab(lab_root, [*default_cells(), _code(source, "no-exec")])
    assert lab_findings(lab_root, "labbook") == []


def test_markdown_mentions_are_exempt_and_outputs_fail(lab_root):
    cells = default_cells()
    cells.append(new_markdown_cell("Run `competition_runner.py`; read `results.csv` with `read_csv`."))
    write_lab(lab_root, cells)
    assert lab_findings(lab_root, "labbook") == []
    cells[4].outputs = [nbformat.v4.new_output("stream", name="stdout", text="hi\n")]
    cells[4].execution_count = 3
    write_lab(lab_root, cells)
    assert lab_findings(lab_root, "labbook") == [
        f"FAIL: {UNIT}: lab code cell 3 has outputs", f"FAIL: {UNIT}: lab code cell 3 is executed"]


def test_a_failing_analysis_cell_fails_execution(lab_root):
    write_lab(lab_root, [*default_cells(), _code("assert False, 'boom'\n")])
    findings = lab_findings(lab_root, "labbook")
    assert len(findings) == 1 and "real-sim.ipynb execution failed" in findings[0], findings


def test_a_missing_sample_or_config_fails(lab_root):
    (lab_root / "data/generated/sample.csv").unlink()
    findings = lab_findings(lab_root, "labbook")
    assert len(findings) == 1 and "sample_csv data/generated/sample.csv does not exist" in findings[0]
    (lab_root / "labbook/curriculum/labs.yaml").write_text("sample: x.csv\n", encoding="utf-8")
    assert lab_findings(lab_root, "labbook") == [
        "FAIL: labbook/labs.yaml: must be a mapping with exactly one key, sample_csv (a path)"]


def test_a_stray_labs_directory_fails(lab_root):
    write_manifest(lab_root, "labbook", unit="unit-02-extra")
    write_lab(lab_root, default_cells(), unit="unit-02-extra")
    assert lab_findings(lab_root, "labbook") == [
        "FAIL: unit-02-extra: a labs/ directory without manifest lab: true"]
    write_manifest(lab_root, "plain")
    (lab_root / "plain/units" / UNIT / "labs").mkdir()
    assert lab_findings(lab_root, "plain") == [f"FAIL: {UNIT}: a labs/ directory without manifest lab: true"]


def test_lab_true_in_a_book_without_the_flag_fails(lab_root):
    write_manifest(lab_root, "plain", lab=True)
    write_lab(lab_root, default_cells(), book="plain")
    assert lab_findings(lab_root, "plain") == [f"FAIL: {UNIT}: manifest lab: true needs the 'labs' book flag"]
    # manifest-check refuses the key outside a `labs` book, and accepts it in one
    assert FLAGGED_MANIFEST_KEYS["lab"] == "labs" and "lab" not in MANIFEST_KEYS
    message = f"FAIL: {UNIT}: manifest key 'lab' is only allowed in books with the 'labs' flag"
    assert manifest_findings(lab_root, "plain", UNIT) == [message]
    assert message not in manifest_findings(lab_root, "labbook", UNIT)


def test_a_non_boolean_lab_key_fails(lab_root):
    write_manifest(lab_root, "labbook", lab="yes")
    assert lab_findings(lab_root, "labbook") == [f"FAIL: {UNIT}: manifest lab must be true or false"]


# --- the exclusion pin ---------------------------------------------------------------------------
# Publish and export read named top-level notebooks only (lesson / exercises / checkpoint / brief /
# solutions). The pin turns `publication` and `site` on for a fixture book whose unit has a TRACKED
# `labs/real-sim.ipynb`, and proves neither pipeline ever opens or ships it, so it survives the
# flags being turned on for a labs book later.

_spec = importlib.util.spec_from_file_location(
    "site_demo_book_labs", Path(__file__).parent / "fixtures" / "site" / "demo_book.py")
demo_book = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(demo_book)


def test_a_lab_notebook_is_never_collected_by_publish_or_export(tmp_path, monkeypatch):
    answers.clear_caches()
    root = demo_book.build_site_root(tmp_path / "root")
    registry = root / "books.yaml"
    registry.write_text(registry.read_text(encoding="utf-8") + "  publication: true\n  labs: true\n",
                        encoding="utf-8")
    unit_dir = root / "demo" / "units" / "unit-01-demo"
    lab = write_lab(root, default_cells(), book="demo", unit="unit-01-demo")
    # what the publication pipeline needs to run: its config, the setup chapter and teacher notes
    write_publication_config(root / "demo")
    (root / "demo" / "docs").mkdir()
    for name in ("unit-00-getting-set-up.md", "unit-00-teacher-notes.md"):
        (root / "demo" / "docs" / name).write_text("# Getting set up\n", encoding="utf-8")
    (unit_dir / "teacher-notes.md").write_text("## Goals\n\n- Race.\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    assert lab.is_file()

    opened: list[Path] = []
    real_read = nbformat.read

    def recording_read(path, *args, **kwargs):
        opened.append(Path(path).resolve())
        return real_read(path, *args, **kwargs)

    monkeypatch.setattr(nbformat, "read", recording_read)

    # publish: the entry list holds entry folders only, and a lab is never a student-family source
    book = root / "demo"
    for edition in publish.EDITIONS:
        listed = publish.entries(book, edition)
        assert [path for _, path in listed if "labs" in path.parts] == []
        if publish.profile(edition)["student_family"]:
            assert not publish.allowed_source(lab, edition), edition
        if publish.profile(edition)["body"] == "answers":
            publish.render_answer_chapter(unit_dir, edition, mainmatter=True)
        else:
            publish.render_chapter(unit_dir, "unit", edition)

    # export: the whole bundle
    result = export_book(root, "demo", tmp_path / "bundle")
    assert result is not None
    shipped = [path for path in (tmp_path / "bundle").rglob("*") if path.is_file()]
    assert shipped and not any("real-sim" in path.name or "labs" in path.parts for path in shipped)
    assert not any(b"real-sim" in path.read_bytes() for path in shipped)

    # non-vacuous: both pipelines did open the unit's own notebooks
    assert (unit_dir / "lesson.ipynb").resolve() in opened
    assert (unit_dir / "exercises.ipynb").resolve() in opened
    assert lab.resolve() not in opened
    assert not any("labs" in path.parts for path in opened)
