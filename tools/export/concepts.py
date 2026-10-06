"""Per-cell concept attribution for the site export (design 012 D8, D11; plan 101 C).

A code cell's concepts come from `concept_scan.detect` with the book's scanner profile,
intersected with the book's registered concept ids. A heading or code cell's `metadata.concepts`
list overrides the scan; every id in it must be registered, or the export reports
`FAIL: <key>: unregistered concept <id>` (site-check fails on it).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

import yaml

from tools.books import book_path
from tools.concept_scan import ScanProfile, detect, scanner_profile


@dataclass(frozen=True)
class Registry:
    """One book's concept registry (`curriculum/concepts.yaml`)."""

    concepts: tuple[dict, ...]  # each {id, name, category}, in registry order
    ids: frozenset[str]
    profile: ScanProfile

    def category(self, concept_id: str) -> str:
        for concept in self.concepts:
            if concept["id"] == concept_id:
                return concept["category"]
        raise ValueError(f"unregistered concept {concept_id}")


def book_registry(root: Path, book: str) -> Registry:
    path = book_path(root, book) / "curriculum" / "concepts.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw = data.get("concepts", []) if isinstance(data, dict) else []
    concepts = tuple(
        {"id": c["id"], "name": c.get("name", c["id"]), "category": c.get("category", "")}
        for c in raw if isinstance(c, dict) and isinstance(c.get("id"), str)
    )
    return Registry(concepts, frozenset(c["id"] for c in concepts), scanner_profile(list(raw)))


def cell_concepts(profile: ScanProfile, registered, source: str) -> list[str]:
    """The registered concepts `detect` finds in `source`, sorted; `[]` when it does not parse."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    used, _unknown = detect(tree, registered_concepts=set(registered), profile=profile)
    return sorted(set(used) & set(registered))


def concept_override(key: str, metadata, registered) -> tuple[list[str] | None, list[str]]:
    """A cell's `metadata.concepts` override: `(ids or None, findings)`.

    None means the cell has no override (scan instead). The ids keep only registered concepts,
    sorted and unique; every unregistered id gives `FAIL: <key>: unregistered concept <id>`.
    """
    if not hasattr(metadata, "get") or "concepts" not in metadata:
        return None, []
    value = metadata.get("concepts")
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        return [], [f"FAIL: {key}: metadata.concepts must be a list of concept ids"]
    findings = [f"FAIL: {key}: unregistered concept {v}" for v in value if v not in registered]
    return sorted({v for v in value if v in registered}), findings
