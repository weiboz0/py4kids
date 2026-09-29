"""Plan 090 Phase D: the four python-concepts editions, edition blocks, the print Starter rule,
the Answer Key boundary, the audit's per-edition rules, output/ ownership and the CLI."""

import json
from pathlib import Path

import nbformat
import pytest

from tools import cli, publish, publish_audit
from tools.publish import (
    EDITIONS,
    allowed_source,
    build,
    filter_edition_blocks,
    output_stem,
    redundant_starter,
    render_items,
)
from tools.publish_output import refresh_output

REPO = Path(__file__).resolve().parents[1]
md = nbformat.v4.new_markdown_cell
code = nbformat.v4.new_code_cell


# --- edition blocks -------------------------------------------------------------------------

LIST_WITH_BLOCKS = (
    '# How to Use This Book\n\n'
    '## Reading the page\n\n'
    '- **Program:** code.\n'
    '<!-- edition: student -->\n'
    '- **Starter:** full.\n'
    '<!-- /edition -->\n'
    '<!-- edition: teacher -->\n'
    '- **Starter:** teacher.\n'
    '<!-- /edition -->\n'
    '- **Check lines:** checks.\n\n'
    '<!-- edition: student-print -->\n'
    'Starting code is in your notebook.\n'
    '<!-- /edition -->\n'
    'Shared ending.\n')


def test_edition_blocks_inside_a_list_leave_no_blank_line():
    print_text = filter_edition_blocks(LIST_WITH_BLOCKS, 'student-print')
    assert '- **Program:** code.\n- **Check lines:** checks.\n' in print_text
    assert 'Starter' not in print_text and '<!--' not in print_text
    assert 'Starting code is in your notebook.\nShared ending.' in print_text
    full = filter_edition_blocks(LIST_WITH_BLOCKS, 'student')
    assert '- **Program:** code.\n- **Starter:** full.\n- **Check lines:** checks.\n' in full
    assert 'teacher.' not in full and 'Starting code' not in full
    teacher = filter_edition_blocks(LIST_WITH_BLOCKS, 'teacher')
    assert '- **Program:** code.\n- **Starter:** teacher.\n- **Check lines:** checks.\n' in teacher
    assert filter_edition_blocks('<!-- edition: student|teacher -->\nboth\n<!-- /edition -->\n', 'teacher') == 'both\n'
    assert filter_edition_blocks('plain\n', 'answer-key') == 'plain\n'


def test_dropped_paragraph_block_leaves_one_blank_line():
    text = 'Before.\n\n<!-- edition: teacher -->\nTeacher only.\n<!-- /edition -->\n\nAfter.\n'
    assert filter_edition_blocks(text, 'student') == 'Before.\n\nAfter.\n'
    assert filter_edition_blocks(text, 'teacher') == 'Before.\n\nTeacher only.\n\nAfter.\n'
    kept_gap = 'Before.\n\n\nAfter.\n'
    assert filter_edition_blocks(kept_gap, 'student') == kept_gap
    for edition in EDITIONS:
        assert '\n\n\n' not in filter_edition_blocks(LIST_WITH_BLOCKS, edition)


@pytest.mark.parametrize('text,message', [
    ('<!-- edition: studnet -->\nx\n<!-- /edition -->\n', 'unknown edition studnet'),
    ('<!-- edition: student -->\nx\n', 'never closed'),
    ('x\n<!-- /edition -->\n', 'closed but never opened'),
    ('<!-- edition: student -->\n<!-- edition: teacher -->\nx\n<!-- /edition -->\n', 'opened inside'),
    ('<!-- edition student -->\nx\n<!-- /edition -->\n', 'malformed'),
    ('<!--edition: student-->\nx\n<!-- /edition -->\n', 'malformed'),
])
def test_bad_edition_markers_fail(text, message):
    with pytest.raises(ValueError, match=message):
        filter_edition_blocks(text, 'student')


def test_real_how_to_use_filters_for_every_edition():
    source = (REPO / 'python-concepts' / 'front-matter' / 'how-to-use.md').read_text(encoding='utf-8')
    texts = {edition: filter_edition_blocks(source, edition) for edition in EDITIONS}
    assert all('<!--' not in text for text in texts.values())
    full_starter = '- **Starter:** A beginning for your exercise program'
    assert full_starter not in texts['student-print'] and 'exercises notebook' in texts['student-print']
    assert full_starter in texts['student'] and full_starter in texts['teacher']
    assert 'Answers to Selected Exercises' not in texts['student-print']
    assert "Teacher's Edition" not in texts['student-print'] + texts['student']


# --- the print Starter rule -----------------------------------------------------------------

def test_redundant_starter_rule():
    statement = '### T\n\n```python\nclub = "Crew"\nwhile i < 5:\n    print(i)\n```'
    assert redundant_starter('# Write your code here.\npass\n', statement)
    assert redundant_starter('   \n', statement)
    assert redundant_starter('club = "Crew"\n\n# Print it.\n', statement)
    assert redundant_starter('while i < 5:\n        print(i)\n', statement)  # indentation ignored
    assert not redundant_starter('club = "Crew"\nprint(club)\n', statement)
    assert not redundant_starter('import random\n', statement)


def _exercises(entry: Path) -> None:
    nbformat.write(nbformat.v4.new_notebook(cells=[
        md('# Practice'),
        md('## Exercise 1'),
        md('### Given Values\n\nSpec.\n\n```python\nclub = "Crew"\n```'),
        code('club = "Crew"\n\n# Print the sign.', id='starter-redundant'),
        md('## Exercise 2'),
        md('### Empty\n\nSpec.'),
        code('', id='starter-empty'),
        md('## Exercise 3'),
        md('### Repair It\n\nRepair the broken program below. Put the repair in an empty cell.'),
        code('name = "Ada"\nprint(f"Hi {nam}")', id='broken-program'),
        code('', id='repair-cell'),
    ]), entry / 'exercises.ipynb')


def test_print_omits_redundant_starters_keeps_required_and_drops_answer_refs(tmp_path):
    entry = tmp_path / 'units' / 'unit-01-fixture'
    entry.mkdir(parents=True)
    _exercises(entry)
    full, full_inventory, items = render_items(entry / 'exercises.ipynb', 'unit', 'student', entry, entry.name)
    lean, lean_inventory, lean_items = render_items(entry / 'exercises.ipynb', 'unit', 'student-print', entry,
                                                    entry.name)
    assert items == lean_items
    assert full.count('::: {.starter}') == 2 and lean.count('::: {.starter}') == 1
    assert 'print(f"Hi {nam}")' in lean and '# Print the sign.' not in lean
    assert [(r['id'], r['kind']) for r in lean_inventory] == [
        ('starter-redundant', 'starter-omitted'), ('starter-empty', 'starter-omitted'),
        ('broken-program', 'starter'), ('repair-cell', 'starter-omitted')]
    assert {r['kind'] for r in full_inventory} == {'starter'}
    assert 'Answer on page \\pageref{ans:unit-01-fixture:1}.' in full
    assert 'Answer on page' not in lean and '\\pageref' not in lean
    assert '### Exercise 3 — Repair It' in lean and '### Exercise 2 — Empty' in lean
    starters = [(cell_id, source, kind) for cell_id, (kind, source) in
                publish_audit.starter_kinds(entry, 'unit', 'student-print').items()]
    assert [(i, k) for i, _, k in starters] == [(r['id'], r['kind']) for r in lean_inventory]
    assert publish_audit.print_equivalence_findings('u1', full, lean, starters) == []
    assert publish_audit.starter_panel_findings('u1', lean, starters) == []


def test_print_audit_sentinels_catch_drift(tmp_path):
    entry = tmp_path / 'units' / 'unit-01-fixture'
    entry.mkdir(parents=True)
    _exercises(entry)
    full, _, _ = render_items(entry / 'exercises.ipynb', 'unit', 'student', entry, entry.name)
    lean, _, _ = render_items(entry / 'exercises.ipynb', 'unit', 'student-print', entry, entry.name)
    starters = [(cell_id, source, kind) for cell_id, (kind, source) in
                publish_audit.starter_kinds(entry, 'unit', 'student-print').items()]
    edited = lean.replace('Spec.', 'Changed spec.', 1)
    assert publish_audit.print_equivalence_findings('u1', full, edited, starters)
    kept_missing = lean.replace('print(f"Hi {nam}")', 'print("Hi")')
    assert publish_audit.starter_panel_findings('u1', kept_missing, starters)
    omitted_printed = full.replace('Answer on page', 'See page')
    assert publish_audit.starter_panel_findings('u1', omitted_printed, starters)
    assert publish_audit.print_equivalence_findings('u1', full, omitted_printed, starters)


def test_real_unit1_exercise20_broken_program_stays_in_print():
    entry = REPO / 'python-concepts' / 'units' / 'unit-01-output-and-variables'
    body, inventory, _ = render_items(entry / 'exercises.ipynb', 'unit', 'student-print', entry, entry.name)
    kinds = {record['id']: record['kind'] for record in inventory}
    assert kinds['057d796ebeff'] == 'starter'
    assert publish_audit.PRINT_REQUIRED_STARTERS <= set(kinds)
    assert 'print("Room: + room_name)' in body
    assert list(kinds.values()).count('starter-omitted') > 20


# --- whole-edition builds -------------------------------------------------------------------

SENTINELS = ('TEACHER_NOTE_SENTINEL_90', 'EVEN_SOLUTION_SENTINEL_90', 'CHECKPOINT_SOLUTION_SENTINEL_90',
             'SETUP_TEACHER_SENTINEL_90', 'FOR_TEACHERS_SENTINEL_90')


@pytest.fixture
def book(tmp_path):
    (tmp_path / 'books.yaml').write_text('books_version: 2\nbooks:\n- id: python-concepts\n  root: python-concepts\n  title: Python, Concept by Concept\n  subtitle: Learn Python one idea at a time\n  publication: true\n')
    root = tmp_path / 'python-concepts'
    (root / 'docs').mkdir(parents=True)
    (root / 'docs' / 'unit-00-getting-set-up.md').write_text(
        '# Unit 0 — Getting Set Up\n\nGet ready.\n\n## Install Python\n\nStart.\n')
    (root / 'docs' / 'unit-00-teacher-notes.md').write_text('# Notes\n\nSETUP_TEACHER_SENTINEL_90\n')
    front = root / 'front-matter'
    front.mkdir()
    (front / 'preface.md').write_text('# About This Book\n')
    (front / 'how-to-use.md').write_text(LIST_WITH_BLOCKS)
    (front / 'for-teachers.md').write_text('# For Teachers\n\nFOR_TEACHERS_SENTINEL_90\n')
    (front / 'answer-key-intro.md').write_text(
        '# Using This Answer Key\n\n## Try first\n\nTry first.\n<!-- edition: student -->\nNOT_IN_KEY\n<!-- /edition -->\n')
    back = root / 'back-matter'
    back.mkdir()
    (back / 'glossary.md').write_text('# Glossary\n')
    (back / 'quick-reference.md').write_text('# Quick Reference\n')
    (root / 'syllabus.md').write_text(
        '# Python, Concept by Concept — Syllabus\n\n| entry | kind | lessons | the hook |\n|---|---|---|---|\n'
        '| `unit-01-fixture` | unit | 1 | Hook. |\n'
        '| `checkpoint-01-fixture` | checkpoint | 1 | Test. |\n')
    unit = root / 'units' / 'unit-01-fixture'
    (unit / 'assets').mkdir(parents=True)
    (unit / 'teacher-notes.md').write_text('# Notes\n\nTEACHER_NOTE_SENTINEL_90\n')
    nbformat.write(nbformat.v4.new_notebook(cells=[
        md('# Signs\n\nA hook.'), md('## Lesson 1\n\nText.'),
        code('print("hi")', outputs=[nbformat.v4.new_output('stream', name='stdout', text='hi\n')])]),
        unit / 'lesson.ipynb')
    _exercises(unit)
    nbformat.write(nbformat.v4.new_notebook(cells=[
        md('# Signs Solutions'), md('> **Note for teachers:** TEACHER_NOTE_SENTINEL_90'),
        md('## Exercise 1\n\n### Given Values'), code('club = "Crew"\nprint(club)\nassert club == "Crew"'),
        md('## Exercise 2\n\n### Empty'), code('print("EVEN_SOLUTION_SENTINEL_90")'),
        md('## Exercise 3\n\n### Repair It'), code('name = "Ada"\nprint(f"Hi {name}")'),
    ]), unit / 'solutions.ipynb')
    (unit / 'assets' / 'solutions_ex2.py').write_text('print("EVEN_SOLUTION_SENTINEL_90")\n')
    checkpoint = root / 'checkpoints' / 'checkpoint-01-fixture'
    checkpoint.mkdir(parents=True)
    (checkpoint / 'teacher-notes.md').write_text('# Notes\n\nTEACHER_NOTE_SENTINEL_90\n')
    nbformat.write(nbformat.v4.new_notebook(cells=[
        md('# Checkpoint 1: Fixture\n\nTest.'), md('## Question 1'), md('### Q\n\nDo it.'), code('# answer')]),
        checkpoint / 'checkpoint.ipynb')
    nbformat.write(nbformat.v4.new_notebook(cells=[
        md('# Solutions'), md('## Question 1\n\n### Q'), code('print("CHECKPOINT_SOLUTION_SENTINEL_90")')]),
        checkpoint / 'solutions.ipynb')
    return tmp_path


def _project_text(project: Path) -> str:
    return '\n'.join(path.read_text() for path in sorted(project.rglob('*')) if path.is_file()
                     and path.suffix in {'.qmd', '.yml', '.json', '.tex'})


def test_answer_key_edition_contents_and_source_boundary(book, monkeypatch):
    opened = []
    real_read = publish.read_source
    real_notebook = publish.notebook

    def spy_read(path, edition):
        opened.append(Path(path).name)
        return real_read(path, edition)

    def spy_notebook(path, edition):
        opened.append(Path(path).name)
        return real_notebook(path, edition)

    monkeypatch.setattr(publish, 'read_source', spy_read)
    monkeypatch.setattr(publish, 'notebook', spy_notebook)
    project = build(book, 'python-concepts', 'answer-key')
    assert set(opened) <= {'syllabus.md', 'answer-key-intro.md', 'lesson.ipynb', 'exercises.ipynb'}
    chapters = json.loads((project / 'inventory.json').read_text())['chapters']
    assert [(c['id'], c['kind']) for c in chapters] == [
        ('answer-key-intro', 'front'), ('answers-unit-01-fixture', 'answers')]
    assert publish_audit.expected_chapter_ids('answer-key', ['unit-01-fixture', 'checkpoint-01-fixture']) == [
        c['id'] for c in chapters]
    text = _project_text(project)
    for sentinel in SENTINELS:
        assert sentinel not in text
    assert '::: {.teacher}' not in text and '## Answer key' not in text and 'NOT_IN_KEY' not in text
    answers = (project / 'answers-unit-01-fixture.qmd').read_text()
    assert answers.startswith('# Unit 1 — Signs {pub-label="Unit 1" pub-mainmatter="true"}')
    assert '### Unit 1, Exercise 1 — Given Values\n' in answers
    assert '### Unit 1, Exercise 3 — Repair It\n' in answers
    assert 'Exercise 2' not in answers and 'Check: `club` → `"Crew"`' in answers
    assert '\\pageref' not in text and '\\label{ans:' not in text
    assert publish_audit.answer_coverage_findings(answers, [(1, 1), (1, 3)]) == []
    assert not (project / 'glossary.qmd').exists() and not (project / 'the-index.qmd').exists()
    config = (project / '_quarto.yml').read_text()
    assert 'output-file: "python-concepts-answer-key"' in config and 'classoption: [open=any, headings=normal]' in config
    assert config.split('chapters:')[1].split('format:')[0].split() == [
        '-', 'index.qmd', '-', 'answers-unit-01-fixture.qmd']
    assert '\\date{Answer Key}' in (project / 'theme' / 'theme.tex').read_text()
    assert publish_audit.leak_findings(book, 'python-concepts', chapters, project, 'answer-key') == []


def _key_equivalence(book, key_qmd):
    full = (book / 'python-concepts' / 'build' / 'publish' / 'student' / 'answers.qmd').read_text()
    return publish_audit.answer_key_equivalence_findings(
        'answers-unit-01-fixture', 1, key_qmd, full, 'Signs', {1: 'Given Values', 2: 'Empty', 3: 'Repair It'},
        mainmatter=True)


def test_answer_key_equals_the_full_edition_appendix(book):
    build(book, 'python-concepts', 'student')
    project = build(book, 'python-concepts', 'answer-key')
    key = (project / 'answers-unit-01-fixture.qmd').read_text()
    assert _key_equivalence(book, key) == []
    changed_title = key.replace('— Repair It', '— Fix It')
    assert any('Exercise 3 title differs' in f for f in _key_equivalence(book, changed_title))
    prose = key.replace('### Unit 1, Exercise 3', 'Ask for help if stuck.\n\n### Unit 1, Exercise 3')
    assert any('Exercise 1 answer differs' in f for f in _key_equivalence(book, prose))
    heading_prose = key.replace('```{=latex}', 'A note for the class.\n\n```{=latex}', 1)
    assert any('heading block' in f for f in _key_equivalence(book, heading_prose))
    even = key.replace('### Unit 1, Exercise 3',
                       '### Unit 1, Exercise 2 — Empty\n\n```python\nprint(2)\n```\n\n### Unit 1, Exercise 3')
    assert any('entries differ' in f for f in _key_equivalence(book, even))
    hidden_even = key.replace('### Unit 1, Exercise 3', '#### Exercise 2\n\nprint(2)\n\n### Unit 1, Exercise 3')
    assert _key_equivalence(book, hidden_even)


def test_answer_key_boundary_denies_teacher_and_solution_sources():
    for name in ('teacher-notes.md', 'solutions.ipynb', 'for-teachers.md', 'preface.md', 'how-to-use.md',
                 'checkpoint.ipynb', 'brief.ipynb', 'glossary.md'):
        assert not allowed_source(Path('python-concepts/x') / name, 'answer-key'), name
    assert not allowed_source(Path('python-concepts/units/u/assets/solutions_ex1.py'), 'answer-key')
    assert not allowed_source(Path('python-concepts/units/u/assets/l1.py'), 'answer-key')
    assert allowed_source(Path('python-concepts/front-matter/answer-key-intro.md'), 'answer-key')
    assert not allowed_source(Path('python-concepts/front-matter/answer-key-intro.md'), 'student')
    assert not allowed_source(Path('python-concepts/front-matter/answer-key-intro.md'), 'bogus')
    for edition in ('student', 'student-print'):
        assert not allowed_source(Path('python-concepts/units/u/solutions.ipynb'), edition)
        assert not allowed_source(Path('python-concepts/units/u/teacher-notes.md'), edition)


def test_answer_key_leak_guard_catches_even_and_checkpoint_solutions(book):
    project = build(book, 'python-concepts', 'answer-key')
    chapters = json.loads((project / 'inventory.json').read_text())['chapters']
    path = project / 'answers-unit-01-fixture.qmd'
    path.write_text(path.read_text() + '\n```python\nprint("EVEN_SOLUTION_SENTINEL_90")\n```\n'
                    + '\n```python\nprint("CHECKPOINT_SOLUTION_SENTINEL_90")\n```\n')
    findings = publish_audit.leak_findings(book, 'python-concepts', chapters, project, 'answer-key')
    assert 'FAIL: answer-key: answers: solution leak from unit-01-fixture Exercise 2' in findings
    assert 'FAIL: answer-key: answers: solution leak from checkpoint-01-fixture Question 1' in findings


def test_print_and_full_editions_from_the_profile(book):
    lean = build(book, 'python-concepts', 'student-print')
    full = build(book, 'python-concepts', 'student')
    teacher = build(book, 'python-concepts', 'teacher')
    entry_order = ['unit-01-fixture', 'checkpoint-01-fixture']
    for edition, project in (('student-print', lean), ('student', full), ('teacher', teacher)):
        chapters = json.loads((project / 'inventory.json').read_text())['chapters']
        assert [c['id'] for c in chapters] == publish_audit.expected_chapter_ids(edition, entry_order)
        config = (project / '_quarto.yml').read_text()
        files = config.split('chapters:')[1].split('format:')[0].split()[1::2]
        assert files == publish_audit.expected_quarto_files(edition, entry_order)
        assert f'output-file: "python-concepts-{edition}"' in config
        assert output_stem('python-concepts', edition) == f'python-concepts-{edition}'
        assert 'title: "Python, Concept by Concept"' in config
        assert 'subtitle: "Learn Python one idea at a time"' in config
        theme = (project / 'theme' / 'theme.tex').read_text()
        assert ('\\uppertitleback{Python, Concept by Concept\\\\Learn Python one idea at a time'
                '\\\\First edition, 2026}') in theme
        assert '(folder python-concepts/)' in theme and '@TITLE@' not in theme
        assert f'classoption: [{EDITIONS[edition]["classoption"]}, headings=normal]' in config
        assert '\\date{' + EDITIONS[edition]['edition_label'] + '}' in (project / 'theme' / 'theme.tex').read_text()
    assert not (lean / 'answers.qmd').exists() and (full / 'answers.qmd').exists()
    lean_text, full_text = _project_text(lean), _project_text(full)
    assert '\\pageref' not in lean_text and 'Answer on page' not in lean_text
    assert 'Answer on page' in full_text
    for sentinel in SENTINELS:
        assert sentinel not in lean_text
    assert 'club = "Crew"\nprint(club)' not in lean_text  # no solution at all in print
    assert '- **Program:** code.\n- **Check lines:** checks.' in (lean / 'how-to-use.qmd').read_text()
    assert '- **Starter:** full.' in (full / 'how-to-use.qmd').read_text()
    assert '- **Starter:** teacher.' in (teacher / 'how-to-use.qmd').read_text()
    chapters = json.loads((lean / 'inventory.json').read_text())['chapters']
    assert publish_audit.leak_findings(book, 'python-concepts', chapters, lean, 'student-print', hide_odd=True,
                                       kinds=frozenset({'unit', 'checkpoint', 'front', 'setup'})) == []
    unit = next(c for c in chapters if c['id'] == 'unit-01-fixture')
    starters = [(cell_id, source, kind) for cell_id, (kind, source) in
                publish_audit.starter_kinds(book / unit['source'], 'unit', 'student-print').items()]
    assert publish_audit.print_equivalence_findings(
        unit['id'], (full / unit['file']).read_text(), (lean / unit['file']).read_text(), starters) == []


def test_unknown_edition_marker_fails_the_build(book):
    path = book / 'python-concepts' / 'front-matter' / 'how-to-use.md'
    path.write_text(path.read_text() + '<!-- edition: online -->\nx\n<!-- /edition -->\n')
    with pytest.raises(ValueError, match='unknown edition online'):
        build(book, 'python-concepts', 'student')
    with pytest.raises(ValueError, match='edition must be one of'):
        build(book, 'python-concepts', 'ebook')


# --- audit rules ----------------------------------------------------------------------------

def test_phrase_bans_are_edition_specific():
    text = 'Answers are in the separate Answer Key.'
    assert publish_audit.student_phrase_findings(text, 'how-to-use.qmd') == [
        'FAIL: student: how-to-use.qmd: banned phrase Answer key']
    assert publish_audit.student_phrase_findings(text, 'how-to-use.qmd', 'student-print') == []
    assert publish_audit.student_phrase_findings(text, 'index.qmd', 'answer-key') == []
    for edition in ('student', 'student-print', 'answer-key'):
        assert publish_audit.student_phrase_findings("Ask your teacher's help", 'x', edition)
    assert publish_audit.student_phrase_findings('assert x', 'answers-unit-01.qmd', 'answer-key', answers=True)


def test_leak_guard_scans_every_answers_kind_chapter(tmp_path, monkeypatch):
    project = tmp_path
    (project / 'a.qmd').write_text('```python\nprint("hidden solution")\n```\n')
    chapters = [{'id': 'answers-unit-01-x', 'kind': 'answers', 'file': 'a.qmd'}]
    entry = tmp_path / 'python-concepts' / 'units' / 'unit-01-x'
    entry.mkdir(parents=True)
    nbformat.write(nbformat.v4.new_notebook(cells=[
        md('# S'), md('## Exercise 1'), code('print("odd")'), md('## Exercise 2'),
        code('print("hidden solution")')]), entry / 'solutions.ipynb')
    monkeypatch.setattr(publish_audit, 'entries', lambda book, edition: [('unit-01-x', entry)])
    assert publish_audit.leak_findings(tmp_path, 'python-concepts', chapters, project, 'answer-key') == [
        'FAIL: answer-key: answers: solution leak from unit-01-x Exercise 2']
    (project / 'a.qmd').write_text('```python\nprint("odd")\n```\n')
    assert publish_audit.leak_findings(tmp_path, 'python-concepts', chapters, project, 'answer-key') == []
    assert publish_audit.leak_findings(tmp_path, 'python-concepts', chapters, project, 'student-print', hide_odd=True) == [
        'FAIL: student-print: answers: solution leak from unit-01-x Exercise 1']


# --- output/ ownership ----------------------------------------------------------------------

def _pdf(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'%PDF-1.5 ' + path.name.encode())
    return path


def test_output_scripts_replace_only_their_own_files(tmp_path):
    build_dir = tmp_path / 'python-concepts' / 'build'
    handout = _pdf(build_dir / 'handouts' / 'unit-01-a.pdf')
    syllabus = _pdf(build_dir / 'syllabus.pdf')
    refresh_output(tmp_path, 'python-concepts', 'pdf', [handout, syllabus])
    out = tmp_path / 'output' / 'python-concepts'
    _pdf(out / 'python-concepts-student-old.pdf')  # a renamed edition from an earlier build
    student = _pdf(build_dir / 'publish' / 'student' / '_book' / 'python-concepts-student.pdf')
    key = _pdf(build_dir / 'publish' / 'answer-key' / '_book' / 'python-concepts-answer-key.pdf')
    refresh_output(tmp_path, 'python-concepts', 'book', [student, key])
    assert sorted(p.relative_to(out).as_posix() for p in out.rglob('*.pdf')) == [
        'handouts/unit-01-a.pdf', 'python-concepts-answer-key.pdf', 'python-concepts-student.pdf', 'syllabus.pdf']
    (out / 'handouts' / 'unit-99-removed.pdf').write_bytes(b'stale')
    new_handout = _pdf(build_dir / 'handouts' / 'unit-02-b.pdf')
    refresh_output(tmp_path, 'python-concepts', 'pdf', [new_handout, syllabus])
    assert sorted(p.relative_to(out).as_posix() for p in out.rglob('*.pdf')) == [
        'handouts/unit-02-b.pdf', 'python-concepts-answer-key.pdf', 'python-concepts-student.pdf', 'syllabus.pdf']
    with pytest.raises(ValueError, match='owns only'):
        refresh_output(tmp_path, 'python-concepts', 'book', [syllabus])
    with pytest.raises(ValueError, match='owns only'):
        refresh_output(tmp_path, 'python-concepts', 'pdf', [student])
    with pytest.raises(ValueError, match='missing or empty'):
        refresh_output(tmp_path, 'python-concepts', 'book', [build_dir / 'python-concepts-nothing.pdf'])
    assert (out / 'python-concepts-student.pdf').exists()  # a failed refresh deletes nothing


def test_output_readme_and_gitignore_cover_every_file():
    readme = (REPO / 'output' / 'README.md').read_text()
    for edition in EDITIONS:
        assert f'`python-concepts-{edition}.pdf`' in readme
    for name in ('syllabus.pdf', 'patterns.pdf', 'handouts/<unit>.pdf',
                 'scripts/build-book.sh', 'scripts/build-pdf.sh'):
        assert name in readme
    assert 'output/**/*.pdf' in (REPO / '.gitignore').read_text().splitlines()
    assert 'tools.publish_output --book "$book" --owner book' in (REPO / 'scripts' / 'build-book.sh').read_text()
    assert 'tools.publish_output --book "$book" --owner pdf' in (REPO / 'scripts' / 'build-pdf.sh').read_text()


# --- CLI ------------------------------------------------------------------------------------

def test_cli_edition_choices_match_the_profile(capsys):
    assert cli.EDITION_CHOICES == tuple(sorted(EDITIONS, key=cli.EDITION_CHOICES.index))
    assert set(cli.EDITION_CHOICES) == set(EDITIONS)
    for edition in EDITIONS:
        assert cli._parser().parse_args(['--book', 'python-concepts', 'publish', '--edition', edition]).edition == edition
    assert cli.main(['--book', 'python-concepts', 'publish', '--edition', 'ebook']) == 2
    assert 'invalid choice' in capsys.readouterr().err


def test_theme_layout_guards():
    theme = (REPO / 'tools' / 'publish_theme' / 'theme.tex').read_text()
    lua = (REPO / 'tools' / 'publish_theme' / 'panels.lua').read_text()
    # open=any editions start Unit 1 on the next page; open=right keeps the odd-page start.
    assert r'\if@openright\puboriginalmainmatter\else\clearpage' in theme
    # A chapter's short last box takes under four extra lines instead of a page of its own.
    assert r'\newcommand{\pubfinalbox}' in theme and r'\ifdim\dimen@<4\baselineskip' in theme
    assert r'code={\ifpubfinalbox\tcbset{unbreakable}\fi}' in theme
    assert "'\\\\pubfinalbox{'" in lua and 'lines <= 3 and chapter_end' in lua
    # The heading-less the-index.qmd no longer yields an empty chapter (a blank page).
    assert 'el.level == 1 and #el.content == 0 then return {}' in lua
