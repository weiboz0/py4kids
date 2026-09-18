# Design 002 — Book 1 Algorithm-Pattern Thread

**Status:** proposed (brainstormed 2026-09-17; awaiting review → plan lifecycle)
**Scope:** Book 1 only (a cross-book pattern contract for Book 2 is explicitly out of scope here).

## 1. Motivation

Book 1 teaches concepts and (after plan 037) exercises each concept to real authoring depth. This
design adds the *next* layer: a small set of **named, reusable algorithm patterns** — the small jobs a
concept does — woven through the units as a first-class, CI-tracked thread.

Three intents, all from the author:
1. **Concept mastery through real jobs.** A concept "clicks" when the student sees it *do* something —
   a running total, counting matches, finding the biggest.
2. **Computational thinking.** Each pattern contrasts *how a human does it at-a-glance* vs. *how the
   computer must do it step-by-step* — the core "a program thinks differently than you" idea.
3. **Spaced, varied repetition.** Each pattern reappears in several later units, in different project
   contexts, to enforce learning through varied practice (the "spiral").

## 2. Scope & depth ceiling

- **Linear, single-pass patterns + gentle efficiency intuition** only: "one pass beats two," "stop
  early when you find it" (`break`/short-circuit as the first taste of doing less work).
- **NOT in Book 1** (these are Book 2's): big-O / formal complexity, sorting-algorithm internals,
  recursion, two-pointers, prefix sums, graph traversal, complete search. The computational-thinking
  framing stays qualitative ("step-by-step vs at-a-glance"), never asymptotic.
- Book 1 only. Book 2 may later grow its own pattern registry / a cross-book contract; not now.

## 3. The pattern catalog (7)

| id | name | home unit | computer-vs-human hook | requires_concepts | reappears (varied) |
|----|------|-----------|------------------------|-------------------|--------------------|
| `running-total` | Running total (accumulate) | unit-04 | a human eyeballs a sum; the computer adds one item at a time into a total | accumulator, arithmetic | u05 (as a function), u07 average, u08 sum-counts, u09 read-and-sum |
| `count-by-condition` | Counting by condition | unit-04 | count matches by checking each item once and bumping a counter | accumulator, if-statement, comparison | u06 count chars, u07 above-threshold, u08 tally |
| `find-extreme` | Find max / min (running best) | unit-07 | keep the "best so far" while scanning, not "see all at once" | list-loop, comparison | u08 most-common, u10 top pet, u05 biggest(a,b,c) |
| `linear-search` | Linear search + early stop | unit-06 | check items one by one; `break` when found = stop working early | for-loop / in-operator, break-statement | u07 is-in-board, u08 lookup, u09 find-in-file |
| `filter-into-list` | Filter into a new list | unit-07 | build a NEW list of only the items that pass a test | list-append, list-loop, if-statement | u08, u09, u06 keep-vowels |
| `transform-each` | Transform each (map) | unit-06 | apply the SAME step to every item, producing a new sequence | for-loop, string-methods / arithmetic | u08 translate-each, u07 adjust-scores, u03 per-shape |
| `loop-until` | Loop until a threshold | unit-02 | repeat until a condition flips; the computer re-checks the condition every pass | while-loop, comparison | u07 while, project-01, u04 |

Notes:
- **unit-01 hosts no patterns** (pre-loop); **unit-02 is lean** — it hosts only `loop-until`.
- **unit-05** is where several patterns are *packaged as functions* (`total(nums)`, `count_evens(nums)`,
  `biggest(a,b,c)`) — a natural reappearance context that also reinforces functions/return.
- `count-by-condition` and `find-extreme`/`linear-search` share DNA; they stay distinct because the
  student-facing "job" and the comp-thinking hook differ.

## 4. Tracking model (first-class — mirrors the concept model)

- **Registry:** `book1/curriculum/patterns.yaml` (sibling of `concepts.yaml`). Each entry:
  `id`, `name`, `description`, `hook` (the computer-vs-human line), `requires_concepts` (list).
  `patterns_version: 1`.
- **Tags:** every `manifest.yaml` and its matching `coverage-map.yaml` entry gain two optional lists:
  - `introduces_patterns:` — the pattern's single home unit.
  - `practices_patterns:` — each varied reappearance.
  Analogous to `introduces`/`practices` for concepts. `introduces_patterns ∩ practices_patterns` stays
  empty within an entry (a pattern is introduced OR practiced at a given entry, not both).
- **Reappearances reuse existing exercises where they already embody the pattern** (e.g. unit-07
  already sums/averages/finds-max; unit-08 already tallies) — such an exercise is *tagged + given a
  brief Spotlight framing*, not rewritten. Net-new exercises are authored only where a unit needs an
  appearance it lacks. This keeps the footprint bounded on top of the plan-037 growth.

## 5. CI enforcement (new checks in `tools/`, wired into `scripts/ci-local.sh`)

Mirrors plan 016's `concept-scan` promotion approach (ported into the `tools/` package + registered in
`tools/checks.py` + wired into ci-local; blocking; book-level).

- **`pattern-coverage`** (mirrors `coverage-check`): every registry pattern is `introduces_patterns`
  in **exactly one** unit (its home) and `practices_patterns` in **≥3** later pre-capstone entries (the
  enforced spiral); every tag references a known registry id; a pattern's home precedes all its
  reappearances.
- **`pattern-prereq`** (mirrors `prereq-check` / closure): a pattern may be tagged at an entry only if
  all its `requires_concepts` are introduced ≤ that entry.
- **`patterns-doc-check`**: the student catalog `book1/reference/patterns.md` lists every registry
  pattern (catalog ↔ registry in sync), so the human-readable and machine-readable views can't drift.
- **Manifest==map** for the new tag lists (extends the existing `manifest-check`).

**Embodiment is tag + reviewer-enforced, NOT AST-scanned.** A pattern is a *shape*, not a token, so a
scanner can't reliably verify an exercise truly embodies a tagged pattern (unlike `concept-scan` for
concept usage). CI enforces the metadata spiral + closure + catalog sync; the **4-way content-review
gate's blind-solve** confirms each tagged exercise genuinely demonstrates its pattern. (No fragile
`pattern-scan` heuristic — deliberately rejected to avoid MANUAL_ONLY-style false-positive churn.)

**Spiral parameter N = 3 reappearances** (≥4 total appearances per pattern incl. home). Encoded as the
`pattern-coverage` threshold; per-pattern may exceed it.

## 6. Student-facing form

- **Pattern Spotlight cell** (recurring): a short markdown cell at each host/reappearance point that
  names the pattern, states the computer-vs-human hook + the gentle-efficiency note, and points to the
  catalog. At the home unit it introduces; at reappearances it's a one-line "you've seen this pattern —
  here it is again in a new job."
- **Exercises**: the pattern's authoring exercise(s), in the unit's project hook. New where needed;
  otherwise an existing exercise re-framed under a Spotlight.
- **Catalog**: `book1/reference/patterns.md` — the 7 patterns, each with its hook, its enabling
  concepts, and "where you'll meet it" (home + reappearances). The one place a student can see the
  whole pattern vocabulary.

## 7. Footprint & pacing

- Concentrated in units **04, 07, 08** (pattern-rich), with reappearances across **02, 03, 05, 06, 09,
  10** and **project-01**. Unit-01 untouched; unit-02 gets only `loop-until` (lean rule preserved).
- Estimated **+12–20 net-new exercises** (the range reflects how many reappearances land on existing
  exercises via tag+Spotlight vs. net-new). Each touched unit keeps its ≤16-core ceiling and its
  multi-lesson pacing budget; Spotlight cells are short; ≥1 appearance of each pattern sits on an
  in-class path.
- Stretch/`stretch` rules unchanged; patterns are core (a pattern's spiral must not depend on stretch).

## 8. Verification (named phase — required)

Ships content **and** tooling, so the plan carries a named verification phase: `ci-local` ALL GREEN
incl. the new `pattern-coverage`/`pattern-prereq`/`patterns-doc-check`; pytest for the new checks
(real-book passes; a one-fault fixture fails; closure/spiral fixtures); notebook exec + hygiene + the
existing concept checks still green; PDF build; pre-merge guard. Proficiency/embodiment is confirmed at
the content gate (reviewers solve each pattern exercise blind and confirm it demonstrates the pattern).

## 9. Rollout

Design → **plan (next free number)** → 4-way plan-review gate → phased implementation → 4-way
content-review gate → PR(s) → merge, per AGENTS.md. Dispatch:
- **Tooling** (`patterns.yaml` schema loader, the three checks, tests, ci-local wiring) → Codex
  (GPT-5.6-sol), like plan 016.
- **Content** (Spotlight cells, exercises, tagging, catalog) → Codex statements + solutions in separate
  sessions.
Likely **phased PRs** (e.g. Term 1–2 patterns + tooling, then Term 3–4) to keep each content gate's
blind-solve tractable — decided at plan time.

## 10. Out of scope

- Book 2 patterns / a cross-book pattern registry contract (future).
- An AST `pattern-scan` heuristic (rejected in §5).
- Any big-O/complexity, sorting internals, or recursion (§2 ceiling).
- Re-opening plan-037 exercise coverage (this thread sits on top of it).

## 11. Decisions resolved during brainstorming (2026-09-17)

- Intent = mastery + computational-thinking + spaced varied repetition (all three).
- Depth ceiling = linear + gentle efficiency intuition (no big-O / sorting / recursion).
- Form = first-class tracked thread (registry + tags + CI), student-facing via Spotlight cells + catalog.
- Embodiment enforcement = tag + reviewer (no AST pattern-scan).
- Spiral N = ≥3 reappearances.
- Pattern set = the 7 in §3; unit-01 excluded, unit-02 lean.
