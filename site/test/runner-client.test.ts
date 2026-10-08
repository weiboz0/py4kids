/**
 * The runner client's message binding (plan 104 Phase A, D7): a reply is accepted only from the
 * runner origin, from the iframe's own window, as a valid envelope, for a pending id (of the
 * right type and session); every request is posted with the exact runner origin; requests time
 * out as "runner unavailable". The browser proofs are in e2e/runner.spec.ts.
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import { RunnerClient, RunnerUnavailableError, RunnerVersionError, type Incoming, type ResultReply } from '../src/lib/runner-client';

const ORIGIN = 'http://localhost:4392';

function harness(timeouts = { bootMs: 1000, runSlackMs: 1000 }) {
  const posted: { message: any; targetOrigin: string }[] = [];
  const frame = { postMessage: (message: unknown, targetOrigin: string) => posted.push({ message, targetOrigin }) };
  let handler: ((event: Incoming) => void) | null = null;
  let current: typeof frame | null = frame;
  let n = 0;
  const client = new RunnerClient({
    runnerOrigin: ORIGIN,
    frame: () => current,
    listen: (h) => {
      handler = h;
      return () => {
        handler = null;
      };
    },
    timeouts,
    newId: () => `id-${++n}`,
  });
  const deliver = (event: Incoming) => handler?.(event);
  return { client, frame, posted, deliver, setFrame: (f: typeof frame | null) => (current = f), listening: () => handler !== null };
}

function resultFor(id: string, session: string, extra: Partial<ResultReply> = {}): ResultReply {
  return {
    v: 2,
    type: 'result',
    id,
    session,
    stdout: 'hi\n',
    stderr: '',
    results: [],
    timing: { boot_ms: 1, run_ms: 2, restart_ms: 0 },
    status: 'ok',
    interrupts: 'sab',
    session_new: true,
    truncated: false,
    segments: [],
    ...extra,
  };
}

const flush = () => new Promise((r) => setTimeout(r, 0));

afterEach(() => {
  vi.useRealTimers();
});

describe('RunnerClient', () => {
  it('posts a valid run envelope with the exact runner origin, and accepts the matching result', async () => {
    const { client, frame, posted, deliver } = harness();
    const { id, result } = client.run({ session: 'u01', code: 'print("hi")' });
    await flush();
    expect(posted).toEqual([
      {
        message: { v: 2, type: 'run', id, session: 'u01', code: 'print("hi")', stdin: '', files: [], check: null, budget_ms: 5000 },
        targetOrigin: ORIGIN,
      },
    ]);
    expect(client.receive({ origin: ORIGIN, source: frame, data: resultFor(id, 'u01') })).toBe('accepted');
    await expect(result).resolves.toMatchObject({ stdout: 'hi\n' });
    expect(client.isPending(id)).toBe(false);
    // the same reply again: the id is completed, so it is dropped
    expect(client.receive({ origin: ORIGIN, source: frame, data: resultFor(id, 'u01') })).toBe('unknown-id');
    void deliver;
  });

  it('drops a reply from the wrong origin', async () => {
    const { client, frame } = harness();
    const { id } = client.run({ session: 's', code: '' });
    for (const origin of ['http://127.0.0.1:4391', 'http://localhost:4393', 'https://localhost:4392', 'null', '']) {
      expect(client.receive({ origin, source: frame, data: resultFor(id, 's') })).toBe('wrong-origin');
    }
    expect(client.isPending(id)).toBe(true);
  });

  it('drops a reply from another window on the runner origin (wrong source)', async () => {
    const { client, setFrame } = harness();
    const { id, result } = client.run({ session: 's', code: '' });
    await flush();
    result.catch(() => {});
    const popup = { postMessage: () => {} };
    expect(client.receive({ origin: ORIGIN, source: popup, data: resultFor(id, 's') })).toBe('wrong-source');
    expect(client.receive({ origin: ORIGIN, source: null, data: resultFor(id, 's') })).toBe('wrong-source');
    setFrame(null);
    expect(client.receive({ origin: ORIGIN, source: popup, data: resultFor(id, 's') })).toBe('wrong-source');
    expect(client.isPending(id)).toBe(true);
  });

  it('drops a reply for an unknown id, the wrong reply type, or the wrong session', async () => {
    const { client, frame } = harness();
    const { id } = client.run({ session: 's', code: '' });
    expect(client.receive({ origin: ORIGIN, source: frame, data: resultFor('nobody', 's') })).toBe('unknown-id');
    expect(client.receive({ origin: ORIGIN, source: frame, data: resultFor(id, 'other') })).toBe('unknown-id');
    const ready = { v: 2, type: 'ready', id, python: '3.12', pyodide: '0.27.8', isolated: true, boot_ms: 1 };
    expect(client.receive({ origin: ORIGIN, source: frame, data: ready })).toBe('unknown-id');
    expect(client.isPending(id)).toBe(true);
  });

  it('drops an invalid envelope', async () => {
    const { client, frame } = harness();
    const { id } = client.run({ session: 's', code: '' });
    const bad: unknown[] = [
      null,
      'result',
      { ...resultFor(id, 's'), extra: 1 },
      { ...resultFor(id, 's'), status: 'passed' },
      { ...resultFor(id, 's'), stdout: 5 },
      { ...resultFor(id, 's'), id: '../x' },
      { v: 2, type: 'run', id, session: 's', code: '', stdin: '', files: [], check: null, budget_ms: 5000 },
    ];
    for (const data of bad) expect(client.receive({ origin: ORIGIN, source: frame, data })).toBe('invalid');
    expect(client.isPending(id)).toBe(true);
  });

  it('listens through the given subscription and stops on dispose, rejecting what is pending', async () => {
    const { client, frame, deliver, listening } = harness();
    const ping = client.ping();
    await flush();
    deliver({ origin: ORIGIN, source: frame, data: { v: 2, type: 'ready', id: 'id-1', python: '3.12.7', pyodide: '0.27.8', isolated: true, boot_ms: 900 } });
    await expect(ping).resolves.toMatchObject({ pyodide: '0.27.8' });
    const { result } = client.run({ session: 's', code: '' });
    client.dispose();
    expect(listening()).toBe(false);
    await expect(result).rejects.toBeInstanceOf(RunnerUnavailableError);
  });

  it('times out as "runner unavailable" (e.g. the iframe was navigated away)', async () => {
    vi.useFakeTimers();
    const { client } = harness({ bootMs: 500, runSlackMs: 100 });
    const ping = client.ping();
    const run = client.run({ session: 's', code: '', budget_ms: 200 });
    const pingDone = expect(ping).rejects.toBeInstanceOf(RunnerUnavailableError);
    const runDone = expect(run.result).rejects.toBeInstanceOf(RunnerUnavailableError);
    await vi.advanceTimersByTimeAsync(200 + 1000 + 100 + 1);
    await runDone;
    await vi.advanceTimersByTimeAsync(500);
    await pingDone;
    expect(client.isPending(run.id)).toBe(false);
  });

  it('sends reset, ping and interrupt envelopes; interrupt only for a pending run', async () => {
    const { client, frame, posted } = harness();
    const reset = client.reset('u02');
    const { id } = client.run({ session: 'c1', code: 'while True: pass', check: { kind: 'output', turtle: false }, budget_ms: 1000 });
    await flush();
    client.interrupt(id);
    client.interrupt('not-pending');
    await flush();
    expect(posted.map((p) => [p.message.type, p.message.id, p.targetOrigin])).toEqual([
      ['reset', 'id-1', ORIGIN],
      ['run', id, ORIGIN],
      ['interrupt', id, ORIGIN],
    ]);
    expect(client.receive({ origin: ORIGIN, source: frame, data: { v: 2, type: 'restarted', id: 'id-1', boot_ms: 1000 } })).toBe('accepted');
    await expect(reset).resolves.toMatchObject({ type: 'restarted' });
  });

  it('refuses to send an invalid request', async () => {
    const { client, posted } = harness();
    const { result } = client.run({ session: 'not a valid session!', code: '' });
    await expect(result).rejects.toBeInstanceOf(TypeError);
    expect(posted).toEqual([]);
  });

  it('refuses a non-origin runner origin', () => {
    expect(() => new RunnerClient({ runnerOrigin: 'http://localhost:4392/', frame: () => null, listen: () => () => {} })).toThrow();
    expect(() => new RunnerClient({ runnerOrigin: '', frame: () => null, listen: () => () => {} })).toThrow();
  });
});

describe('RunnerClient: envelope version 2 (plan 105)', () => {
  const RID = 'f'.repeat(64);
  const HASH = '0'.repeat(64);

  it('drops a version-1 reply (this page speaks only version 2)', async () => {
    const { client, frame, deliver } = harness();
    const ping = client.ping();
    await flush();
    const v1 = { type: 'ready', id: 'id-1', python: '3.12', pyodide: '0.27.8', isolated: true, boot_ms: 1 };
    expect(client.receive({ origin: ORIGIN, source: frame, data: v1 })).toBe('invalid');
    expect(client.isPending('id-1')).toBe(true);
    deliver({ origin: ORIGIN, source: frame, data: { ...v1, v: 2 } });
    await expect(ping).resolves.toMatchObject({ type: 'ready' });
  });

  it('rejects with RunnerVersionError on version-mismatch (an older runner): reload', async () => {
    const { client, frame } = harness();
    const ping = client.ping();
    await flush();
    expect(client.receive({ origin: ORIGIN, source: frame, data: { type: 'version-mismatch', id: 'id-1', supported: [1] } })).toBe('accepted');
    await expect(ping).rejects.toBeInstanceOf(RunnerVersionError);
    await expect(ping).rejects.toBeInstanceOf(RunnerUnavailableError);
  });

  it('precaches with progress, and resolves on precached', async () => {
    const { client, frame, posted } = harness();
    const seen: [number, number][] = [];
    const done = client.precache({ book: 'acsl', content_hash: HASH, release_id: RID }, (b, t) => seen.push([b, t]));
    await flush();
    expect(posted[0]!.message).toEqual({ v: 2, type: 'precache', id: 'id-1', book: 'acsl', content_hash: HASH, files: [], release_id: RID });
    expect(client.receive({ origin: ORIGIN, source: frame, data: { v: 2, type: 'precache-progress', id: 'id-1', bytes: 5, total: 10 } })).toBe('accepted');
    expect(client.isPending('id-1')).toBe(true);
    expect(client.receive({ origin: ORIGIN, source: frame, data: { v: 2, type: 'precached', id: 'id-1', ok: true, bytes: 10, persisted: false } })).toBe('accepted');
    await expect(done).resolves.toMatchObject({ ok: true, bytes: 10 });
    expect(seen).toEqual([[5, 10]]);
  });

  it('sends prepare-activate and resolves on runner-activated; progress for another request is dropped', async () => {
    const { client, frame, posted } = harness();
    const activated = client.prepareActivate(RID, 1000);
    await flush();
    expect(posted[0]!.message).toEqual({ v: 2, type: 'prepare-activate', id: 'id-1', release_id: RID });
    expect(client.receive({ origin: ORIGIN, source: frame, data: { v: 2, type: 'precache-progress', id: 'id-1', bytes: 1, total: 2 } })).toBe('unknown-id');
    expect(client.receive({ origin: ORIGIN, source: frame, data: { v: 2, type: 'runner-activated', id: 'id-1', release_id: RID } })).toBe('accepted');
    await expect(activated).resolves.toMatchObject({ release_id: RID });
  });

  it('times out a prepare-activate the runner never answers', async () => {
    vi.useFakeTimers();
    const { client } = harness();
    const activated = client.prepareActivate(RID, 10_000);
    const caught = activated.catch((e: unknown) => e);
    await vi.advanceTimersByTimeAsync(10_001);
    expect(await caught).toBeInstanceOf(RunnerUnavailableError);
  });
});
