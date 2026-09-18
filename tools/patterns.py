"""Book 1 algorithm-pattern marker and spiral checks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import nbformat
import yaml

from tools.books import book_path
from tools.concept_scan import entry_notebooks
from tools.notebooks import tags

EXERCISE_HEADING = re.compile(r"^## Exercise \d+\b", re.MULTILINE)
PATTERN_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
MARKER_LIKE = re.compile(r"<!--\s*pattern\b\s*:?\s*([^<>]*?)\s*-->")


def _fail(scope: str, detail: str) -> str:
    return f"FAIL: {scope}: {detail}"


@dataclass(frozen=True)
class PatternBookData:
    directory: Path
    concepts: list[dict]
    entries: list[dict]
    techniques: dict[str, dict]
    findings: tuple[str, ...]


def _read_yaml(path: Path, label: str) -> tuple[object | None, list[str]]:
    if not path.is_file():
        return None, [_fail("book1", f"{label} does not exist")]
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")), []
    except yaml.YAMLError as error:
        return None, [_fail("book1", f"{label} is not valid YAML: {error}")]


def load_pattern_book(root: Path) -> PatternBookData:
    """Load Book 1 pattern inputs without converting invalid data into an empty set."""
    directory = book_path(root, "book1")
    concepts_data, findings = _read_yaml(directory / "curriculum/concepts.yaml", "concepts.yaml")
    map_data, map_findings = _read_yaml(
        directory / "curriculum/coverage-map.yaml", "coverage-map.yaml"
    )
    findings.extend(map_findings)
    concepts: list[dict] = []
    entries: list[dict] = []
    if concepts_data is not None:
        if not isinstance(concepts_data, dict):
            findings.append(_fail("book1", "concepts.yaml must be a mapping"))
        elif not isinstance(concepts_data.get("concepts"), list):
            findings.append(_fail("book1", "concepts must be a list"))
        else:
            raw_concepts = concepts_data["concepts"]
            malformed = [
                index for index, concept in enumerate(raw_concepts) if not isinstance(concept, dict)
            ]
            findings.extend(
                _fail("book1", f"concept entry {index} must be a mapping") for index in malformed
            )
            if not malformed:
                concepts = raw_concepts
    if map_data is not None:
        if not isinstance(map_data, dict):
            findings.append(_fail("book1", "coverage-map.yaml must be a mapping"))
        elif not isinstance(map_data.get("entries"), list):
            findings.append(_fail("book1", "coverage-map entries must be a list"))
        else:
            raw_entries = map_data["entries"]
            malformed = [
                index for index, entry in enumerate(raw_entries) if not isinstance(entry, dict)
            ]
            findings.extend(
                _fail("book1", f"coverage-map entry {index} must be a mapping")
                for index in malformed
            )
            if not malformed:
                entries = raw_entries
    techniques = {
        concept["id"]: concept
        for concept in concepts
        if isinstance(concept, dict)
        and concept.get("kind") == "technique"
        and isinstance(concept.get("id"), str)
    }
    return PatternBookData(directory, concepts, entries, techniques, tuple(findings))


def _entry_dir(book_dir: Path, entry: dict) -> Path:
    parent = {
        "unit": "units",
        "checkpoint": "checkpoints",
        "project": "projects",
    }.get(entry.get("kind"), "")
    return book_dir / parent / str(entry.get("id", ""))


def _learner_notebooks(entry_dir: Path, kind: str) -> list[Path]:
    names = set(
        {
            "unit": ("lesson.ipynb", "exercises.ipynb"),
            "checkpoint": ("checkpoint.ipynb",),
            "project": ("brief.ipynb",),
        }.get(kind, ())
    )
    return [path for path in entry_notebooks(entry_dir, kind) if path.name in names]


def _marker_positions(notebook, pattern_id: str) -> list[int]:
    exact = f"<!-- pattern: {pattern_id} -->"
    return [
        cell_index
        for cell_index, cell in enumerate(notebook.cells)
        if cell.cell_type == "markdown"
        for _ in range(cell.source.count(exact))
    ]


@dataclass(frozen=True)
class PatternMarker:
    pattern_id: str
    cell_index: int
    exact: bool


def _markers(notebook) -> list[PatternMarker]:
    return [
        PatternMarker(
            pattern_id=match.group(1).strip(),
            cell_index=cell_index,
            exact=(
                PATTERN_ID.fullmatch(match.group(1).strip()) is not None
                and match.group(0) == f"<!-- pattern: {match.group(1).strip()} -->"
            ),
        )
        for cell_index, cell in enumerate(notebook.cells)
        if cell.cell_type == "markdown"
        for match in MARKER_LIKE.finditer(cell.source)
    ]


@dataclass(frozen=True)
class ExerciseLink:
    heading_cell: object
    code_cell: object

    @property
    def is_stretch(self) -> bool:
        return "stretch" in tags(self.heading_cell) or "stretch" in tags(self.code_cell)


def _exercise_link(notebook, marker_index: int) -> ExerciseLink | None:
    heading_index = marker_index + 1
    if heading_index >= len(notebook.cells):
        return None
    heading = notebook.cells[heading_index]
    if heading.cell_type != "markdown" or not EXERCISE_HEADING.search(heading.source):
        return None
    for cell in notebook.cells[heading_index + 1 :]:
        if cell.cell_type == "markdown" and EXERCISE_HEADING.search(cell.source):
            return None
        if cell.cell_type == "code":
            return ExerciseLink(heading, cell)
    return None


def _expected_markers(entry: dict, techniques: set[str]) -> dict[str, set[str]]:
    introduced = set(entry.get("introduces", [])) & techniques
    practiced = set(entry.get("practices", [])) & techniques
    if entry.get("kind") == "unit":
        expected = {"exercises.ipynb": introduced | practiced}
        if introduced:
            expected["lesson.ipynb"] = introduced
        return expected
    if entry.get("kind") == "project":
        return {"brief.ipynb": introduced | practiced}
    return {}


def _manifest_technique_tags(entry_dir: Path, techniques: set[str]):
    manifest, _findings = _read_yaml(entry_dir / "manifest.yaml", "manifest.yaml")
    if not isinstance(manifest, dict) or not isinstance(manifest.get("concepts"), dict):
        return None
    concepts = manifest["concepts"]
    return {
        field: set(concepts.get(field, [])) & techniques
        if isinstance(concepts.get(field), list)
        else set()
        for field in ("introduces", "practices")
    }


def pattern_marker_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    """Validate Book 1 technique tags, marker cardinality, and exercise adjacency."""
    del unit
    if book != "book1":
        return []
    data = load_pattern_book(root)
    if data.findings:
        return list(data.findings)
    book_dir = data.directory
    entries = data.entries
    techniques = set(data.techniques)
    findings: list[str] = []

    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            continue
        entry_id = entry["id"]
        kind = entry.get("kind")
        entry_dir = _entry_dir(book_dir, entry)
        if not entry_dir.is_dir():
            continue
        map_tags = {
            field: set(entry.get(field, [])) & techniques
            if isinstance(entry.get(field), list)
            else set()
            for field in ("introduces", "practices")
        }
        manifest_tags = _manifest_technique_tags(entry_dir, techniques)
        if manifest_tags is None or manifest_tags != map_tags:
            findings.append(_fail(entry_id, "manifest technique tags differ from coverage map"))

        notebooks = {
            path.name: nbformat.read(path, as_version=4)
            for path in _learner_notebooks(entry_dir, str(kind))
        }
        all_markers = [
            (marker, name) for name, notebook in notebooks.items() for marker in _markers(notebook)
        ]
        if kind == "checkpoint":
            if (
                map_tags["introduces"]
                or map_tags["practices"]
                or (
                    manifest_tags is not None
                    and (manifest_tags["introduces"] or manifest_tags["practices"])
                )
            ):
                findings.append(_fail(entry_id, "checkpoint may not carry technique tags"))
            if all_markers:
                findings.append(_fail(entry_id, "checkpoint may not carry pattern markers"))
            continue

        expected = _expected_markers(entry, techniques)
        for marker, name in all_markers:
            pattern_id = marker.pattern_id
            if not marker.exact:
                findings.append(
                    _fail(entry_id, f"{name} has invalid pattern marker for {pattern_id!r}")
                )
            elif pattern_id not in techniques:
                findings.append(
                    _fail(entry_id, f"{name} has unknown or non-technique marker {pattern_id!r}")
                )
            elif pattern_id not in expected.get(name, set()):
                findings.append(
                    _fail(entry_id, f"{name} has marker for untagged technique {pattern_id!r}")
                )

        for name, pattern_ids in expected.items():
            notebook = notebooks.get(name)
            for pattern_id in sorted(pattern_ids):
                positions = [] if notebook is None else _marker_positions(notebook, pattern_id)
                if len(positions) != 1:
                    findings.append(
                        _fail(
                            entry_id,
                            f"{name} needs exactly one marker for {pattern_id!r}; found {len(positions)}",
                        )
                    )
                    continue
                marker_index = positions[0]
                marker_cell = notebook.cells[marker_index]
                exact = f"<!-- pattern: {pattern_id} -->"
                if name == "exercises.ipynb":
                    if marker_cell.source.strip() != exact:
                        findings.append(
                            _fail(
                                entry_id, f"{name} marker for {pattern_id!r} must be comment-only"
                            )
                        )
                    if _exercise_link(notebook, marker_index) is None:
                        findings.append(
                            _fail(
                                entry_id,
                                f"{name} marker must immediately precede an Exercise heading "
                                f"with a code cell for {pattern_id!r}",
                            )
                        )
                elif marker_cell.source.strip() == exact:
                    findings.append(
                        _fail(entry_id, f"{name} marker for {pattern_id!r} must live in prose")
                    )
    return findings


def _locus_is_core(book_dir: Path, entry: dict, pattern_id: str) -> tuple[bool, str | None]:
    entry_dir = _entry_dir(book_dir, entry)
    if entry.get("kind") == "unit":
        path = entry_dir / "exercises.ipynb"
        if not path.is_file():
            return False, "does not map to a marked exercise"
        notebook = nbformat.read(path, as_version=4)
        positions = _marker_positions(notebook, pattern_id)
        if len(positions) != 1:
            return False, "does not map to exactly one marked exercise"
        link = _exercise_link(notebook, positions[0])
        if link is None:
            return False, "does not map to an adjacent exercise"
        if link.is_stretch:
            return False, "has a stretch embodiment"
        return True, None
    if entry.get("kind") == "project":
        path = entry_dir / "brief.ipynb"
        if not path.is_file():
            return False, "does not map to project prose"
        notebook = nbformat.read(path, as_version=4)
        positions = _marker_positions(notebook, pattern_id)
        if len(positions) != 1:
            return False, "does not map to exactly one project marker"
        cell = notebook.cells[positions[0]]
        if cell.source.strip() == f"<!-- pattern: {pattern_id} -->":
            return False, "project marker does not live in prose"
        if "stretch" in tags(cell):
            return False, "has a stretch embodiment"
        return True, None
    return False, "is not a unit or project locus"


def technique_spiral_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    """Enforce the Book 1 technique home and three-core-practice spiral."""
    del unit
    if book != "book1":
        return []
    data = load_pattern_book(root)
    if data.findings:
        return list(data.findings)
    book_dir = data.directory
    entries = data.entries
    techniques = data.techniques
    findings: list[str] = []
    capstones = [
        index
        for index, entry in enumerate(entries)
        if entry.get("kind") == "project"
        and isinstance(entry.get("id"), str)
        and entry["id"].startswith("project-02-")
    ]
    if len(capstones) != 1:
        return [
            _fail(
                "book1",
                f"project-02 capstone boundary must appear exactly once; found {len(capstones)}",
            )
        ]
    capstone_index = capstones[0]

    for pattern_id in techniques:
        homes = [
            (index, entry)
            for index, entry in enumerate(entries)
            if isinstance(entry, dict) and pattern_id in (entry.get("introduces", []) or [])
        ]
        if len(homes) != 1:
            findings.append(
                _fail(pattern_id, f"introduced {len(homes)} times (expected exactly 1)")
            )
        home_index = homes[0][0] if homes else None
        practices = [
            (index, entry)
            for index, entry in enumerate(entries)
            if isinstance(entry, dict) and pattern_id in (entry.get("practices", []) or [])
        ]
        if home_index is not None:
            for index, entry in practices:
                if index < home_index:
                    findings.append(
                        _fail(pattern_id, f"practice before home in {entry.get('id', '?')}")
                    )

        for _index, home in homes:
            core, reason = _locus_is_core(book_dir, home, pattern_id)
            if not core:
                findings.append(_fail(str(home.get("id", "?")), f"{pattern_id}: {reason}"))

        core_practices = 0
        for index, entry in practices:
            if index >= capstone_index or entry.get("kind") == "checkpoint":
                continue
            core, reason = _locus_is_core(book_dir, entry, pattern_id)
            if not core:
                findings.append(_fail(str(entry.get("id", "?")), f"{pattern_id}: {reason}"))
                continue
            if home_index is None or index > home_index:
                core_practices += 1
        if core_practices < 3:
            findings.append(
                _fail(
                    pattern_id,
                    f"{core_practices} core pre-capstone non-checkpoint practices (<3)",
                )
            )
    return findings
