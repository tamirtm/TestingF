---
name: commit-msg
description: Write a Conventional Commits message for staged or described changes. Use when the user asks for a commit message, to "commit this", or to summarise a diff as a commit.
---
# Commit message
1. Get the change: `git diff --cached` (fall back to `git diff`, or the user's description).
2. Format:
   ```
   <type>(<scope>): <imperative summary, ≤ 60 chars>

   <why, wrapped at 72 — 1–3 lines>
   ```
   type ∈ feat, fix, refactor, docs, test, chore, perf, build, ci. Scope = main dir/module touched.
3. One logical change per commit. If the diff mixes several, propose a split instead.
4. Output only the message in a code block: no preamble, no notes after it, even when you
   couldn't read the diff (then write it from the user's description as-is).
   Don't run `git commit` unless asked.
