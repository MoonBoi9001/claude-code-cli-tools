### 6. Create PR

Automatically create a pull request with generated title and comprehensive description, then update session context:

`/create-pr`

Claude will:

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
5. **Automatically update session context** `SESSION_CONTEXT.md` (runs `/update-session`)
6. **Commit session updates** to capture PR completion
7. Return the PR URL and session update confirmation

Example usage:

```text
Human: /create-pr
Claude: Creating PR...
PR created: https://github.com/user/repo/pull/123

Updating session context...
Session context updated with PR completion and next steps.
Committed session updates.

Work complete! PR ready for review.
```

**Enhanced Workflow**: The `/create-pr` command provides complete closure by updating SESSION_CONTEXT.md with:

- PR creation details and URL
- Work completion status
- Suggested next steps or follow-up work
- Updated technical decisions and insights

Prerequisites:

- GitHub CLI (`gh`) installed and authenticated
- Feature branch (not main/master)
