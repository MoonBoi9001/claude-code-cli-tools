# Claude Workflow Automation

---

**This repository contains powerful commands for developers using Claude Code.**

## What This Gives You

**Your New Claude Code Superpowers:**
1. **`/create-issue [flags]`** - Plan and document tasks with AI-assisted GitHub issue creation, including smart suggestions aligned with your project's scope for better team collaboration. Supports `--update` for session persistence.
2. **`/fix-issue --<issue-number> [flags]`** - Let Claude analyze GitHub issues and propose tailored code solutions that fit your project's architecture. Supports `--update` for session persistence.
3. **`/commit [flags]`** - Smart commit workflow with AI-generated messages, branch safety checks, auto-branching for merged PRs, and intelligent domain-based commit splitting. Supports `--no-auto-stage` to skip auto-staging and `--update` for session persistence.
4. **`/close-issue --<issue-number> [flags]`** - Automatically close GitHub issues with contextual comments to the issue thread, intelligently detecting and referencing the commit or PR that fixed the issue. Supports `--update` for session persistence.
5. **`/create-pr [flags]`** - Generate pull requests with conventional commit titles, context-aware descriptions scaled by change complexity, and merge strategy recommendations. Supports `--draft` for draft PRs and `--update` for session persistence.

**Utility Commands:**
- **`/update-session`** - Manually persist key session insights to `SESSION_CONTEXT.md` for long-term documentation, enabling easy recaps in future Claude instances.

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

### Step 2: Set Up Each Project (30 seconds)

In any project where you want to use these commands:

```bash
# Run this one command:
curl -s https://raw.githubusercontent.com/MoonBoi9001/claude-code-cli-tools/main/SESSION_CONTEXT.md -o SESSION_CONTEXT.md && \
[ -s CLAUDE.md ] && echo -e "\n" >> CLAUDE.md || true; \
echo -e "# Session Context Import\n@./SESSION_CONTEXT.md" >> CLAUDE.md && \
grep -q "SESSION_CONTEXT.md" .gitignore 2>/dev/null || echo "SESSION_CONTEXT.md" >> .gitignore
```

This command:
- Downloads SESSION_CONTEXT.md 
- Adds the import to your CLAUDE.md (creates it if needed)
- Adds SESSION_CONTEXT.md to .gitignore (creates it if needed)

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
- `/update-session` - Persist session insights to external memory.

**Project Files**:
- `CLAUDE.md` - Auto-loaded by Claude (commit this)
- `SESSION_CONTEXT.md` - Your private notes (gitignored)

---

## 🔧 Troubleshooting

### Claude Code CLI Installation Issues

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

**"cp: cannot create directory"**
- Create parent directory first: `mkdir -p ~/.claude`

**"command not found: claude"**
- Install Claude Code CLI: https://docs.anthropic.com/en/docs/claude-code/quickstart

**Commands not working in project**
- Ensure CLAUDE.md exists and imports SESSION_CONTEXT.md
- Verify SESSION_CONTEXT.md exists in project root

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
