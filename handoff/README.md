# Memory handoff
Context pack for local AI agents, models, API clients and skills. Snapshot 2026-10-24.

| File | Use it for |
|---|---|
| `MEMORY.md` | Full human-readable memory: who/what, workbench rules, projects, skills, model/API notes, open threads |
| `memories.jsonl` | One fact per line (`id`, `type`, `tags`, `text`) for vector stores / memory tools |
| `system-prompt.md` | Paste as the system prompt of any local agent |
| `../.claude/skills/*/SKILL.md` | The skills themselves, verbatim; any agent can follow them |

## Importing
- **Claude Code (local)**: clone the repo; `CLAUDE.md` and `.claude/` load automatically. For memory across all
  projects, append `MEMORY.md` §1 and §5 to `~/.claude/CLAUDE.md`.
- **Claude.ai memory**: paste `MEMORY.md` into a chat and ask it to import it (the `import-memory` skill).
- **Claude API / Agent SDK**: put `system-prompt.md` (+ `MEMORY.md`) in `system`, with `cache_control` so it's cached.
- **Ollama**: `FROM <model>` + `SYSTEM """<system-prompt.md>"""` in a Modelfile; keep MEMORY.md as a RAG doc.
- **Open WebUI / LM Studio / AnythingLLM**: system prompt = `system-prompt.md`; add `MEMORY.md` and the SKILL.md files to a knowledge base.
- **mem0 / Letta / Chroma / any vector store**: load `memories.jsonl`, embedding `text`, storing the rest as metadata:
  ```python
  import json
  for line in open("handoff/memories.jsonl"):
      m = json.loads(line)
      store.add(m["text"], metadata={"id": m["id"], "type": m["type"], "tags": m["tags"]})
  ```
- **Aider / Continue / Cline / Cursor**: point their rules/conventions file at `system-prompt.md`.

Update this pack when rules, projects or skills change. `MEMORY.md` is the source; keep `memories.jsonl` in sync.
