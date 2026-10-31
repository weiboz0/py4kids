"""scripts/aio/aio-provision-cache.sh (design 014 D8, plan aio-001 Phase A).

Group-free and offline: artifacts are served from file:// URLs (curl reads them like any other
source), and the manifest parser runs under this interpreter (pyyaml is a core dependency).
"""

import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "aio" / "aio-provision-cache.sh"

pytestmark = pytest.mark.skipif(
    shutil.which("curl") is None or shutil.which("sha256sum") is None,
    reason="needs curl and sha256sum",
)

CACHE = "aio-ml/reference/cache"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _setup(tmp_path, artifacts):
    """A throwaway repo root with a manifest; `artifacts` maps relative cache path -> bytes
    served from a source directory. Returns (root, {path: source file})."""
    src, root = tmp_path / "src", tmp_path / "repo"
    src.mkdir()
    (root / "aio-ml" / "curriculum").mkdir(parents=True)
    entries, sources = [], {}
    for i, (rel, data) in enumerate(artifacts.items()):
        f = src / f"a{i}.bin"
        f.write_bytes(data)
        sources[rel] = f
        entries.append(
            {"id": f"art{i}", "url": f.as_uri(), "path": f"{CACHE}/{rel}", "sha256": _sha(data)}
        )
    _write_manifest(root, entries)
    return root, sources


def _write_manifest(root, entries):
    (root / "aio-ml" / "curriculum" / "artifacts.yaml").write_text(
        yaml.safe_dump({"schema": 1, "artifacts": entries})
    )


def _manifest(root):
    return yaml.safe_load((root / "aio-ml" / "curriculum" / "artifacts.yaml").read_text())


def _run(root, allow_file=True):
    env = dict(os.environ, AIO_PYTHON=sys.executable)
    if allow_file:
        env["AIO_PROVISION_ALLOW_FILE_URLS"] = "1"
    else:
        env.pop("AIO_PROVISION_ALLOW_FILE_URLS", None)
    return subprocess.run(
        ["bash", str(SCRIPT), "--root", str(root)],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


ARTS = {"gensim/information.json": b'{"models": {}}', "torch/hub/checkpoints/w.pth": b"\x00w" * 50}


def test_fetch_verify_then_skip(tmp_path):
    root, _ = _setup(tmp_path, ARTS)
    first = _run(root)
    assert first.returncode == 0, first.stderr
    assert "PASS (2 fetched, 0 already present)" in first.stdout
    for rel, data in ARTS.items():
        assert (root / CACHE / rel).read_bytes() == data
        assert not (root / CACHE / f"{rel}.tmp").exists()
    second = _run(root)  # idempotent: nothing is downloaded again
    assert second.returncode == 0, second.stderr
    assert "PASS (0 fetched, 2 already present)" in second.stdout
    assert "GET" not in second.stdout


def test_skip_does_not_download(tmp_path):
    root, sources = _setup(tmp_path, ARTS)
    assert _run(root).returncode == 0
    for f in sources.values():
        f.unlink()  # a present, verified file needs no source at all
    res = _run(root)
    assert res.returncode == 0, res.stderr
    assert "2 already present" in res.stdout


def test_corrupt_local_file_is_refetched(tmp_path):
    root, _ = _setup(tmp_path, ARTS)
    assert _run(root).returncode == 0
    target = root / CACHE / "torch/hub/checkpoints/w.pth"
    target.write_bytes(b"X" + target.read_bytes()[1:])
    res = _run(root)
    assert res.returncode == 0, res.stderr
    assert "wrong sha256; re-fetching" in res.stderr
    assert "PASS (1 fetched, 1 already present)" in res.stdout
    assert target.read_bytes() == ARTS["torch/hub/checkpoints/w.pth"]


def test_download_mismatch_fails_loudly(tmp_path):
    root, sources = _setup(tmp_path, ARTS)
    sources["gensim/information.json"].write_bytes(b"tampered upstream")
    res = _run(root)
    assert res.returncode != 0
    assert "sha256 MISMATCH" in res.stderr
    dest = root / CACHE / "gensim/information.json"
    assert not dest.exists() and not Path(f"{dest}.tmp").exists()  # nothing moved into place


def test_failed_download_fails(tmp_path):
    root, sources = _setup(tmp_path, ARTS)
    sources["gensim/information.json"].unlink()
    res = _run(root)
    assert res.returncode != 0
    assert "download failed" in res.stderr


def test_missing_manifest_fails(tmp_path):
    res = _run(tmp_path)
    assert res.returncode != 0
    assert "no manifest" in res.stderr


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("path", "aio-ml/data/w.pth", "under a reference/cache/"),
        ("path", f"{CACHE}/../../escape", "normalized repo-relative"),
        ("path", "/abs/reference/cache/x", "normalized repo-relative"),
        ("sha256", "ABC", "64 lowercase hex"),
        ("url", "http://example.com/x", "must be https://"),
    ],
)
def test_manifest_validation(tmp_path, field, value, message):
    root, _ = _setup(tmp_path, ARTS)
    data = _manifest(root)
    data["artifacts"][0][field] = value
    _write_manifest(root, data["artifacts"])
    res = _run(root)
    assert res.returncode != 0
    assert message in res.stderr
    assert not (root / CACHE).exists()  # validation precedes any download


def test_file_urls_refused_by_default(tmp_path):
    root, _ = _setup(tmp_path, ARTS)
    res = _run(root, allow_file=False)
    assert res.returncode != 0
    assert "must be https://" in res.stderr
