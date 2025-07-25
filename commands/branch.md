### 3. Branch
Create and switch to a new branch based on a GitHub issue:

`/branch <issue-number>`

Claude will (all steps REQUIRED):
1. Fetch issue details from GitHub using the issue number
2. Determine branch type from issue labels or title (feat/fix/docs/chore)
3. Generate semantic branch name including issue number
4. Create and switch to the new branch
5. **🚨 MANDATORY: MUST update session context** `SESSION_CONTEXT.md` (runs `/update-session`) with information - DO NOT skip this step
6. Handle edge cases (uncommitted changes, existing branches, etc...)

**⚠️ CRITICAL REMINDER: Every /branch command MUST end with updating SESSION_CONTEXT.md - this is not optional!**

Example usage:
```
Human: /branch 10
Claude: Fetching issue #10: "Add user authentication system"
Creating branch: feat/issue-10-user-authentication
Switched to new branch 'feat/issue-10-user-authentication'
✅ MANDATORY STEP: Updated session context so a future instance of Claude knows we're working on issue 10
Ready to work on: Add user authentication system
```

Branch naming format: `{type}/issue-{number}-{sanitized-title}`
- **feat**: New features
- **fix**: Bug fixes  
- **docs**: Documentation changes
- **chore**: Maintenance tasks
