#!/usr/bin/env node
/**
 * Serve the built site and the built Python runner together (plan 104 Phase A), each on its own
 * origin from runner/origins.json (or PY4KIDS_SITE_ORIGIN / PY4KIDS_RUNNER_ORIGIN) and each with its
 * own `_headers`, through scripts/serve.mjs. The builds bake these origins in (the site's
 * frame-src; the runner's frame-ancestors and accepted parent), so serve exactly there.
 *
 * Usage: node scripts/serve-both.mjs   (build both first: bash scripts/build-site.sh)
 */
import { existsSync, readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { startServer } from './serve.mjs';

const site = resolve(fileURLToPath(new URL('..', import.meta.url)));
const origins = JSON.parse(readFileSync(join(site, '..', 'runner', 'origins.json'), 'utf-8'));
const servers = [
  { root: join(site, 'dist'), origin: process.env.PY4KIDS_SITE_ORIGIN ?? origins.site },
  { root: join(site, '..', 'runner', 'dist'), origin: process.env.PY4KIDS_RUNNER_ORIGIN ?? origins.runner },
];
for (const { root, origin } of servers) {
  if (!existsSync(join(root, 'index.html'))) {
    console.error(`serve-both: ${root} has no index.html (build first: bash scripts/build-site.sh)`);
    process.exit(1);
  }
  const url = new URL(origin);
  await startServer({ root, port: Number(url.port), host: url.hostname });
  console.log(`serve-both: ${root} at ${origin}`);
}
