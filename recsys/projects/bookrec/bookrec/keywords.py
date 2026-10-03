"""Load the per-book keyword text slice (``keywords.csv.gz``) — the lexical/content substrate.

Kept dependency-light (stdlib ``csv`` + ``gzip``, no pandas, no numpy) so a unit notebook can
``import bookrec`` and read the keyword bags without a heavy stack. The file is a SEPARATE artifact
from ``catalog.csv.gz`` (the five-column catalog is unchanged); each row is ``item_id,keywords``
with ``keywords`` a space-joined bag of tokens (tokens may repeat → term frequency varies).
"""

from __future__ import annotations

import csv
import gzip
from pathlib import Path

REQUIRED_COLUMNS = ("item_id", "keywords")


def _open_text(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, mode="rt", encoding="utf-8", newline="")
    return open(path, encoding="utf-8", newline="")


def load_keywords(path: str | Path) -> dict[int, str]:
    """Load a (optionally gzip'd) keyword CSV into ``{item_id: "space joined token bag"}``.

    Requires the ``item_id`` and ``keywords`` columns. Raises on a missing column, a non-integer
    id, or a duplicate id. Values are returned verbatim (split on spaces for tokens).
    """
    path = Path(path)
    keywords: dict[int, str] = {}
    with _open_text(path) as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        missing = [column for column in REQUIRED_COLUMNS if column not in header]
        if missing:
            raise ValueError(f"keywords {path.name} missing required column(s): {missing}")
        for line_no, row in enumerate(reader, start=2):
            raw_id = (row.get("item_id") or "").strip()
            try:
                item_id = int(raw_id)
            except ValueError as error:
                raise ValueError(
                    f"keywords {path.name} line {line_no}: non-integer item_id {raw_id!r}"
                ) from error
            if item_id in keywords:
                raise ValueError(
                    f"keywords {path.name} line {line_no}: duplicate item_id {item_id}"
                )
            keywords[item_id] = row.get("keywords") or ""
    return keywords
