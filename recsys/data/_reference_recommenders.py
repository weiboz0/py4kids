"""Reference recommenders + recoverability evaluation for the synthetic substrate (plan recsys-004).

These are deliberately *small, numpy-only* reference scorers — not the shipped ``bookrec`` paths —
used by ``tests/test_signal_recoverability.py`` to assert the signal hierarchy the curriculum needs
is recoverable on the generated data. Each scorer returns a per-item score vector for one reader's
seen set; the harness ranks the top-k on ``val`` (cold readers excluded) and compares hit-rates to
the **analytic** expected random floor.

Scorers
-------
- ``popularity``            — train positive counts (U2 baseline).
- ``quality``              — U2 weighted positive-RATE lens ``(pos + m·C)/(expo + m)`` (should stay weak).
- ``genre_cosine``         — TF-IDF genre-profile cosine (U3 coarse content).
- ``keyword_bm25``         — BM25 over the keyword bags (U3 lexical content; finer than genre).
- ``item_item_cf``         — cosine item-item co-occurrence on train positives (U4).
- ``learned_mf``           — a few-epoch logistic MF trained ONLY on the observed train log (U5).
- ``affinity_oracle``      — the exposed true affinity (ground-truth taste ceiling, not the log).
- ``propensity_oracle``    — the generator's exposure log-propensity ``α·log pop + β·z`` (sanity ceiling).
- ``random``               — a seeded per-reader uniform baseline (reported; analytic floor is the denominator).

U12 session-log harness (plan recsys-014 Goal 3; ``tests/test_session_recoverability.py``)
-----------------------------------------------------------------------------------------
Over ``sessions.csv.gz`` + ``series.csv.gz``: ``ordered_train_sequences`` (the Goal-3 ordering
key), popularity, bag item-item CF, last-k CF (k=3), last-k transition (k=5), last-1 transition
(diagnostic), the shuffled control, and ``next_in_series_cohort`` (G3c). The harness and the U12
sequence path consume **positives only**; the session log's sampled negatives exist for schema
parity with the main log (a negative colliding with its positive is dropped, not resampled).
"""

from __future__ import annotations

import csv
import gzip
from collections import defaultdict
from pathlib import Path

import numpy as np


# --------------------------------------------------------------------------- item scorers (global)
def popularity_scores(train_pos_counts: np.ndarray) -> np.ndarray:
    return train_pos_counts.astype(float)


def quality_scores(train_pos_counts: np.ndarray, train_expo_counts: np.ndarray, m: float) -> np.ndarray:
    """U2 weighted positive-rate quality ``(pos + m·C)/(expo + m)`` with global rate ``C``."""
    total_expo = train_expo_counts.sum()
    c = train_pos_counts.sum() / total_expo if total_expo else 0.0
    return (train_pos_counts + m * c) / (train_expo_counts + m)


def _bm25_weights(tf: np.ndarray, k1: float = 1.2, b: float = 0.75) -> np.ndarray:
    """Per-(doc, term) BM25 weights for a term-frequency matrix ``(n_docs, n_terms)``."""
    n_docs = tf.shape[0]
    df = (tf > 0).sum(axis=0)
    idf = np.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)
    doc_len = tf.sum(axis=1)
    avg_len = doc_len.mean() if doc_len.mean() else 1.0
    denom = tf + k1 * (1.0 - b + b * doc_len[:, None] / avg_len)
    return idf * tf * (k1 + 1.0) / np.where(denom == 0.0, 1.0, denom)


def _genre_tfidf(genre_matrix: np.ndarray) -> np.ndarray:
    n = genre_matrix.shape[0]
    present = (genre_matrix > 0).astype(float)
    idf = np.log(n / np.maximum(present.sum(axis=0), 1.0)) + 1.0
    weighted = present * idf
    norms = np.maximum(np.linalg.norm(weighted, axis=1, keepdims=True), 1e-9)
    return weighted / norms


def _item_item_cf(reader_item_pos: np.ndarray) -> np.ndarray:
    """Cosine item-item co-occurrence similarity on a binary reader×item train-positive matrix."""
    norms = np.sqrt((reader_item_pos**2).sum(axis=0))
    sim = (reader_item_pos.T @ reader_item_pos) / np.maximum(np.outer(norms, norms), 1e-9)
    np.fill_diagonal(sim, 0.0)
    return sim


def _learned_mf(
    pos_readers: np.ndarray,
    pos_items: np.ndarray,
    n_readers: int,
    n_books: int,
    *,
    dim: int = 32,
    epochs: int = 300,
    lr: float = 0.5,
    reg: float = 0.05,
    negatives: int = 10,
    seed: int = 0,
) -> np.ndarray:
    """Few-epoch implicit logistic MF on the OBSERVED train positives; returns reader×item scores.

    Standard implicit-feedback training: the observed train **positives** are the signal, paired
    with negatives drawn from each reader's UNOBSERVED complement (the usual implicit-MF practice —
    a sampled negative is never one of that reader's own observed positives — NOT the generator
    oracle). Deterministic (seeded init + seeded negatives, full-batch gradient descent with
    per-entity-averaged gradients so the step is well-scaled regardless of log size). Learns
    ``sigmoid(P_u · Q_i) ≈ liked`` so recovered scores reflect the latent taste the co-occurrence of
    positives imprints — a learned cousin of item-item CF that should beat popularity and content.
    """
    rng = np.random.default_rng(seed)
    p = rng.normal(0.0, 0.1, size=(n_readers, dim))
    q = rng.normal(0.0, 0.1, size=(n_books, dim))
    n_pos = pos_readers.shape[0]
    neg_readers = np.repeat(pos_readers, negatives)
    neg_items = rng.integers(0, n_books, size=n_pos * negatives)
    # Sample negatives from each reader's UNOBSERVED complement: resample any draw that collides
    # with one of that reader's observed positives so no "negative" is actually a known positive.
    observed = set(zip(pos_readers.tolist(), pos_items.tolist()))
    neg_reader_list = neg_readers.tolist()
    pending = [j for j in range(neg_items.shape[0]) if (neg_reader_list[j], int(neg_items[j])) in observed]
    while pending:
        neg_items[pending] = rng.integers(0, n_books, size=len(pending))
        pending = [j for j in pending if (neg_reader_list[j], int(neg_items[j])) in observed]
    u_idx = np.concatenate([pos_readers, neg_readers])
    i_idx = np.concatenate([pos_items, neg_items])
    y = np.concatenate([np.ones(n_pos), np.zeros(n_pos * negatives)])
    count_u = np.maximum(np.bincount(u_idx, minlength=n_readers), 1)[:, None]
    count_i = np.maximum(np.bincount(i_idx, minlength=n_books), 1)[:, None]

    def _accumulate(index: np.ndarray, weighted: np.ndarray, size: int) -> np.ndarray:
        # Per-column bincount is far faster than ``np.add.at`` on a 2-D array.
        out = np.empty((size, weighted.shape[1]))
        for d in range(weighted.shape[1]):
            out[:, d] = np.bincount(index, weights=weighted[:, d], minlength=size)
        return out

    for _ in range(epochs):
        scores = (p[u_idx] * q[i_idx]).sum(axis=1)
        err = y - 1.0 / (1.0 + np.exp(-scores))
        grad_p = _accumulate(u_idx, err[:, None] * q[i_idx], n_readers)
        grad_q = _accumulate(i_idx, err[:, None] * p[u_idx], n_books)
        p += lr * (grad_p / count_u - reg * p)
        q += lr * (grad_q / count_i - reg * q)
    return p @ q.T


# --------------------------------------------------------------------------- analytic random floor
def _analytic_floor(n_books: int, n_seen: int, n_relevant: int, k: int) -> float:
    """U1's expected random hit-rate ``1 − C(N−r, k)/C(N, k)`` over the unseen pool for one reader."""
    pool = n_books - n_seen
    prob_miss = 1.0
    for j in range(k):
        prob_miss *= (pool - n_relevant - j) / (pool - j)
    return 1.0 - prob_miss


# ------------------------------------------------------------- keyword latent-vs-genre structure
def latent_overlap_vs_genre_control(
    latent: np.ndarray,
    genre_matrix: np.ndarray,
    tf: np.ndarray,
    *,
    n_anchors: int = 300,
    genre_pool: int = 60,
    near: int = 8,
    seed: int = 0,
) -> tuple[float, float]:
    """Keyword overlap for latent-NEAR vs latent-FAR books, *controlling for genre*.

    For each anchor, restrict to its ``genre_pool`` most genre-similar other books (so genre is
    held roughly constant), then compare mean keyword cosine of its ``near`` latent-nearest vs its
    ``near`` latent-farthest candidates within that genre-matched pool. If keywords encode structure
    beyond genre, the latent-near overlap exceeds the latent-far (genre-controlled) overlap.
    """
    rng = np.random.default_rng(seed)
    n = latent.shape[0]

    def _unit(matrix: np.ndarray) -> np.ndarray:
        return matrix / np.maximum(np.linalg.norm(matrix, axis=1, keepdims=True), 1e-9)

    lat_u, gen_u, kw_u = _unit(latent), _unit(genre_matrix), _unit(tf)
    anchors = rng.choice(n, size=min(n_anchors, n), replace=False)
    near_overlaps: list[float] = []
    far_overlaps: list[float] = []
    for a in anchors:
        genre_sim = gen_u @ gen_u[a]
        genre_sim[a] = -np.inf
        pool = np.argsort(-genre_sim)[:genre_pool]  # genre-matched candidates
        lat_sim = lat_u[pool] @ lat_u[a]
        order = np.argsort(-lat_sim)
        near_ids = pool[order[:near]]
        far_ids = pool[order[-near:]]
        near_overlaps.append(float((kw_u[near_ids] @ kw_u[a]).mean()))
        far_overlaps.append(float((kw_u[far_ids] @ kw_u[a]).mean()))
    return float(np.mean(near_overlaps)), float(np.mean(far_overlaps))


# ------------------------------------------------------------------------------- full evaluation
def evaluate_recoverability(inter, keyword_tf: np.ndarray, *, k: int = 10, seed: int = 0) -> dict:
    """Evaluate every reference scorer on ``val`` (k, cold readers excluded). Returns a metrics dict.

    ``inter`` is a ``gen_interactions.Interactions``; ``keyword_tf`` is the keyword term-frequency
    matrix ``(n_books, |vocab|)``. All hit-rates are averaged over the eligible-reader set; the
    random denominator is the analytic expected floor (U1).
    """
    catalog = inter.catalog
    n = catalog.n_books
    u, i = inter.reader_ids, inter.item_ids
    sp, lab = inter.splits, inter.labels

    train = sp == "train"
    train_pos = train & (lab == 1)
    val_pos = (sp == "val") & (lab == 1)

    seen_by: dict[int, set[int]] = defaultdict(set)
    val_by: dict[int, set[int]] = defaultdict(set)
    for uu, ii in zip(u[train_pos], i[train_pos]):
        seen_by[int(uu)].add(int(ii))
    for uu, ii in zip(u[val_pos], i[val_pos]):
        val_by[int(uu)].add(int(ii))

    cold = set(inter.cold_readers.tolist())
    readers = [r for r in sorted(val_by) if r not in cold and (val_by[r] - seen_by[r])]

    pop_counts = np.bincount(i[train_pos], minlength=n).astype(float)
    expo_counts = np.bincount(i[train], minlength=n).astype(float)

    reader_item_pos = np.zeros((inter.config.n_readers, n))
    reader_item_pos[u[train_pos], i[train_pos]] = 1.0
    cf_sim = _item_item_cf(reader_item_pos)

    genre_profiles = _genre_tfidf(catalog.genre_matrix)
    bm25 = _bm25_weights(keyword_tf)

    mf_scores = _learned_mf(
        u[train_pos].astype(int), i[train_pos].astype(int), inter.config.n_readers, n, seed=seed
    )
    affinity = inter.affinity_matrix
    propensity = inter.observation_propensity()

    rng = np.random.default_rng(seed)

    def genre_cos(r: int, seen: list[int]) -> np.ndarray:
        profile = genre_profiles[seen].sum(axis=0)
        profile /= max(np.linalg.norm(profile), 1e-9)
        return genre_profiles @ profile

    def kw_bm25(r: int, seen: list[int]) -> np.ndarray:
        return bm25 @ keyword_tf[seen].sum(axis=0)

    scorers = {
        # A fresh uniform draw PER READER (a one-shared-vector draw reports a misleading single-draw
        # number); the gates use the analytic floor as the denominator, never this reported value.
        "random": lambda r, seen: rng.random(n),
        "popularity": lambda r, seen: pop_counts,
        "quality": lambda r, seen: quality_scores(pop_counts, expo_counts, 10.0),
        "genre_cosine": genre_cos,
        "keyword_bm25": kw_bm25,
        "item_item_cf": lambda r, seen: cf_sim[:, seen].sum(axis=1),
        "learned_mf": lambda r, seen: mf_scores[r],
        "affinity_oracle": lambda r, seen: affinity[r],
        "propensity_oracle": lambda r, seen: propensity[r],
    }

    ids = np.arange(n)
    results: dict[str, float] = {}
    pop_topk: list[np.ndarray] = []
    for name, fn in scorers.items():
        hits = []
        for r in readers:
            seen = sorted(seen_by[r])
            relevant = val_by[r] - seen_by[r]
            scores = np.asarray(fn(r, seen), dtype=float).copy()
            scores[seen] = -np.inf
            top = np.lexsort((ids, -scores))[:k]
            hits.append(1.0 if any(int(t) in relevant for t in top) else 0.0)
            if name == "popularity":
                pop_topk.append(top)
        results[name] = float(np.mean(hits)) if hits else 0.0

    results["analytic_floor"] = float(
        np.mean(
            [
                _analytic_floor(n, len(seen_by[r]), len(val_by[r] - seen_by[r]), k)
                for r in readers
            ]
        )
    )
    results["readers"] = len(readers)
    results["positive_rate"] = float(lab.mean())

    # U2 coverage guards. ``random_coverage`` is a per-reader uniform recommender (high coverage),
    # the denominator for the "popularity coverage < 0.1 × random" guard.
    pop_cov_ids = set(np.concatenate(pop_topk).tolist()) if pop_topk else set()
    results["popularity_coverage"] = len(pop_cov_ids) / n
    rc_rng = np.random.default_rng(seed + 1)
    random_ids: set[int] = set()
    for r in readers:
        unseen = np.setdiff1d(ids, np.fromiter(seen_by[r], dtype=int))
        pick = rc_rng.choice(unseen, size=min(k, len(unseen)), replace=False)
        random_ids.update(int(x) for x in pick)
    results["random_coverage"] = len(random_ids) / n
    all_counts = np.bincount(i, minlength=n)
    ordered = np.sort(all_counts)[::-1]
    head = max(1, n // 10)
    results["head_share"] = float(ordered[:head].sum() / ordered.sum())
    # head-share of the POPULARITY recommender itself (U2 "head_share==1.0").
    results["pop_rec_head_share"] = _pop_rec_head_share(pop_cov_ids, all_counts, n)

    near, far = latent_overlap_vs_genre_control(
        catalog.latent, catalog.genre_matrix, keyword_tf, seed=seed
    )
    results["kw_latent_near_overlap"] = near
    results["kw_genre_control_overlap"] = far
    return results


def _pop_rec_head_share(rec_ids: set[int], all_counts: np.ndarray, n: int) -> float:
    """Fraction of the popularity recommender's recommended items that fall in the popular head."""
    if not rec_ids:
        return 0.0
    head = max(1, n // 10)
    head_ids = set(np.argsort(-all_counts, kind="stable")[:head].tolist())
    return len(rec_ids & head_ids) / len(rec_ids)


# ======================================================================================================
# U12 session-log recoverability harness (plan recsys-014 Goal 3)
# ======================================================================================================
# The protocol is fixed by the plan; it is the same cohort the book's scoreboard uses
# (``bookrec/scoreboard.py``):
#
# - **Positives only.** The harness (and the U12 sequence path) consume ``label == 1`` rows only. The
#   session log's sampled negatives are kept for schema parity with the main interaction log; a
#   sampled negative that collides with its positive is dropped, not resampled (``gen_sessions.py``).
# - **Ordering key.** Per reader, positives sorted by ``(timestamp, file row order)``.
# - **Train-only references.** Every reference learns from TRAIN positives only; transitions are
#   consecutive pairs *within* a reader's train positives (the last-train → first-val pair is never
#   counted).
# - **Cohort.** Relevance = val positives − train positives; a reader is eligible iff that set is
#   non-empty (and the reader has a train history to query with); candidates exclude train
#   positives; k = 10. Every method is scored on the identical cohort.
# - **Shuffled control.** Each reader's train sequence is permuted with one
#   ``np.random.default_rng(seed + 1000)`` (readers visited in id order); the permuted sequences
#   feed BOTH transition learning and the query, so only order differs from the real path.
# - **Ties.** A tiny popularity term (``1e-6 · pop / max pop``) breaks score ties, then a stable
#   ``argsort`` (lowest item id first).

SESSION_K = 10
LAST_K_CF = 3  # last-k CF query window
LAST_K_TRANSITION = 5  # last-k transition query window (also the G3c "v is visible" window)
SHUFFLE_SEED_OFFSET = 1000


def _session_columns(path) -> dict[str, np.ndarray]:
    """Read a session-log CSV (``reader_id,item_id,session_id,timestamp,split,label``) in file order."""
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    readers: list[int] = []
    items: list[int] = []
    stamps: list[int] = []
    splits: list[str] = []
    labels: list[int] = []
    with opener(path, mode="rt", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            readers.append(int(row["reader_id"]))
            items.append(int(row["item_id"]))
            stamps.append(int(row["timestamp"]))
            splits.append(row["split"])
            labels.append(int(row["label"]))
    return {
        "reader_ids": np.array(readers, dtype=np.int64),
        "item_ids": np.array(items, dtype=np.int64),
        "timestamps": np.array(stamps, dtype=np.int64),
        "splits": np.array(splits, dtype="<U5"),
        "labels": np.array(labels, dtype=np.int64),
    }


def ordered_positive_sequences(
    reader_ids: np.ndarray,
    item_ids: np.ndarray,
    timestamps: np.ndarray,
    splits: np.ndarray,
    labels: np.ndarray,
) -> tuple[dict[int, list[int]], dict[int, list[int]]]:
    """Per reader: the ordered TRAIN-positive and VAL-positive item lists (Goal-3 ordering key).

    Rows are in file order; positives are sorted per reader by ``(timestamp, file row order)``.
    Test rows are never read (the test split is sealed).
    """
    pos = np.nonzero(np.asarray(labels) == 1)[0]
    order = pos[np.lexsort((pos, timestamps[pos], reader_ids[pos]))]
    train: dict[int, list[int]] = {}
    val: dict[int, list[int]] = {}
    for idx in order:
        split = splits[idx]
        if split == "train":
            train.setdefault(int(reader_ids[idx]), []).append(int(item_ids[idx]))
        elif split == "val":
            val.setdefault(int(reader_ids[idx]), []).append(int(item_ids[idx]))
    return train, val


def ordered_split_sequences(path) -> tuple[dict[int, list[int]], dict[int, list[int]]]:
    """Load a session-log CSV and return ``(train, val)`` ordered positive sequences per reader."""
    return ordered_positive_sequences(**_session_columns(path))


def ordered_train_sequences(path) -> dict[int, list[int]]:
    """Each reader's ordered TRAIN-positive item list from a session-log CSV (positives only)."""
    return ordered_split_sequences(path)[0]


def next_volume_from_series(path, n_items: int) -> np.ndarray:
    """Dense ``(n_items,)`` map from ``series.csv.gz``: item id of volume ``v+1``, else ``-1``."""
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    by_series: dict[int, dict[int, int]] = {}
    with opener(path, mode="rt", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            volumes = by_series.setdefault(int(row["series_id"]), {})
            volumes[int(row["volume"])] = int(row["item_id"])
    nxt = -np.ones(n_items, dtype=np.int64)
    for volumes in by_series.values():
        for vol, item in volumes.items():
            if vol + 1 in volumes:
                nxt[item] = volumes[vol + 1]
    return nxt


def shuffled_sequences(train: dict[int, list[int]], seed: int) -> dict[int, list[int]]:
    """The shuffled control: each reader's sequence permuted by ``default_rng(seed + 1000)``."""
    rng = np.random.default_rng(seed + SHUFFLE_SEED_OFFSET)
    return {u: [int(x) for x in rng.permutation(train[u])] for u in sorted(train)}


def sequence_popularity(train: dict[int, list[int]], n_items: int) -> np.ndarray:
    """Train-positive counts per item (the popularity reference)."""
    pop = np.zeros(n_items)
    for seq in train.values():
        np.add.at(pop, seq, 1.0)
    return pop


def bag_cf_similarity(train: dict[int, list[int]], n_items: int) -> np.ndarray:
    """Item-item cosine over the binary reader × item train-positive matrix (the U4 model)."""
    readers = sorted(train)
    matrix = np.zeros((len(readers), n_items))
    for row, u in enumerate(readers):
        matrix[row, train[u]] = 1.0
    return _item_item_cf(matrix)


def transition_counts(seqs: dict[int, list[int]], n_items: int) -> np.ndarray:
    """First-order transition counts ``T[a, b]`` over consecutive pairs within each sequence."""
    src: list[int] = []
    dst: list[int] = []
    for seq in seqs.values():
        src.extend(seq[:-1])
        dst.extend(seq[1:])
    flat = np.bincount(
        np.asarray(src, dtype=np.int64) * n_items + np.asarray(dst, dtype=np.int64),
        minlength=n_items * n_items,
    )
    return flat.reshape(n_items, n_items).astype(float)


def bag_cf_scores(sim: np.ndarray, seq: list[int]) -> np.ndarray:
    return sim[sorted(set(seq))].sum(axis=0)


def lastk_cf_scores(sim: np.ndarray, seq: list[int], k: int = LAST_K_CF) -> np.ndarray:
    return sim[seq[-k:]].sum(axis=0)


def lastk_transition_scores(
    trans: np.ndarray, seq: list[int], k: int = LAST_K_TRANSITION
) -> np.ndarray:
    return trans[seq[-k:]].sum(axis=0)


def last1_transition_scores(trans: np.ndarray, seq: list[int]) -> np.ndarray:
    return trans[seq[-1]]


def session_eligible_readers(train: dict[int, list[int]], val: dict[int, list[int]]) -> list[int]:
    """The common cohort: readers with a train history and a val positive not seen in train."""
    return [u for u in sorted(val) if u in train and set(val[u]) - set(train[u])]


def next_in_series_cohort(
    train: dict[int, list[int]],
    val: dict[int, list[int]],
    next_volume: np.ndarray,
    readers: list[int],
    window: int = LAST_K_TRANSITION,
) -> list[tuple[int, int, int]]:
    """G3c events ``(reader, v, v+1)``: v among the reader's last ``window`` train positives and
    volume v+1 a val positive NOT seen in train (recommendable)."""
    events: list[tuple[int, int, int]] = []
    for u in readers:
        seq = train[u]
        relevant = set(val[u]) - set(seq)
        for v in sorted(set(seq[-window:])):
            w = int(next_volume[v])
            if w >= 0 and w in relevant:
                events.append((u, v, w))
    return events


def _top_k(scores: np.ndarray, exclude, tiny: np.ndarray, k: int) -> set[int]:
    s = scores + tiny
    s[list(exclude)] = -np.inf
    return set(np.argsort(-s, kind="stable")[:k].tolist())


def _paired_se(a: list[float], b: list[float]) -> float:
    d = np.asarray(a) - np.asarray(b)
    return float(d.std(ddof=1) / np.sqrt(len(d))) if len(d) > 1 else 0.0


def evaluate_session_recoverability(
    train: dict[int, list[int]],
    val: dict[int, list[int]],
    next_volume: np.ndarray,
    n_items: int,
    *,
    seed: int,
    k: int = SESSION_K,
) -> dict:
    """Score every Goal-3 reference on the common cohort; return hit@k metrics + G3 quantities.

    ``seed`` is the session seed (the shuffled control uses ``seed + 1000``). Keys: ``eligible``;
    ``popularity``, ``bag_cf``, ``lastk_cf``, ``transk``, ``transk_shuf``, ``last1``,
    ``last1_shuf`` (hit@k, any val positive) and ``next_<method>`` (the first unseen val positive);
    ``g3a_diff``; ``g3b_ratio`` / ``g3b_diff``; ``g3c_n`` / ``g3c_transk`` / ``g3c_bag`` /
    ``g3c_ratio`` / ``g3c_diff``; ``link_T`` / ``link_S`` (the reported series-link diagnostic);
    ``g3d_ratio``; and paired SEs ``g3a_se`` / ``g3b_se``.
    """
    shuffled = shuffled_sequences(train, seed)
    readers = session_eligible_readers(train, val)
    pop = sequence_popularity(train, n_items)
    tiny = 1e-6 * pop / max(pop.max(), 1e-9)
    sim = bag_cf_similarity(train, n_items)
    trans = transition_counts(train, n_items)
    trans_shuf = transition_counts(shuffled, n_items)

    methods = ("popularity", "bag_cf", "lastk_cf", "transk", "transk_shuf", "last1", "last1_shuf")
    hit: dict[str, list[float]] = {m: [] for m in methods}
    next_hit: dict[str, list[float]] = {m: [] for m in methods}
    tops_by_reader: dict[int, dict[str, set[int]]] = {}
    for u in readers:
        seq, sseq = train[u], shuffled[u]
        seen = set(seq)
        relevant = set(val[u]) - seen
        first = next(i for i in val[u] if i not in seen)
        scores = {
            "popularity": pop,
            "bag_cf": bag_cf_scores(sim, seq),
            "lastk_cf": lastk_cf_scores(sim, seq),
            "transk": lastk_transition_scores(trans, seq),
            "transk_shuf": lastk_transition_scores(trans_shuf, sseq),
            "last1": last1_transition_scores(trans, seq),
            "last1_shuf": last1_transition_scores(trans_shuf, sseq),
        }
        tops = {m: _top_k(sc, seen, tiny, k) for m, sc in scores.items()}
        tops_by_reader[u] = tops
        for m in methods:
            hit[m].append(float(bool(tops[m] & relevant)))
            next_hit[m].append(float(first in tops[m]))

    g3c: dict[str, list[float]] = {"transk": [], "bag_cf": [], "link_T": [], "link_S": []}
    for u, v, w in next_in_series_cohort(train, val, next_volume, readers):
        g3c["transk"].append(float(w in tops_by_reader[u]["transk"]))
        g3c["bag_cf"].append(float(w in tops_by_reader[u]["bag_cf"]))
        g3c["link_T"].append(float(w in _top_k(trans[v], {v}, tiny, k)))
        g3c["link_S"].append(float(w in _top_k(sim[v], {v}, tiny, k)))

    def _mean(values: list[float]) -> float:
        return float(np.mean(values)) if values else 0.0

    out: dict[str, float] = {"eligible": len(readers)}
    for m in methods:
        out[m] = _mean(hit[m])
        out["next_" + m] = _mean(next_hit[m])
    out["g3a_diff"] = out["lastk_cf"] - out["bag_cf"]
    out["g3a_se"] = _paired_se(hit["lastk_cf"], hit["bag_cf"])
    out["g3b_ratio"] = out["transk"] / max(out["transk_shuf"], 1e-9)
    out["g3b_diff"] = out["transk"] - out["transk_shuf"]
    out["g3b_se"] = _paired_se(hit["transk"], hit["transk_shuf"])
    out["g3c_n"] = len(g3c["transk"])
    out["g3c_transk"] = _mean(g3c["transk"])
    out["g3c_bag"] = _mean(g3c["bag_cf"])
    out["g3c_ratio"] = out["g3c_transk"] / max(out["g3c_bag"], 1e-9)
    out["g3c_diff"] = out["g3c_transk"] - out["g3c_bag"]
    out["link_T"] = _mean(g3c["link_T"])
    out["link_S"] = _mean(g3c["link_S"])
    out["g3d_ratio"] = out["bag_cf"] / max(out["popularity"], 1e-9)
    return out
