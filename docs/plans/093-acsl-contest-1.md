# Plan 093 — ACSL Contest 1: Number Systems, Recursive Functions, What Does This Program Do?

**Goal:** Ship the Contest 1 part of *Contest Python: ACSL*: one unit per Contest 1 category, then the Contest 1 practice checkpoint. This is the part students study before the first contest window (Oct 19, 2026 – Jan 10, 2027).

**Spec:** design 009 (D1–D5 and the roadmap row for 093). User decisions, 2026-09-29:
- "continue with plan 093 on autopilot and all other contest followed"
- the earlier decisions quoted in plan 092 (one book for every division, marked by level; organized by the contest season)

## Survey (2026-09-29, main at efb3866)

- **Existing book:** `acsl/` holds `unit-00-acsl-foundations`, which introduces `input-parse`, `str-split`, `tuple` and `complete-search`.
- **`season.yaml` Contest 1 units:**
  - Computer Number Systems — elementary, junior, intermediate, senior
  - Recursive Functions — junior, intermediate, senior
  - What Does This Program Do? – Branching — junior, intermediate, senior (the merged all-constructs unit, design 009 D3)
- **Shared concept ids** available via `peers`, with entries identical to `usaco-bronze`:
  - `base-conversion` (technique, number-theory)
  - `recursion` (feature, techniques)
  - `code-tracing` (technique, techniques)
- **Checkpoint rules:** 6–8 question headings (`tools/notebooks.py`), strict prerequisites (no borrowed tools), and a Grading section in the teacher notes. The ACSL format is short-answer questions plus exactly one programming problem.

## The entries (all under `acsl/`)

Every unit follows the Foundations conventions:
- a project-first hook cell and 3 lessons
- **at least 14 exercises**, mixing programming items (judged line-exact, with edge fixtures) and short-answer items (`**Answer:**` line and a top-level `verify` assert)
- a ladder tag plus a visible "_Division: X and above._" line on each heading
- at least 2 `stretch` Challenges
- only concepts from *Python by Projects*, Foundations, or earlier in this unit

| Entry | ACSL category | Divisions | Introduces | Content |
|---|---|---|---|---|
| `unit-01-computer-number-systems` | Computer Number Systems | elementary, junior, intermediate, senior | `base-conversion` | **Elementary section first:** binary, octal and hex place value; converting small numbers; counting in a base. Items tagged `acsl-elementary`, all short-answer. **Then Junior+:** conversions between bases 2/8/10/16 via place value and repeated division; the 2/8/16 grouping shortcut; arithmetic in a base (add, subtract); comparing values across bases. Python: `int(s, base)` and hand-written conversion loops (the loops are taught; the `int(s, base)` form only after the hand method). Programming items read numbers and bases. |
| `unit-02-recursive-functions` | Recursive Functions | junior, intermediate, senior | `recursion` | ACSL style: evaluating a recursively defined *f(x)* by hand, laid out as a call table; one-branch and multi-branch definitions; functions of two variables. Then Python: `def` a function that calls itself, base cases, tracing calls, the call stack. Short-answer items evaluate a given definition at a value; programming items implement one. |
| `unit-03-wdtpd-branching` | What Does This Program Do? – Branching | junior, intermediate, senior | `code-tracing` | **Junior:** tracing `if`/`elif`/`else` chains, nested conditions, `and`/`or`/`not` and integer arithmetic (`//`, `%`) through short programs, with exact printed output. **Intermediate+ section** (tagged `acsl-intermediate`): Contest 1 covers all constructs for these divisions, so it also traces loops, lists and strings. ACSL's own pseudocode is shown next to Python where it helps. Mostly short-answer, with a few programming "predict then verify" items. |
| `checkpoint-01-contest-1-practice` | Practice (contest 1) | junior, intermediate, senior | — | A timed ACSL-style practice: 6 short-answer questions (2 per category, a mix of Junior and Intermediate tags) plus exactly 1 programming problem (Junior), 7 questions in all. Strict: only taught concepts. The teacher notes include Grading (ACSL scoring: 1 point per short answer; the programming problem scored on hidden test cases). |

## Phase A — Registry (inline, active session)

- `acsl/curriculum/concepts.yaml`: add `base-conversion`, `recursion` and `code-tracing`, byte-identical to USACO's entries.
- `acsl/curriculum/coverage-map.yaml`: add the four entries in season order, filled from the authors' final concept lists.
- `acsl/syllabus.md`: the Contest 1 rows move from *planned* to shipped (the syllabus-check row form).

## Phase B — Lessons and statements (Opus subagents, one per entry, in parallel; each owns only its folder)

Four authors: three units and the checkpoint.
- Each unit author writes `manifest.yaml` (with the `acsl:` block), `lesson.ipynb`, `exercises.ipynb`, and the lesson assets `lN.py` with fixtures.
- The checkpoint author writes `manifest.yaml` and `checkpoint.ipynb`.
- Each reports its concept lists for Phase A.

## Phase C — Solutions (Opus subagents, separate fresh sessions, one per entry)

- Programming items: `assets/exN.py` or `qN.py` with fixtures, and no-exec mirrors in the notebook.
- Short-answer items: `assets/traceN.py` (or equivalent) where a program is involved, a worked answer, and a `verify` cell.
- Solved from the statements only.

## Phase D — Teacher notes (inline)

Four `teacher-notes.md`: the required headings, plus Grading for the checkpoint. They cover division paths (Elementary: unit 01's Elementary section is the whole Contest 1 path), pacing against the contest window, and common mistakes (e.g. confusing place value with digit value; missing the base case; tracing `elif` after a true branch).

## Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN. For `acsl` this covers structure, hygiene, noexec, cell-lint, exec-solutions, exec-lessons, manifest, prereq, coverage, concept-scan, stretch, judge-check, source-policy and `acsl-check`. `acsl-check` confirms the season order, the practice checkpoint after the last Contest 1 unit, and valid division subsets.
2. The global concept check passes with the three new shared ids, identical to USACO's.
3. Blind solves in the content gate: reviewers solve a sample of short-answer and programming items from each entry, and the practice checkpoint in full.
4. Post-execution report.

## Out of scope

- Contests 2–4 (094–096).
- The USACO trim (097).
- ACSL publication.

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- The verification phase is named. The scope is 3 units and a checkpoint, as in earlier content plans.
- Watch items:
  - the Elementary section must be fully non-programming and usable alone
  - the Intermediate+ tracing section must not use concepts beyond *Python by Projects*
  - `int(s, base)` must come after the hand method
  - the checkpoint must have exactly one programming question
- `[glm]` skipped: user decision 2026-09-28, until further notice.

## Content Review
_(filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
