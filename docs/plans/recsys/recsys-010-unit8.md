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
- **CPU-deterministic:** the path seeds `torch.manual_seed` (embedding init) + a numpy RNG (negative sampling),
  `torch.use_deterministic_algorithms(True)`, and **single-thread** (`torch.set_num_threads(1)`). The determinism GATE
  (design §184 — tolerance-based, NEVER exact-float): two seeded fits yield **identical top-k ranking + `allclose`
  embeddings/scores**; bit-identical weights (`np.array_equal`) hold on CPU here and may be an extra bonus assertion,
  not the gate. **Process-global side-effect:** `use_deterministic_algorithms(True)`/`set_num_threads(1)` mutate
  process state — the path saves + restores the previous values around `fit` (so later cells/tests are unaffected),
  OR documents the global set as intentional; Phase B decides + states which.
- **Tiny + fast (MEASURED, settled):** pinned `embedding_dim=32, n_epochs≈30–60, lr=0.01, n_negatives≈4–10,
  batch_size=256, weight_decay=1e-4` → **~1–4 s per fit** (eval ~2 s), far under the 120 s/cell cap. Every training
  loop runs **≥ 2× per CI pass** (lesson + solutions; milestone a 3rd) — trivially within budget. **Inline training,
  NO cached-artifact machinery** (like U5). Phase B reports the AGGREGATE exec time (lesson + solutions + milestone +
  determinism tests) to confirm the whole-book budget.
- **torch stays in the `recsys` group only:** `two_tower.py` imports torch at module top; it is imported ONLY on the
  routed `--group recsys` path, so the group-free global test suite never imports torch (mirror the existing routed
  paths). No torch import leaks into `bookrec/__init__` eager paths that the group-free suite hits — verify.

## Why this works on the data (empirical, MEASURED — [fable] probe round 1; Phase B re-confirms on shipped code)
The two-tower is MF's latent dot-product re-expressed, but trained with a **pairwise ranking objective** (BPR) + Adam
mini-batches — and on this data, **with regularization, that ranking objective is a clear new accuracy high.**
Measured (dim 32, Adam lr 0.01, uniform complement negatives, `manual_seed(0)`+deterministic+1-thread; val k=10, 60
cold readers excluded, 500 readers; MF re-measured 0.276, CF 0.252, lexical 0.158, floor 0.012):
- **`weight_decay = 1e-4` → hit@10 ≈ 0.36** (seeds 0/1/2/3 → 0.360/0.366/0.364/0.372 — ~4 SE above MF, not noise),
  fit **~1–4 s**. This is the **best path in the book so far** (> MF 0.276 > CF 0.252).
- **`weight_decay = 0` → overfits** (BPR loss → ~0) to **0.20–0.23 (below CF)** — the hand-delivered overfitting
  lesson: a pairwise loss that memorizes the train pairs generalizes worse.

**Honest, binding thesis:** the two-tower is the *same* reader·item embedding dot product as U5's MF — what changed is
the **objective and optimizer** (pairwise BPR + Adam + weight decay vs pointwise logistic full-batch GD), and the
ranking objective **wins on top-k** (≈0.36 vs 0.276) *provided it is regularized*. The lesson teaches BOTH: why the
architecture is MF re-expressed, and why regularization decides whether it tops MF or collapses below CF.

Phase-B gate (pre-declared, fixed seed, bind to the measured numbers): `tt_hit ≥ mf_hit − 0.03` AND `tt_hit ≥ 1.2×pop`
AND `tt_hit ≥ pop + 0.03` AND `tt_hit ≥ lexical` (the regularized path clears `tt ≥ mf − 0.03` with room; an
unregularized path correctly fails). Determinism gate per design §184 (tolerance-based, never exact-float): two seeded
fits give **identical top-k ranking + `allclose` embeddings/scores** (bit-identical weights hold on CPU here and may be
asserted as a bonus, not as the gate). Budget: 1–4 s/fit ⇒ **inline training (no cached-artifact machinery)**;
≥2×/CI trivially met. Reviewers re-verify on the shipped code.

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
- `TwoTowerRetrievalPath(BaseRetrievalPath)` (name `"two-tower"`, version `"1"`). Constructor with PINNED defaults
  (measured): `embedding_dim=32`, `n_epochs=60` (30–60 fine), `learning_rate=0.01`, `n_negatives=10` (4–10 fine),
  `batch_size=256`, **`weight_decay=1e-4`** (REQUIRED — Adam L2; `wd=0` overfits below CF), `seed=0`.
  `fit(interactions, catalog=None)` — EXACT protocol signature; item universe = full catalog, readers = ≥1 train
  positive; builds reader/item `nn.Embedding` towers, trains by **BPR** `-logσ(s⁺−s⁻)` (reader, train-positive,
  uniform sampled negative from the reader's unobserved complement; numpy RNG) with Adam (`weight_decay`),
  mini-batches, `torch.manual_seed` + `use_deterministic_algorithms(True)` + `set_num_threads(1)` (save/restore the
  globals around fit); leakage-safe (train only). **Retrieve contract:** `retrieve(reader_id, context, k)` scores ALL
  catalog books by `reader_emb · item_embᵀ`, excludes `context["seen"]` (**a known reader with empty `seen` still gets
  up to k recs** — the score doesn't depend on `seen`), top-k via `_finish`; ONLY a reader with no learned embedding
  (unknown/cold) → `[]`. `load`/`artifact` store the trained weights as **numpy arrays** (so `load` reconstructs
  scores WITHOUT importing torch) + ids + params. Export so the group-free suite never imports torch (no eager torch
  import from `__init__`).
- Tests (routed `--group recsys`), bound to the measured numbers (seed 0, k=10, 60 cold excl): **`tt_hit ≥ mf_hit −
  0.03` AND `tt_hit ≥ 1.2×pop` AND `tt_hit ≥ pop + 0.03` AND `tt_hit ≥ lexical`** (regularized ~0.36 clears these; an
  unregularized path fails `tt ≥ mf − 0.03`); **determinism = identical top-k ranking + `allclose` embeddings** (bonus
  `np.array_equal`); a tiny hand-checkable BPR step reduces the loss; leakage-safe; a KNOWN reader with empty `seen`
  returns k recs, an UNKNOWN reader → `[]`; fit→artifact→load identical recs (load without torch); registers as
  `two-tower-v1`.
- **torch-isolation test (replaces the obsolete `test_unit07.py::test_bookrec_imports_no_gensim_or_torch`):** keep a
  **gensim** prohibition everywhere; assert torch is imported ONLY via `two_tower` (not eagerly from `bookrec`); and
  add an **import-blocked subprocess** check — `sys.modules["torch"]=None`, then `import bookrec` + exercise the
  non-torch paths succeed and `"torch" not in sys.modules` (uv's single `.venv` physically has torch, so merely
  running the group-free suite does NOT prove non-import).
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green + deterministic; the import-blocked
subprocess proves no torch leak on the group-free path; **report two-tower val hit@10 vs MF/CF + the AGGREGATE exec
time (lesson+solutions+milestone+determinism) so the lesson is bound to data and the ≥2×/CI budget is proven.**

### Phase C — lesson.ipynb (Opus subagent; project-first)
Hook: "U5 learned taste factors with numpy gradient descent — what if a neural network learned them instead?". From
scratch → reveal: (1) the **two-tower** idea (reader tower + item tower, dot-product score) as MF re-expressed; (2) the
**BPR** pairwise loss + its gradient — derive a **single contrastive step by hand** (numpy/torch) and watch it push a
positive above a negative; (3) build the towers in PyTorch (`nn.Embedding`, Adam, mini-batches, `manual_seed` +
deterministic + single-thread; use `loss.item()` not `float(loss)`), train, reveal `TwoTowerRetrievalPath`.
**(3b) regularization — the pivotal beat:** train once with `weight_decay=0` and watch the BPR loss collapse toward 0
while val hit@10 *drops to ~0.20–0.23 (below CF)* — memorizing the train pairs; then add `weight_decay=1e-4` and it
jumps to **~0.36**. Score on `val`: the two-tower is the **best path in the book so far (~0.36 > MF 0.276 > CF
0.252)** — the honest Phase-B story: the SAME reader·item dot product as U5's MF, but the **pairwise BPR ranking
objective + Adam + weight decay wins on top-k** (vs U5's pointwise logistic full-batch GD). **The bridge:** U5 MF
(numpy GD) / U7 GloVe (pretrained) / U8 two-tower (learned neural) are all dot-product retrievers over embeddings; U9
adds *feature* towers for cold items, U11/U12 build on the learned stack. Note determinism (seed/threads) as a
reproducibility lesson. ASCII only; `rank(exclude=seen)`; reuse `bookrec`; training tiny/seeded/in-budget (~1–4 s).
**Verify:** `exec-lessons` clean (within budget); non-empty markdown first cell; `concept-scan` clean.

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents)
≥6 `## Exercise N`; ≥2 `stretch`; exercises NO solutions/outputs; solutions mirror all, clean (fixed seeds,
deterministic torch), ≥3 non-vacuous asserts. Drill: implement the dot-product score + a BPR step by hand; build/train
the towers; show the loss falling; register `TwoTowerRetrievalPath` + read the val scoreboard vs MF/CF/lexical/random
(two-tower ~0.36, the new best — honest, not "on par"); confirm determinism (two seeded fits → identical ranking +
`allclose`). Stretch e.g.: **sweep `weight_decay ∈ {0, 1e-5, 1e-4, 1e-3}` and plot val hit@10** (0 overfits ~0.21,
1e-4 peaks ~0.36 — the regularization lesson + the U9 bridge); two-tower vs MF top-k agreement on a reader; show the
score is a dot product of learned embeddings. Taught-before-assessed; keep training small/seeded (`loss.item()`).
**Verify:** `hygiene`/`structure`/`cell-lint`/`noexec`; `exec-solutions` clean (budget); `concept-scan` clean.

### Phase E — milestone notebook (Opus subagent)
`recsys/projects/bookrec/milestones/unit-08-two-tower.ipynb` — fixed-seed demo: train + register
`TwoTowerRetrievalPath` (regularized, `weight_decay=1e-4`), val scoreboard vs random/popularity/lexical/CF/MF
(two-tower ~0.36 — the new best, honestly above MF; NOT "on par"), one reader's
two-tower recs + the embedding dot-product view, and (optionally) the two-tower added to the U6 pinned blend. Passes
`milestone-check` + `exec-solutions` + `concept-scan`; ≤ budget; no `split="test"`.

### Phase F — teacher-notes.md (inline)
`## Goals`, `## Pacing` (60–90 min / 2–3 sittings, hook first, all exercises), `## Common mistakes` (**omitting
`weight_decay` → BPR loss collapses to ~0 and val hit@10 drops BELOW CF — the headline overfitting trap**;
non-determinism from unseeded torch / multi-thread; leaking val into training; confusing BPR *pairwise* ranking loss
with U5's *pointwise* logistic loss; reading "two-tower > MF" as "neural is always better" rather than "the ranking
objective + regularization wins here"), `## Discussion prompts` (MF vs two-tower — same dot-product model, different
objective + optimizer; why a pairwise ranking loss beats pointwise on top-k; why weight decay matters so much on only
5,303 train positives; what a neural tower buys that numpy MF doesn't → feature towers/cold-start U9),
`## Differentiation`.

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

**[sol] — REJECT** (3 Must + 2 Should; registry closure confirmed). All verified legitimate:
1. `[OPEN]` **Must** — the "bit-identical fits" determinism gate violates the book-wide **tolerance-based, never
   exact-float** law (design §184). → Gate on seeded negatives + deterministic algorithms + single-thread yielding
   **identical top-k RANKING** + **`allclose` params/scores** (tolerance), not exact equality.
2. `[OPEN]` **Must** — torch isolation under-specified: a top-level `import torch` in `two_tower.py` trips the existing
   `test_bookrec_imports_no_gensim_or_torch` (`recsys/projects/bookrec/tests/test_unit07.py:277`). Phase B must
   REPLACE it with (a) a gensim-only prohibition and (b) a torch-import-routing test, and PROVE the group-free import
   path never imports torch via an **import-blocked subprocess** (uv's shared `.venv` physically contains torch, so
   "the group-free suite still passes" does NOT prove torch isn't imported). No eager torch import from `__init__`.
3. `[OPEN]` **Must** — the gate (vs pop/lexical/CF, tolerances chosen post-measurement) disagrees with Phases C–E's
   unconditional "on par with MF". → Pre-declare a seed-bound **MF-parity** tolerance (`tt_hit ≥ mf_hit − tol`, state
   tol) and gate it, measured-first; keep "on par with MF" downstream only if it holds, else make the claims
   conditional on the measured result.
4. `[OPEN]` **Should** — retrieve contract: a KNOWN fitted reader with empty `seen` must still get up to k recs
   (scored by `reader_emb · itemᵀ`, independent of `seen`); only a reader with NO learned embedding → `[]`. Current
   "empty-seen/no-factor reader → []" conflates them (the U5 bug) — fix the wording.
5. `[OPEN]` **Should** — report the AGGREGATE exec count + runtime (lesson + solutions + milestone + determinism
   tests), not one per-fit time; caching only helps if the measured total stays in the whole-book budget AND the
   regen check is affordable.
6. `[CONFIRMED]` **Nice** — registry closure correct (requires ⊆ U1/U4/U5/U7; concepts globally unique;
   practices∩introduces=∅; 24.5<30); Phase G named; features/ANN/reranker deferred.

**[fable] — REJECT** (3 Must + 3 Should + 2 Nice; **ran a seeded torch probe** — thesis-changing). Measured (dim 32,
BPR, Adam, uniform complement negatives, `manual_seed(0)`+deterministic+1-thread, val k=10, 60 cold excl, MF
re-measured 0.276): **weight_decay is the decisive knob** — wd 0 → overfits (BPR loss→0) to **0.20–0.23 (below CF)**;
**wd 1e-4 → ~0.36** (seeds 1/2/3 → 0.366/0.364/0.372, ~4 SE above MF, NOT noise). Fit **1–4 s** (eval ~2 s); two
seeded fits bit-identical. So the two-tower is a **clear new high (~0.36 > MF 0.276 > CF 0.252)** when regularized —
the plan's "≈ MF, not a new high" premise is backwards.
1. `[OPEN]` **Must** — add **`weight_decay`** (Adam L2, default ≈1e-4) to the `TwoTowerRetrievalPath` constructor
   (absent from my list) and TEACH it: BPR loss collapsing to ~0 while val hit@10 drops is the overfitting lesson.
2. `[OPEN]` **Must** — rewrite the "on par with MF / not a new high" narrative (Phases C–F + the teacher-notes
   "common mistake: expecting it to beat MF") — the opposite of measurement. Honest story: same latent dot-product,
   different **objective + optimizer** (pairwise BPR + Adam mini-batches + weight decay vs U5's pointwise logistic
   full-batch GD) → the **ranking objective wins on top-k (~0.36)**. Make it measure-bound in BOTH directions (the
   plan only had a `< MF` branch).
3. `[OPEN]` **Must** (= [sol]#3) — gate bind to MF: pre-declare `tt_hit ≥ mf_hit − 0.03` (as U5) + `≥ 1.2×pop` +
   `≥ pop+0.03` + `≥ lexical`; with the measured ~0.36 comfortably satisfied, an unregularized path correctly fails.
4. `[OPEN]` **Should** (= [sol]#2) — torch isolation can't be shown by RUNNING the group-free suite (uv's single
   `.venv` physically has torch; the global `tests/` never import `bookrec`). Concrete check: an **import-blocked
   subprocess** (`sys.modules["torch"]=None`) where `import bookrec` + the non-torch paths succeed and `"torch" not in
   sys.modules`; rewrite `test_unit07.py:277` (gensim-only prohibition + torch-routing), don't delete it.
5. `[OPEN]` **Should** — `use_deterministic_algorithms(True)` + `set_num_threads(1)` are PROCESS-GLOBAL; calling them
   in `fit` mutates state for later cells/tests. Document as intentional OR save/restore after fit. Keep numpy-sampled
   negatives + `torch.manual_seed` init (bit-reproducible on CPU, confirmed).
6. `[OPEN]` **Should** (= [sol]#5) — measured 1–4 s/fit settles it: **inline training, no cached-artifact machinery**;
   drop that fallback. Pinned defaults: `n_epochs 30–60, lr 0.01, n_negatives 4–10, batch_size 256, weight_decay 1e-4,
   dim 32`. (Report aggregate exec time across lesson+solutions+milestone+determinism tests.)
7. `[OPEN]` **Nice** (reconciles [sol]#1) — bit-identity IS achievable on CPU here, but per design §184 "tolerance-
   based, never exact-float" the GATE is identical top-k **ranking** + **`allclose`** params; keep `np.array_equal` as
   a strong CPU bonus assertion only.
8. `[OPEN]` **Nice** — use `loss.item()` (not `float(loss)` on a grad tensor — torch 2.14 warns); add a stretch
   exercise sweeping `weight_decay ∈ {0, 1e-5, 1e-4, 1e-3}` vs val hit@10 (the U9 regularization/hard-negative bridge).

### Plan-review outcome (round 1): **NOT consensus — [sol] REJECT (3 Must) + [fable] REJECT (3 Must, thesis-changing probe) + [self] APPROVE.** [fable]'s probe RE-GROUNDS the unit: with weight_decay the two-tower is a NEW HIGH (~0.36), not "≈ MF"; without it, it overfits below CF. Fold both → **v2**: add weight_decay + pinned defaults; rewrite the thesis (ranking objective wins) measure-bound; MF-bound numeric gate (`tt ≥ mf − 0.03`); tolerance/ranking determinism gate (not exact-float); concrete torch-isolation subprocess test + rewrite `test_unit07` no-torch assertion; process-global determinism note; inline (no cache); `loss.item()` + weight_decay-sweep stretch; retrieve contract (known+empty-seen→recs, unknown→[]). Then round-2 re-review (both rejecters).

### Round 2 (on v2)

**v2 changelog** (folds [sol] 3 Must + 2 Should and [fable] 3 Must + 3 Should): (a) **`weight_decay=1e-4`** added to
the constructor + pinned defaults (dim32/e60/lr0.01/10-neg/batch256/wd1e-4) [fable#1/#6/sol#5]; (b) "Why this works"
+ Phases C/E/F rewritten to the MEASURED thesis — regularized two-tower **~0.36, the new best** (not "≈ MF"); wd=0
overfits below CF (the taught lesson); the pairwise-BPR-ranking-objective-wins story, measure-bound both directions
[fable#2/#8]; (c) numeric gate bound to **MF** (`tt ≥ mf − 0.03`) + pop/lexical, pre-declared [sol#3/fable#3]; (d)
determinism gate = identical top-k ranking + `allclose` (design §184, not exact-float), bit-identical a CPU bonus
[sol#1/fable#7]; (e) torch isolation = rewrite `test_unit07`'s no-torch assertion (gensim-only + torch-routing) + an
**import-blocked subprocess** proving no torch leak on the group-free path [sol#2/fable#4]; (f) process-global
`use_deterministic_algorithms`/`set_num_threads` saved+restored around fit [fable#5]; (g) inline training, no cache,
aggregate-timing report [sol#5/fable#6]; (h) retrieve contract — known reader + empty `seen` → k recs, only no-embedding
→ `[]` [sol#4]; (i) `loss.item()` [fable#8].

**[self] — APPROVE (round 2).** The thesis is now data-correct (regularized two-tower is the new high ~0.36, with the
overfitting-without-weight-decay lesson); gate MF-bound + pre-declared; determinism tolerance-based per §184; torch
isolation has a concrete import-blocked-subprocess proof + the `test_unit07` rewrite; artifact stores numpy weights
(torch-free load); inline + in budget. No [self] blockers.

_([sol] + [fable] round-2 verdicts appended on hand-back.)_

## Content Review

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->
