# Plan 069 — Book 1b foundation: registry, fastforward tooling, scaffolding, and U01 template

**Origin:** author request (2026-09-21): "work on a book1b, a different version of book 1 with the same
scope of content coverage … organized around concepts … weaken the verbose story, and focus on the
language concepts with real problem solving practices in math, simple algo or other area of middle
student's interest." Follow-ups: fastforward concepts before they are taught to make examples real;
draw from math / simple algo / turtle / other; exercises "mini cp and leetcode style but with simple
question backgrounds"; "no budget cap for # of exercises."
**Design:** `docs/designs/004-book1b-concept-first.md`.

## Motivation

Book 1b is a concept-first, story-light Year-1 edition covering the **same 62 concepts** as Book 1,
authored fresh with mini-CP / LeetCode-style problems.
This plan lays the foundation and proves the whole pipeline end-to-end:
the three book-aware tooling changes fastforward needs, the `book1b/` scaffolding, and **U01 authored
completely** as the template every later unit follows.
Units U02–U13, the checkpoints, and the end-of-book Algorithm Challenge land in follow-on content
plans (070+), each adding its own coverage-map entry as it ships.

## Design decisions this plan implements (from design 004)

- **Variant registry:** `book1b` registers with `variant_of: book1`, `prereq_policy: fastforward`,
  `buildout: true`, `concept_minimum: 40`, `lesson_budget: [30, 60]`, `depends_on: []` (self-contained).
- **Full catalog up front, incremental coverage-map:** `book1b/curriculum/concepts.yaml` is identical
  to Book 1's 62-concept catalog; `coverage-map.yaml` lists only authored entries (this plan: U01).
- **Fastforward:** `requires` strict, `practices`/**unit** content may reach forward; checkpoint and
  project content stay strict.
- **Spine fix (plan review):** `import-statement` is introduced in **U06** (turtle — `import turtle` is
  its natural motivation), not U08; U08 introduces only `random-module` with `requires: [import-statement]`.
  `comparison` is introduced in **U02** (even/odd needs `n % 2 == 0`), not U03.

## Tooling changes (dispatch to `codex:codex-rescue`, GPT-5.6-sol, per the agent-dispatch table)

All relaxations are **book-scoped by an EXPLICIT config flag** — Book 1 and Book 2 carry no such flag
and are strict by default. Regression is proven by **mutation tests** (below), not merely by the
existing suite staying green.

**A. `tools/books.py`**
- Read optional `variant_of` (str), `prereq_policy` (str), and `buildout` (bool).
- Add `is_buildout(root, book) -> bool` reading the **explicit** `buildout` flag (default False). Do
  NOT derive it from "is everything introduced" — that predicate is self-referential and would disable
  the very checks it gates (plan-review [sol] blocker 2). `concept_minimum`/`lesson_budget` already honored.

**B. `tools/curriculum.py`**
- `global_concept_uniqueness_findings`: skip id collisions between a book and its `variant_of` target
  (both directions); **assert the variant's `concepts.yaml` is content-identical to its parent's**
  (new finding if they diverge).
- `introduction_findings`: always enforce "introduced at most once"; enforce "every catalog concept
  introduced" only when `not is_buildout(root, book)`.
- `prereq_findings`: when `prereq_policy == "fastforward"`, validate closure over `requires` only (drop
  `practices` from the ordering check). `requires` stays strict. `checkpoint_findings` is **untouched**.
- `lesson_budget_findings`: enforce the *upper* bound always; enforce the *lower* bound only when
  `not is_buildout(root, book)`.

**C. `tools/concept_scan.py`**
- For a `prereq_policy == "fastforward"` book, apply the whole-catalog allowance (`union |= registered`)
  **only when `entry["kind"] == "unit"`**. Checkpoints and projects keep the strict per-entry set
  ([sol] blocker 3 — otherwise a checkpoint could use an unintroduced concept undetected). The
  untaught-*method* check runs for every entry. Book 1 keeps its per-unit set.

**D. Build & registry integration** (without these, a partial Book 1b fails ci-local immediately —
[sol]/[fable] blocker):
- `scripts/ci-local.sh`: the registry assertion (`ci-local.sh:15`, currently `["book1","book2"]`)
  accepts `book1b`; add a Book 1b invocation block mirroring the Book 1 curriculum + notebook-execution
  + hygiene + manifest steps **minus** the Book-1-only pattern checks; build Book 1b PDFs
  (`scripts/build-pdf.sh` gains a `book1b` path if needed).
- `scripts/pre-merge-guard.sh`: the collision loop (`pre-merge-guard.sh:77`) iterates `book1b` too.
- `tests/test_books.py`: the two-book registry assertion (`test_books.py:12`) is updated to include `book1b`.

**Book 1b ci-local check matrix** (what runs for `book1b`, all via `python -m tools.cli --book book1b <check>`):
concepts-schema, coverage/map-schema, uniqueness (variant-exempt), introduction (buildout-relaxed),
prereq (fastforward), lesson-budget (buildout-relaxed lower), practice, checkpoint, syllabus,
concept-scan (unit-fastforward), manifest, notebook-execution, notebook-hygiene, stretch, PDF build.
**Not run:** pattern-marker / technique-spiral / patterns-doc (hard-gated to `book1`).

**Tests** (`tests/`): fixture roots for a variant pair, a fastforward book, and a buildout book, plus
**mutation tests** — deleting an introduction from a strict (non-buildout) fixture still fails
`introduction_findings`; deleting enough lessons still fails `lesson_budget_findings`; the same deletions
in a `buildout: true` fixture do NOT fail. `syllabus_findings` needs no code change (matches only
pipe-delimited rows) — but Book 1b's `syllabus.md` lists the planned-unit roadmap as **prose, not a
table** (authoring rule, Phase B).

## Scaffolding (`book1b/`)

Mirrors design 000 §1 / Book 1's layout:
```
book1b/
├── syllabus.md                 # arc table (shipped entries) + roadmap prose (planned units)
├── curriculum/
│   ├── concepts.yaml           # full 62-concept catalog, identical to book1
│   └── coverage-map.yaml       # U01 entry only (grows per plan)
├── units/unit-01-output-and-variables/
│   ├── manifest.yaml
│   ├── lesson.ipynb
│   ├── exercises.ipynb
│   ├── solutions.ipynb
│   ├── teacher-notes.md
│   └── assets/                 # seeded generators only if a dataset is needed
├── checkpoints/                # (empty until a checkpoint plan)
├── projects/                   # (empty until the Algorithm Challenge plan)
├── reference/                  # concept-index stub
├── docs/                       # learner-facing stub
└── build/                      # gitignored
```
`books.yaml` gains the `book1b` entry. `.gitignore` covers `book1b/build/` (as for Book 1).

## U01 — Output & Variables (the template unit)

Introduces: run-program, print, comment, string-literal, variable, naming, input, string-concat,
f-string, error-messages. Requires: none. `lessons: 3` (matches Book 1 U01). Fastforward is available
but U01 needs little of it.

- **lesson.ipynb** opens with a concrete problem ("print a tidy fact sheet the computer fills in from a
  few values"), teaches each concept on a short worked-example ladder (minimal → one twist → realistic),
  and stays story-light. The opening cell poses a genuine problem with a visible payoff, never concept
  exposition (design §6 engagement criterion).
- **exercises.ipynb** — mini-CP / LeetCode style, **volume favored**: each exercise has a simple
  background, a precise spec, and ≥1 worked sample (input → expected output). Backgrounds from math,
  labels, and formatting. ≥2 `stretch` ("Challenge") exercises; core never depends on them. NO solutions,
  no executed outputs.
- **solutions.ipynb** — runs top-to-bottom clean with fixed seeds, using the **pre-function form** (U01
  is before U07/`def-function`, design §7): each exercise is "given these values, produce this exact
  output", `input()` is replaced by fixed sample values, and the solution `assert`s the assembled
  string/number (e.g. `assert fact_sheet == "…"`). Several cases per exercise (a content-gate rule — the
  CI floor is only ≥3 assert-bearing cells notebook-wide, design §6). No `input()` in executable cells
  (prompt-only forms tagged `no-exec`, per design 003 where applicable).
- **teacher-notes.md** — goals, 60–90 min pacing, the opening problem, common mistakes, discussion
  prompts, differentiation, and a **core-set vs. extra-practice partition** of the exercise bank so a
  lesson stays 60–90 min even though the bank is large (design §7; the exercise-volume + lean-early-units
  balance).
- **manifest.yaml** — `introduces`/`requires`/`practices` matching the coverage-map entry; provenance
  original; blueprint version.

**Dispatch (per AGENTS.md agent-dispatch table):** lesson + exercise STATEMENTS via `codex:codex-rescue`
(GPT-5.6-sol); SOLUTIONS via a SEPARATE fresh `codex:codex-rescue` session that does not read the
statements' outline; teacher-notes inline. Cross-model verification is the content gate.

## Phases

### Phase A — book-aware tooling + build/registry integration + tests
`tools/books.py`, `tools/curriculum.py`, `tools/concept_scan.py` (relaxations A–C);
`scripts/ci-local.sh`, `scripts/pre-merge-guard.sh`, `scripts/build-pdf.sh`, `tests/test_books.py`
(integration D); `tests/` fixtures + new cases + **mutation tests**.
Verification: `pytest` (new + mutation cases pass; full existing suite green — Book 1/Book 2 unchanged);
`bash scripts/ci-local.sh` still green on the current two-book repo before any book1b/ content exists
(registry now *accepts* book1b but book1b is absent, so its block is a no-op / clean SKIP).

### Phase B — registry + `book1b/` scaffolding + catalog + syllabus + U01 coverage-map entry
`books.yaml` (book1b entry with `buildout: true`), `book1b/` tree, `concepts.yaml` (identical to Book 1),
`coverage-map.yaml` (U01, `lessons: 3`), `syllabus.md` (table = shipped entries; roadmap of planned
units + the Algorithm Challenge as **prose**), `reference/`+`docs/` stubs, `.gitignore` (`book1b/build/`).
Verification: `python -m tools.cli --book book1b <check>` GREEN for each curriculum check (concepts/map
schema, uniqueness-exempt, introduction buildout-relaxed, prereq-fastforward, lesson-budget, practice,
checkpoint, syllabus).

### Phase C — U01 authored end-to-end
manifest + lesson + exercises + solutions + teacher-notes (+ seeded assets if needed), via the dispatch above.

### Phase V — verification
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN across Book 1, Book 2, and Book 1b
  (registry+lint, unit tests, notebook execution + hygiene, manifest/prereq/coverage/stretch, PDF build,
  pre-merge guard). No false SKIP.
- U01 `solutions.ipynb` executes top-to-bottom clean; every exercise's asserts pass; `exercises.ipynb`
  is solution-free with no executed outputs; ≥2 `stretch` cells present; opening cell is a problem, not drill.
- Scope allowlist: `git diff --name-only $(git merge-base HEAD main)..HEAD` = this plan + design 004 +
  `tools/{books,curriculum,concept_scan}.py` + `scripts/{ci-local,pre-merge-guard,build-pdf}.sh` +
  `tests/` additions + `books.yaml` + `.gitignore` + the `book1b/` tree.

## Out of scope

- **U02–U13 content, the checkpoints, and the Algorithm Challenge project** — follow-on plans 070+.
  This plan authors only U01 (plus all scaffolding and tooling), so the "capstone practices everything"
  coverage guarantee (design §6) activates only when the Algorithm Challenge lands; Book 1b is
  legitimately in buildout until then.
- **`docs/architecture/decisions.md` ADR stub** — governance-locked, human-reviewed; deferred unless the
  user asks for it inline (design §9).
- No changes to Book 1 or Book 2 content or to their strict policies.
- Not an erratum (new content), so no `ERRATA.md` entry.
- **Verification phase:** Phase V is the named verification phase (U01 is a unit → required).

## Plan Review

### Round 1 (2026-09-21) — [self] inline; [sol] gpt-5.6-sol; [glm] opencode; [fable] Fable 5 (dispatched parallel).

#### [self] (2026-09-21)
**APPROVE.** I verified every tooling integration point against the actual source before writing the plan:
- `curriculum.py` `global_concept_uniqueness_findings` iterates all registered books and flags any id in
  >1 book — so book1b (a full 62-id catalog copy) needs the `variant_of` exemption; confirmed.
- `referenced_concepts_findings` needs no change (book1b `own`=62, `depends_on: []` ⇒ empty baseline;
  introduces ⊆ own, requires/practices ⊆ own — existence holds under fastforward).
- `introduction_findings` "never introduced" would fail a buildout coverage-map ⇒ gate behind
  `is_complete_book`; "introduced twice" stays.
- `prereq_findings` currently rejects requires|practices before introduction ⇒ fastforward drops
  practices, keeps requires + (separately) checkpoint alignment strict.
- `lesson_budget_findings` sums entry lessons ⇒ a buildout book fails the lower bound ⇒ gate the lower
  bound behind `is_complete_book` (caught in self-review, folded).
- `concept_scan.py` per-entry `union` + `gaps = used - union` ⇒ fastforward sets `union |= registered`;
  untaught-method net retained.
- `syllabus_findings` matches only pipe-delimited rows ⇒ roadmap must be prose (folded as an authoring rule).
Spine closure over `requires` is satisfiable in order (checked all 13 units: e.g. U02 requires ⊆ U01;
U05 requires while-loop/accumulator/loop-counter ⊆ U04; U13 requires def/params/return ⊆ U07). U01
requires nothing, so it is authorable immediately. Phase V is the named verification phase (U01 is a
unit). Book 1 and Book 2 stay strict/complete, so all relaxations are inert for them (regression test
mandated in Phase A). No open blockers.
**[self] correction (round 1):** my "checked all 13 units" was wrong on U06 — `import turtle` makes
`import-statement` a *core* U06 dependency, not an incidental fastforward. Fixed (import-statement→U06).

#### [sol] round 1 (2026-09-21) — gpt-5.6-sol, read-only. **REJECT.**
Four blockers + two nits, all FOLDED:
- B1 (ci-local integration): `ci-local.sh:15` registry `== ["book1","book2"]`, per-book invocations
  (27/45), PDF book1-only (61); `tests/test_books.py:12`; `pre-merge-guard.sh:77`; Phase B's bare
  `python -m tools.cli` needs `--book`+check (`cli.py:21`). → new Tooling section **D** + check matrix;
  Phase A/B/V + scope allowlist updated.
- B2 (`is_complete_book` circular — would disable the missing-introduction + lesson-lower checks, incl.
  for Book 1/2): → replaced with an **explicit** `buildout: true` flag + `is_buildout` helper +
  **mutation tests** proving strict books still fail on a deleted introduction / lessons.
- B3 (`union |= registered` breaks checkpoint content-alignment — `concept_scan` scans checkpoints):
  → the allowance now applies to **unit** entries only; checkpoints/projects strict (design §5/§6).
- B4 (U06 `import-statement` ordering) = [fable] B1 → folded.
- N5 verification phase present (Phase V) — confirmed. N6 (`notebooks.py` floor is notebook-wide, not
  per-exercise) → per-exercise rigor stated as a content-gate rule (design §6/§7).

#### [fable] round 1 (2026-09-21) — Fable 5, read-only. **REJECT** (would APPROVE on the fold).
Two blockers + nits, all FOLDED:
- B1 (U06 `import-statement`) → import-statement moved to U06; U08 = random-module requires it.
- B2 (ci-local.sh registry hard-fails + no book1b block; allowlist excluded it) → Tooling D + allowlist.
- Nits: comparison→U02 (even/odd needs `n%2==0`); pre-function mini-CP form for U01 (design §7);
  post-U13 checkpoint **mandatory** (§3/§6); turtle practice sites (U07 `draw_polygon`, U08 turtle
  random walk); §6 "three vs four checks" + pattern-checks inert-for-book1b; U11 background avoids
  untaught `join`; U01 `lessons: 3` + core/extra split; Algorithm Challenge in syllabus roadmap;
  lesson_budget upper tightened to 60; engagement criterion restated for book1b (§6).

#### [glm] round 1 — dispatched via `opencode:opencode-review` but WITHOUT the mandated
`--model volcengine-plan/glm-5.3` (an out-of-date AGENTS.md copy at dispatch time); its verdict does not
count toward consensus. Re-dispatched correctly in round 2.

### Round 2 (2026-09-21) — revised plan/design after folding all round-1 findings.
_(Awaiting [sol] / [glm] (volcengine-plan/glm-5.3) / [fable] on the revised commit.)_

## Content Review

_(4-way content-review gate — filled before PR.)_

## Post-Execution Report

_(Filled before shipping.)_
