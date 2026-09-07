# Plan 012 — Unit 09 Save Point Implementation Plan

**Goal:** Ship `unit-09-save-point` — the files unit — where students make a program REMEMBER
between runs: write a save file with `with open(..., "w")`, read it back with `with open(...)`,
and rebuild game state (a list of high scores, a few settings) from what was saved.

**Architecture:** Standard unit pipeline (plan 004), plus ONE small infra step. Two things land UP
FRONT in Phase A: (1) a `.gitignore` entry for the runtime scratch files the notebooks create
(see FILE-I/O below), and (2) the substrate map amendment (validated with the AST concept-scanner).
The unit's helper functions take arguments and return values (`parameters`, `return-value` →
requires); the save/load/display beats use `builtin-functions` (`len`), `dict-literal`+`dict-access`
(a settings dict written to a file), `if-statement`+`in-operator` (search the save text),
`list-literal`+`list-append`+`list-loop` (the score list), `print`/`variable`/`f-string`/
`string-literal`, `string-concat`+`type-conversion` (`str(score) + "\n"` and `int(line)`),
`int-type`, and `error-messages` (a FileNotFoundError beat) → practices. All taught by units 01–08;
verified green in scratch.

**Spec:** `book1/curriculum/coverage-map.yaml` (binding, amended); plan 004 unit conventions;
D-001; design-000 §4 (notebook execution).

## Global Constraints

- All plan-004 unit Global Constraints apply (map-equal manifest, hook-first, exercise ≥6 core +
  ≥2 stretch, solution floors + per-line bans, non-vacuous asserts incl. no tautologies, five
  teacher-notes headings, per-lesson allocation, commit trailers).
- **FILE-I/O CI-SAFETY (binding — this unit's central risk):** `ci-local` executes BOTH
  `solutions.ipynb` AND `lesson.ipynb` (minus `no-exec` cells) with the notebook's cwd set to the
  UNIT DIRECTORY (design-000 §4 / `execute_notebooks` `resources.metadata.path`). Therefore:
  1. Every file the notebooks open for writing uses a RELATIVE filename that lands in the unit dir,
     and each is **WRITE-THEN-READ within the same notebook** — the notebook CREATES the file it
     later reads (no committed data file to ship, no read of a file that might be absent).
  2. Writes use mode `"w"` (overwrite) with DETERMINISTIC content — NEVER append mode `"a"` (which
     would grow the file every CI run). Re-running is idempotent.
  3. The scratch filenames are gitignored in Phase A so the runtime-created files never show up as
     git noise or get committed. Use ONLY these two scratch names so the ignore stays tight:
     `savegame.txt` and `settings.txt` (both in the unit dir).
  4. The FileNotFoundError teaching beat (`open("missing.txt")`) lives in a `no-exec`-tagged cell
     (like the unit-07 IndexError / unit-08 KeyError beats) so CI never runs it. Its traceback is
     shown in a following markdown cell.
  5. `os.remove`/`os.path`/`tempfile`/`pathlib` are NOT taught — NO cleanup code, NO imports; the
     gitignore handles the leftover scratch files.
- Coverage-map amendment (EXACTLY this, pre-audited + scanner-derived green):
  - append to `unit-09-save-point.requires` — `parameters, return-value`.
  - append to `unit-09-save-point.practices` — `builtin-functions, dict-literal, if-statement,
    list-literal, print, variable, string-concat, string-literal, type-conversion, int-type,
    error-messages`.
  - All introduced by units 01–08; `practices ∩ introduces` empty (introduces = file-read/
    file-write/with-statement). Apply surgically (no YAML round-trip). Manifest carries the lists.
- **Pre-gate closure self-check (standing):** run the AST concept-scanner scoped to unit-09 and
  confirm ZERO used-but-unlisted concepts AND zero untaught methods before the `[sol]` content gate.
- **File API (binding):** files are opened ONLY with `with open(name, "w") as f:` (write) and
  `with open(name) as f:` (read); write with `f.write(text)`, read with `f.read()` or `for line in
  f:`. The `with`-statement is mandatory (no bare `open(...)` without `with`; no manual `.close()`).
  NO `.readlines`/`.writelines`/`.seek`/`.tell`; NO append mode.
- **No `.split()` (binding, closure trap):** the taught `string-methods` subset is upper/lower/
  strip/replace. Save files store ONE value per line; reading uses `for line in f:` + `.strip()`
  (drop the newline) + `int(...)` for numbers — NEVER `line.split(...)`. NO list slicing
  (`lines[1:]`), NO comparison operators (`==`/`<`/`>`) in student code — searching the save text
  uses `in` membership.
- **No dicts-beyond-taught / no OOP** (unit 10). Dicts use only `{...}` literals + `[key]` access
  (`.get`/`.items` optional but keep it simple). No classes. No nested loops.
- Process (standing): no commits while a `[sol]` review is in flight; codex prompts name the
  in-process execution fallback and avoid bare CLI-flag-like tokens.

## Out of scope

Content plan → Phase C is the mandatory named verification phase. Out of scope: unit 10 / checkpoint
04 / project 02 (later plans); the latent practice-completeness hygiene PR + scanner promotion
(tracked separately); PDF handouts; any map edit beyond the Phase-A substrate amendment; OOP;
`.split()`; append-mode files; `os`/`tempfile`/`pathlib`.

## Phases

Dispatch per AGENTS.md: lesson/exercise statements via codex; solutions via a SEPARATE blind codex
session; teacher notes inline; map amendment + gitignore + manifest inline.

### Phase A — gitignore + map amendment + manifest (inline)

1. Append to `.gitignore` (surgical): a comment + `book1/units/unit-09-save-point/savegame.txt`
   and `book1/units/unit-09-save-point/settings.txt` (the runtime scratch files).
2. Amend `coverage-map.yaml` per Global Constraints (surgical, requires + practices).
3. `book1/units/unit-09-save-point/manifest.yaml`, map-equal to the amended entry; lands with the
   directory in Phase B.
- **Acceptance (Phase A):** the gitignore + map amendment ALONE are green (`uv run pytest -q` +
  `ci-local`) before any unit directory exists.

### Phase B — unit-09-save-point content (2 lessons)

Blueprint (introduces file-read, file-write, with-statement; requires list-append, string-methods,
def-function, for-loop, + amended parameters/return-value; practices list-loop, dict-access,
f-string, in-operator, + amended builtin-functions/dict-literal/if-statement/list-literal/print/
variable/string-concat/string-literal/type-conversion/int-type/error-messages):
- Hook: SAVE POINT — a game that forgets everything when you close it is no fun. Teach the program
  to WRITE the player's progress to a file and LOAD it back next time.
- Lesson 1 (file-write, with-statement) — open on the hook: `with open("savegame.txt", "w") as f:`
  then `f.write("Ada\n")` and, for a score list, `for score in scores: f.write(str(score) + "\n")`
  (list-loop + type-conversion + string-concat). Explain `with` closes the file automatically, and
  `"\n"` is the newline that puts each value on its own line. A settings dict written to a second
  file: `settings = {"volume": 8, "difficulty": "easy"}`; `f.write(str(settings["volume"]) + "\n")`
  (dict-literal + dict-access). Show the file was created by reading it straight back with
  `f.read()`.
- Lesson 2 (file-read) — open on the thread ("yesterday we saved; today we load"): read the whole
  file `with open("savegame.txt") as f: content = f.read()`; then rebuild a list line-by-line —
  `loaded = []` / `with open("savegame.txt") as f: for line in f: loaded.append(int(line.strip()))`
  (list-append + type-conversion + string-methods) — noting `.strip()` drops the trailing newline.
  A `load_scores(filename)` helper returns the list (def-function/parameters/return-value);
  `print(f"Loaded {len(loaded)} scores")` (builtin-functions + f-string). Search the save text with
  membership: `if "Ada" in content: print("Welcome back, Ada!")` (if-statement + in-operator). The
  deliberate bug in a `no-exec` cell: `open("missing.txt")` → FileNotFoundError, read the traceback
  together (error-messages); the fix is to save before you load.
- Exercises ≥6 core + ≥2 stretch, each HOMING a concept: save-a-name (write one line), save-a-score-
  list (write loop + str + "\n"), load-the-file (read + print), load-scores-into-a-list (read loop +
  int + strip + append), count-the-saved-scores (builtin-functions len), save-settings (dict-access
  write), search-the-save (in-operator membership), save-then-load (a `save`+`load` round-trip via
  helpers); stretch: highest-saved-score (load then `max`), append-a-new-high (load list, `.append`,
  re-SAVE with `"w"` — NOT append mode). input() appears only in an exercise PROMPT; solutions are
  parameterized with fixed filenames (`savegame.txt`).
- Solutions: execute headless (they WRITE-THEN-READ `savegame.txt`/`settings.txt` in the unit dir,
  deterministic `"w"` mode, gitignored), input-free, non-vacuous asserts — a round-trip assert
  (`load_scores(save_scores([100, 200], "savegame.txt")) == [100, 200]`), a length assert, a
  membership assert on read content, a settings read-back assert. NO append mode, NO os/tempfile.
- Teacher notes: five headings, per-lesson allocation (L1 write/with, L2 read/parse/helpers), 60-min
  cuts, differentiation; common mistakes (forgetting `"\n"` so everything runs together; forgetting
  `.strip()` before `int()`; using append mode and doubling the file; reading a file that was never
  saved → FileNotFoundError; forgetting `with` and leaving the file open).

### Phase C — Verification (NAMED, mandatory)

Mechanical: full pytest green; `ci-local.sh` ALL GREEN (exec-lessons + exec-solutions BOTH run the
file I/O — confirm no stray committed files: the scratch files are gitignored); AST concept-scanner
scoped to unit-09 clean; solutions execute with non-vacuous round-trip asserts; manifest map-equal.
Reviewer duties: blind-solve exercises; cumulative closure (only ≤unit-09 — NO `.split()`, NO
append mode, NO `os`/`tempfile`/`pathlib`/`.readlines`, NO list slicing, NO comparison operators in
student code, NO classes/nested-loops — check explicitly); every file open uses `with`; writes are
deterministic `"w"` and every written file is read back in the same notebook (no missing-file read
except the `no-exec` FileNotFoundError beat); the scratch files are gitignored; solutions
non-vacuous/complete; grading usable; timing; hook-first; age-appropriate.

**Acceptance criteria:** the unit directory complete; `uv run pytest -q` green; ci-local ALL GREEN;
concept-scanner clean; the two scratch files gitignored (no git noise after a CI run); content gate
4-way consensus.

---

## Plan Review

### Review 1 — [self] (2026-09-07)
APPROVE. Substrate scanner-DERIVED (not guessed) from the planned save/load code + validated green.
The unit's central risk — file I/O in CI-executed notebooks (BOTH lessons and solutions run, cwd =
unit dir) — is handled by the binding FILE-I/O CI-SAFETY rules: write-then-read self-contained
scratch files, deterministic `"w"` mode (never append), gitignored scratch, FileNotFoundError in a
`no-exec` cell, and no untaught cleanup (`os`/`tempfile`). Closure honors the no-`.split()` trap
(one-value-per-line files, `for line in f` + `.strip()` + `int()`), membership-not-comparison, and
no list slicing. `dict-access` (a pre-existing map practice) is homed by a settings-dict write beat
(adding `dict-literal`). `practices ∩ introduces` empty.
