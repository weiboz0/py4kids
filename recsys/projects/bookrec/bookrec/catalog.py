"""Load the book catalog slice — a gzip'd CSV of stable-int-id book records.

Kept dependency-light (stdlib ``csv`` + ``gzip``) so a unit notebook can ``import bookrec`` and
load the catalog without pulling pandas. The schema is the minimal U1 slice; later units read
extra columns through the same loader. Item ids are parsed to stable ``int``s and must be unique.
"""

from __future__ import annotations

import csv
import gzip
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

REQUIRED_COLUMNS = ("item_id", "title")


@dataclass(frozen=True)
class Book:
    """One catalog row: a stable int id plus its metadata fields."""

    item_id: int
    title: str
    fields: Mapping[str, str] = field(default_factory=dict)


def _open_text(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, mode="rt", encoding="utf-8", newline="")
    return open(path, encoding="utf-8", newline="")


def load_catalog(path: str | Path) -> dict[int, Book]:
    """Load a (optionally gzip'd) CSV catalog into ``{item_id: Book}``.

    Requires at least the ``item_id`` and ``title`` columns; any further columns are kept in
    :attr:`Book.fields`. Raises on a missing column, a non-integer id, or a duplicate id.
    """
    path = Path(path)
    catalog: dict[int, Book] = {}
    with _open_text(path) as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        missing = [column for column in REQUIRED_COLUMNS if column not in header]
        if missing:
            raise ValueError(f"catalog {path.name} missing required column(s): {missing}")
        for line_no, row in enumerate(reader, start=2):
            raw_id = (row.get("item_id") or "").strip()
            try:
                item_id = int(raw_id)
            except ValueError as error:
                raise ValueError(
                    f"catalog {path.name} line {line_no}: non-integer item_id {raw_id!r}"
                ) from error
            if item_id in catalog:
                raise ValueError(
                    f"catalog {path.name} line {line_no}: duplicate item_id {item_id}"
                )
            extra = {
                key: (value or "")
                for key, value in row.items()
                if key not in ("item_id", "title")
            }
            catalog[item_id] = Book(item_id=item_id, title=row.get("title") or "", fields=extra)
    return catalog
