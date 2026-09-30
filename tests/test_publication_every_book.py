"""Plan 097 Phase D: the publication pipeline for every book (design 010 D1-D3).

Fixture books under tmp_path: a python-concepts-style item, a heading-body item (*Python by Projects*
style), a judge programming item with Input/Constraints/Sample sections and a `_Division:_` line, and a
short-answer item with a `**Your answer:**` placeholder whose solution has a `verify` cell and an
`**Answer:**` line. Plus the per-book config, the source boundary, stdin programs, lesson headings,
checkpoint and Problem titles, project running headers and scoped phrase exemptions.
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import nbformat
import pytest
from publication_helpers import MINIMAL_CONFIG, fixture_config, write_publication_config

from tools import cli, publish, publish_audit
from tools.books import PublicationConfigError, publication_config, publication_config_errors
from tools.publish import allowed_source, build, entries, route_code

md = nbformat.v4.new_markdown_cell
code = nbformat.v4.new_code_cell

EX3_MIRROR = ('import sys\n\n# EX3_MIRROR_SENTINEL\ndata = sys.stdin.read().split()\n'
              'print(sum(int(x) for x in data[1:]))\n')
EX2_SOLUTION = 'print("EVEN_EX2_SENTINEL")\n'
Q1_MIRROR = 'import sys\n\n# Q1_MIRROR_SENTINEL\nprint(len(sys.stdin.read().split()))\n'
P1_MIRROR = 'import sys\n\n# P1_MIRROR_SENTINEL\nprint(sys.stdin.read().strip())\n'
CONTEST_CONFIG = """\
setup:
  source: docs/getting-set-up.md
  teacher_notes: docs/getting-set-up-teacher-notes.md
  numbered: false
project_headers:
  project-01-fixture: Mock Contest
lesson_heading: '^## L\\d+:'
index_names: [print, len]
audit:
  goals_recap: required
"""
JUDGE_HEADING = (
    '## Exercise 3\n\n_Division: Junior and above._\n\n### Sum Pair\n\n'
    'JUDGE_STATEMENT_SENTINEL: print the sum of the values.\n\n'
    '**Notice:** the values can repeat.\n\n'
    '### Input\n\nThe first line is `N`; then `N` integers follow.\n\n'
    '### Constraints\n\n- `1 <= N <= 10`\n\n'
    '### Sample Input 1\n\n```text\n2\n3 4\n```\n\n'
    '### Sample Output 1\n\n```text\n7\n```')


def _nb(path: Path, *cells) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nbformat.v4.new_notebook(cells=list(cells)), path)


@pytest.fixture
def contest(tmp_path):
    """A judge-style book: an unnumbered setup chapter, a `| # |` syllabus, `## L1:` lessons."""
    (tmp_path / 'books.yaml').write_text(
        'books_version: 2\nbooks:\n- id: contest\n  root: contest\n  title: Contest Fixture\n'
        '  subtitle: Every book\n  publication: true\n  judge: true\n', encoding='utf-8')
    root = tmp_path / 'contest'
    (root / 'docs').mkdir(parents=True)
    (root / 'docs' / 'getting-set-up.md').write_text(
        '# Getting Set Up\n\nRun programs with input files.\n\n## Run a program\n\nUse a terminal.\n')
    (root / 'docs' / 'getting-set-up-teacher-notes.md').write_text('# Notes\n\nSETUP_NOTES_SENTINEL\n')
    front = root / 'front-matter'
    front.mkdir()
    for name, title in (('preface.md', 'About This Book'), ('how-to-use.md', 'How to Use This Book'),
                        ('for-teachers.md', 'For Teachers'), ('answer-key-intro.md', 'Using This Answer Key')):
        (front / name).write_text(f'# {title}\n\nText.\n')
    back = root / 'back-matter'
    back.mkdir()
    (back / 'glossary.md').write_text('# Glossary\n')
    (back / 'quick-reference.md').write_text('# Quick Reference\n')
    (root / 'syllabus.md').write_text(
        '# Syllabus\n\n| # | Entry | Kind | Lessons | The hook |\n|---|---|---|---|---|\n'
        '| 1 | `unit-01-fixture` | unit | 1 | Hook. |\n'
        '| 2 | `checkpoint-01-fixture` | checkpoint | 1 | Test. |\n'
        '| 3 | `project-01-fixture` | project | 1 | Mock. |\n')
    (root / 'publication.yaml').write_text(CONTEST_CONFIG)

    unit = root / 'units' / 'unit-01-fixture'
    (unit / 'assets' / 'verify').mkdir(parents=True)
    (unit / 'teacher-notes.md').write_text('# Notes\n\nUNIT_NOTES_SENTINEL\n')
    (unit / 'assets' / 'ex3.py').write_text(EX3_MIRROR)
    (unit / 'assets' / 'ex2.py').write_text(EX2_SOLUTION)
    (unit / 'assets' / 'ex2_start.py').write_text('# STARTER_FILE_SENTINEL\n')
    (unit / 'assets' / 'verify' / 'check.py').write_text('VERIFY_MODULE = 1\n')
    _nb(unit / 'lesson.ipynb',
        md('# Unit 1 — Reading Input\n\nA hook.'),
        md('### You will learn\n\n- Read input.'),
        md('## L1: Read the whole input\n\nText.'),
        code('import sys\ndata = sys.stdin.read()\nprint(data)', metadata={'tags': ['no-exec']}, id='stdin01'),
        md('### Recap\n\n- Read input.'))
    _nb(unit / 'exercises.ipynb',
        md('# Practice'),
        md('## Exercise 1'), md('### Concept Style\n\nCONCEPT_STATEMENT_SENTINEL.'), code('# starter', id='s1'),
        md('## Exercise 2\n\nHEADING_BODY_SENTINEL: open assets/ex2_start.py and finish it.'),
        code('', id='s2'),
        md(JUDGE_HEADING), code('', id='s3'),
        md('## Exercise 4\n\n_Division: Elementary and above._\n\n### Binary\n\nWhat is 101₂ in base 10?',
           metadata={'tags': ['short-answer']}),
        md('**Your answer:** _(write your answer here)_'))
    _nb(unit / 'solutions.ipynb',
        md('# Solutions\n\nEach program is also saved as assets/exN.py.'),
        md('## Exercise 1'), code('print("odd one")'),
        md('## Exercise 2'), code(EX2_SOLUTION, metadata={'tags': ['no-exec']}),
        md('## Exercise 3'), md('**Notice:** add as you read.'),
        code(EX3_MIRROR, metadata={'tags': ['no-exec']}),
        md('## Exercise 4'), md('Add the places that hold a 1: 4 + 1 = 5.\n\n**Answer:** `5`'),
        code('assert str(int("101", 2)) == "5"  # VERIFY_SENTINEL', metadata={'tags': ['verify']}))

    checkpoint = root / 'checkpoints' / 'checkpoint-01-fixture'
    (checkpoint / 'assets').mkdir(parents=True)
    (checkpoint / 'assets' / 'q1.py').write_text(Q1_MIRROR)
    (checkpoint / 'teacher-notes.md').write_text('# Notes\n\nCP_NOTES_SENTINEL\n')
    _nb(checkpoint / 'checkpoint.ipynb',
        md('# Checkpoint 1 — Mock Round\n\nTimed.'),
        md('## Question 1\n\n### Count Tokens\n\nPrint how many tokens the input has.'), code('', id='q1s'),
        md('## Question 2\n\n### Octal\n\nWhat is 17₈ in base 10?'), md('**Your answer:** _(here)_'))
    _nb(checkpoint / 'solutions.ipynb',
        md('# Solutions'),
        md('## Question 1'), code(Q1_MIRROR, metadata={'tags': ['no-exec']}),
        md('## Question 2'), md('One eight and seven ones.\n\n**Answer:** `15`'),
        code('assert 8 + 7 == 15  # VERIFY_SENTINEL', metadata={'tags': ['verify']}))

    project = root / 'projects' / 'project-01-fixture'
    (project / 'assets').mkdir(parents=True)
    (project / 'assets' / 'p1.py').write_text(P1_MIRROR)
    (project / 'teacher-notes.md').write_text('# Notes\n')
    _nb(project / 'brief.ipynb',
        md('# Grand Mock Contest\n\nEight problems.'),
        md('### Problem 1 — Ledger  *(prefix sums)*\n\nPROBLEM_STATEMENT_SENTINEL.'), code('', id='p1s'))
    _nb(project / 'solutions.ipynb',
        md('# Solutions'), md('## Problem 1'), code(P1_MIRROR, metadata={'tags': ['no-exec']}))
    return tmp_path


def _qmd(project: Path) -> str:
    return '\n'.join(path.read_text(encoding='utf-8') for path in sorted(project.glob('*.qmd')))


def _unit(project: Path) -> str:
    return (project / 'unit-01-fixture.qmd').read_text(encoding='utf-8')


# --- D2: item rendering ---------------------------------------------------------------------

def test_statements_titles_subheads_division_and_no_placeholder(contest):
    project = build(contest, 'contest', 'student')
    unit = _unit(project)
    items = json.loads((project / 'inventory.json').read_text())['chapters']
    titles = {c['id']: [(i['number'], i['title']) for i in c['items']] for c in items if c['items']}
    assert titles['unit-01-fixture'] == [(1, 'Concept Style'), (2, ''), (3, 'Sum Pair'), (4, 'Binary')]
    # (a) python-concepts style, (b) heading-body, (c) judge: every statement is present.
    for sentinel in ('CONCEPT_STATEMENT_SENTINEL', 'HEADING_BODY_SENTINEL', 'JUDGE_STATEMENT_SENTINEL'):
        assert sentinel in unit
    assert '### Exercise 1 — Concept Style\n' in unit and '### Exercise 2\n' in unit
    assert '### Exercise 3 — Sum Pair\n' in unit and '### Exercise 4 — Binary\n' in unit
    for line in ('### Sum Pair', '### Binary', '## Exercise 3'):
        assert line not in unit.splitlines()
    # Structural sections are run-in subheads (prefix match: "Sample Input 1"); samples stay code.
    assert '**Input.** The first line is `N`' in unit
    assert '**Constraints**\n\n- `1 <= N <= 10`' in unit
    assert '**Sample Input 1**\n\n```text\n2\n3 4\n```' in unit
    assert '**Sample Output 1**\n\n```text\n7\n```' in unit
    assert '### Input' not in unit and '### Sample' not in unit and '### Constraints' not in unit
    # The division line is a tag, placed right after the heading; the placeholder prints nothing.
    assert '[Division: Junior and above]{.division}' in unit
    assert '[Division: Elementary and above]{.division}' in unit
    assert unit.index('### Exercise 3 — Sum Pair') < unit.index('[Division: Junior and above]') < unit.index(
        'JUDGE_STATEMENT_SENTINEL')
    assert '_Division:' not in unit and 'Your answer' not in unit
    assert 'What is 101₂ in base 10?' in unit
    # A Notice in a heading cell is a panel, and the audit's source count sees it.
    entry = contest / 'contest' / 'units' / 'unit-01-fixture'
    assert unit.count('::: {.notice}') == publish_audit._expected_notices(entry) == 1
    chapter = next(c for c in items if c['id'] == 'unit-01-fixture')
    kinds = publish_audit.starter_kinds(entry, 'unit', 'student')
    assert [(r['id'], r['kind']) for r in chapter['inventory'] if r['id'] in kinds] == [
        (cell_id, kind) for cell_id, (kind, _) in kinds.items()]
    # A `exN_name.py` starter stays printable; `exN.py` is never listed.
    assert '**assets/ex2_start.py**' in unit and 'STARTER_FILE_SENTINEL' in unit


def test_problem_title_drops_topic_and_project_header_comes_from_config(contest):
    project = build(contest, 'contest', 'teacher')
    brief = (project / 'project-01-fixture.qmd').read_text()
    assert '#### Problem 1 — Ledger\n' in brief
    assert '*(prefix sums)*' not in brief  # the tag lived only on the heading line
    assert 'PROBLEM_STATEMENT_SENTINEL' in brief
    assert '\\chaptermark{Mock Contest}' in brief
    inventory = json.loads((project / 'inventory.json').read_text())['chapters']
    assert next(c for c in inventory if c['id'] == 'project-01-fixture')['items'] == [
        {'number': 1, 'title': 'Ledger'}]
    assert '### Problem 1\n' in brief  # the answer-key heading has no topic tag either


def test_checkpoint_titles_strip_colon_and_dash_forms(tmp_path):
    for heading in ('# Checkpoint 1 — Mock Round', '# Checkpoint 01: Mock Round'):
        entry = tmp_path / heading[-12:].replace(' ', '') / 'checkpoints' / 'checkpoint-01-fixture'
        _nb(entry / 'checkpoint.ipynb', md(heading + '\n\nTimed.'), md('## Question 1\n\n### Q\n\nDo it.'))
        body, _, _, _ = publish.render_chapter(entry, 'checkpoint', 'student', fixture_config())
        assert body.startswith('# Checkpoint 1 — Mock Round {pub-label="Checkpoint 1"}'), heading
        assert '\\chaptermark{Checkpoint 1 — Mock Round}' in body


def test_structural_rule_is_a_prefix_with_an_optional_number():
    for heading in ('Input', 'Output', 'Constraints', 'Sample Input', 'Sample Output 2', 'Example',
                    'Sample Input 1'):
        assert publish.structural(heading), heading
    for heading in ('Input from a person', 'Outputs and more', 'Sum Pair', 'Examples of loops'):
        assert not publish.structural(heading), heading
    group = {'cells': [md('## Exercise 1\n\n### Sample Input 1\n\n```text\n1\n```'), md('### Real Title\n\nx')]}
    assert publish.group_title(group, 'Exercise') == 'Real Title'


def test_project_without_a_configured_header_fails_loudly(contest):
    path = contest / 'contest' / 'publication.yaml'
    path.write_text(CONTEST_CONFIG.replace('  project-01-fixture: Mock Contest\n', '').replace(
        'project_headers:\n', 'project_headers: {}\n'))
    with pytest.raises(ValueError, match='no running header'):
        build(contest, 'contest', 'student')


def test_syllabus_accepts_a_leading_number_column(contest):
    assert [id_ for id_, _ in entries(contest / 'contest', 'student')] == [
        'unit-01-fixture', 'checkpoint-01-fixture', 'project-01-fixture']


# --- the setup chapter ------------------------------------------------------------------------

def test_setup_chapter_unnumbered_and_numbered(contest):
    project = build(contest, 'contest', 'teacher')
    setup = (project / 'getting-set-up.qmd').read_text()
    assert setup.startswith('# Getting Set Up {pub-label="" pub-mainmatter="true"}')
    assert '\\chaptermark{Getting Set Up}' in setup and 'SETUP_NOTES_SENTINEL' in setup
    chapters = json.loads((project / 'inventory.json').read_text())['chapters']
    assert [(c['id'], c['kind'], c['title']) for c in chapters if c['kind'] == 'setup'] == [
        ('getting-set-up', 'setup', 'Getting Set Up')]
    order = ['unit-01-fixture', 'checkpoint-01-fixture', 'project-01-fixture']
    assert [c['id'] for c in chapters] == publish_audit.expected_chapter_ids('teacher', order, 'getting-set-up')
    student = _qmd(build(contest, 'contest', 'student'))
    assert 'SETUP_NOTES_SENTINEL' not in student and 'UNIT_NOTES_SENTINEL' not in student
    # Numbered: the same source titled "Unit 0 — Getting Set Up" is required and rendered as Unit 0.
    config = fixture_config(setup_source='docs/getting-set-up.md', setup_numbered=True,
                            setup_teacher_notes='docs/getting-set-up-teacher-notes.md')
    with pytest.raises(ValueError, match='unexpected setup title'):
        publish.render_setup_chapter(contest / 'contest', 'student', config)
    source = contest / 'contest' / 'docs' / 'getting-set-up.md'
    source.write_text(source.read_text().replace('# Getting Set Up', '# Unit 0 — Getting Set Up'))
    body, _, _, title = publish.render_setup_chapter(contest / 'contest', 'student', config)
    assert body.startswith('# Unit 0 — Getting Set Up {pub-label="Unit 0" pub-mainmatter="true"}')
    assert title == 'Unit 0 — Getting Set Up'
    with pytest.raises(ValueError, match='unexpected setup title'):
        build(contest, 'contest', 'student')  # the config still says unnumbered


def test_outline_finds_the_setup_chapter_by_id_and_keeps_a_real_unit_zero(tmp_path):
    book = tmp_path / 'acsl'
    (book / 'docs').mkdir(parents=True)
    (book / 'docs' / 'getting-set-up.md').write_text('# Getting Set Up\n\n## Run a program\n\nText.\n')
    unit = book / 'units' / 'unit-00-foundations'
    _nb(unit / 'lesson.ipynb', md('# Unit 0 — Foundations\n\nHook.'), md('## Lesson 1: Bits\n\nText.'))
    _nb(unit / 'exercises.ipynb', md('# Practice'), md('## Exercise 1\n\n### Count\n\nDo it.'))
    chapters = [{'id': 'getting-set-up', 'kind': 'setup', 'title': 'Getting Set Up',
                 'source': 'acsl/docs/getting-set-up.md', 'items': []},
                {'id': 'unit-00-foundations', 'kind': 'unit', 'title': 'Unit 0 — Foundations',
                 'source': 'acsl/units/unit-00-foundations', 'items': [{'number': 1, 'title': 'Count'}]}]
    outline = ('+\t"Getting Set Up"\t#page=3\n|\t\t"Run a program"\t#page=3\n'
               '+\t"Unit 0 — Foundations"\t#page=5\n|\t\t"Lesson 1: Bits"\t#page=5\n'
               '|\t\t"Exercises"\t#page=6\n|\t\t\t"Exercise 1 — Count"\t#page=6\n')
    assert publish_audit._missing_lesson_headings(chapters, tmp_path, outline) == []
    # The real Unit 0's lesson heading is never read as a setup section, and vice versa.
    swapped = outline.replace('"Run a program"\t#page=3', '"Lesson 1: Bits"\t#page=3').replace(
        '|\t\t"Lesson 1: Bits"\t#page=5\n', '')
    assert publish_audit._missing_lesson_headings(chapters, tmp_path, swapped) == [
        'getting-set-up: Run a program', 'unit-00-foundations: Lesson 1: Bits']
    no_setup = outline.replace('"Getting Set Up"', '"Setup"')
    assert 'getting-set-up: Getting Set Up' in publish_audit._missing_lesson_headings(
        chapters, tmp_path, no_setup)


# --- D3: answers ------------------------------------------------------------------------------

def test_teacher_answers_short_answer_markdown_no_verify_and_mirror_once(contest):
    project = build(contest, 'contest', 'teacher')
    unit = _unit(project)
    key = unit.split('## Answer key', 1)[1]
    assert '**Answer:** `5`' in key and 'Add the places that hold a 1' in key
    assert '::: {.notice}\nAdd as you read.\n:::' in key  # answer markdown passes through markdown_blocks
    assert 'VERIFY_SENTINEL' not in _qmd(project) and 'assert str(int' not in unit
    # The judge answer is the solution notebook's mirror cell, printed once; the file never is.
    assert key.count('EX3_MIRROR_SENTINEL') == 1 and '**ex3.py**' not in unit
    # Checkpoint answers: the Teacher's Edition prints the mirror cell once and the short answer.
    checkpoint = (project / 'checkpoint-01-fixture.qmd').read_text()
    cp_key = checkpoint.split('## Answer key', 1)[1]
    assert cp_key.count('Q1_MIRROR_SENTINEL') == 1 and '**q1.py**' not in checkpoint
    assert '**Answer:** `15`' in cp_key and 'VERIFY_SENTINEL' not in checkpoint
    assert checkpoint.index('### Question 1 — Count Tokens') < checkpoint.index('## Answer key')
    brief = (project / 'project-01-fixture.qmd').read_text()
    assert brief.count('P1_MIRROR_SENTINEL') == 1 and '**p1.py**' not in brief


def test_student_editions_print_only_odd_unit_answers(contest):
    full = _qmd(build(contest, 'contest', 'student'))
    printed = _qmd(build(contest, 'contest', 'student-print'))
    key = _qmd(build(contest, 'contest', 'answer-key'))
    for text in (full, printed, key):
        assert 'EVEN_EX2_SENTINEL' not in text and 'VERIFY_SENTINEL' not in text
        assert 'Q1_MIRROR_SENTINEL' not in text and 'P1_MIRROR_SENTINEL' not in text
        assert '**Answer:** `15`' not in text  # checkpoint answers are Teacher's Edition only
    assert full.count('EX3_MIRROR_SENTINEL') == 1 and key.count('EX3_MIRROR_SENTINEL') == 1
    assert 'EX3_MIRROR_SENTINEL' not in printed
    answers = (contest / 'contest' / 'build' / 'publish' / 'student' / 'answers.qmd').read_text()
    assert '### Unit 1, Exercise 1 (page' in answers and '### Unit 1, Exercise 3 (page' in answers
    assert 'Exercise 2' not in answers and 'Exercise 4' not in answers


def test_solution_source_boundary():
    for edition in ('student', 'student-print', 'answer-key'):
        for path in ('contest/units/u/assets/ex3.py', 'contest/units/u/assets/ex12.py',
                     'contest/checkpoints/c/assets/q1.py', 'contest/projects/p/assets/p4.py',
                     'contest/units/u/assets/verify/check.py', 'contest/units/u/assets/verify/sub/x.py'):
            assert not allowed_source(Path(path), edition), (edition, path)
            assert allowed_source(Path(path), 'teacher')
    for path in ('contest/units/u/assets/ex2_start.py', 'contest/units/u/assets/l1.py',
                 'contest/units/u/assets/example.py', 'contest/units/u/assets/ex1a.py'):
        assert allowed_source(Path(path), 'student'), path
    assert publish.is_solution_source(Path('u/assets/q12.py'))
    assert not publish.is_solution_source(Path('u/assets/ex1_square.py'))
    assert not publish.is_solution_source(Path('u/ex1.py'))  # only under assets/


def test_student_boundary_refuses_to_read_a_solution_source(contest):
    path = contest / 'contest' / 'units' / 'unit-01-fixture' / 'assets' / 'ex3.py'
    with pytest.raises(ValueError, match='source boundary'):
        publish.read_source(path, 'student')
    assert publish.solution_assets(path.parent.parent, 3) == []
    assert publish.solution_source_files(path.parent.parent, 'unit', 3) == [path]


def test_audit_leak_guard_covers_ex_q_and_p_files_in_student_editions(contest):
    project = build(contest, 'contest', 'student')
    chapters = json.loads((project / 'inventory.json').read_text())['chapters']
    body = frozenset({'unit', 'checkpoint', 'project', 'setup', 'front'})
    assert publish_audit.leak_findings(contest, 'contest', chapters, project, 'student') == []
    assert publish_audit.leak_findings(contest, 'contest', chapters, project, 'student', hide_odd=True,
                                       kinds=body) == []
    unit = project / 'unit-01-fixture.qmd'
    unit.write_text(unit.read_text() + '\n```python\n' + Q1_MIRROR + '```\n\n```python\n' + EX2_SOLUTION
                    + '```\n\n```python\n' + P1_MIRROR + '```\n')
    findings = publish_audit.leak_findings(contest, 'contest', chapters, project, 'student', hide_odd=True,
                                           kinds=body)
    assert findings == ['FAIL: student: answers: solution leak from unit-01-fixture Exercise 2',
                        'FAIL: student: answers: solution leak from checkpoint-01-fixture Question 1',
                        'FAIL: student: answers: solution leak from project-01-fixture Problem 1']
    # A file-only solution (no notebook cell) is still guarded: the exN.py body itself counts.
    solutions = contest / 'contest' / 'units' / 'unit-01-fixture' / 'solutions.ipynb'
    nb = nbformat.read(solutions, as_version=4)
    nb.cells = [cell for cell in nb.cells if 'EVEN_EX2' not in cell.source]
    nbformat.write(nb, solutions)
    assert 'FAIL: student: answers: solution leak from unit-01-fixture Exercise 2' in publish_audit.leak_findings(
        contest, 'contest', chapters, project, 'student', hide_odd=True, kinds=body)
    # The odd answer in the appendix stays allowed.
    assert publish_audit.leak_findings(contest, 'contest', chapters, project, 'student') == []


# --- stdin programs and lesson headings --------------------------------------------------------

def _cell(source, tags=('no-exec',)):
    return SimpleNamespace(source=source, metadata={'tags': list(tags)}, outputs=[], id='x')


def test_stdin_programs_route_to_try_it_with_one_precedence_shared_by_the_audit():
    cases = {
        ('import sys\ndata = sys.stdin.read()', ('no-exec',)): 'tryit-stdin',
        ('data = open(0).read().split()', ('no-exec',)): 'tryit-stdin',
        ('import sys\nname = input()\nrest = sys.stdin.read()', ('no-exec',)): 'tryit-stdin',
        ('import sys\nsys.stdin.read(\n', ('no-exec', 'error-demo')): 'errordemo',
        ('import sys\nwhile True: sys.stdin.read()', ('no-exec', 'hang-demo')): 'hangdemo',
        ('name = input()', ('no-exec',)): 'tryit',
        ('with open("a.txt") as f:\n    print(f.read())', ('no-exec',)): 'program',
        ('print(1)', ()): 'code',
    }
    for (source, tags), kind in cases.items():
        cell = _cell(source, tags)
        route, body = route_code(cell)
        assert route == kind, source
        assert publish_audit._expected_lesson_kind(cell) == kind, source
        if kind == 'tryit-stdin':
            assert body.startswith('::: {.tryit}') and 'sample input file' in body
            assert 'python assets/' not in body
    assert publish.reads_stdin('import sys\nfor line in sys.stdin:\n    pass')
    assert not publish.reads_stdin('opened = file.open(0)') and not publish.reads_stdin('open(10)')


def test_stdin_lesson_cell_is_a_try_it_in_the_built_chapter(contest):
    project = build(contest, 'contest', 'student')
    chapter = next(c for c in json.loads((project / 'inventory.json').read_text())['chapters']
                   if c['id'] == 'unit-01-fixture')
    assert {'id': 'stdin01', 'kind': 'tryit-stdin'} in chapter['inventory']
    assert '::: {.tryit}\n```python\nimport sys\ndata = sys.stdin.read()' in _unit(project)


def test_configured_lesson_heading_keeps_l1_headings_and_drives_the_audit(contest):
    unit = _unit(build(contest, 'contest', 'student'))
    assert '\n## L1: Read the whole input\n' in unit
    loose = publish.markdown_blocks('## L1: Read the whole input\n\nText.')
    assert loose.startswith('### L1:')  # without a configured lesson heading it is demoted
    assert publish.markdown_blocks('## Lesson 2\n\nx', lesson_heading=r'^## Lesson\b').startswith('## Lesson 2')
    lesson = r'^## L\d+:'
    assert publish_audit.panel_findings('unit-01-fixture', unit, lesson) == []
    assert publish_audit.panel_findings('unit-01-fixture', unit, r'^## Lesson\b') == [
        'FAIL: unit-01-fixture: goals position']
    entry = contest / 'contest' / 'units' / 'unit-01-fixture'
    assert publish_audit.lesson_panel_source_findings(entry, lesson) == []
    assert publish_audit.lesson_panel_source_findings(entry, r'^## Lesson\b')


# --- the audit's per-book rules ------------------------------------------------------------------

def test_page_header_reset_is_derived_from_project_headers():
    pages = ('Unit 1\nExercise 1\nAnswer on page 4\n1\f'
             'Mock Contest\nAnswer on page 4\n2\f'
             'Answers to Selected Exercises\nUnit 1, Exercise 1 (page 1)\n4\f')
    stray = 'FAIL: student: page 2: answer reference without exercise heading'
    # Configured, the "Mock Contest" page header ends Unit 1, so its stray reference has no exercise.
    assert stray in publish_audit.reference_findings(pages, ('Mock Contest',))
    # Unconfigured, the page still counts as Unit 1 and the stray reference is not caught.
    assert stray not in publish_audit.reference_findings(pages)
    pattern = publish_audit.header_reset_pattern(('Mock Contest', 'Algorithm Challenge'))
    for header in ('Mock Contest', 'Algorithm Challenge', 'Checkpoint 3', 'Glossary', 'Index',
                   'Quick Reference', 'Answers to Selected Exercises'):
        assert pattern.search(header), header
    assert not publish_audit.header_reset_pattern().search('Algorithm Challenge')


def test_answers_start_check_accepts_the_first_unit_number():
    text = 'Answers to Selected Exercises\nUnit 0, Exercise 1 (page 9)\nCheck: x\f\nGlossary\n'
    assert publish_audit.answers_pdf_findings(text, 0) == []
    assert publish_audit.answers_pdf_findings(text) == ['FAIL: student: answers chapter missing in PDF']


EXEMPT = """\
  phrase_exemptions:
  - phrase: python assets/
    kinds: [unit]
    chapters: ['units/*']
    reason: Contest lessons teach running a program as python assets/lN.py < input.txt.
"""


def _exemption_config(tmp_path):
    (tmp_path / 'books.yaml').write_text(
        'books_version: 2\nbooks:\n- id: contest\n  root: contest\n  publication: true\n')
    root = tmp_path / 'contest'
    (root / 'docs').mkdir(parents=True)
    (root / 'docs' / 'unit-00-getting-set-up.md').write_text('# Unit 0 — Getting Set Up\n')
    (root / 'docs' / 'unit-00-teacher-notes.md').write_text('# Notes\n')
    (root / 'publication.yaml').write_text(MINIMAL_CONFIG + EXEMPT)
    return publication_config(tmp_path, 'contest')


SCOPED_CHAPTERS = [
    {'id': 'preface', 'file': 'index.qmd', 'kind': 'front', 'source': 'contest/front-matter/preface.md'},
    {'id': 'unit-01-a', 'file': 'unit-01-a.qmd', 'kind': 'unit', 'source': 'contest/units/unit-01-a'},
    {'id': 'checkpoint-01-a', 'file': 'checkpoint-01-a.qmd', 'kind': 'checkpoint',
     'source': 'contest/checkpoints/checkpoint-01-a'},
    {'id': 'answers-unit-01-a', 'file': 'answers-unit-01-a.qmd', 'kind': 'answers',
     'source': 'contest/units/unit-01-a'},
    {'id': 'answers', 'file': 'answers.qmd', 'kind': 'answers', 'source': ''},
]
PHRASE = 'Run python assets/l1.py < input.txt.'


def test_scoped_phrase_exemption_at_the_qmd_layer(tmp_path):
    config = _exemption_config(tmp_path)
    qmds = {chapter['file']: PHRASE for chapter in SCOPED_CHAPTERS}
    findings = publish_audit.qmd_phrase_findings(qmds, SCOPED_CHAPTERS, 'student-print', config, 'contest')
    # Allowed in the matching unit chapter only; banned in front matter, in a chapter whose kind or
    # source does not match, in an Answer Key chapter (same unit source) and in the appendix (no source).
    assert findings == [f'FAIL: student-print: {name}: banned phrase python assets/' for name in (
        'index.qmd', 'checkpoint-01-a.qmd', 'answers-unit-01-a.qmd', 'answers.qmd')]
    other = [{'id': 'unit-02-b', 'file': 'u2.qmd', 'kind': 'unit', 'source': 'contest/other/unit-02-b'}]
    assert publish_audit.qmd_phrase_findings({'u2.qmd': PHRASE}, other, 'student-print', config, 'contest')
    # Other banned phrases stay banned in the exempt chapter.
    assert publish_audit.qmd_phrase_findings({'unit-01-a.qmd': 'See the Answer key. ' + PHRASE},
                                             SCOPED_CHAPTERS, 'student', config, 'contest') == [
        'FAIL: student: unit-01-a.qmd: banned phrase Answer key']


def test_scoped_phrase_exemption_at_the_pdf_layer(tmp_path):
    config = _exemption_config(tmp_path)
    titles = ['About This Book', 'Unit 1 — A', 'Checkpoint 1 — A', 'Unit 1 — A', 'Answers to Selected Exercises']
    pages = ['Title page\nContents'] + [f'{title}\nText.' for title in titles]
    outline = ''.join(f'+\t"{title}"\t#page={index + 2}&zoom=nan\n' for index, title in enumerate(titles))
    clean = '\f'.join(pages)
    assert publish_audit.pdf_phrase_findings(clean, outline, SCOPED_CHAPTERS, 'student', config, 'contest',
                                             answers=False) == []
    # Page index -> the region it belongs to; page 2 is the matching unit chapter.
    banned = {0: 'title pages', 1: 'preface', 3: 'checkpoint-01-a', 4: 'answers-unit-01-a', 5: 'answers'}
    for page, chapter_id in banned.items():
        text = '\f'.join(p + ('\n' + PHRASE if index == page else '') for index, p in enumerate(pages))
        findings = publish_audit.pdf_phrase_findings(text, outline, SCOPED_CHAPTERS, 'student', config,
                                                     'contest', answers=False)
        assert findings == [f'FAIL: student: pdf {chapter_id}: banned phrase python assets/'], page
    in_unit = '\f'.join(p + ('\n' + PHRASE if index == 2 else '') for index, p in enumerate(pages))
    assert publish_audit.pdf_phrase_findings(in_unit, outline, SCOPED_CHAPTERS, 'student', config, 'contest',
                                             answers=False) == []
    # When the outline does not match the inventory the scan is unscoped and fails loudly.
    short = ''.join(outline.splitlines(keepends=True)[:3])
    findings = publish_audit.pdf_phrase_findings(in_unit, short, SCOPED_CHAPTERS, 'student', config,
                                                 'contest', answers=False)
    assert findings[0].startswith('FAIL: student: PDF outline chapters differ')
    assert 'FAIL: student: pdf: banned phrase python assets/' in findings


def test_exemption_globs_are_book_relative(tmp_path):
    config = _exemption_config(tmp_path)
    (exemption,) = config.phrase_exemptions
    assert exemption.applies('unit', 'contest/units/unit-01-output-and-variables', 'contest')
    assert not exemption.applies('answers', 'contest/units/unit-01-output-and-variables', 'contest')
    assert not exemption.applies('unit', '', 'contest')
    assert not exemption.applies('unit', 'contest/checkpoints/checkpoint-01', 'contest')
    assert publish_audit.book_prefix(tmp_path, 'contest') == 'contest'
    bad = MINIMAL_CONFIG + EXEMPT.replace("['units/*']", "['contest/units/*']")
    (tmp_path / 'contest' / 'publication.yaml').write_text(bad)
    assert any('must be book-relative' in error for error in publication_config_errors(tmp_path, 'contest'))


# --- config loading and validation ---------------------------------------------------------------

def test_python_concepts_config_holds_the_moved_constants():
    config = publication_config(Path(__file__).resolve().parents[1], 'python-concepts')
    assert config.setup_id == 'unit-00-getting-set-up' and config.setup_numbered
    assert config.setup_title == 'Unit 0 — Getting Set Up'
    assert config.project_headers == {'project-01-algorithm-challenge': 'Algorithm Challenge'}
    assert config.error_demo_ids == {'9442d5582e1f', '25129fdd9963', 'dcec5192b293', 'u02l029',
                                     'u02l079', 'u03l010', 'u04l022', 'u07l009', 'u13l009'}
    assert config.hang_demo_ids == {'u04l012'}
    assert config.print_required_starters == {'057d796ebeff'}
    assert config.error_demo_routing_exceptions == {'u07l034a'}
    assert config.print_page_target == 400
    assert config.turtle_tryits == {'unit-06-turtle-geometry': 3} and config.teacher_turtle_drawings == 21
    assert config.index_names == {'print', 'input', 'range', 'len', 'str', 'int', 'float',
                                  'append', 'split', 'open', 'sorted', 'sum'}
    assert config.lesson_heading == r'^## Lesson\b' and config.phrase_exemptions == ()
    for name in ('ERROR_IDS', 'HANG_IDS', 'PRINT_REQUIRED_STARTERS', 'PRINT_PAGE_TARGET'):
        assert not hasattr(publish_audit, name)
    assert not hasattr(publish, 'SETUP_ID') and not hasattr(publish, 'PYTHON_INDEX_NAMES')
    assert 'unit-00-getting-set-up.md' not in publish.STUDENT_SOURCES


@pytest.mark.parametrize('change,message', [
    ({'setup': {'source': 'docs/unit-00-getting-set-up.md', 'teacher_notes': 'docs/setup-notes.md',
                'numbered': True}}, 'teacher-notes exclusion pattern'),
    ({'setup': {'source': 'docs/missing.md', 'teacher_notes': 'docs/unit-00-teacher-notes.md',
                'numbered': True}}, 'source docs/missing.md does not exist'),
    ({'setup': {'source': 'docs/unit-00-getting-set-up.md',
                'teacher_notes': 'docs/unit-00-teacher-notes.md', 'numbered': 'yes'}}, 'numbered must be'),
    ({'setup': {'source': 'docs/unit-00-getting-set-up.md', 'numbered': True}}, 'missing key teacher_notes'),
    ({'lesson_heading': '^## (Lesson'}, 'invalid regex'),
    ({'lesson_heading': 'Lesson'}, "starting with '^## '"),
    ({'project_headers': {'project-01-x': ''}}, 'needs a header text'),
    ({'audit': {'goals_recap': 'optional'}}, "goals_recap must be 'required'"),
    ({'audit': {'goals_recap': 'required', 'turtle_count': 3}}, 'unknown key turtle_count'),
    ({'audit': {'goals_recap': 'required', 'print_page_target': 'many'}}, 'print_page_target'),
    ({'audit': {'goals_recap': 'required', 'error_demo_ids': 'u01'}}, 'list of non-empty strings'),
    ({'audit': {'goals_recap': 'required', 'phrase_exemptions': [
        {'phrase': 'python assets/', 'kinds': ['unit'], 'chapters': ['units/*']}]}}, 'missing reason'),
    ({'audit': {'goals_recap': 'required', 'phrase_exemptions': [
        {'phrase': 'x', 'kinds': ['lesson'], 'chapters': ['units/*'], 'reason': 'r'}]}}, 'unknown chapter kind'),
    ({'extra': 1}, 'unknown key extra'),
])
def test_config_validation_errors(tmp_path, change, message):
    root = tmp_path / 'book'
    (root / 'docs').mkdir(parents=True)
    (root / 'docs' / 'unit-00-getting-set-up.md').write_text('# Unit 0 — Getting Set Up\n')
    (root / 'docs' / 'unit-00-teacher-notes.md').write_text('# Notes\n')
    (root / 'docs' / 'setup-notes.md').write_text('# Notes\n')
    write_publication_config(root, **change)
    errors = publication_config_errors(tmp_path, 'book')
    assert any(message in error for error in errors), errors
    with pytest.raises(PublicationConfigError, match='FAIL'):
        publication_config(tmp_path, 'book')


def test_publish_and_audit_fail_loudly_without_a_config(contest, capsys):
    (contest / 'contest' / 'publication.yaml').unlink()
    with pytest.raises(PublicationConfigError, match='publication.yaml: missing'):
        build(contest, 'contest', 'student')
    with pytest.raises(PublicationConfigError, match='publication.yaml: missing'):
        publish_audit.audit(contest, 'contest')
    assert cli.main(['--root', str(contest), '--book', 'contest', 'publish', '--edition', 'student']) == 1
    assert cli.main(['--root', str(contest), '--book', 'contest', 'publish-audit']) == 1
    err = capsys.readouterr().err
    assert err.count('contest/publication.yaml: missing') == 2


def test_build_book_script_checks_the_config():
    script = (Path(__file__).resolve().parents[1] / 'scripts' / 'build-book.sh').read_text()
    assert 'publication_config_errors' in script
    assert script.index('publication_config_errors') < script.index('publish --edition')
