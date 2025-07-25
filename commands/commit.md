### 5. Commit
When you want Claude to automatically commit code changes with an appropriate message:

`/commit`

**Commit workflow:**
1. Run `git diff` to analyze changes
2. Automatically detect the commit type (feat/fix/docs/chore/refactor/test)
3. Generate a descriptive commit message based on the changes
4. **Automatically update session context** `SESSION_CONTEXT.md` (runs `/update-session`) with commit details
5. Include all changes in a single commit with:
   - Main changes described in the commit message
   - Session context updates included automatically
   - Claude Code attribution footer
6. Execute the commit

Example usage:
```
Human: /commit
Claude: [analyzes changes and creates commit]
Commit: abc1234 - feat: Add new feature

Updating session context with commit details...
Session context updated with implementation progress.
```

**Prerequisites**:
- Staged or unstaged changes to commit
- Git repository initialized
