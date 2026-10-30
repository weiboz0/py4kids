# Teacher notes — Capstone: Your competition agent (`project-14-competition-agent`)

The capstone closes the book.
Each student takes one file, the **incumbent** (their own race-day file from Unit 13, or `agents/unit-13.py`), makes **one choice of their own** by Unit 13's protocol, tests it fairly, and then shows what every stage of the submitted file bought.
It introduces no new concepts and uses no borrowed tools: every call in the brief was taught in Units 1–13.

**The thesis is the evidence, not the time.**
The reference's own worked choice (`TARGET_SPEED` 45 → 50.0) passed training and validation and then **failed its pre-registered test**: one crash in 24 cars it had never met.
So the reference submits the incumbent, `agents/unit-13.py`.
Students who find that their faster file is not the one they submit have done the project right; reward it.

Every number below is a racekit model number on `monza-like`, on `carla_like(noise=True)`, 3 laps, timing off (the probe record of plan `roar-014`):

| row | what changed | median / spread (s) | time bought (s) | Unit 1's rule | max error (m) |
|---|---|---|---|---|---|
| S0 | the bar: `starter.py` at `TARGET_SPEED` 14 | 1203.55 / 0.70 | — | — | 0.706 (c) |
| S1 | Unit 4: PID steering, flat 14 m/s | 1219.75 / 0.60 | **−16.20** | False | 0.434 (c) |
| S2a | Unit 5: pursuit, same 14 m/s | 1219.90 / 0.55 | −0.15 | False | 0.429 (c) |
| S2b | pursuit at 15 m/s (PID at 15 crashes) | 1138.85 / 0.45 | 81.05 | True | 1.042 (c) |
| S3 | Unit 6: the curvature cap, top 32.5 m/s | 617.05 / 0.15 | 521.80 | True | 0.753 (c) |
| S4 | Unit 7: the speed profile, top 45 | 514.95 / 0.20 | 102.10 | True | 1.575 (c) |
| S5 | Unit 8: the measured grip | 510.20 / 0.15 | 4.75 | True | 1.734 (c) |
| S6 | Unit 9: the line | 482.00 / 0.10 | 28.20 | True | 1.529 |
| S7 | Unit 10: MPC | 482.00 / 0.05 | 0.00 | False | 0.976 |
| S8 | Unit 11: the fallback | 482.00 / 0.05 | 0.00 | False | 0.976 |
| S9 | Unit 13: the re-tune = `unit-13.py`, **submitted** | 468.55 / 0.10 | 13.45 | True | 1.009 |
| S10 | the choice, `TARGET_SPEED` 50.0, **not submitted** (test 23/24) | 447.90 / 0.20 | 20.65 | True | 1.141 |

(c): from the centreline.
The gate: `unit-13.py` beats the bar by 735.00 s, both clean on seeds 0–4 at 0 collisions.

## Goals

By the end of the capstone students can:

- **Set a fair bar.** Race the starter on the grip car and see it crash-loop, although Unit 1 measured the same file clean on the kinematic car (the car changed, not the file); make it clean with its own one knob.
- **Make one choice and test it fairly.** Tune one knob by Unit 13's protocol (crash-aware objective on training cars, whole ticks, edge and margin), judge it on validation cars, freeze it, write the rule down, race their own test cars 120–143 **once**, and submit the candidate only if it passes.
- **Ablate.** Build the submitted file up stage by stage on five seeds: median, spread, time bought, Unit 1's verdict; and cross-check with a leave-one-out.
- **Read an ablation honestly.** A stage can cost time (S1); a stage can buy no time but buy margin (MPC, the fallback); stages are not additive (the grip buys 4.75 s in the build-up and 17.70 s when left out).
- **Qualify and report.** The submitted file against the bar and against Unit 7's agent; `check_submission` on `monza-like`; an engineering report that a reviewer could check.

## Pacing

Plan for **three 60–90 min sittings** plus racing at home (about 175 races, about 24 CPU-minutes serial; the brief marks which cells can run while students write).

1. **Sitting 1: the bar and the choice.**
   - Hook: race the starter capped at 120 s and watch it crash; ask why Unit 1's clean starter crashes now.
   - Milestone 1 (the bar), then start Milestone 2: pick the knob, run the objective races.
   - Homework: finish the search; validation cars.
2. **Sitting 2: freeze, test, build up.**
   - Before anyone races a test car, each student reads their pre-registration aloud to a partner: the frozen file and the rule.
   - The test (24 races); the decision.
   - Milestone 3: the build-up and the plot; the leave-one-out at home.
3. **Sitting 3: qualify and report.**
   - Milestone 4, then the report; pairs swap reports and check one number each against the other's notebook.

## Common mistakes

- **An ablation with one seed.** A 0.15 s "gain" from one race is noise; the table needs spreads and Unit 1's rule.
- **Reading 0.00 s as "MPC is useless".** MPC and the fallback buy margin (line error 1.53 → 0.98 m; Unit 13's held-out cars, where pursuit is clean on 13 of 24), which a time-only table cannot show.
- **Additive thinking.** Adding up the "time bought" column does not predict what removing a stage costs; the leave-one-out shows it.
- **Hiding the order.** The ablation's order is a choice; the report must state it.
- **Tuning on test cars.** Cars 120–143 test **one** frozen candidate, once; a second knob's evidence stops at validation. A student who re-runs Milestone 2 after racing them has spent them (say so in their report; the solutions never race them).
- **A pre-registration that names no rule.** "I will race the test cars" is not a pre-registration; "I submit the candidate only if it is clean on all 24" is. (The plan behind this capstone made exactly this mistake once and recorded it.)
- **Netting a crash into an expected time across different cars.** A test crash and a nominal gain are two facts; report them apart.
- **Ablating the wrong file.** The ablation and the qualification are of the **submitted** file; a rejected candidate is the ablation's last row, marked.
- **Saving the candidate inside the repository.** The repository is public; `candidate.py`, the records and the report live in the student's own `roar-runs` folder, never in a commit.
- **Racing the starter without a long enough cap.** The bar's races take about 1200 s; a 900 s cap reports a crash that did not happen.

## Discussion prompts

- Unit 1 measured the starter clean. Why does the same file crash here, and what does that say about every racekit number in the book?
- PID costs 16 s at the bar's speed and pursuit buys nothing at the same speed. What did each buy instead?
- MPC buys 0.00 s on the nominal car. Would you remove it? What evidence would change your mind?
- The reference's choice was 20.65 s faster and crashed once in 24 new cars. Would you race it on race day? Who decides, and by what rule?
- The CARLA winner took 319.65 s; racekit's best clean file takes 468.55 s on its model of the track. What can racekit tell you about CARLA, and what can it not?

## Differentiation

- **Support:**
  - give Milestone 1's grid results and have students race only the chosen bar on five seeds;
  - let students ablate on seeds 0–2 (the brief allows it, stated in the report);
  - pre-fill the ablation table's columns and have students compute time bought and Unit 1's verdict.
- **Core:** the five milestones as written.
- **Stretch:**
  - a second leave-one-out ordering, or the build-up in a different order, and how much the "time bought" moves;
  - a sweep of the choice's knob on validation cars only, showing where the margin rule lands;
  - the CARLA plan: which three racekit findings they would re-check first on CARLA, and how.

## Rubric

Assess each student's **own** file and choice. A student whose choice failed its test and who submitted the incumbent can earn full credit; a student who submitted a candidate that failed its own rule cannot.

**Meets the brief (full credit):**
- The bar: the starter's crash shown; the knob grid; the bar on five seeds, clean.
- The choice: the knob justified; the objective races with sums in whole ticks; the edge and the margin; validation N/N; the pre-registration written **before** the test; the test raced once; the submitted file decided by the stated rule.
- The ablation of the submitted file on five seeds (or three, stated): median, spread, time bought and Unit 1's verdict for every row; the candidate as a marked last row; a plot; the leave-one-out with verdicts.
- Qualify: Unit 1's rule against the bar at 0 collisions; the comparison with `unit-07.py`; `check_submission` PASS on `monza-like`; the checklist.
- The report: every claim cites a number from the student's own notebook; the stage that cost time; what MPC and the fallback buy; non-additivity; the order; which file is submitted and why; the CARLA caveat.

**Developing:** a fair bar and an ablation with spreads, but a choice without a pre-registered test, or a report that ranks stages by time alone. Name the missing piece as the next step.

**Milestone by milestone, "what done looks like":**
1. **The bar:** "same file, different car"; a clean bar on five seeds (the reference: `TARGET_SPEED` 14, 1203.55 s).
2. **The choice:** a table of settings with sums in ticks; an edge; a margin; validation; a written rule; one test; a decision that follows the rule.
3. **Build it up:** rows S0 onward; a negative or zero row read correctly; the leave-one-out disagreeing with the build-up somewhere, and said so.
4. **Qualify:** the gate stated as numbers (the reference: 735.00 s, Unit 1's rule True).
5. **Report:** a reviewer can check every number.

**Re-teach signal:** if a third of the class or more submits a candidate that failed its own test, or reads a single race as a result, revisit Unit 1's rule and Unit 13's car sets before the end-of-course review.

## Provenance

Original content.
All numbers are measured on racekit, the book's own simulator, with seeded cars and races; none is a CARLA result.
