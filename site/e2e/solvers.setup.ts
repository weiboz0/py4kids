/**
 * The reference-solver parity setup (plan 104 Phase D): CPython's verdict on every solver case by
 * `tools/judge.py` (e2e/helpers/solver_verdicts.py), written once for the parity shards.
 */
import { spawnSync } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname } from 'node:path';
import { expect, test } from '@playwright/test';
import { REPO } from './helpers/content';
import { VERDICTS_FILE, type Solver } from './helpers/solvers';

test('CPython verdicts for every reference solver case (tools/judge.py)', () => {
  test.setTimeout(10 * 60_000);
  const started = Date.now();
  const result = spawnSync('uv', ['run', '--quiet', 'python', 'site/e2e/helpers/solver_verdicts.py'], {
    cwd: REPO,
    encoding: 'utf-8',
    maxBuffer: 256 * 1024 * 1024,
  });
  expect(result.status, result.stderr).toBe(0);
  const solvers = JSON.parse(result.stdout) as Solver[];
  const cases = solvers.reduce((n, s) => n + s.cases.length, 0);
  // Both judge books, and every solver judged on at least two pairs (the judge's own floor).
  expect(new Set(solvers.map((s) => s.book))).toEqual(new Set(['usaco-bronze', 'acsl']));
  for (const s of solvers) expect(s.cases.length, s.solver).toBeGreaterThanOrEqual(2);
  mkdirSync(dirname(VERDICTS_FILE), { recursive: true });
  writeFileSync(VERDICTS_FILE, JSON.stringify(solvers));
  const summary = `${solvers.length} solvers, ${cases} cases judged by CPython in ${((Date.now() - started) / 1000).toFixed(1)} s`;
  test.info().annotations.push({ type: 'solvers', description: summary });
  console.log(`solver parity setup: ${summary}`);
});
