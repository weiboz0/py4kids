"""Shared fixtures for the publication tests: a minimal `publication.yaml` (design 010 D1)."""
from __future__ import annotations

from pathlib import Path

import yaml

from tools.books import PublicationConfig, publication_config

REPO = Path(__file__).resolve().parents[1]

MINIMAL_CONFIG = """\
setup:
  source: docs/unit-00-getting-set-up.md
  teacher_notes: docs/unit-00-teacher-notes.md
  numbered: true
project_headers: {}
lesson_heading: '^## Lesson\\b'
audit:
  goals_recap: required
"""


def write_publication_config(book_root: Path, text: str = MINIMAL_CONFIG, **changes) -> Path:
    """Write `<book_root>/publication.yaml`: the minimal config with top-level keys replaced."""
    data = yaml.safe_load(text)
    data.update(changes)
    path = Path(book_root) / 'publication.yaml'
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding='utf-8')
    return path


def fixture_config(**changes) -> PublicationConfig:
    """An in-memory config for low-level renderer tests (no files needed)."""
    values = {'book': 'fixture', 'setup_source': 'docs/unit-00-getting-set-up.md',
              'setup_teacher_notes': 'docs/unit-00-teacher-notes.md', 'setup_numbered': True,
              'project_headers': {}, 'lesson_heading': r'^## Lesson\b', 'index_names': frozenset()}
    values.update(changes)
    return PublicationConfig(**values)


def python_concepts_config() -> PublicationConfig:
    return publication_config(REPO, 'python-concepts')
