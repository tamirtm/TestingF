---
name: build-test
description: Build and test a project in projects/ (or vendor/ read-only) — detect the stack, install, build, run tests, add missing tests, and report. Use after any code change, or for "build it", "test it", "does it work", "set up CI".
---
# Build & test

1. Detect the stack from its manifest (package.json, pyproject.toml, Cargo.toml, go.mod, Makefile).
   Python: `uv`. Node: `npm`. Rust: `cargo`. Go: `go`.
2. Install, then build. If the build fails, fix the root cause; don't paper over it.
3. Tests:
   - No tests? Add a smoke test first (it imports and runs one real path), then a test for the change.
   - Pick a framework: pytest, vitest/node:test, cargo test, go test.
   - UI or web: use Playwright (Chromium is preinstalled; never run `playwright install`).
4. Make the project testable from the root: add `test.sh` if the stack isn't auto-detected by `scripts/test-all.sh`.
5. Run `scripts/test-all.sh`. Report: ✅/‼️ per suite, failing test names + the first error lines.
Never skip, delete, or weaken a test to get green. Never claim a pass you didn't run.
