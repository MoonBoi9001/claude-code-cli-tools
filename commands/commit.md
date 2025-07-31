### 5. Commit
When you want Claude to automatically commit code changes with an appropriate message:

`/commit [flags]`

**Available flags:**

- `--all` or `-a`: Automatically stage all changes before committing (runs `git add -A`)
- `--no-update`: Skip the mandatory session context update (use with caution)

**Examples:**

- `/commit` - Standard commit with manual staging
- `/commit --all` - Stage all changes and commit
- `/commit --no-update` - Commit without updating session context

**Commit workflow (all steps REQUIRED):**

1. **Parse flags**: Extract `--all`/`-a` and `--no-update` flags
2. **🚨 SAFETY CHECKS**:
   - **REFUSE** if on `main` branch - display error and stop
   - If branch has merged PRs: auto-create new branch with semantic name based on current changes
3. **Handle --all/-a flag** (if provided):
   - Run `git add -A` to stage all changes
   - Inform user: "📦 Staging all changes..."
4. **Verify changes exist**:
   - Run `git diff --cached` to check for staged changes
   - If no staged changes, check `git status --porcelain` for any changes
   - If no changes at all: Display "❌ No changes to commit" and exit
5. **Analyze changes and detect commit splitting needs**:
   - Group files by logical domains: functional code, docs, config, tests, tooling, dependencies
   - **If changes span 2+ unrelated domains**: Suggest splitting commits and ask user for confirmation
   - If approved: Create separate commits for each domain using selective `git add`
   - If declined: Continue with single commit but warn about mixed concerns
   - Identify primary purpose and detect new capabilities
6. **Generate commit**: Auto-detect type (feat/fix/docs/chore/refactor/test), create descriptive message (max 50 chars, imperative mood)
7. **Execute commit and update session context** (unless `--no-update` flag used)

**Example:**

```text
Human: /commit --all
Claude: 📦 Staging all changes...
[analyzes and commits all changes]
Commit: abc1234 - feat: Add new feature

✅ Updating session context with commit details...
```

**Prerequisites**:

- Staged or unstaged changes to commit
- Git repository initialized
- GitHub CLI (`gh`) installed for PR merge detection
