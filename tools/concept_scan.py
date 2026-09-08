"""Blocking, book-level concept-usage completeness check.

Parses every notebook (and .py asset) code cell with AST, detects which
registered concepts are USED with high confidence, and reports any that are
used but absent from that entry's introduces u requires u practices union.

Precision over recall: only report concepts we can detect confidently, so a
finding is (almost) always a real used-but-unlisted gap. Inherently-manual or
fuzzy concepts are never reported as violations (see MANUAL_ONLY). This makes
the check necessary, not sufficient: error-messages, run-program, comment,
naming, scope, loop-counter, type-conversion, int-type, boolean, and the other
MANUAL_ONLY concepts remain reviewer-enforced.

A string ``Constant`` inside a ``JoinedStr`` counts as ``string-literal``. Thus
the literal text in an f-string records both ``f-string`` and ``string-literal``.

Each scan builds a fresh per-book profile. Book 1 retains the original method,
builtin, and manual-only literals; dependent books extend that profile only for
features and techniques present in their own registry.
"""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path

import yaml

from tools.books import book_path, dependency_baseline

# Concepts we do NOT flag as violations: not detectable from code, or too fuzzy
# to assert confidently. These stay reviewer-manual.
MANUAL_ONLY = {
    "run-program", "comment", "error-messages", "naming", "scope",
    "loop-counter", "type-conversion",  # accumulator now DETECTED (removed from MANUAL_ONLY)
    "boolean",  # detectable partially; too many false negatives to assert absence
    "list-index", "dict-access",  # subscript ambiguity vs string-index
    "string-index",               # subscript-index ambiguity vs list/dict
    "list-loop",                  # for-over-collection: type unknown
    "int-type",                   # bare int constants are everywhere; low signal
    "variable", "print",          # ubiquitous; still detected, low value
}

# Methods TAUGHT by book 1 (by the concept that teaches them). A method call whose
# name is not here maps to NO concept id and would slip the closure check silently
# (this is how `.index` nearly leaked into unit-06). Flag any other method call.
TAUGHT_METHODS = {
    "upper", "lower", "strip", "replace",   # string-methods (the taught subset ONLY)
    "append", "sort",                        # lists (unit-07 introduces)
    "items", "keys", "values", "get",        # dicts (unit-08 introduces)
    "read", "readlines", "readline", "write", "close",  # files (unit-09)
    "seed", "randint", "choice",             # random-module
    # turtle methods live in .py assets; add the ones the course uses:
    "forward", "backward", "left", "right", "penup", "pendown", "color",
    "pencolor", "fillcolor", "begin_fill", "end_fill", "goto", "setheading",
    "circle", "dot", "stamp", "speed", "done", "hideturtle", "shape", "bgcolor",
    "width", "pensize", "setup", "title", "exitonclick", "up", "down",
}
STRING_METHODS = {"upper", "lower", "strip", "replace"}  # the TAUGHT subset only
BUILTINS = {"len", "min", "max", "sorted", "sum", "abs", "round"}
DICT_METHODS = {"items", "keys", "values", "get"}


@dataclass(frozen=True)
class ScanProfile:
    taught_methods: frozenset[str]
    builtins: frozenset[str]
    never_flag: frozenset[str]


def scanner_profile(concepts: list[dict]) -> ScanProfile:
    """Build a new immutable profile from one book's own concept registry."""
    registered = {
        concept.get("id")
        for concept in concepts
        if isinstance(concept, dict) and isinstance(concept.get("id"), str)
    }
    techniques = {
        concept["id"]
        for concept in concepts
        if isinstance(concept, dict)
        and concept.get("kind") == "technique"
        and isinstance(concept.get("id"), str)
    }
    taught_methods = set(TAUGHT_METHODS)
    if "str-split" in registered:
        taught_methods.add("split")
    if "set-ops" in registered:
        taught_methods.update({"add", "discard", "remove"})
    if "deque" in registered:
        taught_methods.update({"appendleft", "popleft"})
    return ScanProfile(
        taught_methods=frozenset(taught_methods),
        builtins=frozenset(BUILTINS),
        never_flag=frozenset(set(MANUAL_ONLY) | techniques),
    )


def detect(
    tree: ast.AST,
    *,
    registered_concepts: set[str] | None = None,
    profile: ScanProfile | None = None,
) -> tuple[set[str], set[str]]:
    """Return (concept ids used, unknown method names) — high-confidence only."""
    registered = set() if registered_concepts is None else set(registered_concepts)
    active_profile = profile or scanner_profile([])
    used: set[str] = set()
    unknown_methods: set[str] = set()
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    set_names = {
        target.id
        for node in ast.walk(tree)
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        for target in (
            node.targets if isinstance(node, ast.Assign) else [node.target]
        )
        if isinstance(target, ast.Name)
        and (
            isinstance(node.value, ast.Set)
            or (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "set"
            )
        )
    }

    def add_feature(concept: str) -> None:
        if concept in registered:
            used.add(concept)

    def is_set_expression(node: ast.AST) -> bool:
        return isinstance(node, ast.Set) or (
            isinstance(node, ast.Name) and node.id in set_names
        )

    class V(ast.NodeVisitor):
        def __init__(self):
            self.loop_depth = 0

        def _enter_loop(self, node):
            if self.loop_depth >= 1:
                used.add("nested-loops")
            self.loop_depth += 1
            self.generic_visit(node)
            self.loop_depth -= 1

        def visit_Assert(self, node):
            pass  # asserts are exempt CI scaffolding, not taught concepts

        def visit_For(self, node):
            used.add("for-loop")
            self._enter_loop(node)

        def visit_While(self, node):
            used.add("while-loop")
            self._enter_loop(node)

        def visit_If(self, node):
            used.add("if-statement")
            if node.orelse:
                used.add("elif-else")
            self.generic_visit(node)

        def visit_Break(self, node):
            used.add("break-statement")

        def visit_Compare(self, node):
            for op in node.ops:
                if isinstance(op, (ast.In, ast.NotIn)):
                    used.add("in-operator")
                elif isinstance(op, (ast.Lt, ast.Gt, ast.LtE, ast.GtE, ast.Eq, ast.NotEq)):
                    used.add("comparison")
            self.generic_visit(node)

        def visit_BoolOp(self, node):
            used.add("logical-ops")
            self.generic_visit(node)

        def visit_UnaryOp(self, node):
            if isinstance(node.op, ast.Not):
                used.add("logical-ops")
            if isinstance(node.op, ast.Invert):
                add_feature("bitwise-ops")
            self.generic_visit(node)

        def visit_BinOp(self, node):
            def has_str(n):
                # true if a chain of +/* BinOps bottoms out in any str/JoinedStr leaf
                if (isinstance(n, ast.Constant) and isinstance(n.value, str)) \
                        or isinstance(n, ast.JoinedStr):
                    return True
                if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Mult)):
                    return has_str(n.left) or has_str(n.right)
                return False
            if isinstance(node.op, ast.Sub) and (
                is_set_expression(node.left) or is_set_expression(node.right)
            ):
                add_feature("set-ops")
            if isinstance(node.op, (ast.BitAnd, ast.BitOr, ast.BitXor, ast.LShift, ast.RShift)):
                add_feature("bitwise-ops")
                if isinstance(node.op, (ast.BitAnd, ast.BitOr, ast.BitXor)) and (
                    is_set_expression(node.left) or is_set_expression(node.right)
                ):
                    add_feature("set-ops")
            elif isinstance(node.op, (ast.Add, ast.Mult)) and (
                has_str(node.left) or has_str(node.right)
            ):
                used.add("string-concat")  # str +/* is concat/repeat, not arithmetic
            elif isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div,
                                      ast.FloorDiv, ast.Mod, ast.Pow)):
                used.add("arithmetic")
            self.generic_visit(node)

        def visit_Assign(self, node):
            # accumulator = read-modify-write: the target also appears in the value
            def base_name(t):
                if isinstance(t, ast.Name):
                    return t.id
                if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name):
                    return t.value.id
                if isinstance(t, ast.Attribute):
                    return ast.unparse(t)  # e.g. "self.health" — attribute accumulators
                return None
            targets = {base_name(t) for t in node.targets}
            targets.discard(None)
            if targets:
                # collect both Name ids and full attribute dotted-paths appearing in the value
                names_in_value = {n.id for n in ast.walk(node.value) if isinstance(n, ast.Name)}
                names_in_value |= {ast.unparse(n) for n in ast.walk(node.value)
                                   if isinstance(n, ast.Attribute)}
                if targets & names_in_value:
                    used.add("accumulator")
            self.generic_visit(node)

        def visit_AugAssign(self, node):
            used.add("accumulator")  # x += ... is the accumulator pattern
            if isinstance(node.op, (ast.Add, ast.Mult)) and (
                    (isinstance(node.value, ast.Constant) and isinstance(node.value.value, str))
                    or isinstance(node.value, ast.JoinedStr)):
                used.add("string-concat")
            else:
                used.add("arithmetic")
            self.generic_visit(node)

        def visit_JoinedStr(self, node):
            used.add("f-string")
            self.generic_visit(node)

        def visit_Constant(self, node):
            if isinstance(node.value, str):
                used.add("string-literal")
            elif isinstance(node.value, bool):
                used.add("boolean")
            elif isinstance(node.value, float):
                used.add("float-type")
            self.generic_visit(node)

        def visit_List(self, node):
            used.add("list-literal")
            self.generic_visit(node)

        def visit_Dict(self, node):
            used.add("dict-literal")
            self.generic_visit(node)

        def visit_Set(self, node):
            add_feature("set-literal")
            self.generic_visit(node)

        def visit_Tuple(self, node):
            add_feature("tuple")
            self.generic_visit(node)

        def visit_ListComp(self, node):
            add_feature("comprehension")
            self.generic_visit(node)

        def visit_SetComp(self, node):
            add_feature("comprehension")
            self.generic_visit(node)

        def visit_DictComp(self, node):
            add_feature("comprehension")
            self.generic_visit(node)

        def visit_GeneratorExp(self, node):
            add_feature("comprehension")
            self.generic_visit(node)

        def visit_Subscript(self, node):
            if isinstance(node.slice, ast.Slice):
                used.add("string-slice")  # also covers list slice; rare either way
            self.generic_visit(node)

        def visit_Import(self, node):
            used.add("import-statement")
            for n in node.names:
                if n.name == "random":
                    used.add("random-module")
                if n.name.startswith("turtle"):
                    used.add("turtle-basics")
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            used.add("import-statement")
            if node.module == "random":
                used.add("random-module")
            self.generic_visit(node)

        def visit_With(self, node):
            used.add("with-statement")
            self.generic_visit(node)

        def visit_ClassDef(self, node):
            used.add("class-def")
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    used.add("methods")
                    if item.name == "__init__":
                        used.add("init-method")
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            is_method = isinstance(parents.get(node), ast.ClassDef)
            if not is_method:
                used.add("def-function")
            has_parameters = node.args.args or node.args.kwonlyargs or node.args.vararg
            is_self_only_method = (
                is_method
                and node.args.args
                and node.args.args[0].arg == "self"
                and len(node.args.args) == 1
            )
            if has_parameters and not is_self_only_method:
                used.add("parameters")
            if any(
                isinstance(descendant, ast.Call)
                and isinstance(descendant.func, ast.Name)
                and descendant.func.id == node.name
                for descendant in ast.walk(node)
            ):
                add_feature("recursion")
            self.generic_visit(node)

        def visit_Return(self, node):
            if node.value is not None:
                used.add("return-value")
            self.generic_visit(node)

        def visit_Attribute(self, node):
            if node.attr in STRING_METHODS:
                used.add("string-methods")
            if node.attr == "append":
                used.add("list-append")
            if node.attr == "sort":
                used.add("list-sort")
            if node.attr in DICT_METHODS:
                used.add("dict-loop") if node.attr in {"items", "keys", "values"} else None
            if isinstance(node.value, ast.Name) and node.value.id == "self":
                used.add("attributes")
            if node.attr in ("read", "readlines", "readline"):
                used.add("file-read")
            if node.attr == "write":
                used.add("file-write")
            if node.attr == "split":
                add_feature("str-split")
            if (
                node.attr in {"add", "discard", "remove"}
                and isinstance(node.value, ast.Name)
                and node.value.id in set_names
            ):
                add_feature("set-ops")
            if node.attr in {"appendleft", "popleft"}:
                add_feature("deque")
            self.generic_visit(node)

        def visit_Name(self, node):
            if node.id == "deque":
                add_feature("deque")

        def visit_Call(self, node):
            f = node.func
            if isinstance(f, ast.Attribute):
                # a method call x.name(...) — flag names that map to no taught concept
                recv = f.value
                recv_is_self = isinstance(recv, ast.Name) and recv.id == "self"
                if (f.attr not in active_profile.taught_methods
                        and not f.attr.startswith("__")
                        and not recv_is_self):  # own object methods are fine
                    unknown_methods.add(f.attr)
            if isinstance(f, ast.Name):
                if f.id == "print":
                    used.add("print")
                elif f.id == "input":
                    used.add("input")
                elif f.id == "range":
                    used.add("range-function")
                elif f.id in ("int", "str", "float"):
                    used.add("type-conversion")
                elif f.id == "sorted":
                    used.add("builtin-functions"); used.add("list-sort")
                    if any(keyword.arg == "key" for keyword in node.keywords):
                        add_feature("sorted-key")
                elif f.id in active_profile.builtins:
                    used.add("builtin-functions")
                elif f.id == "open":
                    used.add("with-statement")
                    for kw in node.args[1:2]:
                        if isinstance(kw, ast.Constant) and isinstance(kw.value, str):
                            if "w" in kw.value or "a" in kw.value:
                                used.add("file-write")
                            if "r" in kw.value:
                                used.add("file-read")
            self.generic_visit(node)

    V().visit(tree)
    return used, unknown_methods


def code_sources(nb_path: Path):
    nb = json.loads(nb_path.read_text())
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            src = cell.get("source", [])
            yield "".join(src) if isinstance(src, list) else src


def entry_notebooks(entry_dir: Path, kind: str):
    if kind == "unit":
        names = ["lesson.ipynb", "exercises.ipynb", "solutions.ipynb"]
    elif kind == "checkpoint":
        names = ["checkpoint.ipynb", "solutions.ipynb"]
    else:
        names = ["brief.ipynb", "solutions.ipynb"]
    for n in names:
        p = entry_dir / n
        if p.exists():
            yield p
    assets = entry_dir / "assets"
    if assets.exists():
        yield from assets.glob("*.py")


def concept_scan_findings(
    root: Path, book: str, unit: str | None = None
) -> list[str]:
    """Return high-confidence used-but-unlisted findings for every book entry."""
    del unit
    book_dir = book_path(root, book)
    map_path = book_dir / "curriculum" / "coverage-map.yaml"
    if not map_path.is_file():
        return [f"FAIL: {book}: coverage-map.yaml does not exist"]
    cmap = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    if not isinstance(cmap, dict) or not isinstance(cmap.get("entries"), list):
        return [f"FAIL: {book}: coverage-map entries must be a list"]
    concepts_path = book_dir / "curriculum" / "concepts.yaml"
    concepts_data = (
        yaml.safe_load(concepts_path.read_text(encoding="utf-8"))
        if concepts_path.is_file()
        else {}
    )
    concepts = concepts_data.get("concepts", []) if isinstance(concepts_data, dict) else []
    registered = {
        concept["id"]
        for concept in concepts
        if isinstance(concept, dict) and isinstance(concept.get("id"), str)
    }
    profile = scanner_profile(concepts)
    baseline = dependency_baseline(root, book)
    dirs = {
        "unit": book_dir / "units",
        "checkpoint": book_dir / "checkpoints",
        "project": book_dir / "projects",
    }
    findings: list[str] = []
    for entry in cmap["entries"]:
        kind = entry["kind"]
        eid = entry["id"]
        edir = dirs[kind] / eid
        if not edir.exists():
            continue
        union = (
            set(entry.get("introduces", []) or [])
            | set(entry.get("requires", []) or [])
            | set(entry.get("practices", []) or [])
            | baseline
        )
        used = set()
        methods = set()
        defined_names = set()  # functions + class methods defined in this entry's notebooks
        for nb in entry_notebooks(edir, kind):
            for src in (code_sources(nb) if nb.suffix == ".ipynb" else [nb.read_text()]):
                try:
                    tree = ast.parse(src)
                except SyntaxError:
                    continue
                u, m = detect(tree, registered_concepts=registered, profile=profile)
                used |= u
                methods |= m
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        defined_names.add(node.name)  # incl. class methods (feed/play/status)
        # a call to a method the notebooks define themselves is NOT an untaught library method
        methods -= defined_names
        gaps = sorted((used - union) - profile.never_flag)
        findings.extend(
            f"FAIL: {eid}: used-but-unlisted concept {concept}" for concept in gaps
        )
        findings.extend(
            f"FAIL: {eid}: untaught method {method}" for method in sorted(methods)
        )
    return findings
