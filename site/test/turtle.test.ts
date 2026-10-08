/** Turtle figures as inline SVG (plan 103, "Turtle SVG"). */
import { describe, expect, it } from 'vitest';
import { svgColour, turtleSvg, turtleViewBox } from '../src/lib/turtle';
import type { Segment } from '../src/lib/types';

const seg = (x1: number, y1: number, x2: number, y2: number, color = 'blue', width = 3): Segment =>
  ({ x1, y1, x2, y2, color, width });

// A square drawn up and to the right from the origin (turtle space, y up).
const square = [seg(0, 0, 82, 0), seg(82, 0, 82, 82), seg(82, 82, 0, 82), seg(0, 82, 0, 0)];

describe('turtle SVG', () => {
  it('pads the bounding box by 10 plus the widest stroke, in flipped space', () => {
    // pad = 10 + 3: x from -13 to 95; turtle y 0..82 flips to -82..0, so the box starts at -95.
    expect(turtleViewBox(square)).toEqual({ x: -13, y: -95, width: 108, height: 108 });
    // A segment below the origin: turtle y -40 flips to +40, the bottom of the box.
    expect(turtleViewBox([seg(0, 0, 0, -40, 'red', 1)])).toEqual({ x: -11, y: -11, width: 22, height: 62 });
  });

  it('flips y, draws a white background and keeps every segment', () => {
    const svg = turtleSvg(square, 'Drawing for Squares');
    expect(svg).toContain('viewBox="-13 -95 108 108"');
    expect(svg).toContain('<rect x="-13" y="-95" width="108" height="108" fill="white"/>');
    expect(svg).toContain('<g transform="scale(1,-1)"');
    expect(svg.match(/<line /g)).toHaveLength(4);
    expect(svg).toContain('<line x1="82" y1="0" x2="82" y2="82" stroke="blue" stroke-width="3"/>');
    expect(svg).not.toMatch(/\sstyle=/);
  });

  it('is an image with an accessible name', () => {
    const svg = turtleSvg(square, 'Drawing for <Squares> & "more"');
    expect(svg).toMatch(/^<svg [^>]*role="img"/);
    expect(svg).toContain('aria-label="Drawing for &lt;Squares&gt; &amp; &quot;more&quot;"');
  });

  it('passes colour keywords through and refuses anything else', () => {
    expect(svgColour('darkviolet')).toBe('darkviolet');
    expect(svgColour('#FF0000')).toBe('#ff0000');
    expect(svgColour('red" onload="x')).toBe('black');
    expect(svgColour('url(#a)')).toBe('black');
  });

  it('draws nothing for an empty figure', () => {
    expect(turtleSvg([], 'x')).toBe('');
  });
});
