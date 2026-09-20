# Plan 066 — Project 02 (Grand Adventure) real-input treatment

**Design:** `docs/designs/003-book1-real-input.md` (v6), §2 project markdown path + the u09 files-are-real
precedent + the project-01 (plan 065) integrated-real-form reading. **The FINAL Book-1 real-input slice.**

## Motivation

Project 02 (grand-adventure: a `Hero` class, three flat world dicts, an exploration loop, and file save/load —
the year's biggest build) is the LAST entry to receive the design-003 real-input norm. It follows the project-01
pattern:
- The **brief.ipynb scaffolds already read `input()`** — M1 reads the hero name, M3 reads directions in the
  exploration loop. Per **design §2 brief-row**, a Milestone starter that reads `input()` IS its real-program
  form (M1/M3 real forms live in the brief; the solutions blocks are the model answers).
- The **solutions.ipynb** proves the logic WITHOUT keyboard input: reference `Hero` (fixed `Hero("Ada")`), the
  three world dicts + `describe`/`move` helpers, a **scripted exploration driver** (`scripted_moves` list, seeded
  `random`), file save/load, and asserts (incl. `save_file_contents == "Ada\n17\nsword\nshield\n"`).

What the norm ADDS: make the **interactive assembled adventure** visible in the solutions as one integrated
`**The real program**` block under the existing `## Milestone 5` (the "assemble" milestone) — the input()-reading
form (reads the name + directions) that runs the same reference `Hero`/dicts/helpers and does the real save/load.

All 10 Book-1 units + all 4 checkpoints + project-01 already carry the norm. **This completes the rollout.**

## Metadata change — NONE

`input` is ALREADY in project-02's manifest `practices`, and the real-form is markdown-only → no add (design §5).
No `.split()` (Book-2). The integrated real form uses only union concepts (`class`/`init`/`methods`,
`dict-literal`/`dict-access`, `list`/`list-index`/`list-append`/`list-loop`, `for-loop`, `while-loop`,
`break-statement`, `if`/`elif`/`else`, `in-operator`, `file-read`/`file-write`/`with-statement`, `int-type`/
`type-conversion`, `string-methods` (`.strip()`), `f-string`, `input`, `random-module`, function calls,
`comparison`, `variable`). No `int()` misuse.

## SHAPE — one integrated real-form (the interactive assembled adventure) under `## Milestone 5`

Per the project-01 precedent, a project's one input-shaped "program" is the whole integrated build. The
**assemble** milestone (M5) is where the interactive adventure lives; its fixed twin is the scripted M3 driver +
M4 save/load + M5 assert cell. The real form (interactive) reads the name + directions and runs the same
reference `Hero`/`describe`/`move`/`apply_event`/`pick_up` defined above.

Per-milestone mapping (stated in the block's caption):
- **M1** (reads the hero name) — real form is the brief M1 starter (§2 brief-row); shown integrated in the M5
  block (`Hero(input("Name your hero: "))` + `take_damage(3)`).
- **M2** (three flat world dicts + `describe`/`move` helpers) — **fixed-reference-fixture** (class 4): the world
  is authored reference data, not read; the helpers are pure param functions (no input). Carries a
  `**No real version:**` note under `## Milestone 2` naming class 4 ([sol] BLOCKER 1, design §8). Used, not read,
  in the M5 real form.
- **M3** (reads directions in the exploration loop) — real form is the brief M3 starter (§2 brief-row); shown
  integrated in the M5 block (the interactive `while` loop reading directions).
- **M4** (file save/load) — **files-are-real** (u09): the save writes the real playthrough's hero and the load
  reads the real `adventure_save.txt`. Carries a `**Real version:**` files-are-real note under `## Milestone 4`
  ([sol] BLOCKER 1, u09 precedent); the M5 block does the round-trip with real input. No separate input() form.
- **M5** (assemble) — the integrated `**The real program**` block itself.

**§6 relationship (project-01 reading).** The real form is NOT a §6c line-for-line twin of the scripted driver —
an interactive `while`-input exploration loop has NO CI-runnable line-for-line twin (`input()` can't run in CI).
The scripted driver + save/load + M5 assert cell are the **executable fixed-data twin** (asserts pin `roll==2`,
`hero.health==17`, `inventory==["sword","shield"]`, `current=="river"`,
`save_file_contents=="Ada\n17\nsword\nshield\n"`, and `adventure_summary=="Ada finished with 17 health and found
sword."`). Validation: **§6a** = `ast.parse` of the block; **§6b** = execution parity — Phase B pipes the name +
scripted directions and checks the same final state, the save-file bytes, AND the same
`adventure_summary` RESULT LINE ([sol] BLOCKER 2 — the real form ends by printing that identical summary).

### Real-form specification (solutions markdown, appended after the `assembled-adventure` cell, under `## Milestone 5`)

`**The real program**` — caption: "the whole adventure reading real input, using the `Hero` class, world dicts,
and helpers (`describe`/`move`/`apply_event`/`pick_up`) defined above; `random` is imported in the top
`seed-adventure` cell ([fable] N3). Milestones 1 and 3 read input in the brief starters (the name and the
directions); this reference shows them assembled and interactive. Milestone 2's world dicts are fixed reference
data, and Milestone 4's save/load round-trips this playthrough through the real `adventure_save.txt`. Collect at
least one item before quitting, as Milestone 3 requires, so the inventory index has something to show ([fable]
N2)." Uses project-02's house style (plain `"..."` for non-interpolated strings, `f"..."` only for interpolation):
```python
hero_name = input("Name your hero: ")
hero = Hero(hero_name)
print(f"Starting hero: {hero.name}")
print(f"Starting health: {hero.health}")
print(f"Starting inventory: {hero.inventory}")
health_after_damage = hero.take_damage(3)
print(f"Health after damage: {health_after_damage}")

roll = random.randint(1, 6)
apply_event(hero, roll)

current = "cave"
while True:
    print(f"You are in the {current}.")
    print(describe(descriptions, current))
    direction = input("Choose a direction, or q to quit: ").strip()
    next_room = move(exits, current, direction)
    if next_room == "quit":
        print("Your hero rests for now.")
        break
    if next_room == current:
        print("You can't go that way.")
    current = next_room
    if current in room_items:
        item = room_items[current]
        if item not in hero.inventory:
            hero.pick_up(item)
            print(f"You pick up the {item}.")

first_collected_item = hero.inventory[0]
print(f"You still carry the {first_collected_item}.")

with open("adventure_save.txt", "w") as save_file:
    save_file.write(hero.name + "\n")
    save_file.write(str(hero.health) + "\n")
    for item in hero.inventory:
        save_file.write(item + "\n")

loaded_name = ""
loaded_health = 0
loaded_items = []
line_number = 0
with open("adventure_save.txt", "r") as save_file:
    for saved_line in save_file:
        cleaned_line = saved_line.strip()
        if line_number == 0:
            loaded_name = cleaned_line
        elif line_number == 1:
            loaded_health = int(cleaned_line)
        else:
            loaded_items.append(cleaned_line)
        line_number = line_number + 1

adventure_summary = f"{loaded_name} finished with {loaded_health} health and found {first_collected_item}."
print(adventure_summary)
```
(N1: the `if next_room == current:` message is only reached on an invalid direction; the parity path
`east/west/east/east/q` never triggers it. N6: `Starting inventory` print restored. BLOCKER 2: the block now ends
with the SAME `adventure_summary` line the M5 fixed cell prints/asserts.)
Uses the reference `Hero`/`describe`/`move`/`apply_event`/`pick_up`/dicts defined in the cells above
(non-self-contained, like project-01's block). It reads every input the adventure needs (name + directions) and
does the real file round-trip. **Validated (fresh scratch cwd, `random.seed(4)`, piped `Ada` + `east/west/east/
east/q`):** roll=2 (no event), health 17, `current=="river"`, inventory `["sword","shield"]`, save file bytes
`Ada\n17\nsword\nshield\n` — exact parity with the M5 assert cell.

## Data growth (§3) — N/A

The world (3 rooms) + inventory (2 items) are fixed reference fixtures the student EXTENDS ("add your own
rooms"); they are not toy SOURCE data read from input. §3 realism-growth does not apply.

## Phases

### Phase A — apply to project-02 solutions.ipynb (markdown only; NO brief.ipynb / manifest / metadata / adventure_save.txt change)

Four markdown edits to `solutions.ipynb` (only):
1. Append ONE `**The real program**` markdown cell after the `assembled-adventure` code cell (end of notebook,
   under the existing `## Milestone 5` heading — no new heading needed). The block is the integrated interactive
   adventure per spec, in project-02's house style.
2. Under `## Milestone 2` (after the `flat-world` code cell): a `**No real version:**` note naming class 4
   (fixed-reference-fixture — the world dicts are authored reference data; `describe`/`move` are pure helpers)
   ([sol] BLOCKER 1).
3. Under `## Milestone 4` (after the `save-and-load` code cell): a `**Real version:**` files-are-real note
   (the save/load round-trips the real playthrough through the real `adventure_save.txt`; no input() form)
   ([sol] BLOCKER 1, u09).
4. Extend the `reference-intro` cell with a one-sentence forward pointer ("the interactive version is shown under
   `## Milestone 5` at the end") to match project-01's intro pointer ([glm] NIT-1).
`brief.ipynb`, `manifest.yaml`, `teacher-notes.md` are NOT touched (byte-unchanged; teacher-notes audit no-op).

### Phase B — verification

- ci-local ALL GREEN (`TMPDIR=/dev/shm bash scripts/ci-local.sh`): registry+lint, notebook execution+hygiene,
  manifest/prereq/coverage, PDF build, pre-merge guard.
- Real-form validation ([sol]/[glm] fresh-process rule from project-01): `ast.parse` the block (§6a); run it in a
  FRESH process in a SCRATCH cwd (so its `adventure_save.txt` write never clobbers the project-dir artifact) with
  `random.seed(4)` injected + the reference `Hero`/dicts/helpers defined, piped `Ada\neast\nwest\neast\neast\nq\n`
  → (§6b) final state health 17 / `current=="river"` / inventory `["sword","shield"]`; the written save file
  bytes equal `Ada\n17\nsword\nshield\n`; AND the final printed RESULT LINE equals
  `Ada finished with 17 health and found sword.` (identical to the M5 fixed cell's `adventure_summary` — [sol]
  BLOCKER 2). Exactly one `randint` call (roll=2), matching the fixed driver.
- Confirm 0 `input()` in any `solutions.ipynb` **code** cell (the real form + all three notes are markdown).
- Scope invariant ([sol] BLOCKER 3 — NAME-LIST ALLOWLIST): `git diff --name-only $(git merge-base HEAD main)..HEAD`
  must equal EXACTLY `docs/plans/066-project02-real-input.md` and
  `book1/projects/project-02-grand-adventure/solutions.ipynb` (proves NO other tracked file changed, not merely
  that brief/manifest/teacher-notes are unchanged). `adventure_save.txt` is a **gitignored** artifact
  (.gitignore:34) regenerated by the M4/M5 solution cells; its post-CI bytes stay `Ada\n17\nsword\nshield\n`
  (byte check, not git diff — git can't diff an ignored file).

## Out of scope

- No brief.ipynb edit, no new milestones, no difficulty change, no metadata change, no adventure_save.txt change.
  teacher-notes.md audit-only. Only `solutions.ipynb` is modified.
- **Verification exemption:** project-content plan; Phase B is the named verification phase.
- The design-§4 dict-idiom fix (flagged in plan 064) remains a separate future docs slice — this plan uses no
  dict-read idiom (the world dicts are authored, not read).

## Plan Review

### Round 1 (2026-09-20) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.

#### [self] (2026-09-20)
**APPROVE.** One integrated real form under the EXISTING `## Milestone 5` mirrors project-01 (integrated capstone;
solutions already milestone-organized so no new heading). Mapping sound: M1/M3 real forms are the brief starters
(§2 brief-row), M2 fixed-reference-fixture (authored world dicts + pure helpers), M4 files-are-real (u09). §6c
N/A (interactive loop, no CI-runnable line-for-line twin) → §6b execution parity + §6a state-contract asserts.
Parity VALIDATED locally (fresh scratch cwd, seed(4), piped `Ada`+`east/west/east/east/q`): roll=2 (no event),
health 17, `current=="river"`, inventory `["sword","shield"]`, save bytes `Ada\n17\nsword\nshield\n` — exact
match to the M5 assert cell; exactly one randint. Metadata NONE (input already in manifest + markdown-only). No
`.split()`; **no dict-READ idiom** (world dicts are authored) so the design-§4 bug is not in play. adventure_save.txt
gitignored (.gitignore:34) → byte-invariant check, scratch-cwd validation. Phase B named. Closure clean.

#### [fable] (2026-09-20)
**APPROVE WITH NITS.** Independently validated (fresh scratch cwd, seed(4), piped `Ada`+`east/west/east/east/q`):
one randint→2 (no event), health 17, `current=="river"`, inventory `["sword","shield"]`, save bytes
`Ada\n17\nsword\nshield\n`, final line exact — parity with the M5 assert cell. Shape/mapping sound (one block
under existing `## Milestone 5`, matches project-01; M1/M3 brief starters §2 brief-row; M2 class 4; M4
files-are-real). Pedagogy good; whole build realized; reference class/helpers untouched. Phase B proper. Nits
(none blocking):
- N1: real form silently re-describes the room on a bad direction (`move` returns `current`), vs brief M3's
  "You can't go that way." → add `if next_room == current: print("You can't go that way.")` (keeps `move`
  unchanged; the parity path never hits it). → FOLD (brief-M3 fidelity).
- N2: quitting before collecting → `hero.inventory[0]` IndexError → caption half-sentence "collect at least one
  item before quitting, as Milestone 3 requires" (not a guard). → FOLD (caption).
- N3: caption should mention `apply_event` and that `random` is imported in the top `seed-adventure` cell (the
  block calls `random.randint` without its own import). → FOLD (caption).
- N4: a roll of 1 in a real run applies 3 silent damage — consistent with `apply_event`; WONTFIX (optionally
  note the trap is silent/optional). → leave.
- N5: design §1/§8 wants class-4 exempts to carry a `**No real version:**` note; M2 is handled via the M5
  caption (project-01 precedent — M2 is a consumed component, not a standalone task). → FOLD: state in the plan
  that no separate `## Milestone 2` note is added, so the content gate doesn't raise it.
- N6: real form omits `print(f"Starting inventory: {hero.inventory}")` (in brief M1 / solutions cell 3). → FOLD
  (add for fidelity; prints `[]`, no state change, parity unaffected).

#### [glm] (2026-09-20)
**APPROVE WITH NITS.** All 7 checks verified; independently reran parity in a fresh scratch cwd (seed(4), piped
`Ada`+`east/west/east/east/q`): roll=2, health 17, river, `["sword","shield"]`, save bytes `Ada\n17\nsword\nshield\n`,
exactly one randint `[(1,6)]`. Shape/mapping sound (append under existing `## Milestone 5`, no new heading —
correctly different from project-01; M1/M3 brief starters §2 brief-row; M2 class 4; M4 files-are-real). Closure
clean; NO dict-READ idiom so the §4 hazard genuinely not in play (deferral correctly scoped out). Metadata NONE.
Save-file byte-handling correct (gitignored, byte-compare not git-diff, scratch-cwd). Scope: merge-base diff =
plan only; Phase B enforces byte-unchanged. Nits:
- NIT-1 (consistency): project-01's solutions intro carries a forward pointer to its real form; project-02's
  `reference-intro` has none → add a one-sentence pointer ("the interactive version is under `## Milestone 5`").
  → FOLD.
- NIT-2 (= [fable] N6): block omits the M1 `print(f"Starting inventory: {hero.inventory}")` line → add for
  fidelity. → FOLD. (Also flags the SHAPE prose says `Hero(input(...))` while the spec block uses the two-line
  `hero_name = input(...)` form — trivial; the two-line form matching the brief is kept.)

#### [sol] (2026-09-20) — reviewed stale draft 9dde674
**REJECT** (3 BLOCKERs). Seeded parity, fidelity, closure, metadata, gitignored-file handling all PASS.
Resolution:
- `[OPEN]` BLOCKER 1 — per-task cue notes: design §8 wants M2 to carry a `**No real version:**
  fixed-reference-fixture (class 4)` note; u09 wants M4 to carry a `**Real version:**` files-are-real note. The
  M5 caption alone doesn't satisfy the per-task cues, and project-02 solutions HAVE `## Milestone 2`/`## Milestone
  4` headings. RESOLVED: add the two cue notes under those headings (still ONE real-program block under M5). This
  supersedes [fable] N5 (caption-only) — [sol]'s per-task-cue reading is correct for a milestone-organized project.
- `[OPEN]` BLOCKER 2 — §6b result-line parity: the fixed M5 cell prints/asserts
  `adventure_summary == "Ada finished with 17 health and found sword."`, but the draft's real form ended with a
  DIFFERENT line. RESOLVED: the real form now ends by computing + printing the SAME
  `adventure_summary = f"{loaded_name} finished with {loaded_health} health and found {first_collected_item}."`,
  so §6b result-line parity is exact. (Also fixed wording: §6a is `ast.parse`; the scripted driver + asserts are
  the executable fixed-data twin / M5 assert proof, not a "§6a proof".)
- `[OPEN]` BLOCKER 3 — scope check: RESOLVED: Phase B now uses a merge-base NAME-LIST ALLOWLIST requiring the
  changed set to be exactly {the plan file, solutions.ipynb}, plus the separate gitignored-file byte check.
Re-verifying [sol] on the reworked plan (no 3-of-4 shortcut on a REJECT).

#### [sol] round 2 (2026-09-20) — re-verify on 501d90b
**APPROVE WITH NITS.** All 3 BLOCKERs RESOLVED (M2/M4 cue notes under existing headings; real form ends with the
identical `adventure_summary` + Phase-B result-line check; name-list allowlist scope + §6a/§6b wording). Re-ran
the fenced form: one randint→2, health 17, river, `["sword","shield"]`, save bytes exact, result line matches the
M5 assert; unchanged reference fns; no `.split()`/dict-read; metadata NONE. NIT: Phase A said "Three" edits but
listed four → fixed to "Four".

### Round 1 — FINAL outcome: **FULL 4-way plan-review consensus.** [self]/[fable]/[glm]/[sol] APPROVE (all nits
folded; [sol] REJECT→APPROVE after M2/M4 cue notes + §6b result-line parity + name-list allowlist scope). Gate
CLOSED → implementation.

## Content Review
_(pending)_

## Post-Execution Report
_(pending)_
