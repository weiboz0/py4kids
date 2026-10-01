"""Curriculum rules promoted from the Plan 002/004 interim tests."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from tools.books import (
    assumed_baseline,
    book_entries,
    book_flag,
    book_path,
    concept_minimum,
    is_buildout,
    known_baseline,
    lesson_budget,
    peers,
    prereq_policy,
    qualified_concept_id_pattern,
    variant_of,
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
MAP_ENTRY_KEYS = {
    1: {
        "id",
        "kind",
        "title",
        "lessons",
        "introduces",
        "requires",
        "practices",
    },
    2: {
        "id",
        "kind",
        "title",
        "lessons",
        "introduces",
        "requires",
        "practices",
        "auxiliary",
    },
}
# Qualified concept ids are `<owner>:<concept-id>`; the owner alternation is built from the
# registered book ids (tools.books.qualified_concept_id_pattern), never hard-coded.
QUALIFIED_CONCEPT_TAIL = r"[a-z0-9]+(?:-[a-z0-9]+)*"


def _fail(book: str, detail: str) -> str:
    return f"FAIL: {book}: {detail}"


def _curriculum(root: Path, book: str) -> Path:
    return book_path(root, book) / "curriculum"


def peer_registry_findings(root: Path) -> list[str]:
    """Validate ``peers`` in books.yaml: a list of known, other book ids, declared symmetrically."""
    registered = book_entries(root)
    findings = []
    for registered_book, entry in registered.items():
        if "peers" not in entry:
            continue
        declared = entry["peers"]
        if not isinstance(declared, list) or not all(isinstance(v, str) for v in declared):
            findings.append(_fail("books", f"{registered_book!r} peers must be a list of book ids"))
            continue
        for peer in declared:
            if peer == registered_book:
                findings.append(_fail("books", f"{registered_book!r} lists itself as a peer"))
            elif peer not in registered:
                findings.append(_fail("books", f"{registered_book!r} peer {peer!r} is unknown"))
            elif registered_book not in peers(root, peer):
                findings.append(
                    _fail(
                        "books",
                        f"{registered_book!r} peer {peer!r} is asymmetric "
                        f"({peer!r} does not list {registered_book!r})",
                    )
                )
    return findings


def _is_peer_pair(root: Path, first: str, second: str) -> bool:
    """Two distinct registered books that list each other as peers."""
    registered = book_entries(root)
    return (
        first != second
        and first in registered
        and second in registered
        and second in peers(root, first)
        and first in peers(root, second)
    )


def global_concept_uniqueness_findings(root: Path) -> list[str]:
    """Report concept ids defined by more than one registered book.

    Two exemptions: a ``variant_of`` pair (whose whole catalogues must be equal), and a validated
    symmetric ``peers`` pair (design 008 D3), which may each define a shared id only when the two
    registry entries are identical as dicts (name, category and ``kind``, including its absence).
    """
    registered = book_entries(root)
    owners: dict[str, set[str]] = {}
    catalogs: dict[str, object] = {}
    entries: dict[tuple[str, str], dict] = {}
    for registered_book in registered:
        path = _curriculum(root, registered_book) / "concepts.yaml"
        if not path.is_file():
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        catalogs[registered_book] = data
        if not isinstance(data, dict) or not isinstance(data.get("concepts"), list):
            continue
        for concept in data["concepts"]:
            if isinstance(concept, dict) and isinstance(concept.get("id"), str):
                owners.setdefault(concept["id"], set()).add(registered_book)
                entries.setdefault((registered_book, concept["id"]), concept)

    def is_variant_pair(books: set[str]) -> bool:
        return any(
            parent in registered and books <= {candidate, parent}
            for candidate in books
            if (parent := variant_of(root, candidate)) is not None
        )

    peer_findings = peer_registry_findings(root)

    def is_peer_set(books: set[str]) -> bool:
        if peer_findings:
            return False  # an invalid peer registry grants no exemption
        ordered = sorted(books)
        return all(
            _is_peer_pair(root, first, second)
            or is_variant_pair({first, second})
            for index, first in enumerate(ordered)
            for second in ordered[index + 1 :]
        )

    findings = list(peer_findings)
    for concept_id, books in sorted(owners.items()):
        if len(books) < 2 or is_variant_pair(books):
            continue
        if not is_peer_set(books):
            findings.append(
                _fail(
                    "books",
                    f"concept id {concept_id!r} is defined in multiple books: {sorted(books)}",
                )
            )
            continue
        definitions = [entries[(book, concept_id)] for book in sorted(books)]
        if any(definition != definitions[0] for definition in definitions[1:]):
            findings.append(
                _fail(
                    "books",
                    f"concept id {concept_id!r} drifts between peers {sorted(books)}: "
                    "concepts.yaml entries must be identical",
                )
            )
    missing = object()
    for registered_book in sorted(registered):
        parent = variant_of(root, registered_book)
        if parent in registered and catalogs.get(registered_book, missing) != catalogs.get(
            parent, missing
        ):
            findings.append(
                _fail(
                    "books",
                    f"variant {registered_book!r} concepts.yaml differs from parent {parent!r}",
                )
            )
    return findings


def _concept_data(root: Path, book: str):
    return yaml.safe_load((_curriculum(root, book) / "concepts.yaml").read_text(encoding="utf-8"))


def _map_data(root: Path, book: str):
    return yaml.safe_load(
        (_curriculum(root, book) / "coverage-map.yaml").read_text(encoding="utf-8")
    )


def _has_duplicates(values: list[object]) -> bool:
    return any(value in values[:index] for index, value in enumerate(values))


def auxiliary_schema_details(entry: dict, root: Path, book: str) -> list[str]:
    """Return schema-v2 auxiliary errors without attaching a book/entry scope."""
    values = entry.get("auxiliary")
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        return ["auxiliary must be a list of qualified ids"]

    details = []
    qualified = qualified_concept_id_pattern(root, book, QUALIFIED_CONCEPT_TAIL)
    if not all(qualified.fullmatch(value) for value in values):
        details.append("auxiliary must contain qualified ids")
    if _has_duplicates(values):
        details.append("auxiliary has duplicates")
    kind = entry.get("kind")
    if isinstance(kind, str) and kind in {"checkpoint", "project"} and values:
        details.append("auxiliary must be empty")
        return details

    raw = set()
    for field in ("introduces", "requires", "practices"):
        field_values = entry.get(field)
        if isinstance(field_values, list):
            raw.update(value for value in field_values if isinstance(value, str))
    normalized = {
        value.removeprefix(f"{book}:") if value.startswith(f"{book}:") else value
        for value in values
    }
    overlap = normalized & raw
    if overlap:
        details.append(
            "auxiliary overlaps introduces/requires/practices: " f"{sorted(overlap)}"
        )
    return details


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
    map_version = data.get("map_version")
    if map_version not in MAP_ENTRY_KEYS:
        return [_fail(book, "map_version must be 1 or 2")]
    if map_version == 2 and not book_flag(root, book, "patterns"):
        return [_fail(book, "map_version 2 is only supported for patterns books")]
    ids = [entry.get("id") for entry in entries]
    if _has_duplicates(ids):
        findings.append(_fail(book, "duplicate entry ids"))
    for entry in entries:
        if set(entry) != MAP_ENTRY_KEYS[map_version]:
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
        if map_version == 2:
            findings.extend(
                _fail(book, f"{entry['id']}.{detail}")
                for detail in auxiliary_schema_details(entry, root, book)
            )
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
    below_minimum = total < minimum and not is_buildout(root, book)
    above_maximum = maximum is not None and total > maximum
    if below_minimum or above_maximum:
        bound = f"{minimum:g}+" if maximum is None else f"{minimum:g}-{maximum:g}"
        return [_fail(book, f"lesson budget {total:g} outside {bound}")]
    return []


def referenced_concepts_findings(root: Path, book: str) -> list[str]:
    concepts = _concept_data(root, book).get("concepts", [])
    own = {concept["id"] for concept in concepts if "id" in concept}
    known = own | known_baseline(root, book)
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
    if not is_buildout(root, book) and set(introduced) != known:
        findings.append(_fail(book, f"never introduced: {sorted(missing)}"))
    return findings


def _is_transitive_dependent(root: Path, candidate: str, dependency: str) -> bool:
    """Return whether candidate depends on dependency by walking books.yaml."""
    registry = book_entries(root)
    if candidate not in registry or dependency not in registry:
        return False

    pending = [candidate]
    visited: set[str] = set()
    while pending:
        current = pending.pop()
        if current in visited:
            continue
        visited.add(current)
        depends_on = registry.get(current, {}).get("depends_on", [])
        if not isinstance(depends_on, list):
            continue
        dependencies = [value for value in depends_on if isinstance(value, str)]
        if dependency in dependencies:
            return True
        pending.extend(value for value in dependencies if value in registry)
    return False


def _registered_concepts(root: Path, book: str) -> set[str]:
    """Return ids owned by a registered book, failing closed on malformed data."""
    if book not in book_entries(root):
        return set()
    path = _curriculum(root, book) / "concepts.yaml"
    if not path.is_file():
        return set()
    try:
        if concepts_schema_findings(root, book):
            return set()
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (KeyError, OSError, TypeError, yaml.YAMLError):
        return set()
    if not isinstance(data, dict) or not isinstance(data.get("concepts"), list):
        return set()
    return {
        concept["id"]
        for concept in data["concepts"]
        if isinstance(concept, dict) and isinstance(concept.get("id"), str)
    }


def _auxiliary_prereq_findings(
    root: Path, book: str, entries: list[dict]
) -> list[str]:
    """Validate that schema-v2 borrowed tools come from a future owner."""
    home_positions: dict[str, int] = {}
    for index, entry in enumerate(entries):
        for concept_id in entry.get("introduces", []):
            home_positions.setdefault(concept_id, index)

    owner_concepts: dict[str, set[str]] = {}
    owner_is_dependent: dict[str, bool] = {}
    findings = []
    for index, entry in enumerate(entries):
        entry_id = entry.get("id", "?")
        for qualified_id in entry.get("auxiliary", []):
            owner, concept_id = qualified_id.split(":", 1)
            if owner == book:
                home_index = home_positions.get(concept_id)
                if home_index is None:
                    findings.append(
                        _fail(
                            book,
                            f"{entry_id}.auxiliary {qualified_id} has no home introduction",
                        )
                    )
                elif home_index <= index:
                    findings.append(
                        _fail(
                            book,
                            f"{entry_id}.auxiliary {qualified_id} must have a later home "
                            "introduction",
                        )
                    )
            elif concept_id not in owner_concepts.setdefault(
                owner, _registered_concepts(root, owner)
            ):
                findings.append(
                    _fail(
                        book,
                        f"{entry_id}.auxiliary {qualified_id} has no registered owner",
                    )
                )
            elif not owner_is_dependent.setdefault(
                owner, _is_transitive_dependent(root, owner, book)
            ):
                findings.append(
                    _fail(
                        book,
                        f"{entry_id}.auxiliary {qualified_id} owner {owner} is not a "
                        f"transitive dependent of {book}",
                    )
                )
    return findings


def prereq_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    del unit
    schema_findings = map_schema_findings(root, book)
    if schema_findings:
        return schema_findings
    findings = []
    map_data = _map_data(root, book)
    entries = map_data.get("entries", [])
    if map_data.get("map_version") == 2:
        findings.extend(_auxiliary_prereq_findings(root, book, entries))
    seen = known_baseline(root, book)
    # Which fields must close over already-introduced concepts. Fastforward books check
    # `requires` only (a unit's core teaching); `practices` may reach forward. Not an ordering.
    checked_fields = (
        ("requires",)
        if prereq_policy(root, book) == "fastforward"
        else ("requires", "practices")
    )
    for entry in entries:
        missing = {
            concept
            for field in checked_fields
            for concept in entry.get(field, [])
        } - seen
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
    assumed = assumed_baseline(root, book)
    for entry in entries:
        overlap = set(entry.get("practices", [])) & set(entry.get("introduces", []))
        if overlap:
            findings.append(
                _fail(
                    book,
                    f"{entry.get('id', '?')} practices its own introductions: {sorted(overlap)}",
                )
            )
        practiced_assumed = set(entry.get("practices", [])) & assumed
        # Flag assumed-baseline practice for units AND projects: a baseline id is assessable with
        # no coverage obligation, so practising it earns silent, undeserved credit. Checkpoints are
        # covered by `checkpoint_findings`, so they are excluded here to avoid a double-finding.
        if entry.get("kind") in ("unit", "project") and practiced_assumed:
            findings.append(
                _fail(
                    book,
                    f"{entry.get('id', '?')} practices assumed baseline concepts: "
                    f"{sorted(practiced_assumed)}",
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
    assumed = assumed_baseline(root, book)
    seen = known_baseline(root, book)
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
            practiced_assumed = set(entry.get("practices", [])) & assumed
            if practiced_assumed:
                findings.append(
                    _fail(
                        book,
                        f"{entry.get('id', '?')} practices assumed baseline concepts: "
                        f"{sorted(practiced_assumed)}",
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
