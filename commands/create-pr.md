### 6. Create PR

Automatically create a pull request with generated title and comprehensive description, then update session context:

`/create-pr [flags]`

**Available flags:**

- `--no-update`: Skip the mandatory session context update (use with caution)

Claude will (all steps REQUIRED):

1. Analyze branch changes and commit history vs the base branch
2. Review all file changes to understand the full scope
3. Generate a semantic PR title following conventional commit format
4. Create PR via GitHub CLI with:
   - Executive summary
   - Motivation and context
   - Categorized change list with type prefixes (feat/fix/docs/etc)
   - Future improvement suggestions
   - Potential issue identification/Risk assessment
   - Notes for reviewers section
5. **Handle session context update**:
   - If `--no-update` flag is NOT present: **MANDATORY update** `SESSION_CONTEXT.md` (runs `/update-session`) with PR details
   - If `--no-update` flag IS present: Skip session update (inform user: "⚠️ Skipping session context update as requested")
6. **Commit session updates** to capture PR completion
7. Return the PR URL and session update confirmation

**⚠️ CRITICAL REMINDER: Every /create-pr command MUST end with updating SESSION_CONTEXT.md unless --no-update flag is used!**

Example usage:

```text
Human: /create-pr
Claude: Creating PR...
PR created: https://github.com/user/repo/pull/123

✅ MANDATORY STEP: Updating session context...
Session context updated with PR completion and next steps.
Committed session updates.

Work complete! PR ready for review.
```

```text
Human: /create-pr --no-update
Claude: Creating PR...
PR created: https://github.com/user/repo/pull/456

⚠️ Skipping session context update as requested

PR ready for review.
```

**Enhanced Workflow**: The `/create-pr` command provides complete closure by updating SESSION_CONTEXT.md with:

- PR creation details and URL
- Work completion status
- Suggested next steps or follow-up work
- Updated technical decisions and insights

Prerequisites:

- GitHub CLI (`gh`) installed and authenticated
- Feature branch (not main/master)
