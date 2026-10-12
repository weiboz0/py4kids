/**
 * The site's offline post-build (plan 105 Phases A and D) on a small synthetic dist: icons from the
 * SVG, release-specific asset names, and the per-book download manifests (the manifest builder).
 */
import { existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, sep } from 'node:path';
import { gzipSync, inflateSync } from 'node:zlib';
import { afterAll, describe, expect, it } from 'vitest';
import { hashedName, releaseSpecificViolations } from '../scripts/fingerprint';
import { assetImports, buildBookManifest, fileOf, htmlLoads, urlOf } from '../scripts/offline-manifest';
import { pwaBuild } from '../scripts/pwa-build';
import { encodePng, parseIconSvg, pathSegments, renderIcon } from '../scripts/pwa-icons';

const SITE = join(import.meta.dirname, '..');
const scratch = join(SITE, 'node_modules', '.cache');
mkdirSync(scratch, { recursive: true });
const work = mkdtempSync(join(scratch, 'py4kids-pwa-'));
afterAll(() => rmSync(work, { recursive: true, force: true }));

const FAVICON = readFileSync(join(SITE, 'public', 'favicon.svg'), 'utf-8');

function fragment(url: string): Buffer {
  return gzipSync(Buffer.from(`pagefind_dcd${JSON.stringify({ url, meta: {} })}`));
}

function page(body: string, contentHash = false): string {
  return `<!doctype html><html><head><script src="/scripts/theme.js"></script><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.ico" sizes="32x32"><link rel="manifest" href="/manifest.webmanifest"><link rel="stylesheet" href="/code.css"><link rel="stylesheet" href="/_astro/Base.Ab12Cd34.css"></head><body${contentHash ? ' data-content-hash="sha256:1"' : ''}>${body}<script type="module" src="/_astro/page.Xy12Zw34.js"></script></body></html>`;
}

function fakeDist(name: string): string {
  const dist = join(work, name);
  const put = (path: string, data: string | Buffer) => {
    mkdirSync(dirname(join(dist, path)), { recursive: true });
    writeFileSync(join(dist, path), data);
  };
  put('favicon.svg', FAVICON);
  put('favicon.ico', Buffer.from([0, 0, 1, 0]));
  put('scripts/theme.js', '/* theme */');
  put('code.css', '.sh-1{}');
  put('manifest.webmanifest', readFileSync(join(SITE, 'public', 'manifest.webmanifest'), 'utf-8'));
  put('_astro/Base.Ab12Cd34.css', 'body{}');
  put('_astro/page.Xy12Zw34.js', 'import{a}from"./shared.Qq11Ww22.js";const e=()=>import("./editor.Ee55Rr66.js");');
  put('_astro/shared.Qq11Ww22.js', 'export const a=1;');
  put('_astro/editor.Ee55Rr66.js', 'export default 2;');
  put('_astro/unused.Uu00Ii99.js', 'export default 3;');
  put('index.html', page('<a href="/demo/">demo</a>'));
  put('search/index.html', page('<section data-search data-pagefind="/pagefind/pagefind.js"></section>'));
  put('demo/index.html', page('<a href="/demo/u1/">u1</a>', true));
  put('demo/u1/index.html', page('<p>lesson</p>'));
  put('demo/u1/practice/check/e1.json', '{"key":"demo:u1:e1"}');
  put('demo/files/u1/fixtures/1.in', '1\n');
  put('other/index.html', page('', true));
  put('pagefind/pagefind.js', 'export {}');
  put('pagefind/pagefind-worker.js', '');
  put('pagefind/pagefind-entry.json', '{}');
  put('pagefind/wasm.en.pagefind', 'w');
  put('pagefind/index/en_1.pf_index', 'i');
  put('pagefind/filter/en_1.pf_filter', 'f');
  put('pagefind/fragment/en_a.pf_fragment', fragment('/demo/u1/'));
  put('pagefind/fragment/en_b.pf_fragment', fragment('/other/'));
  put('_headers', '/*\n');
  return dist;
}

function tree(dir: string): Record<string, string> {
  const out: Record<string, string> = {};
  const walk = (d: string) => {
    for (const e of readdirSync(d, { withFileTypes: true })) {
      if (e.isDirectory()) walk(join(d, e.name));
      else out[relative(dir, join(d, e.name)).split(sep).join('/')] = readFileSync(join(d, e.name)).toString('base64');
    }
  };
  walk(dir);
  return out;
}

describe('the icons (rasterised from public/favicon.svg)', () => {
  it('reads the favicon design', () => {
    const design = parseIconSvg(FAVICON);
    expect(design.viewBox).toBe(32);
    expect(design.rect.fill).toEqual([0x0a, 0x58, 0xca]);
    expect(design.stroke.segments).toEqual([
      [8, 10, 14, 16],
      [14, 16, 8, 22],
      [16, 22, 24, 22],
    ]);
    expect(pathSegments('M0 0H4V4Z')).toEqual([
      [0, 0, 4, 0],
      [4, 0, 4, 4],
      [4, 4, 0, 0],
    ]);
    expect(() => parseIconSvg(FAVICON.replace('<path', '<circle r="1"/><path'))).toThrow();
  });

  it('writes a valid PNG: rounded corners transparent, the stroke white, the background blue', () => {
    const design = parseIconSvg(FAVICON);
    const size = 64;
    const rgba = renderIcon(design, size);
    const at = (x: number, y: number) => [...rgba.subarray((y * size + x) * 4, (y * size + x) * 4 + 4)];
    expect(at(0, 0)[3]).toBe(0); // corner, outside the rounded rect
    expect(at(4, 32)).toEqual([0x0a, 0x58, 0xca, 255]);
    expect(at(40, 44)).toEqual([255, 255, 255, 255]); // on the underscore (16..24, 22) * 2
    const maskable = renderIcon(design, size, { maskable: true });
    expect(maskable[3]).toBe(255); // full bleed
    const png = encodePng(rgba, size, size);
    expect([...png.subarray(0, 8)]).toEqual([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
    expect(png.readUInt32BE(16)).toBe(size);
    expect(png.subarray(12, 16).toString('latin1')).toBe('IHDR');
    const idatLength = png.readUInt32BE(33);
    expect(png.subarray(37, 41).toString('latin1')).toBe('IDAT');
    expect(inflateSync(png.subarray(41, 41 + idatLength)).length).toBe((size * 4 + 1) * size);
  });
});

describe('the manifest builder', () => {
  it('maps dist paths and URLs both ways', () => {
    expect(urlOf('index.html')).toBe('/');
    expect(urlOf('demo/u1/index.html')).toBe('/demo/u1/');
    expect(fileOf('/demo/u1/')).toBe('demo/u1/index.html');
    expect(fileOf('/demo/files/a%20b.txt?x=1')).toBe('demo/files/a b.txt');
  });

  it('finds what a page loads, not where it links', () => {
    expect(htmlLoads(page('<a href="/elsewhere/">x</a><img src="/demo/f.svg">')).sort()).toEqual(
      ['/_astro/Base.Ab12Cd34.css', '/_astro/page.Xy12Zw34.js', '/code.css', '/demo/f.svg', '/favicon.ico', '/favicon.svg', '/manifest.webmanifest', '/scripts/theme.js'].sort(),
    );
    expect(assetImports('import{a}from"./b.X1.js";import("./c.Y2.js");__vite(["_astro/d.Z3.js"])', '/_astro/a.js').sort()).toEqual(
      ['/_astro/b.X1.js', '/_astro/c.Y2.js', '/_astro/d.Z3.js'].sort(),
    );
  });

  it('lists the book, the assets its pages import (transitively), and its Pagefind fragments only', async () => {
    const dist = fakeDist('one');
    await pwaBuild(dist);
    const manifests = readdirSync(join(dist, '_offline'));
    expect(manifests.map((m) => m.split('.')[0]).sort()).toEqual(['demo', 'other']);
    const demo = JSON.parse(readFileSync(join(dist, '_offline', manifests.find((m) => m.startsWith('demo.'))!), 'utf-8'));
    const urls: string[] = demo.files.map((f: { url: string }) => f.url);
    expect(urls).toContain('/demo/');
    expect(urls).toContain('/demo/u1/');
    expect(urls).toContain('/demo/u1/practice/check/e1.json');
    expect(urls).toContain('/demo/files/u1/fixtures/1.in');
    for (const asset of ['/_astro/page.Xy12Zw34.js', '/_astro/shared.Qq11Ww22.js', '/_astro/editor.Ee55Rr66.js', '/_astro/Base.Ab12Cd34.css']) expect(urls).toContain(asset);
    expect(urls).not.toContain('/_astro/unused.Uu00Ii99.js');
    expect(urls.some((u) => /^\/code\.[0-9a-f]{10}\.css$/.test(u))).toBe(true);
    expect(urls.some((u) => /^\/manifest\.[0-9a-f]{10}\.webmanifest$/.test(u))).toBe(true);
    expect(urls.some((u) => /^\/icons\/icon-192\.[0-9a-f]{10}\.png$/.test(u))).toBe(true);
    expect(urls.some((u) => /^\/pagefind\/[0-9a-f]{10}\/fragment\/en_a\.pf_fragment$/.test(u))).toBe(true);
    expect(urls.some((u) => u.endsWith('/fragment/en_b.pf_fragment'))).toBe(false);
    expect(urls.some((u) => u.startsWith('/other/'))).toBe(false);
    expect(demo.count).toBe(urls.length);
    expect(demo.bytes).toBe(demo.files.reduce((n: number, f: { bytes: number }) => n + f.bytes, 0));
    expect(demo.content_hash).toMatch(/^[0-9a-f]{64}$/);
    // Every listed URL is a file of dist/ (caching copies only what is already there).
    for (const url of urls) expect(existsSync(join(dist, fileOf(url))), url).toBe(true);
  });

  it('is deterministic: two builds of the same dist are byte-identical', async () => {
    const a = fakeDist('det-a');
    const b = fakeDist('det-b');
    await pwaBuild(a);
    await pwaBuild(b);
    expect(tree(a)).toEqual(tree(b));
  });

  it("changes a book's content hash with its files and the assets it loads, not with other pages", async () => {
    const hashOf = async (name: string, edit: (dist: string) => void) => {
      const dist = fakeDist(name);
      edit(dist);
      await pwaBuild(dist);
      const m = readdirSync(join(dist, '_offline')).find((f) => f.startsWith('demo.'))!;
      return JSON.parse(readFileSync(join(dist, '_offline', m), 'utf-8')).content_hash as string;
    };
    const base = await hashOf('h0', () => {});
    expect(await hashOf('h1', (d) => writeFileSync(join(d, 'index.html'), page('<p>new home</p>')))).toBe(base);
    expect(await hashOf('h2', (d) => writeFileSync(join(d, 'demo', 'files', 'u1', 'fixtures', '1.in'), '2\n'))).not.toBe(base);
    expect(await hashOf('h3', (d) => writeFileSync(join(d, '_astro', 'shared.Qq11Ww22.js'), 'export const a=2;'))).not.toBe(base);
  });

  it('refuses a page that loads a file not in dist/', () => {
    const dist = fakeDist('missing');
    writeFileSync(join(dist, 'demo', 'u1', 'index.html'), page('<img src="/nowhere.png">'));
    expect(() => buildBookManifest(dist, 'demo')).toThrow(/nowhere\.png/);
  });
});

describe('release-specific asset URLs', () => {
  it('renames the root assets and Pagefind, and rewrites the pages', async () => {
    const dist = fakeDist('fp');
    await pwaBuild(dist);
    const home = readFileSync(join(dist, 'index.html'), 'utf-8');
    expect(home).toMatch(/src="\/scripts\/theme\.[0-9a-f]{10}\.js"/);
    expect(home).toMatch(/href="\/code\.[0-9a-f]{10}\.css"/);
    expect(home).toMatch(/href="\/manifest\.[0-9a-f]{10}\.webmanifest"/);
    expect(home).not.toMatch(/"\/(?:code\.css|favicon\.svg|scripts\/theme\.js|manifest\.webmanifest)"/);
    expect(readFileSync(join(dist, 'search', 'index.html'), 'utf-8')).toMatch(/data-pagefind="\/pagefind\/[0-9a-f]{10}\/pagefind\.js"/);
    expect(existsSync(join(dist, 'pagefind', 'pagefind.js'))).toBe(false);
    const manifest = readdirSync(dist).find((f) => f.endsWith('.webmanifest'))!;
    const icons = (JSON.parse(readFileSync(join(dist, manifest), 'utf-8')) as { icons: { src: string }[] }).icons;
    for (const icon of icons) expect(existsSync(join(dist, fileOf(icon.src))), icon.src).toBe(true);
    expect(releaseSpecificViolations(dist, ['demo', 'other'])).toEqual([]);
  });

  it('names a stable-named asset outside the books', () => {
    const dist = fakeDist('stable');
    writeFileSync(join(dist, 'stray.js'), '');
    expect(releaseSpecificViolations(dist, ['demo', 'other'])).toContain('stray.js');
    expect(hashedName('a/b.css', Buffer.from('x'))).toMatch(/^a\/b\.[0-9a-f]{10}\.css$/);
  });

});
