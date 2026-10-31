"""Detect reference overlap at the granularity appropriate to each artifact.

Following the plan-004 unit-path precedent, short structured mock manifest specs
provide the failing TF-IDF cosine signal against both reference text and a distinct
reference-summary stream. Full mock statement files retain their verbatim-copy
shingle check and also receive a higher-threshold, warning-only cosine drift signal
reported once per statement-file/corpus-part pair.
"""

from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

import nbformat

from tools.aio.model import Report, _parse_yaml, load_mock_manifests

SHINGLE_SIZE = 8
SHINGLE_THRESHOLD = 2
COSINE_THRESHOLD = 0.35
FILE_COSINE_WARNING_THRESHOLD = 0.5
REMEDY = "reference corpus absent; run bash scripts/aio/fetch-reference.sh"

# Register mandated by mocktests/blueprint.yaml style_rules must not dominate
# mock-test cosine similarity. These patterns intentionally cover only that register.
MOCK_REGISTER_BOILERPLATE_PATTERNS = (
    r"(?im)^\s*(?:\*\*)?Total:\s*\d+\s+points?\.?(?:\*\*)?\s*$",
    r"(?i)(?:#+\s*)?Part\s+\d+\.\d+\s*\(\s*\d+\s+points?\s*\)",
    r"(?i)\bReasoning\s+(?:is\s+)?(?:not\s+)?required\b[.;]?",
    r"(?i)\bCoding\s+(?:is\s+)?(?:not\s+)?(?:allowed|required|needed)\b[.;]?",
    r"(?im)^\s*[-*]?\s*(?:\*\*)?[A-E][.)](?:\*\*)?\s*",
    r"(?im)\bWrite\s+[^\n]*?\s+in\s+the\s+unique\s+form\b[^\n]*",
    r"(?i)\bWhat\s+is\s+\$?p\s*\+\s*q\$?\s*\?",
)


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _shingles(text: str) -> set[tuple[str, ...]]:
    words = _words(text)
    return {tuple(words[i : i + SHINGLE_SIZE]) for i in range(max(0, len(words) - SHINGLE_SIZE + 1))}


LATEX_MATH_PATTERN = re.compile(
    r"\$\$.*?\$\$|\$[^$\n]+\$|\\\[.*?\\\]|\\\(.*?\\\)", re.DOTALL
)


def _without_boilerplate(text: str) -> str:
    # Shared mathematical notation (e.g. a standard DDPM forward step) is not copied
    # prose; drop LaTeX math spans from the artifact before shingling.
    text = LATEX_MATH_PATTERN.sub(" ", text)
    lines = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if (
            stripped.startswith(("import ", "from "))
            or "default_rng" in line
            or "SEED =" in line
        ):
            continue
        lines.append(line)
    return "\n".join(lines)


def _without_mock_register_boilerplate(text: str) -> str:
    for pattern in MOCK_REGISTER_BOILERPLATE_PATTERNS:
        text = re.sub(pattern, " ", text)
    return text


def _tf(text: str) -> Counter[str]:
    return Counter(_words(text))


def _corpus_dfs(documents: list[str]) -> Counter[str]:
    dfs: Counter[str] = Counter()
    for doc in documents:
        dfs.update(set(_words(doc)))
    return dfs


def _cosine(query: str, document: str, doc_count: int, base_dfs: Counter[str]) -> float:
    q_tf = _tf(query)
    d_tf = _tf(document)
    if not q_tf or not d_tf:
        return 0.0
    dfs = base_dfs.copy()
    dfs.update(set(_words(query)))
    terms = set(q_tf) | set(d_tf)
    numerator = 0.0
    q_norm = 0.0
    d_norm = 0.0
    for term in terms:
        idf = math.log((1 + doc_count) / (1 + dfs[term])) + 1
        q_weight = q_tf[term] * idf
        d_weight = d_tf[term] * idf
        numerator += q_weight * d_weight
        q_norm += q_weight * q_weight
        d_norm += d_weight * d_weight
    if q_norm == 0 or d_norm == 0:
        return 0.0
    return numerator / math.sqrt(q_norm * d_norm)


def _collect_text_fields(node: Any) -> list[str]:
    if isinstance(node, dict):
        texts = [str(node["text"])] if node.get("text") else []
        for value in node.values():
            texts.extend(_collect_text_fields(value))
        return texts
    if isinstance(node, list):
        texts: list[str] = []
        for value in node:
            texts.extend(_collect_text_fields(value))
        return texts
    return []


def _collect_summary_fields(node: Any) -> list[str]:
    if isinstance(node, dict):
        summaries = [str(node["summary"])] if node.get("summary") else []
        for value in node.values():
            summaries.extend(_collect_summary_fields(value))
        return summaries
    if isinstance(node, list):
        summaries: list[str] = []
        for value in node:
            summaries.extend(_collect_summary_fields(value))
        return summaries
    return []


def _corpus(
    root: Path,
) -> tuple[list[tuple[str, str]], list[tuple[str, str]], str | None, list[str]]:
    reference = root / "reference"
    # PDFs alone are a valid corpus (spec Task 5); index.yaml text fields are additive.
    if not reference.exists() or not (
        any(reference.glob("*/index.yaml")) or any(reference.glob("*/*.pdf"))
    ):
        return [], [], REMEDY, []
    if shutil.which("pdftotext") is None:
        return [], [], f"pdftotext unavailable; {REMEDY}", []
    parts: list[tuple[str, str]] = []
    summaries: list[tuple[str, str]] = []
    failures: list[str] = []
    for ref_dir in sorted(reference.glob("*")):
        if not ref_dir.is_dir():
            continue
        index = ref_dir / "index.yaml"
        if index.exists():
            try:
                parsed_index = _parse_yaml(index.read_text())
                for offset, text in enumerate(_collect_text_fields(parsed_index)):
                    parts.append((f"{index}#text-{offset}", text))
                for offset, summary in enumerate(_collect_summary_fields(parsed_index)):
                    summaries.append((f"{index}#summary-{offset}", summary))
            except (OSError, ValueError) as exc:
                return [], [], f"{index}: cannot read corpus index ({exc}); {REMEDY}", []
        for pdf in sorted(ref_dir.glob("*.pdf")):
            proc = subprocess.run(
                ["pdftotext", str(pdf), "-"],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                parts.append((str(pdf), proc.stdout))
            else:
                # A silently-dropped corpus part would let copied content escape
                # scanning; surface every extraction failure as a loud warning.
                failures.append(
                    f"corpus part NOT scanned (pdftotext failed, rc={proc.returncode}): {pdf}"
                )
    if not parts:
        return [], [], REMEDY, failures
    return parts, summaries, None, failures


def _problem_texts(root: Path, manifest_path: Path, problem) -> tuple[str, str, list[str]]:
    warnings: list[str] = []
    statement_texts: list[str] = []
    if not problem.files:
        warnings.append(f"{manifest_path}: {problem.id} has no files; scanning spec only")
    for rel in problem.files:
        path = manifest_path.parent / rel
        if path.exists():
            statement_texts.append(path.read_text(errors="ignore"))
        else:
            warnings.append(f"{manifest_path}: {problem.id} listed missing file {rel}")
    return problem.spec, "\n".join(statement_texts), warnings


def _notebook_text(path: Path) -> str:
    notebook = nbformat.read(path, as_version=4)
    return "\n".join(
        str(cell.get("source", ""))
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") in {"markdown", "code"}
    )


def _statement_file_text(path: Path) -> str:
    if path.suffix == ".ipynb":
        return _notebook_text(path)
    return path.read_text(errors="ignore")


def _expected_corpus_parts(root: Path) -> list[Path]:
    """Every PDF corpus part a book's `reference/` holds (what extraction must yield)."""
    reference = root / "reference"
    return sorted(reference.glob("*/*.pdf")) if reference.is_dir() else []


def _corpus_reconciliation(
    root: Path, corpus: list[tuple[str, str]], failures: list[str]
) -> tuple[str, list[str]]:
    """py4kids aio-001: expected versus extracted corpus parts, and every shortfall as an error."""
    expected = _expected_corpus_parts(root)
    extracted = {label for label, _ in corpus if label.endswith(".pdf")}
    index_parts = sum(1 for label, _ in corpus if not label.endswith(".pdf"))
    note = (
        f"{root.name} corpus: PDF parts expected {len(expected)}, extracted {len(extracted)}; "
        f"index text parts {index_parts}; extraction failures {len(failures)}"
    )
    errors = [f"--require-corpus: {failure}" for failure in failures]
    errors.extend(
        f"--require-corpus: corpus part not extracted: {pdf}"
        for pdf in expected
        if str(pdf) not in extracted and not any(str(pdf) in failure for failure in failures)
    )
    return note, errors


def check_overlap(
    root: str | Path, *, book_number: int | None = None, require_corpus: bool = False
) -> Report:
    root = Path(root)
    corpus, summary_corpus, skipped, corpus_failures = _corpus(root)
    notes: list[str] = []
    if require_corpus:
        # py4kids aio-001 Phase D: a missing corpus or ANY extraction warning fails the scan.
        if skipped:
            return Report(
                name="overlap-scan", ok=False, errors=[f"--require-corpus: {skipped}"]
            )
        note, corpus_errors = _corpus_reconciliation(root, corpus, corpus_failures)
        notes.append(note)
        if corpus_errors:
            return Report(name="overlap-scan", ok=False, errors=corpus_errors, notes=notes)
    elif skipped:
        return Report(name="overlap-scan", ok=True, skipped=skipped)
    corpus_texts = [text for _, text in corpus]
    corpus_cosine_texts = [_without_mock_register_boilerplate(text) for text in corpus_texts]
    # Hoisted per-corpus precomputation: shingles per reference doc + document frequencies
    # (previously recomputed inside the per-problem loop — O(P x R x |corpus|)).
    corpus_shingles = [
        (label, text, _shingles(text), _without_mock_register_boilerplate(text))
        for label, text in corpus
    ]
    base_dfs = _corpus_dfs(corpus_cosine_texts)
    doc_count = len(corpus_texts) + 1
    summary_cosine_texts = [
        (label, _without_mock_register_boilerplate(text))
        for label, text in summary_corpus
    ]
    summary_base_dfs = _corpus_dfs([text for _, text in summary_cosine_texts])
    summary_doc_count = len(summary_cosine_texts) + 1
    errors: list[str] = []
    warnings: list[str] = list(corpus_failures)
    statement_paths: set[Path] = set()
    for manifest in load_mock_manifests(root, book_number=book_number):
        for problem in manifest.problems:
            spec_text, statement_text, text_warnings = _problem_texts(
                root, manifest.path, problem
            )
            warnings.extend(text_warnings)
            statement_paths.update(
                manifest.path.parent / rel
                for rel in problem.files
                if (manifest.path.parent / rel).exists()
            )
            problem_shingles = _shingles(_without_boilerplate(statement_text))
            cosine_text = _without_mock_register_boilerplate(
                _without_boilerplate(spec_text)
            )
            for label, _, reference_shingles, reference_cosine_text in corpus_shingles:
                overlap = len(problem_shingles & reference_shingles)
                cosine = _cosine(cosine_text, reference_cosine_text, doc_count, base_dfs)
                if overlap >= SHINGLE_THRESHOLD or cosine >= COSINE_THRESHOLD:
                    hit = f"{manifest.path}: {problem.id} overlaps {label} (shingles={overlap}, cosine={cosine:.2f})"
                    if problem.provenance == "adapted" and problem.adapted_from:
                        warnings.append(hit)
                    else:
                        errors.append(hit)
            for label, reference_cosine_text in summary_cosine_texts:
                cosine = _cosine(
                    cosine_text,
                    reference_cosine_text,
                    summary_doc_count,
                    summary_base_dfs,
                )
                if cosine >= COSINE_THRESHOLD:
                    hit = (
                        f"{manifest.path}: {problem.id} overlaps {label} "
                        f"(summary-cosine={cosine:.2f})"
                    )
                    if problem.provenance == "adapted" and problem.adapted_from:
                        warnings.append(hit)
                    else:
                        errors.append(hit)
    for path in sorted(statement_paths):
        cosine_text = _without_mock_register_boilerplate(
            _without_boilerplate(_statement_file_text(path))
        )
        for label, _, _, reference_cosine_text in corpus_shingles:
            cosine = _cosine(cosine_text, reference_cosine_text, doc_count, base_dfs)
            if cosine >= FILE_COSINE_WARNING_THRESHOLD:
                warnings.append(
                    f"{path} has file-level cosine drift with {label} "
                    f"(cosine={cosine:.2f})"
                )
    for path in sorted(root.glob("units/*/practice/*.ipynb")):
        text = _without_boilerplate(_notebook_text(path))
        notebook_shingles = _shingles(text)
        for label, _, reference_shingles, _ in corpus_shingles:
            overlap = len(notebook_shingles & reference_shingles)
            if overlap >= SHINGLE_THRESHOLD:
                errors.append(f"{path} overlaps {label} (shingles={overlap})")
                break
    return Report(
        name="overlap-scan", ok=not errors, errors=errors, warnings=warnings, notes=notes
    )


# --- archive mode (py4kids aio-001 Phase D): `overlap-scan --require-corpus --paths <dir>` ----
# Every file under <dir> is scored by its text against every aio book's reference corpus with
# the verbatim-copy shingle detector (SHINGLE_THRESHOLD shingles of SHINGLE_SIZE words), the
# rule the scanner applies to practice notebooks. Fail closed: a file with any other extension,
# a file that does not decode or parse, a missing corpus or any corpus extraction failure fails.

ARCHIVE_TEXT_SUFFIXES = frozenset({
    ".md", ".yaml", ".yml", ".py", ".sh", ".txt", ".csv", ".json", ".toml", ".lua", ".tex",
})
ARCHIVE_TEXT_NAMES = frozenset({".gitignore", ".gitkeep"})


def _archive_notebook_text(path: Path) -> str:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(notebook, dict) or not isinstance(notebook.get("cells"), list):
        raise ValueError("not a notebook (no cells list)")  # noqa: TRY004
    texts: list[str] = []
    for cell in notebook["cells"]:
        if not isinstance(cell, dict):
            raise ValueError("malformed notebook cell")  # noqa: TRY004
        if cell.get("cell_type") not in {"markdown", "code"}:
            continue
        source = cell.get("source", "")
        if isinstance(source, list):
            source = "".join(str(line) for line in source)
        texts.append(str(source))
    return "\n".join(texts)


def _archive_file_text(path: Path) -> str | None:
    """A scannable file's text, or None when its extension is not scannable."""
    if path.suffix == ".ipynb":
        return _archive_notebook_text(path)
    if path.suffix in ARCHIVE_TEXT_SUFFIXES or path.name in ARCHIVE_TEXT_NAMES:
        return path.read_text(encoding="utf-8", errors="strict")
    return None


def check_overlap_paths(scan_root: str | Path, book_roots: list[Path]) -> Report:
    """Archive mode: scan every file under `scan_root` against all `book_roots` corpora."""
    name = "overlap-scan"
    scan_root = Path(scan_root)
    if not scan_root.is_dir():
        return Report(name=name, ok=False, errors=[f"--paths: not a directory: {scan_root}"])
    errors: list[str] = []
    notes: list[str] = []
    corpus: list[tuple[str, set[tuple[str, ...]]]] = []
    for book_root in book_roots:
        parts, _summaries, skipped, failures = _corpus(Path(book_root))
        if skipped:
            errors.append(f"--require-corpus: {Path(book_root).name}: {skipped}")
            continue
        note, corpus_errors = _corpus_reconciliation(Path(book_root), parts, failures)
        notes.append(note)
        errors.extend(corpus_errors)
        corpus.extend((label, _shingles(text)) for label, text in parts)
    if errors:
        return Report(name=name, ok=False, errors=errors, notes=notes)
    if not corpus:
        return Report(name=name, ok=False, errors=["--require-corpus: no corpus parts"], notes=notes)

    scanned = 0
    files = sorted(path for path in scan_root.rglob("*") if not path.is_dir())
    for path in files:
        if path.is_symlink():
            errors.append(f"{path}: symlink is not scanned (fail closed)")
            continue
        try:
            text = _archive_file_text(path)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"{path}: cannot read or parse ({exc.__class__.__name__}: {exc})")
            continue
        if text is None:
            errors.append(f"{path}: unscannable extension {path.suffix or path.name!r} (fail closed)")
            continue
        scanned += 1
        file_shingles = _shingles(_without_boilerplate(text))
        for label, reference_shingles in corpus:
            overlap = len(file_shingles & reference_shingles)
            if overlap >= SHINGLE_THRESHOLD:
                errors.append(f"{path} overlaps {label} (shingles={overlap})")
    notes.append(
        f"archive {scan_root}: files {len(files)}, scanned {scanned}, corpus parts {len(corpus)}"
    )
    return Report(name=name, ok=not errors, errors=errors, notes=notes)
