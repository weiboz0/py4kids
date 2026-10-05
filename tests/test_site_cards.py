"""Predict cards, concept cards and glossary records (design 012 D8; plan 101 C)."""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from tools.books import book_path, books_with_flag
from tools.export.cards import concept_cards, glossary_records, predict_cards
from tools.export.concepts import book_registry
from tools.export.ids import duplicate_key_findings
from tools.export.lesson import lesson_dirs, lesson_export
from tools.publish import glossary_entries

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = Path(__file__).parent / "fixtures" / "site" / "units" / "unit-01-demo"
SCHEMA = json.loads((ROOT / "tools/export/schema/bundle.schema.json").read_text(encoding="utf-8"))
KEY = "python-projects/unit-01-demo/lesson"


def card_validator() -> Draft202012Validator:
    return Draft202012Validator(SCHEMA).evolve(schema=SCHEMA["$defs"]["card"])


def glossary(book: str) -> str:
    return (book_path(ROOT, book) / "back-matter" / "glossary.md").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def fixture_lesson():
    return lesson_export(ROOT, "python-projects", FIXTURE, timeout_s=2)


def test_predict_cards(fixture_lesson):
    cards = {card["block"]: card for card in predict_cards(fixture_lesson.blocks)}
    assert cards[f"{KEY}/c3"] == {"key": f"{KEY}/c3#predict", "kind": "predict",
                                  "block": f"{KEY}/c3", "mode": "typed", "prelude": []}
    assert cards[f"{KEY}/c9"]["mode"] == "flip"  # a two-line output
    assert cards[f"{KEY}/c2"]["prelude"] == [f"{KEY}/c1"]
    assert f"{KEY}/c5" not in cards and f"{KEY}/c6" not in cards  # timeout, error
    assert f"{KEY}/c1" not in cards  # no output
    assert f"{KEY}/c7" not in cards  # not a code block
    mismatch = {"key": "b/e/lesson/x", "type": "code", "code": "print(1)", "output": "1\n",
                "probe": "mismatch", "prelude": []}
    assert predict_cards([mismatch]) == []
    validator = card_validator()
    for card in cards.values():
        assert not list(validator.iter_errors(card))


FOUR = """# Glossary

**Apple** — A fruit. *(Unit 1)*
<!-- concept: apple -->

**Banana** — A *long* fruit with `peel`. *(Units 2–4)*
<!-- concept: banana -->

**Cherry** — A small fruit. *(Units 3, 5)*
<!-- concept: cherry -->

**Date** — A sweet fruit. *(Unit 0)*
<!-- concept: date; index: dates -->

**Hammer** — A tool. *(Unit 2)*
<!-- concept: hammer -->

**Saw** — Another tool. *(Unit 2)*
<!-- concept: saw -->

**Moon** — Alone in its category. *(Unit 6)*
<!-- concept: moon -->
"""
CONCEPTS = [
    {"id": "apple", "name": "Apple", "category": "fruit"},
    {"id": "banana", "name": "Banana", "category": "fruit"},
    {"id": "cherry", "name": "Cherry", "category": "fruit"},
    {"id": "date", "name": "Date", "category": "fruit"},
    {"id": "hammer", "name": "Hammer", "category": "tools"},
    {"id": "saw", "name": "Saw", "category": "tools"},
    {"id": "moon", "name": "Moon", "category": "space"},
]


def test_glossary_records_fixture():
    records = glossary_records(FOUR)
    assert records[1] == {"term": "Banana", "concept": "banana",
                          "definition_md": "A *long* fruit with `peel`.", "units": [2, 3, 4]}
    assert records[2]["units"] == [3, 5]
    assert records[3]["units"] == [0]
    assert len(records) == len(glossary_entries(FOUR)) == 7


def test_concept_cards_deterministic():
    records = glossary_records(FOUR)
    first = concept_cards(CONCEPTS, records, book="b")
    assert first == concept_cards(CONCEPTS, records, book="b")
    cards = {card["concept"]: card for card in first}
    assert cards["apple"]["distractors"] == ["Banana", "Cherry", "Date"]
    assert cards["cherry"]["distractors"] == ["Date", "Apple", "Banana"]  # wraps around
    category = {c["id"]: c["category"] for c in CONCEPTS}
    term_category = {r["term"]: category[r["concept"]] for r in records}
    for card in first:
        assert all(term_category[t] == category[card["concept"]] for t in card["distractors"])
        assert card["term"] not in card["distractors"]
    assert cards["hammer"]["mode"] == "choice" and cards["hammer"]["distractors"] == ["Saw"]
    assert cards["moon"] == {"key": "b/back-matter/glossary/moon", "kind": "concept",
                             "concept": "moon", "term": "Moon",
                             "definition_md": "Alone in its category.", "mode": "flip",
                             "distractors": []}
    validator = card_validator()
    for card in first:
        assert not list(validator.iter_errors(card)), card["key"]


def test_concept_cards_unknown_concept_fails():
    with pytest.raises(ValueError, match="moon"):
        concept_cards(CONCEPTS[:-1], glossary_records(FOUR), book="b")


@pytest.mark.parametrize("book", ["python-projects", "python-concepts", "usaco-bronze", "acsl"])
def test_glossary_records_real_books(book):
    source = glossary(book)
    records = glossary_records(source)
    assert len(records) == len(glossary_entries(source))
    assert [r["term"] for r in records] == [term for term, _c, _k in glossary_entries(source)]
    for record in records:
        assert record["definition_md"] and record["units"]
        assert " *(Unit" not in record["definition_md"]


@pytest.mark.parametrize("book", ["python-projects", "python-concepts", "usaco-bronze", "acsl"])
def test_concept_cards_real_books(book):
    registry = book_registry(ROOT, book)
    records = glossary_records(glossary(book))
    cards = concept_cards(list(registry.concepts), records, book=book)
    assert len(cards) == len(records)
    category_of_term = {r["term"]: registry.category(r["concept"]) for r in records}
    validator = card_validator()
    for card in cards:
        own = registry.category(card["concept"])
        assert all(category_of_term[term] == own for term in card["distractors"])
        assert not list(validator.iter_errors(card)), card["key"]


def test_keys_unique_across_kinds(fixture_lesson):
    """A predict card's key differs from its block's; block and card keys never collide.

    Items join this union in Phase E (`site_check_findings` runs it over blocks, items and cards).
    """
    cards = predict_cards(fixture_lesson.blocks)
    assert cards and all(card["key"] != card["block"] for card in cards)
    keys = [b["key"] for b in fixture_lesson.blocks] + [c["key"] for c in cards]
    assert duplicate_key_findings(keys) == []
    for book in books_with_flag(ROOT, "site"):
        registry = book_registry(ROOT, book)
        keys = []
        for entry_dir in lesson_dirs(ROOT, book):
            blocks = lesson_export(ROOT, book, entry_dir, probe=False, registry=registry).blocks
            for block in blocks:
                block["probe"] = "standalone"  # every code block card-eligible: the widest key set
            keys += [b["key"] for b in blocks] + [c["key"] for c in predict_cards(blocks)]
        keys += [c["key"] for c in concept_cards(list(registry.concepts),
                                                 glossary_records(glossary(book)), book=book)]
        assert duplicate_key_findings(keys) == [], book
