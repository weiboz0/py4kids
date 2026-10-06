"""Derive the committed, vocabulary-restricted GloVe subset (plan recsys-009, design 011 §6).

This is an **off-CI** derivation script (run once by the author, its two output files committed):
CI never runs it and never needs ``gensim``. It streams the cached word2vec-format GloVe file
``~/gensim-data/glove-wiki-gigaword-100/glove-wiki-gigaword-100.gz`` with ``gzip`` + ``str.split``
(no ``gensim`` — a probe confirmed the plain-text stream works), restricts the 400k-word pretrained
vocabulary to the recsys-004 slice vocabulary (:func:`recsys.data.vocabulary.vocabulary`), and
writes a publish-safe subset under ``recsys/data/glove/``:

- ``glove_subset.npy`` — ``float16`` ``(n_vocab, 100)`` matrix, one row per slice-vocabulary token
  in **fixed vocabulary order**. Out-of-vocabulary tokens (expected: exactly ``starfall``) get a
  **zero row** and are listed in the sidecar ``missing`` (they are skipped at pooling downstream).
- ``glove_subset.json`` — sidecar: ``dim``, ``tokens`` (row order), ``token_index``, ``missing``,
  the upstream gensim-data artifact + its checksum, the PDDL-1.0 license note + GloVe software
  Apache-2.0, and the **sha256 of the ``.npy`` bytes** (the committed integrity check re-verifies it).

The GloVe vector **data** is licensed PDDL-1.0 (gensim-data metadata), so a vocabulary-restricted
~0.12 MB subset is redistributable / publish-safe — distinct from the GloVe *software*'s Apache-2.0
and from the license-gated ISBNdb catalog.

Run from the repo root::

    uv run python recsys/data/derive_glove_subset.py
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

# Allow ``import vocabulary`` whether run as a script from the repo root or elsewhere.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from vocabulary import vocabulary

DIM = 100
N_GENRES = 12
LATENT_DIM = 16

GLOVE_GZ = Path.home() / "gensim-data" / "glove-wiki-gigaword-100" / "glove-wiki-gigaword-100.gz"
UPSTREAM_CHECKSUM = "40ec481866001177b8cd4cb0df92924f"  # gensim-data information.json
OUT_DIR = Path(__file__).resolve().parent / "glove"
NPY_PATH = OUT_DIR / "glove_subset.npy"
JSON_PATH = OUT_DIR / "glove_subset.json"

LICENSE = (
    "PDDL-1.0 (http://opendatacommons.org/licenses/pddl/); "
    "Wikipedia 2014 + Gigaword 5, uncased, 100-d; GloVe software Apache-2.0"
)


def _stream_vectors(gz_path: Path, wanted: set[str]) -> dict[str, np.ndarray]:
    """Stream the word2vec-format GloVe ``.gz`` and return vectors for the ``wanted`` tokens.

    No gensim: the first line is a ``"<nrows> <dim>"`` header, every later line is
    ``"<token> <v1> ... <vDIM>"``. We keep only rows whose token is wanted and stop early once all
    are found.
    """
    found: dict[str, np.ndarray] = {}
    with gzip.open(gz_path, mode="rt", encoding="utf-8") as handle:
        header = handle.readline().split()
        if len(header) != 2 or int(header[1]) != DIM:
            raise ValueError(f"unexpected GloVe header {header!r} (expected '<n> {DIM}')")
        for line in handle:
            space = line.find(" ")
            token = line[:space]
            if token not in wanted or token in found:
                continue
            values = line[space + 1 :].split()
            if len(values) != DIM:
                raise ValueError(f"token {token!r}: {len(values)} values, expected {DIM}")
            found[token] = np.asarray(values, dtype=np.float32)
            if len(found) == len(wanted):
                break
    return found


def derive() -> None:
    tokens = vocabulary(N_GENRES, LATENT_DIM)
    if len(tokens) != len(set(tokens)):
        raise ValueError("slice vocabulary has duplicate tokens")
    print(f"slice vocabulary: {len(tokens)} distinct tokens")

    if not GLOVE_GZ.is_file():
        raise FileNotFoundError(f"cached GloVe file missing: {GLOVE_GZ}")
    vectors = _stream_vectors(GLOVE_GZ, set(tokens))
    missing = [token for token in tokens if token not in vectors]
    print(f"GloVe coverage: {len(vectors)}/{len(tokens)} (missing: {missing})")

    matrix = np.zeros((len(tokens), DIM), dtype=np.float16)
    for row, token in enumerate(tokens):
        vector = vectors.get(token)
        if vector is not None:
            matrix[row] = vector.astype(np.float16)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    np.save(NPY_PATH, matrix, allow_pickle=False)
    sha256 = hashlib.sha256(NPY_PATH.read_bytes()).hexdigest()

    sidecar = {
        "dim": DIM,
        "tokens": tokens,
        "token_index": {token: row for row, token in enumerate(tokens)},
        "missing": missing,
        "source": "glove-wiki-gigaword-100",
        "upstream": f"gensim-data glove-wiki-gigaword-100 ({UPSTREAM_CHECKSUM})",
        "license": LICENSE,
        "sha256": sha256,
    }
    JSON_PATH.write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")

    size_mb = NPY_PATH.stat().st_size / 1_000_000
    print(f"wrote {NPY_PATH} ({size_mb:.3f} MB, shape {matrix.shape}, sha256 {sha256[:16]}…)")
    print(f"wrote {JSON_PATH}")


if __name__ == "__main__":
    derive()
