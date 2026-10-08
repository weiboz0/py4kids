/**
 * Reference-solver parity (plan 104 Phase D; design 012 §3 "Reference solvers"), SLOW: every
 * reference solver `assets/{l,ex,q,p}N.py` of every `judge: true` book (usaco-bronze, acsl) runs
 * in Pyodide, through the real runner, against ALL its fixture pairs, and every case's verdict
 * equals `tools/judge.py`'s.
 *
 * - CPython's verdicts come from `e2e/helpers/solver_verdicts.py` (the judge's own walk and
 *   `_run_case`), computed once at test time by the `solvers-setup` project (solvers.setup.ts).
 * - The solvers and fixtures are read from the repository at test time, never from the site:
 *   nothing here is shipped.
 * - Each case is one `run` with a `fixture` check and a fresh session, exactly as the practice
 *   page sends it, so the runner gives every case a fresh Python worker; the matching mode is the
 *   book's (`line` for acsl, `token` otherwise) and the budget is the site's rule (max(1 s, 10x
 *   the solver's CPython time rounded up to 100 ms), capped at 10 s), from the `cpu_ms` the
 *   bundle ships for that item; only solvers that ship no fixtures item (lesson solvers) fall
 *   back to the CPython time measured now.
 * - The items are split into SHARDS balanced by case count; each shard is one test with its own
 *   page (and runner), and the shards run in parallel (`pnpm -C site e2e:solvers`).
 */
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { expect, test } from '@playwright/test';
import { caseBudget } from '../src/lib/check-model';
import { allItems, REPO } from './helpers/content';
import { openRunner, type Browserside } from './helpers/runner';
import { SHARDS, VERDICTS_FILE, type Solver } from './helpers/solvers';

test.describe.configure({ mode: 'parallel' });

/** `tools/export/timing.py`'s `round_ms`: up to the next 100 ms, clamped to [100, 10000]. */
const roundMs = (ms: number) => Math.min(10_000, Math.max(100, Math.ceil(Math.max(0, ms) / 100) * 100));

/** The `cpu_ms` the site ships per fixtures item, keyed `<book>/<entry>/<stem>` (its fixture folder). */
function shippedCpuMs(): Map<string, number> {
  const out = new Map<string, number>();
  for (const { book, item } of allItems()) {
    if (item.check?.kind !== 'fixtures' || item.check.cases.length === 0) continue;
    const folder = /^files\/([^/]+)\/fixtures\/([^/]+)\//.exec(item.check.cases[0]!.in_file);
    if (folder) out.set(`${book}/${folder[1]}/${folder[2]}`, item.check.cpu_ms);
  }
  return out;
}

/** The runner's fixture verdict as the judge's category. */
function category(results: { pass: boolean; detail: string }[]): string {
  if (results.length === 0) return 'no verdict';
  const failed = results.find((r) => !r.pass);
  if (!failed) return 'pass';
  if (failed.detail.startsWith('failed:')) return 'failed';
  return failed.detail;
}

/** Greedy balance by case count, largest first: shard `i`'s solvers. */
function shardOf(solvers: Solver[], i: number): Solver[] {
  const load = Array.from({ length: SHARDS }, () => 0);
  const out: Solver[][] = Array.from({ length: SHARDS }, () => []);
  const order = [...solvers].sort((a, b) => b.cases.length - a.cases.length || a.solver.localeCompare(b.solver));
  for (const s of order) {
    const k = load.indexOf(Math.min(...load));
    out[k]!.push(s);
    load[k]! += s.cases.length;
  }
  return out[i]!.sort((a, b) => a.solver.localeCompare(b.solver));
}

for (let shard = 0; shard < SHARDS; shard++) {
  test(`reference solvers in Pyodide match tools/judge.py: shard ${shard + 1} of ${SHARDS}`, async ({ page }) => {
    const solvers = JSON.parse(readFileSync(VERDICTS_FILE, 'utf-8')) as Solver[];
    const mine = shardOf(solvers, shard);
    const shipped = shippedCpuMs();
    const total = mine.reduce((n, s) => n + s.cases.length, 0);
    test.setTimeout(30 * 60_000);
    await openRunner(page);
    const started = Date.now();
    const mismatches: string[] = [];
    let cases = 0;
    for (const solver of mine) {
      const code = readFileSync(join(REPO, solver.solver), 'utf-8');
      const budget = caseBudget(shipped.get(`${solver.book}/${solver.entry}/${solver.stem}`)
        ?? roundMs(Math.max(...solver.cases.map((c) => c.cpu_ms))));
      const runs = solver.cases.map((c) => ({ stdin: readFileSync(join(REPO, c.in), 'utf-8'), expected: readFileSync(join(REPO, c.out), 'utf-8') }));
      // One item per evaluate (a batch), its cases sent one at a time as the practice page does.
      const got = await page.evaluate(
        async ({ code, runs, match, budget, tag }) => {
          const { runner } = window as unknown as Browserside;
          const out: { status: string; interrupts: string; results: { pass: boolean; detail: string }[]; stderr: string }[] = [];
          let i = 0;
          for (const r of runs) {
            const result = await runner.run({
              session: `${tag}-${++i}`,
              code,
              stdin: r.stdin,
              check: { kind: 'fixture', expected: r.expected, match, turtle: false },
              budget_ms: budget,
            }).result;
            out.push({ status: result.status, interrupts: result.interrupts, results: result.results, stderr: result.stderr.slice(-400) });
          }
          return out;
        },
        { code, runs, match: solver.match, budget, tag: `parity-${shard}-${cases}` },
      );
      solver.cases.forEach((c, i) => {
        const browser = category(got[i]!.results);
        if (browser !== c.verdict) {
          mismatches.push(`${solver.solver} ${c.name}: Pyodide ${browser} (${got[i]!.status}; ${got[i]!.stderr.trim().split('\n').pop() ?? ''}), judge ${c.verdict}`);
        }
      });
      cases += solver.cases.length;
    }
    const ms = Date.now() - started;
    const summary = `shard ${shard + 1}/${SHARDS}: ${mine.length} solvers, ${cases} cases in ${(ms / 1000).toFixed(1)} s (${(ms / Math.max(1, cases)).toFixed(0)} ms/case), ${mismatches.length} mismatches`;
    test.info().annotations.push({ type: 'solvers', description: summary });
    console.log(`solver parity ${summary}`);
    expect(cases).toBe(total);
    expect(mismatches).toEqual([]);
  });
}
