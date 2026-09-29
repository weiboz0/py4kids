"""``acsl-check``: the ACSL season structure (design 009 D2-D3, plan 092 D3).

BOOK-SCOPED to books with the ``acsl: true`` flag in ``books.yaml``; returns ``[]`` for any other
book (an intentional no-op, like the judge). For an ``acsl`` book it checks:

- ``curriculum/season.yaml`` is well formed (contest 0 is Foundations; ``Practice`` is reserved);
- every unit manifest carries ``acsl: {contest, category, divisions}`` with ``category`` a
  ``units`` entry of that contest and ``divisions`` a subset of that entry's divisions (so a
  Junior LISP unit fails); every checkpoint carries the reserved ``category: Practice`` for a
  contest 1-4; ``divisions`` holds ladder levels only (never ``classroom``);
- every ``## Exercise N`` / ``## Question N`` heading cell carries exactly one ladder tag
  (``acsl-elementary|acsl-junior|acsl-intermediate|acsl-senior``), never below the entry's lowest
  division, and never ``acsl-classroom``;
- a practice checkpoint has exactly one programming question (a ``## Question N`` heading cell
  not tagged ``short-answer``), and it is the last question (plan 093);
- in coverage-map order, shipped units follow the season's ``units`` order and each practice
  checkpoint comes after its contest's last unit; a contest part with a shipped unit has its
  practice checkpoint.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from tools.books import book_flag, book_path
from tools.judge import SHORT_ANSWER_TAG
from tools.notebooks import (
    EXERCISE_HEADING,
    QUESTION_HEADING,
    _fail,
    _markdown_heading_occurrences,
    content_dirs,
    read_nb,
    tags,
)

PRACTICE = "Practice"
TAG_PREFIX = "acsl-"
BLOCK_KEYS = {"contest", "category", "divisions"}


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def load_season(root: Path, book: str) -> tuple[dict | None, list[str]]:
    """Return (season data, schema findings); data is None when it cannot be used."""
    path = book_path(root, book) / "curriculum" / "season.yaml"
    scope = f"{book}/season.yaml"
    if not path.is_file():
        return None, [_fail(book, "curriculum/season.yaml does not exist")]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        return None, [_fail(scope, f"does not parse ({type(error).__name__})")]
    if not isinstance(data, dict):
        return None, [_fail(scope, "must be a mapping")]
    findings = []
    if data.get("season_version") != 1:
        findings.append(_fail(scope, "season_version must be 1"))
    for key in ("source", "retrieved"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            findings.append(_fail(scope, f"{key} must record where and when the map was taken"))
    divisions, ladder = data.get("divisions"), data.get("ladder")
    if not _string_list(divisions) or not _string_list(ladder):
        return None, findings + [_fail(scope, "divisions and ladder must be lists of names")]
    if len(set(ladder)) != len(ladder) or not set(ladder) <= set(divisions):
        findings.append(_fail(scope, "ladder must be distinct divisions"))
    if "classroom" in ladder:
        findings.append(_fail(scope, "classroom is a season-map column, not a ladder level"))
    contests = data.get("contests")
    if not isinstance(contests, list) or not all(isinstance(c, dict) for c in contests):
        return None, findings + [_fail(scope, "contests must be a list of mappings")]
    numbers = [contest.get("contest") for contest in contests]
    if not all(_is_int(number) for number in numbers) or len(set(numbers)) != len(numbers):
        return None, findings + [_fail(scope, "contest numbers must be distinct integers")]
    if 0 not in numbers:
        findings.append(_fail(scope, "contest 0 (Foundations) is missing"))
    for contest in contests:
        label = f"contest {contest['contest']}"
        units = contest.get("units")
        if not (
            isinstance(units, list)
            and units
            and all(
                isinstance(unit, dict)
                and set(unit) == {"name", "divisions"}
                and isinstance(unit["name"], str)
                and _string_list(unit["divisions"])
                and unit["divisions"]
                for unit in units
            )
        ):
            findings.append(
                _fail(scope, f"{label} units must be a non-empty list of {{name, divisions}}")
            )
            continue
        unit_names = [unit["name"] for unit in units]
        if len(set(unit_names)) != len(unit_names):
            findings.append(_fail(scope, f"{label} units repeat a name"))
        if PRACTICE in unit_names:
            findings.append(_fail(scope, f"{label} units use the reserved {PRACTICE!r}"))
        for unit in units:
            if not set(unit["divisions"]) <= set(ladder) or len(set(unit["divisions"])) != len(
                unit["divisions"]
            ):
                findings.append(
                    _fail(scope, f"{label} unit {unit['name']!r} divisions must be ladder levels")
                )
        categories = contest.get("categories", {})
        if not isinstance(categories, dict) or not all(
            division in divisions and _string_list(names)
            for division, names in categories.items()
        ):
            findings.append(_fail(scope, f"{label} categories must map divisions to name lists"))
    if findings:
        return None, findings
    return data, []


def _unit_map(contest: dict) -> dict[str, list[str]]:
    """A contest's units in book order: category name -> the ladder levels that take it."""
    return {unit["name"]: unit["divisions"] for unit in contest.get("units", [])}


def _block_findings(scope: str, kind: str, block: object, season: dict) -> list[str]:
    """Validate one manifest ``acsl:`` block against the season map."""
    if block is None:
        return [_fail(scope, f"{kind} manifest needs an acsl: block (design 009 D3)")]
    if not isinstance(block, dict) or set(block) != BLOCK_KEYS:
        return [_fail(scope, f"acsl block keys must be {sorted(BLOCK_KEYS)}")]
    findings = []
    contests = {contest["contest"]: contest for contest in season["contests"]}
    number, category, divisions = block["contest"], block["category"], block["divisions"]
    if not _is_int(number) or number not in contests:
        findings.append(_fail(scope, f"acsl contest {number!r} is not in season.yaml"))
    elif kind == "checkpoint":
        if category != PRACTICE:
            findings.append(
                _fail(scope, f"a checkpoint's acsl category must be {PRACTICE!r}, not {category!r}")
            )
        elif number == 0:
            findings.append(_fail(scope, f"{PRACTICE} checkpoints belong to contests 1-4"))
    elif category == PRACTICE:
        findings.append(_fail(scope, f"{PRACTICE!r} is reserved for practice checkpoints"))
    elif not isinstance(category, str) or category not in _unit_map(contests[number]):
        findings.append(
            _fail(scope, f"acsl category {category!r} is not a unit of contest {number}")
        )
    ladder = season["ladder"]
    if not _string_list(divisions) or not divisions or len(set(divisions)) != len(divisions):
        findings.append(_fail(scope, "acsl divisions must be a non-empty list of distinct levels"))
        return findings
    for division in divisions:
        if division == "classroom":
            findings.append(_fail(scope, "classroom is never a division (a path only)"))
        elif division not in ladder:
            findings.append(_fail(scope, f"acsl division {division!r} is not a ladder level"))
    allowed = None
    if kind == "unit" and _is_int(number) and number in contests and isinstance(category, str):
        allowed = _unit_map(contests[number]).get(category)
    if allowed is not None:
        extra = [d for d in divisions if d in ladder and d not in allowed]
        if extra:
            findings.append(
                _fail(
                    scope,
                    f"acsl divisions {extra} do not take contest {number} {category!r} "
                    f"(season.yaml allows {allowed})",
                )
            )
    return findings


def _tag_findings(scope: str, entry_dir: Path, kind: str, block: dict | None,
                  season: dict) -> list[str]:
    """Exactly one ladder tag per item heading, never below the entry's lowest division."""
    notebook_name, pattern = {
        "unit": ("exercises.ipynb", EXERCISE_HEADING),
        "checkpoint": ("checkpoint.ipynb", QUESTION_HEADING),
    }[kind]
    path = entry_dir / notebook_name
    if not path.is_file():
        return []  # structure-check reports the missing notebook
    ladder = season["ladder"]
    lowest = None
    if isinstance(block, dict) and _string_list(block.get("divisions")):
        levels = [ladder.index(d) for d in block["divisions"] if d in ladder]
        if levels and len(levels) == len(block["divisions"]):
            lowest = min(levels)
    notebook = read_nb(path)
    findings = []
    seen_cells: set[int] = set()
    for heading, index in _markdown_heading_occurrences(notebook, pattern):
        item = heading.removeprefix("## ")
        if index in seen_cells:
            findings.append(_fail(scope, f"{item}: each item heading needs its own cell"))
            continue
        seen_cells.add(index)
        division_tags = [tag for tag in tags(notebook.cells[index]) if tag.startswith(TAG_PREFIX)]
        if f"{TAG_PREFIX}classroom" in division_tags:
            findings.append(_fail(scope, f"{item}: acsl-classroom is not a division tag"))
            continue
        unknown = [tag for tag in division_tags if tag.removeprefix(TAG_PREFIX) not in ladder]
        if unknown:
            findings.append(_fail(scope, f"{item}: unknown division tag(s) {unknown}"))
            continue
        if len(division_tags) != 1:
            findings.append(
                _fail(scope, f"{item}: needs exactly one division tag (found {division_tags})")
            )
            continue
        level = ladder.index(division_tags[0].removeprefix(TAG_PREFIX))
        if lowest is not None and level < lowest:
            findings.append(
                _fail(
                    scope,
                    f"{item}: {division_tags[0]} is below the {kind}'s lowest division "
                    f"{ladder[lowest]!r}",
                )
            )
    return findings


def _practice_findings(scope: str, entry_dir: Path) -> list[str]:
    """A practice checkpoint closes with exactly one programming question (plan 093)."""
    path = entry_dir / "checkpoint.ipynb"
    if not path.is_file():
        return []  # structure-check reports the missing notebook
    notebook = read_nb(path)
    questions: list[tuple[str, bool]] = []
    seen_cells: set[int] = set()
    for heading, index in _markdown_heading_occurrences(notebook, QUESTION_HEADING):
        if index in seen_cells:
            continue  # _tag_findings reports a shared heading cell
        seen_cells.add(index)
        is_short = SHORT_ANSWER_TAG in tags(notebook.cells[index])
        questions.append((heading.removeprefix("## "), not is_short))
    programming = [item for item, is_programming in questions if is_programming]
    if not programming:
        return [_fail(scope, "a practice checkpoint needs exactly one programming question "
                             "(a Question heading not tagged short-answer); found none")]
    if len(programming) > 1:
        return [_fail(scope, "a practice checkpoint needs exactly one programming question; "
                             f"found {len(programming)}: {programming}")]
    if questions[-1][0] != programming[0]:
        return [_fail(scope, f"the programming question ({programming[0]}) must be the last "
                             f"question (last is {questions[-1][0]})")]
    return []


def _read_block(entry_dir: Path) -> tuple[bool, object]:
    """(manifest usable, its acsl block or None)."""
    path = entry_dir / "manifest.yaml"
    if not path.is_file():
        return False, None
    manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        return False, None
    return True, manifest.get("acsl")


def _season_order_findings(root: Path, book: str, season: dict,
                           blocks: dict[str, tuple[str, dict]]) -> list[str]:
    """Coverage-map order of shipped entries follows the season; practice closes each part."""
    map_path = book_path(root, book) / "curriculum" / "coverage-map.yaml"
    data = yaml.safe_load(map_path.read_text(encoding="utf-8")) if map_path.is_file() else None
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        return [_fail(book, "coverage-map entries must be a list")]
    contests = {contest["contest"]: contest for contest in season["contests"]}
    ordered = [
        entry["id"]
        for entry in data["entries"]
        if isinstance(entry, dict) and entry.get("id") in blocks
    ]
    ordered += sorted(set(blocks) - set(ordered))  # shipped but unmapped: manifest-check reports
    findings = []
    previous = None
    unit_contests: set[int] = set()
    practice: dict[int, list[str]] = {}
    for entry_id in ordered:
        kind, block = blocks[entry_id]
        number = block["contest"]
        order = list(_unit_map(contests[number]))
        if kind == "checkpoint":
            key = (number, len(order))
            practice.setdefault(number, []).append(entry_id)
        else:
            key = (number, order.index(block["category"]))
            unit_contests.add(number)
        if previous is not None and key <= previous[0]:
            findings.append(
                _fail(
                    entry_id,
                    f"out of season order: contest {number} {block['category']!r} comes after "
                    f"{previous[1]} (season.yaml units order; practice closes its part)",
                )
            )
        previous = (key, entry_id)
    for number, entry_ids in sorted(practice.items()):
        if len(entry_ids) > 1:
            findings.append(
                _fail(book, f"contest {number} has more than one practice checkpoint: {entry_ids}")
            )
        if number not in unit_contests:
            findings.append(
                _fail(entry_ids[0], f"contest {number} practice checkpoint has no shipped unit")
            )
    for number in sorted(unit_contests - set(practice)):
        if number != 0:
            findings.append(
                _fail(book, f"contest {number} has shipped units but no practice checkpoint")
            )
    return findings


def acsl_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    if not book_flag(root, book, "acsl"):
        return []  # intentional no-op outside acsl books (see module docstring)
    entries, findings = content_dirs(root, book, unit)
    if findings:
        return findings
    season, findings = load_season(root, book)
    if season is None:
        return findings
    valid: dict[str, tuple[str, dict]] = {}
    for entry_dir, kind in entries:
        if kind == "project":
            continue  # no project carries an acsl block (design 009)
        scope = entry_dir.name
        usable, block = _read_block(entry_dir)
        if not usable:
            continue  # manifest-check reports a missing or malformed manifest
        block_findings = _block_findings(scope, kind, block, season)
        findings.extend(block_findings)
        findings.extend(_tag_findings(scope, entry_dir, kind, block, season))
        if kind == "checkpoint" and isinstance(block, dict) and block.get("category") == PRACTICE:
            findings.extend(_practice_findings(scope, entry_dir))
        if not block_findings:
            valid[scope] = (kind, block)
    if unit is None:
        findings.extend(_season_order_findings(root, book, season, valid))
    return findings
