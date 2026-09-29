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
    entry = Path('python-concepts/projects/project-01-algorithm-challenge')
    key = publish.answer_key(entry, 'project', [{'number': 11, 'title': ''}])
    assert key.index('Check: `running_totals_to_file("p11_in.txt", "p11_out.txt")`') < key.index(
        'with open("p11_out.txt", "r") as f:')


def test_real_u06_exercise_one_asset_does_not_include_exercise_ten():
    entry = Path('python-concepts/units/unit-06-turtle-geometry')
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
    assert publish_audit.solution_leak(tokens, [tokens])
    long_tokens = publish.code_tokens(' '.join(f'word{i}' for i in range(40)))
    embedded = publish.code_tokens('before = 1\n' + ' '.join(f'word{i}' for i in range(40)) + '\nafter = 2')
    assert publish_audit.solution_leak(embedded, [long_tokens])
    # A short hidden solution embedded in a larger block is not flagged (too common to be a leak).
    short = publish.code_tokens('x = 1')
    assert not publish_audit.solution_leak(publish.code_tokens('y = 2\nx = 1\nz = 3'), [short])
    # A shared idiom (a fragment of a hidden solution) is not a leak.
    assert not publish_audit.solution_leak(long_tokens[2:23], [long_tokens])


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


def test_check_lines_state_the_value_and_never_say_is_true():
    cases = {
        'assert f(1) == 2': 'Check: `f(1)` → `2`',
        'assert is_spammy("hi") is False': 'Check: `is_spammy("hi")` → `False`',
        'assert find(x) is None': 'Check: `find(x)` → `None`',
        'assert not is_even(3)': 'Check: `is_even(3)` → `False`',
        'assert is_even(4)': 'Check: `is_even(4)` → `True`',
        'assert ready': 'Check: `ready` → `True`',
        'assert a < b': 'Check: `a < b` → `True`',
        'assert "x" in word': 'Check: `"x" in word` → `True`',
        'assert f(1) != 2': 'Check: `f(1) != 2` → `True`',
    }
    for source, line in cases.items():
        rendered = publish.render_solution_code(source)
        assert rendered.strip() == line, source
        assert 'is true' not in rendered


def test_student_real_version_keeps_its_full_stop():
    assert publish.strip_solution_pointer(
        'reads the size with input() — see the solution.') == 'reads the size with input().'
    assert publish.strip_solution_pointer(
        'reads it with input(), then draws it — see the solution') == 'reads it with input(), then draws it.'
    assert publish.strip_solution_pointer('Done! — see the solution.') == 'Done!'
    assert publish.strip_solution_pointer('no pointer here') == 'no pointer here'


def test_glossary_units_take_the_first_unit_of_a_range():
    source = ('**Break and continue** — `break` leaves. *(Units 4–5)*\n<!-- concept: b -->\n'
              '**Method** — A function on an object. *(Unit 13)*\n<!-- concept: m -->\n')
    assert publish.glossary_units(source) == {'Break and continue': 4, 'Method': 13}


def test_index_waits_for_the_teaching_unit():
    terms = [('Method', 'methods', []), ('String methods', 'string-methods', ['`find`'])]
    units = {'Method': 13, 'String methods': 9}
    qmd = 'A greatest-common-divisor method. Call `text.find("a")`.\n'
    early = publish.index_first_prose(qmd, terms, 7, units)
    assert r'\index{' not in early
    late = publish.index_first_prose(qmd, terms, 13, units)
    assert r'\index{method@Method}' in late and r'\index{string methods@String methods}' in late
    glossary = [(term, concept, aliases) for term, concept, aliases in terms]
    assert publish_audit.index_source_findings(late, glossary, 7, units) == [
        'FAIL: index before taught in unit 7: method@Method',
        'FAIL: index before taught in unit 7: string methods@String methods']
    assert publish_audit.index_source_findings(late, glossary, 13, units) == []


def test_index_code_keys_match_real_code_only_and_case_sensitively():
    names = publish.index_first_prose('Print `print("Open")` then `# open-path` and `Open`.\n', [])
    assert r'\texttt{open}' not in names
    assert names.count(r'\texttt{print}') == 1
    output = publish.index_first_prose('It prints `Digit sum: 7`, then `sum(xs)`.\n', [])
    assert '`sum(xs)`' + r'\index{Python names!sum@\texttt{sum}}' in output
    assert '`Digit sum: 7`' + r'\index' not in output
    terms = [('List changes', 'list-append', ['`.append`', '`.remove`']),
             ('Random choice', 'random-module', ['`random.choice`']),
             ('Logical operators', 'logical-ops', ['and', 'or', 'not'])]
    prose = publish.index_first_prose(
        'Remove all four digits and make a choice: `choice`, `NameError: name x is not defined`.\n', terms)
    assert r'\index{' not in prose
    code = publish.index_first_prose('Use `nums.remove(3)`, `random.choice(xs)`, `not done`.\n', terms)
    for entry in ('list changes@List changes', 'random choice@Random choice',
                  'logical operators@Logical operators'):
        assert r'\index{' + entry + '}' in code


def test_index_headword_can_be_suppressed_and_hyphenated_words_do_not_match():
    terms = [('String', 'string-literal', ['-String', 'string literal']),
             ('Name', 'naming', ['-Name', 'meaningful names']),
             ('Counter variable', 'loop-counter', ['loop counter'])]
    qmd = 'An f-string, a string, a coin counter, a name. A string literal; meaningful names; a loop counter.\n'
    indexed = publish.index_first_prose(qmd, terms)
    assert 'string literal' + r'\index{string@String}' in indexed
    assert 'meaningful names' + r'\index{name@Name}' in indexed
    assert 'loop counter' + r'\index{counter variable@Counter variable}' in indexed
    assert indexed.count(r'\index{') == 3


def test_python_concepts_glossary_keys_are_precise_and_every_term_has_a_unit():
    source = (Path(__file__).resolve().parents[1] / 'python-concepts' / 'back-matter' / 'glossary.md').read_text(
        encoding='utf-8')
    terms = publish.glossary_entries(source)
    units = publish.glossary_units(source)
    assert set(units) == {term for term, _, _ in terms}
    assert units['Break and continue'] == 4
    generic = {'find', 'choice', 'remove', 'pop', 'counter', 'total', 'program', 'search', 'map',
               'list', 'class', 'range', 'method', 'name', 'string', 'insert', 'sort', 'self'}
    prose_keys = {key.casefold() for _, _, aliases in terms for key in aliases
                  if not key.startswith(('`', '-'))}
    assert not prose_keys & generic


def test_python_name_units_prefer_glossary_keys_then_first_lesson_use():
    glossary = [('Built-in function', 'builtin-functions', ['len', 'min']),
                ('List changes', 'list-append', ['`.append`']),
                ('Float', 'float-type', ['decimal number'])]
    first_units = {'Built-in function': 7, 'List changes': 10, 'Float': 2}
    lessons = {3: ['n = 5\nprint(len("abc"))'],
               7: ['sorted = 1', 'total = sum([1, 2])'],
               10: ['xs = [3, 1]\nys = sorted(xs)\nxs.append(4)']}
    units = publish.python_name_units(glossary, first_units, lessons)
    assert units['len'] == 7  # the glossary key wins over an earlier lesson use
    assert units['append'] == 10 and units['float'] == 2
    assert units['sum'] == 7
    assert units['sorted'] == 10  # assigning to the name is not a use
    assert 'open' not in units


def test_python_name_mentioned_before_it_is_taught_is_not_indexed():
    qmd = 'Do not use `sorted`, `sum(xs)`, or `open`. Use `len(s)`.\n'
    name_units = {'sorted': 10, 'sum': 7, 'len': 3}
    early = publish.index_first_prose(qmd, [], 3, {}, name_units)
    assert r'\texttt{sorted}' not in early and r'\texttt{sum}' not in early
    assert r'\texttt{open}' not in early  # no teaching unit: never indexed
    assert '`len(s)`' + r'\index{Python names!len@\texttt{len}}' in early
    late = publish.index_first_prose(qmd, [], 10, {}, name_units)
    assert r'\index{Python names!sorted@\texttt{sorted}}' in late
    assert r'\index{Python names!sum@\texttt{sum}}' in late
    ungated = publish.index_first_prose(qmd, [])
    assert publish_audit.index_source_findings(ungated, [], 3, {}, name_units) == [
        r'FAIL: index before taught in unit 3: Python names!sorted@\texttt{sorted}',
        r'FAIL: index before taught in unit 3: Python names!sum@\texttt{sum}',
        r'FAIL: index before taught in unit 3: Python names!open@\texttt{open}']
    assert publish_audit.index_source_findings(late, [], 10, {}, name_units) == []


def test_python_concepts_python_names_wait_for_their_teaching_unit():
    book = Path(__file__).resolve().parents[1] / 'python-concepts'
    source = (book / 'back-matter' / 'glossary.md').read_text(encoding='utf-8')
    glossary = publish.glossary_entries(source)
    units = publish.python_name_units(glossary, publish.glossary_units(source), publish.lesson_code(book))
    names = publish.PYTHON_INDEX_NAMES - {term.casefold() for term, _, _ in glossary}
    assert names <= set(units)
    assert units['sorted'] > 3
