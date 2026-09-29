"""Plan 091 guard: the old book ids and "Book N" names never come back in live files.

Design 008 renamed `book1` / `book1b` / `book2` to `python-projects` / `python-concepts` /
`usaco-bronze`, and student- and teacher-facing text names a book by its title.
Historical records (docs/plans, docs/designs, docs/reviews, docs/architecture, ERRATA.md) keep the
old ids and are never scanned.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
THIS_FILE = Path(__file__).resolve()

# (name, pattern) — every rule the E3 grep uses.
PATTERNS = (
    ("path segment", re.compile(r"(^|[^-\w])book(1b?|2)/", re.MULTILINE)),
    ("CLI value", re.compile(r"--book book(1b?|2)\b")),
    ("quoted id", re.compile(r"""['"]book(1b?|2)['"]""")),
    ("qualified id", re.compile(r"book(1b?|2):[a-z]")),
    ("old output name", re.compile(r"Book1b-|Book[12]-", re.IGNORECASE)),
    ("book name", re.compile(r"\bBook (1b|1|2)\b")),
)
# A link to a historical design or plan keeps its file name (`docs/designs/005-book1b-…md`).
HISTORICAL_FILE_NAME = re.compile(r"(?:designs|plans)/\d{3}-[\w.-]+")
# The one-release pre-merge-guard transition map (plan 091 B3) names the old roots on purpose.
TRANSITION_MARKER = "plan-091-transition"
TRANSITION_FILE = "scripts/pre-merge-guard.sh"
HISTORICAL_PREFIXES = ("docs/plans/", "docs/designs/", "docs/reviews/", "docs/architecture/")
LIVE_DIRS = ("tools/", "tests/", "scripts/")
LIVE_FILES = ("books.yaml", ".gitignore", "output/README.md", "README.md", "TODO.md")


def _book_roots() -> tuple[str, ...]:
    registry = yaml.safe_load((REPO / "books.yaml").read_text(encoding="utf-8"))
    return tuple(book["root"] + "/" for book in registry["books"])


def _repo_files() -> list[str]:
    listed = subprocess.run(
        ["git", "ls-files", "-co", "--exclude-standard"],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    return [path for path in listed if (REPO / path).is_file()]


def live_files() -> list[str]:
    roots = _book_roots()
    selected = []
    for path in _repo_files():
        if path.startswith(HISTORICAL_PREFIXES) or path.rsplit("/", 1)[-1] == "ERRATA.md":
            continue
        if (REPO / path).resolve() == THIS_FILE:
            continue  # this test's own patterns
        if path.startswith(LIVE_DIRS + roots) or path in LIVE_FILES:
            selected.append(path)
    return selected


def _text(path: str) -> str | None:
    try:
        return (REPO / path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None  # binary asset


def _project_structure_section() -> str:
    text = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    start = text.index("## Project Structure")
    end = text.index("\n## ", start + 1)
    return text[start:end]


def findings_for(label: str, text: str) -> list[str]:
    found = []
    for number, line in enumerate(text.splitlines(), 1):
        if label == TRANSITION_FILE and TRANSITION_MARKER in line and line.startswith("TRANSITION = {"):
            continue  # the one-release old→new map must name the old roots
        scanned = HISTORICAL_FILE_NAME.sub("", line)
        for name, pattern in PATTERNS:
            if pattern.search(scanned):
                found.append(f"{label}:{number}: {name}: {line.strip()[:160]}")
    return found


def test_no_old_book_ids_or_names_in_live_files():
    findings = []
    for path in live_files():
        text = _text(path)
        if text is not None:
            findings.extend(findings_for(path, text))
    findings.extend(findings_for("AGENTS.md §Project Structure", _project_structure_section()))
    assert findings == [], "\n".join(findings)


def test_live_file_set_covers_every_scope():
    files = set(live_files())
    for required in ("books.yaml", ".gitignore", "output/README.md", "TODO.md",
                     "scripts/ci-local.sh", "tools/publish.py", "tests/test_books.py"):
        assert required in files
    for root in _book_roots():
        assert any(path.startswith(root) for path in files), root
    assert not any(path.startswith(HISTORICAL_PREFIXES) for path in files)
    assert not any(path.endswith("/ERRATA.md") or path == "ERRATA.md" for path in files)
    assert "tests/test_book_ids.py" not in files


def test_patterns_flag_old_forms_and_spare_historical_links():
    flagged = (
        "cd book1b/units/unit-06",
        "uv run py4kids-tools --book book2 judge-check",
        "book_id == 'book1b'",
        '- book2:str-split',
        "output/book1b/BOOK1B-Student.pdf",
        "Book2-Teacher.pdf",
        "the Book 1 syllabus",
        "How Book 1b differs",
    )
    for sample in flagged:
        assert findings_for("sample", sample), sample
    spared = (
        "Full design: `../docs/designs/005-book1b-concept-first.md`.",
        "see `docs/plans/017-book2-infrastructure.md` AD-001",
        "python-concepts/units/unit-06-turtle-geometry/",
        "usaco-bronze:str-split",
    )
    for sample in spared:
        assert not findings_for("sample", sample), sample


def test_design_000_section_1_points_to_design_008():
    text = (REPO / "docs/designs/000-project-design.md").read_text(encoding="utf-8")
    start = text.index("## 1. Repo structure")
    end = text.index("\n## 2.", start)
    assert "008-book-series-naming.md" in text[start:end]


def test_transition_exemption_is_limited_to_the_guard_map():
    marked = 'book = "book1"  # plan-091-transition'
    assert findings_for("tools/example.py", marked), "marker must not exempt other files"
    assert findings_for(TRANSITION_FILE, marked), "marker must not exempt other lines of the guard"
    guard_line = next(line for line in (REPO / TRANSITION_FILE).read_text(encoding="utf-8").splitlines()
                      if TRANSITION_MARKER in line)
    assert findings_for(TRANSITION_FILE, guard_line) == []
