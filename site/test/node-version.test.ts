/** The Node version guard of the leak test ([fable] content review 1, finding 4). */
import { describe, expect, it } from 'vitest';
import { nodeVersionProblem } from './helpers/node-version';

describe('nodeVersionProblem', () => {
  it('accepts Node 22.12 and later', () => {
    for (const v of ['22.12.0', '22.20.1', '23.0.0', '24.21.0']) expect(nodeVersionProblem(v)).toBeNull();
  });

  it('explains how to get a usable Node on anything older', () => {
    for (const v of ['20.20.1', '22.11.9', '18.0.0']) {
      const problem = nodeVersionProblem(v);
      expect(problem).toContain(`Node ${v}`);
      expect(problem).toContain('>= 22.12');
      expect(problem).toContain('source scripts/site-env.sh');
    }
  });
});
