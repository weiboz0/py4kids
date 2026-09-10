"""Source-policy AST checker for Book 2 (Plan 036).

Mechanically enforces the always-banned, scanner-blind surface that ``concept-scan`` does not catch
and that has been reviewer-caught all through Book 2: chained comparison, list/str repetition,
ternary, ``global``/``nonlocal``, ``del``, augmented assign, comprehensions, banned imports/methods,
and builtins outside a pinned allowlist.  Scans executable reference code — ``lesson.ipynb`` +
``solutions.ipynb`` code cells and every ``assets/*.py`` (solvers + helpers).

BOOK-SCOPED to ``book2`` (returns ``[]`` otherwise — intentional no-op, same as the judge).
"""

from __future__ import annotations

import ast
import builtins as _builtins
from pathlib import Path

from tools.notebooks import _fail, code_cells, content_dirs, read_nb

# Precise, reject-by-default allowlist (audited against all current book2 content — the only
# builtins in use are abs/int/len/max/min/print/range/set/sorted/str/sum). `deque` is imported,
# not a builtin, so it is never flagged by the builtin check.
ALLOWED_BUILTINS = {
    "len", "min", "max", "sorted", "sum", "abs", "round",  # the free set
    "input", "print", "range",                              # stdin + iteration
    "int", "str",                                           # type conversion
    "set",                                                  # set-literal / set-ops constructor
}
PY_BUILTINS = frozenset(dir(_builtins))
BANNED_METHODS = {"pop", "join", "index", "count", "find"}


class _DefinedNames(ast.NodeVisitor):
    """Collect names defined/imported/bound in a module, to exempt them from the builtin check."""

    def __init__(self) -> None:
        self.names: set[str] = set()

    def visit_FunctionDef(self, node):
        self.names.add(node.name)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.names.add(node.name)
        self.generic_visit(node)

    def visit_arg(self, node):
        self.names.add(node.arg)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.names.add(node.id)

    def visit_Import(self, node):
        for alias in node.names:
            self.names.add(alias.asname or alias.name.split(".")[0])

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.names.add(alias.asname or alias.name)


def _check_source(source: str, scope: str, where: str) -> list[str]:
    findings: list[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [_fail(scope, f"{where}: does not parse ({exc.msg})")]
    defined = _DefinedNames()
    defined.visit(tree)

    def report(node, ban: str) -> None:
        findings.append(_fail(scope, f"{where}:{getattr(node, 'lineno', '?')}: banned {ban}"))

    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and len(node.ops) > 1:
            report(node, "chained comparison")
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            for operand in (node.left, node.right):
                if isinstance(operand, ast.List) or (
                    isinstance(operand, ast.Constant) and isinstance(operand.value, str)
                ):
                    report(node, "list/str repetition")
                    break
        elif isinstance(node, ast.IfExp):
            report(node, "ternary (if-expression)")
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            report(node, "global/nonlocal")
        elif isinstance(node, ast.Delete):
            report(node, "del")
        elif isinstance(node, ast.AugAssign):
            report(node, "augmented assignment (e.g. +=)")
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            report(node, "comprehension")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] == "itertools":
                    report(node, "import itertools")
        elif isinstance(node, ast.ImportFrom):
            if node.module == "itertools":
                report(node, "import from itertools")
            if node.module == "collections":
                for alias in node.names:
                    if alias.name == "Counter":
                        report(node, "import collections.Counter")
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in BANNED_METHODS:
                report(node, f".{func.attr}()")
            elif (
                isinstance(func, ast.Name)
                and func.id in PY_BUILTINS
                and func.id not in ALLOWED_BUILTINS
                and func.id not in defined.names
            ):
                report(node, f"builtin {func.id}()")
    return findings


def source_policy_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    if book != "book2":
        return []  # intentional no-op outside book2 (see module docstring)
    entries, findings = content_dirs(root, book, unit)
    if findings:
        return findings
    for entry_dir, _kind in entries:
        scope = entry_dir.name
        for nb_name in ("lesson.ipynb", "solutions.ipynb"):
            path = entry_dir / nb_name
            if path.is_file():
                for idx, cell in enumerate(code_cells(read_nb(path))):
                    findings.extend(_check_source(cell.source, scope, f"{nb_name}[cell {idx}]"))
        assets = entry_dir / "assets"
        if assets.is_dir():
            for script in sorted(assets.glob("*.py")):
                findings.extend(
                    _check_source(script.read_text(encoding="utf-8"), scope, f"assets/{script.name}")
                )
    return findings
