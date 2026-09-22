# Plan 069 — "Borrowed tools" MECHANISM: policy + schema v2 + cell-aware scanner + tests (no content)

**Origin:** author directive (2026-09-21) to relax Book 1's strict prereq-closure so examples/exercises feel less
toy-like, by allowing future concepts as auxiliary "borrowed tools". **Advisory review:** sol + fable surveyed
Book 1 and converged on the design. **User decisions:** (Q1) scope = mechanism + pilot; (Q2) *lift* u02's
"don't count your guesses" ban; (Q3) pilot = u04 + u08; (Q4, after review) **split tooling from pilot content**.

**This plan (069) ships the MECHANISM ONLY** — governance + design docs + schema v2 + the cell-aware scanner +
a synthetic mutation-test suite + an empty `auxiliary: []` metadata migration. **No student-facing content
changes.** The u04/u08 pilot and the u02 counting-ban lift land in **follow-up plan 070**, which inherits the
design settled here. This split is per [sol]'s plan-review (self-proving tooling via synthetic fixtures, cleanly
reviewable) and the user's Q4 choice.

Creates design authority **`docs/designs/004-borrowed-tools.md`**. Related: [[twins-must-showcase-the-concept]],
design 003 (real-input), design 000. Round-1 review (below) was on a bundled draft; the plan was restructured to
tooling-only per consensus.

## Motivation

Strict prereq closure — "nothing may be used before the unit that introduces it" (`prereq_findings`
curriculum.py:227; `concept_scan` flags any concept used in a code cell outside a unit's
`introduces ∪ requires ∪ practices` union) — forces toy examples. The "borrowed tool" exception lets a future
concept appear as GIVEN, contract-only code the student never writes or is assessed on, earning no teaching
credit. This plan builds and proves the machinery; content follows in 070.

## The design (→ `docs/designs/004-borrowed-tools.md`)

**Core rule.** A future concept may appear in CORE material only as an explicitly-marked **borrowed tool**: given
machinery in a lesson demo or exercise scaffold the student *reads, consumes the output of, or calls* — never
authors, completes, selects, repairs, traces, or explains. It earns **no** teaching credit and **never** advances
teach order. Checkpoints and projects stay strict (`auxiliary: []`).

**Two exception kinds:**
- **(K1) Borrowed black-box tool** — a future *tool* used as given code the student does NOT write (a list
  literal as inert given data; `.split()` in a given input adapter; `len`/`max`/`round` as an opaque call; a
  supplied helper). Appears only inside a **GIVEN region** (exercise) or a `demo`/`real-form`-tagged cell
  (lesson/solution). The student's authored lines use taught concepts only.
  - **Loop-header carve-out ([sol] B2 / [fable] N2):** a `for x in <given collection>:` header that only
    *delivers* a given collection's items is a **data-delivery idiom** (like `input()`), not "control-flow that
    determines the solution". It is legal ONLY when it sits inside the GIVEN region and the student writes the
    loop **body** (which carries the taught concept). A given list literal + its delivering `for x in <it>:`
    header count as **ONE composite borrowed tool** ([fable] N1); declare only the *detectable* id
    (`book1:list-literal`) — `list-loop` is `MANUAL_ONLY` (concept_scan.py:37), invisible to the scanner, so it
    is NOT declared and is exempt from the "declared-but-unused" finding.
- **(K2) Composed-from-taught** — a construct built ENTIRELY from already-taught primitives that the registry
  merely *names* as a later concept, which the student MAY write. **Represented as a CLOSED, non-extensible
  exception table ([sol] B1)**, NOT a general "anything composed" rule (that would be a spine-sized hole). A K2
  entry is `{cell-id, concept-ids, exact-AST-form}`; the scanner authorizes it only when ALL match. The single
  K2 case this mechanism ships (its u02 *content* is deferred to plan 070) is the guess counter: concept ids
  `{book1:loop-counter, book1:accumulator}` (it registers as BOTH — `loop-counter` u03, `accumulator` u04,
  concept_scan.py:223–244), role `composed`, AST form **`name = name + 1`** ONLY (plain-Name target, literal `1`,
  `+`; NOT `+=`, alternate operator, subscript, attribute, or any other form). K2 verifies its primitives are
  already taught, never adds either concept to `seen`/practice/coverage/spiral, and is disjoint from
  checkpoints/projects. Any mutation of entry/concept/cell/role/AST-form fails.

**Eligibility test (K1):** a construct is a borrowed tool only if a reviewer could replace it with its resulting
value (or a named helper call) without changing what the learner must reason about, write, debug, or receive
credit for.

**Never eligible to lead** (spine-protection denylist — auxiliary may not COMPUTE the assessed skill):
find-extreme→`max`/`min`; running-total→`sum`; count-by-condition→`.count`; list-sort→`sorted`;
linear-search→`in`/`.index`; transform-each→comprehensions; the unit's own `introduces` before its lesson;
anything the rubric names or a solution must author/select/modify/explain/trace; control-flow that determines the
solution (`if`, loops [except the delivery carve-out], `break`, `def`/`return`, classes); mutation when mutation
is the skill (`.append`, `.sort`, dict/attr assignment, file writes); error syntax in debug/trace tasks; and ANY
auxiliary in a checkpoint/project. **Already-taught concepts are NOT auxiliaries** — they belong in
`requires`/`practices` (e.g. u04 needs `for-loop` there; source-2 cleanup, plan 070).

**Budget — "one new idea, one borrowed tool" per cell:** ≤ ONE borrowed tool per code cell; it must (a) be a
single call/literal (or the one list+delivery-header composite) with a self-describing name, (b) not sit on the
line carrying the taught concept, (c) be replaceable by a fixed value without changing what the cell teaches,
(d) **never appear in a graduated one-increment build-up rung** (a culminating *put-it-together* cell is not a
build-up rung, but to avoid ambiguity the pilot targets exercises, not lesson ladder rungs — [sol] B2). Same tool
reused across a unit counts as one.

**Borrowed tool ≠ stretch/preview:** stretch is optional and the student MAY write the future construct; a
borrowed tool supports a CORE task but is supplied and contract-only. "Change this / write another / fix / explain"
⇒ it is a preview, not a borrowed tool.

**Marking convention** (learner-facing; extends `**Notice:**`): first local use gets a three-beat callout (≤~25
words): *what it does* · *"you'll own it in Unit N"* (Book-2 variant: *"next year, in Book 2, you'll open this
box"* — [fable] N6) · *"borrow it like `randint`"*. Later uses get a 5-word inline comment. **Never** "advanced /
don't worry / just trust / you don't need to understand". Positive scoping replaces "do not use…" bans. Exercise
scaffolds delimit the given source with GIVEN-region markers (`# GIVEN TOOL — do not edit` … `# your work begins
below`). Teacher notes get a "Borrowed tools in this unit" block (assessed spine + "earns no credit").

## Governance / design amendments (Phase A; human-reviewed — exact wording surfaced for sign-off)

- **`AGENTS.md`** "Self-containedness is law" → add the borrowed-tool carve-out (used-before-taught permitted ONLY
  as a marked, given, no-credit borrowed tool per design 004; taught-before-**assessed** unchanged;
  checkpoints/projects strict).
- **`docs/designs/000-project-design.md` §2** → same carve-out + pointer to 004.
- **NEW `docs/designs/004-borrowed-tools.md`** → the full norm above (K1/K2, loop-header carve-out, closed K2
  table, eligibility, denylist, budget, marking, tooling contract, checkpoint/project exclusion, revision log).
- **`docs/designs/003-book1-real-input.md` v7 ([sol] B4 / [fable] N4):** §4 — fixed-count reads stay the DEFAULT
  idiom, but `.split()` is permitted as a `book2:str-split` borrowed tool per design 004; §2/§5 — solution/lesson
  **real-form markdown fences are now scanned** for auxiliaries (previously deliberately invisible); §6 — add a
  **borrowed-data-twin clause** ([fable] N7): when a fixed-data twin's data is a borrowed list, §6b/§6c parity is
  judged on the loop **body + result line** (not line-for-line loop head), like the §6d fragment oracle, so a
  `for score in scores:` twin may pair with a counted `while`/`input()` real form; §9 revision entry.

## Schema v2 + tooling (Phases B–C)

**Schema v2 ([sol] B5).** Book 1 becomes `map_version: 2` and every Book-1 manifest `blueprint_version: 2`;
validators are **version-dispatched**; **Book 2 stays v1** unchanged. v2 adds an `auxiliary:` field to every
Book-1 coverage-map entry and mirrored unit manifest (checkpoints/projects: `auxiliary: []`, and non-empty is
rejected). Auxiliaries use **qualified ids** (`book1:list-literal`, `book2:str-split`);
`introduces`/`requires`/`practices` keep raw ids. Grammar/validation: qualified-id form, no duplicates,
`auxiliary` disjoint from the three raw fields, manifest↔map `auxiliary` equality. **This plan sets
`auxiliary: []` everywhere (empty migration) — a pure metadata change that keeps ci-local green.**

**Cell metadata (used by content in 070; validated now).** A borrowed-tool cell carries `tags:[auxiliary,
<role>]` with role ∈ `demo` | `given` | `real-form` | `composed` (exactly one), and `py4kids_auxiliary:[<qualified
ids>]`. Neither the entry declaration nor the cell tag alone authorizes; both are required. Malformed metadata
and >1 role fail.

**`prereq_findings` (curriculum.py:227):** exclude `auxiliary` from `(requires ∪ practices) − seen`; never add
`auxiliary` to `seen`; `book1:<id>` home-intro must be *later* than the entry (else it belongs in
requires/practices); `book2:<id>` must have a registered Book-2 owner that is a transitive **dependent** of Book 1
([sol] item 6 — `dependency_baseline(book1)` is empty, so check the cross-book graph directly, books.yaml:8);
reject non-empty `auxiliary` on checkpoints/projects; exclude `auxiliary` from `practice_findings`, checkpoint
coverage, technique-spiral, uniqueness, and the "only-capstone-practices" calc.

**`concept_scan` — cell-aware ([sol] B2/B3, item 6):**
- `code_sources()` (~:428) yields (path, cell index, source, tags, declared auxiliary ids, role); drop the
  entry-wide pre-authorization `used` union (~:484–495) for per-block authorization:
  `block_allowed = baseline ∪ introduces ∪ requires ∪ practices ∪ this-block's-declared-auxiliary`; a future
  concept used OUTSIDE its tagged block still fails. (Entry-wide two-pass helper-definition collection retained.)
- **Parse EVERY Python fence** in governed notebooks — code cells AND markdown fences — then use tags/declarations
  only for *authorization* ([sol] B3 fixes the "scan only tagged fences yet untagged must fail" contradiction).
  A `SyntaxError` in a governed fence now **fails** (not silent `continue`, concept_scan.py:499). Checkpoint/
  project solution fences are included.
- **Global `.split()` recognition:** detect raw `.split()`→`str-split` regardless of active book, resolve to its
  unique qualified owner `book2:str-split`, and **suppress the double "untaught method split" finding** when
  authorized (concept_scan.py:73/373); untagged/unauthorized `.split()` still fails; no `str-split` is registered
  in Book 1 (avoids `global_concept_uniqueness_findings`, curriculum.py:52).
- New findings: undeclared cell auxiliary id; declared-but-unused (MANUAL_ONLY ids exempt — [fable] N1); K1
  auxiliary AST node outside a GIVEN region; GIVEN region not byte-identical between an exercise and its paired
  solution; K2 authorization only for an exact `{cell-id, concept-ids, AST-form, role:composed}` table match.
- The `real-form` cell tag does not exist yet ([fable] N9) — Phase C introduces it (coexists with `no-exec`;
  markdown cells carry `tags`).

## Synthetic mutation-test suite (Phase D — proves the tooling WITHOUT real content)

Tiny fixture notebooks/manifests under `tests/fixtures/` (not Book-1 content) exercising:
- **K1:** future concept passes ONLY inside a declared+tagged GIVEN region; remove the cell tag → fail; remove the
  entry declaration → fail; move the construct outside the GIVEN region → fail; a later entry cannot treat it as
  taught (`seen` unchanged); no practice/spiral credit; checkpoint & project `auxiliary` declarations → fail;
  untagged `.split()` in a Python markdown fence → fail; `book2:str-split` passes without duplicating the
  registry id; exercise vs solution GIVEN regions must be byte-identical; a `SyntaxError` fence → fail.
- **K2 negative matrix:** only the exact `name = name + 1` in the named cell with role `composed` and the two
  declared ids passes; `+=`, alternate operator, subscript/attribute target, a different cell, a different
  concept, or a missing role each → fail; no `seen`/practice/coverage credit.
- **Book-2 isolation:** Book 2 (v1) behavior unchanged; a non-vacuous Book2→Book1 same-process test that extending
  the Book-1 profile does not leak recognition globally.

## Phases
- **A** — governance + design docs (AGENTS.md, design 000 §2, new design 004, design 003 v7). Exact wording drafted
  and surfaced to the user before merge.
- **B** — schema v2 validators (version-dispatched) + the empty `auxiliary: []` migration across every Book-1 map
  entry + manifest; Book 2 stays v1.
- **C** — `prereq_findings` + cell-aware `concept_scan` (parse-all-fences, global `.split()`, roles incl.
  `real-form`/`composed`, K2 closed table, cross-book dependent check).
- **D** — synthetic mutation-test suite (above); wire into ci-local.
- **E** — verification.

### Phase E — verification
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN after the empty migration (pure metadata; no content moved).
- The full mutation matrix passes (each removal/mutation breaks as designed); Book-2 v1 regression green.
- `git diff --name-only $(git merge-base HEAD main)..HEAD` = this plan + AGENTS.md + design 000 + design 004 +
  design 003 + `tools/{curriculum,concept_scan,notebooks}.py` + `tests/**` + every Book-1 `manifest.yaml` +
  `book1/curriculum/coverage-map.yaml`. **No `book1/units/**/*.ipynb` content cell changes** (0 lesson/exercise/
  solution cell edits — this plan changes no examples).

## Out of scope
- **ALL student-facing content changes** → plan 070 (u04 lists-as-given-data + drop over-restriction bans; u08
  `.split()` adapter; u02 counting-ban lift + K2 table entries + teacher-notes). 070 inherits design 004/003-v7.
- Broad enrichment rollout across other units (phased follow-ups after the pilot).
- Book-2 schema migration; checkpoints/projects gaining any auxiliary (stay strict).
- Spine cases that must NOT be relaxed (u01 baseline; u03 unrolled-square→loop; u06 manual scan→`.index`; u07
  find-extreme→`max`; u09 file helpers; trace/predict/debug tasks).
- Not an erratum (a realism/pedagogy improvement). **Verification phase:** Phase E.

## Plan Review

### Round 1 (2026-09-21) — on the bundled draft (28d8306). [self]/[sol]/[fable] reviewed; [glm] timed out.
[self] APPROVE-with-open-questions · [fable] APPROVE-WITH-NITS (N1–N9) · [sol] REJECT (5 BLOCKERs + split
recommendation) · [glm] opencode TIMEOUT (no verdict). Consensus: restructure to **tooling-only** (this plan) +
a pilot-content follow-up (plan 070); user confirmed the split (Q4). All BLOCKERs/nits folded into the design +
tooling contract above. Round-1 verdicts are preserved in git history (commits 218c49e / 015153c).

### Round 2 (2026-09-21) — [self] inline; [sol]/[glm]/[fable] on the restructured tooling-only plan.
#### [self] (2026-09-21)
**APPROVE.** Restructured to mechanism-only per consensus. Folded: [sol] B1 (K2 closed cell-id/AST table),
B2 (loop-header carve-out + list-literal-only declaration + `for-loop`→requires is 070's content concern +
exercises-not-rungs), B3 (parse-all-fences, SyntaxError fails, checkpoint fences), B4 (design 003 v7), B5 (schema
v2 map_version:2/blueprint_version:2 version-dispatched), item 6 (cross-book transitive-dependent + global
`.split()` recognition + Book-2 isolation test), item 7 (split). Folded [fable] N1 (one composite tool +
MANUAL_ONLY exempt), N2, N3 (both K2 ids + composed role), N4, N6, N7 (§6 borrowed-data-twin clause), N9
(real-form tag). Empty migration keeps ci-local green; pilot content deferred to 070.

#### [fable] round 2 (2026-09-21)
**APPROVE WITH NITS** — N1–N9 verified resolved; restructure STRENGTHENED the design. New nits (text folds, no
re-review needed if folded):
- N10: the `Given:`/`Your job:` exercise-statement framing dropped out — restore it in design 004's marking
  convention (070 inherits it). → FOLD.
- N11 (concrete/required): parse-all-fences is RETROACTIVE — 22 existing Book-1 markdown fences flag `input`
  used-but-unlisted (u03 solutions; cp02/cp03/cp04 solutions — the design-003 §5 deliberately-invisible
  real-forms; 0 SyntaxErrors). Phase B empty migration must ALSO add `practices:[input]` to u03/cp02/cp03/cp04
  (map+manifest in sync); design 003 v7 §5 must state the per-unit-audit contingency is superseded (markdown
  real-forms now visible → declare under the General Rule); make explicit the entry-wide two-pass `defined_names`
  collects from markdown fences AND code cells (else method false-positives fire). Still pure metadata; Phase E
  can't be green otherwise. → FOLD.
- N12: synthetic fixtures should mirror the 3 real shapes (exercise+solution GIVEN region byte-identical; lesson
  no-exec+real-form CODE cell; solutions markdown real-form fence). → FOLD.
- N13: callout wording is K1-shaped ("borrow it") — wrong for K2 (the kid BUILT it; "Unit 4 NAMES it"); add a K2
  naming-variant callout + explicitly exempt `composed` from the GIVEN-region requirement. → FOLD.
- precision: `auxiliary` disjointness compares after stripping the `book1:` prefix; "`book1:<id>` home-intro later
  than the entry" uses MAP order, not registry order. → FOLD.
Confirmed sound: book2:str-split resolution (book2 registers str-split + depends_on book1); mechanism fully
judgeable by synthetic fixtures (nothing needs a real example); K2 honesty; checkpoints/projects strict.

#### [sol] (pending)
#### [glm] (pending — opencode)

## Content Review
_(pending)_

## Post-Execution Report
_(pending)_
