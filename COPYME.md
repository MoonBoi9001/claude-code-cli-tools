## Quick Commands

1. **`/recap`** - Get overview of current work state and context
2. **`/create-issue`** - Plan and document what needs to be done (automatically updates session context)
3. **`/branch <issue-number>`** - Create feature branch linked to issue
4. **`/fix-issue <issue-number>`** - Implement solution with issue context
5. **`/commit`** - Commit changes with smart messaging (automatically updates session context)
6. **`/create-pr`** - Create pull request (automatically updates session context)
7. **`/close-issue <issue-number>`** - Close issue with commit reference

**Utility Commands:**
8. **`/update-session`** - Manually update SESSIONCONTEXT.md. Note that `/update-session` is automatically run after `/create-issue`, `/commit` and `/create-pr`)

### 1. Recap
Quick load context into new claude session and get an overview of current work state and suggested next actions:

`/recap`

Claude will:
1. Review SESSIONCONTEXT.md
2. Show current branch and commit status
3. List recent commits and changes
4. Display open issues with priorities
5. Show uncommitted changes if any
6. Suggest logical next actions based on context
7. Provide session continuity information

Example usage:
```
Human: /recap
Claude: [displays current context summary and next action suggestions]
```

Example output:
```
## Current Context
- **Branch**: feature-branch (2 commits ahead of main)
- **Last commit**: feat: Add user authentication
- **Uncommitted changes**: None

## Recent Activity (Last 3 commits)
- abc123: feat: Add user authentication system
- def456: fix: Resolve login validation issue
- ghi789: docs: Update API documentation

## Open Issues (3 total)
**High Priority:**
- #10: Implement payment processing
- #11: Add user dashboard

## Suggested Next Actions
1. Continue work on issue #10 payment processing
2. Create branch for user dashboard feature
```

### 2. Create Issue
Create GitHub issues with context-aware descriptions:

`/create-issue`

Claude will:
1. Propose an issue based on current session context
2. Present draft for approval/modification
3. Allow user to propose alternative issue
4. Format and enhance user proposals
5. Create issue via GitHub CLI upon approval
6. **Automatically update session context** with issue details

Example usage:
```
Human: /create-issue
Claude: [proposes issue or accepts user proposal, then creates it]
Issue #15 created successfully.

Updating session context with issue details...
Session context updated with new issue information.
```

### 3. Branch
Create and switch to a new branch based on a GitHub issue:

`/branch <issue-number>`

Claude will:
1. Fetch issue details from GitHub using the issue number
2. Determine branch type from issue labels or title (feat/fix/docs/chore)
3. Generate semantic branch name including issue number
4. Create and switch to the new branch
5. Update session context with issue information
6. Handle edge cases (uncommitted changes, existing branches, etc...)

Example usage:
```
Human: /branch 10
Claude: Fetching issue #10: "Add user authentication system"
Creating branch: feat/issue-10-user-authentication
Switched to new branch 'feat/issue-10-user-authentication'
Ready to work on: Add user authentication system
```

Branch naming format: `{type}/issue-{number}-{sanitized-title}`
- **feat**: New features
- **fix**: Bug fixes  
- **docs**: Documentation changes
- **chore**: Maintenance tasks

### 4. Fix Issue
Analyze a GitHub issue and propose code solutions to address the requirements:

`/fix-issue <issue-number>`

Claude will:
1. Fetch issue details (title, description, requirements, labels)
2. Analyze the codebase to understand relevant files and architecture
3. Identify the specific changes needed to address the issue
4. Propose concrete code implementations with:
   - File modifications or new file creation
   - Implementation details and technical approach
   - Integration with existing codebase patterns
   - Testing considerations and validation steps
5. Present the proposed solution for review and approval
6. Optionally implement the changes if approved

Example usage:
```
Human: /fix-issue 10
Claude: Analyzing issue #10: "Add user authentication system"

Issue analysis:
- Type: New feature implementation
- Scope: Backend authentication with JWT tokens
- Requirements: Login, registration, password reset

Proposed solution:
1. Create authentication middleware
2. Add user model and database schema
3. Implement JWT token generation

Would you like me to implement these changes?
```

Analysis approach:
- **Issue classification**: Determine if it's a bug fix, feature, or improvement
- **Codebase impact**: Identify which files and modules need changes
- **Technical feasibility**: Assess complexity and implementation approach
- **Architecture alignment**: Ensure solution fits existing patterns
- **Testing strategy**: Propose validation and testing approaches

### 5. Commit
When you want Claude to automatically commit code changes with an appropriate message:

`/commit`

**Commit workflow:**
1. Run `git diff` to analyze changes
2. Automatically detect the commit type (feat/fix/docs/chore/refactor/test)
3. Generate a descriptive commit message based on the changes
4. **Automatically update session context** with commit details
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
5. **Automatically update session context** (runs `/update-session`)
6. **Commit session updates** to capture PR completion
7. Return the PR URL and session update confirmation

Example usage:
```
Human: /create-pr
Claude: Creating PR...
PR created: https://github.com/user/repo/pull/123

Updating session context...
Session context updated with PR completion and next steps.
Committed session updates.

Work complete! PR ready for review.
```

**Enhanced Workflow**: The `/create-pr` command provides complete closure by updating SESSIONCONTEXT.md with:
- PR creation details and URL
- Work completion status
- Suggested next steps or follow-up work
- Updated technical decisions and insights

Prerequisites:
- GitHub CLI (`gh`) installed and authenticated
- Feature branch (not main/master)

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
6. Update session context to reflect issue completion

Example usage:
```
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

### 8. Update Session
Persist session context to SESSIONCONTEXT.md for seamless session recovery:

`/update-session`

Claude will:
1. Review recent commits and changes in current session
2. Analyze PR descriptions and comments
3. Extract key decisions, implementations, and discoveries
4. Update the "Session Context" section in SESSIONCONTEXT.md
5. Include:
   - Current work summary
   - Technical decisions made
   - Issues discovered
   - Next steps identified
   - Important code changes

**Auto-Update Integration:**
- **Automatically runs after `/create-issue`** (captures issue details and planning)
- **Automatically runs after `/commit`** (captures implementation changes)
- **Automatically runs after `/create-pr`** (captures PR completion and next steps)

**Manual Use Cases:**
- **Before switching branches** or ending a session
- **After major discoveries** or architectural decisions
- **When context gets stale** or needs refreshing
- **Mid-development insights** that should be preserved

Example usage:
```
Human: /update-session
Claude: [updates SESSIONCONTEXT.md with current session context]
```
