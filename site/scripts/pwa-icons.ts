/**
 * The web app manifest's PNG icons, rasterised at build time from public/favicon.svg (plan 105
 * Phase A: "icons generated locally from an SVG"; the generator is committed, the PNGs are build
 * output, never committed blobs). No dependencies: the favicon is one rounded `<rect>` and one
 * stroked `<path>` (round caps and joins), so a pixel is inside the rect, or within half the
 * stroke width of a path segment; 4×4 supersampling anti-aliases the edges. The PNG is RGBA,
 * filter 0, deflated with node:zlib.
 *
 * Only the SVG features the favicon uses are supported; anything else throws (so a redesign
 * cannot silently render wrong).
 */
import { crc32, deflateSync } from 'node:zlib';

export interface IconDesign {
  viewBox: number;
  rect: { rx: number; fill: [number, number, number] };
  stroke: { width: number; color: [number, number, number]; segments: [number, number, number, number][] };
}

const hex = (value: string): [number, number, number] => {
  const m = /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.exec(value.trim());
  if (!m) throw new Error(`icon: unsupported colour ${value}`);
  const h = m[1]!.length === 3 ? [...m[1]!].map((c) => c + c).join('') : m[1]!;
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
};

const attr = (tag: string, name: string): string | undefined => new RegExp(`\\s${name}="([^"]*)"`).exec(tag)?.[1];

/** Path data (M m L l H h V v Z z, implicit repeats) to line segments. */
export function pathSegments(d: string): [number, number, number, number][] {
  const tokens = d.match(/[MmLlHhVvZz]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?/g) ?? [];
  const out: [number, number, number, number][] = [];
  let x = 0;
  let y = 0;
  let startX = 0;
  let startY = 0;
  let command = '';
  let i = 0;
  const num = () => {
    const t = tokens[i++];
    if (t === undefined || /[A-Za-z]/.test(t)) throw new Error(`icon: bad path data ${d}`);
    return Number(t);
  };
  while (i < tokens.length) {
    if (/[A-Za-z]/.test(tokens[i]!)) command = tokens[i++]!;
    const rel = command === command.toLowerCase();
    switch (command.toUpperCase()) {
      case 'M': {
        const nx = num() + (rel ? x : 0);
        const ny = num() + (rel ? y : 0);
        [x, y, startX, startY] = [nx, ny, nx, ny];
        command = rel ? 'l' : 'L'; // further pairs are implicit line-tos
        break;
      }
      case 'L': {
        const nx = num() + (rel ? x : 0);
        const ny = num() + (rel ? y : 0);
        out.push([x, y, nx, ny]);
        [x, y] = [nx, ny];
        break;
      }
      case 'H': {
        const nx = num() + (rel ? x : 0);
        out.push([x, y, nx, y]);
        x = nx;
        break;
      }
      case 'V': {
        const ny = num() + (rel ? y : 0);
        out.push([x, y, x, ny]);
        y = ny;
        break;
      }
      case 'Z':
        out.push([x, y, startX, startY]);
        [x, y] = [startX, startY];
        break;
      default:
        throw new Error(`icon: unsupported path command ${command}`);
    }
  }
  return out;
}

/** Read the favicon's design: a square viewBox, one full-size rounded rect, one stroked path. */
export function parseIconSvg(svg: string): IconDesign {
  const viewBox = /viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"/.exec(svg);
  if (!viewBox || viewBox[1] !== viewBox[2]) throw new Error('icon: the SVG needs a square viewBox "0 0 N N"');
  const size = Number(viewBox[1]);
  const tags = svg.match(/<(?!svg|\/)[a-z]+\b[^>]*>/g) ?? [];
  if (tags.length !== 2 || !tags[0]!.startsWith('<rect') || !tags[1]!.startsWith('<path')) {
    throw new Error('icon: the SVG must be exactly one <rect> then one <path>');
  }
  const [rect, path] = tags as [string, string];
  if (Number(attr(rect, 'width')) !== size || Number(attr(rect, 'height')) !== size) throw new Error('icon: the rect must fill the viewBox');
  if (attr(path, 'stroke-linecap') !== 'round' || attr(path, 'stroke-linejoin') !== 'round' || attr(path, 'fill') !== 'none') {
    throw new Error('icon: the path must be an unfilled stroke with round caps and joins');
  }
  return {
    viewBox: size,
    rect: { rx: Number(attr(rect, 'rx') ?? 0), fill: hex(attr(rect, 'fill') ?? '#000') },
    stroke: { width: Number(attr(path, 'stroke-width') ?? 1), color: hex(attr(path, 'stroke') ?? '#000'), segments: pathSegments(attr(path, 'd') ?? '') },
  };
}

/**
 * Render the design to `size`×`size` RGBA. `maskable`: a full-bleed square background with the
 * design's foreground scaled into the central 80% safe zone (the platform applies its own mask).
 */
export function renderIcon(design: IconDesign, size: number, { maskable = false } = {}): Uint8Array {
  const rgba = new Uint8Array(size * size * 4);
  const S = 4;
  const unit = design.viewBox;
  const scale = size / unit;
  // In maskable icons the stroke is drawn at 80% around the centre; the background has no corners.
  const inner = maskable ? 0.8 : 1;
  const r = design.rect.rx;
  const inRect = (x: number, y: number) => {
    if (maskable) return true;
    const cx = Math.min(Math.max(x, r), unit - r);
    const cy = Math.min(Math.max(y, r), unit - r);
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r;
  };
  const half = design.stroke.width / 2;
  const onStroke = (x0: number, y0: number) => {
    const x = (x0 - unit / 2) / inner + unit / 2;
    const y = (y0 - unit / 2) / inner + unit / 2;
    return design.stroke.segments.some(([x1, y1, x2, y2]) => {
      const dx = x2 - x1;
      const dy = y2 - y1;
      const len = dx * dx + dy * dy;
      const t = len === 0 ? 0 : Math.max(0, Math.min(1, ((x - x1) * dx + (y - y1) * dy) / len));
      return (x - x1 - t * dx) ** 2 + (y - y1 - t * dy) ** 2 <= half * half;
    });
  };
  for (let row = 0; row < size; row++) {
    for (let col = 0; col < size; col++) {
      let inside = 0;
      let stroke = 0;
      for (let i = 0; i < S; i++) {
        for (let j = 0; j < S; j++) {
          const x = (col + (j + 0.5) / S) / scale;
          const y = (row + (i + 0.5) / S) / scale;
          if (!inRect(x, y)) continue;
          inside++;
          if (onStroke(x, y)) stroke++;
        }
      }
      const mix = inside === 0 ? 0 : stroke / inside;
      const at = (row * size + col) * 4;
      for (let c = 0; c < 3; c++) rgba[at + c] = Math.round(design.rect.fill[c]! + (design.stroke.color[c]! - design.rect.fill[c]!) * mix);
      rgba[at + 3] = Math.round((inside / (S * S)) * 255);
    }
  }
  return rgba;
}

function chunk(type: string, data: Uint8Array): Buffer {
  const head = Buffer.alloc(8);
  head.writeUInt32BE(data.length, 0);
  head.write(type, 4, 'latin1');
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([head.subarray(4), data])) >>> 0, 0);
  return Buffer.concat([head, data, crc]);
}

/** A PNG file of RGBA pixels. */
export function encodePng(rgba: Uint8Array, width: number, height: number): Buffer {
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8; // bit depth
  ihdr[9] = 6; // RGBA
  const raw = Buffer.alloc((width * 4 + 1) * height);
  for (let y = 0; y < height; y++) {
    raw[y * (width * 4 + 1)] = 0; // filter: none
    Buffer.from(rgba.buffer, rgba.byteOffset + y * width * 4, width * 4).copy(raw, y * (width * 4 + 1) + 1);
  }
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk('IHDR', ihdr),
    chunk('IDAT', deflateSync(raw, { level: 9 })),
    chunk('IEND', new Uint8Array(0)),
  ]);
}

/** The icon files the manifest names (dist-relative path, size, maskable). */
export const ICONS = [
  { path: 'icons/icon-192.png', size: 192, maskable: false },
  { path: 'icons/icon-512.png', size: 512, maskable: false },
  { path: 'icons/icon-maskable-512.png', size: 512, maskable: true },
  { path: 'icons/apple-touch-icon-180.png', size: 180, maskable: true },
] as const;
