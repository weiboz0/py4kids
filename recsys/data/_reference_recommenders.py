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
- ``random``               — a seeded uniform baseline (reported; analytic floor is the denominator).
"""

from __future__ import annotations

from collections import defaultdict

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
    with uniformly-sampled negatives (the usual implicit-MF practice — NOT the generator oracle).
    Deterministic (seeded init + seeded negatives, full-batch gradient descent with per-entity-
    averaged gradients so the step is well-scaled regardless of log size). Learns
    ``sigmoid(P_u · Q_i) ≈ liked`` so recovered scores reflect the latent taste the co-occurrence of
    positives imprints — a learned cousin of item-item CF that should beat popularity and content.
    """
    rng = np.random.default_rng(seed)
    p = rng.normal(0.0, 0.1, size=(n_readers, dim))
    q = rng.normal(0.0, 0.1, size=(n_books, dim))
    n_pos = pos_readers.shape[0]
    neg_readers = np.repeat(pos_readers, negatives)
    neg_items = rng.integers(0, n_books, size=n_pos * negatives)
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
    random_vec = rng.random(n)

    def genre_cos(r: int, seen: list[int]) -> np.ndarray:
        profile = genre_profiles[seen].sum(axis=0)
        profile /= max(np.linalg.norm(profile), 1e-9)
        return genre_profiles @ profile

    def kw_bm25(r: int, seen: list[int]) -> np.ndarray:
        return bm25 @ keyword_tf[seen].sum(axis=0)

    scorers = {
        "random": lambda r, seen: random_vec,
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
