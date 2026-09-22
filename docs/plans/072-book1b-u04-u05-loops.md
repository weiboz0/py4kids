# Plan 072 — Book 1b Units 04 (Loops & Counting) + 05 (For & Range) + Checkpoint 02

**Origin:** Book 1b buildout (standing directive, "full book 1b implementation").
**Design:** `docs/designs/005-book1b-concept-first.md` §3 (unit table + checkpoint boundaries), §5, §7.
**Template:** Units 01–03 (plans 070–071) — clone their shape exactly; follow all authoring guardrails below.

## Scope

Two adjacent pre-function loop units + their checkpoint (U05 is a checkpoint boundary, design §3):
- **U04 — Loops & Counting** (`while`), **U05 — For & Range**, **checkpoint-02 — Loops** (assesses U01–U05).
Book 1b stays `buildout: true`.

## Coverage-map entries (the contract)

**unit-04-loops-and-counting** — `lessons: 3`
- introduces: `[while-loop, break-statement, loop-counter, accumulator, sentinel-loop, running-total, count-by-condition]`
- requires: `[if-statement, comparison, arithmetic, int-type, variable, print]`
- practices: `[boolean, elif-else, f-string, string-literal, naming, comment, error-messages]`

**unit-05-for-and-range** — `lessons: 3`
- introduces: `[for-loop, range-function, nested-loops]`
- requires: `[while-loop, accumulator, loop-counter, arithmetic, comparison, variable, print]`
- practices: `[running-total, count-by-condition, int-type, boolean, f-string, if-statement, elif-else, string-literal, naming, break-statement]`

**checkpoint-02-loops** — `kind: checkpoint`, `lessons: 0.5`
- introduces: `[]`
- requires: `[print, variable, while-loop, for-loop, accumulator, comparison, arithmetic]`
- practices: `[print, variable, while-loop, break-statement, loop-counter, accumulator, running-total,
  count-by-condition, for-loop, range-function, nested-loops, if-statement, elif-else, comparison, boolean,
  arithmetic, int-type, f-string]`
  - Checkpoints stay STRICT (no fastforward): every practiced/required id is introduced by U01–U05, so
    `checkpoint_findings` passes. Because loops/accumulator are NOW taught, checkpoint-02 MAY use small
    loops (unlike checkpoint-01) — but keep it to `while`/`for` over a `range`, no lists (lists are U10).

Closure (strict over `requires`) holds in order. Metadata is honest to content (every id is genuinely used).

## Key teaching notes

- **U04 is `while`-only** (no `for`/`range`/lists — those are U05/U07/U10). Counting uses a manual counter
  (`i = 0; while i < n: … ; i = i + 1`). **`accumulator` is introduced here**, so `total = total + n` /
  `count = count + 1` become legal FROM U04 on (they were forbidden in U01–U03 and in checkpoint-01).
- The three technique concepts land as ordinary concepts: **sentinel-loop** ("repeat until a stop value"),
  **running-total** (accumulate a sum), **count-by-condition** (count how many satisfy a test).
- **U05** introduces `for`/`range`/`nested-loops`; it reuses the accumulator/counting techniques on `range`.

## Authoring guardrails (Phase C/D)

- Pre-function (no `def` until U07). No lists/dicts (U10/U11). No `round/min/max/abs/sum/len` (builtins, U07) —
  sums/counts are done with the accumulator idiom, never `sum(...)`/`len(...)`.
- Floats printed exactly; integer division `//` and `%` on non-negative operands; no `:.2f`.
- Every loop TERMINATES; `while` loops advance their counter/condition each pass (no infinite loops in
  executable cells); the deliberate error beats are an infinite-loop-avoided note + a `SyntaxError`/off-by-one.
- U04 opener = a real counting/repetition problem (e.g. "how many steps does 27 take to reach 1?" Collatz;
  or a factorial/running-total), NOT "here is `while`". U05 opener = a nested/tabular problem (times table,
  number triangle). Openings are problems, not drill.
- ≥8 mini-CP exercises per unit, **core ≤7** + extra + ≥2 Challenge; house solution form (capture→print→assert);
  solution-free student notebooks, no outputs, no `input()` in graded code (fenced try-it only); unique cell ids.
- **checkpoint-02:** VISIBLE `## Question N` headings (6–8), solutions mirror them, teacher-notes with
  `## Grading` + full section set; mixes U01–U05 with ≥2 loop questions; strict (no lists/builtins, but loops OK).

## Phases

### Phase A — plan-review gate (4-way). No implementation until consensus.
### Phase B — contracts: append the 3 coverage-map entries + 3 syllabus rows + 3 manifests; `coverage-check` + `prereq-check` GREEN.
### Phase C — statements (Codex, gpt-5.6-sol): each unit's lesson+exercises; checkpoint.ipynb. Follow every guardrail.
### Phase D — solutions (SEPARATE fresh Codex): each unit's + the checkpoint's solutions.ipynb (house form; mirror headings).
### Phase E — teacher-notes (inline) + verification: `teacher-notes.md` per unit + checkpoint grading notes; full
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN across the three books; exec-solutions/exec-lessons clean;
≥2 stretch per unit; openings are problems. Scope allowlist = this plan + the U04/U05 unit trees +
`book1b/checkpoints/checkpoint-02-loops/` + coverage-map + syllabus.

## Out of scope

- U06–U13, the later checkpoints, the Algorithm Challenge — plans 073+.
- No tooling/governance/Book-1/Book-2 changes. Not an erratum.
- **Verification phase:** Phase E is the named verification phase (units + checkpoint → required).

## Plan Review

### Round 1 (2026-09-22) — [self] inline; [sol]/[glm]/[fable] dispatched.

#### [self] — **APPROVE.**
Closure verified in order: U04 requires ⊆ U01–U03; U05 requires ⊆ U01–U04 (`while-loop`/`accumulator`/
`loop-counter` are U04); checkpoint-02 requires ⊆ U01–U05. No entry practices its own introductions
(U05 practices U04's `running-total`/`count-by-condition`, which are U04 introductions, not U05's — legal).
Introduced-once through U05: U01(10)+U02(6)+U03(4)+U04(7)+U05(3)=30 distinct catalog ids. Metadata kept
tight to definitely-used concepts (dropped speculative `input`/`type-conversion` from U04 to avoid the
metadata-mismatch findings seen on plan 071). U04 is `while`-only and is where `accumulator` (`x = x + …`)
becomes legal. Checkpoint-02 may use loops (now taught) but stays strict (no lists/builtins). Phase E is the
named verification phase. No open blockers.

_(Awaiting [sol] / [glm] (volcengine-plan/glm-5.3) / [fable].)_

## Content Review

_(4-way content-review gate — filled before PR.)_

## Post-Execution Report

_(Filled before shipping.)_
