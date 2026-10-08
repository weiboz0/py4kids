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
   - **`expected-output`** only when the statement (or the starter) fixes the exact output (D4): it fixes every **input value** the program uses, not only a sample.
     - A worked sample that only illustrates, where the student chooses their own values (python-concepts unit 01 Exercise 7: "your club and day"), is **not** fixed; retag it `self-check`.
     - Retagging an item *to* `expected-output` against the tool's `output not fixed by the statement` verdict needs a phase-log line quoting the statement sentence that fixes each output line. The content gate samples these first.
   - **`asserts`** only when the statement tells the student the names the asserts use, **and** every asserted value is one the statement fixes. The reviewer compares each assert's operands with the task's fixed inputs and its permitted choices. Example: python-projects unit 01 Exercise 3 asserts the solution's own snack while the student may choose words, so it is not `asserts`.
   - **`predict`** only for trace questions.
   - **`answer`** only for short answers with exactly one canonical `**Answer:**` line.
   - **`fixtures`** only for stdin programs with fixture pairs.
   - **`self-check`** is the honest fallback.

   A tag is never chosen to make an item easier to check than its statement supports.
   - **Every task requirement is accounted for.** The reviewer lists the statement's requirements and marks each one as either verified by the kind (the output, the asserted values) or not verifiable by it.
     - A method requirement is an example of the second kind: "use `+`, not an f-string" (python-concepts unit 01 Exercise 4); "use a loop".
     - Unverifiable requirements go into heading-cell metadata `also_check: [...]` (short sentences from the statement). The site shows them as a self-check list beside the automatic check, so a correct output alone is never presented as full marks.
     - If the item's **core** result cannot be verified, the item is `self-check`.
2. **Making an item checkable by a statement edit.** This is allowed only when a statement sentence already **instructs the student to store or name that value** under that name and just fails to mark it. Example: "store the count in total" becomes "store the count in `total`".
   - A word used in prose ("Print a title", "the running total", "a short story") is not a rule-2 case.
   - Expect about 5–10 such edits in total.
   - Any wider statement change is out of scope; such items stay `self-check`.
   - Every statement edit is listed in the post-execution report.
   - **Regression contract.** The baseline digests (`tests/data/<book>-publish-baseline.json`) stay immutable.
     - Each file a statement edit changes gets an allowed-diffs entry whose reason cites `design 012 D4 (plan 102 rule 2)` and names the item. `tests/test_publication_regression.py`'s reason rule is extended to accept that citation alongside design 010 D2/D3.
     - The phase log records, for each edit, that reverting exactly that edit reproduces the baseline digest.
     - acsl has no baseline. It relies on `ci-local`'s PDF build and `publish-audit`, and Phase D makes no statement edits.
   - Solutions never change, except to keep a solution's mirror equal to an edited starter.
3. **`answer_format`** (heading-cell metadata `answer_format: {case, hint, aliases?}`):
   - Program output (`expected-output`, `predict`) stays `case: sensitive`, because Python output is case-sensitive, and needs no metadata unless the hint is misleading.
   - **Significant whitespace.** Where the statement makes whitespace part of the answer (a required tab, indentation or alignment: python-concepts unit 01 Exercise 14's `\t`), set `answer_format.whitespace: exact`. Normalisation then keeps internal whitespace, stripping only trailing spaces on each line and trailing blank lines. If even that cannot express the requirement, the item is `self-check`.
   - ACSL short answers get `case: insensitive` exactly where the topic's canonical form is case-free:
     - hexadecimal digits
     - Boolean variable names, where the unit's rule says so
     - LISP atoms, where the unit's rule says so
   - The hint names the form the unit teaches (for example "a hexadecimal number", "a prefix expression", "a list such as (A B)").
   - **For every `answer` item whose canonical is not a single token,** the hint states the taught form *verbatim*: separator, order and spelling. Examples:
     - unit 08 multi-select: "letters of every correct option, in order, separated by a comma and a space"
     - sum-of-products: terms alphabetical, the plain letter before `~`
     - unit 12 paths: "in alphabetical order, separated by a comma and a space"
     - unit 07: `true` / `NIL`

     The phase log cites the lesson sentence that teaches each hinted form.
   - **Aliases.** The unit-04 prefix/postfix answers with `↑` (e-024, e-026, e-028, e-030, e-040; checkpoint-02 d0aca7dc) are typed `^` on a keyboard, as the unit itself teaches. `answer_format.aliases: {"^": "↑"}` maps the typed form before hashing; Phase 0 adds that support.
   - Every one of the 90 derived letter-bearing ACSL formats is decided explicitly, and so is every Python one where case could matter.
4. **Single-token `expected-output` items** (6 + 8) are confirmed by reading the statement **body** (not its heading): the token must be the statement's fixed answer, not an incidental digit. Otherwise retag. Example: `python-projects/unit-10-pet-simulator/exercises/c8e092dc`'s canonical `3` comes only from the heading "Exercise 3", so it must be retagged or justified.
5. **`self-check` requirements:** where the derived checklist misstates the task, heading-cell metadata `requirements: [...]` gives 2–6 short sentences taken from the statement's own instructions, never from the solution.
6. **Concepts:**
   - Unattributed lesson code blocks and items get a cell `concepts: [...]` list.
   - The ids come only from the book's own registry (D11), features or techniques; `site-check` validates them.
   - Attribute **only** when the block actually exercises the concept (D8: the mastery map must not pretend). Examples:
     - `boolean-algebra` for a usaco-bronze unit-02 Boolean-logic block
     - `complete-search` for a unit-05 search block
     - `code-tracing` for an ACSL trace block
   - Boilerplate that exercises nothing (`print(3, 4)` in acsl unit 00) stays unattributed and goes on the phase log's gap list.
7. **Flip:** at the end of each phase, the book's `site.yaml` gets `classification: confirmed`, and `site-check --book <b>` must show no `FAIL:`.

## Phases

Each phase runs on its own book. Phases A–D run in four parallel worktrees, one Opus authoring agent per book, then merge in turn. Each agent:
1. runs `uv run py4kids-tools classify --book <b> --apply`;
2. reviews every item under the Rules, unit by unit, and edits tags and metadata, and statements where rule 2 allows;
3. runs `export` and `site-check` for its book;
4. reruns the publication regression test for its book;
5. records a phase log, `docs/plans/102-logs/<book>.md`, with:
   - **one line per item** (key, final kind, a short reason); `classify --apply` marks everything confirmed before anyone reads it, so the log is what shows each item was reviewed
   - per-unit counts
   - every retag, every statement edit (with its revert-reproduces-baseline note) and every `answer_format` decision (with its lesson citation)

- **Phase 0: answer-format extensions and `also_check`** (tooling, before Phases A–D).
  - **`aliases`:** `answer_format` gains an optional `aliases` map, `{typed: canonical}`, with single-character or token keys.
  - **`whitespace`:** `answer_format` gains an optional `whitespace: collapse|exact` (default `collapse`). `exact` strips only trailing spaces per line and trailing blank lines.
  - The bundle schema, `normalise` (aliases applied after whitespace and case), `answer_hash`, the answer model's check 4, and `hash_vectors.json` all honour both, so part C's JavaScript port follows them.
  - **`also_check`:** items gain an optional `also_check: [string]`, exported from heading-cell metadata for every kind except `self-check`.
    - It is counted by the answer model's check 2 against its statement source, like `requirements`.
    - It is validated: each entry must be a sentence drawn from the statement, checked by the same tie rule as `requirements`.
  - Tests:
    - `^` and `↑` hash the same under `aliases: {"^": "↑"}`, and differ without the alias
    - `a\tb` and `a b` hash differently under `whitespace: exact`, and the same under `collapse`
    - `also_check` round-trips from heading metadata into the bundle, and a hidden canonical injected there fails
    - the vectors cover each case
- **Phase A: python-concepts** (391 items). Expected to be mostly confirmations: its statements carry worked samples.
- **Phase B: python-projects** (236 items). Most of the work is the self-check items: confirm each one, backticking named variables only where rule 2 allows (about 5–10 items), and give each a sound checklist. Retag or justify `c8e092dc` (rule 4).
- **Phase C: usaco-bronze** (161 items, all `fixtures`).
  - Confirm each item's sample pair matches its statement.
  - **Validate every fixture pair independently.** A separate Opus agent, which never reads the reference solvers (`assets/exN.py`, `qN.py`, `pN.py`) or the solution notebooks, writes its own solver for each item from the statement alone and runs it on every pair. Any mismatch is investigated and the wrong side fixed: a bad `.out` is regenerated from a corrected reference only after review.
  - Attribute 59 lesson blocks and 1 item under rule 6.
- **Phase D: acsl** (359 items).
  - Decide all 90 letter-bearing `answer_format`s under rule 3, including the six `↑` aliases.
  - Confirm the 72 `fixtures` items, with the same independent blind-solver validation of every pair as Phase C.
  - Attribute 128 lesson blocks and 1 item under rule 6.
  - Make no statement edits.
- **Phase E: verification (named verification phase).**
  - After all four merges: `site-check` for all four books shows no `FAIL:`, with `classification: confirmed`.
  - `tests/test_site_*` and the publication regression tests pass.
  - A new test, `tests/test_site_confirmed.py`, asserts:
    - every item of every site book carries exactly one `check-*` tag, and every `site.yaml` is `confirmed`
    - every confirmed single-token `expected-output` token occurs in the statement body, excluding its heading line
    - every non-single-token `answer` item has a heading-cell `answer_format` with a hint
    - every phase log has one line per item of its book
  - `scripts/ci-local.sh` runs solo on the final commit, rendering every book, because statements may change.

## Content-gate focus

Reviewers sample at least 25 items per book across all kinds. For each sampled item they also list its requirements and confirm each is either verified by the kind or listed in `also_check`. Items whose statement mentions tabs, spaces, indentation or alignment are sampled first.
They take items from each phase log's retag lines and from every rule-1 `expected-output` exception first. They solve each item blind from the student-facing statement, then judge whether the confirmed check would accept their correct answer and reject a wrong one. They also review every statement edit and every ACSL `answer_format` decision.

## Out of scope

- Parts B–D (site, runner, PWA).
- The `slide-break` pass (part B).
- New exercises.
- Rewriting statements beyond rule 2.
- Turning open-ended items into checked ones.
- The python-concepts checkpoint-03 Q3 and checkpoint-04 Q5 curriculum question (user decision pending).

## Plan Review

### Round 1 (1ebc6b0)

- `[self]` APPROVE (before the reviewers' evidence).
- `[sol]` **REJECT** (gpt-6-sol):
  - `[FIXED]` `asserts` must also check that every asserted value is fixed by the task (unit 01 Exercise 3).
  - `[FIXED]` A worked sample that only illustrates is not fixed (python-concepts unit 01 Exercise 7).
  - `[FIXED]` Every fixture pair is validated independently, by a blind solver (Phases C and D).
  - `[FIXED]` An honest regression-baseline procedure for statement edits (rule 2).
  - `[FIXED]` Concept attribution must show a real concept match (rule 6).
  - `[FIXED]` (nit) The slide-break pass and its audit gate will be named in the part B plan.
- `[fable]` **REJECT**:
  - `[FIXED]` `↑` vs `^`: Phase 0 adds `answer_format.aliases`.
  - `[FIXED]` Hints for multi-token answers state the taught form verbatim, with a lesson citation.
  - `[FIXED]` (nits) Rule 2 sharpened (≈5–10 edits); rule 4 checks the statement body (`c8e092dc`); rule-1 exceptions need a quoted sentence; concepts are features or techniques and only when exercised; acsl has no baseline and no statement edits; the phase log has one line per item.

### Round 2 (a66aa8f)

- `[sol]` **REJECT** (gpt-6-sol):
  - `[FIXED]` Method requirements (python-concepts unit 01 Exercise 4: `+`, not an f-string) are invisible to an output check. Every requirement is now accounted for: unverifiable ones go into `also_check` (Phase 0), shown as a self-check list beside the automatic check; an item whose core result is unverifiable is `self-check`.
  - `[FIXED]` Significant whitespace (unit 01 Exercise 14's `\t`) was collapsed. Added `answer_format.whitespace: exact` (Phase 0) and a review rule.

## Content Review

## Post-Execution Report
