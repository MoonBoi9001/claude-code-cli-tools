# Claude Workflow Automation

---

**This Repo contains powerful tools for developers using Claude Code CLI.**

## What This Gives You

**Your new superpowers to use in the Claude CLI:**
1. **`/recap`** - Quickly regain context on your project's status, recent changes, open issues, and suggested next steps – for continuity across Claude sessions.
2. **`/create-issue`** - Plan and document tasks with AI-assisted GitHub issue creation, including smart suggestions aligned with your project's scope for better team collaboration.
3. **`/branch <issue-number>`** - Automatically generate and switch to semantically named branches linked to specific GitHub issues, ensuring organized development and easy progress tracking.
4. **`/fix-issue <issue-number>`** - Let Claude analyze GitHub issues and propose tailored code solutions that fit your project's architecture.
5. **`/commit`** - Create meaningful commits with AI-generated titles and detailed descriptions that capture change impacts, improving Git history usefullness.
6. **`/close-issue <issue-number>`** - Automatically close GitHub issues with contextual comments to the issue thread, additionally referencing the commit that fixed the issue.
7. **`/create-pr`** - Generate pull requests with insightful titles and descriptions highlighting changes, motivations, and benefits.

**Utility Commands:**
- **`/update-claude`** - Manually persist key session insights to SESSIONCONTEXT.md for long-term documentation, enabling easy recaps in future Claude instances. 

## Quick Setup

1. **Copy the ENTIRE contents of COPYME.md and paste it at the end of your CLAUDE.md file:**
> You can use the "Copy raw file" button native to GitHub to copy the entire file content.

👉 **[Open COPYME.md file](COPYME.md)**

2. **Create a copy of the SESSIONCONTEXT file linked below in your project's root directory.**

👉 **[SESSIONCONTEXT.md](SESSIONCONTEXT.md)**

3. **Add the SESSIONCONTEXT file to your .gitignore**

> You can run the following command in your terminal to add it to .gitignore, or ask claude to add it for you, or manually add it.

```bash
echo "SESSIONCONTEXT.md" >>  .gitignore || echo "SESSIONCONTEXT.md" > .gitignore
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
