### (Required Flags: --<issue-number>. Available Flags: --update)

#### Flags:
**Required flags:**
- `--<issue-number>`: The GitHub issue we want to close
**Available flags:**
- `--update`: Perform a mandatory session context update

#### Description:
Inteligently close a GitHub issue with automatic detection of the resolving commit or PR:

#### Use:
`/close-issue [flags]`

#### Claude will:
1. Fetch the issue details (title, description, keywords)
2. Analyze recent commit/PR history to find the resolving commit/PR by:
   - Matching commit/PR titles and descriptions with issue details
   - Looking for issue number references (#4, Issue #4, etc.)
   - Analyzing code changes relevant to the issue topic
   - Preferring recent commits/PR's over older ones
3. Post a comment in the github issue thread with:
   - Resolution confirmation
   - Specific commit SHA256 hash or PR # that fixed the issue
   - Brief summary of how the commit/PR resolved the issue
4. Close the issue automatically
5. **Update session:**
   - If `--update` specified: automatically run `/update-session`
