/**
 * Turtle figures as inline SVG (plan 103, "Turtle SVG"): no image file, no data: URL, no style
 * attribute. Turtle space has y pointing up, so the drawing is flipped with `scale(1,-1)`; the
 * viewBox is the segments' bounding box (in flipped space), padded by 10 units plus the widest
 * stroke; a fixed white background keeps black strokes visible in dark mode. Colours are the
 * turtle's colour names, passed through as SVG colour keywords (anything else draws black).
 */

import type { Segment } from './types';
import { escapeHtml } from './markdown';

export const PAD = 10;

/** A turtle colour as an SVG paint: a keyword or a hex colour, else black. */
export function svgColour(colour: string): string {
  const c = colour.trim();
  return /^[a-zA-Z]{1,40}$/.test(c) || /^#(?:[0-9a-fA-F]{3}){1,2}$/.test(c) ? c.toLowerCase() : 'black';
}

const num = (n: number) => String(Math.round(n * 1000) / 1000);

export interface ViewBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

/** The padded bounding box, in the flipped (SVG) coordinates the figure is drawn in. */
export function turtleViewBox(segments: Segment[]): ViewBox {
  const xs = segments.flatMap((s) => [s.x1, s.x2]);
  const ys = segments.flatMap((s) => [s.y1, s.y2]);
  const pad = PAD + Math.max(0, ...segments.map((s) => s.width));
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  // After scale(1,-1) a turtle y becomes -y: the top of the drawing is -maxY.
  return { x: minX - pad, y: -maxY - pad, width: maxX - minX + 2 * pad, height: maxY - minY + 2 * pad };
}

/** The figure as an inline `<svg role="img" aria-label=…>`. */
export function turtleSvg(segments: Segment[], label: string): string {
  if (segments.length === 0) return '';
  const box = turtleViewBox(segments);
  const lines = segments
    .map(
      (s) =>
        `<line x1="${num(s.x1)}" y1="${num(s.y1)}" x2="${num(s.x2)}" y2="${num(s.y2)}" ` +
        `stroke="${escapeHtml(svgColour(s.color))}" stroke-width="${num(s.width)}"/>`,
    )
    .join('');
  return (
    `<svg class="turtle-figure" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${escapeHtml(label)}" ` +
    `viewBox="${num(box.x)} ${num(box.y)} ${num(box.width)} ${num(box.height)}" ` +
    `width="${num(box.width)}" height="${num(box.height)}">` +
    `<rect x="${num(box.x)}" y="${num(box.y)}" width="${num(box.width)}" height="${num(box.height)}" fill="white"/>` +
    `<g transform="scale(1,-1)" fill="none" stroke-linecap="round" stroke-linejoin="round">${lines}</g></svg>`
  );
}
