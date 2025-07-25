### 7. Close Issue

Close a GitHub issue with automatic detection of the resolving commit:

`/close-issue <issue-number>`

Claude will (all steps REQUIRED):

1. Fetch issue details (title, description, keywords)
2. Analyze recent commit history to find the resolving commit by:
   - Matching commit titles/descriptions with issue keywords
   - Looking for issue number references (#4, Issue #4, etc.)
   - Analyzing code changes relevant to the issue topic
   - Preferring recent commits over older ones
3. Present the identified commit for confirmation
4. Post a comment to the issue with:
   - Resolution confirmation  
   - Specific commit SHA256 hash that fixed the issue
   - Brief summary of how the commit resolves the issue
5. Close the issue automatically
6. **🚨 MANDATORY: MUST update session context** `SESSION_CONTEXT.md` (runs `/update-session`) to reflect issue completion - DO NOT skip this step

**⚠️ CRITICAL REMINDER: Every /close-issue command MUST end with updating SESSION_CONTEXT.md - this is not optional!**

Example usage:

```text
Human: /close-issue 4
Claude: Analyzing commits to find resolution for issue #4...

Found resolving commit:
- abc789: "feat: Add user authentication system"

Posting resolution comment and closing issue...
Issue #4 closed successfully with commit abc789.

✅ MANDATORY STEP: Updating session context to reflect issue completion...
Session context updated with issue closure details.
```

Smart matching criteria:

- **Direct references**: Commit mentions issue number (#4, Issue #4, fixes #4)
- **Keyword matching**: Issue title words found in commit title/description
- **Topic correlation**: Code changes align with issue requirements
- **Recency weighting**: Prefer recent commits that likely contain the fix
