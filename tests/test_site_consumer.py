"""The minimal bundle consumer (`tests/site_consumer.py`), a stand-in for part B (plan 101 F).

(a) it renders every entry of every real book without a KeyError and writes only under tmp_path;
(b) every key it reads is declared by the bundle schema (a recording dict proves it);
(c) on a fixture bundle each check kind shows its control, a project page shows its intro, `before`
and outro ("Make it yours"), a unit shows its card deck, the glossary renders, and one real odd
turtle exercise's `answer_md` renders with its `{=latex}` block stripped.
"""

import html
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from tools.export import answers
from tools.export.bundle import export_book

sys.path.insert(0, str(Path(__file__).parent))
import site_consumer

ROOT = Path(__file__).resolve().parents[1]
REAL_BOOKS = ["python-projects", "python-concepts", "usaco-bronze", "acsl"]
SCHEMA = json.loads((ROOT / "tools/export/schema/bundle.schema.json").read_text(encoding="utf-8"))
DEFS = SCHEMA["$defs"]
_spec = importlib.util.spec_from_file_location(
    "site_demo_book", Path(__file__).parent / "fixtures" / "site" / "demo_book.py")
demo_book = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(demo_book)


# --- a recording reader -------------------------------------------------------------------------


class Recorder:
    def __init__(self):
        self.reads: list[tuple[str, tuple, str]] = []  # (bundle file, JSON pointer, key read)
        self.raw: dict[str, object] = {}

    def load(self, path: Path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        name = Path(path).name if Path(path).name == "book.json" else f"entries/{Path(path).name}"
        self.raw[name] = data
        return self.wrap(data, name, ())

    def wrap(self, value, name: str, pointer: tuple):
        if isinstance(value, dict):
            return RecordingDict(self, name, pointer, value)
        if isinstance(value, list):
            return [self.wrap(v, name, (*pointer, i)) for i, v in enumerate(value)]
        return value


class RecordingDict(dict):
    def __init__(self, recorder: Recorder, name: str, pointer: tuple, data: dict):
        super().__init__({k: recorder.wrap(v, name, (*pointer, k)) for k, v in data.items()})
        self._log = (recorder, name, pointer)

    def _record(self, key):
        recorder, name, pointer = self._log
        recorder.reads.append((name, pointer, key))

    def __getitem__(self, key):
        self._record(key)
        return super().__getitem__(key)

    def get(self, key, default=None):
        self._record(key)
        return super().get(key, default)

    def __contains__(self, key):
        self._record(key)
        return super().__contains__(key)


_VALID: dict[tuple[int, int], bool] = {}


def _valid(node: dict, instance) -> bool:
    """Memoised on the (schema node, instance) pair; `_VALID` is cleared before each walk over one
    recorder's JSON, which stays alive for the whole walk (so no id is reused within it)."""
    key = (id(node), id(instance))
    if key not in _VALID:
        _VALID[key] = Draft202012Validator(SCHEMA).evolve(schema=node).is_valid(instance)
    return _VALID[key]


def _candidates(node: dict, instance) -> list[dict]:
    """`node` and every subschema that applies to `instance` ($ref, allOf, a valid oneOf/anyOf
    branch, the if/then/else branch taken)."""
    while "$ref" in node:
        node = DEFS[node["$ref"].rsplit("/", 1)[1]]
    out = [node]
    for sub in node.get("allOf", []):
        out += _candidates(sub, instance)
    for word in ("oneOf", "anyOf"):
        for sub in node.get(word, []):
            if _valid(sub, instance):
                out += _candidates(sub, instance)
    if "if" in node:
        branch = node.get("then") if _valid(node["if"], instance) else node.get("else")
        if branch:
            out += _candidates(branch, instance)
    return out


def declared(definition: str, raw, pointer: tuple, key: str) -> bool:
    nodes, instance = [DEFS[definition]], raw
    for step in pointer:
        children = []
        for node in nodes:
            for candidate in _candidates(node, instance):
                if isinstance(step, int) and "items" in candidate:
                    children.append(candidate["items"])
                elif isinstance(step, str) and step in candidate.get("properties", {}):
                    children.append(candidate["properties"][step])
        nodes, instance = children, instance[step]
    return any(key in candidate.get("properties", {})
               for node in nodes for candidate in _candidates(node, instance))


# --- fixtures -----------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def demo_bundle(tmp_path_factory):
    answers.clear_caches()
    base = tmp_path_factory.mktemp("consumer-demo")
    root = demo_book.build_site_root(base / "root")
    export_book(root, "demo", base / "bundle")
    return base / "bundle"


def _snapshot() -> dict[str, int]:
    out = {}
    for directory, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", ".venv", "__pycache__", ".pytest_cache",
                                                ".ruff_cache")]
        for name in files:
            path = os.path.join(directory, name)
            out[path] = os.stat(path).st_mtime_ns
    return out


# --- (a) every real entry renders ---------------------------------------------------------------


@pytest.mark.slow
@pytest.mark.parametrize("book", REAL_BOOKS)
def test_renders_every_real_entry(real_site_bundle, tmp_path, book):
    bundle = real_site_bundle(book)
    before = _snapshot()
    written = site_consumer.render_bundle(bundle, tmp_path / "site")
    assert _snapshot() == before  # nothing written in the repo
    entries = json.loads((bundle / "book.json").read_text())["entries"]
    assert len(written) == len(entries) + 2
    assert all(path.is_relative_to(tmp_path) for path in written)
    assert {p.name for p in (tmp_path / "site").iterdir()} == {p.name for p in written}


# --- (b) only declared fields are read ----------------------------------------------------------


def _assert_declared(recorder: Recorder) -> int:
    _VALID.clear()
    undeclared = []
    for name, pointer, key in set(recorder.reads):
        definition = "book_file" if name == "book.json" else "entry_file"
        if not declared(definition, recorder.raw[name], pointer, key):
            undeclared.append((name, pointer, key))
    assert undeclared == []
    return len(set(recorder.reads))


def test_declared_check_catches_an_undeclared_key(demo_bundle):
    raw = json.loads((demo_bundle / "entries" / "unit-01-demo.json").read_text())
    _VALID.clear()
    assert declared("entry_file", raw, ("items", 1, "check"), "hash")
    assert not declared("entry_file", raw, ("items", 0, "check"), "hash")  # a fixtures check
    assert not declared("entry_file", raw, ("items", 0), "solution")
    assert declared("entry_file", raw, ("lesson", "blocks", 0), "md")


def test_fixture_bundle_reads_only_declared_keys(demo_bundle, tmp_path):
    recorder = Recorder()
    site_consumer.render_bundle(demo_bundle, tmp_path / "site", load=recorder.load)
    assert _assert_declared(recorder) > 40


@pytest.mark.slow
@pytest.mark.parametrize("book", REAL_BOOKS)
def test_real_bundle_reads_only_declared_keys(real_site_bundle, tmp_path, book):
    recorder = Recorder()
    site_consumer.render_bundle(real_site_bundle(book), tmp_path / "site", load=recorder.load)
    assert _assert_declared(recorder) > 40


# --- (c) the pages ------------------------------------------------------------------------------


def _section(page: str, key: str) -> str:
    start = page.index(f'id="{key}"')
    return page[start:page.index("</section>", start)]


def test_each_check_kind_shows_its_control(demo_bundle, tmp_path):
    site_consumer.render_bundle(demo_bundle, tmp_path / "site")
    page = (tmp_path / "site" / "unit-01-demo.html").read_text()
    entry = json.loads((demo_bundle / "entries" / "unit-01-demo.json").read_text())
    kinds: dict[str, str] = {}
    for item in entry["items"]:
        kinds.setdefault(item["check"]["kind"], item["key"])
    assert set(kinds) == set(site_consumer.CONTROL)
    for kind, key in kinds.items():
        section = _section(page, key)
        control = site_consumer.CONTROL[kind]
        assert f'class="{control}"' in section, kind
        assert all(f'class="{other}"' not in section
                   for other in site_consumer.CONTROL.values() if other != control), kind
    assert "<pre>3\n</pre>" in _section(page, kinds["fixtures"])  # only the sample's input shows
    assert "10" not in _section(page, kinds["fixtures"]).split('class="fixture-list"')[1]
    assert "for i in range(3)" in _section(page, kinds["predict"])
    asserts = next(i for i in entry["items"] if i["key"] == kinds["asserts"])["check"]
    section = _section(page, kinds["asserts"])
    assert "Checks: double" in section  # the function summary
    assert section.count('class="assert-result"') == 2  # one pass/fail line per assert
    assert "assert double" not in section and "double(3)" not in section  # D5: no assert source
    for item in entry["items"]:
        if item["check"]["kind"] == "asserts":
            assert html.escape(item["check"]["source"]) not in page
            assert item["check"]["source"] not in page
    assert asserts["source"].startswith("assert double(3) == 6")
    assert '<details class="answer">' in _section(page, kinds["predict"])  # odd: after-attempt
    assert '<details class="answer">' not in _section(page, kinds["answer"])  # even: none
    # plan 102 Phase 0: an item's `also_check` shows as a self-check list beside its check.
    also = next(i for i in entry["items"] if i.get("also_check"))
    section = _section(page, also["key"])
    assert '<ul class="also-check">' in section
    assert section.count('<input type="checkbox">') == len(also["also_check"])
    assert html.escape(also["also_check"][0]) in section


def test_checkpoint_project_cards_and_glossary(demo_bundle, tmp_path):
    site_consumer.render_bundle(demo_bundle, tmp_path / "site")
    site = tmp_path / "site"
    checkpoint = (site / "checkpoint-01-demo.html").read_text()
    assert checkpoint.count('class="item checkpoint"') == 2
    project = (site / "project-01-demo.html").read_text()
    assert project.index("Build two helpers") < project.index("Milestone 2") \
        < project.index("Problem 2") < project.index("Make it yours")
    assert project.index("Make it yours") > project.rindex("</section>")  # the outro
    unit = (site / "unit-01-demo.html").read_text()
    deck = unit[unit.index('<div class="deck">'):]
    assert 'class="card concept' in deck and "Shows a value on the screen." in deck
    glossary = (site / "glossary.html").read_text()
    assert all(term in glossary for term in ("print", "variable", "for loop", "range"))
    index = (site / "index.html").read_text()
    assert "Quick Reference" in index and "unit-01-demo.html" in index


@pytest.mark.slow
def test_odd_turtle_answer_md_renders(real_site_bundle):
    entry = json.loads((real_site_bundle("python-concepts") / "entries"
                        / "unit-06-turtle-geometry.json").read_text())
    item = next(i for i in entry["items"] if i["answer_visibility"] == "after-attempt"
                and "{=latex}" in i["answer_md"])
    assert item["number"] % 2 and "::: {.program}" in item["answer_md"]
    rendered = site_consumer.markdown(item["answer_md"])
    assert "{=latex}" not in rendered and "tikzpicture" not in rendered
    assert '<div class="program">' in rendered and rendered.count("</div>") >= 1
    assert '<pre class="python answer-code">' in rendered
    assert re.search(r"import turtle", rendered)
    assert ":::" not in rendered
