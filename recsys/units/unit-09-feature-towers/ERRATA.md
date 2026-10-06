# Errata — Unit 9 (feature towers and item cold-start)

## 2026-10-06 — milestone notebook committed with stored outputs (hygiene; no content change)

**Affected:** `recsys/projects/bookrec/milestones/unit-09-feature-towers.ipynb`
(merged in PR #141, commit `bd6997c`).

**What was wrong:** the milestone was committed with executed outputs and `execution_count` set on its
7 code cells. Milestones must be committed **cleared** (outputs stripped, `execution_count: null`) —
`milestone-check` enforces this, and CI re-executes them fresh. The stray outputs were introduced
during Unit 9's content-review rounds by a re-execution helper that wrote the executed notebook back
to disk; the final full `scripts/ci-local.sh` was not re-run after that step (only the per-notebook
exec + static checks were), so `milestone-check` did not re-flag it before merge.

**Impact:** none on content or correctness — the milestone's code, numbers, and prose are unchanged and
it still executes top-to-bottom clean. The only effect was a `milestone-check` hygiene failure
(14 findings) that surfaced on the next full `ci-local.sh` run (during Unit 10, recsys-012).

**Fix:** cleared the milestone's outputs and `execution_count` (zero content change), restoring the
state Unit 9's own Phase E shipped and its gates passed. Applied on the `feature/recsys-012-unit10`
branch (user-approved, 2026-10-06) so Unit 10's Phase G `ci-local.sh` goes green; this is a
typo-class hygiene correction (no 2-way diagnosis). Unit 9's lesson and solutions notebooks correctly
retain their outputs (exec-lessons / exec-solutions compare/retain them) and were **not** touched.

**Prevention:** after any content-gate re-execution that writes notebooks back to disk, re-run the full
`scripts/ci-local.sh` (not just per-notebook exec + static checks) before merge, so `milestone-check`
re-validates milestone hygiene.
