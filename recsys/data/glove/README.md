# Committed GloVe subset

`glove_subset.npy` + `glove_subset.json` are a **vocabulary-restricted slice** of the pretrained
`glove-wiki-gigaword-100` word vectors, used by Unit 7's `SemanticEmbeddingRetrievalPath`.

- **Contents:** the 100-dimensional GloVe vector for each of the catalog's 608 vocabulary words
  (`recsys/data/vocabulary.py`), as a `float16` `(608, 100)` array (~0.12 MB). The one word GloVe lacks
  (`starfall`) is stored as a zero row and listed in the sidecar's `missing` field.
- **Source / citation:** Jeffrey Pennington, Richard Socher, Christopher D. Manning.
  *GloVe: Global Vectors for Word Representation.* EMNLP 2014. Model: `glove-wiki-gigaword-100`
  (trained on Wikipedia 2014 + Gigaword 5, uncased, 100-d), distributed via gensim-data.
- **License:** the vector **data** is released under the **Open Data Commons Public Domain Dedication and
  License (PDDL-1.0)** — `http://opendatacommons.org/licenses/pddl/`. (The GloVe *software* is Apache-2.0.)
  A small vocabulary-restricted subset is redistributable; this committed slice carries no PII or proprietary
  content, so it is safe in this public repository.
- **Reproduce:** `recsys/data/derive_glove_subset.py` regenerates both files deterministically from the cached
  `~/gensim-data/glove-wiki-gigaword-100/glove-wiki-gigaword-100.gz` (streamed with `gzip`+`str.split`, no gensim).
  `tools/glove_integrity.py` (run in `scripts/ci-local.sh`) verifies the committed `.npy` matches the sidecar
  `sha256` and stays under 1 MB.
