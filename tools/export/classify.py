"""Check-kind classification (design 012 D4; plan 101 Phase D).

A content plan confirms each item's check kind as a heading-cell tag (`check-fixtures`,
`check-answer`, `check-asserts`, `check-expected-output`, `check-predict`, `check-self`). Until then
`propose_kind` proposes one, first match wins:

1. `fixtures`: a judge book item with a solver `assets/<prefix>N.py` and fixture pairs.
2. `answer`: a `short-answer` heading tag.
3. `predict`: the statement asks what code prints, and its program prints something.
4. `asserts`: the solution's top-level asserts load only names the starter binds or the statement
   names in backticks (Python builtins aside).
5. `expected-output`: the solution prints the same non-empty output on two runs, without `input()`
   or unseeded `random`, and every non-empty output line occurs (as a whole token sequence) in the
   statement or the starter, so a correct student program can match it (a worked sample, or a
   fix-the-bug starter's own text). Otherwise the output holds the solution's own choices: the
   reason is `output not fixed by the statement`.
6. `self-check`.

`apply_proposals` writes the proposed tags (content-plan work; never run on real books here).
"""

from __future__ import annotations

import re
from pathlib import Path

import nbformat

from tools.books import book_path
from tools.judge import SHORT_ANSWER_TAG
from tools.publish import entries

from . import answers
from .items import Item, entry_content, entry_items

KINDS = ("fixtures", "answer", "asserts", "expected-output", "predict", "self-check")
TAG = {k: f"check-{'self' if k == 'self-check' else k}" for k in KINDS}
KIND_OF_TAG = {tag: kind for kind, tag in TAG.items()}
UNFIXED = "output not fixed by the statement"
PREDICT = re.compile(r"(?i)(what (does|will) .* print|predict( the)? output|code to trace|"
                     r"trace (this|the) code|predict (the )?(values?|result|exact)|"
                     r"without running|before running)")


def _check_tags(cell) -> list[str]:
    return [tag for tag in cell.metadata.get("tags", []) if tag.startswith("check-")]


def confirmed_kind(item: Item) -> str | None:
    """The kind a heading-cell `check-*` tag confirms (the first known one), else None."""
    for tag in _check_tags(item.heading_cell):
        if tag in KIND_OF_TAG:
            return KIND_OF_TAG[tag]
    return None


def tag_findings(item: Item) -> list[str]:
    """More than one `check-*` heading tag, an unknown `check-*` tag, or one on a body cell."""
    findings = []
    heading = _check_tags(item.heading_cell)
    if len(heading) > 1:
        findings.append(f"FAIL: {item.key}: more than one check-* tag: {', '.join(heading)}")
    findings.extend(f"FAIL: {item.key}: unknown check tag {tag}" for tag in heading
                    if tag not in KIND_OF_TAG)
    for cell in item.cells[1:]:
        for tag in _check_tags(cell):
            findings.append(f"FAIL: {item.key}: {tag} on a non-heading cell ({cell.get('id')}); "
                            "check-* tags go on the item's heading cell")
    return findings


def propose_kind(root: Path, book: str, item: Item) -> tuple[str, str]:
    """(kind, reason) by the ordered rules in the module docstring."""
    pairs = answers.fixture_pairs(root, book, item)
    if pairs:
        return "fixtures", f"solver assets/{answers.solver_stem(item)}.py with {len(pairs)} fixture pair(s)"
    if SHORT_ANSWER_TAG in item.heading_cell.metadata.get("tags", []):
        return "answer", "short-answer tag"
    skipped = []
    if PREDICT.search(item.statement_source):
        run = answers.predict_run(item)
        if run is None:
            skipped.append("trace statement without a program")
        elif run.status != "ok" or not run.stdout.strip():
            skipped.append("trace program prints nothing" if run.status == "ok"
                           else f"trace program gives {run.status}")
        else:
            return "predict", "the statement asks what the program prints"
    if item.solution_group is None:
        return "self-check", "no matching solution section"
    portable, reason = answers.asserts_portability(item)
    if portable:
        return "asserts", reason
    if not reason.startswith("no top-level assert"):
        skipped.append(reason)
    ok, why = answers.expected_output_runs(item)
    if ok and answers.output_fixed_by_statement(item):
        return "expected-output", why
    skipped.append(UNFIXED if ok else why)
    return "self-check", "; ".join(skipped)


def item_kind(root: Path, book: str, item: Item) -> tuple[str, str]:
    """The kind the export uses: the confirmed tag, else the proposal."""
    confirmed = confirmed_kind(item)
    if confirmed is not None:
        return confirmed, f"confirmed by {TAG[confirmed]}"
    return propose_kind(root, book, item)


def _kind_of(entry_id: str) -> str:
    return "unit" if entry_id.startswith("unit-") else (
        "checkpoint" if entry_id.startswith("checkpoint-") else "project")


def _site_entries(root: Path, book: str, entry: str | None) -> list[tuple[Path, str]]:
    selected = [(entry_dir, _kind_of(entry_id))
                for entry_id, entry_dir in entries(book_path(root, book), "teacher")
                if entry is None or entry_id == entry]
    if entry is not None and not selected:
        raise ValueError(f"{book}: no syllabus entry {entry}")
    return selected


def classification_rows(root: Path, book: str, entry: str | None = None) -> list[tuple[str, str, str, str]]:
    """(key, proposed kind, confirmed kind or '', reason) per item, for `classify`."""
    rows = []
    for entry_dir, kind in _site_entries(root, book, entry):
        for item in entry_items(root, book, entry_dir, kind):
            proposed, reason = propose_kind(root, book, item)
            rows.append((item.key, proposed, confirmed_kind(item) or "", reason))
    return rows


def apply_proposals(root: Path, book: str, entry: str | None = None) -> list[str]:
    """Write the proposed `check-*` tag to every item heading cell without one; return the keys.

    The notebook round-trips through nbformat, so cell ids and outputs are kept.
    """
    changed: list[str] = []
    for entry_dir, kind in _site_entries(root, book, entry):
        content = entry_content(root, book, entry_dir, kind)
        updates: dict[str, str] = {}
        for item in content.items:
            if _check_tags(item.heading_cell):
                continue
            proposed, _ = propose_kind(root, book, item)
            updates[item.heading_cell.get("id")] = TAG[proposed]
            changed.append(item.key)
        if not updates:
            continue
        path = Path(entry_dir) / f"{content.items[0].notebook}.ipynb"
        notebook = nbformat.read(path, as_version=4)
        for cell in notebook.cells:
            tag = updates.get(cell.get("id"))
            if tag is not None and tag not in cell.metadata.get("tags", []):
                cell.metadata["tags"] = [*cell.metadata.get("tags", []), tag]
        nbformat.write(notebook, path)
    return changed
