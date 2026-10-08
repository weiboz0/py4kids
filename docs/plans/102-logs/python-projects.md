# Plan 102 Phase B log — python-projects

Check-kind confirmation for all 236 python-projects items under plan 102's Rules.
Every statement was read against its starter, the solution's top-level asserts, the canonical output (expected-output, predict) and the derived self-check list.
Keys below drop the `python-projects/` prefix.

## Summary

| kind | proposed (classify) | confirmed |
|---|---:|---:|
| asserts | 91 | 59 |
| expected-output | 17 | 11 |
| predict | 6 | 7 |
| self-check | 122 | 159 |
| total | 236 | 236 |

- Retags: 40 (listed below).
- Statement edits (rule 2): **none**. Every non-portable assert name was checked against its statement; no sentence instructs storing a value under a name and merely fails to mark it (the bare words are prose: 'the running total', 'the midpoint', 'for the champion', 'a verdict'). Names that appear only in a `**Real version:**` panel (`double_message`, `final_message`, `border_total`, `pets`) are not core-task instructions, so marking them would be a wider change. No allowed-diffs entries are needed; the publish baseline is untouched.
- Authored `requirements`: 42 self-check items (where the derived list misstated the task). Authored `also_check`: 69 items.
- `answer_format`: 0 authored; every hidden-answer item keeps the derived, case-sensitive format (see below).
- `whitespace: exact`: none (no python-projects statement makes tabs, indentation or alignment part of an answer).
- Concepts: the 3 unattributed lesson blocks are attributed; 0 items were unattributed; gap list empty.

## Per-unit counts (confirmed)

| entry | items | asserts | expected-output | predict | self-check |
|---|---:|---:|---:|---:|---:|
| unit-01-story-machine | 9 | 0 | 1 | 0 | 8 |
| unit-02-number-detective | 10 | 0 | 0 | 0 | 10 |
| checkpoint-01-first-steps | 7 | 1 | 0 | 2 | 4 |
| unit-03-turtle-art-studio | 12 | 3 | 1 | 0 | 8 |
| unit-04-quiz-show | 21 | 0 | 0 | 1 | 20 |
| unit-05-function-factory | 22 | 11 | 1 | 1 | 9 |
| checkpoint-02-loops-and-functions | 8 | 0 | 0 | 3 | 5 |
| project-01-arcade-night | 4 | 0 | 0 | 0 | 4 |
| unit-06-secret-codes | 24 | 3 | 0 | 0 | 21 |
| unit-07-high-score-hall | 24 | 9 | 0 | 0 | 15 |
| unit-08-word-wizard | 23 | 11 | 2 | 0 | 10 |
| checkpoint-03-data-wrangler | 8 | 5 | 2 | 0 | 1 |
| unit-09-save-point | 25 | 8 | 2 | 0 | 15 |
| unit-10-pet-simulator | 26 | 5 | 1 | 0 | 20 |
| checkpoint-04-year-one-finale | 8 | 3 | 1 | 0 | 4 |
| project-02-grand-adventure | 5 | 0 | 0 | 0 | 5 |

## Retags

- `unit-01-story-machine/exercises/exercise-three`: asserts -> self-check. assert tests the solution's snack while the student chooses their own words (rule 1(b), plan example)
- `checkpoint-01-first-steps/checkpoint/checkpoint-05`: asserts -> self-check. scripted input() (rule 1 named case); derived checklist is the one-line task
- `checkpoint-01-first-steps/checkpoint/checkpoint-11`: asserts -> self-check. naming/comment question; asserted player_guess == 37 is not fixed by the task
- `unit-04-quiz-show/exercises/exercises-01`: asserts -> self-check. score == 2 depends on the student's chosen booleans (rule 1(b))
- `unit-04-quiz-show/exercises/exercises-03`: asserts -> self-check. score == 3 depends on the student's chosen booleans (rule 1(b), brief example)
- `unit-04-quiz-show/exercises/exercises-05`: asserts -> self-check. score == 4 depends on the student's chosen correct/category (rule 1(b))
- `unit-04-quiz-show/exercises/18831267`: asserts -> self-check. the two asserts (penalty True/score 2, penalty False) need different student-chosen booleans and cannot both hold
- `unit-04-quiz-show/exercises/u04-ex08`: asserts -> self-check. core task reads the answers with input(); asserts compare scripted answers
- `unit-04-quiz-show/exercises/u04-ex09`: asserts -> self-check. q/strikes/score depend on the student's three chosen boolean results
- `unit-04-quiz-show/exercises/u04-ex10`: asserts -> self-check. scripted input() (rule 1 named case)
- `unit-04-quiz-show/exercises/u04-ex11`: asserts -> self-check. scripted input() (rule 1 named case)
- `unit-04-quiz-show/exercises/u04-count-correct-heading`: asserts -> self-check. scripted input() (rule 1 named case)
- `unit-04-quiz-show/exercises/exercises-14`: asserts -> self-check. core task asks the player with input(); score == 8 compares the solution's stand-in answers
- `unit-05-function-factory/exercises/exercise-3-heading`: asserts -> self-check. double_message is named only in the Real version panel, not the core task; expected-output does not fit because the solution prints an extra explanation line
- `unit-05-function-factory/exercises/exercise-9-heading`: asserts -> self-check. turn_angle(7) is portable (rule 1(a)) but final_message is named only in the Real version panel and its text is the student's own f-string
- `unit-05-function-factory/exercises/exercise-7-heading`: asserts -> self-check. border_total is named only in the Real version panel; the printed 280 does not occur in the statement (single-token rule)
- `checkpoint-02-loops-and-functions/checkpoint/question-3-heading`: asserts -> self-check. message == 'Hello, Maya!' depends on the student's sample name and greeting wording (rule 1(b))
- `checkpoint-02-loops-and-functions/checkpoint/question-6-heading`: self-check -> predict. a trace question ('Predict the one message that prints') whose fenced program prints one line; the tool's regex missed the wording
- `unit-06-secret-codes/exercises/b8560ccca999`: expected-output -> self-check. the 3 is the worked example's illustration; the statement never fixes what the program prints, and the assert names the solution's own result
- `unit-06-secret-codes/exercises/3e97d2c30aa2`: expected-output -> self-check. 'Scan a message' leaves the message open; xyzapple -> 3 only illustrates
- `unit-06-secret-codes/exercises/aa3b6e2e8b04`: expected-output -> self-check. 'a word' is not fixed; abc -> 6 only illustrates
- `unit-07-high-score-hall/exercises/0ffe49bf`: asserts -> self-check. the asserts only re-check the given list, not the fix or the loop output; the first cell errors on purpose, so a whole-program output check does not fit
- `unit-07-high-score-hall/exercises/5c20b19f`: asserts -> self-check. scripted input() (rule 1 named case)
- `unit-07-high-score-hall/exercises/dfc665d7`: asserts -> self-check. scripted input() (rule 1 named case)
- `unit-07-high-score-hall/exercises/d8fc52e2`: asserts -> self-check. `best is None` and `best is scores` describe the two phases and cannot both hold after the student's code
- `unit-07-high-score-hall/exercises/exercise-14-linear-search`: asserts -> self-check. the asserts (1050 and 'not found') are for two different bars and cannot both hold
- `unit-07-high-score-hall/exercises/a293634ac2fe`: asserts -> self-check. best/worst appear only in the worked example; the task says 'track both the highest and lowest' without naming them, so a correct program may use other names; derived checklist matches
- `unit-08-word-wizard/exercises/2d315b39`: asserts -> self-check. `known is True` and `known is False` are the two phases and cannot both hold; the f-string wording is the student's own
- `unit-08-word-wizard/exercises/5703c375`: asserts -> expected-output. the assert re-checks a literal lookup and passes without the student's result; the fixed lookup prints `???`, which the statement shows
- `checkpoint-03-data-wrangler/checkpoint/question-1`: asserts -> self-check. the assert re-checks the given word, not the student's f-string, whose separators are free
- `unit-09-save-point/exercises/0cc7f084`: expected-output -> self-check. the core result is the file contents; the confirmation line alone would pass without writing the file
- `unit-09-save-point/exercises/e2692eb8`: expected-output -> self-check. the core result is the file contents; the confirmation line alone would pass without writing the file
- `unit-10-pet-simulator/exercises/c8e092dc`: expected-output -> self-check. the canonical 3 occurs only in the heading 'Exercise 3'; the body never states it, and new_hunger is the solution's own name
- `unit-10-pet-simulator/exercises/7067fd3f`: asserts -> self-check. pets[0].name == 'Ivy' tests the student's chosen pet names
- `unit-10-pet-simulator/exercises/23283984`: expected-output -> self-check. which meal and treat to feed is the student's choice, so Buddy's hunger is not fixed
- `unit-10-pet-simulator/exercises/29dbfcff`: asserts -> self-check. hunger 3 depends on the student's own food dictionary
- `unit-10-pet-simulator/exercises/c368d34e`: asserts -> self-check. the pets list ('several pets') is the student's own
- `unit-10-pet-simulator/exercises/7b04a673`: asserts -> self-check. `pets` is named only in the Real version panel and len(pets) >= 3 does not check show_trick
- `unit-10-pet-simulator/exercises/4dfdb434`: asserts -> self-check. pet names and foods are the student's own
- `project-02-grand-adventure/brief/milestone-1`: asserts -> self-check. scripted input() (rule 1 named case)

Main reasons:
- Asserts on student-chosen values (rule 1(b)): booleans, sample names, pet names, food amounts, pets lists.
- Scripted `input()` (rule 1): the seven named items plus `u04 exercises-14` and `u04 u04-ex08`, whose core tasks read `input()`.
- Asserts that cannot all hold after one student program (two phases or two bars asserted together): `u04 18831267`, `u07 d8fc52e2`, `u07 exercise-14-linear-search`, `u08 2d315b39`.
- Asserts that re-check given data, not the student's work: `u07 0ffe49bf`, `cp03 question-1` (to self-check), `u08 5703c375` (to expected-output).
- Names given only in the `**Real version:**` panel: `u05 exercise-3/7/9`, `u10 7b04a673`.
- Single-token expected-output (rule 4): see below.
- Output-only checks whose core result is a file: `u09 0cc7f084`, `u09 e2692eb8`.

## Rule 4: single-token expected-output items

| item | token | decision |
|---|---|---|
| unit-06-secret-codes/exercises/b8560ccca999 | 3 | self-check: the 3 is a worked-example illustration; nothing tells the program what to print |
| unit-06-secret-codes/exercises/3e97d2c30aa2 | 3 | self-check: 'Scan a message' leaves the input open |
| unit-06-secret-codes/exercises/aa3b6e2e8b04 | 6 | self-check: 'a word' leaves the input open |
| checkpoint-03-data-wrangler/checkpoint/question-8 | 0 | kept: body says 'a missing "fig" price becomes `0`, and print that price' |
| unit-10-pet-simulator/exercises/c8e092dc | 3 | self-check: the 3 occurs only in the heading 'Exercise 3' |
| unit-10-pet-simulator/exercises/3052f533 | 10 | kept: the body's `while buddy.happiness < 10:` with `play` adding 1 ends at exactly 10, so the body fixes the answer |

The two non-numeric single-token outputs, `???` in `u08 da9cf3d6` and `u08 5703c375`, are the lookup defaults the bodies show (`.get(word, "???")`, `.get("fish", "???")`).

No item was retagged *to* `expected-output` against the tool's `output not fixed by the statement` verdict. `u08 5703c375` moved from asserts, and the tool reports its output as fixed by the statement.

## `answer_format` decisions

All are program output (`expected-output`, `predict`), so all stay `case: sensitive` (rule 3), with the derived hint. No hint misleads, so none is authored.

| item | kind | derived hint | decision |
|---|---|---|---|
| unit-01-story-machine/exercises/exercise-two | expected-output | one line | derived, case-sensitive |
| checkpoint-01-first-steps/checkpoint/checkpoint-03 | predict | one line | derived, case-sensitive |
| checkpoint-01-first-steps/checkpoint/checkpoint-07 | predict | one line | derived, case-sensitive |
| unit-03-turtle-art-studio/exercises/exercise-1 | expected-output | one line | derived, case-sensitive |
| unit-04-quiz-show/exercises/exercises-11 | predict | one line | derived, case-sensitive |
| unit-05-function-factory/exercises/exercise-5-heading | predict | several lines | derived, case-sensitive |
| unit-05-function-factory/exercises/exercise-11-heading | expected-output | several lines | derived, case-sensitive |
| checkpoint-02-loops-and-functions/checkpoint/question-1-heading | predict | several lines | derived, case-sensitive |
| checkpoint-02-loops-and-functions/checkpoint/question-5-heading | predict | several lines | derived, case-sensitive |
| checkpoint-02-loops-and-functions/checkpoint/question-6-heading | predict | one line | derived, case-sensitive |
| unit-08-word-wizard/exercises/da9cf3d6 | expected-output | one line | derived, case-sensitive |
| unit-08-word-wizard/exercises/5703c375 | expected-output | one line | derived, case-sensitive |
| checkpoint-03-data-wrangler/checkpoint/question-6 | expected-output | several lines | derived, case-sensitive |
| checkpoint-03-data-wrangler/checkpoint/question-8 | expected-output | a number | derived, case-sensitive |
| unit-09-save-point/exercises/3113af24 | expected-output | one line | derived, case-sensitive |
| unit-09-save-point/exercises/180acfe5 | expected-output | one line | derived, case-sensitive |
| unit-10-pet-simulator/exercises/3052f533 | expected-output | a number | derived, case-sensitive |
| checkpoint-04-year-one-finale/checkpoint/c400000e | expected-output | several lines | derived, case-sensitive |

No multi-token `answer` items exist in this book, so no lesson citations are needed.

## `whitespace: exact` items

None.

## Concept attributions and gap list

| lesson block | concepts | why |
|---|---|---|
| unit-01-story-machine/lesson/8a9940ed | error-messages | the broken `print("...)` error demo the lesson has students run and read from the bottom |
| unit-02-number-detective/lesson/u02-seed | random-module | `random.seed(1)` fixes the random module's sequence |
| unit-10-pet-simulator/lesson/d1c787cd | attributes, error-messages | the `buddy.hapiness` AttributeError demo: a misspelled attribute and its traceback |

Gap list: empty (0 unattributed lesson blocks, 0 unattributed items after this phase).

## Notes for part C

- Several unit-09 and checkpoint-04 asserts depend on a file that an earlier exercise in the same notebook writes: `savegame.txt`, `settings.txt` or `finale.txt`. They are `e5a7e9a1`, `25c296a7`, `exercise-14-linear-search`, `exercise-15-find-extreme`, `exercise-16-filter-into-list` and `c4000008`. The statements fix the expected values, but the runner must give these items the earlier exercises' file state.
- Turtle items carry `turtle: true`, and their turtle requirements are in `also_check`.

## Per-item lines

### unit-01-story-machine

- `unit-01-story-machine/exercises/exercise-one` — self-check — open-ended title and message; derived checklist matches
- `unit-01-story-machine/exercises/exercise-two` — expected-output — fix-the-quote starter fixes the one output line
- `unit-01-story-machine/exercises/exercise-three` — self-check — RETAG asserts->self-check: assert tests the solution's snack while the student chooses their own words (rule 1(b), plan example) [requirements x2]
- `unit-01-story-machine/exercises/exercise-four` — self-check — student's own story; derived checklist matches
- `unit-01-story-machine/exercises/exercise-five` — self-check — input() core; student's own message; derived checklist matches
- `unit-01-story-machine/exercises/exercise-six` — self-check — input() core; own story; derived checklist matches
- `unit-01-story-machine/exercises/exercise-seven` — self-check — name is the student's own; derived checklist split a sentence [requirements x3]
- `unit-01-story-machine/exercises/challenge-one` — self-check — own multi-paragraph story; derived checklist matches
- `unit-01-story-machine/exercises/challenge-two` — self-check — input() core; own emoji and title; derived checklist matches

### unit-02-number-detective

- `unit-02-number-detective/exercises/exercise-1` — self-check — unseeded random roll; derived checklist matches
- `unit-02-number-detective/exercises/exercise-2` — self-check — input() core (one guess); derived checklist matches
- `unit-02-number-detective/exercises/exercise-4` — self-check — two-player input() game; derived checklist opened with a parenthetical [requirements x4]
- `unit-02-number-detective/exercises/exercise-5` — self-check — input() debug (type 12); derived checklist keeps every instruction (its opening description is pinned by tests/test_site_answers.py)
- `unit-02-number-detective/exercises/exercise-6` — self-check — random secret and input() loop; derived checklist matches
- `unit-02-number-detective/exercises/exercise-7` — self-check — span, midpoint, even_or_odd, span_size, span_message are the solution's names (prose, not a rule-2 case); derived checklist dropped the signal and str(span) requirements [requirements x6]
- `unit-02-number-detective/exercises/exercise-8` — self-check — is_correct is named but verdict is the solution's own name, and the solution prints the Boolean twice, so neither asserts nor expected-output fits; derived checklist split a sentence [requirements x4]
- `unit-02-number-detective/exercises/exercise-3` — self-check — random secret, input() loop; derived checklist matches
- `unit-02-number-detective/exercises/challenge-1` — self-check — random secret, input() loop; derived checklist matches
- `unit-02-number-detective/exercises/challenge-2` — self-check — player-driven input() replies; derived checklist matches

### checkpoint-01-first-steps

- `checkpoint-01-first-steps/checkpoint/checkpoint-01` — asserts — rule 1(b): `clue_message` named, `clues_found = 4` fixed by the shown code [also_check x2]
- `checkpoint-01-first-steps/checkpoint/checkpoint-03` — predict — trace question with a printing program
- `checkpoint-01-first-steps/checkpoint/checkpoint-05` — self-check — RETAG asserts->self-check: scripted input() (rule 1 named case); derived checklist is the one-line task
- `checkpoint-01-first-steps/checkpoint/checkpoint-07` — predict — trace question with a printing program [also_check x1]
- `checkpoint-01-first-steps/checkpoint/checkpoint-09` — self-check — fill-the-blank condition in an input() loop; derived checklist matches
- `checkpoint-01-first-steps/checkpoint/checkpoint-11` — self-check — RETAG asserts->self-check: naming/comment question; asserted player_guess == 37 is not fixed by the task [requirements x4]
- `checkpoint-01-first-steps/checkpoint/checkpoint-13` — self-check — input() guess; derived checklist matches

### unit-03-turtle-art-studio

- `unit-03-turtle-art-studio/exercises/exercise-1` — expected-output — statement fixes the report line `4 sides of 80 steps`; turtle drawing listed in also_check [also_check x3]
- `unit-03-turtle-art-studio/exercises/exercise-2` — asserts — rule 1(b): `n = 7`, `angle`, `side_number` named and fixed [also_check x3]
- `unit-03-turtle-art-studio/exercises/exercise-3` — self-check — headless plan prints nothing; derived checklist opened with a description [requirements x3]
- `unit-03-turtle-art-studio/exercises/exercise-4` — self-check — trace table plus own labels; derived checklist matches
- `unit-03-turtle-art-studio/exercises/exercise-5` — self-check — flagship turtle build with own side_length; derived checklist missed the headless-cell tasks [requirements x6]
- `unit-03-turtle-art-studio/exercises/exercise-6` — asserts — rule 1(b): starter names and fixed repaired loop counts; labels named [also_check x2]
- `unit-03-turtle-art-studio/exercises/exercise-7` — self-check — own side length and color; derived checklist matches
- `unit-03-turtle-art-studio/exercises/exercise-8` — self-check — own side length and color; derived checklist matches
- `unit-03-turtle-art-studio/exercises/exercise-9` — self-check — turtle ring; derived checklist matches
- `unit-03-turtle-art-studio/exercises/exercise-10` — asserts — rule 1(b): `shape_count = 3`, `side_count = 5`, `stroke_number` named and fixed [also_check x2]
- `unit-03-turtle-art-studio/exercises/challenge-1` — self-check — own side_length, prediction and explanation; derived checklist opened with a description [requirements x4]
- `unit-03-turtle-art-studio/exercises/challenge-2` — self-check — paper plan with own colors; derived checklist matches

### unit-04-quiz-show

- `unit-04-quiz-show/exercises/exercises-01` — self-check — RETAG asserts->self-check: score == 2 depends on the student's chosen booleans (rule 1(b))
- `unit-04-quiz-show/exercises/exercises-03` — self-check — RETAG asserts->self-check: score == 3 depends on the student's chosen booleans (rule 1(b), brief example)
- `unit-04-quiz-show/exercises/exercises-05` — self-check — RETAG asserts->self-check: score == 4 depends on the student's chosen correct/category (rule 1(b))
- `unit-04-quiz-show/exercises/exercises-07` — self-check — input() sudden-death round; derived checklist dropped the break requirement [requirements x6]
- `unit-04-quiz-show/exercises/exercises-09` — self-check — input() repair; derived checklist opened with a description [requirements x4]
- `unit-04-quiz-show/exercises/exercises-11` — predict — trace-and-predict of a fixed starter
- `unit-04-quiz-show/exercises/18831267` — self-check — RETAG asserts->self-check: the two asserts (penalty True/score 2, penalty False) need different student-chosen booleans and cannot both hold [requirements x4]
- `unit-04-quiz-show/exercises/u04-ex08` — self-check — RETAG asserts->self-check: core task reads the answers with input(); asserts compare scripted answers
- `unit-04-quiz-show/exercises/u04-ex09` — self-check — RETAG asserts->self-check: q/strikes/score depend on the student's three chosen boolean results
- `unit-04-quiz-show/exercises/u04-ex10` — self-check — RETAG asserts->self-check: scripted input() (rule 1 named case)
- `unit-04-quiz-show/exercises/u04-ex11` — self-check — RETAG asserts->self-check: scripted input() (rule 1 named case)
- `unit-04-quiz-show/exercises/u04-count-correct-heading` — self-check — RETAG asserts->self-check: scripted input() (rule 1 named case)
- `unit-04-quiz-show/exercises/a62f9f478759` — self-check — counters are the solution's names; output format free; derived checklist matches
- `unit-04-quiz-show/exercises/80aad2bf4129` — self-check — total is prose ('running total'), output format free; derived checklist matches
- `unit-04-quiz-show/exercises/cf3b006732d4` — self-check — total is prose, output format free; derived checklist matches
- `unit-04-quiz-show/exercises/bb5c58d03be5` — self-check — streak count is prose, output format free; derived checklist matches
- `unit-04-quiz-show/exercises/05af34fed0e1` — self-check — own names, output format free; derived checklist matches
- `unit-04-quiz-show/exercises/1eb08ee31017` — self-check — own names, output format free; derived checklist matches
- `unit-04-quiz-show/exercises/840b5965e301` — self-check — input() sentinel homework; derived checklist matches
- `unit-04-quiz-show/exercises/exercises-14` — self-check — RETAG asserts->self-check: core task asks the player with input(); score == 8 compares the solution's stand-in answers
- `unit-04-quiz-show/exercises/exercises-16` — self-check — last_shown is the solution's name and the printed format is free; derived checklist included two notes [requirements x4]

### unit-05-function-factory

- `unit-05-function-factory/exercises/exercise-1-heading` — self-check — two sample names chosen by the student; derived checklist matches
- `unit-05-function-factory/exercises/exercise-2-heading` — self-check — own variable names; derived checklist opened with two descriptions [requirements x2]
- `unit-05-function-factory/exercises/exercise-3-heading` — self-check — RETAG asserts->self-check: double_message is named only in the Real version panel, not the core task; expected-output does not fit because the solution prints an extra explanation line [requirements x4]
- `unit-05-function-factory/exercises/exercise-4-heading` — self-check — outside variable and message are the student's own; derived checklist matches
- `unit-05-function-factory/exercises/exercise-5-heading` — predict — trace question with a printing program [also_check x3]
- `unit-05-function-factory/exercises/exercise-6-heading` — asserts — rule 1(b): `last_pen_size`, `side_moves` named, four stamps fixed [also_check x5]
- `unit-05-function-factory/exercises/exercise-8-heading` — self-check — caller's variable is the student's own; derived checklist opened with descriptions [requirements x3]
- `unit-05-function-factory/exercises/exercise-9-heading` — self-check — RETAG asserts->self-check: turn_angle(7) is portable (rule 1(a)) but final_message is named only in the Real version panel and its text is the student's own f-string [requirements x6]
- `unit-05-function-factory/exercises/exercise-10-heading` — asserts — rule 1(b): `stamps_drawn` named, 3 x 4 grid fixed [also_check x4]
- `unit-05-function-factory/exercises/exercise-11-heading` — expected-output — statement fixes both output lines (`20` and `10`) [also_check x2]
- `unit-05-function-factory/exercises/exercise-7-heading` — self-check — RETAG asserts->self-check: border_total is named only in the Real version panel; the printed 280 does not occur in the statement (single-token rule)
- `unit-05-function-factory/exercises/b7b2ccf7b701` — asserts — rule 1(a): calls the specified count_bonus_stamps(n) [also_check x1]
- `unit-05-function-factory/exercises/469f592aa1ac` — asserts — rule 1(a): calls the specified total_even_stamps(n) [also_check x1]
- `unit-05-function-factory/exercises/de1d576f18c6` — asserts — rule 1(a): calls the specified stamps_in_triangle(rows) [also_check x1]
- `unit-05-function-factory/exercises/0e7e3394dc87` — asserts — rule 1(a): calls the specified average_side(n) [also_check x1]
- `unit-05-function-factory/exercises/182cd68d5c0e` — asserts — rule 1(a): calls the specified stamps_that_fit / width_used [also_check x1]
- `unit-05-function-factory/exercises/1434564ae2ca` — asserts — rule 1(a): calls the specified stamps_to_pass / width_when_passed [also_check x1]
- `unit-05-function-factory/exercises/96e5c4adff6a` — asserts — rule 1(a): calls the specified stamps_to_reach(target) [also_check x1]
- `unit-05-function-factory/exercises/84b61ce63d9c` — asserts — rule 1(a): calls the specified count_jumbo_stamps(n, threshold) [also_check x1]
- `unit-05-function-factory/exercises/3b3a2099bdd9` — asserts — rule 1(a): calls the specified total_ribbon(n, start, growth) [also_check x1]
- `unit-05-function-factory/exercises/challenge-1-prompt` — self-check — own badge values; derived checklist matches
- `unit-05-function-factory/exercises/challenge-2-prompt` — self-check — written plan in a markdown fence; derived checklist matches

### checkpoint-02-loops-and-functions

- `checkpoint-02-loops-and-functions/checkpoint/question-1-heading` — predict — trace question with a printing program
- `checkpoint-02-loops-and-functions/checkpoint/question-2-heading` — self-check — names are only in the code fence and the single printed 10 does not occur in the statement; derived checklist included a description [requirements x3]
- `checkpoint-02-loops-and-functions/checkpoint/question-3-heading` — self-check — RETAG asserts->self-check: message == 'Hello, Maya!' depends on the student's sample name and greeting wording (rule 1(b))
- `checkpoint-02-loops-and-functions/checkpoint/question-4-heading` — self-check — explanation question; derived checklist opened with 'Read the two functions.' [requirements x3]
- `checkpoint-02-loops-and-functions/checkpoint/question-5-heading` — predict — trace question with a printing program [also_check x2]
- `checkpoint-02-loops-and-functions/checkpoint/question-6-heading` — predict — RETAG self-check->predict: a trace question ('Predict the one message that prints') whose fenced program prints one line; the tool's regex missed the wording [also_check x1]
- `checkpoint-02-loops-and-functions/checkpoint/question-7-heading` — self-check — turtle trace answered in words (shape name), no program output; derived checklist matches
- `checkpoint-02-loops-and-functions/checkpoint/question-8-heading` — self-check — sample booleans chosen by the student; derived checklist matches

### project-01-arcade-night

- `project-01-arcade-night/brief/milestone-1` — self-check — no matching solution section; derived checklist picked up a pattern comment and spotlight text [requirements x2]
- `project-01-arcade-night/brief/milestone-2` — self-check — no matching solution section; derived checklist included descriptions [requirements x3]
- `project-01-arcade-night/brief/milestone-3` — self-check — no matching solution section; derived checklist matches
- `project-01-arcade-night/brief/milestone-4` — self-check — solution has no code; derived checklist matches

### unit-06-secret-codes

- `unit-06-secret-codes/exercises/exercise-1-heading` — self-check — stored names are the student's own; the single printed word does not occur in the statement; derived checklist matches
- `unit-06-secret-codes/exercises/exercise-2-heading` — self-check — piece names and f-string wording are the student's own; derived checklist matches
- `unit-06-secret-codes/exercises/exercise-3-heading` — self-check — own names and message wording; derived checklist matches
- `unit-06-secret-codes/exercises/exercise-4-heading` — self-check — own names and message wording; derived checklist matches
- `unit-06-secret-codes/exercises/exercise-5-heading` — self-check — input() core; derived checklist matches
- `unit-06-secret-codes/exercises/exercise-6-heading` — self-check — input() core message; derived checklist matches
- `unit-06-secret-codes/exercises/exercise-7-heading` — self-check — traceback-reading debug with own names; derived checklist stopped before the second round [requirements x3]
- `unit-06-secret-codes/exercises/exercise-8-heading` — self-check — input() core; derived checklist matches
- `unit-06-secret-codes/exercises/exercise-9-heading` — self-check — input() core; derived checklist matches
- `unit-06-secret-codes/exercises/exercise-10-heading` — self-check — stored output names and f-strings are the student's own; derived checklist matches
- `unit-06-secret-codes/exercises/exercise-11-heading` — self-check — stored result name is the student's own; derived checklist dropped the call and output [requirements x6]
- `unit-06-secret-codes/exercises/exercise-12-heading` — asserts — rule 1(b): `vowel_count` named, message fixed [also_check x2]
- `unit-06-secret-codes/exercises/exercise-13-heading` — asserts — rule 1(b): `coded_message` named, message fixed [also_check x2]
- `unit-06-secret-codes/exercises/exercise-14-heading` — asserts — rule 1(b): `found_position` named, target fixed [also_check x2]
- `unit-06-secret-codes/exercises/b8560ccca999` — self-check — RETAG expected-output->self-check (rule 4): the 3 is the worked example's illustration; the statement never fixes what the program prints, and the assert names the solution's own result
- `unit-06-secret-codes/exercises/d6c123b4f1b3` — self-check — counter names and printed format are the student's own; derived checklist matches
- `unit-06-secret-codes/exercises/3e97d2c30aa2` — self-check — RETAG expected-output->self-check (rule 4): 'Scan a message' leaves the message open; xyzapple -> 3 only illustrates
- `unit-06-secret-codes/exercises/d16a0c4336ee` — self-check — function name is not given by the statement; derived checklist matches
- `unit-06-secret-codes/exercises/13516621cf0e` — self-check — function name is not given by the statement; derived checklist matches
- `unit-06-secret-codes/exercises/aa3b6e2e8b04` — self-check — RETAG expected-output->self-check (rule 4): 'a word' is not fixed; abc -> 6 only illustrates
- `unit-06-secret-codes/exercises/74e3a708d4e6` — self-check — own names and report format; derived checklist matches
- `unit-06-secret-codes/exercises/4e7509aba504` — self-check — own names and report format; derived checklist matches
- `unit-06-secret-codes/exercises/challenge-1-prompt` — self-check — own message and keyword; derived checklist matches
- `unit-06-secret-codes/exercises/challenge-2-prompt` — self-check — own sample message and shift; derived checklist matches

### unit-07-high-score-hall

- `unit-07-high-score-hall/exercises/34bc0cc9` — asserts — rule 1(b): `scores`, `new_score` named and fixed [also_check x2]
- `unit-07-high-score-hall/exercises/a1d39a77` — self-check — midpoint/champion/rookie are prose names; derived checklist matches
- `unit-07-high-score-hall/exercises/0ffe49bf` — self-check — RETAG asserts->self-check: the asserts only re-check the given list, not the fix or the loop output; the first cell errors on purpose, so a whole-program output check does not fit [requirements x4]
- `unit-07-high-score-hall/exercises/5c20b19f` — self-check — RETAG asserts->self-check: scripted input() (rule 1 named case)
- `unit-07-high-score-hall/exercises/0f3f7fcc` — asserts — rule 1(a): calls the specified board_line(place, score) [also_check x1]
- `unit-07-high-score-hall/exercises/dfc665d7` — self-check — RETAG asserts->self-check: scripted input() (rule 1 named case)
- `unit-07-high-score-hall/exercises/22ce315f` — self-check — input() core; derived checklist matches
- `unit-07-high-score-hall/exercises/d8fc52e2` — self-check — RETAG asserts->self-check: `best is None` and `best is scores` describe the two phases and cannot both hold after the student's code [requirements x3]
- `unit-07-high-score-hall/exercises/2af960b7` — self-check — average is not stored under a named variable; derived checklist matches
- `unit-07-high-score-hall/exercises/f6304b22` — self-check — best is prose ('for the best score'); derived checklist included a retrieval question [requirements x5]
- `unit-07-high-score-hall/exercises/54467865` — self-check — tiers is the solution's list; derived checklist included spotlight text [requirements x4]
- `unit-07-high-score-hall/exercises/b770a983` — asserts — rule 1(b): `clean_winners` named, raw names fixed [also_check x2]
- `unit-07-high-score-hall/exercises/1b327946` — self-check — champion is prose ('for the champion'); derived checklist included spotlight text [requirements x4]
- `unit-07-high-score-hall/exercises/exercise-14-linear-search` — self-check — RETAG asserts->self-check: the asserts (1050 and 'not found') are for two different bars and cannot both hold [requirements x4]
- `unit-07-high-score-hall/exercises/exercise-15-find-extreme` — asserts — rule 1(b): `best_name`, `best_score` named, lists fixed [also_check x2]
- `unit-07-high-score-hall/exercises/exercise-16-filter-into-list` — asserts — rule 1(b): `qualifying_scores` named, list and threshold fixed [also_check x2]
- `unit-07-high-score-hall/exercises/c0f4354dcb88` — asserts — rule 1(b): `rookie_name`, `rookie_score` named, lists fixed [also_check x1]
- `unit-07-high-score-hall/exercises/a293634ac2fe` — self-check — RETAG asserts->self-check: best/worst appear only in the worked example; the task says 'track both the highest and lowest' without naming them, so a correct program may use other names; derived checklist matches
- `unit-07-high-score-hall/exercises/db46d99c1316` — self-check — own names; derived checklist matches
- `unit-07-high-score-hall/exercises/fab4a9bad828` — asserts — rule 1(b): the task says to 'set the place' and shows it as `place = 3`; inputs fixed in the starter
- `unit-07-high-score-hall/exercises/e9416bdf353e` — self-check — own names; derived checklist matches
- `unit-07-high-score-hall/exercises/c0fd1808472b` — self-check — own names; derived checklist matches
- `unit-07-high-score-hall/exercises/cc86d261` — asserts — rule 1(b): `scores` named and fixed [also_check x1]
- `unit-07-high-score-hall/exercises/457f59a6` — asserts — rule 1(b): `scores`, `second_scores` named and fixed [also_check x3]

### unit-08-word-wizard

- `unit-08-word-wizard/exercises/105432ac` — asserts — rule 1(b): `translations` named and fixed [also_check x1]
- `unit-08-word-wizard/exercises/da9cf3d6` — expected-output — fixed word and lookup default fix the printed `???`
- `unit-08-word-wizard/exercises/2d315b39` — self-check — RETAG asserts->self-check: `known is True` and `known is False` are the two phases and cannot both hold; the f-string wording is the student's own [requirements x4]
- `unit-08-word-wizard/exercises/366b84ad` — asserts — rule 1(b): `translations`, `new_words` named and fixed [also_check x3]
- `unit-08-word-wizard/exercises/65ac3053` — asserts — rule 1(b): `counts`, `cats_lead` named and fixed [also_check x2]
- `unit-08-word-wizard/exercises/b707e4b1` — self-check — clean word name and f-string are the student's own; derived checklist matches
- `unit-08-word-wizard/exercises/1b6d5913` — self-check — own f-string wording; derived checklist matches
- `unit-08-word-wizard/exercises/5703c375` — expected-output — RETAG asserts->expected-output: the assert re-checks a literal lookup and passes without the student's result; the fixed lookup prints `???`, which the statement shows [also_check x1]
- `unit-08-word-wizard/exercises/8f10cb43` — self-check — champion_checks is the solution's list; derived checklist matches
- `unit-08-word-wizard/exercises/f19523bc` — asserts — rule 1(b): `labels`, `visits` named and fixed [also_check x2]
- `unit-08-word-wizard/exercises/fb534bb7` — asserts — rule 1(b): `visited_words`, `visited_count` named and fixed [also_check x2]
- `unit-08-word-wizard/exercises/72e56d51` — self-check — owls_lead is the solution's name; derived checklist included spotlight text [requirements x5]
- `unit-08-word-wizard/exercises/762d0c80` — self-check — new_best_checks is the solution's list; derived checklist included spotlight text [requirements x5]
- `unit-08-word-wizard/exercises/c7c41c5a` — asserts — rule 1(a)+(b): calls the specified translate(); `translated_words` named [also_check x1]
- `unit-08-word-wizard/exercises/4d735639` — asserts — rule 1(b): `english_word` named, phrasebook and target fixed [also_check x1]
- `unit-08-word-wizard/exercises/exercise-16-filter-into-list` — asserts — rule 1(b): `long_words` named, list fixed [also_check x2]
- `unit-08-word-wizard/exercises/a29bfcb25864` — self-check — total is the solution's name and the printed format is free; derived checklist matches
- `unit-08-word-wizard/exercises/2a2bf0043516` — asserts — rule 1(b): `rarest_word`, `rarest_count` named, counts fixed [also_check x1]
- `unit-08-word-wizard/exercises/146ae9190dda` — self-check — known/unknown are parenthetical labels, not instructed names; derived checklist matches
- `unit-08-word-wizard/exercises/6974b3ca91bb` — self-check — own names; derived checklist matches
- `unit-08-word-wizard/exercises/931175eff090` — self-check — own names; derived checklist matches
- `unit-08-word-wizard/exercises/aef2318b` — asserts — rule 1(b): `translations` named and fixed [also_check x2]
- `unit-08-word-wizard/exercises/challenge-2-flip-prompt` — asserts — rule 1(b): `spanish_to_english` named, source fixed [also_check x1]

### checkpoint-03-data-wrangler

- `checkpoint-03-data-wrangler/checkpoint/question-1` — self-check — RETAG asserts->self-check: the assert re-checks the given word, not the student's f-string, whose separators are free
- `checkpoint-03-data-wrangler/checkpoint/question-2` — asserts — rule 1(b): `cleaned` named and fixed [also_check x1]
- `checkpoint-03-data-wrangler/checkpoint/question-3` — asserts — rule 1(b): `scores` named and fixed [also_check x1]
- `checkpoint-03-data-wrangler/checkpoint/question-4` — asserts — rule 1(b): `total` named, scores fixed [also_check x3]
- `checkpoint-03-data-wrangler/checkpoint/question-5` — asserts — rule 1(b): `scores` named and fixed [also_check x1]
- `checkpoint-03-data-wrangler/checkpoint/question-6` — expected-output — every printed line is fixed by the statement
- `checkpoint-03-data-wrangler/checkpoint/question-7` — asserts — rule 1(b): `counts` named, words fixed [also_check x1]
- `checkpoint-03-data-wrangler/checkpoint/question-8` — expected-output — single token `0` confirmed by the body: 'a missing "fig" price becomes `0`, and print that price' [also_check x1]

### unit-09-save-point

- `unit-09-save-point/exercises/0cc7f084` — self-check — RETAG expected-output->self-check: the core result is the file contents; the confirmation line alone would pass without writing the file
- `unit-09-save-point/exercises/8e2e922b` — self-check — reads the file from Exercise 1; derived checklist included a description [requirements x3]
- `unit-09-save-point/exercises/7241e26c` — self-check — reads the file from Exercise 1; derived checklist matches
- `unit-09-save-point/exercises/e2692eb8` — self-check — RETAG expected-output->self-check: the core result is the file contents; the confirmation line alone would pass without writing the file
- `unit-09-save-point/exercises/36533a17` — self-check — reads the settings file; derived checklist split the expected lines [requirements x6]
- `unit-09-save-point/exercises/3113af24` — expected-output — statement fixes the printed loaded list (a save-load round trip) [also_check x2]
- `unit-09-save-point/exercises/7b137fa5` — self-check — depends on the Exercise 6 helpers and file; derived checklist matches
- `unit-09-save-point/exercises/7eb48e53` — asserts — rule 1(b): `dragon_save` named, text fixed [also_check x1]
- `unit-09-save-point/exercises/96238996` — asserts — rule 1(b): `first_save`, `second_save` named, list fixed [also_check x2]
- `unit-09-save-point/exercises/180acfe5` — expected-output — statement fixes the printed line `Mina can resume forest.` [also_check x2]
- `unit-09-save-point/exercises/4b1cd37e` — self-check — depends on the file from earlier exercises; derived checklist matches
- `unit-09-save-point/exercises/e5a7e9a1` — asserts — rule 1(b): `loaded` named; the file state from earlier exercises fixes it (statement shows the list) [also_check x2]
- `unit-09-save-point/exercises/25c296a7` — asserts — rule 1(b): `total` named; earlier file state fixes it (statement shows 4925) [also_check x2]
- `unit-09-save-point/exercises/exercise-14-linear-search` — asserts — rule 1(b): `found_name` named; settings file fixes it (statement shows Mina) [also_check x2]
- `unit-09-save-point/exercises/exercise-15-find-extreme` — asserts — rule 1(b): `best_score` named; file fixes it (statement shows 1350) [also_check x1]
- `unit-09-save-point/exercises/exercise-16-filter-into-list` — asserts — rule 1(b): `high_scores` named; file and threshold fix it [also_check x2]
- `unit-09-save-point/exercises/9a1700000001` — self-check — count name and report format are the student's own; derived checklist matches
- `unit-09-save-point/exercises/9a1800000001` — self-check — own names and report format; derived checklist matches
- `unit-09-save-point/exercises/9a1900000001` — asserts — rule 1(b): `lowest` named ('Seed your `lowest` variable'), list fixed [also_check x1]
- `unit-09-save-point/exercises/9a2000000001` — self-check — position counter name is prose; derived checklist matches
- `unit-09-save-point/exercises/9a2100000001` — self-check — own names; derived checklist matches
- `unit-09-save-point/exercises/9a2200000001` — self-check — own names; derived checklist matches
- `unit-09-save-point/exercises/9a2300000001` — self-check — own names; derived checklist matches
- `unit-09-save-point/exercises/exercise-16-highest-saved-score` — self-check — depends on the file; own names; derived checklist matches
- `unit-09-save-point/exercises/exercise-17-add-new-high` — self-check — depends on the file and an earlier helper; derived checklist matches

### unit-10-pet-simulator

- `unit-10-pet-simulator/exercises/4ef1ecca` — asserts — rule 1(b): `buddy` named, class fixed [also_check x1]
- `unit-10-pet-simulator/exercises/02e5b720` — self-check — pet variables and names are the student's own; derived checklist matches
- `unit-10-pet-simulator/exercises/c8e092dc` — self-check — RETAG expected-output->self-check (rule 4): the canonical 3 occurs only in the heading 'Exercise 3'; the body never states it, and new_hunger is the solution's own name
- `unit-10-pet-simulator/exercises/69aa5fc9` — self-check — status line wording and variable are the student's own; derived checklist matches
- `unit-10-pet-simulator/exercises/7067fd3f` — self-check — RETAG asserts->self-check: pets[0].name == 'Ivy' tests the student's chosen pet names
- `unit-10-pet-simulator/exercises/23283984` — self-check — RETAG expected-output->self-check: which meal and treat to feed is the student's choice, so Buddy's hunger is not fixed
- `unit-10-pet-simulator/exercises/c01f80c7` — self-check — pet variable is the student's own; derived checklist matches
- `unit-10-pet-simulator/exercises/0162f536` — asserts — rule 1(b): `buddy` bound by the starter; the unfixed typo raises, the fix passes [also_check x2]
- `unit-10-pet-simulator/exercises/29dbfcff` — self-check — RETAG asserts->self-check: hunger 3 depends on the student's own food dictionary
- `unit-10-pet-simulator/exercises/49e4da55` — self-check — own snack dictionary; derived checklist matches
- `unit-10-pet-simulator/exercises/4871eefe` — self-check — own pet names; derived checklist matches
- `unit-10-pet-simulator/exercises/8968232c` — self-check — buddy and the status line are the student's own; derived checklist matches
- `unit-10-pet-simulator/exercises/c368d34e` — self-check — RETAG asserts->self-check: the pets list ('several pets') is the student's own [requirements x5]
- `unit-10-pet-simulator/exercises/3052f533` — expected-output — single token `10` confirmed by the body: `while buddy.happiness < 10:` with play adding 1 ends at exactly 10, so the bound fixes the printed answer [also_check x1]
- `unit-10-pet-simulator/exercises/exercise-15-filter-into-list` — asserts — rule 1(b): `pets`, `happy_pets`, `happiness_threshold` named and fixed [also_check x2]
- `unit-10-pet-simulator/exercises/a160c0de0001` — self-check — count name and report are the student's own; derived checklist matches
- `unit-10-pet-simulator/exercises/a170c0de0001` — self-check — 'a total' is prose; derived checklist matches
- `unit-10-pet-simulator/exercises/a180c0de0001` — asserts — rule 1(b): `found` flag named, pets fixed [also_check x1]
- `unit-10-pet-simulator/exercises/a190c0de0001` — self-check — new list name is the student's own; derived checklist matches
- `unit-10-pet-simulator/exercises/a200c0de0001` — self-check — tracker names are the student's own; derived checklist matches
- `unit-10-pet-simulator/exercises/a210c0de0001` — asserts — rule 1(b): `counts` named, moods fixed [also_check x1]
- `unit-10-pet-simulator/exercises/a220c0de0001` — self-check — pet variable and counter are the student's own; derived checklist stopped before the break and report [requirements x6]
- `unit-10-pet-simulator/exercises/a230c0de0001` — self-check — pet variable and counter are the student's own; derived checklist stopped before the report [requirements x5]
- `unit-10-pet-simulator/exercises/a240c0de0001` — self-check — result list name is the student's own; derived checklist matches
- `unit-10-pet-simulator/exercises/7b04a673` — self-check — RETAG asserts->self-check: `pets` is named only in the Real version panel and len(pets) >= 3 does not check show_trick
- `unit-10-pet-simulator/exercises/4dfdb434` — self-check — RETAG asserts->self-check: pet names and foods are the student's own

### checkpoint-04-year-one-finale

- `checkpoint-04-year-one-finale/checkpoint/c4000002` — asserts — rule 1(b): `hero` named and fixed [also_check x1]
- `checkpoint-04-year-one-finale/checkpoint/c4000004` — self-check — new_health is the solution's name; the single printed 13 does not occur in the statement; derived checklist matches
- `checkpoint-04-year-one-finale/checkpoint/c4000006` — self-check — writes a file and prints nothing; derived checklist matches
- `checkpoint-04-year-one-finale/checkpoint/c4000008` — asserts — rule 1(b): `loaded` named; the Question 3 file fixes it [also_check x1]
- `checkpoint-04-year-one-finale/checkpoint/c400000a` — asserts — rule 1(b): `loaded` named; the loaded list fixes it [also_check x2]
- `checkpoint-04-year-one-finale/checkpoint/c400000c` — self-check — printed format and lines list are the student's own; derived checklist matches
- `checkpoint-04-year-one-finale/checkpoint/c400000e` — expected-output — every printed line is fixed by the statement
- `checkpoint-04-year-one-finale/checkpoint/c4000010` — self-check — the printed default is the student's own; derived checklist opened with a description [requirements x2]

### project-02-grand-adventure

- `project-02-grand-adventure/brief/milestone-1` — self-check — RETAG asserts->self-check: scripted input() (rule 1 named case) [requirements x5]
- `project-02-grand-adventure/brief/milestone-2` — self-check — own rooms; derived checklist opened with a description [requirements x4]
- `project-02-grand-adventure/brief/milestone-3` — self-check — input() exploration loop; derived checklist opened with a description [requirements x4]
- `project-02-grand-adventure/brief/milestone-4` — self-check — depends on the playthrough's hero; derived checklist opened with a description [requirements x3]
- `project-02-grand-adventure/brief/milestone-5` — self-check — whole-program playthrough with input(); derived checklist matches
