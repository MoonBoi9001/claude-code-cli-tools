### (Available Flags: --update)

#### Flags:
**Available flags:**
- `--update`: Perform a mandatory session context update

#### Description:
Create GitHub issues with context-aware descriptions:

#### Use:
`/create-issue [flags]`

#### Claude will:
1. Intelligently propose an issue based on recent discussion or session context
2. Present draft for approval/modification
3. Allow user to propose alternative issue
4. Format and enhance user proposals
5. Create issue via GitHub CLI upon user approval
6. If `--update` specified: automatically run `/update-session`
