# Plan 034 — Book 1 Worked-Example Ladders: U09 + U10 (rollout batch 3)

**Goal:** Apply the proven worked-example-ladder standard (plan 031) to U09 (Save Point — files) and U10
(Pet Simulator — classes), the Book-1 finale units.

**Architecture:** Same as the merged plan-031/032/033 batches: each introduced concept → minimal →
one-step-up → realistic ladder + one-line `**Notice:**`; completeness + gradual pacing (exactly one increment
per rung — the "realistic" rung stays FOCUSED on the concept; the full multi-concept program becomes a
separate **"Put it together:"** application cell, NOT a ladder rung — the pattern [sol] required in batches
1–2); rung count follows difficulty; reused concepts get a one-line recap. Lesson-only; concepts/exercises/
solutions/checkpoints unchanged; `lessons` advisory (book1 budget `[28, 44]`, current total 38). **Only U09
grows 2→3; U10 is ALREADY 3 lessons and STAYS 3** (its 3-section structure holds — ladders add rungs within
it, not a new lesson). Book1 total goes **38 → 39**. Standard in `docs/plans/031-book1-worked-examples.md`.

**Tech stack:** Jupyter lesson notebooks; `tools/`; `scripts/ci-local.sh`.

## Global Constraints (closure specifics — reviewer-enforced; concept-scan is unit-level/global-sets)

- **U09 Save Point** introduces `file-read, file-write, with-statement`; union has `list-append,
  string-methods, def-function, for-loop, parameters, return-value, list-loop, dict-access, f-string,
  in-operator, builtin-functions, dict-literal, if-statement, list-literal, print, variable, string-concat,
  string-literal, type-conversion, int-type, error-messages, input`. Order: file-write → file-read;
  **`with-statement` is CO-TAUGHT** — it wraps every file op (`with open(...) as f:`), so it shares the
  write/read ladders with its own focused "the `with` block closes the file automatically" rung/Notice (the
  import+random pattern from batch 1). Real file I/O EXECUTES under `exec-lessons` (writes/reads
  `savegame.txt`/`settings.txt`, as the shipped lesson already does) — keep the same filenames; the
  `FileNotFoundError` demo stays `no-exec`. Taught string method here: `.strip()`.
- **U10 Pet Simulator** introduces `class-def, init-method, attributes, methods`; union has `def-function,
  parameters, return-value, dict-access, while-loop, f-string, if-statement, accumulator, list-append,
  arithmetic, comparison, dict-literal, elif-else, for-loop, list-loop, list-literal, list-index, print, variable, int-type, input, string-literal, error-messages`. Order: class-def + `__init__` (CO-TAUGHT — a class is introduced with its
  `__init__`) → attributes (`self.x`, read/change) → methods. The class is re-defined to add methods (fine in
  one kernel). The `AttributeError` misspelling demo stays `no-exec`.
- **Execution:** `exec-lessons` runs every non-`no-exec` cell in one kernel; prefer executable rungs; `no-exec`
  the error demos. (U09 has no `input()` rungs in the core; U10's are executable with literal calls.)
- **Concepts unchanged:** U09/U10 `manifest.concepts` + coverage-map entries identical EXCEPT `lessons`.
  Exercises/solutions/checkpoints untouched; lessons open project-first.
- **House style:** allowed Book-1 constructs; unique ids; no stored outputs; `**Notice:**` lines;
  teacher-notes `## Pacing` blocks == the new `lessons` count.

## Out of scope

- Turtle units U03, U05 (final batch, plan 035). Any change to concepts/exercises/solutions/checkpoints.
- **Verification-phase note:** ships reworked unit lessons WITH a named verification phase (Phase C).

## Phases

### Phase A — U09 "Save Point" lesson ladders

Rework `book1/units/unit-09-save-point/lesson.ipynb`: ladders for `file-write` (`with open("f","w") as f:
f.write(one line)` → write several lines with a loop → write a mixed settings file), `file-read` (read the
whole file with `.read()` → loop the file object line-by-line → build a list with `.strip()`+`int()`+
`.append()`), with `with-statement` given a focused Notice/rung that the `with` block auto-closes the file.
`load_scores` helper + the `in`-search settings read become **"Put it together:"** applications. `\n` newline
explained. Set `manifest.yaml` `lessons: 3` (from 2) and update teacher-notes `## Pacing`.

### Phase B — U10 "Pet Simulator" lesson ladders

Rework `book1/units/unit-10-pet-simulator/lesson.ipynb`: ladders for `class-def`+`init-method` (a minimal
`class Pet` with `__init__` setting one attribute → set several attributes), `attributes` (read `buddy.name`
→ two independent objects → change an attribute `luna.hunger = 7`), `methods` (add one method → a method with
a parameter (`feed(amount)`) → a method that changes attributes (`play`/`pass_time`) → a method that returns
(`status`)). The foods-dict feed, the multi-pet loop, and the `while buddy.happiness < 10` play-loop become
**"Put it together:"** applications. **U10 `manifest.yaml` STAYS `lessons: 3`** (already 3; the 3 sections
just get richer ladders) — keep teacher-notes at 3 lessons (update the pacing text to the ladder framing).
Note: after re-defining `Pet` to add methods, RE-INSTANTIATE the pets (make new `Pet(...)` objects) so they
have the new methods; and `__init__` is itself a method that sets attributes, so the class+`__init__` rung
names them in passing (usage-order ≠ naming-order, sanctioned).

### Phase C — map/syllabus + Verification (named verification phase)

- `book1/curriculum/coverage-map.yaml`: set U09 `lessons: 3` (U10 is already 3 — leave it) (= manifests;
  book1 total 38 → **39**, ≤ 44). `book1/syllabus.md`: update the U09 arc-table `Lessons` cell (2→3; U10's row
  is already 3) and the figures — "~38 lessons"→39, "summing to 38 — 30 unit lessons"→"39 — 31 unit lessons",
  "~36–38 class sessions"→"~37–39". Update the ladder parenthetical to name U09 and U10 (both reworked here).
- `scripts/ci-local.sh` ALL GREEN: `exec-lessons` (file I/O + class cells run clean), `concept-scan`,
  `coverage`/`prereq`, `lesson-budget` (≤ 44), manifest==map, structure/hygiene/noexec, PDF, pre-merge guard.
- **Closure + completeness/gradual audit (primary content-review duty):** no rung uses a later-in-unit/
  untaught concept; each ladder complete + one-increment with the realistic rung FOCUSED (full programs
  framed "Put it together"); co-taught `with-statement` / `class-def`+`__init__` each get a genuine focused
  rung; Notices accurate; lessons open project-first; `## Pacing` blocks == `lessons`.

## Post-Execution Report

**Status:** Implemented; `scripts/ci-local.sh` ALL GREEN (pre-merge-guard OK, CI_EXIT=0).

- **Phase A — U09 Save Point** (`lesson.ipynb` rebuilt 14→24 cells, 10 code + 1 `no-exec`):
  3 lessons. L1 file-write ladder (one line → loop several scores → mixed `settings.txt`);
  `with-statement` co-taught with a focused auto-close Notice. L2 file-read ladder with bridge
  (`.read()` whole → `for line in f:` print → `.strip()` clean → `int()`+`.append()` rebuild list).
  L3 **"Put it together"**: `load_scores(filename)` helper (return) + `in`-search of `settings.txt`;
  `FileNotFoundError` demo `no-exec`. manifest + map `lessons: 2→3`; teacher-notes `## Pacing` = 3.
- **Phase B — U10 Pet Simulator** (`lesson.ipynb` rebuilt 31 cells, 13 code + 1 `no-exec`):
  STAYS 3 lessons. L1 `class-def`+`__init__` co-taught ladder (minimal class → several attributes)
  + `attributes` ladder (read `buddy.name` → two independent objects → change `luna.hunger`). L2
  `methods` ladder GROWN incrementally (`play` → `feed(amount)`+return → `pass_time` → `status` with
  if/elif/else+return), re-instantiating `buddy` after each class redefinition. L3 **"Put it
  together"**: foods-dict feed, multi-pet loop, `while buddy.happiness < 10`; `AttributeError` demo
  `no-exec`. manifest/map unchanged at `lessons: 3`; teacher-notes pacing reframed to the ladder.
- **Phase C:** coverage-map U09 `lessons: 3` (U10 already 3); book1 total **38 → 39** (31 unit
  lessons, ≤ 44). syllabus arc-table U09 row 2→3, figures "~39 lessons", "summing to 39 — 31 unit
  lessons", "~37–39 class sessions", ladder parenthetical names U09 (U10 already 3). All CI checks
  green: concept-scan (closure within each union, order write→read / class→attrs→methods),
  exec-lessons (file I/O + class cells run clean under one kernel; error demos `no-exec`),
  coverage/prereq/manifest==map, structure/hygiene/noexec, PDF, pre-merge-guard.

## Plan Review

### Round 1 (2026-09-09, HEAD 5dd5c02) — [glm] REJECT · [fable] REJECT · [sol] pending

Both externals verified closure (U09 write→read + co-taught `with`; U10 class+`__init__` co-taught; both
within union), the "Put it together" framing, gitignored file-I/O, and Phase C adequacy. They REJECT on one
shared factual error:

1. `[FIXED]` **[glm B1 / fable B1] U10 is ALREADY `lessons: 3`** (shipped), not 2 — the plan double-counted it
   (no-op "set 3 from 2"; total "38→40" wrong). → Corrected: only U09 grows 2→3, U10 stays 3; book1 total
   **38→39**, 31 unit lessons; Phase B/C/Architecture + syllabus figures all fixed.
2. `[FIXED]` **[glm/fable N1] U10 union list omitted `string-literal`/`error-messages`** → added.
3. `[FIXED]` **[glm/fable] U10 class re-definition** — Phase B now says RE-INSTANTIATE pets after adding
   methods (so they have them), and notes `__init__` names attributes/methods in passing (usage≠naming,
   sanctioned).
4. `[noted]` **[glm/fable] watch at content gate**: U09 file-read rung 3 (`.strip()`+`int()`+`.append()`) and
   U10 `status` (return + if/elif/else) may need a bridge — add one rather than widening the rung.

Closure, hygiene (gitignore covers savegame.txt/settings.txt; exec cwd=unit_dir), metadata, and Phase C all
verified sound. Re-confirming [glm]/[fable]; [sol] pending.

### Round 2 (HEAD eaa357c) — [fable] APPROVE · [sol] APPROVE · [glm] AWN · CONSENSUS

B1 (U10-already-3 double-count) verified FIXED by all three (arithmetic 38→39/31 unit lessons exact). [glm] AWN (tightened an editorial syllabus parenthetical — done); [fable] APPROVE; [sol] APPROVE.

**CONSENSUS — plan-review gate CLOSED:** [self] APPROVE · [fable] APPROVE · [glm] APPROVE WITH NITS · [sol] APPROVE. Cleared for implementation. Author notes: only U09 lessons 2→3 (U10 stays 3); add a bridge if U09 file-read rung-3 (strip+int+append) or U10 status (return+if/elif/else) jumps; re-instantiate pets after the class gains methods.

## Content Review

4-way content-review gate (HEAD d8ff840). Verdicts tagged [self]/[sol]/[glm]/[fable].

### [self] APPROVE WITH NITS (2026-09-10)

Audited both notebooks cell-by-cell. CLOSURE ✓ — every rung stays within its unit's manifest
union and lesson order (U09 write→read; U10 class→attrs→methods); only `.strip()` string method in
U09; U10 `play`/`feed`/`pass_time` accumulators + arithmetic + comparison + elif-else all in U10's
union. COMPLETENESS/PACING ✓ — each ladder graduates one increment per rung; full multi-concept
programs (U09 `load_scores`+settings search; U10 foods-dict/multi-pet/while-play) are framed
**"Put it together"** cells, not rungs. PROJECT-FIRST ✓ (both open on the hook). Error demos
(`FileNotFoundError`, `AttributeError`) `no-exec`. teacher-notes `## Pacing` == lessons (U09=3,
U10=3). Nits watched (not blocking): U09 file-read rung 4 (`int()`+`.append()`) and U10 `status`
(if/elif/else + return) each lean on reused scaffolding to stay realistic — each adds a single new
file/method idea, so within the one-increment bar; flag if an external reviewer reads them as jumps.

### Round 1 (HEAD d8ff840) — [fable] APPROVE WITH NITS · [glm] REJECT · [sol] REJECT

External reviewers confirmed closure (both unions, orders, `.strip()`-only, re-instantiation),
project-first opens, "Put it together" framing, and pacing counts (U09=3, U10=3). Blocking findings
(all `[FIXED]`):

1. `[FIXED]` **[sol #3 / glm B1] U10 `methods` ladder not one-increment** — `feed` added a parameter
   AND a return in one rung; `pass_time` added no new capability as its own rung; `status` bundled
   decision + print + return. → Rebuilt to a monotone ladder: rung 1 the method concept (two
   same-shape mutators `play`+`pass_time`), rung 2 `feed` adds only a **parameter** (no return),
   rung 3 `feed` adds only a **return**, rung 4 `status` adds only a **decision** (print-only,
   return dropped).
2. `[FIXED]` **[sol #1] U09 file-read ladder jump** — the final rung created a list, `int()`-
   converted, and `.append()`-ed at once. → Added an intermediate rung that collects cleaned lines
   into a LIST of strings (`.append()` only); the final rung's single new step is `int()`.
3. `[FIXED]` **[sol #2] U10 class+`__init__` rungs read attributes before the attributes ladder** —
   `print(buddy.name)` externally read an attribute, pre-empting the attributes concept. → The
   class+`__init__` construction rungs now confirm with a literal `print("Made a new pet!")`; the
   first external attribute read is the attributes ladder's rung 1.
4. `[FIXED]` **[fable N1] U09 teacher-notes literal newline** — the `\n` code span was split across a
   real line break. → Restored to the two-character `\n`.
5. `[FIXED]` **[glm N1 / fable N2, N3 / sol] Notice over-claims** — U09 write rung-2 Notice trimmed
   to "one score per line"; U09 int rung Notice names only `int(...)`; U10 `feed`/`status` Notices
   each now name exactly one new thing. **[fable N4]** U10 attributes rung 1 now reads `happiness`
   (was a duplicate of the init rung's readback).

### Round 2 (HEAD pending) — re-dispatched to [sol]/[glm]/[fable]

_(awaiting verdicts)_
