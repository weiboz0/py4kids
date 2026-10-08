// The learning website (design 012 part B; plan 103). A static build with no inline scripts or
// styles (the strict CSP, D9) and no integrations that load remote assets.
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'astro/config';
import { resolveOrigins } from '../deploy/origins.mjs';

// The Python runner's origins (plan 104, D7), configured only in deploy/origins.json and read
// through deploy/origins.mjs (plan 105 Phase D): PY4KIDS_TARGET picks local or production (with the
// preview pair), and PY4KIDS_SITE_ORIGIN / PY4KIDS_RUNNER_ORIGIN override both with one pair.
const { primary, pairs } = resolveOrigins();
const runnerOrigin = primary.runner;
const originPairs = pairs.map(({ site, runner }) => ({ site, runner }));
// frame-src lists every runner the build accepts; the client picks its partner at run time.
const frameSrc = originPairs.map((p) => p.runner).join(' ');

/** Fill the runner origins into dist/_headers (the CSP's frame-src). */
const runnerHeaders = {
  name: 'py4kids-runner-origin',
  hooks: {
    'astro:build:done': ({ dir }) => {
      const path = fileURLToPath(new URL('_headers', dir));
      const text = readFileSync(path, 'utf-8').replaceAll('{{RUNNER_ORIGIN}}', frameSrc);
      if (text.includes('{{')) throw new Error('_headers: an unfilled placeholder');
      writeFileSync(path, text);
    },
  },
};

export default defineConfig({
  output: 'static',
  trailingSlash: 'always',
  build: {
    format: 'directory',
    // Every stylesheet is an external file: the CSP's style-src is 'self' only.
    inlineStylesheets: 'never',
  },
  // No dev toolbar overlay.
  devToolbar: { enabled: false },
  integrations: [runnerHeaders],
  vite: {
    define: {
      'import.meta.env.PY4KIDS_RUNNER_ORIGIN': JSON.stringify(runnerOrigin),
      'import.meta.env.PY4KIDS_ORIGIN_PAIRS': JSON.stringify(originPairs),
    },
    build: {
      // Never inline a script or asset as a data: URL or inline <script>.
      assetsInlineLimit: 0,
    },
  },
});
