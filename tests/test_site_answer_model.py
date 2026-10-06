"""The answer-model checks over a written bundle (design 012 D5; plan 101 F, checks 1-6).

Every regression the plan names injects one leak into an exported bundle (a JSON string or a copied
file) and expects a `FAIL:`; the legitimate collisions (`True` in another statement, a canonical in a
shipped fixture `.out`, an even answer equal to an odd released one) must pass.
"""

import importlib.util
import json
import re
import shutil
from pathlib import Path

import pytest
import yaml

from tools.export import answers
from tools.export.answer_model import (
    COUNTED_FIELDS,
    FIELD_TIES,
    TIES,
    AnswerModel,
    counted,
    load_bundle,
    tie_of,
)
from tools.export.bundle import dumps, export_book
from tools.export.check import answer_model_findings

ROOT = Path(__file__).resolve().parents[1]
REAL_BOOKS = ["python-projects", "python-concepts", "usaco-bronze", "acsl"]
_spec = importlib.util.spec_from_file_location(
    "site_demo_book", Path(__file__).parent / "fixtures" / "site" / "demo_book.py")
demo_book = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(demo_book)


# --- helpers ------------------------------------------------------------------------------------


class Demo:
    def __init__(self, root: Path, bundle: Path):
        self.root, self.bundle = root, bundle
        self.model = AnswerModel(root, "demo")


@pytest.fixture(scope="module")
def demo(tmp_path_factory):
    answers.clear_caches()
    base = tmp_path_factory.mktemp("answer-model")
    root = demo_book.build_answer_model_root(base / "root")
    export_book(root, "demo", base / "bundle")
    return Demo(root, base / "bundle")


@pytest.fixture
def bundle(demo, tmp_path):
    """A private copy of the demo bundle to inject into."""
    copy = tmp_path / "bundle"
    shutil.copytree(demo.bundle, copy)
    return copy


def fails(model: AnswerModel, bundle_dir: Path) -> list[str]:
    return [f for f in model.findings(bundle_dir) if f.startswith("FAIL:")]


def entry_path(bundle_dir: Path, entry: str) -> Path:
    return bundle_dir / "entries" / f"{entry}.json"


def edit_item(bundle_dir: Path, entry: str, label: str, edit) -> None:
    path = entry_path(bundle_dir, entry)
    data = json.loads(path.read_text(encoding="utf-8"))
    edit(next(item for item in data["items"] if item["label"] == label))
    path.write_text(dumps(data), encoding="utf-8")


def append_to_statement(bundle_dir: Path, entry: str, label: str, text: str) -> None:
    def edit(item):
        item["statement_md"] += "\n" + text + "\n"
    edit_item(bundle_dir, entry, label, edit)


def append_to_file(bundle_dir: Path, relative: str, text: str) -> None:
    path = bundle_dir / relative
    path.write_text(path.read_text(encoding="utf-8") + "\n" + text + "\n", encoding="utf-8")


COPIED_FILE = "files/unit-01-demo/assets/count_helper.py"


# --- the demo bundle: clean, and the legitimate collisions ----------------------------------------


def test_clean_demo_bundle_passes(demo):
    """Shipped asserts, the `True` collision, the `.out` collision (`20` = fixture `2.out`), the
    odd/even `1110` collision and the odd released explanation all pass."""
    assert fails(demo.model, demo.bundle) == []
    # The hook in check.py runs the same checks.
    assert [f for f in answer_model_findings(demo.root, "demo", demo.bundle)
            if f.startswith("FAIL:")] == []


def test_hook_reports_injected_leak(demo, bundle):
    """`check.answer_model_findings` (the site-check hook) runs the checks."""
    append_to_statement(bundle, "unit-03-leaks", "Exercise 4", "159")
    found = answer_model_findings(demo.root, "demo", bundle)
    assert any("u3e04: hidden answer text" in f for f in found), found


def test_collisions_are_really_present(demo):
    """The passing collisions are real: the canonicals occur in the bundle, the baseline allows them."""
    bundle = load_bundle(demo.bundle)
    counts = demo.model.canonical_counts(bundle)
    by_key = {key: (b, s) for key, b, s in counts}
    leaks = "demo/unit-03-leaks/exercises/"
    assert by_key[leaks + "u3e11"] == (1, 1)  # `20`: once, as fixtures/ex1/2.out
    b, s = by_key[leaks + "u3e09"]  # even `1110` = odd Exercise 1's released answer
    assert b == s >= 1
    b, s = by_key[leaks + "u3e02"]  # `True` appears in Exercise 9's statement
    assert b == s >= 1
    # The odd released explanation is in the bundle and not part of the hidden prose corpus.
    assert demo_book.ODD_PROSE in json.dumps(json.loads(
        entry_path(demo.bundle, "unit-03-leaks").read_text()), ensure_ascii=False)
    assert all(demo_book.ODD_PROSE not in p.text for p in demo.model.hidden_prose)


# --- check 2: hidden canonical texts ------------------------------------------------------------


def test_injected_canonical_in_statement_fails(demo, bundle):
    append_to_statement(bundle, "unit-03-leaks", "Exercise 4", "159")
    found = fails(demo.model, bundle)
    assert any(f.startswith("FAIL: demo: demo/unit-03-leaks/exercises/u3e04: hidden answer text")
               for f in found), found


def test_injected_case_insensitive_canonical_fails(demo, bundle):
    append_to_statement(bundle, "unit-01-demo", "Exercise 2", "It is a zebra.")
    found = fails(demo.model, bundle)
    assert any("demo/unit-01-demo/exercises/u1e03: hidden answer text" in f for f in found), found


def test_extra_copy_of_fixture_text_fails(demo, bundle):
    """`20` occurs once (fixtures/ex1/2.out): an extra copy in a JSON string fails the count."""
    append_to_statement(bundle, "unit-01-demo", "Exercise 6", "Print 20 greetings.")
    found = fails(demo.model, bundle)
    assert any("demo/unit-03-leaks/exercises/u3e11: hidden answer text" in f for f in found), found


def test_canonical_in_self_check_requirement_fails(demo, bundle):
    """[sol] 3: every student-visible string counts, self-check requirements included."""
    edit_item(bundle, "unit-01-demo", "Exercise 6",
              lambda item: item["check"]["requirements"].append("The sum is 159."))
    found = fails(demo.model, bundle)
    assert any("u3e04: hidden answer text" in f and "check/requirements/2" in f
               for f in found), found


def test_canonical_in_answer_format_hint_fails(demo, bundle):
    def edit(item):
        item["check"]["answer_format"]["hint"] = "like 159"
    edit_item(bundle, "unit-03-leaks", "Exercise 2", edit)
    found = fails(demo.model, bundle)
    assert any("u3e04: hidden answer text" in f and "answer_format/hint" in f for f in found), found


def test_canonical_in_concept_name_fails(demo, bundle):
    data = json.loads((bundle / "book.json").read_text())
    data["concepts"][0]["name"] = "Printing 159"
    (bundle / "book.json").write_text(dumps(data))
    found = fails(demo.model, bundle)
    assert any("u3e04: hidden answer text" in f and "concepts/0/name" in f for f in found), found


def test_counted_fields_are_everything_but_non_content(demo):
    """Every string field is counted except keys, ids, paths, hashes, enums, titles and labels,
    and the fields tied to a counted one (`check.program`, card terms and definitions)."""
    bundle = load_bundle(demo.bundle)
    counted = {s.field for s in bundle.strings if demo.model.counted(s)}
    assert {"md", "statement_md", "starter", "answer_md", "requirements", "hint", "name",
            "definition_md", "term", "reference_md", "source", "code", "output"} <= counted
    assert not counted & {"key", "id", "file", "hash", "kind", "type", "title", "label",
                          "in_file", "out_file", "content_hash", "program", "functions"}


def test_card_terms_are_tied_to_the_glossary(demo, bundle):
    path = entry_path(bundle, "unit-01-demo")
    data = json.loads(path.read_text())
    card = next(c for c in data["cards"] if c["kind"] == "concept")
    card["term"] = "printing 159"
    path.write_text(dumps(data))
    found = fails(demo.model, bundle)
    assert f"FAIL: {card['key']}: concept card term differs from the glossary" in found, found


def test_entry_outside_the_syllabus_is_a_fail_not_a_crash(demo, bundle):
    """[fable] 7: `_odd_findings` reports an entry the syllabus does not list."""
    data = json.loads((bundle / "book.json").read_text())
    record = next(r for r in data["entries"] if r["id"] == "unit-03-leaks")
    record["id"] = "unit-99-ghost"
    (bundle / "book.json").write_text(dumps(data))
    found = fails(demo.model, bundle)
    assert any(f.startswith("FAIL: demo: unit-99-ghost: entry is not in the syllabus")
               for f in found), found


def test_extra_copy_of_odd_answer_collision_fails(demo, bundle):
    append_to_statement(bundle, "unit-03-leaks", "Exercise 8", "Hint: `1110`.")
    found = fails(demo.model, bundle)
    assert any("demo/unit-03-leaks/exercises/u3e09: hidden answer text" in f for f in found), found


def test_canonical_in_copied_file_fails(demo, bundle):
    append_to_file(bundle, COPIED_FILE, "# 159")
    found = fails(demo.model, bundle)
    assert any("u3e04: hidden answer text" in f for f in found), found


def test_whole_token_only(demo, bundle):
    """`159` never matches inside `1590`; `True` never inside `Trueish`."""
    append_to_statement(bundle, "unit-01-demo", "Exercise 6", "Count to 1590 or say Trueish.")
    assert fails(demo.model, bundle) == []


# --- check 1: hidden code -----------------------------------------------------------------------


def test_even_verify_cell_in_starter_fails(demo, bundle):
    edit_item(bundle, "unit-03-leaks", "Exercise 4",
              lambda item: item.update(starter=demo_book.VERIFY_159))
    found = fails(demo.model, bundle)
    assert any(re.match(r"FAIL: demo: demo/unit-03-leaks/exercises/u3e04: solution code leaked "
                        r"into entries/unit-03-leaks\.json:items/\d+/starter", f) for f in found), found


def test_shipped_asserts_pass_and_are_the_only_ones_removed(demo):
    removed = demo.model.removed_asserts
    assert "assert describe([3, 4]) == '2 scores, best 4'" in removed
    assert not any("159" in statement for statement in removed)


def test_asserts_source_with_def_fails(demo, bundle):
    def edit(item):
        item["check"]["source"] = "def helper():\n    return 1\nassert describe([1]) == helper()"
    edit_item(bundle, "unit-03-leaks", "Exercise 6", edit)
    found = fails(demo.model, bundle)
    assert "FAIL: demo/unit-03-leaks/exercises/u3e06: asserts.source holds non-assert code" in found


def test_hidden_function_body_in_starter_fails(demo, bundle):
    starter = "# my attempt\nprint('start')\n" + demo_book.DESCRIBE + "\nprint(describe([1, 2]))\n"
    edit_item(bundle, "unit-03-leaks", "Exercise 6", lambda item: item.update(starter=starter))
    found = fails(demo.model, bundle)
    assert any("solution code leaked into entries/unit-03-leaks.json:items/5/starter" in f
               for f in found), found


def test_solution_asset_in_json_fails(demo, bundle):
    fence = "```python\n" + demo_book.DESCRIBE_ASSET + "```"
    append_to_statement(bundle, "unit-01-demo", "Exercise 6", fence)
    found = fails(demo.model, bundle)
    assert any("solution code leaked into entries/unit-01-demo.json:items/5/statement_md" in f
               and "solutions_ex6.py" in f for f in found), found


def test_solution_asset_in_copied_file_fails(demo, bundle):
    append_to_file(bundle, COPIED_FILE, demo_book.DESCRIBE_ASSET)
    found = fails(demo.model, bundle)
    assert any(f"solution code leaked into {COPIED_FILE}" in f and "solutions_ex6.py" in f
               for f in found), found


def test_challenge_solution_asset_fails(demo, bundle):
    append_to_statement(bundle, "unit-01-demo", "Exercise 6",
                        "```python\n" + demo_book.SHOUT_ASSET + "```")
    found = fails(demo.model, bundle)
    assert any("solution code leaked" in f and "solutions_challenge1.py" in f for f in found), found


def test_verify_helper_in_copied_file_fails(demo, bundle):
    """`assets/verify/**` is hidden: the whole helper copied into a shipped file fails."""
    append_to_file(bundle, COPIED_FILE, "def check(value):\n    return value == 6\n")
    found = fails(demo.model, bundle)
    assert any("assets/verify/check.py" in f for f in found), found


# --- check 6: hidden prose ----------------------------------------------------------------------


@pytest.mark.parametrize("paragraph", ["EVEN_PROSE", "CHECKPOINT_PROSE", "PROJECT_PROSE"])
def test_explanation_paragraph_in_json_fails(demo, bundle, paragraph):
    append_to_statement(bundle, "unit-01-demo", "Exercise 6", getattr(demo_book, paragraph))
    found = fails(demo.model, bundle)
    assert any("solution prose leaked" in f for f in found), found


@pytest.mark.parametrize("paragraph", ["EVEN_PROSE", "CHECKPOINT_PROSE", "PROJECT_PROSE"])
def test_explanation_paragraph_in_copied_file_fails(demo, bundle, paragraph):
    append_to_file(bundle, COPIED_FILE, "# " + getattr(demo_book, paragraph))
    found = fails(demo.model, bundle)
    assert any("solution prose leaked" in f and COPIED_FILE in f for f in found), found


def test_short_answer_bearing_prose_fails(demo, bundle):
    """`So the answer is 159.` is short but holds its item's canonical: it is hidden prose."""
    assert any(p.text == demo_book.SHORT_PROSE for p in demo.model.hidden_prose)
    edit_item(bundle, "unit-03-leaks", "Exercise 6",
              lambda item: item["before"].append({
                  "key": "demo/unit-03-leaks/exercises/injected", "type": "prose",
                  "md": demo_book.SHORT_PROSE, "needs_prelude": False, "prelude": [],
                  "files": [], "concepts": [], "probe": None, "tags": []}))
    found = fails(demo.model, bundle)
    assert any("solution prose leaked" in f for f in found), found


def test_odd_released_explanation_passes(demo, bundle):
    """An odd exercise's explanation is public (the Student Book prints it): it is not hidden prose,
    so even another copy of it passes."""
    append_to_statement(bundle, "unit-01-demo", "Exercise 6", demo_book.ODD_PROSE)
    assert fails(demo.model, bundle) == []


# --- checks 3-5: odd answers, hashes, visibility ------------------------------------------------


def test_odd_answer_must_equal_appendix(demo, bundle):
    edit_item(bundle, "unit-03-leaks", "Exercise 3",
              lambda item: item.update(answer_md=item["answer_md"] + "\n\nAnd more."))
    assert ("FAIL: demo/unit-03-leaks/exercises/u3e03: answer_md differs from the Student Book "
            "appendix text (student_answer_text)") in fails(demo.model, bundle)


def test_after_attempt_set_is_the_odd_unit_exercises(demo, bundle):
    def reveal(item):
        item.update(answer_visibility="after-attempt", answer_md="**Answer:** `159`")
    edit_item(bundle, "unit-03-leaks", "Exercise 4", reveal)
    edit_item(bundle, "unit-03-leaks", "Exercise 5",
              lambda item: (item.update(answer_visibility="none"), item.pop("answer_md")))
    found = fails(demo.model, bundle)
    assert ("FAIL: demo/unit-03-leaks/exercises/u3e04: after-attempt but not an odd unit exercise"
            in found), found
    assert ("FAIL: demo/unit-03-leaks/exercises/u3e05: odd unit exercise is not after-attempt"
            in found), found


def test_hash_must_match_canonical(demo, bundle):
    def edit(item):
        item["check"]["hash"] = "sha256:" + "0" * 64
    edit_item(bundle, "unit-03-leaks", "Exercise 2", edit)
    assert ("FAIL: demo/unit-03-leaks/exercises/u3e02: check.hash does not match its canonical "
            "answer") in fails(demo.model, bundle)


def test_hash_case_follows_answer_format(demo, bundle):
    def edit(item):
        item["check"]["answer_format"]["case"] = "sensitive"
    edit_item(bundle, "unit-01-demo", "Exercise 2", edit)  # authored insensitive
    assert any("u1e03: check.hash does not match" in f for f in fails(demo.model, bundle))


def test_none_item_with_answer_md_fails(demo, bundle):
    edit_item(bundle, "unit-03-leaks", "Exercise 10",
              lambda item: item.update(answer_md="**Answer:** later"))
    assert ("FAIL: demo/unit-03-leaks/exercises/u3e11: answer_visibility none but answer_md "
            "ships") in fails(demo.model, bundle)


# --- the baseline is exactly what the bundle maps -----------------------------------------------


SOLUTION_LIKE = re.compile(r"(^|/)(solutions[^/]*|teacher-notes[^/]*|(ex|q|p)\d+\.py)$|/verify/")


def test_baseline_provenance(demo):
    """Every allowance comes from material the bundle maps: its entries' lesson and statement
    notebooks, the source of every copied file, the glossary and quick reference, and the odd
    answers it releases. No solution source counts."""
    bundle = load_bundle(demo.bundle)
    book = bundle.documents["book.json"]
    mapped = {"demo/back-matter/glossary.md", "demo/back-matter/quick-reference.md",
              "demo/curriculum/concepts.yaml"}
    items = {item["key"] for document in bundle.documents.values() if isinstance(document, dict)
             for item in document.get("items", [])}
    dirs = {"unit": "units", "checkpoint": "checkpoints", "project": "projects"}
    stems = {"unit": "exercises", "checkpoint": "checkpoint", "project": "brief"}
    released = set()
    for entry in book["entries"]:
        base = f"demo/{dirs[entry['kind']]}/{entry['id']}"
        data = bundle.documents[entry["file"]]
        if data["lesson"]:
            mapped.add(f"{base}/lesson.ipynb")
        if data["items"] or data["intro"] or data["outro"]:
            mapped.add(f"{base}/{stems[entry['kind']]}.ipynb")
        for path in data["files"]:
            relative = path.split("/", 2)[2]
            fixture = re.fullmatch(r"fixtures/([^/]+)/(\d+\.(?:in|out))", relative)
            mapped.add(f"{base}/assets/{fixture[1]}/{fixture[2]}" if fixture else f"{base}/{relative}")
        released |= {item["key"] for item in data["items"]
                     if item["answer_visibility"] == "after-attempt"}
    sources = demo.model.baseline(bundle)
    assert sources
    origins = set()
    for source in sources:
        path, _, part = source.origin.partition("#")
        if part.startswith("answer:"):
            assert part.removeprefix("answer:") in released, source.origin
            assert path.endswith("/solutions.ipynb")
        elif part.startswith("asserts:"):  # the asserts an `asserts` item ships by design
            assert part.removeprefix("asserts:") in items, source.origin
            assert path.endswith("/solutions.ipynb")
        elif part.startswith("check:"):  # the export's own check text from the statement
            assert part.removeprefix("check:") in items, source.origin
            assert path in mapped, source.origin
        else:
            assert path in mapped, source.origin
            assert not SOLUTION_LIKE.search(path), source.origin
        origins.add(path)
    assert {"demo/back-matter/quick-reference.md", "demo/units/unit-01-demo/assets/ex1/2.out",
            "demo/units/unit-01-demo/lesson.ipynb"} <= origins
    assert sum(1 for s in sources if "#answer:" in s.origin) == len(released)
    # [sol] 2 (content review 2): the registry gives field-level allowance, exactly the exported
    # projection's counted field (`name`, one source per concept), never the raw file.
    registry = [s for s in sources if s.origin.startswith("demo/curriculum/concepts.yaml")]
    assert sorted((s.origin, s.text) for s in registry) == sorted(
        (f"demo/curriculum/concepts.yaml#concept:{c['id']}/name", c["name"])
        for c in book["concepts"])


def test_registry_allowance_is_only_the_exported_projection(demo, bundle, tmp_path):
    """[sol] 2 (content review 2): `159` in an unexported registry field (an extra `kind:` value
    and a comment) earns no allowance, so `159` injected into a statement still fails."""
    root = tmp_path / "root"
    shutil.copytree(demo.root, root, symlinks=True)
    registry = root / "demo" / "curriculum" / "concepts.yaml"
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["concepts"][0]["kind"] = "159"
    registry.write_text("# 159 is not exported\n" + yaml.safe_dump(data, sort_keys=False),
                        encoding="utf-8")
    model = AnswerModel(root, "demo")
    assert fails(model, bundle) == []
    append_to_statement(bundle, "unit-03-leaks", "Exercise 4", "159")
    found = fails(model, bundle)
    assert any("u3e04: hidden answer text leaked" in f and "(1 occurrence(s), 0 in exported" in f
               for f in found), found


# --- [sol] 3 (content review 2): every string field is counted or tied ----------------------------


def _schema_string_fields() -> set[str]:
    """Every property name the bundle schema types as a string (or a list of strings)."""
    schema = json.loads((ROOT / "tools/export/schema/bundle.schema.json").read_text())
    defs = schema["$defs"]

    def stringy(node) -> bool:
        if not isinstance(node, dict):
            return False
        if "$ref" in node:
            return stringy(defs[node["$ref"].rsplit("/", 1)[1]])
        types = node.get("type")
        types = types if isinstance(types, list) else [types]
        if "string" in types or "pattern" in node or (
                "enum" in node and any(isinstance(v, str) for v in node["enum"])):
            return True
        if "array" in types:
            return stringy(node.get("items"))
        return any(stringy(sub) for key in ("allOf", "anyOf", "oneOf") for sub in node.get(key, []))

    names: set[str] = set()

    def walk(node) -> None:
        if isinstance(node, dict):
            for name, sub in (node.get("properties") or {}).items():
                if stringy(sub):
                    names.add(name)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
    walk(schema)
    return names


def test_schema_string_fields_are_classified():
    """Each string field the schema declares is counted by check 2 or held by a named tie check."""
    names = _schema_string_fields()
    assert {"md", "statement_md", "color", "title", "key", "route"} <= names
    unclassified = names - COUNTED_FIELDS - set(FIELD_TIES)
    assert unclassified == set(), unclassified
    assert set(FIELD_TIES.values()) <= set(TIES)


def _assert_counted_or_tied(bundle_dir: Path) -> None:
    for string in load_bundle(bundle_dir).strings:
        tie = tie_of(string)
        assert counted(string) == (tie is None), string.where
        assert tie is None or tie in TIES, (string.where, tie)
        assert tie is not None or string.field in COUNTED_FIELDS, string.where


def test_every_demo_string_field_is_counted_or_tied(demo):
    _assert_counted_or_tied(demo.bundle)


@pytest.mark.slow
@pytest.mark.parametrize("book", REAL_BOOKS)
def test_every_real_string_field_is_counted_or_tied(real, book):
    _assert_counted_or_tied(real(book)[1])


def set_pointer(bundle_dir: Path, where: str, value) -> None:
    document, _, pointer = where.partition(":")
    path = bundle_dir / document
    data = json.loads(path.read_text(encoding="utf-8"))
    parts = pointer.split("/")
    node = data
    for part in parts[:-1]:
        node = node[int(part)] if isinstance(node, list) else node[part]
    last = parts[-1]
    node[int(last) if isinstance(node, list) else last] = value
    path.write_text(dumps(data), encoding="utf-8")


def _uncounted_paths(bundle_dir: Path) -> dict[str, str]:
    """One location per uncounted field path (list indexes generalised)."""
    out: dict[str, str] = {}
    for string in load_bundle(bundle_dir).strings:
        if not counted(string):
            out.setdefault(re.sub(r"/\d+", "/#", string.where), string.where)
    return out


def test_hidden_canonical_in_any_uncounted_demo_field_fails(demo, tmp_path):
    """`159` (u3e04's hidden answer) written into any field check 2 does not count fails a tie."""
    paths = _uncounted_paths(demo.bundle)
    assert len(paths) > 40
    missed = []
    for n, (general, where) in enumerate(sorted(paths.items())):
        copy = tmp_path / f"b{n}"
        shutil.copytree(demo.bundle, copy)
        set_pointer(copy, where, "159")
        if not fails(demo.model, copy):
            missed.append(general)
    assert missed == [], missed


def test_pdf_links_are_tied_to_the_release(demo, bundle):
    set_pointer(bundle, "book.json:pdfs", {"student": "https://example.org/159.pdf"})
    found = fails(demo.model, bundle)
    assert any("pdfs" in f for f in found), found


def test_canonical_in_title_is_not_counted_but_tied(demo, bundle):
    """Titles are not check-2 content (plan 101 F), but the title tie holds them to the source."""
    edit_item(bundle, "unit-03-leaks", "Exercise 4", lambda item: item.update(title="159"))
    found = fails(demo.model, bundle)
    assert not any("hidden answer text" in f for f in found), found
    assert any("demo/unit-03-leaks/exercises/u3e04: title" in f for f in found), found


def _first_where(bundle_dir: Path, pattern: str) -> str:
    return next(where for general, where in sorted(_uncounted_paths(bundle_dir).items())
                if re.fullmatch(pattern, general))


@pytest.mark.slow
@pytest.mark.parametrize(("book", "pattern", "message"), [
    ("python-projects", r"entries/.*:lesson/blocks/#/figure/#/color", "turtle figure differs"),
    ("python-projects", r"entries/.*:lesson/blocks/#/tags/#", "tag"),
    ("acsl", r"entries/.*:items/#/division/#", "division"),
    ("acsl", r"book\.json:settings/acsl_divisions/#", "settings"),
])
def test_real_hidden_canonical_in_uncounted_field_fails(real, tmp_path, book, pattern, message):
    """Uncounted fields the demo bundle lacks: a hidden canonical of the book written into a turtle
    segment `color`, a lesson tag, an item division or a settings value fails its tie."""
    model, out = real(book)
    copy = tmp_path / book
    shutil.copytree(out, copy)
    canonical = next(text for _kind, text, _case in model.canonicals.values() if text.strip())
    set_pointer(copy, _first_where(copy, pattern), canonical.strip())
    found = fails(model, copy)
    assert any(message in f for f in found), found


def test_unexported_quick_reference_gives_no_allowance(demo, bundle):
    """With `reference_md` emptied, the quick reference is not exported and earns nothing."""
    data = json.loads((bundle / "book.json").read_text())
    data["reference_md"] = ""
    (bundle / "book.json").write_text(dumps(data))
    assert not any("quick-reference" in s.origin for s in demo.model.baseline(load_bundle(bundle)))


# --- the real books -----------------------------------------------------------------------------


@pytest.fixture(scope="module")
def real(real_site_bundle):
    """`real(book)`: (the book's AnswerModel, its exported bundle), each built once."""
    models: dict[str, AnswerModel] = {}

    def get(book: str) -> tuple[AnswerModel, Path]:
        if book not in models:
            models[book] = AnswerModel(ROOT, book)
        return models[book], real_site_bundle(book)
    return get


@pytest.mark.slow
@pytest.mark.parametrize("book", REAL_BOOKS)
def test_real_books_have_no_answer_model_fail(real, book):
    model, out = real(book)
    findings = model.findings(out)
    assert [f for f in findings if f.startswith("FAIL:")] == [], findings[:20]
    stats = model.stats
    assert stats["hidden_code"] > 0 and stats["canonicals"] >= 0 and stats["hidden_prose"] > 0


def _acsl_copy(real, tmp_path) -> tuple[AnswerModel, Path]:
    model, out = real("acsl")
    copy = tmp_path / "acsl"
    shutil.copytree(out, copy)
    return model, copy


@pytest.mark.slow
def test_real_acsl_injected_quick_reference_answer_fails(real, tmp_path):
    """`A + ~B` (unit-08 Exercise 6, even) also occurs in the exported quick reference; one more
    copy in a statement field fails."""
    model, bundle = _acsl_copy(real, tmp_path)
    reference = json.loads((bundle / "book.json").read_text())["reference_md"]
    assert "A + ~B" in reference
    append_to_statement(bundle, "unit-08-boolean-algebra", "Exercise 2", "Try `A + ~B`.")
    found = fails(model, bundle)
    assert any(f.startswith("FAIL: acsl: acsl/unit-08-boolean-algebra/exercises/e-012: hidden "
                            "answer text leaked") for f in found), found


@pytest.mark.slow
@pytest.mark.parametrize("text", ["So the answer is 5E.", "5E"])
def test_real_acsl_injected_5e_fails(real, tmp_path, text):
    model, bundle = _acsl_copy(real, tmp_path)
    append_to_statement(bundle, "unit-01-computer-number-systems", "Exercise 2", text)
    found = fails(model, bundle)
    assert any(f.startswith("FAIL: acsl: acsl/unit-01-computer-number-systems/exercises/e-046: "
                            "hidden answer text leaked") for f in found), found
    if text != "5E":
        assert any("unit-01-computer-number-systems/solutions.ipynb#" in f
                   and "solution prose leaked" in f for f in found), found


@pytest.mark.slow
def test_real_visible_hidden_code_is_counted_not_dropped(real, tmp_path):
    """[sol] 1: checkpoint-03 Q3's `sum_to_n` solution also appears in a lesson, so the clean
    bundle passes; one more copy in another item's starter raises its count and fails."""
    model, out = real("python-concepts")
    hidden = next(c for c in model.hidden_code if c.origin.endswith(
        "checkpoint-03-functions-and-randomness/solutions.ipynb#cp03sol-q3-code"))
    assert not [f for f in model.findings(out) if f.startswith("FAIL:")]
    copy = tmp_path / "python-concepts"
    shutil.copytree(out, copy)
    body = model._strip_shipped(hidden.text)
    assert "def sum_to_n" in body
    edit_item(copy, "checkpoint-03-functions-and-randomness", "Question 1",
              lambda item: item.update(starter=item["starter"] + "\n\n" + body))
    found = fails(model, copy)
    assert any("solution code leaked into entries/checkpoint-03-functions-and-randomness.json:"
               "items/0/starter" in f and f.endswith(f"(from {hidden.origin})") for f in found), found


SUM_TO_N = "checkpoint-03-functions-and-randomness/solutions.ipynb#cp03sol-q3-code"


def _concepts_sum_to_n(real, tmp_path):
    """(model, a copy of the python-concepts bundle, the hidden `sum_to_n` body, the lesson block
    that shows it): the stream occurs three times in the exported sources and the clean bundle (a
    unit-07 lesson block, and twice in an odd exercise's released answer)."""
    model, out = real("python-concepts")
    hidden = next(c for c in model.hidden_code if c.origin.endswith(SUM_TO_N))
    copy = tmp_path / "python-concepts"
    shutil.copytree(out, copy)
    lesson = json.loads(entry_path(copy, "unit-07-functions").read_text(encoding="utf-8"))
    block = next(b for b in lesson["lesson"]["blocks"] if "def sum_to_n" in b.get("code", ""))
    return model, copy, model._strip_shipped(hidden.text), block["key"]


def edit_block(bundle_dir: Path, entry: str, key: str, edit) -> None:
    path = entry_path(bundle_dir, entry)
    data = json.loads(path.read_text(encoding="utf-8"))
    edit(next(b for b in data["lesson"]["blocks"] if b["key"] == key))
    path.write_text(dumps(data), encoding="utf-8")


@pytest.mark.slow
def test_real_hidden_code_counts_occurrences_in_one_field(real, tmp_path):
    """[sol] 1 (content review 2): occurrences are counted, not containing fields. The lesson's
    copy moved into ONE starter as two copies keeps the containing fields at two (passing a
    field count against 3) but makes four occurrences against the three the sources hold."""
    model, copy, body, key = _concepts_sum_to_n(real, tmp_path)
    edit_block(copy, "unit-07-functions", key, lambda block: block.update(code="print('moved')\n"))
    edit_item(copy, "checkpoint-03-functions-and-randomness", "Question 1",
              lambda item: item.update(starter=item["starter"] + "\n\n" + body + "\n\n" + body))
    found = fails(model, copy)
    assert any("solution code leaked into entries/checkpoint-03-functions-and-randomness.json:"
               "items/0/starter" in f and "(4 occurrence(s), 3 in exported sources)" in f
               for f in found), found


@pytest.mark.slow
def test_real_hidden_code_extra_copy_in_the_same_field_fails(real, tmp_path):
    """[sol] 1: a second copy appended to the lesson block that already holds the visible one."""
    model, copy, body, key = _concepts_sum_to_n(real, tmp_path)
    edit_block(copy, "unit-07-functions", key,
               lambda block: block.update(code=block["code"] + "\n\n" + body))
    found = fails(model, copy)
    assert any("solution code leaked into entries/unit-07-functions.json:lesson/blocks/" in f
               and "(4 occurrence(s), 3 in exported sources)" in f for f in found), found


@pytest.mark.slow
def test_real_hidden_code_extra_copy_in_one_copied_file_fails(real, tmp_path):
    """[sol] 1: the lesson's copy moved into one copied file, plus an extra copy in that file."""
    model, copy, body, key = _concepts_sum_to_n(real, tmp_path)
    edit_block(copy, "unit-07-functions", key, lambda block: block.update(code="print('moved')\n"))
    target = next(path for path, text in load_bundle(copy).files.items()
                  if text is not None and path.endswith(".py"))
    append_to_file(copy, target, body + "\n\n" + body)
    found = fails(model, copy)
    assert any(f"solution code leaked into {target}" in f
               and "(4 occurrence(s), 3 in exported sources)" in f for f in found), found


@pytest.mark.slow
def test_real_acsl_verify_cell_in_starter_fails(real, tmp_path):
    model, bundle = _acsl_copy(real, tmp_path)
    hidden = next(c for c in model.hidden_code if c.origin.startswith(
        "acsl/units/unit-08-boolean-algebra/solutions.ipynb") and '"1110"' in c.text)
    edit_item(bundle, "unit-08-boolean-algebra", "Exercise 4",
              lambda item: item.update(starter=hidden.text))
    found = fails(model, bundle)
    assert any("solution code leaked into entries/unit-08-boolean-algebra.json:" in f
               and f.endswith(f"(from {hidden.origin})") for f in found), found
