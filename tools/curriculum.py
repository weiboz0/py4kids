"""Curriculum rules promoted from the Plan 002/004 interim tests."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from tools.books import (
    book_entries,
    book_path,
    concept_minimum,
    dependency_baseline,
    lesson_budget,
)

CATEGORIES = {
    "io",
    "data",
    "strings",
    "control",
    "loops",
    "functions",
    "collections",
    "files",
    "oop",
    "graphics",
    "modules",
    "search",
    "sorting",
    "data-structures",
    "graphs",
    "number-theory",
    "techniques",
}
ENTRY_PATTERNS = {
    "unit": r"^unit-[0-9]{2}-[a-z0-9-]+$",
    "project": r"^project-[0-9]{2}-[a-z0-9-]+$",
    "checkpoint": r"^checkpoint-[0-9]{2}-[a-z0-9-]+$",
}


def _fail(book: str, detail: str) -> str:
    return f"FAIL: {book}: {detail}"


def _curriculum(root: Path, book: str) -> Path:
    return book_path(root, book) / "curriculum"


def global_concept_uniqueness_findings(root: Path) -> list[str]:
    """Report concept ids defined by more than one registered book."""
    owners: dict[str, set[str]] = {}
    for registered_book in book_entries(root):
        path = _curriculum(root, registered_book) / "concepts.yaml"
        if not path.is_file():
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("concepts"), list):
            continue
        for concept in data["concepts"]:
            if isinstance(concept, dict) and isinstance(concept.get("id"), str):
                owners.setdefault(concept["id"], set()).add(registered_book)
    return [
        _fail(
            "books",
            f"concept id {concept_id!r} is defined in multiple books: {sorted(books)}",
        )
        for concept_id, books in sorted(owners.items())
        if len(books) > 1
    ]


def _concept_data(root: Path, book: str):
    return yaml.safe_load((_curriculum(root, book) / "concepts.yaml").read_text(encoding="utf-8"))


def _map_data(root: Path, book: str):
    return yaml.safe_load(
        (_curriculum(root, book) / "coverage-map.yaml").read_text(encoding="utf-8")
    )


def _has_duplicates(values: list[object]) -> bool:
    return any(value in values[:index] for index, value in enumerate(values))


def concepts_schema_findings(root: Path, book: str) -> list[str]:
    data = _concept_data(root, book)
    if not isinstance(data, dict):
        return [_fail(book, "concepts.yaml must be a mapping")]
    concepts = data.get("concepts", [])
    if not isinstance(concepts, list):
        return [_fail(book, "concepts must be a list")]
    malformed = [index for index, concept in enumerate(concepts) if not isinstance(concept, dict)]
    if malformed:
        return [_fail(book, f"concept entry {index} must be a mapping") for index in malformed]

    findings = []
    if data.get("concepts_version") != 1:
        findings.append(_fail(book, "concepts_version must be 1"))
    minimum = concept_minimum(root, book)
    if len(concepts) < minimum:
        findings.append(_fail(book, f"concept registry has fewer than {minimum} concepts"))
    ids = [concept.get("id") for concept in concepts]
    if _has_duplicates(ids):
        findings.append(_fail(book, "duplicate concept ids"))
    for concept in concepts:
        if set(concept) not in ({"id", "name", "category"}, {"id", "name", "category", "kind"}):
            findings.append(_fail(book, f"bad concept keys in {concept.get('id', concept)}"))
            continue
        if "kind" in concept and (
            not isinstance(concept["kind"], str)
            or concept["kind"] not in {"feature", "technique"}
        ):
            findings.append(
                _fail(book, f"bad concept kind in {concept['id']}: {concept['kind']}")
            )
        if not isinstance(concept["category"], str) or concept["category"] not in CATEGORIES:
            findings.append(_fail(book, f"unknown category: {concept['category']}"))
        if not isinstance(concept["id"], str) or not re.fullmatch(
            r"[a-z0-9]+(-[a-z0-9]+)*", concept["id"]
        ):
            findings.append(_fail(book, f"non-kebab concept id: {concept['id']!r}"))
    return findings


def map_schema_findings(root: Path, book: str) -> list[str]:
    data = _map_data(root, book)
    if not isinstance(data, dict):
        return [_fail(book, "coverage-map.yaml must be a mapping")]
    entries = data.get("entries", [])
    if not isinstance(entries, list):
        return [_fail(book, "coverage-map entries must be a list")]
    malformed = [index for index, entry in enumerate(entries) if not isinstance(entry, dict)]
    if malformed:
        return [_fail(book, f"coverage-map entry {index} must be a mapping") for index in malformed]

    findings = []
    if data.get("map_version") != 1:
        findings.append(_fail(book, "map_version must be 1"))
    ids = [entry.get("id") for entry in entries]
    if _has_duplicates(ids):
        findings.append(_fail(book, "duplicate entry ids"))
    for entry in entries:
        if set(entry) != {
            "id",
            "kind",
            "title",
            "lessons",
            "introduces",
            "requires",
            "practices",
        }:
            findings.append(_fail(book, f"bad entry keys in {entry.get('id', entry)}"))
            continue
        kind = entry["kind"]
        pattern = ENTRY_PATTERNS.get(kind) if isinstance(kind, str) else None
        entry_id = entry["id"]
        if pattern is None or not isinstance(entry_id, str) or not re.match(pattern, entry_id):
            findings.append(_fail(book, f"bad entry id: {entry['id']}"))
        lessons = entry["lessons"]
        if not isinstance(lessons, (int, float)) or lessons <= 0:
            findings.append(_fail(book, f"{entry['id']} lessons must be positive"))
        for field in ("introduces", "requires", "practices"):
            values = entry[field]
            if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
                findings.append(_fail(book, f"{entry['id']}.{field} must be a list of ids"))
    return findings


def lesson_budget_findings(root: Path, book: str) -> list[str]:
    data = _map_data(root, book)
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        return []
    entries = data["entries"]
    if not entries or not all(
        isinstance(entry, dict) and isinstance(entry.get("lessons"), (int, float))
        for entry in entries
    ):
        return []
    total = sum(entry["lessons"] for entry in entries)
    minimum, maximum = lesson_budget(root, book)
    if total < minimum or (maximum is not None and total > maximum):
        bound = f"{minimum:g}+" if maximum is None else f"{minimum:g}-{maximum:g}"
        return [_fail(book, f"lesson budget {total:g} outside {bound}")]
    return []


def referenced_concepts_findings(root: Path, book: str) -> list[str]:
    concepts = _concept_data(root, book).get("concepts", [])
    own = {concept["id"] for concept in concepts if "id" in concept}
    known = own | dependency_baseline(root, book)
    findings = []
    for entry in _map_data(root, book).get("entries", []):
        for field in ("introduces", "requires", "practices"):
            allowed = own if field == "introduces" else known
            unknown = set(entry.get(field, [])) - allowed
            if unknown:
                findings.append(
                    _fail(
                        book,
                        f"{entry.get('id', '?')}.{field} references unknown concepts: "
                        f"{sorted(unknown)}",
                    )
                )
    return findings


def introduction_findings(root: Path, book: str) -> list[str]:
    known = {concept["id"] for concept in _concept_data(root, book).get("concepts", [])}
    introduced = [
        concept
        for entry in _map_data(root, book).get("entries", [])
        for concept in entry.get("introduces", [])
    ]
    findings = []
    if len(introduced) != len(set(introduced)):
        findings.append(_fail(book, "concept introduced twice"))
    missing = known - set(introduced)
    if set(introduced) != known:
        findings.append(_fail(book, f"never introduced: {sorted(missing)}"))
    return findings


def prereq_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    del unit
    schema_findings = map_schema_findings(root, book)
    if schema_findings:
        return schema_findings
    findings = []
    seen = dependency_baseline(root, book)
    for entry in _map_data(root, book).get("entries", []):
        missing = (set(entry.get("requires", [])) | set(entry.get("practices", []))) - seen
        if missing:
            findings.append(
                _fail(
                    book,
                    f"{entry.get('id', '?')} uses concepts not yet introduced: {sorted(missing)}",
                )
            )
        seen |= set(entry.get("introduces", []))
    return findings


def practice_findings(root: Path, book: str) -> list[str]:
    entries = _map_data(root, book).get("entries", [])
    findings = []
    for entry in entries:
        overlap = set(entry.get("practices", [])) & set(entry.get("introduces", []))
        if overlap:
            findings.append(
                _fail(
                    book,
                    f"{entry.get('id', '?')} practices its own introductions: {sorted(overlap)}",
                )
            )
        for field in ("introduces", "requires", "practices"):
            values = entry.get(field, [])
            if len(values) != len(set(values)):
                findings.append(_fail(book, f"{entry.get('id', '?')}.{field} has duplicates"))
    known = {concept["id"] for concept in _concept_data(root, book).get("concepts", [])}
    capstone_id = next(
        (entry.get("id") for entry in reversed(entries) if entry.get("kind") == "project"),
        None,
    )
    pre_capstone = {
        concept
        for entry in entries
        if entry.get("id") != capstone_id
        for concept in entry.get("practices", [])
    }
    book_dir = book_path(root, book)
    capstone_authored = capstone_id is not None and (
        book_dir / "projects" / capstone_id
    ).is_dir()
    if capstone_authored and not known <= pre_capstone:
        findings.append(_fail(book, f"only the capstone practices: {sorted(known - pre_capstone)}"))
    return findings


def checkpoint_findings(root: Path, book: str) -> list[str]:
    findings = []
    seen = dependency_baseline(root, book)
    for entry in _map_data(root, book).get("entries", []):
        if entry.get("kind") == "checkpoint":
            if entry.get("introduces"):
                findings.append(_fail(book, f"{entry.get('id', '?')} introduces concepts"))
            untaught = set(entry.get("practices", [])) - seen
            if untaught:
                findings.append(
                    _fail(
                        book,
                        f"{entry.get('id', '?')} assesses untaught concepts: {sorted(untaught)}",
                    )
                )
        seen |= set(entry.get("introduces", []))
    return findings


def syllabus_findings(root: Path, book: str) -> list[str]:
    entries = _map_data(root, book).get("entries", [])
    syllabus = (book_path(root, book) / "syllabus.md").read_text(encoding="utf-8")
    findings = []
    positions = []
    for entry in entries:
        lessons = entry["lessons"]
        lesson_text = f"{lessons:g}" if isinstance(lessons, (int, float)) else str(lessons)
        row = re.search(
            rf"\|\s*`{re.escape(entry['id'])}`\s*\|\s*{entry['kind']}\s*\|"
            rf"\s*{lesson_text}\s*\|",
            syllabus,
        )
        if not row:
            findings.append(_fail(book, f"syllabus table missing/incorrect row for {entry['id']}"))
        else:
            positions.append(row.start())
    if len(positions) == len(entries) and positions != sorted(positions):
        findings.append(_fail(book, "syllabus table order differs from map order"))
    all_rows = re.findall(
        r"\|\s*`((?:unit|project|checkpoint)-[0-9]{2}-[a-z0-9-]+)`\s*\|", syllabus
    )
    if sorted(all_rows) != sorted(entry["id"] for entry in entries):
        findings.append(_fail(book, "stale/extra syllabus rows"))
    return findings


def coverage_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    del unit
    findings = concepts_schema_findings(root, book)
    findings += global_concept_uniqueness_findings(root)
    findings += map_schema_findings(root, book)
    if findings:
        return findings
    findings = lesson_budget_findings(root, book)
    if findings:
        return findings
    findings = referenced_concepts_findings(root, book)
    findings += introduction_findings(root, book)
    findings += practice_findings(root, book)
    findings += checkpoint_findings(root, book)
    if findings:
        return findings
    return syllabus_findings(root, book)
