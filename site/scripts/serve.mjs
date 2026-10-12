#!/usr/bin/env node
/**
 * The test server for the built site (plan 103 Phase F): serves `dist/` the way Cloudflare Pages
 * does, so the browser tests see the real response headers.
 *
 * - `_headers` (Cloudflare Pages format): a URL pattern on an unindented line, its headers on the
 *   indented `Name: value` lines below; `#` lines are comments. Every rule whose pattern matches
 *   the request path applies, in file order; a header set by more than one rule is joined with
 *   `, `; an indented `! Name` line removes a header an earlier rule set. Patterns match the whole
 *   path: `*` (a splat) matches any characters, `:name` matches one path segment. An absolute
 *   pattern (`https://host/path`) matches only when its host is this server's host.
 * - Paths: `/a/b/` serves `a/b/index.html`; `/a/b` redirects (308) to `/a/b/` when that directory
 *   has an index.html; `/a/b.html` serves the file. `_headers` itself and dotfiles are never
 *   served. A missing path is `404.html` when the build has one, else a plain 404.
 * - Only GET and HEAD; anything else is 405 (the site never sends a body).
 *
 * Usage: node scripts/serve.mjs [--root DIR] [--port N] [--host H]   (defaults: dist, 4321, 127.0.0.1)
 * Import: `startServer({ root, port, host })` resolves to `{ server, url, close }`.
 */

import { createReadStream, existsSync, readFileSync, statSync } from 'node:fs';
import { createServer } from 'node:http';
import { extname, join, normalize, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
  '.wasm': 'application/wasm',
  '.zip': 'application/zip',
  '.txt': 'text/plain; charset=utf-8',
  '.xml': 'application/xml',
  '.webmanifest': 'application/manifest+json',
  '.woff2': 'font/woff2',
};

/**
 * Parse `_headers` into rules: `[{ pattern, set: [[name, value]], detach: [name] }]`, in file
 * order. Header names are lower-cased.
 */
export function parseHeadersFile(text) {
  const rules = [];
  let current;
  for (const raw of text.split(/\r?\n/)) {
    if (raw.trim() === '' || raw.trimStart().startsWith('#')) continue;
    if (!/^\s/.test(raw)) {
      current = { pattern: raw.trim(), set: [], detach: [] };
      rules.push(current);
      continue;
    }
    if (!current) throw new Error(`_headers: header before any URL pattern: ${raw}`);
    const line = raw.trim();
    if (line.startsWith('!')) {
      current.detach.push(line.slice(1).trim().toLowerCase());
      continue;
    }
    const colon = line.indexOf(':');
    if (colon < 1) throw new Error(`_headers: not a header line: ${raw}`);
    current.set.push([line.slice(0, colon).trim().toLowerCase(), line.slice(colon + 1).trim()]);
  }
  return rules;
}

const escapeRe = (s) => s.replace(/[.+?^${}()|[\]\\]/g, '\\$&');

/** A `_headers` URL pattern as a whole-path RegExp (`*` splat, `:name` one segment). */
export function patternRegExp(pattern) {
  let path = pattern;
  let host = null;
  const absolute = /^https?:\/\/([^/]+)(\/.*)?$/.exec(pattern);
  if (absolute) {
    host = absolute[1];
    path = absolute[2] ?? '/';
  }
  const body = path
    .split(/(\*|:[A-Za-z_]\w*)/)
    .map((part) => (part === '*' ? '.*' : part.startsWith(':') && part.length > 1 ? '[^/]+' : escapeRe(part)))
    .join('');
  return { host, re: new RegExp(`^${body}$`) };
}

/** The headers `rules` give a request for `pathname` on `host`, as a Map (lower-case names). */
export function headersFor(rules, pathname, host = 'localhost') {
  const out = new Map();
  for (const rule of rules) {
    const { host: ruleHost, re } = patternRegExp(rule.pattern);
    if (ruleHost !== null && ruleHost !== host) continue;
    if (!re.test(pathname)) continue;
    for (const [name, value] of rule.set) out.set(name, out.has(name) ? `${out.get(name)}, ${value}` : value);
    for (const name of rule.detach) out.delete(name);
  }
  return out;
}

/** The file a request path maps to: `{ file }`, `{ redirect }` or `null` (404). */
export function resolvePath(root, pathname) {
  let decoded;
  try {
    decoded = decodeURIComponent(pathname);
  } catch {
    return null;
  }
  if (decoded.includes('\0')) return null;
  const segments = decoded.split('/').filter(Boolean);
  // Never serve `_headers` or a dotfile (Cloudflare Pages does not).
  if (segments.some((s) => s.startsWith('.')) || segments.at(-1) === '_headers') return null;
  const full = normalize(join(root, ...segments));
  if (full !== root && !full.startsWith(root + sep)) return null;
  const isFile = (p) => existsSync(p) && statSync(p).isFile();
  if (decoded.endsWith('/')) {
    const index = join(full, 'index.html');
    return isFile(index) ? { file: index } : null;
  }
  if (isFile(full)) return { file: full };
  if (isFile(join(full, 'index.html'))) return { redirect: `${pathname}/` };
  return null;
}

/**
 * Serve `root` at `host:port`. `delayMs` (tests only: a slow network for one file) is called with
 * each request's path and holds the response that many milliseconds.
 * @param {{ root?: string, port?: number, host?: string, delayMs?: (path: string) => number }} [options]
 */
export function startServer({ root = 'dist', port = 4321, host = '127.0.0.1', delayMs = undefined } = {}) {
  const base = resolve(root);
  const headersPath = join(base, '_headers');
  const rules = existsSync(headersPath) ? parseHeadersFile(readFileSync(headersPath, 'utf-8')) : [];
  const notFound = join(base, '404.html');

  const server = createServer((req, res) => {
    const wait = delayMs ? delayMs(new URL(req.url ?? '/', 'http://x').pathname) : 0;
    if (wait > 0) setTimeout(() => respond(req, res), wait);
    else respond(req, res);
  });

  function respond(req, res) {
    if (res.destroyed) return;
    const url = new URL(req.url ?? '/', `http://${req.headers.host ?? 'localhost'}`);
    for (const [name, value] of headersFor(rules, url.pathname, url.hostname)) res.setHeader(name, value);
    if (req.method !== 'GET' && req.method !== 'HEAD') {
      res.setHeader('allow', 'GET, HEAD');
      res.writeHead(405, { 'content-type': 'text/plain; charset=utf-8' }).end('method not allowed\n');
      return;
    }
    const found = resolvePath(base, url.pathname);
    if (found?.redirect) {
      res.writeHead(308, { location: found.redirect + url.search }).end();
      return;
    }
    let file = found?.file;
    let status = 200;
    if (!file) {
      if (!existsSync(notFound)) {
        res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' }).end('not found\n');
        return;
      }
      file = notFound;
      status = 404;
    }
    const size = statSync(file).size;
    res.writeHead(status, {
      'content-type': TYPES[extname(file).toLowerCase()] ?? 'application/octet-stream',
      'content-length': size,
      'cache-control': 'no-cache',
    });
    if (req.method === 'HEAD') {
      res.end();
      return;
    }
    createReadStream(file).pipe(res);
  }

  return new Promise((resolveStart, reject) => {
    server.once('error', reject);
    server.listen(port, host, () => {
      const address = server.address();
      const url = `http://${host}:${typeof address === 'object' && address ? address.port : port}`;
      resolveStart({ server, url, close: () => new Promise((done) => server.close(() => done())) });
    });
  });
}

function args(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i += 2) {
    const [flag, value] = [argv[i], argv[i + 1]];
    if (!['--root', '--port', '--host'].includes(flag) || value === undefined) {
      console.error('usage: node scripts/serve.mjs [--root DIR] [--port N] [--host H]');
      process.exit(2);
    }
    out[flag.slice(2)] = flag === '--port' ? Number(value) : value;
  }
  return out;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const options = args(process.argv.slice(2));
  const site = resolve(fileURLToPath(new URL('..', import.meta.url)));
  const root = options.root ?? join(site, 'dist');
  if (!existsSync(join(root, 'index.html'))) {
    console.error(`serve: ${root} has no index.html (build the site first: bash scripts/build-site.sh)`);
    process.exit(1);
  }
  const { url } = await startServer({ ...options, root });
  console.log(`serve: ${root} at ${url}`);
}
