"""aio-model guard rules (design 014; plan aio-001 Phase D): id collisions and tracked-path refusals."""

import subprocess
from pathlib import Path

from tools import guard


def collisions(*refs, roots=("aio-a",)):
    return guard.aio_collision_failures({name: set(paths) for name, paths in refs}, roots)


def test_distinct_aio_unit_and_mocktest_ids_pass():
    assert collisions(
        (
            "WORKTREE",
            {
                "aio-a/units/01-F1-python/manifest.yaml",
                "aio-a/units/02-C1-models/manifest.yaml",
                "aio-a/units/B2-019-attention/manifest.yaml",
                "aio-a/units/B2-020-language/manifest.yaml",
                "aio-a/mocktests/r1-001/manifest.yaml",
                "aio-a/mocktests/r1-002/manifest.yaml",
                "aio-a/mocktests/blueprint.yaml",
            },
        ),
    ) == []


def test_duplicate_teaching_order_prefix_across_refs_fails():
    assert collisions(
        ("WORKTREE", {"aio-a/units/10-C5-embeddings/manifest.yaml"}),
        ("origin/main", {"aio-a/units/10-C13-other/manifest.yaml"}),
    ) == ["duplicate aio-a/units order number(s): 10"]


def test_duplicate_unit_code_fails():
    assert collisions(
        ("WORKTREE", {"aio-a/units/10-C5-embeddings/manifest.yaml"}),
        ("origin/main", {"aio-a/units/20-C5-embeddings-v2/manifest.yaml"}),
    ) == ["duplicate aio-a/units code(s): C5"]


def test_duplicate_round2_unit_number_fails():
    assert collisions(
        ("WORKTREE", {"aio-a/units/B2-025-new/lessons/a.ipynb"}),
        ("origin/main", {"aio-a/units/B2-025-other/manifest.yaml"}),
    ) == ["duplicate aio-a/units number(s): B2-025"]


def test_duplicate_mocktest_id_fails():
    assert collisions(
        ("WORKTREE", {"aio-a/mocktests/r2-002/manifest.yaml"}),
        ("origin/main", {"aio-a/mocktests/r2-002-draft/manifest.yaml"}),
    ) == ["duplicate aio-a/mocktests number(s): r2-002"]


def test_same_pathname_in_both_refs_is_deduplicated():
    path = "aio-a/units/10-C5-embeddings/manifest.yaml"
    assert collisions(("WORKTREE", {path}), ("origin/main", {path})) == []


def test_rules_apply_only_to_given_aio_roots():
    assert collisions(
        ("WORKTREE", {"other/units/10-C5-a/x", "other/units/10-C5-b/x"}),
    ) == []


def test_tracked_reference_and_grading_files_are_refused():
    tracked = [
        "aio-a/reference/.gitkeep",
        "aio-a/reference/analysis.md",
        "aio-a/reference/r1-2026/paper.pdf",
        "aio-a/reference/cache/glove.txt",
        "aio-a/units/18-C11-competition-craft/data/heldout.csv",
        "aio-a/units/18-C11-competition-craft/data/train.csv",
        "aio-a/units/18-C11-competition-craft/practice/p17_log.csv",
        "aio-a/mocktests/r1-001/data/p09_heldout.csv",
        "py4kids-book/reference/r1-2026/paper.pdf",
    ]
    assert guard.aio_tracked_path_failures(tracked, ["aio-a"]) == [
        "tracked local-only aio grading file: aio-a/mocktests/r1-001/data/p09_heldout.csv",
        "tracked local-only aio reference file: aio-a/reference/cache/glove.txt",
        "tracked local-only aio reference file: aio-a/reference/r1-2026/paper.pdf",
        "tracked local-only aio grading file: aio-a/units/18-C11-competition-craft/data/heldout.csv",
        "tracked local-only aio grading file: aio-a/units/18-C11-competition-craft/practice/p17_log.csv",
    ]


def test_guard_failures_key_aio_rules_on_content_model(tmp_path, monkeypatch):
    (tmp_path / "books.yaml").write_text(
        "books_version: 2\n"
        "books:\n"
        "- {id: plain, number: 1, root: plain, depends_on: []}\n"
        "- {id: olymp, number: 4, root: olymp, depends_on: [], content_model: aio, aio_round: 1}\n",
        encoding="utf-8",
    )
    paths = {
        "WORKTREE": {
            "olymp/units/03-C1-a/manifest.yaml",
            "olymp/units/03-C2-b/manifest.yaml",
            "plain/units/03-C1-a/manifest.yaml",
            "plain/units/03-C2-b/manifest.yaml",
        }
    }
    tracked = ["olymp/reference/r1-2026/paper.pdf", "plain/reference/r1-2026/paper.pdf"]
    monkeypatch.setattr(guard, "_paths", lambda _root, ref: paths[ref])
    monkeypatch.setattr(guard, "_git_lines", lambda _root, *args: tracked)
    monkeypatch.setattr(
        guard, "_git", lambda _root, *args: subprocess.CompletedProcess(args, 1, "", "")
    )

    assert guard.guard_failures(Path(tmp_path), ["WORKTREE"]) == [
        "duplicate olymp/units order number(s): 03",
        "tracked local-only aio reference file: olymp/reference/r1-2026/paper.pdf",
    ]
