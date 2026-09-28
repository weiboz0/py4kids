"""Unit 0 publication contracts."""

import json
from pathlib import Path

import pytest

from tools import publish
from tools.publish import allowed_source, build
from tools.publish_audit import _missing_lesson_headings


@pytest.fixture
def book(tmp_path):
    (tmp_path / 'books.yaml').write_text('books:\n- id: book1b\n')
    root = tmp_path / 'book1b'
    (root / 'docs').mkdir(parents=True)
    (root / 'docs' / 'unit-00-getting-set-up.md').write_text(
        '# Unit 0 — Getting Set Up\n\nFirst program.\n\n'
        '## Install Python\n\nNotice: Keep going.\n\n'
        '### Windows\n\n```text\npy --version\n```\n\n'
        '## Checklist\n\n- [ ] Python works.\n')
    (root / 'docs' / 'unit-00-teacher-notes.md').write_text(
        '# Teacher Notes\n\nSETUP_PRIVATE_SENTINEL_1845\n')
    (root / 'front-matter').mkdir()
    (root / 'front-matter' / 'preface.md').write_text('# About This Book\n')
    (root / 'front-matter' / 'how-to-use.md').write_text('# How to use\n')
    (root / 'front-matter' / 'for-teachers.md').write_text('# For teachers\n')
    (root / 'back-matter').mkdir()
    (root / 'back-matter' / 'glossary.md').write_text('# Glossary\n')
    (root / 'back-matter' / 'quick-reference.md').write_text('# Quick Reference\n')
    (root / 'syllabus.md').write_text(
        '# Book 1b — Year 1 Syllabus\n\n'
        '| entry | kind | lessons | the hook |\n|---|---|---|---|\n'
        '| `unit-01-fixture` | unit | 1 | Hook. |\n')
    return tmp_path


def test_setup_chapter_keeps_section_levels_and_teacher_panel(book):
    source = book / 'book1b' / 'docs' / 'unit-00-getting-set-up.md'
    student, inventory, items, title = publish.render_setup_chapter(source, 'student')
    teacher, _, _, _ = publish.render_setup_chapter(source, 'teacher')
    assert student.startswith('# Unit 0 — Getting Set Up {pub-label="Unit 0" pub-mainmatter="true"}')
    assert r'\chaptermark{Unit 0 — Getting Set Up}' in student
    assert '::: {.opener}\nFirst program.' in student
    assert '## Install Python' in student and '## Checklist' in student
    assert '### Windows' in student and '#### Windows' not in student
    assert '::: {.notice}\nKeep going.' in student
    assert '```text\npy --version\n```' in student
    assert '- [ ] Python works.' in student
    assert student.index('::: {.opener}') < teacher.index('::: {.teacher}') < teacher.index('## Install Python')
    assert 'SETUP_PRIVATE_SENTINEL_1845' not in student
    assert 'SETUP_PRIVATE_SENTINEL_1845' in teacher
    assert inventory == items == [] and title == 'Unit 0 — Getting Set Up'


def test_setup_source_is_allowed_but_all_teacher_notes_are_denied():
    assert allowed_source(Path('book1b/docs/unit-00-getting-set-up.md'), 'student')
    for name in ('unit-00-teacher-notes.md', 'teacher-notes.md', 'other-teacher-notes-extra.md'):
        assert not allowed_source(Path('book1b/docs') / name, 'student')


def test_setup_is_first_separate_chapter_in_both_editions(book, monkeypatch):
    from tools import publish

    monkeypatch.setattr(publish, 'render_chapter',
                        lambda entry, kind, edition: ('# Unit 1 — Fixture\n', [], [], 'Fixture'))
    for edition in ('student', 'teacher'):
        project = build(book, 'book1b', edition)
        chapters = json.loads((project / 'inventory.json').read_text())['chapters']
        assert [chapter['kind'] for chapter in chapters] == (
            ['front', 'front'] + (['front'] if edition == 'teacher' else [])
            + ['setup', 'unit'] + (['answers'] if edition == 'student' else [])
            + ['glossary', 'quickref', 'index'])
        assert [(c['id'], c['kind']) for c in chapters if c['kind'] in {'setup', 'unit'}] == [
            ('unit-00-getting-set-up', 'setup'), ('unit-01-fixture', 'unit')]
        assert next(c for c in chapters if c['kind'] == 'setup')['source'] == 'book1b/docs/unit-00-getting-set-up.md'
        config = (project / '_quarto.yml').read_text()
        assert config.index('unit-00-getting-set-up.qmd') < config.index('unit-01-fixture.qmd')
        assert (project / 'the-index.qmd').read_text() == '\\printindex\n'
        assert 'pub-mainmatter="true"' in (project / 'unit-00-getting-set-up.qmd').read_text()
        project_text = '\n'.join(p.read_text() for p in project.glob('*.qmd'))
        if edition == 'student':
            assert 'SETUP_PRIVATE_SENTINEL_1845' not in project_text
        else:
            assert 'SETUP_PRIVATE_SENTINEL_1845' in project_text


def test_setup_outline_requires_chapter_and_every_level_two_section(book):
    chapter = [{'id': 'unit-00-getting-set-up', 'kind': 'setup',
                'source': 'book1b/docs/unit-00-getting-set-up.md'}]
    complete = ('+\t"Unit 0 — Getting Set Up"\t#page=1\n'
                '|\t\t"Install Python"\t#page=1\n'
                '|\t\t"Checklist"\t#page=2\n')
    assert _missing_lesson_headings(chapter, book, complete) == []
    assert _missing_lesson_headings(chapter, book, complete.replace('"Checklist"', '"Windows"')) == [
        'unit-00-getting-set-up: Checklist']
    assert _missing_lesson_headings(chapter, book, complete.replace('\t\t"Install Python"', '\t\t\t"Install Python"')) == [
        'unit-00-getting-set-up: Install Python']
    assert _missing_lesson_headings(chapter, book, complete.replace('Unit 0 — Getting Set Up', 'Unit 1 — Fixture')) == [
        'unit-00-getting-set-up: Unit 0 — Getting Set Up',
        'unit-00-getting-set-up: Install Python', 'unit-00-getting-set-up: Checklist']
