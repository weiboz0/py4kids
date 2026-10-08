"""The bundle writer and site-check (design 012 D3, D5, D7; plan 101 E)."""

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import nbformat
import pytest
from jsonschema import Draft202012Validator

from tools.books import books_with_flag
from tools.export import answers
from tools.export import bundle as bundle_module
from tools.export.bundle import ExportError, export_book
from tools.export.check import site_check_findings
from tools.export.classify import apply_proposals

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "tools/export/schema/bundle.schema.json").read_text(encoding="utf-8"))
_spec = importlib.util.spec_from_file_location(
    "site_demo_book", Path(__file__).parent / "fixtures" / "site" / "demo_book.py")
demo_book = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(demo_book)

ENTRIES = ["unit-01-demo", "unit-02-more", "checkpoint-01-demo", "project-01-demo", "project-02-demo"]
SOLUTION_NAME = re.compile(r"^(ex|q|p)\d+\.py$")


def tree(directory: Path) -> dict[str, bytes]:
    """Every file under `directory` as {relative posix path: bytes}."""
    return {path.relative_to(directory).as_posix(): path.read_bytes()
            for path in sorted(directory.rglob("*")) if path.is_file()}


def validate(data: dict, definition: str) -> list[str]:
    validator = Draft202012Validator(SCHEMA).evolve(schema=SCHEMA["$defs"][definition])
    return [error.message for error in validator.iter_errors(data)]


@pytest.fixture
def site_root(tmp_path):
    answers.clear_caches()
    return demo_book.build_site_root(tmp_path / "root")


def test_export_layout_fixture_book(site_root, tmp_path):
    out = tmp_path / "bundle"
    result = export_book(site_root, "demo", out)
    files = tree(out)
    assert {"book.json", *(f"entries/{e}.json" for e in ENTRIES)} <= set(files)
    assert all(path in ("book.json",) or path.startswith(("entries/", "files/")) for path in files)
    for path, data in files.items():
        if path.endswith(".json"):
            text = data.decode("utf-8")
            assert text.endswith("}\n")
            assert str(site_root) not in text and str(tmp_path) not in text
            loaded = json.loads(text)
            assert validate(loaded, "book_file" if path == "book.json" else "entry_file") == [], path
            assert text == json.dumps(loaded, sort_keys=True, ensure_ascii=False, indent=1) + "\n"
    book = json.loads(files["book.json"])
    assert [entry["id"] for entry in book["entries"]] == ENTRIES
    assert book["entries"][0] == {"id": "unit-01-demo", "kind": "unit", "title": "Unit 1 — Demo",
                                  "number": 1, "file": "entries/unit-01-demo.json"}
    assert book["book"] == {"id": "demo", "title": "Demo Book", "subtitle": "",
                            "flags": {"acsl": False, "judge": True}}
    assert book["release"] == {"tag": "unreleased", "content_hash": result.content_hash}
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", result.content_hash)
    assert book["pdfs"] is None
    assert [g["term"] for g in book["glossary"]] == ["print", "variable", "for loop", "range"]
    assert book["reference_md"].startswith("# Quick Reference")
    assert {c["id"] for c in book["concepts"]} >= {"print", "for-loop"}

    unit = json.loads(files["entries/unit-01-demo.json"])
    assert unit["entry"] == {"id": "unit-01-demo", "kind": "unit", "title": "Unit 1 — Demo"}
    blocks = unit["lesson"]["blocks"]
    assert blocks[0]["type"] == "opener" and blocks[1]["type"] == "goals"
    program = [b for b in blocks if b["type"] == "program"]
    assert program and program[0]["files"] == ["files/unit-01-demo/assets/count_helper.py"]
    cards = unit["cards"]
    assert {c["kind"] for c in cards} == {"predict", "concept"}
    concept_keys = [c["key"] for c in cards if c["kind"] == "concept"]
    assert concept_keys == ["demo/back-matter/glossary/print", "demo/back-matter/glossary/variable"]
    unit2 = json.loads(files["entries/unit-02-more.json"])
    assert [c["concept"] for c in unit2["cards"] if c["kind"] == "concept"] == [
        "for-loop", "range-function"]
    # Every listed file is copied; the copied files are exactly the listed ones.
    listed = set(unit["files"])
    assert {"files/unit-01-demo/assets/count_helper.py",
            "files/unit-01-demo/fixtures/ex1/1.in", "files/unit-01-demo/fixtures/ex1/2.out"} <= listed
    assert {p for p in files if p.startswith("files/unit-01-demo/")} == listed
    fixtures = next(i for i in unit["items"] if i["check"]["kind"] == "fixtures")
    assert fixtures["check"]["cases"][0]["in_file"] == "files/unit-01-demo/fixtures/ex1/1.in"
    assert files["files/unit-01-demo/fixtures/ex1/1.in"] == b"3\n"
    checkpoint = json.loads(files["entries/checkpoint-01-demo.json"])
    assert checkpoint["lesson"] is None and checkpoint["cards"] == []

    # The report goes to build/site-report, never into the bundle.
    report = json.loads((site_root / "build" / "site-report" / "demo.json").read_text())
    assert report == result.report
    assert report["probes"]["demo/unit-01-demo/lesson/l1c2"]["status"] == "prelude"
    assert report["distractor_fallbacks"] == {"demo/back-matter/glossary/for-loop": 1,
                                              "demo/back-matter/glossary/print": 0,
                                              "demo/back-matter/glossary/range-function": 1,
                                              "demo/back-matter/glossary/variable": 0}
    assert "demo/unit-01-demo/exercises/u1e11" in report["self_check"]
    # [fable] 5: unattributed items are reported per check kind; short answers (no code) are exempt.
    unattributed = report["unattributed"]["items"]
    assert isinstance(unattributed, dict) and "answer" not in unattributed
    assert all(isinstance(keys, list) and keys for keys in unattributed.values())
    assert report["unattributed"]["short_answer_exempt"] == 2  # u1e03 and c1c01
    assert "concepts: unattributed" not in report["notes"].get(
        "demo/unit-01-demo/exercises/u1e03", [])
    assert report["classification"]["total"] == sum(len(json.loads(files[f"entries/{e}.json"])["items"])
                                                     for e in ENTRIES)
    assert not any("report" in path for path in files)

    # Keys: blocks, side blocks, items and cards, each once.
    assert len(result.keys) == len(set(result.keys))
    assert "demo/unit-01-demo/exercises/u1e01" in result.keys
    assert "demo/unit-01-demo/lesson/l1c2#predict" in result.keys
    assert "demo/back-matter/glossary/print" in result.keys
    # The repo tree is unchanged: the probe ran in a temp copy.
    assert not (site_root / "demo" / "units" / "unit-01-demo" / "scratch.txt").exists()


def test_export_replaces_stale_files(site_root, tmp_path):
    out = tmp_path / "bundle"
    (out / "files" / "unit-09-gone").mkdir(parents=True)
    (out / "files" / "unit-09-gone" / "old.py").write_text("x")
    (out / "entries").mkdir()
    (out / "entries" / "unit-09-gone.json").write_text("{}")
    export_book(site_root, "demo", out)
    assert not (out / "files" / "unit-09-gone").exists()
    assert not (out / "entries" / "unit-09-gone.json").exists()


EXPORT = ("import sys\nfrom pathlib import Path\nfrom tools.export.bundle import export_book\n"
          "print(export_book(Path(sys.argv[1]), 'demo', Path(sys.argv[2])).content_hash)\n")


def run_export(root: Path, out: Path, seed: str) -> str:
    env = {**os.environ, "PYTHONHASHSEED": seed}
    result = subprocess.run([sys.executable, "-c", EXPORT, str(root), str(out)], cwd=ROOT, env=env,
                            capture_output=True, text=True, check=True)
    return result.stdout.strip().splitlines()[-1]


def test_export_deterministic_across_hashseed(site_root, tmp_path):
    """Review Focus 4: another PYTHONHASHSEED, new mtimes (as after a `git checkout`) and an
    untracked scratch file named by a lesson cell give a byte-identical bundle and hash."""
    first = run_export(site_root, tmp_path / "one", "1")
    entry = site_root / "demo" / "units" / "unit-01-demo"
    (entry / "scratch.txt").write_text("left over by a notebook run\n")
    (entry / "assets" / "untracked_helper.py").write_text("print('scratch')\n")
    for path in (site_root / "demo").rglob("*"):
        if path.is_file():
            os.utime(path, (1_000_000_000, 1_000_000_000))
    second = run_export(site_root, tmp_path / "two", "2")
    assert first == second
    assert tree(tmp_path / "one") == tree(tmp_path / "two")
    assert not any("scratch" in path or "untracked" in path for path in tree(tmp_path / "two"))


def test_no_solution_source_copied(site_root, tmp_path):
    out = tmp_path / "bundle"
    export_book(site_root, "demo", out)
    unit = site_root / "demo" / "units" / "unit-01-demo"
    assert (unit / "assets" / "ex1.py").is_file() and (unit / "assets" / "verify" / "check.py").is_file()
    copied = [path for path in tree(out) if path.startswith("files/")]
    assert copied
    for path in copied:
        name = path.rsplit("/", 1)[-1]
        assert not SOLUTION_NAME.match(name), path
        assert "/verify/" not in path and not name.startswith("solutions"), path
    text = "\n".join(data.decode("utf-8") for data in tree(out).values())
    assert "return value == 6" not in text  # the verify helper's body


@pytest.mark.parametrize("smuggled", ["files/unit-01-demo/assets/ex1.py",
                                      "files/unit-01-demo/assets/verify/check.py",
                                      "files/unit-01-demo/solutions.ipynb"])
def test_solution_source_listing_fails(site_root, tmp_path, monkeypatch, smuggled):
    """A solution source named in any item's `files` stops the export (the writer asserts it)."""
    real = bundle_module.export_item

    def leaky(root, book, item, *rest):
        exported = real(root, book, item, *rest)
        if item.key.endswith("/u1e01"):
            exported.data["files"] = [*exported.data["files"], smuggled]
        return exported

    monkeypatch.setattr(bundle_module, "export_item", leaky)
    with pytest.raises(ValueError, match="never ships"):
        export_book(site_root, "demo", tmp_path / "bundle")
    assert not (tmp_path / "bundle" / smuggled).exists()


def test_untracked_listed_file_fails(site_root, tmp_path, monkeypatch):
    (site_root / "demo" / "units" / "unit-01-demo" / "assets" / "loose.py").write_text("x = 1\n")
    real = bundle_module.export_item

    def loose(root, book, item, *rest):
        exported = real(root, book, item, *rest)
        if item.key.endswith("/u1e01"):
            exported.data["files"] = [*exported.data["files"], "files/unit-01-demo/assets/loose.py"]
        return exported

    monkeypatch.setattr(bundle_module, "export_item", loose)
    with pytest.raises(ValueError, match="not a tracked student file"):
        export_book(site_root, "demo", tmp_path / "bundle")


def test_pdf_links(site_root, tmp_path):
    result = export_book(site_root, "demo", tmp_path / "rel", release="pdfs-2026-09-30")
    book = json.loads((tmp_path / "rel" / "book.json").read_text())
    base = "https://github.com/weiboz0/py4kids/releases/download/pdfs-2026-09-30/"
    assert book["pdfs"] == {edition: f"{base}demo-{edition}.pdf"
                            for edition in ("student-print", "student", "answer-key", "teacher")}
    assert book["release"] == {"tag": "pdfs-2026-09-30", "content_hash": result.content_hash}
    assert validate(book, "book_file") == []


def test_content_hash_ignores_release_object(site_root, tmp_path, monkeypatch):
    """The hash covers every bundle file but `book.json`'s `release` object (the tag lives there);
    the PDF links are content, so a release tag changes the hash only through `pdfs`."""
    monkeypatch.setattr(bundle_module, "pdf_links", lambda book, release: None)
    one = export_book(site_root, "demo", tmp_path / "a", release="unreleased")
    two = export_book(site_root, "demo", tmp_path / "b", release="v1")
    assert one.content_hash == two.content_hash
    a, b = tree(tmp_path / "a"), tree(tmp_path / "b")
    assert a.keys() == b.keys() and all(a[p] == b[p] for p in a if p != "book.json")


def test_duplicate_key_across_kinds_fails(site_root, tmp_path, monkeypatch):
    """Items join the key union: an item keyed like a lesson block is a duplicate id."""
    real = bundle_module.export_item

    def clash(root, book, item, *rest):
        exported = real(root, book, item, *rest)
        if item.key.endswith("/u1e01"):
            exported.data["key"] = "demo/unit-01-demo/lesson/l1c3"
        return exported

    monkeypatch.setattr(bundle_module, "export_item", clash)
    with pytest.raises(ExportError) as error:
        export_book(site_root, "demo", tmp_path / "bundle")
    assert error.value.findings == ["FAIL: duplicate id: demo/unit-01-demo/lesson/l1c3 (2 times)"]
    assert not (tmp_path / "bundle" / "book.json").exists()


def test_missing_id_fails(site_root, tmp_path):
    path = site_root / "demo" / "units" / "unit-02-more" / "lesson.ipynb"
    data = json.loads(path.read_text())
    del data["cells"][1]["id"]
    data["nbformat_minor"] = 4
    path.write_text(json.dumps(data))
    findings = site_check_findings(site_root, "demo")
    assert findings == [f"FAIL: {path}: cell 1 has no id"]


def test_schema_error_fails(site_root, tmp_path, monkeypatch):
    real = bundle_module.export_item

    def bad(root, book, item, *rest):
        exported = real(root, book, item, *rest)
        if item.key.endswith("/u1e01"):
            exported.data["surprise"] = 1
        return exported

    monkeypatch.setattr(bundle_module, "export_item", bad)
    findings = site_check_findings(site_root, "demo")
    assert len(findings) == 1
    assert findings[0].startswith("FAIL: entries/unit-01-demo.json: schema: ")
    assert "surprise" in findings[0]


def test_site_check_fixture_book_passes(site_root):
    findings = site_check_findings(site_root, "demo")
    assert not [f for f in findings if f.startswith("FAIL:")], findings
    info = [f for f in findings if f.startswith("INFO:")]
    assert len(info) == 1
    assert re.match(r"INFO: demo: classification proposed: 0/\d+ items confirmed by check-\* tags",
                    info[0])
    assert all(f.startswith(("INFO:", "WARN:")) for f in findings)


def test_site_check_order_and_continuity(site_root):
    """A vanished ledger key fails; it comes before the classification line."""
    ids = site_root / "site" / "ids"
    ids.mkdir(parents=True)
    (ids / "demo.json").write_text(json.dumps(["demo/unit-01-demo/lesson/gone"]) + "\n")
    findings = site_check_findings(site_root, "demo")
    assert findings[0].startswith("FAIL: demo: id vanished since the ledger: "
                                  "demo/unit-01-demo/lesson/gone")
    (ids / "demo-retired.yaml").write_text("demo/unit-01-demo/lesson/gone: retired\n")
    assert not [f for f in site_check_findings(site_root, "demo") if f.startswith("FAIL:")]


def test_classification_confirmed_requires_tags(site_root):
    (site_root / "demo" / "site.yaml").write_text("classification: confirmed\nfixture_budget_kb: 130\n")
    findings = site_check_findings(site_root, "demo")
    untagged = [f for f in findings if "no check-* tag" in f]
    assert "FAIL: demo/unit-01-demo/exercises/u1e01: no check-* tag (site.yaml classification: confirmed)" \
        in untagged
    info = [f for f in findings if f.startswith("INFO:")]
    total = int(re.search(r"0/(\d+)", info[0])[1])
    assert len(untagged) == total
    assert findings.index(untagged[-1]) < findings.index(info[0])
    answers.clear_caches()
    apply_proposals(site_root, "demo")
    answers.clear_caches()
    findings = site_check_findings(site_root, "demo")
    assert not [f for f in findings if f.startswith("FAIL:")], findings
    assert any(re.match(rf"INFO: demo: classification confirmed: {total}/{total} ", f) for f in findings)


def test_site_check_probe_error_fails(tmp_path):
    answers.clear_caches()
    boom = demo_book.code("boom", "print(1 / 0)", outputs=[
        nbformat.v4.new_output("stream", name="stdout", text="never\n")])
    root = demo_book.build_site_root(tmp_path / "root", extra_lesson_cells=[boom])
    findings = site_check_findings(root, "demo")
    fails = [f for f in findings if f.startswith("FAIL:")]
    assert fails == ["FAIL: demo/unit-01-demo/lesson/boom: lesson probe error: "
                     + fails[0].split("lesson probe error: ", 1)[1]]
    assert "ZeroDivisionError" in fails[0]
    # The bundle carries `probe: null` for it, never the error.
    entry = json.loads((root / "build" / "site-check" / "demo" / "entries" / "unit-01-demo.json")
                       .read_text())
    block = next(b for b in entry["lesson"]["blocks"] if b["key"].endswith("/boom"))
    assert block["probe"] is None


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   check=True, capture_output=True)


def test_site_check_cache(site_root, monkeypatch):
    """Committed, clean paths reuse build/site-check/<book>/findings.json; a dirty tree recomputes."""
    (site_root / ".gitignore").write_text("build/\n")
    (site_root / "tools").mkdir(exist_ok=True)  # the demo timing cache is under tools/
    (site_root / "tools" / "x.py").write_text("")
    git(site_root, "add", "-A")
    git(site_root, "commit", "-q", "-m", "fixture")
    first = site_check_findings(site_root, "demo")
    cache = site_root / "build" / "site-check" / "demo" / "findings.json"
    assert json.loads(cache.read_text())["findings"] == first

    def boom(*_args, **_kwargs):
        raise AssertionError("export ran despite a valid cache")

    monkeypatch.setattr("tools.export.check.export_book", boom)
    assert site_check_findings(site_root, "demo") == first
    (site_root / "demo" / "syllabus.md").write_text(
        (site_root / "demo" / "syllabus.md").read_text() + "\n")
    with pytest.raises(AssertionError, match="despite a valid cache"):
        site_check_findings(site_root, "demo")


def test_report_lists_single_token_outputs():
    """[fable] 3 (content review 2): the report's `single_token_outputs` list collects the items
    whose `expected-output` canonical is one numeric token, for a content plan to confirm."""
    report = {"derived_formats": [], "unmatched_samples": [], "single_token_outputs": [],
              "notes": {}}
    bundle_module._note_lists(report, "b/u/exercises/a", [f"{answers.SINGLE_TOKEN_NOTE} (18)"])
    bundle_module._note_lists(report, "b/u/exercises/b", ["answer_format: derived (token)"])
    assert report["single_token_outputs"] == ["b/u/exercises/a"]
    assert report["derived_formats"] == ["b/u/exercises/b"]


def test_non_site_book_is_refused(tmp_path):
    root = demo_book.build_demo_root(tmp_path / "root")
    (root / "books.yaml").write_text((root / "books.yaml").read_text().replace("  site: true\n", ""))
    with pytest.raises(ValueError, match="demo is not a site book"):
        export_book(root, "demo", tmp_path / "out")


@pytest.mark.slow
@pytest.mark.parametrize("book", ["python-projects", "python-concepts", "usaco-bronze", "acsl"])
def test_site_check_real_books(book):
    assert book in books_with_flag(ROOT, "site")
    findings = site_check_findings(ROOT, book)
    assert not [f for f in findings if f.startswith("FAIL:")], findings
