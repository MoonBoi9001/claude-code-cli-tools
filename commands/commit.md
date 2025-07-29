### 5. Commit
When you want Claude to automatically commit code changes with an appropriate message:

`/commit [flags]`

**Available flags:**

- `--all` or `-a`: Automatically stage all changes before committing (runs `git add -A`)
- `--no-update`: Skip the mandatory session context update (use with caution)

**Examples:**

- `/commit` - Standard commit with manual staging
- `/commit --all` - Stage all changes and commit
- `/commit -a` - Same as --all (short form)
- `/commit --no-update` - Commit without updating session context
- `/commit --all --no-update` - Stage all changes and commit without updating session context

**Commit workflow (all steps REQUIRED):**

1. **Parse command flags** (if any provided):
   - Extract `--all`/`-a` flag for auto-staging
   - Extract `--no-update` flag to skip session update
   - Validate flag combinations
2. **🚨 MANDATORY SAFETY CHECKS**:
   a. Check current branch with `git branch --show-current`
      - **IMMEDIATELY REFUSE** if on `main` branch - commits to main are NEVER allowed
      - Display error: "❌ ERROR: Cannot commit to main branch. Please create a feature branch first."
      - Stop execution completely - do not proceed with any other steps
   b. Check if branch has merged PRs with `gh pr list --state merged --head <branch-name>`
      - If merged PR exists, automatically create a new branch:
        - Analyze the uncommitted changes to determine the new work's purpose
        - Generate semantic name based on the NEW changes, not the old branch
        - Examples: 
          - If adding API endpoints: `feat/user-profile-endpoints`
          - If fixing authentication: `fix/jwt-token-expiry`
          - If refactoring database queries: `refactor/optimize-user-queries`
        - Run `git checkout -b <new-branch-name>`
        - Inform user: "🔄 Previous PR merged. Created new branch: `<new-branch-name>` based on current changes"
3. **Handle --all/-a flag** (if provided):
   - Run `git add -A` to stage all changes
   - Inform user: "📦 Staging all changes..."
4. **Verify changes exist**:
   - Run `git diff --cached` to check for staged changes
   - If no staged changes, check `git status --porcelain` for any changes
   - If no changes at all: Display "❌ No changes to commit" and exit
5. Analyze staged changes with `git diff --cached`
6. Perform comprehensive change analysis:
   - **Identify primary purpose**: What is the main goal of these changes?
   - **Detect new capabilities**: Look for added functions, methods, options, or features
   - **Recognize patterns**:
     - New lines starting with numbers often indicate new steps/features in documentation
     - Added conditionals/validations often indicate new constraints or safeguards
     - New parameters/options suggest enhanced functionality
   - **Weigh significance**: Features > fixes > improvements > refactors > docs > style
7. Automatically detect the commit type (feat/fix/docs/chore/refactor/test):
   - feat: New functionality or capabilities added
   - fix: Bug fixes or corrections
   - docs: ONLY if changes are purely documentation with no functional impact
   - refactor: Code restructuring without changing functionality
   - test: Adding or modifying tests
   - chore: Maintenance tasks, dependency updates
8. Generate a descriptive commit message that:
   - **Title**: Max 50 characters (imperative mood: "Add", not "Added")
   - Highlights the most impactful change
   - Explains what was added/changed and why (when apparent)
   - Keeps secondary changes in the body, not the title
9. Execute the git commit
10. **Handle session context update**:
   - If `--no-update` flag is NOT present: **MANDATORY update** `SESSION_CONTEXT.md` (runs `/update-session`) with commit details
   - If `--no-update` flag IS present: Skip session update (inform user: "⚠️ Skipping session context update as requested")

**⚠️ CRITICAL REMINDER: Every /commit command MUST end with updating SESSION_CONTEXT.md unless --no-update flag is used!**

Example usage:

```text
Human: /commit
Claude: [analyzes changes and creates commit]
Commit: abc1234 - feat: Add new feature

✅ MANDATORY STEP: Updating session context with commit details...
Session context updated with implementation progress.
```

```text
Human: /commit --all
Claude: 📦 Staging all changes...
[analyzes and commits all changes]
Commit: def5678 - fix: Resolve parsing issue in config loader

✅ MANDATORY STEP: Updating session context with commit details...
Session context updated with implementation progress.
```

```text
Human: /commit --no-update
Claude: [analyzes changes and creates commit]
Commit: ghi9012 - docs: Update API documentation

⚠️ Skipping session context update as requested
```

**Prerequisites**:

- Staged or unstaged changes to commit
- Git repository initialized
- GitHub CLI (`gh`) installed for PR merge detection
