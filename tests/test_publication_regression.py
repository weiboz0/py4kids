"""Plan 097 regression contract: python-concepts' generated Quarto projects equal the immutable
pre-change baseline, except for files listed (with a D2/D3 reason) in the allowed-diffs list."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

import yaml

from tools.publish import EDITIONS, build

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / 'tests' / 'data'
BASELINE = DATA / 'python-concepts-publish-baseline.json'
ALLOWED = DATA / 'python-concepts-publish-allowed-diffs.yaml'


def digest(project: Path) -> dict[str, str]:
    """SHA-256 of every generated .qmd and inventory.json of one edition's Quarto project."""
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(project.iterdir())
            if path.suffix == '.qmd' or path.name == 'inventory.json'}


def allowed_diffs() -> dict[tuple[str, str], str]:
    entries = yaml.safe_load(ALLOWED.read_text(encoding='utf-8'))['allowed_diffs'] or []
    allowed = {}
    for entry in entries:
        assert set(entry) == {'edition', 'file', 'reason'}, entry
        assert entry['edition'] in EDITIONS, entry
        assert re.search(r'\bD[23]\b', entry['reason']), f'reason must name a design 010 D2/D3 rule: {entry}'
        allowed[(entry['edition'], entry['file'])] = entry['reason']
    return allowed


def test_baseline_covers_every_edition():
    baseline = json.loads(BASELINE.read_text(encoding='utf-8'))
    assert set(baseline['editions']) == set(EDITIONS)
    for edition, files in baseline['editions'].items():
        assert 'inventory.json' in files and any(name.endswith('.qmd') for name in files), edition


def test_python_concepts_output_matches_the_baseline(tmp_path):
    # Build from a copy so the test never touches python-concepts/build (the rendered editions).
    shutil.copy(REPO / 'books.yaml', tmp_path / 'books.yaml')
    shutil.copytree(REPO / 'python-concepts', tmp_path / 'python-concepts',
                    ignore=shutil.ignore_patterns('build'))
    baseline = json.loads(BASELINE.read_text(encoding='utf-8'))['editions']
    differing = set()
    for edition in EDITIONS:
        current = digest(build(tmp_path, 'python-concepts', edition))
        expected = baseline[edition]
        differing |= {(edition, name) for name in set(current) | set(expected)
                      if current.get(name) != expected.get(name)}
    allowed = allowed_diffs()
    assert differing <= set(allowed), f'unlisted differences from the baseline: {sorted(differing - set(allowed))}'
    assert set(allowed) <= differing, f'stale allowed-diffs entries: {sorted(set(allowed) - differing)}'
