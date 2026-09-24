# Plan 084 — Book 1b enrichment: Units 12–13, checkpoint real versions, syllabus refresh

**Goal:** Finish design 006: apply D3–D9 to U12 (Files) and U13 (Objects) — split the dense
multi-function cells, teach the missing facets (file append mode, comma-separated records, lists and
dicts as attributes, objects in a list, a method that draws, state machines), add CP-ready real versions,
and grow varied exercise sets; give all five checkpoints real-program notes; refresh the syllabus.

**Spec:** `docs/designs/006-book1b-enrichment.md` (D3 U12/U13 idioms, D4 U12 saved text-art / U13
`draw()`/`render()`, D5 BankAccount/Inventory classes, D9 U12 file-based reports and U13 state machines);
U12–U13 audit (2026-09-24, this plan's author, from the shipped notebooks).
Conventions are those of plans 080–083 (lead-in rule, binding numbering, values tables, depth rule with
the ≥3-reps-or-`requires` metadata rule, executed fence parity, bare-`input()` fences, pinned repairs,
scanner-visible reps, fixture grep).

## Dependencies

Stacked on plans 082 (U09 string methods incl. `split`/`startswith`) and 083 (U10 `split` parsing,
`join` over a list, list methods, grids; U11 dict order). Implementation starts only after 083 merges.

## Global constraints

- **Function/class form:** every exercise defines the named function(s) or class(es); solutions assert
  several distinct cases; the real program reads stdin with bare `input()` and prints the result.
- **Files:** every file exercise writes its own known data before reading it (re-runnable); paths are
  literal names ending in `.txt` passed as a parameter; solutions use unit-local file names prefixed
  `ex<N>_` so exercises never share a file. `open` always sits in a `with` block after Lesson 1's
  "old way" contrast; modes are explicit (`"w"`, `"r"`, `"a"`).
- **U12 toolkit:** everything through U11 plus `open` with `"w"`/`"r"`/`"a"`, `with`, `f.write`,
  `f.read`, `f.readline`, `for line in f:`, `line.strip()`, `line.split(",")` (split with a separator —
  a `string-methods` facet taught by a new rung). Never: `readlines`, `writelines`, `os`, `csv`, `json`,
  `try`/`except`, `enumerate`, tuple unpacking, comprehensions.
- **U13 toolkit:** U12 plus `class`, `__init__`, `self.` attributes, methods (returning, or changing
  `self`), objects passed to functions and methods, **lists and dicts as attributes**, **objects in a
  list**, `** 0.5` (already shipped in U13). Never: inheritance, `__str__`/`__repr__`, class attributes,
  `@` decorators, dataclasses, `pass`.
- **ASCII art:** methods/functions RETURN the picture as one string (`"\n".join(rows)`); no trailing
  spaces.
- **Contract lines:** every exercise ends with exactly one `**Real version:**` or `**No real version:**`
  line. U12 real programs read the data from stdin (`n`, then `n` lines, or one line of values), save it
  to a file, reload it, and print; U13 real programs read the constructor/method arguments and print the
  results. No-real cases: repair/predict exercises only.
- **Values:** fixtures below are grep-clean against shipped Book 1b and plans 082/083 (the author already
  replaced `Lea`, `Lin`, `birch`, `flour`, `quiet`, and avoided the shipped names `Board`, `Robot`,
  `Inventory` as class names).

## U12 — Files

**Rungs (lesson):**
1. **Split the dense first cell** `u12l004` (three functions, `with`, `"w"`, `"r"`, `f.read`, a loop and an
   f-string write at once). `u12l003` is split so each sentence sits above the rung it introduces:
   (a) `with open("lesson_l1_one.txt", "w") as f:` / `f.write("840\n")` (write one line; `with` closes
   the file); (b) `with open("lesson_l1_one.txt", "r") as f:` / `print(f.read())` (read it back);
   (c) a loop that writes three scores with `f.write(f"{score}\n")`; then the existing function cell
   `u12l004` as the "put it in functions" rung.
2. **After `u12l008` (end of Lesson 1): "Add to the end with `"a"`"** — rung: write `"610\n"` with `"w"`,
   then `with open(path, "a") as f: f.write("905\n")`, then read → `610` / `905`. Notice: `"w"` starts a
   fresh file, `"a"` keeps what is there and adds at the end.
3. **Split the dense statistics cell** `u12l013` (four functions) into four rungs, each with the matching
   sentence of `u12l012` as its lead-in: running total; count-by-condition; best-so-far; built-in
   statistics (the list rebuild). Notices carry the worked values `2345`, `2`, `735`,
   `[420, 735, 2345, 4]`.
4. **After `u12l017` (records across lines): "One record per line, fields split by commas"** — rungs:
   `line = "Mina,4,860"` / `parts = line.split(",")` / `print(parts)`; then `int(parts[2])` → `860`;
   then a loop over a saved file of three comma lines printing each name.
5. **D3 — one real-input `no-exec` cell per lesson:** L1 reads `n`, then `n` scores, saves them and
   prints the file text; L2 reads a target and counts saved scores at or above it; L3 reads a name and
   searches the saved roster.

**Shipped text to rewrite:** `u12l003` (split as above; "For this first lesson, `f.read()`…" stays with
rung b); `u12e001`/`u12e002` intros (new partition; real versions); U12 teacher-notes Goals, pacing,
Challenge count and Value plan.

**New exercises:**

| title | kind | fixture → exact result | genre |
|---|---|---|---|
| Append a Late Score | C | `append_round_trip([62, 48], 91, path)` → writes 62 and 48 with `"w"`, appends 91 with `"a"`, reloads → `[62, 48, 91]` (purpose comment required) | files & persistence |
| Save a Text Map | C | `map_round_trip(["#.#", "...", "#.#"], path)` → reloads `['#.#', '...', '#.#']` (one row per line, `strip`) (purpose comment required) | ASCII art, files |
| Best Team from Records | C | `best_team(["Ivo,15", "Uma,9", "Sam,22"], path)` → `"Sam"` (save the lines, reload, `split(",")`, strict find-extreme on `int(parts[1])`) (purpose comment required) | records, find-extreme |
| Words in a File | MP | `file_word_count(["red sails drift", "past docks"], path)` → 5 (`len(line.split())` per line) | text, files |
| Longest Saved Line | MP | `longest_line(["ash", "cedar grove", "oak"], path)` → `"cedar grove"` (strict `>`, first longest) | text, find-extreme |
| Numbered Lines | MP | `numbered(["whisk batter", "add eggs", "bake"], path)` → `"1: whisk batter\n2: add eggs\n3: bake"` (a line counter; rows `f"{number}: {text}"` joined with `"\n"`) | text layout |
| Average from a File | MP | `saved_average([70, 80, 96], path)` → 82.0; the stand-in and real program print `f"Average: {average}"` | statistics |
| Grade Report | MP | `grade_report([91, 78, 85, 62, 97], path)` → `"A: 2\nB: 1\nC: 1\nD: 1"` (A ≥ 90, B ≥ 80, C ≥ 70, else D; four counters and an `elif` ladder while reading) | data report |
| Shout Copy | MP | `shout_copy(["hush now", "well done"], source, target)` → reads `source`, writes each line `.upper()` to `target`, reloads `target` → `['HUSH NOW', 'WELL DONE']` | text, files |
| Keep the To-Dos | MP | `keep_todo(["TODO paint", "done sweep", "TODO wash"], source, target)` → `['TODO paint', 'TODO wash']` (`startswith("TODO")`, filtered into a second file) | filtering, files |
| Event Log | MP | `log_events(["start", "jump", "land"], path)` → writes `LOG` with `"w"`, then appends each event with its own `"a"` block, reloads → `['LOG', 'start', 'jump', 'land']` | files & persistence |
| First Long Word | MP | `first_long_word(["sky", "meadow", "brook"], 5, path)` → `"meadow"` (return at the first saved line with `len(word) >= 5`; `"none"` after the loop) | searching |
| Line of a Name | MP | `line_of(["Rae", "Tovi", "Wen"], "Wen", path)` → 3, `(…, "Zia", path)` → -1 (a line counter; return at the first match) | searching |
| Chart from a File | MP | `chart_from_file([3, 1, 4], path)` → `"###\n#\n####"` | ASCII art |
| Fix the Missing File | MP | broken: `with open("missing_scores.txt", "r") as f:` / `    print(f.read())` → `FileNotFoundError: [Errno 2] No such file or directory: 'missing_scores.txt'`; repaired: write `12` with `"w"` first → prints `12` (No real version) | debug & repair |
| Fix the Write Mode | MP | broken: `with open("ex_mode.txt", "r") as f:` / `    f.write("5\n")` (after the file exists) → `io.UnsupportedOperation: not writable`; repaired mode `"w"`, then read → prints `5` (No real version) | debug & repair |
| Predict the Overwrite | MP | predict: write `1` with `"w"`, write `2` with `"w"`, append `3` with `"a"`, then `print(f.read().strip())` → `2` / `3` (No real version) | tracing |
| Challenge: Merge Two Score Files | S | `merge_files([12, 40], [25, 3], path_a, path_b)` → `[3, 12, 25, 40]` (reload both, combine, `sort`) | files, sorting |
| Challenge: High-Score Table | S | `update_high_scores([900, 850, 700], 880, path)` → saves, reloads, adds 880, keeps the top three in descending order via `sorted` and indexes `-1`, `-2`, `-3`, rewrites the file → `[900, 880, 850]` | files, sorting |

## U13 — Objects

**Rungs (lesson):**
1. **Before `u13l003`:** a one-attribute class first — `class Marker:` / `__init__(self, label)` /
   `self.label = label`, `m = Marker("A")`, `print(m.label)`; `u13l002`'s class/`__init__` sentences are
   its lead-in; a new lead-in ("Now give the class two attributes") sits above `u13l003`.
2. **Before `u13l012`:** a Rectangle with only `area` (one method); `u13l012` (three methods) becomes the
   "more methods" rung with its own lead-in.
3. **After `u13l016`: "A method that draws"** — `draw(self)` returns `"\n".join(rows)` of
   `"#" * self.width`, one row per unit of height → `Rectangle(4, 2).draw()` in the lesson uses
   `(5, 2)` → `"#####\n#####"`.
4. **After `u13l027` (Counter): "A list as an attribute"** — `class Shelf:` with `self.books = []` and
   `add(self, title)` appending; then "Objects in a list" — a loop over three `Point`s printing each
   `x`; then **"A state machine"** — `class Lamp:` with `self.state = "off"` and `press(self)` switching
   `"off"` → `"on"` → `"off"` with `if`/`else`.
5. **D3 — one real-input `no-exec` cell per lesson:** L1 reads `x` and `y` and builds a `Point`; L2 reads
   a width and height and prints `area()`; L3 reads `n` and `n` titles into a `Shelf`.

**Shipped text to rewrite:** `u13e001`/`u13e002` intros; `u13l028` ("Put it together" gains lists as
attributes and state); U13 teacher-notes Goals, pacing, Challenge count, Value plan.

**New exercises:**

| title | kind | fixture → exact result | genre |
|---|---|---|---|
| Draw a Rectangle | C | `Rectangle(4, 2).draw()` → `"####\n####"` (purpose comment required) | ASCII art, objects |
| Bank Account | C | `BankAccount("Noor", 50)`; `deposit(30)` → 80; `withdraw(100)` → `"Insufficient funds"` (balance stays 80); `withdraw(25)` → 55 (purpose comment required) | modeling, state |
| Traffic Light | C | `TrafficLight()` starts `"green"`; `next()` → `"yellow"`, `"red"`, `"green"` (an `if`/`elif`/`else` state machine) (purpose comment required) | state machines |
| Playlist | MP | `Playlist()`; `add("Tide")`, `add("Ember")` → `count()` 2, `songs` `['Tide', 'Ember']` (a list attribute) | modeling |
| Vending Machine | MP | `VendingMachine(3)`; `insert(1)` → `"Insert 2 more"`, `insert(1)` → `"Insert 1 more"`, `insert(2)` → `"Vend! Change: 1"` (credit resets to 0) | state machines |
| Stockroom | MP | `Stockroom()`; `add("rivet", 10)`, `add("washer", 4)`, `remove("rivet", 3)` → `stock` `{'rivet': 7, 'washer': 4}` (a dict attribute; `add` uses the membership pattern) | modeling, dicts |
| Student Grades | MP | `Student("Kai")`; `add_score(80)`, `add_score(90)` → `average()` 85.0 | statistics, objects |
| Game Board | MP | `GameBoard(3)` fills a 3×3 list-of-lists with `"."`; `place(0, 0, "X")`, `place(2, 2, "O")` → `render()` `"X..\n...\n..O"` | grid & board, ASCII art |
| Total Area | MP | `total_area([Rectangle(2, 3), Rectangle(4, 5)])` → 26 (objects in a list) | aggregation |
| Closest Point | MP | `closest(Point(0, 0), [Point(3, 4), Point(1, 1), Point(6, 8)])` → the `Point(1, 1)` object (strict find-extreme on `distance`); the stand-in prints `f"{best.x} {best.y}"` → `1 1` | searching |
| Fix the Missing self | MP | broken: `def area():` inside `class Rect` → `Rect(3, 4).area()` raises `TypeError: Rect.area() takes 0 positional arguments but 1 was given`; repaired `def area(self):` → `12` (No real version) | debug & repair |
| Fix the Attribute Typo | MP | broken: `self.hieght = height` then `volume` reads `self.height` → `AttributeError: 'Box' object has no attribute 'height'`; repaired → `Box(2, 3, 4).volume()` → `24` (No real version) | debug & repair |
| Predict Two Counters | MP | predict: `a = Counter("x")`, `b = Counter("x")`, `b.increment(5)`, `print(a.count, b.count)` → `0 5` (No real version) | tracing |
| Challenge: Rover Commands | S | `Rover()` at `(0, 0)` facing `"N"`; `run("FFRFF")` → `position()` `"(2, 2) facing E"` (`"NESW"` with `find` to turn; `F` moves one step) | state machines, grids |
| Challenge: Save the Stockroom | S | `Stockroom.save(path)` writes `name,qty` lines; module-level `load_stockroom(path)` rebuilds it → `{'rivet': 7, 'washer': 4}` | files & persistence |

## Checkpoints — real-version notes (all five)

Each checkpoint question gets exactly one closing `**Real version:**` / `**No real version:**` line in
`checkpoint.ipynb`, and each Real version gets a `**The real program**` fence + `Sample input` /
`Expected output` in the checkpoint's `solutions.ipynb` (bare `input()`, the checkpoint's own toolkit —
**strict: nothing beyond the units the checkpoint covers**; no borrowed tools). No-real cases: trace /
repair questions (e.g. CP01 Q7 Read the Final Traceback Line) and CP03 Q7's seeded roll (fixed seed, no
input). Question statements, points and answers are otherwise unchanged. Checkpoint teacher-notes add
one line explaining the real-version notes.

## Syllabus refresh

`book1b/syllabus.md` "Shipped so far" gains an **Enrichment (design 006, plans 079–084)** subsection:
per-unit exercise counts after enrichment, the real-input pattern, the ASCII-art and genre threads, and
the widened toolkit (079). Roadmap text is unchanged.

## Binding final exercise order (Challenges last; `More Practice: ` prefix)

- **U12 (28):** 1–7 existing core · 8 Append a Late Score · 9 Save a Text Map · 10 Best Team from Records
  · 11–24 MP: Words in a File, Longest Saved Line, Numbered Lines, Average from a File, Grade Report, Shout
  Copy, Keep the To-Dos, Event Log, First Long Word, Line of a Name, Chart from a File, Fix the Missing
  File, Fix the Write Mode, Predict the Overwrite · 25–28 Challenges: Prove That a Fresh Save Replaces the Old One (was 8), Find Two Statistics
  in One Pass (was 9), Merge Two Score Files, High-Score Table.
- **U13 (24):** 1–7 existing core · 8 Draw a Rectangle · 9 Bank Account · 10 Traffic Light · 11–20 MP:
  Playlist, Vending Machine, Stockroom, Student Grades, Game Board, Total Area, Closest Point, Fix the
  Missing self, Fix the Attribute Typo, Predict Two Counters · 21–24 Challenges: Rectangle Size Band (was
  8), Counter Snapshot (was 9), Rover Commands, Save the Stockroom.

## Depth (D7: introduced ≥5, practiced ≥3; counted from solutions stand-in code)

- **U12 introduces:** `file-read`, `file-write`, `with-statement` — each ≥20 (every file exercise).
- **U12 practices** (named reps): `transform-each` 3 (Ex 2, Shout Copy, Save a Text Map);
  `linear-search` 3 (Ex 7, First Long Word, Line of a Name — each returns at the first match);
  `find-extreme` 4 (Ex 5, Challenge 2, Best Team from Records, Longest Saved Line); `running-total`/
  `accumulator` ≥3 (Ex 3, Average from a File, Challenge 2); `count-by-condition` 3 (Ex 3, Grade Report,
  Words in a File); `builtin-functions` ≥3; `list-literal` ≥3; `f-string` 3 (Numbered Lines, Average
  from a File, Grade Report); `comment` 3 (Ex 8–10 stand-ins); `int-type`/`naming` ≥3.
- **U13 introduces:** `class-def`, `init-method`, `attributes` ≥20; `methods` ≥18.
- **U13 practices:** `f-string` ≥3 (Ex 5, Closest Point, Rover Commands); `float-type` 3 (Ex 4,
  Student Grades, Closest Point's distances); `file-read`/`file-write`/`with-statement` 3 (Ex 7,
  Challenge 2 Counter Snapshot, Save the Stockroom); `type-conversion` 3 (Ex 7, Counter Snapshot, Save
  the Stockroom); `comment` 3 (Ex 8–10); `int-type`/`naming` ≥3.

## Metadata deltas (manifest + coverage-map; ≥3 named reps → `practices`, fewer → `requires`)

- **U12 `practices` +=** `input`, `type-conversion` (every real program), `string-concat` (Chart from a
  File, Numbered Lines, Save a Text Map); **`requires` +=** `elif-else` (Grade Report — one rep),
  `list-sort` (Merge, High-Score Table — two reps), `error-messages` (two repairs).
- **U13 `practices` −=** `string-slice` (one exercise rep, Ex 5 → **`requires`**).
- **U13 `practices` +=** `input` (every real program), `list-append` (Playlist, Shelf lesson, Game Board,
  Stockroom save), `dict-access` (Stockroom, Save the Stockroom, Challenge load), `elif-else` (Traffic
  Light, Vending Machine, Rover Commands), `find-extreme` (Closest Point only → `requires`),
  `nested-loops` (Game Board only → `requires`), `error-messages` (two repairs → `requires`),
  `list-loop` (Total Area, Closest Point, Student Grades), `string-concat` (Draw a Rectangle, Game Board,
  Rover Commands).
- Checkpoints: no manifest change (fences are reviewer-enforced, the checkpoint's concepts unchanged).

## Phases

- **Phase B (Codex gpt-6-sol ×3, direct `codex exec` in the main checkout):** U12 statements + rungs;
  U13 statements + rungs; checkpoint Real/No-real lines (all five `checkpoint.ipynb`).
- **Phase C (Codex ×3, separate fresh sessions):** U12 and U13 solutions (stand-ins + asserts, fences);
  checkpoint solution fences.
- **Phase D (inline):** U12/U13 teacher-notes; checkpoint teacher-notes lines; syllabus refresh; metadata
  deltas.
- **Phase E — VERIFICATION (audits first, ci-local last):** toolkit AST audit of every cell and fence
  (U12/U13 allow-lists; checkpoints against their covered units); contract + fence-parity audit (every
  fence EXECUTED with its Sample input, in a scratch directory so file fences cannot touch the repo;
  stdout == Expected output == the stand-in's printed lines) for U12, U13 and all five checkpoints; file
  hygiene (solutions leave no stray files outside the unit folder; `ex<N>_` prefixes unique); fixture grep;
  depth + genre tables; manifest ↔ coverage-map diff + honesty scan; `scripts/ci-local.sh` ALL GREEN;
  post-execution report.

## Out of scope

Tooling; Book 1; the project (`project-01-algorithm-challenge`) — its brief already reads stdin.

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- Every fixture computed by running reference code (scratch script), including the exact
  `FileNotFoundError`, `io.UnsupportedOperation: not writable`, `TypeError` and `AttributeError` lines;
  shipped-name collisions replaced before review (`Lea`, `Lin`, `birch`, `flour`, `quiet`; class names
  `Board`/`Robot`/`Inventory` avoided).
- Folded before dispatch: `linear-search` given two early-exit exercises (First Long Word, Line of a
  Name; U12 → 28); thin tags moved to `requires` under the ≥3-reps rule (U12 `elif-else`, U13
  `string-slice`).
- Watch items: checkpoint fences must stay inside each checkpoint's covered units (strict); U12 fences
  write files, so Phase E runs them in a scratch directory.

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
