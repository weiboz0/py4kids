# Plan 069 — "Borrowed tools": a narrow auxiliary-concept exception + pilot (u02 / u04 / u08)

**Origin:** author directive (2026-09-21): "Book 1 currently strictly follows the learning order of concepts,
making some examples and exercises limited to learned concepts at that point; relax this constraint to allow
future concepts in examples as auxiliary tools" — i.e., make examples/exercises more realistic (less toy feel).
**Advisory review:** sol (codex) + fable (Fable) surveyed all of Book 1 and converged on the design below.
**User decisions (AskUserQuestion, 2026-09-21):** (1) scope = *mechanism + pilot* (broad enrichment deferred to
follow-ups); (2) *lift* the u02 "don't count your guesses" ban; (3) pilot = *u04 + u08*.

Design authority created by this plan: **`docs/designs/004-borrowed-tools.md`** (the "borrowed-tools" norm,
sibling of design 003). Related: [[twins-must-showcase-the-concept]], design 003 (real-input), design 000.

## Motivation

Today a CRITICAL RULE enforces strict prereq closure — "nothing may be used before the unit that introduces it"
(`prereq_findings` in `tools/curriculum.py:227`; `concept_scan` flags any concept used in a code cell outside a
unit's `introduces ∪ requires ∪ practices` union). The reviewers found toy-feel has **three sources**:
1. **Genuine future concepts** (lists/`len` before u07; `.split()`, owned by Book 2, in u08) — needs a new
   mechanism to let them appear as *given* black boxes.
2. **Over-restriction of ALREADY-taught concepts** (u04 avoids `for`/`range` although u03 taught them; "do not
   use…" statement bans) — needs no new mechanism, only removing the bans.
3. **CI-executability substitutes** (scripted-player twins) — already addressed by design 003 / plans 067–068.

This plan builds the mechanism for (1), and applies both (1) and a scoped slice of (2) to a **pilot** (u04, u08)
plus the user-approved u02 counting-ban lift. Broad enrichment and the full over-restriction sweep are **deferred
to phased follow-up plans** once the pilot proves the mechanism.

## The design — the "borrowed tool" exception (goes in design 004)

**Core rule.** A future concept may appear in CORE material only as an explicitly-marked **borrowed tool**: given
machinery in a lesson demo or an exercise scaffold that the student *reads, consumes the output of, or calls* —
never authors, completes, selects, repairs, traces, or explains. It earns **no** teaching credit and never
advances teach order. Checkpoints and projects stay strict (`auxiliary: []`).

**Two exception kinds** (both narrow):
- **(K1) Borrowed black-box tool** — a future *tool* concept used as given code the student does NOT write:
  a list literal as inert given data, `.split()` in a given input adapter, `len()`/`max()`/`round()` as an
  opaque call, a supplied helper `next_scripted_guess()`. Appears only inside a **GIVEN region** (exercise) or a
  `demo`/`real-form`-tagged cell (lesson/solution). The student's authored lines use taught concepts only.
- **(K2) Composed-from-taught** — a construct built ENTIRELY from already-taught primitives that the registry
  merely *names* as a later concept, which the student MAY write. The only sanctioned instance in this plan is
  u02 counting: `guesses = guesses + 1` is variable-reassignment (u02 cells 29–30) + arithmetic (u02 cell 15);
  the registry pattern-detects it as `accumulator` (owned by u04). The later unit still formally introduces and
  assesses the *named technique*. **(K2) is deliberately narrow** — allowed only when every token is taught and
  the future unit still owns the named pattern; it is the user's explicit direction, overriding sol's "keep the
  paper tally" position (recorded so the gate does not re-litigate it).

**Eligibility test (K1).** A construct is a borrowed tool only if a reviewer could replace it with its resulting
value (or a named helper call) without changing what the learner must reason about, write, debug, or receive
credit for.

**Never eligible to lead** (spine-protection denylist — an auxiliary may not COMPUTE the assessed skill):
find-extreme → `max`/`min`; running-total → `sum`; count-by-condition → `.count`; list-sort → `sorted`;
linear-search → `in`/`.index`; transform-each → comprehensions; plus: the unit's own `introduces` before its
lesson; anything the rubric names or a correct solution must author/select/modify/explain/trace; control-flow
that determines the solution (`if`, loops, `break`, `def`/`return`, classes); mutation when mutation is the skill
(`.append`, `.sort`, dict/attr assignment, file writes); error-producing syntax in debug/trace tasks; and ANY
auxiliary use in a checkpoint or project.

**Budget — "one new idea, one borrowed tool" per cell.** At most ONE borrowed tool per code cell; it must (a) be
a single call/literal with a self-describing name, (b) not sit on the line carrying the taught concept, (c) be
replaceable by a fixed value without changing what the cell teaches, (d) never appear in a graduated build-up
rung (the plans-031–035/049 one-increment ladders stay pure). The same tool reused across a unit counts as one.

**Borrowed tool ≠ stretch/preview.** Stretch is optional and the student MAY write the future construct (design
000 mixed-ability rule). A borrowed tool may support a CORE task but is supplied and contract-only; if a task
says "change this / write another / fix this call / explain how it works", it is a preview, not a borrowed tool.

**Marking convention** (learner-facing; extends the existing `**Notice:**` style):
- First local use gets a rendered callout — three beats, ≤~25 words: *what it does* (concrete) · *"you'll own it
  in Unit N"* (a promise) · *"borrow it like `randint`"* (anchor to a trusted tool). Example:
  > **Borrowed tool — ready-made data:** `scores = [4, 6, 5, 7, 3]` is a **list**: one name holding all five
  > scores in order. You'll build and change lists yourself in Unit 7 — for now, borrow it like `randint`.
- Later uses get a 5-word inline comment: `scores = [4, 6, 5, 7, 3]   # borrowed: a list (Unit 7)`.
- **Never** "advanced", "don't worry", "just trust", "you don't need to understand" (each implies something to
  fear). "Borrow" / "own" is the whole metaphor. Do not over-mark (that is how u07's repeated "Real version:"
  note went invisible).
- Replace taxonomy bans with positive scoping: not "Do not use a list/`for`/functions" but
  "This exercise checks that YOU keep the running total — the list is given; the loop and the total are your job."
- Exercise scaffolds delimit the supplied source with GIVEN-region markers:
  ```python
  # GIVEN TOOL — do not edit
  scores = [4, 6, 5, 7, 3]
  # your work begins below
  ```
- Teacher notes get a "Borrowed tools in this unit" block naming the assessed spine and stating the tool earns no
  credit ("Same as `randint` — someone wrote it for us; in Unit N we open the box").

## Representation + tooling

**Schema v2 (Book 1 only; Book 2 stays v1 until it migrates intentionally).** Add an `auxiliary:` field to every
Book-1 coverage-map entry and mirrored unit manifest (checkpoints/projects: `auxiliary: []`). Entries reference
auxiliaries with **qualified ids** — `book1:list-literal`, `book2:str-split` — while `introduces`/`requires`/
`practices` keep raw ids. Cells that use a borrowed tool carry cell metadata `tags:[auxiliary, <role>]` (role ∈
`demo` | `given` | `real-form`) and `py4kids_auxiliary:[book1:list-literal, …]`. Neither the entry declaration
nor the cell tag alone makes code pass — both are required.

**`prereq_findings` (curriculum.py:227) changes:**
1. Keep computing missing normal concepts from `(requires ∪ practices) − seen`; **exclude** `auxiliary`.
2. **Never** add `auxiliary` ids to `seen` (only `introduces` advances teach order, line ~243 — unchanged).
3. `auxiliary` must be disjoint from `introduces`/`requires`/`practices`.
4. `book1:<id>` auxiliary: the concept's home introduction must be *later* than this entry (if already taught it
   belongs in `requires`/`practices`). `book2:<id>`: require a registered Book-2 owner + forward relationship
   (Book 2 depends on Book 1, not vice-versa) — a qualified forward reference that grants **no** ownership/credit
   (this is how `.split()` is used in u08 WITHOUT registering `str-split` in Book 1, avoiding the
   `global_concept_uniqueness_findings` collision, curriculum.py:52).
5. Reject non-empty `auxiliary` on checkpoints and projects.
6. Exclude `auxiliary` from `practice_findings`, checkpoint coverage, technique-spiral, and "only capstone
   practices" calculations.

**`concept_scan` (concept_scan.py) — cell-aware:**
- `code_sources()` (~:428) yields (path, cell index, source, tags, declared auxiliary ids, role) instead of bare
  strings; stop aggregating one entry-wide `used` set before authorization (~:484–495).
- Per source block: `normal_allowed = baseline ∪ introduces ∪ requires ∪ practices`;
  `block_allowed = normal_allowed ∪ that_block's_declared_auxiliary`. A future concept used OUTSIDE its tagged
  block still fails.
- New findings: undeclared cell auxiliary id; declared-but-unused; unauthorized role tag; auxiliary AST node
  outside a GIVEN region (exercises); GIVEN region mismatched between an exercise and its paired solution.
- Global recognition: detect raw `.split()`/`str-split` regardless of the active book, then resolve authorization
  against `book2:str-split` (today it is only recognized when the active book registers it — concept_scan.py:73).
- **Scan fenced Python inside `real-form`-tagged markdown cells** (design 003 deliberately made solution markdown
  invisible; without this, u08 could use `.split()` in a real-program block with no enforcement — design 003 §2).

**Mutation tests (must accompany the tooling):** same-book future concept passes ONLY inside a declared+tagged
GIVEN region; removing the cell tag fails; removing the entry declaration fails; moving the construct outside the
GIVEN region fails; a later entry cannot treat the auxiliary as taught; auxiliary earns no practice/spiral credit;
checkpoint/project auxiliary declarations fail; an untagged `.split()` in a Python markdown fence fails;
`book2:str-split` passes without duplicating the registry id; exercise and solution GIVEN regions must be
byte-identical.

## Governance / design amendments (human-reviewed — surfaced for sign-off)

Proposed exact wording is in Phase A; these edits are normally human-reviewed but are covered by this directive.
- **`AGENTS.md`** "Self-containedness is law" bullet → add the borrowed-tool carve-out (used-before-taught is
  permitted ONLY as a marked, given, no-credit borrowed tool per design 004; taught-before-**assessed** is
  unchanged; checkpoints/projects stay strict).
- **`docs/designs/000-project-design.md` §2** (prereq-closure / mixed-ability) → same carve-out + pointer to 004.
- **New `docs/designs/004-borrowed-tools.md`** → the full norm above (policy, K1/K2, eligibility, denylist,
  budget, marking, tooling contract, checkpoint/project exclusion).

## Pilot content

**u02 — lift the counting ban (K2, user-approved).** Drop "do not count your guesses / tally on paper" from
lesson cell 66 and exercises cells 0 / Ex3 / Ch1 / Ch2; let students write `guesses = guesses + 1`. Add a light
Notice: "This counting trick is called an **accumulator** — Unit 4 makes it official." Declare
`auxiliary:[book1:accumulator]` on u02 with the K2 rationale. The u04 accumulator lesson/assessment is unchanged
(it still formally introduces the named technique). No change to u02's existing while-twins (plan 067).

**u04 — lists as given data (K1) + drop over-restriction (source 2).** Convert the counter-keyed 5-way if/elif
dispatch that stands in for a 5-element list into a GIVEN list + given `for` iteration, leaving the accumulator /
count / `break` body for the student. Pilot slice (sol's recommendation): **lesson cells 54 and 63**, and **one
of Exercises 14–18** (Ex14 "Add only the passing rounds" is the cleanest — `scores = [4,6,5,7,3]`, student writes
`if score >= 5: total = total + score`). Reword its statement to the Given:/Your job: split; drop the "do not use
a list/`for`/`range`/functions" bans (note: `for`/`range` are already-taught u03 concepts — removing those bans
is source-2 cleanup that needs no auxiliary; only the list literal is a borrowed tool). Declare
`auxiliary:[book1:list-literal, book1:list-loop]` on u04. Solutions keep the GIVEN region byte-identical and do
the graded work with taught concepts (asserts unchanged, e.g. Ex14 `assert total == 18`). The design-003 real
`input()` form is UNCHANGED — the twin and the real form now differ only in where the data comes from (honest).

**u08 — `.split()` as a given input adapter (K1, the hard case).** Replace one fixed-count read in a lesson cell
(cell 27 or 36) and one solution real-form block (e.g. cell 14 or 33) with a marked
`words = input(...).split()` adapter (lists + list-loops are already taught by u08, so only `.split()` leads).
Declare `auxiliary:[book2:str-split]` on u08. This exercises BOTH the code-cell path and the markdown real-form
path and the cross-book owner rule. `.split()` is NOT registered in Book 1.

## Phases

### Phase A — design + governance (docs only)
Write `docs/designs/004-borrowed-tools.md`; amend `AGENTS.md` + `docs/designs/000` with the carve-out (exact
wording drafted here and surfaced to the user for sign-off before merge).

### Phase B — tooling + tests
Schema v2 `auxiliary:` field (map-schema + manifest-schema validators); `prereq_findings` changes; `concept_scan`
cell-aware redesign + markdown-real-form scanning + global `.split()` recognition + `book2:` qualified refs; add
`auxiliary: []` to every Book-1 map entry + manifest (no content change); the full mutation-test suite. ci-local
stays green with `auxiliary: []` everywhere (pure metadata migration).

### Phase C — pilot content
u02 counting-ban lift; u04 lists-as-given-data (lesson 54/63 + Ex14) with the bans dropped; u08 `.split()` adapter
(one lesson cell + one real-form). Each borrowed tool marked per the convention; GIVEN regions byte-identical
between exercise and solution.

### Phase D — verification
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN. Mutation tests pass (each removal breaks as designed).
Standalone-run each changed solution cell (asserts pass). §6b real-form parity preserved for u04/u08 twins.
Targeted checks: the student never authors an auxiliary in the pilot exercises; removing a tag/declaration/GIVEN
marker fails; checkpoints/projects still reject `auxiliary`. Scope allowlist = the plan + design 004 + AGENTS.md +
design 000 + the tooling files + u02/u04/u08 notebooks + manifests + coverage-map.

## Out of scope (deferred follow-ups)

- Broad example/exercise enrichment across the other units (u01, u03 colors, u05, u06, u07, u09, projects) — a
  phased rollout AFTER the pilot proves the mechanism (like the design-003 rollout).
- The full "stop over-restricting already-taught concepts" sweep beyond the u04 pilot slice.
- Book-2 schema migration to v2; checkpoints/projects gaining any auxiliary (they stay strict).
- Spine cases the reviewers said MUST NOT be relaxed: u01's zero-baseline; u03 unrolled-square→loop; u06 manual
  alphabet scan → `.index`; u07 find-extreme → `max`/records; u09 file ops hidden by helpers; any trace/predict/
  debug task; GIVEN-region markers on lesson/solution demos (v1 uses cell tags there; exercises use GIVEN regions).
- Not an erratum (nothing is wrong today — a realism/pedagogy improvement).
- **Verification phase:** Phase D is the named verification phase (this plan ships tooling + pilot content, both
  verified there).

## Plan Review

### Round 1 (2026-09-21) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.

#### [self] (2026-09-21)
**APPROVE (with open questions for the gate).** Synthesizes both advisory reports + the three user decisions.
Design spine is sound: borrowed-tool = given/contract-only, never authored/assessed; spine-protection denylist;
one-tool budget; checkpoints/projects strict; qualified `book2:str-split` forward-ref avoids the uniqueness
collision; markdown real-form scanning closes the design-003 blind spot. Self-flagged for gate scrutiny:
(1) SIZE — governance + schema v2 + concept_scan redesign + 3-unit pilot in one plan; is this reviewable, or
should Phase B tooling and Phase C content split? (2) K2 (u02 `x=x+1` "composed-from-taught") is the contentious
piece — sol argued keep the ban; it's the user's explicit call, flagged so the gate doesn't re-litigate the
DECISION but should still check the MECHANISM (how concept_scan stops flagging student-written `accumulator` in
u02 without a GIVEN region — K2 waives the given-only rule, which needs a clean tooling story). (3) GIVEN-region
byte-identical exercise↔solution enforcement — confirm feasible. (4) governance wording (Phase A) needs the
exact `AGENTS.md`/design-000 text before merge (surfaced to user).

#### [fable] (2026-09-21)
**APPROVE WITH NITS** — design faithfully carries the guardrails; pilot is the right first step; keep it one plan
(the pilot IS the mutation test). Required fixes (fold before Phase B/C):
- N1: one-tool budget violated by u04 declaring `list-literal`+`list-loop` → define "a ready-made list + `for x in
  <it>:`" as ONE composite tool; exempt MANUAL_ONLY ids (list-loop) from the "declared-but-unused" finding.
- N2: denylist forbids "loops as solution control-flow" but the pilot GIVES a `for` header → carve out that a
  header delivering given items is a data-delivery idiom (like input()) that sits INSIDE the GIVEN region; the
  loop BODY stays the student's; budget clause (b) holds because the body lines carry the taught concept.
- N3: K2 underspecified — `guesses = guesses + 1` registers as BOTH `loop-counter` (u03) AND `accumulator` (u04)
  → declare both; K2 student-WRITES it (no GIVEN region) → needs a `composed` role exempt from GIVEN-region +
  declared-but-unused, still zero credit, still checkpoint/project-disjoint; u02 teacher-notes state counter-free
  design → update.
- N4: design 003 must ALSO be amended (v7: §4 fixed-count stays DEFAULT but `.split()` allowed as book2:str-split
  borrowed tool; §2/§5 real-form markdown now scanned; §9 entry) → add to governance list; teacher-notes
  (u02/u04) must be in the allowlist + Phase C.
Nits: N5 Ex14 has no "do not use" ban — it is OVER-PRESCRIPTIVE ("counter-bounded while + if/elif chain"); that
sentence is the rewrite target; Ex15-18 carry the same sentence, state they STAY as-is in the pilot. N6 u08
promise "own it in Book 2" is 2 years out → "next year, in Book 2, you'll open this box" + a Book-2 callout
variant. N7 (important) the "real form UNCHANGED, differs only in data source" claim is contradictory — the new
`for` twin breaks design 003 §6c line-for-line parity with the `while`/input() real form; PICK one: (i) keep the
while/input() real form + amend design 003 §6 with a "borrowed-data twin" clause (parity on body + result line,
like §6d) [fable recommends], or (ii) fixed-count `[int(input()),…]` + same `for`. N8 u04 map entry lacks
`for-loop`/`range-function` in requires/practices → add `for-loop` (and range if used) to u04 practices or
concept_scan fails the source-2 cleanup. N9 the `real-form` cell tag does not exist yet → Phase B introduces it
(coexists with `no-exec`; markdown cells carry `tags`).

#### [sol] (pending)
#### [glm] (pending — opencode)

## Content Review
_(pending)_

## Post-Execution Report
_(pending)_
