from __future__ import annotations

import ast
import os
import re
import shlex
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from conftest import ROOT

# The aio producers (design 014 D3: usaaio's tools/, scripts/ and tests/ live under tools/aio/,
# scripts/aio/ and tools/aio/tests/ in py4kids). usaaio pinned the contract tests below (which
# build their own repository-root fixtures) in the dropped plan019-path-inventory.yaml
# (`task0_contract_tests`, minus the dropped test_reference_migration.py).
AIO_PYTHON_PRODUCERS = ("tools/aio", "scripts/aio")
AIO_SHELL_PRODUCERS = "scripts/aio"
CONTRACT_TESTS = frozenset(
    {
        "tools/aio/tests/test_books.py",
        "tools/aio/tests/test_book_isolation.py",
        "tools/aio/tests/test_clean_checkout.py",
    }
)
CONTENT_TOKENS = {
    "units",
    "curriculum",
    "mocktests",
    "reference",
    "syllabus.md",
    "sources.yaml",
    "course-structure.md",
    "build",
}


def _looks_like_content_path(value: str) -> bool:
    normalized = value.replace("\\", "/")
    return any(
        normalized == token
        or normalized.startswith(f"{token}/")
        or f"/{token}/" in normalized
        or normalized.endswith(f"/{token}")
        for token in CONTENT_TOKENS
    )


def _invalid_root_accesses(source: str, *, language: str) -> list[str]:
    if language == "shell":
        patterns = (
            r"\bfind\s+units\b",
            r"\bfor\s+dir\s+in\s+units\s+mocktests\b",
        )
    else:
        patterns = (
            r"\bPath\(\s*[\"']syllabus\.md[\"']\s*\)",
            r"\bcheck_[a-z_]+\(\s*(?:repo_root|ROOT)\s*\)",
        )
    return [pattern for pattern in patterns if re.search(pattern, source)]


def _division_parts(node: ast.AST) -> list[ast.AST]:
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        return [*_division_parts(node.left), *_division_parts(node.right)]
    return [node]


def _repo_root_aliases(tree: ast.AST) -> set[str]:
    aliases = {"ROOT", "repo_root"}
    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            value = node.value
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            rendered = ast.unparse(value) if value is not None else ""
            discovered_root = (
                "Path(__file__)" in rendered
                and (".parents[" in rendered or ".parent" in rendered)
            ) or bool(
                re.fullmatch(
                    r"(?:Path\.cwd\(\)|Path\(['\"]\.['\"]\)|"
                    r"Path\(os\.getcwd\(\)\)|os\.getcwd\(\))"
                    r"(?:\.(?:resolve|absolute)\(\))*",
                    rendered,
                )
            )
            if (isinstance(value, ast.Name) and value.id in aliases) or discovered_root:
                for target in targets:
                    if isinstance(target, ast.Name) and target.id not in aliases:
                        aliases.add(target.id)
                        changed = True
    return aliases


def _is_repo_root_expression(node: ast.AST, aliases: set[str]) -> bool:
    if isinstance(node, ast.Name):
        return node.id in aliases
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"resolve", "absolute"}
    ):
        return _is_repo_root_expression(node.func.value, aliases)
    return False


def _path_literal_values(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Path":
        return [
            arg.value
            for arg in node.args
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
        ]
    return []


def _actual_python_root_accesses(path: Path) -> list[dict[str, object]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    aliases = _repo_root_aliases(tree)
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    violations: list[dict[str, object]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            if isinstance(parents.get(node), ast.BinOp):
                continue
            parts = _division_parts(node)
            anchor = parts[0]
            values = [value for part in parts[1:] for value in _path_literal_values(part)]
            if _is_repo_root_expression(anchor, aliases):
                if any(value in {"aio-ml", "aio-dl"} for value in values):
                    violations.append(
                        {"line": node.lineno, "kind": "hardcoded-repo-book-root"}
                    )
                elif any(_looks_like_content_path(value) for value in values):
                    violations.append(
                        {"line": node.lineno, "kind": "repo-root-path-join"}
                    )
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "joinpath"
            and _is_repo_root_expression(node.func.value, aliases)
            and any(
                value in {"aio-ml", "aio-dl"} or _looks_like_content_path(value)
                for arg in node.args
                for value in _path_literal_values(arg)
            )
        ):
            values = [
                value
                for arg in node.args
                for value in _path_literal_values(arg)
            ]
            kind = (
                "hardcoded-repo-book-root"
                if any(value in {"aio-ml", "aio-dl"} for value in values)
                else "repo-root-path-join"
            )
            violations.append({"line": node.lineno, "kind": kind})
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "Path"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == "syllabus.md"
        ):
            violations.append({"line": node.lineno, "kind": "literal-root-syllabus"})
        if isinstance(node, ast.Call):
            function = node.func
            name = (
                function.id
                if isinstance(function, ast.Name)
                else function.attr
                if isinstance(function, ast.Attribute)
                else ""
            )
            if name.startswith("check_") and any(
                _is_repo_root_expression(value, aliases)
                for value in [*node.args, *(kw.value for kw in node.keywords)]
            ):
                violations.append({"line": node.lineno, "kind": "unselected-checker-root"})
    return sorted(violations, key=lambda row: (int(row["line"]), str(row["kind"])))


def _shell_expanding_text(source: str) -> str:
    """Remove single-quoted shell literals while preserving expanding contexts."""
    output: list[str] = []
    in_single = False
    in_double = False
    escaped = False
    for character in source:
        if escaped:
            output.append(
                " " if in_single or character in {"$", "`"} else character
            )
            escaped = False
            continue
        if character == "\\" and not in_single:
            output.append(character)
            escaped = True
            continue
        if character == "'" and not in_double:
            in_single = not in_single
            output.append(" ")
            continue
        if character == '"' and not in_single:
            in_double = not in_double
        output.append(character if not in_single else " ")
    return "".join(output)


def _shell_variable_reference_pattern(names: set[str]) -> str:
    alternatives = "|".join(re.escape(name) for name in sorted(names))
    return rf"\$(?:\{{(?:{alternatives})\}}|(?:{alternatives})(?![A-Za-z0-9_]))"


def _shell_logical_lines(source: str) -> list[tuple[int, str]]:
    """Join shell continuations and retain the first physical source line."""
    logical: list[tuple[int, str]] = []
    pending = ""
    first_line = 1
    for line_number, line in enumerate(source.splitlines(), start=1):
        if not pending:
            first_line = line_number
        trailing_backslashes = len(line) - len(line.rstrip("\\"))
        if trailing_backslashes % 2:
            pending += line[:-1]
            continue
        logical.append((first_line, pending + line))
        pending = ""
    if pending:
        logical.append((first_line, pending))
    return logical


def _shell_words(source: str) -> list[str]:
    """Split top-level shell words without splitting command substitutions."""
    words: list[str] = []
    current: list[str] = []
    in_single = False
    in_double = False
    escaped = False
    command_depth = 0
    index = 0
    while index < len(source):
        character = source[index]
        if escaped:
            current.append(character)
            escaped = False
            index += 1
            continue
        if character == "\\" and not in_single:
            current.append(character)
            escaped = True
            index += 1
            continue
        if character == "'" and not in_double:
            in_single = not in_single
        elif character == '"' and not in_single:
            in_double = not in_double
        if (
            character == "$"
            and index + 1 < len(source)
            and source[index + 1] == "("
            and not in_single
        ):
            command_depth += 1
        elif character == ")" and command_depth and not in_single:
            command_depth -= 1
        if character.isspace() and not in_single and not in_double and not command_depth:
            if current:
                words.append("".join(current))
                current = []
        else:
            current.append(character)
        index += 1
    if current:
        words.append("".join(current))
    return words


def _shell_word_text(source: str) -> str:
    """Preserve literal word segments while masking their expansion markers."""
    output: list[str] = []
    in_single = False
    in_double = False
    escaped = False
    for character in source:
        if escaped:
            output.append(" " if character in {"$", "`"} else character)
            escaped = False
            continue
        if character == "\\" and not in_single:
            output.append(character)
            escaped = True
            continue
        if character == "'" and not in_double:
            in_single = not in_single
            output.append(character)
            continue
        if character == '"' and not in_single:
            in_double = not in_double
        output.append(" " if in_single and character in {"$", "`"} else character)
    return "".join(output)


def _shell_normalized_word(word: str) -> str | None:
    try:
        normalized = shlex.split(_shell_word_text(word), posix=True)
    except ValueError:
        return None
    return normalized[0] if len(normalized) == 1 else None


def _shell_assignment(word: str) -> tuple[str, str] | None:
    assignment = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)=(.*)", word)
    return assignment.groups() if assignment else None


def _shell_assignments(source: str) -> list[tuple[str, str]]:
    words = _shell_words(source)
    if not words:
        return []
    declaration_builtins = {"declare", "export", "local", "readonly", "typeset"}
    if _shell_normalized_word(words[0]) in declaration_builtins:
        return [
            assignment
            for word in words[1:]
            if (assignment := _shell_assignment(word)) is not None
        ]
    assignments: list[tuple[str, str]] = []
    for word in words:
        assignment = _shell_assignment(word)
        if assignment is None:
            break
        assignments.append(assignment)
    return assignments


def _without_shell_redirections(tokens: list[str]) -> list[str] | None:
    operators = {"<", ">", ">>", "<>", ">&", "<&", "&>"}
    controls = operators | {";", "|", "||", "&&"}
    argv: list[str] = []
    index = 0
    while index < len(tokens):
        operator_index = index
        if (
            re.fullmatch(r"__AIO_SHELL_FD_\d+__", tokens[operator_index])
            and operator_index + 1 < len(tokens)
            and tokens[operator_index + 1] in operators
        ):
            operator_index += 1
        if tokens[operator_index] not in operators:
            argv.append(tokens[index])
            index += 1
            continue
        target_index = operator_index + 1
        if target_index >= len(tokens) or tokens[target_index] in controls:
            return None
        index = target_index + 1
    return argv


def _mark_adjacent_shell_fds(command: str) -> str:
    output: list[str] = []
    in_single = False
    in_double = False
    escaped = False
    index = 0
    while index < len(command):
        character = command[index]
        if escaped:
            output.append(character)
            escaped = False
            index += 1
            continue
        if character == "\\" and not in_single:
            output.append(character)
            escaped = True
            index += 1
            continue
        if character == "'" and not in_double:
            in_single = not in_single
        elif character == '"' and not in_single:
            in_double = not in_double
        if not in_single and not in_double and character.isdigit():
            end = index
            while end < len(command) and command[end].isdigit():
                end += 1
            at_word_boundary = (
                index == 0
                or command[index - 1].isspace()
                or command[index - 1] in ";|&("
            )
            if at_word_boundary and end < len(command) and command[end] in "<>":
                output.append(f"__AIO_SHELL_FD_{command[index:end]}__")
                index = end
                continue
        output.append(character)
        index += 1
    return "".join(output)


def _is_git_root_command(command: str) -> bool:
    try:
        lexer = shlex.shlex(
            _mark_adjacent_shell_fds(command),
            posix=True,
            punctuation_chars="><&;|",
        )
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        return False
    return _without_shell_redirections(tokens) == [
        "git",
        "rev-parse",
        "--show-toplevel",
    ]


def _has_git_root_substitution(source: str) -> bool:
    expanding = _shell_expanding_text(source)
    for match in re.finditer(r"\$\(([^()]*)\)", expanding):
        raw_command = source[match.start(1) : match.end(1)]
        if _is_git_root_command(raw_command):
            return True
    return False


def _shell_discovers_repo_root(value: str, aliases: set[str]) -> bool:
    expanding = _shell_expanding_text(value)
    return bool(
        re.search(_shell_variable_reference_pattern({"PWD"}), expanding)
        or re.search(r"\$\(\s*pwd\s*\)", expanding)
        or _has_git_root_substitution(value)
        or re.search(_shell_variable_reference_pattern(aliases), expanding)
    )


def _shell_find_uses_units_root(source: str, aliases: set[str]) -> bool:
    words = _shell_words(source)
    index = 0
    while index < len(words) and _shell_assignment(words[index]) is not None:
        index += 1
    if index >= len(words) or _shell_normalized_word(words[index]) != "find":
        return False
    index += 1
    if index < len(words) and _shell_normalized_word(words[index]) == "--":
        index += 1
    if index >= len(words):
        return False
    path = _shell_normalized_word(words[index])
    return bool(
        path
        and re.fullmatch(
            rf"{_shell_variable_reference_pattern(aliases)}/units(?:/.*)?",
            path,
        )
    )


def _actual_shell_root_accesses(path: Path) -> list[dict[str, object]]:
    repository_root_reference = _shell_variable_reference_pattern(
        {"PWD", "ROOT", "repo_root"}
    )
    patterns = {
        "root-find-units": re.compile(r"\bfind\s+units(?:\s|$)"),
        "root-find-units-mocktests": re.compile(r"\bfind\s+units\s+mocktests(?:\s|$)"),
        "root-for-units-mocktests": re.compile(
            r"\bfor\s+(?:dir|[A-Za-z_][A-Za-z0-9_]*)\s+in\s+units\s+mocktests\b"
        ),
        "hardcoded-repo-book-root": re.compile(
            rf"{repository_root_reference}/aio-(?:ml|dl)(?:[/\"'\s]|$)"
        ),
    }
    violations: list[dict[str, object]] = []
    root_names = {"PWD", "ROOT", "repo_root"}
    aliases = set(root_names)
    for line_number, line in _shell_logical_lines(path.read_text(encoding="utf-8")):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        expanding_line = _shell_expanding_text(line)
        for kind, pattern in patterns.items():
            if pattern.search(expanding_line):
                violations.append({"line": line_number, "kind": kind})
        for name, value in _shell_assignments(line):
            if _shell_discovers_repo_root(value, aliases):
                aliases.add(name)
        if _shell_find_uses_units_root(line, aliases):
            violations.append({"line": line_number, "kind": "root-find-variable-units"})
    return violations


def _actual_repository_root_accesses(
    repo: Path = ROOT,
    *,
    python_dirs: tuple[str, ...] = ("tools", "scripts", "tests"),
    shell_dir: str = "scripts",
) -> dict[str, list[dict[str, object]]]:
    violations: dict[str, list[dict[str, object]]] = {}
    for base in (repo / name for name in python_dirs):
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.py")):
            relative = path.relative_to(repo).as_posix()
            if relative in CONTRACT_TESTS:
                continue
            rows = _actual_python_root_accesses(path)
            if relative.startswith(("tests/", "tools/aio/tests/")):
                rows = [
                    row for row in rows if row["kind"] != "hardcoded-repo-book-root"
                ]
            if rows:
                violations[relative] = rows
    for path in sorted((repo / shell_dir).rglob("*.sh")):
        rows = _actual_shell_root_accesses(path)
        if rows:
            violations[path.relative_to(repo).as_posix()] = rows
    return violations


@pytest.mark.parametrize(
    ("source", "language"),
    [
        ("find units -name manifest.yaml", "shell"),
        ("for dir in units mocktests; do echo $dir; done", "shell"),
        ('source = Path("syllabus.md")', "python"),
        ("check_scope(repo_root)", "python"),
    ],
)
def test_static_contract_rejects_repository_root_content_access(source: str, language: str) -> None:
    assert _invalid_root_accesses(source, language=language)


def test_static_contract_allows_selected_book_local_joins() -> None:
    assert _invalid_root_accesses('root / "units"', language="python") == []
    assert (
        _invalid_root_accesses('find "$book_root/units" -name manifest.yaml', language="shell")
        == []
    )


@pytest.mark.parametrize(
    ("relative", "source", "line", "kind"),
    [
        ("tools/producer.py", 'ROOT.joinpath("units")\n', 1, "repo-root-path-join"),
        ("tools/producer.py", 'BASE = ROOT\nBASE / "units"\n', 2, "repo-root-path-join"),
        ("tools/producer.py", 'ROOT / Path("units")\n', 1, "repo-root-path-join"),
        ("tools/producer.py", "check_scope(root=ROOT)\n", 1, "unselected-checker-root"),
        (
            "tools/producer.py",
            'repo_root.resolve() / "curriculum"\n',
            1,
            "repo-root-path-join",
        ),
        (
            "scripts/producer.sh",
            'find "$repo_root/units" -name manifest.yaml\n',
            1,
            "root-find-variable-units",
        ),
        (
            "tools/producer.py",
            'ROOT / "aio-ml"\n',
            1,
            "hardcoded-repo-book-root",
        ),
        (
            "scripts/producer.sh",
            'book_root="$repo_root/aio-ml"\n',
            1,
            "hardcoded-repo-book-root",
        ),
        (
            "tools/producer.py",
            'PROJECT = Path(__file__).resolve().parents[1]\nPROJECT / "units"\n',
            2,
            "repo-root-path-join",
        ),
        (
            "tools/producer.py",
            'PROJECT = Path(__file__).resolve().parents[1]\nBASE = PROJECT\nBASE / "units"\n',
            3,
            "repo-root-path-join",
        ),
        (
            "scripts/producer.sh",
            'content_root="$PWD"\nfind "$content_root/units" -name manifest.yaml\n',
            2,
            "root-find-variable-units",
        ),
        (
            "scripts/producer.sh",
            'content_root="$ROOT"\nfind "$content_root/units" -name manifest.yaml\n',
            2,
            "root-find-variable-units",
        ),
        (
            "scripts/producer.sh",
            'content_root="${ROOT}"\nfind "$content_root/units" -name manifest.yaml\n',
            2,
            "root-find-variable-units",
        ),
        (
            "tools/producer.py",
            'PROJECT = Path.cwd()\nPROJECT / "units"\n',
            2,
            "repo-root-path-join",
        ),
        (
            "tools/producer.py",
            'PROJECT = Path(".").resolve()\nBASE = PROJECT\nBASE / "units"\n',
            3,
            "repo-root-path-join",
        ),
        (
            "tools/producer.py",
            'PROJECT = Path(os.getcwd())\nPROJECT.joinpath("curriculum")\n',
            2,
            "repo-root-path-join",
        ),
        (
            "scripts/producer.sh",
            (
                'content_root=$(git rev-parse --show-toplevel)\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
            "root-find-variable-units",
        ),
        (
            "scripts/producer.sh",
            (
                'project=$(git rev-parse --show-toplevel)\ncontent_root="$project"\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            3,
            "root-find-variable-units",
        ),
        (
            "scripts/producer.sh",
            (
                'project="$(git rev-parse --show-toplevel)"\n'
                'content_root="${project}"\n'
                'find "${content_root}/units" -name manifest.yaml\n'
            ),
            3,
            "root-find-variable-units",
        ),
        (
            "scripts/producer.sh",
            (
                'content_root="${PWD}"\n'
                'find "${content_root}/units" -name manifest.yaml\n'
            ),
            2,
            "root-find-variable-units",
        ),
        (
            "scripts/producer.sh",
            (
                'content_root="$(git rev-parse --show-toplevel 2>/dev/null)"\n'
                'find "${content_root}/units" -name manifest.yaml\n'
            ),
            2,
            "root-find-variable-units",
        ),
        (
            "scripts/producer.sh",
            (
                'content_root="$( git rev-parse --show-toplevel )"\n'
                'find "${content_root}/units" -name manifest.yaml\n'
            ),
            2,
            "root-find-variable-units",
        ),
        (
            "scripts/producer.sh",
            (
                'content_root=$(  git  rev-parse  --show-toplevel 2>&1 )\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
            "root-find-variable-units",
        ),
        (
            "scripts/producer.sh",
            (
                'project="$(git rev-parse --show-toplevel 2> /dev/null)"\n'
                'content_root="${project}"\n'
                'find "${content_root}/units" -name manifest.yaml\n'
            ),
            3,
            "root-find-variable-units",
        ),
    ],
)
def test_actual_scanner_rejects_root_access_mutations_in_discovered_producers(
    tmp_path: Path, relative: str, source: str, line: int, kind: str
) -> None:
    producer = tmp_path / relative
    producer.parent.mkdir(parents=True, exist_ok=True)
    producer.write_text(source, encoding="utf-8")

    assert _actual_repository_root_accesses(tmp_path) == {relative: [{"line": line, "kind": kind}]}


def test_actual_scanner_allows_bookspec_and_book_local_root_joins(tmp_path: Path) -> None:
    producer = tmp_path / "tools" / "producer.py"
    producer.parent.mkdir(parents=True)
    producer.write_text(
        'book.root / "units"\nselected_root.joinpath("curriculum")\n', encoding="utf-8"
    )
    shell = tmp_path / "scripts" / "producer.sh"
    shell.parent.mkdir(parents=True)
    shell.write_text('find "$book_root/units" -name manifest.yaml\n', encoding="utf-8")

    cwd_selected = tmp_path / "tools" / "selected.py"
    cwd_selected.write_text(
        'repo = Path.cwd()\nbook_root = selected_book.root\nbook_root / "units"\n',
        encoding="utf-8",
    )
    shell.write_text(
        'repo=$(git rev-parse --show-toplevel)\n'
        'book_root="$selected_book_root"\n'
        'find "$book_root/units" -name manifest.yaml\n',
        encoding="utf-8",
    )

    safe_shell = tmp_path / "scripts" / "safe-selected.sh"
    safe_shell.write_text(
        'repo="${PWD}"\n'
        'book_root="${SELECTED_BOOK_ROOT}"\n'
        'find "${book_root}/units" -name manifest.yaml\n'
        "literal='${PWD}'\n"
        'find "${literal}/units" -name manifest.yaml\n',
        encoding="utf-8",
    )

    assert _actual_repository_root_accesses(tmp_path) == {}


@pytest.mark.parametrize(
    "source",
    [
        'literal="\\${PWD}"\nfind "${literal}/units" -name manifest.yaml\n',
        (
            'book_root="${ROOT_FOR_SELECTED_BOOK}"\n'
            'find "${book_root}/units" -name manifest.yaml\n'
        ),
        'book_root="$ROOTED"\nfind "$book_root/units" -name manifest.yaml\n',
        'book_root="${MY_PWD}"\nfind "${book_root}/units" -name manifest.yaml\n',
        (
            'selected_alias="${SELECTED_BOOK_ROOT}"\n'
            'book_root="$selected_alias"\n'
            'find "$book_root/units" -name manifest.yaml\n'
        ),
    ],
)
def test_actual_scanner_preserves_safe_shell_path_controls(
    tmp_path: Path, source: str
) -> None:
    producer = tmp_path / "scripts" / "safe-selected.sh"
    producer.parent.mkdir(parents=True)
    producer.write_text(source, encoding="utf-8")

    assert _actual_repository_root_accesses(tmp_path) == {}


@pytest.mark.parametrize(
    ("source", "line"),
    [
        ('find "$PWD/units" -name manifest.yaml\n', 1),
        ('find "${PWD}/units" -name manifest.yaml\n', 1),
        (
            (
                'content_root=$(git "rev-parse" --show-toplevel)\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                "content_root=$(git 'rev-parse' '--show-toplevel')\n"
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'content_root=$(git rev-parse --show-toplevel> /dev/null)\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'content_root=$("git" \'rev-parse\' "--show-toplevel" > /dev/null)\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'content_root=$(git rev-parse --show-toplevel>/dev/null)\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'content_root=$(git rev-parse --show-toplevel 2>/dev/null)\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'content_root=$(git rev-parse --show-toplevel 2>&1)\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'content_root="$(git rev-parse \\\n'
                '  --show-toplevel)"\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            3,
        ),
        (('find "$PWD/uni\\\n' 'ts" -name manifest.yaml\n'), 1),
        (
            (
                'content_root=$(git rev-parse --show-top\\\n'
                'level)\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            3,
        ),
        (
            (
                'export content_root="$PWD"\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'readonly content_root="${PWD}"\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'local content_root=$(git rev-parse --show-toplevel)\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'declare content_root="$ROOT"\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'typeset content_root="${repo_root}"\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'export project="$PWD" content_root="$project"\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'readonly project=$(git rev-parse --show-toplevel)\n'
                'local middle="$project" content_root="${middle}"\n'
                'find "${content_root}/units" -name manifest.yaml\n'
            ),
            3,
        ),
    ],
)
def test_actual_scanner_rejects_normalized_shell_root_discovery(
    tmp_path: Path, source: str, line: int
) -> None:
    producer = tmp_path / "scripts" / "producer.sh"
    producer.parent.mkdir(parents=True)
    producer.write_text(source, encoding="utf-8")

    assert _actual_repository_root_accesses(tmp_path) == {
        "scripts/producer.sh": [{"line": line, "kind": "root-find-variable-units"}]
    }


@pytest.mark.parametrize(
    "source",
    [
        'book_root="$PWD_SUFFIX"\nfind "$book_root/units" -name manifest.yaml\n',
        'book_root="${PWD_SUFFIX}"\nfind "$book_root/units" -name manifest.yaml\n',
        (
            'book_root=$(git rev-parse --show-prefix)\n'
            'find "$book_root/units" -name manifest.yaml\n'
        ),
        (
            'book_root=$(git status --show-toplevel)\n'
            'find "$book_root/units" -name manifest.yaml\n'
        ),
        (
            'book_root=$(echo git rev-parse --show-toplevel)\n'
            'find "$book_root/units" -name manifest.yaml\n'
        ),
        (
            'book_root=$(git rev-parse --show-toplevel; echo suffix)\n'
            'find "$book_root/units" -name manifest.yaml\n'
        ),
        (
            'export selected="${ROOT_FOR_SELECTED_BOOK}" book_root="$selected"\n'
            'find "$book_root/units" -name manifest.yaml\n'
        ),
        (
            'readonly selected="${SELECTED_BOOK_ROOT}"\n'
            'local middle="$selected" book_root="$middle"\n'
            'find "$book_root/units" -name manifest.yaml\n'
        ),
    ],
)
def test_actual_scanner_allows_normalized_shell_near_misses(
    tmp_path: Path, source: str
) -> None:
    producer = tmp_path / "scripts" / "safe-selected.sh"
    producer.parent.mkdir(parents=True)
    producer.write_text(source, encoding="utf-8")

    assert _actual_repository_root_accesses(tmp_path) == {}


@pytest.mark.parametrize(
    ("source", "line"),
    [
        ('find "$PWD"/units -name manifest.yaml\n', 1),
        ('find "${PWD}"/units -name manifest.yaml\n', 1),
        ('find -- "$PWD/units" -name manifest.yaml\n', 1),
        ('find "$PWD"/uni"ts" -name manifest.yaml\n', 1),
        (
            'project="$PWD"\nfind -- "${project}"/units -name manifest.yaml\n',
            2,
        ),
        (
            (
                'content_root=$(git rev-parse --show-toplevel</dev/null)\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'content_root=$(git rev-parse --show-toplevel < /dev/null)\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'content_root=$(2>/dev/null git rev-parse --show-toplevel)\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'content_root=$(git 2>/dev/null rev-parse --show-toplevel)\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'content_root=$(2>"/dev/null" git rev-parse < /dev/null '
                '--show-toplevel 3>&1)\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'export marker content_root="$PWD"\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
        (
            (
                'declare -r marker content_root="${ROOT}"\n'
                'find "$content_root/units" -name manifest.yaml\n'
            ),
            2,
        ),
    ],
)
def test_actual_scanner_rejects_bounded_shell_command_variants(
    tmp_path: Path, source: str, line: int
) -> None:
    producer = tmp_path / "scripts" / "producer.sh"
    producer.parent.mkdir(parents=True)
    producer.write_text(source, encoding="utf-8")

    assert _actual_repository_root_accesses(tmp_path) == {
        "scripts/producer.sh": [{"line": line, "kind": "root-find-variable-units"}]
    }


@pytest.mark.parametrize(
    "source",
    [
        (
            'book_root="${SELECTED_BOOK_ROOT}"\n'
            'printf "%s\\n" book_root="$PWD"\n'
            'find "$book_root/units" -name manifest.yaml\n'
        ),
        (
            'book_root="${SELECTED_BOOK_ROOT}"\n'
            'printf "%s\\n" ignored=value project="$PWD" book_root="$project"\n'
            'find "$book_root/units" -name manifest.yaml\n'
        ),
        'printf find "$PWD/units"\n',
        'find -- "$PWD_SUFFIX/units" -name manifest.yaml\n',
        (
            'book_root=$(git 2>/dev/null rev-parse --show-toplevel extra)\n'
            'find "$book_root/units" -name manifest.yaml\n'
        ),
        (
            'book_root=$(2>/dev/null echo git rev-parse --show-toplevel)\n'
            'find "$book_root/units" -name manifest.yaml\n'
        ),
        (
            'book_root=$(git rev-parse < /dev/null --show-prefix)\n'
            'find "$book_root/units" -name manifest.yaml\n'
        ),
    ],
)
def test_actual_scanner_allows_bounded_shell_command_near_misses(
    tmp_path: Path, source: str
) -> None:
    producer = tmp_path / "scripts" / "safe-selected.sh"
    producer.parent.mkdir(parents=True)
    producer.write_text(source, encoding="utf-8")

    assert _actual_repository_root_accesses(tmp_path) == {}


@pytest.mark.parametrize(
    "source",
    [
        'find "$PWD"/\'units\' -name manifest.yaml\n',
        'find "${PWD}"/\'un\'\'its\' -name manifest.yaml\n',
        'find "$PWD"\'/\'units -name manifest.yaml\n',
        (
            'project="$PWD"\n'
            'find "${project}"/\'units\' -name manifest.yaml\n'
        ),
    ],
)
def test_actual_scanner_rejects_expanding_and_literal_word_segments(
    tmp_path: Path, source: str
) -> None:
    producer = tmp_path / "scripts" / "producer.sh"
    producer.parent.mkdir(parents=True)
    producer.write_text(source, encoding="utf-8")

    expected_line = 2 if source.startswith("project=") else 1
    assert _actual_repository_root_accesses(tmp_path) == {
        "scripts/producer.sh": [
            {"line": expected_line, "kind": "root-find-variable-units"}
        ]
    }


@pytest.mark.parametrize(
    "source",
    [
        "find '$PWD/units' -name manifest.yaml\n",
        "find '${PWD}'/'units' -name manifest.yaml\n",
        "find '$PWD'/\"units\" -name manifest.yaml\n",
        (
            'project="$PWD"\n'
            "find '${project}'/units -name manifest.yaml\n"
        ),
    ],
)
def test_actual_scanner_allows_nonexpanding_literal_word_segments(
    tmp_path: Path, source: str
) -> None:
    producer = tmp_path / "scripts" / "safe-selected.sh"
    producer.parent.mkdir(parents=True)
    producer.write_text(source, encoding="utf-8")

    assert _actual_repository_root_accesses(tmp_path) == {}


@pytest.mark.parametrize(
    "command",
    [
        "2 > /dev/null git rev-parse --show-toplevel",
        "git 2 > /dev/null rev-parse --show-toplevel",
        "git rev-parse 2 > /dev/null --show-toplevel",
        "git rev-parse --show-toplevel 2 > /dev/null",
    ],
)
def test_actual_scanner_does_not_treat_spaced_digits_as_redirect_fds(
    tmp_path: Path, command: str
) -> None:
    producer = tmp_path / "scripts" / "safe-selected.sh"
    producer.parent.mkdir(parents=True)
    producer.write_text(
        f'book_root=$( {command} )\nfind "$book_root/units" -name manifest.yaml\n',
        encoding="utf-8",
    )

    assert _actual_repository_root_accesses(tmp_path) == {}


def test_actual_scanner_allows_spaced_bare_redirect_in_exact_git_command(
    tmp_path: Path,
) -> None:
    producer = tmp_path / "scripts" / "producer.sh"
    producer.parent.mkdir(parents=True)
    producer.write_text(
        'book_root=$(git > /dev/null rev-parse --show-toplevel)\n'
        'find "$book_root/units" -name manifest.yaml\n',
        encoding="utf-8",
    )

    assert _actual_repository_root_accesses(tmp_path) == {
        "scripts/producer.sh": [
            {"line": 2, "kind": "root-find-variable-units"}
        ]
    }


def test_actual_producers_have_no_repository_root_content_access() -> None:
    # usaaio's pre-cutover branch (a root syllabus.md compared against the dropped inventory's
    # transition list) cannot arise here: test_atomic_cutover refuses every legacy root.
    actual = _actual_repository_root_accesses(
        ROOT, python_dirs=AIO_PYTHON_PRODUCERS, shell_dir=AIO_SHELL_PRODUCERS
    )
    assert actual == {}, actual


def test_atomic_cutover_has_every_moved_producer_and_no_legacy_root() -> None:
    expected = (
        "syllabus.md",
        "curriculum/course-schedule.yaml",
        "curriculum/coverage-map.yaml",
        "curriculum/material-inventory.yaml",
        "curriculum/official-topics.yaml",
        "curriculum/source-manifest.yaml",
        "units",
        "mocktests/blueprint.yaml",
        "reference",
        "docs/course-structure.md",
    )
    for book in ("aio-ml", "aio-dl"):
        for relative in expected:
            assert (ROOT / book / relative).exists(), f"missing producer {book}/{relative}"
    for legacy in ("syllabus.md", "curriculum", "units", "mocktests", "reference"):
        path = ROOT / legacy
        assert not path.exists(), f"legacy producer remains: {legacy}"
        assert not path.is_symlink(), f"legacy symlink remains: {legacy}"


def test_book_local_generated_paths_are_ignored_without_ignoring_sources(
    tmp_path: Path,
) -> None:
    ignored = (
        "aio-ml/build/mock.pdf",
        "aio-dl/build/unit.pdf",
        "aio-ml/mocktests/r1-001/build/test.pdf",
        "aio-ml/reference/r1-2026/paper.pdf",
        "aio-dl/reference/r2-2026/day1.pdf",
        "aio-ml/units/18-C11-competition-craft/data/heldout.csv",
        "aio-ml/units/18-C11-competition-craft/practice/p15_contract.csv",
        "aio-ml/mocktests/r1-001/data/p09_heldout.csv",
    )
    sources = (
        "aio-ml/syllabus.md",
        "aio-dl/syllabus.md",
        "aio-ml/reference/analysis.md",
        "aio-dl/reference/analysis.md",
        "aio-ml/units/18-C11-competition-craft/data/make_dataset.py",
        "aio-ml/mocktests/r1-001/data/gen_p09.py",
        "aio-ml/mocktests/r1-001/problems/p09.ipynb",
    )

    git_dir = tmp_path / "metadata.git"
    subprocess.run(
        ["git", "init", "--bare", str(git_dir)],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"},
    )
    git_prefix = [
        "git",
        f"--git-dir={git_dir}",
        f"--work-tree={ROOT}",
        "-c",
        f"core.excludesFile={os.devnull}",
        "check-ignore",
        "--no-index",
        "--quiet",
    ]
    git_env = {
        **os.environ,
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
    }

    for relative in ignored:
        proc = subprocess.run(
            [*git_prefix, relative],
            check=False,
            env=git_env,
        )
        assert proc.returncode == 0, relative
    for relative in sources:
        assert (ROOT / relative).is_file(), relative
        proc = subprocess.run(
            [*git_prefix, relative],
            check=False,
            env=git_env,
        )
        assert proc.returncode == 1, relative




# --- scripts/aio/verify-clean-checkout.sh (plan aio-001 Phase D / F.2) ---------------------
# usaaio's verifier archived HEAD and ran its own ci-local (PDF builds and every solution) in the
# archive. The py4kids rewrite clones HEAD into a fresh directory, provisions step B into the
# clone from outside it, runs ci-local there and then requires every provisioned file to be
# ignored and untracked. These tests drive the real script against a fixture repository whose
# provisioning and CI are stubs that record a trace and check what they can see.

_FIXTURE_GITIGNORE = """\
__pycache__/
aio-*/reference/*
!aio-*/reference/.gitkeep
!aio-*/reference/analysis.md
"""

_STUB_FETCH = """\
#!/usr/bin/env bash
set -euo pipefail
[[ $1 == --root && $3 == --all ]]
root=$2
printf 'fetch:%s\\n' "$root" >> "$VERIFY_TRACE"
for book in aio-ml aio-dl; do
  mkdir -p "$root/$book/reference/2026"
  printf '%s\\n' '%PDF-1.4 fixture paper' > "$root/$book/reference/2026/paper.pdf"
done
"""

_STUB_PROVISION = """\
#!/usr/bin/env bash
set -euo pipefail
[[ $1 == --root ]]
root=$2
printf 'provision:%s\\n' "$root" >> "$VERIFY_TRACE"
mkdir -p "$root/aio-ml/reference/cache"
printf 'artifact\\n' > "$root/aio-ml/reference/cache/artifact.bin"
"""

_STUB_CI = """\
#!/usr/bin/env bash
set -euo pipefail
[[ $PWD == "$CLONE" ]]
[[ $TMPDIR == /dev/shm ]]
[[ ! -e UNTRACKED_WORKTREE_SENTINEL ]]
[[ $(cat TRACKED_HEAD_SENTINEL) == "committed bytes" ]]
[[ -s aio-ml/reference/cache/artifact.bin ]]
for book in aio-ml aio-dl; do
  [[ -s "$book/reference/2026/paper.pdf" ]]
done
printf 'ci:%s\\n' "$PWD" >> "$VERIFY_TRACE"
"""

# The verifier lists the aio roots with `uv run --frozen python -` and py4kids' tools/books.py
# (copied into the fixture). This stub `uv` runs that interpreter directly, so no environment
# is synced into the fixture.
_STUB_UV = """\
#!/usr/bin/env bash
set -euo pipefail
[[ $1 == run && $2 == --frozen && $3 == python ]]
shift 3
exec "$TEST_PYTHON" "$@"
"""


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True)


def _write_executable(path: Path, source: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    path.chmod(0o755)


def _clean_checkout_fixture(
    tmp_path: Path,
    *,
    verifier_mutator: Callable[[str], str] | None = None,
    fetch_source: str = _STUB_FETCH,
    provision_source: str = _STUB_PROVISION,
    ci_source: str = _STUB_CI,
    gitignore: str = _FIXTURE_GITIGNORE,
) -> Path:
    repo = tmp_path / "clean-repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    source_verifier = ROOT / "scripts" / "aio" / "verify-clean-checkout.sh"
    assert source_verifier.is_file(), "scripts/aio/verify-clean-checkout.sh is the missing producer"
    verifier_source = source_verifier.read_text(encoding="utf-8")
    if verifier_mutator is not None:
        verifier_source = verifier_mutator(verifier_source)
    _write_executable(repo / "scripts" / "aio" / "verify-clean-checkout.sh", verifier_source)
    _write_executable(repo / "scripts" / "aio" / "fetch-reference.sh", fetch_source)
    _write_executable(repo / "scripts" / "aio" / "aio-provision-cache.sh", provision_source)
    _write_executable(repo / "scripts" / "ci-local.sh", ci_source)
    (repo / "tools").mkdir()
    for name in ("__init__.py", "books.py"):
        shutil.copy2(ROOT / "tools" / name, repo / "tools" / name)
    (repo / "books.yaml").write_text(
        "books_version: 2\n"
        "books:\n"
        "  - {id: python-projects, number: 1, root: python-projects, depends_on: []}\n"
        "  - {id: aio-ml, number: 4, root: aio-ml, depends_on: [], content_model: aio,"
        " aio_round: 1}\n"
        "  - {id: aio-dl, number: 4, root: aio-dl, depends_on: [aio-ml], content_model: aio,"
        " aio_round: 2}\n",
        encoding="utf-8",
    )
    (repo / ".gitignore").write_text(gitignore, encoding="utf-8")
    for book in ("aio-ml", "aio-dl"):
        (repo / book / "reference").mkdir(parents=True)
        (repo / book / "reference" / ".gitkeep").write_text("", encoding="utf-8")
        (repo / book / "reference" / "analysis.md").write_text("# Analysis\n", encoding="utf-8")
    (repo / "python-projects" / "reference").mkdir(parents=True)
    (repo / "python-projects" / "reference" / "notes.md").write_text("py4kids\n", encoding="utf-8")
    tracked_sentinel = repo / "TRACKED_HEAD_SENTINEL"
    tracked_sentinel.write_text("committed bytes\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "clean checkout fixture")
    tracked_sentinel.write_text("dirty staged bytes\n", encoding="utf-8")
    _git(repo, "add", tracked_sentinel.name)
    (repo / "UNTRACKED_WORKTREE_SENTINEL").write_text(
        "must not enter the clone\n", encoding="utf-8"
    )
    return repo


def _run_clean_checkout(
    tmp_path: Path, repo: Path, **extra_env: str
) -> tuple[subprocess.CompletedProcess[str], list[str], Path]:
    parent = tmp_path / "shm"
    parent.mkdir(exist_ok=True)
    fake_bin = tmp_path / "fake-bin"
    _write_executable(fake_bin / "uv", _STUB_UV)
    trace = tmp_path / "trace.log"
    trace.write_text("", encoding="utf-8")
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("GIT_", "AIO_CLEAN_CHECKOUT_", "AIO_REFERENCE_SOURCE"))
    }
    env.update(
        {
            "PATH": f"{fake_bin}:{env['PATH']}",
            "TEST_PYTHON": sys.executable,
            "VERIFY_TRACE": str(trace),
            "AIO_CLEAN_CHECKOUT_PARENT": str(parent),
            **extra_env,
        }
    )
    proc = subprocess.run(
        ["bash", "scripts/aio/verify-clean-checkout.sh"],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc, trace.read_text(encoding="utf-8").splitlines(), parent


def _assert_complete_clean_checkout(
    proc: subprocess.CompletedProcess[str], lines: list[str], parent: Path
) -> None:
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert [line.split(":", 1)[0] for line in lines] == ["fetch", "provision", "ci"], lines
    clones = {line.split(":", 1)[1] for line in lines}
    assert len(clones) == 1, lines
    clone = Path(clones.pop())
    assert clone.parent == parent
    assert clone.name.startswith("aio-clean-checkout.")
    assert not clone.exists(), "the clone is removed unless AIO_CLEAN_CHECKOUT_KEEP=1"
    assert "3 provisioned file(s)" in proc.stdout
    assert "PASS verify-clean-checkout" in proc.stdout


def test_clean_checkout_verifier_clones_provisions_into_the_clone_and_runs_ci(
    tmp_path: Path,
) -> None:
    repo = _clean_checkout_fixture(tmp_path)

    proc, lines, parent = _run_clean_checkout(tmp_path, repo)

    _assert_complete_clean_checkout(proc, lines, parent)
    assert not any((repo / book / "reference" / "2026").exists() for book in ("aio-ml", "aio-dl"))


def test_clean_checkout_keep_leaves_a_clone_with_only_ignored_provisioned_files(
    tmp_path: Path,
) -> None:
    repo = _clean_checkout_fixture(tmp_path)

    proc, lines, _ = _run_clean_checkout(tmp_path, repo, AIO_CLEAN_CHECKOUT_KEEP="1")

    assert proc.returncode == 0, proc.stdout + proc.stderr
    clone = Path(lines[-1].split(":", 1)[1])
    status = subprocess.run(
        ["git", "-C", str(clone), "status", "--porcelain", "--ignored"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    assert sorted(line for line in status if "__pycache__" not in line) == [
        "!! aio-dl/reference/2026/",
        "!! aio-ml/reference/2026/",
        "!! aio-ml/reference/cache/",
    ]
    head = _git(clone, "rev-parse", "HEAD").stdout
    assert head == _git(repo, "rev-parse", "HEAD").stdout


def test_clean_checkout_reference_source_copies_each_aio_root_instead_of_fetching(
    tmp_path: Path,
) -> None:
    repo = _clean_checkout_fixture(tmp_path)
    source = tmp_path / "corpus"
    for book in ("aio-ml", "aio-dl"):
        paper = source / book / "reference" / "2026" / "paper.pdf"
        paper.parent.mkdir(parents=True)
        paper.write_text("%PDF-1.4 local corpus\n", encoding="utf-8")
    (source / "aio-ml" / "reference" / "r1-2026").mkdir()
    (source / "aio-ml" / "reference" / "r1-2026" / "index.yaml").write_text(
        "parts: []\n", encoding="utf-8"
    )
    stray = source / "python-projects" / "reference" / "stray.pdf"
    stray.parent.mkdir(parents=True)
    stray.write_text("not an aio root\n", encoding="utf-8")

    proc, lines, _ = _run_clean_checkout(
        tmp_path, repo, AIO_REFERENCE_SOURCE=str(source), AIO_CLEAN_CHECKOUT_KEEP="1"
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert [line.split(":", 1)[0] for line in lines] == ["provision", "ci"], lines
    clone = Path(lines[-1].split(":", 1)[1])
    assert (clone / "aio-ml/reference/r1-2026/index.yaml").is_file()
    assert (clone / "aio-dl/reference/2026/paper.pdf").read_text() == "%PDF-1.4 local corpus\n"
    assert not (clone / "python-projects/reference/stray.pdf").exists()
    assert "4 provisioned file(s)" in proc.stdout


def test_clean_checkout_reference_source_without_a_book_reference_fails_closed(
    tmp_path: Path,
) -> None:
    repo = _clean_checkout_fixture(tmp_path)
    source = tmp_path / "corpus"
    (source / "aio-ml" / "reference").mkdir(parents=True)

    proc, lines, _ = _run_clean_checkout(tmp_path, repo, AIO_REFERENCE_SOURCE=str(source))

    assert proc.returncode != 0
    assert "AIO_REFERENCE_SOURCE has no aio-dl/reference/" in proc.stderr
    assert not any(line.startswith("ci:") for line in lines)


def _comment_out(marker: str) -> Callable[[str], str]:
    def mutate(source: str) -> str:
        lines = source.splitlines(keepends=True)
        mutated = [
            f"# mutation removed: {line}"
            if marker in line and line.strip() and not line.lstrip().startswith("#")
            else line
            for line in lines
        ]
        assert mutated != lines, f"fixture could not locate {marker!r}"
        return "".join(mutated)

    return mutate


def _replace_with_worktree_copy_verifier(_source: str) -> str:
    return """#!/usr/bin/env bash
set -euo pipefail
export CLONE=$(mktemp -d "$AIO_CLEAN_CHECKOUT_PARENT/aio-clean-checkout.XXXXXX")
cp -a . "$CLONE"
bash "$CLONE/scripts/aio/fetch-reference.sh" --root "$CLONE" --all
bash "$CLONE/scripts/aio/aio-provision-cache.sh" --root "$CLONE"
(cd "$CLONE" && TMPDIR=/dev/shm bash scripts/ci-local.sh)
echo "3 provisioned file(s)"
echo "PASS verify-clean-checkout"
rm -rf "$CLONE"
"""


@pytest.mark.parametrize(
    ("fixture_kwargs", "message"),
    [
        pytest.param(
            {"verifier_mutator": _comment_out('bash -c "$ci_cmd"')},
            None,
            id="comment-only-verifier-skips-ci",
        ),
        pytest.param(
            {"verifier_mutator": _comment_out('fetch-reference.sh" --root')},
            None,
            id="verifier-skips-fetch",
        ),
        pytest.param(
            {"verifier_mutator": _comment_out('aio-provision-cache.sh" --root')},
            None,
            id="verifier-skips-provisioning",
        ),
        pytest.param(
            {"verifier_mutator": _replace_with_worktree_copy_verifier},
            None,
            id="worktree-copy-leaks-untracked-and-staged-sentinels",
        ),
        pytest.param(
            {"gitignore": "__pycache__/\naio-*/reference/2026/\n"},
            "provisioned file is not ignored: aio-ml/reference/cache/artifact.bin",
            id="provisioned-cache-not-ignored",
        ),
        pytest.param(
            {"provision_source": _STUB_PROVISION + "printf 'leak\\n' > \"$root/LEAK.txt\"\n"},
            "untracked-unignored",
            id="provisioning-leaks-an-unignored-file",
        ),
        pytest.param(
            {"ci_source": _STUB_CI + "printf 'edited\\n' >> TRACKED_HEAD_SENTINEL\n"},
            "tracked changes",
            id="ci-modifies-a-tracked-file",
        ),
        pytest.param(
            {"ci_source": _STUB_CI + "exit 7\n"},
            None,
            id="ci-failure-is-blocking",
        ),
    ],
)
def test_clean_checkout_adversarial_mutations_fail(
    tmp_path: Path, fixture_kwargs: dict[str, Any], message: str | None
) -> None:
    repo = _clean_checkout_fixture(tmp_path, **fixture_kwargs)

    proc, lines, parent = _run_clean_checkout(tmp_path, repo)

    with pytest.raises(AssertionError):
        _assert_complete_clean_checkout(proc, lines, parent)
    if message is not None:
        assert proc.returncode != 0
        assert message in proc.stdout + proc.stderr
