### (Available Flags: --draft, --update)

#### Flags:
**Available flags:**
- `--draft`: Create as draft PR
- `--update`: Perform a mandatory session context update

#### Description:
Intelligently create a pull request with a conventional commit title (max 50 chars), a context-aware description, and a context-aware merge strategy recommendation:

#### Use: 
`/create-pr [flags]`

#### Claude will:
1. **Analyze git diff, status, and commits:**
   - Review actual code changes, file scope, and commit structure
   - Determine semantic impact (patch/minor/major-like changes)
2. **Generate conventional commit title (max 50 chars):**
   - Create appropriate type prefix (feat/fix/docs/refactor/etc.)
   - Concise description of primary change
3. **Scale PR description based on semantic impact:**
   - **Simple** (patch-like): Bug fixes, documentation, small tweaks
     *Brief summary + motivation + key changes + impact*
   - **Medium** (minor-like): New features, API additions, refactoring, dependency upgrades, new configuration options
     *Detailed summary + thorough motivation + in-depth changes + broader impact*
   - **Complex** (major-like): Breaking changes, architecture shifts, new systems, database migrations
     *Full structured sections: executive summary, motivation & context, categorized changes, risks, reviewer notes*
4. Claude will also recommend an appropriate merge strategy in the chat, with a clear justification (this will not be posted in the PR description).
   - **Rebase and merge**: Clean sequential commits with individual value
   - **Create a merge commit**: Multiple domains or educational commit progression
   - **Squash and merge**: Single logical change or messy development history
5. **Update session:**
   - If `--update` specified: automatically run `/update-session`
