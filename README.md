<div align="center">

# Claude Code CLI Tools

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/built%20for-Claude%20Code-7c3aed.svg)](https://docs.anthropic.com/en/docs/claude-code)

**Global settings, skills, hooks, and slash commands for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).**

Drop into `~/.claude/` and forget about it -- works across every project.

</div>

<br/>

## Overview

This repo ships a complete `~/.claude/` configuration. Slash commands cover the git-to-GitHub workflow. Skills activate on-demand when Claude recognises a matching task. Hooks auto-approve safe operations and hard-block dangerous ones. A settings file pre-approves ~170 command patterns so Claude can work fluidly with minimal permission prompts.

<details>
<summary><strong>Repository structure</strong></summary>

<br/>

```
global .claude settings/
 |- CLAUDE.md                      global instructions
 |- CODING-STANDARDS.md            DRY, KISS, SOLID, TDD, fail-fast, no silent failures
 |- RALPH-LOOP.md                  autonomous iteration loop in bubblewrap sandbox
 |- settings.json                  permissions, hooks, model, statusline, plugins
 |- mcp_servers.json               Playwright browser automation
 |- statusline.sh                  context window, git, model, session, burn rate
 |- permission-sound.sh            audio notification on permission request
 |
 |- commands/
 |   |- commit.md                  /commit
 |   |- create-pr.md               /create-pr
 |   |- create-issue.md            /create-issue
 |   |- fix-issue.md               /fix-issue
 |   '- close-issue.md             /close-issue
 |
 |- hooks/
 |   |- auto-approve-reads.py      Read, Glob, Grep
 |   |- auto-approve-edits.py      Edit, Write
 |   |- auto-approve-piped-bash.py
 |   |- auto-approve-ssh.py
 |   |- auto-approve-webfetch.py
 |   |- block-env-files.py         .env read/write protection
 |   |- block-force-push.py        git push --force protection
 |   |- block-dangerous-proxmox.py
 |   |- hook_utils.py              shared utilities
 |   '- test_hooks.py
 |
 '- local/
     |- claude-wrapper.sh          wrapper with health check
     '- claude-health-check.sh

skills/
 |- agent-teams/SKILL.md           coordinated agent squads
 |- subagent-guide/SKILL.md        subagent prompt engineering
 |- ansi-table/SKILL.md            terminal table rendering
 '- create-skill/SKILL.md          skill authoring guide
```

</details>

<br/>

## Commands

Five slash commands handle the full git-to-GitHub lifecycle. Available in every Claude Code session once installed.

<table>
<tr>
<td width="180"><strong><code>/commit</code></strong></td>
<td>AI-generated commit messages, branch safety checks, auto-branching for merged PRs, domain-based commit splitting. <code>--no-auto-stage</code> to skip staging.</td>
</tr>
<tr>
<td><strong><code>/create-pr</code></strong></td>
<td>Conventional commit titles, descriptions scaled by change complexity, merge strategy recommendations. <code>--draft</code> for draft PRs.</td>
</tr>
<tr>
<td><strong><code>/create-issue</code></strong></td>
<td>Structured GitHub issues with smart suggestions aligned to project scope.</td>
</tr>
<tr>
<td><strong><code>/fix-issue --&lt;n&gt;</code></strong></td>
<td>Analyses a GitHub issue and proposes code changes that fit the project architecture.</td>
</tr>
<tr>
<td><strong><code>/close-issue --&lt;n&gt;</code></strong></td>
<td>Closes with a contextual comment, auto-detecting the resolving commit or PR.</td>
</tr>
</table>

<br/>

## Skills

Skills stay out of context until Claude determines they match the current task, then load on-demand.

<table>
<tr>
<td width="180"><strong>agent-teams</strong></td>
<td>Coordinates agent teams (squads) for parallel work requiring inter-agent communication -- competing hypotheses, cross-layer changes, multi-component features. Triggers on "squad", "agent squad", "team".</td>
</tr>
<tr>
<td><strong>subagent-guide</strong></td>
<td>Loaded automatically before any use of the Agent tool. Covers prompt design for subagents (which start with zero context), critical thinking, domain awareness, and model selection.</td>
</tr>
<tr>
<td><strong>ansi-table</strong></td>
<td>Renders CSV, parquet, dataframes, and analysis results as colour-coded Unicode box-drawing tables in the terminal. Handles column sizing, width constraints, and text wrapping automatically.</td>
</tr>
<tr>
<td><strong>create-skill</strong></td>
<td>A meta-skill for authoring new skills. Walks through placement, frontmatter, description writing, and troubleshooting undertriggering.</td>
</tr>
</table>

<br/>

## Hooks

Hooks fire on Claude Code events and serve two purposes.

> **Auto-approval** -- reads, edits, piped bash, SSH, and web fetches are approved without prompting, so Claude works fluidly without constant permission dialogs.

> **Safety blocking** -- `.env` files cannot be read or written. `git push --force` is rejected. Destructive Proxmox commands are blocked before execution. These run as `PreToolUse` hooks, so the operation never reaches Claude's tools.

All hooks share `hook_utils.py` for common patterns. `test_hooks.py` provides the test suite.

<br/>

## Configuration

| File | Role |
|------|------|
| **settings.json** | Binds hooks to events, sets the default model to Opus, configures the statusline, enables plugins (rust-analyzer LSP), and defines ~170 pre-approved command patterns spanning git, GitHub CLI, Docker, Proxmox, ZFS, npm, cargo, and common system utilities. |
| **CODING-STANDARDS.md** | Standards for all code Claude produces: DRY/KISS/SOLID, async discipline, security at boundaries, TDD with AAA structure, fail-fast validation, observable fallbacks, conventional commits. |
| **RALPH-LOOP.md** | Autonomous iteration loop where Claude runs repeatedly inside a [bubblewrap](https://github.com/containers/bubblewrap) sandbox -- reading a prompt, working, committing, and continuing until acceptance criteria are met. |
| **statusline.sh** | Multi-line status bar: directory, git branch, latest commit, model, Claude Code version, context window remaining, session time, burn rate. Built with [cc-statusline](https://www.npmjs.com/package/@chongdashu/cc-statusline). |
| **mcp_servers.json** | Registers [Playwright](https://playwright.dev/) as an MCP server for browser automation during QA. |

<br/>

## Installation

Requires [Claude Code](https://docs.anthropic.com/en/docs/claude-code/quickstart), [GitHub CLI](https://cli.github.com/) (`gh auth login`), and git with your identity configured.

```bash
git clone https://github.com/MoonBoi9001/claude-code-cli-tools.git
cd claude-code-cli-tools

# Global settings
cp -ri "global .claude settings/." ~/.claude/

# Skills
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
```

The `-i` flag prompts before overwriting existing files. Restart Claude Code after copying.

<br/>

## Making It Yours

This configuration reflects a workflow across blockchain infrastructure, Proxmox homelab management, and web development. The permission lists, hooks, and statusline are tuned for that context -- trim what you don't need, extend what's missing. Hooks toggle individually in `settings.json`. Skills are self-contained directories; remove any, or author new ones with `/create-skill`.

<br/>

---

<div align="center">
<sub>MIT License -- see <a href="LICENSE">LICENSE</a></sub>
</div>
