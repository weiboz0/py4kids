"""Phase D publication contracts."""

from pathlib import Path

import nbformat

from tools import publish, publish_audit


def test_check_lines_preserve_order_blank_lines_and_nested_asserts():
    source = ('value = side_effect()\n\nassert save(value) == 3\n'
              'for item in values:\n    assert item > 0\n\nprint(value)')
    rendered = publish.render_solution_code(source)
    assert rendered.index('value = side_effect()') < rendered.index('Check: `save(value)` → `3`')
    assert rendered.index('Check: `save(value)` → `3`') < rendered.index('for item in values:')
    assert '    assert item > 0' in rendered
    assert 'value = side_effect()\n\n```' in rendered
    assert rendered.index('for item in values:') < rendered.index('print(value)')
    multiline = publish.render_solution_code('assert sum(\n    [1, 2]\n) == 3')
    assert 'Check: `sum( [1, 2] )` → `3`' in multiline
    assert multiline.count('Check:') == 1


def test_student_answer_sources_are_odd_unit_only(tmp_path):
    unit = tmp_path / 'units' / 'unit-01-fixture'
    (unit / 'assets').mkdir(parents=True)
    (unit / 'assets' / 'solutions_ex1_square.py').write_text('print(1)\n')
    (unit / 'assets' / 'solutions_ex10.py').write_text('print(10)\n')
    nbformat.write(nbformat.v4.new_notebook(cells=[
        nbformat.v4.new_markdown_cell('# Solutions'),
        nbformat.v4.new_markdown_cell('## Exercise 1'),
        nbformat.v4.new_code_cell('print(1)'),
        nbformat.v4.new_markdown_cell('## Exercise 2'),
        nbformat.v4.new_code_cell('print(2)'),
    ]), unit / 'solutions.ipynb')
    groups, assets = publish.student_answer_sources(unit)
    assert [g['number'] for g in groups] == [1]
    assert [p.name for p in assets[1]] == ['solutions_ex1_square.py']
    assert not publish.allowed_source(unit / 'solutions.ipynb', 'student')
    assert not publish.allowed_source(unit / 'assets' / 'solutions_ex1_square.py', 'student')
    assert publish.student_answer_sources(tmp_path / 'checkpoints' / 'checkpoint-01-fixture') == ([], {})


def test_real_version_keeps_student_wording_and_drops_no_real_panel(tmp_path):
    entry = tmp_path / 'units' / 'unit-01-fixture'
    entry.mkdir(parents=True)
    nbformat.write(nbformat.v4.new_notebook(cells=[
        nbformat.v4.new_markdown_cell('# Practice'),
        nbformat.v4.new_markdown_cell('## Exercise 1'),
        nbformat.v4.new_markdown_cell('**Real version:** Run the file — see the solution.'),
        nbformat.v4.new_markdown_cell('**No real version:** This is a prediction task.'),
    ]), entry / 'exercises.ipynb')
    student, _, _ = publish.render_items(entry / 'exercises.ipynb', 'unit', 'student', entry,
                                         entry.name)
    teacher, _, _ = publish.render_items(entry / 'exercises.ipynb', 'unit', 'teacher', entry,
                                         entry.name)
    assert '::: {.realprog}\nRun the file' in student
    assert 'see the solution' not in student
    assert 'There is no real program' not in student + teacher
    assert student.count('::: {.realprog}') == teacher.count('::: {.realprog}') == 1


def test_panels_and_directives():
    assert publish.markdown_blocks('### You will learn\n\n- Names') == (
        '::: {.goals}\n- Names\n:::\n')
    assert publish.markdown_blocks('### Recap\n\n- Names') == (
        '::: {.recap}\n- Names\n:::\n')
    assert '# turtle-check:' not in publish.code_block('print(1)\n# turtle-check: open-path\n')
    assert '# turtle-check:' not in publish.markdown_blocks(
        '```python\nprint(1)\n# turtle-check: open-path\n```')
    theme = Path('tools/publish_theme/theme.tex').read_text()
    lua = Path('tools/publish_theme/panels.lua').read_text()
    for phrase in ('First edition, 2026', 'Copyright © 2026 Weibo Zhou',
                   'Written for Python 3.12 or newer', 'https://github.com/weiboz0/py4kids'):
        assert phrase in theme
    assert r'\uppertitleback' in theme and r'\lowertitleback' in theme
    assert r'\makeindex[intoc]' in theme
    assert 'pubgoals' in theme and 'pubrecap' in theme
    assert 'goals=true, recap=true' in lua
    assert "c == '\\\\'" in lua


def test_answer_labels_and_asset_number_boundary(tmp_path):
    entry = tmp_path / 'units' / 'unit-06-fixture'
    (entry / 'assets').mkdir(parents=True)
    (entry / 'assets' / 'solutions_ex1_square.py').write_text('print(1)\n')
    (entry / 'assets' / 'solutions_ex10.py').write_text('print(10)\n')
    nbformat.write(nbformat.v4.new_notebook(cells=[
        nbformat.v4.new_markdown_cell('# Solutions'),
        nbformat.v4.new_markdown_cell('## Exercise 1'),
        nbformat.v4.new_code_cell('assert running_totals_to_file([1], "p11_out.txt") == None\n'
                                      'print(open("p11_out.txt").read())'),
    ]), entry / 'solutions.ipynb')
    result = publish.answer_key(entry, 'unit', [{'number': 1, 'title': ''}], edition='student')
    assert r'\label{ans:unit-06-fixture:1}' in result
    assert r'\pageref{ex:unit-06-fixture:1}' in result
    assert 'Check: `running_totals_to_file([1], "p11_out.txt")` → `None`' in result
    assert result.index('Check:') < result.index('print(open')
    assert 'solutions_ex1_square.py' in result
    assert 'solutions_ex10.py' not in result


def test_real_problem_11_check_precedes_output_file_read():
    entry = Path('book1b/projects/project-01-algorithm-challenge')
    key = publish.answer_key(entry, 'project', [{'number': 11, 'title': ''}])
    assert key.index('Check: `running_totals_to_file("p11_in.txt", "p11_out.txt")`') < key.index(
        'with open("p11_out.txt", "r") as f:')


def test_real_u06_exercise_one_asset_does_not_include_exercise_ten():
    entry = Path('book1b/units/unit-06-turtle-geometry')
    assert [path.name for path in publish.solution_assets(entry, 1)] == ['solutions_ex1.py']


def test_student_phrase_and_panel_audits():
    qmd = ('# Unit 1\n\n::: {.opener}\nHook.\n:::\n\n'
           '::: {.goals}\n- Print values.\n:::\n\n## Lesson 1\n\n'
           '::: {.recap}\n- Print values.\n:::\n\n## Exercises\n')
    assert publish_audit.panel_findings('unit-01-fixture', qmd) == []
    assert publish_audit.panel_findings('unit-01-fixture', qmd.replace('::: {.recap}', '### Recap'))
    assert publish_audit.panel_findings('unit-01-fixture', qmd.replace(
        '## Lesson 1', 'Extra prose.\n\n## Lesson 1'))
    assert publish_audit.student_phrase_findings('Teacher’s Edition', 'pdf')
    assert publish_audit.student_phrase_findings('assert x == 1', 'answers')


def test_leak_guard_catches_whole_and_embedded_but_not_shared_idioms():
    tokens = publish.code_tokens('result = calculate(1, 2, 3)\nprint(result)')
    assert publish_audit.solution_leak(tokens, [tokens], [])
    long_tokens = publish.code_tokens(' '.join(f'word{i}' for i in range(40)))
    embedded = publish.code_tokens('before = 1\n' + ' '.join(f'word{i}' for i in range(40)) + '\nafter = 2')
    assert publish_audit.solution_leak(embedded, [long_tokens], [])
    assert not publish_audit.solution_leak(embedded, [long_tokens], [long_tokens])
    # A shared idiom (a fragment of a hidden solution) is not a leak.
    assert not publish_audit.solution_leak(long_tokens[2:23], [long_tokens], [])


def test_glossary_index_parser_and_prose_boundary():
    glossary = '**print** — Show text. *(Unit 1)*\n<!-- concept: print; index: display -->\n'
    assert publish.glossary_entries(glossary) == [('print', 'print', ['display'])]
    qmd = '# print\n\n```python\nprint(1)\n```\n\n`print` and print a value.\n'
    indexed = publish.index_first_prose(qmd, [('Print', 'print', ['display'])])
    assert indexed.count(r'\index{print@Print}') == 1
    assert '`print`' + r'\index{print@Print}' in indexed
    assert 'and print a value' in indexed
    bold = publish.index_first_prose('A **decimal number** value.\n',
                                     [('Float', 'float-type', ['decimal number'])])
    assert bold == 'A ' + r'\index{float@Float}' + '**decimal number** value.\n'


def test_index_aliases_share_one_entry_and_restricted_names_use_code_only():
    terms = [('Logical operators', 'logical-ops', ['and', 'or', 'not']),
             ('Class', 'class-def', ['class']),
             ('Code comment', 'comment', ['comment']),
             ('File writing', 'file-write', ['`write`'])]
    qmd = ('# class and comment\n```python\nclass X: pass\n```\n'
           'The class and comment are here.\n'
           'Use `and` and `write` to add a comment.\n'
           'Another class and another comment.\n')
    indexed = publish.index_first_prose(qmd, terms)
    assert indexed.count(r'\index{logical operators@Logical operators}') == 1
    assert indexed.count(r'\index{class@Class}') == 0
    assert indexed.count(r'\index{code comment@Code comment}') == 1
    assert indexed.count(r'\index{file writing@File writing}') == 1
    assert '`and`' + r'\index{logical operators@Logical operators}' in indexed
    assert '`write`' + r'\index{file writing@File writing}' in indexed
    assert 'comment' + r'\index{code comment@Code comment}' in indexed
    assert 'The class and comment' in indexed
    assert r'\index{and}' not in indexed
    names = publish.index_first_prose('print and `print`; `len` then len.\n', [])
    assert names.count(r'\index{Python names!print@\texttt{print}}') == 1
    assert names.count(r'\index{Python names!len@\texttt{len}}') == 1
    boolean = publish.index_first_prose('A true fact. Use `True`.\n',
                                        [('Boolean', 'boolean', ['True'])])
    assert 'true' + r'\index{boolean@Boolean}' not in boolean
    assert '`True`' + r'\index{boolean@Boolean}' in boolean


def test_index_audit_rejects_glossary_only_case_duplicates_and_prose_keyword():
    glossary = [('Class', 'class-def', ['class']), ('Code comment', 'comment', ['comment'])]
    good = (r'\item Class, \hyperpage{21}, \hyperpage{643}' + '\n'
            r'\item Code comment, \hyperpage{10}, \hyperpage{643}')
    assert publish_audit.index_findings(good, glossary, {643}) == []
    assert publish_audit.index_findings(good.replace(r'\hyperpage{10}, ', ''), glossary, {643})
    assert publish_audit.index_findings(good + '\n' + r'\item class, \hyperpage{22}',
                                        glossary, {643})
    assert publish_audit.index_source_findings('The class' + r'\index{class@Class}' + '.\n', glossary)
    assert publish_audit.index_source_findings('Use `class`' + r'\index{class@Class}' + '.\n',
                                               glossary) == []
    assert publish_audit.index_source_findings(
        'Call print' + r'\index{Python names!print@\texttt{print}}' + '.\n', glossary)
    assert publish_audit.index_source_findings(
        'Call `print`' + r'\index{Python names!print@\texttt{print}}' + '.\n', glossary) == []
    assert publish_audit.index_source_findings(
        '`len`' + r'\index{built-in function@Built-in function}'
        + r'\index{Python names!len@\texttt{len}}' + '.\n', glossary) == []


def test_cross_references_match_unit_and_exercise():
    pages = ('Unit 1\nExercise 1\nAnswer on page 3\n1\f'
             'Unit 2\nExercise 1\nAnswer on page 4\n2\f'
             'Answers to Selected Exercises\nUnit 1, Exercise 1 (page 1)\n3\f'
             'Answers to Selected Exercises\nUnit 2, Exercise 1 (page 2)\n4\f')
    assert publish_audit.reference_findings(pages) == []
    assert publish_audit.reference_findings(pages.replace('Answer on page 3', 'Answer on page 4'))
    assert publish_audit.reference_findings(pages.replace('Unit 1, Exercise 1 (page 1)',
                                                         'Unit 1, Exercise 1 (page 2)'))
    assert publish_audit.reference_findings(pages.replace('Exercise 1\nAnswer on page 3',
                                                         'Answer on page 3', 1))
    assert publish_audit.reference_findings(pages + 'Unit 1\nAnswer on page 3\n99\f')
    continuation = ('Unit 1\nExercise 1\n1\fExercises\nAnswer on page 3\n2\f'
                    'Answers to Selected Exercises\nUnit 1, Exercise 1 (page 1)\n3\f')
    assert publish_audit.reference_findings(continuation) == []
    assert publish_audit.reference_findings(continuation.replace('(page 1)\n3\f',
                                                                 '(page 1)\f')) == []
    assert publish_audit.reference_findings('Preface\fContents\f' + continuation.replace(
        '(page 1)\n3\f', '(page 1)\f')) == []


def test_audit_sentinels_for_index_labels_and_answer_coverage():
    assert publish_audit.glossary_findings(['print'], [('print', 'print', [])]) == []
    assert publish_audit.glossary_findings(['print'], [])
    assert publish_audit.index_findings(r'\item print, \hyperpage{1}', [('print', 'print', [])]) == []
    assert publish_audit.index_findings('', [('print', 'print', [])])
    assert publish_audit.index_findings(r'\item Input validation, \hyperpage{1}',
                                        [('Input', 'input', [])])
    assert publish_audit.label_log_findings('LaTeX Warning: There were undefined references.')
    assert publish_audit.label_log_findings("LaTeX Warning: Reference `ans:1' on page 2 undefined")
    assert publish_audit.label_log_findings('Label `ex:1` multiply defined')
    assert publish_audit.answer_coverage_findings('### Unit 1, Exercise 1 (page 4)', [(1, 1)]) == []
    assert publish_audit.answer_coverage_findings('### Unit 1, Exercise 2 (page 4)', [(1, 1)])
    pdf = 'Unit 1, Exercise 1 (page 2)\nCheck: x → 2\fGlossary\nterm\f'
    assert publish_audit.answers_pdf_findings(pdf) == []
    assert publish_audit.answers_pdf_findings(pdf.replace('Check: x', 'assert x'))
    assert 'makeindex "$name.idx"' in Path('scripts/build-book.sh').read_text()


def test_challenge_heading_audit_accepts_explicit_exercise_label():
    qmd = ('### Challenge — Draw a square\n\n```{=latex}\n'
           '\\label{ex:unit-01-fixture:3}\n```\n\n::: {.challenge}\n'
           '**Exercise 3**\n:::\n\n### Exercise 4\n')
    assert publish_audit.rendered_item_numbers(qmd, 'unit') == [3, 4]


def test_lesson_panel_source_positions(tmp_path):
    entry = tmp_path / 'units' / 'unit-01-fixture'
    entry.mkdir(parents=True)
    path = entry / 'lesson.ipynb'
    cells = [nbformat.v4.new_markdown_cell('# Unit 1\n\nA hook.'),
             nbformat.v4.new_markdown_cell('### You will learn\n\n- Print.'),
             nbformat.v4.new_markdown_cell('## Lesson 1\n\nPrint.'),
             nbformat.v4.new_markdown_cell('### Recap\n\n- Print.')]
    nbformat.write(nbformat.v4.new_notebook(cells=cells), path)
    assert publish_audit.lesson_panel_source_findings(entry) == []
    cells.insert(2, nbformat.v4.new_markdown_cell('An extra note.'))
    nbformat.write(nbformat.v4.new_notebook(cells=cells), path)
    assert publish_audit.lesson_panel_source_findings(entry)
