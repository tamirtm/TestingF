---
name: workflow-lab
description: Build and test workflow automations (scripts, scheduled jobs, API/webhook pipelines, n8n/Make/Zapier logic, Claude headless runs) in lab/workflows with fixtures and dry runs. Use for "automate X", "build a workflow", "test my automation".
---
# Workflow lab

Each workflow lives in `lab/workflows/<name>/`:
```
run.sh          # entry point; honours DRY_RUN=1 (default) → print intended side effects, don't perform
fixtures/       # recorded real inputs (API responses, files, webhook payloads), secrets scrubbed
expected/       # expected outputs for each fixture
test.sh         # runs run.sh on every fixture with DRY_RUN=1, diffs against expected/
README.md       # trigger, inputs, outputs, side effects, required env vars, schedule
```

## Rules
- **Side effects behind DRY_RUN.** That covers anything that sends, posts, writes to a remote, or spends money. Go live only when the human says so.
- **Secrets only from env vars.** List them in README.md, never commit them, and redact them from fixtures.
- **Make it idempotent and observable.** Re-running mustn't double-send. Log one line per step with a timestamp.
- **Use Claude inside a workflow headless.** Run `claude -p "<task>" --output-format json --max-turns N --max-budget-usd X` and parse `.result`.
- **Visual tools (n8n/Make/Zapier).** Keep the logic as testable code or exported JSON here, test it with fixtures, then port it.

## Done when
`lab/workflows/<name>/test.sh` passes, and `scripts/test-all.sh` picks it up automatically.
