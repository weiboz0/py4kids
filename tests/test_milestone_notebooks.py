"""Group-free tests for milestone-notebook discovery, execution, hygiene, and seed policy.

Milestone notebooks (``<book>/projects/*/milestones/*.ipynb``) are a first-class gated artifact
but NOT a ``project-*`` curriculum-map entry. These tests build throwaway notebooks in a temp tree
and must NOT require the recsys dependency group (they import only tools + nbformat).
"""

from __future__ import annotations

import nbformat

from tools.notebooks import (
    exec_milestones_findings,
    milestone_hygiene_findings,
    milestone_notebooks,
)

BOOK = "demo-book"


def _milestones_dir(root, book=BOOK):
    path = root / book / "projects" / "bookrec" / "milestones"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write(path, cells):
    nbformat.write(nbformat.v4.new_notebook(cells=cells), str(path))


def test_absent_dirs_are_clean(tmp_path):
    # No projects/ at all -> empty, no error.
    assert milestone_notebooks(tmp_path, BOOK) == []
    assert milestone_hygiene_findings(tmp_path, BOOK) == []
    assert exec_milestones_findings(tmp_path, BOOK) == []
    # projects/ exists but no milestones/ dir -> still clean.
    (tmp_path / BOOK / "projects" / "bookrec").mkdir(parents=True)
    (tmp_path / BOOK / "projects" / ".gitkeep").write_text("", encoding="utf-8")
    assert milestone_notebooks(tmp_path, BOOK) == []
    assert milestone_hygiene_findings(tmp_path, BOOK) == []


def test_discovery_and_dotfile_filter(tmp_path):
    milestones = _milestones_dir(tmp_path)
    _write(milestones / "m1.ipynb", [nbformat.v4.new_code_cell("value = 1")])
    _write(milestones / "m2.ipynb", [nbformat.v4.new_code_cell("value = 2")])
    # A hidden/checkpoint notebook must never be swept.
    _write(milestones / ".ipynb_checkpoints-m1.ipynb", [nbformat.v4.new_code_cell("x = 1")])
    found = milestone_notebooks(tmp_path, BOOK)
    names = [path.name for path in found]
    assert names == ["m1.ipynb", "m2.ipynb"]  # sorted, dotfile excluded
    # Non-notebook siblings are not matched by the glob.
    (milestones / "pyproject.toml").write_text("", encoding="utf-8")
    assert [p.name for p in milestone_notebooks(tmp_path, BOOK)] == ["m1.ipynb", "m2.ipynb"]


def test_clean_milestone_execs_and_passes_hygiene(tmp_path):
    milestones = _milestones_dir(tmp_path)
    _write(
        milestones / "m1.ipynb",
        [
            nbformat.v4.new_markdown_cell("# Milestone demo"),
            nbformat.v4.new_code_cell("import random\nrandom.seed(4)\nvalue = random.randint(0, 9)"),
        ],
    )
    assert milestone_hygiene_findings(tmp_path, BOOK) == []
    assert exec_milestones_findings(tmp_path, BOOK) == []


def test_stored_outputs_fail(tmp_path):
    milestones = _milestones_dir(tmp_path)
    cell = nbformat.v4.new_code_cell("value = 1")
    cell.outputs = [nbformat.v4.new_output("stream", name="stdout", text="1\n")]
    _write(milestones / "m1.ipynb", [cell])
    findings = milestone_hygiene_findings(tmp_path, BOOK)
    assert any("has outputs" in finding for finding in findings)


def test_nonnull_execution_count_fails(tmp_path):
    milestones = _milestones_dir(tmp_path)
    cell = nbformat.v4.new_code_cell("value = 1")
    cell.execution_count = 1
    _write(milestones / "m1.ipynb", [cell])
    findings = milestone_hygiene_findings(tmp_path, BOOK)
    assert any("is executed" in finding for finding in findings)


def test_unseeded_from_random_import_fails(tmp_path):
    milestones = _milestones_dir(tmp_path)
    _write(
        milestones / "m1.ipynb",
        [nbformat.v4.new_code_cell("from random import randint\nvalue = randint(0, 9)")],
    )
    findings = milestone_hygiene_findings(tmp_path, BOOK)
    assert any("from random import" in finding for finding in findings)


def test_unseeded_random_use_fails(tmp_path):
    milestones = _milestones_dir(tmp_path)
    _write(
        milestones / "m1.ipynb",
        [nbformat.v4.new_code_cell("import random\nvalue = random.random()")],
    )
    findings = milestone_hygiene_findings(tmp_path, BOOK)
    assert any("without random.seed(4)" in finding for finding in findings)


def test_seed_after_use_fails(tmp_path):
    milestones = _milestones_dir(tmp_path)
    _write(
        milestones / "m1.ipynb",
        [nbformat.v4.new_code_cell("import random\nvalue = random.random()\nrandom.seed(4)")],
    )
    findings = milestone_hygiene_findings(tmp_path, BOOK)
    assert any("must precede first use" in finding for finding in findings)


def test_unseeded_numpy_default_rng_fails(tmp_path):
    milestones = _milestones_dir(tmp_path)
    _write(
        milestones / "m1.ipynb",
        [nbformat.v4.new_code_cell("import numpy as np\nrng = np.random.default_rng()\nx = rng.random()")],
    )
    findings = milestone_hygiene_findings(tmp_path, BOOK)
    assert any("numpy default_rng() without a seed" in finding for finding in findings)


def test_seeded_numpy_default_rng_passes(tmp_path):
    milestones = _milestones_dir(tmp_path)
    _write(
        milestones / "m1.ipynb",
        [
            nbformat.v4.new_markdown_cell("# Milestone demo"),
            nbformat.v4.new_code_cell("import numpy as np\nrng = np.random.default_rng(0)\nx = rng.random()"),
        ],
    )
    assert milestone_hygiene_findings(tmp_path, BOOK) == []


def test_unseeded_numpy_legacy_global_fails(tmp_path):
    milestones = _milestones_dir(tmp_path)
    _write(
        milestones / "m1.ipynb",
        [nbformat.v4.new_code_cell("import numpy as np\nx = np.random.random()")],
    )
    findings = milestone_hygiene_findings(tmp_path, BOOK)
    assert any("numpy random without np.random.seed" in finding for finding in findings)


def test_seeded_numpy_legacy_global_passes(tmp_path):
    milestones = _milestones_dir(tmp_path)
    _write(
        milestones / "m1.ipynb",
        [
            nbformat.v4.new_markdown_cell("# Milestone demo"),
            nbformat.v4.new_code_cell("import numpy as np\nnp.random.seed(0)\nx = np.random.random()"),
        ],
    )
    assert milestone_hygiene_findings(tmp_path, BOOK) == []


def test_numpy_seed_after_use_fails(tmp_path):
    milestones = _milestones_dir(tmp_path)
    _write(
        milestones / "m1.ipynb",
        [nbformat.v4.new_code_cell("import numpy as np\nx = np.random.random()\nnp.random.seed(0)")],
    )
    findings = milestone_hygiene_findings(tmp_path, BOOK)
    assert any("np.random.seed(...) must precede first use" in finding for finding in findings)


def test_non_random_numpy_is_not_flagged(tmp_path):
    milestones = _milestones_dir(tmp_path)
    _write(
        milestones / "m1.ipynb",
        [
            nbformat.v4.new_markdown_cell("# Milestone demo"),
            nbformat.v4.new_code_cell("import numpy as np\norder = np.argsort(np.array([3, 1, 2]))"),
        ],
    )
    assert milestone_hygiene_findings(tmp_path, BOOK) == []
