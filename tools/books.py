"""Helpers for resolving books and their dependency-provided concepts."""

from __future__ import annotations

from pathlib import Path

import yaml


def book_entries(root: Path) -> dict[str, dict]:
    """Return registered books keyed by id; tolerate legacy fixture roots."""
    path = Path(root).resolve() / "books.yaml"
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("books"), list):
        return {}
    return {
        entry["id"]: entry
        for entry in data["books"]
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }


def book_entry(root: Path, book: str) -> dict:
    return book_entries(root).get(book, {"id": book, "root": book, "depends_on": []})


def book_path(root: Path, book: str) -> Path:
    entry = book_entry(root, book)
    relative = entry.get("root", book)
    return Path(root).resolve() / relative


def introduced_concepts(root: Path, book: str) -> set[str]:
    path = book_path(root, book) / "curriculum" / "coverage-map.yaml"
    if not path.is_file():
        return set()
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        return set()
    return {
        concept
        for entry in data["entries"]
        if isinstance(entry, dict)
        for concept in entry.get("introduces", [])
        if isinstance(concept, str)
    }


def dependency_baseline(root: Path, book: str) -> set[str]:
    """Return concepts introduced by all direct and transitive dependencies."""
    registry = book_entries(root)

    def resolve(current: str, trail: frozenset[str]) -> set[str]:
        if current in trail:
            raise ValueError(f"cyclic book dependency involving {current}")
        entry = registry.get(current, {"depends_on": []})
        result: set[str] = set()
        for dependency in entry.get("depends_on", []) or []:
            if not isinstance(dependency, str):
                continue
            result |= introduced_concepts(root, dependency)
            result |= resolve(dependency, trail | {current})
        return result

    return resolve(book, frozenset())


def concept_minimum(root: Path, book: str) -> int:
    entry = book_entry(root, book)
    configured = entry.get("concept_minimum")
    if isinstance(configured, int) and not isinstance(configured, bool) and configured >= 0:
        return configured
    return 1 if entry.get("depends_on") else 40


def lesson_budget(root: Path, book: str) -> tuple[float, float | None]:
    entry = book_entry(root, book)
    configured = entry.get("lesson_budget")
    if (
        isinstance(configured, list)
        and len(configured) == 2
        and all(isinstance(value, (int, float)) for value in configured)
    ):
        return configured[0], configured[1]
    return (1, None) if entry.get("depends_on") else (28, 32)
