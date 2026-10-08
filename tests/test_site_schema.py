"""The bundle and progress-event JSON Schemas (design 012 D3, D11; plan 101 B)."""

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from tools.export import SCHEMA_VERSION

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "tools" / "export" / "schema"
HASH = "sha256:" + "0" * 64
HASH2 = "sha256:" + "ab" * 32


def load(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


BUNDLE = load("bundle.schema.json")
EVENT = load("progress-event.schema.json")


def validator(schema: dict, definition: str | None = None) -> Draft202012Validator:
    """A validator for the whole schema, or for one of its `$defs` (refs resolve against the root)."""
    root = Draft202012Validator(schema)
    return root if definition is None else root.evolve(schema=schema["$defs"][definition])


def errors(instance, schema=BUNDLE, definition=None) -> list[str]:
    return [error.message for error in validator(schema, definition).iter_errors(instance)]


def is_valid(instance, schema=BUNDLE, definition=None) -> bool:
    return validator(schema, definition).is_valid(instance)


# --- samples ---------------------------------------------------------------------------------


def block(key, type_, **fields):
    base = {"key": key, "type": type_, "needs_prelude": False, "prelude": [], "files": [],
            "concepts": [], "probe": None, "tags": []}
    base.update(fields)
    return base


def book_json() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "book": {"id": "acsl", "title": "Contest Python: ACSL",
                 "subtitle": "From Elementary to Senior, one contest at a time",
                 "flags": {"acsl": True, "judge": True}},
        "release": {"tag": "unreleased", "content_hash": HASH},
        "entries": [
            {"id": "unit-01-computer-number-systems", "kind": "unit",
             "title": "Computer Number Systems", "number": 1,
             "file": "entries/unit-01-computer-number-systems.json"},
            {"id": "checkpoint-01-contest-1", "kind": "checkpoint", "title": "Contest 1",
             "number": 1, "file": "entries/checkpoint-01-contest-1.json"},
            {"id": "project-01-arcade-night", "kind": "project", "title": "Arcade Night",
             "number": None, "file": "entries/project-01-arcade-night.json"},
        ],
        "concepts": [{"id": "base-conversion", "name": "Number base conversion",
                      "category": "number-theory"}],
        "glossary": [{"term": "Hexadecimal", "definition_md": "Base 16, with digits `0`–`F`.",
                      "concept": "base-conversion", "units": [1, 3]}],
        "reference_md": "# Quick Reference\n\n| a | b |\n",
        "settings": {"lesson_heading": "^## Lesson", "acsl_divisions": ["junior", "senior"]},
        "pdfs": {edition: f"https://github.com/weiboz0/py4kids/releases/download/t/acsl-{edition}.pdf"
                 for edition in ("student-print", "student", "answer-key", "teacher")},
    }


def unit_entry() -> dict:
    key = "acsl/unit-01-computer-number-systems"
    return {
        "schema_version": SCHEMA_VERSION,
        "entry": {"id": "unit-01-computer-number-systems", "kind": "unit",
                  "title": "Computer Number Systems"},
        "lesson": {"blocks": [
            block(f"{key}/lesson/h0", "opener", md="Computers count in binary."),
            block(f"{key}/lesson/m1", "goals", md="### You will learn\n\n- bases"),
            block(f"{key}/lesson/m2", "prose", md="## Bases\n\nText."),
            block(f"{key}/lesson/m2#2", "prose", md="### More\n\nText.", tags=["slide-break"]),
            block(f"{key}/lesson/m3", "notice", md="**Notice:** hex digits."),
            block(f"{key}/lesson/c1", "code", code="x = 3", route="code", probe="standalone",
                  concepts=["base-conversion"]),
            block(f"{key}/lesson/c2", "code", code="print(x * 2)", output="6\n",
                  route="code+output", probe="prelude", needs_prelude=True,
                  prelude=[f"{key}/lesson/c1"]),
            block(f"{key}/lesson/c3", "tryit", code="n = input()", route="tryit-stdin",
                  stdin=True, sample_input="5\n"),
            block(f"{key}/lesson/c4", "error-demo", code="1/0", route="errordemo"),
            block(f"{key}/lesson/c5", "hang-demo", code="while True: pass", route="hangdemo"),
            block(f"{key}/lesson/c6", "turtle-figure", code="import turtle", route="figure",
                  figure=[{"x1": 0, "y1": 0, "x2": 100, "y2": 0, "color": "black", "width": 1}]),
            block(f"{key}/lesson/c7", "program", code="print(open('d.txt').read())",
                  route="program", files=["files/unit-01-computer-number-systems/d.txt"],
                  probe="mismatch"),
            block(f"{key}/lesson/a1#asset:hex.py", "program", code="print(hex(255))"),
            block(f"{key}/lesson/m9", "recap", md="### Recap\n\n- done"),
        ]},
        "intro": [block(f"{key}/exercises/p1", "prose", md="Work through these.")],
        "items": [
            {
                "key": f"{key}/exercises/e1", "kind": "unit", "number": 1, "label": "Exercise 1",
                "title": "Binary to decimal", "division": ["junior"], "stretch": False,
                "concepts": ["base-conversion"], "statement_md": "Convert `1011`.", "starter": "",
                "files": [], "check": {"kind": "answer", "hash": HASH,
                                       "answer_format": {"case": "sensitive", "hint": "a number"},
                                       "turtle": False, "confirmed": True},
                "answer_visibility": "after-attempt", "answer_md": "**Answer:** 11",
                "before": [],
            },
            {
                "key": f"{key}/exercises/e2", "kind": "unit", "number": 2, "label": "Exercise 2",
                "title": "Hex", "division": [], "stretch": False, "concepts": [],
                "statement_md": "Convert `FF`.", "starter": "# your code\n",
                "files": [], "check": {"kind": "answer", "hash": HASH2,
                                       "answer_format": {"case": "insensitive", "hint": "a number"},
                                       "turtle": False, "confirmed": False},
                "answer_visibility": "none",
                "before": [block(f"{key}/exercises/n1", "notice", md="**Notice:** a hint.")],
            },
            {
                "key": f"{key}/exercises/n2#2", "kind": "challenge", "number": None,
                "label": "Challenge 1", "title": "Draw", "division": [], "stretch": True,
                "concepts": [], "statement_md": "Draw a square.", "starter": "import turtle",
                "files": [], "check": {"kind": "self-check", "requirements": ["a square"],
                                       "turtle": True, "confirmed": False},
                "answer_visibility": "none",
                "before": [block(f"{key}/exercises/n2", "prose", md="## Challenge"),
                           block(f"{key}/exercises/s1", "starter", code="import turtle")],
            },
        ],
        "outro": [block(f"{key}/exercises/z1", "prose", md="Make it yours."),
                  block(f"{key}/exercises/z2", "goals", md="- [ ] it runs")],
        "cards": [
            {"key": f"{key}/lesson/c2#predict", "kind": "predict", "block": f"{key}/lesson/c2",
             "mode": "typed", "prelude": [f"{key}/lesson/c1"]},
            {"key": "acsl/back-matter/glossary/base-conversion", "kind": "concept",
             "concept": "base-conversion", "term": "Hexadecimal",
             "definition_md": "Base 16.", "mode": "choice",
             "distractors": ["Binary", "Octal", "Decimal"]},
            {"key": "acsl/back-matter/glossary/bfs", "kind": "concept", "concept": "bfs",
             "term": "Breadth-first search", "definition_md": "Level by level.",
             "mode": "flip", "distractors": []},
        ],
        "files": ["files/unit-01-computer-number-systems/d.txt"],
    }


def check(kind: str) -> dict:
    fmt = {"case": "sensitive", "hint": "one line"}
    base = {"turtle": False, "confirmed": False}
    data = {
        "fixtures": {"cases": [
            {"n": 1, "in_file": "files/unit-03-x/fixtures/ex1/1.in",
             "out_file": "files/unit-03-x/fixtures/ex1/1.out", "sample": True},
            {"n": 2, "in_file": "files/unit-03-x/fixtures/ex1/2.in",
             "out_file": "files/unit-03-x/fixtures/ex1/2.out", "sample": False}],
            "match": "token", "over_budget": [3], "cpu_ms": 200},
        "answer": {"hash": HASH, "answer_format": fmt},
        "asserts": {"source": "assert double(3) == 6", "functions": ["double"]},
        "expected-output": {"hash": HASH, "answer_format": fmt},
        "predict": {"hash": HASH, "answer_format": fmt, "program": "print(1 + 1)"},
        "self-check": {"requirements": ["it draws a square", "it uses a loop"]},
    }[kind]
    return {"kind": kind, **data, **base}


def item_with(check_data: dict, **fields) -> dict:
    item = copy.deepcopy(unit_entry()["items"][1])
    item["check"] = check_data
    item.update(fields)
    return item


# --- tests -----------------------------------------------------------------------------------


def test_schemas_are_valid_2020_12():
    Draft202012Validator.check_schema(BUNDLE)
    Draft202012Validator.check_schema(EVENT)
    assert BUNDLE["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert EVENT["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert BUNDLE["$id"] == f"py4kids/bundle/{SCHEMA_VERSION}"
    assert SCHEMA_VERSION == "1.1.0"


def _objects(node):
    if isinstance(node, dict):
        if node.get("type") == "object" or "properties" in node:
            yield node
        for value in node.values():
            yield from _objects(value)
    elif isinstance(node, list):
        for value in node:
            yield from _objects(value)


@pytest.mark.parametrize("schema", [BUNDLE, EVENT], ids=["bundle", "progress-event"])
def test_additional_properties_false_throughout(schema):
    objects = list(_objects(schema))
    assert objects
    for node in objects:
        if node.get("type") == "object" and "properties" in node:
            assert node.get("additionalProperties") is False, node
        elif node.get("type") == "object":  # a map (pdfs) constrains its keys and values
            assert "propertyNames" in node or node.get("additionalProperties") is False, node


def test_book_json_validates():
    assert errors(book_json()) == []
    assert errors(book_json(), definition="book_file") == []
    unreleased = book_json()
    unreleased["pdfs"] = None
    del unreleased["settings"]["acsl_divisions"]
    assert errors(unreleased, definition="book_file") == []


def test_book_json_rejects_unknown_and_missing_fields():
    extra = book_json()
    extra["book"]["owner"] = "x"
    assert not is_valid(extra, definition="book_file")
    missing = book_json()
    del missing["reference_md"]
    assert not is_valid(missing, definition="book_file")
    bad_edition = book_json()
    bad_edition["pdfs"]["deluxe"] = "https://example.com/x.pdf"
    assert not is_valid(bad_edition, definition="book_file")
    bad_version = book_json()
    bad_version["schema_version"] = "0.9.0"
    assert not is_valid(bad_version, definition="book_file")


def test_entry_with_intro_outro_and_before_validates():
    entry = unit_entry()
    assert errors(entry) == []
    assert errors(entry, definition="entry_file") == []
    assert entry["intro"] and entry["outro"] and entry["items"][1]["before"]


def test_checkpoint_entry_without_lesson_validates():
    entry = unit_entry()
    entry["entry"]["kind"] = "checkpoint"
    entry["lesson"] = None
    for item in entry["items"]:
        item["kind"] = "checkpoint"
        item["answer_visibility"] = "none"
        item.pop("answer_md", None)
    assert errors(entry, definition="entry_file") == []


@pytest.mark.parametrize("kind", ["code", "tryit", "error-demo", "program", "opener"])
def test_intro_outro_before_blocks_are_restricted(kind):
    entry = unit_entry()
    entry["intro"].append(block("acsl/unit-01-computer-number-systems/exercises/q",
                                kind, code="x", md="x"))
    assert not is_valid(entry, definition="entry_file")


def test_block_shape():
    good = block("b/unit-01-x/lesson/c1", "code", code="x = 1")
    assert is_valid(good, definition="block")
    assert not is_valid({**good, "type": "video"}, definition="block")
    assert not is_valid({**good, "extra": 1}, definition="block")
    assert not is_valid({**good, "probe": "timeout"}, definition="block")  # FAIL, never data
    assert not is_valid({**good, "probe": "error"}, definition="block")
    assert not is_valid(block("b/unit-01-x/lesson/c1", "code"), definition="block")  # no code
    assert not is_valid(block("b/unit-01-x/lesson/m1", "prose"), definition="block")  # no md
    assert not is_valid(block("b/unit-01-x/lesson/c6", "turtle-figure", code="t"),
                        definition="block")  # no figure
    tagless = dict(good)
    del tagless["tags"]
    assert not is_valid(tagless, definition="block")
    assert not is_valid({**good, "key": "not a key"}, definition="block")


@pytest.mark.parametrize(
    "kind", ["fixtures", "answer", "asserts", "expected-output", "predict", "self-check"]
)
def test_every_check_kind_validates(kind):
    assert errors(item_with(check(kind)), definition="item") == []
    assert errors(check(kind), definition="check") == []


def test_check_rejects_mixed_or_unknown_kinds():
    mixed = {**check("answer"), "requirements": ["x"]}
    assert not is_valid(mixed, definition="check")
    assert not is_valid({**check("answer"), "kind": "bogus"}, definition="check")
    no_flags = check("answer")
    del no_flags["confirmed"]
    assert not is_valid(no_flags, definition="check")
    assert not is_valid({**check("answer"), "hash": "md5:abc"}, definition="check")
    empty = {**check("self-check"), "requirements": []}
    assert not is_valid(empty, definition="check")


def test_fixtures_ship_paths_not_text():
    inline = check("fixtures")
    inline["cases"][0]["input"] = "3\n1 2 3\n"
    assert not is_valid(inline, definition="check")
    outside = check("fixtures")
    outside["cases"][0]["in_file"] = "assets/ex1/1.in"
    assert not is_valid(outside, definition="check")
    bad_match = {**check("fixtures"), "match": "exact"}
    assert not is_valid(bad_match, definition="check")


def test_answer_md_tied_to_after_attempt():
    hidden = item_with(check("answer"))
    assert is_valid(hidden, definition="item")
    assert not is_valid({**hidden, "answer_md": "**Answer:** 255"}, definition="item")
    odd = unit_entry()["items"][0]
    assert is_valid(odd, definition="item")
    no_answer = dict(odd)
    del no_answer["answer_md"]
    assert not is_valid(no_answer, definition="item")
    # after-attempt is for odd unit exercises only
    assert not is_valid({**odd, "number": 2}, definition="item")
    assert not is_valid({**odd, "kind": "checkpoint"}, definition="item")
    assert not is_valid({**odd, "kind": "challenge", "number": None}, definition="item")
    assert not is_valid({**odd, "answer_visibility": "always"}, definition="item")


def test_cards():
    cards = unit_entry()["cards"]
    for card in cards:
        assert errors(card, definition="card") == []
    predict, choice, flip = cards
    assert not is_valid({**predict, "mode": "choice"}, definition="card")
    assert not is_valid({**predict, "key": predict["block"]}, definition="card")  # needs #predict
    assert not is_valid({**choice, "distractors": ["a", "b", "c", "d"]}, definition="card")
    assert not is_valid({**choice, "distractors": []}, definition="card")  # choice needs one
    assert is_valid({**choice, "distractors": ["Binary"]}, definition="card")
    assert not is_valid({**flip, "distractors": ["x"]}, definition="card")
    assert not is_valid({**choice, "mode": "typed"}, definition="card")
    assert not is_valid({**choice, "key": "acsl/unit-01-x/lesson/c1"}, definition="card")


# --- progress events (D11) -------------------------------------------------------------------

EVENT_KINDS = ["lesson-run", "slide", "card", "exercise", "checkpoint", "project", "self-check"]


def event(kind: str, **fields) -> dict:
    base = {
        "schema": "py4kids/progress-event/1.0.0",
        "event_id": "6f1c2a9e-3b4d-4c5e-8f60-123456789abc",
        "book": "acsl",
        "item_key": "acsl/unit-01-computer-number-systems/exercises/e1",
        "kind": kind,
        "result": "pass",
        "detail": {},
        "duration_ms": 1200,
        "timestamp": "2026-10-05T12:00:00Z",
        "content_hash": HASH,
    }
    base.update(fields)
    return base


SAMPLE_DETAIL = {
    "lesson-run": ({"result": "done"}, {}),
    "slide": ({"result": "seen"}, {}),
    "card": ({"result": "pass"}, {"self_grade": "got-it", "box": 2}),
    "exercise": ({"result": "fail"}, {"cases": [{"n": 1, "pass": True}, {"n": 2, "pass": False}]}),
    "checkpoint": ({"result": "pass"}, {"cases": [{"n": 1, "pass": True}]}),
    "project": ({"result": "partial"}, {"checklist": [True, False]}),
    "self-check": ({"result": "done"}, {"checklist": [True, True], "self_grade": "not-yet"}),
}


@pytest.mark.parametrize("kind", EVENT_KINDS)
def test_progress_event_per_kind(kind):
    fields, detail = SAMPLE_DETAIL[kind]
    assert errors(event(kind, detail=detail, **fields), schema=EVENT) == []


def test_progress_event_fields_exactly_d11():
    assert set(EVENT["properties"]) == {"schema", "event_id", "book", "item_key", "kind",
                                        "result", "detail", "duration_ms", "timestamp",
                                        "content_hash"}
    assert set(EVENT["required"]) == set(EVENT["properties"])
    assert EVENT["properties"]["kind"]["enum"] == EVENT_KINDS


def test_progress_event_carries_no_code_or_text():
    assert not is_valid(event("exercise", code="print(1)"), schema=EVENT)
    assert not is_valid(event("exercise", detail={"text": "my answer is 5"}), schema=EVENT)
    assert not is_valid(event("exercise", detail={"answer": "5"}), schema=EVENT)
    assert not is_valid(event("exercise", detail={"cases": [{"n": 1, "pass": True,
                                                             "stdout": "5"}]}), schema=EVENT)
    assert not is_valid(event("card", detail={"self_grade": "maybe"}), schema=EVENT)
    assert not is_valid(event("card", detail={"box": "2"}), schema=EVENT)
    assert not is_valid(event("project", detail={"checklist": ["done"]}), schema=EVENT)
    assert not is_valid(event("bogus"), schema=EVENT)
    missing = event("slide")
    del missing["event_id"]
    assert not is_valid(missing, schema=EVENT)
