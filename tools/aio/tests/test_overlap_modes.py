"""py4kids aio-001 Phase D: `overlap-scan --require-corpus` and the `--paths` archive mode."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from tools.aio.checks.overlap import (
    SHINGLE_SIZE,
    SHINGLE_THRESHOLD,
    check_overlap,
    check_overlap_paths,
)

needs_pdftotext = pytest.mark.skipif(
    shutil.which("pdftotext") is None, reason="pdftotext (poppler-utils) is not installed"
)

# Long enough for SHINGLE_THRESHOLD shingles of SHINGLE_SIZE words.
COPIED = (
    "a contestant trains a gradient boosted ensemble on the provided tabular features and "
    "reports the held out macro averaged score after tuning the learning rate schedule"
)
ORIGINAL = "students plot the loss curve of their own toy model and describe what they see"


def _book(root: Path, *, text: str = COPIED, pdf: bytes | None = None) -> Path:
    paper = root / "reference" / "r1-2026"
    paper.mkdir(parents=True)
    (paper / "index.yaml").write_text(
        "problems:\n"
        f"  - id: q1\n    text: {json.dumps(text)}\n    summary: {json.dumps('a summary')}\n",
        encoding="utf-8",
    )
    if pdf is not None:
        (paper / "paper.pdf").write_bytes(pdf)
    return root


def _notebook(path: Path, *, markdown: str = "", code: str = "") -> Path:
    cells = [
        {"cell_type": "markdown", "metadata": {}, "source": markdown},
        {"cell_type": "code", "metadata": {}, "source": code, "outputs": [], "execution_count": None},
    ]
    notebook = {"cells": cells, "metadata": {}, "nbformat": 4, "nbformat_minor": 5}
    path.write_text(json.dumps(notebook), encoding="utf-8")
    return path


def test_copied_text_is_long_enough_to_trip_the_detector():
    assert len(COPIED.split()) >= SHINGLE_SIZE + SHINGLE_THRESHOLD - 1


# --- --require-corpus ------------------------------------------------------------------------


def test_missing_corpus_skips_without_flag_and_fails_with_it(tmp_path):
    assert check_overlap(tmp_path).skipped
    report = check_overlap(tmp_path, require_corpus=True)
    assert not report.ok
    assert report.skipped is None
    assert "--require-corpus" in report.errors[0]
    assert "scripts/aio/fetch-reference.sh" in report.errors[0]


@needs_pdftotext
def test_corpus_extraction_failure_fails_with_flag(tmp_path):
    book = _book(tmp_path, pdf=b"%PDF-1.4 truncated garbage")
    lenient = check_overlap(book)
    assert lenient.ok
    assert any("NOT scanned" in warning for warning in lenient.warnings)

    report = check_overlap(book, require_corpus=True)
    assert not report.ok
    assert any("NOT scanned" in error for error in report.errors)
    assert "PDF parts expected 1, extracted 0" in report.notes[0]
    assert "extraction failures 1" in report.notes[0]


@needs_pdftotext
def test_complete_corpus_passes_with_flag_and_reports_parts(tmp_path):
    report = check_overlap(_book(tmp_path), require_corpus=True)
    assert report.ok, report.errors
    assert "PDF parts expected 0, extracted 0; index text parts 1; extraction failures 0" in (
        report.notes[0]
    )


# --- --paths archive mode --------------------------------------------------------------------


@needs_pdftotext
def test_archive_with_planted_corpus_text_fails(tmp_path):
    book = _book(tmp_path / "book")
    archive = tmp_path / "archive"
    (archive / "plans").mkdir(parents=True)
    (archive / "plans" / "001-clean.md").write_text(ORIGINAL, encoding="utf-8")
    (archive / "plans" / "002-audit.md").write_text(
        f"An audit quoted the paper: {COPIED}.", encoding="utf-8"
    )

    report = check_overlap_paths(archive, [book])

    assert not report.ok
    assert len(report.errors) == 1
    assert "002-audit.md overlaps" in report.errors[0]
    assert any("files 2, scanned 2" in note for note in report.notes)


@needs_pdftotext
def test_archive_scans_notebook_markdown_and_code(tmp_path):
    book = _book(tmp_path / "book")
    archive = tmp_path / "archive"
    archive.mkdir()
    _notebook(archive / "clean.ipynb", markdown=ORIGINAL, code="x = 1")
    _notebook(archive / "copied.ipynb", code=f"# {COPIED}")

    report = check_overlap_paths(archive, [book])

    assert [error.split(" overlaps ")[0] for error in report.errors] == [
        str(archive / "copied.ipynb")
    ]


@needs_pdftotext
def test_archive_inline_import_spans_are_boilerplate_but_copied_prose_is_not(tmp_path):
    # The starter imports a reference paper shares with all Python ML material: usaaio's
    # boilerplate rule drops lines that begin with import/from; archive prose quotes them as
    # inline code spans instead (usaaio docs/plans/006-units-tranche-2.md:166).
    book = _book(
        tmp_path / "book", text=f"import numpy as np import matplotlib.pyplot as plt {COPIED}"
    )
    archive = tmp_path / "archive"
    archive.mkdir()
    prose = (
        "the only hits are the universal `import numpy as np` / "
        "`import matplotlib.pyplot as plt` starter boilerplate"
    )
    (archive / "inline-imports.md").write_text(prose, encoding="utf-8")
    (archive / "copied.md").write_text(f"{prose}. {COPIED}.", encoding="utf-8")
    # The same words outside a code span are still prose and still a hit.
    (archive / "plain.md").write_text(
        "the only hits are import numpy as np import matplotlib pyplot as plt here",
        encoding="utf-8",
    )

    report = check_overlap_paths(archive, [book])

    assert sorted(error.split(" overlaps ")[0] for error in report.errors) == [
        str(archive / "copied.md"),
        str(archive / "plain.md"),
    ]


@needs_pdftotext
def test_archive_clean_text_passes(tmp_path):
    book = _book(tmp_path / "book")
    archive = tmp_path / "archive"
    archive.mkdir()
    for name in ("a.md", "b.yaml", "c.py", "d.sh", "e.txt", ".gitkeep"):
        (archive / name).write_text(ORIGINAL, encoding="utf-8")

    report = check_overlap_paths(archive, [book])

    assert report.ok, report.errors
    assert any("files 6, scanned 6" in note for note in report.notes)


@needs_pdftotext
def test_archive_fails_closed_on_unknown_extension_and_parse_errors(tmp_path):
    book = _book(tmp_path / "book")
    archive = tmp_path / "archive"
    archive.mkdir()
    (archive / "figure.png").write_bytes(b"\x89PNG\r\n")
    (archive / "broken.ipynb").write_text("{not json", encoding="utf-8")
    (archive / "latin1.md").write_bytes(b"caf\xe9")

    report = check_overlap_paths(archive, [book])

    assert not report.ok
    joined = "\n".join(report.errors)
    assert "figure.png: unscannable extension '.png'" in joined
    assert "broken.ipynb: cannot read or parse" in joined
    assert "latin1.md: cannot read or parse" in joined


def test_archive_fails_without_corpus(tmp_path):
    archive = tmp_path / "archive"
    archive.mkdir()
    (archive / "a.md").write_text(ORIGINAL, encoding="utf-8")

    report = check_overlap_paths(archive, [tmp_path / "book-without-reference"])

    assert not report.ok
    assert "--require-corpus" in report.errors[0]


@needs_pdftotext
def test_archive_fails_on_corpus_extraction_failure(tmp_path):
    book = _book(tmp_path / "book", pdf=b"%PDF-1.4 truncated garbage")
    archive = tmp_path / "archive"
    archive.mkdir()
    (archive / "a.md").write_text(ORIGINAL, encoding="utf-8")

    report = check_overlap_paths(archive, [book])

    assert not report.ok
    assert any("NOT scanned" in error for error in report.errors)


def test_archive_requires_a_directory(tmp_path):
    report = check_overlap_paths(tmp_path / "missing", [])
    assert not report.ok
    assert "not a directory" in report.errors[0]
