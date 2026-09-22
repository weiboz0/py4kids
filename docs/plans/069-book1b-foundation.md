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
the book-aware tooling changes fastforward needs (Tooling A–D), the `book1b/` scaffolding, and **U01 authored
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
[sol]/[fable]/[glm] blocker). These edits land in **Phase B together with the `books.yaml` change**, so
the registry test never asserts a book that does not yet exist ([sol]-r2 B1):
- `scripts/ci-local.sh`: the registry assertion (`ci-local.sh:15-18`) accepts the new exact registry;
  add a Book 1b invocation block mirroring the Book 1 curriculum + notebook + turtle + hygiene + manifest
  steps **minus** the Book-1-only pattern checks. The block is **existence-guarded (`[ -d book1b ]`)**
  because the CLI checks *fail closed* on a missing root (`notebooks.py:80-83`); before `book1b/` exists
  it is a labelled `SKIP (plan 069)`.
- **PDF build:** `scripts/build-pdf.sh` is already `--book`-generic; only its pattern-doc probe is
  book1-gated (`build-pdf.sh:22`), so ci-local invokes it for `book1b` unchanged (no build-pdf edit).
- `scripts/pre-merge-guard.sh`: the collision loop (`pre-merge-guard.sh:77`) iterates `book1b` too.
- `tests/test_books.py`: update the registry assertion (`test_books.py:12-18`) — **all** of ids,
  numbers, roots, and positional `depends_on`, in the pinned order **`["book1","book1b","book2"]`**,
  numbers **`[1,1,2]`** (book1b is Year 1, grouped with its sibling; book2 stays last so its
  `depends_on: [book1]` position is unaffected).
- `tests/test_tools.py`: extend the CI-contract test (`test_tools.py:1227`, which currently asserts only
  the Book 1 PDF invocation) to assert the Book 1b invocation block.

**Book 1b ci-local check matrix** — the **actual CLI check names** ([sol]-r2 B2 / [fable]-r2 / [glm]-r2),
each `python -m tools.cli --book book1b <name>` (both `--book` and a check name are required; `cli.py:21`).
`coverage-check` is a composite (concepts-schema → uniqueness → map-schema → lesson-budget → referenced →
introduction → practice → checkpoint → syllabus, per `coverage_findings`):
`coverage-check`, `prereq-check`, `concept-scan`, `manifest-check`, `structure-check`, `hygiene-check`,
`cell-lint`, `noexec-check`, `stretch-check`, `exec-solutions`, `exec-lessons`, `turtle-check`, + PDF build.
**Not run for book1b:** pattern-marker / technique-spiral / patterns-doc (hard-gated `if book != "book1"`;
`patterns.py:201,339`, `patterns_doc.py:163,177`).

**Tests** (`tests/`): fixture roots for a variant pair, a fastforward book, and a buildout book, plus
**mutation tests proving the relaxation is NARROW** ([sol]-r2 B3), not a disabled check:
- strict (unflagged) fixture: deleting an introduction still fails `introduction_findings`; deleting
  enough lessons still fails `lesson_budget_findings` (these are the existing `test_tools.py`
  never-introduced case ~1094/1130 and the `test_book2_tooling` lesson-budget case — must stay green).
- `buildout: true` fixture: those two deletions do NOT fail — **but** a *duplicate* introduction STILL
  fails, and exceeding the lesson *upper* bound STILL fails (relaxation is completeness/lower-bound only).
- fastforward scan boundary: an unlisted **detectable** concept is accepted in a **unit** entry but
  **rejected in a checkpoint AND in a project**, untaught-method detection still firing in all three.
- **fastforward prereq boundary** ([sol]-r3): in a fastforward fixture, a not-yet-introduced concept in a
  unit's **`requires`** STILL fails `prereq_findings`, while the **same** concept in **`practices`**
  PASSES — proving the new branch drops only `practices`, not both fields (`curriculum.py:227` currently
  checks `requires | practices` together, so an impl that exempts both must be caught here).
- uniqueness: the `variant_of` exemption applies **only** when an id's owner-set ⊆ {variant, parent} — a
  triple collision (id also defined by `book2`) STILL fails ([glm]-r1).
`syllabus_findings` needs no code change (matches only pipe-delimited rows) — Book 1b's `syllabus.md`
lists the planned-unit roadmap as **prose, not a table** (authoring rule, Phase B).

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
├── checkpoints/.gitkeep        # empty dir needs .gitkeep to survive git (book1/book2 convention)
├── projects/.gitkeep           # empty dir needs .gitkeep (else fail-closed dir checks break on clone)
├── reference/                  # concept-index stub
├── docs/                       # learner-facing stub
└── build/                      # gitignored
```
`books.yaml` gains the `book1b` entry (order `["book1","book1b","book2"]`).
**`.gitkeep`** placeholders in `checkpoints/` and `projects/` are mandatory: git does not track empty
dirs, so without them a fresh clone fails `test_book_roots_have_required_layout` and every fail-closed
dir check (`notebooks.py:100-105,116-122`), even though Phase V passes locally ([glm] blocker).
No `.gitignore` edit is needed — the unanchored `build/` / `*.pdf` patterns already cover
`book1b/build/` at any depth ([glm]); it is dropped from scope.

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
  is before U07/`def-function`, design §7). Each solution **mirrors the student's visible form** — the
  same separate `print` calls, never an untaught `"\n"`-joined string or multi-line join as the shown
  answer — and **asserts the produced output line by line** against the exact expected text (a 4-line
  card → 4 line asserts). A "repair the error" exercise shows the *directly repaired instruction*, with
  the assert added separately. **No `input()` in ANY solutions code cell** — `_solution_policy_findings`
  flags `input(` tag-blind (`notebooks.py:278-280`); real `input()` forms live only in markdown, as in
  Book 1 ([glm]-r1 nit 6). Per-line asserts are the pre-function reading of "assertion rigor" (design §7).
- **Notebook structure floors to pin for the fresh Codex session** ([glm]-r1 nit 7): `exercises.ipynb`
  has **≥6 `## Exercise N` headings** in the exact format (`notebooks.py:533-535`) and **no**
  "Solution"-like headings (`notebooks.py:500-513`); `solutions.ipynb` **mirrors every exercise heading**
  with code beneath it (`notebooks.py:560-579`).
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

**Phase-sequencing note ([sol]-r2 B1):** the registry change (`books.yaml`) and the registry-asserting
edits (`tests/test_books.py`, `tests/test_tools.py`, `scripts/ci-local.sh` registry line) must land in the
**same** phase, or the updated tests go red between phases. Phase A is therefore pure tooling with
**self-contained fixtures** (it never edits the real registry or the real registry tests); Phase B makes
the registry change and all registry-coupled edits together.

### Phase A — book-aware tooling + fixture tests (no real-registry edits)
`tools/books.py`, `tools/curriculum.py`, `tools/concept_scan.py` (relaxations A–C) + `tests/` **fixture**
roots (variant pair / fastforward / buildout) + new cases + the **narrow-scope mutation tests** (Tooling D).
Verification: `pytest` (new + mutation cases pass; **full existing suite green, Book 1/Book 2 unchanged** —
this is why Phase A touches no real registry or registry test); `bash scripts/ci-local.sh` still green on
the untouched two-book repo.

### Phase B — registry + integration edits + `book1b/` scaffolding + catalog + syllabus + U01 map entry
Together (so registry asserts stay green): `books.yaml` (book1b entry, `buildout: true`, order
`["book1","book1b","book2"]`); the integration-D edits (`ci-local.sh` registry + existence-guarded book1b
block, `pre-merge-guard.sh`, `tests/test_books.py`, `tests/test_tools.py` CI-contract); the `book1b/` tree
with `.gitkeep`s; `concepts.yaml` (content-identical to Book 1); `coverage-map.yaml` (U01, `lessons: 3`);
`syllabus.md` (table = shipped entries; roadmap of planned units + the Algorithm Challenge as **prose**);
`reference/`+`docs/` stubs.
Verification: `python -m tools.cli --book book1b coverage-check` and `... prereq-check` GREEN (these
composites exercise concepts/map schema, uniqueness-exempt, introduction buildout-relaxed, lesson-budget,
practice, checkpoint, syllabus, and fastforward ordering); `pytest` green (registry tests now expect the
three-book registry).

### Phase C — U01 authored end-to-end
manifest + lesson + exercises + solutions + teacher-notes (+ seeded assets if needed), via the dispatch above.

### Phase V — verification
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN across Book 1, Book 2, and Book 1b
  (registry+lint, unit tests, notebook execution + hygiene, manifest/prereq/coverage/stretch/turtle,
  PDF build, pre-merge guard). No false SKIP.
- U01 `solutions.ipynb` executes top-to-bottom clean; every exercise's asserts pass; `exercises.ipynb`
  is solution-free with no executed outputs; ≥2 `stretch` cells present; opening cell is a problem, not drill.
- Scope allowlist: `git diff --name-only $(git merge-base HEAD main)..HEAD` = this plan + design 004 +
  `tools/{books,curriculum,concept_scan}.py` + `scripts/{ci-local,pre-merge-guard}.sh` +
  `tests/{test_books,test_tools}.py` + new `tests/` fixtures + `books.yaml` + the `book1b/` tree
  (incl. `checkpoints/.gitkeep`, `projects/.gitkeep`). **No `.gitignore` / `build-pdf.sh` edit** (both no-ops).

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

**SUPERSEDED-TERMINOLOGY NOTE:** the round-1 `[self]` (and the round-1 `[sol]`/`[glm]` REJECTs) reason via
a derived `is_complete_book` predicate. That is **superseded** by the explicit `buildout: true` config flag
([sol]-r2 B2 / [glm]-r2) — a derived predicate is circular (it would disable the very check it gates). The
normative requirement is the explicit flag in the Tooling section; those historical entries stand as record.

### Round 2 (2026-09-21) — on commit 634cd14 (round-1 folds). [glm] on volcengine-plan/glm-5.3.

#### [fable] round 2 — **APPROVE WITH NITS.**
Both round-1 blockers resolved; all 8 round-1 nits confirmed present; mechanically re-verified the §3
table is a true 62-id partition. 8 new nits, ALL FOLDED: real CLI check names (coverage-check/prereq-check
composites); add turtle-check (+ structure/noexec/cell-lint) to the matrix; explicit `[ -d book1b ]` guard
+ `SKIP (plan 069)` label + pinned registry order; §11 "Tooling A–D" wording; carve turtle exercises out of
the §7 assert rule (verified by execution + turtle-check) and extend §8 to U06 + turtle practice sites;
U12 file concepts need a practice site like U13's (post-U13 checkpoint / U13 background); U02 sets the
fastforward-tagging convention (U01 needs little); add a round-2 [self].

#### [glm] round 2 (volcengine-plan/glm-5.3) — **APPROVE WITH NITS.**
Verified all four round-1 folds against the real code (integration sites, non-circular buildout flag,
unit-only scan, spine 62-once + order incl. U08 requires import-statement). 4 nits, ALL FOLDED: `.gitkeep`
in checkpoints/ + projects/ (git can't track empty dirs — else fresh-clone failure invisible to Phase V);
turtle-check (+ structure/noexec/cell-lint) in the matrix; `[ -d book1b ]` existence guard + pinned
registry order `["book1","book1b","book2"]` / numbers `[1,1,2]`; `.gitignore` item is a no-op (dropped);
AGENTS.md "two independently complete roots" needs the deferred human-governance update (§9).

#### [sol] round 2 — **REJECT** (round-1 B3/B4 resolved; approach validated; 3 integration/test blockers + 1 nit, ALL FOLDED).
- B1 (phase sequencing): Phase A edited `test_books.py` then required green, but Phase B adds book1b to
  `books.yaml` → test red between phases. → Phases re-sequenced: Phase A is pure tooling + **fixtures only**;
  Phase B lands the registry change + all registry-coupled edits together. Update ALL test_books assertions
  + exact order.
- B2 (matrix not executable CLI): → matrix rewritten with real CLI names; turtle-check added; CI-contract
  test (`test_tools.py:1227`) extended; corrected — build-pdf.sh is already generic (no edit).
- B3 (mutation tests too loose): → added narrow-scope cases (duplicate-intro still fails in buildout;
  lesson UPPER still fails in buildout; fastforward accepted in units, rejected in checkpoints AND projects,
  untaught-method still live).
- nit (stale `is_complete_book` in historical [self]): → superseded-terminology note added above.

#### Delayed [glm] round 1 (default model — does NOT count toward consensus) — surfaced 3 NEW valid items, FOLDED:
`.gitkeep` (= [glm]-r2 nit 1); solutions `input()` convention (no `input(` in any solutions code cell,
`notebooks.py:278-280`); U01 notebook floors (≥6 exercise headings, no Solution headings, solutions mirror
headings) + the uniqueness triple-collision test.

#### [self] round 2 (2026-09-21) — **APPROVE.**
Re-reviewed the revised plan against the code paths [sol]/[glm]/[fable] cited: phases re-sequenced so no
registry test is red between phases; check matrix uses real CLI names + turtle-check; mutation tests now
prove narrow scope (duplicate-intro / upper-bound still fail under buildout; scan boundary units-yes /
checkpoints+projects-no; triple-collision fails); `.gitkeep` + `input()`-in-markdown-only + notebook floors
pinned; buildout is the explicit flag (non-circular). No open [self] blockers.

### Round 3 (2026-09-21) — on commit af5992b. Re-dispatched [sol] only (the sole round-2 REJECT).

#### [sol] round 3 — **REJECT** (round-2 B1/B2, terminology, .gitkeep, input() all verified resolved;
one residual blocker):
- B3 residual: the mutation set proved buildout completeness/upper-bound + scan boundary + triple-collision,
  but did NOT mandate a test for the **fastforward prereq** relaxation — `prereq_findings`
  (`curriculum.py:227`) checks `requires | practices` together, and the plan adds a branch dropping only
  `practices`; the existing strict-fixture test (`test_tools.py:1198-1217`) can't detect an impl that
  exempts BOTH fields, and U01 can't cover it (U02 is the first forward-practice site). → **FOLDED:** added a
  fastforward-prereq-boundary mutation test (forward concept in `requires` still fails; same in `practices`
  passes).
[sol] round 3 explicitly re-verified B1 (no registry test red between phases; pinned order safe — no
monotonic/sorting assertion in test_books.py), B2 (all check spellings match `checks.py:26-44`;
build-pdf.sh generic; test_tools.py:1227 is the CI-contract test), and the .gitkeep / no-input() folds.

### Round 4 (2026-09-21) — on commit d89d064.

#### [sol] round 4 — **APPROVE.** B3 closed (the added test requires the forward `requires` case to fail
and the `practices` case to pass, catching an impl that exempts neither or both fields); all prior
round-2/round-3 blockers remain resolved; no other blocker.

### Plan-review outcome: **FULL 4-way consensus** — [self] APPROVE · [sol] APPROVE ·
[glm] (volcengine-plan/glm-5.3) APPROVE WITH NITS · [fable] APPROVE WITH NITS. No open blockers.
Four rounds: round 1 (2× REJECT) fixed the spine (import-statement→U06), the circular buildout predicate,
the checkpoint content-scan leak, and the ci-local/registry integration; round 2 ([sol] REJECT) fixed
phase sequencing, CLI-name accuracy, and narrow-scope mutation tests + the empty-dir/.gitkeep and
input()-convention traps; rounds 3–4 closed the fastforward-prereq mutation-test gap. Gate CLOSED → implementation.

## Content Review

Scope: U01 content (lesson/exercises/solutions/teacher-notes/manifest) + the tooling/scripts/tests from
Phases A–B (conventional code review, same roster). Commit c7ce111.

### Review 1 — [self] (2026-09-22)
- **Verdict**: APPROVE.
Blind-solved a sample of the 12 exercises from the statements alone and compared to solutions: Ex1
(Welcome Sign), Ex4 (`+` concat), Ex5 (f-string), Ex6/Ex12 (error-messages — unclosed quote / NameError),
Ex8 (the 4-line fact card). All specs give exact expected output + a worked sample, so each is
blind-solvable; solutions mirror all 12 headings, assert each (12/12 non-vacuous), and `exec-solutions`
passes, so the asserted outputs are correct. The 12 exercises cover all 10 introduced concepts; core
(1–6)/extra (7–10)/Challenge (11–12) partition keeps a lesson within 60–90 min. Lesson opens on a concrete
problem (fill a fact card), never concept drill (engagement law ✓). Zero-experience accessible: nothing
used beyond U01's introduces; `input()` appears only in markdown; no arithmetic/loops needed. Provenance
original. Tooling reviewed in Phase A/B (fixture + mutation tests green; Book 1/Book 2 unchanged; full
ci-local ALL GREEN across the three books). No open [self] findings.

### Review 1 — [fable] (2026-09-22) — **APPROVE WITH NITS** (no Must Fix). Blind-solved 12/12 exact match.
1. `[FIXED]` Ex12 broken line has two spaces → literal repair mismatches; and SyntaxError precedes NameError so "repair the first error" misleads. Should Fix. → one space + reworded to iterative "fix the error the traceback shows first, re-run, fix the next".
2. `[FIXED]` Students never author a variable (all prefilled). Should Fix. → added a core exercise where the student writes their own named variables + assignment.
3. `[FIXED]` CI-speak in student text; students never actually run `input()`. Should Fix. → de-jargoned lesson text + added a hands-on "try `input()` in a new cell with your teacher" guidance.
4. `[FIXED]` Undefined "traceback"/"operator"/"assignment". → defined on first use.
5. `[FIXED]` Solutions use untaught `\n`/multi-line as the shown answer; asserts one case. Should Fix. → solutions re-authored to mirror the student `print` form with per-line asserts (design §7 clarified).
6. `[FIXED]` Challenge 1 easier than core Ex8. Nice. → reworked to practice reassignment.
7. `[FIXED]` teacher-notes inaccuracies (core doesn't touch input/naming; no keyboard-card in core; forward TypeError). → teacher-notes rewritten to match the revised set.
8. `[FIXED]` Engagement "make it yours". Nice. → explicit make-it-yours step in the final build.
9. `[FIXED]` "no list/loop" untaught-noise in student text. Nice. → removed from student-facing text.

### Review 1 — [glm] (2026-09-22, volcengine-plan/glm-5.3) — **APPROVE WITH NITS**. Blind-solved 12/12; ci-local ALL GREEN.
1. `[FIXED]` Solutions Ex8/10/11 use untaught `\n`/multi-line as the visible path. Should Fix. → (same fix as [fable] 5).
2. `[FIXED]` Ex12 "first error" wording. Nice. → reworded.
3. `[FIXED]` Ex8 given values identical to lesson final build (verbatim retype). Nice. → varied the values.
4. `[FIXED]` Record the pre-function one-assert reading vs design §6. Nice. → design §7 now defines per-line asserts as the pre-function rigor; §6/§7 reconciled.
5. `[FIXED]` `curriculum.py` `ordered_fields` misnames the logic. Nice. → renamed `checked_fields` + comment.

### Review 1 — [sol] (2026-09-22, gpt-5.6-sol) — **REJECT**. Blind-solved 12/12 correct outputs; blockers on the assertion contract.
1. `[FIXED]` **Must Fix** — every exercise asserts one case; the design/plan "several cases per exercise" contract is unmet. → **Contract clarified** (design §7): for the pre-function form there is ONE deterministic fixed-input case, so rigor = asserting the expected output **line by line** (a 4-line card → 4 asserts); "several distinct input cases" is the FUNCTION-form rule (U07+). Both [fable] and [glm] endorsed this reading. Solutions re-authored to per-line asserts, satisfying it concretely.
2. `[FIXED]` Ex6 solution rewrites the instruction (`result = …`) instead of repairing it. Should Fix. → solutions now show the directly repaired instruction, assert separately.
3. `[FIXED]` teacher-notes overclaim (core touches all 10 / "keyboard-filled card") + no real `input()` practice. Should Fix. → teacher-notes corrected + hands-on `input()` guidance added.

### Content-review round 1 outcome: 3× APPROVE-WITH-NITS ([self]/[fable]/[glm]) + 1 REJECT ([sol], Must Fix on the assertion contract). All findings folded (notebooks re-authored + design §7 contract clarified + tooling rename + teacher-notes). Re-review round 2 dispatched.

### Round 2 (2026-09-22) — after folding all round-1 content findings.
_(Awaiting [sol] / [glm] (volcengine-plan/glm-5.3) / [fable] on the revised commit.)_

## Post-Execution Report

_(Filled before shipping.)_
