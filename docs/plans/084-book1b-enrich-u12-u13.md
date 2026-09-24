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
  `f.read`, `f.readline`, `for line in f:`, `line.strip()`, `line.split()` (U09's word walk), `line.split(",")` (split with a separator —
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
- **Values:** every new fixture is grepped (whole word) against shipped Book 1b and plans 082/083 before
  Phase B and again in Phase E; replaced so far: `Lea`, `Lin`, `birch`, `cedar`, `larch`, `flour`,
  `quiet`, `Sam`, `Noor`, `Kai`, `610`, and the class names `Board`, `Robot`, `Inventory`, `Box`.
- **Counting rule (as plans 080–083):** scanner closure reads code cells only; the D7 depth audit counts
  distinct exercises from solution stand-in code **plus executed real-program fences** (the only source of
  `input` reps, since solution code cells never call `input()`); lesson rungs never count.

## U12 — Files

**Rungs (lesson):**
1. **Split the dense first cell** `u12l004` (three functions, `with`, `"w"`, `"r"`, `f.read`, a loop and an
   f-string write at once). `u12l003` is split so each sentence sits above the rung it introduces:
   (a) `with open("lesson_l1_one.txt", "w") as f:` / `f.write("840\n")` (write one line; `with` closes
   the file); (b) `with open("lesson_l1_one.txt", "r") as f:` / `print(f.read())` (read it back);
   (c) a loop that writes three scores with `f.write(f"{score}\n")`; then the existing function cell
   `u12l004` as the "put it in functions" rung.
2. **After `u12l008` (end of Lesson 1): "Add to the end with `"a"`"** — rung: write `"575\n"` with `"w"`,
   then `with open(path, "a") as f: f.write("905\n")`, then read → `575` / `905`. Notice: `"w"` starts a
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
rung b); `u12l012` (split across the four statistics rungs of rung 3); `u12l014` ("The last function
deliberately uses a direct file loop…" → one Notice per rung, each naming its own function and value); `u12e001`/`u12e002` intros (new partition; real versions); U12 teacher-notes Goals, pacing,
Challenge count and Value plan.

**New exercises:**

| title | kind | fixture → exact result | genre |
|---|---|---|---|
| Append a Late Score | C | `append_round_trip([62, 48], 91, path)` → writes 62 and 48 with `"w"`, appends 91 with `"a"`, reloads → `[62, 48, 91]` (purpose comment required) | files & persistence |
| Save a Text Map | C | `map_round_trip(["#.#", "...", "#.#"], path)` → reloads `['#.#', '...', '#.#']` (one row per line, `strip`) (purpose comment required) | ASCII art, files |
| Best Team from Records | C | `best_team(["Ivo,15", "Uma,9", "Teo,22"], path)` → `"Teo"` (save the lines, reload, `split(",")`, strict find-extreme on `int(parts[1])` seeded `best_points = -1`, `best_name = ""` as CP04 Q5 does) (purpose comment required) | records, find-extreme |
| Long Words in a File | MP | `long_word_count(["red sails drift", "past docks"], path)` → 4 (count words longer than 3 letters while walking `line.split()`) | text, files |
| Longest Saved Line | MP | `longest_line(["ash", "fir hollow", "oak"], path)` → `"fir hollow"` (strict `>`, first longest) | text, find-extreme |
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
2. **Before `u13l012`:** a Rectangle with the shipped signature `(code, width, height)` and only `area`
   (one method); `u13l012` (three methods) becomes the
   "more methods" rung with its own lead-in.
3. **After `u13l016`: "A method that draws"** — `draw(self)` returns `"\n".join(rows)` of
   `"#" * self.width`, one row per unit of height, rows collected with `append` → the lesson uses
   `Rectangle("D-1", 5, 2)` (the lesson's `(code, width, height)` class) → `"#####\n#####"` (the exercise
   defines its own two-argument class and uses `(4, 2)`).
4. **After `u13l027` (Counter): "A list as an attribute"** — `class Shelf:` with `self.books = []` and
   `add(self, title)` appending; then **"A dictionary as an attribute"** — `class Scoreboard:` with
   `self.points = {}` and `record(self, name, amount)` storing `self.points[name] = amount` (one idea: the
   attribute is a dict; used before Stockroom); then "Objects in a list" — a loop over three `Point`s printing each
   `x`; then **"A state machine"** — `class Lamp:` with `self.state = "off"` and `press(self)` switching
   `"off"` → `"on"` → `"off"` with `if`/`else`.
5. **D3 — one real-input `no-exec` cell per lesson:** L1 reads `x` and `y` and builds a `Point`; L2 reads
   a width and height and prints `area()`; L3 reads `n` and `n` titles into a `Shelf`.

**Shipped text to rewrite:** `u13l001` intro (also names lists as attributes and state); `u13l002`
(its heading "Make a point that carries two coordinates" and lead-in move down to `u13l003`; the new
`Marker` rung gets the heading "Make an object with one attribute"); `u13e001`/`u13e002` intros; `u13l028` ("Put it together" gains lists as
attributes and state); U13 teacher-notes Goals, pacing, Challenge count, Value plan.

**New exercises:**

| title | kind | fixture → exact result | genre |
|---|---|---|---|
| Draw a Rectangle | C | `Rectangle(4, 2).draw()` → `"####\n####"` (rows appended to a list, then `"\n".join(rows)`) (purpose comment required) | ASCII art, objects |
| Bank Account | C | `BankAccount("Idris", 50)`; `deposit(30)` → 80; `withdraw(100)` → `"Insufficient funds"` (balance stays 80); `withdraw(25)` → 55 (purpose comment required) | modeling, state |
| Traffic Light | C | `TrafficLight()` starts `"green"`; `next()` → `"yellow"`, `"red"`, `"green"` (an `if`/`elif`/`else` state machine) (purpose comment required) | state machines |
| Playlist | MP | `Playlist()`; `add("Tide")`, `add("Ember")` → `song_count()` 2 (not `count` — that name belongs to the untaught `list.count`), `songs` `['Tide', 'Ember']` (a list attribute) | modeling |
| Vending Machine | MP | `VendingMachine(3)`; `insert(1)` → `"Insert 2 more"`, `insert(1)` → `"Insert 1 more"`, `insert(2)` → `"Vend! Change: 1"` (credit resets to 0) | state machines |
| Stockroom | MP | `Stockroom()`; `add("rivet", 10)`, `add("washer", 4)`, `remove("rivet", 3)` → `stock` `{'rivet': 7, 'washer': 4}` (a dict attribute; `add` uses the membership pattern) | modeling, dicts |
| Student Grades | MP | `Student("Yusra")`; `add_score(80)`, `add_score(90)` → `average()` 85.0 | statistics, objects |
| Game Board | MP | `GameBoard(3)` fills a 3×3 list-of-lists with `"."` (each row built with `append`); `place(0, 0, "X")`, `place(2, 2, "O")` → `render()` `"X..\n...\n..O"` | grid & board, ASCII art |
| Total Area | MP | `total_area([Rectangle(2, 3), Rectangle(4, 5)])` → 26 (objects in a list) | aggregation |
| Closest Point | MP | `closest(Point(0, 0), [Point(3, 4), Point(1, 1), Point(6, 8)])` → the `Point(1, 1)` object (strict find-extreme on `distance`); the stand-in prints `f"{best.x} {best.y}"` → `1 1` | searching |
| Fix the Missing self | MP | broken: `def area():` inside `class Rect` → `Rect(3, 4).area()` raises `TypeError: Rect.area() takes 0 positional arguments but 1 was given`; repaired `def area(self):` → `12` (No real version) | debug & repair |
| Fix the Attribute Typo | MP | broken: `self.hieght = height` then `volume` reads `self.height` → `AttributeError: 'Crate' object has no attribute 'height'`; repaired → `Crate(2, 3, 4).volume()` → `24` (No real version) | debug & repair |
| Predict Two Counters | MP | predict (the cell shows its own `Counter` whose `increment(self, amount)` adds `amount`): `a = Counter("x")`, `b = Counter("x")`, `b.increment(5)`, `print(a.count, b.count)` → `0 5` (No real version) | tracing |
| Challenge: Rover Commands | S | `Rover()` at `(0, 0)` facing `"N"`; `run("FFRFF")` → `position()` `"(2, 2) facing E"` (turn with `"NESW"[("NESW".find(facing) + 1) % 4]` for `R` and `- 1 … % 4` for `L`, so W→N wraps; `F` moves one step) | state machines, grids |
| Challenge: Save the Stockroom | S | `Stockroom.save(path)` writes `name,qty` lines; module-level `load_stockroom(path)` rebuilds it → `{'rivet': 7, 'washer': 4}` | files & persistence |

## Checkpoints — real-version notes (all five)

**What changes.** Graded answers stay fixed-value (the introductions' "use the fixed given values" /
"Do not use `input()`" rules stay for the graded cells). Each introduction (`cp01s001`–`cp05s001`)
gains one sentence: "Each question ends with a **Real version** note: the solutions show the same
program reading its values with `input()`, the way a contest problem does — it is not graded." Each
question gets exactly one closing `**Real version:**` / `**No real version:**` line; question text,
points and answers are otherwise unchanged. Each Real version gets a `**The real program**` fence in the
checkpoint's `solutions.ipynb` with the pinned **Sample input** / **Expected output** below. The only **No real version** is CP01 Q7 (it
reads a traceback — D3's trace exception); CP02 Q6's fixed interval becomes a real version that reads
its last round number. Fences are
**strict**: only concepts taught up to and including the last unit the checkpoint assesses (CP01 → U03,
CP02 → U05, CP03 → U08, CP04 → U11, CP05 → U13), no borrowed tools; `input` is a U01 concept, so every
checkpoint may use it. CP04's fences use `split` (U09) and list indexing `parts[1]` (U10), inside its
range; Phase E's checkpoint audit checks fences against the taught range, not the checkpoint manifest. Booleans are read as `yes`/`no` and compared with
`==`. Function-form checkpoints (CP03–CP05) define the function in the fence, read the arguments, call
it and print the result.

| q | real input (Sample input, one item per line) | Expected output |
|---|---|---|
| CP01 Q1 | `Maya` / `Oakland` | `Maya is from Oakland.` |
| CP01 Q2 | `markers` | `Item: markers` |
| CP01 Q3 | `155` | `2 hours 35 minutes` |
| CP01 Q4 | `8` / `12` (read as text, converted with `int`) | `Average: 10.0` |
| CP01 Q5 | `94` | `Level A` |
| CP01 Q6 | `12` / `no` / `yes` (`has_pass = input() == "yes"`) | `Entry approved` |
| CP01 Q7 | **No real version** (reads a traceback) | — |
| CP02 Q1 | `67` | `Ready` |
| CP02 Q2 | `137` / `12` | `11 cartons, 5 left` |
| CP02 Q3 | `9` | `Count: 9` |
| CP02 Q4 | `9` | `Steps: 19` |
| CP02 Q5 | `20` | `Sum: 210` |
| CP02 Q6 | `50` (the last round number; the loop runs `range(1, last + 1)`) | `Count: 7` |
| CP02 Q7 | `6` | `1 2 3 4 5 6` / `2 4 6 8 10 12` / `3 6 9 12 15 18` / `4 8 12 16 20 24` / `5 10 15 20 25 30` / `6 12 18 24 30 36` (six lines, exactly) |
| CP03 Q1 | `19` | `True` |
| CP03 Q2 | `8` / `1.25` (text passed to `travel_cost`) | `Trip cost: $13.5` |
| CP03 Q3 | `20` | `210` |
| CP03 Q4 | `20` | `8` |
| CP03 Q5 | `74` | `Silver` |
| CP03 Q6 | `8` / `12` / `10` | `10.7` |
| CP03 Q7 | `30` (trials; the function still seeds with `random.seed(4)`) | `5` |
| CP04 Q1 | `Lake` | `8` |
| CP04 Q2 | `2` / `balls 6` / `cones 9` / `cones` (`n`, `n` lines `item count` split into a dict, then the item) | `9` |
| CP04 Q3 | `red blue red` (one line, `split`) | `{'red': 2, 'blue': 1}` |
| CP04 Q4 | `3` / `notebooks 4` / `pencils 10` / `erasers 3` | `17` |
| CP04 Q5 | `3` / `robot 5` / `rocket 8` / `maze 3` | `rocket` |
| CP04 Q6 | `3` | `Result: Gold: 10` |
| CP04 Q7 | `map star map` (one line, `split`) | `map: 2 of 3` |
| CP05 Q1 | `14 27 31` (one line; saved to `q1_scores.txt`, reloaded) | `[14, 27, 31]` |
| CP05 Q2 | `12 19 7 19` (one line; written to `q2_scores.txt`) | `[57, 19, 2]` |
| CP05 Q3 | `Comet Otter Falcon` / `Otter` (teams on one line, then the target) | `Found Otter` |
| CP05 Q4 | `6` / `2` | `6` / `2` (`first.x`, `first.y`) |
| CP05 Q5 | `8` / `3` | `24` / `8 by 3 has area 24` |
| CP05 Q6 | `12` | `gold` / `True` |
| CP05 Q7 | `NW-17` / `9` / `4` (saved to `q7_rectangle.txt`, read back) | `NW` / then the saved text printed with `print(text, end="")` → `NW-17` / `9` / `4` |

CP02 Q4, CP03 Q1/Q6/Q7 and CP04 Q7 values are the questions' own worked samples; Phase E runs every fence
(in a scratch directory for the CP05 file questions) and compares stdout with this table and with the
graded answer's value. Checkpoint teacher-notes add one line explaining the notes.

## Syllabus refresh

`book1b/syllabus.md` "Shipped so far" gains an **Enrichment (design 006, plans 079–084)** subsection:
per-unit exercise counts after enrichment, the real-input pattern, the ASCII-art and genre threads, and
the widened toolkit (079). Roadmap text is unchanged.

## Binding final exercise order (Challenges last; `More Practice: ` prefix)

- **U12 (28):** 1–7 existing core · 8 Append a Late Score · 9 Save a Text Map · 10 Best Team from Records
  · 11–24 MP: Long Words in a File, Longest Saved Line, Numbered Lines, Average from a File, Grade Report, Shout
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
  Long Words in a File); `builtin-functions` ≥3; `list-literal` ≥3; `f-string` 3 (Numbered Lines, Average
  from a File, Grade Report); `comment` 3 (Ex 8–10 stand-ins); `int-type`/`naming` ≥3.
- **U13 introduces:** `class-def`, `init-method`, `attributes` ≥20; `methods` ≥18.
- **U13 practices:** `f-string` ≥3 (Ex 5, Closest Point, Rover Commands); `float-type` 3 (Ex 4,
  Student Grades' `/`, Closest Point's `** 0.5`); `file-read`/`file-write`/`with-statement` 3 (Ex 7,
  Challenge 2 Counter Snapshot, Save the Stockroom); `type-conversion` 3 (Ex 7, Counter Snapshot, Save
  the Stockroom); `comment` 3 (Ex 8–10); `int-type`/`naming` ≥3.

## Metadata deltas (manifest + coverage-map; ≥3 named exercise reps → `practices`, fewer → `requires`)

The rule is applied to the concepts this plan's new work touches; shipped `requires` tags that the
existing exercises already use heavily (U12 `list-append`, `for-loop`) are left as shipped. U12
`list-loop` goes to **`practices`** with named reps: Append a Late Score (saves its list with a loop),
Save a Text Map (loops the rows), Event Log (loops the events) — and it joins the D7 reconciliation.

- **U12 `practices` +=** `input`, `type-conversion` (the real programs that read numbers — ≥3; stand-ins: Ex 2's
  `int(line.strip())` etc.), `string-methods` is already required — `split(",")`, `startswith`, `upper`
  (Best Team, Keep the To-Dos, Shout Copy) move it to **`practices`**. **`requires` +=** `elif-else`
  (Grade Report — one rep), `string-concat` (Chart from a File — one rep; Numbered Lines uses an f-string
  and `join`), `float-type` (Average from a File — one rep), `list-sort` (Merge, High-Score Table — two
  reps), `error-messages` (two repairs), `list-index` (High-Score Table's `-1`/`-2`/`-3` — one rep).
- **U13 `practices` −=** `string-slice` (one exercise rep, Ex 5 → **`requires`**).
- **U13 `practices` +=** `input` (every real program's fence), `list-append` (Playlist, Draw a Rectangle,
  Game Board — each pins `append`), `elif-else` (Traffic Light, Vending Machine, Rover Commands),
  `list-loop` (Total Area, Closest Point, Game Board's `render()`), `for-loop` (Draw a Rectangle, Game Board,
  Total Area), `list-literal` (Game Board, Total Area, Closest Point), `builtin-functions` (Student
  Grades `len`/`sum`, Game Board `range`… `len`, Draw a Rectangle `range`) — Phase E confirms each with the
  scanner on the stand-ins before the manifests change. **`requires` +=** `dict-literal`, `dict-access`
  (Stockroom, Save the Stockroom — two reps), `in-operator` (Stockroom's membership), `range-function`,
  `string-methods` (Rover's `find`, Save the Stockroom's `split`), `find-extreme` (Closest Point),
  `nested-loops` (Game Board), `error-messages` (two repairs), `list-index` (Game Board's `self.cells[row][col]` — one rep),
  `dict-loop` (Save the Stockroom's `for name in self.stock:` — one rep), `string-concat` (Draw a Rectangle's
  `"#" * width`, Rover's position text — two reps), `accumulator` (Total Area — one rep).
- `float-type` stays a U13 practice with three semantic reps: Ex 4 (`** 0.5` → `5.0`), Student Grades
  (`/` → `85.0`), Closest Point (`** 0.5` distances). (The scanner marks `float-type` only on float
  literals such as `0.5`; the reps are semantic, not scanner-inferred.)
- Checkpoints: no manifest change — fences are read-only notes, reviewer-enforced and not scanned, and
  `input` (U01) is inside every checkpoint's taught range; the checkpoints' graded code stays input-free.

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
  stdout == Expected output == the stand-in's printed lines) for U12, U13 (whose Ex 7, Counter Snapshot
and Save the Stockroom fences also write files) and all five checkpoints (against the table above — a checkpoint fence's stdout is compared with the table's Expected output,
which is the graded answer's asserted value in the printed form the table pins, since the shipped
CP03–CP05 solution cells assert returned values rather than print them);
a D3 lesson audit (one real-input `no-exec` cell per lesson: U12 3/3, U13 3/3); a D7 reconciliation that
lists, for every `practices` concept of U12 and U13, the distinct exercises supplying it; file
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

### Round 1 — verdicts

- `[self]` APPROVE WITH NITS (above).
- `[fable]` **REJECT** — fixtures not grep-clean (`Noor`, `Kai`, `Sam`, `cedar`, class `Box`); the
  checkpoint section needs every question's Real/No-real decision, input shape and sample; nits: U13
  deltas incomplete (for-loop, list-literal, builtin-functions, dict/in/range/string-methods),
  `dict-access` two reps, U12 `string-concat`/`count-by-condition` reps dishonest, U12 float, `input`
  counting, Best Team seed, rewrite list (`u12l012`, `u13l001`), U13 rung 3 wording, Phase E scratch dir
  for U13 fences.
- `[sol]` **REJECT** — checkpoint contract contradicts the "Do not use `input()`" introductions and pins
  no samples; depth/metadata reps (U12 count-by-condition, string-concat; U13 list-append, dict-access,
  float-type; the `input` counting rule); fixtures (`Sam`, `Noor`, `Kai`, `610`); missing rewrites
  (`u13l002`, `u12l014`); Phase E needs D3 and D7 evidence.
- `[glm]` pending.

### Round 1 — fold

- `[FIXED]` fixtures: `Teo`, `Idris`, `Yusra`, `fir hollow`, `Crate`, `575` (whole-word grep-clean);
  Best Team pins its seed.
- `[FIXED]` checkpoints: introductions gain a "not graded" Real-version sentence (graded cells keep
  "Do not use `input()`"); all 35 questions pinned with input shape, Sample input and Expected output;
  No real version for CP01 Q7 only (a traceback-reading question — D3's trace exception).
- `[FIXED]` counting rule stated (stand-ins + executed fences; lesson rungs never count); Words in a File
  → **Long Words in a File** (a conditional count, 4); U12 `string-concat`, `float-type`, `elif-else`,
  `list-sort`, `list-index`, `error-messages` → `requires`; U13 `list-append` reps pinned (Playlist, Draw a
  Rectangle, Game Board); `dict-access` → `requires`; U13 deltas completed from the scanner's view.
- `[FIXED]` rewrite list adds `u12l012`, `u12l014`, `u13l001`, `u13l002`; U13 rung 3 wording.
- `[FIXED]` Phase E adds the D3 lesson count, the D7 per-concept reconciliation, and scratch-directory
  execution for U13 and CP05 file fences.

### Round 1 — [glm] APPROVE WITH NITS (folded)

- Its four required fixes were already covered by the [fable]/[sol] fold (`dict-access` → `requires`;
  Long Words in a File as the third conditional count; `Sam`/`Kai`/`cedar` replaced; `string-concat`
  → `requires` in both units).
- `[FIXED]` nits: `list-loop` reps (Total Area, Closest Point, Game Board `render()`); `type-conversion`
  claim narrowed to number-reading programs; checkpoint `input` exemption stated; rung 2 keeps the shipped
  `(code, width, height)` signature; U12 toolkit names `line.split()`; Rover turns wrap with `% 4`.

### Round 2 — [fable] APPROVE WITH NITS (folded)

- `[FIXED]` rung 3 pins `Rectangle("D-1", 5, 2)`; Predict Two Counters shows its own
  `increment(self, amount)`; CP02's taught range ends at U05 (syllabus order); CP04 fence
  `split`/indexing stated as in range; U13 `requires` += `list-index`, `dict-loop`; the ≥3-reps rule's
  scope stated and U12 `list-loop` added to `requires`. `Mina` reuse in U12 rung 4 stays consistent with
  the shipped cell.

### Round 2 — [sol] REJECT (folded)

- `[FIXED]` (already folded from [fable] r2) the draw rung calls `Rectangle("D-1", 5, 2)`.
- `[FIXED]` checkpoint fences are compared with the table's Expected output (the graded answer's
  asserted value in its pinned printed form), since CP03–CP05 solution cells assert rather than print.
- `[FIXED]` a single-idea **dictionary-as-attribute** rung (`Scoreboard`) precedes Stockroom.
- `[FIXED]` the `float-type` note describes semantic reps, not scanner inference.

### Round 3 — [sol] REJECT (folded)

- `[FIXED]` CP02 Q7's Expected output pins all six rows byte-exactly.
- `[FIXED]` CP02 Q6 gets a real version (reads the last round number `50` → `Count: 7`); CP01 Q7 is the
  only No real version (D3's trace exception).
- `[FIXED]` U12 `list-loop` → `practices` with three named reps (Append a Late Score, Save a Text Map,
  Event Log), included in the D7 reconciliation.

### Round 4 — CONSENSUS

- `[sol]` APPROVE (r4, HEAD 9e5cba6) — all 34 checkpoint real-version outputs recomputed; round 1–3 issues
  resolved.
- `[fable]` APPROVE WITH NITS (r2, nits folded) · `[glm]` APPROVE WITH NITS (r1, nits folded) ·
  `[self]` APPROVE WITH NITS.

**Consensus reached — implementation starts after plan 083 merges.**

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
