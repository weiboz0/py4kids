/**
 * The two test servers under the test's control (plan 105): the site and the runner, each served
 * by scripts/serve.mjs with its own `_headers`, at the origins the build baked in. `stop()` closes
 * every connection, so the next request is refused: the network is really gone, for pages,
 * workers and service workers alike.
 */
import { test as base } from '@playwright/test';
import { BASE_URL, DIST, RUNNER_DIST, RUNNER_URL } from '../e2e/helpers/env';
import { startServer } from '../scripts/serve.mjs';

interface Running {
  server: import('node:http').Server;
  close(): Promise<void>;
}

export class Servers {
  private running: Running[] = [];

  /**
   * Serve `roots` (default: the built dists) at the baked-in origins. `delayMs` slows chosen files
   * (by origin and path), standing in for a slow network.
   */
  async start(roots: { site: string; runner: string } = { site: DIST, runner: RUNNER_DIST }, delayMs?: (origin: string, path: string) => number): Promise<void> {
    if (this.running.length > 0) return;
    for (const [root, origin] of [
      [roots.site, BASE_URL],
      [roots.runner, RUNNER_URL],
    ] as const) {
      const url = new URL(origin);
      const delay = delayMs ? (path: string) => delayMs(url.origin, path) : undefined;
      this.running.push((await startServer({ root, port: Number(url.port), host: url.hostname, delayMs: delay })) as Running);
    }
  }

  async stop(): Promise<void> {
    for (const r of this.running) {
      r.server.closeAllConnections();
      await r.close();
    }
    this.running = [];
  }
}

export const test = base.extend<{ servers: Servers }>({
  servers: async ({}, use) => {
    const servers = new Servers();
    await servers.start();
    await use(servers);
    await servers.stop();
  },
});

export { expect } from '@playwright/test';
