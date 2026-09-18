# Plan 047 — Book 1 Algorithm-Pattern Thread Implementation Plan

**Goal:** Implement design 002 — a first-class, CI-tracked thread of **7 named algorithm patterns** in
Book 1, registered as `kind: technique` concepts, each introduced once and spiralled to **≥3 core,
non-checkpoint reappearances** in varied contexts, with student **Pattern Spotlights** + a delivered
catalog, enforced by three new CI checks — so every pattern's "job" is mastered through spaced, varied
authoring and computational-thinking framing.

**Architecture:** Reuse the existing concept model (no new registry/schema): 7 `kind: technique`,
`category: techniques` entries in `book1/curriculum/concepts.yaml`, tagged through the existing
`introduces`/`practices` lists in unit `manifest.yaml` + `coverage-map.yaml`. Student-facing:
`<!-- pattern: id -->` Spotlight/marker cells + `book1/reference/patterns.md`. New tooling:
`technique-spiral`, `patterns-doc-check`, `pattern-marker` in `tools/`, wired into `ci-local`. Content
(Spotlights + exercises + solutions) authored by Codex per the AGENTS.md dispatch; tooling by Codex.

**Spec:** `docs/designs/002-book1-algorithm-patterns.md` (v6, 2-way-approved — the authority for the
pattern set, homes, forward-only closure-safe spiral, per-locus reuse/promote/new status, embodiment
definitions, and CI semantics). Also: `book1/curriculum/{concepts,coverage-map}.yaml`,
`tools/curriculum.py`/`concept_scan.py`/`notebooks.py`, `scripts/build-pdf.sh`, plan 016 (CI-check
promotion precedent), plan 037 (the exercise depth this sits on + its Phase-V volume thresholds).

## Global Constraints

- **The design is the authority.** The §3 catalog (pattern set, homes, spiral loci + their
  reuse/promote/new status, embodiment definitions) is FIXED by design 002 — this plan implements it and
  MUST NOT add, drop, or re-classify a §3 locus. The plan owns only the deferred mechanics (§0 of the
  design): the exact cell ledger, `pattern-marker` cardinality/adjacency, the catalog generator, and
  pytest fixtures.
- **Reuse `kind: technique` — no new schema.** Each pattern is `{id, name, category: techniques,
  kind: technique}` in `book1/curriculum/concepts.yaml`; `name` carries "Kid name (formal name)". Tags go
  in the existing `introduces`/`practices` lists (manifest == map). Do NOT add new YAML keys.
- **`requires` closure:** a pattern's same-unit enabling concepts are co-introduced and go in NO
  `requires` list (the inherited `prereq_findings` checks `requires ∪ practices` before the entry's own
  `introduces`); only genuinely-earlier-unit enablers may appear in `requires`. Intra-unit order
  (Spotlight/exercise after the enabling lesson beat) is a content-gate duty.
- **Spiral bar (per design §5.1):** every Book-1 pattern id is `introduces`d in exactly ONE home and
  `practices`d in **≥3 pre-capstone, non-checkpoint entries**, each a **core** (non-stretch) embodiment
  matching the design's embodiment definition. Checkpoints do NOT tag patterns.
- **Vertical slice per pattern (per design §8):** a pattern id is added to `concepts.yaml` ONLY when its
  home + all its ≥3 core reappearances + its catalog row land in the same PR — so `main` is valid and
  `technique-spiral` is never red between PRs. The `filter-into-list` slice (touches u07+u08+u09+u10,
  four units in one PR) ships LAST.
- **Embodiment = tag + reviewer.** No AST `pattern-scan`. CI enforces the metadata spiral + markers +
  catalog sync; the 4-way content gate blind-solves each marked exercise against the design's embodiment
  definitions. Technique ids are silenced in `concept-scan` via the existing dynamic `never_flag`
  profile (no `MANUAL_ONLY` edit).
- **Markers:** every entry tagging a pattern id carries a `<!-- pattern: <id> -->` markdown cell in that
  entry's notebooks, mapped kind→notebook (unit home: `lesson.ipynb` + the exercise; unit reappearance:
  `exercises.ipynb` above the tagged exercise; project: `brief.ipynb`). Markers are HTML comments
  (dropped by nbconvert/pandoc; hygiene/PDF unaffected).
- **No max exercise ceiling (per design §7 v7, user directive):** there is NO per-unit cap on core
  exercise count. Projected core counts (u07≈16, u08≈16, u09≈16, u10≈15) are informative pacing data,
  not limits; the ledger records resulting counts but proves no ≤16 bound. Units 01 untouched; u02 gets
  one lean one-sentence Spotlight only. New
  exercises are core, non-stretch; each home is in-class; extra reps route to homework/More-Practice in
  teacher-notes; each home gets a 2-minute unplugged trace. Carry plan-037 Phase-V volume thresholds
  (>2× cells / >30% PDF pages / >25% wall-time = gate finding; 120 s per-cell exec).
- **Concept-closure (scanner-derived `practices`, pre-authorized):** the new pattern exercises exercise
  regular concepts the target units do not yet list, so `concept-scan` (AST, used-but-unlisted) will go
  RED unless those concepts are added to the target unit's `practices`. Following the **plan-016 /
  plan-037 precedent**, these **scanner-derived `practices` additions are pre-authorized** for this plan.
  Each must be **closure-clean** (the concept is `introduces`d in an entry ≤ the target unit), verified
  by the inherited `prereq_findings`. Enumerated (all closure-clean):
  `break-statement` (introduced u04) → add to `practices` of **u07, u08, u09** (linear-search reps with
  `break`); `accumulator` (introduced u04) + `arithmetic-operators` (≤u02) → **u09** (running-total
  read-and-sum, new); `comparison-operators` (≤u02) → **u09** (find-extreme best-so-far, new). No
  `introduces`/`requires` edit for any regular concept; scanner-derived `practices` **only**. The ledger
  records each addition + its introducing entry; a content-gate reviewer re-runs `concept-scan` per slice.
- **Stretch preservation (per `notebooks.py` ≥2-stretch rule, L537):** every unit's `exercises.ipynb`
  must retain **≥2 `stretch`-tagged (Challenge) cells**. Current reality: **every** touched unit has
  exactly 2. The design's 3 stretch→core **promotions** therefore require status-preserving replacements:
  **u10** promotes BOTH its stretch cells (Ex13 find-extreme, Ex14 sentinel-loop) → add **+2** new
  Challenge cells; **u08** promotes Challenge 1 (reverse-lookup) → add **+1** new Challenge cell. These
  replacements are **status-preserving** (they keep the ≥2 floor; they are NOT §3 loci and carry no
  pattern tag/marker). Any other unit whose stretch cell is promoted gets the same treatment; the ledger's
  `stretch-remaining` column proves ≥2 for every touched unit.
- **Do not touch:** `introduces`/`requires` for regular concepts (technique tags + the enumerated
  scanner-derived `practices` additions above are the ONLY metadata edits); Book 2 anything; governance
  files. Standing process: branch `feature/book1-algorithm-patterns`; no commits
  while a `[sol]` review is in flight; `GH_TOKEN=$(cat .gh-token)`; content SOLUTIONS in a separate
  fresh Codex session.

## Out of scope

- A separate `patterns.yaml`; an AST `pattern-scan`; big-O/sorting/recursion; Book 2 pattern growth;
  re-opening plan-037 coverage. A follow-up amends design 001 §2 once these ids ship (not here).

## Phases

Dispatch per AGENTS.md: **the reuse ledger is produced INLINE** (it resolves exact curriculum loci,
actions, and per-unit core counts — curriculum architecture, which AGENTS.md routes inline, not to
Codex; read-only agents may gather raw headings/tags, but the ledger's status/action decisions are
inline and approved before content implementation). Tooling code (the 3 checks + catalog generator) →
Codex (GPT-5.6-sol); Spotlight/exercise STATEMENTS → Codex; SOLUTIONS → separate fresh Codex session;
teacher-notes + metadata tags → inline.

### Phase A — Ledger + tooling foundation (tooling; ships PR-1, no pattern ids yet)

1. **Reuse ledger** — committed to **`book1/curriculum/pattern-ledger.md`** (a tracked artifact the
   content gate checks against; NOT plan prose): the ~28-row table — per locus: `pattern, entry, exact
   exercise heading, core/stretch now, action (reuse-tag/promote/new), enabling concepts, resulting unit
   core count, stretch-remaining`. **Produced INLINE and approved BEFORE any content phase** (see
   Dispatch note). With the ceiling lifted (design §7 v7) the ledger no longer proves a ≤16 bound; it
   MUST (a) record each touched unit's resulting core count as informative pacing data (projected
   u07≈16, u08≈16, u09≈16, u10≈15), (b) prove every pattern reaches **≥3 core non-checkpoint
   reappearances**, and (c) record `stretch-remaining` ≥2 for every unit whose stretch cells are touched
   (see the stretch-preservation constraint below). The verbatim ledger is embedded in this plan's
   appendix (§Ledger) as the source of record; the committed file is generated from it. Produced FIRST so
   all later phases build from real cells.
2. **`technique-spiral`** check in `tools/` (Book-1-scoped): each Book-1 `kind: technique` id is
   `introduces`d once + `practices`d in ≥3 pre-capstone non-checkpoint entries whose marked exercise is
   **core** (not stretch). **Core-detection:** an exercise is stretch iff its prompt cell or its adjacent
   solution code cell carries the `stretch` tag (`"stretch" in tags(cell)`, reusing `notebooks.tags`);
   the marker's tag→cell link (from `pattern-marker`, step 3) identifies which exercise a locus is, so
   spiral and marker are **co-designed**. Scope: iterate only ids registered under Book 1's
   `concepts.yaml` and invoke on the Book-1 tree, so Book-2 techniques are never in scope. Registered in
   `tools/checks.py`; wired into `ci-local`. Green on the empty Book-1 technique set (no patterns yet).
3. **`pattern-marker`** check — exact rules: for every `(entry, pattern-id)` where the entry
   `practices`/`introduces` the id, there is **exactly one** `<!-- pattern: <id> -->` markdown cell (an
   HTML-comment-only markdown cell) in the entry's notebooks, located via `concept_scan.entry_notebooks`
   (unit home: `lesson.ipynb` **and** the home `exercises.ipynb`; unit reappearance: `exercises.ipynb`;
   project: `brief.ipynb`). **Cardinality:** duplicate id in one notebook → FAIL; missing marker → FAIL;
   marker for an unregistered/unknown id → FAIL; **checkpoint carrying any pattern tag or marker →
   FAIL**. **Adjacency:** in an `exercises.ipynb` the marker cell is the markdown cell **immediately
   preceding** the tagged exercise's prompt cell (this is the tag→exercise link `technique-spiral`
   consumes for core-detection); in `lesson.ipynb`/`brief.ipynb` the marker sits in the Spotlight cell.
   Markers are HTML comments (dropped by nbconvert/pandoc — hygiene/PDF unaffected).
4. **`patterns-doc-check`** + **catalog generator**: `tools/patterns_doc.py generate` writes
   `book1/reference/patterns.md` from **machine-readable inputs** — the map's technique tags (home +
   reappearances table) plus a small committed data file `book1/curriculum/patterns-catalog.yaml`
   (`{id: {hook, enabling_concepts: [...]}}`) that supplies the prose the schema deliberately does not
   hold (no new `concepts.yaml` fields — the no-new-schema rule). The check: (a) committed
   `patterns.md` == generator output (byte-stable); (b) every registered Book-1 technique id appears with
   its `name` (from `concepts.yaml`), `hook`, and `enabling_concepts`; (c) each listed enabling concept
   is `introduces`d in an entry ≤ the pattern's home. Wire `tools/patterns_doc.py --check` into
   `tools/checks.py`; add the catalog to `scripts/build-pdf.sh` (pandoc, like `syllabus.md`), **guarding
   the step so it is a no-op when the Book-1 technique set is empty and never touches Book 2's build**.
5. **Tests:** pytest with discriminating fault fixtures — duplicate home; practice-before-home; only-two
   practices; checkpoint-only-third; stretch-only embodiment; unknown id; manifest/map mismatch; stale
   catalog; missing marker; duplicate marker; marker-adjacency wrong (marker not immediately before the
   prompt); checkpoint-carrying-a-tag; **Book-2 non-interference** (a fixture registering a Book-2-only
   technique id with <3 Book-1 practices must NOT fail `technique-spiral`, proving Book-1 scoping — cf.
   design §5.1). Real book passes (empty Book-1 technique set) + each fixture fails closed.
- **Acceptance (A):** `ci-local` ALL GREEN with the 3 checks active on the current (pattern-free) book;
  the committed ledger records per-unit resulting core counts and proves ≥3 core reappearances for all 7
  patterns (no ≤16 proof — ceiling lifted); catalog builds to PDF; Book 2 stays green throughout.

### Phases B–H — one vertical slice per pattern (content + tagging + catalog row)

Each slice, per the ledger, in the design's §3 order-of-safety. A slice = register the id in
`concepts.yaml`; tag its home (`introduces`) + its ≥3 reappearances (`practices`) in map+manifests; add
the `<!-- pattern: id -->` markers; author/adapt the Spotlight cells + exercises (reuse-tag / promote /
new per the ledger); add the catalog row; align teacher-notes (in-class home + unplugged trace). Each
slice keeps `ci-local` GREEN (technique-spiral satisfied for that id on merge).

Each promoting slice adds its stretch replacement **in the same slice** so every merge keeps ≥2 stretch
per unit (the vertical-slice invariant):
- **Phase B — `sentinel-loop`** (home u02 Ex3; reappearances project-01 M1, u07 Ex12 [`while` doubling,
  the true sentinel — not Ex13 which is counter/accumulator-bounded], u10 Ex14 promote → **+1 replacement
  Challenge cell in u10** in this slice).
- **Phase C — `running-total`** (home u04; u05 Ex7, u07 Ex4, u09 read-and-sum new; u09 gets
  `accumulator`+`arithmetic-operators` scanner-derived `practices`).
- **Phase D — `count-by-condition`** (home u04; u06 count-matches new, u07 Ex5, u08 Ex5/7 tally-by-key).
- **Phase E — `transform-each`** (home u06; u07 Ex6, u08 Ex10, u09 Ex3 — all reuse).
- **Phase F — `linear-search`** (home u06 + break; u07 loop+break new, u08 Challenge-1 reverse-lookup
  promote+break → retitle to Exercise-15 on promotion + move its solution heading, **+1 replacement
  Challenge cell in u08** in this slice, u09 find-in-file new; `break-statement` scanner-derived
  `practices` on u07/u08/u09).
- **Phase G — `find-extreme`** (home u07 champion-by-name new; u08 Ex6, u09 best-so-far new [+
  `comparison-operators` scanner-derived `practices` on u09], u10 Ex13 promote + `best_pet` → **+1
  replacement Challenge cell in u10** in this slice).
- **Phase H — `filter-into-list`** (home u07 new; u08/u09/u10 new) — **LAST** (touches four units in one
  PR — the largest/riskiest slice; ceiling no longer a factor).

Per-slice acceptance: the pattern's home+≥3 core reappearances embody the design's definition (content
gate confirms); markers present + adjacency-correct; catalog row generated-clean; the touched unit's
`stretch-remaining` ≥2 and its `concept-scan` green; `ci-local` GREEN incl.
`technique-spiral`/`pattern-marker`/`patterns-doc-check`.

### Phase V — Verification (named, mandatory)

`uv run pytest -q` green (incl. the new check fixtures); `scripts/ci-local.sh` ALL GREEN incl.
`technique-spiral` + `pattern-marker` + `patterns-doc-check` + the inherited concept checks +
notebook exec/hygiene/cell-lint + PDF (incl. the catalog) + pre-merge guard. **Volume budget
(plan-037 disposition, per PR):** measure the touched units' change in notebook cell count, PDF page
count, and exec wall-time; any slice exceeding **>2× cells / >30% PDF pages / >25% wall-time** (or any
cell >120 s) requires an **explicit content-gate sign-off** recorded in the PR's Content Review — not a
silent "recorded". No per-unit core-count cap (ceiling lifted); the ledger's counts are informative.
Confirm Book 2 stays green. **Proficiency/embodiment (reviewer-enforced):** for each of
the 7 patterns, a reviewer confirms the home + ≥3 core non-checkpoint reappearances each embody the
design's definition, in varied contexts (data-type/packaging/twist axis recorded in the Spotlight), with
the home in-class.

**Acceptance criteria:** all 7 patterns registered + spiralled ≥3 core; committed ledger records
per-unit core counts + `stretch-remaining` ≥2 + scanner-derived `practices` (no ≤16 proof); 3 new
checks green + fault-tested (incl. Book-2 non-interference); catalog delivered in the PDF; `ci-local`
ALL GREEN; `pre-merge-guard --pr` OK; plan-review + (per-PR) content-review 4-way consensus. **Rollout:**
phased PRs by pattern-group (Phase A + B–E as PR-1..n; the `filter-into-list` slice last), each a
complete vertical slice so `main` stays green.

---

## Plan Review

_(4-way gate — consensus = all four APPROVE / APPROVE WITH NITS, no open blockers.)_

### Round 1 (2026-09-18) — verdicts

- **[self] → APPROVE WITH NITS.** Spec-coverage vs design 002: every §3 pattern maps to a vertical slice;
  3 new checks + ledger + catalog are Phase A; NAMED Phase V present. No locus added/dropped/reclassified.
  NIT: name the ledger's home (`book1/curriculum/pattern-ledger.md`).
- **[glm] → REJECT** — B1 concept-closure (`break-statement` on u06–u09; `accumulator`/`arithmetic`/
  `comparison` on u09 → `concept-scan` RED unless added to `practices`); B2 stretch preservation (u10
  promotions leave <2 stretch). Both "small plan edits, expected to flip to APPROVE".
- **[fable] → REJECT** — same B1 + B2.
- **[sol] → REJECT** — (1) the exact ~28-row ledger is deferred + its location unresolved; the design
  assigns the exact ledger to the plan and needs it before rollout; (2) marker cardinality/adjacency +
  catalog-generator command/inputs undefined ("define … here") and the catalog's hooks/enabling-concepts
  have no source under the no-new-schema rule; (3) the ledger is dispatched to Codex but it is curriculum
  architecture → must be produced inline. NITS: add a Book-2 non-interference fixture; Phase V must
  repeat plan-037's explicit threshold sign-off (not merely "recorded").

### v2 reconciliation (2026-09-18) — all round-1 findings folded

- **User directive (mid-review): removed the ≤16 exercise ceiling** (design §7 v7). Constraints, Phase A,
  Phase V, acceptance, and the ledger reframed: counts are informative, not capped.
- **B1 (glm/fable):** new "Concept-closure" constraint — scanner-derived `practices` **pre-authorized**
  (plan-016/037 precedent), each closure-clean, enumerated (`break-statement`→u07/u08/u09;
  `accumulator`+`arithmetic-operators`→u09; `comparison-operators`→u09); "Do not touch" reworded to forbid
  only `introduces`/`requires` edits.
- **B2 (glm/fable), corrected by the real audit:** every unit has exactly 2 stretch cells, so **u08**
  (promotes Challenge 1) needs **+1** and **u10** (promotes Ex13+Ex14) needs **+2** replacement Challenge
  cells — added **in the promoting slice** to keep every merge ≥2; new "Stretch preservation" constraint +
  ledger `stretch-remaining` column.
- **[sol] B1:** the exact ~28-row ledger is now produced **inline** and embedded in **Appendix — Reuse
  ledger** (committed to `book1/curriculum/pattern-ledger.md`); records counts + `stretch-remaining` +
  scanner-derived practices (no ≤16 proof).
- **[sol] B2:** Phase A.3 defines exact marker cardinality/adjacency + core-detection; A.4 defines the
  `tools/patterns_doc.py generate` command + machine-readable inputs (`patterns-catalog.yaml` for
  hooks/enabling-concepts, no new schema).
- **[sol] B3:** Dispatch note now routes the ledger inline (Codex keeps tooling/content only).
- **[sol] nits:** Book-2 non-interference fixture added to Phase A.5; Phase V now requires explicit
  plan-037 threshold sign-off + Book-2-stays-green confirmation.

### Round 2 — [self] → APPROVE. [sol]/[glm]/[fable] re-dispatched on v2 (pending).

## Content Review

_(4-way gate — pre-PR after implementation, per PR. Findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`.)_

## Post-Execution Report

_(Written before PR.)_

---

## Appendix — Reuse ledger (source of record)

Produced INLINE from the real notebooks (exact headings + `stretch`-tag audit, 2026-09-18). This is the
acceptance artifact; `book1/curriculum/pattern-ledger.md` is generated verbatim from it and checked by
the content gate. **No ≤16 cap** (design §7 v7) — "resulting core" is informative pacing data. New/adapt
headings are the planned authoring targets (content gate confirms embodiment). `H*` = heading exact as in
the notebook; `→new`/`→promote`/`reuse` = action.

**Baseline core/stretch (audited):** u02 8/2 · u04 10/2 · u05 11/2 · u06 11/2 · u07 13/2 · u08 14/2 ·
u09 12/2 · u10 12/2. Project-01 has no `stretch` cells (milestones only).

| pattern | entry | exercise heading | now | action | enabling concepts | slice |
|---|---|---|---|---|---|---|
| running-total | u04 (home) | *new* "Running total: add the round scores" | new core | →new | accumulator (u04 co-intro), arithmetic (≤u02) | C |
| running-total | u05 | H "Exercise 7" `total_card_borders(n)` | core | reuse | — | C |
| running-total | u07 | H "Exercise 4 / Total and Average" | core | reuse | — | C |
| running-total | u09 | *new* "Sum the saved scores" (read-and-sum) | new core | →new | accumulator, arithmetic (both scanner-derived `practices` on u09), file-read (u09) | C |
| count-by-condition | u04 (home) | *new/adapt* "Count the correct answers" | new core | →new | comparison (≤u02), if (u02) | D |
| count-by-condition | u06 | *new* "Count the vowels" (count-matches) | new core | →new | in-operator (u06), comparison | D |
| count-by-condition | u07 | H "Exercise 5 / Award a Score Tier" | core | reuse | — | D |
| count-by-condition | u08 | H "Exercise 5: Count the Words" (tally-by-key) | core | reuse | — | D |
| find-extreme | u07 (home) | *new* "Champion by name" (best_name+best_score) | new core | →new | list-loop (u07), comparison | G |
| find-extreme | u08 | H "Exercise 6: Most Common Word" | core | reuse | — | G |
| find-extreme | u09 | *new* "Highest score by scanning" (best-so-far, no `max()`) | new core | →new | comparison (scanner-derived `practices` on u09) | G |
| find-extreme | u10 | H "Exercise 13: Happiest Pet" + `best_pet` | **stretch** | →promote | — | G (**+1 u10 stretch replacement**) |
| linear-search | u06 (home) | lesson `for … range(26)` scan + home ex adds `break` | new/adapt core | →new/adapt | for (u03), break (u04), in (u06), comparison | F |
| linear-search | u07 | *new* "Find the first over the bar, stop early" | new core | →new | break (scanner-derived `practices` on u07) | F |
| linear-search | u08 | H "Challenge 1: Reverse Lookup" → **Exercise 15** + `break` | **stretch** | →promote | break (scanner-derived `practices` on u08) | F (**+1 u08 stretch replacement**) |
| linear-search | u09 | *new* "Find a name in the save file" | new core | →new | break (scanner-derived `practices` on u09) | F |
| transform-each | u06 (home) | *new/adapt* "Do the same to each character" | new core | →new/adapt | for (u03), string-methods (u06) | E |
| transform-each | u07 | H "Exercise 6 / Tidy the Champion Names" | core | reuse | — | E |
| transform-each | u08 | H "Exercise 10: Translate a List" | core | reuse | — | E |
| transform-each | u09 | H "Exercise 3: Load Scores into a List" (line→int) | core | reuse | — | E |
| filter-into-list | u07 (home) | *new* "Keep only the qualifying scores" | new core | →new | list-append (u07), comparison | H |
| filter-into-list | u08 | *new* "Keep only the long words" | new core | →new | list-append, comparison | H |
| filter-into-list | u09 | *new* "Load only the high scores" | new core | →new | list-append, comparison, file-read | H |
| filter-into-list | u10 | *new* "List the happy pets" | new core | →new | list-append, comparison | H |
| sentinel-loop | u02 (home) | H "Exercise 3" while-until-guessed game | core | reuse-as-home | while (u02), comparison (u02) | B |
| sentinel-loop | project-01 | M1 `while choice != "q"` menu | core | reuse | — | B |
| sentinel-loop | u07 | H "Exercise 12: Double the Qualifying Threshold" (`while`, true sentinel) | core | reuse | — | B |
| sentinel-loop | u10 | H "Exercise 14: Play Until Happy" (`while happiness<10`) | **stretch** | →promote | — | B (**+1 u10 stretch replacement**) |

**Resulting per-unit core count (projected, informative — not a cap):**

| unit | baseline core | +new core | resulting core | stretch after (promotions −, replacements +) |
|---|---|---|---|---|
| u02 | 8 | 0 (sentinel home = reuse Ex3) | 8 | 2 |
| u04 | 10 | +2 (running-total + count homes) | 12 | 2 |
| u05 | 11 | 0 (reuse Ex7) | 11 | 2 |
| u06 | 11 | +2 (count-matches new; linear-search & transform-each homes) | 13 | 2 |
| u07 | 13 | +3 (find-extreme home, filter home, loop+break) | 16 | 2 |
| u08 | 14 | +2 (reverse-lookup promote→core, filter new) | 16 | 2 − 1 promote + 1 repl = 2 |
| u09 | 12 | +4 (read-and-sum, best-so-far, find-in-file, filter — all new) | 16 | 2 |
| u10 | 12 | +3 (Ex13 promote, Ex14 promote, filter new) | 15 | 2 − 2 promote + 2 repl = 2 |

Every pattern reaches **≥3 core non-checkpoint reappearances** (home excluded): running-total u05/u07/u09;
count-by-condition u06/u07/u08; find-extreme u08/u09/u10; linear-search u07/u08/u09; transform-each
u07/u08/u09; filter-into-list u08/u09/u10; sentinel-loop project-01/u07/u10. Every touched unit keeps
`stretch-remaining` ≥2. Scanner-derived `practices` additions (all closure-clean): `break-statement`
(intro u04) → u07/u08/u09; `accumulator` (u04) + `arithmetic-operators` (≤u02) → u09;
`comparison-operators` (≤u02) → u09.
