/** Shared by the reference-solver parity setup and test (plan 104 Phase D). */
import { join } from 'node:path';
import { SITE } from './env';

/** Parallel shards (one page and runner each). */
export const SHARDS = 4;

/** Where solvers.setup.ts writes CPython's verdicts for solvers.spec.ts to read. */
export const VERDICTS_FILE = join(SITE, 'node_modules', '.cache', 'py4kids-solver-verdicts.json');

/** One solver and its cases, as e2e/helpers/solver_verdicts.py prints them. */
export interface Solver {
  book: string;
  entry: string;
  stem: string;
  /** Repo-relative path of the solver. */
  solver: string;
  match: 'line' | 'token';
  cases: { name: string; in: string; out: string; verdict: string; problem: string | null; cpu_ms: number }[];
}
