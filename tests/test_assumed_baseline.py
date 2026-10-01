import re
from pathlib import Path

import nbformat
import pytest
import yaml

from tools import books
from tools.concept_scan import concept_scan_findings
from tools.curriculum import (
    checkpoint_findings,
    coverage_findings,
    practice_findings,
    prereq_findings,
)


def _write_yaml(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _entry(
    entry_id: str,
    *,
    kind: str = "unit",
    introduces: list[str] | None = None,
    requires: list[str] | None = None,
    practices: list[str] | None = None,
    map_version: int = 1,
) -> dict:
    entry = {
        "id": entry_id,
        "kind": kind,
        "title": "Synthetic fixture",
        "lessons": 1,
        "introduces": introduces or [],
        "requires": requires or [],
        "practices": practices or [],
    }
    if map_version == 2:
        entry["auxiliary"] = []
    return entry


def _write_map(root: Path, map_version: int, entries: list[dict]) -> None:
    _write_yaml(
        root / "advanced/curriculum/coverage-map.yaml",
        {"map_version": map_version, "entries": entries},
    )
    rows = "\n".join(
        f"| `{entry['id']}` | {entry['kind']} | {entry['lessons']} |" for entry in entries
    )
    (root / "advanced/syllabus.md").write_text(rows + "\n", encoding="utf-8")


@pytest.fixture(params=[1, 2], ids=["map-v1", "map-v2"])
def baseline_root(tmp_path: Path, request: pytest.FixtureRequest) -> tuple[Path, int]:
    map_version = request.param
    _write_yaml(
        tmp_path / "books.yaml",
        {
            "books_version": 2,
            "books": [
                {
                    "id": "base",
                    "root": "base",
                    "depends_on": [],
                    "concept_minimum": 1,
                    "lesson_budget": [1, 10],
                },
                {
                    "id": "advanced",
                    "root": "advanced",
                    "depends_on": ["base"],
                    "concept_minimum": 1,
                    "lesson_budget": [1, 10],
                    "patterns": map_version == 2,
                },
            ],
        },
    )
    _write_yaml(
        tmp_path / "base/curriculum/concepts.yaml",
        {
            "concepts_version": 1,
            "concepts": [{"id": "base-feature", "name": "Base", "category": "data"}],
        },
    )
    _write_yaml(
        tmp_path / "base/curriculum/coverage-map.yaml",
        {
            "map_version": 1,
            "entries": [
                _entry("unit-01-base", introduces=["base-feature"]),
            ],
        },
    )
    _write_yaml(
        tmp_path / "advanced/curriculum/concepts.yaml",
        {
            "concepts_version": 1,
            "concepts": [
                {"id": "own-concept", "name": "Own concept", "category": "data"}
            ],
        },
    )
    _write_yaml(
        tmp_path / "advanced/curriculum/baseline.yaml",
        {
            "baseline_version": 1,
            "entries": [{"id": "arithmetic", "name": "Arithmetic"}],
        },
    )
    entries = [
        _entry(
            "unit-01-advanced",
            introduces=["own-concept"],
            requires=["arithmetic"],
            map_version=map_version,
        )
    ]
    _write_map(tmp_path, map_version, entries)
    unit = tmp_path / "advanced/units/unit-01-advanced"
    unit.mkdir(parents=True)
    nbformat.write(
        nbformat.v4.new_notebook(
            cells=[nbformat.v4.new_code_cell("total = 1 + 2", id="baseline-arithmetic")]
        ),
        unit / "lesson.ipynb",
    )
    return tmp_path, map_version


def test_assumed_and_known_baseline_are_opt_in_and_union_dependencies(
    baseline_root: tuple[Path, int],
) -> None:
    root, _ = baseline_root

    assert books.assumed_baseline(root, "advanced") == {"arithmetic"}
    assert books.known_baseline(root, "advanced") == {"base-feature", "arithmetic"}
    assert books.dependency_baseline(root, "advanced") == {"base-feature"}
    assert books.assumed_baseline(root, "base") == set()


def test_assumed_concept_is_legal_in_requires_without_coverage_obligation(
    baseline_root: tuple[Path, int],
) -> None:
    root, _ = baseline_root

    assert prereq_findings(root, "advanced") == []
    assert coverage_findings(root, "advanced") == []


def test_concept_scan_allows_assumed_concept_in_v1_and_v2(
    baseline_root: tuple[Path, int],
) -> None:
    root, map_version = baseline_root
    _write_map(
        root,
        map_version,
        [
            _entry(
                "unit-01-advanced",
                introduces=["own-concept"],
                map_version=map_version,
            )
        ],
    )

    assert concept_scan_findings(root, "advanced") == []


def test_concept_scan_allows_declared_library_methods_in_v1_and_v2(
    baseline_root: tuple[Path, int],
) -> None:
    root, _ = baseline_root
    baseline_path = root / "advanced/curriculum/baseline.yaml"
    baseline = yaml.safe_load(baseline_path.read_text(encoding="utf-8"))
    baseline["library_methods"] = ["read_csv", "groupby"]
    _write_yaml(baseline_path, baseline)
    unit = root / "advanced/units/unit-01-advanced"
    nbformat.write(
        nbformat.v4.new_notebook(
            cells=[
                nbformat.v4.new_code_cell(
                    "frame = pd.read_csv(path)\ngroups = frame.groupby(column)",
                    id="baseline-library-methods",
                )
            ]
        ),
        unit / "lesson.ipynb",
    )

    assert books.assumed_library_methods(root, "advanced") == {"read_csv", "groupby"}
    assert concept_scan_findings(root, "advanced") == []


def test_concept_scan_still_flags_undeclared_library_method(
    baseline_root: tuple[Path, int],
) -> None:
    root, _ = baseline_root
    unit = root / "advanced/units/unit-01-advanced"
    nbformat.write(
        nbformat.v4.new_notebook(
            cells=[
                nbformat.v4.new_code_cell(
                    "result = library.undeclared_method()",
                    id="undeclared-library-method",
                )
            ]
        ),
        unit / "lesson.ipynb",
    )

    assert any(
        "untaught method undeclared_method" in finding
        for finding in concept_scan_findings(root, "advanced")
    )


def test_non_baseline_concept_is_still_flagged(
    baseline_root: tuple[Path, int],
) -> None:
    root, _ = baseline_root
    _write_yaml(
        root / "advanced/curriculum/baseline.yaml",
        {"baseline_version": 1, "entries": []},
    )

    assert prereq_findings(root, "advanced") == [
        "FAIL: advanced: unit-01-advanced uses concepts not yet introduced: ['arithmetic']"
    ]
    assert any(
        "requires references unknown concepts: ['arithmetic']" in finding
        for finding in coverage_findings(root, "advanced")
    )
    _write_map(
        root,
        baseline_root[1],
        [
            _entry(
                "unit-01-advanced",
                introduces=["own-concept"],
                map_version=baseline_root[1],
            )
        ],
    )
    assert any(
        "used-but-unlisted concept arithmetic" in finding
        for finding in concept_scan_findings(root, "advanced")
    )


def test_unit_practicing_assumed_baseline_is_flagged(
    baseline_root: tuple[Path, int],
) -> None:
    root, map_version = baseline_root
    entries = [
        _entry(
            "unit-01-advanced",
            introduces=["own-concept"],
            requires=["arithmetic"],
            practices=["arithmetic"],
            map_version=map_version,
        )
    ]
    _write_map(root, map_version, entries)

    assert practice_findings(root, "advanced") == [
        "FAIL: advanced: unit-01-advanced practices assumed baseline concepts: ['arithmetic']"
    ]


def test_project_practicing_assumed_baseline_is_flagged(
    baseline_root: tuple[Path, int],
) -> None:
    root, map_version = baseline_root
    entries = [
        _entry(
            "unit-01-advanced",
            introduces=["own-concept"],
            requires=["arithmetic"],
            map_version=map_version,
        ),
        _entry(
            "project-01-advanced",
            kind="project",
            practices=["arithmetic"],
            map_version=map_version,
        ),
    ]
    _write_map(root, map_version, entries)

    assert practice_findings(root, "advanced") == [
        "FAIL: advanced: project-01-advanced practices assumed baseline concepts: ['arithmetic']"
    ]


def test_checkpoint_practicing_assumed_baseline_is_flagged(
    baseline_root: tuple[Path, int],
) -> None:
    root, map_version = baseline_root
    entries = [
        _entry(
            "checkpoint-01-advanced",
            kind="checkpoint",
            practices=["arithmetic"],
            map_version=map_version,
        ),
        _entry(
            "unit-01-advanced",
            introduces=["own-concept"],
            requires=["arithmetic"],
            map_version=map_version,
        ),
    ]
    _write_map(root, map_version, entries)

    assert checkpoint_findings(root, "advanced") == [
        (
            "FAIL: advanced: checkpoint-01-advanced practices assumed baseline concepts: "
            "['arithmetic']"
        )
    ]


def test_baseline_id_may_not_be_introduced_by_a_dependency(
    baseline_root: tuple[Path, int],
) -> None:
    root, _ = baseline_root
    # ``base`` (a dependency of ``advanced``) introduces ``base-feature``; declaring it "assumed"
    # in advanced is a contradiction — it is taught upstream, not an assessable-no-credit baseline.
    _write_yaml(
        root / "advanced/curriculum/baseline.yaml",
        {"baseline_version": 1, "entries": [{"id": "base-feature", "name": "Base feature"}]},
    )

    with pytest.raises(
        ValueError,
        match=r"assumed baseline ids are introduced by a dependency: \['base-feature'\]",
    ):
        books.assumed_baseline(root, "advanced")


@pytest.mark.parametrize(
    ("contents", "message"),
    [
        ("[not, a, mapping]\n", "baseline.yaml must be a mapping"),
        ("baseline_version: [\n", "baseline.yaml is not valid YAML"),
        ("baseline_version: 2\nentries: []\n", "baseline_version must be 1"),
        ("baseline_version: 1\nentries: {}\n", "baseline entries must be a list"),
        (
            "baseline_version: 1\nentries:\n  - arithmetic\n",
            "baseline entry 0 must be a mapping",
        ),
        (
            (
                "baseline_version: 1\nentries:\n  - id: arithmetic\n    name: Arithmetic\n"
                "    extra: nope\n"
            ),
            "bad baseline keys in entry 0",
        ),
        (
            "baseline_version: 1\nentries:\n  - id: 7\n    name: Arithmetic\n",
            "baseline entry 0 id and name must be strings",
        ),
        (
            "baseline_version: 1\nentries:\n  - id: arithmetic\n    name: 7\n",
            "baseline entry 0 id and name must be strings",
        ),
        (
            (
                "baseline_version: 1\nentries:\n  - id: arithmetic\n    name: One\n"
                "  - id: arithmetic\n    name: Two\n"
            ),
            "duplicate baseline ids: ['arithmetic']",
        ),
        (
            "baseline_version: 1\nentries:\n  - id: Not_Kebab\n    name: Bad\n",
            "non-kebab baseline id: 'Not_Kebab'",
        ),
        (
            "baseline_version: 1\nentries: []\nextra: nope\n",
            (
                "baseline.yaml keys must be exactly ['baseline_version', 'entries'] "
                "with optional 'library_methods'"
            ),
        ),
    ],
)
def test_malformed_baseline_fails_closed(
    baseline_root: tuple[Path, int], contents: str, message: str
) -> None:
    root, _ = baseline_root
    (root / "advanced/curriculum/baseline.yaml").write_text(contents, encoding="utf-8")

    with pytest.raises(ValueError, match=re.escape(message)):
        books.assumed_baseline(root, "advanced")


@pytest.mark.parametrize(
    ("library_methods", "message"),
    [
        ({"read_csv": True}, "library_methods must be a list"),
        (["read_csv", 7], "library method 1 must be a string"),
        (["not-valid"], "library method 0 must be an identifier: 'not-valid'"),
        (["read_csv", "read_csv"], "duplicate library methods: ['read_csv']"),
    ],
)
def test_malformed_library_methods_fail_closed(
    baseline_root: tuple[Path, int], library_methods: object, message: str
) -> None:
    root, _ = baseline_root
    _write_yaml(
        root / "advanced/curriculum/baseline.yaml",
        {
            "baseline_version": 1,
            "entries": [{"id": "arithmetic", "name": "Arithmetic"}],
            "library_methods": library_methods,
        },
    )

    with pytest.raises(books.BaselineConfigError, match=re.escape(message)):
        books.assumed_library_methods(root, "advanced")


def test_baseline_id_may_not_also_be_owned_by_the_book(
    baseline_root: tuple[Path, int],
) -> None:
    root, _ = baseline_root
    _write_yaml(
        root / "advanced/curriculum/concepts.yaml",
        {
            "concepts_version": 1,
            "concepts": [
                {"id": "arithmetic", "name": "Arithmetic", "category": "data"}
            ],
        },
    )

    with pytest.raises(
        ValueError,
        match="assumed baseline ids also appear in concepts.yaml: \\['arithmetic'\\]",
    ):
        books.assumed_baseline(root, "advanced")
