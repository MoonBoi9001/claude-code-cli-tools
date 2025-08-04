### (Available Flags: --no-auto-stage, --update)

#### Flags:
**Available flags:**
- `--no-auto-stage`: Do not automatically stage all changes before committing
- `--update`: Perform a mandatory session context update

#### Description:
Intelligently commit with conventional commit titles/descriptions and domain-aware commit splitting:

#### Use: 
`/commit [flags]`

#### Claude will:
1. **Parse and validate flags:**
   - Extract flags from command
2. **Safety checks:**
   - Check if on `main`/`master` branch
   - Check for merged PRs on current branch using `gh pr list --state merged --head <branch>`
3. **Handle staging based on flags:**
   - Automatically run `git add -A` unless `--no-auto-stage` flag provided
   - Use `git status --porcelain` to verify staging state
4. **Verify committable changes exist and perform a full code review:**
   - Intelligently run either `git diff` or `git diff --cached` to check for staged changes
     - Do not use the  `--stat` flag when running `git diff`
   - If no staged changes: use `git status` to check for unstaged changes
5. **Change branch away from `main`/`master` if relevant:**
   - If on `main`/`master` or a merged PR is found, prepare to create and switch to a new semantic branch with a name based on a `git diff` analysis
6. **Analyze changes and detect commit splitting opportunities:**
   - Categorize changed files by logical domains:
     - **Functional code**: Core business logic, features, bug fixes
     - **Documentation**: README, docs, comments, API documentation
     - **Configuration**: Package files, CI/CD, environment config
     - **Tests**: Unit tests, integration tests, test utilities
     - **Tooling**: Scripts, development tools, linting config
     - **Dependencies**: Package updates, version bumps
   - **Domain conflict detection**: If changes span 2+ unrelated domains:
     - Present domain breakdown to user with file counts
     - Suggest splitting into separate commits for better history
     - Automatically split with selective `git add` per domain
   - Identify primary change purpose and scope
7. **Generate conventional commit message:**
   - Auto-detect commit type: `feat`/`fix`/`docs`/`chore`/`refactor`/`test`/`build`/`ci`
   - Create concise, descriptive message (max 50 characters, imperative mood)
   - Include scope when applicable: `feat(auth): add user login`
   - Ensure message accurately reflects primary change purpose
8. **Execute commit and maintain session context:**
   - Perform `git commit` with generated message
   - Display commit hash and message confirmation
   - Handle commit failures gracefully with actionable error messages
9.  **Update session:**
   - If the `--update` flag is given, automatically run the `/update-session` command.
