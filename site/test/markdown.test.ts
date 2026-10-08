/** The Markdown pipeline (plan 103 Phase B tests). */
import { describe, expect, it } from 'vitest';
import { CONTAINER_LABELS, codeCss, divClasses, highlightCode, renderMarkdown } from '../src/lib/markdown';

const noStyle = (html: string) => expect(html).not.toMatch(/\sstyle=/);

describe('Pandoc fenced divs', () => {
  it.each(Object.keys(CONTAINER_LABELS))('renders the %s class', (cls) => {
    const html = renderMarkdown(`::: {.${cls}}\nInside **${cls}**.\n:::\n`);
    expect(html).toContain(`<div class="callout callout-${cls}">`);
    expect(html).toContain(`Inside <strong>${cls}</strong>.`);
    const label = CONTAINER_LABELS[cls];
    if (label) expect(html).toContain(`<p class="callout-label">${label}</p>`);
    else expect(html).not.toContain('callout-label');
    expect(html).not.toContain(':::');
  });

  it('renders an unknown class visibly, as a plain block', () => {
    const html = renderMarkdown('::: {.mystery}\nStill **here**.\n:::\n');
    expect(html).toContain('<div class="callout callout-unknown" data-div="mystery">');
    expect(html).toContain('Still <strong>here</strong>.');
    expect(html).not.toContain(':::');
  });

  it('reads the class list from Pandoc attributes', () => {
    expect(divClasses('{.notice}')).toEqual(['notice']);
    expect(divClasses(' {#x .realprog key=v .extra} ')).toEqual(['realprog', 'extra']);
    expect(divClasses('notice')).toEqual(['notice']);
    expect(divClasses('')).toEqual([]);
  });

  it('renders the realprog div as the real data writes it', () => {
    const html = renderMarkdown('Text.\n\n::: {.realprog}\nA real program does this.\n:::\n\nAfter.');
    expect(html).toContain('<p class="callout-label">Real program</p>');
    expect(html).toContain('<p>After.</p>');
  });
});

describe('raw blocks', () => {
  it('drops a {=latex} fence', () => {
    const html = renderMarkdown('Before.\n\n```{=latex}\n\\begin{pubfigure}\n\\end{pubfigure}\n```\n\nAfter.');
    expect(html).not.toContain('pubfigure');
    expect(html).not.toContain('{=latex}');
    expect(html).toContain('<p>Before.</p>');
    expect(html).toContain('<p>After.</p>');
  });

  it('drops inline raw latex', () => {
    const html = renderMarkdown('A `\\newpage`{=latex} B');
    expect(html).toBe('<p>A  B</p>\n');
  });

  it('shows any other raw format as escaped code, never as markup', () => {
    const html = renderMarkdown('```{=html}\n<script>x()</script>\n```');
    expect(html).not.toContain('<script>');
    expect(html).toContain('&lt;script&gt;');
  });
});

describe('HTML comments', () => {
  it('drops a comment line without splitting the paragraph (python-projects pattern marks)', () => {
    const html = renderMarkdown('Repeat until done (sentinel loop)\n<!-- pattern: sentinel-loop -->\nYou know when you are done.');
    expect(html).toBe('<p>Repeat until done (sentinel loop)\nYou know when you are done.</p>\n');
  });

  it('drops a comment between blocks, multi-line and inline comments', () => {
    expect(renderMarkdown('A.\n\n<!-- pattern: sentinel-loop -->\n**B.**')).toBe('<p>A.</p>\n<p><strong>B.</strong></p>\n');
    expect(renderMarkdown('A.\n<!-- one\ntwo -->\nB.')).toBe('<p>A.\nB.</p>\n');
    expect(renderMarkdown('A <!-- x --> B')).toBe('<p>A  B</p>\n');
  });

  it('keeps a comment inside code', () => {
    expect(renderMarkdown('Write `<!-- x -->` here.')).toContain('<code>&lt;!-- x --&gt;</code>');
    expect(renderMarkdown('```text\n<!-- kept -->\n```')).toContain('&#x3C;!-- kept -->');
  });
});

describe('tables', () => {
  it('renders a GFM pipe table with th scope and alignment classes', () => {
    const html = renderMarkdown('| Loop | Trips |\n|---|---:|\n| `range(3)` | 3 |\n');
    expect(html).toContain('<th scope="col">Loop</th>');
    expect(html).toContain('<th class="align-right" scope="col">Trips</th>');
    expect(html).toContain('<td class="align-right">3</td>');
    expect(html).toContain('<code>range(3)</code>');
    noStyle(html);
  });
});

describe('escaping', () => {
  it('escapes a raw <name> token instead of dropping it', () => {
    const html = renderMarkdown('Print `<name> is from <hometown>.` then <name> again.');
    expect(html).toContain('<code>&lt;name&gt; is from &lt;hometown&gt;.</code>');
    expect(html).toContain('then &lt;name&gt; again.');
    expect(html).not.toContain('<name>');
  });

  it('escapes <name> inside fenced code', () => {
    const html = renderMarkdown('```python\nprint("<name>")\n```');
    expect(html).not.toContain('<name>');
    expect(html).toContain('&#x3C;name>');
  });
});

describe('math (Pandoc tex_math_dollars, KaTeX MathML)', () => {
  it('keeps prices as text (python-concepts unit 3)', () => {
    const text =
      'Under 13 costs $6. Ages 13–17 cost $8 on weekdays or $9 on Saturday/Sunday.';
    const html = renderMarkdown(text);
    expect(html).toBe(`<p>${text}</p>\n`);
    expect(html).not.toContain('<math');
  });

  it('renders $\\overline{A}$ as MathML (acsl unit 8)', () => {
    const html = renderMarkdown('| ACSL paper | This book |\n|---|---|\n| $\\overline{A}$ | `~A` |\n');
    expect(html).toContain('<math xmlns="http://www.w3.org/1998/Math/MathML">');
    expect(html).toContain('<mi>A</mi>');
    expect(html).toContain('<annotation encoding="application/x-tex">\\overline{A}</annotation>');
    expect(html).not.toContain('$');
    noStyle(html);
  });

  it('follows the opening and closing rules', () => {
    expect(renderMarkdown('a $ x$ b')).not.toContain('<math');
    expect(renderMarkdown('a $x $ b')).not.toContain('<math');
    expect(renderMarkdown('from $x$5 on')).not.toContain('<math');
    expect(renderMarkdown('a \\$x$ b')).not.toContain('<math');
    expect(renderMarkdown('a $x$ b')).toContain('<math');
    expect(renderMarkdown('`$x$`')).not.toContain('<math');
  });

  it('renders $$…$$ as display math', () => {
    const html = renderMarkdown('$$\\overline{A\\overline{B} + C} + AB$$');
    expect(html).toContain('display="block"');
    noStyle(html);
  });

  it('shows a formula KaTeX cannot parse as code', () => {
    expect(renderMarkdown('bad $\\frac{1$ here')).toContain('<code class="math-error">\\frac{1</code>');
  });
});

describe('code', () => {
  it('highlights with classes, never inline styles', () => {
    const html = highlightCode('def f(x):\n    return x + 1\n');
    expect(html).toMatch(/^<pre class="shiki [^"]*"/);
    expect(html).toContain('class="sh-');
    noStyle(html);
    expect(codeCss()).toMatch(/\.sh-[a-z0-9]+\{--shiki-light:#[0-9a-fA-F]+;--shiki-dark:/);
    expect(codeCss()).toContain(":root[data-theme='dark'] .shiki span{color:var(--shiki-dark)}");
  });

  it('highlights a fenced block and renders text fences plainly', () => {
    expect(renderMarkdown('```python\nx = 1\n```')).toContain('class="sh-');
    const text = renderMarkdown('```text\n3 4\n```');
    expect(text).toContain('3 4');
    noStyle(text);
  });

  it('never renders an image', () => {
    const html = renderMarkdown('![a cat](https://example.com/cat.png)');
    expect(html).not.toContain('<img');
    expect(html).toContain('a cat');
  });
});
