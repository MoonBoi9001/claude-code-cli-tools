### 7. Close Issue

Close a GitHub issue with automatic detection of the resolving commit:

`/close-issue <issue-number>`

Claude will:

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
6. Update session context `SESSION_CONTEXT.md` (runs `/update-session`) to reflect issue completion

Example usage:

```text
Human: /close-issue 4
Claude: Analyzing commits to find resolution for issue #4...

Found resolving commit:
- abc789: "feat: Add user authentication system"

Posting resolution comment and closing issue...
Issue #4 closed successfully with commit abc789.
```

Smart matching criteria:

- **Direct references**: Commit mentions issue number (#4, Issue #4, fixes #4)
- **Keyword matching**: Issue title words found in commit title/description
- **Topic correlation**: Code changes align with issue requirements
- **Recency weighting**: Prefer recent commits that likely contain the fix
