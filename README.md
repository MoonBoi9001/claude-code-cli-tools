# Claude Workflow Automation

---

**This Repo contains powerful commands for developers using Claude Code.**

## What This Gives You

**Your New Claude Code Superpowers:**
1. **`/create-issue [flags]`** - Plan and document tasks with AI-assisted GitHub issue creation, including smart suggestions aligned with your project's scope for better team collaboration. Supports `--update` for session persistence.
2. **`/fix-issue --<issue-number> [flags]`** - Let Claude analyze GitHub issues and propose tailored code solutions that fit your project's architecture. Supports `--update` for session persistence.
3. **`/commit [flags]`** - Smart commit workflow with AI-generated messages, branch safety checks, auto-branching for merged PRs, and intelligent domain-based commit splitting. Supports `--no-stage` to skip auto-staging and `--update` for session persistence.
4. **`/close-issue --<issue-number> [flags]`** - Automatically close GitHub issues with contextual comments to the issue thread, intelligently detecting and referencing the commit or PR that fixed the issue. Supports `--update` for session persistence.
5. **`/create-pr [flags]`** - Generate pull requests with conventional commit titles, context-aware descriptions scaled by change complexity, and merge strategy recommendations. Supports `--draft` for draft PRs and `--update` for session persistence.

**Utility Commands:**
- **`/update-session`** - Manually persist key session insights to SESSION_CONTEXT.md for long-term documentation, enabling easy recaps in future Claude instances. 

## Quick Setup (< 1 minute)

### Step 1: Install Commands (one time only)

```bash
# Clone and install in one command:
git clone https://github.com/MoonBoi9001/claude-code-cli-tools.git && \
mkdir -p ~/.claude/commands && \
cp -ri claude-code-cli-tools/commands/* ~/.claude/commands/
```

```bash
# If you're already in the claude-code-cli-tools directory:
cp -ri commands/* ~/.claude/commands/
```

**Or manually:** Download this repo as ZIP, create `~/.claude/commands/`, and copy all files from the `commands` folder there.

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

### What You Just Installed

**Commands** (in ~/.claude/commands/):
- `/commit [flags]` - Smart commits with safety checks, auto-branching, and domain splitting
- `/create-pr [flags]` - Generate PRs with conventional titles and scaled descriptions
- `/create-issue [flags]` - Create well-structured GitHub issues with context awareness
- `/fix-issue --<issue#> [flags]` - Analyze issues and implement solutions
- `/close-issue --<issue#> [flags]` - Close issues with automatic resolution detection
- `/update-session` - Persist session insights to external memory

**Project Files**:
- `CLAUDE.md` - Auto-loaded by Claude (commit this)
- `SESSION_CONTEXT.md` - Your private notes (gitignored)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
