# Plan 011 — Checkpoint 03 Data Wrangler Implementation Plan

**Goal:** Ship `checkpoint-03-data-wrangler` — Term 3's assessment — where students demonstrate
the term's data-handling skills: string surgery (index/slice/methods/membership, unit 06), lists
(build/index/append/loop/sort/builtins, unit 07), and dictionaries (build/lookup/`.get`/`.items`
walk, unit 08). No new concepts; a comprehensive, self-contained checkpoint.

**Architecture:** Standard checkpoint pipeline (plan 005/006), no new tooling. ONE map amendment
lands UP FRONT (the standing substrate audit, validated with the AST concept-scanner): the
checkpoint entry lists only the 13 term-3 HEADLINE concepts and omits the substrate the questions
use — `print`/`variable`/`f-string`/`string-literal` (display), `if-statement`/`elif-else`/
`boolean` (conditionals + membership predicates; all conditions are `in`-membership, never `==`,
so `comparison` is NOT used and NOT listed), `for-loop` (list/dict loops),
`accumulator`/`arithmetic`/`int-type` (totals + the word counter), and `error-messages` (the
fix-the-bug beat). All taught by units 01–08; verified green in scratch. This mirrors the
checkpoint-02 substrate amendment (plan 006).

**Spec:** `book1/curriculum/coverage-map.yaml` (binding, amended); plan 005/006 checkpoint
conventions; D-001.

## Global Constraints

- Checkpoint conventions (plan 005/006): `checkpoint.ipynb` has `## Question N` headings (6–8,
  sequential, unique), each followed by an EMPTY student code cell; any broken/"fix this" snippet
  lives in a MARKDOWN fence (never an executable code cell); NO stretch tags; NO solutions in the
  checkpoint. `solutions.ipynb` mirrors `## Question N`, runs top-to-bottom clean and input-free
  with non-vacuous asserts (no tautologies). `teacher-notes.md` carries SIX headings: Goals,
  Pacing, Common mistakes, Discussion prompts, Differentiation, **Grading**. Checkpoint dir prefix
  `checkpoint-03-`. Manifest map-equal.
- Coverage-map amendment (EXACTLY this, pre-audited + scanner-validated green):
  - append to `checkpoint-03-data-wrangler.requires` — `for-loop`.
  - append to `checkpoint-03-data-wrangler.practices` — `for-loop, print, variable, f-string,
    string-literal, if-statement, boolean, accumulator, arithmetic, int-type, elif-else,
    error-messages` (`for-loop` in BOTH requires and practices, matching shipped cp-02 — students
    actively WRITE loops in Q4/Q7; fable plan-review).
  - **`comparison` is deliberately NOT listed** (fable plan-review): no question uses `==`/`<`/`>`;
    all conditionals are MEMBERSHIP (`in`, already listed). Q6/Q7 use `if <key> in <dict>:`, never a
    `== sentinel` compare — matching the taught unit-08 `.get`/`in` idiom. The Phase-C scanner is
    the backstop for any stray `==`.
  - All introduced by units 01–08; `checkpoint-only-taught` holds. Apply surgically (no YAML
    round-trip). Manifest carries the amended lists.
- **Pre-gate closure self-check (standing from plans 008–010):** run the AST concept-scanner
  scoped to checkpoint-03 and confirm ZERO used-but-unlisted concepts AND zero untaught methods
  before dispatching the `[sol]` content review.
- **Closure (binding):** questions use ONLY concepts taught through unit 08. String methods stay
  in the taught subset `upper/lower/strip/replace` (NO `.split()`). Lists use only
  `.append`/`.sort` + `len`/`max`/`min` (NO `.pop`/`.insert`/`.remove`/`.index`/`sorted()`).
  Dicts use only `[]`/`.get`/`.items` (NO `.pop`/`.update`/`.setdefault`/`.keys`/`.values`). NO
  files/classes (units 09/10), NO nested loops, NO comprehensions, NO sets. Word-counting
  iterates a GIVEN word list, never a split sentence.
- **Assessment scope (binding):** the checkpoint assesses ONLY skills taught in units 06–08 (with
  their substrate). No question introduces anything new or requires an out-of-budget construct.
- **Self-contained questions (binding, fable/glm plan-review):** every question RESTATES its own
  data in its own cell (e.g. Q4/Q5 restate `scores = [88, 92, 75, 100]` rather than relying on the
  list Q3 built and mutated). No question depends on kernel state left by an earlier cell, so
  each is order-independent and gradable in isolation. Solutions likewise restate data per
  question. (Q5's in-place `.sort` therefore mutates only its own local list.)
- **Input discipline:** the checkpoint + solutions are input-free (a checkpoint is worked in
  class); NO `input()` anywhere, including question prompts (unlike units, a checkpoint has no
  "type your…" beat — all data is given).
- Process (standing): no commits while a `[sol]` review is in flight; codex prompts name the
  in-process execution fallback and avoid bare CLI-flag-like tokens.

## Out of scope

Checkpoint plan → Phase C is the mandatory named verification phase. Out of scope: units 09+
(later plans); the latent practice-completeness hygiene PR + scanner promotion (tracked
separately); PDF handouts; any map edit beyond the Phase-A substrate amendment; files/classes.

## Phases

Dispatch per AGENTS.md: checkpoint question STATEMENTS via codex; solutions via a SEPARATE blind
codex session; teacher notes inline; map amendment + manifest inline.

### Phase A — map amendment + manifest (inline)

1. Amend `coverage-map.yaml` per Global Constraints (surgical, requires + practices); full suite
   green with the amendment alone before content.
2. `book1/checkpoints/checkpoint-03-data-wrangler/manifest.yaml`, map-equal to the amended entry;
   lands with the complete directory in Phase B.
- **Acceptance (Phase A):** the map amendment ALONE is green (`uv run pytest -q` + `ci-local`)
  before any checkpoint directory exists.

### Phase B — checkpoint-03-data-wrangler content (8 questions)

Blueprint (requires list-literal, dict-literal, string-index, for-loop; practices = the 13
term-3 headline concepts + amended for-loop/print/variable/f-string/string-literal/if-statement/boolean/
accumulator/arithmetic/int-type/elif-else/error-messages):
- Title: `# Checkpoint 3 — Data Wrangler`. A short framing line (a "data wrangler" tidies and
  summarizes messy data — show what you have learned this term).
- **Q1 — string surgery (string-index, string-slice, string-literal):** given `word = "wizardry"`,
  grab the first char `word[0]`, the last `word[-1]`, a slice `word[2:5]`, and the reverse
  `word[::-1]`; print each in an f-string.
- **Q2 — clean and search text (string-methods, in-operator, boolean):** given
  `phrase = "  Hello, Data World!  "`, produce a stripped lowercase version with `.strip().lower()`
  and a `.replace(",", "")`; print whether `"data"` is `in` the cleaned phrase (a True/False value).
- **Q3 — build a list (list-literal, list-index, list-append, int-type):** start
  `scores = [88, 92, 75]`, append `100`, then print the first and last scores.
- **Q4 — measure a list (list-loop, for-loop, builtin-functions, accumulator, arithmetic):** loop
  the scores printing each; then print `len`, `max` (top), `min` (low), and a `total` accumulated
  in a loop (integers only — no average, so no float).
- **Q5 — rank a list (list-sort, boolean, list-index):** sort a copy-free `scores` list
  `.sort(reverse=True)` (in place) and print the top three by index 0/1/2.
- **Q6 — a price book (dict-literal, dict-access, in-operator, if-statement, elif-else, boolean):**
  build `prices = {"apple": 3, "pear": 2, "plum": 4}`; look up `prices["pear"]`; use `.get("fig", 0)`
  for a missing key; print whether `"apple" in prices` (a True/False value); then a 3-way
  MEMBERSHIP branch homes a REAL `elif` (no `comparison` — fable/glm plan-review):
  `if "plum" in prices: print(prices["plum"])  elif "pear" in prices: print(prices["pear"])
  else: print("sold out")`.
- **Q7 — count words (dict-loop, dict-access, in-operator, if-statement, elif-else, accumulator,
  arithmetic, int-type):** given `words = ["cat","dog","cat","bird","cat"]`, build `counts = {}`
  with ONE loop (`if word in counts: counts[word] = counts[word] + 1  else: counts[word] = 1`),
  then print each `word` and `count` with `.items()`.
- **Q8 — fix the bug (error-messages, dict-access):** a MARKDOWN fence shows a crashing snippet
  `prices = {"apple": 3}` then `print(prices["fig"])` raising a KeyError; the student rewrites it in
  the code cell using `.get("fig", 0)` so it prints safely. The question names the traceback's
  final line (`KeyError: 'fig'`) as the clue.
- Solutions: mirror `## Question N`, execute headless + input-free, non-vacuous asserts — e.g.
  `word[::-1] == "yrdraziw"`; `"data" in cleaned`; `len(scores) == 4` after append; `total == 355`;
  `scores[0] == max(...)` after reverse-sort; `prices.get("fig", 0) == 0`; `counts["cat"] == 3`;
  the Q8 safe result `prices.get("fig", 0) == 0`.
- Teacher notes: SIX headings incl. `## Grading` — per-question point allocation, what full credit
  looks like, and common partial-credit cases; **35–40 min pacing** (checkpoint is 0.5 lesson;
  Q4/Q7 are multi-step write-from-scratch — cp-02 allots 35–45 min, fable/glm plan-review); a
  "run cells top-to-bottom / each question is self-contained" note; common mistakes (off-by-one
  slice bounds; `.sort()` returns None; KeyError vs `.get`; counting the dict instead of the word
  list); differentiation (a struggling student may skip Q5/Q8).

### Phase C — Verification (NAMED, mandatory)

Mechanical: full pytest green; `ci-local.sh` ALL GREEN; AST concept-scanner scoped to
checkpoint-03 clean (zero used-but-unlisted, zero untaught methods) BEFORE the content gate;
solutions execute with non-vacuous asserts; manifest map-equal; checkpoint checks pass
(sequential-unique `## Question N`, no stretch, broken snippets in markdown only).
Reviewer duties: blind-solve every question; cumulative closure (only ≤unit-08 concepts — NO
`.split()`, NO files/classes, NO untaught list/dict methods, NO nested loops — check explicitly);
each question is solvable and its reference correct; asserts non-vacuous; grading rubric usable +
point allocation sums sensibly; timing (30 min); no `input()` anywhere; assesses only taught
skills (nothing un-taught assessed — the checkpoint discipline).

**Acceptance criteria:** the checkpoint directory complete; `uv run pytest -q` green; ci-local ALL
GREEN; concept-scanner clean; content gate 4-way consensus.

---

## Plan Review

### Review 1 — [self] (2026-09-07)
APPROVE. Substrate amendment pre-audited from the 8-question design + scanner-validated green
(prereq/practice/reference/schema/checkpoint/introduction curriculum checks). Design honors:
checkpoint conventions (`## Question N`, empty student cells, broken snippets in markdown, no
stretch, six teacher-notes headings incl. Grading); cumulative closure (only ≤unit-08 — `.split()`
forbidden, only taught list/dict methods, no files/classes/nested-loops); input-free throughout
(no `input()` even in prompts — a checkpoint gives all data). Verified each amended concept has a
home: print/variable/f-string/string-literal (all Qs), if-statement/boolean (Q2/Q6),
elif-else (Q6/Q7 else), for-loop/accumulator/arithmetic/int-type (Q4/Q7), error-messages (Q8).
`practices ∩ requires`-only concept `for-loop` moved to requires (load-bearing, mirrors cp-02).

### Review 2 — [fable] (2026-09-07)
APPROVE WITH NITS → all addressed (revised in place before commit):
1. `[FIXED]` (Primary) `comparison` risk — Q6/Q7 conditionals PINNED to `in`-membership (never
   `==`); Q6 now a 3-way membership `elif`; `comparison` explicitly NOT listed; scanner backstop.
2. `[FIXED]` (Minor) `elif-else` half-exercised — Q6 now has a REAL membership `elif` (no comparison).
3. `[FIXED]` (Minor) `for-loop` in requires only — added to practices too (mirrors cp-02).
4. `[FIXED]` (Minor) 30-min budget optimistic — widened to 35–40 min in teacher-notes.
5. `[FIXED]` (Low) shared mutable `scores` — Self-contained-questions constraint: every question
   restates its own data (order-independent).
- fable affirmed: closure sound (every construct taught ≤unit-08, verbatim in several cases);
  conventions match cp-02; no over-listing; asserts numerically correct.

### Review 3 — [glm] (2026-09-07)
APPROVE WITH NITS → all addressed:
- `[FIXED]` NIT-1 elif-else half-exercised — real membership elif in Q6 (same fix as fable #2).
- `[FIXED]` NIT-2 shared `scores` across Q3–Q5 — self-contained restated data per question.
- `[FIXED]` NIT-3 for-loop in practices — added.
- `[FIXED]` NIT-4 stale `comparison` in Architecture prose — removed.
- glm affirmed: closure PASS (no used-but-unlisted), closure-safety PASS (no .split/untaught
  methods/files/classes/nested-loops), conventions PASS, assessment quality PASS.

### Round 2 revisions (2026-09-07)
Amendment now: requires += `for-loop`; practices += `for-loop, print, variable, f-string,
string-literal, if-statement, boolean, accumulator, arithmetic, int-type, elif-else,
error-messages`. Q6 = 3-way membership elif (homes elif-else, no comparison). Every question
restates its data. Pacing 35–40 min. Re-validated green; Q6 re-smoke-tested (elif-else present,
comparison absent). Awaiting [sol].

### Review 4 — [sol] (2026-09-07)
APPROVE WITH NITS. Full beat-by-beat mapping of all 8 questions → every concept homed, no
used-but-unlisted, no over-listing, no untaught leak (strings ≤4-method subset, lists .append/.sort
+ len/max/min, dicts []/.get/.items, no .split/files/classes/nested-loops). Q6/Q7 conditions use
MEMBERSHIP not comparison (the `==` at solution asserts are exempt scaffolding). Scratch
prereq-check + coverage-check PASS.
- `[FIXED]` NIT: Phase-B "practices" summary omitted `for-loop` (stale prose) — added.

## Plan Gate — CONSENSUS REACHED (2026-09-07)
- `[self]` APPROVE · `[fable]` APPROVE WITH NITS · `[glm]` APPROVE WITH NITS · `[sol]` APPROVE WITH NITS.
- All nits resolved (elif-else real membership elif; self-contained data; for-loop in practices;
  comparison-prose removed; 35–40 min pacing; Phase-B summary). No open blockers; no REJECT.
- **Gate PASSED. Proceeding to Phase A → Phase B → Phase C.**
