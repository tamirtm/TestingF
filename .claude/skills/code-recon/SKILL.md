---
name: code-recon
description: Reverse-engineer and map unfamiliar code (source repos, minified/bundled JS, compiled binaries, APKs, file formats, network protocols) to understand how it works. Use for "how does this work", "reverse engineer", "figure out the format/API", "map this codebase".
---
# Code recon

## Scope check (first, always)
Proceed only for: open source, the user's own code, code they're licensed to inspect, security
research on their own systems, or interoperability with a format/protocol. Refuse to: bypass licence
checks/DRM/auth, extract secrets or keys, or clone a proprietary product's code. If unclear, ask.

## Source repos
1. Use the `recon-mapper` subagent for big repos so the file dumps stay out of the main context.
2. Produce `notes/RECON.md` in the target's project folder (or chat if none):
   - **Purpose** (3 lines) · **Entry points** (CLI/main/routes) · **Module map** (dir → responsibility)
   - **Data flow** for the 1–2 paths the user cares about, with `file:line` references
   - **External deps & side effects** (network, disk, env vars) · **Tests**: how to run them
   - **Gotchas** (globals, magic config, codegen)
3. Prove understanding: write or run one small test or script that exercises the path you described.

## Minified / bundled JS
`npx --yes js-beautify -f bundle.js -o pretty.js` → find strings/URLs with `rg` → map
webpack modules → rename symbols as you learn them into a notes table. For heavy obfuscation:
`npx --yes webcrack bundle.js -o out/`.

## Binaries / firmware / APKs
`file`, `strings -n 8`, `xxd | head`, `binwalk -e` (archives/firmware), `objdump -d`/`r2 -A` (ELF),
`readelf -a`, `ltrace`/`strace` on a sandboxed run, `jadx` (APK → Java, if installed).
Write findings in the same RECON.md shape.

## File formats / protocols
Collect 3+ samples → diff with `xxd` → hypothesise the structure → write a parser + round-trip
test in projects/. The test passing is the proof.
