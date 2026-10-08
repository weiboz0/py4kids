# Sourced by scripts/build-site.sh and scripts/ci-local.sh (design 012 part B; plan 103).
# Puts a Node that meets Astro's engines (>= 22.12; .nvmrc pins Node 24 LTS) on PATH, activating
# it through nvm when the shell's default Node is older, and finds pnpm and a Chromium.
# Run from the repository root (nvm reads .nvmrc there).

# True when `node` exists and is >= 22.12.
site_node_ok() {
  command -v node >/dev/null 2>&1 &&
    node -e 'const [a, b] = process.versions.node.split(".").map(Number); process.exit(a > 22 || (a === 22 && b >= 12) ? 0 : 1)'
}

# Activate the .nvmrc Node through nvm if needed; true when a usable Node is on PATH.
site_node_env() {
  site_node_ok && return 0
  local nvm_sh="${NVM_DIR:-$HOME/.nvm}/nvm.sh"
  [[ -s "$nvm_sh" ]] || return 1
  set +eu
  # shellcheck disable=SC1090
  . "$nvm_sh" --no-use
  nvm use --silent >/dev/null 2>&1
  set -eu
  site_node_ok
}

# Sets SITE_PNPM to the pnpm command (pnpm, else corepack's pnpm at package.json's version).
site_pnpm() {
  export COREPACK_ENABLE_DOWNLOAD_PROMPT=0
  if command -v pnpm >/dev/null 2>&1; then
    SITE_PNPM=(pnpm)
  elif command -v corepack >/dev/null 2>&1; then
    SITE_PNPM=(corepack pnpm)
  else
    return 1
  fi
}

# True when a Chromium exists (system, or a Playwright download); Phase F's browser tests need it.
site_chromium() {
  local name
  for name in chromium chromium-browser google-chrome google-chrome-stable; do
    command -v "$name" >/dev/null 2>&1 && return 0
  done
  compgen -G "${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}/chromium-*" >/dev/null
}
