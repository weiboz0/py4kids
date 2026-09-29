"""Helpers for resolving books and their dependency-provided concepts."""

from __future__ import annotations

import re
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


def variant_of(root: Path, book: str) -> str | None:
    configured = book_entry(root, book).get("variant_of")
    return configured if isinstance(configured, str) else None


def prereq_policy(root: Path, book: str) -> str | None:
    configured = book_entry(root, book).get("prereq_policy")
    return configured if isinstance(configured, str) else None


def is_buildout(root: Path, book: str) -> bool:
    configured = book_entry(root, book).get("buildout", False)
    return configured if isinstance(configured, bool) else False


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


def book_flag(root: Path, book: str, flag: str) -> bool:
    """Return a boolean feature flag from books.yaml (absent or non-boolean means False).

    Tools key features on these flags, never on book ids (design 008):
    ``publication`` (book-publication pipeline), ``judge`` (stdin solvers + subprocess judge),
    ``patterns`` (pattern checks and the coverage-map v2 / markdown concept scan).
    """
    configured = book_entry(root, book).get(flag, False)
    return configured if isinstance(configured, bool) else False


def books_with_flag(root: Path, flag: str) -> list[str]:
    """Return registered book ids (registry order) whose ``flag`` is true."""
    return [book for book in book_entries(root) if book_flag(root, book, flag)]


def book_title(root: Path, book: str) -> str:
    configured = book_entry(root, book).get("title")
    return configured if isinstance(configured, str) and configured.strip() else book


def book_subtitle(root: Path, book: str) -> str:
    configured = book_entry(root, book).get("subtitle")
    return configured if isinstance(configured, str) else ""


def output_pdf_name(book: str, edition: str) -> str:
    """The one PDF file name for a book edition: ``<id>-<edition>.pdf`` (design 008 D1)."""
    return f"{book}-{edition}.pdf"


def qualified_owner_alternation(root: Path, book: str | None = None) -> str:
    """Regex alternation of every registered book id (plus ``book``), longest first.

    Qualified concept ids are ``<owner>:<concept-id>``; building the owner part from the
    registry lets hyphenated ids (``usaco-bronze:str-split``) and future books work unedited.
    """
    owners = set(book_entries(root))
    if book:
        owners.add(book)
    ordered = sorted(owners, key=lambda owner: (-len(owner), owner))
    return "|".join(re.escape(owner) for owner in ordered) or "(?!)"


def qualified_concept_id_pattern(
    root: Path, book: str | None = None, concept: str = r"[a-z][a-z0-9-]*"
) -> re.Pattern[str]:
    """Compiled ``^(owner|...):<concept>$`` for the registered owners."""
    return re.compile(rf"^(?:{qualified_owner_alternation(root, book)}):{concept}$")
