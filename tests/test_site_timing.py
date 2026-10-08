"""Plan 104 Phase C: `check.cpu_ms` from the committed timing cache, and odd answers' turtle
`answer_figures`, both tied by the answer model."""

import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tools.books import book_path
from tools.cli import main
from tools.export import SCHEMA_VERSION, answers
from tools.export.answer_model import AnswerModel
from tools.export.bundle import dumps, export_book
from tools.export.check import site_check_findings
from tools.export.timing import CACHE_DIR, MAX_MS, MIN_MS, TimingCache, cache_path, round_ms
from tools.publish import entries
from tools.turtle_figure import turtle_segments

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "site_demo_book", Path(__file__).parent / "fixtures" / "site" / "demo_book.py")
demo_book = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(demo_book)

EX1 = "demo/unit-01-demo/exercises/u1e01"
EX5 = "demo/unit-01-demo/exercises/u1e09"
TURTLE_ASSET = ("import turtle\n\nfor side in range(3):\n    turtle.forward(40)\n"
                "    turtle.left(120)\n")


def tree(directory: Path) -> dict[str, bytes]:
    return {path.relative_to(directory).as_posix(): path.read_bytes()
            for path in sorted(directory.rglob("*")) if path.is_file()}


def entry_doc(bundle: Path, entry: str) -> dict:
    return json.loads((bundle / "entries" / f"{entry}.json").read_text(encoding="utf-8"))


def item_of(bundle: Path, key: str) -> dict:
    entry = key.split("/")[1]
    return next(item for item in entry_doc(bundle, entry)["items"] if item["key"] == key)


def edit_item(bundle: Path, key: str, edit) -> None:
    entry = key.split("/")[1]
    path = bundle / "entries" / f"{entry}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    edit(next(item for item in data["items"] if item["key"] == key))
    path.write_text(dumps(data), encoding="utf-8")


def fails(model: AnswerModel, bundle: Path) -> list[str]:
    return [f for f in model.findings(bundle) if f.startswith("FAIL:")]


@pytest.fixture
def site_root(tmp_path):
    answers.clear_caches()
    return demo_book.build_site_root(tmp_path / "root")


# --- rounding ----------------------------------------------------------------------------------


@pytest.mark.parametrize(("measured", "expected"), [
    (0, MIN_MS), (1, 100), (23.4, 100), (100, 100), (100.1, 200), (950, 1000), (1001, 1100),
    (9_999, 10_000), (250_000, MAX_MS),
])
def test_round_ms_rounds_up_and_clamps(measured, expected):
    assert round_ms(measured) == expected


# --- the cache ---------------------------------------------------------------------------------


def test_export_reads_cpu_ms_from_the_committed_cache(site_root, tmp_path):
    demo_book.write_timings(site_root, cpu_ms=300)
    export_book(site_root, "demo", tmp_path / "out")
    check = item_of(tmp_path / "out", EX1)["check"]
    assert check["kind"] == "fixtures" and check["cpu_ms"] == 300
    assert all("cpu_ms" not in item["check"] for item in entry_doc(tmp_path / "out",
                                                                     "unit-01-demo")["items"]
               if item["check"]["kind"] != "fixtures")


def test_missing_cache_entry_fails_export(site_root, tmp_path):
    cache_path(site_root, "demo").unlink()
    with pytest.raises(ValueError) as error:
        export_book(site_root, "demo", tmp_path / "out")
    message = str(error.value)
    assert message.startswith(f"FAIL: {EX1}: no timing in {CACHE_DIR}/demo.json")
    assert "export --measure" in message
    assert not (tmp_path / "out" / "book.json").exists()
    findings = site_check_findings(site_root, "demo")
    assert any(f.startswith(f"FAIL: {EX1}: no timing") for f in findings), findings


def test_missing_key_fails_even_with_a_cache(site_root, tmp_path):
    path = cache_path(site_root, "demo")
    data = json.loads(path.read_text())
    data["items"] = {"demo/unit-01-demo/exercises/other": data["items"][EX1]}
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match=f"FAIL: {EX1}: no timing"):
        export_book(site_root, "demo", tmp_path / "out")


def test_stale_cache_entry_fails_export(site_root, tmp_path):
    solver = site_root / "demo" / "units" / "unit-01-demo" / "assets" / "ex1.py"
    solver.write_text("print(2 * int(input()))\n")
    demo_book.git_add(site_root)
    answers.clear_caches()
    with pytest.raises(ValueError, match=f"FAIL: {EX1}: stale timing"):
        export_book(site_root, "demo", tmp_path / "out")


def test_measure_refreshes_the_cache(site_root, tmp_path):
    path = cache_path(site_root, "demo")
    path.unlink()
    export_book(site_root, "demo", tmp_path / "measured", measure=True)
    data = json.loads(path.read_text())
    assert data["version"] == 1 and data["book"] == "demo"
    assert list(data["items"]) == [EX1]
    entry = data["items"][EX1]
    assert entry["cpu_ms"] == round_ms(entry["measured_ms"]) == 100  # a one-line solver
    assert entry["cases"] == 2 and entry["fingerprint"].startswith("sha256:")
    assert item_of(tmp_path / "measured", EX1)["check"]["cpu_ms"] == entry["cpu_ms"]
    # The refreshed cache now serves a plain export, byte-identically.
    export_book(site_root, "demo", tmp_path / "plain")
    assert tree(tmp_path / "measured") == tree(tmp_path / "plain")


def test_measure_drops_entries_the_export_no_longer_uses(site_root, tmp_path):
    path = cache_path(site_root, "demo")
    data = json.loads(path.read_text())
    data["items"]["demo/unit-09-gone/exercises/x"] = data["items"][EX1]
    path.write_text(json.dumps(data))
    export_book(site_root, "demo", tmp_path / "out", measure=True)
    assert list(json.loads(path.read_text())["items"]) == [EX1]


def test_measure_refuses_a_solver_that_fails_its_fixtures(site_root, tmp_path):
    fixture = site_root / "demo" / "units" / "unit-01-demo" / "assets" / "ex1" / "2.out"
    fixture.write_text("21\n")
    demo_book.git_add(site_root)
    answers.clear_caches()
    before = cache_path(site_root, "demo").read_bytes()
    with pytest.raises(ValueError, match="solver fails its fixture 2.in"):
        export_book(site_root, "demo", tmp_path / "out", measure=True)
    assert cache_path(site_root, "demo").read_bytes() == before  # never half-written


def test_plain_export_never_writes_the_cache(site_root, tmp_path):
    before = cache_path(site_root, "demo").read_bytes()
    export_book(site_root, "demo", tmp_path / "out")
    assert cache_path(site_root, "demo").read_bytes() == before


def test_bad_cache_version_fails(site_root, tmp_path):
    cache_path(site_root, "demo").write_text(json.dumps({"version": 0, "items": {}}))
    with pytest.raises(ValueError, match="not a version 1 timing cache"):
        export_book(site_root, "demo", tmp_path / "out")


def test_cli_export_measure(site_root, tmp_path, capsys):
    cache_path(site_root, "demo").unlink()
    assert main(["--root", str(site_root), "--book", "demo", "export", "--out",
                 str(tmp_path / "one")]) == 1
    assert "no timing" in capsys.readouterr().out
    assert main(["--root", str(site_root), "--book", "demo", "export", "--measure", "--out",
                 str(tmp_path / "two")]) == 0
    assert "timings measured" in capsys.readouterr().out
    assert EX1 in json.loads(cache_path(site_root, "demo").read_text())["items"]


def test_export_is_deterministic_whatever_the_raw_measurement(site_root, tmp_path):
    """Two exports are byte-identical; the bundle holds only the rounded `cpu_ms`, so a re-measure
    whose raw time moves within the same 100 ms step changes nothing."""
    export_book(site_root, "demo", tmp_path / "one")
    path = cache_path(site_root, "demo")
    data = json.loads(path.read_text())
    data["items"][EX1]["measured_ms"] = 87
    path.write_text(json.dumps(data))
    export_book(site_root, "demo", tmp_path / "two")
    assert tree(tmp_path / "one") == tree(tmp_path / "two")


def test_timing_cache_api(site_root):
    cache = TimingCache(site_root, "demo")
    assert cache.entry(EX1)["cpu_ms"] == 100
    assert cache.entry("nope") is None


# --- answer figures and the answer-model ties ---------------------------------------------------


class Demo:
    def __init__(self, root: Path, bundle: Path):
        self.root, self.bundle = root, bundle
        self.model = AnswerModel(root, "demo")


@pytest.fixture(scope="module")
def turtle_demo(tmp_path_factory):
    """The answer-model demo plus a turtle solution asset for odd unit-01 Exercise 5."""
    answers.clear_caches()
    base = tmp_path_factory.mktemp("timing")
    root = demo_book.build_answer_model_root(base / "root")
    demo_book.write(root / "demo" / "units" / "unit-01-demo" / "assets" / "solutions_ex5.py",
                    TURTLE_ASSET)
    demo_book.git_add(root)
    answers.clear_caches()
    export_book(root, "demo", base / "bundle")
    return Demo(root, base / "bundle")


@pytest.fixture
def bundle(turtle_demo, tmp_path):
    copy = tmp_path / "bundle"
    shutil.copytree(turtle_demo.bundle, copy)
    return copy


def test_answer_figures_only_on_the_odd_turtle_answer(turtle_demo):
    with_figures = {}
    for record in json.loads((turtle_demo.bundle / "book.json").read_text())["entries"]:
        for item in entry_doc(turtle_demo.bundle, record["id"])["items"]:
            if "answer_figures" in item:
                with_figures[item["key"]] = item
    assert list(with_figures) == [EX5]
    item = with_figures[EX5]
    assert item["answer_visibility"] == "after-attempt"
    assert item["answer_figures"] == [{"caption": "Drawing made by the program above",
                                       "segments": turtle_segments(TURTLE_ASSET)}]
    assert len(item["answer_figures"][0]["segments"]) == 3
    assert item["answer_md"].count(r"\begin{tikzpicture}") == 1
    # The even turtle item (unit-02 Exercise 4) gets none: its answer is never released.
    assert "answer_figures" not in item_of(turtle_demo.bundle,
                                           "demo/unit-02-more/exercises/u2e07")


def test_turtle_demo_passes_the_answer_model(turtle_demo):
    assert fails(turtle_demo.model, turtle_demo.bundle) == []


@pytest.mark.parametrize("edit", [
    lambda item: item["answer_figures"][0]["segments"][0].update(x2=41.0),
    lambda item: item["answer_figures"][0]["segments"][0].update(color="red"),
    lambda item: item["answer_figures"][0].update(caption="Drawing for 159"),
    lambda item: item["answer_figures"].append(item["answer_figures"][0]),
    lambda item: item.pop("answer_figures"),
], ids=["segment", "color", "caption", "extra", "removed"])
def test_tampered_answer_figures_fail(turtle_demo, bundle, edit):
    edit_item(bundle, EX5, edit)
    found = fails(turtle_demo.model, bundle)
    assert any(f"FAIL: {EX5}: answer_figures differ" in f for f in found), found


def test_answer_figures_on_an_item_without_a_turtle_answer_fail(turtle_demo, bundle):
    key = "demo/unit-01-demo/exercises/u1e05"  # odd Exercise 3, no turtle
    figure = item_of(bundle, EX5)["answer_figures"]
    edit_item(bundle, key, lambda item: item.update(answer_figures=figure))
    found = fails(turtle_demo.model, bundle)
    assert any(f"FAIL: {key}: answer_figures differ" in f for f in found), found


def test_answer_figures_on_a_hidden_answer_fail_the_schema(turtle_demo, bundle):
    key = "demo/unit-02-more/exercises/u2e07"
    figure = item_of(bundle, EX5)["answer_figures"]
    edit_item(bundle, key, lambda item: item.update(answer_figures=figure))
    found = fails(turtle_demo.model, bundle)
    assert any("schema" in f for f in found), found
    assert any(f"FAIL: {key}: answer_figures differ" in f for f in found), found


@pytest.mark.parametrize("value", [200, 1000])
def test_tampered_cpu_ms_fails(turtle_demo, bundle, value):
    edit_item(bundle, EX1, lambda item: item["check"].update(cpu_ms=value))
    found = fails(turtle_demo.model, bundle)
    assert found == [f"FAIL: {EX1}: check.cpu_ms is not its entry in {CACHE_DIR}/demo.json"]


@pytest.mark.parametrize("value", [150, 0, 20_000])
def test_out_of_range_cpu_ms_fails_the_schema(turtle_demo, bundle, value):
    edit_item(bundle, EX1, lambda item: item["check"].update(cpu_ms=value))
    found = fails(turtle_demo.model, bundle)
    assert any("schema" in f and "cpu_ms" in f for f in found), found


def test_missing_cpu_ms_fails(turtle_demo, bundle):
    edit_item(bundle, EX1, lambda item: item["check"].pop("cpu_ms"))
    found = fails(turtle_demo.model, bundle)
    assert any("schema" in f for f in found), found
    assert any("check.cpu_ms is not its entry" in f for f in found), found


def test_stale_cache_fails_the_timing_tie(turtle_demo, tmp_path):
    root = tmp_path / "root"
    shutil.copytree(turtle_demo.root, root)
    path = cache_path(root, "demo")
    data = json.loads(path.read_text())
    data["items"][EX1]["fingerprint"] = "sha256:" + "0" * 64
    path.write_text(json.dumps(data))
    found = fails(AnswerModel(root, "demo"), turtle_demo.bundle)
    assert found == [f"FAIL: {EX1}: stale timing in {CACHE_DIR}/demo.json"]


def test_schema_version_is_1_1_0():
    assert SCHEMA_VERSION == "1.1.0"


# --- the real books -----------------------------------------------------------------------------


def _git_tracked(path: Path) -> bool:
    result = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch",
                             str(path.relative_to(ROOT))], capture_output=True, check=False)
    return result.returncode == 0


@pytest.mark.slow
@pytest.mark.parametrize("book", ["usaco-bronze", "acsl"])
def test_real_timing_cache_matches_the_fixtures_items(real_site_bundle, book):
    """The committed cache holds exactly the book's fixtures items, each with a sane cpu_ms."""
    path = cache_path(ROOT, book)
    assert _git_tracked(path), path
    cache = json.loads(path.read_text())["items"]
    bundle = real_site_bundle(book)
    fixtures = {}
    for entry_id, _dir in entries(book_path(ROOT, book), "student"):
        for item in entry_doc(bundle, entry_id)["items"]:
            if item["check"]["kind"] == "fixtures":
                fixtures[item["key"]] = item["check"]["cpu_ms"]
    assert fixtures and set(fixtures) == set(cache)
    assert all(fixtures[key] == cache[key]["cpu_ms"] for key in fixtures)
    assert all(MIN_MS <= value <= MAX_MS and value % 100 == 0 for value in fixtures.values())


@pytest.mark.slow
@pytest.mark.parametrize("book", ["python-projects", "python-concepts"])
def test_real_books_without_fixtures_need_no_cache(real_site_bundle, book):
    bundle = real_site_bundle(book)
    for entry_id, _dir in entries(book_path(ROOT, book), "student"):
        assert all(item["check"]["kind"] != "fixtures"
                   for item in entry_doc(bundle, entry_id)["items"])
    assert not cache_path(ROOT, book).exists()
