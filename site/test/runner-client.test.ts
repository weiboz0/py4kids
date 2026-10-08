/**
 * The runner client's message binding (plan 104 Phase A, D7): a reply is accepted only from the
 * runner origin, from the iframe's own window, as a valid envelope, for a pending id (of the
 * right type and session); every request is posted with the exact runner origin; requests time
 * out as "runner unavailable". The browser proofs are in e2e/runner.spec.ts.
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import { RunnerClient, RunnerUnavailableError, type Incoming, type ResultReply } from '../src/lib/runner-client';

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
        message: { type: 'run', id, session: 'u01', code: 'print("hi")', stdin: '', files: [], check: null, budget_ms: 5000 },
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
    const ready = { type: 'ready', id, python: '3.12', pyodide: '0.27.8', isolated: true, boot_ms: 1 };
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
      { type: 'run', id, session: 's', code: '', stdin: '', files: [], check: null, budget_ms: 5000 },
    ];
    for (const data of bad) expect(client.receive({ origin: ORIGIN, source: frame, data })).toBe('invalid');
    expect(client.isPending(id)).toBe(true);
  });

  it('listens through the given subscription and stops on dispose, rejecting what is pending', async () => {
    const { client, frame, deliver, listening } = harness();
    const ping = client.ping();
    await flush();
    deliver({ origin: ORIGIN, source: frame, data: { type: 'ready', id: 'id-1', python: '3.12.7', pyodide: '0.27.8', isolated: true, boot_ms: 900 } });
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
    expect(client.receive({ origin: ORIGIN, source: frame, data: { type: 'restarted', id: 'id-1', boot_ms: 1000 } })).toBe('accepted');
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
