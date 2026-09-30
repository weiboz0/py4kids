"""Plan 098 Phase A: publisher and audit gaps exposed by *Python by Projects* (one fixture per fix)."""
from __future__ import annotations

from pathlib import Path

import nbformat
import pytest

from tools.publish import (
    EDITIONS,
    answer_key,
    item_groups,
    render_items,
    split_challenges,
    student_answer_sources,
)
from tools.publish_audit import (
    challenge_findings,
    fenced_code_lines,
    markdown_artefact_findings,
    reference_findings,
    starter_kinds,
    starter_panel_findings,
)

md = nbformat.v4.new_markdown_cell
code = nbformat.v4.new_code_cell


def _write(path: Path, cells) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nbformat.v4.new_notebook(cells=cells), path)


# --- A1: project preface code cells are Starter panels in every edition -----------------------------

def _brief(entry: Path) -> None:
    _write(entry / 'brief.ipynb', [
        md('# Arcade Night\n\nHook.', id='hook'),
        md('## Milestone 1\n\n### Open the arcade\n\nRun this starter.\n\n```python\nchoice = ""\n```',
           id='m1'),
        code('choice = ""', id='menu-scaffold'),  # every code line is in the statement: still printed
        md('## Milestone 2\n\nFinish the game.', id='m2'),
        code('import random\n\ndef lucky_guess():\n    return 0  # TODO', id='lucky-scaffold'),
        code('', id='empty-scaffold'),
        md('## Make it yours\n\nAdd a game.', id='yours'),
    ])


@pytest.mark.parametrize('edition', [name for name, edition in EDITIONS.items() if edition['body'] == 'book'])
def test_project_preface_scaffolds_are_starters_in_every_edition(tmp_path, edition):
    entry = tmp_path / 'projects' / 'project-01-fixture'
    _brief(entry)
    body, inventory, items = render_items(entry / 'brief.ipynb', 'project', edition, entry, entry.name)
    assert items == []
    assert inventory == [{'id': 'menu-scaffold', 'kind': 'starter'},
                         {'id': 'lucky-scaffold', 'kind': 'starter'},
                         {'id': 'empty-scaffold', 'kind': 'starter'}]
    assert body.count('::: {.starter}') == 2
    assert body.index('### Milestone 1') < body.index('::: {.starter}\n```python\nchoice = ""')
    assert body.index('### Milestone 2') < body.index('def lucky_guess')
    kinds = starter_kinds(entry, 'project', edition)
    assert [(cell_id, kind) for cell_id, (kind, _) in kinds.items()] == [
        ('menu-scaffold', 'starter'), ('lucky-scaffold', 'starter'), ('empty-scaffold', 'starter')]


def test_print_starter_panel_count_includes_project_scaffolds(tmp_path):
    entry = tmp_path / 'projects' / 'project-01-fixture'
    _brief(entry)
    body, inventory, _ = render_items(entry / 'brief.ipynb', 'project', 'student-print', entry, entry.name)
    by_id = {record['id']: record['kind'] for record in inventory}
    starters = [(cell_id, source, by_id.get(cell_id, 'missing'))
                for cell_id, (_, source) in starter_kinds(entry, 'project', 'student-print').items()]
    assert starter_panel_findings('project-01-fixture', body, starters) == []
    # A dropped scaffold panel is caught by the count.
    dropped = body.replace('::: {.starter}\n```python\nchoice = ""\n```\n:::', '')
    assert 'FAIL: student-print: project-01-fixture: Starter panel count' in starter_panel_findings(
        'project-01-fixture', dropped, starters)


# --- A2: colon-form item titles ---------------------------------------------------------------------

def test_colon_form_titles_and_challenge_lead(tmp_path):
    entry = tmp_path / 'units' / 'unit-08-fixture'
    _write(entry / 'exercises.ipynb', [
        md('# Word Wizard Exercises', id='title'),
        md('## Exercise 1: Build a Phrasebook\n\nMake a dictionary.', id='e1'),
        code('', id='e1-work'),
        md('## Exercise 2: Merge the Books\n\n**Challenge:** merge two dictionaries.\n\n'
           '**Real version:** read the pairs.', id='e2', metadata={'tags': ['stretch']}),
        code('', id='e2-work', metadata={'tags': ['stretch']}),
    ])
    body, _, items = render_items(entry / 'exercises.ipynb', 'unit', 'student', entry, entry.name)
    assert items == [{'number': 1, 'title': 'Build a Phrasebook'}, {'number': 2, 'title': 'Merge the Books'}]
    assert '### Exercise 1 — Build a Phrasebook\n' in body
    assert '### Challenge — Merge the Books\n' in body
    assert '::: {.challenge}\n**Exercise 2**\n:::\n\nMerge two dictionaries.' in body
    assert '**Challenge:**' not in body
    assert 'Exercise 1:' not in body and 'Exercise 2:' not in body


def test_challenge_lead_kept_without_a_heading_title(tmp_path):
    entry = tmp_path / 'units' / 'unit-01-fixture'
    _write(entry / 'exercises.ipynb', [
        md('# Practice', id='title'),
        md('## Exercise 1\n\n### A title\n\n**Challenge:** keep me.', id='e1', metadata={'tags': ['stretch']}),
    ])
    body, _, _ = render_items(entry / 'exercises.ipynb', 'unit', 'student', entry, entry.name)
    assert '**Challenge:** keep me.' in body


# --- A3: unnumbered challenge items -----------------------------------------------------------------

def _exercises(heading_one: str, heading_two: str, heading_three: str, note: bool = True):
    cells = [
        md('# Practice', id='title'),
        md('## Exercise 1\n\n### Warm up\n\nPrint hello.', id='e1'),
        code('', id='e1-work'),
        md('## Exercise 2\n\n### Loop it\n\nPrint three times.', id='e2'),
        code('# loop here', id='e2-work'),
    ]
    if note:
        cells += [md('## Challenge', id='note', metadata={'tags': ['stretch']}),
                  md('Try these after the earlier exercises.', id='note-intro')]
    cells += [
        md(f'{heading_one}\n\nWrite a story.\n\n**Real version:** read the hero — see the solution.',
           id='c1', metadata={'tags': ['stretch']}),
        code('hero = ""  # your story', id='c1-work', metadata={'tags': ['stretch']}),
        md(f'{heading_two}\n\nBuild a cipher.', id='c2', metadata={'tags': ['stretch']}),
        code('', id='c2-work', metadata={'tags': ['stretch']}),
        md(f'{heading_three}\n\nDraw a flower.', id='c3', metadata={'tags': ['stretch']}),
    ]
    return cells


def _solutions(layout: str, level: str = '###'):
    cells = [
        md('# Solutions', id='s-title'),
        md('## Exercise 1', id='s1'),
        code('print("hello")\nassert True', id='s1-code'),
        md('## Exercise 2', id='s2'),
        code('for n in range(3):\n    print("again and again and again")', id='s2-code'),
    ]
    if layout == 'separate':
        cells += [md('## Challenge', id='s-note'), md(f'{level} Challenge 1\n\nA story.', id='s-c1')]
    else:  # the pre-Phase-B layout: Challenge 1's heading sits inside the note cell
        cells += [md('## Challenge\n\n### Challenge 1\n\nA story.', id='s-note')]
    cells += [
        code('hero = "Zee"\nprint(f"{hero} climbed the silver stairs to the castle.")', id='s-c1-code'),
        md(f'{level} Challenge 2\n\nThe cipher.', id='s-c2'),
        code('message = "abc"[::-1]\nprint(message.upper())\nassert message == "cba"', id='s-c2-code'),
        md(f'{level} Challenge 3\n\nThe flower.', id='s-c3'),
        code('petals = 6\nfor petal in range(petals):\n    print("petal", petal)', id='s-c3-code'),
    ]
    return cells


HEADING_FORMS = [
    # (headings as authored, headings as printed)
    (('### Challenge 1', '### Challenge 2: Two-Step Cipher', '### Challenge 3 — Flower Stamp'),
     ('### Challenge 1\n', '### Challenge 2 — Two-Step Cipher\n', '### Challenge 3 — Flower Stamp\n')),
    (('## Challenge 1', '## Challenge 2: Two-Step Cipher', '## Challenge 3 — Flower Stamp'),
     ('### Challenge 1\n', '### Challenge 2 — Two-Step Cipher\n', '### Challenge 3 — Flower Stamp\n')),
]


@pytest.mark.parametrize('layout', ['separate', 'embedded'])
@pytest.mark.parametrize('forms', HEADING_FORMS, ids=['level-3', 'level-2'])
def test_unnumbered_challenges_render_with_teacher_answers(tmp_path, forms, layout):
    authored, printed = forms
    level2 = authored[0].startswith('## ')
    entry = tmp_path / 'units' / 'unit-01-fixture'
    _write(entry / 'exercises.ipynb', _exercises(*authored, note=not level2))
    _write(entry / 'solutions.ipynb', _solutions(layout, '##' if level2 and layout == 'separate' else '###'))
    (entry / 'assets').mkdir()
    (entry / 'assets' / 'solutions_challenge3.py').write_text('print("flower")\n')

    # Exercise numbering and counts are unchanged; no challenge cell joins the last exercise.
    _, groups = item_groups(nbformat.read(entry / 'exercises.ipynb', as_version=4).cells, 'Exercise')
    assert [group['number'] for group in groups] == [1, 2]
    assert [c.id for c in groups[-1]['cells']] == ['e2', 'e2-work']

    for edition in ('student', 'student-print', 'teacher'):
        body, inventory, items = render_items(entry / 'exercises.ipynb', 'unit', edition, entry, entry.name)
        assert [item['number'] for item in items] == [1, 2]
        for heading in printed:
            assert body.count(heading) == 1, (edition, heading)
        assert body.index(printed[0]) < body.index(printed[1]) < body.index(printed[2])
        # The marker reads plain "Challenge": the heading above it already names the number.
        assert body.count('::: {.challenge}\n**Challenge**\n:::') == 3
        assert '**Challenge 1**' not in body and '**Challenge 3**' not in body
        assert '### Challenge 1\n\n::: {.challenge}\n**Challenge**\n:::' in body
        assert 'Write a story.' in body and 'Draw a flower.' in body
        assert r'\label{ex:unit-01-fixture:' not in body.split('### Challenge 1', 1)[1]
        assert 'Answer on page' not in body.split('### Challenge 1', 1)[1]
        # The Starter is kept (it is not in the statement); the empty one is inventoried.
        assert '::: {.starter}\n```python\nhero = ""  # your story' in body
        kinds = [record['kind'] for record in inventory if record['id'] in {'c1-work', 'c2-work'}]
        assert kinds == (['starter', 'starter-omitted'] if edition == 'student-print' else ['starter', 'starter'])
        if not level2:
            assert body.count('### Challenge\n\nTry these after the earlier exercises.') == 1
        if edition != 'teacher':
            assert '::: {.realprog}\nRead the hero.\n:::' in body  # the solution pointer goes

    key = answer_key(entry, 'unit', items)
    answers = key.split('### Challenge 1', 1)
    assert len(answers) == 2 and '### Exercise 2' in answers[0]
    assert '### Challenge 1\n\nA story.\n\n```{.python .answer-code}\nhero = "Zee"' in key
    assert 'A story.' in answers[1] and 'The cipher.' in answers[1]
    assert 'Check: `message` → `"cba"`' in answers[1]
    assert '**solutions_challenge3.py**' in answers[1]
    teacher_body, _, _ = render_items(entry / 'exercises.ipynb', 'unit', 'teacher', entry, entry.name)
    teacher_qmd = teacher_body + '\n\n' + key
    assert challenge_findings('unit-01-fixture', teacher_qmd, entry, 'teacher') == []
    missing = teacher_qmd.replace('### Challenge 3 — Flower Stamp\n\nThe flower.', 'The flower.')
    missing = missing[:missing.index('## Answer key')] + missing[missing.index('## Answer key'):].replace(
        '### Challenge 3 — Flower Stamp', 'Flower Stamp')
    assert challenge_findings('unit-01-fixture', missing, entry, 'teacher') == [
        'FAIL: teacher: unit-01-fixture: challenge answer coverage']

    # The student editions print no challenge answers: the odd answers are exercises only.
    odd, _ = student_answer_sources(entry)
    assert [group['number'] for group in odd] == [1]
    assert 'hero = "Zee"' not in answer_key(entry, 'unit', items, edition='student')
    student_body, _, _ = render_items(entry / 'exercises.ipynb', 'unit', 'student', entry, entry.name)
    assert challenge_findings('unit-01-fixture', student_body, entry, 'student') == []
    assert challenge_findings('unit-01-fixture', student_body.replace('### Challenge 2', 'Challenge 2'),
                              entry, 'student') == ['FAIL: student: unit-01-fixture: rendered challenge items']

    # The audit's Starter expectations include the challenges, in document order.
    kinds = starter_kinds(entry, 'unit', 'student-print')
    assert list(kinds) == ['e1-work', 'e2-work', 'c1-work', 'c2-work']
    assert [kind for kind, _ in kinds.values()][2:] == ['starter', 'starter-omitted']


def _unit_with_lead_in(entry: Path) -> None:
    """A challenge section whose lead-in holds a code cell, and a challenge whose statement starts
    `**Challenge:**`."""
    _write(entry / 'exercises.ipynb', [
        md('# Practice', id='title'),
        md('## Exercise 1\n\n### Warm up\n\nPrint hello.', id='e1'),
        code('greeting = "hi"  # finish me', id='e1-work'),
        md('## Challenge', id='note', metadata={'tags': ['stretch']}),
        code('shared = [1, 2, 3]  # used by every challenge', id='lead-code'),
        md('### Challenge 1: Twice\n\n**Challenge:** double every number.', id='c1',
           metadata={'tags': ['stretch']}),
        code('doubled = []  # your loop', id='c1-work', metadata={'tags': ['stretch']}),
    ])
    _write(entry / 'solutions.ipynb', [
        md('# Solutions', id='s-title'),
        md('## Exercise 1', id='s1'),
        code('print("hello")', id='s1-code'),
        md('## Challenge', id='s-note'),
        md('### Challenge 1', id='s-c1'),
        code('doubled = [n * 2 for n in shared]\nprint(doubled)', id='s-c1-code'),
    ])


@pytest.mark.parametrize('edition', ['student', 'student-print', 'teacher'])
def test_unnumbered_challenge_strips_its_challenge_lead(tmp_path, edition):
    entry = tmp_path / 'units' / 'unit-01-fixture'
    _unit_with_lead_in(entry)
    body, _, _ = render_items(entry / 'exercises.ipynb', 'unit', edition, entry, entry.name)
    assert '### Challenge 1 — Twice\n\n::: {.challenge}\n**Challenge**\n:::\n\nDouble every number.' in body
    assert '**Challenge:**' not in body


@pytest.mark.parametrize('edition', ['student', 'student-print', 'teacher'])
def test_challenge_lead_in_code_cells_are_starters_after_the_exercises(tmp_path, edition):
    entry = tmp_path / 'units' / 'unit-01-fixture'
    _unit_with_lead_in(entry)
    body, inventory, _ = render_items(entry / 'exercises.ipynb', 'unit', edition, entry, entry.name)
    lead_panel = '::: {.starter}\n```python\nshared = [1, 2, 3]  # used by every challenge\n```\n:::'
    assert body.count(lead_panel) == 1
    assert body.index('greeting = "hi"') < body.index(lead_panel) < body.index('### Challenge 1')
    assert [record['id'] for record in inventory] == ['e1-work', 'lead-code', 'c1-work']
    assert {record['kind'] for record in inventory} == {'starter'}
    # The audit's expectations follow the publisher's print order: exercises, lead-in, challenges.
    kinds = starter_kinds(entry, 'unit', edition)
    assert list(kinds) == ['e1-work', 'lead-code', 'c1-work']
    by_id = {record['id']: record['kind'] for record in inventory}
    starters = [(cell_id, source, by_id[cell_id]) for cell_id, (_, source) in kinds.items()]
    assert starter_panel_findings('unit-01-fixture', body, starters) == []


def test_challenge_answer_findings_empty_and_duplicate_sections(tmp_path):
    entry = tmp_path / 'units' / 'unit-01-fixture'
    _unit_with_lead_in(entry)
    body, _, items = render_items(entry / 'exercises.ipynb', 'unit', 'teacher', entry, entry.name)
    qmd = body + '\n\n' + answer_key(entry, 'unit', items)
    assert challenge_findings('unit-01-fixture', qmd, entry, 'teacher') == []

    # A challenge heading with no answer under it is a finding.
    cells = nbformat.read(entry / 'solutions.ipynb', as_version=4).cells
    _write(entry / 'solutions.ipynb', cells[:-1])
    empty = body + '\n\n' + answer_key(entry, 'unit', items)
    assert '### Challenge 1 — Twice' in empty
    assert challenge_findings('unit-01-fixture', empty, entry, 'teacher') == [
        'FAIL: teacher: unit-01-fixture: empty answer for Challenge 1']

    # A repeated challenge heading in the solutions (or the exercises) is a finding.
    _write(entry / 'solutions.ipynb', [*cells, md('### Challenge 1\n\nAgain.', id='s-c1-again')])
    assert 'FAIL: teacher: unit-01-fixture: duplicate challenge headings in solutions: 1' in challenge_findings(
        'unit-01-fixture', qmd, entry, 'teacher')
    _write(entry / 'solutions.ipynb', cells)
    exercises = nbformat.read(entry / 'exercises.ipynb', as_version=4).cells
    _write(entry / 'exercises.ipynb', [*exercises, md('### Challenge 1\n\nOnce more.', id='c1-again')])
    assert 'FAIL: student: unit-01-fixture: duplicate challenge headings in exercises: 1' in challenge_findings(
        'unit-01-fixture', qmd, entry, 'student')


def test_leak_guard_hides_unnumbered_challenge_solutions(tmp_path, monkeypatch):
    from tools import publish_audit

    entry = tmp_path / 'units' / 'unit-01-fixture'
    _unit_with_lead_in(entry)
    monkeypatch.setattr(publish_audit, 'book_path', lambda root, book_id: tmp_path)
    monkeypatch.setattr(publish_audit, 'entries', lambda book, edition: [('unit-01-fixture', entry)])
    build = tmp_path / 'build'
    build.mkdir()
    chapters = [{'id': 'unit-01-fixture', 'kind': 'unit', 'file': 'u.qmd'}]
    kinds = frozenset({'unit'})
    body, _, _ = render_items(entry / 'exercises.ipynb', 'unit', 'student', entry, entry.name)
    (build / 'u.qmd').write_text(body, encoding='utf-8')
    assert publish_audit.leak_findings(tmp_path, 'fixture', chapters, build, kinds=kinds) == []
    leaked = body + '\n```python\ndoubled = [n * 2 for n in shared]\nprint(doubled)\n```\n'
    (build / 'u.qmd').write_text(leaked, encoding='utf-8')
    assert publish_audit.leak_findings(tmp_path, 'fixture', chapters, build, kinds=kinds) == [
        'FAIL: student: unit unit-01-fixture: solution leak from unit-01-fixture Challenge 1']


def test_challenge_title_under_an_exercise_is_not_a_challenge():
    """python-concepts' `### Challenge 1: Title` under `## Exercise N` titles that exercise, and a
    `## Challenge` note followed by exercises stays a section note between items."""
    cells = [md('# Practice'), md('## Exercise 1'), md('### Challenge 1: Alternating Case\n\nDo it.'),
             md('## Challenge'), md('## Exercise 2'), md('### Challenge: Big\n\nGo.')]
    rest, lead_in, challenges = split_challenges(cells)
    assert (len(rest), lead_in, challenges) == (6, [], [])
    _, groups = item_groups(cells, 'Exercise')
    assert [group['number'] for group in groups] == [1, 2]
    assert [c.source for c in groups[1]['interlude']] == ['## Challenge']


def test_exercise_after_a_challenge_section_fails():
    cells = [md('# Practice'), md('## Exercise 1'), md('## Challenge 1: Early'), md('## Exercise 2')]
    with pytest.raises(ValueError, match='challenge section must end the exercises'):
        split_challenges(cells)


# --- A4: the Markdown-artefact check ignores printed code comments ----------------------------------

def test_artefact_check_ignores_heading_lines_printed_from_code_fences():
    qmd = ('### Exercise 1 — Hello\n\n```{.python .answer-code}\n# Exercise 1 —   Hello\nprint("hi")\n```\n')
    fences = fenced_code_lines([qmd])
    assert markdown_artefact_findings('Answers\n# Exercise 1 — Hello\nprint("hi")\n', fences, 'student') == []
    assert markdown_artefact_findings('Answers\n# Exercise 2 — Other\n', fences, 'student') == [
        'FAIL: student: literal Markdown/Quarto artefact in PDF: # Exercise']
    assert markdown_artefact_findings('Text\n# Exercise 1 — Hello\n', set(), 'teacher') == [
        'FAIL: teacher: literal Markdown/Quarto artefact in PDF: # Exercise']
    # A long code comment that the PDF wraps prints as the start of the fence line.
    wrapped = fenced_code_lines(['```python\n# Exercise 1 — greeting card with plain print lines (no variables needed)\n```\n'])
    assert markdown_artefact_findings('# Exercise 1 — greeting card with plain print lines (no variables needed\n',
                                      wrapped, 'student') == []
    # Quarto fence syntax is always an artefact, even when a code block holds the same line.
    assert markdown_artefact_findings('Text\n::: {.notice}\n', fenced_code_lines(['```\n::: {.notice}\n```\n']),
                                      'student') == ['FAIL: student: literal Markdown/Quarto artefact in PDF: ::: {']
    # Prose lines never came from a fence: the Markdown heading outside a fence still counts.
    assert markdown_artefact_findings('## Lesson 2\n', fenced_code_lines(['## Lesson 2\n']), 'student') == [
        'FAIL: student: literal Markdown/Quarto artefact in PDF: ## L']


# --- A5: cross-reference attribution anchors the exercise heading to a whole line --------------------

def _pages(*pages: str) -> str:
    return '\f'.join(pages)


def test_wrapped_prose_does_not_claim_an_answer_reference():
    text = _pages(
        'Unit 5 — Function Factory\n10\nExercise 15 — Stamp Row\nUse the same stamp as\n'
        "Exercise 16's grid.\nAnswer on page 11.\n",
        'Answers to Selected Exercises\n11\nUnit 5, Exercise 15 (page 10)\nprint("row")\n')
    assert reference_findings(text) == []
    # A real mismatch still fails: Exercise 17 has no answer on page 11.
    wrong = text.replace('Exercise 15 — Stamp Row', 'Exercise 17 — Stamp Row')
    assert 'FAIL: student: Unit 5 Exercise 17: answer page 11' in reference_findings(wrong)


def test_bare_exercise_marker_line_still_sets_the_exercise():
    """A stretch item's heading reads "Challenge — Title"; its marker line "Exercise 15" names it."""
    text = _pages(
        'Unit 5 — Function Factory\n10\nChallenge — Stamp Row\nExercise 15\nDo it.\nAnswer on page 11.\n',
        'Answers to Selected Exercises\n11\nUnit 5, Exercise 15 (page 10)\nprint("row")\n')
    assert reference_findings(text) == []


# --- Project milestone answers (Teacher's Edition only) --------------------------------------------

def _milestone_project(entry: Path) -> None:
    _brief(entry)
    _write(entry / 'solutions.ipynb', [
        code('import random\nrandom.seed(4)', id='seed'),
        md('# Arcade Night Reference\n\nThis reference builds the games.', id='s-title'),
        md('## Lucky Guess\n\nA match earns 5 points.', id='s-lucky'),
        code('def lucky_guess(guess):\n    return 5 if guess == "2" else 0', id='s-lucky-code'),
        md('## Milestone 1\n\nThe finished menu.', id='s-m1'),
        code('choice = "q"\nwhile choice != "q":\n    print("menu")\nprint("closed")\nassert choice == "q"',
             id='s-m1-code'),
        md('## Milestone 2\n\n**The real program**\n\n```python\nguess = input("Pick: ")\n```', id='s-m2'),
    ])


def test_project_milestone_answers_in_the_teacher_edition_only(tmp_path):
    from tools.publish_audit import answer_key_coverage_findings

    entry = tmp_path / 'projects' / 'project-01-fixture'
    _milestone_project(entry)
    key = answer_key(entry, 'project', [])
    headings = [line for line in key.splitlines() if line.startswith('#')]
    assert headings == ['## Answer key', '### Lucky Guess', '### Milestone 1 — Open the arcade',
                        '### Milestone 2']
    assert 'random.seed' not in key and 'This reference builds' not in key
    assert 'A match earns 5 points.' in key and 'def lucky_guess' in key
    assert 'Check: `choice` → `"q"`' in key and 'assert ' not in key
    assert '```{.python .answer-code}\nguess = input("Pick: ")' in key
    for edition in ('student', 'student-print'):
        assert answer_key(entry, 'project', [], edition=edition) == ''
    qmd = '# Arcade Night\n\n' + key
    assert answer_key_coverage_findings('project-01-fixture', 'project', qmd, [], entry) == []
    assert answer_key_coverage_findings('project-01-fixture', 'project',
                                        qmd.replace('### Milestone 2\n', ''), [], entry) == [
        'FAIL: teacher: project-01-fixture: answer-key coverage']


def test_project_without_answers_has_no_answer_key_heading(tmp_path):
    from tools.publish_audit import answer_key_coverage_findings

    entry = tmp_path / 'projects' / 'project-01-fixture'
    _brief(entry)
    _write(entry / 'solutions.ipynb', [md('# Reference\n\nNothing to answer yet.')])
    assert answer_key(entry, 'project', []) == ''
    assert answer_key_coverage_findings('project-01-fixture', 'project', '# Arcade Night\n', [], entry) == []
    assert answer_key_coverage_findings('project-01-fixture', 'project', '# A\n\n## Answer key\n', [], entry) == [
        'FAIL: teacher: project-01-fixture: answer-key coverage']


def test_leak_guard_hides_project_milestone_solutions(tmp_path, monkeypatch):
    from tools import publish_audit

    entry = tmp_path / 'projects' / 'project-01-fixture'
    _milestone_project(entry)
    monkeypatch.setattr(publish_audit, 'book_path', lambda root, book_id: tmp_path)
    monkeypatch.setattr(publish_audit, 'entries', lambda book, edition: [('project-01-fixture', entry)])
    project = tmp_path / 'build'
    project.mkdir()
    chapters = [{'id': 'project-01-fixture', 'kind': 'project', 'file': 'p.qmd'}]
    leaked = '```python\ndef lucky_guess(guess):\n    return 5 if guess == "2" else 0\n```\n'
    (project / 'p.qmd').write_text('::: {.starter}\n```python\nchoice = ""\n```\n:::\n', encoding='utf-8')
    kinds = frozenset({'project'})
    assert publish_audit.leak_findings(tmp_path, 'fixture', chapters, project, kinds=kinds) == []
    (project / 'p.qmd').write_text(leaked, encoding='utf-8')
    assert publish_audit.leak_findings(tmp_path, 'fixture', chapters, project, kinds=kinds) == [
        'FAIL: student: project project-01-fixture: solution leak from project-01-fixture Lucky Guess']
