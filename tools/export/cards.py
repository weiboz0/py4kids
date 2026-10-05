"""Quiz cards and glossary records for the site export (design 012 D8; plan 101 C).

- **Predict cards** come from lesson `code` blocks that have stored output and probe status
  `standalone` or `prelude`: `typed` when the normalised output is one line, else `flip`. Lesson
  outputs are visible on the page, so no hash ships.
- **Concept cards** come from the glossary, one per entry. Distractors are other glossary terms of
  the same concept `category`, always category-local: 3 peers or more give a 3-distractor
  `choice` card, 1–2 peers a smaller `choice` card, none a term → definition `flip` card.
"""

from __future__ import annotations

import re

from tools.export.ids import card_key, concept_card_key
from tools.export.normalise import normalise

GLOSSARY_RECORD = re.compile(
    r"^\*\*(?P<term>.+?)\*\* — (?P<definition>.+?)\s*\*\(Units? (?P<units>[^)]+)\)\*[ \t]*\n"
    r"<!-- concept: (?P<concept>[\w-]+)(?:; index: [^>]+?)? -->",
    re.MULTILINE,
)
UNIT_RANGE = re.compile(r"^(\d+)\s*[–-]\s*(\d+)$")


def _units(text: str) -> list[int]:
    units: list[int] = []
    for part in (p.strip() for p in text.split(",")):
        if match := UNIT_RANGE.match(part):
            first, last = int(match[1]), int(match[2])
            if last < first:
                raise ValueError(f"glossary unit range runs backwards: {text}")
            units.extend(range(first, last + 1))
        elif part.isdigit():
            units.append(int(part))
        else:
            raise ValueError(f"glossary unit tag not understood: {text}")
    return units


def glossary_records(source: str) -> list[dict]:
    """Every `**Term** — definition *(Unit N)*` line with its next-line `<!-- concept: … -->`.

    Each record is `{term, concept, definition_md, units}`: `definition_md` is the Markdown between
    ` — ` and the unit tag, verbatim; `units` expands ranges (`4–6`) and comma lists (`4, 7`).
    """
    return [
        {"term": m["term"], "concept": m["concept"], "definition_md": m["definition"].strip(),
         "units": _units(m["units"])}
        for m in GLOSSARY_RECORD.finditer(source)
    ]


def predict_cards(blocks: list[dict]) -> list[dict]:
    """One predict card per eligible lesson block, in block order."""
    cards = []
    for block in blocks:
        if block.get("type") != "code" or block.get("probe") not in ("standalone", "prelude"):
            continue
        output = normalise(block.get("output", ""), case="sensitive")
        if not output:
            continue
        cards.append({
            "key": card_key(block["key"]),
            "kind": "predict",
            "block": block["key"],
            "mode": "typed" if "\n" not in output else "flip",
            "prelude": list(block.get("prelude", [])),
        })
    return cards


def _term_order(term: str) -> tuple[str, str]:
    return (term.casefold(), term)


def concept_cards(concepts: list[dict], glossary: list[dict], *, book: str) -> list[dict]:
    """One concept card per glossary record, in glossary order (deterministic distractors).

    `concepts` is the book's registry (`{id, name, category}`); `glossary` is `glossary_records`.
    A card's distractors are the terms after its own in the sorted (casefolded) term list of its
    category, wrapping around, at most 3.
    """
    category = {concept["id"]: concept["category"] for concept in concepts}
    missing = sorted({record["concept"] for record in glossary} - set(category))
    if missing:
        raise ValueError(f"{book}: glossary concepts missing from concepts.yaml: {missing}")
    by_category: dict[str, list[str]] = {}
    for record in glossary:
        terms = by_category.setdefault(category[record["concept"]], [])
        if record["term"] not in terms:
            terms.append(record["term"])
    for terms in by_category.values():
        terms.sort(key=_term_order)
    cards = []
    for record in glossary:
        terms = by_category[category[record["concept"]]]
        own = terms.index(record["term"])
        distractors = [terms[(own + step) % len(terms)] for step in range(1, min(3, len(terms) - 1) + 1)]
        cards.append({
            "key": concept_card_key(book, record["concept"]),
            "kind": "concept",
            "concept": record["concept"],
            "term": record["term"],
            "definition_md": record["definition_md"],
            "mode": "choice" if distractors else "flip",
            "distractors": distractors,
        })
    return cards
