import py_compile
import re
from pathlib import Path

import nbformat
import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
UNITS_ROOT = REPO / "book1" / "units"
UNIT_DIRS = sorted(d for d in UNITS_ROOT.glob("unit-*") if d.is_dir())

if not UNIT_DIRS:
    pytest.skip("no unit directories yet (pre-content)", allow_module_level=True)

REQUIRED_FILES = ("manifest.yaml", "lesson.ipynb", "exercises.ipynb",
                  "solutions.ipynb", "teacher-notes.md")
MANIFEST_KEYS = {"id", "kind", "blueprint_version", "lessons", "concepts", "provenance"}
NOTES_HEADINGS = ("## Goals", "## Pacing", "## Common mistakes",
                  "## Discussion prompts", "## Differentiation")
PLAN_004_UNITS = ("unit-01-story-machine", "unit-02-number-detective",
                  "unit-03-turtle-art-studio")

# Mechanical patterns (plan 004 Global Constraints): matched per line of code-cell source.
INTERACTIVE = re.compile(r"\binput\s*\(")
GUI_IMPORT = re.compile(r"^\s*(import|from)\s+(turtle|tkinter)\b", re.MULTILINE)
RANDOM_FROM_IMPORT = re.compile(r"^\s*from\s+random\s+import\b", re.MULTILINE)
EXERCISE_HEADING = re.compile(r"^## Exercise \d+", re.MULTILINE)
ASSET_REF = re.compile(r"assets/[\w.-]+\.py")


def load_map_entry(unit_id):
    data = yaml.safe_load(
        (REPO / "book1" / "curriculum" / "coverage-map.yaml").read_text(encoding="utf-8")
    )
    matches = [e for e in data["entries"] if e["id"] == unit_id]
    assert matches, f"{unit_id} not in coverage map"
    return matches[0]


def read_nb(path):
    return nbformat.read(path, as_version=4)


def code_cells(nb):
    return [c for c in nb.cells if c.cell_type == "code"]


def tags(cell):
    return cell.get("metadata", {}).get("tags", [])


@pytest.fixture(params=UNIT_DIRS, ids=lambda d: d.name)
def unit_dir(request):
    return request.param


def test_layout(unit_dir):
    for name in REQUIRED_FILES:
        assert (unit_dir / name).is_file(), f"{unit_dir.name} missing {name}"
    manifest = yaml.safe_load((unit_dir / "manifest.yaml").read_text(encoding="utf-8"))
    if "turtle-basics" in manifest["concepts"]["introduces"]:
        assets = unit_dir / "assets"
        assert assets.is_dir(), f"{unit_dir.name} introduces turtle but has no assets/"
        referenced = set()
        for nb_name in ("lesson.ipynb", "exercises.ipynb", "solutions.ipynb"):
            for cell in read_nb(unit_dir / nb_name).cells:
                referenced.update(ASSET_REF.findall(cell.source))
        for ref in sorted(referenced):
            assert (unit_dir / ref).is_file(), f"{unit_dir.name} references missing {ref}"
        for script in sorted(assets.glob("*.py")):
            py_compile.compile(str(script), doraise=True)


def test_manifest_schema_and_map_agreement(unit_dir):
    manifest = yaml.safe_load((unit_dir / "manifest.yaml").read_text(encoding="utf-8"))
    assert set(manifest) == MANIFEST_KEYS, f"{unit_dir.name} manifest keys {set(manifest)}"
    assert manifest["kind"] == "unit"
    assert manifest["blueprint_version"] == 1
    assert manifest["provenance"] == "original"
    assert manifest["id"] == unit_dir.name
    entry = load_map_entry(manifest["id"])
    assert manifest["lessons"] == entry["lessons"]
    # concepts.requires IS the design's "prerequisites" field (plan 004 Phase A check 2).
    assert set(manifest["concepts"]) == {"introduces", "requires", "practices"}
    for field in ("introduces", "requires", "practices"):
        assert sorted(manifest["concepts"][field]) == sorted(entry[field]), (
            f"{unit_dir.name} concepts.{field} differs from coverage map"
        )


def test_student_hygiene(unit_dir):
    nb = read_nb(unit_dir / "exercises.ipynb")
    for i, cell in enumerate(code_cells(nb)):
        assert cell.outputs == [], f"{unit_dir.name} exercises code cell {i} has outputs"
        assert cell.execution_count is None, f"{unit_dir.name} exercises cell {i} executed"
    for cell in nb.cells:
        # Proxy: heading-style leaks only; real leakage is the content gate's judgment.
        assert not re.search(r"(?i)^#+\s*solution", cell.source, re.MULTILINE), (
            f"{unit_dir.name} exercises contain a solution heading"
        )


def test_exercise_structure(unit_dir):
    nb = read_nb(unit_dir / "exercises.ipynb")
    markdown = "\n".join(c.source for c in nb.cells if c.cell_type == "markdown")
    headings = EXERCISE_HEADING.findall(markdown)
    assert len(headings) >= 6, f"{unit_dir.name}: {len(headings)} exercise headings (<6)"
    stretch = [c for c in nb.cells if "stretch" in tags(c)]
    assert len(stretch) >= 2, f"{unit_dir.name}: {len(stretch)} stretch-tagged cells (<2)"


def test_solutions_structure_and_execution(unit_dir):
    from nbclient import NotebookClient

    ex_nb = read_nb(unit_dir / "exercises.ipynb")
    sol_nb = read_nb(unit_dir / "solutions.ipynb")
    ex_md = "\n".join(c.source for c in ex_nb.cells if c.cell_type == "markdown")
    exercise_headings = EXERCISE_HEADING.findall(ex_md)

    # Every exercise heading mirrored, each followed by >=1 code cell before the next.
    sequence = [(c.cell_type, c.source) for c in sol_nb.cells]
    for heading in exercise_headings:
        idx = next(
            (i for i, (t, s) in enumerate(sequence)
             if t == "markdown" and re.search(rf"^{re.escape(heading)}\b", s, re.MULTILINE)),
            None,
        )
        assert idx is not None, f"{unit_dir.name} solutions missing '{heading}'"
        following = []
        for t, s in sequence[idx + 1:]:
            if t == "markdown" and EXERCISE_HEADING.search(s):
                break
            following.append(t)
        assert "code" in following, f"{unit_dir.name} solutions: no code under '{heading}'"

    codes = code_cells(sol_nb)
    assert sum("assert" in c.source for c in codes) >= 3, (
        f"{unit_dir.name} solutions need >=3 assert cells"
    )
    joined = "\n".join(c.source for c in codes)
    for c in codes:
        assert not INTERACTIVE.search(c.source), f"{unit_dir.name} solutions call input()"
        assert not GUI_IMPORT.search(c.source), f"{unit_dir.name} solutions import a GUI"
        assert not RANDOM_FROM_IMPORT.search(c.source), (
            f"{unit_dir.name} solutions use 'from random import' (only 'import random')"
        )
    if "random." in joined:
        seed_pos = joined.find("random.seed(4)")
        first_use = next(
            (m.start() for m in re.finditer(r"\brandom\.\w+", joined)
             if not joined.startswith("random.seed(4)", m.start())),
            None,
        )
        assert seed_pos != -1, f"{unit_dir.name} solutions use random without random.seed(4)"
        if first_use is not None:
            assert seed_pos < first_use, (
                f"{unit_dir.name} solutions: random.seed(4) must precede first use"
            )

    client = NotebookClient(
        sol_nb, timeout=120, kernel_name="python3",
        resources={"metadata": {"path": str(unit_dir)}},
    )
    client.execute()


def test_lesson_conventions(unit_dir):
    nb = read_nb(unit_dir / "lesson.ipynb")
    assert nb.cells, f"{unit_dir.name} lesson is empty"
    first = nb.cells[0]
    # Hook position proxy: hookness itself is the content gate's call (D-001, unit-level).
    assert first.cell_type == "markdown" and first.source.strip(), (
        f"{unit_dir.name} lesson must open with non-empty markdown"
    )
    for i, cell in enumerate(code_cells(nb)):
        if INTERACTIVE.search(cell.source) or GUI_IMPORT.search(cell.source):
            assert "no-exec" in tags(cell), (
                f"{unit_dir.name} lesson code cell {i} is interactive/GUI but not no-exec"
            )


def test_teacher_notes_structure(unit_dir):
    notes = (unit_dir / "teacher-notes.md").read_text(encoding="utf-8")
    for heading in NOTES_HEADINGS:
        assert heading in notes, f"{unit_dir.name} teacher notes missing '{heading}'"


@pytest.mark.xfail(reason="strict once Phase D lands all three units", strict=False)
def test_all_three_units_present():
    for unit_id in PLAN_004_UNITS:
        assert (UNITS_ROOT / unit_id).is_dir(), f"{unit_id} missing"
