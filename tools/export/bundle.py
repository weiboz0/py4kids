"""Assemble, validate and write a book's site bundle (design 012 D3, D5, D7; plan 101 E).

Layout under `out_dir`:

- `book.json`: the book manifest (`book`, `release`, `entries` in syllabus order, `concepts`,
  `glossary`, `reference_md`, `settings`, `pdfs`).
- `entries/<entry-id>.json`: one unit, checkpoint or project (`lesson`, `intro`, `items`, `outro`,
  `cards`, `files`). A glossary concept card sits in the entry of its term's first unit.
- `files/<entry-id>/<path>`: every file a block or item lists, plus fixture pairs as
  `files/<entry-id>/fixtures/<stem>/<n>.in|.out`. Only git-tracked files `allowed_source(…,
  'student')` admits (plus tracked fixtures) are copied; a solution source, `assets/verify/**` or a
  `solutions*` file is never copied (`_shippable_source` asserts it).

Determinism: JSON is written with `sort_keys=True, ensure_ascii=False, indent=1` and a trailing
newline, lists keep document order, sets are sorted, and nothing holds a timestamp or an absolute
path. `content_hash` is sha256 over the sorted `(relative path, bytes)` of every bundle file, with
`book.json` hashed without its `release` object (`_content_hash` gives the exact framing).

The report (probe statuses, unattributed concepts, classification, self-check reasons, derived
formats, fixture notes, distractor fallbacks) goes to `build/site-report/<book>.json`, never into
the bundle; `site-check` turns it into findings.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import nbformat
from jsonschema import Draft202012Validator

from tools.books import (
    book_flag,
    book_path,
    book_subtitle,
    book_title,
    output_pdf_name,
    publication_config,
)
from tools.publish import (
    SOLUTION_SOURCE,
    allowed_source,
    entries,
    is_solution_source,
    read_source,
)

from . import SCHEMA_VERSION
from .cards import concept_cards, glossary_records, predict_cards
from .classify import tag_findings
from .concepts import book_registry
from .ids import duplicate_key_findings, missing_id_findings
from .items import STEM, entry_content, export_item, item_concept_findings
from .lesson import lesson_export
from .probe import tracked_files

SCHEMA_PATH = Path(__file__).parent / "schema" / "bundle.schema.json"
PDF_EDITIONS = ("student-print", "student", "answer-key", "teacher")
RELEASE_URL = "https://github.com/weiboz0/py4kids/releases/download/{release}/{name}"
UNRELEASED = "unreleased"
ENTRY_NUMBER = re.compile(r"^(?:unit|checkpoint|project)-(\d+)-")


@dataclass
class ExportResult:
    out_dir: Path
    content_hash: str
    keys: list[str]  # every block, side-block, item and card key, in bundle order
    report: dict


class ExportError(ValueError):
    """The export failed on schema errors or missing/duplicate ids; `findings` are `FAIL:` lines."""

    def __init__(self, findings: list[str]):
        self.findings = list(findings)
        super().__init__("\n".join(self.findings))


def dumps(data) -> str:
    """The bundle's one JSON encoding."""
    return json.dumps(data, sort_keys=True, ensure_ascii=False, indent=1) + "\n"


@cache
def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def schema_findings(relative: str, data, definition: str) -> list[str]:
    """`FAIL:` per schema error of one bundle file (`definition`: `book_file` or `entry_file`)."""
    schema = _schema()
    validator = Draft202012Validator(schema).evolve(schema=schema["$defs"][definition])
    out = []
    for error in sorted(validator.iter_errors(data), key=lambda e: (list(map(str, e.absolute_path)),
                                                                      e.message)):
        where = "/".join(str(part) for part in error.absolute_path) or "(root)"
        out.append(f"FAIL: {relative}: schema: {where}: {error.message}")
    return out


def pdf_links(book: str, release: str) -> dict | None:
    """Release PDF links by edition; None while unreleased."""
    if release == UNRELEASED:
        return None
    return {edition: RELEASE_URL.format(release=release, name=output_pdf_name(book, edition))
            for edition in PDF_EDITIONS}


def _entry_kind(entry_id: str) -> str:
    return entry_id.split("-", 1)[0]


def _entry_number(entry_id: str) -> int | None:
    match = ENTRY_NUMBER.match(entry_id)
    return int(match[1]) if match else None


def _statement_title(entry_dir: Path, kind: str) -> str:
    path = entry_dir / f"{STEM[kind]}.ipynb"
    if not path.is_file():
        return entry_dir.name
    notebook = nbformat.read(path, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == "markdown" and cell.source.startswith("# "):
            return cell.source.splitlines()[0].removeprefix("# ").strip()
    return entry_dir.name


def _shippable_source(bundle_path: str, source: Path, tracked: set[str], entry_dir: Path,
                      fixture: bool) -> None:
    """Raise unless `source` may ship: never a solution source, `assets/verify/**` or solutions."""
    relative = Path(source).resolve().relative_to(Path(entry_dir).resolve())
    if (is_solution_source(relative) or SOLUTION_SOURCE.match(relative.name)
            or relative.name.startswith("solutions") or "teacher-notes" in relative.name):
        raise ValueError(f"FAIL: {bundle_path}: a solution source never ships ({relative.as_posix()})")
    if relative.as_posix() not in tracked:
        raise ValueError(f"FAIL: {bundle_path}: not a tracked student file ({relative.as_posix()})")
    if not fixture and not allowed_source(source, "student"):
        raise ValueError(f"FAIL: {bundle_path}: not a tracked student file "
                         f"(allowed_source rejects {relative.as_posix()})")


def _content_hash(contents: dict[str, bytes]) -> str:
    """sha256 over `path NUL length NUL bytes` per bundle file, in sorted path order."""
    digest = hashlib.sha256()
    for relative in sorted(contents):
        data = contents[relative]
        digest.update(relative.encode("utf-8") + b"\0" + str(len(data)).encode("ascii") + b"\0")
        digest.update(data)
    return "sha256:" + digest.hexdigest()


def _settings(root: Path, book: str) -> dict:
    heading = ""
    if book_flag(root, book, "publication"):
        heading = publication_config(root, book).lesson_heading or ""
    settings: dict = {"lesson_heading": heading}
    if book_flag(root, book, "acsl"):
        from tools.acsl import load_season

        season, _findings = load_season(root, book)
        if season and isinstance(season.get("ladder"), list):
            settings["acsl_divisions"] = list(season["ladder"])
    return settings


def _back_matter(base: Path, name: str) -> str:
    path = base / "back-matter" / name
    return read_source(path, "student") if path.is_file() else ""


def _keys_of(entry: dict) -> list[str]:
    keys = [block["key"] for block in (entry["lesson"] or {}).get("blocks", [])]
    keys += [block["key"] for block in entry["intro"]]
    for item in entry["items"]:
        keys += [block["key"] for block in item["before"]]
        keys.append(item["key"])
    keys += [block["key"] for block in entry["outro"]]
    keys += [card["key"] for card in entry["cards"]]
    return keys


def _note_lists(report: dict, key: str, notes: list[str]) -> None:
    for note in notes:
        if note.startswith("answer_format: derived"):
            report["derived_formats"].append(key)
        elif note.startswith("fixtures: no pair matches"):
            report["unmatched_samples"].append(key)
    if notes:
        report["notes"][key] = list(notes)


def export_book(root: Path, book: str, out_dir: Path, release: str = UNRELEASED) -> ExportResult:
    """Export `book` as a bundle under `out_dir` (replacing its `book.json`, `entries/`, `files/`)."""
    root, out_dir = Path(root), Path(out_dir)
    if not book_flag(root, book, "site"):
        raise ValueError(f"{book} is not a site book (books.yaml site: true)")
    base = book_path(root, book)
    registry = book_registry(root, book)
    entry_list = entries(base, "student")

    missing = [finding for entry_id, entry_dir in entry_list
               for stem in ("lesson", STEM[_entry_kind(entry_id)])
               if (entry_dir / f"{stem}.ipynb").is_file()
               for finding in missing_id_findings(entry_dir / f"{stem}.ipynb")]
    if missing:
        raise ExportError(missing)

    glossary = glossary_records(_back_matter(base, "glossary.md"))
    cards_by_unit: dict[int, list[dict]] = {}
    concept_card_list = concept_cards(list(registry.concepts), glossary, book=book)
    for record, card in zip(glossary, concept_card_list, strict=True):
        cards_by_unit.setdefault(min(record["units"]), []).append(card)
    unit_numbers = {_entry_number(entry_id) for entry_id, _ in entry_list
                    if _entry_kind(entry_id) == "unit"}
    orphan = sorted(set(cards_by_unit) - unit_numbers)
    if orphan:
        raise ValueError(f"FAIL: {book}: glossary cites units with no syllabus entry: {orphan}")

    report: dict = {
        "book": book, "probes": {}, "concept_findings": [], "tag_findings": [],
        "unattributed": {"blocks": [], "items": []}, "classification": {},
        "self_check": {}, "derived_formats": [], "unmatched_samples": [], "over_budget": {},
        "notes": {}, "distractor_fallbacks": {},
    }
    classification = {"total": 0, "confirmed": 0, "by_kind": {}, "unconfirmed": []}
    documents: dict[str, dict] = {}
    copies: dict[str, Path] = {}
    keys: list[str] = []
    book_entries = []

    for entry_id, entry_dir in entry_list:
        kind = _entry_kind(entry_id)
        tracked = set(tracked_files(entry_dir))
        lesson = None
        if kind == "unit" and (entry_dir / "lesson.ipynb").is_file():
            lesson = lesson_export(root, book, entry_dir, registry=registry)
            report["concept_findings"] += lesson.findings
            report["unattributed"]["blocks"] += lesson.unattributed
            for key, result in lesson.probes.items():
                report["probes"][key] = {"status": result.status, "detail": result.detail}
        intro: list[dict] = []
        outro: list[dict] = []
        item_data: list[dict] = []
        fixture_sources: dict[str, Path] = {}
        if (entry_dir / f"{STEM[kind]}.ipynb").is_file():
            content = entry_content(root, book, entry_dir, kind)
            intro, outro = content.intro, content.outro
            report["concept_findings"] += item_concept_findings(root, book, content.items)
            for item in content.items:
                report["tag_findings"] += tag_findings(item)
                exported = export_item(root, book, item)
                data = exported.data
                item_data.append(data)
                key = data["key"]
                classification["total"] += 1
                classification["by_kind"][exported.kind] = (
                    classification["by_kind"].get(exported.kind, 0) + 1)
                if exported.confirmed:
                    classification["confirmed"] += 1
                else:
                    classification["unconfirmed"].append(key)
                if exported.kind == "self-check":
                    report["self_check"][key] = exported.reason
                if not data["concepts"]:
                    report["unattributed"]["items"].append(key)
                if data["check"]["kind"] == "fixtures":
                    from .answers import fixture_files

                    sources = dict(fixture_files(root, book, item))
                    for case in data["check"]["cases"]:
                        for field in ("in_file", "out_file"):
                            fixture_sources[case[field]] = sources[case[field]]
                    if data["check"]["over_budget"]:
                        report["over_budget"][key] = list(data["check"]["over_budget"])
                _note_lists(report, key, exported.notes)

        cards = predict_cards(lesson.blocks) if lesson else []
        if kind == "unit":
            cards += cards_by_unit.get(_entry_number(entry_id), [])
        blocks = lesson.blocks if lesson else []
        listed: list[str] = []
        for block in [*blocks, *intro, *outro]:
            listed += block.get("files", [])
        for data in item_data:
            listed += data["files"]
            for block in data["before"]:
                listed += block.get("files", [])
        listed += list(fixture_sources)
        prefix = f"files/{entry_id}/"
        for bundle_path in listed:
            if not bundle_path.startswith(prefix):
                raise ValueError(f"FAIL: {bundle_path}: listed outside its entry {entry_id}")
            fixture = bundle_path in fixture_sources
            source = fixture_sources[bundle_path] if fixture else entry_dir / bundle_path[len(prefix):]
            _shippable_source(bundle_path, source, tracked, entry_dir, fixture)
            copies[bundle_path] = source

        title = lesson.title if lesson else _statement_title(entry_dir, kind)
        entry = {
            "schema_version": SCHEMA_VERSION,
            "entry": {"id": entry_id, "kind": kind, "title": title},
            "lesson": {"blocks": blocks} if lesson else None,
            "intro": intro, "items": item_data, "outro": outro, "cards": cards,
            "files": sorted(set(listed)),
        }
        documents[f"entries/{entry_id}.json"] = entry
        keys += _keys_of(entry)
        book_entries.append({"id": entry_id, "kind": kind, "title": title,
                             "number": _entry_number(entry_id), "file": f"entries/{entry_id}.json"})

    for card in concept_card_list:
        report["distractor_fallbacks"].update(
            {card["key"]: len(card["distractors"])} if len(card["distractors"]) < 3 else {})
    report["classification"] = classification

    book_doc = {
        "schema_version": SCHEMA_VERSION,
        "book": {"id": book, "title": book_title(root, book), "subtitle": book_subtitle(root, book),
                 "flags": {"acsl": book_flag(root, book, "acsl"),
                           "judge": book_flag(root, book, "judge")}},
        "entries": book_entries,
        "concepts": [dict(concept) for concept in registry.concepts],
        "glossary": glossary,
        "reference_md": _back_matter(base, "quick-reference.md"),
        "settings": _settings(root, book),
        "pdfs": pdf_links(book, release),
    }

    contents: dict[str, bytes] = {"book.json": dumps(book_doc).encode("utf-8")}
    for relative, document in documents.items():
        contents[relative] = dumps(document).encode("utf-8")
    for bundle_path, source in copies.items():
        contents[bundle_path] = source.read_bytes()
    content_hash = _content_hash(contents)
    book_doc["release"] = {"tag": release, "content_hash": content_hash}
    contents["book.json"] = dumps(book_doc).encode("utf-8")

    problems = schema_findings("book.json", json.loads(contents["book.json"]), "book_file")
    for relative in documents:
        problems += schema_findings(relative, json.loads(contents[relative]), "entry_file")
    problems += duplicate_key_findings(keys)
    if problems:
        raise ExportError(problems)

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "book.json").unlink(missing_ok=True)
    for part in ("entries", "files"):
        shutil.rmtree(out_dir / part, ignore_errors=True)
    for relative in sorted(contents):
        path = out_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents[relative])

    report_path = root / "build" / "site-report" / f"{book}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(dumps(report), encoding="utf-8")
    return ExportResult(out_dir, content_hash, keys, json.loads(dumps(report)))
