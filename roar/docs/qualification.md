# Qualification record: the author's reference runs on the official simulator

This file is the record that design 013 §7.3 asks for.
It holds **only the author's reference agents**, never student results: the repository is public.

Every racekit number in the book is a model number.
This record is where the book's reference agents meet CARLA itself.

## Final qualification (before `roar-014` sets the `publication` flag)

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

## Interim checks (early warnings; they do not block shipping)

Each check is the **first run of the named agent exactly as shipped**; a later, re-tuned run never replaces it.
A FAIL is surfaced as a follow-up and triggers an errata/fix plan before the next part of the book ships.

| plan | agent | check | submission SHA-256 | repository commit | result |
|---|---|---|---|---|---|
| `roar-006` | `roar/projects/racekit/agents/unit-07.py` | untimed, 3 laps, 0 collisions | `4d56c05bfa3ba50de3e4e0c15fcb07dd4d5e33db24219497c389a0f63fa3eb9f` (at the `roar-006` Phase A commit; re-recorded if the file changes before merge) | the `roar-006` merge commit | PENDING (author) |
| `roar-013` | `roar/projects/racekit/agents/unit-13.py` | timed | `5a64c19ed58cf8e27e5b493b317df199add9f65e43c50643f539fda4dfccf0da` (at the `roar-013` Phase A commit; re-recorded if the file changes before merge) | the `roar-013` merge commit | PENDING (author) |
