# Teacher notes — Unit 8: The two-tower model in PyTorch

This is the **first PyTorch unit**. It re-expresses Unit 5's matrix factorization as a learned neural **two-tower**
(a reader-ID embedding tower and a book-ID embedding tower whose dot product scores a match), trained with the
**BPR pairwise ranking loss** and Adam. The headline result is honest and surprising: once **regularized**, the
two-tower is the **book's best path so far (~0.34 hit@10, above MF's 0.276)** — but without weight decay it overfits
to ~0.14 (below even lexical). The lesson teaches both the architecture (MF re-expressed) and why regularization
decides the outcome.

## Goals

By the end of this unit students can:

- Explain the **two-tower / dual-encoder**: two `nn.Embedding` towers, score = `reader_emb · book_emb` — the SAME
  latent dot product as Unit 5's MF, now a neural module.
- Write the **BPR** pairwise loss `-log σ(s⁺ − s⁻)` over (reader, positive, sampled-negative) triples and derive one
  contrastive gradient step by hand (torch autograd confirms it) — contrast with Unit 5's *pointwise* logistic loss.
- Train embeddings in **PyTorch**: `nn.Embedding`, `optim.Adam`, mini-batches, epochs, and the determinism trio
  (`torch.manual_seed` + `use_deterministic_algorithms(True)` + `set_num_threads(1)`).
- Read the scoreboard honestly: the regularized two-tower (~0.34) is the **new best** (> MF 0.276 > CF 0.252 >
  lexical 0.158) — the ranking objective + Adam + weight decay win on top-k — and explain *why* weight decay is
  decisive (`weight_decay=0` collapses the BPR loss toward 0 and the val hit@10 to ~0.14, below CF).

This unit introduces `two-tower`, `bpr-loss`, and `neural-training`; it re-exercises Unit 1's retrieve-then-rank /
offline-evaluation / top-k metrics, Unit 4's implicit feedback (sampled negatives), Unit 5's latent factors, and
Unit 7's embedding retrieval.

## Pacing

The unit opens with its **project hook** — *U5 learned the taste factors with numpy gradient descent; what if a
neural network learned them?* Plan **60–90 minutes across two to three sittings**; assign all exercises (1–7: 5 core
+ 2 Challenge). Each full-config training fit is ~15 s, so sittings stay well within budget.

1. **Sitting 1 (~30 min) — the model and the loss.** The two-tower dot product (Ex1); the BPR pairwise loss and one
   contrastive step by hand (Ex2).
2. **Sitting 2 (~35 min) — train it and read the board.** `nn.Embedding` + Adam + mini-batch BPR training and the
   falling loss (Ex3); register `TwoTowerRetrievalPath` and read the honest val scoreboard — the new best (Ex4);
   determinism (Ex5).
3. **Sitting 3 (~20 min, + Challenges) — regularization and the bridge.** The `weight_decay` sweep (Ex6) and the
   two-tower-is-MF dot-product-retriever bridge (Ex7).

## Common mistakes

- **Omitting `weight_decay` — the headline trap.** With `weight_decay=0` the BPR loss drives toward ~0 (it memorizes
  the train pairs) and val hit@10 drops to **~0.14, below CF and lexical**. `weight_decay=1e-4` is what makes the
  two-tower the best path (~0.34). This is the unit's central lesson, not a footnote.
- **Non-determinism.** Unseeded torch / multiple threads / `use_deterministic_algorithms(False)` give different
  results each run. Seed all three and single-thread; two seeded fits should give identical top-k ranking.
- **Confusing the losses.** BPR is a *pairwise ranking* loss (does the positive outscore a sampled negative?); U5's
  logistic MF loss is *pointwise* (is each (reader, item) a like?). The pairwise objective is why the two-tower edges
  ahead on top-k.
- **Reading "two-tower > MF" as "neural is always better".** It is the SAME dot-product model; what wins here is the
  ranking objective + Adam + regularization on this small log — not neural magic.
- **Leaking the holdout into training.** Train on `train` positives only; `val` is for the scoreboard, `test` stays
  sealed for Checkpoint B.

## Discussion prompts

- The two-tower and MF are the same `reader · item` dot product. What actually changed to move hit@10 from 0.276 to
  0.34 — and could you get MF there by changing *its* objective?
- Why does weight decay matter so much on only ~5,300 train positives? What is the model memorizing when the BPR loss
  hits ~0?
- BPR asks "is the positive above a *sampled* negative?" How would the result change if the negatives were the
  exposure (`label==0`) rows instead of uniform complement draws? (tie back to Unit 5's negatives beat.)
- A neural tower buys us a place to add *features* (subjects, author, GloVe) for books with no interaction history.
  What would that fix that the ID-only two-tower cannot? (forward to Unit 9 cold-start.)

## Provenance

Original content. The **BPR** pairwise loss is from Rendle, Freudenthaler, Gantner & Schmidt-Thieme,
*BPR: Bayesian Personalized Ranking from Implicit Feedback* (UAI 2009) — worth a one-line attribution in the lesson
for a calc/linalg audience; the two-tower / dual-encoder framing is standard retrieval practice, no single source.

## Differentiation

- **Support:** give the training loop (`nn.Embedding` + Adam + the BPR batch) and the seeding trio as starter
  snippets so the lesson stays on the *ideas* (dot product, pairwise loss, regularization); pair-program Ex3.
- **Core:** Exercises 1–5 unaided, using `TwoTowerRetrievalPath` after the by-hand step in Ex2.
- **Stretch:** the `weight_decay` sweep at its 20 training epochs (0 → ~0.18 overfit (below CF), 1e-4 → ~0.35 peak —
  a vivid regularization curve; the lesson's 60-epoch demo overfits harder, ~0.14) and
  reconstructing the path's score by hand from the learned embeddings. Ask strong students to predict the sweep shape
  before running it, and to explain why the biggest `weight_decay` (1e-3) *underfits*.
