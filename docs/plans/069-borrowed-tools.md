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
  entry is `{cell-id, concept-ids, exact-AST-form}`; the scanner authorizes it only when ALL match. 069 ships the K2 MECHANISM with an EMPTY production table; the one real case it will hold — added in plan 070,
  not here — is the guess counter. The pattern is
  curricularly BOTH `loop-counter` (u03) and `accumulator` (u04), but the scanner EMITS only `accumulator`
  (`loop-counter` is MANUAL_ONLY, never emitted — concept_scan.py:222/41), so K2 AUTHORIZES the emitted
  `accumulator` and DECLARES both ids `{book1:loop-counter, book1:accumulator}` for curriculum honesty. Role
  `composed`; AST form **`name = name + 1`** ONLY (plain-Name target, literal `1`, `+`; NOT `+=`, `1 + n`
  operand-swap, alternate operator, subscript, attribute, or any other form). Authorization is **per-statement**
  ([glm] N2 — a second, non-matching accumulator statement in the same cell still fails), never adds either
  concept to `seen`/practice/coverage/spiral, and is disjoint from checkpoints/projects. **069 ships an EMPTY
  production K2 table** ([sol] B1 / [glm] N3) — the mechanism is proven by synthetic fixtures; the actual u02
  cell-ID rows are added in plan 070. The table lives in a versioned registry file
  (`book1/curriculum/k2-exceptions.yaml`, keyed by the notebook's real `cell["id"]`); an entry whose cell-id does
  not exist **fails closed**. `code_sources()` must therefore extract the real `cell["id"]`, not the index.
  Any mutation of entry/concept/cell/role/AST-form fails.

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
below`), and the exercise STATEMENT frames the task as **Given:** (the tool + what it yields) / **Your job:** (the
taught skill) — [fable] N10. **K2 callout variant ([fable] N13):** K2 is NAMED, not borrowed — the honest message
is "you built this counter from a variable and `+ 1`; **Unit 4 gives the pattern a name** (accumulator)", never
"borrow it". A `composed` cell is exempt from the GIVEN-region requirement (the student authored it). Teacher
notes get a "Borrowed tools in this unit" block (assessed spine + "earns no credit"). **Budget enforcement
([glm] N6):** the ≤1-borrowed-tool-per-cell rule is CI-enforced by requiring at most ONE detectable id in
`py4kids_auxiliary` per cell (MANUAL_ONLY ids excluded from the count); >1 detectable id fails.

## Governance / design amendments (Phase A; human-reviewed — exact wording surfaced for sign-off)

- **`AGENTS.md`** "Self-containedness is law" → add the borrowed-tool carve-out (used-before-taught permitted ONLY
  as a marked, given, no-credit borrowed tool per design 004; taught-before-**assessed** unchanged;
  checkpoints/projects strict).
- **`docs/designs/000-project-design.md` §2** → same carve-out + pointer to 004.
- **NEW `docs/designs/004-borrowed-tools.md`** → the full norm above (K1/K2, loop-header carve-out, closed K2
  table, eligibility, denylist, budget, marking, tooling contract, checkpoint/project exclusion, revision log).
- **`docs/designs/003-book1-real-input.md` v7 ([sol] B4 / [fable] N4):** §4 — fixed-count reads stay the DEFAULT
  idiom, but `.split()` is permitted as a `book2:str-split` borrowed tool per design 004; §2/§5 — solution/lesson
  **real-form markdown fences are now scanned ONLY for borrowed tools** ([glm] B1, SUPERSEDES [fable] N11): an
  untagged/undeclared `.split()` (or other borrowed tool) in a real-form fence fails, but the GENERAL
  used-but-unlisted closure stays CODE-CELL-ONLY, so §5's deliberate invisibility of real-form markdown is
  PRESERVED (no `practices:[input]` adds, no checkpoint edits); §6 — add a
  **borrowed-data-twin clause** ([fable] N7): when a fixed-data twin's data is a borrowed list, §6b/§6c parity is
  judged on the loop **body + result line** (not line-for-line loop head), like the §6d fragment oracle, so a
  `for score in scores:` twin may pair with a counted `while`/`input()` real form; §9 revision entry stating v7 SUPERSEDES v6's `.split()` rejection (this plan IS the shared-tool change v6 said was required).

## Schema v2 + tooling (Phases B–C)

**Schema v2 ([sol] B5).** Book 1 becomes `map_version: 2` and every Book-1 manifest `blueprint_version: 2`;
validators are **version-dispatched**; **Book 2 stays v1** unchanged. v2 adds an `auxiliary:` field to every
Book-1 coverage-map entry and mirrored unit manifest (checkpoints/projects: `auxiliary: []`, and non-empty is
rejected). Auxiliaries use **qualified ids** (`book1:list-literal`, `book2:str-split`);
`introduces`/`requires`/`practices` keep raw ids. `auxiliary` lives as a top-level `concepts.auxiliary` list in
the manifest (mirroring the map entry). Grammar/validation: qualified-id form, no duplicates, `auxiliary` disjoint
from the three raw fields AFTER stripping the `book1:` prefix ([sol] B5 / [glm] N5 — `book1:list-literal` vs raw
`list-literal`), manifest↔map `auxiliary` equality, and cross-version consistency (a v2 manifest under a v1 map or
vice-versa fails; v2 REQUIRES the `auxiliary` key on every entry, v1 FORBIDS it). The `book1:<id>` home-intro
check uses MAP order (not registry order). **This plan sets
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
- **"Governed" = every notebook the map/manifests own** (Book-1 units + checkpoints + projects). In governed
  notebooks: CODE cells get the FULL closure + per-block authorization (as today, now cell-aware). MARKDOWN
  Python fences are parsed for `SyntaxError` (which now **fails**, not silent `continue` at concept_scan.py:503)
  and scanned **ONLY for borrowed tools** — declared auxiliary ids + globally-recognized tools like `.split()`;
  the GENERAL used-but-unlisted closure does NOT apply to markdown ([glm] B1 — this preserves design-003 §5
  invisibility; a taught-but-unlisted concept like `input` in a real-form fence does NOT fail). Checkpoint/project
  fences are scanned under this same borrowed-tools-only rule (they may hold none — `auxiliary: []`).
- **Global `.split()` recognition:** detect raw `.split()`→`str-split` regardless of active book, resolve to its
  unique qualified owner `book2:str-split`, and **suppress the double "untaught method split" finding** when
  authorized (concept_scan.py:73/373); untagged/unauthorized `.split()` still fails; no `str-split` is registered
  in Book 1 (avoids `global_concept_uniqueness_findings`, curriculum.py:52).
- New findings: undeclared cell auxiliary id; declared-but-unused (MANUAL_ONLY ids exempt — [fable] N1); **in an
  EXERCISE**, a K1 auxiliary AST node outside a GIVEN region ([sol] G1 — lesson `demo`/solution `real-form` cells
  authorize via cell tag + declaration ALONE, no GIVEN region, so the u08 real-form is not rejected); GIVEN region
  not byte-identical between an exercise and its solution, paired by a **stable shared task id declared on both
  cells** ([sol] G2 — never positional); K2 authorization only for an exact `{cell-id, concept-ids, AST-form,
  role:composed}` per-statement table match.
- The `real-form` cell tag does not exist yet ([fable] N9) — Phase C introduces it (coexists with `no-exec`;
  markdown cells carry `tags`).

## Synthetic mutation-test suite (Phase D — proves the tooling WITHOUT real content)

Tiny fixture notebooks/manifests under `tests/fixtures/` (not Book-1 content), mirroring the **three real
content shapes** ([fable] N12) so plan 070 authors against a proven shape — (i) an exercise + paired solution with
a GIVEN region (byte-identical, paired by task id), (ii) a lesson `no-exec` + `real-form` CODE cell, (iii) a
solutions MARKDOWN `real-form` fence — exercising:
- **K1:** future concept passes ONLY inside a declared+tagged GIVEN region; remove the cell tag → fail; remove the
  entry declaration → fail; move the construct outside the GIVEN region → fail; a later entry cannot treat it as
  taught (`seen` unchanged); no practice/spiral credit; checkpoint & project `auxiliary` declarations → fail;
  untagged `.split()` in a Python markdown fence → fail; `book2:str-split` passes without duplicating the
  registry id; exercise vs solution GIVEN regions must be byte-identical; a `SyntaxError` fence → fail.
- **K2 negative matrix:** only the exact `name = name + 1` in the named cell with role `composed` and the two
  declared ids passes; `+=`, the `n = 1 + n` operand-swap, an alternate operator, a subscript/attribute target, a
  different cell, a different concept, or a missing role each → fail; **per-statement lock** — one valid K2
  statement PLUS a second, non-matching `accumulator` statement in the SAME cell → the cell still fails (proves
  authorization is per-statement, not cell-wide); no `seen`/practice/coverage credit.
- **Book-2 isolation:** Book 2 (v1) behavior unchanged; a non-vacuous Book2→Book1 same-process test that extending
  the Book-1 profile does not leak recognition globally.
- **Markdown-scope lock ([glm] B1):** a markdown Python fence using a taught-but-unlisted concept (e.g. `input`)
  does NOT fail; an untagged/undeclared `.split()` in a markdown fence DOES fail.
- **Schema/metadata ([sol] B5 / [glm] N5/N6):** malformed/duplicate/unqualified `py4kids_auxiliary`; zero /
  multiple / wrong role; `auxiliary` overlapping requires/practices (after prefix-normalize); v2-manifest-under-v1-map
  (and vice-versa); a map↔manifest auxiliary-VALUE mismatch (same entry, different `auxiliary` lists) → fail;
  >1 detectable auxiliary id in one cell (budget) → fail; a missing/duplicate pairing id → fail.
- **prereq edges:** `book1:<id>` home-intro NOT later than the entry → fail; `book2:<id>` owner missing or not a
  transitive dependent of book1 → fail; declared-but-unused (with MANUAL_ONLY exemption verified).
- **Existing v1 tests ([glm] N1):** update the v1-hardcoded assertions (test_tools.py:623-624/913/1050; the v1
  fixtures in test_patterns/test_concept_scan/test_book2_tooling) to version-dispatch; they stay green ONLY if the
  v1 path is byte-preserved — a locked regression.

## Phases
- **A** — governance + design docs (AGENTS.md, design 000 §2, new design 004, design 003 v7). Exact wording drafted
  and surfaced to the user before merge.
- **B** — schema v2 validators (version-dispatched: Book-1 `map_version:2`/`blueprint_version:2`, Book 2 v1) + the
  empty `auxiliary: []` migration across every Book-1 map entry + manifest; **update the existing v1-hardcoded
  tests to version-dispatch** ([glm] N1). NO `practices:[input]` adds — the markdown general-closure invisibility
  is preserved by the narrow markdown scan (Phase C), so the migration stays pure metadata.
- **C** — `prereq_findings` + cell-aware `concept_scan` (parse-all-fences, global `.split()`, roles incl.
  `real-form`/`composed`, K2 closed table, cross-book dependent check).
- **D** — synthetic mutation-test suite (above); wire into ci-local.
- **E** — verification.

### Phase E — verification
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN after the empty migration (pure metadata; no content moved).
- The full mutation matrix passes (each removal/mutation breaks as designed); Book-2 v1 regression green.
- `git diff --name-only $(git merge-base HEAD main)..HEAD` = this plan + AGENTS.md + design 000 + design 004 +
  design 003 + `tools/{curriculum,concept_scan,notebooks}.py` + `tests/**` + every Book-1 `manifest.yaml` +
  `book1/curriculum/coverage-map.yaml` + the new `book1/curriculum/k2-exceptions.yaml` (empty table). **No `book1/units/**/*.ipynb` content cell changes** (0 lesson/exercise/
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

#### [sol] round 2 (2026-09-21)
**REJECT** — narrowed to precise tooling-contract gaps (B2/B3/B4/item6/item7 RESOLVED). To fold, then re-verify:
- B1 (K2) not resolved: (a) inconsistency — 069 ships the K2 MECHANISM with an EMPTY production table (proven by
  synthetic fixtures); the u02 cell-ID rows are added in 070 (reword the "one case ships now" line). (b)
  `code_sources()` must extract the notebook's real `cell["id"]` — K2 keys on it, not the index. (c) "registers as
  BOTH" is FALSE for the scanner: `loop-counter` is MANUAL_ONLY (never emitted), only `accumulator` is emitted
  (concept_scan.py:222) — so K2 AUTHORIZES the emitted `accumulator` and DECLARES both ids for curriculum honesty
  (loop-counter is never flagged anyway).
- G1 (blocking): the "reject K1 AST node outside a GIVEN region" rule would wrongly reject the planned u08
  real-form cell → qualify GIVEN-regions as **exercise-only**; lesson `demo`/solution `real-form` cells authorize
  via cell tag + declaration alone (no GIVEN region).
- G2 (blocking): "paired solution" undefined → define a deterministic PAIRING KEY (a stable task/cell id shared by
  the exercise scaffold and its solution) for the byte-identical GIVEN-region check; no positional pairing.
- B5 gaps: `auxiliary` disjointness must compare after normalizing the `book1:` prefix (= [fable] precision);
  Phase D must add malformed/duplicate `py4kids_auxiliary`, zero/multiple/wrong role, declared-but-unused +
  MANUAL_ONLY-exempt, TWO K1 tools in one cell (budget enforcement), map↔manifest version + auxiliary-field
  mismatch, and missing/duplicate pairing-id mutations.
Phase E scope claim confirmed correct (empty migration edits manifests + coverage-map, not notebook cells).

#### [glm] round 2 (2026-09-21)
**REJECT** — one blocker (B1); "everything else approve-quality"; verified end-to-end vs code. Fold:
- B1 (blocker, SUPERSEDES [fable] N11): applying the FULL closure to markdown fences breaks Phase E — 20 existing
  fences (u03/cp02/cp03/cp04) fail on `input`, 15 in checkpoints where the plan FORBIDS edits (no in-plan remedy).
  Fix: markdown fences are parsed for SyntaxError and scanned ONLY for BORROWED TOOLS (declared auxiliary ids +
  globally-recognized tools like `.split()`); the general used-but-unlisted closure stays CODE-CELL-ONLY,
  preserving design-003 §5 invisibility (NO `practices:[input]` adds, NO checkpoint edits). Define "governed" +
  add locking test "a markdown fence using a taught-but-unlisted concept (input) does NOT fail". [fable] N11's
  practices-add approach is DROPPED.
- N1: existing v1-hardcoded tests (test_tools.py:623-624/913/1050; v1 fixtures in test_patterns/concept_scan/
  book2) → Phase B owns updating them to version-dispatch (locked tests).
- N2: K2 authorization is PER-STATEMENT (cell-level would let a 2nd non-matching accumulator in the same cell
  slip) → add that mutation.
- N3: state the K2 table's storage location + amendment path; a table entry whose cell-id doesn't exist fails
  CLOSED (forces 069 to ship an EMPTY production table; = [sol] B1a).
- N4: add operand-swap `n = 1 + n` to the K2 negative matrix.
- N5: state where `auxiliary` lives in the manifest (top-level vs under `concepts`); a v2 manifest under a v1 map
  (or vice-versa) fails; v2 requires `auxiliary`, v1 forbids it.
- N6: the "≤1 borrowed tool per cell" budget has NO tooling finding → state it is CI-enforced via
  `py4kids_auxiliary` length (≤1 detectable id) or explicitly reviewer-manual.
- design 003 v7 §9 entry must say it SUPERSEDES v6's `.split()` rejection (this plan IS the shared-tool change).
Verified sound: empty migration ci-local-green (only map_schema/manifest read the changed surfaces, version-
dispatched); dependency_baseline(book1) empty so reverse-graph dependent check works; book2:str-split end-to-end
(owner book2 unit-01, depends_on book1); K2 ids correct; Phase-E scope claim correct.

### Round 3 (2026-09-21) — re-verify [sol] + [glm] REJECTs (all round-2 findings folded; [fable] r2 nits folded, no re-review needed).
#### [sol] round 3 (2026-09-21)
**REJECT** — G1/G2/[glm]-B1-markdown all RESOLVED; 4 tiny text fixes remain:
- B1a: the K2 paragraph still reads as if the guess-counter case "ships" — reword to "the MECHANISM ships (empty
  production table); the u02 rows come in 070".
- B1b: Phase-E changed-file allowlist must include the new `book1/curriculum/k2-exceptions.yaml`.
- B1c: Phase D must add the explicit per-statement LOCK — one valid K2 statement PLUS a second non-matching
  accumulator statement in the SAME cell → fail (proves per-statement, not cell-wide, authorization).
- B5: Phase D must add the map↔manifest auxiliary-VALUE mismatch mutation (only the invariant + version-mismatch
  are present today).

#### [glm] round 3 (2026-09-21)
**APPROVE WITH NITS** — B1 resolved (empirically: exactly 20 input-fences, 0 SyntaxErrors, 0 `.split()` in book1
→ empty-migration Phase E green); the 4 must-fold residuals were identical to [sol]'s and are now folded.

#### [sol] round 4 / final (2026-09-21)
**APPROVE** — all 4 round-3 residuals confirmed resolved (B1a K2-mechanism-empty-table, B1b k2-exceptions.yaml in
allowlist, B1c per-statement lock, B5 map↔manifest value-mismatch + `1+n` operand-swap).

### Plan-review outcome: **FULL 4-way consensus** — [self]/[sol] APPROVE · [fable]/[glm] APPROVE-WITH-NITS (all
folded). 3 review rounds (r1 bundled draft → restructured to tooling-only per user Q4; r2/r3 tightened the tooling
contract). Gate CLOSED → Phase A (governance wording surfaced to the user for sign-off before merge).

## Content Review

4-way gate on the TOOLING (plan 069 ships no notebook content; per `docs/content-review-gate.md`, tooling changes
get a conventional code review by the same roster). Reviewers audit commit `7d34f91` (Phases B–D) against
`docs/designs/004-borrowed-tools.md §8`.

### Review 1 — [self] (2026-09-22)
- **Verdict**: APPROVE
Read the full diff of `tools/curriculum.py`, `tools/notebooks.py`, `tools/concept_scan.py` (not just the tests) and
confirmed each design-004 §8 clause:
1. Schema v2 is fail-closed and version-dispatched — `map_schema_findings`/`manifest_findings` reject a v2 manifest
   under a v1 map and vice-versa (`blueprint_version != map_version`), v2 requires `auxiliary` on every entry
   (`MAP_ENTRY_KEYS`/`MANIFEST_CONCEPT_KEYS` exact-set), v1 forbids it, `map_version 2` is book1-only,
   checkpoints/projects reject non-empty `auxiliary`, `auxiliary` is disjoint from introduces/requires/practices
   after stripping `book1:`, and manifest↔map auxiliary values must agree.
2. `_auxiliary_prereq_findings` excludes `auxiliary` from `(requires∪practices)−seen`, never adds it to `seen`,
   requires a book1 aux home strictly LATER than the entry in MAP order (`home_index <= index` fails), and requires
   a book2 aux to resolve to a registered Book-2 owner that is a transitive DEPENDENT of Book 1.
3. `concept_scan` is cell-aware; **markdown Python fences are scanned ONLY for borrowed tools** — the markdown
   branch flags undeclared borrowed tools then `continue`s BEFORE the general `used − block_allowed` closure, which
   therefore stays code-cell-only (design-003 §5 real-form-markdown invisibility preserved). SyntaxError in a fence
   still fails; backtick+tilde+indented+language-attributed fences parse (`_python_fences`). An undeclared FUTURE
   Book-1 concept in a fence fails by map order (`future_concepts`).
4. `.split()` → `book2:str-split` recognized globally; the duplicate "untaught method split" is suppressed only when
   the block is authorized; undeclared/untagged `.split()` still fails.
5. K2 loader is closed/non-extensible (`_load_k2` fixes keys, concept-id set, `exact-ast-form == "name = name + 1"`,
   role `composed`), authorization is PER STATEMENT (`_exact_counter_statement` requires `name = name + 1` exactly —
   `type(x) is int` excludes bool, rejects `+=`, `1 + n`, subscript/attr; a second non-matching accumulator
   statement in the cell defeats `all(_exact_counter_statement)` → the cell fails), and a stale/duplicate cell-id
   fails closed (`all_cell_ids.count(...) != 1`). Shipped table is empty.
6. One-tool budget enforced (`_metadata_findings`: >1 detectable id → fail; MANUAL_ONLY excluded). GIVEN regions are
   byte-identical, paired by `py4kids_task_id` not position, and GIVEN enforcement is exercise-only; lesson demo /
   solution real-form authorize by tag+declaration.
7. Book 2 (v1) routes to `_legacy_scan_findings`, preserving pre-069 behavior and finding text byte-for-byte.
Verification: `TMPDIR=/dev/shm bash scripts/ci-local.sh` → **ALL GREEN** in this kernel-capable env (the codex
build sandbox's 11 Jupyter `socket()` failures were pure sandbox artifacts — cleared here); 93 borrowed-tools tests
pass; full non-execution suite green.
Nit (Nice-to-Have, non-blocking): the exercise GIVEN path calls `detect()` twice per block (once for `used`, once via
`_borrowed_occurrences`); a minor efficiency cost only.

### Review 2 — [fable] (2026-09-22)
- **Verdict**: APPROVE WITH NITS
Verified §8 items 1–6 in code (not just tests); ran the four touched test modules (478 passed) and direct scanner
probes. Confirmed markdown-borrowed-only `continue`, fail-closed schema/K2/prereq, byte-identity GIVEN pairing, and
the v1 legacy path. Also flagged the markdown scan is *stricter* than §8 (future Book-1 concepts flagged) — a good
fail-closed deviation to record in design 004's revision history.
1. `[OPEN]` Should Fix — `concept_scan.py:~1054` entry-wide method-profile widening is **fail-open**: a
   method-bearing borrowed concept (e.g. `book2:set-ops`) declared on one cell adds its methods (`.remove` etc.) to
   the untaught-method whitelist for EVERY block of the entry, so an undeclared sibling cell using that method passes
   silently. Fix: compute unknown-methods per block against only that block's declared owner concepts.
2. `[OPEN]` Should Fix — Book-2 **syntax** features (comprehension, tuple-unpack, set literal) are invisible in
   Book-1 code cells because `add_feature` gates on `entry_registered`; an undeclared comprehension in a Book-1 cell
   yields no finding, though §4 denylists comprehensions. Pre-069 behavior, but 069 claims closure over borrowed
   Book-2 tools. Fix: for v2 books, treat the dependent book's *feature* ids like `str-split` (global recognition +
   required declaration).
3. `[OPEN]` Should Fix — `concept_scan.py:~1088` per-fence "declared auxiliary … is unused" on multi-fence markdown
   cells: metadata is per cell but a `_Block` is emitted per fence, so a two-`python`-fence real-form cell where only
   the second uses `.split()` fails on the first. Latent (0 such cells today) but blocks the design-003 "fixed-data
   + real form in one markdown cell" shape. Fix: aggregate `used` across a cell's fences before the unused check.
4. `[OPEN]` Nice to Have — markdown future-concept branch (~1124) doesn't subtract `never_flag`, so `int()`/`True`
   in a fence would fail as `book1:type-conversion`/`boolean` though the same code cell is exempt. Filter through
   `never_flag`.
5. `[OPEN]` Nice to Have — fences with info `python3`/`py3`/`{.python}`/none are not scanned; an author could hide
   `.split()` in a bare fence. (No live slip: 222 untagged fences hold only text/output.)
6. `[OPEN]` Nice to Have — an unclosed NON-python fence swallows later python fences in the cell; report any unclosed
   fence, not only python ones.
7. `[OPEN]` Nice to Have — a `no-exec` unit code cell with a SyntaxError is silently dropped from closure; a
   deliberately unparsable no-exec cell routes around the scanner. Require no-exec cells to parse, or emit a finding.
8. `[OPEN]` Nice to Have — K2 cell-ids must be book-globally-unique (fail-closed, good), but Book 1 reuses 105 ids
   across notebooks and has 2 true within-notebook duplicates (u02 solutions `u2-ex8-heading`/`u2-ex8-code`);
   document the uniqueness requirement + add a separate nbformat-duplicate hygiene check.
9. `[OPEN]` Nice to Have — an entry-level `auxiliary` id no cell declares is never flagged (only cell-level unused
   is), yet it widens `entry_registered`/profile. Add an entry-level "declared by entry, by no cell" finding.
10. `[OPEN]` Nice to Have — asset `.py` is read twice (source + parse); harmless.

### Review 3 — [sol] (2026-09-22)
- **Verdict**: REJECT
Adversarial probes reproduced three gaps (138 borrowed-tool/prereq/pattern tests pass; the probes below are the
holes those tests miss).
1. `[OPEN]` Must Fix — `concept_scan.py:~1054` entry-level auxiliary widens the untaught-method whitelist for every
   cell in the entry. Declaring `book2:set-ops` on one cell lets an undeclared sibling's `other.remove(2)` pass
   silently (detection only emits `set-ops` for a statically-recognized set receiver). Violates cell-local
   authorization. **(Same as [fable] #1 — corroborated.)**
2. `[OPEN]` Must Fix — `concept_scan.py:~664,~1147` K2 is not fully per-statement / exact-form: candidate collection
   considers only `Assign`/`AugAssign`, so an annotated (`m: int = m + 1`) or walrus (`(m := m + 1)`) second
   accumulator is never examined — the valid first statement authorizes cell-level `accumulator` while the
   non-matching second slips. Violates "`name = name + 1` only; any second non-matching accumulator fails".
3. `[OPEN]` Must Fix — `concept_scan.py:~1198,~1234` every auxiliary SOLUTION code cell is forced to carry
   `py4kids_task_id` and an exercise partner; a standalone `auxiliary, real-form` solution code cell with authorized
   `.split()` fails "requires py4kids_task_id". §8 says solution real-form authorizes via tag+declaration alone
   (pairing is exercise-GIVEN-only); markdown real-forms already bypass this, so authorization is representation-
   dependent. Contract violation.

### Review 4 — [glm] (2026-09-22)
- **Verdict**: NO VERDICT (opencode invocation timed out after 1200 s, SIGTERM — known [glm]/opencode flakiness;
  see [[book1-real-input]]). Re-dispatched in the re-review round. If it fails again at the final consensus point,
  the 3-of-4 merge decision goes to the user (as at the u10 content gate).

### Author disposition (round 1 → fix pass, 2026-09-22)
Pre-fix probe: **0** Book-1 code cells use comprehensions / tuple-unpacking / set literals / dict-comps (AST scan),
so [fable] #2 (globally recognize Book-2 syntax features) is a safe, no-false-positive closure — folding it.
Folding as code fixes (codex, tooling dispatch): [sol] #1/#2/#3 (Must), [fable] #1 (=[sol] #1), #2, #3 (Should),
and cheap/safe Nice-to-Haves #4 (never_flag in markdown branch), #5 (accept `python3`/`py3` info strings), #6
(report unclosed non-python fences), #7 (flag no-exec code cells with SyntaxError), #9 (entry-declared-but-no-cell).
Deferring with reason: [fable] #8 second half (a general nbformat within-notebook duplicate-cell-id hygiene check,
incl. the pre-existing u02 `u2-ex8-*` duplicates) is a distinct hygiene concern → tracked follow-up, not 069; the
K2 book-global-uniqueness *requirement* is documented in design 004 §8. [fable] #10 (asset double-read) folded if
trivial. Each Must-Fix gets a dedicated regression test.

### Round-1 resolution (fix commit; codex GPT-5.6-sol per tooling dispatch; 2026-09-22)
All changes confined to `tools/concept_scan.py` + `tests/test_borrowed_tools_scan.py` (no notebook/manifest/map
edits). `TMPDIR=/dev/shm bash scripts/ci-local.sh` → **ALL GREEN**; 107 borrowed-tools tests pass; 12 new
regressions (≥1 per Must-Fix). Codex's own TDD review caught + fixed two extra edge cases (annotation-only
`m: int = ...` is not an accumulator; a same-cell exercise authorization leak).
- [sol] #1 / [fable] #1 → `[FIXED]` — method-whitelist widening is now per validated cell (owner-concept method
  profile scoped to the declaring cell, plus GIVEN-region method enforcement in exercises). Tests
  `test_method_profile_authorization_is_cell_local`, `test_exercise_method_authorization_is_limited_to_given_region`.
- [sol] #2 → `[FIXED]` — accumulator-candidate collection now includes `AnnAssign` + `NamedExpr` (walrus) at both
  sites; any non-exact second accumulator fails the cell; annotation-only assignment is not an accumulator. Tests
  `test_k2_rejects_non_exact_accumulator_node_types`, `test_annotation_only_statement_is_not_an_accumulator`.
- [sol] #3 → `[FIXED]` — solution real-form CODE cells authorize by tag+declaration alone; task_id/pairing required
  only when the solution cell contains a GIVEN region. Test
  `test_solution_real_form_without_given_region_needs_no_pairing_id`.
- [fable] #2 → `[FIXED]` — for v2 books the dependent book's feature ids (kind≠technique) are globally recognized in
  detection and must be declared as borrowed tools (undeclared comprehension/tuple/set in a Book-1 cell now fails).
  Verified 0 false positives (0 existing Book-1 cells use these). Tests
  `test_dependent_book_feature_requires_cell_declaration`, `test_dependent_book_feature_is_authorized_in_paired_given_region`.
- [fable] #3 → `[FIXED]` — markdown `used` is aggregated across a cell's python fences before the unused check.
  Test `test_markdown_unused_check_aggregates_all_fences_in_cell`.
- [fable] #4 → `[FIXED]` — markdown future-concept branch subtracts `never_flag` (`test_markdown_manual_only_future_concept_is_not_flagged`).
- [fable] #5 → `[FIXED]` — `python3`/`py3` fence info strings are scanned (`test_python3_markdown_fence_is_scanned_for_borrowed_tools`).
- [fable] #6 → `[FIXED]` — unclosed non-python fences fail closed (`test_unclosed_non_python_markdown_fence_fails_closed`).
- [fable] #7 → `[WONTFIX]` — flagging a `no-exec` code cell with a SyntaxError would break valid shipped content:
  Unit 1 *intentionally* ships two `no-exec` SyntaxError cells for debug/predict-the-error lessons. Correct skip.
- [fable] #8 → `[FIXED]` (first half: K2 cell-ids must be book-globally-unique — already enforced fail-closed;
  requirement documented) / `[WONTFIX]`-deferred (second half: a general nbformat within-notebook duplicate-cell-id
  hygiene check, incl. pre-existing u02 `u2-ex8-*` dups — distinct follow-up, out of 069 mechanism scope).
- [fable] #9 → `[FIXED]` — entry-level "declared by entry, by no cell" auxiliary finding added
  (`test_entry_auxiliary_must_be_declared_by_a_cell`).
- [fable] #10 → `[WONTFIX]` — asset double-read is a harmless micro-perf nit; left as-is.
All `[OPEN]` findings resolved (FIXED or WONTFIX-with-reason). Re-review round (4-way) follows on the fixed tree.

### Re-review round 2 — [self] (2026-09-22)
- **Verdict**: APPROVE
Read the full `git diff 7d34f91 b7eb731 -- tools/concept_scan.py`. All three [sol] Must-Fixes are structurally
closed: (1) the entry-wide `entry_profile` is removed — each block now uses `block_profile` from only its own
validated `declared`, and exercise GIVEN-region method enforcement adds any borrowed method used OUTSIDE the region
back to `methods`; (2) `_is_accumulator_statement` + both candidate collections now include `AnnAssign`/`NamedExpr`,
with a `value is None` guard so annotation-only `m: int` is not an accumulator; (3) the solutions branch computes
`region` first and only requires `task_id`/pairing when a GIVEN region is present, so a standalone real-form solution
code cell authorizes by tag+declaration alone. [fable] #2 generalizes str-split into `_dependent_feature_owners`
(book2 feature ids, kind≠technique); codex added a `visit_Tuple` guard so Book-1-owned `for k,v in d.items()` and
`return a,b` are not mis-flagged as `book2:tuple` (the reason ci-local stayed green). Verified NO double-finding
regression from removing `methods.discard("split")`: `taught_methods` gains `split` whenever str-split is registered
(concept_scan.py:94), and str-split is always registered now, so `.split()` never enters `unknown_methods` — it
emits the `str-split` concept and flows through the single general "undeclared borrowed tool" path; authorized
str-split fixtures are among the 107 passing tests. `TMPDIR=/dev/shm bash scripts/ci-local.sh` → ALL GREEN.
No new holes found in the delta.

### Re-review round 2 — [fable] (2026-09-22)
- **Verdict**: APPROVE WITH NITS
Read the full delta + current file end-to-end; ran a 25-scenario scratchpad probe calling `concept_scan_findings`
directly; `tests/test_borrowed_tools_scan.py` 89 passed; real `concept_scan_findings(repo,"book1")` and `"book2"`
both `[]`; verified book1∩book2 concept ids = ∅ and no Book-2 id collides with MANUAL_ONLY. All 3 prior Should-Fixes
RESOLVED (method-profile now per-cell incl. GIVEN-scoped method enforcement; Book-2 syntax closure over the 8
detectable feature ids with no over-flag and no fail-open on wrong-id; multi-fence markdown aggregation emits exactly
one unused finding). Nice-to-Haves #4/#5/#6/#9 RESOLVED; #7 WONTFIX reasoning confirmed SOUND (located the two
intentional Unit-1 broken no-exec cells: exercises cell `exercise-two-broken`, lesson cell `8a9940ed`). Three new
non-blocking nits (all fail-closed or fail-silent-narrow):
1. `[OPEN]` Low (pre-existing) — a markdown cell tagged `auxiliary`/`real-form` with `py4kids_auxiliary` but ZERO
   python fences produces no `_Block`, so its metadata/declaration is never validated (only caught by the entry-level
   #9 check when no other cell declares the id). No untaught code slips (there is no fence to authorize). Suggest
   emitting one empty markdown block for a governed markdown cell carrying auxiliary metadata.
2. `[OPEN]` Low (latent) — `_dependent_feature_owners` (~824) doesn't exclude ids also registered in the scanned
   book; today book1∩book2=∅ so unreachable, and a future collision fails LOUD (fail-closed) but with misleading
   text. A one-line guard / explicit registry-collision finding would self-explain.
3. `[OPEN]` Trivial — the exercise borrowed-method loop (~1283) adds to `methods` after `methods -= defined_names`,
   so an entry-defined `def add` called as `obj.add()` outside GIVEN would be reported. Fail-closed; asymmetry note.

### Re-review round 2 — [sol] (2026-09-22)
- **Verdict**: REJECT
All three prior Must-Fixes confirmed RESOLVED by adversarial probe (cell-local method auth incl. same-cell
below-GIVEN; K2 rejects annotated + walrus second accumulators, standalone `m: int` clean; solution real-form with
no GIVEN region passes, GIVEN-whitespace mismatch still fails). ONE new blocking finding:
1. `[OPEN]` Must Fix — `concept_scan.py:424,~1126` the generalized dependent-feature recognition treats every bare
   `Name("deque")` as use of `book2:deque` regardless of binding. Valid Book-1 code `deque = 1` / `print(deque)`
   now emits `undeclared borrowed tool book2:deque` (returned `[]` at 7d34f91) — a newly introduced CI false
   positive violating the scanner's precision-first contract. (The opposite-direction miss `import deque as Queue`
   predates the delta; out of scope.) Confirmed live: `detect("deque = 1\nprint(deque)")` → used includes `deque`.

### Re-review round 2 — [glm] (2026-09-22)
- **Verdict**: NO VERDICT (opencode timed out after 1200 s, SIGTERM — again; [glm]/opencode has now mechanically
  failed BOTH round 1 and round 2 despite a tightened single-commit prompt). Per [[book1-real-input]], a 3-of-4
  merge on [self]+[sol]+[fable] consensus requires explicit user OK; that decision will be surfaced at the final
  consensus point if [glm] remains the sole blocker.

### Author disposition (round 2 → fix pass, 2026-09-22)
Round-2 verdicts: [self] APPROVE · [fable] APPROVE WITH NITS (N1–N3, non-blocking, fail-closed) · [sol] REJECT
(deque false positive, blocking) · [glm] pending. [sol]'s deque finding is a genuine precision regression (bare-Name
`visit_Name` trigger at :424, previously gated out for Book 1). Folding as one codex pass: the deque fix (recognize
`book2:deque` only via a `deque(...)` call / attribute + the existing `appendleft`/`popleft` methods, NOT a bare
Name; audit the other 7 detectable feature ids for analogous bare-identifier over-detection) plus [fable] N1
(validate fence-less declared markdown cells), N2 (dependent-feature registry-collision guard/clarity), N3 (subtract
`defined_names` from the GIVEN-scoped borrowed-method additions). Each gets a regression test.

### Round-2 resolution (fix commit f166a5e; codex GPT-5.6-sol; 2026-09-22)
All in `tools/concept_scan.py` + tests. `TMPDIR=/dev/shm bash scripts/ci-local.sh` → ALL GREEN; 113 focused tests
pass; live book1/book2 scans `[]`; bare-deque probe `[]` while `deque(...)` still detected.
- [sol] r2 #1 (deque FP) → `[FIXED]` — `visit_Name` deque trigger removed; `book2:deque` now recognized only via a
  `deque(...)` call / `<x>.deque` attribute (+ existing `.appendleft()`/`.popleft()`). 7-feature bare-identifier
  audit: none over-detect. Tests `test_bare_deque_identifier_is_not_a_borrowed_tool`,
  `test_undeclared_deque_constructor_is_a_borrowed_tool`, `test_attributed_deque_constructor_is_detected`.
- [fable] r2 N1 → `[FIXED]` — fence-less governed markdown cells carrying auxiliary metadata emit an empty block so
  metadata + unused checks run (`test_fenceless_declared_markdown_cell_reports_unused_auxiliary`).
- [fable] r2 N2 → `[FIXED]` — `_dependent_feature_owners` excludes ids also registered in the scanned book (defers
  to local concept, fail-closed) (`test_scanned_book_concept_wins_dependent_registry_collision`).
- [fable] r2 N3 → `[FIXED]` — post-GIVEN borrowed-method additions exclude entry-defined names
  (`test_entry_defined_borrowed_method_is_not_untaught_outside_given`).

### Re-review round 3 — [self] (2026-09-22)
- **Verdict**: APPROVE
Read `git diff b7eb731 f166a5e`. All four fixes structurally correct (deque call/attr-only; N1 empty-block only when
`not fences and has_auxiliary_metadata` so a fenced declared cell is unaffected; N2 `registered`-exclusion guard
fail-closed; N3 `defined_names` exclusion doesn't over-suppress a genuinely untaught method). Verified live: bare
`deque` not a feature, `deque()` still detected; ci-local ALL GREEN.

### Re-review round 3 — [fable] (2026-09-22)
- **Verdict**: APPROVE (no blocking findings)
Probed each fix via scratchpad fixtures; `uv run ruff` clean; full `uv run pytest` 651 passed; focused scan module
95 passed; live book1/book2 scans `[]`. N1 RESOLVED (empty block flows through metadata + unused checks; no
over-flag on fenced declared cells or plain prose; empty-block cell-id only tightens the K2 `count==1` fail-closed
check, and K2 matching stays code-block-only — no hole). N2 RESOLVED (collision id gets local `used-but-unlisted`
wording, fail-closed; genuine future concept cannot slip). N3 RESOLVED (entry-defined method not reported outside
GIVEN; a genuinely untaught method still reported; concept-level GIVEN containment via `_borrowed_occurrences`
unweakened). Deque RESOLVED (bare name `[]`; `deque(...)`/`collections.deque(...)` still detected).
- Pre-existing, non-blocking (NOT introduced by f166a5e; old `visit_Name` had the same gap) → `[WONTFIX]`-deferred
  optional follow-up: an aliased `from collections import deque as dq; dq()` is not name-recognized (no
  `visit_ImportFrom` hook for `collections.deque`); fails closed via `import-statement`/`list-append` in practice,
  contrived in student Book-1 code, reviewer-catchable. fable: "Not required for this gate." Tracked with the other
  Book-2 detector-hardening follow-ups.

### Re-review round 3 — [sol] (2026-09-22)
- **Verdict**: REJECT
Deque bare-name FP confirmed RESOLVED (`deque = 1; print(deque)` → `[]`; `deque()`/`collections.deque()`/
`.appendleft()`/`.popleft()` still flagged). 7-feature bare-identifier audit clean; collision guard sound; round-1
Must-Fixes + N1 intact. Two NEW findings:
1. `[OPEN]` Must Fix — `concept_scan.py:424` standalone `<x>.deque` attribute fails open: `queue_type =
   collections.deque` (type referenced, not called) → `[]`. Detection recognizes attributed `deque` only as a call
   target; a bare attribute access slips.
2. `[OPEN]` Must Fix — `concept_scan.py:1310` the [fable]-N3 fix (exclude entry-`defined_names` from post-GIVEN
   borrowed-method additions) is a fail-OPEN: `defined_names` is entry-global + name-based, so an unrelated
   `def add(value)` suppresses a genuine `set().add()` used OUTSIDE the GIVEN region (probe emitted neither
   `untaught method add` nor `outside the GIVEN region`).

### Author disposition (round 3 → fix pass, 2026-09-22)
Round-3 verdicts: [self] APPROVE · [fable] APPROVE · [sol] REJECT (2 new) · [glm] final attempt pending.
Both [sol] findings are genuine latent precision holes (no shipped-content impact — auxiliary is empty). Note:
finding #2 was introduced by MY choice to fold [fable]'s "Trivial" N3 — over-folding a fail-closed nit created a
fail-open. Resolution: (a) recognize `book2:deque` on a bare `<x>.deque` attribute access (visit_Attribute), not
only in call position; (b) REVERT the N3 exclusion — the post-GIVEN loop targets METHOD calls (`obj.add()`), which
never resolve to a standalone `def add(value)`, so a borrowed method used outside GIVEN must be flagged regardless
of `defined_names`; [fable] round-2 N3 → `[WONTFIX]` (misguided: method-vs-function conflation; its concern was
fail-closed, reverting removes sol's fail-open). Both get regression tests. This is a bounded, converging fix — no
open design questions remain.

### Re-review round 3 — [glm] (2026-09-22)
- **Verdict**: APPROVE WITH NITS (completed — no timeout this round; [glm] is functional, so NO 3-of-4 user decision
  is required after all)
Verified all four f166a5e changes correct via focused suites (101+18 pass incl. 6 new regressions) + AST/scan
probes; no new fail-open or FP introduced by the commit. Three nits:
1. `[OPEN]` Low — same N3 residual as [sol] round-3 #2 (entry-defined method name silences a genuine borrowed-method
   misuse outside GIVEN on an untyped receiver). Being fixed by the N3 revert (fix pass 3).
2. `[OPEN]` Low (informational) — if a future colliding local concept id has `kind: technique` or is MANUAL_ONLY,
   both the borrow path and the local path go silent. No live book1∩book2 collision exists; future-registration
   hazard only. → `[WONTFIX]`-note (documented hazard; unreachable today).
3. `[OPEN]` Informational (PRE-EXISTING, not introduced by f166a5e) — `collections.deque()` in a declared GIVEN
   region also emits `untaught method deque` (the method branch doesn't know `deque`-as-attribute is the feature);
   `from collections import deque; deque()` is clean. Adjacent to fix pass 3's new `<x>.deque` attribute
   recognition — fix pass 3 must ensure an AUTHORIZED deque doesn't feature+untaught-method double-flag (verify on
   landing); otherwise a documented follow-up.

### Round-3 resolution (fix commit 3d46f50; codex GPT-5.6-sol; 2026-09-22)
`tools/concept_scan.py` + tests. 114 focused tests pass; live book1/book2 `[]`; `ci-local` ALL GREEN.
- [sol] r3 #1 → `[FIXED]` — `visit_Attribute` registers `book2:deque` for any `<x>.deque` access; bare-Name `deque`
  stays clean. `test_undeclared_deque_attribute_is_a_borrowed_tool`.
- [sol] r3 #2 / [glm] r3 nit 1 → `[FIXED]` — reverted the N3 exclusion; a borrowed method outside GIVEN is flagged
  regardless of `defined_names`. Test replaced by `test_entry_defined_name_does_not_authorize_borrowed_method_outside_given`.
- [fable] r2 N3 → `[WONTFIX]` (superseded — its fail-closed concern created a fail-open; reverted).
- [glm] r3 nit 2 → `[WONTFIX]` — future registry-collision + technique/MANUAL_ONLY silence; unreachable
  (book1∩book2=∅); documented hazard.
- [glm] r3 nit 3 → `[WONTFIX]`-deferred — verified live: an AUTHORIZED `collections.deque()` still also emits
  "untaught method deque" (pre-existing; `deque()` spelling is clean). Not reachable in shipped (empty auxiliary) or
  plan-070 content (list-literal + `.split()`). Tracked with the Book-2 detector-hardening follow-ups.
Round-4 verification dispatched on 3d46f50 (all four).

### Re-review round 4 — final verification on 3d46f50 (2026-09-22)
- **[self]**: APPROVE — verified live: `queue_type = collections.deque` → `undeclared borrowed tool book2:deque`;
  `deque = 1`/`print(deque)` → clean; unrelated `def add` + `alias.add(2)` outside GIVEN → `untaught method add`;
  ci-local ALL GREEN.
- **[fable]**: APPROVE (no new findings) — confirmed the N3 revert cannot over-flag a genuine function call
  (post-GIVEN loop handles only `ast.Attribute` method calls, never bare `add(...)`), and `.deque` attribute
  recognition lives in `visit_Attribute` so a bare-Name `deque=1` never reaches it. 96/96 scan tests pass. Noted the
  already-deferred `collections.deque()` double-emit as non-blocking, not re-raised.
- **[sol]**: APPROVE — both round-3 findings RESOLVED (`queue_type = collections.deque` → `undeclared borrowed
  tool book2:deque`; bare-name probes `deque=1`/`print(deque)`/`x=deque`/`f(deque)` all `[]`; unrelated `def add` +
  `alias.add(2)` outside GIVEN → `untaught method add`, genuine inside-GIVEN `set().add()` clean). 114 focused tests
  pass; live book1/book2 `[]`. No new blocking findings.

### Content-review outcome: **FULL 4-way consensus** on `3d46f50` — [self]/[sol]/[fable]/[glm] all APPROVE
4 rounds (r1 REJECT×1 + nits → r2 REJECT×1 + nits → r3 REJECT×1 → r4 clean). All `[OPEN]` findings resolved
(FIXED or WONTFIX-with-reason). [glm] timed out in r1+r2 (opencode flakiness) but completed r3+r4, so no 3-of-4
user decision was needed. Deferred (documented, non-shipped) follow-ups for a future Book-2 detector-hardening
slice: aliased `collections.deque as X` import recognition; authorized `collections.deque()` untaught-method
double-emit; registry-collision `technique`/MANUAL_ONLY silence; general within-notebook duplicate-cell-id nbformat
hygiene check. Gate CLOSED.
- **[glm]**: APPROVE (no new findings) — both hunks correct; `.deque` attribute FP class is the same accepted
  name-collision as the existing `appendleft`/`popleft` lines (no new FP), and the N3 revert restores accepted
  pre-round-2 semantics with `defined_names` still live in the general untaught-method path. Deferred
  `collections.deque()` double-emit noted, not re-raised.

## Post-Execution Report

### 2026-09-22 — Phases B–D

Implemented the mechanism-only scope with no changes to existing Book-1 notebook cells.

- **Phase B:** migrated the Book-1 coverage map and all 16 Book-1 manifests to schema v2 with empty
  `auxiliary: []` declarations; kept Book 2 on schema v1; added version-dispatched, fail-closed map and manifest
  validation for presence, grammar, duplicates, normalized overlap, strict checkpoint/project emptiness,
  blueprint/map agreement, and manifest/map value agreement.
- **Phase C:** made prerequisite validation enforce later Book-1 homes and registered transitive-dependent Book-2
  owners without advancing `seen` or earning practice/coverage/spiral credit; made concept-scan cell-aware with
  real cell IDs, per-block authorization, borrowed-only markdown scanning, global `book2:str-split` ownership,
  contextual roles, exact GIVEN-region pairing by `py4kids_task_id`, the one-tool budget, and the closed,
  per-statement K2 exception loader. Added `book1/curriculum/k2-exceptions.yaml` at version 1 with an empty table.
- **Phase D:** added the three promised fixture shapes under `tests/fixtures/borrowed_tools/` and the full K1, K2,
  metadata/schema, prerequisite-edge, byte-identity, ID-not-position, and Book-2-isolation mutation matrix in
  `tests/test_borrowed_tools_{scan,prereq}.py`, plus version-dispatch locks in the existing test modules.

Verification evidence:

- `PATH=/tmp/py4kids-plan069-bin:$PATH PY4KIDS_CI=1 .venv/bin/python -m pytest -q -k 'not exec'`:
  **583 passed, 48 deselected**. The temporary shim only supplies the existing `uv run ruff` call used by
  `cell-lint`; it changes no repository file.
- Ruff, Book-1 and Book-2 manifest/prerequisite/coverage/concept scans, Book-1 technique spiral, all remaining
  non-kernel structure/content checks, Book-2 judge/source policy, PDF build, `git diff --check`, and
  `scripts/pre-merge-guard.sh`: **PASS**.
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` cannot start in this sandbox because its command PATH omits the
  installed `/home/chris/.local/bin/uv`. With that path restored plus a writable offline uv cache, CI step 1
  passes and step 2 reaches **618 passed, 2 skipped, 11 failed**; every failure is a Jupyter kernel
  `socket()` `PermissionError: [Errno 1] Operation not permitted`. The script then stops by design.
- `git diff --name-only -- 'book1/**/*.ipynb'` is empty. The only new notebooks are synthetic files under
  `tests/fixtures/borrowed_tools/`.

All planned implementation work is complete. Native `exec-lessons` / `exec-solutions` verification is the only
uncompleted gate in this write sandbox and must be rerun by the orchestrator in its kernel-capable environment.
The requested commit could not be created because this sandbox mounts `.git` read-only; `git add` failed with
`Unable to create '.git/index.lock': Read-only file system`. The scoped changes remain unstaged on the requested
feature branch for the orchestrator to commit after rerunning the native execution gate.

### 2026-09-22 — Finalization (orchestrator, kernel-capable env)

Committed Phases B–D as `7d34f91` after re-running the native execution gate here: `TMPDIR=/dev/shm bash
scripts/ci-local.sh` → **ALL GREEN** (the codex build sandbox's 11 Jupyter `socket()` failures were pure sandbox
artifacts). Then took the plan through the 4-way content-review gate (tooling code review per
`docs/content-review-gate.md`), folding findings across 4 rounds:
- `7d34f91` — Phases B–D mechanism (schema v2 + cell-aware scanner + empty K2 table + mutation matrix).
- `b7eb731` — round-1 fixes ([sol] 3 Must-Fix: cell-local method auth, K2 AnnAssign/walrus, solution real-form;
  [fable] Should-Fix: Book-2 syntax closure, multi-fence markdown; + safe nits).
- `f166a5e` — round-2 fixes ([sol] deque bare-name false positive; [fable] N1/N2/N3).
- `3d46f50` — round-3 fixes ([sol] `<x>.deque` attribute fail-open; revert of the N3 exclusion fail-open).

Final state: **FULL 4-way content consensus on `3d46f50`**; `ci-local` ALL GREEN; live book1/book2 concept scans
`[]`; borrowed-tools test suite green; ZERO changes to existing notebook content (mechanism-only). No `[OPEN]`
findings remain. The listed detector-hardening items are documented, non-shipped, non-plan-070 follow-ups.
Ready for PR + `pre-merge-guard --pr` + squash-merge. The visible "less-toy" example rewrites remain plan 070.
