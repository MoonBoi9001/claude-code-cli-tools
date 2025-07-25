### 8. Update Session

Persist session context to SESSION_CONTEXT.md for seamless session recovery:

`/update-session`

Claude will:

1. Review recent commits and changes in current session
2. Analyze PR descriptions and comments
3. Extract key decisions, implementations, and discoveries
4. Update the "Session Context" document `SESSION_CONTEXT.md`
5. Include:
   - Current work summary
   - Technical decisions made
   - Issues discovered
   - New learnings
   - Next steps identified
   - Important code changes
6. Intelligently lightly prune the SESSION_CONTEXT.md document if it gets longer than 400 lines
7. Strictly ensure that the SESSION_CONTEXT.md document is never longer than 500 lines

**Auto-Update Integration:**

- **Automatically runs after `/branch`** (captures that we're now working on solving a new issue)
- **Automatically runs after `/close-issue`** (captures an issue has been closed/addressed)
- **Automatically runs after `/commit`** (captures implementation changes)
- **Automatically runs after `/create-issue`** (captures issue details and planning)
- **Automatically runs after `/create-pr`** (captures PR completion and next steps)

**Manual Use Cases:**

- **Before switching branches** or ending a session
- **Before compacting the Claude chat history** or clearing the Claude chat history
- **After major discoveries** or architectural decisions
- **When context gets stale** or needs refreshing
- **Mid-development insights** that should be preserved

Example usage:

```text
Human: /update-session
Claude: [updates `SESSION_CONTEXT.md` with current session context]
```
