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
  4. The FileNotFoundError teaching beat (`with open("missing.txt") as f: f.read()`) lives in a `no-exec`-tagged cell
     (like the unit-07 IndexError / unit-08 KeyError beats) so CI never runs it. Its traceback is
     shown in a following markdown cell.
  5. `os.remove`/`os.path`/`tempfile`/`pathlib` are NOT taught — NO cleanup code, NO imports; the
     gitignore handles the leftover scratch files.
- Coverage-map amendment (EXACTLY this, pre-audited + scanner-derived green):
  - append to `unit-09-save-point.requires` — `parameters, return-value`.
  - append to `unit-09-save-point.practices` — `builtin-functions, dict-literal, if-statement,
    list-literal, print, variable, string-concat, string-literal, type-conversion, int-type,
    error-messages, input` (`input` homed by the "save-my-score" exercise PROMPT only — prose, not
    an executable cell; solution parameterized with a fixed score, matching units 07/08; sol
    plan-review caught it used-but-unlisted).
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
variable/string-concat/string-literal/type-conversion/int-type/error-messages/input):
- Hook: SAVE POINT — a game that forgets everything when you close it is no fun. Teach the program
  to WRITE the player's progress to a file and LOAD it back next time.
- **PAYLOAD SPLIT (binding, fable plan-review — prevents an int-parse crash):** `savegame.txt`
  holds INTEGER SCORE lines ONLY (so every line int-parses clean). `settings.txt` holds TEXT lines
  (player name, volume, difficulty) and is read back as TEXT via membership ONLY — its lines are
  NEVER `int(...)`-parsed. The two files never mix payloads; each read/membership beat names which
  file it targets.
- Lesson 1 (file-write, with-statement) — open on the hook: save a SCORE LIST to `savegame.txt` —
  `scores = [1200, 850, 990]`; `with open("savegame.txt", "w") as f: for score in scores:
  f.write(str(score) + "\n")` (list-loop + type-conversion + string-concat). Explain `with` closes
  the file automatically and `"\n"` puts each value on its own line. Then save the player + settings
  as TEXT to `settings.txt` — `settings = {"volume": 8, "difficulty": "easy"}`; `with
  open("settings.txt", "w") as f: f.write("Ada\n"); f.write(str(settings["volume"]) + "\n");
  f.write(settings["difficulty"] + "\n")` (dict-literal + dict-access). Show each file was created by
  reading it straight back with `f.read()`. **Give `"\n"` its own teaching beat (glm plan-review):**
  it is new syntax (no concept id — absorbed under `string-literal`) — explain that `"\n"` is the
  invisible "new line" character that ends a line, so each `f.write(... + "\n")` starts the next
  value on a fresh line; without it everything runs together.
- Lesson 2 (file-read) — open on the thread ("yesterday we saved; today we load"): read the whole
  scores file `with open("savegame.txt") as f: content = f.read()`; then rebuild the score list
  line-by-line — `loaded = []` / `with open("savegame.txt") as f: for line in f:
  loaded.append(int(line.strip()))` (list-append + type-conversion + string-methods) — noting
  `.strip()` drops the trailing newline and EVERY line of `savegame.txt` is an integer.
  A `load_scores(filename)` helper returns the list (def-function/parameters/return-value);
  `print(f"Loaded {len(loaded)} scores")` (builtin-functions + f-string). Search the SETTINGS text
  with membership: `with open("settings.txt") as f: info = f.read()`; `if "Ada" in info:
  print("Welcome back, Ada!")` (if-statement + in-operator) — `settings.txt` is read as TEXT, never
  int-parsed. The deliberate bug in a `no-exec` cell: `with open("missing.txt") as f: f.read()` →
  FileNotFoundError, read the traceback together (error-messages); the fix is to save before you
  load.
- Exercises ≥6 core + ≥2 stretch, each HOMING a concept (each names its target file): save-a-score-
  list (write loop + str + "\n" → `savegame.txt`), load-the-file (read + print `savegame.txt`),
  load-scores-into-a-list (read loop + int + strip + append from `savegame.txt`), count-the-saved-
  scores (builtin-functions `len`), save-settings (dict-access write name+volume+difficulty as TEXT
  → `settings.txt`), search-the-settings (in-operator membership on `settings.txt` text — e.g.
  `if "Ada" in info`), save-then-load (a `save`+`load` integer round-trip via helpers on
  `savegame.txt`), save-my-score (the PROMPT asks for a SCORE via `input("Your score? ")` — the
  student is told NOT to call it; the reference solution uses a FIXED sample score, `int()`s it,
  appends to the scores list, and re-SAVEs to `savegame.txt` — a SCORE→int path so the int-only
  split HOLDS; this is the NAMED home for `input`, glm/sol plan-review); stretch: highest-saved-score
  (load `savegame.txt` then `max`), add-a-new-high (load list, `.append`, re-SAVE with `"w"` — NOT
  append mode; the word "add" not "append" so it can't steer a beginner toward mode `"a"` — glm
  plan-review). input() appears only in the save-my-score PROMPT; solutions are parameterized with
  fixed values and the fixed filenames.
- Solutions: execute headless (they WRITE-THEN-READ `savegame.txt`/`settings.txt` in the unit dir,
  deterministic `"w"` mode, gitignored), input-free, non-vacuous asserts — an integer round-trip
  assert (`load_scores(save_scores([100, 200], "savegame.txt")) == [100, 200]`), a length assert
  (`len(loaded) == 3`), a TEXT membership assert on the settings read-back
  (`"Ada" in info` after reading `settings.txt`), and a settings value membership (`"easy" in info`).
  `settings.txt` lines are NEVER int-parsed. NO append mode, NO os/tempfile.
- Teacher notes: five headings, per-lesson allocation (L1 write/with, L2 read/parse/helpers), 60-min
  cuts, differentiation; common mistakes (forgetting `"\n"` so everything runs together; forgetting
  `.strip()` before `int()`; using append mode and doubling the file; reading a file that was never
  saved → FileNotFoundError; forgetting `with` and leaving the file open).

### Phase C — Verification (NAMED, mandatory)

Mechanical: full pytest green; **CLEAN-SLATE RUN (glm plan-review):** `rm -f
book1/units/unit-09-save-point/savegame.txt book1/units/unit-09-save-point/settings.txt` immediately
BEFORE the final `ci-local.sh` run, so the notebooks must CREATE the files themselves — green then
genuinely evidences create-before-read (ci-local otherwise can't falsify a read-before-write since
the gitignored files persist across runs and exec-solutions precedes exec-lessons). `ci-local.sh`
ALL GREEN (exec-lessons + exec-solutions BOTH run the file I/O; the scratch files are gitignored, so
`git status` stays clean after the run). The AST concept-scanner scoped to unit-09 is an ADVISORY
pre-gate aid (a scratch prototype, not wired into `tools/` — see Out of scope), not a mechanical CI
gate; closure is enforced by reviewer manual checks + the 4-way blind-solve. Solutions execute with
non-vacuous round-trip asserts; manifest map-equal.
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

### Review 2 — [fable] (2026-09-07)
REJECT → all findings RESOLVED (revised in place before commit):
1. `[FIXED]` (BLOCKING, file-I/O) `savegame.txt` mixed a NAME line with SCORE lines, so Lesson 2's
   `int(line.strip())` over every line → `int("Ada")` ValueError → exec-lessons FAILS; and the
   welcome beat needed "Ada" present — mutually exclusive on one file. **PAYLOAD SPLIT**:
   `savegame.txt` = integer scores ONLY (int-parse clean); `settings.txt` = TEXT (name, volume,
   difficulty) read back via membership ONLY, never int-parsed. Empirically re-validated: the
   corrected design executes clean via NotebookClient (cwd=unit dir), all round-trip + membership
   asserts pass, idempotent `"w"` mode.
2. `[FIXED]` (Nit) FileNotFoundError beat used a bare `open()` — now `with open("missing.txt") as f:`
   (models the with-only File API rule; still a no-exec cell).
3. `[FIXED]` (Watch) `settings.txt` read-back is TEXT/membership only — never `int(...)`-parsed
   (folded into the payload split).
- fable affirmed everything else sound: completeness (no used-but-unlisted), amendment correctness
  (all added concepts taught ≤unit-08, `practices ∩ introduces` empty), no over-listing (dict-access
  homed by `settings["volume"]`), closure safety (no .split/list-slice/comparison/os/tempfile/append/
  classes/nested-loops), no cross-notebook dependency / no git noise, hook-first pedagogy.

### Review 3 — [glm] (2026-09-07)
APPROVE WITH NITS (glm reviewed the working-tree file, which already carried the payload-split fix —
so it confirmed the corrected design: closure PASS, over-listing PASS, pedagogy PASS). Nits, all
fixed:
- `[FIXED]` glm-1 (highest): ci-local can't falsify read-before-write (gitignored scratch persists;
  exec-solutions precedes exec-lessons) — added a CLEAN-SLATE `rm -f` of the two scratch files before
  the final Phase-C ci-local so green evidences create-before-read.
- `[FIXED]` glm-2: the concept-scanner is a scratch ADVISORY prototype, not a mechanical CI gate —
  Phase C reworded (closure enforced by reviewers + blind-solve).
- `[FIXED]` glm-3: settings.txt read-back is membership-only (no int reconstruction of the volume
  line) — the payload split already guarantees `settings.txt` is never int-parsed; reinforced.
- `[FIXED]` glm-4: renamed the "append-a-new-high" stretch to "add-a-new-high" (the word "append"
  must not steer a beginner toward mode `"a"`).
- `[FIXED]` glm-5: `"\n"` is new syntax with no concept id — added an explicit Lesson-1 teaching beat.

### Review 4 — [sol] (2026-09-07)
REJECT → all findings RESOLVED. sol confirmed the file-I/O design is sound (no read-before-write,
no parse bug, clean-slate run good, gitignore paths correct) and closure otherwise maps cleanly;
scratch prereq-check + coverage-check PASS.
- `[FIXED]` (BLOCKER) `input` used-but-unlisted — the exercise prompt uses `input()`; added `input`
  to the practices amendment (homed by a "save-my-score" PROMPT only, solution parameterized —
  matching units 07/08).
- `[FIXED]` (nit) Architecture summary still showed bare `open("missing.txt")` — now
  `with open("missing.txt") as f: f.read()`.
- `[FIXED]` (nit) stretch still literally named "append-a-new-high" — renamed to "add-a-new-high".

### Round 2 revisions (2026-09-07)
Amendment now: requires += `parameters, return-value`; practices += `builtin-functions, dict-literal,
if-statement, list-literal, print, variable, string-concat, string-literal, type-conversion,
int-type, error-messages, input` (12). Payload split (fable) empirically re-validated; glm's 5 nits
+ sol's input blocker + doc nits all fixed. Re-validated green. Re-dispatching [glm]/[fable]/[sol]
round 2 to confirm.

### Round 2 re-review verdicts (2026-09-07)
**[fable] round 2: APPROVE WITH NITS.** Round-1 int-parse BLOCKER truly resolved — payload split
coherent end-to-end (savegame.txt only ever int-parsed; settings.txt only text/membership; no name
leak; asserts on the correct files). Closure PASS (every amended concept ≤unit-08, `practices ∩
introduces` empty, `input` correctly homed), over-listing PASS, closure-safety PASS (no .split/
slicing/os/tempfile/append/classes/nested-loops; with-only opens; FileNotFound in no-exec). No new
problems (separate `with` blocks avoid exhausted-iterator; clean-slate forces create-before-read).
Content-gate nits: N1 narrate `for line in f:` as `for-loop` file-iteration (not list-loop —
list-loop is `for score in scores`; both in-union, no gap); N2 confirm `==`/`<`/`>` stay OUT of
student exercise cells (only in solution asserts). Awaiting [glm]/[sol] round 2.

**[glm] round 2: APPROVE WITH NITS.** All 5 round-1 nits confirmed resolved; payload split coherent
+ closure-safe; amended union complete + not over-listed. New nit FIXED: the `input` home was a
"phantom exercise" (amendment cited "save-my-score" but the Phase-B enumeration lacked it) — added
`save-my-score` explicitly as a SCORE→`int()`→`savegame.txt` path (so the int-only split holds) and
pinned it as input's named home; also fixed the residual literal "append-a-new-high" → "add-a-new-high".
Optional advisory-wording touch-up on the scanner mentions: left as-is (Phase C already frames the
scanner as advisory).

**[sol] round 2: REJECT → resolved.** sol confirmed input blocker FIXED, open() nit FIXED, closure
scan NONE FOUND (all 25 union symbols homed; prereq/coverage PASS), file-I/O design sound. Sole
REJECT reason: the leftover literal `append-a-new-high` in the Phase-B exercise enumeration (sol
reviewed committed HEAD, before the working-tree rename). `[FIXED]` — the exercise is now
`add-a-new-high` in the enumeration; the only remaining `append-a-new-high` strings are ledger
history describing the rename. Re-dispatching a focused [sol] round 3 to confirm.

**[sol] round 3: APPROVE.** Enumeration confirmed: `save-my-score` present (input's home,
score→int→savegame.txt); stretch is `add-a-new-high`; `append-a-new-high` only in ledger history.

## Plan Gate — CONSENSUS REACHED (2026-09-07)
- `[self]` APPROVE · `[fable]` APPROVE WITH NITS · `[glm]` APPROVE WITH NITS · `[sol]` APPROVE (r3).
- Round 1 was a convergent 2× REJECT (fable int-parse crash; sol `input` used-but-unlisted) + glm
  5 nits; all fixed in round 2, plus a round-2 phantom-exercise + doc-literal nit, fixed in round 3.
  The file-I/O CI-safety design was empirically validated against the real NotebookClient executor.
  No open blockers.
- **Gate PASSED. Proceeding to Phase A → Phase B → Phase C.**
