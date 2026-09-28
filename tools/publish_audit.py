"""Audit generated publication projects against notebook sources and rendered PDFs."""
from __future__ import annotations

import json
import re
import subprocess
import tokenize
from pathlib import Path

import yaml

from tools.fake_turtle import imports_turtle
from tools.publish import (
    CODE_ONLY_NAMES,
    EDITIONS,
    ITEM,
    NOTICE,
    SETUP_ID,
    answer_chapter_heading,
    code_block,
    code_tokens,
    entries,
    glossary_entries,
    glossary_units,
    group_title,
    index_entry,
    item_groups,
    lesson_code,
    notebook,
    panel,
    python_name_units,
    redundant_starter,
)
from tools.turtle_real import real_programs

ERROR_IDS = {'9442d5582e1f', '25129fdd9963', 'dcec5192b293', 'u02l029',
             'u02l079', 'u03l010', 'u04l022', 'u07l009', 'u13l009'}
HANG_IDS = {'u04l012'}
INDEPENDENCE_BANS = ("Teacher's Edition", 'your teacher', 'with your teacher',
                     'ask your teacher', 'not graded', 'no-exec', 'solutions.ipynb',
                     'python assets/', 'Lesson One', "checked by the course's test suite",
                     'There is no real program')
# The full edition also bans "Answer key" in its text. The print edition and the Answer Key say
# "Answer Key" on purpose; the `'## Answer key' in qmd` check guards the teacher heading in every
# student-family edition and the leak guard guards the code.
STUDENT_BANS = INDEPENDENCE_BANS + ('Answer key',)
# Book 1b Starters the print rule must keep (code that exists only in the Starter).
PRINT_REQUIRED_STARTERS = {'057d796ebeff'}  # Unit 1, Exercise 20: the broken program to repair
PRINT_PAGE_TARGET = 400


def phrase_bans(edition: str) -> tuple[str, ...]:
    return STUDENT_BANS if edition == 'student' else INDEPENDENCE_BANS


def student_phrase_findings(text: str, location: str, edition: str = 'student',
                            answers: bool | None = None) -> list[str]:
    normalized = text.replace('’', "'").casefold()
    if answers is None:
        answers = location == 'answers'
    banned = phrase_bans(edition) + (('assert',) if answers else ())
    return [f'FAIL: {edition}: {location}: banned phrase {phrase}' for phrase in banned
            if phrase.casefold() in normalized]


def answers_pdf_findings(text: str) -> list[str]:
    start = re.search(r'Unit\s+1,\s*Exercise\s+1\s*\(page\s+\d+\)', text)
    if not start:
        return ['FAIL: student: answers chapter missing in PDF']
    ending = re.search(r'(?m)(?:^|\f)Glossary\s*$', text[start.end():])
    if not ending:
        return ['FAIL: student: glossary chapter missing after answers']
    return student_phrase_findings(text[start.start():start.end() + ending.start()], 'answers')


def glossary_findings(introduced: list[str], glossary: list[tuple]) -> list[str]:
    return [] if sorted(concept for _, concept, _ in glossary) == sorted(introduced) else [
        'FAIL: glossary concept coverage']


def index_findings(index_text: str, glossary: list[tuple],
                   glossary_pages: set[int] | None = None) -> list[str]:
    if not index_text.strip():
        return ['FAIL: index empty']
    items = {}
    findings = []
    for match in re.finditer(r'(?m)^\s*\\(?:item|subitem) (.+?), \\hyperpage', index_text):
        display = re.sub(r'\\texttt\{([^}]*)\}', r'\1', match[1]).replace(r'\_', '_')
        next_item = re.search(r'(?m)^\s*\\(?:item|subitem) ', index_text[match.end():])
        end = match.end() + next_item.start() if next_item else len(index_text)
        pages = {int(page) for page in re.findall(r'\\hyperpage\{(\d+)\}',
                 index_text[match.start():end])}
        if display.casefold() in items:
            findings.append(f'FAIL: index duplicate case entry {display}')
        items[display.casefold()] = pages
    for term, _, _ in glossary:
        pages = items.get(term.casefold())
        if pages is None:
            findings.append(f'FAIL: index missing {term}')
        elif glossary_pages is not None and not (pages - glossary_pages):
            findings.append(f'FAIL: index glossary-only {term}')
    return findings


def index_source_findings(qmd: str, glossary: list[tuple], unit: int | None = None,
                          first_units: dict[str, int] | None = None,
                          name_units: dict[str, int] | None = None) -> list[str]:
    """Reject restricted alias hits placed in ordinary prose, and terms or Python names indexed before their unit.

    With `name_units`, a "Python names" subentry whose name has no teaching unit counts as untaught.
    """
    taught = {index_entry(term): first for term, first in (first_units or {}).items()}
    python_entry = re.compile(r'Python names!(\w+)@\\texttt\{\1\}')
    restricted = {index_entry(term): {key.strip('`').casefold() for key in [term, *aliases]
                                      if key.strip('`').casefold() in CODE_ONLY_NAMES or key.startswith('`')}
                  for term, _, aliases in glossary}
    findings = []
    for line in qmd.splitlines():
        for match in re.finditer(r'\\index\{((?:[^{}]|\{[^{}]*\})+)\}', line):
            prefix = re.sub(r'(?:\\index\{(?:[^{}]|\{[^{}]*\})+\})+$', '',
                            line[:match.start()])
            if match[1].startswith('Python names!') and not prefix.endswith('`'):
                findings.append(f'FAIL: index restricted name in prose: {match[1]}')
                continue
            name = python_entry.fullmatch(match[1])
            if name and unit is not None and name_units is not None:
                if name_units.get(name[1], unit + 1) > unit:
                    findings.append(f'FAIL: index before taught in unit {unit}: {match[1]}')
                continue
            if unit is not None and taught.get(match[1], 0) > unit:
                findings.append(f'FAIL: index before taught in unit {unit}: {match[1]}')
            aliases = restricted.get(match[1], set())
            if not aliases:
                continue
            if prefix.endswith('`'):
                continue
            if any(re.search(r'(?i)(?<!\w)' + re.escape(key) + r'$' , prefix)
                   for key in aliases):
                findings.append(f'FAIL: index restricted name in prose: {match[1]}')
    return findings


def glossary_page_numbers(pdf_text: str) -> set[int]:
    pages = pdf_text.split('\f')
    start = next((i for i, page in enumerate(pages) if page.startswith('Glossary\n')), None)
    end = next((i for i, page in enumerate(pages) if page.startswith('Quick Reference\n')), None)
    if start is None or end is None or end <= start:
        return set()
    for physical in range(start + 1, end):
        match = re.search(r'(?m)^(\d+)\s+Glossary\b', pages[physical])
        if match:
            offset = physical + 1 - int(match[1])
            return set(range(start + 1 - offset, end + 1 - offset))
    return set()


def label_log_findings(log: str) -> list[str]:
    return ['FAIL: LaTeX label/reference warning'] if re.search(
        r'(?:multiply defined|undefined references|Reference [`\']?[^\n]+?undefined)',
        log, re.IGNORECASE) else []


def answer_coverage_findings(answers: str, expected: list[tuple[int, int]]) -> list[str]:
    actual = [(int(unit), int(number)) for unit, number in re.findall(
        r'^### Unit (\d+), Exercise (\d+)\b', answers, re.MULTILINE)]
    return [] if actual == expected else ['FAIL: odd exercise answer coverage']


def rendered_item_numbers(qmd: str, kind: str) -> list[int]:
    heading = '####' if kind == 'project' else '###'
    label = ITEM[kind]
    matches = list(re.finditer(rf'(?m)^{heading} (?:{label} (\d+)\b|Challenge — [^\n]+)', qmd))
    numbers = []
    for index, match in enumerate(matches):
        if match[1]:
            numbers.append(int(match[1]))
            continue
        section = qmd[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(qmd)]
        challenge = re.search(rf'(?m)^::: \{{\.challenge\}}\n\*\*{label} (\d+)\*\*', section)
        if challenge:
            numbers.append(int(challenge[1]))
    return numbers


def panel_findings(id_: str, qmd: str) -> list[str]:
    """Goals end at the first lesson; recap ends at Exercises."""
    findings = []
    if qmd.count('::: {.goals}') != 1 or qmd.count('::: {.recap}') != 1:
        findings.append(f'FAIL: {id_}: goals/recap count')
        return findings
    lesson = re.search(r'(?m)^## Lesson\b', qmd)
    exercise = re.search(r'(?m)^## Exercises\b', qmd)
    if not lesson or not re.search(r'(?ms)^::: \{\.goals\}\n(?:(?!^:::).)*^:::\s*\Z',
                                   qmd[:lesson.start()]):
        findings.append(f'FAIL: {id_}: goals position')
    if not exercise or not re.search(r'(?ms)^::: \{\.recap\}\n(?:(?!^:::).)*^:::\s*\Z',
                                     qmd[:exercise.start()]):
        findings.append(f'FAIL: {id_}: recap position')
    return findings


def lesson_panel_source_findings(entry: Path) -> list[str]:
    cells = notebook(entry / 'lesson.ipynb', 'student').cells
    lessons = [index for index, cell in enumerate(cells)
               if cell.cell_type == 'markdown' and cell.source.startswith('## Lesson')]
    if not lessons or lessons[0] == 0 or not (
            cells[lessons[0] - 1].cell_type == 'markdown'
            and cells[lessons[0] - 1].source.startswith('### You will learn')):
        return [f'FAIL: {entry.name}: goals source position']
    if not cells or cells[-1].cell_type != 'markdown' or not cells[-1].source.startswith('### Recap'):
        return [f'FAIL: {entry.name}: recap source position']
    return []


def _contains(haystack: tuple, needle: tuple) -> bool:
    return any(haystack[i:i + len(needle)] == needle
               for i in range(len(haystack) - len(needle) + 1))


def solution_leak(block: tuple, solutions: list[tuple]) -> bool:
    """A printed block leaks a hidden solution when it equals it or contains all of it.

    Shared idioms (a file-writing loop, a class taught in the lesson) are not leaks: only a whole hidden
    solution cell or asset (at least 30 tokens when embedded in a larger block) counts.
    """
    for stream in solutions:
        if not stream:
            continue
        if block == stream:
            return True
        if len(stream) >= 30 and _contains(block, stream):
            return True
    return False


def printed_code(qmd: str) -> list[tuple]:
    result = []
    for code in re.findall(r'```(?:python|\{\.python[^}]*\})\n(.*?)\n```', qmd, re.DOTALL):
        try:
            result.append(code_tokens(code))
        except tokenize.TokenError:
            # An unfinished starter is not a printable solution stream.
            continue
    return result


def _tokenize_if_complete(source: str) -> tuple:
    try:
        return code_tokens(source)
    except tokenize.TokenError:
        return ()


def leak_findings(root: Path, chapters: list[dict], project: Path, edition: str = 'student',
                  hide_odd: bool = False, kinds: frozenset[str] = frozenset({'answers'})) -> list[str]:
    """Guard the chapters of the given kinds (by default every `answers` chapter, the only place a
    student-family edition prints solution material) against hidden solutions: even unit exercises,
    checkpoints and the project, plus the odd unit exercises when `hide_odd`."""
    blocks = [stream for chapter in chapters if chapter['kind'] in kinds
              for stream in printed_code((project / chapter['file']).read_text(encoding='utf-8'))]
    findings = []
    for id_, entry in entries(root / 'book1b', 'student'):
        kind = id_.split('-', 1)[0]
        label = ITEM[kind]
        solutions = notebook(entry / 'solutions.ipynb', 'teacher')
        _, groups = item_groups(solutions.cells, label)
        for group in groups:
            number = group['number']
            if kind == 'unit' and number % 2 and not hide_odd:
                continue
            sources = [_tokenize_if_complete(cell.source) for cell in group['cells'] if cell.cell_type == 'code']
            if kind == 'unit':
                assets = [path for path in (entry / 'assets').glob('solutions_ex*.py')
                          if re.match(rf'solutions_ex{number}(?!\d)', path.stem)]
                sources += [_tokenize_if_complete(path.read_text(encoding='utf-8')) for path in assets]
            if any(solution_leak(block, sources) for block in blocks):
                findings.append(f'FAIL: {edition}: answers: solution leak from {id_} {label} {number}')
    return findings


def reference_findings(pdf_text: str) -> list[str]:
    """Check printed page references against unit-qualified exercise headings."""
    raw_pages = []
    for physical, page in enumerate(pdf_text.split('\f'), 1):
        if page.strip():
            top = [line.strip() for line in page.splitlines() if line.strip()][:2]
            top_number = next((int(line) for line in top if line.isdigit()), None)
            raw_pages.append((physical, page, top_number))
    unit_pages = [(physical, page, top_number) for physical, page, top_number in raw_pages
                  if any(re.match(r'^Unit\s+\d+\b', line.strip())
                         for line in [line for line in page.splitlines() if line.strip()][:2])]
    offset = next((physical - top_number for physical, _, top_number in unit_pages
                   if top_number is not None), None)
    if offset is None:
        offset = next((physical - int(numbers[0]) for physical, page, _ in unit_pages
                       for numbers in [re.findall(r'(?m)^\s*(\d+)\s*$', page)] if numbers), 0)
    pages = []
    current_unit = None
    for physical, page, top_number in raw_pages:
        printed = top_number if top_number is not None else physical - offset
        header = page[:200]
        unit = re.search(r'(?m)^Unit\s+(\d+)(?:\s+[—–-].*)?\s*$', header)
        if unit:
            current_unit = int(unit[1])
        elif re.search(r'(?m)^(?:Checkpoint\s+\d+|Algorithm Challenge|Answers to Selected Exercises|Glossary|Quick Reference|Index)\b', header):
            current_unit = None
        pages.append((printed, page, current_unit))
    by_number = {number: (page, unit) for number, page, unit in pages}
    findings = []
    active_unit = None
    active_exercise = None
    for number, page, unit_on_page in pages:
        for unit, exercise, source_page in re.findall(
                r'Unit\s+(\d+),\s*Exercise\s+(\d+)\s*\(page\s+(\d+)\)', page):
            source, source_unit = by_number.get(int(source_page), ('', None))
            if source_unit != int(unit) or not re.search(rf'(?m)^Exercise\s+{exercise}\b', source):
                findings.append(f'FAIL: student: Unit {unit} Exercise {exercise}: source page {source_page}')
        if unit_on_page != active_unit:
            active_unit = unit_on_page
            active_exercise = None
        for event in re.finditer(r'(?m)^Exercise\s+(\d+)\b|Answer on page\s+(\d+)', page):
            if event[1]:
                active_exercise = int(event[1])
                continue
            target_page, _ = by_number.get(int(event[2]), ('', None))
            if active_unit is None or active_exercise is None:
                findings.append(f'FAIL: student: page {number}: answer reference without exercise heading')
            elif not re.search(rf'Unit\s+{active_unit},\s*Exercise\s+{active_exercise}\b', target_page):
                findings.append(f'FAIL: student: Unit {active_unit} Exercise {active_exercise}: answer page {event[2]}')
    return findings


def _expected_lesson_kind(cell) -> str:
    tags = cell.metadata.get('tags', [])
    if 'no-exec' not in tags:
        return 'code+output' if any(o.get('text') for o in cell.outputs) else 'code'
    if 'error-demo' in tags:
        return 'errordemo'
    if 'hang-demo' in tags:
        return 'hangdemo'
    if re.search(r'(^|\n)\s*(?:import turtle|from turtle import)', cell.source) and 'input(' in cell.source:
        return 'tryit+figure'
    if re.search(r'(^|\n)\s*(?:import turtle|from turtle import)', cell.source):
        return 'figure'
    if 'input(' in cell.source:
        return 'tryit'
    return 'program'


def _turtle_drawing_findings(entry: Path, qmd: str, edition: str) -> list[str]:
    """Match sample-input figure captions to the lesson and answer-key sources."""
    if not entry.name.startswith('unit-'):
        return []
    findings = []
    lesson = notebook(entry / 'lesson.ipynb', 'student')
    tryits = [cell for cell in lesson.cells if cell.cell_type == 'code'
              and _expected_lesson_kind(cell) == 'tryit+figure']
    lesson_qmd = qmd.rsplit('## Exercises', 1)[0]
    for cell in tryits:
        sample = cell.metadata.get('sample_input')
        caption = f'Drawing for the sample input: {sample}'
        if sample is None or lesson_qmd.count(caption + '}\n\\end{pubfigure}') != 1:
            findings.append(f'FAIL: {edition}: {entry.name}: try-it figure {cell.id}')
    tryit_tokens = {code_tokens(cell.source) for cell in tryits}
    for asset in sorted((entry / 'assets').glob('*.py')) if (entry / 'assets').exists() else []:
        if (f'**assets/{asset.name}**' in lesson_qmd
                and code_tokens(asset.read_text(encoding='utf-8')) in tryit_tokens):
            findings.append(f'FAIL: {edition}: {entry.name}: try-it asset {asset.name} listed again in full')
    if entry.name.startswith('unit-06-') and len(tryits) != 3:
        findings.append(f'FAIL: {edition}: {entry.name}: expected three turtle try-it figures')
    if edition != 'teacher':
        return findings
    _, groups = item_groups(notebook(entry / 'solutions.ipynb', 'teacher').cells, 'Exercise')
    answer = qmd.split('## Answer key', 1)[-1]
    for group in groups:
        number = group['number']
        turtle_programs = [(source, sample) for source, sample in real_programs(group)
                           if imports_turtle(source)]
        if not turtle_programs:
            continue
        section = re.search(rf'(?ms)^### Exercise {number}\b.*?(?=^### Exercise \d+\b|\Z)', answer)
        for _, sample in turtle_programs:
            caption = 'Drawing for the sample input: ' + ', '.join((sample or '').splitlines())
            if section is None or section[0].count(caption + '}\n\\end{pubfigure}') != 1:
                findings.append(f'FAIL: teacher: {entry.name}: Exercise {number} real-program drawing')
    return findings


def _source_code(entry: Path, kind: str):
    first = notebook(entry / ('lesson.ipynb' if kind == 'unit' else
                              'checkpoint.ipynb' if kind == 'checkpoint' else 'brief.ipynb'), 'student')
    cells = list(first.cells)
    if kind == 'unit':
        cells += list(notebook(entry / 'exercises.ipynb', 'student').cells)
    return cells


def _notice_count(cells):
    return sum(bool(NOTICE.match(p)) for c in cells if c.cell_type == 'markdown'
               for p in re.split(r'\n\s*\n', c.source.strip()))


def _expected_notices(entry: Path) -> int:
    lesson = notebook(entry / 'lesson.ipynb', 'student')
    exercise = notebook(entry / 'exercises.ipynb', 'student')
    count = _notice_count(lesson.cells)
    preface, groups = item_groups(exercise.cells, 'Exercise')
    count += _notice_count(preface)
    for group in groups:
        cells = group['cells'][1:]
        for index, cell in enumerate(cells):
            if cell.cell_type != 'markdown':
                continue
            source = cell.source
            if index == 0 and source.startswith('### '):
                source = source.partition('\n')[2].strip()
            count += sum(bool(NOTICE.match(p)) for p in re.split(r'\n\s*\n', source) if p)
    return count


def _outline_heading(title: str) -> str:
    """Match source headings to PDF bookmarks, allowing inline code spans."""
    title = re.sub(r'`[^`]*`', '', title)
    return re.sub(r'\s+', ' ', title).strip().casefold()


def _missing_lesson_headings(chapters: list[dict], root: Path, outline: str) -> list[str]:
    sections: dict[int, list[str]] = {}
    setup_present = False
    setup_sections: list[str] = []
    unit_number = None
    for line in outline.splitlines():
        title_match = re.search(r'"([^"]+)"', line)
        if not title_match:
            continue
        if re.match(r'^[+|]\t"', line):
            setup_present = setup_present or title_match[1] == 'Unit 0 — Getting Set Up'
            unit_match = re.match(r'Unit (\d+)\b', title_match[1])
            unit_number = int(unit_match[1]) if unit_match else None
        elif re.match(r'^[+|]\t{2}"', line) and unit_number == 0:
            setup_sections.append(_outline_heading(title_match[1]))
        elif re.match(r'^[+|]\t{2,}"', line) and unit_number is not None:
            sections.setdefault(unit_number, []).append(_outline_heading(title_match[1]))
    missing = []
    for chapter in chapters:
        if chapter['kind'] == 'setup':
            if not setup_present:
                missing.append(f'{SETUP_ID}: Unit 0 — Getting Set Up')
            source = (root / chapter['source']).read_text(encoding='utf-8')
            for title in re.findall(r'^## ([^\n]+)', source, re.MULTILINE):
                expected = _outline_heading(title)
                if not any(bookmark.startswith(expected) for bookmark in setup_sections):
                    missing.append(f'{SETUP_ID}: {title}')
            continue
        if chapter['kind'] != 'unit':
            continue
        number = int(re.search(r'unit-(\d+)', chapter['id'])[1])
        bookmarks = sections.get(number, [])
        entry = root / chapter['source']
        for cell in notebook(entry / 'lesson.ipynb', 'student').cells:
            if cell.cell_type != 'markdown':
                continue
            for title in re.findall(r'^## ([^\n]+)', cell.source, re.MULTILINE):
                expected = _outline_heading(title)
                if not any(bookmark.startswith(expected) for bookmark in bookmarks):
                    missing.append(f"{chapter['id']}: {title}")
        if 'exercises' not in bookmarks:
            missing.append(f"{chapter['id']}: Exercises")
        exercise = notebook(entry / 'exercises.ipynb', 'student')
        _, groups = item_groups(exercise.cells, 'Exercise')
        titles = {item['number']: item['title'] for item in chapter['items']}
        for group in groups:
            number = group['number']
            stretch = any('stretch' in cell.metadata.get('tags', []) for cell in group['cells'])
            title = titles[number]
            display = (f'Challenge — {title}' if stretch else
                       f'Exercise {number}' + (f' — {title}' if title else ''))
            expected = _outline_heading(display)
            if not any(bookmark.startswith(expected) for bookmark in bookmarks):
                missing.append(f"{chapter['id']}: {display}")
    return missing


def expected_chapter_ids(edition: str, entry_order: list[str]) -> list[str]:
    """The chapter order an edition's profile implies."""
    edition_profile = EDITIONS[edition]
    front = [name.removesuffix('.md') for name in edition_profile['front']]
    if edition_profile['body'] == 'answers':
        return front + [f'answers-{id_}' for id_ in entry_order if id_.startswith('unit-')]
    return (front + [SETUP_ID] + entry_order
            + (['answers'] if edition_profile['answers_appendix'] else [])
            + (['glossary', 'quick-reference'] if edition_profile['back_matter'] else [])
            + (['index'] if edition_profile['index'] else []))


def expected_quarto_files(edition: str, entry_order: list[str]) -> list[str]:
    return ['index.qmd' if position == 0 else 'the-index.qmd' if id_ == 'index' else f'{id_}.qmd'
            for position, id_ in enumerate(expected_chapter_ids(edition, entry_order))]


def starter_kinds(entry: Path, kind: str, edition: str) -> dict[str, tuple[str, str]]:
    """Each item code cell's id -> (expected inventory kind, source) under the edition's Starter rule."""
    source = entry / ('exercises.ipynb' if kind == 'unit' else 'checkpoint.ipynb' if kind == 'checkpoint'
                      else 'brief.ipynb')
    _, groups = item_groups(notebook(source, 'student').cells, ITEM[kind])
    required = EDITIONS[edition]['starters'] == 'required'
    kinds = {}
    for group in groups:
        statement = '\n'.join(c.source for c in group['cells'] if c.cell_type == 'markdown')
        for cell in (group['cells'] if kind == 'project' else group['cells'][1:]):
            if cell.cell_type == 'code':
                omitted = required and redundant_starter(cell.source, statement)
                kinds[cell.id] = ('starter-omitted' if omitted else 'starter', cell.source)
    return kinds


def _starter_panel(source: str) -> str:
    return panel('starter', code_block(source)).rstrip()


ANSWER_REF_LINE = re.compile(r'\n\nAnswer on page \\pageref\{ans:[^}]+\}\.')


def print_equivalence_findings(id_: str, full_qmd: str, print_qmd: str,
                               starters: list[tuple[str, str, str]]) -> list[str]:
    """The print chapter must equal the full-edition chapter minus exactly the Starter panels the print
    inventory records as `starter-omitted` and the "Answer on page" lines.

    `starters` lists (cell id, source, print kind) in document order.
    """
    expected = ANSWER_REF_LINE.sub('', full_qmd)
    cursor = 0
    for cell_id, source, kind in starters:
        if not source.strip():
            continue
        text = _starter_panel(source)
        at = expected.find(text, cursor)
        if at < 0:
            return [f'FAIL: student-print: {id_}: Starter {cell_id} missing from the full edition']
        if kind == 'starter-omitted':
            start = at - 2 if expected[max(at - 2, 0):at] == '\n\n' else at
            expected = expected[:start] + expected[at + len(text):]
            cursor = start
        else:
            cursor = at + len(text)
    if expected != print_qmd:
        return [(f'FAIL: student-print: {id_}: differs from the full edition beyond omitted Starters '
                 'and answer references')]
    return []


def starter_panel_findings(id_: str, print_qmd: str, starters: list[tuple[str, str, str]]) -> list[str]:
    """Every kept Starter prints its panel, in order; no omitted Starter prints one."""
    findings = []
    cursor = 0
    kept_texts = [_starter_panel(source) for _, source, kind in starters
                  if kind == 'starter' and source.strip()]
    for cell_id, source, kind in starters:
        if not source.strip():
            continue
        text = _starter_panel(source)
        if kind == 'starter':
            at = print_qmd.find(text, cursor)
            if at < 0:
                findings.append(f'FAIL: student-print: {id_}: Starter {cell_id} panel missing')
            else:
                cursor = at + len(text)
        elif print_qmd.count(text) > kept_texts.count(text):
            findings.append(f'FAIL: student-print: {id_}: omitted Starter {cell_id} still printed')
    if print_qmd.count('::: {.starter}') != len(kept_texts):
        findings.append(f'FAIL: student-print: {id_}: Starter panel count')
    return findings


ANSWER_HEADING = re.compile(r'(?m)^### Unit (\d+), Exercise (\d+)([^\n]*)\n')
ANSWER_LABEL = re.compile(r'\A\s*```\{=latex\}\n\\label\{ans:[^}\n]+\}\n```\n')
FULL_ANSWER_REF = re.compile(r' \(page \\pageref\{ex:[^}\n]+\}\)')


def answer_entries(qmd: str) -> tuple[str, list[tuple[int, int, str, str]]]:
    """Split answers text into its preamble and (unit, exercise, heading tail, body) entries."""
    headings = list(ANSWER_HEADING.finditer(qmd))
    preamble = qmd[:headings[0].start()] if headings else qmd
    result = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(qmd)
        result.append((int(heading[1]), int(heading[2]), heading[3], qmd[heading.end():end]))
    return preamble, result


def answer_key_equivalence_findings(id_: str, unit: int, key_qmd: str, full_answers: str,
                                    lesson_title: str, titles: dict[int, str],
                                    mainmatter: bool) -> list[str]:
    """An Answer Key chapter must be exactly its heading block plus, for each of the unit's entries in
    the full edition's appendix, the same answer body under a titled flat heading.

    Only the heading form ("(page N)" becomes "— Exercise Title") and the appendix's `ans:` label differ.
    `titles` maps each exercise number to its statement-heading title in the exercises notebook.
    """
    findings = []
    preamble, key = answer_entries(key_qmd)
    if preamble.rstrip() != answer_chapter_heading(unit, lesson_title, mainmatter).rstrip():
        findings.append(f'FAIL: answer-key: {id_}: chapter heading block differs or has extra text')
    _, full = answer_entries(full_answers)
    expected = []
    for entry_unit, number, tail, body in full:
        if entry_unit != unit:
            continue
        if FULL_ANSWER_REF.fullmatch(tail) is None:
            findings.append(f'FAIL: answer-key: {id_}: full-edition heading form for Exercise {number}')
        expected.append((number, ANSWER_LABEL.sub('', body, count=1).strip()))
    if [(u, number) for u, number, _, _ in key] != [(unit, number) for number, _ in expected]:
        findings.append(f'FAIL: answer-key: {id_}: entries differ from the full edition '
                        f'({[number for _, number, _, _ in key]})')
        return findings
    for (_, number, tail, body), (_, full_body) in zip(key, expected):
        title = titles.get(number, '')
        if tail != (f' — {title}' if title else ''):
            findings.append(f'FAIL: answer-key: {id_}: Exercise {number} title differs from the exercises notebook')
        if body.strip() != full_body:
            findings.append(f'FAIL: answer-key: {id_}: Exercise {number} answer differs from the full edition')
    return findings


def item_headings(qmd: str) -> list[str]:
    return re.findall(r'(?m)^#{3,4} (?:Exercise|Challenge|Question|Problem)\b[^\n]*', qmd)


def audit(root: Path, book_id: str) -> list[str]:
    book = root / book_id
    findings: list[str] = []
    entry_order = [id_ for id_, _ in entries(book, 'student')]
    source_tags = {'error-demo': set(), 'hang-demo': set()}
    candidates = set()
    for id_, entry in entries(book, 'student'):
        if not id_.startswith('unit-'):
            continue
        for c in notebook(entry / 'lesson.ipynb', 'student').cells:
            if c.cell_type != 'code':
                continue
            tags = c.metadata.get('tags', [])
            for tag, ids in source_tags.items():
                if tag in tags:
                    ids.add(c.id)
            if ('no-exec' in tags and _expected_lesson_kind(c) not in
                    {'tryit', 'tryit+figure', 'figure'} and c.id != 'u07l034a'):
                candidates.add(c.id)
    if source_tags['error-demo'] != ERROR_IDS or source_tags['hang-demo'] != HANG_IDS or candidates != ERROR_IDS | HANG_IDS:
        findings.append('FAIL: error-demo/hang-demo source tags differ from re-derived list')
    for edition, edition_profile in EDITIONS.items():
        findings.extend(_audit_edition(root, book_id, book, edition, edition_profile, entry_order))
    if not any(x.startswith('FAIL:') for x in findings):
        findings.append('publish-audit: PASS')
    return findings


def _audit_edition(root: Path, book_id: str, book: Path, edition: str, edition_profile: dict,
                   entry_order: list[str]) -> list[str]:
    findings: list[str] = []
    student_family = edition_profile['student_family']
    answer_body = edition_profile['body'] == 'answers'
    answer_key_drawings = 0
    project = book / 'build' / 'publish' / edition
    inv_path = project / 'inventory.json'
    if not inv_path.exists():
        return [f'FAIL: {edition}: no inventory']
    manifest = json.loads(inv_path.read_text(encoding='utf-8'))
    chapters = manifest['chapters']
    if [c['id'] for c in chapters] != expected_chapter_ids(edition, entry_order):
        findings.append(f'FAIL: {edition}: chapter order')
    config = (project / '_quarto.yml').read_text(encoding='utf-8')
    configured = re.findall(r'^    - ([^\n]+\.qmd)$', config, re.MULTILINE)
    if configured != expected_quarto_files(edition, entry_order):
        findings.append(f'FAIL: {edition}: Quarto chapter order')
    if f'output-file: "{edition_profile["output_name"]}"' not in config or (
            f'classoption: [{edition_profile["classoption"]},' not in config):
        findings.append(f'FAIL: {edition}: Quarto output name or class options differ from the profile')
    qmds = {file.name: file.read_text(encoding='utf-8') for file in sorted(project.glob('*.qmd'))}
    kinds = {chapter['file']: chapter['kind'] for chapter in chapters}
    if student_family:
        for name, text in qmds.items():
            findings.extend(student_phrase_findings(text, name, edition, answers=kinds.get(name) == 'answers'))
            if '## Answer key' in text:
                findings.append(f'FAIL: {edition}: {name}: answer key present')
            if '::: {.teacher}' in text:
                findings.append(f'FAIL: {edition}: {name}: teacher panel present')
        findings.extend(leak_findings(root, chapters, project, edition))
    if edition_profile['answers_appendix'] or answer_body:
        answers = '\n'.join(qmds.get(c['file'], '') for c in chapters if c['kind'] == 'answers')
        expected_answers = []
        for id_, entry in entries(book, 'student'):
            if id_.startswith('unit-'):
                _, groups = item_groups(notebook(entry / 'exercises.ipynb', 'student').cells, 'Exercise')
                unit = int(re.search(r'unit-(\d+)', id_)[1])
                expected_answers += [(unit, group['number']) for group in groups if group['number'] % 2]
        findings.extend(f'FAIL: {edition}: {finding.removeprefix("FAIL: ")}'
                        for finding in answer_coverage_findings(answers, expected_answers))
    if student_family and not edition_profile['answer_refs']:
        for name, text in qmds.items():
            if 'Answer on page' in text or '\\pageref' in text:
                findings.append(f'FAIL: {edition}: {name}: page cross-reference present')
    if edition == 'student-print':
        findings.extend(leak_findings(root, chapters, project, edition, hide_odd=True,
                                      kinds=frozenset({'unit', 'checkpoint', 'project', 'setup', 'front'})))
        full = book / 'build' / 'publish' / 'student'
        for chapter in chapters:
            if chapter['kind'] not in {'unit', 'checkpoint', 'project'}:
                continue
            by_id = {record['id']: record['kind'] for record in chapter['inventory']}
            source_kinds = starter_kinds(root / chapter['source'], chapter['kind'], edition)
            starters = [(cell_id, source, by_id.get(cell_id, 'missing'))
                        for cell_id, (_, source) in source_kinds.items()]
            if book_id == 'book1b':
                for cell_id in PRINT_REQUIRED_STARTERS & set(by_id):
                    if by_id[cell_id] != 'starter':
                        findings.append(f'FAIL: student-print: {chapter["id"]}: required Starter {cell_id} omitted')
            print_qmd = qmds[chapter['file']]
            findings.extend(starter_panel_findings(chapter['id'], print_qmd, starters))
            full_file = full / chapter['file']
            if not full_file.exists():
                findings.append(f'FAIL: student-print: {chapter["id"]}: full edition missing for equivalence')
                continue
            full_qmd = full_file.read_text(encoding='utf-8')
            if item_headings(full_qmd) != item_headings(print_qmd):
                findings.append(f'FAIL: student-print: {chapter["id"]}: exercise headings differ from the full edition')
            findings.extend(print_equivalence_findings(chapter['id'], full_qmd, print_qmd, starters))
        if book_id == 'book1b' and not PRINT_REQUIRED_STARTERS <= {
                record['id'] for chapter in chapters for record in chapter['inventory']}:
            findings.append('FAIL: student-print: required Starter ids missing from the inventory')
    if answer_body:
        full_answers = book / 'build' / 'publish' / 'student' / 'answers.qmd'
        if not full_answers.exists():
            findings.append(f'FAIL: {edition}: full edition answers missing for equivalence')
        else:
            full_text = full_answers.read_text(encoding='utf-8')
            answer_chapters = [chapter for chapter in chapters if chapter['kind'] == 'answers']
            for position, chapter in enumerate(answer_chapters):
                entry = root / chapter['source']
                lesson_title = notebook(entry / 'lesson.ipynb', 'student').cells[0].source.splitlines()[0]
                _, groups = item_groups(notebook(entry / 'exercises.ipynb', 'student').cells, 'Exercise')
                titles = {group['number']: group_title(group, 'Exercise') for group in groups}
                findings.extend(answer_key_equivalence_findings(
                    chapter['id'], int(re.search(r'unit-(\d+)', chapter['id'])[1]),
                    qmds.get(chapter['file'], ''), full_text, lesson_title.removeprefix('# '), titles,
                    mainmatter=position == 0))
    index_text = ''
    glossary: list[tuple] = []
    if edition_profile['back_matter']:
        glossary_text = qmds.get('glossary.qmd', '')
        glossary = glossary_entries(glossary_text)
        first_units = glossary_units(glossary_text)
        name_units = python_name_units(glossary, first_units, lesson_code(book))
        introduced = [concept for id_, entry in entries(book, 'student') if id_.startswith('unit-')
                      for concept in yaml.safe_load((entry / 'manifest.yaml').read_text(encoding='utf-8'))[
                          'concepts']['introduces']]
        findings.extend(f'FAIL: {edition}: {finding.removeprefix("FAIL: ")}'
                        for finding in glossary_findings(introduced, glossary))
    if edition_profile['index']:
        index = project / (edition_profile['output_name'] + '.ind')
        index_text = index.read_text(encoding='utf-8') if index.exists() else ''
        findings.extend(f'FAIL: {edition}: {finding.removeprefix("FAIL: ")}'
                        for finding in index_findings(index_text, glossary))
        for chapter in chapters:
            if chapter['kind'] == 'unit':
                findings.extend(f'FAIL: {edition}: {finding.removeprefix("FAIL: ")}'
                                for finding in index_source_findings(
                                    qmds[chapter['file']], glossary,
                                    int(re.match(r'unit-(\d+)', chapter['id'])[1]), first_units, name_units))
    for chapter in chapters:
        id_ = chapter['id']; kind = chapter['kind']; entry = root / chapter['source']
        qmd = qmds.get(chapter['file'], '')
        if re.search(r'^#{1,6}\s+\d+(?:\.\d+)*\.\s+', qmd, re.MULTILINE):
            findings.append(f'FAIL: {edition}: {id_}: numbered heading text')
        if kind in {'setup', 'front', 'answers', 'glossary', 'quickref', 'index'}:
            continue
        cells = _source_code(entry, kind)
        lesson_ids = ({c.id for c in notebook(entry / 'lesson.ipynb', 'student').cells}
                      if kind == 'unit' else set())
        item_kinds = starter_kinds(entry, kind, edition)
        expected_codes = [(c.id, _expected_lesson_kind(c) if c.id in lesson_ids
                           else item_kinds.get(c.id, ('starter', ''))[0])
                          for c in cells if c.cell_type == 'code']
        actual_codes = [(x['id'], x['kind']) for x in chapter['inventory'] if not x['id'].startswith(('asset:', 'data:'))]
        if actual_codes != expected_codes or len({cell_id for cell_id, _ in actual_codes}) != len(actual_codes):
            findings.append(f'FAIL: {edition}: {id_}: typed code inventory')
        source = entry / ('exercises.ipynb' if kind == 'unit' else 'checkpoint.ipynb' if kind == 'checkpoint' else 'brief.ipynb')
        _, groups = item_groups(notebook(source, 'student').cells, ITEM[kind])
        numbers = [g['number'] for g in groups]
        if numbers != [x['number'] for x in chapter['items']]:
            findings.append(f'FAIL: {edition}: {id_}: item order')
        student_part = qmd.split('## Answer key', 1)[0]
        rendered = rendered_item_numbers(student_part, kind)
        if rendered != numbers:
            findings.append(f'FAIL: {edition}: {id_}: rendered item titles')
        if kind == 'unit' and qmd.count('::: {.notice}') != _expected_notices(entry):
            findings.append(f'FAIL: {edition}: {id_}: Notice count')
        if kind == 'unit':
            findings.extend(f'FAIL: {edition}: {finding.removeprefix("FAIL: ")}'
                            for finding in panel_findings(id_, qmd))
            findings.extend(f'FAIL: {edition}: {finding.removeprefix("FAIL: ")}'
                            for finding in lesson_panel_source_findings(entry))
        if kind == 'unit' and book_id == 'book1b':
            findings.extend(_turtle_drawing_findings(entry, qmd, edition))
            if edition == 'teacher':
                answer_key_drawings += qmd.split('## Answer key', 1)[-1].count(
                    '\\color{black!60}Drawing for the sample input:')
        if edition == 'teacher' and (qmd.count('## Answer key') != 1 or [int(x) for x in re.findall(r'^### ' + ITEM[kind] + r' (\d+)\b', qmd.split('## Answer key', 1)[-1], re.MULTILINE)] != numbers):
            findings.append(f'FAIL: {edition}: {id_}: answer-key coverage')
    if edition == 'teacher' and book_id == 'book1b' and answer_key_drawings != 21:
        findings.append(f'FAIL: teacher: expected 21 turtle real-program drawings, got {answer_key_drawings}')
    name = edition_profile['output_name']
    pdf = project / '_book' / f'{name}.pdf'
    tex = project / f'{name}.tex'
    if not tex.exists():
        findings.append(f'FAIL: {edition}: generated TeX missing')
    else:
        tex_text = tex.read_text(encoding='utf-8')
        if r'\setcounter{secnumdepth}{-\maxdimen}' not in tex_text or r'\setcounter{tocdepth}{1}' not in tex_text:
            findings.append(f'FAIL: {edition}: heading numbering or TOC depth')
        if student_family and not edition_profile['answer_refs'] and r'\pageref{ans:' in tex_text:
            findings.append(f'FAIL: {edition}: answer page reference in TeX')
    if not pdf.exists():
        findings.append(f'FAIL: {edition}: PDF missing')
        return findings
    text = subprocess.run(['pdftotext', str(pdf), '-'], check=True, capture_output=True, text=True).stdout
    page_count = text.count('\f')
    if edition_profile['back_matter'] and edition_profile['index']:
        pages = glossary_page_numbers(text)
        if not pages:
            findings.append(f'FAIL: {edition}: glossary pages unresolved')
        else:
            findings.extend(f'FAIL: {edition}: {finding.removeprefix("FAIL: ")}'
                            for finding in index_findings(index_text, glossary, pages)
                            if 'glossary-only' in finding)
    artefact = re.search(r'(?m)^[ \t]*(?:#{2,6} +\S|# +(?:Lesson|Unit|Exercise|Exercises|Challenge|Question|Problem)\b|:::(?:[ \t]*\{|[ \t]*$)|```)', text)
    if artefact:
        findings.append(f'FAIL: {edition}: literal Markdown/Quarto artefact in PDF: {artefact.group().strip()}')
    outline = subprocess.run(['mutool', 'show', str(pdf), 'outline'], check=True,
                             capture_output=True, text=True).stdout
    for heading in _missing_lesson_headings(chapters, root, outline):
        findings.append(f'FAIL: {edition}: {heading}: heading missing from PDF outline')
    if answer_body:
        for chapter in chapters:
            if chapter['kind'] == 'answers' and chapter['title'] not in outline:
                findings.append(f'FAIL: {edition}: {chapter["title"]}: chapter missing from PDF outline')
    if re.search(r'\b(?:In|Out) \[', text):
        findings.append(f'FAIL: {edition}: notebook prompt in PDF')
    if edition == 'student' and 'Answer key' in text:
        findings.append('FAIL: student: answer key in PDF')
    if student_family:
        findings.extend(student_phrase_findings(text, 'pdf', edition, answers=answer_body))
    if edition == 'student':
        findings.extend(answers_pdf_findings(text))
        findings.extend(reference_findings(text))
    if (student_family and not edition_profile['answer_refs']
            and re.search(r'Answer on page|\(page\s+\d+\)', text)):
        findings.append(f'FAIL: {edition}: page cross-reference in PDF')
    if edition == 'teacher' and text.count('Answer key') < len(entry_order):
        findings.append('FAIL: teacher: answer keys missing in PDF')
    log_paths = (project / 'render.log', project / 'latex-audit.log')
    if any(not path.exists() for path in log_paths):
        findings.append(f'FAIL: {edition}: render log missing')
    log = '\n'.join(path.read_text(encoding='utf-8') for path in log_paths if path.exists())
    if 'Missing character' in log:
        findings.append(f'FAIL: {edition}: Missing character in render log')
    findings.extend(f'FAIL: {edition}: {finding.removeprefix("FAIL: ")}'
                    for finding in label_log_findings(log))
    boxes = [float(x) for x in re.findall(r'Overfull \\hbox \((\d+(?:\.\d+)?)pt too wide\)', log)]
    if len(boxes) > 5 or any(x > 10 for x in boxes):
        findings.append(f'FAIL: {edition}: overfull hboxes: {len(boxes)}, max {max(boxes, default=0):g}pt')
    if edition == 'student-print' and page_count > PRINT_PAGE_TARGET:
        findings.append(f'WARN: student-print: {page_count} pages, above the soft target of {PRINT_PAGE_TARGET}')
    findings.append(f'{edition}: {len(chapters)} chapters, {sum(len(c["items"]) for c in chapters)} items, '
                    f'{len(boxes)} overfull hboxes, {page_count} pages')
    return findings
