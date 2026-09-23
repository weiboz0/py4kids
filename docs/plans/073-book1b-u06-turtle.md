# Plan 073 — Book 1b Unit 06 (Turtle Geometry)

**Origin:** Book 1b buildout ("full book 1b implementation").
**Design:** `docs/designs/005-book1b-concept-first.md` §3 (U06 row), §7 (turtle exercises verified by
execution + `turtle-check`; the assert-exemption is the per-exercise authoring rule, NOT the CI minimum),
§8 (turtle runs as `.py` scripts).
**Templates:** Book 1b U01–U05 (prose/teacher-notes); **Book 1 `unit-03-turtle-art-studio` for the turtle
FILE STRUCTURE** (assets/*.py + no-exec lesson cells + headless-companion solutions + turtle-check).

## Scope

One unit — **U06 Turtle Geometry** — in the turtle format, done ALONE (distinct format; first terminal
encounter). Next checkpoint is after U08, so none here. Book 1b stays `buildout: true`.

## Coverage-map entry (the contract) — 7-key shape

**unit-06-turtle-geometry** — `kind: unit`, `title: "Turtle Geometry — drawing with loops and angles"`, `lessons: 3`
- introduces: `[import-statement, turtle-basics, turtle-drawing]`
- requires: `[for-loop, range-function, arithmetic, variable]`
- practices: `[nested-loops, loop-counter, accumulator, int-type, float-type, comment, naming, run-program, error-messages]`

Closure: requires ⊆ U01–U05 (for-loop/range U05, arithmetic U02, variable U01); `import-statement`
introduced here (design §3/§5). No self-practice. 30→33 introduced-once.

### Design §6 practice-coverage record (reworded per [glm]/[sol])
A unit cannot practice its OWN introductions, so U06's three intros (`import-statement`/`turtle-basics`/
`turtle-drawing`) get their later practice sites in **U07** (`draw_polygon`) and **U08** (turtle random
walk) per design §3 — deferred, not claimed here. U06 ADDS practice sites for earlier intros:
`nested-loops` (rings/spirals), `loop-counter` (side/shape counters), `accumulator` (growing spiral
`side = side + step`), `float-type` (the polygon angle `360 / n`, e.g. `360 / 7 = 51.428…`),
`int-type` (integer side/shape/pen-down counts and integer `n`/`side` in the headless companions),
`error-messages` (the wrong-directory `can't open file` and the missing-`turtle.`-prefix `NameError`,
read as callbacks), `comment`/`naming` (the asset-script convention), `run-program` (the terminal run —
this unit's core activity). Every practiced concept is introduced ≤ U06 (float-type/int-type U02,
error-messages/comment/naming/run-program U01, nested-loops U05, loop-counter/accumulator U04). All 30
pre-U06 introductions remain practiced (plan-072 record). Capstone anchor dormant (buildout).

## File structure (clone Book 1 `unit-03-turtle-art-studio` EXACTLY)

Turtle CODE lives ONLY in `assets/*.py` (run headless by `turtle-check` via the `fake_turtle` stub) and in
`lesson.ipynb` **`no-exec`-tagged** cells. **`solutions.ipynb` code cells carry no `import turtle`** —
`_solution_policy_findings` (notebooks.py:631, solutions.ipynb ONLY) flags a GUI import regardless of
`no-exec` (notebooks.py:287) and requires **≥3 non-vacuous assert cells** notebook-wide (notebooks.py:281-283).
**`exercises.ipynb` code cells also carry no `import turtle`** — this one is an AUTHORING rule, NOT a CI check
(exercises are never executed; `_solution_policy_findings` does not scan them): the turtle program is a `.py`
asset the student runs in the terminal, so a turtle import in an exercise notebook cell would be dead/misleading.

- **assets/lN_*.py** — lesson turtle scripts (`import turtle`, draw one thing, one terminal `turtle.done()`).
- **assets/exN_*.py** — exercise STARTER scripts: a VALID CLOSED placeholder that already draws (≥1 pen-down
  move, e.g. a small square) with the task in comments (NOT an empty TODO — every asset runs under
  turtle-check and must make ≥1 pen-down move and close its path).
- **assets/solutions_*.py** — finished turtle programs.
- **lesson.ipynb** — markdown teaching; turtle demos shown in **`no-exec`** code cells; optional NON-turtle
  headless cells (the "angles as math" computation) may run. Problem-first opening (see below).
- **exercises.ipynb** — mini-CP statements: `## Exercise N` / `### Title` / background / **Specification** /
  a **checkable "expected output"** for a drawing = the shape named PLUS a checkable number (n, side, the
  turn angle `360 / n`, total turn, pen-down-move count, "ends where it started: yes/no") / which
  `assets/exN_*.py` to complete and run in the terminal. Solution-free, NO executed outputs, NO "Solution"
  headings, ≥8 exercises, core ≤7, ≥2 `stretch` Challenge. Code cells (if any) are HEADLESS (no `import turtle`).
- **solutions.ipynb** — mirrors every `## Exercise N`. Per exercise: a **markdown fenced block** "The real
  program (`assets/solutions_*.py`)" showing the turtle code, AND a **headless companion code cell** that
  computes the math (`angle = 360 / n`; `total_turn = n * angle` is a FLOAT, so assert closure with a
  tolerance — `abs(total_turn - 360) < 1e-6` — NOT `== 360.0`, which is unreliable across n; side/shape/
  pen-down counts as ints, ends-at-start bool) with **asserts** (≥3 non-vacuous assert cells
  notebook-wide; NO `import turtle`). This is where "angles as
  math" is written down and blind-solved by the gate roster; turtle-drawing correctness is verified by
  `turtle-check` on the `.py`.
- **teacher-notes.md** — Goals / Pacing (per-lesson 60-MIN CUTs) / Common mistakes / Discussion prompts /
  Differentiation. (Asset presence is enforced by `structure-check`: `layout_findings` requires an `assets/`
  dir when `turtle-basics` appears (notebooks.py:348-357), and `_assets_reference_findings` requires every
  referenced `assets/*.py` to exist and compile (notebooks.py:367-392) — NOT `manifest-check`.)
- **manifest.yaml** — matches the coverage-map entry.

## Turtle API — a fixed **subset** of the `fake_turtle` stub (turtle-check executes every asset)

**Module-level style ONLY:** `import turtle` then `turtle.forward(...)` etc. — NO `t = turtle.Turtle()`
and NO `screen = turtle.Screen()` (the stub exposes `Turtle`/`Screen` at fake_turtle.py:102-124, but
objects/attributes are Book 2; module-level matches the u03 template).
Use ONLY: `forward`, `backward`, `left`, `right`, `penup`, `pendown`, `pencolor`, `color`, `pensize`,
`speed`, `bgcolor`, and one terminal `done()`. **Do NOT use** `begin_fill`/`end_fill`/`fillcolor`, `circle`,
`goto`, `setheading`, `dot`, `stamp`, `hideturtle`, `shape`, `setup`, `title`, `width`, `up`, `down` — the
stub genuinely lacks these (fake_turtle.py:50-95 defines no such module fns) → `AttributeError` →
turtle-check FAIL. **`exitonclick` is the one exception:** the stub HAS it as a no-op (fake_turtle.py:98), so
it would NOT fail turtle-check — we still ban it by CONVENTION and use one terminal `done()` (matching Book 1
u03); Phase E audits this statically, since the tooling can't. So **`turtle-drawing` = pen
color (`pencolor`/`color`) + `pensize` + shapes drawn with `forward`/turn — NO fill, NO circle.** Use `left`
consistently (a Notice states `left(90)` mirrors `right(90)`). Loop variable is a real name (`corner`,
`side_number`, `shape`) — NOT `_` (never taught).

## Path-closure contract (fake_turtle.py:207-220)

Every `assets/*.py` must EITHER close its path (end at the draw-start position AND total heading change ≡ 0
mod 360, both within the tooling's 1e-6 tolerance, fake_turtle.py:211-215) OR carry the exact comment
`# turtle-check: open-path`. Also: ≥1 pen-down move; < 10,000 moves.
- Polygons: `n × (360 / n) == 360` for ANY n ≥ 3 — the float angle closes within tolerance (empirically
  verified: n=7 with `left(360 / n)` ends at ~(1e-13, 2e-14), total turn 360.0000000000001, both < 1e-6;
  Book 1 `u03/assets/l2_polygon.py` ships `360 / n` with n=7 and passes CI). **`//` is NOT required for
  closure** — that was the round-1 error. Rings: `shapes × between_turn == 360`. Stars: 5-point uses
  `720 / 5 == 144.0`, and `5 × 144 ≡ 0 (mod 360)` — closes.
- The **growing spiral** (L3) and any open corner do NOT close → carry `# turtle-check: open-path`
  (Book 1 `assets/l1_corner.py` precedent). exN STARTERS draw a closed placeholder (so they pass too).

## Teaching ("angles as math")

- **Lesson 1 — Move & Draw (import-statement, turtle-basics).** Problem-first opener (u03 move): the teacher
  runs the L3 gallery script as a 30-second teaser — "we'll build this; today, the first shape." Then L1's
  OWN reachable payoff: "the turtle only knows forward and turn — what turn makes a square? Predict, then
  run." `import turtle`, `forward`/`left`/`right`, `penup`/`pendown` (a travel-without-drawing rung); a
  square by hand, then with a `for` loop. **FIRST TERMINAL ENCOUNTER (~15 min, budget it like Book 1 u03):**
  File → New → Terminal, `cd` to the unit dir, `python assets/l1_square.py`, edit-save-rerun; expect to
  repeat twice. (The exterior-angle payoff for *any* polygon is L2.)
- **Lesson 2 — Any Polygon (turtle-drawing).** The exterior-angle insight, taught as the GENERAL rule with
  true division: a regular n-gon turns `360 / n` each corner
  (`for corner in range(n): forward(side); left(360 / n)`), + `pencolor`/`pensize` (NO fill). **n=7 is a CORE
  predict-then-run rung, not a Challenge:** `360 / 7 = 51.428…`, "the turtle turns by a decimal just the
  same," and the heptagon closes — mirroring Book 1 u03's non-negotiable-core discovery. `float-type` (U02)
  is what makes the rule honest for every n. **`//` is a CONTRAST Notice only:** "`360 // n` is a
  whole-number shortcut that lands on the same angle ONLY when n divides 360 (3/4/5/6/8/9/10/12); for n=7,
  `360 // 7 = 51` and `7 × 51 = 357 ≠ 360`, so the shape wouldn't close — that's why we use `/`." The n=7
  Challenge becomes **"predict what `left(360 // 7)` draws and explain the gap,"** never the place the
  correct rule first appears. Stars use `720 / n` (5 → 144.0, "two full turns").
- **Lesson 3 — Patterns with Nested Loops (nested-loops).** A ring of polygons (`for shape … : draw; left`),
  then a growing spiral (`side = side + step` — `accumulator`; open-path marker). Gallery Final build.

Per-lesson 60-MIN CUT: L1 keep the square loop AND the edit-save-rerun live (that terminal run IS this
unit's core `run-program` activity, introduced this lesson — never cut it); drop the `penup`/`pendown`
travel rung instead. L2 the `360 / n` polygon loop is non-negotiable core (drop color/pensize flourishes,
defer the n=7 contrast Notice). L3 ring live, growing spiral as "try it".

## Beginner traps (teacher-notes Common mistakes + lesson Notices)

**Calling `forward(100)` without the `turtle.` prefix after `import turtle` → `NameError`** (THE trap of the
introduced concept — module-level import means every call is `turtle.forward`; read the error, add the
prefix; an `error-messages` callback); running from the wrong directory (`can't open file` — a second
`error-messages` callback); putting `turtle.done()` INSIDE the loop (draw stalls after one side) — it goes
once, at the very end; the turtle window opens BEHIND JupyterLab; closing the window ends the script (re-run,
don't rescue); forgetting the turn → a straight line; forgetting `forward` → a spinning turtle; **exterior
vs interior angle** (a triangle turns 120, not 60 — let the wrong prediction happen, then fix it); `left` vs
`right` mirror; `penup` without `pendown` (nothing draws); missing final `turtle.done()` (window flashes and
vanishes); `range(n)` gives 0..n-1.

## Value plan (per plan-072 lesson)

Each lesson rung / exercise / Challenge uses a DISTINCT `(n, side, color)` and its own checkable number
(distinct from the lesson rungs and from each other). List them in teacher-notes so the gate can check.

## Phases

### Phase A — plan-review gate (4-way). No implementation until consensus.
### Phase B — contracts: coverage-map entry (7-key: kind/title/lessons + introduces/requires/practices) + syllabus row + manifest; `--book book1b coverage-check` + `prereq-check` GREEN.
### Phase C — statements + assets (Codex): lesson.ipynb (no-exec turtle demos) + exercises.ipynb + assets/lN_*.py + assets/exN_*.py starters (closed placeholders). Pin: module-level API subset + `360 / n` angle + closure rule; include an error-reading Notice (missing-`turtle.`-prefix `NameError`, wrong-dir `can't open file`) so the `error-messages` practice is real.
### Phase D — solutions (SEPARATE fresh Codex): solutions.ipynb (markdown "real program" blocks + headless-companion asserts, NO `import turtle`, ≥3 assert cells) + assets/solutions_*.py; verify `turtle-check` passes on all scripts.
### Phase E — teacher-notes (inline) + verification: full `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN
across the three books (esp. `turtle-check`, `structure-check` incl. the GUI-import + ≥3-assert rules,
`exec-lessons` skipping no-exec turtle cells, `stretch-check`, layout/asset presence, PDF). **AST/static audit:**
every `assets/*.py` uses only the pinned method subset, uses module-level style only (no `turtle.Turtle()`/
`Screen()`), uses **`/` not `//` in any angle computation** (guards against silently reintroducing the
rejected rule), ends with exactly one terminal `turtle.done()` (no `exitonclick()`), and either closes its
path or carries `# turtle-check: open-path`. Scope allowlist = this plan + the U06 tree + coverage-map + syllabus.

## Out of scope
- U07–U13, checkpoints, Algorithm Challenge — plans 074+. No tooling/stub extension, no governance/Book-1/2 changes.
- **Verification phase:** Phase E is the named verification phase (unit → required).

## Plan Review

### Round 1 (2026-09-23) — [self] APPROVE (superseded by folds below); [sol] REJECT; [glm] REJECT; [fable] REJECT.
All three REJECTed on the turtle-format spec (not the curriculum contract, which all verified GREEN:
closure, 30→33 introduced-once, honest metadata, named verification). Blockers, ALL FOLDED into the rewrite
above:
- **solutions.ipynb** re-specified to the u03 convention: NO `import turtle` in code cells; turtle program in
  a markdown "real program" block + `assets/solutions_*.py`; solutions code cells are **headless companions
  with ≥3 non-vacuous asserts** (the §7 exemption is the per-exercise rule, not the CI minimum). ([fable]1/[sol]1/[glm]1-2)
- **Turtle API pinned to the fake_turtle stub subset** (no fill/circle/goto/setheading/etc.); turtle-drawing
  = color + pensize + polygons. ([sol]2/[glm]3/[fable])
- **Path-closure contract** added (close, or `# turtle-check: open-path`; ≥1 pen-down; exN starters draw a
  closed placeholder). ([sol]3/[glm]4/[fable]2)
- **Lifecycle** pinned: one terminal `turtle.done()`, no `exitonclick()`; Phase-E AST audit. ([sol]4/[glm]6)
- §6 record reworded (U06 doesn't practice its own intros; deferred to U07/U08). ([glm]5)
- 7-key coverage entry (kind/title) ([glm]7); asset-presence attribution → structure-check/layout ([sol]6/[glm]).
- [fable] P1/P2 folded: FIRST-TERMINAL-ENCOUNTER pacing; beginner-traps list; the `//`-angle "why" + n=7
  Challenge (stars 720//n); per-lesson cuts; "expected output" = shape + checkable number; named loop var;
  value plan; metadata `practices += accumulator, run-program`.

### Round 2 (2026-09-23) — rewritten to the correct turtle format. Re-dispatched [sol]/[glm]/[fable].

**[self] APPROVE WITH NITS.** Re-verified the fold against the tooling:
- fake_turtle.py:50-124 confirms the supported module-level set = forward/backward/left/right/penup/pendown/
  pensize/pencolor/color/speed/bgcolor/done (+ `exitonclick` and `Screen`/`Turtle` as no-ops); the plan's
  banned list (fill/circle/goto/setheading/dot/stamp/hideturtle/shape/setup/title/width/up/down) is exactly
  the unsupported set. **Self-caught nit (FIXED):** the draft wrongly claimed `exitonclick` would
  `AttributeError` — it is a no-op (fake_turtle.py:98); corrected to "banned by u03 convention, not by the
  stub," Phase E audits it statically.
- fake_turtle.py:147/200-219 confirms the closure contract (marker `# turtle-check: open-path`, >=1 pen-down,
  <10000 moves, position+heading closure) as the plan states.
- notebooks.py `_solution_policy_findings` (GUI-import ban + >=3 non-vacuous asserts) is satisfied by the
  headless-companion solutions.ipynb spec.
- Contract: requires ⊆ U01–U05 (closure holds); introduces = the 3 new; practices honest; §6 record no longer
  self-practices; named verification phase (E) present.

**[sol] APPROVE** — curriculum contract sound; no turtle API mismatch (and confirmed the `exitonclick` fix
reads correctly); closure contract + closed-starter requirement correct; solutions format satisfies policy
(headless companions exceed the 3-assert minimum); Phase E is the named verification phase; no evident later
content-gate blocker.

**[glm] APPROVE WITH NITS** — no blockers; three wording/citation nits, ALL FOLDED (below).

**[fable] REJECT** — one blocker + nits, all folded (below). The blocker is a genuine catch: `360 // n` as
the CANONICAL polygon rule is mathematically dishonest and its tooling rationale was false — [fable] ran the
stub and showed `left(360 / n)` closes a 7-gon within the 1e-6 tolerance, and Book 1 `u03/l2_polygon.py`
already ships `360 / n` with n=7 passing CI. Teaching `//` as core (fixed only in a `stretch` Challenge) would
leave students with a wrong general rule that U07's `draw_polygon` inherits.

### Round-2 fold (applied 2026-09-23; re-dispatching round 3)
- **[fable] BLOCKER — angle rule.** `angle = 360 / n` is now the taught CORE rule (true division); **n=7 is a
  core predict-then-run rung** (`51.428…`, closes), mirroring u03's non-negotiable-core discovery. `//`
  demoted to a CONTRAST Notice ("whole-number shortcut, exact only when n | 360"); the n=7 Challenge is now
  "predict what `left(360 // 7)` draws + explain the gap." `practices += float-type` (the float angle) and
  `int-type` kept honest via `total_turn`/counts in the headless companions; closure bullet reworded (`/`
  closes within tolerance; `//` NOT required). Stars use `720 / n`.
- **[fable] nits:** beginner traps += missing-`turtle.`-prefix `NameError` (THE trap of the introduced
  concept) and `done()`-inside-loop; `practices += error-messages` (two error-reading callbacks, Phase C now
  requires an error Notice); L1 60-min cut fixed (keep edit-save-rerun = the `run-program` core; drop the
  `penup`/`pendown` travel rung — the polygon loop is L2); L1 gains a u03-style L3-gallery teaser so L1 has
  its own reachable payoff; module-level style pinned (`turtle.forward`, no `t = turtle.Turtle()` — objects
  are Book 2).
- **[glm] nits:** `exitonclick` mechanism reworded (stub HAS it as a no-op; banned by convention, Phase-E
  audited) — the "PIN to subset" heading now reads "a fixed subset"; exercises.ipynb no-turtle-import
  clarified as an AUTHORING rule (NOT CI — `_solution_policy_findings` scans solutions.ipynb only,
  notebooks.py:631); asset-presence citation completed (`layout_findings` 348-356 + `_assets_reference_findings`
  367-392).

### Round 3 (2026-09-23) — CONSENSUS. All four APPROVE / APPROVE WITH NITS, no blockers.
- **[self] APPROVE** — the fold is a clean improvement: honest `360 / n` core rule, metadata backed by real content, no regression.
- **[sol] APPROVE WITH NITS** — angle fold correct; metadata honest; format intact; requires-closure + Phase E explicit. NIT: `total_turn` is a float, so "integer total_turn"/`== 360.0` is inaccurate — use tolerance.
- **[glm] APPROVE** — no nits; empirically swept n=3..9999 confirming `360 / n` closes ≪ 1e-6; all metadata honest (9 practices ≤ U06, 30→33 introduced-once, no self-practice); no format regression.
- **[fable] APPROVE WITH NITS** — blocker + all r2 nits confirmed resolved. NITs: (1) same float `total_turn` wording; (2) add "no `//` in `assets/*.py` angle computation" to the Phase-E audit.

**Round-3 nit fold (applied 2026-09-23):** §6 record `int-type` no longer rests on `total_turn` (now
side/shape/pen-down counts + integer `n`/`side`); solutions.ipynb spec asserts closure with tolerance
(`abs(total_turn - 360) < 1e-6`), not `== 360.0`; Phase-E audit adds "`/` not `//` in angle computation"
+ module-level-only; `layout_findings` citation 348-356→348-357 ([glm] immaterial note). **Gate PASSED.**

## Content Review

### Round 1 (2026-09-23) — [self] APPROVE; [glm] APPROVE WITH NITS; [fable] APPROVE WITH NITS; [sol] REJECT.
All four blind-solved 9/9 with zero correctness mismatches; project-first hook confirmed; ci-local ALL GREEN.
One REJECT ([sol]) on value-distinctness; the rest are nits. Dispositions:

**Value-distinctness ([sol]#1 Must Fix):** partially valid.
- `[FIXED]` Ex1/Ex5 were both squares (n=4); Ex5 → travel + **octagon** (n=8, 45°). Ex4/Ex9 were both
  heptagons (n=7, reusing the lesson's n=7); Ex9 → an **eleven-sided shape** (n=11), which also enlarges the
  `//` gap to a visible 8° (addresses [fable]#1). This removes both exact-shape repeats and the lesson-number reuse.
- `[WONTFIX]` Ex3 pentagon (n=5) vs Ex8 star (n=5): distinct angle (72°/144°), total turn (360°/720°) and
  drawing; "5" is intrinsic to a five-point star. Same-shape core polygons necessarily share that shape's
  angle with any lesson example, but sides/colours/contexts differ so no answer can be transcribed — the
  distinctness rule (no copyable values) holds. [glm]/[fable] both judged distinctness satisfied.

**Provenance ([sol]#4 Should Fix):** `[WONTFIX]` — `tools/notebooks.py:445-446` MANDATES `provenance:
original` for every unit and `adapted-from` is not a valid `MANIFEST_KEYS` entry, so the proposed fix would
fail CI. Measured overlap with Book 1 u03 is 9 six-word sequences, ALL mechanical (run-command file paths,
the "ends where it started" checkable convention, a generic square description) — no substantive content
reuse; [glm] and [fable] independently judged it original. Reworded the couple of generic echoes anyway.

**Backward in Goals ([sol]#2 / [glm]#2 / [fable]#5):** `[FIXED]` — removed `backward` from teacher-notes Goals.

**Ex9 "in your notes" has no response location ([sol]#3):** `[FIXED]` — added a markdown prediction/response
cell in exercises.ipynb for the `//`-gap comparison.

**"Expected output" lists un-printed values ([fable]#2 Should Fix):** `[FIXED]` — relabelled "Check
yourself:" and added `print()` of the key verifiable numbers (Ex7 accumulator `print(side)`→95, Ex4 angle),
so the claims are observable in the terminal.

**Nice-to-haves:** `[FIXED]` starter-comment colours aligned to specs ([fable]#3); one-sentence glosses for
`pencolor`/`pensize` (L1) and `bgcolor`/`speed(0)` (gallery) ([glm]#1/[fable]#4); `left(92)`/`left(91)`
motivated ([fable]#6); Ex4 now asks the student to state the angle before running ([fable]#7).
`[self]` (verification, [sol]#5): the native `exec-solutions` DID pass in the main env (full ci-local ALL
GREEN); [sol]'s sandbox couldn't run `uv`, so this is a sandbox limitation, not a content defect.

### Round 2 (2026-09-23) — CONSENSUS. [self] APPROVE; [glm] APPROVE; [fable] APPROVE; [sol] APPROVE WITH NITS.
All four blind re-solved the changed exercises (Ex5 octagon, Ex9 eleven-sided) with zero mismatches; the
value-distinctness blocker is RESOLVED (core n now 4/3/5/7/8/6, distinct); provenance WONTFIX confirmed
acceptable (all three externals verified `notebooks.py:38/426/445` mandate `provenance: original`). No `[OPEN]`
Must/Should findings remain. Nits folded:
- `[FIXED]` ([sol]/[glm]/[fable]) Ex5 starter renamed `ex5_travel_square.py` → `ex5_travel_octagon.py`
  (references updated; structure-check PASS).
- `[FIXED]` ([fable]) Ex9 starter comment "explain its 8-degree gap" → "the shortcut's 8-degree gap".
- `[WONTFIX]` colour/color spelling drift (cosmetic; Python identifiers unaffected) and the optional Ex9
  fast-finisher enrichment ([fable], out of the approved scope).

**Content-review gate PASSED (4-way consensus).** Proceeding to PR.

## Post-Execution Report

**Status: implemented, ci-local ALL GREEN (2026-09-23). Content-review gate next.**

Shipped `book1b/units/unit-06-turtle-geometry/`:
- **Phase B (contracts):** coverage-map entry + manifest + syllabus row; `coverage-check`/`prereq-check`
  GREEN; 30→33 introduced-once, no duplicate introductions, requires/practices all introduced ≤ U06.
- **Phase C (statements + assets, Codex gpt-5.6-sol):** `lesson.ipynb` (34 cells, 9 no-exec turtle demos —
  L1 Move & Draw + gallery teaser + first-terminal-encounter + NameError/can't-open-file notices; L2 Any
  Polygon `360 / n` core rule, n=7 core rung, `//` contrast Notice, `720 / n` star; L3 ring + growing spiral
  + gallery), `exercises.ipynb` (9 exercises: 7 core + 2 stretch), 9 lesson assets + 9 exercise starters.
- **Phase D (solutions, SEPARATE fresh Codex):** `solutions.ipynb` (headless companions, NO `import turtle`,
  84 non-vacuous asserts, all 9 exercises mirrored, `//` only in the Ex9 gap contrast) + 9 `solutions_ex*.py`.
- **Phase E (teacher-notes inline + verification):** `teacher-notes.md` (full heading set + value plan +
  beginner traps). `TMPDIR=/dev/shm bash scripts/ci-local.sh` → **ALL GREEN** (registry/lint, unit tests,
  notebook exec + hygiene, manifest/prereq/coverage/stretch, turtle-check, structure-check, PDF build,
  pre-merge-guard). AST audit over all 27 assets: ALL CLEAN (module-level only; `360 / n` never `//` in
  drawn assets; no banned methods; exactly one terminal `turtle.done()`, no `exitonclick`; closure or
  `# turtle-check: open-path`).

Values are distinct per exercise/rung (value plan in teacher-notes). No deviations from the approved plan.
