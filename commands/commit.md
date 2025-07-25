### 5. Commit
When you want Claude to automatically commit code changes with an appropriate message:

`/commit`

**Commit workflow:**
1. Run `git diff` to analyze changes
2. Perform comprehensive change analysis:
   - **Identify primary purpose**: What is the main goal of these changes?
   - **Detect new capabilities**: Look for added functions, methods, options, or features
   - **Recognize patterns**:
     - New lines starting with numbers often indicate new steps/features in documentation
     - Added conditionals/validations often indicate new constraints or safeguards
     - New parameters/options suggest enhanced functionality
   - **Weigh significance**: Features > fixes > improvements > refactors > docs > style
3. Automatically detect the commit type (feat/fix/docs/chore/refactor/test):
   - feat: New functionality or capabilities added
   - fix: Bug fixes or corrections
   - docs: ONLY if changes are purely documentation with no functional impact
   - refactor: Code restructuring without changing functionality
   - test: Adding or modifying tests
   - chore: Maintenance tasks, dependency updates
4. Generate a descriptive commit message that:
   - **Title**: Max 50 characters (imperative mood: "Add", not "Added")
   - Highlights the most impactful change
   - Explains what was added/changed and why (when apparent)
   - Keeps secondary changes in the body, not the title
5. **Automatically update session context** `SESSION_CONTEXT.md` (runs `/update-session`) with commit details
6. Include all changes in a single commit with:
   - Main changes described in the commit message
   - Session context updates included automatically
   - Claude Code attribution footer
7. Execute the commit

Example usage:

```text
Human: /commit
Claude: [analyzes changes and creates commit]
Commit: abc1234 - feat: Add new feature

Updating session context with commit details...
Session context updated with implementation progress.
```

**Prerequisites**:

- Staged or unstaged changes to commit
- Git repository initialized
