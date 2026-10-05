"""Global keys, uniqueness and the committed id ledger (design 012 D3; plan 101 B).

Every block, item and card has a global key `book/entry/notebook/cell_id`, plus `#<part>` for a
part split out of one cell. Cards derived from a block add `#predict`; concept cards are
`book/back-matter/glossary/<concept-id>`. Keys are unique across blocks, items and cards together.

The ledger `site/ids/<book>.json` is the sorted key list of the last release. A key that vanishes
from the bundle must be mapped in `site/ids/<book>-retired.yaml` (`<old key>: <new key>` or
`<old key>: retired`), so progress stored under it can follow or be marked stale.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable
from pathlib import Path

import yaml

LEDGER_DIR = Path("site") / "ids"
RETIRED = "retired"


def _check_segment(name: str, value: str) -> None:
    if not isinstance(value, str) or not value or any(c in value for c in "/# \t\n"):
        raise ValueError(f"bad {name} for a global key: {value!r}")


def item_key(book: str, entry: str, notebook: str, cell_id: str, part: int | None = None) -> str:
    """`book/entry/notebook/cell_id`, plus `#<part>` when `part` is given (a split-out part).

    `notebook` is the file stem (`lesson`, `exercises`, `checkpoint`, `brief`).
    """
    for name, value in (("book", book), ("entry", entry), ("notebook", notebook),
                        ("cell id", cell_id)):
        _check_segment(name, value)
    key = f"{book}/{entry}/{notebook}/{cell_id}"
    if part is None:
        return key
    if not isinstance(part, int) or isinstance(part, bool) or part < 1:
        raise ValueError(f"bad part for a global key: {part!r}")
    return f"{key}#{part}"


def card_key(block_key: str) -> str:
    """The key of the predict card derived from a lesson block."""
    return block_key + "#predict"


def concept_card_key(book: str, concept_id: str) -> str:
    """The key of a glossary concept card."""
    return f"{book}/back-matter/glossary/{concept_id}"


def duplicate_key_findings(keys: Iterable[str]) -> list[str]:
    """One `FAIL:` per key that occurs more than once (run over blocks, items and cards together)."""
    counts = Counter(keys)
    return [f"FAIL: duplicate id: {key} ({count} times)"
            for key, count in sorted(counts.items()) if count > 1]


def missing_id_findings(nb_path: Path) -> list[str]:
    """One `FAIL:` per cell without a non-empty `id` (read raw: nbformat may fill ids in)."""
    data = json.loads(Path(nb_path).read_text(encoding="utf-8"))
    return [f"FAIL: {nb_path}: cell {index} has no id"
            for index, cell in enumerate(data.get("cells", []))
            if not isinstance(cell.get("id"), str) or not cell["id"]]


def ledger_path(root: Path, book: str) -> Path:
    return Path(root) / LEDGER_DIR / f"{book}.json"


def retired_path(root: Path, book: str) -> Path:
    return Path(root) / LEDGER_DIR / f"{book}-retired.yaml"


def load_ledger(root: Path, book: str) -> set[str]:
    """The keys of the committed ledger (empty when the book has none yet)."""
    path = ledger_path(root, book)
    if not path.is_file():
        return set()
    return set(json.loads(path.read_text(encoding="utf-8")))


def write_ledger(root: Path, book: str, keys: Iterable[str]) -> None:
    """Write the sorted, de-duplicated key list (deterministic: indent 1, trailing newline)."""
    path = ledger_path(root, book)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(set(keys)), ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8")


def continuity_findings(root: Path, book: str, keys: Iterable[str]) -> list[str]:
    """`FAIL:` per ledger key that is neither in `keys` nor mapped in the retired file."""
    current = set(keys)
    where = f"site/ids/{book}-retired.yaml"
    retired: dict = {}
    path = retired_path(root, book)
    if path.is_file():
        try:
            retired = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as error:
            return [f"FAIL: {book}: {where}: invalid YAML: {error}"]
        if not isinstance(retired, dict) or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in retired.items()
        ):
            return [f'FAIL: {book}: {where} must be a mapping of old key to new key or "retired"']
    findings = []
    for key in sorted(load_ledger(root, book) - current):
        if key not in retired:
            findings.append(
                f"FAIL: {book}: id vanished since the ledger: {key} "
                f'(map it in {where} as `{key}: <new key or "retired">`)'
            )
        elif retired[key] != RETIRED and retired[key] not in current:
            findings.append(f"FAIL: {book}: {where} maps {key} to {retired[key]}, "
                            "which is not in the bundle")
    return findings
