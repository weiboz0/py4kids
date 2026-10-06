# Plan recsys-010 — Unit 8: The two-tower model in PyTorch (MF re-expressed as a learned neural retriever)

**Design:** `docs/designs/011-recsys-book.md` (§7 libraries/determinism/ceilings, §8 row 8, §9 CI budget). **Book:**
`recsys` (Book 3). **Autopilot** per AGENTS.md. Second Part-2 unit, on the Units 1–7 substrate. Ships the
**behavioral two-tower** retrieval path: a reader ID-embedding tower and a book ID-embedding tower whose dot product
scores a match, trained in **PyTorch** by **BPR** (pairwise ranking) on implicit feedback + sampled negatives.
**This is the first PyTorch unit** (torch 2.x CPU, already in the `recsys` dependency group since recsys-001).
The pedagogical spine: U5's MF learned the same reader/item factors by full-batch numpy gradient descent; U8
re-expresses it as a **learned neural** dot-product retriever (the two-tower), the shape U9 extends with features and
U11/U12 build on. No ANN (U10 — retrieval stays exact brute-force). No generator change.

## Scope
**Unit 8** (`recsys/units/unit-08-two-tower/`). Teaches the **two-tower / dual-encoder** architecture (`nn.Embedding`
reader + item towers; score = dot product), the **BPR pairwise loss** (`-log σ(s⁺ − s⁻)` over (reader, positive,
sampled-negative) triples), and **mini-batch neural training** in PyTorch (Adam, epochs, seeding) — contrasted with
U5's full-batch numpy MF. Ships a `TwoTowerRetrievalPath` in `bookrec` (torch) + a Unit-8 milestone. No feature towers
or item cold-start (U9); no hard negatives beyond uniform sampled negatives (U9); no ANN/FAISS (U10).

## Determinism & budget (MANDATORY — design §7/§9, binding)
- **CPU-deterministic:** the path sets `PYTHONHASHSEED` expectations via a seeded `torch.Generator`/`torch.manual_seed`,
  `torch.use_deterministic_algorithms(True)`, and **single-thread** (`torch.set_num_threads(1)` within fit) so two
  fits at the same seed are **bit-identical** (asserted). numpy seed for negative sampling.
- **Tiny + fast:** `embedding_dim ~32`, few epochs, mini-batch — sized so one fit is well under the **120 s per-cell**
  cap. Every training loop runs **≥ 2× per CI pass** (lesson + solutions) — Phase B MUST report the measured per-fit
  time so the plan proves the budget. **No cached-artifact machinery** unless the measured fit exceeds budget (prefer
  inline training like U5; if it is too slow, fall back to a seeded cached-model artifact + a required-regen check per
  design §9 — decide from the Phase-B measurement).
- **torch stays in the `recsys` group only:** `two_tower.py` imports torch at module top; it is imported ONLY on the
  routed `--group recsys` path, so the group-free global test suite never imports torch (mirror the existing routed
  paths). No torch import leaks into `bookrec/__init__` eager paths that the group-free suite hits — verify.

## Why this works on the data (empirical — MUST be measured in Phase B before the lesson claims anything)
The two-tower is MF re-expressed, so it should land **near MF's 0.276** hit@10 on `val` (seed, k=10, 60 cold readers
excluded). Phase B MUST train the shipped path and bind the lesson to the measured number, honestly:
- Expected: two-tower ≈ MF (both are learned dot-product retrievers over ID embeddings) — **on par with MF/CF**, well
  above lexical/popularity/floor. Frame as "the SAME latent idea, now learned by a neural optimizer (Adam + BPR
  mini-batches) instead of full-batch numpy GD" — NOT a new accuracy high (it is not expected to beat MF materially).
- If two-tower < MF by more than a small tolerance → tune epochs/lr within budget to reach parity, OR frame honestly
  (the point is the *architecture/training*, the bridge to U9/U11/U12, not a leaderboard win) and record the gap.
- Phase-B test binds a numeric gate at a fixed seed (e.g. `tt_hit ≥ 1.2×pop AND tt_hit ≥ lexical AND tt_hit ≥ CF −
  tol`), plus determinism (two fits bit-identical) — set tolerances from the measurement. Reviewers verify empirically.

## Buildout
Whole-book `lessons` total becomes **24.5** (U1–U8 at 3 each = 24 + Checkpoint A 0.5) < 30 → `buildout: true`
retained. (Crosses ≥30 around U10–U11; a later plan removes it.)

## Audience & retained laws
Advanced baseline (design 011; `gradients`/`linear-algebra`/`vectors`/`dot-product` declared; neural-net training is
taught here, not assumed). Retained in full: project-first; taught-before-assessed; student notebooks NO
solutions/outputs; solutions + milestone run clean (fixed seeds, deterministic torch); teacher-notes;
from-scratch→reveal (derive the BPR gradient / a single contrastive step by hand, then the PyTorch module — design
§7 "from-scratch realistic for … U8's ID-only two-tower + single-step contrastive gradient"); a stretch exercise.
CPU-deterministic; routed `--group recsys`; within the per-notebook exec budget.

## Concepts introduced (3) — `concepts.yaml`
- `two-tower` — the dual-encoder architecture: a reader-ID embedding tower + a book-ID embedding tower, score =
  dot product of the two embeddings; MF re-expressed as a learned neural retriever. `kind: technique`,
  `category: techniques`.
- `bpr-loss` — Bayesian Personalized Ranking: the pairwise implicit-feedback loss `-log σ(s⁺ − s⁻)` over (reader,
  positive, sampled-negative) triples; why a *ranking* loss for implicit top-k. `kind: technique`,
  `category: techniques`.
- `neural-training` — training embeddings in PyTorch: `nn.Embedding`, autograd, an optimizer (Adam), mini-batches and
  epochs, seeding/determinism — contrasted with U5's full-batch numpy gradient descent. `kind: technique`,
  `category: techniques`.
All three globally unique (confirm 0 hits across `*/curriculum/concepts.yaml` in Phase A).

### Coverage-map entry
`unit-08-two-tower`, `kind: unit`, `title: "The two-tower model"`, `lessons: 3`,
`introduces: [two-tower, bpr-loss, neural-training]`,
`requires: [retrieve-then-rank, offline-evaluation, top-k-ranking-metrics, implicit-feedback, matrix-factorization,
latent-factors, gradient-descent, embedding-retrieval]`,
`practices: [retrieve-then-rank, offline-evaluation, top-k-ranking-metrics, implicit-feedback, latent-factors,
embedding-retrieval]`.
(All required ids introduced by U1/U4/U5/U7. `latent-factors`+`embedding-retrieval` genuinely re-exercised (the towers
ARE learned embeddings scored by a dot product); `implicit-feedback` re-exercised (BPR sampled negatives). `practices
∩ introduces = ∅`; no `project` entry → capstone rule inert; closes under buildout.)

## Phases

### Phase A — registry + syllabus
- `concepts.yaml`: add the 3 ids. `coverage-map.yaml`: add the Unit-8 entry (buildout comment → "twenty-four and a
  half"). `baseline.yaml`: declare new `x.name(...)` methods used by authored cells (e.g. torch `nn.Embedding`,
  `manual_seed`, `use_deterministic_algorithms`, `set_num_threads`, optimizer `.step`/`.zero_grad`, `.backward`,
  tensor ops as used; `TwoTowerRetrievalPath`).
- `unit-08-two-tower/manifest.yaml`; `syllabus.md` arc row `| 8 | \`unit-08-two-tower\` | unit | 3 | <hook> |` after
  the U7 row; rebuild PDF.
**Verify:** manifest/prereq/coverage/syllabus green; buildout holds (24.5<30); concepts unique.

### Phase B — `bookrec` two-tower path (Opus subagent; PyTorch, CPU-deterministic)
Dispatch an **Opus subagent**. STUDY `factorization.py` (MF — the model the two-tower re-expresses; same val harness),
`protocol.py` (`BaseRetrievalPath`, `fit`/`retrieve`/`artifact`/`load`, `_finish`), `scoreboard.py`,
`neighborhood.py`/`embeddings.py` (conventions). Add `bookrec/two_tower.py` (torch at module top — imported only under
`--group recsys`):
- `TwoTowerRetrievalPath(BaseRetrievalPath)` (name `"two-tower"`, version `"1"`). Constructor: `embedding_dim=32`,
  `n_epochs`, `learning_rate`, `n_negatives`, `batch_size`, `seed`. `fit(interactions, catalog=None)` — EXACT protocol
  signature; item universe = full catalog, readers = ≥1 train positive; builds reader/item `nn.Embedding` towers,
  trains by **BPR** (reader, train-positive, uniform sampled negative from the reader's unobserved complement) with
  Adam, mini-batches, fixed seed + `use_deterministic_algorithms(True)` + `set_num_threads(1)`; leakage-safe (train
  only). `retrieve(reader_id, context, k)` scores all catalog books by `reader_emb · item_embᵀ`, excludes
  `context["seen"]`, top-k via `_finish`; a reader with no learned embedding → `[]` (cold reader). `load`/`artifact`
  round-trip the trained embedding weights + ids + params (numpy arrays in the artifact, so load needs no torch to
  reconstruct scores — OR document torch-on-load). Deterministic. Export from `__init__` **lazily/guarded** so the
  group-free suite never imports torch.
- Tests (routed `--group recsys`): the two-tower clears the measured gate on `val` (bind to Phase-B numbers:
  `tt_hit ≥ 1.2×pop AND ≥ lexical AND ≥ CF − tol`, two-tower ≈ MF); **two fits bit-identical** (determinism); a tiny
  hand-checkable BPR step reduces the loss; leakage (val/test rows don't affect training); empty-seen/no-factor reader
  → `[]`; fit→artifact→load identical recs; registers as `two-tower-v1`. Keep fit FAST — **report the measured per-fit
  seconds**.
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green, deterministic; the group-free suite still
passes WITHOUT torch importable on its path (no torch leak); **report two-tower val hit@10 vs MF/CF + the per-fit time
so the lesson is bound to data and the ≥2×/CI budget is proven.**

### Phase C — lesson.ipynb (Opus subagent; project-first)
Hook: "U5 learned taste factors with numpy gradient descent — what if a neural network learned them instead?". From
scratch → reveal: (1) the **two-tower** idea (reader tower + item tower, dot-product score) as MF re-expressed; (2) the
**BPR** pairwise loss + its gradient — derive a **single contrastive step by hand** (numpy/torch) and watch it push a
positive above a negative; (3) build the towers in PyTorch (`nn.Embedding`, Adam, mini-batches, `manual_seed` +
deterministic + single-thread), train, reveal `TwoTowerRetrievalPath`; score on `val` — **on par with MF/CF** (the
honest Phase-B story: the same latent idea, learned neurally). **The bridge:** U5 MF (numpy GD) / U7 GloVe (pretrained)
/ U8 two-tower (learned neural) are all dot-product retrievers over embeddings; U9 adds *feature* towers for cold
items, U11/U12 build on the learned stack. Note determinism (seed/threads) as a reproducibility lesson. ASCII only;
`rank(exclude=seen)`; reuse `bookrec`; keep training tiny/seeded/in-budget.
**Verify:** `exec-lessons` clean (within budget); non-empty markdown first cell; `concept-scan` clean.

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents)
≥6 `## Exercise N`; ≥2 `stretch`; exercises NO solutions/outputs; solutions mirror all, clean (fixed seeds,
deterministic torch), ≥3 non-vacuous asserts. Drill: implement the dot-product score + a BPR step by hand; build/train
the towers; show the loss falling; register `TwoTowerRetrievalPath` + read the val scoreboard vs MF/CF/lexical/random
(on par with MF); confirm determinism (two seeded fits identical). Stretch e.g.: effect of `embedding_dim`/epochs;
two-tower vs MF top-k agreement on a reader; show the score is a dot product of learned embeddings (the U9/U11 bridge).
Taught-before-assessed; keep training small/seeded.
**Verify:** `hygiene`/`structure`/`cell-lint`/`noexec`; `exec-solutions` clean (budget); `concept-scan` clean.

### Phase E — milestone notebook (Opus subagent)
`recsys/projects/bookrec/milestones/unit-08-two-tower.ipynb` — fixed-seed demo: train + register
`TwoTowerRetrievalPath`, val scoreboard vs random/popularity/lexical/CF/MF (two-tower on par with MF), one reader's
two-tower recs + the embedding dot-product view, and (optionally) the two-tower added to the U6 pinned blend. Passes
`milestone-check` + `exec-solutions` + `concept-scan`; ≤ budget; no `split="test"`.

### Phase F — teacher-notes.md (inline)
`## Goals`, `## Pacing` (60–90 min / 2–3 sittings, hook first, all exercises), `## Common mistakes` (non-determinism
from unseeded torch / multi-thread; expecting the two-tower to beat MF — it's on par; over-large dim/epochs → slow or
overfit; leaking val into training; confusing BPR pairwise loss with U5's pointwise logistic loss), `## Discussion
prompts` (MF vs two-tower — same idea, different optimizer; why a pairwise ranking loss; what a neural tower buys that
numpy MF doesn't → features/cold-start U9), `## Differentiation`.

### Phase G — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Units 1–8 + Checkpoint A + the Unit-8 milestone AND
`bash scripts/pre-merge-guard.sh --pr` OK. buildout holds (24.5). Confirm CPU-determinism (two fits identical), no
torch import on the group-free suite path, and the two-tower exec (≥2× per pass) stays within the whole-book CI budget.

## Out of scope
No feature towers / item cold-start / hard negatives (U9); no ANN/FAISS (U10 — exact brute-force retrieval here); no
reranker (U11); no sequence model (U12); no generator change; no `projects/project-*` entry (capstone=U14); no
Checkpoint B (U13); no buildout removal; no GPU (CPU-deterministic only).

## Verification phase declared
Phase G is this plan's named verification phase.

## Plan Review

### Round 1 (on v1)

**[self] — APPROVE.** Registry closes: `requires` ⊆ U1 (retrieve-then-rank/offline-evaluation/top-k-ranking-metrics)
+ U4 (implicit-feedback) + U5 (matrix-factorization/latent-factors/gradient-descent) + U7 (embedding-retrieval), all
introduced; `practices ∩ introduces = ∅`; buildout 24.5<30 (Checkpoint A 0.5 counted); concepts unique (confirm in
Phase A). Determinism is specified as a hard contract (seed + `use_deterministic_algorithms(True)` + single-thread,
two bit-identical fits asserted) per design §7; the ≥2×/CI budget is addressed by tiny dims/epochs + a required
Phase-B timing report (inline training preferred; cached-model fallback only if measured too slow). torch isolation
required (import only on the routed group; no leak into the group-free suite). The accuracy claim is conditional +
measure-first (two-tower ≈ MF 0.276, not a new high) with a numeric seed-bound gate. Protocol-substitutable Phase B.
Named Phase G; project-first; from-scratch single-contrastive-step then reveal; ≥6/≥2-stretch/≥3-asserts;
teacher-notes; milestone. No scope creep (features/cold-start=U9, ANN=U10, reranker=U11). Open for Phase B/gate: the
empirical match-to-MF + per-fit timing ([fable] is probing); the artifact should store numpy weights so `load` needs
no torch (flagged in Phase B). No [self] blockers.

_([sol] + [fable] round-1 verdicts appended on hand-back.)_

## Content Review

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->
