# Plan 102 — Site content confirmation for all four books (design 012, rollout step 2)

**Goal:** Every checkable item in the four `site: true` books gets a confirmed check kind, each as a heading-cell `check-*` tag, with sound check data.
Every hidden-answer item gets a correct `answer_format`.
Every concept gap is attributed.
Then each book's `site.yaml` flips to `classification: confirmed`, so `site-check` fails on any untagged item from then on.

**Spec:** design 012 D3, D4, D5 and D8, and §4 row 2.
Tooling from plan 101 (`classify --apply`, `site-check`).
User, 2026-10-06: "go ahead with the content plans on autopilot", and the goal "non stop until full working learning website".

**Deviation from design 012 §4 (recorded, not a scope change):**
- §4 plans "one content plan per book". This plan covers all four books, one phase per book, so one set of gates serves them all.
- The `slide-break` pass moves to the part B plan, because it needs B's slide splitter and slide audit (D6).

## Survey (2026-10-06, plan 101 tooling on main 43ec33b)

| book | items | proposed kinds | derived `answer_format` with letters | single-token `expected-output` | `self-check` | unattributed (lesson blocks / items) |
|---|---|---|---|---|---|---|
| python-projects | 236 | asserts 91, expected-output 17, predict 6, self-check 122 | 12 | 6 | 122 | 3 / 0 |
| python-concepts | 391 | asserts 193, expected-output 164, predict 7, self-check 27 | 128 | 8 | 27 | 4 / 0 |
| usaco-bronze | 161 | fixtures 161 | 0 | 0 | 0 | 59 / 1 |
| acsl | 359 | answer 287, fixtures 72 | 90 | 0 | 0 | 128 / 1 (+287 short answers exempt) |

- No `check-*` tag exists yet; every book has `classification: proposed`.
- Most python-projects self-check reasons are "asserts test the solution's own choices (`total`, `tip_count`, …)". The statement often names the variable without backticks, so the free-name rule cannot see it.

## Rules (apply to every phase)

1. **Tags.** `classify --apply` writes the proposed tag to each untagged heading cell. A reviewer then confirms each item against its student-facing statement, and replaces the tag where the proposal is wrong:
   - **`expected-output`** only when the statement (or the starter) fixes the exact output (D4).
   - **`asserts`** only when the statement tells the student the names the asserts use.
   - **`predict`** only for trace questions.
   - **`answer`** only for short answers with exactly one canonical `**Answer:**` line.
   - **`fixtures`** only for stdin programs with fixture pairs.
   - **`self-check`** is the honest fallback.

   A tag is never chosen to make an item easier to check than its statement supports.
2. **Making an item checkable by a statement edit.** This is allowed only when the statement already asks for the exact name or output and just fails to mark it. Example: "store the count in total" becomes "store the count in `total`".
   - Any wider statement change is out of scope; such items stay `self-check`.
   - Every statement edit is listed in the post-execution report.
   - Statement edits must leave the PDFs correct (the publication regression baselines are allowed to change only for listed edits, through each book's allowed-diffs file).
   - Solutions never change, except to keep a solution's mirror equal to an edited starter.
3. **`answer_format`** (heading-cell metadata `answer_format: {case, hint}`):
   - Program output (`expected-output`, `predict`) stays `case: sensitive`, because Python output is case-sensitive, and needs no metadata unless the hint is misleading.
   - ACSL short answers get `case: insensitive` exactly where the topic's canonical form is case-free:
     - hexadecimal digits
     - Boolean variable names, where the unit's rule says so
     - LISP atoms, where the unit's rule says so
   - The hint names the form the unit teaches (for example "a hexadecimal number", "a prefix expression", "a list such as (A B)").
   - Every one of the 90 derived letter-bearing ACSL formats is decided explicitly, and so is every Python one where case could matter.
4. **Single-token `expected-output` items** (6 + 8) are confirmed by reading the statement: the token must be the statement's fixed answer, not an incidental digit. Otherwise retag.
5. **`self-check` requirements:** where the derived checklist misstates the task, heading-cell metadata `requirements: [...]` gives 2–6 short sentences taken from the statement's own instructions, never from the solution.
6. **Concepts:**
   - Unattributed lesson code blocks and items get a cell `concepts: [...]` list.
   - The ids come only from the book's own registry (D11); `site-check` validates them.
   - Where no registered concept fits (for example a contest lesson's plain I/O boilerplate), use the closest registered feature concept. If none fits, leave the block unattributed and list it as a known gap (the mastery map then simply does not count it).
7. **Flip:** at the end of each phase, the book's `site.yaml` gets `classification: confirmed`, and `site-check --book <b>` must show no `FAIL:`.

## Phases

Each phase runs on its own book. Phases A–D run in four parallel worktrees, one Opus authoring agent per book, then merge in turn. Each agent:
1. runs `uv run py4kids-tools classify --book <b> --apply`;
2. reviews every item under the Rules, unit by unit, and edits tags and metadata, and statements where rule 2 allows;
3. runs `export` and `site-check` for its book;
4. reruns the publication regression test for its book;
5. records per-unit counts, every retag, every statement edit and every `answer_format` decision in a phase log, `docs/plans/102-logs/<book>.md`.

- **Phase A: python-concepts** (391 items). Expected to be mostly confirmations: its statements carry worked samples.
- **Phase B: python-projects** (236 items). Most of the work is the self-check items: backtick named variables where rule 2 allows, and otherwise confirm `self-check` with a sound checklist.
- **Phase C: usaco-bronze** (161 items, all `fixtures`). Confirm each item's sample pair matches its statement, and attribute 59 lesson blocks and 1 item.
- **Phase D: acsl** (359 items). Decide all 90 letter-bearing `answer_format`s, confirm the 72 `fixtures` items, and attribute 128 lesson blocks and 1 item.
- **Phase E: verification (named verification phase).**
  - After all four merges: `site-check` for all four books shows no `FAIL:`, with `classification: confirmed`.
  - `tests/test_site_*` and the publication regression tests pass.
  - A new test, `tests/test_site_confirmed.py`, asserts that every item of every site book carries exactly one `check-*` tag and that every `site.yaml` is `confirmed`.
  - `scripts/ci-local.sh` runs solo on the final commit, rendering every book, because statements may change.

## Content-gate focus

Reviewers sample at least 25 items per book across all kinds. They solve each item blind from the student-facing statement, then judge whether the confirmed check would accept their correct answer and reject a wrong one. They also review every statement edit and every ACSL `answer_format` decision.

## Out of scope

- Parts B–D (site, runner, PWA).
- The `slide-break` pass (part B).
- New exercises.
- Rewriting statements beyond rule 2.
- Turning open-ended items into checked ones.
- The python-concepts checkpoint-03 Q3 and checkpoint-04 Q5 curriculum question (user decision pending).

## Plan Review

## Content Review

## Post-Execution Report
