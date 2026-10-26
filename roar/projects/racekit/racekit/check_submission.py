"""``check_submission``: prove a submission file has the official shape and runs (design 013 §4.1).

``python -m racekit.check_submission path/to/submission.py`` (exit status 0 on success, 1 on failure).

It proves exactly the following, and nothing more:

1. the file parses as **Python 3.8** (``ast.parse(..., feature_version=(3, 8))``) and an AST deny-list
   finds no 3.9+ runtime API: ``str.removeprefix`` / ``removesuffix``, ``functools.cache``,
   ``math.lcm``, ``itertools.pairwise``, ``int.bit_count``, ``zip(..., strict=)``, ``dict | dict``
   and ``|=`` on dicts, ``np.trapezoid``, runtime ``X | Y`` types and builtin-generic subscripts
   (``list[int]``); ``X | Y`` and builtin generics are also refused in **annotation positions**,
   which ``from __future__ import annotations`` would hide from a 3.8 run;
2. its imports are ``numpy``, ``roar_py_interface`` or a Python 3.8 standard-library module (the
   committed list ``racekit/contract/py38_stdlib.txt``); it defines ``RoarCompetitionSolution``
   with the official constructor, and ``initialize`` and ``step`` as ``async def``;
3. it completes a racekit race on ``test-circuit`` with no exception and no action-validation
   error, and with ``step()`` compute p99 ≤ 5 ms after 50 warm-up ticks.

It does not prove performance on the official simulator.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Set, Union

from .roar_py_interface import ActionValidationError
from .runner import (
    CONSTRUCTOR_PARAMS,
    DEFAULT_LAPS,
    DEFAULT_MAX_SECONDS,
    SOLUTION_CLASS,
    RaceResult,
    run_race,
)

STEP_P99_BUDGET_MS = 5.0
WARMUP_TICKS = 50
CHECK_TRACK = "test-circuit"
ALLOWED_THIRD_PARTY = frozenset({"numpy", "roar_py_interface"})
STDLIB_LIST = Path(__file__).resolve().parent / "contract" / "py38_stdlib.txt"

BUILTIN_GENERICS = frozenset({"list", "dict", "set", "frozenset", "tuple", "type"})
BUILTIN_TYPES = frozenset(
    {"int", "float", "complex", "str", "bytes", "bool", "list", "dict", "set", "frozenset", "tuple", "type"}
)
DENIED_ATTRIBUTES = {
    "removeprefix": "str.removeprefix is Python 3.9+",
    "removesuffix": "str.removesuffix is Python 3.9+",
    "bit_count": "int.bit_count is Python 3.10+",
    "trapezoid": "np.trapezoid needs numpy 2.0 (use np.trapz on numpy < 1.25)",
}
DENIED_MODULE_NAMES = {
    ("functools", "cache"): "functools.cache is Python 3.9+",
    ("math", "lcm"): "math.lcm is Python 3.9+",
    ("itertools", "pairwise"): "itertools.pairwise is Python 3.10+",
}


def py38_stdlib() -> FrozenSet[str]:
    """The committed, exhaustive Python 3.8 standard-library top-level module names."""
    lines = STDLIB_LIST.read_text(encoding="utf-8").splitlines()
    return frozenset(line.strip() for line in lines if line.strip() and not line.startswith("#"))


def _is_dict_expr(node: ast.AST) -> bool:
    if isinstance(node, (ast.Dict, ast.DictComp)):
        return True
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "dict"


def _is_runtime_type(node: ast.AST) -> bool:
    if isinstance(node, ast.Name) and node.id in BUILTIN_TYPES:
        return True
    if isinstance(node, ast.Constant) and node.value is None:
        return True
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return _is_runtime_type(node.left) and _is_runtime_type(node.right)
    return False


def _annotation_findings(annotation: Optional[ast.AST], line: int) -> List[str]:
    if annotation is None:
        return []
    if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
        try:
            annotation = ast.parse(annotation.value, mode="eval").body
        except SyntaxError:
            return []
    found = []
    for node in ast.walk(annotation):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            found.append(f"line {line}: an `X | Y` annotation is Python 3.10+ (use typing.Union/Optional)")
        elif isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id in BUILTIN_GENERICS:
            found.append(
                f"line {line}: `{node.value.id}[...]` in an annotation is Python 3.9+ (use typing.List etc.)"
            )
    return found


def deny_list_findings(tree: ast.AST) -> List[str]:
    """Every 3.9+ runtime API and annotation form in ``tree`` (design 013 §4.1)."""
    findings: List[str] = []
    aliases: Dict[str, str] = {}  # local name -> module, for `import functools as ft`
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                aliases[alias.asname or alias.name.split(".")[0]] = alias.name
    annotation_ids: Set[int] = set()
    for node in ast.walk(tree):
        line = getattr(node, "lineno", 0)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            arguments = node.args
            every = arguments.posonlyargs + arguments.args + arguments.kwonlyargs
            every += [arg for arg in (arguments.vararg, arguments.kwarg) if arg is not None]
            for arg in every:
                findings += _annotation_findings(arg.annotation, arg.lineno)
                if arg.annotation is not None:
                    annotation_ids.update(id(sub) for sub in ast.walk(arg.annotation))
            findings += _annotation_findings(node.returns, line)
            if node.returns is not None:
                annotation_ids.update(id(sub) for sub in ast.walk(node.returns))
        elif isinstance(node, ast.AnnAssign):
            findings += _annotation_findings(node.annotation, line)
            annotation_ids.update(id(sub) for sub in ast.walk(node.annotation))
    for node in ast.walk(tree):
        line = getattr(node, "lineno", 0)
        if isinstance(node, ast.Attribute):
            if node.attr in DENIED_ATTRIBUTES:
                findings.append(f"line {line}: {DENIED_ATTRIBUTES[node.attr]}")
            elif isinstance(node.value, ast.Name):
                module = aliases.get(node.value.id, node.value.id)
                reason = DENIED_MODULE_NAMES.get((module, node.attr))
                if reason:
                    findings.append(f"line {line}: {reason}")
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                reason = DENIED_MODULE_NAMES.get((node.module, alias.name))
                if reason:
                    findings.append(f"line {line}: {reason}")
                if alias.name in DENIED_ATTRIBUTES and node.module in ("numpy", "np"):
                    findings.append(f"line {line}: {DENIED_ATTRIBUTES[alias.name]}")
        elif isinstance(node, ast.Call):
            is_zip = isinstance(node.func, ast.Name) and node.func.id == "zip"
            if is_zip and any(keyword.arg == "strict" for keyword in node.keywords):
                findings.append(f"line {line}: zip(..., strict=) is Python 3.10+")
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            if id(node) in annotation_ids:
                continue
            if _is_dict_expr(node.left) or _is_dict_expr(node.right):
                findings.append(f"line {line}: `dict | dict` is Python 3.9+ (use {{**a, **b}})")
            elif _is_runtime_type(node):
                findings.append(f"line {line}: a runtime `X | Y` type is Python 3.10+ (use a tuple)")
        elif isinstance(node, ast.AugAssign) and isinstance(node.op, ast.BitOr):
            if _is_dict_expr(node.value):
                findings.append(f"line {line}: `|=` on a dict is Python 3.9+ (use dict.update)")
        elif (
            isinstance(node, ast.Subscript)
            and id(node) not in annotation_ids
            and isinstance(node.value, ast.Name)
            and node.value.id in BUILTIN_GENERICS
        ):
            findings.append(f"line {line}: `{node.value.id}[...]` at runtime is Python 3.9+")
    return sorted(set(findings), key=lambda text: (int(text.split()[1].rstrip(":")), text))


def import_findings(tree: ast.AST, stdlib: Optional[FrozenSet[str]] = None) -> List[str]:
    """Imports outside numpy, roar_py_interface and the Python 3.8 standard library."""
    allowed = ALLOWED_THIRD_PARTY | (py38_stdlib() if stdlib is None else stdlib)
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                findings.append(f"line {node.lineno}: a relative import cannot work in a single submission file")
                continue
            names = [node.module or ""]
        else:
            continue
        for name in names:
            top = name.split(".")[0]
            if top not in allowed:
                findings.append(
                    f"line {node.lineno}: import {name!r} is not allowed "
                    "(only the standard library, numpy and roar_py_interface)"
                )
    return findings


def shape_findings(tree: ast.Module) -> List[str]:
    """The official class, its constructor signature, and async initialize/step."""
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == SOLUTION_CLASS]
    if not classes:
        return [f"no top-level class {SOLUTION_CLASS}"]
    body = {node.name: node for node in classes[-1].body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    findings = []
    init = body.get("__init__")
    expected = ["self", *CONSTRUCTOR_PARAMS]
    if init is None:
        findings.append(f"{SOLUTION_CLASS} has no __init__")
    else:
        params = [arg.arg for arg in init.args.posonlyargs + init.args.args]
        extra = init.args.vararg or init.args.kwarg or init.args.kwonlyargs
        if params != expected or extra:
            findings.append(f"{SOLUTION_CLASS}.__init__ must take ({', '.join(expected)}); it takes ({', '.join(params)})")
    for name in ("initialize", "step"):
        method = body.get(name)
        if method is None:
            findings.append(f"{SOLUTION_CLASS} has no {name}() method")
        elif not isinstance(method, ast.AsyncFunctionDef):
            findings.append(f"{SOLUTION_CLASS}.{name} must be `async def`")
    return findings


class SubmissionReport:
    """The structured result of ``check_submission``."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.stages: Dict[str, List[str]] = {"parse": [], "shape": [], "race": []}
        self.skipped: List[str] = []
        self.race: Optional[RaceResult] = None
        self.step_p99_ms: Optional[float] = None

    @property
    def findings(self) -> List[str]:
        return [f"{stage}: {text}" for stage, texts in self.stages.items() for text in texts]

    @property
    def ok(self) -> bool:
        return not self.findings and not self.skipped

    def __str__(self) -> str:
        lines = [f"check_submission {self.path}: {'PASS' if self.ok else 'FAIL'}"]
        lines += [f"  FAIL {finding}" for finding in self.findings]
        lines += [f"  SKIP {stage} (an earlier stage failed)" for stage in self.skipped]
        if self.race is not None:
            lines.append(
                f"  race: {self.race!r}; step() p99 {self.step_p99_ms:.3f} ms "
                f"(budget {STEP_P99_BUDGET_MS} ms, {WARMUP_TICKS} warm-up ticks excluded)"
            )
        return "\n".join(lines)


def check_submission(
    path: Union[str, Path],
    track: str = CHECK_TRACK,
    laps: int = DEFAULT_LAPS,
    max_seconds: float = DEFAULT_MAX_SECONDS,
) -> SubmissionReport:
    """Run the three stages on ``path`` and return a ``SubmissionReport``."""
    path = Path(path)
    report = SubmissionReport(path)
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path), feature_version=(3, 8))
    except SyntaxError as error:
        report.stages["parse"].append(f"not valid Python 3.8: {error.msg} (line {error.lineno})")
        report.skipped += ["shape", "race"]
        return report
    report.stages["parse"] += deny_list_findings(tree)
    report.stages["shape"] += import_findings(tree) + shape_findings(tree)
    if report.findings:
        report.skipped.append("race")
        return report
    try:
        result = run_race(path, track, laps=laps, max_seconds=max_seconds)
    except ActionValidationError as error:
        report.stages["race"].append(f"invalid action: {error}")
        return report
    except Exception as error:  # noqa: BLE001 - any exception from the submission is a finding
        report.stages["race"].append(f"the race raised {type(error).__name__}: {error}")
        return report
    report.race = result
    report.step_p99_ms = result.step_ms_p99(WARMUP_TICKS)
    if report.step_p99_ms > STEP_P99_BUDGET_MS:
        report.stages["race"].append(
            f"step() p99 {report.step_p99_ms:.2f} ms exceeds the {STEP_P99_BUDGET_MS} ms budget"
        )
    return report


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m racekit.check_submission", description=__doc__.splitlines()[0])
    parser.add_argument("submission", type=Path)
    parser.add_argument("--track", default=CHECK_TRACK)
    parser.add_argument("--laps", type=int, default=DEFAULT_LAPS)
    parser.add_argument("--max-seconds", type=float, default=DEFAULT_MAX_SECONDS)
    args = parser.parse_args(argv)
    import numpy

    version = ".".join(str(part) for part in sys.version_info[:3])
    print(f"racekit.check_submission: python={version} numpy={numpy.__version__}")
    report = check_submission(args.submission, args.track, args.laps, args.max_seconds)
    print(report)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
