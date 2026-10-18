---
name: skill-lab
description: Create, test, and iterate on Claude Code skills in lab/skills with real evals (claude plugin eval). Use for "make a skill", "test my skill", "why isn't my skill triggering", "improve this skill".
---
# Skill lab

## Create
`lab/skills/<name>/skills/<name>/SKILL.md`, with frontmatter `name` + `description`, plus
`lab/skills/<name>/.claude-plugin/plugin.json` (`{"name","version","description"}`). Without the
manifest the eval runner reports "Plugin under test: none resolved" and tests plain Claude.
Copy `lab/skills/commit-msg` as the template.
- The description decides when the skill triggers. Say WHAT it does and WHEN to use it, using the user's likely words.
- Keep the body under ~150 lines. Move long reference material into sibling files the skill tells Claude to read.
- Scripts the skill runs go next to SKILL.md (e.g. `scripts/`) and are referenced by relative path.

## Eval (claude plugin eval)
From `lab/skills/<name>/`:
- `claude plugin eval init --bare <case>` scaffolds `evals/<case>/prompt.md` + `graders/criteria.md`.
- Write at least 3 cases:
  - one where the skill **should trigger** (the user's words);
  - one realistic hard case;
  - one **should NOT trigger** (a nearby task).
- prompt.md frontmatter sets `max_turns` and `allowed_tools`. Graders are `type: llm` criteria files with a `weight`.
- Run `scripts/eval-skill.sh <name>`. It runs 3 runs per case, compares against a no-skill baseline, caps cost at US$2, and keeps the report local.
- Read the per-case scores and the with/without delta. A skill that doesn't beat the baseline isn't earning its tokens.

## Iterate
Change one thing per round: the description for triggering problems, the body for quality problems. Re-run and
keep a short changelog in `lab/skills/<name>/CHANGELOG.md` with each round's score.

## Ship
When it passes: copy `skills/<name>/` to wherever it's used (a project's `.claude/skills/`, or your
claude-skills repo) and note the eval score in its README.
