#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
DRY_RUN=1 ./run.sh fixtures | sort > /tmp/inbox-triage.out
diff -u expected/dry-run.txt /tmp/inbox-triage.out && echo "inbox-triage: ok"
