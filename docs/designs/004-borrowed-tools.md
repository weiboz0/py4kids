# Design 004 — Borrowed tools: a narrow auxiliary-concept exception to prereq closure

**Status:** APPROVED — v1 (2026-09-21). Authority for the "borrowed tool" relaxation of Book 1's strict
prereq-closure. Sibling of design 003 (real-input). Mechanism shipped by plan 069; first content pilot in
plan 070. Amends `AGENTS.md` "Self-containedness is law" and design 000 §2 (the carve-out); amends design 003 to
v7 (`.split()` as a borrowed tool; real-form markdown scanned for borrowed tools; borrowed-data-twin parity).

## 1. Why

Strict prereq closure ("nothing may be used before the unit that introduces it") forces toy examples: pre-list
units hand-count instead of looping a list, data is absurdly small, and "do not use…" bans tell a middle-schooler
the course is holding back. This norm lets a **future** concept appear in core material as a **borrowed tool** —
so examples feel real — without weakening what the student is actually taught and assessed on.

## 2. Core rule

A future concept may appear in CORE material ONLY as an explicitly-marked **borrowed tool**: *given* machinery in
a lesson demo or exercise scaffold that the student **reads, consumes the output of, or calls** — never authors,
completes, selects, repairs, traces, or explains. A borrowed tool earns **no teaching credit** and **never
advances teach order** (`seen`). **Checkpoints and projects are strict** — no borrowed tools. Taught-**before-
assessed** is never relaxed.

## 3. The two exception kinds

### K1 — borrowed black-box tool
A future *tool* used as given code the student does NOT write: a list literal as inert given data, `.split()` in
a given input adapter, `len`/`max`/`round` as an opaque call, a supplied helper function. It appears only inside a
**GIVEN region of an exercise** or a `demo`/`real-form`-tagged lesson/solution cell. The student's authored lines
use taught concepts only.

**Loop-header carve-out.** A `for x in <given collection>:` header that only *delivers* a given collection's items
is a **data-delivery idiom** (like `input()`), NOT "control-flow that determines the solution". It is legal only
when it sits inside the GIVEN region and the student writes the loop **body** (which carries the taught concept).
A given list literal + its delivering `for x in <it>:` header count as **ONE composite borrowed tool**; declare
only the *detectable* id (`book1:list-literal`) — `list-loop` is `MANUAL_ONLY`, invisible to the scanner, so it is
not declared and is exempt from the "declared-but-unused" check.

**Eligibility test:** a construct is a borrowed tool only if a reviewer could replace it with its resulting value
(or a named helper call) without changing what the learner must reason about, write, debug, or receive credit for.

### K2 — composed-from-taught
A construct built ENTIRELY from already-taught primitives that the registry merely *names* as a later concept,
which the student MAY write. This is a **closed, non-extensible exception table** (`book1/curriculum/
k2-exceptions.yaml`), NOT a general "anything composed" rule. Each row is `{cell-id, concept-ids, exact-AST-form,
role: composed}`, keyed by the notebook's real `cell["id"]`; the scanner authorizes a statement only when ALL
match, **per statement** (a second, non-matching statement of the named concept in the same cell still fails). A
row whose cell-id does not exist fails closed. K2 verifies its primitives are already taught, never adds the
concept to `seen`/practice/coverage/spiral, and is disjoint from checkpoints/projects.

The one sanctioned case (content added in plan 070): the guess counter. The pattern is curricularly BOTH
`loop-counter` (u03) and `accumulator` (u04); the scanner emits only `accumulator` (`loop-counter` is
`MANUAL_ONLY`, never emitted), so K2 authorizes the emitted `accumulator` and declares both ids for curriculum
honesty. AST form **`name = name + 1`** ONLY (plain-Name target, literal `1`, `+`; NOT `+=`, `1 + n` operand-swap,
alternate operator, subscript, attribute, or any other form).

## 4. Never eligible to lead (spine-protection denylist)

A borrowed tool may not COMPUTE the assessed skill: find-extreme→`max`/`min`; running-total→`sum`;
count-by-condition→`.count`; list-sort→`sorted`; linear-search→`in`/`.index`; transform-each→comprehensions. Also
never: the unit's own `introduces` before its lesson; anything the rubric names or a solution must
author/select/modify/explain/trace; control-flow that determines the solution (`if`, loops [except the delivery
carve-out], `break`, `def`/`return`, classes); mutation when mutation is the skill (`.append`, `.sort`, dict/attr
assignment, file writes); error-producing syntax in debug/trace tasks; and ANY auxiliary in a checkpoint/project.
**Already-taught concepts are NOT borrowed tools** — they belong in `requires`/`practices`.

## 5. Budget — "one new idea, one borrowed tool" per cell

At most ONE borrowed tool per code cell (or the one list+delivery-header composite), with a self-describing name;
it must not sit on the line carrying the taught concept; it must be replaceable by a fixed value without changing
what the cell teaches; and it must **never appear in a graduated one-increment build-up rung** (a culminating
put-it-together cell is not a build-up rung, but content targets exercises, not lesson ladder rungs). The same
tool reused across a unit counts as one. CI enforces the budget by requiring at most one *detectable* id in a
cell's `py4kids_auxiliary` (MANUAL_ONLY ids excluded from the count).

## 6. Borrowed tool ≠ stretch/preview

Stretch is optional and the student MAY write the future construct (design 000 mixed-ability rule). A borrowed
tool supports a CORE task but is supplied and contract-only. If a task says "change this / write another / fix
this call / explain how it works", the construct is a preview, not a borrowed tool.

## 7. Marking convention (learner-facing)

Extends the existing `**Notice:**` style. First local use of a **K1** tool gets a three-beat callout (≤~25 words):
*what it does* (concrete) · *"you'll own it in Unit N"* (Book-2 variant: *"next year, in Book 2, you'll open this
box"*) · *"borrow it like `randint`"*. Example:
> **Borrowed tool — ready-made data:** `scores = [4, 6, 5, 7, 3]` is a **list**: one name holding all five scores
> in order. You'll build and change lists yourself in Unit 7 — for now, borrow it like `randint`.

Later uses get a 5-word inline comment (`scores = [...]   # borrowed: a list (Unit 7)`). **Never** "advanced /
don't worry / just trust / you don't need to understand". Positive scoping replaces "do not use…" bans, and an
exercise using a K1 tool frames the task as **Given:** (the tool + what it yields) / **Your job:** (the taught
skill). Exercise scaffolds delimit the given source with GIVEN-region markers
(`# GIVEN TOOL — do not edit` … `# your work begins below`).

**K2 is NAMED, not borrowed.** The honest message is "you built this counter from a variable and `+ 1`; **Unit 4
gives the pattern a name** (accumulator)" — never "borrow it". A `composed` cell is exempt from the GIVEN-region
requirement (the student authored it).

Teacher notes carry a "Borrowed tools in this unit" block: the assessed spine, and that each tool earns no credit
("same as `randint` — someone wrote it for us; in Unit N we open the box").

## 8. Tooling contract (implemented in plan 069)

**Schema v2 (Book 1 only; Book 2 stays v1).** Book-1 coverage-map is `map_version: 2`, every Book-1 manifest is
`blueprint_version: 2`; validators are version-dispatched. v2 adds a top-level `concepts.auxiliary` list (mirrored
map↔manifest) using **qualified ids** (`book1:list-literal`, `book2:str-split`); `introduces`/`requires`/
`practices` keep raw ids. `auxiliary` is disjoint from the three raw fields after stripping the `book1:` prefix;
v2 requires the key on every entry, v1 forbids it; a v2 manifest under a v1 map (or vice-versa) fails.
Checkpoints/projects require `auxiliary: []` (non-empty rejected).

**Cell metadata.** A borrowed-tool cell carries `tags:[auxiliary, <role>]` (role ∈ `demo` | `given` |
`real-form` | `composed`, exactly one) and `py4kids_auxiliary:[<qualified ids>]`. Both the entry declaration AND
the cell tag are required; neither alone authorizes.

**`prereq_findings`:** exclude `auxiliary` from `(requires ∪ practices) − seen`; never add `auxiliary` to `seen`;
`book1:<id>` home-intro must be *later* than the entry (else it belongs in requires/practices, checked in MAP
order); `book2:<id>` must have a registered Book-2 owner that is a transitive **dependent** of Book 1; reject
non-empty `auxiliary` on checkpoints/projects; exclude `auxiliary` from practice/coverage/technique-spiral/
uniqueness/only-capstone calculations.

**`concept_scan` — cell-aware.** Per code block:
`block_allowed = baseline ∪ introduces ∪ requires ∪ practices ∪ that-block's-declared-auxiliary`; a future concept
used outside its tagged block fails. In every **governed** notebook (all Book-1 units + checkpoints + projects):
code cells get the full closure; **markdown Python fences are parsed for `SyntaxError` (which fails) and scanned
ONLY for borrowed tools** (declared auxiliary ids + globally-recognized tools like `.split()`) — the general
used-but-unlisted closure stays **code-cell-only**, preserving design-003 §5 invisibility of real-form markdown.
Raw `.split()` is recognized globally, resolved to its qualified owner `book2:str-split`, and the double
"untaught method" finding is suppressed when authorized; untagged/undeclared `.split()` still fails. Exercise↔
solution GIVEN regions must be byte-identical, paired by a stable shared task id (never positional). GIVEN-region
enforcement is **exercise-only**; lesson `demo`/solution `real-form` cells authorize via tag + declaration alone.

## 9. Revision history

- **v1 (2026-09-21):** created by plan 069. Establishes K1/K2, the loop-header carve-out, the closed K2 table, the
  spine denylist, the one-tool budget, the marking convention, and the tooling contract. Companion amendments:
  `AGENTS.md`, design 000 §2, design 003 → v7.
