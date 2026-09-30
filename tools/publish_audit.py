"""Audit generated publication projects against notebook sources and rendered PDFs."""
from __future__ import annotations

import json
import re
import subprocess
import tokenize
from itertools import pairwise
from pathlib import Path

import yaml

from tools.books import (
    ANSWER_BANS,
    INDEPENDENCE_BANS,
    STUDENT_BANS,
    PublicationConfig,
    book_flag,
    book_path,
    publication_config,
)
from tools.fake_turtle import imports_turtle
from tools.publish import (
    CODE_ONLY_NAMES,
    EDITIONS,
    ITEM,
    NOTICE,
    answer_chapter_heading,
    challenge_solution_assets,
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
    output_stem,
    panel,
    project_answer_headings,
    project_sections,
    python_name_units,
    reads_stdin,
    redundant_starter,
    solution_assets,
    solution_source_files,
    statement_text,
    title_heading,
    unit_challenges,
)
from tools.turtle_real import real_programs

# The ban lists live in tools.books (INDEPENDENCE_BANS, STUDENT_BANS, ANSWER_BANS), where
# publication.yaml's phrase exemptions are validated against them.
# The full edition also bans "Answer key" in its text. The print edition and the Answer Key say
# "Answer Key" on purpose; the `'## Answer key' in qmd` check guards the teacher heading in every
# student-family edition and the leak guard guards the code.
# Every book-specific expectation (error/hang demo ids, required print Starters, the print page target,
# turtle counts, phrase exemptions, project headers, the lesson heading) lives in the book's
# publication.yaml (tools.books.publication_config; design 010 D1).


def phrase_bans(edition: str) -> tuple[str, ...]:
    return STUDENT_BANS if edition == 'student' else INDEPENDENCE_BANS


def student_phrase_findings(text: str, location: str, edition: str = 'student',
                            answers: bool | None = None, allowed: frozenset[str] = frozenset()) -> list[str]:
    """Banned phrases in a student-family text. `allowed` holds the phrases the book's
    publication.yaml exempts for this chapter (see `chapter_exemptions`)."""
    normalized = text.replace('’', "'").casefold()
    if answers is None:
        answers = location == 'answers'
    exempt = {phrase.casefold() for phrase in allowed}
    banned = phrase_bans(edition) + (ANSWER_BANS if answers else ())
    return [f'FAIL: {edition}: {location}: banned phrase {phrase}' for phrase in banned
            if phrase.casefold() in normalized and phrase.casefold() not in exempt]


def book_prefix(root: Path, book_id: str) -> str:
    """The repo-relative book folder that prefixes every inventory `source` (`<book id>`)."""
    return book_path(root, book_id).relative_to(Path(root).resolve()).as_posix()


def chapter_exemptions(config: PublicationConfig, chapter: dict | None, prefix: str) -> frozenset[str]:
    """Phrases exempt in one chapter: its inventory `kind` must be listed and its book-relative
    `source` must match a glob. Anything outside a recorded chapter (no chapter) gets none."""
    if chapter is None:
        return frozenset()
    return config.exempt_phrases(chapter.get('kind'), chapter.get('source'), prefix)


def qmd_phrase_findings(qmds: dict[str, str], chapters: list[dict], edition: str,
                        config: PublicationConfig, prefix: str) -> list[str]:
    """The `.qmd` layer: each generated chapter is checked against its own source's exemptions."""
    by_file = {chapter['file']: chapter for chapter in chapters}
    findings = []
    for name, text in qmds.items():
        chapter = by_file.get(name)
        findings.extend(student_phrase_findings(
            text, name, edition, answers=chapter is not None and chapter['kind'] == 'answers',
            allowed=chapter_exemptions(config, chapter, prefix)))
    return findings


def outline_chapter_starts(outline: str) -> list[tuple[str, int]]:
    """Top-level PDF bookmarks (one per chapter, in order) and their physical start pages."""
    return [(match[1], int(match[2])) for match in
            re.finditer(r'(?m)^[+|]\t"([^"]+)"\t#page=(\d+)', outline)]


def chapter_page_texts(text: str, outline: str, chapters: list[dict]) -> list[tuple[dict | None, str]] | None:
    """Split pdftotext output into chapter page ranges using the PDF outline's chapter start pages.

    The pages before the first chapter (title and contents pages) come first, with no chapter.
    Returns None when the outline's chapters do not match the inventory one-to-one.
    """
    starts = outline_chapter_starts(outline)
    pages = text.split('\f')
    if len(starts) != len(chapters) or not starts or any(
            later <= earlier for (_, earlier), (_, later) in pairwise(starts)):
        return None
    regions: list[tuple[dict | None, str]] = [(None, '\f'.join(pages[:starts[0][1] - 1]))]
    for index, (chapter, (_, start)) in enumerate(zip(chapters, starts)):
        end = starts[index + 1][1] - 1 if index + 1 < len(starts) else len(pages)
        regions.append((chapter, '\f'.join(pages[start - 1:end])))
    return regions


def pdf_phrase_findings(text: str, outline: str, chapters: list[dict], edition: str,
                        config: PublicationConfig, prefix: str, answers: bool) -> list[str]:
    """The PDF-text layer: each chapter's page range is checked against its own source's exemptions."""
    regions = chapter_page_texts(text, outline, chapters)
    if regions is None:
        return ([f'FAIL: {edition}: PDF outline chapters differ from the inventory (phrase scan unscoped)']
                + student_phrase_findings(text, 'pdf', edition, answers=answers))
    findings = []
    for chapter, region in regions:
        location = 'pdf ' + (chapter['id'] if chapter else 'title pages')
        findings.extend(student_phrase_findings(region, location, edition, answers=answers,
                                                allowed=chapter_exemptions(config, chapter, prefix)))
    return findings


def answers_pdf_findings(text: str, first_unit: int = 1) -> list[str]:
    """The answers appendix starts at the book's first unit's Exercise 1 and ends at the Glossary."""
    start = re.search(rf'Unit\s+{first_unit},\s*Exercise\s+1\s*\(page\s+\d+\)', text)
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


def panel_findings(id_: str, qmd: str, lesson_heading: str) -> list[str]:
    """Goals end at the first lesson (the book's `lesson_heading`); recap ends at Exercises."""
    findings = []
    if qmd.count('::: {.goals}') != 1 or qmd.count('::: {.recap}') != 1:
        findings.append(f'FAIL: {id_}: goals/recap count')
        return findings
    lesson = re.search('(?m)' + lesson_heading, qmd)
    exercise = re.search(r'(?m)^## Exercises\b', qmd)
    if not lesson or not re.search(r'(?ms)^::: \{\.goals\}\n(?:(?!^:::).)*^:::\s*\Z',
                                   qmd[:lesson.start()]):
        findings.append(f'FAIL: {id_}: goals position')
    if not exercise or not re.search(r'(?ms)^::: \{\.recap\}\n(?:(?!^:::).)*^:::\s*\Z',
                                     qmd[:exercise.start()]):
        findings.append(f'FAIL: {id_}: recap position')
    return findings


def lesson_panel_source_findings(entry: Path, lesson_heading: str) -> list[str]:
    cells = notebook(entry / 'lesson.ipynb', 'student').cells
    lessons = [index for index, cell in enumerate(cells)
               if cell.cell_type == 'markdown' and re.match(lesson_heading, cell.source)]
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


def leak_findings(root: Path, book_id: str, chapters: list[dict], project: Path, edition: str = 'student',
                  hide_odd: bool = False, kinds: frozenset[str] = frozenset({'answers'})) -> list[str]:
    """Guard the chapters of the given kinds (by default every `answers` chapter, the only place a
    student-family edition prints solution material) against hidden solutions: even unit exercises,
    checkpoints and the project, plus the odd unit exercises when `hide_odd`.

    A finding names where the leak printed: `answers` for an answer chapter, otherwise the chapter's
    kind and id (e.g. `unit unit-01-x`), so a body-scan leak points at the chapter that holds it.
    """
    located = []  # (where, printed code blocks) per scanned chapter, in chapter order
    for chapter in chapters:
        if chapter['kind'] not in kinds:
            continue
        where = 'answers' if chapter['kind'] == 'answers' else f"{chapter['kind']} {chapter['id']}"
        located.append((where, printed_code((project / chapter['file']).read_text(encoding='utf-8'))))
    findings = []
    for id_, entry in entries(book_path(root, book_id), 'student'):
        kind = id_.split('-', 1)[0]
        label = ITEM[kind]
        solutions = notebook(entry / 'solutions.ipynb', 'teacher')
        _, groups = item_groups(solutions.cells, label)
        for group in groups:
            number = group['number']
            if kind == 'unit' and number % 2 and not hide_odd:
                continue
            sources = [_tokenize_if_complete(cell.source) for cell in group['cells'] if cell.cell_type == 'code']
            files = solution_source_files(entry, kind, number)  # exN.py / qN.py / pN.py
            if kind == 'unit':
                files += solution_assets(entry, number)
            sources += [_tokenize_if_complete(path.read_text(encoding='utf-8')) for path in files]
            for where in dict.fromkeys(where for where, blocks in located
                                       if any(solution_leak(block, sources) for block in blocks)):
                findings.append(f'FAIL: {edition}: {where}: solution leak from {id_} {label} {number}')
        if kind == 'project' and not groups:
            # A Problem-less project's milestone and reference sections are Teacher's Edition only.
            for section in project_sections(solutions.cells):
                sources = [_tokenize_if_complete(cell.source) for cell in section['cells']
                           if cell.cell_type == 'code']
                for where in dict.fromkeys(where for where, blocks in located
                                           if any(solution_leak(block, sources) for block in blocks)):
                    findings.append(f"FAIL: {edition}: {where}: solution leak from {id_} {section['heading']}")
        if kind != 'unit':
            continue
        # Unnumbered challenges print no answer in any student-family edition (plan 098 A3).
        for challenge in unit_challenges(solutions.cells)[1]:
            number = challenge['number']
            sources = [_tokenize_if_complete(cell.source) for cell in challenge['cells']
                       if cell.cell_type == 'code']
            sources += [_tokenize_if_complete(path.read_text(encoding='utf-8'))
                        for path in challenge_solution_assets(entry, number)]
            for where in dict.fromkeys(where for where, blocks in located
                                       if any(solution_leak(block, sources) for block in blocks)):
                findings.append(f'FAIL: {edition}: {where}: solution leak from {id_} Challenge {number}')
    return findings


BACK_MATTER_HEADERS = ('Answers to Selected Exercises', 'Glossary', 'Quick Reference', 'Index')


def header_reset_pattern(project_headers: tuple[str, ...] = ()) -> re.Pattern[str]:
    """Page headers that end a unit: checkpoints, the book's project running headers
    (publication.yaml `project_headers`) and the fixed back-matter names."""
    names = [re.escape(name) for name in dict.fromkeys((*project_headers, *BACK_MATTER_HEADERS))]
    return re.compile(r'(?m)^(?:Checkpoint\s+\d+|' + '|'.join(names) + r')\b')


def reference_findings(pdf_text: str, project_headers: tuple[str, ...] = ()) -> list[str]:
    """Check printed page references against unit-qualified exercise headings."""
    resets = header_reset_pattern(project_headers)
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
        elif resets.search(header):
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
        # An exercise heading is a whole line (`Exercise 16` or `Exercise 16 — Title`), so prose that
        # wraps to begin a line with "Exercise 16's ..." never claims the next "Answer on page" (plan 098 A5).
        for event in re.finditer(r'(?m)^Exercise (\d+)(?: — .*)?[ \t]*$|Answer on page\s+(\d+)', page):
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
    """Mirror of `tools.publish.route_code`, with the same precedence and the same stdin predicate."""
    tags = cell.metadata.get('tags', [])
    if 'no-exec' not in tags:
        return 'code+output' if any(o.get('text') for o in cell.outputs) else 'code'
    if 'error-demo' in tags:
        return 'errordemo'
    if 'hang-demo' in tags:
        return 'hangdemo'
    if reads_stdin(cell.source):
        return 'tryit-stdin'
    if re.search(r'(^|\n)\s*(?:import turtle|from turtle import)', cell.source) and 'input(' in cell.source:
        return 'tryit+figure'
    if re.search(r'(^|\n)\s*(?:import turtle|from turtle import)', cell.source):
        return 'figure'
    if 'input(' in cell.source:
        return 'tryit'
    return 'program'


def _turtle_drawing_findings(entry: Path, qmd: str, edition: str,
                             turtle_tryits: dict[str, int] | None = None) -> list[str]:
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
    expected = (turtle_tryits or {}).get(entry.name)
    if expected is not None and len(tryits) != expected:
        findings.append(f'FAIL: {edition}: {entry.name}: expected {expected} turtle try-it figures, got {len(tryits)}')
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
    lead_in, challenges = unit_challenges(exercise.cells)
    count += _notice_count(preface) + _notice_count(lead_in)
    for group, numbered in [*((group, True) for group in groups), *((group, False) for group in challenges)]:
        found = title_heading(group) if numbered else None
        heading = statement_text(group['cells'][0].source, True, found[1] if found else None)
        count += sum(bool(NOTICE.match(p)) for p in re.split(r'\n\s*\n', heading) if p)
        cells = group['cells'][1:]
        for index, cell in enumerate(cells):
            if cell.cell_type != 'markdown':
                continue
            source = cell.source
            if index == 0 and source.startswith('### '):
                source = source.partition('\n')[2].strip()
            count += sum(bool(NOTICE.match(p)) for p in re.split(r'\n\s*\n', source) if p)
    return count


def notice_count_findings(id_: str, qmd: str, entry: Path, edition: str) -> list[str]:
    """The Notice panels of a unit chapter's body match its lesson and exercise sources.

    Only the body before the Teacher's Edition `## Answer key` counts: a worked solution may hold its
    own Notice, which `_expected_notices` (lesson and exercise sources) does not expect.
    """
    body = qmd.split('## Answer key', 1)[0]
    if body.count('::: {.notice}') != _expected_notices(entry):
        return [f'FAIL: {edition}: {id_}: Notice count']
    return []


def _outline_heading(title: str) -> str:
    """Match source headings to PDF bookmarks, allowing inline code spans."""
    title = re.sub(r'`[^`]*`', '', title)
    return re.sub(r'\s+', ' ', title).strip().casefold()


def _missing_lesson_headings(chapters: list[dict], root: Path, outline: str) -> list[str]:
    """Every lesson, exercise and setup section heading must be a PDF bookmark.

    The setup chapter is found by its inventory record (kind `setup`, its id and title), never by the
    number 0, so a book whose Unit 0 is a real unit keeps it as Unit 0.
    """
    setup_titles = {chapter['title'] for chapter in chapters if chapter['kind'] == 'setup'}
    sections: dict[int, list[str]] = {}
    present: set[str] = set()
    setup_sections: list[str] = []
    in_setup = False
    unit_number = None
    for line in outline.splitlines():
        title_match = re.search(r'"([^"]+)"', line)
        if not title_match:
            continue
        if re.match(r'^[+|]\t"', line):
            in_setup = title_match[1] in setup_titles
            if in_setup:
                present.add(title_match[1])
            unit_match = None if in_setup else re.match(r'Unit (\d+)\b', title_match[1])
            unit_number = int(unit_match[1]) if unit_match else None
        elif re.match(r'^[+|]\t{2}"', line) and in_setup:
            setup_sections.append(_outline_heading(title_match[1]))
        elif re.match(r'^[+|]\t{2,}"', line) and unit_number is not None:
            sections.setdefault(unit_number, []).append(_outline_heading(title_match[1]))
    missing = []
    for chapter in chapters:
        if chapter['kind'] == 'setup':
            if chapter['title'] not in present:
                missing.append(f"{chapter['id']}: {chapter['title']}")
            source = (root / chapter['source']).read_text(encoding='utf-8')
            for title in re.findall(r'^## ([^\n]+)', source, re.MULTILINE):
                expected = _outline_heading(title)
                if not any(bookmark.startswith(expected) for bookmark in setup_sections):
                    missing.append(f"{chapter['id']}: {title}")
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


def expected_chapter_ids(edition: str, entry_order: list[str], setup_id: str) -> list[str]:
    """The chapter order an edition's profile implies (`setup_id`: publication.yaml's setup chapter)."""
    edition_profile = EDITIONS[edition]
    front = [name.removesuffix('.md') for name in edition_profile['front']]
    if edition_profile['body'] == 'answers':
        return front + [f'answers-{id_}' for id_ in entry_order if id_.startswith('unit-')]
    return (front + [setup_id] + entry_order
            + (['answers'] if edition_profile['answers_appendix'] else [])
            + (['glossary', 'quick-reference'] if edition_profile['back_matter'] else [])
            + (['index'] if edition_profile['index'] else []))


def expected_quarto_files(edition: str, entry_order: list[str], setup_id: str) -> list[str]:
    return ['index.qmd' if position == 0 else 'the-index.qmd' if id_ == 'index' else f'{id_}.qmd'
            for position, id_ in enumerate(expected_chapter_ids(edition, entry_order, setup_id))]


def _always_starter_kind(cell) -> tuple[str, str]:
    return ('verify-omitted' if 'verify' in cell.metadata.get('tags', []) else 'starter', cell.source)


def starter_kinds(entry: Path, kind: str, edition: str) -> dict[str, tuple[str, str]]:
    """Each item code cell's id -> (expected inventory kind, source) under the edition's Starter rule,
    in document order.

    A project's preface code cells (milestone scaffolds) and a challenge lead-in's code cells are
    Starters in every edition, never `starter-omitted`; unnumbered challenges follow the item rule
    (plan 098 A1, A3).
    """
    source = entry / ('exercises.ipynb' if kind == 'unit' else 'checkpoint.ipynb' if kind == 'checkpoint'
                      else 'brief.ipynb')
    cells = notebook(source, 'student').cells
    preface, groups = item_groups(cells, ITEM[kind])
    required = EDITIONS[edition]['starters'] == 'required'
    kinds = {}
    if kind == 'project':
        for cell in preface:
            if cell.cell_type == 'code':
                kinds[cell.id] = _always_starter_kind(cell)
    lead_in, challenges = unit_challenges(cells) if kind == 'unit' else ([], [])

    def item_kinds(group) -> None:
        statement = '\n'.join(c.source for c in group['cells'] if c.cell_type == 'markdown')
        for cell in group['cells']:
            if cell.cell_type != 'code':
                continue
            if 'verify' in cell.metadata.get('tags', []):
                kinds[cell.id] = ('verify-omitted', cell.source)
                continue
            omitted = required and redundant_starter(cell.source, statement)
            kinds[cell.id] = ('starter-omitted' if omitted else 'starter', cell.source)

    # The publisher's print order: the exercise groups, then the challenge lead-in, then the challenges.
    for group in groups:
        item_kinds(group)
    for cell in lead_in:
        if cell.cell_type == 'code':
            kinds[cell.id] = _always_starter_kind(cell)
    for group in challenges:
        item_kinds(group)
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
        if not source.strip() or kind == 'verify-omitted':
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


def answer_key_coverage_findings(id_: str, kind: str, qmd: str, numbers: list[int], entry: Path) -> list[str]:
    """Teacher's Edition: one `## Answer key` with an answer for every item. A Problem-less project
    answers each solution section (`project_answer_headings`) instead, and a chapter with nothing to
    answer has no Answer key heading at all."""
    headings = project_answer_headings(entry) if kind == 'project' and not numbers else []
    expected_keys = 1 if numbers or headings or kind != 'project' else 0
    answers = qmd.split('## Answer key', 1)[-1] if expected_keys else ''
    item_numbers = [int(x) for x in re.findall(r'^### ' + ITEM[kind] + r' (\d+)\b', answers, re.MULTILINE)]
    project_headings = re.findall(r'(?m)^### (.+)$', answers) if headings else []
    if qmd.count('## Answer key') != expected_keys or item_numbers != numbers or project_headings != headings:
        return [f'FAIL: teacher: {id_}: answer-key coverage']
    return []


def challenge_findings(id_: str, qmd: str, entry: Path, edition: str) -> list[str]:
    """Unnumbered challenges (plan 098 A3), counted apart from exercises: each source challenge prints
    once as `### Challenge N[ — Title]` with its marker in the chapter body, and the Teacher's Edition
    answer key has an answer for every challenge (the student editions have none)."""
    _, challenges = unit_challenges(notebook(entry / 'exercises.ipynb', 'student').cells)
    numbers = [challenge['number'] for challenge in challenges]
    body, _, answers = qmd.partition('## Answer key')
    findings = []
    for where, found in (('exercises', numbers), ('solutions', _solution_challenge_numbers(entry))):
        duplicates = sorted({number for number in found if found.count(number) > 1})
        if duplicates:
            findings.append(f'FAIL: {edition}: {id_}: duplicate challenge headings in {where}: '
                            + ', '.join(map(str, duplicates)))
    rendered = [int(match[1]) for match in re.finditer(
        r'(?m)^### Challenge (\d+)\b[^\n]*\n\n::: \{\.challenge\}\n\*\*Challenge\*\*\n:::', body)]
    if rendered != numbers or len(re.findall(r'(?m)^### Challenge \d+\b', body)) != len(numbers):
        findings.append(f'FAIL: {edition}: {id_}: rendered challenge items')
    if edition == 'teacher':
        headings = list(re.finditer(r'(?m)^### Challenge (\d+)\b[^\n]*$', answers))
        if [int(match[1]) for match in headings] != numbers:
            findings.append(f'FAIL: {edition}: {id_}: challenge answer coverage')
        for match in headings:
            # An answer section runs to the next heading of level 1-3; a heading alone is no answer.
            following = re.search(r'(?m)^#{1,3} ', answers[match.end():])
            end = match.end() + following.start() if following else len(answers)
            if not answers[match.end():end].strip():
                findings.append(f'FAIL: {edition}: {id_}: empty answer for Challenge {match[1]}')
    return findings


def _solution_challenge_numbers(entry: Path) -> list[int]:
    """The challenge numbers of a unit's solutions notebook, in order (duplicates kept)."""
    solutions = entry / 'solutions.ipynb'
    if not solutions.exists():
        return []
    return [challenge['number'] for challenge in unit_challenges(notebook(solutions, 'teacher').cells)[1]]


FENCE_LINE = re.compile(r'^[ \t]*```')
ARTEFACT = re.compile(r'(?m)^[ \t]*(?:#{2,6} +\S|# +(?:Lesson|Unit|Exercise|Exercises|Challenge|Question|Problem)\b'
                      r'|:::(?:[ \t]*\{|[ \t]*$)|```)')


def _normalised_line(line: str) -> str:
    return ' '.join(line.split())


def fenced_code_lines(qmds) -> set[str]:
    """Every line inside a fenced code block of an edition's generated `.qmd` files, whitespace-normalised."""
    lines = set()
    for text in qmds:
        fenced = False
        for line in text.splitlines():
            if FENCE_LINE.match(line):
                fenced = not fenced
                continue
            if fenced:
                lines.add(_normalised_line(line))
    return lines


def _fence_line_match(line: str, fence_lines: set[str]) -> bool:
    """True when `line` is a code-fence line, or the start of one that the PDF wrapped."""
    return line in fence_lines or any(fence.startswith(line) for fence in fence_lines)


def markdown_artefact_findings(text: str, fence_lines: set[str], edition: str) -> list[str]:
    """Literal Markdown or Quarto syntax left in the PDF text (the first one found).

    A heading-like match (`## ...`, `# Exercise ...`) is ignored when its whole line, whitespace-
    normalised, is a line inside a fenced code block of the edition's `.qmd`: a printed code comment,
    not an unrendered heading (plan 098 A4). `:::` and backtick fences are always artefacts.
    """
    for match in ARTEFACT.finditer(text):
        start = text.rfind('\n', 0, match.start()) + 1
        end = text.find('\n', match.start())
        line = text[start:end if end >= 0 else len(text)].replace('\f', '')
        heading_like = not match.group().lstrip().startswith((':::', '```'))
        if heading_like and _fence_line_match(_normalised_line(line), fence_lines):
            continue
        return [f'FAIL: {edition}: literal Markdown/Quarto artefact in PDF: {match.group().strip()}']
    return []


def item_headings(qmd: str) -> list[str]:
    return re.findall(r'(?m)^#{3,4} (?:Exercise|Challenge|Question|Problem)\b[^\n]*', qmd)


def audit(root: Path, book_id: str) -> list[str]:
    config = publication_config(root, book_id)  # fails loudly without a valid publication.yaml
    book = book_path(root, book_id)
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
                    {'tryit', 'tryit-stdin', 'tryit+figure', 'figure'}
                    and c.id not in config.error_demo_routing_exceptions):
                candidates.add(c.id)
    error_ids, hang_ids = config.error_demo_ids, config.hang_demo_ids
    if (source_tags['error-demo'] != error_ids or source_tags['hang-demo'] != hang_ids
            or candidates != error_ids | hang_ids):
        findings.append('FAIL: error-demo/hang-demo source tags differ from re-derived list')
    for edition, edition_profile in EDITIONS.items():
        findings.extend(_audit_edition(root, book_id, book, edition, edition_profile, entry_order,
                                       config))
    if not any(x.startswith('FAIL:') for x in findings):
        findings.append('publish-audit: PASS')
    return findings


def _audit_edition(root: Path, book_id: str, book: Path, edition: str, edition_profile: dict,
                   entry_order: list[str], config: PublicationConfig) -> list[str]:
    findings: list[str] = []
    prefix = book_prefix(root, book_id)
    unit_numbers = [int(re.match(r'unit-(\d+)', id_)[1]) for id_ in entry_order if id_.startswith('unit-')]
    student_family = edition_profile['student_family']
    answer_body = edition_profile['body'] == 'answers'
    answer_key_drawings = 0
    challenge_count = 0
    publication = book_flag(root, book_id, 'publication')
    project = book / 'build' / 'publish' / edition
    inv_path = project / 'inventory.json'
    if not inv_path.exists():
        return [f'FAIL: {edition}: no inventory']
    manifest = json.loads(inv_path.read_text(encoding='utf-8'))
    chapters = manifest['chapters']
    if [c['id'] for c in chapters] != expected_chapter_ids(edition, entry_order, config.setup_id):
        findings.append(f'FAIL: {edition}: chapter order')
    quarto_config = (project / '_quarto.yml').read_text(encoding='utf-8')
    configured = re.findall(r'^    - ([^\n]+\.qmd)$', quarto_config, re.MULTILINE)
    if configured != expected_quarto_files(edition, entry_order, config.setup_id):
        findings.append(f'FAIL: {edition}: Quarto chapter order')
    if f'output-file: "{output_stem(book_id, edition)}"' not in quarto_config or (
            f'classoption: [{edition_profile["classoption"]},' not in quarto_config):
        findings.append(f'FAIL: {edition}: Quarto output name or class options differ from the profile')
    qmds = {file.name: file.read_text(encoding='utf-8') for file in sorted(project.glob('*.qmd'))}
    if student_family:
        findings.extend(qmd_phrase_findings(qmds, chapters, edition, config, prefix))
        for name, text in qmds.items():
            if '## Answer key' in text:
                findings.append(f'FAIL: {edition}: {name}: answer key present')
            if '::: {.teacher}' in text:
                findings.append(f'FAIL: {edition}: {name}: teacher panel present')
        findings.extend(leak_findings(root, book_id, chapters, project, edition))
    if edition == 'student':
        # Outside the odd answers, no solution (notebook cell, exN.py, qN.py, pN.py) may be printed.
        findings.extend(leak_findings(root, book_id, chapters, project, edition, hide_odd=True,
                                      kinds=frozenset({'unit', 'checkpoint', 'project', 'setup', 'front'})))
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
        findings.extend(leak_findings(root, book_id, chapters, project, edition, hide_odd=True,
                                      kinds=frozenset({'unit', 'checkpoint', 'project', 'setup', 'front'})))
        full = book / 'build' / 'publish' / 'student'
        for chapter in chapters:
            if chapter['kind'] not in {'unit', 'checkpoint', 'project'}:
                continue
            by_id = {record['id']: record['kind'] for record in chapter['inventory']}
            source_kinds = starter_kinds(root / chapter['source'], chapter['kind'], edition)
            starters = [(cell_id, source, by_id.get(cell_id, 'missing'))
                        for cell_id, (_, source) in source_kinds.items()]
            if publication:
                for cell_id in config.print_required_starters & set(by_id):
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
        if publication and not config.print_required_starters <= {
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
        name_units = python_name_units(glossary, first_units, lesson_code(book), config.index_names)
        introduced = [concept for id_, entry in entries(book, 'student') if id_.startswith('unit-')
                      for concept in yaml.safe_load((entry / 'manifest.yaml').read_text(encoding='utf-8'))[
                          'concepts']['introduces']]
        findings.extend(f'FAIL: {edition}: {finding.removeprefix("FAIL: ")}'
                        for finding in glossary_findings(introduced, glossary))
    if edition_profile['index']:
        index = project / (output_stem(book_id, edition) + '.ind')
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
        if kind == 'unit':
            findings.extend(notice_count_findings(id_, qmd, entry, edition))
        if kind == 'unit':
            findings.extend(f'FAIL: {edition}: {finding.removeprefix("FAIL: ")}'
                            for finding in panel_findings(id_, qmd, config.lesson_heading))
            findings.extend(f'FAIL: {edition}: {finding.removeprefix("FAIL: ")}'
                            for finding in lesson_panel_source_findings(entry, config.lesson_heading))
        if kind == 'unit' and publication:
            findings.extend(_turtle_drawing_findings(entry, qmd, edition, config.turtle_tryits))
            if edition == 'teacher':
                answer_key_drawings += qmd.split('## Answer key', 1)[-1].count(
                    '\\color{black!60}Drawing for the sample input:')
        if edition == 'teacher':
            findings.extend(answer_key_coverage_findings(id_, kind, qmd, numbers, entry))
        if kind == 'unit':
            findings.extend(challenge_findings(id_, qmd, entry, edition))
            challenge_count += len(unit_challenges(notebook(source, 'student').cells)[1])
    if edition == 'teacher' and publication and answer_key_drawings != config.teacher_turtle_drawings:
        findings.append(f'FAIL: teacher: expected {config.teacher_turtle_drawings} turtle real-program '
                        f'drawings, got {answer_key_drawings}')
    name = output_stem(book_id, edition)
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
    findings.extend(markdown_artefact_findings(text, fenced_code_lines(qmds.values()), edition))
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
        findings.extend(pdf_phrase_findings(text, outline, chapters, edition, config, prefix,
                                            answers=answer_body))
    if edition == 'student':
        findings.extend(answers_pdf_findings(text, min(unit_numbers, default=1)))
        findings.extend(reference_findings(text, tuple(config.project_headers.values())))
    if (student_family and not edition_profile['answer_refs']
            and re.search(r'Answer on page|\(page\s+\d+\)', text)):
        findings.append(f'FAIL: {edition}: page cross-reference in PDF')
    if edition == 'teacher' and text.count('Answer key') < sum(
            '## Answer key' in qmds.get(chapter['file'], '') for chapter in chapters):
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
    target = config.print_page_target
    if edition == 'student-print' and target is not None and page_count > target:
        findings.append(f'WARN: student-print: {page_count} pages, above the soft target of {target}')
    challenges = f', {challenge_count} challenges' if challenge_count else ''
    findings.append(f'{edition}: {len(chapters)} chapters, {sum(len(c["items"]) for c in chapters)} items'
                    f'{challenges}, {len(boxes)} overfull hboxes, {page_count} pages')
    return findings
