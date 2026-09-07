# Plan 005 — Checkpoint 01 + Unit 04 Implementation Plan

**Goal:** Ship the next two coverage-map entries in teaching order — `checkpoint-01-first-steps` (the year's first assessment, covering units 01–02) and `unit-04-quiz-show` — establishing the checkpoint pipeline (conventions + mechanical checks) the remaining three checkpoints will reuse.

**Architecture:** Unit 04 follows the plan-004 unit pipeline unchanged. Checkpoints get first-class conventions mirroring units (student notebook with no solutions, blind-authored solutions, map-equal manifest, teacher notes with grading guidance) and the `tools/` checks are extended from unit-only to unit+checkpoint scope. Two curriculum-data amendments ride along (Global Constraints carry the binding text): unit-04's `requires` gains `arithmetic`, `int-type`, and `variable`, and checkpoint-01's `practices` gains `error-messages` — both verified green against every curriculum invariant.

**Spec:** design 000 §1–§3; `book1/curriculum/coverage-map.yaml` (binding); plan 004's conventions + follow-ups; plan 003's check registry.

## Global Constraints

- All plan-004 Global Constraints apply verbatim to unit 04 (map-equal manifest, hook-first,
  exercise/solution floors and bans, seed rules, five teacher-notes headings, per-lesson
  concept allocation in Pacing, commit trailers per plan 002).
- **Checkpoint conventions (binding on all Book 1 checkpoints, new):**
  - Directory `book1/checkpoints/<map-id>/` with `manifest.yaml`, `checkpoint.ipynb`
    (student-facing), `solutions.ipynb`, `teacher-notes.md`.
  - `manifest.yaml`: same schema as units with `kind: checkpoint`; `concepts` EQUAL the map
    entry (the map already forces `introduces: []`).
  - `checkpoint.ipynb`: questions are markdown headings matching `^## Question \d+`,
    6–8 of them for a half-lesson; NO solutions, NO outputs, `input()` allowed;
    checkpoints contain NO stretch/challenge questions at all — definitive rule, not
    merely unchecked (assessments assess; the mixed-ability rule lives in units);
    every question uses only concepts from the entry's `practices` ∪ `requires`;
    deliberately BROKEN or incomplete snippets ride as fenced code inside MARKDOWN
    cells, never code cells — so cell-lint and hygiene stay clean with no `no-exec`
    mechanism needed, and any real code cells (answer starters) must LINT clean
    (nothing executes checkpoint.ipynb — input() is allowed there); checkpoint.ipynb
    also carries NO `stretch` tags (mechanically scanned) and no solution headings.
  - `solutions.ipynb`: mirrors every `## Question N` heading with ≥1 code cell,
    ≥3 assert cells, the unit solution conventions verbatim (no input()/GUI,
    `import random` only, seed-before-first-use, self-contained, scaffolding note).
  - `teacher-notes.md`: the five unit headings PLUS `## Grading` (per-question intent,
    what partial understanding looks like, when to re-teach vs move on) — all six
    headings bound to `structure-check` with a one-fault fixture each way.
- Coverage-map amendments are EXACTLY these two (rev2, gate round 1):
  (a) `unit-04-quiz-show.requires` += `arithmetic, int-type, variable` — the score
  accumulator's core path depends on all three ([sol] round-1 #2); all introduced by
  units 01–02, closure holds;
  (b) `checkpoint-01-first-steps.practices` += `error-messages` — traceback reading is
  units 01–02's signature skill and the blueprint's Question 1 assesses it; introduced
  in unit 01, so the checkpoint-taught-only law holds ([glm]/[fable]/[sol] round-1
  blocker resolution, option (b)).
  Nothing else in the map changes; all curriculum invariants must pass; both new
  manifests carry the amended lists.
- Process (standing follow-ups, plans 003/004): NO commits to this branch while a [sol]
  review is in flight; codex content-gate prompts name the in-process execution fallback
  upfront.
- Counter framing, stated precisely ([fable]/[glm] round-1): `loop-counter` is INTRODUCED
  by unit 03 per the binding map; unit 02's teacher notes promise counting "next unit",
  which unit 03 honors. What unit 04 adds is counters IN THE GAME CONTEXT where the
  promise was made — scores and questions-asked — as `practices`, and the lesson says so.

## Out of scope

This is a CONTENT plan (a named verification phase is therefore mandatory — Phase E).
Out of scope: checkpoints 02–04 and units 05+ (later plans reuse today's conventions);
PDF handouts for checkpoints (build-pdf stays unit-scoped until a checkpoint-print need
is real); auto-grading (design 000 out-of-scope); any change to unit-01..03 content.

## Phases

Dispatch per AGENTS.md: statements (checkpoint questions + unit-04 lesson/exercises) via
codex GPT-5.6-sol; SOLUTIONS via a SEPARATE fresh blind codex session (finished statements
only — never the blueprints); teacher/grading notes inline; `tools/` extension via codex;
map amendment + manifests inline (trivially-scoped data edits).

### Phase A — checkpoint support in tools (TDD, codex)

**Files:** `tools/notebooks.py`, `tools/checks.py`, `tests/test_tools.py`, `tests/test_book1_units.py` (or a new thin wrapper module for checkpoints).
1. `checkpoint_dirs(root, book, ident=None)` mirroring `unit_dirs` (fail-closed the same
   way on missing book/checkpoints dirs; an existing-but-empty `checkpoints/` = N=0 pass —
   which is also why the REAL book stays green before Phase C: `book1/checkpoints/`
   currently holds only `.gitkeep`).
2. **Check scope matrix (exhaustive — no other reading is valid):**
   BOTH scopes: `manifest-check` (map-equal; kind per scope), `hygiene-check`
   (exercises.ipynb / checkpoint.ipynb), `structure-check` (units: as today; checkpoints:
   `^## Question \d+` count 6–8 both directions, solutions mirroring + code-under-each-
   question + ≥3 asserts + input/GUI/from-random bans + seed ordering, six teacher-notes
   headings incl. `## Grading`, checkpoint layout file set, checkpoint prefix rule when
   unscoped), `exec-solutions`, `cell-lint` (checkpoint.ipynb code cells lint like any
   other — broken snippets are markdown by convention, so no exclusion exists).
   UNIT-ONLY, unchanged: `noexec-check`, `stretch-check`, `exec-lessons`, `turtle-check`.
   ci-local needs zero edits (steps invoke check names).
3. **`--unit <id>` selector matrix:** an id matching `unit-*` narrows to the unit scope;
   an id matching `checkpoint-*` narrows to the checkpoint scope; passing a
   `checkpoint-*` id to a UNIT-ONLY check exits 2 with usage (mirroring the
   `BOOK_LEVEL_CHECKS` guard); a well-formed id whose directory doesn't exist exits 1
   fail-closed; both prefix rules run only in unscoped mode (as today). Tests cover all
   four combinations plus the usage case.
4. **One-fault fixtures — one generated mutation per NEW rule; a rule without a fixture
   is a finding (plan-003 law; the following list is exhaustive for this plan):**
   checkpoint layout (each required file removed), manifest kind + map-equality drift,
   hygiene (outputs / executed cell), question-count floor AND ceiling, solutions
   missing a mirrored heading, no-code-under-a-question, assert floor, each of the three
   pattern bans, seed-ordering, a failing checkpoint exec-solutions, each missing
   teacher-notes heading incl. `## Grading`, a solution heading leaked into
   checkpoint.ipynb, a `stretch` tag in checkpoint.ipynb, checkpoint prefix violation
   (gap and orphan), missing checkpoints-root/dir/target fail-closed cases, and the
   `--unit` matrix cases (including an id matching NEITHER `unit-*` nor `checkpoint-*`,
   which falls into unit scope and fails closed exit 1 — pinned by a test). The fixture-factory BASELINE gains an empty `checkpoints/` dir plus one
   generated VALID checkpoint (map-equal against the fixture map's checkpoint entry,
   satisfying the checkpoint prefix rule) verified all-green before mutations —
   this baseline change is load-bearing ([fable] round-1 #3). Existing unit fixtures
   unchanged.
5. Parity guard: all existing unit checks and their one-fault tests unchanged and green
   on the real book (same pass set as plan 003 shipped).

### Phase B — map amendment ONLY (inline)

1. Amend `coverage-map.yaml` exactly per Global Constraints (both amendments).
2. Full suite green with the amendment alone — verified pre-gate by two reviewers:
   the map edit without new directories passes every check.
3. NO manifests here: a manifest-only directory is discoverable and breaks
   layout/structure/hygiene between phases ([fable] round-1 #1 — verified mechanically).
   Each manifest lands in the same phase and commit as its directory's COMPLETE file set
   (Phase C for the checkpoint, Phase D for the unit); every phase commit leaves the
   repo green.

### Phase C — checkpoint-01-first-steps content

Blueprint (statements codex; solutions blind codex; grading notes inline):
- 7 questions over the entry's amended practices (u01–u02 material), ~30–45 min of a
  lesson slot: fix-the-error (traceback reading — legal via map amendment (b); the broken
  snippet lives in a markdown fence per the conventions), predict-the-output (f-string +
  arithmetic), write-a-line (input + int conversion), trace an if/elif chain, complete a
  while loop (CONDITION-completion — fill in `while guess != secret:` — never a
  counter-style loop; `loop-counter` is untaught at checkpoint time), a naming/comment
  judgment question, one small build-it (mini mad-libs, or a one-guess detective with a
  HARD-CODED secret — `random-module` is outside the union and stays out).
  Tone: "show what you've got", zero trick questions.
- Teacher notes + `## Grading`: what each question is FOR, common partial answers,
  the re-teach signal (≥1/3 of class missing loops → re-teach before unit 03's density).

### Phase D — unit-04-quiz-show content (2 lessons)

Blueprint per the map (introduces accumulator, logical-ops, conditional-nesting,
break-statement; practices boolean, type-conversion, loop-counter, error-messages):
- Hook: host your own quiz show — scores, streaks, sudden death.
- Lesson 1 (accumulator, logical-ops): a 3-question quiz in straight-line code from
  concepts kids already own (input, int conversion, if/elif); `score = score + 1` names
  the accumulator pattern, and a visible `questions_asked` counter brings counting into
  the game context (loop-counter PRACTICE — the concept itself arrived in unit 03 — 
  without needing a question-dispatch loop, which would demand lists). The streak bonus needs `and`
  (answer right AND streak alive) — logical operators arrive because the bonus rule
  demands them.
- Lesson 2 (conditional-nesting, break-statement): a final round where a question has a
  follow-up only if the first part is right (nesting), and SUDDEN DEATH — one wrong
  answer ends the round immediately (`break` arrives as the drama mechanic).
  Loop shape, named so nothing gets smuggled ([fable] round-1 #7): the sudden-death round
  is a `while` loop over a `questions_asked` counter with an if/elif chain keyed on the
  counter dispatching 3 hard-coded questions — NO lists (unit 07), NO functions in core.
- Exercises ≥6 core + 2 stretch: score-the-answers snippets, fix-the-streak-logic,
  add-a-category-bonus (nesting), sudden-death remix, error-messages debugging,
  predict-the-score; stretch: double-or-nothing round, lightning round with a countdown
  (loop-counter countdown, no new concepts).
- Teacher notes: five headings, per-lesson allocation, 60-min cut points, differentiation;
  common mistakes (accumulator reset inside the loop, `and`/`or` swap, break outside loop).

### Phase E — Verification (NAMED, mandatory)

Mechanical: full pytest green (including the new checkpoint one-fault fixtures);
`bash scripts/ci-local.sh` ALL GREEN (checkpoint checks now live in steps 3–4 via the
extended registry); solutions execute with asserts; manifests map-equal; curriculum
invariants green with the amended map.
Reviewer duties (content gate): blind-solve every question and exercise; content-level
cumulative closure (checkpoint questions use only practices ∪ requires; unit-04 content
only taught-before concepts); solutions non-vacuous and complete; grading notes usable by
a real teacher; difficulty/timing (checkpoint ≤ half a lesson; unit lessons 60–90 min);
hook-first for unit 04; age-appropriateness.

**Acceptance criteria:** both directories complete; extended checks green with negative
coverage; ci-local ALL GREEN; content gate 4-way consensus.

---

## Plan Review

### Review 1 — [self] (2026-09-06)
- **Verdict**: APPROVE — allocation exact, no dispatch-loop leakage, conventions mirror units + grading, named verification present.

### Review 2 — [glm] (2026-09-06)
- **Verdict**: REJECT
1. `[FIXED]` (Blocker) Checkpoint Q1 (traceback reading) uses `error-messages`, outside checkpoint-01's map union; detective variant would need `random-module`. → Resolution: map amendment (b) adds `error-messages` to checkpoint-01 practices; build-it uses a hard-coded secret; the "EXACTLY" amendment clause restated for both amendments.
2. `[FIXED]` (Should Fix) Phase B manifests-before-content breaks the repo between phases. → Phase B is amendment-only; manifests land with their complete file sets.
3. `[FIXED]` (Should Fix) Phase A scope mapping contradictory. → Exhaustive check scope matrix added.
4. `[FIXED]` (Should Fix) `## Grading` had no mechanical home/fixture. → Bound to structure-check; fixture required.
5. `[FIXED]` (Minor) One-fault enumeration incomplete; cell-lint stance unstated. → Exhaustive fixture list added; broken snippets ride in markdown so cell-lint covers checkpoint code cells with no exclusions.
6. `[FIXED]` (Minor) "Machine learns to count" misattribution. → Reworded (unit 03 introduces; unit 04 pays off in the game context).

### Review 3 — [fable] (2026-09-06)
- **Verdict**: REJECT
1. `[FIXED]` (Must Fix) Phase B ordering — verified mechanically both ways. → As glm #2; amendment-alone-green finding cited in Phase B.
2. `[FIXED]` (Must Fix) Union violation (= glm #1); also: while-loop question must be condition-completion (no counters at checkpoint time). → All three addressed in Phase C.
3. `[FIXED]` (Should Fix) Fixture-factory baseline never gains checkpoints/. → Baseline change specified as load-bearing (empty dir + one valid checkpoint).
4. `[FIXED]` (Should Fix) cell-lint scope for broken checkpoint snippets. → Markdown-fence convention; lint applies to real code cells.
5. `[FIXED]` (Should Fix) `--unit` not implementable as written. → Selector matrix with exit codes + tests.
6. `[FIXED]` (Should Fix) Notes/Grading + several new rules missing from check/fixture lists. → Exhaustive lists, plan-003 "rule without a fixture" law restated.
7. `[FIXED]` (Nit) L2 loop shape unnamed. → while + counter-keyed if/elif chain, no lists.
8. `[FIXED]` (Nit) Counter-promise framing. → As glm #6.
9. `[FIXED]` (Nit) Standing process follow-ups. → Added to Global Constraints.

### Review 4 — [sol] (2026-09-06)
- **Verdict**: REJECT
1. `[FIXED]` (Blocker) Union violation (= glm #1 / fable #2). → Amendment (b).
2. `[FIXED]` (Major) `variable` missing from unit-04 requires though the core path assigns/updates score and questions_asked. → Amendment (a) now adds arithmetic, int-type, AND variable (matches u02/u03/u07 precedent).
3. `[FIXED]` (Major) Grading-heading enforcement unassigned. → As glm #4.
4. `[FIXED]` (Major) `--unit` contract ambiguous. → As fable #5.
5. `[FIXED]` (Major) Fixture inventory incomplete. → As fable #6 / glm #5.
6. `[FIXED]` (Minor) "NO stretch requirement" vs "NO stretch" ambiguity. → Definitive: checkpoints contain no stretch/challenge questions at all.

### Round 2 (2026-09-06)
- **[sol]**: APPROVE WITH NITS — 11/11 items PASS; nit: stale Architecture paragraph. `[FIXED]` (rewritten to the two-amendment set).
- **[glm]**: APPROVE WITH NITS — both amendments re-verified green in /tmp with a HEAD control; nits: same Architecture line `[FIXED]`; L1 counter phrasing residue `[FIXED]` (reworded to unit-03 introduction / game-context practice).
- **[fable]**: APPROVE WITH NITS — full mechanical verification (amendments green through all 11 CLI checks incl. real exec; fixture baseline implementable against the existing fixture map's checkpoint entry; markdown-fence convention mechanically true; phase greenness traced). Nits, all `[FIXED]`: checkpoint solution-heading one-fault fixture added to the list; "run clean" → "LINT clean" (nothing executes checkpoint.ipynb); typo-id selector case pinned (unit scope, exit 1, tested); the definitive no-stretch rule got a mechanical stretch-tag scan + fixture.

### Gate result (2026-09-06)
- `[self]` APPROVE · `[sol]` APPROVE WITH NITS · `[glm]` APPROVE WITH NITS · `[fable]` APPROVE WITH NITS.
- Full consensus, no `[OPEN]` items — **gate PASSED; approval to implement.**

## Content Review

### Review 1 — [self] (2026-09-06)
- **Verdict**: APPROVE — concept-boundary sweep clean (keyword hits all in prose/comments); hook opens unit 04; 269 tests green, ci-local ALL GREEN.

### Review 2 — [glm] (2026-09-06)
- **Verdict**: APPROVE WITH NITS — blind-solved all 15 items, zero discrepancies; unit-scope parity verified; full CLI exit-code matrix probed, no fail-open.
1. `[FIXED]` Both new solutions notebooks lack cell ids (MissingIDFieldWarning; future hard error). → normalize() pass; verified 0 warnings.
2. `[FIXED]` Teacher notes overstate `not` (only and/or in material). → a real `not` beat added (lesson + exercise 7 + solution); notes now accurate.

### Review 3 — [fable] (2026-09-06)
- **Verdict**: APPROVE WITH NITS — zero blind-solve discrepancies; parity vs main verified live; fail-open probed clean.
1. `[FIXED]` Missing cell ids (= glm #1).
2. `[FIXED]` Checkpoint Q3 solution hides the answer behind the stand-in. → real answer line shown in the Q3 markdown.
3. `[FIXED]` Teacher-notes `not` overstatement (= glm #2).
4. `[FIXED]` Checkpoint Q1 "do not run it yet" — "yet" implies a later run. → dropped.
5. `[FIXED]` E5 solution could show the repaired line. → added to the E5 markdown.

### Review 4 — [sol] (2026-09-06)
- **Verdict**: REJECT (first attempt failed on a forwarder flag-parse error; re-dispatched)
1. `[FIXED]` (Blocker) `logical-ops` covers and/or/not but only and/or taught. → real `not` beat added (glm/fable saw it as notes-trim; resolved the stronger way — genuine coverage).
2. `[FIXED]` (Major) Q3/E5 answer keys hide the requested `int(input(...))` line. → shown in markdown (= fable #2/#5).
3. `[FIXED]` (Major) Q4 explanation wrong (false `if` "skipped by later elif" — it was evaluated False). → solution matched to the real question (secret=20, guess=27 → "Too high") with a correct top-to-bottom explanation.
4. `[FIXED]` (Major) Rubric too loose (Q5/Q7 accept violating answers). → grading notes tightened to name the required shapes.
5. `[FIXED]` (Major) Assertions assert setup not derived answer (Q5 keep_guessing; Challenge 2 none). → keep_guessing and countdown outcomes now asserted.
6. `[FIXED]` (Major) Assert floor accepts `assert True`. → non-vacuous check added (bare-constant asserts excluded) + fixture.
7. `[FIXED]` (Major) Question check accepts six "Question 1"s. → sequential-unique 1..N check (gated to in-range counts) + fixture.

### Review 5 — [sol] round 2 (2026-09-06)
- **Verdict**: REJECT — 6 of 7 verified fixed; only finding 2's E5 half remained: the markdown described the fix but didn't show the literal `bonus = int(input("Bonus points: "))` line (Q3 did).
1. `[FIXED]` E5 solution markdown now shows the literal repaired line, matching the Q3 treatment sol approved.

### Review 6 — [sol] round 3 (2026-09-06)
- **Verdict**: APPROVE — E5 solution shows the literal input line; commit touched nothing else.

### Gate result (2026-09-06)
- `[self]` APPROVE · `[sol]` APPROVE (round 3) · `[glm]` APPROVE WITH NITS · `[fable]` APPROVE WITH NITS.
- Full consensus, no `[OPEN]` items — **content gate PASSED; clear to ship.**

## Post-Execution Report (2026-09-06)

**Shipped:** the year's first assessment (`checkpoint-01-first-steps` — 7 questions over units 01–02, blind-authored solutions, teacher notes with a full `## Grading` section) and `unit-04-quiz-show` (2 lessons introducing accumulator, logical-ops incl. a real `not` beat, conditional-nesting, break; blind solutions; teacher notes), plus the tools/tests extension giving checkpoints first-class mechanical checks (scope matrix, `--unit` selector, checkpoint prefix rule, ~20 one-fault fixtures) and two general hardenings (non-vacuous assert floor; sequential-unique question numbers). Two map amendments: unit-04 requires += arithmetic/int-type/variable; checkpoint-01 practices += error-messages. Final: 271 tests, ci-local ALL GREEN.

**Gate history:** plan gate 2 rounds (all three externals REJECTED round 1 — the checkpoint-union blocker, Phase-B ordering, and Phase-A under-specification; rev2 resolved all 21 findings). Content gate 3 rounds: [glm]/[fable] APPROVE WITH NITS on first pass (zero blind-solve discrepancies); [sol] found real defects the others missed — a wrong Q4 explanation, weak assertions, and two tooling gaps (vacuous asserts, non-sequential question numbers) — all fixed; a lone E5 residual closed in round 3.

**Deliberate deviation from two reviewers, resolved the stronger way:** glm/fable read the `not` mismatch as "trim the teacher notes"; sol read it as under-coverage of the `logical-ops` concept. Resolved by genuinely teaching `not` (lesson beat + exercise 7 + solution), which satisfies all three.

**Limitations:** checkpoint handouts are not PDF-built (build-pdf stays unit-scoped until a real need); no auto-grading (design out-of-scope).

**Follow-ups:**
- Next content slice: unit 05 (Function Factory) + checkpoint 02 territory; the checkpoint pipeline is now reusable.
- Standing: the codex forwarder mangles prompts containing tokens that look like CLI flags (a literal `-p`/model-name fragment triggered a "'pytest' model not supported" 400); phrase content-gate prompts to avoid bare flag-like tokens.
