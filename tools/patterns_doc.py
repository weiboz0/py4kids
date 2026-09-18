"""Generate and verify the Book 1 algorithm-pattern reference."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from tools.patterns import PatternBookData, load_pattern_book

HEADER = """# Book 1 Algorithm Patterns

This reference is generated from the curriculum pattern catalog and coverage map.
Do not edit it by hand.
"""


def _fail(detail: str) -> str:
    return f"FAIL: book1: {detail}"


def _catalog_input(root: Path) -> tuple[PatternBookData, dict, list[str]]:
    data = load_pattern_book(root)
    findings = list(data.findings)
    path = data.directory / "curriculum/patterns-catalog.yaml"
    if not path.is_file():
        findings.append(_fail("patterns-catalog.yaml does not exist"))
        return data, {}, findings
    try:
        catalog = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        findings.append(_fail(f"patterns-catalog.yaml is not valid YAML: {error}"))
        return data, {}, findings
    if not isinstance(catalog, dict):
        findings.append(_fail("patterns-catalog.yaml must be a mapping"))
        return data, {}, findings
    return data, catalog, findings


def _catalog_findings(root: Path) -> list[str]:
    data, catalog, findings = _catalog_input(root)
    if findings:
        return findings
    technique_ids = set(data.techniques)
    non_string_keys = [key for key in catalog if not isinstance(key, str)]
    if non_string_keys:
        rendered = sorted(repr(key) for key in non_string_keys)
        findings.append(_fail(f"catalog keys must be string technique ids: {rendered}"))
    catalog_ids = {key for key in catalog if isinstance(key, str)}
    missing = sorted(technique_ids - catalog_ids)
    extra = sorted(catalog_ids - technique_ids)
    if missing:
        findings.append(_fail(f"catalog is missing technique ids: {missing}"))
    if extra:
        findings.append(_fail(f"catalog has unregistered technique ids: {extra}"))

    concept_ids = {
        concept["id"]
        for concept in data.concepts
        if isinstance(concept, dict) and isinstance(concept.get("id"), str)
    }
    introduced_at: dict[str, int] = {}
    for index, entry in enumerate(data.entries):
        if not isinstance(entry, dict):
            continue
        for concept_id in entry.get("introduces", []) or []:
            if isinstance(concept_id, str):
                introduced_at.setdefault(concept_id, index)

    for technique in data.techniques.values():
        pattern_id = technique["id"]
        if not isinstance(technique.get("name"), str) or not technique["name"].strip():
            findings.append(_fail(f"technique {pattern_id!r} needs a name"))
        row = catalog.get(pattern_id)
        if not isinstance(row, dict):
            if pattern_id in catalog:
                findings.append(_fail(f"catalog row {pattern_id!r} must be a mapping"))
            continue
        if set(row) != {"hook", "enabling_concepts"}:
            findings.append(
                _fail(f"catalog row {pattern_id!r} must contain hook and enabling_concepts")
            )
            continue
        if not isinstance(row["hook"], str) or not row["hook"].strip():
            findings.append(_fail(f"catalog row {pattern_id!r} needs a non-empty hook"))
        enabling = row["enabling_concepts"]
        if not isinstance(enabling, list) or not all(isinstance(item, str) for item in enabling):
            findings.append(_fail(f"catalog row {pattern_id!r} enabling_concepts must be ids"))
            continue
        homes = [
            index
            for index, entry in enumerate(data.entries)
            if isinstance(entry, dict) and pattern_id in (entry.get("introduces", []) or [])
        ]
        if len(homes) != 1:
            findings.append(_fail(f"technique {pattern_id!r} must have exactly one home"))
            continue
        home_index = homes[0]
        for enabling_id in enabling:
            if enabling_id not in concept_ids:
                findings.append(
                    _fail(f"{pattern_id!r} enabling concept {enabling_id!r} is not registered")
                )
            elif enabling_id not in introduced_at or introduced_at[enabling_id] > home_index:
                findings.append(
                    _fail(
                        f"{pattern_id!r} enabling concept {enabling_id!r} "
                        "is not introduced by its home"
                    )
                )
    return findings


def generated_patterns_text(root: Path) -> str:
    data, catalog, input_findings = _catalog_input(root)
    if input_findings or _catalog_findings(root):
        raise ValueError("cannot generate patterns.md from invalid pattern catalog")
    if not data.techniques:
        return HEADER + "\nNo algorithm patterns are registered yet.\n"

    sections = [HEADER.rstrip()]
    for technique in data.techniques.values():
        pattern_id = technique["id"]
        row = catalog[pattern_id]
        home = next(
            entry["id"]
            for entry in data.entries
            if isinstance(entry, dict) and pattern_id in (entry.get("introduces", []) or [])
        )
        practices = [
            entry["id"]
            for entry in data.entries
            if isinstance(entry, dict) and pattern_id in (entry.get("practices", []) or [])
        ]
        enabling = ", ".join(f"`{concept_id}`" for concept_id in row["enabling_concepts"])
        where_rows = [
            "| Role | Entry |",
            "| --- | --- |",
            f"| Home | `{home}` |",
            *(f"| Reappearance | `{entry_id}` |" for entry_id in practices),
        ]
        sections.append(
            "\n".join(
                (
                    f"## {technique['name']}",
                    "",
                    row["hook"].strip(),
                    "",
                    f"- Pattern id: `{pattern_id}`",
                    f"- Enabling concepts: {enabling or 'None'}",
                    "",
                    "### Where you'll meet it",
                    "",
                    *where_rows,
                )
            )
        )
    return "\n\n".join(sections) + "\n"


def generate_patterns_document(root: Path, book: str = "book1") -> Path:
    if book != "book1":
        raise ValueError("patterns.md generation is Book 1 only")
    findings = _catalog_findings(root)
    if findings:
        raise ValueError("\n".join(findings))
    data = load_pattern_book(root)
    output = data.directory / "reference/patterns.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(generated_patterns_text(root), encoding="utf-8")
    return output


def patterns_doc_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    del unit
    if book != "book1":
        return []
    findings = _catalog_findings(root)
    if findings:
        return findings
    path = load_pattern_book(root).directory / "reference/patterns.md"
    if not path.is_file():
        return [_fail("reference/patterns.md does not exist")]
    if path.read_bytes() != generated_patterns_text(root).encode("utf-8"):
        return [_fail("reference/patterns.md is out of date; run tools/patterns_doc.py generate")]
    return []


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", nargs="?", choices=("generate",))
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--pdf-probe", action="store_true")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    return parser


def main(argv=None) -> int:
    arguments = _parser().parse_args(argv)
    if arguments.pdf_probe:
        findings = _catalog_findings(arguments.root)
        if findings:
            print("\n".join(findings))
            return 1
        data = load_pattern_book(arguments.root)
        print("present" if data.techniques else "empty")
        return 0
    if arguments.check:
        findings = patterns_doc_findings(arguments.root, "book1")
        if findings:
            print("\n".join(findings))
            return 1
        print("patterns-doc-check: PASS")
        return 0
    if arguments.action == "generate":
        print(generate_patterns_document(arguments.root))
        return 0
    _parser().print_usage()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
