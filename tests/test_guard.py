"""Collision checks for top-level and namespaced plan files."""

import os
import subprocess
import sys
from pathlib import Path

from tools import guard

REPO = Path(__file__).resolve().parents[1]


def findings(*refs):
    return guard.plan_collision_failures({name: set(paths) for name, paths in refs})


def test_duplicate_namespaced_number_within_one_ref_fails():
    assert findings(
        ("WORKTREE", {"docs/plans/recsys/recsys-001-a.md", "docs/plans/recsys/recsys-001-b.md"}),
    ) == ["duplicate docs/plans/recsys number(s): recsys-001"]


def test_duplicate_namespaced_number_across_refs_fails():
    assert findings(
        ("WORKTREE", {"docs/plans/recsys/recsys-001-feature.md"}),
        ("origin/main", {"docs/plans/recsys/recsys-001-main.md"}),
    ) == ["duplicate docs/plans/recsys number(s): recsys-001"]


def test_same_pathname_in_both_refs_is_deduplicated():
    path = "docs/plans/recsys/recsys-001-foundation.md"
    assert findings(("WORKTREE", {path}), ("origin/main", {path})) == []


def test_distinct_namespaced_numbers_pass():
    assert findings(
        (
            "WORKTREE",
            {
                "docs/plans/recsys/recsys-001-foundation.md",
                "docs/plans/recsys/recsys-002-first-unit.md",
            },
        ),
    ) == []


def test_top_level_plan_numbers_remain_enforced():
    assert findings(
        ("WORKTREE", {"docs/plans/092-one.md", "docs/plans/092-two.md"}),
    ) == ["duplicate docs/plans number(s): 092"]


def test_only_immediate_namespace_directories_are_scanned():
    assert findings(
        (
            "WORKTREE",
            {
                "docs/plans/recsys/archive/recsys-001-a.md",
                "docs/plans/recsys/archive/recsys-001-b.md",
            },
        ),
    ) == []


def test_namespace_name_is_matched_literally():
    assert findings(
        (
            "WORKTREE",
            {
                "docs/plans/a.b/a.b-001-one.md",
                "docs/plans/a.b/a.b-001-two.md",
                "docs/plans/a.b/axb-001-three.md",
                "docs/plans/a.b/axb-001-four.md",
            },
        ),
    ) == ["duplicate docs/plans/a.b number(s): a.b-001"]


def test_full_collision_check_includes_namespaced_plans():
    path_sets = {
        "WORKTREE": {"docs/plans/recsys/recsys-001-worktree.md"},
        "origin/main": {"docs/plans/recsys/recsys-001-main.md"},
    }
    assert guard.collision_failures(path_sets, book_roots=[]) == [
        "duplicate docs/plans/recsys number(s): recsys-001"
    ]


def test_pr_main_fetches_fresh_ref_and_checks_deduplicated_union(monkeypatch, capsys):
    git_calls = []
    path_calls = []
    shared = "docs/plans/recsys/recsys-002-shared.md"
    paths = {
        "WORKTREE": {"docs/plans/recsys/recsys-001-worktree.md", shared},
        "origin/main": {"docs/plans/recsys/recsys-001-main.md", shared},
    }

    def fake_git(_root, *args):
        git_calls.append(args)
        return subprocess.CompletedProcess(args, 1 if args[0] == "grep" else 0, "", "")

    def fake_paths(_root, ref):
        path_calls.append(ref)
        return paths[ref]

    monkeypatch.setattr(guard, "_git", fake_git)
    monkeypatch.setattr(guard, "_paths", fake_paths)
    monkeypatch.setattr(guard, "_git_lines", lambda _root, *args: [])

    assert guard.main(["--pr"]) == 1
    assert git_calls[0] == (
        "fetch",
        "-q",
        "origin",
        "+refs/heads/main:refs/remotes/origin/main",
    )
    assert path_calls == ["WORKTREE", "origin/main"]
    assert capsys.readouterr().out.splitlines() == [
        "FAIL: duplicate docs/plans/recsys number(s): recsys-001"
    ]


def test_pr_main_fails_closed_when_fresh_fetch_fails(monkeypatch, capsys):
    monkeypatch.setattr(
        guard,
        "_git",
        lambda _root, *args: subprocess.CompletedProcess(args, 1, "", "fetch failed"),
    )
    monkeypatch.setattr(
        guard,
        "guard_failures",
        lambda *_args: (_ for _ in ()).throw(AssertionError("guard must not run after fetch failure")),
    )

    assert guard.main(["--pr"]) == 1
    assert capsys.readouterr().err == (
        "FAIL: origin/main fetch unavailable; --pr union is unverified\n"
    )


def test_shell_wrapper_forwards_arguments_to_python_module(tmp_path):
    fake_uv = tmp_path / "uv"
    fake_uv.write_text(
        "#!/bin/sh\n"
        'test "$1" = run || exit 90\n'
        "shift\n"
        'exec "$@"\n',
        encoding="utf-8",
    )
    fake_uv.chmod(0o755)
    env = os.environ | {
        "PATH": f"{tmp_path}:{Path(sys.executable).parent}:{os.environ['PATH']}"
    }

    result = subprocess.run(
        ["bash", REPO / "scripts/pre-merge-guard.sh", "unexpected"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert result.stderr == (
        "usage: pre-merge-guard.sh [--pr]   (unknown argument: unexpected)\n"
    )
