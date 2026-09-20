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
`input`, `if`/`elif`/`else`, `break-statement`, function calls, `accumulator`, `comparison`, `f-string`,
`print`, `variable`, `string-literal`).

## SHAPE — one integrated real-form (the interactive arcade)

A project is an INTEGRATED capstone build, not a set of independent exercises. Its one input-shaped "program"
is the whole arcade: the menu loop (M1) reads choices; game 1 (M2) reads a guess; game 2 (M3) reads two answers;
the scoreboard (M4) accumulates. The scripted **Fixed arcade driver** (`fixed-arcade-driver`, scripts
`1`→`2`→`q`) is the executable fixed-data twin; its **real form** is the interactive driver that reads the menu
choice and each game's input, calling the UNCHANGED reference param functions.

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

### Real-form specification (solutions markdown, after the `fixed-arcade-driver` cell)

`**The real program**` — caption ([fable] nit 1, explaining input placement): "the interactive arcade — the
menu, both games, and the scoreboard reading real input. Your arcade reads the guess/answers INSIDE
`lucky_guess()`/`quick_quiz()`; this reference reads them in the driver and passes them in, so the very same
functions work in the fixed driver above and here." Code uses the project's `f""` house style so it matches the
brief's M4 scaffold line-for-line:
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
scripting scaffolding. **Placement ([fable] nit 4):** project-01's solutions have no `## Milestone N` headings
(they use `## Lucky Guess` / `## Quick Quiz` / `## Fixed arcade driver`), so the block goes under
`## Fixed arcade driver` as the M4-integrating twin — this is a project-01-specific mapping and does NOT set a
"no Milestone heading" precedent for project-02 (whose solutions already use `## Milestone N`).

## Data growth (§3) — N/A

Project-01 has no data lists; it is a functions + control-flow + random game. §3 does not apply.

## Phases

### Phase A — apply to project-01 solutions.ipynb (markdown only; NO brief.ipynb / manifest / metadata change)

Add one `**The real program**` markdown cell immediately AFTER the `fixed-arcade-driver` code cell (before the
`check-*` assert cells), containing the interactive arcade driver per spec (§6c: same menu/branch/scoreboard
structure as the fixed driver + the brief scaffold, with the scripted choices replaced by `input()` reads).
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
- Scope invariant: `git diff --quiet` for brief.ipynb, manifest.yaml, teacher-notes.md.

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

#### [sol] (pending)
#### [glm] (pending — opencode)

## Content Review
_(pending)_

## Post-Execution Report
_(pending)_
