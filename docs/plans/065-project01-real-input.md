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

`**The real program**` (caption: the interactive arcade — reads the menu and each game's input):
```python
score = 0
rounds_played = 0
choice = ""

while choice != "q":
    print("--- ARCADE NIGHT ---")
    print("1: Lucky Guess")
    print("2: Quick Quiz")
    print("q: Quit")
    choice = input("Choose a game: ")

    if choice == "1":
        guess = input("Pick an integer from 1 through 5: ")
        score = score + lucky_guess(guess)
        rounds_played = rounds_played + 1
    elif choice == "2":
        answer_one = input("Which is larger: 1) 8 or 2) 12? ")
        answer_two = input("Which is even: 1) 6 or 2) 7? ")
        score = score + quick_quiz(answer_one, answer_two)
        rounds_played = rounds_played + 1
    elif choice == "q":
        print("The arcade is closing.")
        break
    else:
        print("Choose 1, 2, or q.")

    if choice == "1" or choice == "2":
        print(f"Score: {score} points after {rounds_played} rounds.")

print(f"Final score: {score} points in {rounds_played} rounds.")
```
This reads every input the arcade needs (menu choice each round, the guess, the two quiz answers) and calls the
unchanged reference functions. It is the input()-reading twin of the scripted `fixed-arcade-driver`.

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
- Real-form validation: `ast.parse` the fenced block; then run it with `random.seed(4)` injected + the reference
  functions defined, piped `1\n2\n2\n2\n1\nq\n` (choose 1, guess `2`, choose 2, answers `2`/`1`, quit) →
  reproduces the fixed driver's outcome: `lucky_guess("2")==5`, `quick_quiz("2","1")==4`, final line
  `Final score: 9 points in 2 rounds.` (parity with `check-final-score`'s `score==9`, `rounds_played==2`).
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

#### [sol] (pending)
#### [glm] (pending — opencode)
#### [fable] (pending)

## Content Review
_(pending)_

## Post-Execution Report
_(pending)_
