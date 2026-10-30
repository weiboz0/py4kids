# Qualification record: the author's reference runs on the official simulator

This file is the record that design 013 §7.3 asks for.
It holds **only the author's reference agents**, never student results: the repository is public.

Every racekit number in the book is a model number.
This record is where the book's reference agents meet CARLA itself.

## Final qualification (before a follow-up plan to `roar-014` sets the `site` and `publication` flags)

The final reference submission, on the pinned stack (CARLA 0.9.12, Monza v1.1, `ROAR_Competition` and `ROAR_PY` at
their pinned commits), in **exactly 5 consecutive official-runner launches**.
No launch is discarded or restarted; a host failure is recorded and the 5-launch block restarts, with both blocks kept.
The proxy of design §1.3 must hold: every run clean, median ≤ 329 s.

| field | value |
|---|---|
| hardware, OS, GPU | not yet run |
| CARLA, map, `ROAR_Competition`, `ROAR_PY` versions | not yet run |
| submission file, SHA-256 | not yet run |
| repository commit | not yet run |

| launch | time (s) | collisions | outcome |
|---|---|---|---|
| — | — | — | not yet run |

**The flags wait on this run** (plan `roar-014`, design 013 v4.13 §3).
`roar-014` shipped the capstone with the `site` and `publication` flags unset, because this run needs the author's machine;
a follow-up plan records the five launches here and sets both flags (or, if the proxy fails, a re-tune plan follows, design §7.3).

**The file it races** is the capstone's reference submission, `roar/projects/racekit/agents/unit-13.py`, unchanged
(racekit: 468.55 s median on `monza-like`, seeds 0–4; clean on 24 of 24 of its test cars 72–95),
SHA-256 `5a64c19ed58cf8e27e5b493b317df199add9f65e43c50643f539fda4dfccf0da` (computed with the shell's `sha256sum`),
unless a follow-up plan records an author override of design §6 row 13's rule, and why.
On CARLA it is the lab-assembled file with the author's own Monza line and grip; the submission row above records that file's own SHA-256.

One informational row, **not a submission candidate** under design §6 row 13 (a file is submitted only if it is clean on every fresh car it was never tuned on):

| file | racekit median (s) | fresh cars | verdict |
|---|---|---|---|
| `unit-13.py` with `TARGET_SPEED = 50.0` and nothing else changed (the capstone solution's worked choice; not shipped; SHA-256 `dc01139f616928a839766f6075ac7cce778e6a5ad92d1de97cda5c1f84778b08`, the file `write_variant` writes) | 447.90 | 23 of 24 clean on its pre-registered test cars 96–119 (car 117 collides) | failed N/N: not submitted |

The author may race it on CARLA as an extra row; it never replaces the final qualification's file.

## Interim checks (early warnings; they do not block shipping)

Each check is the **first run of the named agent exactly as shipped**; a later, re-tuned run never replaces it.
A FAIL is surfaced as a follow-up and triggers an errata/fix plan before the next part of the book ships.

| plan | agent | check | submission SHA-256 | repository commit | result |
|---|---|---|---|---|---|
| `roar-006` | `roar/projects/racekit/agents/unit-07.py` | untimed, 3 laps, 0 collisions | `4d56c05bfa3ba50de3e4e0c15fcb07dd4d5e33db24219497c389a0f63fa3eb9f` (at the `roar-006` Phase A commit; re-recorded if the file changes before merge) | the `roar-006` merge commit | PENDING (author) |
| `roar-013` | `roar/projects/racekit/agents/unit-13.py` | timed | `5a64c19ed58cf8e27e5b493b317df199add9f65e43c50643f539fda4dfccf0da` (at the `roar-013` Phase A commit; re-recorded if the file changes before merge) | the `roar-013` merge commit | PENDING (author) |
