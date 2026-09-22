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
  K2 case this mechanism ships (its u02 *content* is deferred to plan 070) is the guess counter. The pattern is
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
  declared ids passes; `+=`, alternate operator, subscript/attribute target, a different cell, a different
  concept, or a missing role each → fail; no `seen`/practice/coverage credit.
- **Book-2 isolation:** Book 2 (v1) behavior unchanged; a non-vacuous Book2→Book1 same-process test that extending
  the Book-1 profile does not leak recognition globally.
- **Markdown-scope lock ([glm] B1):** a markdown Python fence using a taught-but-unlisted concept (e.g. `input`)
  does NOT fail; an untagged/undeclared `.split()` in a markdown fence DOES fail.
- **Schema/metadata ([sol] B5 / [glm] N5/N6):** malformed/duplicate/unqualified `py4kids_auxiliary`; zero /
  multiple / wrong role; `auxiliary` overlapping requires/practices (after prefix-normalize); v2-manifest-under-v1-map
  (and vice-versa); >1 detectable auxiliary id in one cell (budget) → fail; a missing/duplicate pairing id → fail.
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

#### [glm] round 3 — pending

## Content Review
_(pending)_

## Post-Execution Report
_(pending)_
