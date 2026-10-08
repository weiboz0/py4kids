/**
 * The site's static files and build steps (plan 103 Phase E): the `_headers` file (Cloudflare
 * Pages format) with the exact strict CSP, the favicon, and the slide audit covering every
 * `site: true` book.
 */
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { loadBook, loadBooks, repoRoot } from '../src/lib/bundle';
import { runAudit, siteBookIds } from '../src/lib/slide-config';
import { CSP_TEMPLATE, parseHeaders } from './helpers/headers';

const SITE = join(import.meta.dirname, '..');
const PUBLIC = join(SITE, 'public');
const CONTENT = join(repoRoot(), 'site', 'content');

describe('_headers', () => {
  const rules = parseHeaders(readFileSync(join(PUBLIC, '_headers'), 'utf-8'));
  const all = rules.get('/*');

  it('applies the strict CSP and the other headers to every path', () => {
    expect([...rules.keys()]).toEqual(['/*']);
    expect(all?.get('content-security-policy')).toBe(CSP_TEMPLATE);
    expect(all?.get('x-content-type-options')).toBe('nosniff');
    expect(all?.get('referrer-policy')).toBe('no-referrer');
    const policy = all?.get('permissions-policy') ?? '';
    for (const feature of ['camera', 'microphone', 'geolocation', 'payment', 'usb']) {
      expect(policy, feature).toMatch(new RegExp(`(?:^|, )${feature}=\\(\\)(?:,|$)`));
    }
  });

  it("makes the site cross-origin isolated (plan 104: the runner's interrupts)", () => {
    expect(all?.get('cross-origin-opener-policy')).toBe('same-origin');
    expect(all?.get('cross-origin-embedder-policy')).toBe('require-corp');
  });
});

describe('favicon', () => {
  it('ships an SVG icon and a 32x32 ICO, both linked from the layout', () => {
    const svg = readFileSync(join(PUBLIC, 'favicon.svg'), 'utf-8');
    expect(svg).toMatch(/^<svg xmlns="http:\/\/www\.w3\.org\/2000\/svg" viewBox="0 0 32 32">/);
    expect(svg).not.toMatch(/\sstyle=|<style|href=/);
    const ico = readFileSync(join(PUBLIC, 'favicon.ico'));
    expect([...ico.subarray(0, 6)]).toEqual([0, 0, 1, 0, 1, 0]); // an icon with one image
    expect([ico[6], ico[7]]).toEqual([32, 32]);
    expect(ico.readUInt32LE(14) + ico.readUInt32LE(18)).toBe(ico.length);
    const layout = readFileSync(join(SITE, 'src', 'layouts', 'Base.astro'), 'utf-8');
    expect(layout).toContain('<link rel="icon" href="/favicon.svg" type="image/svg+xml" />');
    expect(layout).toContain('<link rel="icon" href="/favicon.ico" sizes="32x32" />');
  });
});

describe('the slide audit covers every site book', () => {
  const repo = repoRoot();
  const fixture = loadBook(join(import.meta.dirname, 'fixtures', 'bundles', 'demo'));

  it('names each audited book with its slide count on its last line', () => {
    const run = runAudit(repo, [fixture], ['demo']);
    expect(run.passed).toBe(true);
    expect(run.lines.at(-1)).toMatch(/^slide-audit: OK: 1 book\(s\): demo \(\d+ slides\)$/);
  });

  it('fails when a site book has no bundle', () => {
    const run = runAudit(repo, [fixture], ['demo', 'missing-book']);
    expect(run.passed).toBe(false);
    expect(run.lines).toContain('slide-audit: missing-book: FAIL no site bundle (run scripts/build-site.sh to export it)');
    expect(run.lines.at(-1)).toMatch(/^slide-audit: FAIL: /);
  });

  const hasReal = existsSync(CONTENT);
  it.skipIf(!hasReal)('lists all four real site books, each with its counts', () => {
    const expected = siteBookIds(repo);
    expect(expected).toEqual(['python-projects', 'python-concepts', 'usaco-bronze', 'acsl']);
    const run = runAudit(repo, loadBooks({ contentDir: CONTENT }), expected);
    expect(run.books.map((b) => b.book)).toEqual(expected);
    for (const id of expected) {
      expect(run.lines.some((l) => l.startsWith(`slide-audit: ${id}: `) && / slides; \d+ failing, \d+ allow-listed;/.test(l)), id).toBe(true);
    }
    expect(run.passed).toBe(true);
    expect(run.lines.at(-1)).toBe(`slide-audit: OK: 4 book(s): ${run.books.map((b) => `${b.book} (${b.slides} slides)`).join(', ')}`);
  });
});
