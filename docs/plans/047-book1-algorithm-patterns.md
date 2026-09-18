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

**Spec:** `docs/designs/002-book1-algorithm-patterns.md` (v7 — the authority for the
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
- **Concept-closure — plan-037-style General Rule (scanner-derived `practices` PRE-AUTHORIZED):** a new
  pattern exercise may make `concept-scan` (AST; observes lesson + exercises + solutions + assets, not
  only the new exercise) detect a concept not yet in the entry's union. **General rule (mirrors plan-037):**
  the implementer MAY add that concept to the entry's `practices` (map + manifest) **iff** it is
  `introduces`d in an entry ≤ the entry (closure, verified by `prereq_findings`), is NOT in the entry's
  own `introduces`, and no `introduces`/`requires` changes are made. Every such addition MUST be recorded
  in the ledger, surfaced in that PR's description AND the content-review gate (not merely the
  post-execution report), and get reviewer sign-off — not a silent license. **Anticipated set (exact
  registry ids** from `concepts.yaml` — `arithmetic`/`comparison`, NOT `*-operators`, which are unknown
  ids that hard-FAIL `referenced_concepts_findings`**):** `break-statement` (intro u04) → `practices` of
  **u06/u07/u08/u09** (linear-search home u06 adds `break`, plus u07/u08/u09 reps); `accumulator` (u04) +
  `arithmetic` (u02) → **u09** (running-total read-and-sum); `comparison` (u02) → **u09** (find-extreme
  best-so-far); `builtin-functions` (intro u07) → **u08** (filter "keep the long words" calls `len()`).
  This list is the *expected* set; the General Rule bounds any further miss.
- **New-exercise authoring guards (avoid genuine prereq violations `practices` cannot fix):** u04 has
  **no `for`/`range`/list** in its union (all loops are counter-bounded `while` + `int(input())`), so the
  u04 homes (running-total, count-by-condition) are authored **`while`-based and use NO list**
  (`list-literal`/`list-append` are u07 — a real prereq violation, not a scanner-derived add). The u06
  transform-each home builds a **new string** (not a list) for the same reason. Content gate confirms.
- **Stretch preservation (per `notebooks.py` L536-538, whose L538 fails when `stretch`-tagged CELLS <2):** the CI floor
  is ≥2 tagged cells; per-unit tagged-cell totals vary (audited: u02 5, u04 5, u05 6, u06 6, u07 5, u08 4,
  u09 4, u10 4 — some units also tag a header cell), so the plan tracks the invariant in **Challenge
  *exercises*** (each = the prompt/heading cell **and** its code cell, both tagged). **Target: every
  touched unit retains ≥2 Challenge exercises** (always ≥2 tagged cells → CI-safe). Promotions & in-slice
  replacements: **u10** promotes BOTH Challenges (Ex13 find-extreme, Ex14 sentinel-loop) → 2→0 → add **+2
  replacement Challenge exercises** (Phase B adds 1 when it promotes Ex14; Phase G adds 1 when it promotes
  Ex13 — so u10 never drops below 2 tagged cells at a merge); **u08** promotes Challenge 1 (reverse-lookup)
  → 2→1 Challenge (Challenge 2's 2 cells remain → CI still ≥2) → add **+1** replacement to keep 2
  Challenges (pedagogical, not a CI necessity). **Mechanics:** a promotion = drop the `stretch` tags from
  the exercise's cells and remove the "**Challenge:**" prompt prefix (u10 Ex13/Ex14 already use
  `## Exercise N` headings; u08 Challenge 1 → retitle `## Exercise 15`); a replacement = a NEW exercise
  with BOTH its heading and code cell `stretch`-tagged, **following the touched unit's own Challenge
  convention** — u08 keeps `## Challenge N`; u10 keeps `## Exercise N` heading + "**Challenge:**" prefix
  (which also keeps those cells inside `solutions_structure` heading-pairing). Replacements are
  **status-preserving** (NOT §3 loci; no pattern tag/marker). The ledger's `stretch-remaining` column
  records **Challenge-exercise count** for every touched unit.
- **Do not touch:** `introduces`/`requires` for regular concepts (technique tags + scanner-derived
  `practices` additions under the General Rule above are the ONLY metadata edits); Book 2 anything; governance
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

1. **Reuse ledger.** The **source of record is this plan's "## Appendix — Reuse ledger"** (produced
   INLINE and approved BEFORE any content phase — see Dispatch note; it already exists in this plan). Phase
   A **materializes it as the tracked file `book1/curriculum/pattern-ledger.md`** (derived from the
   Appendix, normalized for tooling — exact registry ids, prose prefixes dropped — same loci/actions/
   counts; the content gate checks against the file — it is a Phase-A deliverable, NOT yet present in
   earlier commits). Columns per locus: `pattern, entry, exact exercise heading, core/stretch now,
   action (reuse-tag/promote/new), enabling concepts, resulting unit core count, stretch-remaining
   (Challenge-exercise count)`. With the ceiling lifted (design §7 v7) the ledger no longer proves a ≤16
   bound; it MUST (a) record each touched unit's resulting core count as informative pacing data (projected
   u07≈16, u08≈16, u09≈16, u10≈15), (b) prove every pattern reaches **≥3 core non-checkpoint
   reappearances**, and (c) record `stretch-remaining` ≥2 Challenge exercises for every touched unit.
2. **`technique-spiral`** check in `tools/` (Book-1-scoped): each Book-1 `kind: technique` id is
   `introduces`d once + `practices`d in ≥3 pre-capstone non-checkpoint entries whose marked exercise is
   **core** (not stretch). **Core-detection:** an exercise is stretch iff its prompt cell or its adjacent
   solution code cell carries the `stretch` tag (`"stretch" in tags(cell)`, reusing `notebooks.tags`);
   the marker's tag→cell link (from `pattern-marker`, step 3) identifies which exercise a locus is, so
   spiral and marker are **co-designed**. Scope: iterate only ids registered under Book 1's
   `concepts.yaml` and invoke on the Book-1 tree, so Book-2 techniques are never in scope. Registered in
   `tools/checks.py`; wired into `ci-local`. Green on the empty Book-1 technique set (no patterns yet).
3. **`pattern-marker`** check — exact rules: for every `(entry, pattern-id)` where the entry
   `practices`/`introduces` the id, there is **exactly one markdown cell whose source contains
   `<!-- pattern: <id> -->`** in the entry's notebooks (in `exercises.ipynb` this is a dedicated
   HTML-comment-only adjacency cell; in `lesson.ipynb`/`brief.ipynb` the comment lives inside the
   prose-bearing Spotlight cell), located via `concept_scan.entry_notebooks`
   (unit home: `lesson.ipynb` **and** the home `exercises.ipynb`; unit reappearance: `exercises.ipynb`;
   project: `brief.ipynb`). **Cardinality:** duplicate id in one notebook → FAIL; missing marker → FAIL;
   marker for an unregistered/unknown id → FAIL; **checkpoint carrying any pattern tag or marker →
   FAIL**. **Adjacency:** in an `exercises.ipynb` the marker cell is the markdown cell **immediately
   preceding** the tagged exercise's **prompt cell** — defined as the exercise's **heading-bearing
   markdown cell** (the `## Exercise N` cell; u02/u05 split heading and body into separate markdown cells,
   so the marker precedes the heading cell); this is the tag→exercise link `technique-spiral` consumes for
   core-detection. In `lesson.ipynb`/`brief.ipynb` the marker sits in the Spotlight cell.
   Markers are HTML comments (dropped by nbconvert/pandoc — hygiene/PDF unaffected).
4. **`patterns-doc-check`** + **catalog generator**: `tools/patterns_doc.py generate` writes
   `book1/reference/patterns.md` from **machine-readable inputs** — the map's technique tags (home +
   reappearances table) plus a small committed data file `book1/curriculum/patterns-catalog.yaml`
   (`{id: {hook, enabling_concepts: [...]}}`) that supplies the prose the schema deliberately does not
   hold (no new `concepts.yaml` fields — the no-new-schema rule). **`enabling_concepts` MUST use exact
   registry ids** (`if-statement`, `for-loop`, `while-loop`, `in-operator`, `range-function`,
   `break-statement`, `list-append`, … — NOT the ledger's prose shorthand `if`/`for`/`while`/`in`), or
   check (c)'s intro≤home resolution fails. The check: (a) committed
   `patterns.md` == generator output (byte-stable); (b) every registered Book-1 technique id appears with
   its `name` (from `concepts.yaml`), `hook`, and `enabling_concepts`; (c) each listed enabling concept
   id resolves in `concepts.yaml` and is `introduces`d in an entry ≤ the pattern's home. Wire
   `tools/patterns_doc.py --check` into
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
  Challenge exercise in u10** in this slice).
- **Phase C — `running-total`** (home u04; u05 Ex7, u07 Ex4, u09 read-and-sum new; u09 gets
  `accumulator`+`arithmetic` scanner-derived `practices`).
- **Phase D — `count-by-condition`** (home u04; u06 count-matches new, u07 Ex5, u08 Ex5/7 tally-by-key).
- **Phase E — `transform-each`** (home u06; u07 Ex6, u08 Ex10, u09 Ex3 — all reuse).
- **Phase F — `linear-search`** (home u06 + break; u07 loop+break new, u08 Challenge-1 reverse-lookup
  promote+break → retitle to Exercise-15 on promotion + move its solution heading, **+1 replacement
  Challenge exercise in u08** in this slice, u09 find-in-file new; `break-statement` scanner-derived
  `practices` on **u06/u07/u08/u09**).
- **Phase G — `find-extreme`** (home u07 champion-by-name new; u08 Ex6, u09 best-so-far new [+
  `comparison` scanner-derived `practices` on u09], u10 Ex13 promote + `best_pet` → **+1
  replacement Challenge exercise in u10** in this slice).
- **Phase H — `filter-into-list`** (home u07 new; u08/u09/u10 new; `builtin-functions` scanner-derived
  `practices` on u08 for the `len()` filter; u08's new filter exercise is numbered **Exercise 16** (next
  after the Ex15 promoted in Phase F — clean sequential numbering; `solutions_structure_findings` pairs
  by heading lookup, not position, so this is tidiness not a hard constraint)) — **LAST** (touches four
  units in one PR — the largest/riskiest slice; ceiling no longer a factor).

**Exercise numbering (content-authoring):** new core exercises take the next sequential `## Exercise N`
after each unit's current highest core number; where a unit's stretch Challenges sit at the end
(u09 Ex13/14, u10 Ex13/14), new core slot before them or the Challenge pair is renumbered to remain last
(a content-gate detail — pairing is per-heading, so either is CI-green). **Spotlight cells in
`exercises.ipynb` must not use any heading containing "solution"** (case-insensitive) — it trips
`hygiene_findings`' `SOLUTION_HEADING` guard.

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

### Round 2 (2026-09-18) — verdicts on v2

- **[self] → APPROVE.**
- **[sol] → REJECT, no blockers** — 2 nits only: stale "v6" authority ref; "2 stretch" conflates
  exercises with `stretch`-tagged cells (L537 counts cells). Confirmed ceiling-removal clean, stretch
  invariant holds at every merge, ledger sound.
- **[glm] → REJECT** — B1a: `arithmetic-operators`/`comparison-operators` are **nonexistent ids**
  (registry uses `arithmetic`/`comparison`) → would hard-FAIL `referenced_concepts_findings`. B1b:
  `break-statement` addition **omits u06** (linear-search home u06 adds `break`) → `concept-scan` RED on
  u06. NITs: per-cell vs per-exercise stretch arithmetic; stale "v6".
- **[fable] → REJECT** — one blocker: B1 enumeration (same u06 omission + wrong ids as [glm]) **plus**
  the closed whitelist is fragile — two more near-certain scanner misses: u08 filter calls `len()` →
  `builtin-functions` (u07, closure-clean); u04 has NO `for`/`range`/list, so u04 homes must be
  `while`-based and use no list (`list-literal` is u07 = a real prereq violation). Fix: adopt plan-037's
  open **General Rule** + authoring guards. B2 resolved (nits: track stretch as *exercises* not cells;
  promotion/replacement mechanics; u08 filter → Ex16). Everything else confirmed sound (≤16 removal,
  ledger ≥3, Book-2 non-collision, marker lint-safety).

### v3 reconciliation (2026-09-18) — round-2 fixes folded (verified against the registry/notebooks)

- **[glm]/[fable] B1a (verified):** corrected ids to `arithmetic` (concepts.yaml:19) / `comparison`
  (concepts.yaml:22) in the constraint, Phases C/G, ledger, summary. concept_scan.py emits exactly these.
- **[glm]/[fable] B1b (verified):** `break-statement` now on **u06/u07/u08/u09** (u06 union lacks it +
  home adds `break`).
- **[fable] B1c (verified, adopted):** replaced the closed whitelist with plan-037's **General Rule**
  (any scanner-derived `practices` add pre-authorized iff closure-clean, not in `introduces`, no
  `introduces`/`requires` change, recorded in ledger + surfaced in PR/content gate). Added
  `builtin-functions` (u07) → **u08** (filter `len()`) to the anticipated set; added **authoring guards**
  (u04 homes `while`-based/no-list; u06 transform-each builds a string) to prevent genuine u07-prereq
  (`list-literal`) violations `practices` cannot fix.
- **[glm]/[sol]/[fable] B2 (verified):** tagged-cell totals vary per unit (audited u02 5 … u08 4, u10 4);
  restated the invariant in **Challenge exercises** (each = 2 tagged cells → always ≥ the CI ≥2-cell
  floor). Promotion = drop tags + remove "**Challenge:**" prefix; replacement = new `## Challenge N`
  exercise with both cells tagged. u08 Challenge-1 → Exercise-15 (Phase F); u08 filter → Exercise-16
  (Phase H) so `solutions_structure_findings` pairing stays ordered.
- **[fable] nits:** marker "prompt cell" = the heading-bearing markdown cell (u02/u05 split
  heading/body); `pattern-ledger.md` clarified as a Phase-A deliverable (the Appendix is the source of
  record; the file is generated in Phase A, not present in earlier commits).
- **[sol]/[glm]/[fable] nit:** authority ref corrected v6 → **v7** (Spec line).

### Round 3 (2026-09-18) — CONSENSUS, gate CLOSED

- **[self] → APPROVE · [sol] → APPROVE · [glm] → APPROVE WITH NITS · [fable] → APPROVE WITH NITS.**
  All round-2 blockers verified resolved against the registry/tools/notebooks; **no open blockers**.
  [fable] re-verified nothing new goes CI-RED (marker lint-safety, `stretch-check`, `solutions_structure`
  `\b` word-boundary, Book-2 non-interference via dynamic `dependency_baseline` + per-book `never_flag`).
  **4-way consensus reached → plan-review gate CLOSED.**

### v4 (2026-09-18) — non-blocking nits folded (no re-review; consensus already met)

- **[glm] N1:** Phase A.4 now requires `patterns-catalog.yaml` `enabling_concepts` to use **exact
  registry ids** (`if-statement`/`for-loop`/`while-loop`/`in-operator`/…), not the ledger's prose
  shorthand, so `patterns-doc-check`'s intro≤home resolution succeeds.
- **[glm] N2 / citation:** stretch-floor citation corrected to `notebooks.py` L536-538 (L538 is the
  failing `<2` comparison).
- **[fable] N1:** `pattern-marker` restated as "a markdown cell whose source contains `<!-- pattern: id -->`"
  (comment-only adjacency cell in `exercises.ipynb`; inside the Spotlight prose cell in lesson/brief).
- **[fable] N2:** replacement Challenges follow each unit's **local convention** (u08 `## Challenge N`;
  u10 `## Exercise N` + "**Challenge:**" prefix — keeping those cells in `solutions_structure` pairing).
- **[fable] N3:** softened the u08 Ex16 "ordering" rationale (pairing is per-heading, not positional);
  added an exercise-numbering + Spotlight-heading ("no 'solution' in headings") authoring note.

## Content Review

_(4-way gate — pre-PR after implementation, per PR. Findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`.)_

### PR-1 = Phase A (tooling-only, commit 0cde07e) — 2026-09-18

Tooling-only slice (no student content to blind-solve → this gate is a code review of the 3 checks +
generator + ledger). Bundles design 002 + plan 047 + Phase A tooling as the foundation PR.

- **[self] → APPROVE.** Read `tools/patterns.py` + `tools/patterns_doc.py` in full. `technique-spiral`
  and `pattern-marker` implement Phase A.2/A.3 exactly (exactly-one-home; ≥3 core pre-capstone
  non-checkpoint practices via marker→exercise link + `notebooks.tags` stretch-rejection; marker
  cardinality + `## Exercise N` adjacency; comment-only vs in-prose; checkpoints carry no tag/marker;
  manifest==map; capstone via project-02 prefix). Fail-closed on malformed YAML/markers + capstone
  count≠1 (Codex's own quality-review fixes, verified present). `patterns-doc-check` byte-stable +
  enabling_concepts resolve to registry ids introduced ≤ home; book1-only; build-pdf guarded (empty
  no-op, never book2). **Verified in kernel env:** 3 checks PASS book1 / inert book2; pytest 339 passed;
  ruff clean; inherited concept checks + book2 no regression; build-pdf PASS (patterns.pdf absent). No
  unit notebook content changed. Verdict: APPROVE. Awaiting [sol]/[glm]/[fable].
- **[glm] → APPROVE WITH NITS.** Ran pytest (492 passed), ruff clean, 3 checks PASS book1+book2,
  adversarial probes fail closed. Nits (non-blocking): missing-dir checkpoint tag `continue`s past both
  checks; ledger "verbatim" is normalized; `--pdf-probe` skips byte-stability; empty `enabling_concepts`
  allowed.
- **[fable] → APPROVE WITH NITS.** pytest 339 + ad-hoc adversarial probes; Book-2 safe; empty-set green.
  Nits: N1 spiral home-as-reappearance (`index >= home_index`); N2 null-YAML-doc reads as empty; N3
  add project-locus tests in Phase B; N4 `<!-- Pattern:` (capital) ignored; N5 ledger "verbatim".
- **[sol] → REJECT → (fixes applied, re-review dispatched).** Two `[OPEN]` fail-opens, both fixed in
  commit below with discriminating tests:
  - `[FIXED]` **malformed-marker fail-open:** `MARKER_LIKE` required a colon, so a colon-less
    `<!-- pattern id -->` on a checkpoint evaded the no-marker guard. Broadened the regex to
    `<!--\s*pattern\b\s*:?\s*(...)-->` — colon-less/bare now match and are flagged invalid (exact=False),
    so checkpoints reject them and normal entries FAIL "invalid pattern marker". No false positives
    (`patterns`, prose `note: pattern` unmatched). New test
    `test_pattern_marker_rejects_colonless_comment_on_checkpoint`.
  - `[FIXED]` **spiral home-as-reappearance ([sol]+[fable] N1):** `index >= home_index` counted a home
    self-`practices` tag as a reappearance. Changed to `index > home_index`. New test
    `test_technique_spiral_excludes_home_self_practice`.

**Nit dispositions (non-blocking):**
- `[FIXED]` [glm]/[fable] N5 ledger "verbatim" → reworded ledger header + Phase A.1 to "derived/normalized".
- `[WONTFIX]` [glm] missing-dir checkpoint tag + [fable] N2 null-root-YAML: both are caught upstream —
  a registered entry with a missing dir, or an empty `concepts.yaml`, fails `manifest-check`/`registry`/
  `coverage-check` catastrophically before these checks matter; defense-in-depth here isn't worth the
  loop restructuring, and the strictest reviewer ([sol]) did not raise them.
- `[WONTFIX]` [fable] N4 `<!-- Pattern:` (capital): the canonical marker is lowercase; a capitalized
  variant on a *tagged* entry still fails "found 0", and on an untagged entry it is inert prose.
- `[DEFERRED→Phase B]` [fable] N3: add enabling-intro>home / unregistered-id / project-brief-locus
  fixtures when project-01 first becomes a real locus (Phase B).

**Round 2 (commit 1ba7503) — CONSENSUS, content gate CLOSED for PR-1.** [sol] → APPROVE (both fail-opens
verified closed, 43 passed, checks green book1+book2, no new issues). Final: [self] APPROVE · [glm]
APPROVE WITH NITS · [fable] APPROVE WITH NITS · [sol] APPROVE — no open blockers.

### PR-2 = Phase B (sentinel-loop slice, commit ae44749) — 2026-09-18 — CONSENSUS

- **[self] → APPROVE** (Spotlights + markers correct; embodiments match design §3).
- **[sol] → APPROVE** (blind-solved all four loci; only a WONTFIX env note — its sandbox blocked
  exec-solutions so it used an input-trapped plain-Python fallback; all four solution notebooks passed).
- **[fable] → APPROVE WITH NITS** (blind-solved every locus: all four are true condition-driven
  sentinels, none counter-bounded; spiral/stretch/integrity green; pytest 43).
- **[glm] → APPROVE WITH NITS** (embodiments genuine; pytest 446 `-k 'not exec'`; Book 2 zero-diff).
- No open blockers → **content gate CLOSED**.

**Nit dispositions (commit below):**
- `[FIXED]` [fable] N1 + [glm] (pedagogy/self-containedness): u02 lesson Spotlight "Unlike a counted
  loop…" → "Unlike a loop that runs a fixed number of times…" (counted loops are u03; u02 is
  deliberately counter-free).
- `[FIXED]` [fable] N3: renamed `test_real_book_..._empty_technique_set` → `..._pass_on_real_book`.
- `[FIXED]` [fable] N4: added `assert len(pets) >= 3` to the u10 Ex15 solution (unit convention).
- `[FIXED]` [fable] N2: landed the deferred enabling-concept-introduced-after-home fault fixture
  (`test_patterns_doc_rejects_enabling_concept_introduced_after_home`).
- `[WONTFIX]` [glm]/[fable] process: u10 solutions authored inline (env-forced; Codex solutions session
  unreliable under memory pressure) — mitigated by all reviewers blind-solving the marked loci.
- `[WONTFIX]` reappearance-unit teacher-notes not individually updated — the plan requires only the
  home's in-class note + unplugged trace (both in u02 teacher-notes); routing is centralized there.
- Ledger already records the u07 Ex12 selection (Ex13 excluded as accumulator-bounded).

### PR-3 = Phase C (running-total slice, commit cf0bcc8 + nit-fix) — 2026-09-18 — CONSENSUS

- **[self] → APPROVE** (embodiments = named total-so-far; varied contexts; markers correct).
- **[sol] → APPROVE WITH NITS** (blind-solved; nit = u09 Ex13 solution should store `score`).
- **[glm] → APPROVE WITH NITS** (data-flow-verified all loci; nits N1 home-in-class placement, N2 u09
  heading mismatch, N3 u09 `score`).
- **[fable] → APPROVE WITH NITS** (blind-solved u04→17/u05→280/u07→2400/u09→2825; pytest 495; nits =
  u04 stand-in comment, u09 heading, `score` var naming).
- No open blockers → **content gate CLOSED**.

**Nit dispositions (nit-fix commit):**
- `[FIXED]` [glm] N1 (home in-class): relocated the u04 running-total home exercise from the "More
  Practice — homework" section into the in-class block (now Ex8; old Ex8/9/10 → Ex9/10/11 in both
  exercises + solutions) so the home rep is in-class per the plan constraint. **Precedent for D–H: new
  home authoring exercises go in the in-class section.**
- `[FIXED]` [glm] N2 / [fable]: u09 solutions "More Practice … 10–12" → "10–13".
- `[FIXED]` [glm]/[sol]/[fable] N3: u09 Ex13 solution stores `score = int(line.strip())` per the prompt;
  u04 running-total solution uses `score` + a stand-in comment (reworded to avoid the literal `input(`
  token that `structure-check` textually flags — lesson for future solutions).

### PR-4 = Phase D (count-by-condition slice, commit 84e3697 + fixes be81fed) — 2026-09-18 — CONSENSUS

- **[self]/[glm]/[fable] → APPROVE (WITH NITS)** (all blind-solved: u04→2, u06→4, u07→1, u08 tally owl=3).
- **[sol] → REJECT (round 1) → APPROVE (round 2)** — one blocker fixed.
- No open blockers → **content gate CLOSED**.

**Dispositions:**
- `[FIXED]` **[sol] blocker:** the new u06 Ex12 (count-by-condition retrieval) had no teacher-notes
  pacing entry — placed it in Lesson 2 in-class (rides the `in` ladder) + updated the exercise-split
  count (1–11 → 1–12). Lesson learned: **a new core exercise must be added to the unit's teacher-notes
  pacing/allocation** (folded into the D–H authoring instructions).
- `[FIXED]` [glm]/[fable]/[sol] nit: u04 teacher-notes "exercise 8" → "exercise 10" (Accept-either-
  spelling `or` activity, stale after the two u04 renumberings from Phase C + D).
- `[FIXED]` [fable] nit: reworded the u04 Ex9 solution stand-in comment (prompt fixes the booleans).
- `[WONTFIX]` [fable] N4 (Spotlight-to-demo gap): consistent with the Phase-C precedent; leave.

### PR-5 = Phase E (transform-each slice, commit b0f36d9 + fix 5b71599) — 2026-09-18 — CONSENSUS

- **[self]/[glm] → APPROVE** ([glm] clean, no nits); **[fable] → APPROVE WITH NITS**; **[sol] → REJECT
  (round 1) → APPROVE (round 2)**. No open blockers.
- All reviewers blind-solved: u06→"meet @t noon", u07 dedup, u08 translate, u09 [1375,910,1260].

**Dispositions:**
- `[FIXED]` **[fable] NIT-1 (within-unit pacing):** u06 Ex13 (transform-each home) was paced in Lesson 1,
  but its Spotlight is in Lesson 3 and direct string iteration is first modelled in Lesson 2 — moved
  Ex13's pacing + unplugged trace to Lesson 3 (it rides the `encode` per-character rebuild). Teacher-notes
  only. **Precedent for F–H: pace a new home in the lesson that actually teaches its enablers, not just
  "the first lesson".**
- `[NOT-A-DEFECT]` **[sol] round-1 REJECT (byte-stability):** [sol] read "catalog + patterns.md
  byte-stable" as "unchanged from main" and flagged the transform-each catalog/patterns.md additions.
  Clarified: the criterion is "committed patterns.md == generator output" (`patterns-doc-check` PASS);
  registering a pattern MUST add those rows (as B–D did). [sol] round-2 APPROVED under the corrected
  criterion (only the transform-each additions, no churn). Review-wording fix, no code change.
- `[WONTFIX]` [fable] NIT-2 (pre-existing missing cell id) + u07 dedupe observation (design-authorized).

### PR-6 = Phase F (linear-search slice, commit a73dce2 + nit-fix) — 2026-09-18 — CONSENSUS

- **[self] APPROVE · [sol] APPROVE (no findings; AST-audited `break` in all 4 solutions) · [glm]
  APPROVE WITH NITS · [fable] APPROVE WITH NITS.** No open blockers → **content gate CLOSED**.
- Reviewers blind-solved: u06→12, u07→1050/not-found, u08→"dog" (value→key), u09→"Mina". u08 kept 2
  Challenges (Merge + new "Flip the Phrasebook"); break present in every marked locus.

**Dispositions:**
- `[FIXED]` [fable] NIT-1: u09 student-facing header "More Practice … Exercises 10–13" → "10–14" (Ex14
  is now core) in exercises + solutions.
- `[FIXED]` [fable] NIT-3: u06 Spotlight clarified — the lesson's `range(26)` scan has no `break`;
  Exercise 14 adds it (removes a "where's the break?" moment).
- `[RECORDED]` [fable] NIT-2: **an additional scanner-derived `practices += comparison` on u09** was
  needed (the new find-in-file uses `==`), beyond the commit's listed `break-statement`. Closure-clean
  (`comparison` introduced u02 ≤ u09), General Rule. **Phase-G watch:** the ledger projected `comparison`→u09
  for find-extreme's best-so-far — it is ALREADY present now, so Phase G must NOT double-add it.
- `[WONTFIX]` [glm] N2 (u08 teacher-notes "every concept has an in-class rep"): break-statement's in-class
  rep is the u06 home; the u08 Ex15 appearance is a reappearance correctly routed — the claim concerns
  u08's own concepts, so no correction needed.
- `[DEFER]` [fable] NIT-4 (ledger row projects u06=13, now 14): informative; the ledger is refreshed
  in bulk later (prior slices D/E left it untouched — consistent rollout).

### PR-7 = Phase G (find-extreme slice, commit f13e687 + nit-fix) — 2026-09-18 — CONSENSUS

- **[self] APPROVE · [sol] APPROVE (no findings) · [glm] APPROVE WITH NITS · [fable] APPROVE WITH NITS.**
  No open blockers → **content gate CLOSED**.
- Reviewers blind-solved: u07→"Leo 1540", u08→"owl 3", u09→1350 (no `max()`), u10→"Sunny"/best_pet.
  Confirmed **`comparison` NOT double-added to u09** (already present from Phase F); u10 kept 2 Challenges.

**Dispositions:**
- `[FIXED]` [fable] NIT-2: titled the u10 replacement Challenge → "## Exercise 16: Pet-Care List"
  (matches the unit's `Exercise N: Title` convention).
- `[WONTFIX]` [glm]/[fable] NIT-1 (u07 Ex15 home appended after the homework block rather than physically
  inside the in-class block): its in-class delivery is established by the "In-Class Pattern Practice"
  header + teacher-notes pacing ("1–9 and 15"), which **[sol] explicitly validated** (it PASSED the
  pacing/numbering criterion — the same reviewer that blocked Phase D on a pacing gap). A 5-exercise
  renumber on a consensus-approved slice carries more risk than the minor linear-reading oddity; the
  pedagogical "home is in-class" requirement is met.
- `[WONTFIX]` [glm]/[fable] NIT-3 (u09 keeps value-only, not WHO): design §3 explicitly makes u09 the
  `max()`-replacing best-so-far variation (value-only), recorded as its variation axis — within authority.
- `[NO-ACTION]` [fable] NIT-4 (u07 solutions stretch-tag alignment on pre-existing Challenges): benign
  hygiene alignment for `stretch-check` pairing, not a content change.

## Post-Execution Report

### PR-1 = Phase A (tooling foundation) — 2026-09-18

**Shipped:** design 002 (v7) + plan 047 (v4) + Phase A tooling — the pattern-thread foundation. NO
pattern ids registered; the book stays pattern-free and every new check is green on the empty set.

**Delivered (commits 0cde07e + 1ba7503):**
- `tools/patterns.py` — `technique-spiral` + `pattern-marker` checks (Book-1-scoped; exactly-one-home,
  ≥3 core pre-capstone non-checkpoint practices with home excluded, stretch-rejection, marker
  cardinality + `## Exercise N` adjacency + comment-only/in-prose, checkpoints carry none, manifest==map,
  capstone via project-02; fail-closed on malformed YAML/markers + capstone count≠1).
- `tools/patterns_doc.py` — `patterns-doc-check` + catalog generator (byte-stable; enabling_concepts
  resolve to registry ids introduced ≤ home; book1-only).
- `book1/curriculum/patterns-catalog.yaml` (empty), `book1/reference/patterns.md` (empty-but-valid),
  `book1/curriculum/pattern-ledger.md` (the ~28-row acceptance ledger, normalized from the plan Appendix).
- `tools/checks.py` + `tools/cli.py` register 3 book-level checks; `scripts/ci-local.sh` wires them
  book1-only; `scripts/build-pdf.sh` guards the patterns PDF (no-op empty, never book2).
- `tests/test_patterns.py` — 43 fault fixtures incl. Book-2 non-interference + the 2 content-gate
  fail-open regression tests.

**Verification (kernel env):** 3 new checks PASS book1 / inert-PASS book2; inherited concept checks +
book2 no regression; `pytest tests/test_patterns.py tests/test_tools.py` all pass (444 with `-k 'not
exec'`; the only failures anywhere were the known Jupyter-kernel sandbox socket restriction, which does
not affect Phase A — no unit notebook content changed); ruff clean; build-pdf PASS with `patterns.pdf`
correctly absent (empty no-op).

**Gates:** plan-review 4-way CONSENSUS (round-3); content-review 4-way CONSENSUS (round-2). No open
blockers; nits fixed or dispositioned above.

**Deviations from plan:** none material. Ledger is normalized (exact ids) rather than byte-verbatim from
the Appendix (recorded). Two fail-open hardening fixes were added during the content gate (colon-less
marker detection; spiral home exclusion) — both within Phase A scope.

**Next:** pattern slices B–H (one vertical slice per pattern, filter-into-list last), each self-complete
so `main` stays green.

### PR-2 = Phase B (sentinel-loop slice) — 2026-09-18

**Shipped:** the `sentinel-loop` vertical slice (commit ae44749 + nit-fix commit). Registered
`sentinel-loop` (kind: technique); home u02 Ex3 (guess-until-correct) `introduces`; ≥3 core
non-checkpoint reappearances `practices`d — project-01 M1 (`while choice != "q"`), u07 Ex12 (double
threshold until > champion), u10 Ex14 "Play Until Happy" (promoted stretch→core). Spotlights + markers
per design §6; catalog row (`while-loop`, `comparison`) + regenerated patterns.md; u02 teacher-notes
(in-class home + card-flip unplugged trace). u10 stretch preserved (Ex13 + new Ex15 "Pet Talent Show").

**Verification (kernel env):** all 3 pattern checks + concept-scan/manifest/coverage/prereq/stretch/
structure/hygiene/cell-lint/noexec PASS book1; exec-solutions (u10) + exec-lessons (u02) PASS; Book 2
zero-diff + all checks PASS; pytest 44 passed (test_patterns) / 446 `-k 'not exec'`; ruff clean;
patterns.pdf builds (16 KB). No scanner-derived `practices` needed (sentinel-loop uses only
while-loop/comparison already in those units' unions).

**Gates:** content-review 4-way CONSENSUS ([self]/[sol] APPROVE; [glm]/[fable] APPROVE WITH NITS; nits
fixed/dispositioned above).

**Deviation:** u10 solutions authored inline (the Codex solutions session was unreliable under
environment memory pressure — the statement-side Codex job looped in verification and was cancelled
after completing its deliverables); mitigated by the gate's 4-way blind-solve of the marked loci.

### PR-3 = Phase C (running-total slice) — 2026-09-18

**Shipped:** the `running-total` slice. Home u04 (new in-class Ex8 "Running total: add the round scores",
while-based, no list); core reappearances u05 Ex7 (reuse), u07 Ex4 (reuse), u09 (new Ex13 "Sum the saved
scores" read-and-sum). Scanner-derived `practices` on u09: `accumulator` + `arithmetic` (General Rule).
Spotlights + markers; catalog row (`accumulator`, `arithmetic`) + regenerated patterns.md; u04
teacher-notes (in-class home + finger-count unplugged trace).

**Verification (kernel env):** all concept/pattern/notebook checks PASS book1 (u04/u05/u07/u09);
exec-solutions u04+u09 + exec-lessons u04 PASS; Book 2 no regression; pytest 44 / 495 full; ruff
(enforced scope) clean; patterns.pdf builds. Full slice authored by a Codex session (statements/
solutions via internal fresh sub-sessions).

**Gates:** content-review 4-way CONSENSUS ([self]/[sol]/[glm]/[fable]; nits fixed above — notably the
u04 home relocated in-class, establishing the in-class-home precedent for D–H).

### PR-4 = Phase D (count-by-condition slice) — 2026-09-18

**Shipped:** the `count-by-condition` slice. Home u04 (new in-class Ex9 "Count the correct answers",
while-based, no list); core reappearances u06 Ex12 "Count the vowels" (new), u07 Ex5 (reuse), u08 Ex5
"Count the Words" (reuse — the **tally-by-key** count-per-group variation, named in the catalog).
No scanner-derived `practices` needed. Spotlights + markers; catalog row + regenerated patterns.md; u04
teacher-notes (in-class home + hand-raise trace); u06 teacher-notes place Ex12 in Lesson 2. u04
renumbered (count home = Ex9; homework → Ex10–12); u06 count-vowels = Ex12 before its Challenges.

**Verification (kernel env):** all concept/pattern/notebook checks PASS book1 (u04/u06/u07/u08);
exec-solutions u04+u06 + exec-lessons u04 PASS; Book 2 no regression; pytest 44; ruff clean; patterns.pdf
builds. Full slice authored by a single Codex session in one clean pass.

**Gates:** content-review 4-way CONSENSUS ([self]/[glm]/[fable] APPROVE-WITH-NITS; [sol] REJECT→APPROVE
after the u06 Ex12 pacing fix). Lesson folded into D–H: new core exercises must be entered in the unit's
teacher-notes pacing/allocation, and teacher-notes exercise-number references must be updated on renumber.

### PR-5 = Phase E (transform-each slice) — 2026-09-18

**Shipped:** the `transform-each` slice. Home u06 (new in-class Ex13 "Do the same to each character" —
builds a NEW STRING, no list); core reappearances u07 Ex6 (reuse), u08 Ex10 (reuse), u09 Ex3 line→int
(reuse). No scanner-derived `practices`. Spotlights + markers; catalog row (`for-loop`, `string-methods`)
+ regenerated patterns.md; u06 teacher-notes pace Ex13 in Lesson 3 (rides the Caesar `encode` per-char
rebuild).

**Verification (kernel env):** all concept/pattern/notebook checks PASS book1 (u06/u07/u08/u09);
exec-solutions u06 + exec-lessons u06 PASS; Book 2 no regression; pytest 44; ruff clean; patterns.pdf
builds. Full slice authored by a single Codex session.

**Gates:** content-review 4-way CONSENSUS ([self]/[glm] APPROVE; [fable] APPROVE-WITH-NITS; [sol]
REJECT→APPROVE). Lesson folded into F–H: pace a new home in the lesson that teaches its enablers (not
just "the first lesson"). [sol]'s round-1 byte-stability REJECT was a review-criterion misread, resolved
by clarifying "byte-stable" = committed patterns.md == generator output (patterns-doc-check PASS).

### PR-6 = Phase F (linear-search slice) — 2026-09-18

**Shipped:** the `linear-search` slice (heaviest: 4 units + a promotion + a stretch replacement). Home u06
(new in-class Ex14 scan+`break`, paced Lesson 2 off the `range(26)` scan); core reappearances u07 Ex14
(new loop+break), u08 Ex15 (PROMOTE Challenge-1 "Reverse Lookup" → core + break; dict value→key one-by-one
CT contrast), u09 Ex14 (new find-in-file). Scanner-derived `practices`: `break-statement` on
u06/u07/u08/u09 + `comparison` on u09 (find-in-file `==`) — all closure-clean, General Rule. u08 stretch
preserved (Merge + new "Flip the Phrasebook"). Catalog row (`for-loop`, `break-statement`, `in-operator`)
+ regenerated patterns.md; teacher-notes pacing for all 4 units.

**Verification (kernel env):** all concept/pattern/notebook checks PASS book1 (u06/u07/u08/u09);
exec-solutions all 4 units + exec-lessons u06 PASS; Book 2 no regression; pytest 44; ruff clean;
patterns.pdf builds. Full slice authored by a single Codex session.

**Gates:** content-review 4-way CONSENSUS ([self]/[sol] APPROVE; [glm]/[fable] APPROVE-WITH-NITS, nits
fixed/dispositioned). **Phase-G watch:** `comparison` is already on u09 — Phase G (find-extreme best-so-far)
must NOT double-add it.

### PR-7 = Phase G (find-extreme slice) — 2026-09-18

**Shipped:** the `find-extreme` slice — "keep the best so far while scanning, and remember WHO." Home u07
(new in-class Ex15 "Champion by name": parallel names+scores, keep best_name+best_score); core
reappearances u08 Ex6 (reuse best_word/best_count), u09 (new best-so-far, scans without `max()`), u10 Ex13
"Happiest Pet" (PROMOTE stretch→core + `best_pet`). **No new scanner-derived practices** — u09's
`comparison` was already added in Phase F and was NOT double-added (Phase-F watch honored). u10 stretch
preserved (Ex13 promoted; new Ex16 "Pet-Care List" Challenge added). Catalog row (`list-loop`,
`comparison`) + regenerated patterns.md; teacher-notes pacing for all 4 units.

**Verification (kernel env):** all concept/pattern/notebook checks PASS book1 (u07/u08/u09/u10);
exec-solutions u07/u09/u10 + exec-lessons u07 PASS; Book 2 no regression; pytest 44/495; ruff clean;
patterns.pdf builds. Full slice authored by a single Codex session (cancelled after deliverables complete
during a self-review loop; verified inline).

**Gates:** content-review 4-way CONSENSUS ([self]/[sol] APPROVE; [glm]/[fable] APPROVE-WITH-NITS). u07 Ex15
in-class placement WONTFIX (in-class header + teacher-notes pacing, [sol]-validated).

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
| running-total | u04 (home) | *new* "Running total: add the round scores" (`while`-based, no list) | new core | →new | accumulator (u04 co-intro), arithmetic (u02) | C |
| running-total | u05 | H "Exercise 7" `total_card_borders(n)` | core | reuse | — | C |
| running-total | u07 | H "Exercise 4 / Total and Average" | core | reuse | — | C |
| running-total | u09 | *new* "Sum the saved scores" (read-and-sum) | new core | →new | accumulator, arithmetic (both scanner-derived `practices` on u09), file-read (u09) | C |
| count-by-condition | u04 (home) | *new/adapt* "Count the correct answers" (`while`-based, no list) | new core | →new | comparison (u02), if (u02) | D |
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
| filter-into-list | u08 | *new* "Keep only the long words" (Exercise 16) | new core | →new | list-append, comparison, builtin-functions (`len`, scanner-derived on u08) | H |
| filter-into-list | u09 | *new* "Load only the high scores" | new core | →new | list-append, comparison, file-read | H |
| filter-into-list | u10 | *new* "List the happy pets" | new core | →new | list-append, comparison | H |
| sentinel-loop | u02 (home) | H "Exercise 3" while-until-guessed game | core | reuse-as-home | while (u02), comparison (u02) | B |
| sentinel-loop | project-01 | M1 `while choice != "q"` menu | core | reuse | — | B |
| sentinel-loop | u07 | H "Exercise 12: Double the Qualifying Threshold" (`while`, true sentinel) | core | reuse | — | B |
| sentinel-loop | u10 | H "Exercise 14: Play Until Happy" (`while happiness<10`) | **stretch** | →promote | — | B (**+1 u10 stretch replacement**) |

**Resulting per-unit core count (projected, informative — not a cap):**

Stretch column = **Challenge-exercise count** (each = a `stretch`-tagged heading/prompt cell + its
`stretch`-tagged code cell, so ≥2 Challenges ⇒ ≥2 tagged cells, always above the notebooks.py:538 CI floor
of ≥2 cells).

| unit | baseline core | +new core | resulting core | Challenge exercises after (promote −1, replace +1) |
|---|---|---|---|---|
| u02 | 8 | 0 (sentinel home = reuse Ex3) | 8 | 2 (unchanged) |
| u04 | 10 | +2 (running-total + count homes, `while`-based, no list) | 12 | 2 (unchanged) |
| u05 | 11 | 0 (reuse Ex7) | 11 | 2 (unchanged) |
| u06 | 11 | +2 (count-matches new; linear-search & transform-each homes) | 13 | 2 (unchanged) |
| u07 | 13 | +3 (find-extreme home, filter home, loop+break) | 16 | 2 (unchanged) |
| u08 | 14 | +2 (reverse-lookup promote→core Ex15, filter new Ex16) | 16 | 2 − 1 (Ch1) + 1 (repl) = 2 |
| u09 | 12 | +4 (read-and-sum, best-so-far, find-in-file, filter — all new) | 16 | 2 (unchanged) |
| u10 | 12 | +3 (Ex13 promote, Ex14 promote, filter new) | 15 | 2 − 2 (Ex13+Ex14) + 2 (repl) = 2 |

Every pattern reaches **≥3 core non-checkpoint reappearances** (home excluded): running-total u05/u07/u09;
count-by-condition u06/u07/u08; find-extreme u08/u09/u10; linear-search u07/u08/u09; transform-each
u07/u08/u09; filter-into-list u08/u09/u10; sentinel-loop project-01/u07/u10. Every touched unit keeps
≥2 Challenge exercises (≥2 tagged cells) at every merge. Scanner-derived `practices` additions (exact
registry ids, all closure-clean, under the General Rule): `break-statement` (intro u04) →
**u06/u07/u08/u09**; `accumulator` (u04) + `arithmetic` (u02) → u09; `comparison` (u02) → u09;
`builtin-functions` (u07) → u08 (filter `len()`).
