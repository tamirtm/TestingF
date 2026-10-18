---
name: oss-adopt
description: Find, vet, vendor and adapt open-source code for a project. Use when the user wants an existing library/repo/tool to build on ("find something that does X", "use this GitHub repo", "fork and adapt").
---
# Adopt open source

## 1. Find (only if no repo was given)
Search GitHub/package registries. Shortlist up to 3 candidates in a table:
`repo | stars | last commit | license | open issues | fit (1 line)`.
Drop anything with no license, abandoned >2 yrs with open security issues, or a one-person toy for core infra.

## 2. Vet the pick
- `scripts/vendor.sh <url>` (pins the commit, records the license in vendor/manifest.tsv)
- `scripts/license-check.sh vendor/<name>`: obey its verdict. STOP means ask the human.
- Quick health check: does it build, and do its own tests pass? Run them in vendor/<name>, without editing the code.
- Supply chain: skim install scripts (`postinstall`, `setup.py`, `build.rs`, Makefile) for network calls or obfuscation.

## 3. Adapt
- Choose the lightest option that works, in this order:
  1. Depend on it as a package.
  2. Wrap it.
  3. Copy the specific files.
  4. Fork it into projects/.
- Copied/forked code goes in `projects/<proj>/`, with `NOTICE.md` listing: upstream URL, commit,
  license, files taken, what changed. Apache-2.0: also mark changed files.
- Strip what you don't need; keep upstream tests for the parts you kept and make them pass.

## 4. Hand off to build-test
Finish with: what was adopted, license obligations, and the test command.
