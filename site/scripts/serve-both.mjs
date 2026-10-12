#!/usr/bin/env node
/**
 * Serve the built site and the built Python runner together (plan 104 Phase A), each on its own
 * origin from deploy/origins.json (or PY4KIDS_SITE_ORIGIN / PY4KIDS_RUNNER_ORIGIN) and each with its
 * own `_headers`, through scripts/serve.mjs. The builds bake these origins in (the site's
 * frame-src; the runner's frame-ancestors and accepted parent), so serve exactly there.
 *
 * Usage: node scripts/serve-both.mjs   (build both first: bash scripts/build-site.sh)
 */
import { existsSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { resolveOrigins } from '../../deploy/origins.mjs';
import { startServer } from './serve.mjs';

const site = resolve(fileURLToPath(new URL('..', import.meta.url)));
const { primary } = resolveOrigins();
const servers = [
  { root: join(site, 'dist'), origin: primary.site },
  { root: join(site, '..', 'runner', 'dist'), origin: primary.runner },
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
