<div align="center">

<br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".github/assets/banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset=".github/assets/banner-light.svg">
  <img alt="Claude Code CLI Tools" src=".github/assets/banner-light.svg" width="800">
</picture>

<br/>

[![License: MIT](https://img.shields.io/badge/license-MIT-a3a3a3.svg?style=flat-square)](LICENSE)&ensp;
[![Claude Code](https://img.shields.io/badge/claude%20code-compatible-7c3aed.svg?style=flat-square)](https://docs.anthropic.com/en/docs/claude-code)

<br/>

*Drop into `~/.claude/` -- works across every project.*

</div>

<br/>

<img src=".github/assets/divider.svg" width="100%" height="12">

<br/>

This repo ships a complete `~/.claude/` configuration. Slash commands cover the git-to-GitHub workflow. Skills activate on-demand when Claude recognises a matching task. Hooks auto-approve safe operations and hard-block dangerous ones. A settings file pre-approves ~170 command patterns so Claude can work fluidly with minimal permission prompts.

<br/>

<details>
<summary>&ensp;<strong>Repository structure</strong></summary>

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

skills/                               symlinked to ~/.claude/skills
 |- agent-teams/                      coordinated agent squads
 |- ansi-table/                       terminal table rendering
 |- land-pr/                          merge PR, clean up branch
 |- ralph-loop/                       autonomous bubblewrap iteration
 |- rust-skills/                      179 Rust coding rules
 |- subagent-guide/                   subagent prompt engineering
 |
 |- algorithmic-art/                  generative art with p5.js
 |- brand-guidelines/                 Anthropic brand colours/typography
 |- canvas-design/                    visual art in .png/.pdf
 |- claude-api/                       Claude API / Anthropic SDK
 |- doc-coauthoring/                  co-authoring docs and specs
 |- docx/                             Word document manipulation
 |- frontend-design/                  production-grade UI design
 |- internal-comms/                   newsletters, FAQs, updates
 |- mcp-builder/                      MCP server creation
 |- pdf/                              PDF read/write/merge/OCR
 |- pptx/                             PowerPoint manipulation
 |- skill-creator/                    skill authoring with eval loop
 |- slack-gif-creator/                animated GIFs for Slack
 |- theme-factory/                    styling toolkit with presets
 |- web-artifacts-builder/            React/Vite/Tailwind artifacts
 |- webapp-testing/                   Playwright web testing
 '- xlsx/                             spreadsheet manipulation
```

</details>

<br/>
<img src=".github/assets/divider.svg" width="100%" height="12">
<br/>

## Commands

<br/>

<table>
<tr>
<td width="20"></td>
<td width="180"><kbd>/commit</kbd></td>
<td>AI-generated commit messages, branch safety checks, auto-branching for merged PRs, domain-based commit splitting. <code>--no-auto-stage</code> to skip staging.</td>
<td width="20"></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><kbd>/create-pr</kbd></td>
<td>Conventional commit titles, descriptions scaled by change complexity, merge strategy recommendations. <code>--draft</code> for draft PRs.</td>
<td></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><kbd>/create-issue</kbd></td>
<td>Structured GitHub issues with smart suggestions aligned to project scope.</td>
<td></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><kbd>/fix-issue --&lt;n&gt;</kbd></td>
<td>Analyses a GitHub issue and proposes code changes that fit the project architecture.</td>
<td></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><kbd>/close-issue --&lt;n&gt;</kbd></td>
<td>Closes with a contextual comment, auto-detecting the resolving commit or PR.</td>
<td></td>
</tr>
</table>

<br/>
<img src=".github/assets/divider.svg" width="100%" height="12">
<br/>

## Skills

Skills stay out of context until Claude determines they match the current task, then load on-demand.

<br/>

**Custom skills** built for this workflow:

<table>
<tr>
<td width="20"></td>
<td width="180"><code>agent-teams</code></td>
<td>Coordinates agent teams (squads) for parallel work requiring inter-agent communication -- competing hypotheses, cross-layer changes, multi-component features.</td>
<td width="20"></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><code>subagent-guide</code></td>
<td>Loaded automatically before any use of the Agent tool. Covers prompt design for subagents (which start with zero context), critical thinking, domain awareness, and model selection.</td>
<td></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><code>ansi-table</code></td>
<td>Renders CSV, parquet, dataframes, and analysis results as colour-coded Unicode box-drawing tables in the terminal with automatic column sizing and width constraints.</td>
<td></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><code>land-pr</code></td>
<td>Merges the current PR (squash or rebase), deletes the branch, checks out main, and pulls. Invoked manually with <kbd>/land-pr</kbd>.</td>
<td></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><code>ralph-loop</code></td>
<td>Autonomous coding workflow where Claude runs inside a bubblewrap sandbox with iterative execution until acceptance criteria are met.</td>
<td></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><code>rust-skills</code></td>
<td>179 Rust-specific coding rules across 14 categories: ownership, error handling, async patterns, API design, memory optimisation, performance, testing, and common anti-patterns.</td>
<td></td>
</tr>
</table>

<br/>

**Vendored from <a href="https://github.com/anthropics/skills">anthropics/skills</a>** (Apache 2.0):

<table>
<tr>
<td width="20"></td>
<td width="180"><code>skill-creator</code></td>
<td>Full skill authoring workflow with eval loop, benchmarking, description optimisation, and blind A/B comparison.</td>
<td width="20"></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><code>claude-api</code></td>
<td>Claude API and Anthropic SDK reference for Python, TypeScript, Java, Go, Ruby, C#, and PHP.</td>
<td></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><code>pdf</code> &middot; <code>docx</code> &middot; <code>pptx</code> &middot; <code>xlsx</code></td>
<td>Document processing -- read, write, merge, split, fill forms, track changes, validate schemas.</td>
<td></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><code>frontend-design</code></td>
<td>Production-grade frontend interfaces with bold aesthetic direction, avoiding generic AI aesthetics.</td>
<td></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><code>mcp-builder</code></td>
<td>MCP server creation guide covering Python (FastMCP) and TypeScript (MCP SDK) with evaluation scripts.</td>
<td></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><code>webapp-testing</code></td>
<td>Playwright-based web application testing with helper scripts and screenshot/logging capabilities.</td>
<td></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td colspan="2"><code>canvas-design</code> &middot; <code>algorithmic-art</code> &middot; <code>brand-guidelines</code> &middot; <code>theme-factory</code> &middot; <code>web-artifacts-builder</code> &middot; <code>doc-coauthoring</code> &middot; <code>internal-comms</code> &middot; <code>slack-gif-creator</code></td>
<td></td>
</tr>
</table>

<br/>
<img src=".github/assets/divider.svg" width="100%" height="12">
<br/>

## Hooks

Hooks fire on Claude Code events and serve two purposes.

<br/>

> [!TIP]
> **Auto-approval** -- reads, edits, piped bash, SSH, and web fetches are approved without prompting, so Claude works fluidly without constant permission dialogs.

> [!WARNING]
> **Safety blocking** -- `.env` files cannot be read or written. `git push --force` is rejected. Destructive Proxmox commands are blocked before execution. These run as `PreToolUse` hooks, so the operation never reaches Claude's tools.

<br/>

All hooks share `hook_utils.py` for common patterns. `test_hooks.py` provides the test suite.

<br/>
<img src=".github/assets/divider.svg" width="100%" height="12">
<br/>

## Configuration

<br/>

<table>
<tr>
<td width="20"></td>
<td width="200"><strong>settings.json</strong></td>
<td>Binds hooks to events, sets the default model to Opus, configures the statusline, enables plugins (rust-analyzer LSP), and defines ~170 pre-approved command patterns spanning git, GitHub CLI, Docker, Proxmox, ZFS, npm, cargo, and common system utilities.</td>
<td width="20"></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><strong>CODING-STANDARDS.md</strong></td>
<td>Standards for all code Claude produces: DRY/KISS/SOLID, async discipline, security at boundaries, TDD with AAA structure, fail-fast validation, observable fallbacks, conventional commits.</td>
<td></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><strong>RALPH-LOOP.md</strong></td>
<td>Autonomous iteration loop where Claude runs repeatedly inside a <a href="https://github.com/containers/bubblewrap">bubblewrap</a> sandbox -- reading a prompt, working, committing, and continuing until acceptance criteria are met.</td>
<td></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><strong>statusline.sh</strong></td>
<td>Multi-line status bar showing directory, git branch, latest commit, model, Claude Code version, context window remaining, session time, and burn rate. Built with <a href="https://www.npmjs.com/package/@chongdashu/cc-statusline">cc-statusline</a>.</td>
<td></td>
</tr>
<tr><td colspan="4"></td></tr>
<tr>
<td></td>
<td><strong>mcp_servers.json</strong></td>
<td>Registers <a href="https://playwright.dev/">Playwright</a> as an MCP server for browser automation during QA.</td>
<td></td>
</tr>
</table>

<br/>
<img src=".github/assets/divider.svg" width="100%" height="12">
<br/>

## Installation

Requires [Claude Code](https://docs.anthropic.com/en/docs/claude-code/quickstart), [GitHub CLI](https://cli.github.com/) (`gh auth login`), and git with your identity configured.

```bash
git clone https://github.com/MoonBoi9001/claude-code-cli-tools.git
cd claude-code-cli-tools

# Global settings
cp -ri "global .claude settings/." ~/.claude/

# Skills (symlink so updates take effect immediately)
ln -sfn "$(pwd)/skills" ~/.claude/skills
```

> [!NOTE]
> The `-i` flag prompts before overwriting existing files. The skills symlink means edits to `skills/` in the repo are live immediately -- no re-copying needed. Restart Claude Code after initial setup.

<br/>
<img src=".github/assets/divider.svg" width="100%" height="12">
<br/>

## Making It Yours

This configuration reflects a workflow across blockchain infrastructure, Proxmox homelab management, and web development. The permission lists, hooks, and statusline are tuned for that context -- trim what you don't need, extend what's missing. Hooks toggle individually in `settings.json`. Skills are self-contained directories; remove any, or author new ones with <kbd>/skill-creator</kbd>. Anthropic skills are vendored from <a href="https://github.com/anthropics/skills">anthropics/skills</a>; to update, pull that repo and re-copy.

<br/>

---

<div align="center">

<br/>

<sub>MIT License -- see <a href="LICENSE">LICENSE</a></sub>

<br/><br/>

</div>
