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
  `concept_minimum: 40`, `lesson_budget: [30, 90]`, `depends_on: []` (self-contained).
- **Full catalog up front, incremental coverage-map:** `book1b/curriculum/concepts.yaml` is identical
  to Book 1's 62-concept catalog; `coverage-map.yaml` lists only authored entries (this plan: U01).
- **Fastforward:** `requires` strict, `practices`/content may reach forward, checkpoint alignment strict.

## Tooling changes (the three book-aware relaxations + one sync check)

All changes are **book-scoped by config** — Book 1 and Book 2 behavior is unchanged (verified by the
existing suite staying green).

1. `tools/books.py`: read optional `variant_of` (str), `prereq_policy` (str), and treat a book whose
   coverage-map introduces a strict subset of its catalog as "in buildout" (helper
   `is_complete_book(root, book) -> bool`: complete iff every catalog id is introduced). `concept_minimum`
   and `lesson_budget` are already config-honored.
2. `tools/curriculum.py`:
   - `global_concept_uniqueness_findings`: skip id collisions between a book and its `variant_of`
     target (both directions), and **assert the variant's `concepts.yaml` is byte-for-content identical
     to its parent's** (new finding if they diverge).
   - `introduction_findings`: always enforce "introduced at most once"; enforce "every catalog concept
     introduced" only when `is_complete_book` is true (Book 1 stays strict).
   - `prereq_findings`: when `prereq_policy == "fastforward"`, validate closure over `requires` only
     (drop `practices` from the ordering check). `requires` and checkpoint alignment stay strict.
3. `tools/concept_scan.py`: for a fastforward book, the allowed-concept set for a unit's content is the
   **whole catalog** (a fastforwarded concept is not "used-but-unlisted"). Book 1 keeps its per-unit set.

Each change ships with unit tests under `tests/` (fixture book roots: a variant pair, a fastforward
book, and a buildout book), plus a regression assertion that Book 1's checks are unchanged.

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
f-string, error-messages. Requires: none. Fastforward is available but U01 needs little of it.

- **lesson.ipynb** opens with a concrete problem ("print a tidy fact sheet the computer fills in from a
  few values"), teaches each concept on a short worked-example ladder (minimal → one twist → realistic),
  and stays story-light.
- **exercises.ipynb** — mini-CP / LeetCode style, **volume favored**: each exercise has a simple
  background, a precise spec, and ≥1 worked sample (input → expected output). Backgrounds from math,
  labels, and formatting. ≥2 `stretch` ("Challenge") exercises; core never depends on them. NO solutions,
  no executed outputs.
- **solutions.ipynb** — runs top-to-bottom clean with fixed seeds; every exercise's solution asserts
  ≥3 non-vacuous cases; no `input()` in executable cells (prompt-only forms tagged `no-exec`, per
  design 003's real-input convention where applicable).
- **teacher-notes.md** — goals, 60–90 min pacing, the opening problem, common mistakes, discussion
  prompts, differentiation.
- **manifest.yaml** — `introduces`/`requires`/`practices` matching the coverage-map entry; provenance
  original; blueprint version.

**Dispatch (per AGENTS.md agent-dispatch table):** lesson + exercise STATEMENTS via `codex:codex-rescue`
(GPT-5.6-sol); SOLUTIONS via a SEPARATE fresh `codex:codex-rescue` session that does not read the
statements' outline; teacher-notes inline. Cross-model verification is the content gate.

## Phases

### Phase A — book-aware tooling + tests
`tools/books.py`, `tools/curriculum.py`, `tools/concept_scan.py` + `tests/` fixtures and cases.
Verification: `pytest` (new cases pass; full existing suite green — Book 1/Book 2 unchanged).

### Phase B — registry + `book1b/` scaffolding + catalog + syllabus + U01 coverage-map entry
`books.yaml`, `book1b/` tree, `concepts.yaml` (identical to Book 1), `coverage-map.yaml` (U01),
`syllabus.md`, `reference/`+`docs/` stubs, `.gitignore`.
Verification: `python -m tools.cli` curriculum checks GREEN for `book1b` (schema, uniqueness-exempt,
introduction-in-buildout, prereq-fastforward, syllabus).

### Phase C — U01 authored end-to-end
manifest + lesson + exercises + solutions + teacher-notes (+ seeded assets if needed), via the dispatch above.

### Phase V — verification
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN across Book 1, Book 2, and Book 1b
  (registry+lint, unit tests, notebook execution + hygiene, manifest/prereq/coverage/stretch, PDF build,
  pre-merge guard). Any book1b check with no authored content prints no false SKIP.
- U01 `solutions.ipynb` executes top-to-bottom clean; every exercise's asserts pass; `exercises.ipynb`
  is solution-free with no executed outputs; ≥2 `stretch` cells present.
- Scope allowlist: `git diff --name-only $(git merge-base HEAD main)..HEAD` = this plan + design 004 +
  the three `tools/` files + `tests/` additions + `books.yaml` + `.gitignore` + the `book1b/` tree.

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

_(4-way plan-review gate — filled by the gate; consensus required before Phase A.)_

## Content Review

_(4-way content-review gate — filled before PR.)_

## Post-Execution Report

_(Filled before shipping.)_
