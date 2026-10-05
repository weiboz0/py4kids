"""`site-check`: the bundle's ids, answer model and coverage (design 012 D3-D5, D7; plan 101 E).

`site_check_findings(root, book)` exports the book to `build/site-check/<book>/` and returns, in
this order:

1. `site.yaml` errors (then nothing else: the export needs the config);
2. schema errors, then missing and duplicate ids (the export fails on them, so nothing follows);
3. continuity against the committed ledger (`site/ids/<book>.json`);
4. `tag_findings` (misplaced, unknown or several `check-*` tags);
5. concept-override `FAIL:`s (unregistered `metadata.concepts` ids on lesson cells and items);
6. the answer-model findings (`answer_model_findings`, plan 101 Phase F);
7. classification coverage: with `classification: confirmed`, a `FAIL:` per item without a
   `check-*` tag; then one `INFO:` line with the confirmed/total count and the kinds;
8. a `FAIL:` per real-lesson probe `error` or `timeout`, naming the cell key;
9. `WARN:` per over-budget fixture item, per unmatched sample, per probe `mismatch`.

Only `FAIL:` lines fail. The findings are cached in `build/site-check/<book>/findings.json`, keyed
by the committed git tree hashes of `<book>/`, `tools/`, `books.yaml` and `site/ids/<book>*`; the
cache is read and written only when `git status --porcelain` shows those paths clean.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tools.books import site_config, site_config_errors

from .bundle import ExportError, dumps, export_book
from .ids import continuity_findings

CACHE_VERSION = 1


def answer_model_findings(root: Path, book: str, bundle_dir: Path) -> list[str]:
    """The answer-model checks (D5) over the written bundle in `bundle_dir`.

    Plan 101 Phase F implements this hook (leaks of hidden code, text and prose; odd answers;
    hashes; visibility). Until then it returns no findings.
    """
    return []


def _git(root: Path, *args: str) -> str | None:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                            check=False)
    return result.stdout if result.returncode == 0 else None


def cache_key(root: Path, book: str) -> str | None:
    """The committed tree hashes the findings depend on, or None when a path is dirty (or no git)."""
    paths = [book, "tools", "books.yaml", "site/ids"]
    status = _git(root, "status", "--porcelain", "--untracked-files=all", "--", *paths)
    if status is None:
        return None
    for line in status.splitlines():
        path = line[3:].split(" -> ")[-1].strip('"')
        if not path.startswith("site/ids/") or Path(path).name.startswith(book):
            return None
    parts = []
    for path in (book, "tools", "books.yaml"):
        tree = _git(root, "rev-parse", f"HEAD:{path}")
        if tree is None:
            return None
        parts.append(f"{path}={tree.strip()}")
    listing = _git(root, "ls-tree", "HEAD", "--", "site/ids/")
    if listing is None:
        return None
    for line in sorted(listing.splitlines()):
        meta, _, name = line.partition("\t")
        if Path(name).name.startswith((f"{book}.", f"{book}-")):
            parts.append(f"{name}={meta.split()[2]}")
    return f"v{CACHE_VERSION};" + ";".join(parts)


def _probe_detail(detail: str) -> str:
    lines = [line.strip() for line in (detail or "").splitlines() if line.strip()]
    return lines[-1] if lines else "no detail"


def _classification_findings(book: str, mode: str, report: dict) -> list[str]:
    counts = report["classification"]
    findings = []
    if mode == "confirmed":
        findings += [f"FAIL: {key}: no check-* tag (site.yaml classification: confirmed)"
                     for key in counts["unconfirmed"]]
    kinds = ", ".join(f"{kind} {n}" for kind, n in sorted(counts["by_kind"].items()))
    findings.append(f"INFO: {book}: classification {mode}: {counts['confirmed']}/{counts['total']} "
                    f"items confirmed by check-* tags ({kinds or 'no items'})")
    return findings


def _compute(root: Path, book: str, out_dir: Path) -> list[str]:
    try:
        result = export_book(root, book, out_dir)
    except ExportError as error:
        return list(error.findings)
    except ValueError as error:
        lines = [line for line in str(error).splitlines() if line.strip()]
        return [line if line.startswith("FAIL:") else f"FAIL: {book}: export: {line}"
                for line in lines]
    report = result.report
    findings = continuity_findings(root, book, result.keys)
    findings += report["tag_findings"]
    findings += report["concept_findings"]
    findings += answer_model_findings(root, book, out_dir)
    findings += _classification_findings(book, site_config(root, book).classification, report)
    for key, probe in sorted(report["probes"].items()):
        if probe["status"] in ("error", "timeout"):
            findings.append(f"FAIL: {key}: lesson probe {probe['status']}: "
                            f"{_probe_detail(probe['detail'])}")
    for key, cases in sorted(report["over_budget"].items()):
        findings.append(f"WARN: {key}: fixture case(s) {', '.join(map(str, cases))} over the "
                        f"{site_config(root, book).fixture_budget_kb} KB budget")
    findings += [f"WARN: {key}: no fixture pair matches the statement's Sample Input"
                 for key in sorted(report["unmatched_samples"])]
    findings += [f"WARN: {key}: lesson probe mismatch (not card-eligible)"
                 for key, probe in sorted(report["probes"].items()) if probe["status"] == "mismatch"]
    return findings


def site_check_findings(root: Path, book: str) -> list[str]:
    """The ordered site-check findings for `book` (see the module docstring)."""
    root = Path(root)
    config = site_config_errors(root, book)
    if config:
        return config
    out_dir = root / "build" / "site-check" / book
    cache = out_dir / "findings.json"
    key = cache_key(root, book)
    if key is not None and cache.is_file():
        try:
            cached = json.loads(cache.read_text(encoding="utf-8"))
        except ValueError:
            cached = {}
        if cached.get("key") == key and isinstance(cached.get("findings"), list):
            return cached["findings"]
    findings = _compute(root, book, out_dir)
    if key is not None and key == cache_key(root, book):
        out_dir.mkdir(parents=True, exist_ok=True)
        cache.write_text(dumps({"key": key, "findings": findings}), encoding="utf-8")
    return findings
