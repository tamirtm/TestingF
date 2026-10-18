# Dev workbench

Pipeline for every build: **find → vet → vendor → study → adapt → build → test**.

## Layout
| Path | What | Rules |
|---|---|---|
| `vendor/<name>/` | Upstream code, pinned, **never edited** | Fetched by `scripts/vendor.sh`; gitignored; pinned in `vendor/manifest.tsv` |
| `projects/<name>/` | Your adapted builds | Each has its own README, tests, and `NOTICE.md` crediting upstream |
| `lab/skills/<name>/` | Skills under test | Skill folder + `evals/`; run with `scripts/eval-skill.sh` |
| `lab/workflows/<name>/` | Automations under test | `run.sh`, `fixtures/`, `test.sh`; dry-run by default |
| `scripts/` | Repo tooling | `test-all.sh` is the single CI entry point |

## Hard rules
- Check the license before copying a single line (`scripts/license-check.sh vendor/<name>`).
  No license = read-only; never copy. GPL/AGPL code makes the whole project GPL/AGPL. Ask before adopting.
- Reverse engineering is for code we have the right to study: open source, our own, licensed, or
  interoperability analysis. Never bypass licence checks, DRM, auth, or extract secrets/keys.
- Every project change ships with a test. Run `scripts/test-all.sh` before saying "done".
- Workflows touching external services run with `DRY_RUN=1` unless the human says go.

## Skills here
`oss-adopt` · `code-recon` · `build-test` · `skill-lab` · `workflow-lab` (see .claude/skills/).
