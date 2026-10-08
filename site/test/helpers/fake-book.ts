/** A hand-built LoadedBook for the deck and mastery tests (only the fields they read). */
import type { LoadedBook } from '../../src/lib/bundle';
import type { Block, Card, Concept, Item } from '../../src/lib/types';

export function block(key: string, concepts: string[], code = 'print(1)', output = '1\n'): Block {
  return {
    key,
    type: 'code',
    code,
    output,
    needs_prelude: false,
    prelude: [],
    files: [],
    concepts,
    probe: 'standalone',
    tags: [],
  };
}

export function item(key: string, concepts: string[]): Item {
  return {
    key,
    kind: 'unit',
    number: 1,
    label: 'Exercise 1',
    title: 'Exercise 1',
    division: [],
    stretch: false,
    concepts,
    statement_md: 'Do it.',
    starter: '',
    files: [],
    check: { kind: 'self-check', requirements: ['It works.'], turtle: false, confirmed: true },
    answer_visibility: 'none',
    before: [],
  };
}

export function predict(blockKey: string, mode: 'typed' | 'flip' = 'typed', prelude: string[] = []): Card {
  return { key: `${blockKey}#predict`, kind: 'predict', block: blockKey, mode, prelude };
}

export function conceptCard(book: string, concept: string, term: string, distractors: string[] = ['a', 'b']): Card {
  return {
    key: `${book}/back-matter/glossary/${concept}`,
    kind: 'concept',
    concept,
    term,
    definition_md: `The \`${term}\` thing & <more>.`,
    mode: distractors.length ? 'choice' : 'flip',
    distractors,
  };
}

export interface FakeEntry {
  id: string;
  blocks?: Block[];
  cards?: Card[];
  items?: Item[];
}

export function fakeBook(id: string, concepts: Concept[], entries: FakeEntry[]): LoadedBook {
  const records = entries.map((e, i) => ({
    id: e.id,
    kind: 'unit' as const,
    title: `Unit ${i + 1}`,
    number: i + 1,
    file: `entries/${e.id}.json`,
  }));
  return {
    id,
    dir: `/fake/${id}`,
    book: {
      schema_version: '1.0.0',
      book: { id, title: 'Fake', subtitle: 'A fake book', flags: { acsl: false, judge: false } },
      release: { tag: 'unreleased', content_hash: `sha256:${'a'.repeat(64)}` },
      entries: records,
      concepts,
      glossary: [],
      reference_md: '',
      settings: { lesson_heading: '^## Lesson' },
      pdfs: null,
    },
    entries: entries.map((e, i) => ({
      record: records[i]!,
      data: {
        schema_version: '1.0.0',
        entry: { id: e.id, kind: 'unit', title: records[i]!.title },
        lesson: { blocks: e.blocks ?? [] },
        intro: [],
        items: e.items ?? [],
        outro: [],
        cards: e.cards ?? [],
        files: [],
      },
    })),
  };
}
