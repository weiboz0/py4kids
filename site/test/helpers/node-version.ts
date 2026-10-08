/**
 * Astro 7 needs Node >= 22.12 (package.json `engines`). The leak test builds the site, so on an
 * older Node it would fail deep inside the build; it checks first and fails with this message.
 */
export const MIN_NODE = [22, 12] as const;

/** Why `version` (e.g. `process.versions.node`) cannot build the site, or null when it can. */
export function nodeVersionProblem(version: string): string | null {
  const [major = 0, minor = 0] = version.split('.').map(Number);
  if (major > MIN_NODE[0] || (major === MIN_NODE[0] && minor >= MIN_NODE[1])) return null;
  return (
    `The leak test builds the site, which needs Node >= ${MIN_NODE.join('.')}, but this is Node ${version}. ` +
    'From the repository root run `source scripts/site-env.sh && site_node_env` (it activates the .nvmrc Node 24 through nvm), then rerun `pnpm -C site test`.'
  );
}
