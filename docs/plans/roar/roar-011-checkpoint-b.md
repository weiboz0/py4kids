# Plan roar-011 — Checkpoint B: a full agent on a track and a car it has never met

**Design:** `docs/designs/013-roar-book.md` **v4.9** (§4.3 the seeded tracks, §6 CP-B, §7.1).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**Base:** branches from `main` after `roar-010` merges (#165, f62130c).

## Scope
- Checkpoint B `roar/checkpoints/checkpoint-02-part-2/`: `checkpoint.ipynb` (the brief and the questions, no
  solutions, no outputs), `solutions.ipynb`, `teacher-notes.md`, `manifest.yaml`.
  It is **strict**: no borrowed tools, every task draws only on Units 1–11 concepts, and it introduces nothing.
- **Generator:** one more seeded variant, `test-circuit-seed2027`, the **race-day track** (the seed was fixed
  before it was probed, as 2026 was for Checkpoint A). `load_track` already loads it by name; `racekit` does not
  change.
- Reference submission `agents/checkpoint-b.py`: `agents/unit-11.py` with the race-day track's line
  (`LINE_CONTROL`, solved by Unit 9's method), its measured grip (`MU_G`, Unit 8's probes) and
  `MU_FRACTION = 0.48` (the margin rule on the track × car family, below), and a header comment saying why.
- A routed premise test for the gates; registry, syllabus and design entries.

## The idea, and why the checkpoint has one
Design §6: "a full agent under parameter uncertainty; completes hidden perturbed races, timed".
Unit 11 left two findings open: a margin bought on one track did not carry to another (`test-circuit-seed2026`),
and the fraction it shipped was the one with the shortest **expected race time** on its training family.
Checkpoint B puts both to the test on a track and on cars the student has never raced:
- **The race-day track** `test-circuit-seed2027`: the student measures it (Unit 8's grip probes, with the
  nominal carla-like car) and solves its line (Unit 9). Racing it is allowed once, on race day.
- **The race-day cars** are five members of the perturbed family whose factors are **sealed**: `perturb=k` for
  k = 1000–1004 (race seed k mod 5). The brief forbids calling `perturbation_factors` on them or racing them before
  race day; the solutions never do either.
- **Tuning** uses the track × car family: the five training tracks (`test-circuit`, `-seed1` … `-seed4`, each with
  its own line and measured grip) × the training cars (k = 0–23).

The probe shows the two Unit 11 rules **disagree here**, and race day settles it:
- **Expected race time** over the 120 family races is lowest at **0.54** (279.95 s; every race finishes, thanks to
  the fallback), as in Unit 11.
- **The clean rule and the margin rule** (Units 7 and 11): 0.52 is not clean on the family (`test-circuit-seed2`
  crashes two cars), 0.50 is clean on all 120, so the margin rule gives **0.48**.
- **Race day:** at 0.48 all five hidden cars are clean (median 283.90 s); at 0.54 four of five crash once (each
  finishes, after the fallback, in 384.65–477.00 s; mean 382.82 s); Unit 10's agent at 0.54, with no fallback,
  never finishes three of the five.
The lesson: the expected-time rule trusts the family's crash rate, and a new track is not in the family.
The margin is the insurance against what the family did not show; the fallback turns a crash into a slow finish
instead of a DNF. Both are Unit 11 ideas; the checkpoint makes the student choose between them before the race and
justify the choice with evidence. Graded on the evidence and the reasoning; the race is pass/fail.

## Probe evidence (`p1`–`p5`, scratchpad `cpb/`; `carla_like(noise=True, perturb=k)`, MPC budget off (`MPC_BUDGET_MS = None`) in every probe, 700 s cap)
- **`p1` the track** (`gen_tracks.seeded_track(2027)`): length 2631.2 m, 1316 waypoints, half-width 5.41–6.56 m,
  tightest radius 19.3 m, continuous curvature, 0 self-intersections; builds in 0.01 s. Its smoothest line
  (QR + `lsq_linear`, Unit 9) solves in 0.1 s (131 control values).
- **`p2` the grip probes** (Unit 8's rule: `agents/unit-07.py`, A_LAT 3.5, one section's knob at 3.5, one lap, race
  seed 0, 300 s cap, the 99th percentile of |a|): on `test-circuit-seed2026` the rule reproduces the pinned
  `MEASURED_MU_G` exactly. On `test-circuit-seed2027`: **(9.10, 9.55, 7.79, 9.35, 9.00, 7.76)** m/s².
  Section 0's probe finished the lap clean (109.40 s, 0 collisions): it never slid, so 9.10 is a **lower bound**,
  the case Unit 8 taught (`monza-like`'s section 0), and the planner uses it as measured.
- **`p3` the family sweep** (`agents/unit-11.py`, each track's line and measured grip, `test-circuit` as shipped;
  24 training cars × 5 training tracks, race seed k mod 5; 480 races, 2,907 CPU-s, 427 s on 8 workers):

  | fraction | clean / 120 | not clean | mean (all finish) | median |
  |---|---|---|---|---|
  | 0.56 | 110 | `test-circuit` cars 8, 9; `-seed2` cars 1, 8, 9, 10, 13, 16, 17, 20 | 286.95 | 273.95 |
  | 0.54 | 118 | `-seed2` cars 13, 16 | **279.95** | 276.30 |
  | 0.52 | 118 | `-seed2` cars 9, 16 | 282.57 | 278.90 |
  | 0.50 | **120** | — | 282.21 | 281.60 |
  | 0.48 (`p5`) | 120 | — | 285.11 | 284.48 |

  Every not-clean race crashes once and finishes after the fallback. Max line error on clean races ≤ 1.77 m.
- **`p4` race day** (`test-circuit-seed2027`, its `p1` line and `p2` grip; hidden cars k = 1000–1004, race seed
  k mod 5; and, as record only, k = 1005–1023):

  | agent, fraction | hidden: clean | hidden: race times (s) | mean | k = 1000–1023: clean |
  |---|---|---|---|---|
  | Unit 11, 0.58 | 0/5 | 316.75, 378.70, 381.00, 379.65, 379.45 | 367.11 | 9/24 |
  | Unit 11, 0.56 | 1/5 | 382.05, 273.10, 381.45, 381.80, 381.50 | 359.98 | 11/24 |
  | Unit 11, 0.54 | 1/5 | 390.35, 275.45, 386.65, 384.65, 477.00 | 382.82 | 14/24 |
  | Unit 11, 0.52 | 1/5 | 480.40, 278.10, 389.90, 390.40, 486.50 | 405.06 | 17/24 |
  | Unit 11, 0.50 | 3/5 | 281.10, 280.80, 280.55, 486.40, 394.95 | 344.76 | 20/24 |
  | **Unit 11, 0.48** | **5/5** | 283.95, 283.90, 283.60, 283.75, 283.95 (median **283.90**) | 283.83 | 23/24 |
  | Unit 10, 0.54 | 1/5 | 379.85, 275.45, DNF, DNF, DNF (5–6 collisions each) | — | 14/24 (6 DNF) |
  | Unit 10, 0.48 | 5/5 | as Unit 11 at 0.48 (no respawn) | 283.83 | 23/24 |

  Every Unit 11 race finishes. The nominal car (no perturbation) at 0.54 is clean on seeds 0–4 (275.00–275.25 s):
  the race-day risk comes from the cars, not from the track alone. One wide-record car (k = 1005) crashes once even
  at 0.48: the margin makes crashes rarer, not impossible (said in the solutions).
- **`p5` the small protocol** (what the checkpoint asks a student to race): the three lowest-grip training cars
  (16, 18, 8, Unit 11's `grip_order[:3]`) × the five training tracks, race seed **0**: 0.56 not clean (`-seed2` cars
  16, 18), 0.54 not clean (`-seed2` cars 16, 8), 0.52 not clean (`-seed2` car 16), 0.50 and 0.48 clean on all 15.
  It finds the same edge (0.50) and the same margin value (0.48) as the full family.

## Gates (pinned from the probes; any failed assertion stops Phase A and amends the plan)
Only descriptive figures quoted in prose (a median, a mean) may be corrected in the report.
- **CPB.1 the track:** the generator writes `test-circuit-seed2027`, byte-stable (the existing checksum contract),
  with the stats above (length 2631.2 ± 0.1 m, 1316 waypoints, minimum half-width 5.41 ± 0.01 m, tightest radius
  19.3 ± 0.1 m), continuous curvature, 0 self-intersections, half-widths in [5.0, 8.0] m. The stem is pinned
  literally (the hidden grip is keyed to the name).
- **CPB.2 the measurement:** the six Unit 8 probes on `test-circuit-seed2027` give (9.10, 9.55, 7.79, 9.35, 9.00,
  7.76) to 0.01, and section 0's probe finishes with 0 collisions (the lower bound).
- **CPB.3 the family edge** (the small protocol, race seed 0, `agents/unit-11.py` with each track's line and
  measured grip): at 0.54 and at 0.52 at least one of the 15 races is not clean; at 0.50 and 0.48 all 15 are clean.
  So the margin rule gives 0.48.
- **CPB.4 race day** (`agents/checkpoint-b.py`, hidden cars k = 1000–1004, race seed k mod 5, 700 s cap): all five
  **clean**, median ≤ the **target 300 s** (probe 283.90 s).
- **CPB.5 the contrast** (same five races): `agents/unit-11.py` at 0.54 with the race-day line and grip finishes all
  five and is not clean on at least three; `agents/unit-10.py` at 0.54 with the same constants does not finish at
  least one.
- **CPB.6:** `check_submission(agents/checkpoint-b.py, track="test-circuit-seed2027")` passes (outside any pool).
- **Where each gate is asserted.**
  - CPB.1 in `roar/data/tests/test_gen_tracks.py` (the driver test's output list and `SEEDED_STATS` gain the name).
  - CPB.2–CPB.6 in the routed `tests/test_racekit_checkpoint_b.py` (helper `tests/_checkpoint_b_premise.py`,
    a conftest fixture `checkpoint_b_premise`). Jobs: 6 probes; CPB.3 15 + 15 (0.50, 0.48) + 7 + 7 (0.54 and 0.52,
    the first 7 in protocol order: `test-circuit`, `-seed1`, then `-seed2`'s first car, enough to include the
    not-clean race) = 44; CPB.4 5; CPB.5 10. **65 races**, about 65 × 6.1 s + the Unit 10 DNFs (3 × 700 s races,
    about 2.5 races each) ≈ 7.5 CPU-min, about 1 min pooled on 8 workers, plus the six line solves (under 1 s).
  - The **target 300 s** sits above the clean race-day value (283.90 s) and below every fraction that is not clean
    on race day (their means 344.76–405.06 s); it is a racekit target on this track and has nothing to do with the
    book's 329 s CARLA bar on Monza (the teacher notes say so).
  - The expected-time table (`p3`) is **probe record** (480 races are too many for the suite); wherever it is
    quoted it is labelled "the probe record of plan `roar-011`". The checkpoint gives it as data.

## The checkpoint (questions; the brief opens with the project)
**Brief:** "Race day. A track you have never driven, `test-circuit-seed2027`, and a car you have never met: five
cars of the perturbed family, sealed (`perturb=1000` … `1004`). You may measure the track with the carla-like car you
know, solve its line, and tune on the five training tracks with the training cars. You may race the race-day track
once: five races, after every choice is frozen." The rules: the submission is **your own Unit 11 submission**
(`agents/unit-11.py` is the stand-in); only `MU_FRACTION`, `LINE_CONTROL` and `MU_G` change; no
`perturbation_factors` on k ≥ 1000; no race on `test-circuit-seed2027` except the probes and race day.
**The bar:** all five race-day races clean (finished, 0 collisions, max line error ≤ 2 m), median ≤ 300 s.
1. **Measure the track.** Run Unit 8's six grip probes on `test-circuit-seed2027` (the given probe settings) and
   compute each section's μg; say which estimate is a lower bound and why.
2. **Solve its line and plan the lap.** The smoothest line (Unit 9); the planned lap time at 0.54 and at 0.48 with
   the speed profile (Unit 7) on the race-day track, compared with `test-circuit`'s.
3. **Two rules, one table.** From the given family table (the probe record: clean counts, not-clean races and mean
   times per fraction), compute each fraction's expected race time and find the fraction that expected time picks.
   Then apply the clean rule and the margin rule to the same table. Before racing anything: which do you ship, given
   the bar, and why?
4. **Check the family yourself.** The small protocol: the three lowest-grip training cars (from
   `perturbation_factors`) × the five training tracks, race seed 0, starting at 0.54 and going down by 0.02, each
   fraction stopped at its first race that is not clean. Report the edge and the margin value; freeze it;
   `check_submission` on the race-day track.
5. **Race day.** Race the five sealed cars once. Report clean, the median and the mean against the bar, and compare
   with the plan (Question 2).
6. **What bought what.** Given the book's race-day record (the `p4` table, shown only after Question 5), explain:
   what the margin bought on race day; what the fallback bought at 0.54 (Unit 10 against Unit 11), and why it did not
   make 0.54 a good choice; and why the expected time over the family misjudged race day.

## Budgets
- Routed pytest: measured 13.7 min after `roar-010`; this plan adds about 1–1.5 min. **≤ 15.5 min** (v4.10, interim;
  over means stop and amend). The follow-up on the routed-suite budget (a slow tier) is re-stated.
- Checkpoint notebooks: the solutions ≤ **5 min** serial, each cell ≤ 120 s: 6 probes (about 20 s), the line solve,
  Question 4's protocol (7 + 7 + 15 = 29 races, about 180 s, split one fraction per cell and 0.50 in two cells), race
  day (5 races, about 35 s). The checkpoint notebook itself has no outputs and no races.
- Book exec total: about 35.8 CI-min after `roar-010` + about 4.5 = about 40.3, **over** v4.8's 40.
  Design v4.10 raises the interim book-exec target to **50 CI-min** for the rest of the book (Units 12–13 and the
  capstone), recorded as the sixth interim raise; the author's tiering decision stays a follow-up.

## Phases
- **Phase A — track, reference, premise, registry.** (Opus subagent for code; registry inline.)
  - `roar/data/gen_tracks.py` `SEEDED_TRACKS` gains `("test-circuit", 2027)`; `generate.py` writes it (checksums);
    `test_gen_tracks.py` covers it (CPB.1); `conftest`'s missing-track check names it.
  - `agents/checkpoint-b.py`; `tests/_checkpoint_b_premise.py`, `tests/test_racekit_checkpoint_b.py`, the conftest
    fixture; CPB.2–CPB.6 confirmed and logged.
  - `coverage-map.yaml`: `checkpoint-02-part-2`, `kind: checkpoint`, `introduces: []`, `requires` all Unit 1–11
    concepts, `practices` the ones the questions use (grip-identification, racing-line, speed-profile,
    perturbation-testing, respawn-economics, failure-fallback, repeated-run-measurement); manifest mirrors it;
    `syllabus.md` row (no emoji).
  - Design 013 **v4.10**: §4.3 names `test-circuit-seed2027` as Checkpoint B's race-day track; §6 CP-B's gate gets the
    bar (five sealed cars, clean, median ≤ 300 s, tuned on the track × car family only); §7.1 the budgets; changelog.
- **Phase B — statements (Opus) and solutions (Opus, a separate fresh session).** The statements never quote a
  `_truth` value; the sealed cars' factors are never computed in either notebook.
- **Phase C — teacher notes** (inline): goals, a 60–90 min sitting plan (Question 4 is the long part; the short form
  races only `-seed2`, the family's hardest track), grading (the race is pass/fail; the written answers to 3 and 6
  carry the rest; since this plan's table is public, the grade rests on the evidence and the reasoning, never on
  the final number alone), the 300 s target vs the 329 s CARLA bar, common mistakes (shipping the expected-time
  minimum against a clean bar; racing the race-day track before freezing; inspecting the sealed cars; reading a
  lower bound as a measurement).
- **Phase D — verification:** `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN; budgets measured.

## Out of scope
- Any `racekit` library change; any change to Units 1–11 content or agents.
- Per-section knobs on the family; online identification; a CARLA lab (CP-B has none in the design).
- Unit 12's held-out-track and overfitting vocabulary (the checkpoint uses Unit 7's and Unit 11's rules only).

## Plan Review
