"""License-gated real-catalog slice extractor (design 011 §6) — FAILS CLOSED.

The repository is PUBLIC and the local ``books`` PostgreSQL catalog's license is unconfirmed, so
this script commits no real data and refuses to produce a slice unless one of two explicit,
recorded permissions is given:

1. ``--attestation PATH`` — a YAML file recording a *known-permissive* source and license for the
   PostgreSQL ``books`` DB (``source``, ``license``, ``confirmed_by``, ``date``). Only then is the
   ``psycopg`` path taken (``--dsn``), and ``psycopg`` is imported lazily.
2. ``--openlibrary PATH`` — a local Open Library dump (public domain) as the fallback input; no DB
   and no network.

With neither, it prints ``FAIL`` and exits non-zero. Its output is written to the gitignored,
non-promotable ``recsys/data/generated/`` and is never committed. Every run records a manifest:
source + version, the exact query/selection parameters, deterministic total ordering,
normalization + dedup rules, row counts, schema/data-dictionary, and content checksums.

``gensim`` (GloVe-subset derivation, lands with U7) and ``psycopg`` are slice/derivation-only and
imported lazily here — never on the CI exec path.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

try:  # script vs. package-relative import
    from _common import GENERATED_DIR, Manifest, checksum, write_gzip_csv
except ImportError:  # pragma: no cover
    from recsys.data._common import (  # type: ignore[no-redef]
        GENERATED_DIR,
        Manifest,
        checksum,
        write_gzip_csv,
    )

SLICE_COLUMNS = ["item_id", "title", "author", "subjects", "isbn"]
REQUIRED_ATTESTATION_KEYS = {"source", "license", "confirmed_by", "date"}
# A permissive license is required to take the DB path. The local ``books`` DB is ISBNdb-sourced
# (NON-permissive), so an unknown/unlabelled license must fail closed. An attestation may instead
# set ``permissive: true`` to assert the source is permissive under a license not in this list.
PERMISSIVE_LICENSES = {
    "cc0",
    "cc-by",
    "cc-by-sa",
    "pddl",
    "odc-by",
    "public-domain",
}


class SliceRefused(RuntimeError):
    """Raised when no permissive source/license attestation or fallback input is given."""


@dataclass
class SliceResult:
    manifest: Manifest
    output_path: Path


def _normalise_title(title: str) -> str:
    return " ".join(title.strip().split())


def _load_attestation(path: Path) -> dict:
    import yaml  # local: only needed on the DB path

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not REQUIRED_ATTESTATION_KEYS <= set(data):
        raise SliceRefused(
            f"attestation must record {sorted(REQUIRED_ATTESTATION_KEYS)}; got {path}"
        )
    license_value = str(data["license"]).strip().lower()
    permissive_flag = data.get("permissive") is True
    if not permissive_flag and license_value not in PERMISSIVE_LICENSES:
        raise SliceRefused(
            f"refusing the DB path: license {data['license']!r} is not in the permissive "
            f"allowlist {sorted(PERMISSIVE_LICENSES)} and 'permissive: true' is not set"
        )
    return data


def _rows_from_openlibrary(path: Path, limit: int) -> list[dict]:
    """Parse a local Open Library JSONL dump into normalised, de-duplicated rows.

    Deterministic total ordering (by item_id), whitespace-normalised titles, and dedup by
    (title, author). No network, no DB.
    """
    rows: dict[tuple[str, str], dict] = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            title = _normalise_title(str(record.get("title", "")))
            author = str(record.get("author", "")).strip()
            if not title:
                continue
            key = (title.lower(), author.lower())
            if key in rows:
                continue  # dedup rule: first occurrence wins
            rows[key] = {
                "title": title,
                "author": author,
                "subjects": ";".join(record.get("subjects", []) or []),
                "isbn": str(record.get("isbn", "")).strip(),
            }
            if len(rows) >= limit:
                break
    ordered = sorted(rows.values(), key=lambda r: (r["title"].lower(), r["author"].lower()))
    for item_id, row in enumerate(ordered):
        row["item_id"] = item_id
    return ordered


def _rows_from_postgres(dsn: str, limit: int) -> list[dict]:  # pragma: no cover - needs a live DB
    import psycopg  # local: only imported on the attested DB path

    query = (
        "SELECT title, author, subjects, isbn FROM books "
        "ORDER BY title, author LIMIT %(limit)s"
    )
    rows: list[dict] = []
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(query, {"limit": limit})
        for item_id, (title, author, subjects, isbn) in enumerate(cur.fetchall()):
            rows.append(
                {
                    "item_id": item_id,
                    "title": _normalise_title(str(title or "")),
                    "author": str(author or "").strip(),
                    "subjects": str(subjects or "").strip(),
                    "isbn": str(isbn or "").strip(),
                }
            )
    return rows


def run_slice(args: argparse.Namespace) -> SliceResult:
    out_dir = Path(args.output)
    if args.openlibrary:
        source = f"open-library:{Path(args.openlibrary).name}"
        query = f"openlibrary-jsonl limit={args.limit} order=(title,author)"
        rows = _rows_from_openlibrary(Path(args.openlibrary), args.limit)
        license_note = "Open Library (public domain)"
    elif args.attestation:
        attestation = _load_attestation(Path(args.attestation))
        if not args.dsn:
            raise SliceRefused("the attested PostgreSQL path requires --dsn")
        source = f"postgres:{attestation['source']}"
        query = f"books order=(title,author) limit={args.limit}"
        rows = _rows_from_postgres(args.dsn, args.limit)
        license_note = str(attestation["license"])
    else:
        raise SliceRefused(
            "refusing to slice: pass --attestation (recorded permissive source/license) "
            "or --openlibrary (local public-domain fallback). No real catalog is committed."
        )

    path = out_dir / "books_slice.csv.gz"
    digest = write_gzip_csv(
        path,
        SLICE_COLUMNS,
        ([row["item_id"], row["title"], row["author"], row["subjects"], row["isbn"]] for row in rows),
    )
    manifest = Manifest(
        source=source,
        version="1",
        config={"limit": args.limit, "order": "title,author", "query": query},
        rowcounts={"books_slice": len(rows)},
        schema={"books_slice.csv.gz": SLICE_COLUMNS},
        checksums={"books_slice.csv.gz": digest},
        notes={
            "license": license_note,
            "normalization": "whitespace-collapsed titles",
            "dedup": "by lowercased (title, author), first-wins",
            "ordering": "lowercased (title, author) ascending",
            "promotable": False,
            "gitignored": True,
        },
    )
    manifest_path = out_dir / "books_slice.manifest.json"
    manifest_path.write_text(json.dumps(manifest.to_dict(), indent=2, sort_keys=True), "utf-8")
    manifest.checksums["books_slice.manifest.json"] = checksum(manifest_path)
    return SliceResult(manifest=manifest, output_path=path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="License-gated real-catalog slice (fails closed).")
    parser.add_argument("--attestation", help="YAML recording a permissive source/license (DB path)")
    parser.add_argument("--dsn", help="PostgreSQL DSN (only with --attestation)")
    parser.add_argument("--openlibrary", help="local Open Library JSONL dump (public-domain fallback)")
    parser.add_argument("--limit", type=int, default=5000, help="max rows to select")
    parser.add_argument("--output", default=str(GENERATED_DIR), help="output dir (gitignored)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run_slice(args)
    except SliceRefused as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"slice: {result.manifest.rowcounts['books_slice']} rows -> {result.output_path}")
    print(f"sha256: {result.manifest.checksums['books_slice.csv.gz']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
