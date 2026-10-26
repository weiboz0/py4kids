# Upstream sources, licences and the clean-room record

This file is the provenance record for *Applied Python: Autonomous Racing* (design 013 §7.4, plan roar-001).

## `ROAR_PY` (MIT)

- Repository: <https://github.com/augcog/ROAR_PY>.
- Pinned commit: `3cbb087ccc5198248815b57742a945e81ef55b64` (2024-07-26).
- Licence: MIT, "Copyright (c) 2023 Yunhao Cao, Qianxin Gan and the ROAR group at UC Berkeley".
- What this repository derives from it: **only** the interface contract fixture,
  `roar/projects/racekit/racekit/contract/roar_py_contract.json`.
  It records class, method, attribute and parameter names, async flags, observation-space shapes and dtypes,
  and the action keys and ranges, as data.
  It contains no `ROAR_PY` code.
  The MIT notice ships next to it as `roar/projects/racekit/racekit/contract/LICENSE-ROAR_PY`.
- The fixture is written by a committed, deterministic extractor,
  `roar/projects/racekit/scripts/extract_roar_py_contract.py`, which parses a local checkout with `ast`
  and refuses any commit other than the pinned one.
  Re-extraction is a manual step, because it needs a network clone:

  ```bash
  git clone https://github.com/augcog/ROAR_PY /path/to/roar_py
  git -C /path/to/roar_py checkout 3cbb087ccc5198248815b57742a945e81ef55b64
  uv run --group roar python roar/projects/racekit/scripts/extract_roar_py_contract.py /path/to/roar_py
  ```

  The extractor also rewrites the fixture's sha256 sidecar, `roar_py_contract.json.sha256`.

## `ROAR_Competition` (no licence)

- Repository: <https://github.com/augcog/ROAR_Competition>.
- Commit read for the race rules: `ab19e1b` (`competition_code/competition_runner.py`).
- It has **no LICENSE file** (checked 2026-10-25).
  Nothing from it is copied into this repository: no code, no waypoint data, no configuration.
  A routed test (`roar/tests/test_roar_guards.py`) fails if a file named `competition_runner.py` or
  `infrastructure.py` is ever tracked.

## CARLA maps and waypoints

The official race runs on CARLA 0.9.12 with the Monza map v1.1.
The map, its OpenDRIVE file and its waypoint lists are **never** committed or redistributed.
The book's tracks are generated from seeded segment specs by `roar/data/gen_tracks.py`;
`monza-like` is *inspired by* public facts about the Monza circuit and is not the CARLA map.

## Clean-room note

`racekit`'s interface shim (`racekit/roar_py_interface.py`), its race runner and the starter re-implementation
(`roar/projects/racekit/agents/starter.py`) are written from **documented behaviour**:
- the competition documentation at <https://roar.gitbook.io/roar-competition-documentation>;
- the published season reports cited below;
- the race facts recorded in design 013 §1.2, which describe the runner's behaviour in prose.

No upstream source text was copied into them.

## Season reports (design 013 §1.3)

- First place, Summer 2026:
  <https://roar.berkeley.edu/opening-the-corner-late-apex-line-widening-and-per-sectiongrip-tuning-for-the-roar-monza-simulation-race/>
- Third place, Summer 2026:
  <https://roar.berkeley.edu/third-place-solution-in-summer-2026-simulation-racing-series/>
