// The learning website (design 012 part B; plan 103). A static build with no inline scripts or
// styles (the strict CSP, D9) and no integrations that load remote assets.
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'astro/config';

// The Python runner's origin (plan 104, D7), configured only in runner/origins.json; a build for
// another deployment sets PY4KIDS_RUNNER_ORIGIN.
const origins = JSON.parse(readFileSync(new URL('../runner/origins.json', import.meta.url), 'utf-8'));
const runnerOrigin = process.env.PY4KIDS_RUNNER_ORIGIN ?? origins.runner;
if (new URL(runnerOrigin).origin !== runnerOrigin) throw new Error(`not an origin: ${runnerOrigin}`);

/** Fill the runner origin into dist/_headers (the CSP's frame-src). */
const runnerHeaders = {
  name: 'py4kids-runner-origin',
  hooks: {
    'astro:build:done': ({ dir }) => {
      const path = fileURLToPath(new URL('_headers', dir));
      const text = readFileSync(path, 'utf-8').replaceAll('{{RUNNER_ORIGIN}}', runnerOrigin);
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
    },
    build: {
      // Never inline a script or asset as a data: URL or inline <script>.
      assetsInlineLimit: 0,
    },
  },
});
