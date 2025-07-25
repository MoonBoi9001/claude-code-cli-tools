# Claude Workflow Automation

---

**This Repo contains powerful commands for developers using Claude Code.**

## What This Gives You

**Your New Claude Code Superpowers:**
1. **`/recap`** - Quickly regain context on your project's status, recent changes, open issues, and suggested next steps – for continuity across Claude sessions.
2. **`/create-issue`** - Plan and document tasks with AI-assisted GitHub issue creation, including smart suggestions aligned with your project's scope for better team collaboration.
3. **`/branch <issue-number>`** - Automatically generate and switch to semantically named branches linked to specific GitHub issues, ensuring organized development and easy progress tracking.
4. **`/fix-issue <issue-number>`** - Let Claude analyze GitHub issues and propose tailored code solutions that fit your project's architecture.
5. **`/commit`** - Create meaningful commits with AI-generated titles and detailed descriptions that capture change impacts, improving Git history usefullness.
6. **`/close-issue <issue-number>`** - Automatically close GitHub issues with contextual comments to the issue thread, additionally referencing the commit that fixed the issue.
7. **`/create-pr`** - Generate pull requests with insightful titles and descriptions highlighting changes, motivations, and benefits.

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

**That's it!** 🎉 Start using `/recap`, `/commit`, `/create-pr` and more.

### What You Just Installed

**Commands** (in ~/.claude/commands/):
- `/recap` - Get project context and suggested next steps
- `/commit` - Create meaningful commits with good messages
- `/create-pr` - Generate PRs with detailed descriptions
- `/branch <issue#>` - Create branches from GitHub issues
- `/create-issue` - Create well-structured GitHub issues
- `/fix-issue <issue#>` - Get implementation suggestions
- `/close-issue <issue#>` - Close issues with context
- `/update-session` - Save important discoveries

**Project Files**:
- `CLAUDE.md` - Auto-loaded by Claude (commit this)
- `SESSION_CONTEXT.md` - Your private notes (gitignored)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
