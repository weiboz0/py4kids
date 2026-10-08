/**
 * Types for the plan-101 site bundle, hand-written to
 * `tools/export/schema/bundle.schema.json` (schema_version 1.1.0; design 012 D3, D11).
 *
 * The schema is the authority: the loader validates every file against it with Ajv, and
 * `site/test/schema-keys.test.ts` proves every key the site's code reads is declared there.
 * When the schema changes, change these types in the same commit.
 */

export type Sha256 = `sha256:${string}`;
/** `book/entry/notebook/cell_id`, plus `#<part>` for a part split out of one cell. */
export type Key = string;
export type ConceptId = string;
export type DivisionId = string;
export type EntryId = string;
export type EntryKind = 'unit' | 'checkpoint' | 'project';
/** `files/<entry-id>/<path relative to the entry dir>`. */
export type BundlePath = string;

export interface AnswerFormat {
  case: 'sensitive' | 'insensitive';
  hint: string;
}

/** One pen-down turtle move. Turtle space has y pointing up. */
export interface Segment {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  color: string;
  width: number;
}

/** One turtle drawing of an odd answer (plan 104 C), drawn in place of its TikZ. */
export interface AnswerFigure {
  caption: string;
  segments: Segment[];
}

export type ProseBlockType = 'prose' | 'opener' | 'notice' | 'goals' | 'recap';
export type CodeBlockType =
  | 'code'
  | 'tryit'
  | 'error-demo'
  | 'hang-demo'
  | 'turtle-figure'
  | 'program'
  | 'starter';
export type BlockType = ProseBlockType | CodeBlockType;

export interface Block {
  key: Key;
  type: BlockType;
  /** Markdown; present on prose-like blocks. */
  md?: string;
  /** Python source; present on code-like blocks. */
  code?: string;
  /** The stored stream output. */
  output?: string;
  route?: string;
  stdin?: boolean;
  sample_input?: string;
  /** The turtle drawing; present on turtle-figure blocks. */
  figure?: Segment[];
  needs_prelude: boolean;
  prelude: Key[];
  files: BundlePath[];
  concepts: ConceptId[];
  probe: 'standalone' | 'prelude' | 'mismatch' | null;
  tags: string[];
}

/** An intro, outro or item `before` block. */
export interface SideBlock extends Block {
  type: 'prose' | 'notice' | 'goals' | 'recap' | 'starter';
}

export interface FixtureCase {
  n: number;
  in_file: string;
  /** Never rendered unless `sample` (plan 103: hidden answers stay hidden). */
  out_file: string;
  sample: boolean;
}

interface CheckBase {
  turtle: boolean;
  confirmed: boolean;
}

export interface CheckFixtures extends CheckBase {
  kind: 'fixtures';
  cases: FixtureCase[];
  match: 'line' | 'token';
  over_budget: number[];
  /** The reference solver's max CPython ms (rounded up to 100); budget max(1 s, 10x), cap 10 s. */
  cpu_ms: number;
}

/** `hash` is never shown (plan 103). */
export interface CheckAnswer extends CheckBase {
  kind: 'answer';
  hash: Sha256;
  answer_format: AnswerFormat;
}

/** `source` is never printed (plan 103; design 012 D5). */
export interface CheckAsserts extends CheckBase {
  kind: 'asserts';
  source: string;
  functions: string[];
}

export interface CheckExpectedOutput extends CheckBase {
  kind: 'expected-output';
  hash: Sha256;
  answer_format: AnswerFormat;
}

export interface CheckPredict extends CheckBase {
  kind: 'predict';
  hash: Sha256;
  answer_format: AnswerFormat;
  program: string;
}

export interface CheckSelf extends CheckBase {
  kind: 'self-check';
  requirements: string[];
}

export type Check =
  | CheckFixtures
  | CheckAnswer
  | CheckAsserts
  | CheckExpectedOutput
  | CheckPredict
  | CheckSelf;

export interface Item {
  key: Key;
  kind: 'unit' | 'challenge' | 'checkpoint' | 'project';
  number: number | null;
  label: string;
  title: string;
  division: DivisionId[];
  stretch: boolean;
  concepts: ConceptId[];
  statement_md: string;
  starter: string;
  files: BundlePath[];
  check: Check;
  answer_visibility: 'after-attempt' | 'none';
  /** Present only when `answer_visibility` is `after-attempt`. Part B never renders it. */
  answer_md?: string;
  /** The answer's turtle drawings; odd turtle answers only (plan 104 C). */
  answer_figures?: AnswerFigure[];
  before: SideBlock[];
}

export interface PredictCard {
  key: Key;
  kind: 'predict';
  block: Key;
  mode: 'typed' | 'flip';
  prelude: Key[];
}

export interface ConceptCard {
  key: string;
  kind: 'concept';
  concept: ConceptId;
  term: string;
  definition_md: string;
  mode: 'choice' | 'flip';
  /** 1–3 terms for `choice`, none for `flip`. */
  distractors: string[];
}

export type Card = PredictCard | ConceptCard;

export interface EntryRecord {
  id: EntryId;
  kind: EntryKind;
  title: string;
  number: number | null;
  /** `entries/<entry-id>.json`, relative to the bundle directory. */
  file: string;
}

export interface Concept {
  id: ConceptId;
  name: string;
  category: string;
}

export interface GlossaryTerm {
  term: string;
  definition_md: string;
  concept: ConceptId;
  units: number[];
}

export type PdfEdition = 'student-print' | 'student' | 'answer-key' | 'teacher';

export interface BookFile {
  schema_version: '1.1.0';
  book: {
    id: string;
    title: string;
    subtitle: string;
    flags: { acsl: boolean; judge: boolean };
  };
  release: { tag: string; content_hash: Sha256 };
  /** In syllabus order. */
  entries: EntryRecord[];
  concepts: Concept[];
  glossary: GlossaryTerm[];
  reference_md: string;
  settings: { lesson_heading: string; acsl_divisions?: DivisionId[] };
  /** Release PDF links by edition; null when unreleased. */
  pdfs: Record<PdfEdition, string> | null;
}

export interface EntryFile {
  schema_version: '1.1.0';
  entry: { id: EntryId; kind: EntryKind; title: string };
  lesson: { blocks: Block[] } | null;
  intro: SideBlock[];
  items: Item[];
  outro: SideBlock[];
  cards: Card[];
  files: BundlePath[];
}
