"""Plan 102 Phase E: the four site books' confirmed check content.

Every site book is `classification: confirmed`; every item carries exactly one heading `check-*`
tag; single-token `expected-output` canonicals are the statement body's fixed answer (rule 4);
multi-token `answer` items carry an authored hint (rule 3); every phase log has one line per item;
and no checked solution relies on a file the statement does not ask the student to write.

Each assertion is a small `*_findings` helper run over the real books, plus a negative test that
feeds the helper a deliberately broken copy, so a helper that finds nothing cannot pass silently.
"""

from __future__ import annotations

import copy
import functools
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from tools.books import books_with_flag, site_config
from tools.export import answers
from tools.export.classify import _check_tags, _site_entries, confirmed_kind
from tools.export.items import Item, entry_content
from tools.export.normalise import normalise

ROOT = Path(__file__).resolve().parents[1]
BOOKS = ("python-projects", "python-concepts", "usaco-bronze", "acsl")
LOGS = ROOT / "docs" / "plans" / "102-logs"
CHECKED = ("asserts", "expected-output")
RETAGGED = (
    "python-projects/unit-09-save-point/exercises/e5a7e9a1",
    "python-projects/unit-09-save-point/exercises/25c296a7",
    "python-projects/unit-09-save-point/exercises/exercise-14-linear-search",
    "python-projects/unit-09-save-point/exercises/exercise-15-find-extreme",
    "python-projects/unit-09-save-point/exercises/exercise-16-filter-into-list",
    "python-projects/checkpoint-04-year-one-finale/checkpoint/c4000008",
)


@functools.cache
def book_items(book: str) -> tuple[Item, ...]:
    items: list[Item] = []
    for entry_dir, kind in _site_entries(ROOT, book, None):
        items.extend(entry_content(ROOT, book, entry_dir, kind).items)
    return tuple(items)


def _broken(item: Item, **metadata) -> Item:
    """A copy of `item` whose heading cell (deep-copied) has `metadata` overrides."""
    clone = copy.copy(item)
    clone.heading_cell = copy.deepcopy(item.heading_cell)
    for name, value in metadata.items():
        if value is None:
            clone.heading_cell.metadata.pop(name, None)
        else:
            clone.heading_cell.metadata[name] = value
    return clone


def _first(book: str, kind: str, test=lambda item: True) -> Item:
    return next(item for item in book_items(book) if confirmed_kind(item) == kind and test(item))


# --- 1. one check-* tag per item; every site.yaml confirmed --------------------------------------


def tag_count_findings(items) -> list[str]:
    return [f"{item.key}: {len(_check_tags(item.heading_cell))} check-* heading tags "
            f"{_check_tags(item.heading_cell)}"
            for item in items if len(_check_tags(item.heading_cell)) != 1
            or confirmed_kind(item) is None]


def classification_findings(root: Path, books) -> list[str]:
    return [f"{book}: classification {site_config(root, book).classification}"
            for book in books if site_config(root, book).classification != "confirmed"]


def test_site_books_are_the_four():
    assert sorted(books_with_flag(ROOT, "site")) == sorted(BOOKS)


@pytest.mark.parametrize("book", BOOKS)
def test_every_item_has_exactly_one_check_tag(book):
    assert book_items(book)
    assert tag_count_findings(book_items(book)) == []


def test_every_site_book_is_confirmed():
    assert classification_findings(ROOT, BOOKS) == []


def test_tag_count_catches_missing_and_double_tags():
    item = book_items("python-projects")[0]
    untagged = _broken(item, tags=[t for t in item.heading_cell.metadata.get("tags", [])
                                   if not t.startswith("check-")])
    double = _broken(item, tags=[*item.heading_cell.metadata.get("tags", []), "check-self",
                                 "check-asserts"])
    assert len(tag_count_findings([untagged, double])) == 2


def test_classification_catches_proposed(tmp_path):
    shutil.copy(ROOT / "books.yaml", tmp_path / "books.yaml")
    (tmp_path / "acsl").mkdir()
    text = (ROOT / "acsl" / "site.yaml").read_text(encoding="utf-8")
    (tmp_path / "acsl" / "site.yaml").write_text(
        text.replace("classification: confirmed", "classification: proposed"), encoding="utf-8")
    assert classification_findings(tmp_path, ["acsl"]) == ["acsl: classification proposed"]


# --- 2. single-token expected-output canonicals occur in the statement body (rule 4) -------------


def statement_body(item: Item) -> str:
    """The item's statement Markdown without its heading line (`## Exercise 3`)."""
    return item.statement_source.partition("\n")[2]


def single_token_findings(item: Item, canonical: str) -> list[str]:
    output = normalise(canonical, case="sensitive")
    if len(output.split()) != 1:
        return []
    pattern = rf"(?<![\w.]){re.escape(output)}(?!\w)"
    if re.search(pattern, statement_body(item)):
        return []
    return [f"{item.key}: single-token output {output!r} is not in the statement body"]


@pytest.mark.parametrize("book", BOOKS)
def test_single_token_expected_output_is_in_statement_body(book):
    findings = []
    for item in book_items(book):
        if confirmed_kind(item) == "expected-output":
            canonical = answers.canonical_text(item, "expected-output")
            findings.extend(single_token_findings(item, canonical))
    assert findings == []


def test_single_token_ignores_the_heading_line():
    """`c8e092dc`'s trap: a token found only in `## Exercise 3` is no fixed answer."""
    item = copy.copy(_first("python-projects", "expected-output"))
    item.statement_source = "## Exercise 3\n\nPrint how many pets are awake."
    assert single_token_findings(item, "3\n") != []
    item.statement_source = "## Exercise 3\n\nThere are 3 pets; print how many are awake."
    assert single_token_findings(item, "3\n") == []
    assert single_token_findings(item, "two tokens\n") == []


# --- 3. multi-token answer items carry an authored hint (rule 3) ---------------------------------


def answer_format_findings(item: Item) -> list[str]:
    canonical = normalise(answers.answer_line(item), case="sensitive")
    if len(canonical.split()) <= 1:
        return []
    fmt = item.heading_cell.metadata.get("answer_format")
    if isinstance(fmt, dict) and isinstance(fmt.get("hint"), str) and fmt["hint"].strip():
        return []
    return [f"{item.key}: multi-token answer {canonical!r} has no authored answer_format hint"]


@pytest.mark.parametrize("book", BOOKS)
def test_multi_token_answers_have_authored_hint(book):
    findings = [finding for item in book_items(book) if confirmed_kind(item) == "answer"
                for finding in answer_format_findings(item)]
    assert findings == []


def test_answer_format_catches_missing_and_empty_hint():
    def multi(item):
        return len(normalise(answers.answer_line(item), case="sensitive").split()) > 1

    item = _first("acsl", "answer", multi)
    assert answer_format_findings(item) == []
    assert answer_format_findings(_broken(item, answer_format=None)) != []
    empty = {**item.heading_cell.metadata["answer_format"], "hint": "  "}
    assert answer_format_findings(_broken(item, answer_format=empty)) != []


# --- 4. every phase log has one line per item -----------------------------------------------------


LOG_LINE = re.compile(r"^- `([^`]+)` — ", re.MULTILINE)


def log_findings(book: str, text: str, keys) -> list[str]:
    logged: dict[str, int] = {}
    for raw in LOG_LINE.findall(text):
        key = raw if raw.startswith(f"{book}/") else f"{book}/{raw}"
        logged[key] = logged.get(key, 0) + 1
    findings = [f"{book} log: no line for {key}" for key in keys if key not in logged]
    findings += [f"{book} log: {count} lines for {key}" for key, count in logged.items()
                 if count > 1]
    findings += [f"{book} log: line for unknown item {key}" for key in logged if key not in keys]
    return findings


@pytest.mark.parametrize("book", BOOKS)
def test_phase_log_has_one_line_per_item(book):
    text = (LOGS / f"{book}.md").read_text(encoding="utf-8")
    keys = [item.key for item in book_items(book)]
    assert len(set(keys)) == len(keys)
    assert log_findings(book, text, keys) == []


def test_phase_log_catches_missing_duplicate_and_unknown_lines():
    book = "usaco-bronze"
    text = (LOGS / f"{book}.md").read_text(encoding="utf-8")
    keys = [item.key for item in book_items(book)]
    line = next(line for line in text.splitlines() if line.startswith(f"- `{keys[0]}` — "))
    assert log_findings(book, text.replace(line + "\n", ""), keys) == [
        f"{book} log: no line for {keys[0]}"]
    assert log_findings(book, text + line + "\n", keys) == [f"{book} log: 2 lines for {keys[0]}"]
    stray = f"- `{book}/unit-99/exercises/nope` — fixtures — x\n"
    assert log_findings(book, text + stray, keys) == [
        f"{book} log: line for unknown item {book}/unit-99/exercises/nope"]


# --- 5. no hidden file setup behind a checked solution --------------------------------------------


SETUP_COMMENT = re.compile(r"(?im)^[ \t]*#.*\bsetup\b.*$")
WRITE_OPEN = re.compile(r"""\bopen\([^)]*,\s*(?:mode\s*=\s*)?['"][wa]""")


def hidden_setup(code: str) -> bool:
    """A comment line mentioning `setup` followed (anywhere later) by `open(..., "w"/"a")`."""
    return any(WRITE_OPEN.search(code, match.end()) for match in SETUP_COMMENT.finditer(code))


def checked_items():
    return [item for book in BOOKS for item in book_items(book)
            if confirmed_kind(item) in CHECKED]


def test_checked_solutions_have_no_hidden_file_setup():
    flagged = [item.key for item in checked_items() if hidden_setup(answers._solution_code(item))]
    assert flagged == []


def test_hidden_setup_detector():
    assert hidden_setup("# Self-contained setup: write the file\n"
                        "with open('savegame.txt', 'w') as f:\n    f.write('x')\n")
    assert hidden_setup("# setup\nf = open('log.txt', mode='a')\n")
    assert not hidden_setup("with open('savegame.txt', 'w') as f:\n    f.write('x')\n")
    assert not hidden_setup("# setup\nwith open('savegame.txt') as f:\n    print(f.read())\n")
    # the six retagged unit-09 drills really do hide a setup block (that is why they are self-check)
    unit09 = {item.key: item for item in book_items("python-projects")}
    assert all(hidden_setup(answers._solution_code(unit09[key])) for key in RETAGGED[:5])


def missing_file_findings(runs) -> list[str]:
    """`runs`: (key, RunResult) pairs; a FileNotFoundError in any run is a finding."""
    return [f"{key}: {result.stderr.strip().splitlines()[-1]}" for key, result in runs
            if result.status != "ok" and "FileNotFoundError" in result.stderr]


@pytest.mark.slow
def test_checked_solutions_run_with_tracked_files_only():
    """Every asserts / expected-output solution runs in the runner-like sandbox (tracked files
    only); none may need a file that only an earlier exercise or a scratch run wrote."""
    items = checked_items()
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(
            lambda item: answers.run_python(item.entry_dir, answers._solution_code(item)), items))
    assert missing_file_findings(zip((item.key for item in items), results)) == []


def test_missing_file_finding_from_a_real_sandbox_run(tmp_path):
    entry = tmp_path / "unit-00-scratch"
    entry.mkdir()
    (entry / "finale.txt").write_text("untracked scratch\n", encoding="utf-8")  # not git-tracked
    result = answers._run_once(entry, "print(open('finale.txt').read())\n", 20)
    assert result.status == "error"
    [finding] = missing_file_findings([("demo/key", result)])
    assert finding.startswith("demo/key: FileNotFoundError")
    ok = answers._run_once(entry, "print('fine')\n", 20)
    assert missing_file_findings([("demo/ok", ok)]) == []


# --- the six integration retags -------------------------------------------------------------------


def kind_findings(items, keys, kind: str) -> list[str]:
    by_key = {item.key: item for item in items}
    return [f"{key}: {confirmed_kind(by_key[key]) if key in by_key else 'missing'}"
            for key in keys if key not in by_key or confirmed_kind(by_key[key]) != kind]


def test_six_file_reading_items_are_self_check():
    assert kind_findings(book_items("python-projects"), RETAGGED, "self-check") == []


def test_kind_findings_catch_a_reverted_retag():
    items = list(book_items("python-projects"))
    index = next(i for i, item in enumerate(items) if item.key == RETAGGED[-1])
    tags = [t for t in items[index].heading_cell.metadata["tags"] if not t.startswith("check-")]
    items[index] = _broken(items[index], tags=[*tags, "check-asserts"])
    assert kind_findings(items, RETAGGED, "self-check") == [f"{RETAGGED[-1]}: asserts"]
