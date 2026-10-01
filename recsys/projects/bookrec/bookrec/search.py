"""Small, deterministic search helpers for the generated book catalog."""

from __future__ import annotations

from collections.abc import Mapping

from bookrec.catalog import Book


def search_catalog(
    catalog: Mapping[int, Book],
    *,
    text: str | None = None,
    author_id: int | None = None,
    genre: str | None = None,
    year: int | None = None,
) -> list[Book]:
    """Filter the real catalog schema and return matches in stable item-id order.

    ``text`` is a case-insensitive substring search across title, author id, genres, and year.
    The named filters are exact; ``genre`` matches one token in the semicolon-separated field.
    """
    needle = text.casefold().strip() if text is not None else None
    matches: list[Book] = []
    for item_id in sorted(catalog):
        book = catalog[item_id]
        fields = book.fields
        haystack = " ".join(
            [
                book.title,
                fields.get("author_id", ""),
                fields.get("genres", ""),
                fields.get("year", ""),
            ]
        ).casefold()
        genres = {value.strip().casefold() for value in fields.get("genres", "").split(";")}
        if needle is not None and needle not in haystack:
            continue
        if author_id is not None and fields.get("author_id") != str(author_id):
            continue
        if genre is not None and genre.casefold() not in genres:
            continue
        if year is not None and fields.get("year") != str(year):
            continue
        matches.append(book)
    return matches
