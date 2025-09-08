# Claude Workflow Automation

---

**This repository contains powerful commands for developers using Claude Code.**

## What This Gives You

**Your New Claude Code Superpowers:**

1. **`/create-issue [flags]`** - Plan and document tasks with AI-assisted GitHub issue creation, including smart suggestions aligned with your project's scope for better team collaboration.
2. **`/fix-issue --<issue-number> [flags]`** - Let Claude analyze GitHub issues and propose tailored code solutions that fit your project's architecture.
3. **`/commit [flags]`** - Smart commit workflow with AI-generated messages, branch safety checks, auto-branching for merged PRs, and intelligent domain-based commit splitting. Supports `--no-auto-stage` to skip auto-staging.
4. **`/close-issue --<issue-number> [flags]`** - Automatically close GitHub issues with contextual comments to the issue thread, intelligently detecting and referencing the commit or PR that fixed the issue.
5. **`/create-pr [flags]`** - Generate pull requests with conventional commit titles, context-aware descriptions scaled by change complexity, and merge strategy recommendations. Supports `--draft` for draft PRs.

## Prerequisites

Before installing, ensure you have:

- **Claude Code CLI** installed ([installation guide](https://docs.anthropic.com/en/docs/claude-code/quickstart))
- **GitHub CLI** installed and authenticated (`gh auth login`)
- **Git** configured with your email and name

## Quick Setup

### Step 1: Install Global Settings (one time only)

```bash
# 1. Clone the repository:
git clone https://github.com/MoonBoi9001/claude-code-cli-tools.git
cd claude-code-cli-tools

# 2. Copy settings to your home directory:
cp -ri "global .claude settings/." ~/.claude/

# 3. Verify installation:
ls ~/.claude/commands/  # Should show: commit.md, create-pr.md, etc.
```

**Manual installation:** Download as ZIP, then copy `global .claude settings/` contents to `~/.claude/`

**That's it!** 🎉 Start using `/commit`, `/create-pr` and more.

## 🚀 Quick Start

```bash
# View all available commands:
ls ~/.claude/commands/
```

### What You Just Installed

**Commands** (in ~/.claude/commands/):

- `/commit [flags]` - Smart commits with AI-generated messages, safety checks, auto-branching, and domain splitting.
- `/create-pr [flags]` - Generate PRs with conventional titles and scaled descriptions.
- `/create-issue [flags]` - Create well-structured, AI-powered GitHub issues with context awareness.
- `/fix-issue --<issue-number> [flags]` - Analyze issues and implement solutions.
- `/close-issue --<issue-number> [flags]` - Close issues with automatic resolution detection.

**Project Files**:

- `CLAUDE.md` - Auto-loaded by Claude (commit this)

---

## 🔧 Troubleshooting

### Claude Code CLI Installation Issues

**Installation Protection (Prevents Breaking):**
The included health check scripts prevent Claude from breaking due to concurrent npm operations:

```bash
# If Claude stops working, run the health check:
~/.claude/local/claude-health-check.sh

# For automatic protection, update your shell alias:
alias claude="~/.claude/local/claude-wrapper.sh"
```

**Important:** If using `ccusage`, install it globally to prevent conflicts:

```bash
npm install -g ccusage
```

**macOS/Homebrew:**

```bash
# If Claude Code CLI isn't recognized after installation:
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

**Windows/WSL2:**

- Claude Code CLI requires WSL2 on Windows
- Install WSL2 first: `wsl --install`
- Then install Claude Code CLI inside WSL2

**Linux:**

```bash
# If permission denied:
chmod +x ~/.local/bin/claude
```

### Command Not Found

If `/commit` or other commands aren't recognized:

1. Verify files exist: `ls ~/.claude/commands/`
2. Restart Claude Code CLI
3. Check CLAUDE.md imports: `cat CLAUDE.md | grep @`

### GitHub CLI Authentication

```bash
# Check auth status:
gh auth status

# If not authenticated:
gh auth login
```

### Common Issues

cp: cannot create directory

- Create parent directory first: `mkdir -p ~/.claude`

command not found: claude

- Install Claude Code CLI: https://docs.anthropic.com/en/docs/claude-code/quickstart

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
