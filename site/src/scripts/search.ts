/**
 * The search island (plan 103 Pages, `/search/`): the site's own small UI on Pagefind's JS API.
 * `/pagefind/pagefind.js` is the site's own file, written next to the pages by the build; it
 * loads its WebAssembly and index fragments from the same `/pagefind/` folder (the CSP allows
 * `'wasm-unsafe-eval'` for it). Nothing typed here is sent anywhere or saved.
 */

interface ResultData {
  url: string;
  excerpt: string;
  meta: Record<string, string | undefined>;
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
    pagefind = (await import(/* @vite-ignore */ PAGEFIND)) as Pagefind;
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
  link.href = data.url;
  link.textContent = data.meta.title ?? data.url;
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
  excerpt.append(...excerptNodes(data.excerpt));
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
