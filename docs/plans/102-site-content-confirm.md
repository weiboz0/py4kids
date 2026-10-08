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
   - **`asserts`** only when every assert is portable.
     - **Portable means one of two things:**
       - (a) It **calls a function or method the statement specifies**, with any arguments, and compares the result with the specified behaviour. Example: `u07e10a`'s `lcm(5, 7) == 35`, where the statement fixes `lcm(a, b)` and shows only other examples. That is the ideal check.
       - (b) It **compares a top-level name the statement tells the student to use with a value the task's stated inputs fix.**
     - The reviewer compares each assert's operands with the task's fixed inputs and permitted choices.
     - Example: python-projects unit 01 Exercise 3 asserts the solution's own snack while the student chooses "your own words". That fails (b), so it is not `asserts`.
     - **Scripted input.** When the statement's core task, outside the `**Real version:**` panel, reads `input()`, the asserts compare against the solution's scripted sample input and are not portable, so the item is `self-check`. Known python-projects cases:
       - `unit-04-quiz-show`: `u04-ex10`, `u04-ex11`, `u04-count-correct-heading`
       - `unit-07-high-score-hall`: `5c20b19f`, `dfc665d7`
       - `checkpoint-01`: `checkpoint-05`
       - `project-02`: `milestone-1`
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
     - Each file a statement edit changes gets an allowed-diffs entry whose reason cites `design 012 D4 (plan 102 rule 2)` and names the item. `tests/test_publication_regression.py`'s reason rule is extended to accept `D4` only together with the literal `plan 102 rule 2`, so an unrelated D4 reason cannot slip through.
     - The phase log records, for each edit, that reverting exactly that edit reproduces the baseline digest.
     - acsl has no baseline. It relies on `ci-local`'s PDF build and `publish-audit`, and Phase D makes no statement edits.
   - Solutions never change, except to keep a solution's mirror equal to an edited starter.
3. **`answer_format`** (heading-cell metadata `answer_format: {case, hint, aliases?}`):
   - Program output (`expected-output`, `predict`) stays `case: sensitive`, because Python output is case-sensitive, and needs no metadata unless the hint is misleading.
   - **Significant whitespace.** Where the statement makes whitespace part of the answer (a required tab, indentation or alignment: python-concepts unit 01 Exercise 14's `\t`), set `answer_format.whitespace: exact`. Normalisation then keeps internal whitespace, stripping only trailing spaces on each line and trailing blank lines. If even that cannot express the requirement, the item is `self-check`.
     - Each `whitespace: exact` item's hint says how indentation is entered: "type a tab as `\t`, or with the indent key". Each such item is listed in the phase log so part C's answer box handles it.
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
  - **Touch points** (all must change together, or `site-check` fails on the first authored item):
    - `answers.answer_format`, which today rejects any authored metadata whose keys are not exactly `{case, hint}`
    - the bundle schema's `$defs/answer_format`, which has `additionalProperties: false`
    - `normalise` / `answer_hash`
    - the answer model's hash recompute (`answer_model.py`, which passes only `case`)
    - `hash_vectors.json`
  - **`aliases`:** `answer_format` gains an optional `aliases` map, `{typed: canonical}`, with single-character or token keys.
  - **`whitespace`:** `answer_format` gains an optional `whitespace: collapse|exact` (default `collapse`). `exact` folds CRLF, strips trailing spaces on each line, and drops leading and trailing blank lines, as `collapse` does; it keeps all other whitespace (tabs, leading indentation, inner runs).
  - The bundle schema, `normalise` (aliases applied after whitespace and case), `answer_hash`, the answer model's check 4, and `hash_vectors.json` all honour both, so part C's JavaScript port follows them.
  - **`also_check`:** items gain an optional `also_check: [string]`, exported from heading-cell metadata for every kind except `self-check`.
    - It is counted by the answer model's check 2 against its statement source, like `requirements`.
    - It is validated: each entry must be a sentence drawn from the statement.
  - **The statement tie also applies to authored `requirements`.** `answers.check_texts` puts authored metadata into check 2's baseline, so the tie is the guard against a requirement copied from a solution. Both `also_check` and `requirements` entries must occur, normalised, in the item's statement text, or `site-check` FAILs.
  - Tests:
    - `^` and `↑` hash the same under `aliases: {"^": "↑"}`, and differ without the alias
    - `a\tb` and `a b` hash differently under `whitespace: exact`, and the same under `collapse`
    - `also_check` round-trips from heading metadata into the bundle, and a hidden canonical injected there fails
    - the vectors cover each case
- **Phase A: python-concepts** (391 items). Expected to be mostly confirmations: its statements carry worked samples.
- **Phase B: python-projects** (236 items). Most of the work is the self-check items: confirm each one, backticking named variables only where rule 2 allows (about 5–10 items), and give each a sound checklist. Retag or justify `c8e092dc` (rule 4).
- **Phase C: usaco-bronze** (161 items, all `fixtures`).
  - Confirm each item's sample pair matches its statement.
  - **Validate every fixture pair independently.** A separate Opus agent writes its own solver for each item from the statement alone and runs it on every pair.
    - Isolation is enforced, not promised: the agent gets a filtered copy holding only the statement notebooks and the fixture directories. The reference solvers (`assets/exN.py`, `qN.py`, `pN.py`), which sit beside the fixtures, and the solution notebooks are removed.
    - The phase log records per-item pass counts. Any mismatch is investigated and the wrong side fixed: a bad `.out` is regenerated from a corrected reference only after review.
  - Attribute 59 lesson blocks and 1 item under rule 6.
- **Phase D: acsl** (359 items).
  - Author an `answer_format` for all **130** multi-token ACSL `answer` canonicals under rule 3: the 90 letter-bearing ones, plus 40 digit-only lists such as `1 2 3` or `(0,1), (1,0)`, whose hints follow the taught form too (unit 08: "no spaces inside a pair, and a comma and a space between pairs"). This includes the six `↑` aliases.
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

- `[fable]` **REJECT** (round 2, a66aa8f):
  - `[FIXED]` The asserts fold over-reached: about half the asserts items are function calls with arguments the statement does not show (`u07e10a` `lcm(5, 7) == 35`). Portability is now (a) a call to a specified function, or (b) a named variable against task-fixed inputs. Also added the scripted-`input()` exclusion and its seven known items.
  - `[FIXED]` (nits) Phase 0 names all its touch points; ACSL hint authoring is sized at 130, numeric lists included; blind-solver isolation is enforced with a filtered copy and per-item pass counts; the D4 regression reason requires `plan 102 rule 2`.
- `[sol]` **APPROVE** (round 3, 022a1b1, gpt-6-sol).

### Round 4 (a2c7c3b) — CONSENSUS

- `[self]` APPROVE.
- `[sol]` **APPROVE** (gpt-6-sol): the asserts, scripted-input, fixture and answer-format rules hold on sampled items from all four books.
- `[fable]` **APPROVE WITH NITS**: `u07e10a`, unit 01 Exercises 3, 4 and 14 and the seven scripted-input items were verified.
  - `[FIXED]` The statement tie covers `requirements` as well as `also_check`.
  - `[FIXED]` Each `whitespace: exact` hint says how a tab is entered, and these items are listed for part C.
  - `[FIXED]` `exact` is fully defined.
- `[glm]` removed from the roster (docs/content-review-gate.md, user directive 2026-10-05).

## Content Review

Gate roster per `docs/content-review-gate.md`: [self], [sol], [fable] ([glm] removed by the user on 2026-10-05).

### Review 1 — [fable] (2026-10-08)
- **Verdict**: APPROVE WITH NITS. 104 items sampled blind (27 python-projects, 27 python-concepts, 15 usaco-bronze, 35 acsl). Every confirmed check accepted the correct answer and rejected a plausible wrong one. The `↑`/`^` aliases, hex case, the taught list forms and the lesson citations were all verified.
1. `[FIXED]` python-projects unit-03 `exercise-1` is `expected-output`, but `side_length` is the student's own choice (rule 1). Retag `check-self`. Should Fix.
   → Response: Retagged `check-self`; the three former `also_check` entries moved into six statement-quoted `requirements` (variables, loop, pen size, comment and `turtle.done()`, f-string report). Logged in the python-projects retag list and item line.
2. `[FIXED]` The `whitespace: exact` hints say "type a tab as `\t`", but a literal `\t` does not hash as a tab. Add an alias `{"\\t": "\t"}` where a hint mentions it, with a vector. Should Fix.
   → Response: All nine `whitespace: exact` items (every hint mentions `\t`) carry `aliases: {"\\t": "\t"}`. `normalise` applies aliases after whitespace handling, so `exact` still keeps tabs, leading and inner spaces and still tells a tab from a space. Three vectors appended to `hash_vectors.json` (the 41 existing vectors unchanged): u01e14a's typed `\tThe end` and its real-tab canonical hash equal under the alias, and differ without it; `test_typed_backslash_t_is_a_tab_under_the_tab_alias` and `test_tab_hints_carry_the_tab_alias` guard it.
3. `[FIXED]` Derived self-check checklists split sentences inside inline code (cp01 `checkpoint-05`, u09 `0cc7f084`, `e2692eb8`; about 59 fragments). Fix the splitter. Should Fix.
   → Response: `answers._sentences` now masks inline code spans before splitting, so `.`/`!`/`?` inside code never ends a sentence. Tests cover a synthetic case and the three cited items (cp01 `checkpoint-05`, u09 `0cc7f084`, `e2692eb8`). Re-deriving every self-check item, exactly five derived checklists changed (those three plus u07 `5c20b19f` and python-concepts `u13e042`), all from fragments to whole sentences; no other derived list holds a fragment.
4. `[WONTFIX]` usaco-bronze unit-12 statements (`u12e0002/4/6/8/14/16`) never state the input format; it is only in the unit intro. Follow-up content or errata plan. Should Fix (follow-up).
   → Response: Deferred to a follow-up content/errata plan: stating the input format in each statement is a statement change beyond rule 2.
5. `[FIXED]` Construct requirements are missing from `also_check` (cp03 `question-6`, cp04 `c400000e`, `u04e22a`, `u04e23a`). Nice to Have.
   → Response: Fixed with [sol] 2's audit of every checked item in all four books (see [sol] 2): cp03 `question-6` (membership-test branch), cp04 `c400000e` (membership test, `if`/`else`), `u04e22a` ("Add the colon"), `u04e23a` ("Indent both body lines …").
6. `[FIXED]` The python-projects log's summary tables are stale after the integration retags. Nice to Have.
   → Response: The python-projects summary and per-unit tables are recomputed from the notebooks (asserts 52, expected-output 10, predict 7, self-check 167), and its retag list now includes the seven integration retags and `exercise-1` (48). python-concepts totals and its unit-13 row follow the `u13e057` retag; usaco-bronze's and acsl's `also_check` summary lines follow the audit.
7. `[WONTFIX]` `u08e002` wording ("Seed with 4" inside the function) is a pre-existing ambiguity. Nice to Have (follow-up).
   → Response: Deferred to a follow-up content/errata plan: a pre-existing statement ambiguity, outside rule 2.

### Review 1 — [sol] (2026-10-08, gpt-6-sol)
- **Verdict**: REJECT. 25 items sampled per book.
1. `[FIXED]` `u13e057`: the worked sample's `1 1` is not task-fixed output. Retag `check-self` (rule 1). Must Fix.
   → Response: Retagged `check-self` with three `requirements` from its Specification sentences; logged in the python-concepts retag list and item line.
2. `[FIXED]` Output checks accept hard-coded output where `also_check` omits required work: cp03 `question-8` and u08 `5703c375` (safe dictionary lookup), `u02e070` (place-value reversal). Add these, and audit every checked item for the same omission. Must Fix.
   → Response: Audit of every checked item in all four books (925 items: python-projects 69, python-concepts 336, usaco-bronze 161, acsl 359): requirements listed, each marked verified or not, missing ones added to `also_check` verbatim from the statement. Items gaining entries: python-projects 50 (+96 entries), python-concepts 131 (+158), usaco-bronze 3 (+4), acsl 102 (+113). Named: cp03 `question-8` (the safe dictionary-method rewrite), u08 `5703c375` (`.get("fish", "???")`), `u02e070` (place-value reversal with `// 100`, `// 10 % 10`, `% 10`). No existing entry removed; no item's core result found unverifiable. Each log has a content-review-1 audit section and per-item `+N` marks; `test_review1_items_list_their_required_method` guards the named items.
3. `[FIXED]` acsl fixtures `63f51404` (recursive function) and `1c6142c9` (tuple storage) lack `also_check` for the required method. Add them, and review the acsl fixtures the log says need none. Must Fix.
   → Response: `63f51404`: "Write `f` as a recursive Python function with two parameters"; `1c6142c9`: "Store the points as tuples". All 72 acsl fixtures reviewed: 27 gained entries (recursion, try-every-pair search, required data structures, hand-trace-then-translate steps), 45 need none. usaco-bronze's 21 "no also_check" items re-checked: `u07e0012` and `u11e0006` gained entries, 19 need none; `u11e0016` also gained its O(log E) bound.
4. `[FIXED]` `u04-ex09`'s derived checklist omits the counter update and printing both totals. Author `requirements`. Should Fix.
   → Response: Six authored `requirements` from the statement, ending with "Update the question counter each trip and print both totals at the end."

### Coordinator decision (round-1 audit)
- The audit added the statements' own hand-trace instruction ("Work it out by hand first" / "Trace it by hand, using ACSL's rules") as `also_check` on 71 ACSL `answer` items. **Kept**: it is a statement requirement that a hashed answer cannot verify, and showing it beside the answer box is honest about what the check covers.

## Post-Execution Report
