"""The answer model: the ONLY module of the site export that reads solution material (design 012 D5).

Everything a solution notebook, a solution asset, a judge solver or an `assets/verify/**` helper holds
is read here and nowhere else in `tools/export/`. What leaves this module is:

- check data (`check_data`): a salted hash of a canonical text, the top-level asserts
  (`ast.unparse`, never a function body), fixture paths, or a requirements checklist taken from the
  statement;
- `answer_fields`: `after-attempt` plus the Student Book appendix text for odd unit exercises only,
  read through `tools.publish.student_answer_text` (so through `student_answer_sources`);
- concept ids (`solution_concepts`), never code;
- for the answer-model checks (plan 101 Phase F) only, the hidden corpora as data
  (`solution_code_cells`, `solution_asset_files`, `solution_markdown_paragraphs`, `canonical_texts`,
  `released_answers`, `shipped_asserts`, `check_texts`), which are never written into a bundle.

Programs run in a temporary copy of the entry's git-tracked files, with stdin from `/dev/null`,
`PYTHONHASHSEED=0` (1 on the expected-output rule's second run) and a timeout, so a run never
touches the repo tree or reads untracked scratch.
"""

from __future__ import annotations

import ast
import builtins
import functools
import hashlib
import re
import resource
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import nbformat

from tools.books import book_flag, book_path, publication_config, site_config
from tools.fake_turtle import imports_turtle
from tools.judge import ANSWER_LINE, JUDGE_TIMEOUT_S, REPO_ROOT, _fixture_pairs, outputs_match
from tools.publish import (
    ITEM,
    SOLUTION_SOURCE,
    VERIFY_TAG,
    challenge_solution_assets,
    entries,
    fenced_paragraphs,
    is_solution_source,
    item_groups,
    project_sections,
    solution_assets,
    student_answer_sources,
    student_answer_text,
    unit_challenges,
)
from tools.turtle_figure import turtle_segments
from tools.turtle_real import real_programs

from .normalise import WHITESPACE_MODES, answer_hash, normalise
from .probe import sandbox_env
from .timing import TimingCache

if TYPE_CHECKING:  # pragma: no cover
    from .items import Item

RUN_TIMEOUT_S = 20
SOLUTION_PREFIX = {"unit": "ex", "checkpoint": "q", "project": "p"}
BUILTINS = frozenset(dir(builtins))
SAMPLE_INPUT = re.compile(r"^#{2,6} Sample Input\b.*$", re.MULTILINE)
ANY_HEADING = re.compile(r"^#{1,6} ", re.MULTILINE)
FENCE = re.compile(r"^[ \t]*```[^\n]*\n(.*?)^[ \t]*```", re.MULTILINE | re.DOTALL)
INLINE_CODE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
IDENTIFIER = re.compile(r"[A-Za-z_]\w*")
NUMBER = re.compile(r"[-+−]?\d+(?:\.\d+)?")
LETTER = re.compile(r"[^\W\d_]")


# --- running programs ------------------------------------------------------------------------


@dataclass(frozen=True)
class RunResult:
    """One sandboxed run: `status` is `ok`, `error` or `timeout`."""

    status: str
    stdout: str
    stderr: str


@functools.cache
def tracked_paths(directory: Path) -> tuple[str, ...]:
    """The git-tracked files under `directory`, relative to it, sorted (never untracked scratch)."""
    result = subprocess.run(["git", "-C", str(directory), "ls-files", "-z", "--", "."],
                            capture_output=True, check=False)
    if result.returncode != 0:
        return ()
    names = [name for name in result.stdout.decode("utf-8").split("\0") if name]
    return tuple(sorted(name for name in names if (Path(directory) / name).is_file()))


def _run_once(entry_dir: Path, source: str, timeout_s: float, hash_seed: int = 0) -> RunResult:
    env = sandbox_env()
    env["PYTHONHASHSEED"] = str(hash_seed)
    with tempfile.TemporaryDirectory(prefix="py4kids-site-run-") as tmp:
        work = Path(tmp) / Path(entry_dir).name
        work.mkdir()
        for name in tracked_paths(Path(entry_dir)):
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(Path(entry_dir) / name, target)
        script = Path(tmp) / "_site_run.py"
        script.write_text(source, encoding="utf-8")
        try:
            result = subprocess.run([sys.executable, str(script)], cwd=work, env=env,
                                    stdin=subprocess.DEVNULL, capture_output=True, text=True,
                                    timeout=timeout_s, check=False)
        except subprocess.TimeoutExpired as error:
            stdout = error.stdout or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", "replace")
            return RunResult("timeout", stdout, "")
    return RunResult("ok" if result.returncode == 0 else "error", result.stdout, result.stderr)


@functools.cache
def run_python(entry_dir: Path, source: str, attempt: int = 0,
               timeout_s: float = RUN_TIMEOUT_S) -> RunResult:
    """Run `source` once in a fresh temporary copy of the entry's tracked files.

    stdin is `/dev/null`, no display, and `PYTHONHASHSEED=<attempt>`. `attempt` separates deliberate
    repeat runs (the expected-output rule runs a solution twice) in the per-process cache, and its
    distinct hash seed exposes output that depends on set or dict-of-str iteration order, which
    differs between browser (Pyodide) workers.
    """
    return _run_once(Path(entry_dir), source, timeout_s, attempt)


def clear_caches() -> None:
    """Forget cached `git ls-files` listings and runs (tests that edit a fixture tree call this)."""
    tracked_paths.cache_clear()
    run_python.cache_clear()


# --- solution groups ---------------------------------------------------------------------------


def _solutions(entry_dir: Path):
    path = Path(entry_dir) / "solutions.ipynb"
    return nbformat.read(path, as_version=4) if path.is_file() else None


def attach_solutions(items: list[Item], entry_dir: Path, entry_kind: str) -> None:
    """Set each item's `solution_group` (or None when it has no matching solution section).

    Units map `## Exercise N` groups and unnumbered `Challenge N` sections; checkpoints `## Question N`;
    projects `Problem N` groups (by `item_groups`), or, without Problem headings, the solution's
    `## Milestone N` sections (`project_sections`). A milestone whose solution uses named sections
    (`## Lucky Guess`) has no numbered section, so it stays None (a self-check item).
    """
    notebook = _solutions(entry_dir)
    if notebook is None:
        for item in items:
            item.solution_group = None
        return
    cells = notebook.cells
    exercises: dict = {}
    challenges: dict = {}
    questions: dict = {}
    problems: dict = {}
    milestones: dict = {}
    if entry_kind == "unit":
        exercises = {group["number"]: group for group in item_groups(cells, "Exercise")[1]}
        challenges = {group["number"]: group for group in unit_challenges(cells)[1]}
    elif entry_kind == "checkpoint":
        questions = {group["number"]: group for group in item_groups(cells, "Question")[1]}
    else:
        problems = {group["number"]: group for group in item_groups(cells, "Problem")[1]}
        milestones = {section["milestone"]: section for section in project_sections(cells)
                      if section["milestone"] is not None}
    table = {"exercise": exercises, "challenge": challenges, "question": questions,
             "problem": problems, "milestone": milestones}
    for item in items:
        item.solution_group = table[item.mode].get(item.number)


def _code_cells(group) -> list:
    return [cell for cell in (group or {}).get("cells", [])
            if cell.cell_type == "code" and VERIFY_TAG not in cell.metadata.get("tags", [])]


def _solution_code(item: Item) -> str:
    return "\n\n".join(cell.source.rstrip() for cell in _code_cells(item.solution_group)
                       if cell.source.strip())


def solution_concepts(item: Item, concepts_of) -> list[str]:
    """Concept ids of the item's solution code (`concepts_of(source) -> ids`); only ids leave here."""
    found: set[str] = set()
    for cell in _code_cells(item.solution_group):
        if cell.source.strip():
            found.update(concepts_of(cell.source))
    return sorted(found)


# --- asserts ---------------------------------------------------------------------------------


def _top_level_asserts(item: Item) -> list[ast.Assert]:
    nodes: list[ast.Assert] = []
    for cell in _code_cells(item.solution_group):
        try:
            tree = ast.parse(cell.source)
        except SyntaxError:
            continue
        nodes.extend(node for node in tree.body if isinstance(node, ast.Assert))
    return nodes


def _bound_inside(node: ast.AST) -> set[str]:
    """Names an assert binds itself (comprehension targets, lambda parameters, walrus targets)."""
    bound: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.comprehension):
            bound.update(n.id for n in ast.walk(sub.target) if isinstance(n, ast.Name))
        elif isinstance(sub, ast.Lambda):
            arguments = sub.args
            for arg in [*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs]:
                bound.add(arg.arg)
            for arg in (arguments.vararg, arguments.kwarg):
                if arg is not None:
                    bound.add(arg.arg)
        elif isinstance(sub, ast.NamedExpr):
            bound.add(sub.target.id)
    return bound


def assert_free_names(nodes: list[ast.Assert]) -> set[str]:
    """Every name the asserts load, other than Python builtins and names they bind themselves."""
    names: set[str] = set()
    for node in nodes:
        inner = _bound_inside(node)
        names.update(sub.id for sub in ast.walk(node)
                     if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load)
                     and sub.id not in BUILTINS and sub.id not in inner)
    return names


def _called_names(nodes: list[ast.Assert]) -> list[str]:
    called: list[str] = []
    for node in nodes:
        for sub in ast.walk(node):
            if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)
                    and sub.func.id not in BUILTINS and sub.func.id not in called):
                called.append(sub.func.id)
    return called


def starter_bindings(source: str) -> set[str]:
    """Names a Starter binds at top level: `def`, `class` and assignment targets."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    bound: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                bound.update(n.id for n in ast.walk(target) if isinstance(n, ast.Name))
    return bound


def statement_code_names(statement: str) -> set[str]:
    """Identifiers named in the statement's inline code spans (single backticks, not fences)."""
    without_fences = FENCE.sub("", statement)
    return {name for span in INLINE_CODE.findall(without_fences) for name in IDENTIFIER.findall(span)}


def asserts_portability(item: Item) -> tuple[bool, str]:
    """(portable, reason) for the asserts rule (plan 101 D, proposal step 4)."""
    nodes = _top_level_asserts(item)
    if not nodes:
        return False, "no top-level assert in the solution"
    if not any(assert_free_names([node]) for node in nodes):
        return False, "asserts test no name the student writes"
    free = assert_free_names(nodes)
    known = starter_bindings(item.starter) | statement_code_names(item.statement_source)
    missing = sorted(free - known)
    if missing:
        return False, "asserts test the solution's own choices (" + ", ".join(missing) + ")"
    return True, f"{len(nodes)} portable top-level assert(s)"


def asserts_check(item: Item) -> tuple[str, list[str]]:
    """(`source`, `functions`): only the top-level asserts, unparsed, and the non-builtin names called."""
    nodes = _top_level_asserts(item)
    return "\n".join(ast.unparse(node) for node in nodes), _called_names(nodes)


# --- canonical texts -------------------------------------------------------------------------


def _uses_input(source: str) -> bool:
    return re.search(r"\binput\s*\(", source) is not None


def _unseeded_random(source: str) -> bool:
    return (re.search(r"(?m)^\s*(?:import random\b|from random import\b)", source) is not None
            and "seed(" not in source)


def _has_statements(source: str) -> bool:
    """False for a comment-only (or blank) cell: its AST body is empty. A cell that does not parse
    (a fix-the-bug starter) still counts as a program."""
    try:
        return bool(ast.parse(source).body)
    except SyntaxError:
        return True


def statement_program(item: Item) -> str | None:
    """The code a trace item asks about: the item's first code cell with a statement in it (a
    comment-only starter is skipped), else the first Python fence in its statement Markdown."""
    for cell in item.cells:
        if (cell.cell_type == "code" and cell.source.strip() and _has_statements(cell.source)
                and VERIFY_TAG not in cell.metadata.get("tags", [])):
            return cell.source
    for match in FENCE.finditer(item.statement_source):
        opener = item.statement_source[match.start():match.start(1)]
        if "python" in opener:
            return match[1]
    return None


def predict_run(item: Item) -> RunResult | None:
    program = statement_program(item)
    return None if program is None else run_python(item.entry_dir, program)


def expected_output_runs(item: Item) -> tuple[bool, str]:
    """(qualifies, reason) for the expected-output rule; runs the solution twice."""
    code = _solution_code(item)
    if not code:
        return False, "the solution has no code"
    if _uses_input(code) or _uses_input(item.starter):
        return False, "the solution or starter calls input()"
    if _unseeded_random(code) or _unseeded_random(item.starter):
        return False, "the solution uses random without seed()"
    first = run_python(item.entry_dir, code, 0)
    if first.status != "ok":
        return False, f"the solution run gives {first.status}"
    if not first.stdout.strip():
        return False, "the solution prints nothing"
    second = run_python(item.entry_dir, code, 1)
    if second.status != "ok" or second.stdout != first.stdout:
        return False, "the solution's output differs between two runs"
    return True, "the solution prints the same output on two runs"


WORD = re.compile(r"\w+|[^\w\s]")


def _contains_tokens(haystack: list[str], needle: list[str]) -> bool:
    size = len(needle)
    first = needle[0]
    return any(haystack[i] == first and haystack[i:i + size] == needle
               for i in range(len(haystack) - size + 1))


def output_fixed_by_statement(item: Item) -> bool:
    """Whether every non-empty normalised line of the solution's stdout occurs, as a whole token
    sequence, in the statement or the starter (its code cells and the `.py` files it ships).

    A free-design item's solution prints its own sample choices (`random.seed(4)`, a made-up name),
    which no correct student program has to reproduce; a worked sample or a fix-the-bug starter
    fixes the output, so the item can be checked by `expected-output` (plan 101 content review)."""
    stdout = run_python(item.entry_dir, _solution_code(item), 0).stdout
    texts = [item.statement_source, item.starter]
    for path in item.files:
        relative = path.split("/", 2)[2] if path.count("/") >= 2 else ""
        if relative.endswith(".py") and (item.entry_dir / relative).is_file():
            texts.append((item.entry_dir / relative).read_text(encoding="utf-8", errors="replace"))
    haystack = WORD.findall("\n".join(texts))
    lines = [line for line in normalise(stdout, case="sensitive").split("\n") if line.strip()]
    return bool(lines) and all(_contains_tokens(haystack, WORD.findall(line)) for line in lines)


def answer_line(item: Item) -> str:
    """The text of the solution's one `**Answer:** `…`` line; FAIL unless there is exactly one."""
    found = [answer for cell in (item.solution_group or {}).get("cells", [])
             if cell.cell_type == "markdown" for answer in ANSWER_LINE.findall(cell.source)]
    if len(found) != 1:
        raise ValueError(f"FAIL: {item.key}: expected exactly one **Answer:** line in the solution, "
                         f"found {len(found)}")
    return found[0]


def canonical_text(item: Item, kind: str) -> str:
    """The hidden canonical text of an `answer`, `predict` or `expected-output` item."""
    if kind == "answer":
        return answer_line(item)
    if kind == "predict":
        run = predict_run(item)
        if run is None or run.status != "ok" or not run.stdout.strip():
            raise ValueError(f"FAIL: {item.key}: predict needs a statement program with output")
        return run.stdout
    if kind == "expected-output":
        ok, reason = expected_output_runs(item)
        if not ok:
            raise ValueError(f"FAIL: {item.key}: expected-output: {reason}")
        return run_python(item.entry_dir, _solution_code(item), 0).stdout
    raise ValueError(f"no canonical text for check kind {kind}")


def derive_answer_format(canonical: str) -> dict:
    text = normalise(canonical, case="sensitive")
    if NUMBER.fullmatch(text):
        hint = "a number"
    elif "\n" not in text:
        hint = "one line"
    else:
        hint = "several lines"
    return {"case": "sensitive", "hint": hint}


ANSWER_FORMAT_KEYS = frozenset({"case", "hint", "aliases", "whitespace"})


def _valid_answer_format(authored) -> bool:
    if not isinstance(authored, dict) or not {"case", "hint"} <= set(authored) <= ANSWER_FORMAT_KEYS:
        return False
    if authored["case"] not in ("sensitive", "insensitive"):
        return False
    if not isinstance(authored["hint"], str) or not authored["hint"].strip():
        return False
    if "whitespace" in authored and authored["whitespace"] not in WHITESPACE_MODES:
        return False
    aliases = authored.get("aliases", {"-": "-"})
    return (isinstance(aliases, dict) and bool(aliases)
            and all(isinstance(k, str) and k and isinstance(v, str) for k, v in aliases.items()))


def answer_format(item: Item, canonical: str) -> tuple[dict, list[str]]:
    """The heading cell's `metadata.answer_format` (`{case, hint, aliases?, whitespace?}`), else a
    derived format. `aliases` maps a typed form to the canonical one (`{"^": "↑"}`); `whitespace`
    is `collapse` (the default) or `exact` (plan 102 Phase 0). Only authored keys ship, so a format
    without them is unchanged.

    A derived format on a canonical text with letters is reported (content work, plan 101 D).
    """
    authored = item.heading_cell.metadata.get("answer_format")
    if authored is not None:
        if not _valid_answer_format(authored):
            raise ValueError(f"FAIL: {item.key}: metadata.answer_format must be {{case, hint}} "
                             "(plus optional aliases, whitespace) with case sensitive|insensitive, "
                             "a non-empty hint, whitespace collapse|exact and aliases a non-empty "
                             "map of non-empty typed text to canonical text")
        fmt = {"case": authored["case"], "hint": authored["hint"]}
        if "aliases" in authored:
            fmt["aliases"] = dict(authored["aliases"])
        if "whitespace" in authored:
            fmt["whitespace"] = authored["whitespace"]
        return fmt, []
    notes = ["answer_format: derived (letters)"] if LETTER.search(canonical) else []
    return derive_answer_format(canonical), notes


def format_hash(key: str, canonical: str, fmt: dict) -> str:
    """`answer_hash` of `canonical` under an `answer_format` (its case, whitespace and aliases)."""
    return answer_hash(key, canonical, case=fmt.get("case", ""),
                       whitespace=fmt.get("whitespace", "collapse"), aliases=fmt.get("aliases"))


# --- fixtures ----------------------------------------------------------------------------------


def solver_stem(item: Item) -> str | None:
    if item.mode not in ("exercise", "question", "problem") or item.number is None:
        return None
    return f"{SOLUTION_PREFIX[item.entry_kind]}{item.number}"


def fixture_pairs(root: Path, book: str, item: Item) -> list[tuple[int, Path, Path]]:
    """(n, input, output) of a judge book item with a solver `assets/<prefix>N.py`, sorted by n."""
    stem = solver_stem(item)
    if stem is None or not book_flag(root, book, "judge"):
        return []
    assets = Path(item.entry_dir) / "assets"
    if not (assets / f"{stem}.py").is_file():
        return []
    findings: list[str] = []
    pairs = _fixture_pairs(assets / stem, item.entry_dir.name, stem, findings)
    numbered = []
    for inp, outp in pairs:
        if not inp.stem.isdigit():
            raise ValueError(f"FAIL: {item.key}: fixture {inp.name} is not numbered")
        numbered.append((int(inp.stem), inp, outp))
    return sorted(numbered)


def fixture_files(root: Path, book: str, item: Item) -> list[tuple[str, Path]]:
    """(bundle path, source file) of every fixture file the item ships (each pair once)."""
    stem = solver_stem(item)
    out = []
    for n, inp, outp in fixture_pairs(root, book, item):
        base = f"files/{item.entry_dir.name}/fixtures/{stem}/{n}"
        out.extend([(base + ".in", inp), (base + ".out", outp)])
    return out


def sample_input(statement: str) -> str | None:
    """The first code fence anywhere in the statement's first `Sample Input` section, or None."""
    heading = SAMPLE_INPUT.search(statement)
    if heading is None:
        return None
    rest = statement[heading.end():]
    following = ANY_HEADING.search(rest)
    section = rest[:following.start()] if following else rest
    fence = FENCE.search(section)
    return fence[1] if fence else None


def solver_fingerprint(solver: Path, pairs: list[tuple[int, Path, Path]]) -> str:
    """sha256 over the solver's bytes and every fixture pair's (the timing cache's staleness key)."""
    digest = hashlib.sha256()
    for name, data in [("solver", Path(solver).read_bytes()),
                       *((f"{n}.{part}", path.read_bytes()) for n, inp, outp in pairs
                         for part, path in (("in", inp), ("out", outp)))]:
        digest.update(name.encode("utf-8") + b"\0" + str(len(data)).encode("ascii") + b"\0")
        digest.update(data)
    return "sha256:" + digest.hexdigest()


def item_fingerprint(entry_dir: Path, stem: str) -> str | None:
    """The fingerprint of the solver `assets/<stem>.py` and its fixtures, or None without one (the
    answer model's timing tie)."""
    assets = Path(entry_dir) / "assets"
    if not (assets / f"{stem}.py").is_file():
        return None
    pairs = [(int(inp.stem), inp, outp)
             for inp, outp in _fixture_pairs(assets / stem, Path(entry_dir).name, stem, [])
             if inp.stem.isdigit()]
    return solver_fingerprint(assets / f"{stem}.py", sorted(pairs))


MEASURE_REPEATS = 3


def _case_cpu_ms(script: Path, inp: Path, outp: Path, line_exact: bool, label: str) -> float:
    """One case's child CPU time (user + system, ms), run exactly as `tools/judge.py`'s
    `_run_case` runs it; the output must be judged correct."""
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    try:
        result = subprocess.run([sys.executable, str(script)],
                                input=inp.read_text(encoding="utf-8"), text=True,
                                capture_output=True, timeout=JUDGE_TIMEOUT_S, cwd=REPO_ROOT,
                                check=False)
    except subprocess.TimeoutExpired as error:
        raise ValueError(f"FAIL: {label}: solver exceeded {JUDGE_TIMEOUT_S}s on {inp.name}") from error
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    if (result.returncode != 0 or not result.stdout.strip()
            or not outputs_match(result.stdout, outp.read_text(encoding="utf-8"),
                                 line_exact=line_exact)):
        raise ValueError(f"FAIL: {label}: solver fails its fixture {inp.name}; cannot measure")
    return 1000 * ((after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime))


def measure_solver(solver: Path, pairs: list[tuple[int, Path, Path]], line_exact: bool,
                   label: str, repeats: int = MEASURE_REPEATS) -> tuple[float, int]:
    """(the reference solver's maximum CPU ms across the cases, the number of cases); each case
    is the minimum of `repeats` runs, which drops scheduler noise."""
    worst = 0.0
    for _n, inp, outp in pairs:
        worst = max(worst, min(_case_cpu_ms(solver, inp, outp, line_exact, label)
                               for _ in range(repeats)))
    return worst, len(pairs)


def fixtures_check(root: Path, book: str, item: Item,
                   timings: TimingCache | None = None) -> tuple[dict, list[str]]:
    pairs = fixture_pairs(root, book, item)
    if not pairs:
        raise ValueError(f"FAIL: {item.key}: check-fixtures needs a solver and fixture pairs")
    stem = solver_stem(item)
    timings = timings if timings is not None else TimingCache(root, book)
    solver = Path(item.entry_dir) / "assets" / f"{stem}.py"
    line_exact = book_flag(root, book, "acsl")
    cpu_ms = timings.cpu_ms(item.key, solver_fingerprint(solver, pairs),
                            lambda: measure_solver(solver, pairs, line_exact, item.key))
    budget = site_config(root, book).fixture_budget_kb * 1024
    sample = sample_input(item.statement_source)
    wanted = None if sample is None else normalise(sample, case="sensitive")
    cases, over, sample_seen = [], [], False
    for n, inp, outp in pairs:
        base = f"files/{item.entry_dir.name}/fixtures/{stem}/{n}"
        is_sample = (not sample_seen and wanted is not None
                     and normalise(inp.read_text(encoding="utf-8"), case="sensitive") == wanted)
        sample_seen = sample_seen or is_sample
        cases.append({"n": n, "in_file": base + ".in", "out_file": base + ".out", "sample": is_sample})
        if inp.stat().st_size + outp.stat().st_size > budget:
            over.append(n)
    notes = [] if sample_seen else ["fixtures: no pair matches the statement's Sample Input"]
    notes.extend(f"fixtures: case {n} over the {budget // 1024} KB budget" for n in over)
    match = "line" if line_exact else "token"
    return {"cases": cases, "match": match, "over_budget": over, "cpu_ms": cpu_ms}, notes


# --- self-check ------------------------------------------------------------------------------

LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*\S)\s*$")


CODE_SPAN = re.compile(r"(`+)(.+?)(?<!`)\1(?!`)", re.DOTALL)


def _plain_prose(text: str) -> str:
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"(\*\*|__|\*|_|`)", "", text)
    return re.sub(r"\s+", " ", text)


def _plain_masked(text: str) -> tuple[str, list[str]]:
    """`_plain` with each inline code span's text replaced by a placeholder, and those texts."""
    out, codes, position = [], [], 0
    for match in CODE_SPAN.finditer(text):
        out.append(_plain_prose(text[position:match.start()]))
        code = match[2]
        if code.startswith(" ") and code.endswith(" ") and code.strip():
            code = code[1:-1]
        out.append(f"\ue000{len(codes)}\ue001")
        codes.append(code)
        position = match.end()
    out.append(_plain_prose(text[position:]))
    return "".join(out).strip(), codes


CODE_MARK = re.compile("\ue000(\\d+)\ue001")


def _unmask(text: str, codes: list[str]) -> str:
    return CODE_MARK.sub(lambda match: codes[int(match[1])], text)


def _plain(text: str) -> str:
    """Markdown as plain text: links, emphasis and extra whitespace go, but an inline code span keeps
    its exact text (only its backticks go; CommonMark strips one space padding both ends)."""
    masked, codes = _plain_masked(text)
    return _unmask(masked, codes)


def self_check_requirements(item: Item) -> tuple[list[str], list[str]]:
    authored = item.heading_cell.metadata.get("requirements")
    if authored is not None:
        if (not isinstance(authored, list) or not authored
                or not all(isinstance(r, str) and r.strip() for r in authored)):
            raise ValueError(f"FAIL: {item.key}: metadata.requirements must be a non-empty list of text")
        return [r.strip() for r in authored], []
    statement = FENCE.sub("", item.statement_md)
    listed = [_plain(match[1]) for line in statement.split("\n") if (match := LIST_ITEM.match(line))]
    listed = [entry for entry in listed if entry]
    if listed:
        return listed, []
    return statement_sentences(statement)[:MAX_REQUIREMENTS] or [item.label], [
        "self-check: no list in the statement"]


def also_check(item: Item) -> list[str]:
    """The heading cell's `metadata.also_check`: requirements an automatic check cannot see (a method
    the statement demands), shown as a self-check list beside the check (plan 102 Phase 0)."""
    authored = item.heading_cell.metadata.get("also_check")
    if authored is None:
        return []
    if (not isinstance(authored, list) or not authored
            or not all(isinstance(entry, str) and entry.strip() for entry in authored)):
        raise ValueError(f"FAIL: {item.key}: metadata.also_check must be a non-empty list of text")
    return [entry.strip() for entry in authored]


def _tie_text(text: str) -> str:
    return normalise(_plain(text), case="insensitive")


def statement_tie_findings(item: Item, kind: str) -> list[str]:
    """`FAIL:` per authored `also_check` or `requirements` entry that does not occur in the item's
    statement (both as plain text, whitespace collapsed and casefolded; an entry's closing `.`, `!`
    or `?` may end a sentence the statement continues). Authored metadata earns check 2 allowance
    (`check_texts`), so this tie is what stops an entry copied from a solution (plan 102 rule 5)."""
    findings = []
    authored_also = item.heading_cell.metadata.get("also_check")
    if authored_also is not None and kind == "self-check":
        findings.append(f"FAIL: {item.key}: metadata.also_check on a self-check item "
                        "(use requirements)")
    statement = _tie_text(item.statement_md)
    for name in ("also_check", "requirements"):
        authored = item.heading_cell.metadata.get(name)
        if not isinstance(authored, list) or (name == "also_check" and kind == "self-check"):
            continue
        for entry in authored:
            if not isinstance(entry, str) or not entry.strip():
                continue
            text = _tie_text(entry)
            if text not in statement and text.rstrip(".!?") not in statement:
                findings.append(f"FAIL: {item.key}: metadata.{name} entry is not in the statement: "
                                f"{entry.strip()!r}")
    return findings


MAX_REQUIREMENTS = 6
SPECIFICATION = re.compile(r"^\*\*Specification:\*\*\s*")
NOTE = re.compile(r"^\*\*(?:No real version|Real version):\*\*")
BOLD_LABEL = re.compile(r"^\*\*[^*]+\*\*$")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def _sentences(paragraph: str) -> list[str]:
    """The paragraph's plain sentences. A sentence never ends inside an inline code span
    (`print("Hi. Bye")`), so the split runs with every span masked (content review 1, [fable] 3)."""
    masked, codes = _plain_masked(paragraph)
    return [_unmask(s, codes) for s in SENTENCE_END.split(masked) if s]


def statement_sentences(statement: str) -> list[str]:
    """A self-check checklist from statement prose (fences already removed): the sentences of the
    `**Specification:**` paragraph when there is one; else every prose sentence, with headings,
    panels, tables, quotes, bold labels and the `**No real version:**` / `**Real version:**` notes
    left out."""
    prose = [p.strip() for p in re.split(r"\n\s*\n", statement)
             if p.strip() and not p.lstrip().startswith(("#", ":::", "|", ">", "```"))]
    specification = [SPECIFICATION.sub("", p) for p in prose if SPECIFICATION.match(p)]
    if any(p.strip() for p in specification):
        return [s for p in specification for s in _sentences(p)]
    return [s for p in prose if not NOTE.match(p) and not SPECIFICATION.match(p)
            and not BOLD_LABEL.match(p) for s in _sentences(p)]


# --- the check object and answer fields --------------------------------------------------------


def item_uses_turtle(item: Item) -> bool:
    """A turtle item (D4's three-part rule applies in part C): its starter or solution code, a
    starter asset it ships, or its solution asset imports turtle. Course turtle solutions live in
    `assets/solutions_exN*.py` and starters in named `assets/*.py`, not in notebook cells."""
    sources = [item.starter, _solution_code(item)]
    entry = item.entry_dir
    for path in item.files:
        rel = path.split("/", 2)[2] if path.count("/") >= 2 else ""
        if rel.endswith(".py") and (entry / rel).is_file():
            sources.append((entry / rel).read_text(encoding="utf-8"))
    if item.entry_kind == "unit" and item.number is not None:
        assets = (challenge_solution_assets(entry, item.number) if item.mode == "challenge"
                  else solution_assets(entry, item.number))
        sources.extend(path.read_text(encoding="utf-8") for path in assets)
    return any(imports_turtle(source) for source in sources if source)


# A one-token numeric output passes `output_fixed_by_statement` whenever the statement holds that
# number anywhere, so the report lists it for a content plan to confirm (content review 2).
SINGLE_NUMBER = re.compile(r"[-+]?\d+(?:\.\d+)?")
SINGLE_TOKEN_NOTE = "expected-output: single-token output"


def _check(root: Path, book: str, item: Item, kind: str,
           timings: TimingCache | None = None) -> tuple[dict, list[str]]:
    from .classify import confirmed_kind  # classify imports this module

    notes: list[str] = []
    if kind == "fixtures":
        body, notes = fixtures_check(root, book, item, timings)
    elif kind in ("answer", "predict", "expected-output"):
        canonical = canonical_text(item, kind)
        fmt, notes = answer_format(item, canonical)
        body = {"hash": format_hash(item.key, canonical, fmt), "answer_format": fmt}
        output = normalise(canonical, case="sensitive")
        if kind == "expected-output" and SINGLE_NUMBER.fullmatch(output):
            notes = [*notes, f"{SINGLE_TOKEN_NOTE} ({output})"]
        if kind == "predict":
            body["program"] = statement_program(item) or ""
    elif kind == "asserts":
        portable, reason = asserts_portability(item)
        if not portable:
            raise ValueError(f"FAIL: {item.key}: check-asserts: {reason}")
        source, functions = asserts_check(item)
        body = {"source": source, "functions": functions}
    elif kind == "self-check":
        requirements, notes = self_check_requirements(item)
        body = {"requirements": requirements}
    else:
        raise ValueError(f"FAIL: {item.key}: unknown check kind {kind}")
    turtle = item_uses_turtle(item)
    check = {"kind": kind, **body, "turtle": turtle, "confirmed": confirmed_kind(item) is not None}
    return check, notes


def check_data(root: Path, book: str, item: Item, kind: str) -> dict:
    """The schema's `check` object for `item` judged as `kind`."""
    return _check(root, book, item, kind)[0]


def check_notes(root: Path, book: str, item: Item, kind: str) -> list[str]:
    """Report lines for the check (unmatched sample, over-budget pairs, derived formats, …)."""
    return _check(root, book, item, kind)[1]


def _lesson_heading(root: Path, book: str) -> str | None:
    return publication_config(root, book).lesson_heading if book_flag(root, book, "publication") else None


def is_released(item: Item) -> bool:
    """Odd unit exercises show their Student Book answer after an attempt (D3, D5)."""
    return item.mode == "exercise" and item.number is not None and item.number % 2 == 1


def answer_fields(root: Path, book: str, item: Item) -> dict:
    """`answer_visibility` (+ `answer_md`, the Student Book appendix text, for odd unit exercises,
    and `answer_figures` when that answer draws with turtle)."""
    if is_released(item):
        fields = {"answer_visibility": "after-attempt",
                  "answer_md": student_answer_text(item.entry_dir, item.number,
                                                   _lesson_heading(root, book))}
        figures = answer_figures(item.entry_dir, item.number)
        if figures:
            fields["answer_figures"] = figures
        return fields
    return {"answer_visibility": "none"}


def answer_figures(entry_dir: Path, number: int) -> list[dict]:
    """The turtle drawings the Student Book appendix prints for odd unit Exercise `number`, as
    segments (`turtle_segments`), in `_answer_blocks`' order: each turtle real program with a sample
    input, then each printed solution asset that imports turtle. Read only through
    `student_answer_sources`, as `answer_md` is; the site draws these in place of the dropped TikZ."""
    groups, assets = student_answer_sources(Path(entry_dir))
    group = next((g for g in groups if g["number"] == number), None)
    if group is None:
        return []
    out = []
    for program, sample in real_programs(group):
        if imports_turtle(program) and sample is not None:
            out.append({"caption": "Drawing for the sample input: " + ", ".join(sample.splitlines()),
                        "segments": turtle_segments(program, stdin=sample + "\n")})
    for path in assets.get(number, []):
        source = path.read_text(encoding="utf-8")
        if "import turtle" in source or "from turtle import" in source:
            out.append({"caption": "Drawing made by the program above",
                        "segments": turtle_segments(source)})
    return out


# --- the hidden corpora (Phase F's answer-model checks; data only, never bundled) -------------


@dataclass(frozen=True)
class HiddenSource:
    """One piece of solution material.

    `entry` is the entry id; `item` names the item it belongs to (`Exercise 3`, `Challenge 1`,
    `Question 2`, `Problem 4`, `Milestone 2`) or is None; `origin` is the repo-relative path, plus
    `#<cell id>` for a notebook cell; `released` is True when the Student Book prints this material
    as an odd unit answer (through `student_answer_sources`).
    """

    entry: str
    item: str | None
    origin: str
    text: str
    released: bool


def _site_entries(root: Path, book: str) -> list[tuple[str, Path, str]]:
    out = []
    for entry_id, entry_dir in entries(book_path(root, book), "teacher"):
        kind = "unit" if entry_id.startswith("unit-") else (
            "checkpoint" if entry_id.startswith("checkpoint-") else "project")
        out.append((entry_id, entry_dir, kind))
    return out


def _rel(root: Path, path: Path) -> str:
    return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()


def _solution_cell_owners(cells, kind: str) -> dict[int, tuple[str, bool]]:
    """Cell index -> (item name, released) for a solutions notebook's cells."""
    owners: dict[int, tuple[str, bool]] = {}
    index_of = {id(cell): index for index, cell in enumerate(cells)}
    if kind == "unit":
        for group in item_groups(cells, "Exercise")[1]:
            for cell in group["cells"]:
                owners[index_of[id(cell)]] = (f"Exercise {group['number']}", group["number"] % 2 == 1)
        for challenge in unit_challenges(cells)[1]:
            for cell in challenge["cells"]:
                if id(cell) in index_of:
                    owners[index_of[id(cell)]] = (f"Challenge {challenge['number']}", False)
    elif kind == "checkpoint":
        for group in item_groups(cells, ITEM["checkpoint"])[1]:
            for cell in group["cells"]:
                owners[index_of[id(cell)]] = (f"Question {group['number']}", False)
    else:
        problems = item_groups(cells, "Problem")[1]
        for group in problems:
            for cell in group["cells"]:
                owners[index_of[id(cell)]] = (f"Problem {group['number']}", False)
        if not problems:
            for section in project_sections(cells):
                name = (f"Milestone {section['milestone']}" if section["milestone"] is not None
                        else section["heading"])
                for cell in section["cells"]:
                    owners[index_of[id(cell)]] = (name, False)
    return owners


def _printed_in_answer(cell) -> bool:
    """Whether the Student Book prints this code cell of an odd answer (see `_answer_blocks`)."""
    if VERIFY_TAG in cell.metadata.get("tags", []):
        return False
    return not (re.search(r"\brun_path\s*\(\s*[\"']assets/solutions_(?:ex|challenge)", cell.source)
                and "fake_turtle" in cell.source)


def solution_code_cells(root: Path, book: str) -> list[HiddenSource]:
    """Every code cell of every `solutions.ipynb` of the book's syllabus entries."""
    out = []
    for entry_id, entry_dir, kind in _site_entries(root, book):
        notebook = _solutions(entry_dir)
        if notebook is None:
            continue
        owners = _solution_cell_owners(notebook.cells, kind)
        rel = _rel(root, entry_dir / "solutions.ipynb")
        for index, cell in enumerate(notebook.cells):
            if cell.cell_type != "code":
                continue
            item, odd = owners.get(index, (None, False))
            out.append(HiddenSource(entry_id, item, f"{rel}#{cell.get('id')}", cell.source,
                                    odd and _printed_in_answer(cell)))
    return out


def solution_markdown_paragraphs(root: Path, book: str) -> list[HiddenSource]:
    """Every Markdown paragraph (`fenced_paragraphs`) of every `solutions.ipynb` of the book."""
    out = []
    for entry_id, entry_dir, kind in _site_entries(root, book):
        notebook = _solutions(entry_dir)
        if notebook is None:
            continue
        owners = _solution_cell_owners(notebook.cells, kind)
        rel = _rel(root, entry_dir / "solutions.ipynb")
        for index, cell in enumerate(notebook.cells):
            if cell.cell_type != "markdown":
                continue
            item, odd = owners.get(index, (None, False))
            for paragraph in fenced_paragraphs(cell.source):
                if paragraph.strip():
                    out.append(HiddenSource(entry_id, item, f"{rel}#{cell.get('id')}", paragraph, odd))
    return out


def solution_asset_files(root: Path, book: str) -> list[HiddenSource]:
    """Hidden solution files: `solution_assets` of every exercise (odd ones marked released),
    `challenge_solution_assets` of every challenge, every solution source (`exN.py`, `qN.py`, `pN.py`;
    an odd unit `exN.py` is released through its mirror cell) and every `assets/verify/**` file."""
    out: list[HiddenSource] = []
    seen: set[Path] = set()

    def add(entry_id: str, item: str | None, path: Path, released: bool) -> None:
        if path in seen or not path.is_file():
            return
        seen.add(path)
        out.append(HiddenSource(entry_id, item, _rel(root, path),
                                path.read_text(encoding="utf-8", errors="replace"), released))

    for entry_id, entry_dir, kind in _site_entries(root, book):
        notebook = _solutions(entry_dir)
        if notebook is not None and kind == "unit":
            for group in item_groups(notebook.cells, "Exercise")[1]:
                for path in solution_assets(entry_dir, group["number"]):
                    add(entry_id, f"Exercise {group['number']}", path, group["number"] % 2 == 1)
            for challenge in unit_challenges(notebook.cells)[1]:
                for path in challenge_solution_assets(entry_dir, challenge["number"]):
                    add(entry_id, f"Challenge {challenge['number']}", path, False)
        for name in tracked_paths(entry_dir):
            path = entry_dir / name
            if not is_solution_source(path):
                continue
            match = SOLUTION_SOURCE.match(path.name)
            released = False
            item = None
            if match and "verify" not in Path(name).parts[:-1]:
                number = int(re.search(r"\d+", path.stem)[0])
                item = {"ex": "Exercise", "q": "Question", "p": "Problem"}[match[1]] + f" {number}"
                released = kind == "unit" and match[1] == "ex" and number % 2 == 1
            add(entry_id, item, path, released)
    return out


def released_answers(root: Path, book: str) -> dict[str, str]:
    """item key -> `student_answer_text` for every odd unit exercise of the book."""
    from .items import entry_items

    out = {}
    for _entry_id, entry_dir, kind in _site_entries(root, book):
        if kind != "unit":
            continue
        for item in entry_items(root, book, entry_dir, kind):
            if is_released(item):
                out[item.key] = answer_fields(root, book, item)["answer_md"]
    return out


def canonical_texts(root: Path, book: str) -> dict[str, tuple[str, str, str]]:
    """item key -> (check kind, canonical text, case) for every `answer`, `predict` and
    `expected-output` item, under the kind the export uses (confirmed tag, else the proposal)."""
    from .classify import item_kind
    from .items import entry_items

    out = {}
    for _entry_id, entry_dir, kind in _site_entries(root, book):
        for item in entry_items(root, book, entry_dir, kind):
            check_kind = item_kind(root, book, item)[0]
            if check_kind in ("answer", "predict", "expected-output"):
                canonical = canonical_text(item, check_kind)
                fmt, _ = answer_format(item, canonical)
                out[item.key] = (check_kind, canonical, fmt["case"])
    return out


def shipped_asserts(root: Path, book: str) -> dict[str, str]:
    """item key -> the `asserts.source` the export ships, for every `asserts` item."""
    from .classify import item_kind
    from .items import entry_items

    out = {}
    for _entry_id, entry_dir, kind in _site_entries(root, book):
        for item in entry_items(root, book, entry_dir, kind):
            if item_kind(root, book, item)[0] == "asserts":
                out[item.key] = asserts_check(item)[0]
    return out


def check_texts(root: Path, book: str) -> list[tuple[str, str, str]]:
    """(item key, origin, text) of the student-visible text each item's `check` ships, computed from
    the repo, for check 2's baseline: a self-check item's requirements, any other item's
    `also_check`, and a hashed item's `answer_format.hint` and alias texts (origin
    `<statement notebook>#check:<key>`: derived from the statement or authored in its heading
    metadata; `statement_tie_findings` ties authored requirements and `also_check` to the statement),
    and an `asserts` item's shipped asserts (origin
    `<solutions>#asserts:<key>`, which ship by design)."""
    from .classify import item_kind
    from .items import entry_items

    out = []
    for _entry_id, entry_dir, kind in _site_entries(root, book):
        for item in entry_items(root, book, entry_dir, kind):
            check_kind = item_kind(root, book, item)[0]
            statement = f"{_rel(root, entry_dir / f'{item.notebook}.ipynb')}#check:{item.key}"
            if check_kind == "self-check":
                out += [(item.key, statement, text) for text in self_check_requirements(item)[0]]
            else:
                out += [(item.key, statement, text) for text in also_check(item)]
            if check_kind in ("answer", "predict", "expected-output"):
                fmt, _ = answer_format(item, canonical_text(item, check_kind))
                out.append((item.key, statement, fmt["hint"]))
                out += [(item.key, statement, text)
                        for pair in fmt.get("aliases", {}).items() for text in pair]
            elif check_kind == "asserts":
                solutions = f"{_rel(root, entry_dir / 'solutions.ipynb')}#asserts:{item.key}"
                out.append((item.key, solutions, asserts_check(item)[0]))
    return out
