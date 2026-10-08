/**
 * Writes public/favicon.ico (32×32), a raster twin of public/favicon.svg: a blue rounded square
 * with a white `>_` prompt. Run once with `node scripts/favicon.ts` after changing the design;
 * the output is committed. No dependencies: the icon is a 32-bit BMP inside an ICO container.
 */
import { writeFileSync } from 'node:fs';

const SIZE = 32;
const BLUE = [0x0a, 0x58, 0xca];
const RADIUS = 6;
const HALF_STROKE = 1.5;
const SEGMENTS: [number, number, number, number][] = [
  [8, 10, 14, 16],
  [14, 16, 8, 22],
  [16, 22, 24, 22],
];

function inRoundedSquare(x: number, y: number): boolean {
  const cx = Math.min(Math.max(x, RADIUS), SIZE - RADIUS);
  const cy = Math.min(Math.max(y, RADIUS), SIZE - RADIUS);
  return (x - cx) ** 2 + (y - cy) ** 2 <= RADIUS ** 2;
}

function nearStroke(x: number, y: number): boolean {
  return SEGMENTS.some(([x1, y1, x2, y2]) => {
    const dx = x2 - x1;
    const dy = y2 - y1;
    const t = Math.max(0, Math.min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)));
    return (x - x1 - t * dx) ** 2 + (y - y1 - t * dy) ** 2 <= HALF_STROKE ** 2;
  });
}

/** BGRA rows, bottom-up, as a BMP inside an ICO stores them. */
function pixels(): Buffer {
  const out = Buffer.alloc(SIZE * SIZE * 4);
  const S = 4; // 4×4 supersampling
  for (let row = 0; row < SIZE; row++) {
    for (let col = 0; col < SIZE; col++) {
      let inside = 0;
      let white = 0;
      for (let i = 0; i < S; i++) {
        for (let j = 0; j < S; j++) {
          const x = col + (j + 0.5) / S;
          const y = row + (i + 0.5) / S;
          if (!inRoundedSquare(x, y)) continue;
          inside++;
          if (nearStroke(x, y)) white++;
        }
      }
      const mix = inside === 0 ? 0 : white / inside;
      const channel = (c: number) => Math.round(c + (255 - c) * mix);
      const at = ((SIZE - 1 - row) * SIZE + col) * 4;
      out[at] = channel(BLUE[2]!);
      out[at + 1] = channel(BLUE[1]!);
      out[at + 2] = channel(BLUE[0]!);
      out[at + 3] = Math.round((inside / (S * S)) * 255);
    }
  }
  return out;
}

const bgra = pixels();
const mask = Buffer.alloc((SIZE / 8) * SIZE); // the AND mask: all zero (alpha decides)
const header = Buffer.alloc(40);
header.writeUInt32LE(40, 0); // BITMAPINFOHEADER size
header.writeInt32LE(SIZE, 4);
header.writeInt32LE(SIZE * 2, 8); // XOR + AND masks
header.writeUInt16LE(1, 12); // planes
header.writeUInt16LE(32, 14); // bits per pixel
header.writeUInt32LE(bgra.length + mask.length, 20);
const image = Buffer.concat([header, bgra, mask]);

const dir = Buffer.alloc(6 + 16);
dir.writeUInt16LE(1, 2); // type: icon
dir.writeUInt16LE(1, 4); // one image
dir.writeUInt8(SIZE, 6);
dir.writeUInt8(SIZE, 7);
dir.writeUInt16LE(1, 10); // planes
dir.writeUInt16LE(32, 12); // bits per pixel
dir.writeUInt32LE(image.length, 14);
dir.writeUInt32LE(dir.length, 18);

writeFileSync(new URL('../public/favicon.ico', import.meta.url), Buffer.concat([dir, image]));
console.log('wrote public/favicon.ico');
