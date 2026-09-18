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
promotion precedent), plan 037 (the exercise depth this sits on + its ≤16-core/Phase-V thresholds).

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
  all at the 16-core ceiling) ships LAST.
- **Embodiment = tag + reviewer.** No AST `pattern-scan`. CI enforces the metadata spiral + markers +
  catalog sync; the 4-way content gate blind-solves each marked exercise against the design's embodiment
  definitions. Technique ids are silenced in `concept-scan` via the existing dynamic `never_flag`
  profile (no `MANUAL_ONLY` edit).
- **Markers:** every entry tagging a pattern id carries a `<!-- pattern: <id> -->` markdown cell in that
  entry's notebooks, mapped kind→notebook (unit home: `lesson.ipynb` + the exercise; unit reappearance:
  `exercises.ipynb` above the tagged exercise; project: `brief.ipynb`). Markers are HTML comments
  (dropped by nbconvert/pandoc; hygiene/PDF unaffected).
- **Ceiling & pacing (per design §7, verified):** target core counts u07=16, u08=16, u09=16, u10=15;
  every touched unit ≤16 core. Units 01 untouched; u02 gets one lean one-sentence Spotlight only. New
  exercises are core, non-stretch; each home is in-class; extra reps route to homework/More-Practice in
  teacher-notes; each home gets a 2-minute unplugged trace. Carry plan-037 Phase-V volume thresholds
  (>2× cells / >30% PDF pages / >25% wall-time = gate finding; 120 s per-cell exec).
- **Do not touch:** `introduces`/`requires` for regular concepts (only add technique tags); Book 2
  anything; governance files. Standing process: branch `feature/book1-algorithm-patterns`; no commits
  while a `[sol]` review is in flight; `GH_TOKEN=$(cat .gh-token)`; content SOLUTIONS in a separate
  fresh Codex session.

## Out of scope

- A separate `patterns.yaml`; an AST `pattern-scan`; big-O/sorting/recursion; Book 2 pattern growth;
  re-opening plan-037 coverage. A follow-up amends design 001 §2 once these ids ship (not here).

## Phases

Dispatch per AGENTS.md: tooling + the ledger → Codex (GPT-5.6-sol); Spotlight/exercise STATEMENTS →
Codex; SOLUTIONS → separate fresh Codex session; teacher-notes + metadata tags → inline.

### Phase A — Ledger + tooling foundation (tooling; ships PR-1, no pattern ids yet)

1. **Reuse ledger** (`docs/plans/047-…` appendix or `book1/curriculum/pattern-ledger.md`): the ~28-row
   table — per locus: `pattern, entry, exact exercise heading, core/stretch now, action
   (reuse-tag/promote/new), enabling concepts, resulting unit core count`. Must prove every touched unit
   ≤16 (u07=16, u08=16, u09=16, u10=15) and every pattern ≥3 core non-checkpoint reappearances. This is
   the acceptance artifact the design's §7 mandates; produced FIRST so all later phases build from real
   cells.
2. **`technique-spiral`** check in `tools/` (Book-1-scoped): each Book-1 `kind: technique` id is
   `introduces`d once + `practices`d in ≥3 pre-capstone non-checkpoint entries whose marked exercise is
   **core** (not stretch). Registered in `tools/checks.py`; wired into `ci-local`. Green on the empty
   Book-1 technique set (no patterns registered yet).
3. **`pattern-marker`** check: every technique tag on an entry has a matching `<!-- pattern: id -->`
   marker in the correct notebook (kind→notebook map, incl. `brief.ipynb`); unknown/duplicate ids fail;
   checkpoints must carry no pattern tag. Define exact cardinality/adjacency here.
4. **`patterns-doc-check`** + **catalog generator**: generate `book1/reference/patterns.md`'s
   "where you'll meet it" table from the map; check committed == generated; verify every registered
   technique id's name/hook/enabling-concepts present and each enabling concept introduced ≤ home; add
   the catalog to `scripts/build-pdf.sh` (pandoc, like `syllabus.md`).
5. **Tests:** pytest with discriminating fault fixtures — duplicate home; practice-before-home; only-two
   practices; checkpoint-only-third; stretch-only embodiment; unknown id; manifest/map mismatch; stale
   catalog; missing marker. Real book passes (empty technique set) + each fixture fails closed.
- **Acceptance (A):** `ci-local` ALL GREEN with the 3 checks active on the current (pattern-free) book;
  ledger proves ≤16 + ≥3 for all 7 patterns; catalog builds to PDF.

### Phases B–H — one vertical slice per pattern (content + tagging + catalog row)

Each slice, per the ledger, in the design's §3 order-of-safety. A slice = register the id in
`concepts.yaml`; tag its home (`introduces`) + its ≥3 reappearances (`practices`) in map+manifests; add
the `<!-- pattern: id -->` markers; author/adapt the Spotlight cells + exercises (reuse-tag / promote /
new per the ledger); add the catalog row; align teacher-notes (in-class home + unplugged trace). Each
slice keeps `ci-local` GREEN (technique-spiral satisfied for that id on merge).

- **Phase B — `sentinel-loop`** (home u02; reappearances project-01 M1, u07 Ex12/13, u10 Ex14 promote).
- **Phase C — `running-total`** (home u04; u05 Ex7, u07 Ex4, u09 read-and-sum new).
- **Phase D — `count-by-condition`** (home u04; u06 count-matches new, u07 Ex5, u08 tally-by-key).
- **Phase E — `transform-each`** (home u06; u07 Ex6, u08 Ex10, u09 Ex3).
- **Phase F — `linear-search`** (home u06 + break; u07 loop+break new, u08 reverse-lookup promote+break,
  u09 find-in-file new).
- **Phase G — `find-extreme`** (home u07 champion-by-name new; u08 Ex6, u09 best-so-far new, u10 Ex13
  promote + `best_pet`).
- **Phase H — `filter-into-list`** (home u07 new; u08/u09/u10 new) — **LAST** (touches the four
  ceiling units together; design's dual-marker lever if a unit would exceed 16, status-preserving).

Per-slice acceptance: the pattern's home+≥3 core reappearances embody the design's definition (content
gate confirms); markers present; catalog row generated-clean; unit ≤16 core; `ci-local` GREEN incl.
`technique-spiral`/`pattern-marker`/`patterns-doc-check`.

### Phase V — Verification (named, mandatory)

`uv run pytest -q` green (incl. the new check fixtures); `scripts/ci-local.sh` ALL GREEN incl.
`technique-spiral` + `pattern-marker` + `patterns-doc-check` + the inherited concept checks +
notebook exec/hygiene/cell-lint + PDF (incl. the catalog) + pre-merge guard. Volume budget recorded
(≤16 core/unit; the plan-037 thresholds). **Proficiency/embodiment (reviewer-enforced):** for each of
the 7 patterns, a reviewer confirms the home + ≥3 core non-checkpoint reappearances each embody the
design's definition, in varied contexts (data-type/packaging/twist axis recorded in the Spotlight), with
the home in-class.

**Acceptance criteria:** all 7 patterns registered + spiralled ≥3 core; ledger proves ≤16/unit; 3 new
checks green + fault-tested; catalog delivered in the PDF; `ci-local` ALL GREEN; `pre-merge-guard --pr`
OK; plan-review + (per-PR) content-review 4-way consensus. **Rollout:** phased PRs by pattern-group
(Phase A + B–E as PR-1..n; the `filter-into-list` slice last), each a complete vertical slice so `main`
stays green.

---

## Plan Review

_(4-way gate — [self] / [sol] / [glm] / [fable]. To be conducted before implementation.)_

## Content Review

_(4-way gate — pre-PR after implementation, per PR. Findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`.)_

## Post-Execution Report

_(Written before PR.)_
