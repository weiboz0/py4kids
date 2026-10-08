/**
 * The schema-key check (plan 103, Architecture; the TypeScript twin of tests/site_consumer.py's
 * recording reader). `Recorder.wrap` hands the loader a recording proxy for each bundle document;
 * every key the site's code then reads is logged with its JSON pointer, and `undeclaredReads`
 * lists each read the bundle schema does not declare at that position.
 *
 * A key counts as declared when some subschema that applies to the instance (following `$ref`,
 * `allOf`, the valid `oneOf`/`anyOf` branches and the `if`/`then`/`else` branch taken) lists it
 * under `properties`. Reading an absent optional key that is declared is fine; reading a key the
 * schema never declares is a failure, present or not.
 */

import { bundleValidator, SCHEMA_ID } from '../../src/lib/bundle';

type Pointer = (string | number)[];
export interface Read {
  file: string;
  pointer: Pointer;
  key: string;
}

const IGNORED = new Set(['then', 'toJSON', 'constructor', '$$typeof', 'asymmetricMatch', 'nodeType']);

export class Recorder {
  reads: Read[] = [];
  raw = new Map<string, unknown>();
  private proxies = new WeakMap<object, unknown>();

  wrap = <T extends object>(data: T, file: string): T => {
    this.raw.set(file, data);
    return this.proxy(data, file, []) as T;
  };

  private proxy(value: unknown, file: string, pointer: Pointer): unknown {
    if (value === null || typeof value !== 'object') return value;
    const known = this.proxies.get(value);
    if (known) return known;
    const recorder = this;
    const isArray = Array.isArray(value);
    const made = new Proxy(value, {
      get(target, prop, receiver) {
        const result = Reflect.get(target, prop, receiver) as unknown;
        if (typeof prop !== 'string') return result;
        if (isArray) {
          return /^\d+$/.test(prop) ? recorder.proxy(result, file, [...pointer, Number(prop)]) : result;
        }
        if (!IGNORED.has(prop) && !(prop in Object.prototype && !Object.hasOwn(target, prop))) {
          recorder.reads.push({ file, pointer, key: prop });
        }
        return recorder.proxy(result, file, [...pointer, prop]);
      },
      has(target, prop) {
        if (!isArray && typeof prop === 'string') recorder.reads.push({ file, pointer, key: prop });
        return Reflect.has(target, prop);
      },
    });
    this.proxies.set(value, made);
    return made;
  }
}

type Node = Record<string, unknown>;

function resolvePointer(schema: unknown, pointer: string): Node {
  let node = schema as Node;
  for (const part of pointer.split('/').slice(1)) {
    node = node[part.replace(/~1/g, '/').replace(/~0/g, '~')] as Node;
  }
  return node;
}

const escape = (key: string) => key.replace(/~/g, '~0').replace(/\//g, '~1');

export function makeDeclared(schemaPath?: string) {
  const { ajv } = bundleValidator(schemaPath);
  const schema = ajv.getSchema(SCHEMA_ID)?.schema;
  const valid = (ptr: string, instance: unknown): boolean => {
    const fn = ajv.getSchema(`${SCHEMA_ID}#${ptr}`);
    if (!fn) throw new Error(`no subschema at ${ptr}`);
    return fn(instance) as boolean;
  };

  /** `ptr` (after any `$ref`) and every subschema pointer that applies to `instance`. */
  const candidates = (ptr: string, instance: unknown): string[] => {
    let node = resolvePointer(schema, ptr);
    while (typeof node.$ref === 'string') {
      ptr = node.$ref.replace(/^#/, '');
      node = resolvePointer(schema, ptr);
    }
    const out = [ptr];
    (node.allOf as unknown[] | undefined)?.forEach((_, i) => out.push(...candidates(`${ptr}/allOf/${i}`, instance)));
    for (const word of ['oneOf', 'anyOf']) {
      (node[word] as unknown[] | undefined)?.forEach((_, i) => {
        const sub = `${ptr}/${word}/${i}`;
        if (valid(sub, instance)) out.push(...candidates(sub, instance));
      });
    }
    if (node.if !== undefined) {
      const branch = valid(`${ptr}/if`, instance) ? 'then' : 'else';
      if (node[branch] !== undefined) out.push(...candidates(`${ptr}/${branch}`, instance));
    }
    return out;
  };

  const properties = (ptr: string): Node => (resolvePointer(schema, ptr).properties as Node | undefined) ?? {};

  return function declared(definition: string, raw: unknown, pointer: Pointer, key: string): boolean {
    let nodes = [`/$defs/${definition}`];
    let instance = raw;
    for (const step of pointer) {
      const children: string[] = [];
      for (const node of nodes) {
        for (const cand of candidates(node, instance)) {
          const candNode = resolvePointer(schema, cand);
          if (typeof step === 'number' && candNode.items !== undefined) children.push(`${cand}/items`);
          else if (typeof step === 'string' && step in properties(cand)) children.push(`${cand}/properties/${escape(step)}`);
        }
      }
      nodes = children;
      instance = (instance as Record<string | number, unknown>)[step];
    }
    return nodes.some((node) => candidates(node, instance).some((cand) => key in properties(cand)));
  };
}

/** The file's schema definition: `book.json` is a book_file, anything else an entry_file. */
export const definitionOf = (file: string) => (file === 'book.json' ? 'book_file' : 'entry_file');

/** Every distinct read the schema does not declare, as `file pointer key` strings. */
export function undeclaredReads(recorder: Recorder): string[] {
  const declared = makeDeclared();
  const seen = new Set<string>();
  const out: string[] = [];
  for (const read of recorder.reads) {
    const id = `${read.file} /${read.pointer.join('/')} ${read.key}`;
    if (seen.has(id)) continue;
    seen.add(id);
    if (!declared(definitionOf(read.file), recorder.raw.get(read.file), read.pointer, read.key)) out.push(id);
  }
  return out;
}

export function distinctReads(recorder: Recorder): number {
  return new Set(recorder.reads.map((r) => `${r.file} /${r.pointer.join('/')} ${r.key}`)).size;
}
