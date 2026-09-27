"""Audit generated publication projects against notebook sources and rendered PDFs."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from tools.fake_turtle import imports_turtle
from tools.publish import ITEM, NOTICE, SETUP_ID, code_tokens, entries, item_groups, notebook
from tools.turtle_real import real_programs

ERROR_IDS = {'9442d5582e1f', '25129fdd9963', 'dcec5192b293', 'u02l029',
             'u02l079', 'u03l010', 'u04l022', 'u07l009', 'u13l009'}
HANG_IDS = {'u04l012'}


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


def audit(root: Path, book_id: str) -> list[str]:
    book = root / book_id
    findings: list[str] = []
    order = [SETUP_ID] + [id_ for id_, _ in entries(book, 'student')]
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
    for edition in ('student', 'teacher'):
        answer_key_drawings = 0
        project = book / 'build' / 'publish' / edition
        inv_path = project / 'inventory.json'
        if not inv_path.exists():
            findings.append(f'FAIL: {edition}: no inventory'); continue
        manifest = json.loads(inv_path.read_text(encoding='utf-8'))
        chapters = manifest['chapters']
        if [c['id'] for c in chapters] != order:
            findings.append(f'FAIL: {edition}: chapter order')
        config = (project / '_quarto.yml').read_text(encoding='utf-8')
        if [f'{id_}.qmd' for id_ in order] != re.findall(r'^    - ((?:unit|checkpoint|project)-[^\n]+\.qmd)$', config, re.MULTILINE):
            findings.append(f'FAIL: {edition}: Quarto chapter order')
        for chapter in chapters:
            id_ = chapter['id']; kind = chapter['kind']; entry = root / chapter['source']
            qmd = (project / chapter['file']).read_text(encoding='utf-8')
            if re.search(r'^#{1,6}\s+\d+(?:\.\d+)*\.\s+', qmd, re.MULTILINE):
                findings.append(f'FAIL: {edition}: {id_}: numbered heading text')
            if kind == 'setup':
                continue
            cells = _source_code(entry, kind)
            lesson_ids = ({c.id for c in notebook(entry / 'lesson.ipynb', 'student').cells}
                          if kind == 'unit' else set())
            expected_codes = [(c.id, _expected_lesson_kind(c) if c.id in lesson_ids else 'starter')
                              for c in cells if c.cell_type == 'code']
            actual_codes = [(x['id'], x['kind']) for x in chapter['inventory'] if not x['id'].startswith(('asset:', 'data:'))]
            if actual_codes != expected_codes or len({cell_id for cell_id, _ in actual_codes}) != len(actual_codes):
                findings.append(f'FAIL: {edition}: {id_}: typed code inventory')
            source = entry / ('exercises.ipynb' if kind == 'unit' else 'checkpoint.ipynb' if kind == 'checkpoint' else 'brief.ipynb')
            _, groups = item_groups(notebook(source, 'student').cells, ITEM[kind])
            numbers = [g['number'] for g in groups]
            if numbers != [x['number'] for x in chapter['items']]:
                findings.append(f'FAIL: {edition}: {id_}: item order')
            heading = '####' if kind == 'project' else '###'
            student_part = qmd.split('## Answer key', 1)[0]
            rendered = [int(number) for number, challenge in re.findall(
                r'^' + heading + r' (?:' + ITEM[kind] + r' (\d+)\b|Challenge — [^\n]+\n\n::: \{\.challenge\}\n\*\*' + ITEM[kind] + r' (\d+)\*\*)',
                student_part, re.MULTILINE) for number in [number or challenge]]
            if rendered != numbers:
                findings.append(f'FAIL: {edition}: {id_}: rendered item titles')
            if kind == 'unit' and qmd.count('::: {.notice}') != _expected_notices(entry):
                findings.append(f'FAIL: {edition}: {id_}: Notice count')
            if kind == 'unit' and book_id == 'book1b':
                findings.extend(_turtle_drawing_findings(entry, qmd, edition))
                if edition == 'teacher':
                    answer_key_drawings += qmd.split('## Answer key', 1)[-1].count(
                        '\\color{black!60}Drawing for the sample input:')
            if edition == 'teacher':
                if qmd.count('## Answer key') != 1 or [int(x) for x in re.findall(r'^### ' + ITEM[kind] + r' (\d+)\b', qmd.split('## Answer key', 1)[-1], re.MULTILINE)] != numbers:
                    findings.append(f'FAIL: {edition}: {id_}: answer-key coverage')
            elif '## Answer key' in qmd:
                findings.append(f'FAIL: {edition}: {id_}: answer key present')
        if edition == 'teacher' and book_id == 'book1b' and answer_key_drawings != 21:
            findings.append(f'FAIL: teacher: expected 21 turtle real-program drawings, got {answer_key_drawings}')
        pdf = project / '_book' / ('Book1b-Teacher.pdf' if edition == 'teacher' else 'Book1b-Student.pdf')
        tex = project / ('Book1b-Teacher.tex' if edition == 'teacher' else 'Book1b-Student.tex')
        if not tex.exists():
            findings.append(f'FAIL: {edition}: generated TeX missing')
        else:
            tex_text = tex.read_text(encoding='utf-8')
            if r'\setcounter{secnumdepth}{-\maxdimen}' not in tex_text or r'\setcounter{tocdepth}{1}' not in tex_text:
                findings.append(f'FAIL: {edition}: heading numbering or TOC depth')
        if not pdf.exists():
            findings.append(f'FAIL: {edition}: PDF missing'); continue
        text = subprocess.run(['pdftotext', str(pdf), '-'], check=True, capture_output=True, text=True).stdout
        artefact = re.search(r'(?m)^[ \t]*(?:#{2,6} +\S|# +(?:Lesson|Unit|Exercise|Exercises|Challenge|Question|Problem)\b|:::(?:[ \t]*\{|[ \t]*$)|```)', text)
        if artefact:
            findings.append(f'FAIL: {edition}: literal Markdown/Quarto artefact in PDF: {artefact.group().strip()}')
        outline = subprocess.run(['mutool', 'show', str(pdf), 'outline'], check=True,
                                 capture_output=True, text=True).stdout
        for heading in _missing_lesson_headings(chapters, root, outline):
            findings.append(f'FAIL: {edition}: {heading}: heading missing from PDF outline')
        if re.search(r'\b(?:In|Out) \[', text):
            findings.append(f'FAIL: {edition}: notebook prompt in PDF')
        if edition == 'student' and 'Answer key' in text:
            findings.append('FAIL: student: answer key in PDF')
        if edition == 'teacher' and text.count('Answer key') < len(order) - 1:
            findings.append('FAIL: teacher: answer keys missing in PDF')
        log_paths = (project / 'render.log', project / 'latex-audit.log')
        if any(not path.exists() for path in log_paths):
            findings.append(f'FAIL: {edition}: render log missing')
        log = '\n'.join(path.read_text(encoding='utf-8') for path in log_paths if path.exists())
        if 'Missing character' in log:
            findings.append(f'FAIL: {edition}: Missing character in render log')
        boxes = [float(x) for x in re.findall(r'Overfull \\hbox \((\d+(?:\.\d+)?)pt too wide\)', log)]
        if len(boxes) > 5 or any(x > 10 for x in boxes):
            findings.append(f'FAIL: {edition}: overfull hboxes: {len(boxes)}, max {max(boxes, default=0):g}pt')
        findings.append(f'{edition}: {len(chapters)} chapters, {sum(len(c["items"]) for c in chapters)} items, {len(boxes)} overfull hboxes')
    if not any(x.startswith('FAIL:') for x in findings):
        findings.append('publish-audit: PASS')
    return findings
