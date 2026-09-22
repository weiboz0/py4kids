from pathlib import Path

import nbformat
import pytest
import yaml

from tools.books import is_buildout, prereq_policy, variant_of
from tools.concept_scan import concept_scan_findings
from tools.curriculum import (
    global_concept_uniqueness_findings,
    introduction_findings,
    lesson_budget_findings,
    prereq_findings,
)


def _write_yaml(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _concept(concept_id: str) -> dict:
    return {"id": concept_id, "name": concept_id, "category": "data"}


def _entry(
    entry_id: str,
    *,
    kind: str = "unit",
    introduces: list[str] | None = None,
    requires: list[str] | None = None,
    practices: list[str] | None = None,
    lessons: int = 1,
) -> dict:
    return {
        "id": entry_id,
        "kind": kind,
        "title": "Synthetic fixture",
        "lessons": lessons,
        "introduces": introduces or [],
        "requires": requires or [],
        "practices": practices or [],
    }


def _write_book(root: Path, book: str, concepts: list[dict], entries: list[dict]) -> None:
    _write_yaml(
        root / book / "curriculum/concepts.yaml",
        {"concepts_version": 1, "concepts": concepts},
    )
    _write_yaml(
        root / book / "curriculum/coverage-map.yaml",
        {"map_version": 1, "entries": entries},
    )


def _write_entry_notebook(root: Path, entry_id: str, kind: str, source: str) -> None:
    directories = {"unit": "units", "checkpoint": "checkpoints", "project": "projects"}
    names = {
        "unit": "lesson.ipynb",
        "checkpoint": "checkpoint.ipynb",
        "project": "brief.ipynb",
    }
    entry_dir = root / "fast" / directories[kind] / entry_id
    entry_dir.mkdir(parents=True)
    nbformat.write(
        nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(source)]),
        entry_dir / names[kind],
    )


@pytest.fixture
def variant_pair_root(tmp_path: Path) -> Path:
    root = tmp_path / "variant-root"
    _write_yaml(
        root / "books.yaml",
        {
            "books_version": 1,
            "books": [
                {"id": "parent", "root": "parent", "depends_on": []},
                {
                    "id": "variant",
                    "root": "variant",
                    "depends_on": [],
                    "variant_of": "parent",
                },
            ],
        },
    )
    concepts = [_concept("shared-concept")]
    entries = [_entry("unit-01-fixture", introduces=["shared-concept"])]
    _write_book(root, "parent", concepts, entries)
    _write_book(root, "variant", concepts, entries)
    return root


@pytest.fixture
def fastforward_root(tmp_path: Path) -> Path:
    root = tmp_path / "fastforward-root"
    _write_yaml(
        root / "books.yaml",
        {
            "books_version": 1,
            "books": [
                {
                    "id": "fast",
                    "root": "fast",
                    "depends_on": [],
                    "prereq_policy": "fastforward",
                    "concept_minimum": 1,
                    "lesson_budget": [1, 10],
                }
            ],
        },
    )
    _write_book(
        root,
        "fast",
        [_concept("variable"), _concept("arithmetic")],
        [
            _entry("unit-01-fixture", introduces=["variable"]),
            _entry("checkpoint-01-fixture", kind="checkpoint", practices=["variable"]),
            _entry("project-01-fixture", kind="project", practices=["variable"]),
            _entry(
                "unit-02-fixture",
                introduces=["arithmetic"],
                requires=["variable"],
            ),
        ],
    )
    return root


@pytest.fixture
def buildout_root(tmp_path: Path) -> Path:
    root = tmp_path / "buildout-root"
    _write_yaml(
        root / "books.yaml",
        {
            "books_version": 1,
            "books": [
                {
                    "id": "build",
                    "root": "build",
                    "depends_on": [],
                    "buildout": True,
                    "concept_minimum": 1,
                    "lesson_budget": [2, 3],
                }
            ],
        },
    )
    _write_book(
        root,
        "build",
        [_concept("first"), _concept("second")],
        [
            _entry("unit-01-fixture", introduces=["first"]),
            _entry("unit-02-fixture", introduces=["second"]),
        ],
    )
    return root


def test_book_policy_readers_use_explicit_registry_values(
    variant_pair_root: Path,
    fastforward_root: Path,
    buildout_root: Path,
) -> None:
    assert variant_of(variant_pair_root, "variant") == "parent"
    assert variant_of(variant_pair_root, "parent") is None
    assert prereq_policy(fastforward_root, "fast") == "fastforward"
    assert prereq_policy(variant_pair_root, "parent") is None
    assert is_buildout(buildout_root, "build") is True
    assert is_buildout(fastforward_root, "fast") is False


def test_variant_pair_may_coown_identical_concept_catalog(
    variant_pair_root: Path,
) -> None:
    assert global_concept_uniqueness_findings(variant_pair_root) == []


def test_variant_exemption_does_not_allow_third_owner(variant_pair_root: Path) -> None:
    books_path = variant_pair_root / "books.yaml"
    books = yaml.safe_load(books_path.read_text(encoding="utf-8"))
    books["books"].append({"id": "third", "root": "third", "depends_on": []})
    _write_yaml(books_path, books)
    _write_book(
        variant_pair_root,
        "third",
        [_concept("shared-concept")],
        [_entry("unit-01-fixture", introduces=["shared-concept"])],
    )

    assert global_concept_uniqueness_findings(variant_pair_root) == [
        (
            "FAIL: books: concept id 'shared-concept' is defined in multiple books: "
            "['parent', 'third', 'variant']"
        )
    ]


def test_variant_catalog_must_match_parent(variant_pair_root: Path) -> None:
    path = variant_pair_root / "variant/curriculum/concepts.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["concepts"][0]["name"] = "Different name"
    _write_yaml(path, data)

    assert global_concept_uniqueness_findings(variant_pair_root) == [
        "FAIL: books: variant 'variant' concepts.yaml differs from parent 'parent'"
    ]


def test_buildout_allows_catalog_concept_to_remain_unintroduced(
    buildout_root: Path,
) -> None:
    path = buildout_root / "build/curriculum/coverage-map.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["entries"][1]["introduces"] = []
    _write_yaml(path, data)

    assert introduction_findings(buildout_root, "build") == []


def test_buildout_allows_lesson_total_below_lower_bound(buildout_root: Path) -> None:
    path = buildout_root / "build/curriculum/coverage-map.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["entries"] = data["entries"][:1]
    _write_yaml(path, data)

    assert lesson_budget_findings(buildout_root, "build") == []


def test_buildout_still_rejects_duplicate_introduction(buildout_root: Path) -> None:
    path = buildout_root / "build/curriculum/coverage-map.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["entries"][1]["introduces"].append("first")
    _write_yaml(path, data)

    assert introduction_findings(buildout_root, "build") == [
        "FAIL: build: concept introduced twice"
    ]


def test_buildout_still_rejects_lesson_total_above_upper_bound(
    buildout_root: Path,
) -> None:
    path = buildout_root / "build/curriculum/coverage-map.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["entries"][0]["lessons"] = 3
    _write_yaml(path, data)

    assert lesson_budget_findings(buildout_root, "build") == [
        "FAIL: build: lesson budget 4 outside 2-3"
    ]


def test_fastforward_still_rejects_forward_requires(fastforward_root: Path) -> None:
    path = fastforward_root / "fast/curriculum/coverage-map.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["entries"][0]["requires"] = ["arithmetic"]
    _write_yaml(path, data)

    assert prereq_findings(fastforward_root, "fast") == [
        (
            "FAIL: fast: unit-01-fixture uses concepts not yet introduced: "
            "['arithmetic']"
        )
    ]


def test_fastforward_allows_forward_practices(fastforward_root: Path) -> None:
    path = fastforward_root / "fast/curriculum/coverage-map.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["entries"][0]["practices"] = ["arithmetic"]
    _write_yaml(path, data)

    assert prereq_findings(fastforward_root, "fast") == []


def test_fastforward_scan_relaxes_units_only_and_keeps_method_checks(
    fastforward_root: Path,
) -> None:
    source = "value = 1 + 2\nthing.mystery()"
    for entry_id, kind in (
        ("unit-01-fixture", "unit"),
        ("checkpoint-01-fixture", "checkpoint"),
        ("project-01-fixture", "project"),
    ):
        _write_entry_notebook(fastforward_root, entry_id, kind, source)

    assert set(concept_scan_findings(fastforward_root, "fast")) == {
        "FAIL: unit-01-fixture: untaught method mystery",
        "FAIL: checkpoint-01-fixture: used-but-unlisted concept arithmetic",
        "FAIL: checkpoint-01-fixture: untaught method mystery",
        "FAIL: project-01-fixture: used-but-unlisted concept arithmetic",
        "FAIL: project-01-fixture: untaught method mystery",
    }
