#!/usr/bin/env bash
# Single test entry point: runs each project's and workflow's tests by detected stack.
set -uo pipefail
root=$(git -C "$(dirname "$0")" rev-parse --show-toplevel); fail=0; ran=0
run() { echo "── $1: $2"; (cd "$1" && bash -c "$2") || { echo "‼️ FAIL $1"; fail=1; }; ran=$((ran+1)); }
for d in "$root"/projects/*/ "$root"/lab/workflows/*/; do
  [ -d "$d" ] || continue; d=${d%/}
  if   [ -x "$d/test.sh" ];          then run "$d" "./test.sh"
  elif [ -f "$d/package.json" ];     then run "$d" "npm install --silent && npm test --silent"
  elif [ -f "$d/pyproject.toml" ];   then run "$d" "uv run --with pytest pytest -q"
  elif [ -f "$d/Cargo.toml" ];       then run "$d" "cargo test -q"
  elif [ -f "$d/go.mod" ];           then run "$d" "go test ./..."
  fi
done
echo "ran $ran suite(s)"; exit $fail
