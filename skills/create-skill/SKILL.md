---
name: create-skill
description: Create a new Claude Code skill (SKILL.md). Use this skill when the user asks to create a new skill, or wants to turn something (like an existing workflow) into a skill.
---

# Creating Claude Code Skills

A skill is a markdown file that teaches Claude how to do something specific. Claude loads it on-demand when it matches the task, keeping it out of context until needed.

## Before You Build

Not everything should be a skill.

| Situation | Right tool |
|-----------|-----------|
| Guidance needed in every conversation | CLAUDE.md |
| Specialized knowledge for a specific task type | Skill |
| A deliberate action the user triggers manually | Skill with `disable-model-invocation: true` |
| One-off instructions or rarely-used workflows | Nothing -- not everything needs abstraction |

Skills compete for a shared context budget (2% of the context window, fallback 16,000 chars). Every skill's description is always in context. Prefer fewer, well-described skills over many vague ones.

## File Structure

```bash
skill-name/
  SKILL.md           # Required -- the skill definition
  supporting-file.md # Optional -- referenced docs, templates, examples
  scripts/           # Optional -- executable utilities
```

Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files and reference them from `SKILL.md`.

## Placement

Ask the user where the skill should live:

- **Personal** (`~/.claude/skills/<skill-name>/SKILL.md`) -- follows the user across all projects.
- **Project** (`.claude/skills/<skill-name>/SKILL.md`) -- committed to the repo, shared with the team.

## Frontmatter

| Field | Default | Purpose |
|-------|---------|---------|
| `name` | directory name | Display name and `/slash-command`. Lowercase, hyphens, numbers only. Max 64 chars. |
| `description` | -- | How Claude decides when to auto-invoke. Trigger conditions, not marketing copy. Max 1024 chars. |
| `argument-hint` | -- | Autocomplete hint, e.g. `[issue-number]`. |
| `disable-model-invocation` | `false` | Set `true` to prevent auto-invocation. Use for destructive or side-effect operations. |
| `user-invocable` | `true` | Set `false` to hide from `/` menu. Use for background knowledge only. |
| `allowed-tools` | -- | Tools Claude can use without asking when this skill is active. |
| `context` | -- | Set to `fork` to run in an isolated subagent context. |
| `agent` | -- | Subagent type when `context: fork`. Options: `Explore`, `Plan`, `general-purpose`, or custom agents. |
| `hooks` | -- | Hooks scoped to this skill's lifecycle. |

Most skills only need `name` and `description`.

**Description must be a single line.** Do not use YAML multi-line syntax (`>`, `|`, or line breaks) for the `description` field. Write the entire description on the same line as `description:`. Multi-line descriptions break skill loading.

## Content

The markdown body after frontmatter is what Claude reads when the skill activates. Two patterns:

**Reference content** adds knowledge Claude applies inline (conventions, patterns, domain knowledge). Leave `disable-model-invocation` at false so Claude pulls it in automatically.

**Task content** gives step-by-step instructions for a specific action. Often paired with `disable-model-invocation: true` and/or `context: fork`.

Use imperative form. Explain the why behind instructions rather than relying on rigid MUSTs. Include examples where they clarify expected output.

### Dynamic Context

`` !\u200B`command` `` runs shell commands before the content reaches Claude:

```markdown
Current branch: !\u200B`git branch --show-current`
```

### Arguments

When invoked as `/skill-name arg1 arg2`: `$ARGUMENTS` (all), `$0`, `$1` (by index). If `$ARGUMENTS` isn't in the content, arguments are appended automatically.

## Writing Descriptions

The description is the most important field. Claude uses language model reasoning (not keyword matching) to decide activation, and tends to undertrigger. Descriptions should lean slightly assertive about when the skill applies.

**Good:** `Create a new Claude Code skill. Use when the user asks to create, build, or make a skill, or wants to turn something into a skill.`

**Bad:** `A powerful tool for managing skill creation workflows with best practices.`

Be specific about when to trigger. Mention verbs and nouns a user would actually say. List contexts where the skill applies even if not asked for by name. Avoid overlap with other skill descriptions.

## Process

1. **Clarify scope** -- personal or project?
2. **Choose a name** -- lowercase, hyphenated. This becomes the `/slash-command`.
3. **Write the description** -- trigger conditions. Lean slightly pushy to counter undertriggering.
4. **Set frontmatter** -- start with just `name` and `description`. Add other fields only when needed.
5. **Write the content** -- clear, concise instructions with examples where helpful.
6. **Create the files** -- write `SKILL.md` and any supporting files.

## Troubleshooting

**Not triggering:** Check the description includes words users would naturally say. Verify with "What skills are available?" Make the description more assertive.

**Triggering too often:** Make the description more specific, or add `disable-model-invocation: true`.

**Skills crowding each other out:** Run `/context` to check for budget warnings. Consolidate or remove underperforming skills.
