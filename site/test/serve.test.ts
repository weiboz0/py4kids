/**
 * The Phase F test server (site/scripts/serve.mjs) applies `_headers` with the Cloudflare Pages
 * semantics the browser tests rely on, and serves paths the way Pages does.
 */
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import { headersFor, parseHeadersFile, startServer } from '../scripts/serve.mjs';
import { CSP, parseHeaders } from './helpers/headers';

const SITE = join(import.meta.dirname, '..');

describe('_headers semantics', () => {
  const rules = parseHeadersFile(
    [
      '# a comment',
      '/*',
      '  X-Frame: DENY',
      '  X-Multi: a',
      '/docs/*',
      '  X-Multi: b',
      '  ! X-Frame',
      '/users/:id/profile',
      '  X-User: yes',
      'https://other.example/*',
      '  X-Other: yes',
      '',
    ].join('\n'),
  );

  it('applies every matching rule in order, joins repeats and detaches with "!"', () => {
    expect(Object.fromEntries(headersFor(rules, '/'))).toEqual({ 'x-frame': 'DENY', 'x-multi': 'a' });
    expect(Object.fromEntries(headersFor(rules, '/docs/a/b/'))).toEqual({ 'x-multi': 'a, b' });
  });

  it('matches whole paths: a splat spans segments, a placeholder matches exactly one', () => {
    expect(headersFor(rules, '/users/42/profile').get('x-user')).toBe('yes');
    expect(headersFor(rules, '/users/4/2/profile').has('x-user')).toBe(false);
    expect(headersFor(rules, '/users/42/profile/more').has('x-user')).toBe(false);
    expect(headersFor(rules, '/docs').has('x-multi')).toBe(true); // only the /* rule
    expect(headersFor(rules, '/docs').get('x-multi')).toBe('a');
  });

  it('applies an absolute pattern only on its own host', () => {
    expect(headersFor(rules, '/x', 'localhost').has('x-other')).toBe(false);
    expect(headersFor(rules, '/x', 'other.example').get('x-other')).toBe('yes');
  });

  it('reads the real public/_headers exactly as the shared helper does', () => {
    const text = readFileSync(join(SITE, 'public', '_headers'), 'utf-8');
    const mine = headersFor(parseHeadersFile(text), '/acsl/unit-08-boolean-algebra/');
    const theirs = parseHeaders(text).get('/*')!;
    expect(Object.fromEntries(mine)).toEqual(Object.fromEntries(theirs));
    expect(mine.get('content-security-policy')).toBe(CSP);
  });
});

describe('serve.mjs', () => {
  let root: string;
  let server: { url: string; close(): Promise<void> };

  beforeAll(async () => {
    root = mkdtempSync(join(tmpdir(), 'py4kids-serve-'));
    mkdirSync(join(root, 'a'));
    writeFileSync(join(root, 'index.html'), '<!doctype html><title>home</title>');
    writeFileSync(join(root, 'a', 'index.html'), '<!doctype html><title>a</title>');
    writeFileSync(join(root, 'app.js'), 'export {};');
    writeFileSync(join(root, '.secret'), 'no');
    writeFileSync(join(root, '_headers'), '/*\n  X-Test: on\n/a/*\n  X-A: on\n');
    server = await startServer({ root, port: 0 });
  });

  afterAll(async () => {
    await server.close();
    rmSync(root, { recursive: true, force: true });
  });

  it('serves directories, files and types with the matching headers', async () => {
    const home = await fetch(`${server.url}/`);
    expect(home.status).toBe(200);
    expect(home.headers.get('content-type')).toMatch(/^text\/html/);
    expect(home.headers.get('x-test')).toBe('on');
    expect(home.headers.get('x-a')).toBeNull();
    const a = await fetch(`${server.url}/a/`);
    expect(a.headers.get('x-a')).toBe('on');
    const js = await fetch(`${server.url}/app.js`);
    expect(js.headers.get('content-type')).toMatch(/^text\/javascript/);
  });

  it('redirects a directory without its slash, and never serves _headers or dotfiles', async () => {
    const r = await fetch(`${server.url}/a`, { redirect: 'manual' });
    expect(r.status).toBe(308);
    expect(r.headers.get('location')).toBe('/a/');
    expect((await fetch(`${server.url}/_headers`)).status).toBe(404);
    expect((await fetch(`${server.url}/.secret`)).status).toBe(404);
    expect((await fetch(`${server.url}/../../etc/passwd`)).status).toBe(404);
    const missing = await fetch(`${server.url}/nope/`);
    expect(missing.status).toBe(404);
    expect(missing.headers.get('x-test')).toBe('on');
  });

  it('answers only GET and HEAD', async () => {
    expect((await fetch(`${server.url}/`, { method: 'HEAD' })).status).toBe(200);
    expect((await fetch(`${server.url}/`, { method: 'POST', body: 'x' })).status).toBe(405);
  });
});
