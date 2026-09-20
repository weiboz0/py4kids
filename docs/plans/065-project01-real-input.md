# Plan 065 — Project 01 (Arcade Night) real-input treatment

**Design:** `docs/designs/003-book1-real-input.md` (v6), §2 project markdown path. First of two Book-1 projects.

## Motivation

Project 01 (arcade-night: functions + menu loop + scoreboard, using `random`) is the FIRST project to receive
the design-003 real-input norm. Projects differ from units/checkpoints:
- The **brief.ipynb scaffolds already read `input()`** — they ARE the real interactive arcade the student
  builds (menu loop reads the choice; the game scaffolds read the guess / quiz answers).
- The **solutions.ipynb** proves the logic WITHOUT keyboard input: parametrized reference functions
  `lucky_guess(guess)` / `quick_quiz(answer_one, answer_two)`, a **scripted "Fixed arcade driver"** (choices
  `1`,`2`,`q` hard-wired), asserts, and `random.seed(4)`. The `arcade-ci-note` already states the split:
  "A student's real arcade uses `input()` for the menu in `brief.ipynb`; this reference calls the games with
  fixed values to prove the logic without keyboard input."

What the norm ADDS: make the **real interactive arcade** VISIBLE in the solutions as a `**The real program**`
markdown twin of the scripted fixed driver — the input()-reading form the ci-note describes, so the fixed twin
(scripted + asserts) and the real form sit side by side. Real-form is markdown (fenced ```python```), invisible
to concept-scan / solution-policy (which scan code cells).

All 10 Book-1 units + all 4 checkpoints already carry the norm.

## Metadata change — NONE

`input` is ALREADY in project-01's manifest `practices`, and the real-form is markdown-only anyway → no add
(design §5). No `.split()` (Book-2). The real driver uses only union concepts (`while-loop`/`sentinel-loop`,
`input`, `if`/`elif`/`else`, `break-statement`, function calls, `accumulator`, `comparison`, `logical-ops` (the
`or` in the scoreboard condition), `loop-counter`, `arithmetic`, `f-string`, `print`, `variable`,
`string-literal`) — [sol] #4 completeness; no `int()` (string compares).

## SHAPE — one integrated real-form (the interactive arcade)

A project is an INTEGRATED capstone build, not a set of independent exercises. Per **design §2 brief-row / v3**,
where a Milestone starter already reads `input()` that starter IS its real-program form — so M1–M4's real forms
already live in the brief's input()-reading scaffolds ([glm] nit A, [sol] BLOCKER-1 mapping). The one piece not
yet visible in the solutions is the **integrated M4 arcade** (menu loop + both games + scoreboard). So the real
form is placed under a **`## Milestone 4`** heading in solutions (mirroring the brief's `## Milestone 4`, per §2;
solutions milestone headings are unconstrained — `project_milestone_findings` reads brief.ipynb only), and M1–M3
map to their brief starters.

**§6 relationship (the [sol] BLOCKER-2 resolution).** The real form is NOT a §6c line-for-line twin of the
scripted `fixed-arcade-driver` — an interactive menu loop (sentinel `while choice != "q"`, menu prints, `input()`
at loop top, explicit `q`, invalid-choice branch, conditional scoreboard) has NO CI-runnable line-for-line twin
(`input()` can't run in CI). Instead:
- the real form is the **brief M4 scaffold** twin (§2 brief-row — the interactive starter IS the real form),
  completed and calling the reference param functions;
- the `fixed-arcade-driver` is the **§6a return-contract CI proof** (its asserts pin the scored branches:
  quick_quiz's three branches + lucky_guess's match; `while True` + scripted `choice` transitions +
  `lucky_points`/`quiz_points` temporaries are CI scripting, not real structure);
- the real form's interactive structure is validated by **§6b execution parity** (Phase B pipes real input
  through it and checks the scoreboard reproduces the fixed driver's score).

- The reference functions `lucky_guess(guess)` / `quick_quiz(answer_one, answer_two)` stay as the validated
  fixed-data twins (they take fixed values as params; the fixed driver + asserts pin all branches). The real
  driver READS the values (`input(...)`) and passes them in — the input()-reading form of the same logic. The
  games' own input-reading is shown inside this one real driver (it reads the guess / the two answers), so a
  single integrated real program covers M1–M4 without duplicating each game as a separate block.
- This mirrors the brief's `arcade-scoreboard-scaffold` (the completed real arcade), but calls the solutions'
  param functions so the reference logic is unchanged.

**No separate exemptions.** Every milestone is input-shaped and covered by the one real driver. `random.seed(4)`
+ asserts are CI scaffolding (u02 seeded-twin precedent); the real form ships UNSEEDED, and Phase-B validation
injects the seed to reproduce the fixed driver's outcome.

### Real-form specification (solutions markdown, after the `fixed-arcade-driver` cell + asserts)

Add a `## Milestone 4` markdown heading (mirroring the brief), then the real-form block. Caption ([fable] nit 1
+ [glm] nit B): "the interactive arcade — the menu, both games, and the scoreboard reading real input, using the
`lucky_guess`/`quick_quiz` defined above. Your arcade reads the guess/answers INSIDE the game functions; this
reference reads them in the driver and passes them in, so the very same functions work in the fixed driver above
and here." Code uses the project's `f""` house style so it matches the brief's M4 scaffold line-for-line:
```python
score = 0
rounds_played = 0
choice = f""

while choice != f"q":
    print(f"--- ARCADE NIGHT ---")
    print(f"1: Lucky Guess")
    print(f"2: Quick Quiz")
    print(f"q: Quit")
    choice = input(f"Choose a game: ")

    if choice == f"1":
        guess = input(f"Pick an integer from 1 through 5: ")
        score = score + lucky_guess(guess)
        rounds_played = rounds_played + 1
    elif choice == f"2":
        answer_one = input(f"Which is larger: 1) 8 or 2) 12? ")
        answer_two = input(f"Which is even: 1) 6 or 2) 7? ")
        score = score + quick_quiz(answer_one, answer_two)
        rounds_played = rounds_played + 1
    elif choice == f"q":
        print(f"The arcade is closing.")
        break
    else:
        print(f"Choose 1, 2, or q.")

    if choice == f"1" or choice == f"2":
        print(f"Score: {score} points after {rounds_played} rounds.")

print(f"Final score: {score} points in {rounds_played} rounds.")
```
This reads every input the arcade needs (menu choice each round, the guess, the two quiz answers) and calls the
unchanged reference functions. **§6c note ([fable] nit 2):** the real form mirrors the BRIEF's M4
`arcade-scoreboard-scaffold` structure (real `while choice != "q"` menu loop), NOT the `fixed-arcade-driver`
whose `while True:` + scripted `choice = f"2"` reassignments + `lucky_points`/`quiz_points` temporaries are CI
scripting scaffolding. **Placement ([sol] BLOCKER 1):** the block sits under a NEW `## Milestone 4` heading in
solutions (mirroring the brief's `## Milestone 4`, per design §2), added after the `check-*` assert cells. The
component headings (`## Lucky Guess`/`## Quick Quiz`/`## Fixed arcade driver`) stay; M1–M3's real forms are the
brief input()-reading starters (§2 brief-row). project-02 (solutions already `## Milestone N`) is unaffected.

## Data growth (§3) — N/A

Project-01 has no data lists; it is a functions + control-flow + random game. §3 does not apply.

## Phases

### Phase A — apply to project-01 solutions.ipynb (markdown only; NO brief.ipynb / manifest / metadata change)

Add a `## Milestone 4` markdown heading + a `**The real program**` markdown cell AFTER the `check-final-score`
assert cell (end of the notebook), containing the interactive arcade driver per spec (mirrors the brief M4
scaffold structure — menu/branch/scoreboard — reading `input()`, calling the reference functions defined above).
Placing it at the end keeps the reference functions + fixed driver + asserts executing first (the block is
markdown, so it never executes in CI regardless).
`brief.ipynb`, `manifest.yaml`, `teacher-notes.md` are NOT touched (byte-unchanged; teacher-notes audit expected
no-op — the ci-note already describes the split, verify no stale claim).

### Phase B — verification

- ci-local ALL GREEN (`TMPDIR=/dev/shm bash scripts/ci-local.sh`): registry+lint, notebook execution+hygiene,
  manifest/prereq/coverage, PDF build, pre-merge guard.
- Real-form validation: `ast.parse` the fenced block; then run it in a FRESH process ([fable] nit 3 — seed
  consumption: running it after the fixed driver in the same interpreter would consume the first `randint` draw
  and spuriously fail) with `random.seed(4)` injected + the reference functions defined, piped
  `1\n2\n2\n2\n1\nq\n` (choose 1, guess `2`, choose 2, answers `2`/`1`, quit) → reproduces the fixed driver's
  outcome: `lucky_guess("2")==5`, `quick_quiz("2","1")==4`, final line `Final score: 9 points in 2 rounds.`
  (parity with `check-final-score`'s `score==9`, `rounds_played==2`).
- Confirm 0 `input()` in any `solutions.ipynb` **code** cell (the real form is markdown; the reference functions
  and fixed driver remain input-free and CI-runnable).
- Scope invariant ([sol] #6 — bare `git diff --quiet` can pass after staging/commit): compare against the
  merge-base — `git diff --quiet $(git merge-base HEAD main)..HEAD -- <path>` — for brief.ipynb, manifest.yaml,
  teacher-notes.md, proving only solutions.ipynb changed across the branch.

## Out of scope

- No brief.ipynb edit, no new milestones, no difficulty change, no metadata change. teacher-notes.md audit-only.
  Only `solutions.ipynb` is modified.
- **Verification exemption:** project-content plan; Phase B is the named verification phase.
- project-02 (grand-adventure) is a separate plan — the final rollout slice.

## Plan Review

### Round 1 (2026-09-20) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.

#### [self] (2026-09-20)
**APPROVE.** One integrated real-form (the interactive arcade) is the faithful representation of a project — an
integrated capstone build, not independent exercises; the driver reads every input (menu loop, guess, two quiz
answers) and calls the UNCHANGED reference param functions, covering M1–M4. Seeded parity VALIDATED locally: with
`random.seed(4)` secret=2, so piped `1/2/2/2/1/q` → `lucky_guess("2")==5`, `quick_quiz("2","1")==4`, final
`Final score: 9 points in 2 rounds.` (matches the fixed driver's `score==9`, `rounds_played==2`); both fixed and
real forms call `lucky_guess` exactly once → one `randint`, so the seed reproduces. Metadata NONE (`input`
already in manifest + markdown-only). Closure clean (while/sentinel-loop, input, if/elif/else, break, calls,
accumulator, f-string; no `.split()`; no int() — string compares). §3 N/A. Phase B named (ci-local + seeded
piped-parity + 0-input-in-code-cells + scope `git diff`).

#### [fable] (2026-09-20)
**APPROVE WITH NITS.** One-integrated-form shape HOLDS (brief presents M1–M4 as one artifact; M4 subsumes the
menu + both games; per-game blocks would just copy the brief; §2 brief-row says a Milestone starter that already
reads input() IS its real form → the driver is the only piece not yet visible in solutions). Ran the spec block
in a fresh process with seed(4) + reference fns, piped `1/2/2/2/1/q` → `Score: 5…`/`Score: 9…`/`The arcade is
closing.`/`Final score: 9 points in 2 rounds.` — exact parity. Closure clean (union-only, no int()/`.split()`).
Nits (all FOLDED into the plan):
- nit 1: caption should explain input-in-driver vs input-in-function → folded into the caption.
- nit 2 (§6c): the real form mirrors the BRIEF's M4 scaffold, not the `while True` fixed driver (scripting is CI
  artifact) → folded into the SHAPE §6c note.
- nit 3: Phase-B validation must run in a FRESH process (seed consumption) → folded into Phase B.
- nit 4: note the `## Fixed arcade driver` placement in lieu of `## Milestone N` (project-02 has milestone
  headings; project-01 doesn't) → folded into the SHAPE placement note.
Plus adopted the brief's `f""` house style in the real-form code for visual match (optional style note).

#### [glm] (2026-09-20)
**APPROVE WITH NITS** (no blockers). Verified parity empirically (fresh seed(4)→secret 2→lucky_guess("2")=5,
quick_quiz("2","1")=4, piped 1/2/2/2/1/q → Final score: 9 in 2 rounds; one randint each). ONE integrated
real-form right — per design §2 v3, all four brief starters already read input() so they ARE the per-milestone
real forms; per-game solutions blocks would duplicate the starters + create unvalidated third copies with a
divergent signature (`def lucky_guess():` vs asserted `lucky_guess(guess)`) = drift risk. §6c holds at the driver
level (real mirrors brief M4 with param calls; fixed driver's else-as-quit is unreachable scripting). Closure
clean; metadata NONE; Phase B adequate. Nits: (A) cite the §2 v3 "starter-is-the-real-form" clause explicitly;
(B) caption should note the block uses the `lucky_guess`/`quick_quiz` defined above (non-self-contained). → both FOLDED.

#### [sol] (2026-09-20) — reviewed stale draft 1375a3d (pre-folds)
**REJECT** (2 BLOCKERs). Resolution:
- `[OPEN]` BLOCKER 1 — placement: design §2 brief-row says the real form goes under the mirrored `## Milestone N`,
  but the draft placed it under `## Fixed arcade driver`. RESOLVED: add a `## Milestone 4` heading in solutions
  for the real-form block; note M1–M3 real forms are the brief input()-reading starters (§2 brief-row). Safe —
  `project_milestone_findings` reads brief.ipynb only (notebooks.py:737); solutions headings are unconstrained.
- `[OPEN]` BLOCKER 2 — §6c twin: the real driver (sentinel loop, menu prints, invalid branch) is NOT the fixed
  driver (`while True`, scripted) with values→reads, and the asserts pin the 3 quiz branches but not lucky_guess's
  miss branch / the menu's invalid branch. RESOLVED by the correct design reading (the "approved exception" [sol]
  asked for): a project's integrated real form is the **brief M4 scaffold** twin per §2 brief-row (the interactive
  starter IS the real form), NOT a §6c line-for-line twin of the fixed driver — an interactive menu loop has no
  CI-runnable line-for-line twin (input() can't run in CI). Its structure is validated by **§6b execution parity**
  (piped run reproduces the scoreboard); the fixed driver is the §6a return-contract CI proof (asserts pin the
  scored branches). Plan SHAPE/Phase-B reworded to state this.
- [sol] also: concept summary incomplete (add `logical-ops`/`loop-counter`/`arithmetic`) → FOLDED; Phase-B scope
  command should compare against merge-base, not bare `git diff --quiet` → FOLDED.
Re-verifying [sol] on the reworded plan (no 3-of-4 shortcut on a REJECT).

### Round 1 — FINAL outcome: **FULL 4-way plan-review consensus.** [self]/[glm]/[fable]/[sol] APPROVE (all nits
folded; [sol] REJECT→APPROVE after adding the `## Milestone 4` heading + the §2-brief-row/§6b reframing of the
interactive twin + concept-list/scope-command folds). [sol] re-verify reproduced seed(4)→secret 2→score 9 in 2
rounds, one randint each. Gate CLOSED → implementation.

## Content Review

### Round 1 (2026-09-20) — on implementation commit eeae8c3. [self] inline; [sol]/[glm]/[fable] dispatched.

#### [self] (2026-09-20)
**APPROVE.** One markdown cell (`arcade-real-program-m4`) appended: `## Milestone 4` + `**The real program**` +
the interactive-arcade fenced block, calling the unchanged reference functions. Parity VALIDATED in a fresh
process (seed(4)→secret 2, piped `1/2/2/2/1/q` → `Final score: 9 points in 2 rounds.`, one randint). Hygiene: 0
`input()` in code cells (real form is markdown); reference fns + fixed driver + asserts unchanged and execute
first; `## Milestone 4` in solutions harmless (project_milestone_findings reads brief.ipynb only). Scope
(merge-base): only solutions.ipynb changed; brief/manifest/teacher-notes byte-unchanged. Closure clean (no
`.split()`/int()); f"" house style matches brief M4. Caption accurate (uses fns above; input-in-driver vs
in-function; M1–M3 real forms are brief starters). ci-local ALL GREEN.

#### [fable] (2026-09-20)
**APPROVE WITH NITS — no `[OPEN]`.** Diff vs main is exactly solutions.ipynb (+1 markdown cell) + the plan;
brief/manifest/teacher-notes untouched. Simulated the block against the UNCHANGED reference functions with
seed(4) + stubbed input (incl. an invalid choice + quit): menu re-shows, both games play, invalid prints
"Choose 1, 2, or q." without bumping rounds, `q` closes; piped `1/2/2/2/1/q`→`Final score: 9 points in 2
rounds.` (§6b parity, one randint per lucky_guess). `## Milestone 4` can't trip project_milestone_findings
(brief-only, notebooks.py:730). Caption covers all three points (uses fns above; input-in-driver vs in-function;
M1–M3 = brief starters). Reference functions unchanged. Nits (non-blocking):
- nit 1: caption is one dense 50-word sentence → split into two for a Year-One reader. → FOLD.
- nit 2: `arcade-ci-note` is now slightly stale (doesn't mention the interactive form now shown under
  `## Milestone 4`) → add one clause pointing there. → FOLD (still solutions.ipynb).
- nit 3: caption hyphen `1-3` → en-dash `1–3` (house style). → FOLD.
- nit 4: pre-existing `choice = f"1"`/`f""` empty-f-string quirk — out of scope, do NOT touch.

#### [sol] (2026-09-20)
**APPROVE — 0 `[OPEN]`, 0 `[WONTFIX]`.** Parity: fresh subprocess, seed(4), piped `1/2/2/2/1/q` → exit 0, final
line exactly `Final score: 9 points in 2 rounds.`, exactly one randint (runtime + static). Fidelity: all 4 input
prompts match brief M1–M3; menu read inside the sentinel loop; calls unchanged `lucky_guess`/`quick_quiz` once
each. Closure: AST found only union constructs, no `.split()`/int(), all 19 literals `f""`. Metadata NONE
correct. Hygiene: 0 input() in code cells; every pre-existing cell unchanged; all solution cells + 8 asserts
exit 0; project_solutions/project_milestone both `[]` (milestone check reads brief only). Scope: vs merge-base
5bcae13, only solutions.ipynb + the plan changed; brief/manifest/teacher-notes SHA-256 byte-identical. Caption
accurate.

#### [glm] (2026-09-20)
**APPROVE WITH NITS — 0 `[OPEN]`.** Ran `ci-local` ALL GREEN (all 6 steps incl. exec-solutions + guard). Parity
PASS in a fresh process (secret=2, Jackpot 5 + Two-correct 4, final `Final score: 9 points in 2 rounds.`, one
randint). Fidelity: 4 prompts byte-match brief, mirrors arcade-scoreboard-scaffold, calls unchanged param fns,
tokenize-verified `f""`. Closure clean; metadata NONE; hygiene PASS (also exercised CI-invisible branches: invalid
→ "Choose 1, 2, or q." no round bump; quit-only → 0/0). Scope: merge-base diff = solutions.ipynb (+1 cell) +
plan. Same 3 fold-level nits as [fable] (caption density, ci-note pointer, hyphen).

### Content-review outcome: **FULL 4-way consensus.** [self]/[sol] APPROVE · [fable]/[glm] APPROVE-WITH-NITS
(0 `[OPEN]`). Shared 3 nits folded post-consensus (caption split into two sentences + en-dash `1–3`; ci-note now
points to the `## Milestone 4` interactive form); ci-local re-verified GREEN. Gate CLOSED → PR.

## Post-Execution Report

**Status: COMPLETE.** Project 01 (arcade-night) received the design-003 real-input treatment. First of the two
Book-1 projects.

**What shipped** (branch `feature/plan-065-project01-real-input`, `solutions.ipynb` only, +1 markdown cell + a
one-clause ci-note update):
- ONE integrated `**The real program**` block under a new `## Milestone 4` heading (mirrors the brief per §2
  brief-row) — the interactive arcade: sentinel menu loop reads the choice, game 1 reads the guess, game 2 reads
  two answers, scoreboard accumulates; calls the UNCHANGED reference param functions `lucky_guess(guess)` /
  `quick_quiz(answer_one, answer_two)`. M1–M3 real forms are the brief's input()-reading starters.
- **No metadata change** (`input` already in the manifest; markdown-only). §3 N/A (no data lists).
  `brief.ipynb`/`manifest.yaml`/`teacher-notes.md` byte-unchanged.

**Design reading (the [sol] plan-review resolution):** a project's integrated real form is the **brief-milestone
scaffold twin** (§2 brief-row — the interactive starter IS the real form), NOT a §6c line-for-line twin of the
scripted fixed driver (an interactive menu loop has no CI-runnable line-for-line twin). The `fixed-arcade-driver`
is the §6a return-contract CI proof (asserts pin the scored branches); §6b execution parity validates the
interactive structure. This generalizes to project-02.

**Gate history**: plan-review FULL 4-way consensus ([sol] REJECT→APPROVE after adding the `## Milestone 4`
heading + the §2-brief-row/§6b reframing) → implementation (eeae8c3) → content-review FULL 4-way consensus
(0 `[OPEN]`) → 3 cosmetic folds.

**Verification**: `scripts/ci-local.sh` ALL GREEN; seeded parity (fresh process, seed(4)) → `Final score: 9
points in 2 rounds.`; 0 `input()` in code cells; `## Milestone 4` in solutions harmless (milestone check reads
brief); scope invariant (merge-base) clean; `pre-merge-guard --pr`.

**Follow-up:** the design-§4 dict-idiom fix flagged in plan 064 remains open (relevant if project-02 reads dicts;
use explicit-variable reads). project-02 (grand-adventure, has `adventure_save.txt`) is the final rollout slice —
apply the files-are-real precedent for file reads and this project's integrated-real-form / §2-brief-row reading.
