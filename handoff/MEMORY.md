# Memory handoff — tamirtm workbench

Snapshot: 2026-10-24. Source: Claude Code cloud sessions on `tamirtm/TestingF` and `tamirtm/hello-world`.
Load this whole file as long-term memory for any local agent (Claude via API, Ollama/LM Studio/llama.cpp
models, Open WebUI, Letta, mem0, Continue, Aider, etc.). `memories.jsonl` holds the same facts as atomic
records; `system-prompt.md` is a ready-to-paste agent prompt.

---

## 1. Who I am / what I work on
- GitHub: **tamirtm**. Repos: `tamirtm/TestingF` (main workbench), `tamirtm/hello-world` (scratch/test repo, a README only).
- Hobby/business: Magic: The Gathering **proxy cards** printed at **MakePlayingCards (MPC)** via **MPC Autofill**.
  Packaging/branding work for **WPG Proxy Prints** (card box lids, box wraps, seal stickers).
- Professional: drafts **Market Intelligence Scopes of Work (SOW)** + cover emails for **WTC Winnipeg** from discovery-call notes.
- Connected services I use with Claude: Google Drive, Microsoft 365 (Outlook/Teams/SharePoint), Notion, GitHub,
  Expedia, Tripadvisor. Stripe and IBISWorld connectors exist but need (re)authorization.
- Preferences seen so far: wants complete, ready-to-use outputs; plain kebab-case names; dry runs before anything external.

## 2. The workbench (`tamirtm/TestingF`)
Pipeline for every build: **find → vet → vendor → study → adapt → build → test**.

| Path | What | Rules |
|---|---|---|
| `vendor/<name>/` | Upstream code, pinned, never edited | Fetched by `scripts/vendor.sh`; gitignored; pinned in `vendor/manifest.tsv` |
| `projects/<name>/` | Adapted builds | Own README, tests, `NOTICE.md` crediting upstream |
| `lab/skills/<name>/` | Skills under test | Skill folder + `evals/`; run `scripts/eval-skill.sh <name>` |
| `lab/workflows/<name>/` | Automations under test | `run.sh`, `fixtures/`, `expected/`, `test.sh`; `DRY_RUN=1` default |
| `scripts/` | Tooling | `test-all.sh` = single CI entry point |
| `.claude/` | Claude Code config | skills, `recon-mapper` agent, SessionStart hook, permissions |
| `handoff/` | This memory pack | |

### Hard rules (apply to every agent, local or cloud)
1. **License before copying a line**: `scripts/license-check.sh vendor/<name>`.
   - MIT/BSD/ISC/Unlicense → OK, keep copyright in NOTICE.md. Apache-2.0 → OK, keep LICENSE/NOTICE, mark changed files.
   - MPL-2.0 → file-level copyleft. LGPL → link freely, share changes to the lib.
   - **GPL/AGPL → STOP, ask** (makes the whole project GPL/AGPL; AGPL also covers network use).
   - **No license → read-only, never copy.**
2. **Reverse engineering only for code we may study**: open source, our own, licensed, or interoperability.
   Never bypass licence checks, DRM, auth, or extract secrets/keys.
3. **Every project change ships with a test.** Run `scripts/test-all.sh` before saying "done". Never skip/weaken tests.
4. **External side effects run with `DRY_RUN=1`** until the human says go.
5. Secrets only from env vars; never commit them; `.env` files are not read.
6. `vendor/**` is never edited; no `git push --force`.

### Scripts
- `scripts/vendor.sh <git-url> [name] [ref]` — clone at a pinned commit, record license in manifest.
  `scripts/vendor.sh --restore` — re-fetch everything in `vendor/manifest.tsv` (fresh machine).
- `scripts/license-check.sh <dir> [--short]` — identify license + verdict.
- `scripts/test-all.sh` — runs every `projects/*` and `lab/workflows/*` suite by detected stack
  (`test.sh` → npm → `uv run --with pytest pytest -q` → cargo → go). Last run 2026-10-24: **2 suites, all pass**
  (mpc-deck-builder 11 tests; inbox-triage ok).
- `scripts/eval-skill.sh <name>` — `claude plugin eval` with 3 runs/case, no-skill baseline, US$2 cap, threshold 0.8, no publish.

### Tooling assumptions
Python via **uv**, Node via npm, Rust cargo, Go go. Playwright + Chromium for UI tests.
RE tools: radare2, binwalk, gdb, strace, ltrace, xxd, 7z, js-beautify, webcrack, jadx (optional).
CI: GitHub Actions `ubuntu-latest` + `astral-sh/setup-uv@v5` → `scripts/test-all.sh`.

### Vendored upstreams
| name | url | commit | license | how used |
|---|---|---|---|---|
| mpc-autofill | github.com/chilli-axe/mpc-autofill | ceb7c3b2f39b8c8caebe396ec87f2bddba6c3743 | AGPL | **Studied for interoperability only** (order.xml format). No code copied. |

## 3. Projects
### `projects/mpc-deck-builder` (Python ≥3.11, Pillow; CLI `mpcdeck`)
Deck list → Scryfall lookup → art + frame + text render → PNGs with 1/8" bleed → `order.xml` for MPC Autofill.
```
uv run mpcdeck decks/<deck>.txt -o out/<deck>                 # 600 DPI, S30 stock
uv run mpcdeck decks/<deck>.txt -o out/<deck> --dpi 800 --stock S33 --foil
uv run mpcdeck - -o out/quick < list.txt                      # stdin
```
Flags: `--dpi` (600) · `--stock` (S30 default; choices from `order.STOCKS`) · `--foil` · `--art art/` · `--frames frames/` ·
`--custom custom/` (finished designs used as-is) · `--cardback file.png` · `--full-scans` (playtest only) · `--cache .cache/scryfall`.

Card spec: trim 2.48×3.46 in; **output with bleed 2.72×3.70 in** (0.12"/side) =
816×1110 @300, **1632×2220 @600**, 2176×2960 @800. Frame's black border runs through the bleed.

Deck formats accepted: `4 Lightning Bolt`, `4x …`, `1 Sol Ring (C21) 263`, `A // B` (DFC/split), `*F*` foil markers,
`Deck`/`Sideboard`/`Commander` headers, Archidekt category tags; duplicate lines merge. DFC backs go to `backs/`,
others get `cardback.png`. Split-card filenames handled.

Overrides: `art/<Card Name>.png|jpg` · `frames/<key>.png` (key ∈ W U B R G gold artifact land; bleed-size canvas,
transparent art window; text positions in `LAYOUT` in `mpcdeck/render.py`) · `fonts/{regular,bold,italic}.ttf` ·
`custom/<Card Name>.png` (finished card, bleed added if missing).

Output: `out/<deck>/{fronts,backs}/*.png`, `cardback.png`, `order.xml` (relative paths → **run MPC Autofill from inside that folder**).
Network needs `api.scryfall.com` + `cards.scryfall.io` (rate-limited ~10 req/s, cached).
Scryfall `art_crop` is ~626 px wide → upscale (e.g. Real-ESRGAN) into `art/` for sharp 600+ DPI prints.

**Rights**: names, rules text, official art and frames belong to Wizards of the Coast / the artists. Personal playtest
proxies only. **Anything sold must use original frames (the built-in one is original) and owned/licensed art via `art/`
or `custom/`. Never `--full-scans` for cards to be sold** (keeps official frame + copyright line; MPC rejects those).

Code map: `mpcdeck/cli.py` (args, orchestration) · `decklist.py` (parser) · `scryfall.py` (API + cache) ·
`render.py` (frames/text/LAYOUT) · `bleed.py` (bleed extension) · `order.py` (order.xml, STOCKS) ·
tests in `tests/` with offline fixture `tests/fixtures/cards.json`. Decks on file: `decks/smoke-test.txt`, `decks/vintage-cube.txt`.

## 4. Skills (portable instructions — reuse with any agent)
Each lives at `TestingF/.claude/skills/<name>/SKILL.md`. Summaries:

- **oss-adopt** — Find (≤3 candidates: repo|stars|last commit|license|issues|fit; drop unlicensed/abandoned/toys) →
  vet (`vendor.sh`, `license-check.sh`, run its own tests, skim install scripts for network/obfuscation) →
  adapt, lightest first: depend → wrap → copy files → fork; NOTICE.md (url, commit, license, files, changes) →
  hand off to build-test with license obligations + test command.
- **code-recon** — Scope check first (allowed: OSS/own/licensed/interop; refuse DRM/auth/secret extraction).
  Repos: produce RECON.md = Purpose · Entry points · Module map · Data flow with file:line · Side effects · Tests · Gotchas;
  prove it with one test. Minified JS: js-beautify/webcrack. Binaries: file, strings, xxd, binwalk, objdump/r2, readelf,
  strace/ltrace, jadx. Formats: 3+ samples → diff → parser + round-trip test.
- **build-test** — Detect stack → install → build (fix root cause) → add smoke test if none + test for the change →
  ensure root `test-all.sh` picks it up → report ✅/‼️ per suite with first error lines. Never claim an unrun pass.
- **skill-lab** — Skill = `lab/skills/<n>/skills/<n>/SKILL.md` + `.claude-plugin/plugin.json`. Description decides triggering
  (what + when, in user's words). Body ≤ ~150 lines. ≥3 evals: should-trigger, hard case, should-NOT-trigger.
  Change one thing per round; log scores in CHANGELOG.md; must beat no-skill baseline.
- **workflow-lab** — `run.sh` (DRY_RUN=1 default), `fixtures/` (scrubbed), `expected/`, `test.sh`, README (trigger, inputs,
  outputs, side effects, env vars, schedule). Idempotent, one timestamped log line per step. Headless Claude:
  `claude -p "<task>" --output-format json --max-turns N --max-budget-usd X` → parse `.result`.
- **mpc-deck** — save list to `decks/<kebab-name>.txt` → ask only if unclear (DPI 600, S30, no foil, card back) → run mpcdeck →
  verify PNG counts vs order summary + view one card → zip `out/<deck>` → send zip → tell user to run Autofill from inside
  the folder and which stock/bracket. No faking output if Scryfall is blocked; ask about unknown card lines.
- **commit-msg** (lab example, eval Δ +0.67 vs baseline) — Conventional Commits:
  `<type>(<scope>): <imperative ≤60 chars>` + 1–3 line why wrapped at 72; types feat fix refactor docs test chore perf build ci;
  one logical change per commit (else propose split); output only the message in a code block; don't commit unless asked.

Agent: **recon-mapper** (read-only; Read/Grep/Glob/Bash) returns Purpose · Entry points · Module map · Data flow (file:line) ·
Side effects · How to run tests · Open questions.

Workflow example: **inbox-triage** — `./run.sh <inbox> [dest]` sorts notes by keyword into finance (invoice/receipt/payment),
dev (bug/error/stack trace), meetings (meeting/call with), review (else). Moves only when `DRY_RUN=0`.

Account-level skills I also have in Claude (not in the repo): proxy-box-designer (WPG Proxy Prints packaging),
wtcw-mi-sow-builder (WTC Winnipeg MI SOW), docs/docx/pptx/xlsx/pdf, deep-research, dataviz, skill-creator, morning brief.

## 5. Models & API notes (Claude, as of 2026-10)
| Use | Model ID | $/1M in / out |
|---|---|---|
| Default, hard work | `claude-opus-5-5` | 4 / 20 |
| Everyday coding/agents, cheaper | `claude-sonnet-5-5` | 2 / 10 |
| Bulk / subagents / classifiers | `claude-haiku-5-5` | 0.10 / 0.50 (≤100K prompt) |
| Most capable, slow, pricey | `claude-fable-5-1` | 10 / 50 |
All 1M context, 128K max output. Use exact IDs, no date suffix.

Gotchas on current models:
- Thinking: send `thinking: {type: "adaptive"}` or omit it. `budget_tokens` and (Opus 5.5) `{type:"disabled"}` → 400.
  Control depth with `output_config: {effort: "low"|"medium"|"high"|"xhigh"|"max"}`. Opus 5.5 defaults to **medium** — set it.
- No assistant prefill (400). Use structured outputs: `output_config: {format: {...}}` / `client.messages.parse()`.
- Forced `tool_choice` `any`/`tool` → 400 on Opus 5.5 / Sonnet 5.5 / Fable 5.1; use `auto` + `strict: true` tools.
- `temperature`/`top_p`/`top_k` are rejected on current models.
- Always check `stop_reason` (`refusal` exists) before reading content. Stream when `max_tokens` is large.
- Return all parallel `tool_result`s in one user message; failed tool → `is_error: true`.
- Prompt caching is prefix-based (tools → system → messages); keep stable content first.

Minimal Python call:
```python
import anthropic
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY (or `ant auth login` profile)
msg = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,
    output_config={"effort": "high"},
    messages=[{"role": "user", "content": "Hello"}],
)
print(msg.content[0].text if msg.stop_reason != "refusal" else "refused")
```
Agent options: manual tool loop · SDK Tool Runner (`client.beta.messages.tool_runner`) · Claude Agent SDK
(`claude-agent-sdk`, Claude Code as a library) · Managed Agents (Anthropic-hosted).

Local (non-Claude) models: the rules, skills and project facts above are model-agnostic. Small local models follow
short numbered checklists better than prose — feed them the SKILL.md bodies verbatim and `system-prompt.md`.

## 6. Open threads / next steps
- No PRs open. Branch used by Claude sessions: `claude/stoic-hypatia-xdb0ok` (both repos).
- mpc-deck-builder ideas not done: art upscaling step, more custom frame sets, real `vintage-cube` print run.
- `hello-world` has no code; safe to use for experiments.
- To restore on a new machine: `git clone https://github.com/tamirtm/TestingF && cd TestingF && scripts/vendor.sh --restore && scripts/test-all.sh`.
