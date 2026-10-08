/**
 * The isolated Python runner in a real browser (plan 104 Phase A; Phase D adds the full
 * acceptance suite). Both origins are served by scripts/serve.mjs with their own `_headers`
 * (playwright.config.ts): the site, and the runner on its own origin. The site's client
 * (src/lib/runner-client.ts) is bundled here and evaluated in a real site page (Phase B wires it
 * into the pages), so these tests drive the real client, the real iframe and the real workers.
 *
 * Proven here: the iframe loads under the site's COEP; `crossOriginIsolated` is true in the site,
 * the runner page and its worker; a run prints; `input()` reads stdin and raises EOFError at its
 * end; a hang stops with `interrupts: "sab"`, and a loop that swallows the interrupt is stopped
 * by the grace restart; reset clears a session; two checks share no process state (math.pi,
 * builtins.print, sys.path, random); at most three Python workers exist. The boot time (cold and
 * warm) is recorded as a test annotation.
 */
import { expect, test } from '@playwright/test';
import { RUNNER_URL } from './helpers/env';
import { cpython } from './helpers/content';
import { fresh, openRunner, run, runnerFrame, workers, type Browserside } from './helpers/runner';

const check = (turtle = false) => ({ kind: 'output' as const, turtle });

test('the runner loads under the site COEP; the site, runner page and worker are cross-origin isolated', async ({ page, request }) => {
  const csp: string[] = [];
  page.on('console', (m) => {
    if (/Content Security Policy|Refused to/i.test(m.text())) csp.push(m.text());
  });
  const coldStart = Date.now();
  const cold = await openRunner(page);
  const coldWall = Date.now() - coldStart;
  expect(cold.isolated).toBe(true);
  expect(cold.pyodide).toBe('0.27.8');
  expect(cold.python).toMatch(/^3\.12\./);
  expect(await page.evaluate(() => self.crossOriginIsolated)).toBe(true);
  const frame = runnerFrame(page);
  expect(await frame.evaluate(() => self.crossOriginIsolated)).toBe(true);
  // the worker reports its own crossOriginIsolated in `ready.isolated`; check it directly too
  const pyWorkers = page.workers().filter((w) => w.url().startsWith(`${RUNNER_URL}/assets/worker-`));
  expect(pyWorkers.length).toBeGreaterThan(0);
  for (const w of pyWorkers) expect(await w.evaluate(() => self.crossOriginIsolated)).toBe(true);

  // Every runner response carries CORP cross-origin and the isolation headers.
  const html = await (await request.get(`${RUNNER_URL}/`)).text();
  const main = /src="(\/assets\/main-[0-9a-f]+\.js)"/.exec(html)?.[1];
  expect(main).toBeTruthy();
  const workerUrl = pyWorkers[0]!.url();
  for (const url of [`${RUNNER_URL}/`, `${RUNNER_URL}${main}`, workerUrl, `${RUNNER_URL}/pyodide/0.27.8/pyodide.asm.wasm`, `${RUNNER_URL}/pyodide/0.27.8/python_stdlib.zip`]) {
    const headers = (await request.head(url)).headers();
    expect(headers['cross-origin-resource-policy'], url).toBe('cross-origin');
    expect(headers['cross-origin-embedder-policy'], url).toBe('require-corp');
    expect(headers['cross-origin-opener-policy'], url).toBe('same-origin');
    expect(headers['content-security-policy'], url).toContain(`frame-ancestors ${new URL(page.url()).origin}`);
  }

  // Warm boot: the same browser context (compiled WebAssembly cached), a fresh page load.
  const warmStart = Date.now();
  const warm = await openRunner(page);
  const warmWall = Date.now() - warmStart;
  test.info().annotations.push({
    type: 'boot',
    description: `cold: worker ${Math.round(cold.boot_ms)} ms (page to ready ${coldWall} ms); warm: worker ${Math.round(warm.boot_ms)} ms (page to ready ${warmWall} ms)`,
  });
  console.log(`runner boot: cold ${Math.round(cold.boot_ms)} ms (${coldWall} ms wall), warm ${Math.round(warm.boot_ms)} ms (${warmWall} ms wall)`);
  expect(csp).toEqual([]);
});

test('a run prints its output; a lesson session keeps its state', async ({ page }) => {
  await openRunner(page);
  const first = await run(page, { session: 'u01', code: 'x = 20\nprint("hello", x + 1)' });
  expect(first).toMatchObject({ status: 'ok', stdout: 'hello 21\n', stderr: '', interrupts: 'sab', session_new: true });
  const second = await run(page, { session: 'u01', code: 'print(x * 2)' });
  expect(second).toMatchObject({ status: 'ok', stdout: '40\n', session_new: false });
});

test('input() reads stdin, and at the end of input raises EOFError as in CPython', async ({ page }) => {
  await openRunner(page);
  const result = await run(page, { session: 'u02', code: 'name = input("Name? ")\nprint("Hi", name)\ninput()', stdin: 'Ada\n' });
  expect(result.stdout).toBe('Name? Hi Ada\n');
  expect(result.status).toBe('error');
  expect(result.stderr).toMatch(/EOFError: EOF when reading a line\n$/);
  const read = await run(page, { session: fresh(), code: 'import sys\nprint(sum(map(int, sys.stdin.read().split())))', stdin: '1 2\n3\n', check: check() });
  expect(read).toMatchObject({ status: 'ok', stdout: '6\n' });
});

test('a hang is stopped by the SharedArrayBuffer interrupt, and the session survives', async ({ page }) => {
  await openRunner(page);
  await run(page, { session: 'u03', code: 'kept = 7' });
  const start = Date.now();
  const hang = await run(page, { session: 'u03', code: 'while True:\n    pass', budget_ms: 1000 });
  const elapsed = Date.now() - start;
  expect(hang).toMatchObject({ status: 'timeout', interrupts: 'sab' });
  expect(hang.stderr).toContain('time limit');
  expect(elapsed).toBeLessThan(1000 + 1000 + 1500);
  const after = await run(page, { session: 'u03', code: 'print(kept)' });
  expect(after).toMatchObject({ status: 'ok', stdout: '7\n', session_new: false });

  // a check hang too, reported as a failed case
  const fixture = await run(page, {
    session: fresh(),
    code: 'while True:\n    pass',
    check: { kind: 'fixture', expected: '1\n', match: 'token', turtle: false },
    budget_ms: 500,
  });
  expect(fixture).toMatchObject({ status: 'timeout', interrupts: 'sab', results: [{ name: 'case', pass: false, detail: 'time limit' }] });
});

test('a loop that swallows the interrupt is stopped by the grace restart', async ({ page }) => {
  await openRunner(page);
  await run(page, { session: 'u04', code: 'kept = 7' });
  const start = Date.now();
  const code = 'while True:\n    try:\n        while True:\n            pass\n    except KeyboardInterrupt:\n        pass\n';
  const result = await run(page, { session: 'u04', code, budget_ms: 1000 });
  const elapsed = Date.now() - start;
  expect(result).toMatchObject({ status: 'timeout', interrupts: 'restart' });
  expect(elapsed).toBeGreaterThanOrEqual(2000);
  expect(elapsed).toBeLessThan(1000 + 1000 + 1500);
  // The lesson session is lost (the worker was restarted): the next run starts a new one.
  const after = await run(page, { session: 'u04', code: 'print("kept" in dir())' });
  expect(after).toMatchObject({ status: 'ok', stdout: 'False\n', session_new: true });
  expect(await workers(page)).toBeLessThanOrEqual(3);
});

test('the Stop button interrupts a running check', async ({ page }) => {
  await openRunner(page);
  const status = await page.evaluate(async (session) => {
    const { runner } = window as unknown as Browserside;
    const { id, result } = runner.run({ session, code: 'while True:\n    pass', check: { kind: 'output', turtle: false }, budget_ms: 30000 });
    await new Promise((r) => setTimeout(r, 1500));
    runner.interrupt(id);
    return (await result).status;
  }, fresh());
  expect(status).toBe('interrupted');
});

test('reset clears a lesson session', async ({ page }) => {
  await openRunner(page);
  await run(page, { session: 'u05', code: 'y = 1\nopen("save.txt", "w").write("x")' });
  expect((await run(page, { session: 'u05', code: 'print(y)' })).stdout).toBe('1\n');
  const restarted = await page.evaluate(() => (window as unknown as Browserside).runner.reset('u05'));
  expect(restarted.type).toBe('restarted');
  const after = await run(page, { session: 'u05', code: 'import os\nprint("y" in dir(), os.path.exists("save.txt"))' });
  expect(after).toMatchObject({ stdout: 'False False\n', session_new: true });
});

test('two checks share no process state (module globals, builtins, sys.path, random)', async ({ page }) => {
  await openRunner(page);
  const first = await run(page, {
    session: fresh(),
    code: 'import builtins, math, random, sys\nsecret = 1\nmath.pi = 3\nsys.path.append("x")\nrandom.seed(1)\nsys.stdout.write(repr(random.random()))\nbuiltins.print = None\n',
    check: check(),
  });
  expect(first.status).toBe('ok');
  const seeded = first.stdout;
  expect(seeded).toBe('0.13436424411240122');
  const second = await run(page, {
    session: fresh(),
    code: 'import builtins, math, random, sys\nprint("secret" in dir(), math.pi, "x" in sys.path, callable(builtins.print), repr(random.random()))',
    check: check(),
  });
  const [secret, pi, inPath, printOk, value] = second.stdout.trim().split(' ');
  expect([secret, pi, inPath, printOk]).toEqual(['False', '3.141592653589793', 'False', 'True']);
  expect(value).not.toBe(seeded);
  expect(await workers(page)).toBeLessThanOrEqual(3);
});

test('checks grade fixtures (line-exact and token), asserts and the turtle rule', async ({ page }) => {
  await openRunner(page);
  const code = 'print(15)\nprint(10)\nprint(4)';
  const line = await run(page, { session: fresh(), code, check: { kind: 'fixture', expected: '15 10 4\n', match: 'line', turtle: false } });
  expect(line.results).toEqual([{ name: 'case', pass: false, detail: 'wrong output' }]);
  const token = await run(page, { session: fresh(), code, check: { kind: 'fixture', expected: '15 10 4\n', match: 'token', turtle: false } });
  expect(token.results).toEqual([{ name: 'case', pass: true, detail: '' }]);

  const asserts = await run(page, {
    session: fresh(),
    code: 'def double(x):\n    return x * 2',
    check: { kind: 'asserts', asserts: ['assert double(2) == 4  # HIDDEN-SOURCE', 'assert double(2) == 5', 'assert nope(1)'], turtle: false },
  });
  expect(asserts.results.map((r) => [r.pass, r.detail])).toEqual([
    [true, ''],
    [false, 'assertion failed'],
    [false, "NameError: name 'nope' is not defined"],
  ]);
  expect(JSON.stringify(asserts)).not.toContain('HIDDEN-SOURCE');

  const square = 'import turtle\nt = turtle.Turtle()\nfor _ in range(4):\n    t.forward(40)\n    t.left(90)';
  const drawn = await run(page, { session: fresh(), code: square, check: check(true) });
  expect(drawn.results.map((r) => r.pass)).toEqual([true, true, true]);
  expect(drawn.segments).toHaveLength(4);
});

test('at most three Python workers exist while checks and a lesson run', async ({ page }) => {
  await openRunner(page);
  await run(page, { session: 'u06', code: 'pass' });
  let max = 0;
  const poll = setInterval(() => {
    workers(page).then((n) => (max = Math.max(max, n))).catch(() => {});
  }, 50);
  try {
    for (let i = 0; i < 3; i++) await run(page, { session: fresh(), code: 'print(1)', check: check() });
    await run(page, { session: fresh(), code: 'while True:\n    pass', check: check(), budget_ms: 500 });
  } finally {
    clearInterval(poll);
  }
  expect(max).toBeGreaterThanOrEqual(2);
  expect(max).toBeLessThanOrEqual(3);
  expect(await workers(page)).toBeLessThanOrEqual(3);
});

// ---------------------------------------------------------------------------------------------
// Phase D: runner acceptance (design 012 §3) and the boot measurement

/** 20 fixed expressions: recursion depth and float formatting (design 012 §3). */
const PARITY = [
  'import sys',
  'def depth(n):\n    return 0 if n == 0 else 1 + depth(n - 1)',
  'def runaway(n):\n    return runaway(n + 1)',
  'def boom():\n    try:\n        runaway(0)\n    except RecursionError as e:\n        return type(e).__name__ + ": " + str(e)',
  'print(sys.getrecursionlimit())',
  'print(depth(900))',
  'print(boom())',
  'print(0.1 + 0.2)',
  'print(1 / 3)',
  'print(2 ** 0.5)',
  'print(10 / 3)',
  'print(1e16, 1e22, 1e-5, 1e-7)',
  'print(round(2.675, 2), round(0.5), round(1.5), round(-2.5))',
  'print("%.2f" % 2.675, f"{0.1:.20f}")',
  'print(float("inf"), -float("inf"), float("nan"))',
  'print(-0.0, 0.0 == -0.0)',
  'print(sum([0.1] * 10))',
  'print(123456789012345678.0)',
  'print(sys.float_info.max, sys.float_info.epsilon)',
  'print((0.1).hex(), float.fromhex("0x1.8p1"))',
  'print(divmod(7.5, 2), 7.5 // -2, -7 % 3)',
  'print(format(1234567.891, ",.2f"), format(0.000123, "e"), format(1 / 7, ".15g"))',
  'print(repr(1.1 * 3), str(3.0), 2 ** 64 / 3)',
  'import math\nprint(math.pi, math.e, math.sqrt(2), math.fsum([0.1] * 10))',
].join('\n');

test('§3 recursion depth and float formatting match CPython (20 fixed expressions, CPython run at test time)', async ({ page }) => {
  const expected = cpython(PARITY);
  expect(PARITY.split('\n').filter((l) => l.startsWith('print(')).length).toBe(20);
  expect(expected.trim().split('\n')).toHaveLength(20);
  await openRunner(page);
  const asCheck = await run(page, { session: fresh(), code: PARITY, check: check() });
  expect(asCheck.stderr).toBe('');
  expect(asCheck.stdout.split('\n')).toEqual(expected.split('\n'));
  // ...and in a lesson session too (the lesson worker, not only a fresh check worker).
  const asLesson = await run(page, { session: 'u08', code: PARITY });
  expect(asLesson.stdout).toBe(expected);
});

test('cold and warm Pyodide boot under Chromium CPU throttling x4 (recorded)', async ({ browser }) => {
  test.setTimeout(240_000);
  // Throttling is set on the site page's target; the runner iframe and its workers run in the
  // same renderer here (the headless shell gives the frame no separate CDP target), and the
  // unthrottled boot is measured alongside for comparison.
  const measure = async (page: import('@playwright/test').Page, rate: number) => {
    const cdp = await page.context().newCDPSession(page);
    await cdp.send('Emulation.setCPUThrottlingRate', { rate });
    const start = Date.now();
    const info = await openRunner(page);
    const wall = Date.now() - start;
    // The first check after boot (a fresh worker: the spare's boot plus the run).
    const first = Date.now();
    const result = await run(page, { session: fresh(), code: 'print(sum(range(10)))', check: check() });
    const firstCheck = Date.now() - first;
    expect(result.stdout).toBe('45\n');
    await page.close();
    return { worker: Math.round(info.boot_ms), wall, firstCheck };
  };
  const lines: string[] = [];
  for (const rate of [4, 1]) {
    const context = await browser.newContext();
    try {
      const cold = await measure(await context.newPage(), rate);
      // Warm: the same context (the compiled WebAssembly is cached), a fresh page.
      const warm = await measure(await context.newPage(), rate);
      lines.push(
        `CPU x${rate}: cold boot ${cold.worker} ms in the worker (${cold.wall} ms page load to ready; first check ${cold.firstCheck} ms); warm boot ${warm.worker} ms (${warm.wall} ms; first check ${warm.firstCheck} ms)`,
      );
      expect(cold.worker).toBeGreaterThan(0);
      expect(warm.worker).toBeGreaterThan(0);
    } finally {
      await context.close();
    }
  }
  for (const text of lines) {
    test.info().annotations.push({ type: 'boot', description: text });
    console.log(`runner boot, ${text}`);
  }
});
