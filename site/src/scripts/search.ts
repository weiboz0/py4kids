/**
 * The search island (plan 103 Pages, `/search/`): the site's own small UI on Pagefind's JS API.
 * `/pagefind/pagefind.js` is the site's own file, written next to the pages by the build; it
 * loads its WebAssembly and index fragments from the same `/pagefind/` folder (the CSP allows
 * `'wasm-unsafe-eval'` for it). Nothing typed here is sent anywhere or saved.
 */

interface SubResult {
  title: string;
  url: string;
  excerpt: string;
  anchor?: { element: string; id: string; text?: string };
  weighted_locations?: { weight: number; balanced_score: number; location: number }[];
}

interface ResultData {
  url: string;
  excerpt: string;
  meta: Record<string, string | undefined>;
  sub_results?: SubResult[];
}

/**
 * On a practice page (one item shown at a time, plan 106), the item the hit is in: the sub-result
 * (a heading anchor, `#<anchor>-h`) that scores highest, so the link lands on that exercise rather
 * than on item 1. Other pages, and a hit outside any item heading, link to the page.
 */
function practiceTarget(data: ResultData): SubResult | null {
  if (!/\/practice\/(index\.html)?$/.test(data.url)) return null;
  let best: SubResult | null = null;
  let bestScore = 0;
  for (const sub of data.sub_results ?? []) {
    if (!sub.anchor?.id) continue;
    const score = (sub.weighted_locations ?? []).reduce((sum, w) => sum + w.balanced_score, 0);
    if (score > bestScore) {
      best = sub;
      bestScore = score;
    }
  }
  return best;
}

interface Pagefind {
  options(options: Record<string, unknown>): Promise<void>;
  debouncedSearch(
    term: string,
    options?: { filters?: Record<string, string> },
    ms?: number,
  ): Promise<{ results: { id: string; data(): Promise<ResultData> }[] } | null>;
}

const PAGE = 10;
/**
 * Pagefind's loader. The build moves Pagefind into a content-hashed folder (plan 105: every asset
 * URL is release-specific) and rewrites the search page's `data-pagefind` to name it.
 */
const PAGEFIND = '/pagefind/pagefind.js';

const root = document.querySelector<HTMLElement>('[data-search]');
if (root) void start(root);

async function start(root: HTMLElement): Promise<void> {
  const form = root.querySelector<HTMLFormElement>('[data-search-form]')!;
  const input = root.querySelector<HTMLInputElement>('[data-search-input]')!;
  const book = root.querySelector<HTMLSelectElement>('[data-search-book]');
  const status = root.querySelector<HTMLElement>('[data-search-status]')!;
  const list = root.querySelector<HTMLOListElement>('[data-search-results]')!;
  const more = root.querySelector<HTMLButtonElement>('[data-search-more]')!;
  const needsJs = root.querySelector<HTMLElement>('[data-search-needs-js]');

  let pagefind: Pagefind;
  try {
    pagefind = (await import(/* @vite-ignore */ root.dataset.pagefind ?? PAGEFIND)) as Pagefind;
    await pagefind.options({ excerptLength: 24 });
  } catch {
    if (needsJs) needsJs.textContent = 'Search is not available in this copy of the site (its index was not built).';
    return;
  }
  needsJs?.remove();
  form.hidden = false;

  let results: { data(): Promise<ResultData> }[] = [];
  let shown = 0;

  const showMore = async () => {
    const next = results.slice(shown, shown + PAGE);
    shown += next.length;
    const data = await Promise.all(next.map((r) => r.data()));
    for (const d of data) list.append(resultItem(d));
    more.hidden = shown >= results.length;
  };

  const search = async () => {
    const term = input.value.trim();
    const filters = book && book.value ? { book: book.value } : undefined;
    if (term === '') {
      results = [];
      list.replaceChildren();
      status.textContent = '';
      more.hidden = true;
      return;
    }
    const found = await pagefind.debouncedSearch(term, filters ? { filters } : {}, 250);
    if (found === null) return; // a newer search replaced this one
    results = found.results;
    shown = 0;
    list.replaceChildren();
    status.textContent =
      results.length === 0 ? `No pages match “${term}”.` : `${results.length} ${results.length === 1 ? 'page matches' : 'pages match'} “${term}”.`;
    await showMore();
  };

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    void search();
  });
  input.addEventListener('input', () => void search());
  book?.addEventListener('change', () => void search());
  more.addEventListener('click', () => void showMore());
  if (input.value) void search();
}

function resultItem(data: ResultData): HTMLLIElement {
  const li = document.createElement('li');
  li.className = 'search-result';
  const link = document.createElement('a');
  const sub = practiceTarget(data);
  link.href = sub ? sub.url : data.url;
  link.textContent = sub ? `${data.meta.title ?? data.url} › ${sub.title}` : (data.meta.title ?? data.url);
  const heading = document.createElement('p');
  heading.className = 'search-result-title';
  heading.append(link);
  li.append(heading);
  if (data.meta.book) {
    const where = document.createElement('p');
    where.className = 'search-result-book';
    where.textContent = data.meta.book;
    li.append(where);
  }
  const excerpt = document.createElement('p');
  excerpt.className = 'search-result-excerpt';
  excerpt.append(...excerptNodes(sub ? sub.excerpt : data.excerpt));
  li.append(excerpt);
  return li;
}

/** Pagefind's excerpt as text, keeping only its `<mark>` highlights. */
function excerptNodes(html: string): Node[] {
  const template = document.createElement('template');
  template.innerHTML = html; // inert: a template's content never runs or loads anything
  return [...template.content.childNodes].map((node) => {
    if (node.nodeName === 'MARK') {
      const mark = document.createElement('mark');
      mark.textContent = node.textContent;
      return mark;
    }
    return document.createTextNode(node.textContent ?? '');
  });
}
