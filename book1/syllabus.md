# Book 1 — Year 1 Syllabus

Project-first Python fundamentals for middle school students with zero programming experience.
~36 lessons of 60–90 minutes across one school year (the lesson counts are advisory workload estimates — a teacher pulls in as many worked examples as class time allows).
Every unit opens with a project the students want to build; concepts arrive only when the project needs them (decision D-001).
Machine-readable arc: `curriculum/coverage-map.yaml` against `curriculum/concepts.yaml`.
Every unit ships stretch ("Challenge") exercises for faster students; core content never depends on them.

## Arc at a glance

| # | Entry | Kind | Lessons | The hook |
|---|-------|------|---------|----------|
| 1 | `unit-01-story-machine` | unit | 3 | Build a Mad-Libs machine that writes silly stories from your friends' words. |
| 2 | `unit-02-number-detective` | unit | 4 | The computer picks a secret number — outsmart it in as few guesses as possible. |
| 3 | `checkpoint-01-first-steps` | checkpoint | 0.5 | Show what you've got: stories and guessing. |
| 4 | `unit-03-turtle-art-studio` | unit | 3 | Command a robot turtle to draw spirals, stars, and gallery-worthy art. |
| 5 | `unit-04-quiz-show` | unit | 3 | Host your own quiz show with scores, streaks, and sudden death. |
| 6 | `unit-05-function-factory` | unit | 3 | Package your best tricks into reusable machines — greeting cards and turtle stamps. |
| 7 | `checkpoint-02-loops-and-functions` | checkpoint | 0.5 | Loops and functions, proven. |
| 8 | `project-01-arcade-night` | project | 2 | Milestone: design and build your own mini-game; class plays everyone's. |
| 9 | `unit-06-secret-codes` | unit | 3 | Encrypt messages with ciphers only your friends can crack. |
| 10 | `unit-07-high-score-hall` | unit | 2 | A Hall of Fame that tracks and sorts every score in the class. |
| 11 | `unit-08-word-wizard` | unit | 2 | A translator and word-game engine powered by dictionaries. |
| 12 | `checkpoint-03-data-wrangler` | checkpoint | 0.5 | Strings, lists, and dicts, proven. |
| 13 | `unit-09-save-point` | unit | 2 | Games that remember you — save and load real files. |
| 14 | `unit-10-pet-simulator` | unit | 3 | Adopt a virtual pet: feed it, teach it tricks, keep it alive (objects!). |
| 15 | `checkpoint-04-year-one-finale` | checkpoint | 0.5 | Files and objects, proven. |
| 16 | `project-02-grand-adventure` | project | 4 | Capstone: a text adventure (or arcade game) using everything from the year. |

Lesson budget: the map's `lessons` values are advisory workload units summing to 36 — 28 unit lessons + 6 project lessons + 4 half-lesson checkpoints. (Units 01–02 carry worked-example ladders, so they run 3 and 4 lessons respectively; see plan 031.)
On the calendar this fits ~34–36 class sessions: each checkpoint's half-lesson is absorbed into the session that opens the following entry when the schedule is tight.
Turtle-based lessons (units 03/05) run as `.py` scripts launched from the JupyterLab/VS Code terminal — turtle opens its own window and does not draw inside notebook cells; all other work stays in notebooks.

## Term shape

- **Term 1 (foundations):** units 01–02, checkpoint 01 — output, input, variables, decisions, first loops.
- **Term 2 (loops & functions):** units 03–05, checkpoint 02, project 01 — turtle graphics, for/while mastery, functions.
- **Term 3 (data):** units 06–08, checkpoint 03 — string surgery, lists, dictionaries.
- **Term 4 (persistence & objects):** units 09–10, checkpoint 04, project 02 — files, a gentle OOP intro, capstone.

## Rules this syllabus is bound by

- Prereq closure: no concept appears before the entry that introduces it (`coverage-map.yaml` is the contract; enforced by `tests/test_book1_curriculum.py` now, `tools/` from plan 003).
- Practice coverage: every concept is practiced beyond its introduction, before the capstone.
- Checkpoints assess only concepts already taught; they introduce nothing.
- Stretch exercises may preview, but core paths never depend on stretch content.
- Units 01–02 carry the heaviest introduction load at the most fragile point: their teacher notes allocate concepts to specific lessons explicitly, and their exercise sets stay short.
