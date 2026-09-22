from pathlib import Path

import nbformat
import pytest
import yaml

from tools.patterns import pattern_marker_findings, technique_spiral_findings
from tools.patterns_doc import generate_patterns_document, patterns_doc_findings
from tools.patterns_doc import main as patterns_doc_main

REPO = Path(__file__).resolve().parents[1]
PATTERN = "scan-pattern"
BASE = "base-concept"


def _write_yaml(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _write_notebook(path: Path, cells) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nbformat.v4.new_notebook(cells=cells), path)


def _entry(entry_id, *, kind="unit", introduces=None, practices=None):
    return {
        "id": entry_id,
        "kind": kind,
        "title": entry_id,
        "lessons": 1,
        "introduces": introduces or [],
        "requires": [],
        "practices": practices or [],
    }


def _entry_dir(root: Path, entry: dict) -> Path:
    plural = {"unit": "units", "checkpoint": "checkpoints", "project": "projects"}
    return root / "book1" / plural[entry["kind"]] / entry["id"]


def _write_manifest(root: Path, entry: dict) -> None:
    directory = _entry_dir(root, entry)
    directory.mkdir(parents=True, exist_ok=True)
    _write_yaml(
        directory / "manifest.yaml",
        {
            "id": entry["id"],
            "kind": entry["kind"],
            "blueprint_version": 1,
            "lessons": entry["lessons"],
            "concepts": {
                field: list(entry[field]) for field in ("introduces", "requires", "practices")
            },
            "provenance": "original",
        },
    )


def _exercise_cells(pattern=PATTERN, *, heading_tags=None, code_tags=None):
    marker = nbformat.v4.new_markdown_cell(f"<!-- pattern: {pattern} -->")
    heading = nbformat.v4.new_markdown_cell(
        "## Exercise 1\nSolve it.", metadata={"tags": heading_tags or []}
    )
    code = nbformat.v4.new_code_cell("", metadata={"tags": code_tags or []})
    return [marker, heading, code]


def _map(root: Path):
    path = root / "book1/curriculum/coverage-map.yaml"
    return path, yaml.safe_load(path.read_text(encoding="utf-8"))


def _manifest(root: Path, entry_id: str):
    entry = next(entry for entry in _map(root)[1]["entries"] if entry["id"] == entry_id)
    path = _entry_dir(root, entry) / "manifest.yaml"
    return path, yaml.safe_load(path.read_text(encoding="utf-8"))


def _notebook(root: Path, entry_id: str, name="exercises.ipynb"):
    entry = next(entry for entry in _map(root)[1]["entries"] if entry["id"] == entry_id)
    path = _entry_dir(root, entry) / name
    return path, nbformat.read(path, as_version=4)


def _sync_manifest(root: Path, entry: dict) -> None:
    path, manifest = _manifest(root, entry["id"])
    manifest["concepts"] = {
        field: list(entry[field]) for field in ("introduces", "requires", "practices")
    }
    _write_yaml(path, manifest)


@pytest.fixture
def pattern_root(tmp_path):
    _write_yaml(
        tmp_path / "books.yaml",
        {
            "books_version": 1,
            "books": [
                {"id": "book1", "number": 1, "root": "book1", "depends_on": []},
                {
                    "id": "book2",
                    "number": 2,
                    "root": "book2",
                    "depends_on": ["book1"],
                },
            ],
        },
    )
    _write_yaml(
        tmp_path / "book1/curriculum/concepts.yaml",
        {
            "concepts_version": 1,
            "concepts": [
                {"id": BASE, "name": "Base concept", "category": "loops"},
                {
                    "id": PATTERN,
                    "name": "Scan pattern (scan)",
                    "category": "techniques",
                    "kind": "technique",
                },
            ],
        },
    )
    entries = [
        _entry("unit-01-home", introduces=[BASE, PATTERN]),
        _entry("unit-02-practice", practices=[PATTERN]),
        _entry("unit-03-practice", practices=[PATTERN]),
        _entry("unit-04-practice", practices=[PATTERN]),
        _entry("checkpoint-01-review", kind="checkpoint"),
        _entry("project-02-capstone", kind="project"),
    ]
    _write_yaml(
        tmp_path / "book1/curriculum/coverage-map.yaml",
        {"map_version": 1, "entries": entries},
    )
    for entry in entries:
        _write_manifest(tmp_path, entry)
        directory = _entry_dir(tmp_path, entry)
        if entry["kind"] == "unit":
            lesson_cells = [nbformat.v4.new_markdown_cell("# Lesson")]
            if PATTERN in entry["introduces"]:
                lesson_cells.append(
                    nbformat.v4.new_markdown_cell(
                        f"## Pattern spotlight\nNotice the scan.\n<!-- pattern: {PATTERN} -->"
                    )
                )
            _write_notebook(directory / "lesson.ipynb", lesson_cells)
            exercise_cells = (
                _exercise_cells() if PATTERN in entry["introduces"] + entry["practices"] else []
            )
            _write_notebook(directory / "exercises.ipynb", exercise_cells)
        elif entry["kind"] == "checkpoint":
            _write_notebook(
                directory / "checkpoint.ipynb",
                [nbformat.v4.new_markdown_cell("## Question 1")],
            )
        else:
            _write_notebook(
                directory / "brief.ipynb",
                [nbformat.v4.new_markdown_cell("# Capstone")],
            )
    _write_yaml(
        tmp_path / "book1/curriculum/patterns-catalog.yaml",
        {PATTERN: {"hook": "Check each item once.", "enabling_concepts": [BASE]}},
    )
    generate_patterns_document(tmp_path)
    return tmp_path


def test_complete_pattern_fixture_passes_all_checks(pattern_root):
    assert pattern_marker_findings(pattern_root, "book1") == []
    assert technique_spiral_findings(pattern_root, "book1") == []
    assert patterns_doc_findings(pattern_root, "book1") == []


def test_technique_spiral_ignores_auxiliary_occurrences(pattern_root):
    borrowed = "borrowed-pattern"
    concepts_path = pattern_root / "book1/curriculum/concepts.yaml"
    concepts = yaml.safe_load(concepts_path.read_text(encoding="utf-8"))
    concepts["concepts"].append(
        {
            "id": borrowed,
            "name": "Borrowed pattern",
            "category": "techniques",
            "kind": "technique",
        }
    )
    _write_yaml(concepts_path, concepts)

    path, data = _map(pattern_root)
    capstone = next(entry for entry in data["entries"] if entry["kind"] == "project")
    capstone["introduces"].append(borrowed)
    _write_yaml(path, data)
    brief_path, brief = _notebook(pattern_root, capstone["id"], "brief.ipynb")
    brief.cells[0].source += f"\n<!-- pattern: {borrowed} -->"
    nbformat.write(brief, brief_path)
    baseline = technique_spiral_findings(pattern_root, "book1")

    path, data = _map(pattern_root)
    data["map_version"] = 2
    for entry in data["entries"]:
        entry["auxiliary"] = []
    for entry in data["entries"][:3]:
        entry["auxiliary"] = [f"book1:{borrowed}"]
    _write_yaml(path, data)

    assert sum(bool(entry["auxiliary"]) for entry in data["entries"]) == 3
    assert any(f"{borrowed}: 0 core pre-capstone" in finding for finding in baseline)
    assert technique_spiral_findings(pattern_root, "book1") == baseline


def test_generated_patterns_doc_has_map_derived_where_table(pattern_root):
    text = (pattern_root / "book1/reference/patterns.md").read_text(encoding="utf-8")

    assert (
        """### Where you'll meet it

| Role | Entry |
| --- | --- |
| Home | `unit-01-home` |
| Reappearance | `unit-02-practice` |
| Reappearance | `unit-03-practice` |
| Reappearance | `unit-04-practice` |"""
        in text
    )


def test_technique_spiral_rejects_duplicate_home(pattern_root):
    path, data = _map(pattern_root)
    entry = data["entries"][1]
    entry["introduces"] = [PATTERN]
    entry["practices"] = []
    _write_yaml(path, data)
    _sync_manifest(pattern_root, entry)
    lesson_path, lesson = _notebook(pattern_root, entry["id"], "lesson.ipynb")
    lesson.cells.append(nbformat.v4.new_markdown_cell(f"Spotlight.\n<!-- pattern: {PATTERN} -->"))
    nbformat.write(lesson, lesson_path)

    findings = technique_spiral_findings(pattern_root, "book1")

    assert any("introduced 2 times" in finding for finding in findings)


def test_technique_spiral_rejects_practice_before_home(pattern_root):
    path, data = _map(pattern_root)
    data["entries"][0], data["entries"][1] = data["entries"][1], data["entries"][0]
    _write_yaml(path, data)

    findings = technique_spiral_findings(pattern_root, "book1")

    assert any("practice before home" in finding for finding in findings)


def test_technique_spiral_rejects_only_two_practices(pattern_root):
    path, data = _map(pattern_root)
    entry = data["entries"][3]
    entry["practices"] = []
    _write_yaml(path, data)
    _sync_manifest(pattern_root, entry)

    findings = technique_spiral_findings(pattern_root, "book1")

    assert any("2 core pre-capstone non-checkpoint practices (<3)" in f for f in findings)


def test_checkpoint_only_third_does_not_satisfy_spiral(pattern_root):
    path, data = _map(pattern_root)
    data["entries"][3]["practices"] = []
    checkpoint = data["entries"][4]
    checkpoint["practices"] = [PATTERN]
    _write_yaml(path, data)
    _sync_manifest(pattern_root, data["entries"][3])
    _sync_manifest(pattern_root, checkpoint)

    findings = technique_spiral_findings(pattern_root, "book1")

    assert any("2 core pre-capstone non-checkpoint practices (<3)" in f for f in findings)


@pytest.mark.parametrize("tagged_cell", ["heading", "code"])
def test_stretch_only_embodiment_does_not_satisfy_spiral(pattern_root, tagged_cell):
    path, notebook = _notebook(pattern_root, "unit-04-practice")
    index = 1 if tagged_cell == "heading" else 2
    notebook.cells[index].metadata["tags"] = ["stretch"]
    nbformat.write(notebook, path)

    findings = technique_spiral_findings(pattern_root, "book1")

    assert any("stretch embodiment" in finding for finding in findings)
    assert any("2 core pre-capstone non-checkpoint practices (<3)" in f for f in findings)


def test_pattern_marker_rejects_unknown_id(pattern_root):
    path, notebook = _notebook(pattern_root, "unit-02-practice")
    notebook.cells.insert(0, nbformat.v4.new_markdown_cell("<!-- pattern: unknown-pattern -->"))
    nbformat.write(notebook, path)

    assert any(
        "unknown or non-technique marker 'unknown-pattern'" in finding
        for finding in pattern_marker_findings(pattern_root, "book1")
    )


def test_pattern_marker_rejects_marker_like_invalid_id(pattern_root):
    path, notebook = _notebook(pattern_root, "unit-02-practice")
    notebook.cells.insert(0, nbformat.v4.new_markdown_cell("<!-- pattern: unknown_pattern -->"))
    nbformat.write(notebook, path)

    assert any(
        "invalid pattern marker" in finding
        for finding in pattern_marker_findings(pattern_root, "book1")
    )


def test_pattern_marker_rejects_manifest_map_mismatch(pattern_root):
    path, manifest = _manifest(pattern_root, "unit-02-practice")
    manifest["concepts"]["practices"] = []
    _write_yaml(path, manifest)

    assert any(
        "technique tags differ from coverage map" in finding
        for finding in pattern_marker_findings(pattern_root, "book1")
    )


def test_patterns_doc_rejects_stale_catalog_output(pattern_root):
    path = pattern_root / "book1/curriculum/patterns-catalog.yaml"
    catalog = yaml.safe_load(path.read_text(encoding="utf-8"))
    catalog[PATTERN]["hook"] = "A revised hook."
    _write_yaml(path, catalog)

    assert any(
        "patterns.md is out of date" in f for f in patterns_doc_findings(pattern_root, "book1")
    )


def test_patterns_doc_rejects_unregistered_catalog_row(pattern_root):
    path = pattern_root / "book1/curriculum/patterns-catalog.yaml"
    catalog = yaml.safe_load(path.read_text(encoding="utf-8"))
    catalog["stale-pattern"] = {"hook": "Stale.", "enabling_concepts": [BASE]}
    _write_yaml(path, catalog)

    assert any(
        "catalog has unregistered technique ids" in f
        for f in patterns_doc_findings(pattern_root, "book1")
    )


def test_pattern_marker_rejects_missing_home_marker_in_each_required_notebook(pattern_root):
    path, lesson = _notebook(pattern_root, "unit-01-home", "lesson.ipynb")
    lesson.cells[1].source = "## Pattern spotlight\nNotice the scan."
    nbformat.write(lesson, path)

    findings = pattern_marker_findings(pattern_root, "book1")

    assert any("lesson.ipynb needs exactly one marker" in finding for finding in findings)
    assert not any("exercises.ipynb needs exactly one marker" in finding for finding in findings)


def test_pattern_marker_rejects_duplicate_marker_in_one_notebook(pattern_root):
    path, notebook = _notebook(pattern_root, "unit-02-practice")
    notebook.cells.insert(1, nbformat.v4.new_markdown_cell(f"<!-- pattern: {PATTERN} -->"))
    nbformat.write(notebook, path)

    assert any(
        "exercises.ipynb needs exactly one marker" in finding
        for finding in pattern_marker_findings(pattern_root, "book1")
    )


def test_pattern_marker_rejects_wrong_exercise_adjacency(pattern_root):
    path, notebook = _notebook(pattern_root, "unit-02-practice")
    notebook.cells.insert(1, nbformat.v4.new_markdown_cell("Instructions before the exercise."))
    nbformat.write(notebook, path)

    assert any(
        "marker must immediately precede an Exercise heading" in finding
        for finding in pattern_marker_findings(pattern_root, "book1")
    )


def test_pattern_marker_rejects_checkpoint_technique_tag(pattern_root):
    path, data = _map(pattern_root)
    checkpoint = data["entries"][4]
    checkpoint["practices"] = [PATTERN]
    _write_yaml(path, data)
    _sync_manifest(pattern_root, checkpoint)

    assert any(
        "checkpoint may not carry technique tags" in finding
        for finding in pattern_marker_findings(pattern_root, "book1")
    )


def test_pattern_marker_rejects_checkpoint_marker_without_tag(pattern_root):
    path, notebook = _notebook(pattern_root, "checkpoint-01-review", "checkpoint.ipynb")
    notebook.cells.append(nbformat.v4.new_markdown_cell(f"<!-- pattern: {PATTERN} -->"))
    nbformat.write(notebook, path)

    assert any(
        "checkpoint may not carry pattern markers" in finding
        for finding in pattern_marker_findings(pattern_root, "book1")
    )


def test_pattern_marker_rejects_checkpoint_marker_like_invalid_id(pattern_root):
    path, notebook = _notebook(pattern_root, "checkpoint-01-review", "checkpoint.ipynb")
    notebook.cells.append(nbformat.v4.new_markdown_cell("<!-- pattern: unknown_pattern -->"))
    nbformat.write(notebook, path)

    assert any(
        "checkpoint may not carry pattern markers" in finding
        for finding in pattern_marker_findings(pattern_root, "book1")
    )


@pytest.mark.parametrize("check", [pattern_marker_findings, technique_spiral_findings])
def test_pattern_checks_fail_closed_when_concepts_file_is_missing(pattern_root, check):
    (pattern_root / "book1/curriculum/concepts.yaml").unlink()

    assert any(
        "concepts.yaml does not exist" in finding for finding in check(pattern_root, "book1")
    )


@pytest.mark.parametrize("check", [pattern_marker_findings, technique_spiral_findings])
def test_pattern_checks_fail_closed_when_concepts_list_has_wrong_shape(pattern_root, check):
    path = pattern_root / "book1/curriculum/concepts.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["concepts"] = {}
    _write_yaml(path, data)

    assert any("concepts must be a list" in finding for finding in check(pattern_root, "book1"))


@pytest.mark.parametrize("check", [pattern_marker_findings, technique_spiral_findings])
def test_pattern_checks_fail_closed_when_coverage_map_is_missing(pattern_root, check):
    (pattern_root / "book1/curriculum/coverage-map.yaml").unlink()

    assert any(
        "coverage-map.yaml does not exist" in finding for finding in check(pattern_root, "book1")
    )


@pytest.mark.parametrize("check", [pattern_marker_findings, technique_spiral_findings])
def test_pattern_checks_fail_closed_when_entries_list_has_wrong_shape(pattern_root, check):
    path, data = _map(pattern_root)
    data["entries"] = {}
    _write_yaml(path, data)

    assert any(
        "coverage-map entries must be a list" in finding for finding in check(pattern_root, "book1")
    )


@pytest.mark.parametrize(
    ("relative_path", "expected"),
    [
        ("book1/curriculum/concepts.yaml", "concepts.yaml does not exist"),
        ("book1/curriculum/coverage-map.yaml", "coverage-map.yaml does not exist"),
        ("book1/curriculum/patterns-catalog.yaml", "patterns-catalog.yaml does not exist"),
    ],
)
def test_patterns_doc_fails_closed_when_authoritative_input_is_missing(
    pattern_root, relative_path, expected
):
    (pattern_root / relative_path).unlink()

    assert any(expected in finding for finding in patterns_doc_findings(pattern_root, "book1"))


@pytest.mark.parametrize(
    ("relative_path", "field", "expected"),
    [
        ("book1/curriculum/concepts.yaml", "concepts", "concepts must be a list"),
        (
            "book1/curriculum/coverage-map.yaml",
            "entries",
            "coverage-map entries must be a list",
        ),
    ],
)
def test_patterns_doc_fails_closed_when_authoritative_list_has_wrong_shape(
    pattern_root, relative_path, field, expected
):
    path = pattern_root / relative_path
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data[field] = {}
    _write_yaml(path, data)

    assert any(expected in finding for finding in patterns_doc_findings(pattern_root, "book1"))


def test_patterns_doc_fails_closed_when_catalog_has_wrong_shape(pattern_root):
    path = pattern_root / "book1/curriculum/patterns-catalog.yaml"
    _write_yaml(path, [])

    assert any(
        "patterns-catalog.yaml must be a mapping" in finding
        for finding in patterns_doc_findings(pattern_root, "book1")
    )


def test_patterns_doc_and_pdf_probe_reject_non_string_catalog_key(pattern_root, capsys):
    path = pattern_root / "book1/curriculum/patterns-catalog.yaml"
    catalog = yaml.safe_load(path.read_text(encoding="utf-8"))
    catalog[7] = {"hook": "Not a valid id.", "enabling_concepts": [BASE]}
    _write_yaml(path, catalog)

    assert any(
        "catalog keys must be string technique ids" in finding
        for finding in patterns_doc_findings(pattern_root, "book1")
    )
    assert patterns_doc_main(["--root", str(pattern_root), "--pdf-probe"]) == 1
    assert "catalog keys must be string technique ids" in capsys.readouterr().out


def test_post_project_02_practice_does_not_satisfy_spiral(pattern_root):
    path, data = _map(pattern_root)
    late_practice = data["entries"].pop(3)
    data["entries"].append(late_practice)
    data["entries"].append(_entry("project-03-later", kind="project"))
    _write_yaml(path, data)

    findings = technique_spiral_findings(pattern_root, "book1")

    assert any("2 core pre-capstone non-checkpoint practices (<3)" in f for f in findings)


def test_technique_spiral_fails_when_project_02_boundary_is_missing(pattern_root):
    path, data = _map(pattern_root)
    data["entries"] = [
        entry for entry in data["entries"] if not entry["id"].startswith("project-02-")
    ]
    _write_yaml(path, data)

    assert any(
        "project-02 capstone boundary" in finding
        for finding in technique_spiral_findings(pattern_root, "book1")
    )


def test_patterns_pdf_probe_reports_present_for_valid_pattern_book(pattern_root, capsys):
    assert patterns_doc_main(["--root", str(pattern_root), "--pdf-probe"]) == 0
    assert capsys.readouterr().out == "present\n"


def test_patterns_pdf_probe_reports_empty_for_valid_empty_book(tmp_path, capsys):
    # A valid book with NO registered techniques probes as "empty". Uses a dedicated
    # empty fixture (not the real repo, which now registers patterns from Phase B on).
    from tools.patterns_doc import generated_patterns_text

    _write_yaml(
        tmp_path / "books.yaml",
        {
            "books_version": 1,
            "books": [{"id": "book1", "number": 1, "root": "book1", "depends_on": []}],
        },
    )
    _write_yaml(
        tmp_path / "book1/curriculum/concepts.yaml",
        {"concepts_version": 1, "concepts": [{"id": BASE, "name": "Base", "category": "loops"}]},
    )
    _write_yaml(tmp_path / "book1/curriculum/coverage-map.yaml", {"map_version": 1, "entries": []})
    _write_yaml(tmp_path / "book1/curriculum/patterns-catalog.yaml", {})
    (tmp_path / "book1/reference").mkdir(parents=True, exist_ok=True)
    (tmp_path / "book1/reference/patterns.md").write_text(
        generated_patterns_text(tmp_path), encoding="utf-8"
    )

    assert patterns_doc_main(["--root", str(tmp_path), "--pdf-probe"]) == 0
    assert capsys.readouterr().out == "empty\n"


def test_patterns_pdf_probe_fails_on_malformed_concepts(pattern_root, capsys):
    path = pattern_root / "book1/curriculum/concepts.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["concepts"] = {}
    _write_yaml(path, data)

    assert patterns_doc_main(["--root", str(pattern_root), "--pdf-probe"]) == 1
    assert "concepts must be a list" in capsys.readouterr().out


def test_book2_only_technique_does_not_affect_book1_spiral(pattern_root):
    _write_yaml(
        pattern_root / "book2/curriculum/concepts.yaml",
        {
            "concepts_version": 1,
            "concepts": [
                {
                    "id": "book2-only-technique",
                    "name": "Book 2 only",
                    "category": "techniques",
                    "kind": "technique",
                }
            ],
        },
    )
    _write_yaml(
        pattern_root / "book2/curriculum/coverage-map.yaml",
        {
            "map_version": 1,
            "entries": [
                _entry("unit-01-book2", introduces=["book2-only-technique"]),
            ],
        },
    )

    assert technique_spiral_findings(pattern_root, "book1") == []
    assert technique_spiral_findings(pattern_root, "book2") == []


def test_pattern_marker_rejects_colonless_comment_on_checkpoint(pattern_root):
    # A malformed (colon-less) pattern comment must NOT slip past the checkpoint
    # "no marker" guard by evading MARKER_LIKE. (content-gate [sol] fail-open)
    entry = next(
        entry for entry in _map(pattern_root)[1]["entries"] if entry["kind"] == "checkpoint"
    )
    path = _entry_dir(pattern_root, entry) / "checkpoint.ipynb"
    _write_notebook(
        path,
        [
            nbformat.v4.new_markdown_cell("## Question 1"),
            nbformat.v4.new_markdown_cell(f"<!-- pattern {PATTERN} -->"),
        ],
    )

    findings = pattern_marker_findings(pattern_root, "book1")

    assert any("checkpoint may not carry pattern markers" in finding for finding in findings)


def test_technique_spiral_excludes_home_self_practice(pattern_root):
    # Home listing the id in its own `practices` must NOT count as a reappearance;
    # with only two genuine later practices the spiral must fail <3. (content-gate [sol])
    path, data = _map(pattern_root)
    home = data["entries"][0]
    home["practices"] = [PATTERN]  # home self-practices
    data["entries"][3]["practices"] = []  # drop one genuine reappearance -> only two remain
    _write_yaml(path, data)
    _sync_manifest(pattern_root, home)
    _sync_manifest(pattern_root, data["entries"][3])
    # keep notebooks consistent with tags so the home locus stays a valid core home
    dropped_dir = _entry_dir(pattern_root, data["entries"][3])
    _write_notebook(dropped_dir / "exercises.ipynb", [])

    findings = technique_spiral_findings(pattern_root, "book1")

    assert any("core pre-capstone non-checkpoint practices (<3)" in finding for finding in findings)


def test_patterns_doc_rejects_enabling_concept_introduced_after_home(pattern_root):
    # A catalog enabling_concept introduced in a LATER entry than the pattern's home
    # must fail patterns-doc-check (tools/patterns_doc.py intro<=home rule).
    cpath = pattern_root / "book1/curriculum/concepts.yaml"
    cdata = yaml.safe_load(cpath.read_text(encoding="utf-8"))
    cdata["concepts"].append({"id": "late-concept", "name": "Late", "category": "loops"})
    _write_yaml(cpath, cdata)

    mpath, mdata = _map(pattern_root)
    mdata["entries"][3]["introduces"] = ["late-concept"]  # unit-04-practice, after home (index 0)
    _write_yaml(mpath, mdata)

    catp = pattern_root / "book1/curriculum/patterns-catalog.yaml"
    cat = yaml.safe_load(catp.read_text(encoding="utf-8"))
    cat[PATTERN]["enabling_concepts"].append("late-concept")
    _write_yaml(catp, cat)

    findings = patterns_doc_findings(pattern_root, "book1")

    assert any("not introduced by its home" in finding for finding in findings)


def test_real_book_pattern_checks_pass_on_real_book():
    assert pattern_marker_findings(REPO, "book1") == []
    assert technique_spiral_findings(REPO, "book1") == []
    assert patterns_doc_findings(REPO, "book1") == []
