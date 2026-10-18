#!/bin/bash
# Cloud sessions: install inspection / reverse-engineering tools and restore vendored code.
set -euo pipefail
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi
cd "$CLAUDE_PROJECT_DIR"

# Reverse-engineering & inspection tools (apt; skipped when already present)
need=()
for p in radare2:r2 binwalk:binwalk gdb:gdb strace:strace ltrace:ltrace xxd:xxd p7zip-full:7z; do
  command -v "${p#*:}" >/dev/null 2>&1 || need+=("${p%%:*}")
done
if [ ${#need[@]} -gt 0 ]; then
  SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
  $SUDO apt-get update -qq
  DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y -qq "${need[@]}" >/dev/null
fi

# JS deobfuscation helpers (cached in the container image after first run)
command -v js-beautify >/dev/null 2>&1 || npm install -g --silent js-beautify >/dev/null

# Re-fetch pinned upstream code (vendor/ is gitignored)
if [ "$(wc -l < vendor/manifest.tsv)" -gt 1 ]; then
  scripts/vendor.sh --restore || echo "vendor restore failed (check network allowlist)" >&2
fi
