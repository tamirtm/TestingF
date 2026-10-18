#!/usr/bin/env bash
# Eval a skill in lab/skills/<name> with Claude Code's built-in eval runner.
#   scripts/eval-skill.sh <name> [extra claude plugin eval flags]
# Defaults: 3 runs per case, baseline (no-skill) comparison, US$2 cost ceiling, local report only.
set -euo pipefail
root=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
name=${1:?usage: eval-skill.sh <name>}; shift
cd "$root/lab/skills/$name"
claude plugin eval . --max-cost-usd "${MAX_COST_USD:-2}" --no-publish --threshold "${THRESHOLD:-0.8}" "$@"
