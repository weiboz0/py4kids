"""Plan 100 Phase A: publisher and audit gaps exposed by *Contest Python: ACSL* (one fixture per fix)."""
from __future__ import annotations

import shutil
import subprocess
import warnings
from pathlib import Path

import nbformat
import pytest
from publication_helpers import fixture_config
from test_publication_every_book import contest  # noqa: F401  (the judge-style fixture book)

from tools.publish import (
    INDEX_BODY,
    STDIN_NOTE,
    THEME,
    build,
    code_span_names,
    render_chapter,
    reset_kicker,
)
from tools.publish_audit import _turtle_drawing_findings, glossary_page_numbers, reference_findings

md = nbformat.v4.new_markdown_cell
code = nbformat.v4.new_code_cell


def _write(path: Path, cells) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nbformat.v4.new_notebook(cells=cells), path)


# --- A1: a plain `input()` Try-it prints once ----------------------------------------------------------

BINARY = ('n = int(input())\nbits = ""\nwhile n > 0:\n    bits = str(n % 2) + bits\n    n = n // 2\n'
          'print(bits)\n')
HEX = 'parts = input().split()\nprint("#" + "".join(p for p in parts))\n'
TURTLE = '# sample-input: 10\nimport turtle\nturtle.forward(int(input("Length: ")))\n'


def _input_unit(entry: Path) -> None:
    (entry / 'assets').mkdir(parents=True, exist_ok=True)
    (entry / 'assets' / 'l1.py').write_text(BINARY, encoding='utf-8')
    (entry / 'assets' / 'l2.py').write_text(HEX, encoding='utf-8')
    (entry / 'assets' / 'l3.py').write_text('n = int(input())\nprint(n * 2)\n', encoding='utf-8')
    (entry / 'assets' / 'l4.py').write_text(TURTLE, encoding='utf-8')
    _write(entry / 'lesson.ipynb', [
        md('# Unit 1 — Number Systems\n\nA hook.', id='title'),
        # An earlier mention (ACSL u04/u08 "Optional." cells): a later Try-it prints the program.
        md('**Optional.** This unit\'s folder also holds a small program, `assets/l1.py`.', id='early'),
        md('## Lesson 1 — Binary\n\nThis program prints the binary form.\n'
           'It is saved as `assets/l1.py`; you do not need to understand the code yet.', id='l1'),
        # Same code tokens as assets/l1.py (a comment and spacing differ).
        code('n = int(input())  # read n\nbits = ""\nwhile n > 0:\n    bits = str(n % 2) + bits\n'
             '    n = n // 2\nprint(bits)', id='tryit1', metadata={'tags': ['no-exec']}),
        md('To run it, type `python assets/l1.py`, then a number such as `45`.', id='run1'),
        md('## Lesson 2 — Colour codes\n\nPut it together.', id='l2'),
        # Named only by the cell after it.
        code(HEX, id='tryit2', metadata={'tags': ['no-exec']}),
        md('Run it from this unit folder:\n\n```text\npython assets/l2.py < assets/l2/1.in\n```', id='run2'),
        md('## Lesson 3 — Doubling\n\nIt is saved as `assets/l3.py`.', id='l3'),
        # A different program from assets/l3.py: both print.
        code('n = int(input())\nprint(n + n)', id='tryit3', metadata={'tags': ['no-exec']}),
        md('## Lesson 4 — A turtle Try-it\n\nIt is saved as `assets/l4.py`.', id='l4'),
        # Turtle `input()` Try-its (`tryit+figure`) are not deduplicated: the listing stays.
        code(TURTLE, id='turtle4', metadata={'tags': ['no-exec'], 'sample_input': '10'}),
    ])
    _write(entry / 'exercises.ipynb', [md('# Practice', id='x0'), md('## Exercise 1\n\n### Go\n\nDo it.', id='x1')])


def test_plain_input_tryit_prints_once_whichever_cell_names_its_asset(tmp_path):
    entry = tmp_path / 'units' / 'unit-01-fixture'
    _input_unit(entry)
    body, inventory, _, _ = render_chapter(entry, 'unit', 'student', fixture_config())
    lesson = body.split('## Exercises', 1)[0]
    # Named before (and again after): the program prints once, as the Try-it, with no listing,
    # no "saved as" line and no generic stdin note; the run line stays.
    assert lesson.count('bits = str(n % 2) + bits') == 1
    assert '::: {.tryit}\n```python\nn = int(input())  # read n' in lesson
    assert '**assets/l1.py**' not in lesson and 'This program is saved as assets/l1.py' not in lesson
    assert 'type `python assets/l1.py`' in lesson
    # Named only after: printed once too.
    assert lesson.count('parts = input().split()') == 1 and '**assets/l2.py**' not in lesson
    # A different program keeps its listing; so does a turtle Try-it's identical asset.
    assert '**assets/l3.py**' in lesson and '**assets/l4.py**' in lesson
    assert STDIN_NOTE not in lesson
    kinds = [(record['id'], record['kind']) for record in inventory]
    assert kinds[:6] == [('asset:l1.py', 'asset reference'), ('tryit1', 'tryit'),
                         ('tryit2', 'tryit'), ('asset:l2.py', 'asset reference'),
                         ('asset:l3.py', 'asset listing'), ('tryit3', 'tryit')]
    assert ('asset:l4.py', 'asset listing') in kinds and ('turtle4', 'tryit+figure') in kinds


def test_audit_mirror_knows_the_plain_tryit_case(tmp_path):
    entry = tmp_path / 'units' / 'unit-01-fixture'
    _input_unit(entry)
    # No turtle cell here: the turtle Try-it's own listing check is plan 099's.
    lesson = nbformat.read(entry / 'lesson.ipynb', as_version=4)
    lesson.cells = [cell for cell in lesson.cells if cell.id not in {'l4', 'turtle4'}]
    nbformat.write(lesson, entry / 'lesson.ipynb')
    body, _, _, _ = render_chapter(entry, 'unit', 'student', fixture_config())
    assert _turtle_drawing_findings(entry, body, 'student') == []
    lesson_qmd = body.split('## Exercises', 1)[0]
    listed = lesson_qmd + '\n::: {.program}\n**assets/l1.py**\n\n```python\n' + BINARY + '```\n:::\n'
    assert any('try-it asset l1.py listed again in full' in finding
               for finding in _turtle_drawing_findings(entry, listed + '## Exercises', 'student'))
    # A plain Try-it never carries the stdin note.
    noted = lesson_qmd + '\n' + STDIN_NOTE + '\n'
    assert any('expected 0 stdin try-it notes' in finding
               for finding in _turtle_drawing_findings(entry, noted + '## Exercises', 'student'))


# --- A2: the chapter kicker is reset for the back matter ----------------------------------------------

def test_reset_kicker_marks_only_the_opening_heading():
    assert reset_kicker('# Glossary\n\n**Term** — text.\n') == '# Glossary {pub-label=""}\n\n**Term** — text.\n'
    assert reset_kicker('# Quick Reference  \n\n```python\n# a comment\n```\n').startswith(
        '# Quick Reference {pub-label=""}\n')
    # A file that does not open with a plain level-one heading is left alone.
    assert reset_kicker('Intro.\n\n# Later\n') == 'Intro.\n\n# Later\n'
    assert reset_kicker('# Glossary {#glossary}\n') == '# Glossary {#glossary}\n'


@pytest.mark.parametrize('edition', ['student', 'teacher'])
def test_back_matter_chapters_clear_the_kicker(contest, edition):  # noqa: F811
    # Main matter that ends with a checkpoint (ACSL's shape), so the last kicker is "Checkpoint 1".
    syllabus = contest / 'contest' / 'syllabus.md'
    syllabus.write_text(syllabus.read_text().replace(
        '| 3 | `project-01-fixture` | project | 1 | Mock. |\n', ''))
    project = build(contest, 'contest', edition)
    assert (project / 'glossary.qmd').read_text().startswith('# Glossary {pub-label=""}\n')
    assert (project / 'quick-reference.qmd').read_text().startswith('# Quick Reference {pub-label=""}\n')
    assert (project / 'the-index.qmd').read_text() == INDEX_BODY == '\\pubchapterlabel{}\n\n\\printindex\n'
    if edition == 'student':
        assert (project / 'answers.qmd').read_text().startswith(
            '# Answers to Selected Exercises {pub-label=""}\n\n')


@pytest.mark.skipif(shutil.which('pandoc') is None, reason='pandoc is not installed')
def test_empty_pub_label_emits_the_theme_reset():
    source = ('# Checkpoint 4 — Practice {pub-label="Checkpoint 4"}\n\nText.\n\n'
              + reset_kicker('# Glossary\n\nTerms.\n') + '\n' + INDEX_BODY)
    latex = subprocess.run(['pandoc', '-f', 'markdown', '-t', 'latex', '--wrap=none', '--lua-filter',
                            str(THEME / 'panels.lua')], input=source, capture_output=True, text=True,
                           check=True).stdout
    assert latex.count('\\pubchapterlabel{Checkpoint 4}') == 1
    glossary = latex.index('\\pubchapterlabel{}')
    assert glossary < latex.index('Glossary') and 'pub-label' not in latex
    # The Index: the theme's setter clears the kicker before \printindex opens its chapter.
    assert latex.index('\\pubchapterlabel{}', glossary + 1) < latex.index('\\printindex')


def _page(folio: int | None, head: str, body: str) -> str:
    return (f'{folio}\n\n' if folio is not None else '') + f'{head}\n\n{body}\n'


def test_glossary_pages_resolve_for_one_or_more_pages():
    # Physical pages 1-3: answers appendix (a verso with folio 101 on physical 2); then the Glossary
    # opening page (no folio), optionally one verso continuation, then Quick Reference and the Index.
    answers = [_page(None, 'Answers to Selected Exercises', 'x'), _page(101, 'Answers to Selected Exercises', 'y'),
               'Answers to Selected Exercises\n\n102\n\nz\n']
    two_pages = answers + ['Glossary\nTerm — text.\n', _page(104, 'Glossary', 'More.'),
                           'Quick Reference\nCard.\n', '', 'Index\nterm, 103\n']
    assert glossary_page_numbers('\f'.join(two_pages)) == {103, 104}
    # One page: the offset comes from the nearest other back-matter verso page.
    one_page = answers + ['Glossary\nTerm — text.\n', 'Quick Reference\nCard.\n',
                          _page(105, 'Quick Reference', 'More.'), 'Index\nterm, 103\n']
    assert glossary_page_numbers('\f'.join(one_page)) == {103}
    # The Teacher's Edition has no answers appendix: a later verso page gives it.
    assert glossary_page_numbers('\f'.join(['Glossary\nT.\n', 'Quick Reference\nC.\n',
                                            _page(8, 'Quick Reference', 'D.')])) == {6}
    # No folio anywhere: unresolved, as before.
    assert glossary_page_numbers('Glossary\nT.\n\fQuick Reference\nC.\n') == set()
    # The old failure: "Checkpoint 4" still above the heading means no Glossary opening page.
    assert glossary_page_numbers('\f'.join(['Checkpoint 4\n\n' + two_pages[3], *two_pages[4:]])) == set()


# --- A3: a top-of-page integer is the folio only when it fits the page offset -------------------------

def test_sample_input_at_the_top_of_a_page_is_not_its_page_number():
    """The ACSL probe: physical page 373 (folio 363) begins "Exercises" / "2", where "2" is a sample
    input line; it must not be read as page 2, so "Unit 13, Exercise 19 (page 363)" resolves."""
    pages = ['Preface\n\nText.\n'] * 10
    for physical in range(11, 380):
        folio = physical - 10
        if physical == 373:
            pages.append('Exercises\n\n2\n\n3 8 5\n\nExercise 19 — Gate Count\n'
                         'Count the gates.\nAnswer on page 370.\n')
        elif physical % 2:
            pages.append(f'Unit 13 — Digital Electronics\n\n{folio}\n\nText.\n')
        else:
            pages.append(f'{folio}\n\nUnit 13 — Digital Electronics\n\nText.\n')
    pages.append('370\n\nAnswers to Selected Exercises\n\nUnit 13, Exercise 19 (page 363)\nThree.\n')
    text = '\f'.join(pages) + '\f'
    assert pages[372].startswith('Exercises\n\n2') and pages[379].startswith('370')
    assert reference_findings(text) == [], reference_findings(text)
    # A wrong reference still fails.
    assert reference_findings(text.replace('(page 363)', '(page 362)')) == [
        'FAIL: student: Unit 13 Exercise 19: source page 362']


# --- A4: code_span_names is quiet ---------------------------------------------------------------------

def test_code_span_names_emits_no_syntax_warning():
    # `1if` / `3in` make the compiler warn "invalid decimal literal" (before failing, or parsing).
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        assert code_span_names('3in') == set()
        assert code_span_names('2d') == set()
        assert code_span_names('1if x else y') == {'if', 'x', 'else', 'y'}
        assert code_span_names('len(x)') == {'len', 'x'}
    assert [warning for warning in caught if issubclass(warning.category, SyntaxWarning)] == []
