import ast
import json
import shutil
from pathlib import Path

import nbformat
import pytest
import yaml

from tools.concept_scan import (
    code_sources,
    concept_scan_findings,
    detect,
    entry_notebooks,
    scanner_profile,
)
from tools.curriculum import prereq_findings

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "borrowed_tools"


def _write_yaml(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _cell(
    source: str,
    *,
    cell_id: str,
    cell_type: str = "code",
    tags: list[str] | None = None,
    auxiliary: object | None = None,
    task_id: str | None = None,
):
    maker = nbformat.v4.new_code_cell if cell_type == "code" else nbformat.v4.new_markdown_cell
    cell = maker(source)
    cell["id"] = cell_id
    cell["metadata"]["tags"] = tags or []
    if auxiliary is not None:
        cell["metadata"]["py4kids_auxiliary"] = auxiliary
    if task_id is not None:
        cell["metadata"]["py4kids_task_id"] = task_id
    return cell


def _write_notebook(path: Path, cells: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nbformat.v4.new_notebook(cells=cells), path)


def _write_raw_notebook(path: Path, cells: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "cells": cells,
                "metadata": {},
                "nbformat": 4,
                "nbformat_minor": 5,
            }
        ),
        encoding="utf-8",
    )


def _scanner_root(tmp_path: Path, *, auxiliary: list[str] | None = None) -> Path:
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
    concepts = [
        "print",
        "string-literal",
        "input",
        "variable",
        "arithmetic",
        "loop-counter",
        "accumulator",
        "list-literal",
    ]
    _write_yaml(
        tmp_path / "book1/curriculum/concepts.yaml",
        {
            "concepts_version": 1,
            "concepts": [
                {"id": concept, "name": concept, "category": "data"} for concept in concepts
            ],
        },
    )
    _write_yaml(
        tmp_path / "book2/curriculum/concepts.yaml",
        {
            "concepts_version": 1,
            "concepts": [
                {
                    "id": "str-split",
                    "name": "str-split",
                    "category": "io",
                    "kind": "feature",
                }
            ],
        },
    )
    _write_yaml(
        tmp_path / "book1/curriculum/coverage-map.yaml",
        {
            "map_version": 2,
            "entries": [
                {
                    "id": "unit-01-fixture",
                    "kind": "unit",
                    "title": "Fixture",
                    "lessons": 1,
                    "introduces": ["print", "string-literal"],
                    "requires": [],
                    "practices": [],
                    "auxiliary": auxiliary or [],
                }
            ],
        },
    )
    _write_yaml(
        tmp_path / "book2/curriculum/coverage-map.yaml",
        {
            "map_version": 1,
            "entries": [
                {
                    "id": "unit-01-split",
                    "kind": "unit",
                    "title": "Split",
                    "lessons": 1,
                    "introduces": ["str-split"],
                    "requires": [],
                    "practices": [],
                }
            ],
        },
    )
    return tmp_path


def _install_fixture_shape(root: Path, shape: str) -> Path:
    """Copy one checked-in Phase-D shape into a synthetic governed unit."""
    source = FIXTURE_ROOT / shape
    manifest = yaml.safe_load((source / "manifest.yaml").read_text(encoding="utf-8"))
    path, coverage = _map(root)
    concepts = manifest["concepts"]
    for field in ("introduces", "requires", "practices", "auxiliary"):
        coverage["entries"][0][field] = concepts[field]
    if concepts["requires"]:
        coverage["entries"].insert(
            0,
            {
                "id": "unit-00-prerequisite-home",
                "kind": "unit",
                "title": "Synthetic prerequisite home",
                "lessons": 1,
                "introduces": concepts["requires"],
                "requires": [],
                "practices": [],
                "auxiliary": [],
            },
        )
    book1_auxiliary = [
        qualified_id.removeprefix("book1:")
        for qualified_id in concepts["auxiliary"]
        if qualified_id.startswith("book1:")
    ]
    if book1_auxiliary:
        coverage["entries"].append(
            {
                "id": "unit-99-auxiliary-home",
                "kind": "unit",
                "title": "Synthetic later auxiliary home",
                "lessons": 1,
                "introduces": book1_auxiliary,
                "requires": [],
                "practices": [],
                "auxiliary": [],
            }
        )
    _write_yaml(path, coverage)
    target = root / "book1/units/unit-01-fixture"
    target.mkdir(parents=True, exist_ok=True)
    for fixture_path in source.iterdir():
        if fixture_path.is_file():
            shutil.copyfile(fixture_path, target / fixture_path.name)
    return target


def _load_notebook(path: Path):
    return nbformat.read(path, as_version=4)


def _save_notebook(path: Path, notebook) -> None:
    nbformat.write(notebook, path)


def _map(root: Path) -> tuple[Path, dict]:
    path = root / "book1/curriculum/coverage-map.yaml"
    return path, yaml.safe_load(path.read_text(encoding="utf-8"))


def _set_entry(
    root: Path,
    *,
    auxiliary: list[str] | None = None,
    introduces: list[str] | None = None,
) -> None:
    path, data = _map(root)
    if auxiliary is not None:
        data["entries"][0]["auxiliary"] = auxiliary
    if introduces is not None:
        data["entries"][0]["introduces"] = introduces
    _write_yaml(path, data)


def _write_k2(root: Path, rows: list[dict]) -> None:
    _write_yaml(
        root / "book1/curriculum/k2-exceptions.yaml",
        {"k2_exceptions_version": 1, "exceptions": rows},
    )


def _register_book2_feature(root: Path, concept_id: str) -> None:
    path = root / "book2/curriculum/concepts.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["concepts"].append(
        {
            "id": concept_id,
            "name": concept_id,
            "category": "data",
            "kind": "feature",
        }
    )
    _write_yaml(path, data)


def _register_book2_set_ops(root: Path) -> None:
    _register_book2_feature(root, "set-ops")


def _k2_row(cell_id: str = "counter") -> dict:
    return {
        "cell-id": cell_id,
        "concept-ids": ["book1:loop-counter", "book1:accumulator"],
        "exact-ast-form": "name = name + 1",
        "role": "composed",
    }


def _given_bytes(source: str) -> str:
    start = "# GIVEN TOOL — do not edit\n"
    end = "# your work begins below\n"
    before, body = source.split(start, 1)
    assert before == ""
    given, _after = body.split(end, 1)
    return start + given + end


def test_checked_in_fixtures_are_exactly_the_three_governed_shapes():
    assert sorted(path.name for path in FIXTURE_ROOT.iterdir() if path.is_dir()) == [
        "given-pair",
        "lesson-real-form",
        "markdown-real-form",
    ]

    given = FIXTURE_ROOT / "given-pair"
    exercise = _load_notebook(given / "exercises.ipynb").cells[0]
    solution = _load_notebook(given / "solutions.ipynb").cells[0]
    assert exercise.metadata.py4kids_task_id == solution.metadata.py4kids_task_id
    assert _given_bytes(exercise.source).encode() == _given_bytes(solution.source).encode()
    assert exercise.metadata.tags == ["auxiliary", "given"]
    assert solution.metadata.tags == ["auxiliary", "real-form"]

    lesson = _load_notebook(FIXTURE_ROOT / "lesson-real-form/lesson.ipynb").cells[0]
    assert lesson.cell_type == "code"
    assert {"no-exec", "auxiliary", "real-form"} <= set(lesson.metadata.tags)

    markdown = _load_notebook(FIXTURE_ROOT / "markdown-real-form/solutions.ipynb").cells[0]
    assert markdown.cell_type == "markdown"
    assert markdown.metadata.tags == ["auxiliary", "real-form"]
    assert markdown.source.startswith("```python\n")


@pytest.mark.parametrize("shape", ["given-pair", "lesson-real-form", "markdown-real-form"])
def test_checked_in_borrowed_tool_shape_passes_cleanly(tmp_path, shape):
    root = _scanner_root(tmp_path)
    _install_fixture_shape(root, shape)

    assert prereq_findings(root, "book1") == []
    assert concept_scan_findings(root, "book1") == []


def test_fixture_remove_auxiliary_tag_fails_specifically(tmp_path):
    root = _scanner_root(tmp_path)
    unit = _install_fixture_shape(root, "given-pair")
    path = unit / "exercises.ipynb"
    notebook = _load_notebook(path)
    notebook.cells[0].metadata.tags.remove("auxiliary")
    _save_notebook(path, notebook)

    findings = concept_scan_findings(root, "book1")
    assert any("py4kids_auxiliary requires the auxiliary tag" in item for item in findings)


def test_fixture_remove_cell_declaration_fails_specifically(tmp_path):
    root = _scanner_root(tmp_path)
    unit = _install_fixture_shape(root, "given-pair")
    path = unit / "exercises.ipynb"
    notebook = _load_notebook(path)
    del notebook.cells[0].metadata["py4kids_auxiliary"]
    _save_notebook(path, notebook)

    findings = concept_scan_findings(root, "book1")
    assert any("auxiliary tag requires at least one id" in item for item in findings)
    assert any("used-but-unlisted concept list-literal" in item for item in findings)


def test_fixture_remove_entry_declaration_fails_specifically(tmp_path):
    root = _scanner_root(tmp_path)
    _install_fixture_shape(root, "given-pair")
    _set_entry(root, auxiliary=[])

    findings = concept_scan_findings(root, "book1")
    assert any("cell auxiliary ids not declared by entry" in item for item in findings)


def test_fixture_move_construct_outside_given_region_fails_specifically(tmp_path):
    root = _scanner_root(tmp_path)
    unit = _install_fixture_shape(root, "given-pair")
    path = unit / "exercises.ipynb"
    notebook = _load_notebook(path)
    notebook.cells[
        0
    ].source = (
        "# GIVEN TOOL — do not edit\nprint('ready')\n# your work begins below\nscores = [4, 6, 5]\n"
    )
    _save_notebook(path, notebook)

    findings = concept_scan_findings(root, "book1")
    assert any("auxiliary list-literal is outside the GIVEN region" in item for item in findings)


def test_fixture_duplicate_pairing_id_fails_specifically(tmp_path):
    root = _scanner_root(tmp_path)
    unit = _install_fixture_shape(root, "given-pair")
    path = unit / "exercises.ipynb"
    notebook = _load_notebook(path)
    duplicate = notebook.cells[0].copy()
    duplicate["id"] = "duplicate-exercise-side"
    notebook.cells.append(duplicate)
    _save_notebook(path, notebook)

    findings = concept_scan_findings(root, "book1")
    assert any(
        "auxiliary task id borrowed-list-task must pair exactly one exercise cell "
        "with one solution cell" in item
        for item in findings
    )


def test_code_sources_exposes_real_cell_metadata(tmp_path):
    path = tmp_path / "lesson.ipynb"
    _write_notebook(
        path,
        [
            _cell(
                "scores = [1, 2]",
                cell_id="borrowed-data",
                tags=["auxiliary", "demo"],
                auxiliary=["book1:list-literal"],
            )
        ],
    )

    assert list(code_sources(path)) == [
        (
            path,
            "borrowed-data",
            0,
            "scores = [1, 2]",
            ["auxiliary", "demo"],
            ["book1:list-literal"],
            "demo",
        )
    ]


def test_k1_authorization_is_cell_local(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book1:list-literal"])
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            _cell(
                "scores = [1, 2]",
                cell_id="authorized",
                tags=["auxiliary", "demo"],
                auxiliary=["book1:list-literal"],
            ),
            _cell("other = [3, 4]", cell_id="not-authorized"),
        ],
    )

    assert concept_scan_findings(root, "book1") == [
        (
            "FAIL: unit-01-fixture: lesson.ipynb cell not-authorized: "
            "used-but-unlisted concept list-literal"
        )
    ]


def test_markdown_general_closure_ignores_input_but_rejects_undeclared_split(tmp_path):
    root = _scanner_root(tmp_path)
    _write_notebook(
        root / "book1/units/unit-01-fixture/solutions.ipynb",
        [
            _cell(
                "```python\nname = input('Name: ')\n```",
                cell_id="input-fence",
                cell_type="markdown",
            ),
            _cell(
                "```python\nwords = input().split()\n```",
                cell_id="split-fence",
                cell_type="markdown",
            ),
        ],
    )

    findings = concept_scan_findings(root, "book1")

    assert not any("input" in finding for finding in findings)
    assert findings == [
        (
            "FAIL: unit-01-fixture: solutions.ipynb cell split-fence: "
            "undeclared borrowed tool book2:str-split"
        )
    ]


def _add_future_list_home(root: Path) -> None:
    path, data = _map(root)
    data["entries"].append(
        {
            "id": "unit-02-future-lists",
            "kind": "unit",
            "title": "Future lists",
            "lessons": 1,
            "introduces": ["list-literal"],
            "requires": [],
            "practices": [],
            "auxiliary": [],
        }
    )
    _write_yaml(path, data)


def test_markdown_future_book1_concept_requires_cell_declaration(tmp_path):
    root = _scanner_root(tmp_path)
    _add_future_list_home(root)
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            _cell(
                "```python\nname = input('Name: ')\n```",
                cell_id="already-taught-input",
                cell_type="markdown",
            ),
            _cell(
                "```python\nscores = [1, 2]\n```",
                cell_id="future-list",
                cell_type="markdown",
            ),
        ],
    )

    assert concept_scan_findings(root, "book1") == [
        (
            "FAIL: unit-01-fixture: lesson.ipynb cell future-list: "
            "undeclared borrowed tool book1:list-literal"
        )
    ]


def test_markdown_declaration_removal_fails_for_future_book1_concept(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book1:list-literal"])
    _add_future_list_home(root)
    _write_notebook(
        root / "book1/units/unit-01-fixture/solutions.ipynb",
        [
            _cell(
                "```python\nscores = [1, 2]\n```",
                cell_id="removed-cell-declaration",
                cell_type="markdown",
            )
        ],
    )

    assert concept_scan_findings(root, "book1") == [
        (
            "FAIL: unit-01-fixture: entry auxiliary book1:list-literal "
            "is not declared by any cell"
        ),
        (
            "FAIL: unit-01-fixture: solutions.ipynb cell removed-cell-declaration: "
            "undeclared borrowed tool book1:list-literal"
        )
    ]


@pytest.mark.parametrize(
    "source",
    [
        "```python linenums\nwords = text.split()\n```",
        "~~~~py title=adapter\nwords = text.split()\n~~~~",
    ],
)
def test_attributed_python_fence_scans_undeclared_split(tmp_path, source):
    root = _scanner_root(tmp_path)
    _write_notebook(
        root / "book1/units/unit-01-fixture/solutions.ipynb",
        [_cell(source, cell_id="attributed-split", cell_type="markdown")],
    )

    assert any(
        "undeclared borrowed tool book2:str-split" in finding
        for finding in concept_scan_findings(root, "book1")
    )


@pytest.mark.parametrize(
    "source",
    [
        "````python linenums\nif True print('broken')\n````",
        "~~~py title=broken\nif True print('broken')\n~~~",
    ],
)
def test_attributed_python_fence_syntax_error_fails(tmp_path, source):
    root = _scanner_root(tmp_path)
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [_cell(source, cell_id="attributed-broken", cell_type="markdown")],
    )

    assert any(
        "python fence has SyntaxError" in finding
        for finding in concept_scan_findings(root, "book1")
    )


def test_authorized_book2_split_in_markdown_passes_without_duplicate_registry_id(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book2:str-split"])
    _write_notebook(
        root / "book1/units/unit-01-fixture/solutions.ipynb",
        [
            _cell(
                "```python\nwords = input().split()\n```",
                cell_id="split-fence",
                cell_type="markdown",
                tags=["auxiliary", "real-form"],
                auxiliary=["book2:str-split"],
            )
        ],
    )

    book1_registry = yaml.safe_load(
        (root / "book1/curriculum/concepts.yaml").read_text(encoding="utf-8")
    )
    book2_registry = yaml.safe_load(
        (root / "book2/curriculum/concepts.yaml").read_text(encoding="utf-8")
    )
    assert "str-split" not in {row["id"] for row in book1_registry["concepts"]}
    assert [row["id"] for row in book2_registry["concepts"]].count("str-split") == 1
    assert concept_scan_findings(root, "book1") == []


def test_python_markdown_syntax_error_fails(tmp_path):
    root = _scanner_root(tmp_path)
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            _cell(
                "```python\nif True print('broken')\n```",
                cell_id="broken-fence",
                cell_type="markdown",
            )
        ],
    )

    assert concept_scan_findings(root, "book1") == [
        ("FAIL: unit-01-fixture: lesson.ipynb cell broken-fence: python fence has SyntaxError")
    ]


@pytest.mark.parametrize("source", [42, ["print('ok')", 17]])
def test_v2_malformed_code_source_fails_closed(tmp_path, source):
    root = _scanner_root(tmp_path)
    _write_raw_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            {
                "cell_type": "code",
                "id": "malformed-source",
                "metadata": {},
                "source": source,
                "execution_count": None,
                "outputs": [],
            }
        ],
    )

    assert concept_scan_findings(root, "book1") == [
        (
            "FAIL: unit-01-fixture: lesson.ipynb cell malformed-source: "
            "code source must be a string or list of strings"
        )
    ]


def test_v2_code_cell_syntax_error_fails_closed(tmp_path):
    root = _scanner_root(tmp_path)
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [_cell("if True print('broken')", cell_id="broken-code")],
    )

    assert concept_scan_findings(root, "book1") == [
        ("FAIL: unit-01-fixture: lesson.ipynb cell broken-code: code cell has SyntaxError")
    ]


def test_unclosed_python_markdown_fence_fails_closed(tmp_path):
    root = _scanner_root(tmp_path)
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            _cell(
                "```python\nprint('never closed')\n",
                cell_id="unclosed-fence",
                cell_type="markdown",
            )
        ],
    )

    assert concept_scan_findings(root, "book1") == [
        ("FAIL: unit-01-fixture: lesson.ipynb cell unclosed-fence: unclosed python fence")
    ]


def test_unclosed_non_python_markdown_fence_fails_closed(tmp_path):
    root = _scanner_root(tmp_path)
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            _cell(
                "```text\nnot closed\n```python\nwords = text.split()",
                cell_id="unclosed-text-fence",
                cell_type="markdown",
            )
        ],
    )

    assert concept_scan_findings(root, "book1") == [
        (
            "FAIL: unit-01-fixture: lesson.ipynb cell unclosed-text-fence: "
            "unclosed non-python fence"
        )
    ]


@pytest.mark.parametrize("language", ["python3", "py3"])
def test_python3_markdown_fence_is_scanned_for_borrowed_tools(tmp_path, language):
    root = _scanner_root(tmp_path)
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            _cell(
                f"```{language}\nwords = text.split()\n```",
                cell_id=f"{language}-fence",
                cell_type="markdown",
            )
        ],
    )

    assert any(
        "undeclared borrowed tool book2:str-split" in finding
        for finding in concept_scan_findings(root, "book1")
    )


def test_malformed_unhashable_tags_return_finding(tmp_path):
    root = _scanner_root(tmp_path)
    _write_raw_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            {
                "cell_type": "code",
                "id": "bad-tags",
                "metadata": {"tags": [["auxiliary"]]},
                "source": "print('ok')",
                "execution_count": None,
                "outputs": [],
            }
        ],
    )

    assert concept_scan_findings(root, "book1") == [
        (
            "FAIL: unit-01-fixture: lesson.ipynb cell bad-tags: "
            "metadata tags must be a list of strings"
        )
    ]


def test_v1_book1_split_preserves_exact_legacy_finding(tmp_path):
    root = _scanner_root(tmp_path)
    path, data = _map(root)
    data["map_version"] = 1
    del data["entries"][0]["auxiliary"]
    _write_yaml(path, data)
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [_cell("words = text.split()", cell_id="legacy-split")],
    )

    assert concept_scan_findings(root, "book1") == ["FAIL: unit-01-fixture: untaught method split"]


def test_asset_enumeration_is_sorted(tmp_path):
    assets = tmp_path / "entry/assets"
    assets.mkdir(parents=True)
    (assets / "b.py").write_text("print('b')\n", encoding="utf-8")
    (assets / "a.py").write_text("print('a')\n", encoding="utf-8")

    assert [path.name for path in entry_notebooks(tmp_path / "entry", "unit")] == [
        "a.py",
        "b.py",
    ]


def test_v2_asset_syntax_error_fails_closed(tmp_path):
    root = _scanner_root(tmp_path)
    asset = root / "book1/units/unit-01-fixture/assets/broken.py"
    asset.parent.mkdir(parents=True)
    asset.write_text("if True print('broken')\n", encoding="utf-8")

    assert concept_scan_findings(root, "book1") == [
        "FAIL: unit-01-fixture: assets/broken.py has SyntaxError"
    ]


def test_code_sources_does_not_rewrite_notebook(tmp_path):
    path = tmp_path / "lesson.ipynb"
    _write_notebook(path, [_cell("print('hi')", cell_id="stable")])
    before = json.loads(path.read_text(encoding="utf-8"))

    list(code_sources(path))

    assert json.loads(path.read_text(encoding="utf-8")) == before


@pytest.mark.parametrize(
    ("auxiliary", "tags", "expected"),
    [
        ("book1:list-literal", ["auxiliary", "demo"], "must be a list"),
        (
            ["book1:list-literal", 7],
            ["auxiliary", "demo"],
            "must be a list of qualified ids",
        ),
        (["list-literal"], ["auxiliary", "demo"], "unqualified"),
        (
            ["book1:list-literal", "book1:list-literal"],
            ["auxiliary", "demo"],
            "duplicate",
        ),
        ([], ["auxiliary", "demo"], "requires at least one id"),
        (["book1:list-literal"], ["demo"], "requires the auxiliary tag"),
        (["book1:list-literal"], ["auxiliary"], "exactly one auxiliary role"),
        (
            ["book1:list-literal"],
            ["auxiliary", "demo", "given"],
            "exactly one auxiliary role",
        ),
        (
            ["book1:list-literal"],
            ["auxiliary", "preview"],
            "exactly one auxiliary role",
        ),
    ],
)
def test_malformed_cell_auxiliary_metadata_fails(tmp_path, auxiliary, tags, expected):
    root = _scanner_root(tmp_path, auxiliary=["book1:list-literal"])
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            _cell(
                "scores = [1, 2]",
                cell_id="bad-metadata",
                tags=tags,
                auxiliary=auxiliary,
            )
        ],
    )

    assert any(expected in finding for finding in concept_scan_findings(root, "book1"))


def test_cell_id_must_be_declared_by_entry(tmp_path):
    root = _scanner_root(tmp_path)
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            _cell(
                "scores = [1, 2]",
                cell_id="not-in-entry",
                tags=["auxiliary", "demo"],
                auxiliary=["book1:list-literal"],
            )
        ],
    )

    assert any(
        "not declared by entry" in finding for finding in concept_scan_findings(root, "book1")
    )


def test_role_tag_without_auxiliary_marker_or_declaration_fails(tmp_path):
    root = _scanner_root(tmp_path)
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [_cell("print('ready')", cell_id="role-only", tags=["demo"])],
    )

    assert any(
        "auxiliary role requires the auxiliary tag" in finding
        for finding in concept_scan_findings(root, "book1")
    )


def test_detectable_declared_but_unused_fails_and_manual_only_is_exempt(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book1:list-literal", "book1:loop-counter"])
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            _cell(
                "print('ready')",
                cell_id="unused",
                tags=["auxiliary", "demo"],
                auxiliary=["book1:list-literal", "book1:loop-counter"],
            )
        ],
    )

    findings = concept_scan_findings(root, "book1")
    assert any("book1:list-literal is unused" in finding for finding in findings)
    assert not any("loop-counter is unused" in finding for finding in findings)


def test_entry_auxiliary_must_be_declared_by_a_cell(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book1:list-literal"])
    (root / "book1/units/unit-01-fixture").mkdir(parents=True)

    assert concept_scan_findings(root, "book1") == [
        (
            "FAIL: unit-01-fixture: entry auxiliary book1:list-literal "
            "is not declared by any cell"
        )
    ]


def test_markdown_unused_check_aggregates_all_fences_in_cell(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book2:str-split"])
    _write_notebook(
        root / "book1/units/unit-01-fixture/solutions.ipynb",
        [
            _cell(
                "```python\nprint('fixed form')\n```\n\n"
                "```python\nwords = text.split()\n```",
                cell_id="two-real-form-fences",
                cell_type="markdown",
                tags=["auxiliary", "real-form"],
                auxiliary=["book2:str-split"],
            )
        ],
    )

    assert concept_scan_findings(root, "book1") == []


def test_fenceless_declared_markdown_cell_reports_unused_auxiliary(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book2:str-split"])
    _write_notebook(
        root / "book1/units/unit-01-fixture/solutions.ipynb",
        [
            _cell(
                "This real form is missing its Python fence.",
                cell_id="fenceless-real-form",
                cell_type="markdown",
                tags=["auxiliary", "real-form"],
                auxiliary=["book2:str-split"],
            )
        ],
    )

    assert concept_scan_findings(root, "book1") == [
        (
            "FAIL: unit-01-fixture: solutions.ipynb cell fenceless-real-form: "
            "declared auxiliary book2:str-split is unused"
        )
    ]


def test_markdown_manual_only_future_concept_is_not_flagged(tmp_path):
    root = _scanner_root(tmp_path)
    concepts_path = root / "book1/curriculum/concepts.yaml"
    concepts = yaml.safe_load(concepts_path.read_text(encoding="utf-8"))
    concepts["concepts"].append(
        {"id": "type-conversion", "name": "type-conversion", "category": "data"}
    )
    _write_yaml(concepts_path, concepts)
    map_path, coverage = _map(root)
    coverage["entries"].append(
        {
            "id": "unit-02-future-home",
            "kind": "unit",
            "title": "Future home",
            "lessons": 1,
            "introduces": ["type-conversion"],
            "requires": [],
            "practices": [],
            "auxiliary": [],
        }
    )
    _write_yaml(map_path, coverage)
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            _cell(
                "```python\nvalue = int('1')\n```",
                cell_id="manual-only-fence",
                cell_type="markdown",
            )
        ],
    )

    assert concept_scan_findings(root, "book1") == []


def test_two_detectable_tools_exceed_cell_budget(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book1:list-literal", "book2:str-split"])
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            _cell(
                "scores = [1, 2]\nwords = text.split()",
                cell_id="over-budget",
                tags=["auxiliary", "demo"],
                auxiliary=["book1:list-literal", "book2:str-split"],
            )
        ],
    )

    assert any(
        "more than one detectable" in finding for finding in concept_scan_findings(root, "book1")
    )


def test_exercise_and_solution_given_regions_pair_by_task_id_not_position(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book1:list-literal"])
    first_given = "# GIVEN TOOL — do not edit\nfirst = [1, 2]\n# your work begins below\n"
    second_given = "# GIVEN TOOL — do not edit\nsecond = [3, 4]\n# your work begins below\n"
    exercise_cells = [
        _cell(
            first_given + "print('exercise one')",
            cell_id="exercise-one",
            tags=["auxiliary", "given"],
            auxiliary=["book1:list-literal"],
            task_id="task-one",
        ),
        _cell(
            second_given + "print('exercise two')",
            cell_id="exercise-two",
            tags=["auxiliary", "given"],
            auxiliary=["book1:list-literal"],
            task_id="task-two",
        ),
    ]
    solution_cells = [
        _cell(
            second_given + "print('solution two')",
            cell_id="solution-two",
            tags=["auxiliary", "real-form"],
            auxiliary=["book1:list-literal"],
            task_id="task-two",
        ),
        _cell(
            first_given + "print('solution one')",
            cell_id="solution-one",
            tags=["auxiliary", "real-form"],
            auxiliary=["book1:list-literal"],
            task_id="task-one",
        ),
    ]
    _write_notebook(
        root / "book1/units/unit-01-fixture/exercises.ipynb",
        exercise_cells,
    )
    _write_notebook(
        root / "book1/units/unit-01-fixture/solutions.ipynb",
        solution_cells,
    )

    assert [cell.metadata.py4kids_task_id for cell in exercise_cells] == [
        "task-one",
        "task-two",
    ]
    assert [cell.metadata.py4kids_task_id for cell in solution_cells] == [
        "task-two",
        "task-one",
    ]
    assert _given_bytes(exercise_cells[0].source) != _given_bytes(solution_cells[0].source)
    assert concept_scan_findings(root, "book1") == []


def test_exercise_auxiliary_outside_given_region_fails(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book1:list-literal"])
    source = (
        "# GIVEN TOOL — do not edit\nprint('ready')\n# your work begins below\nscores = [1, 2]\n"
    )
    _write_notebook(
        root / "book1/units/unit-01-fixture/exercises.ipynb",
        [
            _cell(
                source,
                cell_id="exercise-side",
                tags=["auxiliary", "given"],
                auxiliary=["book1:list-literal"],
                task_id="task-one",
            )
        ],
    )

    assert any(
        "outside the GIVEN region" in finding for finding in concept_scan_findings(root, "book1")
    )


def test_generic_k1_locality_rejects_function_after_given_region(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book1:def-function"])
    source = (
        "# GIVEN TOOL — do not edit\n"
        "print('ready')\n"
        "# your work begins below\n"
        "def helper():\n"
        "    print('outside')\n"
    )
    _write_notebook(
        root / "book1/units/unit-01-fixture/exercises.ipynb",
        [
            _cell(
                source,
                cell_id="generic-locality",
                tags=["auxiliary", "given"],
                auxiliary=["book1:def-function"],
                task_id="task-one",
            )
        ],
    )

    assert any(
        "auxiliary def-function is outside the GIVEN region" in finding
        for finding in concept_scan_findings(root, "book1")
    )


def test_generic_k1_locality_retains_set_receiver_context(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book2:set-ops"])
    source = "# GIVEN TOOL — do not edit\nvalues = set()\n# your work begins below\nvalues.add(1)\n"
    _write_notebook(
        root / "book1/units/unit-01-fixture/exercises.ipynb",
        [
            _cell(
                source,
                cell_id="set-context",
                tags=["auxiliary", "given"],
                auxiliary=["book2:set-ops"],
                task_id="task-one",
            )
        ],
    )

    findings = concept_scan_findings(root, "book1")
    assert any("auxiliary set-ops is outside the GIVEN region" in finding for finding in findings)
    assert not any("book2:set-ops is unused" in finding for finding in findings)


def test_given_region_bytes_must_match(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book1:list-literal"])
    exercise_source = (
        "# GIVEN TOOL — do not edit\nscores = [1, 2]\n# your work begins below\nprint('done')\n"
    )
    solution_source = (
        "# GIVEN TOOL — do not edit\nscores=[1,2]\n# your work begins below\nprint('done')\n"
    )
    exercise_given = _given_bytes(exercise_source)
    solution_given = _given_bytes(solution_source)
    assert exercise_given.encode() != solution_given.encode()
    assert ast.dump(ast.parse(exercise_given)) == ast.dump(ast.parse(solution_given))

    _write_notebook(
        root / "book1/units/unit-01-fixture/exercises.ipynb",
        [
            _cell(
                exercise_source,
                cell_id="exercise-side",
                tags=["auxiliary", "given"],
                auxiliary=["book1:list-literal"],
                task_id="stable-task",
            )
        ],
    )
    _write_notebook(
        root / "book1/units/unit-01-fixture/solutions.ipynb",
        [
            _cell(
                solution_source,
                cell_id="solution-side",
                tags=["auxiliary", "real-form"],
                auxiliary=["book1:list-literal"],
                task_id="stable-task",
            )
        ],
    )

    assert any(
        "GIVEN regions differ" in finding for finding in concept_scan_findings(root, "book1")
    )


def test_solution_auxiliary_cell_requires_pairing_id(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book1:list-literal"])
    source = "# GIVEN TOOL — do not edit\nscores = [1]\n# your work begins below\n"
    _write_notebook(
        root / "book1/units/unit-01-fixture/solutions.ipynb",
        [
            _cell(
                source,
                cell_id="solution-side",
                tags=["auxiliary", "real-form"],
                auxiliary=["book1:list-literal"],
            )
        ],
    )

    assert any(
        "auxiliary solution cell requires py4kids_task_id" in finding
        for finding in concept_scan_findings(root, "book1")
    )


def test_solution_real_form_without_given_region_needs_no_pairing_id(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book2:str-split"])
    _write_notebook(
        root / "book1/units/unit-01-fixture/solutions.ipynb",
        [
            _cell(
                "words = text.split()",
                cell_id="standalone-real-form",
                tags=["auxiliary", "real-form"],
                auxiliary=["book2:str-split"],
            )
        ],
    )

    assert concept_scan_findings(root, "book1") == []


def test_exercise_auxiliary_cell_requires_pairing_id(tmp_path):
    root = _scanner_root(tmp_path)
    unit = _install_fixture_shape(root, "given-pair")
    path = unit / "exercises.ipynb"
    notebook = _load_notebook(path)
    del notebook.cells[0].metadata["py4kids_task_id"]
    _save_notebook(path, notebook)

    assert any(
        "auxiliary exercise cell requires py4kids_task_id" in finding
        for finding in concept_scan_findings(root, "book1")
    )


@pytest.mark.parametrize(
    ("notebook", "role", "expected"),
    [
        ("lesson.ipynb", "given", "lesson auxiliary cell must use role demo or real-form"),
        ("solutions.ipynb", "demo", "solution auxiliary cell must use role real-form"),
    ],
)
def test_k1_role_must_match_notebook_kind(tmp_path, notebook, role, expected):
    root = _scanner_root(tmp_path, auxiliary=["book1:list-literal"])
    _write_notebook(
        root / f"book1/units/unit-01-fixture/{notebook}",
        [
            _cell(
                "scores = [1]",
                cell_id="wrong-context",
                tags=["auxiliary", role],
                auxiliary=["book1:list-literal"],
                task_id="task-one" if notebook == "solutions.ipynb" else None,
            )
        ],
    )

    assert any(expected in finding for finding in concept_scan_findings(root, "book1"))


def test_exercise_requires_given_role(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book1:list-literal"])
    source = "# GIVEN TOOL — do not edit\nscores = [1]\n# your work begins below\n"
    _write_notebook(
        root / "book1/units/unit-01-fixture/exercises.ipynb",
        [
            _cell(
                source,
                cell_id="wrong-role",
                tags=["auxiliary", "demo"],
                auxiliary=["book1:list-literal"],
                task_id="task-one",
            )
        ],
    )

    assert any(
        "exercise auxiliary cell must use role given" in finding
        for finding in concept_scan_findings(root, "book1")
    )


def _install_k2_case(root: Path, source: str, *, cell_id="counter", role="composed"):
    _set_entry(
        root,
        auxiliary=["book1:loop-counter", "book1:accumulator"],
        introduces=["print", "string-literal", "arithmetic"],
    )
    _write_k2(root, [_k2_row()])
    tags = ["auxiliary", role] if role else ["auxiliary"]
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            _cell(
                source,
                cell_id=cell_id,
                tags=tags,
                auxiliary=["book1:loop-counter", "book1:accumulator"],
            )
        ],
    )


def test_k2_exact_counter_statement_passes(tmp_path):
    root = _scanner_root(tmp_path)
    _install_k2_case(root, "n = n + 1")

    assert concept_scan_findings(root, "book1") == []


def test_k2_composed_exercise_is_exempt_from_given_region_and_pairing(tmp_path):
    root = _scanner_root(tmp_path)
    _set_entry(
        root,
        auxiliary=["book1:loop-counter", "book1:accumulator"],
        introduces=["print", "string-literal", "arithmetic"],
    )
    _write_k2(root, [_k2_row()])
    _write_notebook(
        root / "book1/units/unit-01-fixture/exercises.ipynb",
        [
            _cell(
                "n = n + 1",
                cell_id="counter",
                tags=["auxiliary", "composed"],
                auxiliary=["book1:loop-counter", "book1:accumulator"],
            )
        ],
    )

    assert concept_scan_findings(root, "book1") == []


@pytest.mark.parametrize(
    "source",
    [
        "n += 1",
        "n = 1 + n",
        "n = n - 1",
        "values[0] = values[0] + 1",
        "state.n = state.n + 1",
    ],
)
def test_k2_rejects_non_exact_counter_forms(tmp_path, source):
    root = _scanner_root(tmp_path)
    _install_k2_case(root, source)

    assert any(
        "used-but-unlisted concept accumulator" in finding
        for finding in concept_scan_findings(root, "book1")
    )


def test_k2_authorization_is_per_statement(tmp_path):
    root = _scanner_root(tmp_path)
    _install_k2_case(root, "n = n + 1\nm = 1 + m")

    assert any(
        "used-but-unlisted concept accumulator" in finding
        for finding in concept_scan_findings(root, "book1")
    )


@pytest.mark.parametrize(
    "second_statement",
    ["m: int = m + 1", "(m := m + 1)"],
    ids=["annotated-assignment", "named-expression"],
)
def test_k2_rejects_non_exact_accumulator_node_types(tmp_path, second_statement):
    root = _scanner_root(tmp_path)
    _install_k2_case(root, f"n = n + 1\n{second_statement}")

    assert any(
        "used-but-unlisted concept accumulator" in finding
        for finding in concept_scan_findings(root, "book1")
    )


def test_annotation_only_statement_is_not_an_accumulator(tmp_path):
    root = _scanner_root(tmp_path)
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [_cell("m: int", cell_id="annotation-only")],
    )

    assert concept_scan_findings(root, "book1") == []


def test_k2_row_with_missing_cell_id_fails_closed(tmp_path):
    root = _scanner_root(tmp_path)
    _install_k2_case(root, "n = n + 1")
    _write_k2(root, [_k2_row("missing-cell")])

    findings = concept_scan_findings(root, "book1")
    assert any("must name exactly one existing cell" in finding for finding in findings)
    assert any("used-but-unlisted concept accumulator" in finding for finding in findings)


def test_k2_row_for_different_existing_cell_does_not_authorize_counter(tmp_path):
    root = _scanner_root(tmp_path)
    _set_entry(
        root,
        auxiliary=["book1:loop-counter", "book1:accumulator"],
        introduces=["print", "string-literal", "arithmetic"],
    )
    _write_k2(root, [_k2_row("ordinary")])
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            _cell("print('ordinary')", cell_id="ordinary"),
            _cell(
                "n = n + 1",
                cell_id="counter",
                tags=["auxiliary", "composed"],
                auxiliary=["book1:loop-counter", "book1:accumulator"],
            ),
        ],
    )

    findings = concept_scan_findings(root, "book1")
    assert any(
        "k2 exception cell-id ordinary does not match its concepts, role, location, "
        "and exact AST form" in finding
        for finding in findings
    )
    assert any(
        "lesson.ipynb cell counter: used-but-unlisted concept accumulator" in finding
        for finding in findings
    )


def test_k2_row_with_different_concepts_is_rejected_closed(tmp_path):
    root = _scanner_root(tmp_path)
    _install_k2_case(root, "n = n + 1")
    row = _k2_row()
    row["concept-ids"] = ["book1:accumulator"]
    _write_k2(root, [row])

    findings = concept_scan_findings(root, "book1")
    assert any("k2 exception 0 is not an allowed closed-table row" in item for item in findings)
    assert any("used-but-unlisted concept accumulator" in item for item in findings)


def test_k2_cell_missing_composed_role_is_rejected_closed(tmp_path):
    root = _scanner_root(tmp_path)
    _install_k2_case(root, "n = n + 1", role="")

    findings = concept_scan_findings(root, "book1")
    assert any("borrowed cell must have exactly one auxiliary role" in item for item in findings)
    assert any(
        "k2 exception cell-id counter does not match its concepts, role, location, "
        "and exact AST form" in item
        for item in findings
    )
    assert any("used-but-unlisted concept accumulator" in item for item in findings)


def test_k2_never_authorizes_checkpoint(tmp_path):
    root = _scanner_root(tmp_path)
    path, data = _map(root)
    entry = data["entries"][0]
    entry["id"] = "checkpoint-01-fixture"
    entry["kind"] = "checkpoint"
    entry["introduces"] = ["print", "string-literal", "arithmetic"]
    entry["auxiliary"] = ["book1:loop-counter", "book1:accumulator"]
    _write_yaml(path, data)
    _write_k2(root, [_k2_row()])
    _write_notebook(
        root / "book1/checkpoints/checkpoint-01-fixture/checkpoint.ipynb",
        [
            _cell(
                "n = n + 1",
                cell_id="counter",
                tags=["auxiliary", "composed"],
                auxiliary=["book1:loop-counter", "book1:accumulator"],
            )
        ],
    )

    assert any(
        "used-but-unlisted concept accumulator" in finding
        for finding in concept_scan_findings(root, "book1")
    )


def test_k2_never_authorizes_project(tmp_path):
    root = _scanner_root(tmp_path)
    path, data = _map(root)
    entry = data["entries"][0]
    entry["id"] = "project-01-fixture"
    entry["kind"] = "project"
    entry["introduces"] = ["print", "string-literal", "arithmetic"]
    entry["auxiliary"] = ["book1:loop-counter", "book1:accumulator"]
    _write_yaml(path, data)
    _write_k2(root, [_k2_row()])
    _write_notebook(
        root / "book1/projects/project-01-fixture/brief.ipynb",
        [
            _cell(
                "n = n + 1",
                cell_id="counter",
                tags=["auxiliary", "composed"],
                auxiliary=["book1:loop-counter", "book1:accumulator"],
            )
        ],
    )

    findings = concept_scan_findings(root, "book1")
    assert any(
        "k2 exception cell-id counter does not match its concepts, role, location, "
        "and exact AST form" in item
        for item in findings
    )
    assert any("used-but-unlisted concept accumulator" in item for item in findings)


def test_unauthorized_split_keeps_untaught_method_finding(tmp_path):
    root = _scanner_root(tmp_path)
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [_cell("words = text.split()", cell_id="raw-split")],
    )

    findings = concept_scan_findings(root, "book1")
    assert any("undeclared borrowed tool book2:str-split" in item for item in findings)
    assert any("untaught method split" in item for item in findings)


def test_split_rejects_wrong_book_owner_declaration(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book1:str-split"])
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            _cell(
                "words = text.split()",
                cell_id="wrong-split-owner",
                tags=["auxiliary", "demo"],
                auxiliary=["book1:str-split"],
            )
        ],
    )

    findings = concept_scan_findings(root, "book1")
    assert any("str-split must be declared as book2:str-split" in item for item in findings)
    assert any("undeclared borrowed tool book2:str-split" in item for item in findings)


def test_markdown_solution_enforces_real_form_role_before_scope_exit(tmp_path):
    root = _scanner_root(tmp_path, auxiliary=["book2:str-split"])
    _write_notebook(
        root / "book1/units/unit-01-fixture/solutions.ipynb",
        [
            _cell(
                "```python\nwords = text.split()\n```",
                cell_id="markdown-wrong-role",
                cell_type="markdown",
                tags=["auxiliary", "demo"],
                auxiliary=["book2:str-split"],
            )
        ],
    )

    assert any(
        "solution auxiliary cell must use role real-form" in item
        for item in concept_scan_findings(root, "book1")
    )


def test_k2_rejects_float_one_literal(tmp_path):
    root = _scanner_root(tmp_path)
    _install_k2_case(root, "n = n + 1.0")

    assert any(
        "used-but-unlisted concept accumulator" in finding
        for finding in concept_scan_findings(root, "book1")
    )


def test_k2_row_pointing_at_ordinary_cell_fails_closed(tmp_path):
    root = _scanner_root(tmp_path)
    _set_entry(
        root,
        auxiliary=["book1:loop-counter", "book1:accumulator"],
        introduces=["print", "string-literal", "arithmetic"],
    )
    _write_k2(root, [_k2_row("ordinary")])
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [_cell("print('ordinary')", cell_id="ordinary")],
    )

    assert any(
        "does not match its concepts, role, location, and exact AST form" in finding
        for finding in concept_scan_findings(root, "book1")
    )


def test_k2_prevalidation_rejects_unhashable_cell_declarations_without_crash(tmp_path):
    root = _scanner_root(tmp_path)
    _set_entry(
        root,
        auxiliary=["book1:loop-counter", "book1:accumulator"],
        introduces=["print", "string-literal", "arithmetic"],
    )
    _write_k2(root, [_k2_row()])
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            _cell(
                "n = n + 1",
                cell_id="counter",
                tags=["auxiliary", "composed"],
                auxiliary=[["book1:accumulator"]],
            )
        ],
    )

    findings = concept_scan_findings(root, "book1")
    assert any("py4kids_auxiliary must be a list of qualified ids" in item for item in findings)
    assert any(
        "does not match its concepts, role, location, and exact AST form" in item
        for item in findings
    )


def _install_paired_set_ops(root: Path) -> None:
    _register_book2_set_ops(root)
    _set_entry(root, auxiliary=["book2:set-ops"])
    given = "# GIVEN TOOL — do not edit\nvalues = set()\nvalues.add(1)\n# your work begins below\n"
    _write_notebook(
        root / "book1/units/unit-01-fixture/exercises.ipynb",
        [
            _cell(
                given,
                cell_id="set-exercise",
                tags=["auxiliary", "given"],
                auxiliary=["book2:set-ops"],
                task_id="set-task",
            )
        ],
    )
    _write_notebook(
        root / "book1/units/unit-01-fixture/solutions.ipynb",
        [
            _cell(
                given,
                cell_id="set-solution",
                tags=["auxiliary", "real-form"],
                auxiliary=["book2:set-ops"],
                task_id="set-task",
            )
        ],
    )


def test_authorized_cross_book_set_ops_extends_scanner_profile(tmp_path):
    root = _scanner_root(tmp_path)
    _install_paired_set_ops(root)

    assert concept_scan_findings(root, "book1") == []


def test_cross_book_set_ops_still_fails_in_undeclared_sibling_block(tmp_path):
    root = _scanner_root(tmp_path)
    _install_paired_set_ops(root)
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [_cell("other = set()\nother.add(2)", cell_id="undeclared-set")],
    )

    assert any(
        "lesson.ipynb cell undeclared-set: undeclared borrowed tool book2:set-ops"
        in finding
        for finding in concept_scan_findings(root, "book1")
    )


def test_method_profile_authorization_is_cell_local(tmp_path):
    root = _scanner_root(tmp_path)
    _register_book2_set_ops(root)
    _set_entry(root, auxiliary=["book2:set-ops"])
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [
            _cell(
                "# GIVEN TOOL — do not edit\n"
                "values = set()\n"
                "values.remove(1)\n"
                "# your work begins below\n",
                cell_id="declared-set-method",
                tags=["auxiliary", "demo"],
                auxiliary=["book2:set-ops"],
            ),
            _cell("other.remove(2)", cell_id="undeclared-set-method"),
        ],
    )

    assert any(
        "lesson.ipynb cell undeclared-set-method: untaught method remove" in finding
        for finding in concept_scan_findings(root, "book1")
    )


def test_exercise_method_authorization_is_limited_to_given_region(tmp_path):
    root = _scanner_root(tmp_path)
    _install_paired_set_ops(root)
    given = (
        "# GIVEN TOOL — do not edit\n"
        "values = set()\n"
        "values.remove(1)\n"
        "# your work begins below\n"
    )
    _write_notebook(
        root / "book1/units/unit-01-fixture/exercises.ipynb",
        [
            _cell(
                given + "other.remove(2)\n",
                cell_id="set-exercise",
                tags=["auxiliary", "given"],
                auxiliary=["book2:set-ops"],
                task_id="set-task",
            )
        ],
    )

    assert any(
        "exercises.ipynb cell set-exercise: untaught method remove" in finding
        for finding in concept_scan_findings(root, "book1")
    )


def test_entry_defined_borrowed_method_is_not_untaught_outside_given(tmp_path):
    root = _scanner_root(tmp_path)
    _register_book2_set_ops(root)
    _set_entry(root, auxiliary=["book2:set-ops"])
    source = (
        "# GIVEN TOOL — do not edit\n"
        "values = set()\n"
        "values.add(1)\n"
        "# your work begins below\n"
        "def add(self, value):\n"
        "    pass\n"
        "item.add(2)\n"
    )
    _write_notebook(
        root / "book1/units/unit-01-fixture/exercises.ipynb",
        [
            _cell(
                source,
                cell_id="entry-defined-add",
                tags=["auxiliary", "given"],
                auxiliary=["book2:set-ops"],
                task_id="set-task",
            )
        ],
    )

    assert not any(
        "untaught method add" in finding
        for finding in concept_scan_findings(root, "book1")
    )


def test_bare_deque_identifier_is_not_a_borrowed_tool(tmp_path):
    root = _scanner_root(tmp_path)
    _register_book2_feature(root, "deque")
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [_cell("deque = 1\nprint(deque)", cell_id="deque-variable")],
    )

    assert concept_scan_findings(root, "book1") == []


def test_undeclared_deque_constructor_is_a_borrowed_tool(tmp_path):
    root = _scanner_root(tmp_path)
    _register_book2_feature(root, "deque")
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [_cell("queue = deque()", cell_id="deque-constructor")],
    )

    assert concept_scan_findings(root, "book1") == [
        (
            "FAIL: unit-01-fixture: lesson.ipynb cell deque-constructor: "
            "undeclared borrowed tool book2:deque"
        )
    ]


def test_attributed_deque_constructor_is_detected():
    used, _methods = detect(
        ast.parse("queue = collections.deque()"),
        registered_concepts={"deque"},
        profile=scanner_profile([]),
    )

    assert "deque" in used


def test_scanned_book_concept_wins_dependent_registry_collision(tmp_path):
    root = _scanner_root(tmp_path)
    _register_book2_feature(root, "deque")
    concepts_path = root / "book1/curriculum/concepts.yaml"
    concepts = yaml.safe_load(concepts_path.read_text(encoding="utf-8"))
    concepts["concepts"].append(
        {"id": "deque", "name": "deque", "category": "data", "kind": "feature"}
    )
    _write_yaml(concepts_path, concepts)
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [_cell("queue = deque()", cell_id="local-deque")],
    )

    assert concept_scan_findings(root, "book1") == [
        (
            "FAIL: unit-01-fixture: lesson.ipynb cell local-deque: "
            "used-but-unlisted concept deque"
        )
    ]


def test_dependent_book_feature_requires_cell_declaration(tmp_path):
    root = _scanner_root(tmp_path)
    _register_book2_feature(root, "comprehension")
    _write_notebook(
        root / "book1/units/unit-01-fixture/lesson.ipynb",
        [_cell("copies = [n for n in values]", cell_id="undeclared-comprehension")],
    )

    assert any(
        "lesson.ipynb cell undeclared-comprehension: undeclared borrowed tool "
        "book2:comprehension" in finding
        for finding in concept_scan_findings(root, "book1")
    )


def test_dependent_book_feature_is_authorized_in_paired_given_region(tmp_path):
    root = _scanner_root(tmp_path)
    _register_book2_feature(root, "comprehension")
    _set_entry(
        root,
        auxiliary=["book2:comprehension"],
        introduces=["print", "string-literal"],
    )
    source = (
        "# GIVEN TOOL — do not edit\n"
        "copies = [n for n in values]\n"
        "# your work begins below\n"
        "print(copies)\n"
    )
    _write_notebook(
        root / "book1/units/unit-01-fixture/exercises.ipynb",
        [
            _cell(
                source,
                cell_id="given-comprehension",
                tags=["auxiliary", "given"],
                auxiliary=["book2:comprehension"],
                task_id="comprehension-task",
            )
        ],
    )
    _write_notebook(
        root / "book1/units/unit-01-fixture/solutions.ipynb",
        [
            _cell(
                source,
                cell_id="solution-comprehension",
                tags=["auxiliary", "real-form"],
                auxiliary=["book2:comprehension"],
                task_id="comprehension-task",
            )
        ],
    )

    assert concept_scan_findings(root, "book1") == []


def test_book1_auxiliary_profile_cannot_leak_into_later_book2_v1_scan(tmp_path):
    root = _scanner_root(tmp_path)
    _install_paired_set_ops(root)

    # Non-vacuous first half: this Book-1 scan activates the set-ops profile
    # extension and needs it to authorize both set() and .add().
    assert concept_scan_findings(root, "book1") == []

    concepts_path = root / "book2/curriculum/concepts.yaml"
    concepts = yaml.safe_load(concepts_path.read_text(encoding="utf-8"))
    concepts["concepts"] = [
        concept for concept in concepts["concepts"] if concept["id"] != "set-ops"
    ]
    _write_yaml(concepts_path, concepts)
    _write_notebook(
        root / "book2/units/unit-01-split/lesson.ipynb",
        [_cell("values = set()\nvalues.add(1)", cell_id="book2-v1-set")],
    )

    assert concept_scan_findings(root, "book2") == ["FAIL: unit-01-split: untaught method add"]
