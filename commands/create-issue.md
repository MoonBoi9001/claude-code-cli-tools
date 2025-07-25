### 2. Create Issue
Create GitHub issues with context-aware descriptions:

`/create-issue`

Claude will (all steps REQUIRED):
1. Propose an issue based on current session context
2. Present draft for approval/modification
3. Allow user to propose alternative issue
4. Format and enhance user proposals
5. Create issue via GitHub CLI upon approval
6. **🚨 MANDATORY: MUST update session context** `SESSION_CONTEXT.md` (runs `/update-session`) with issue details - DO NOT skip this step

**⚠️ CRITICAL REMINDER: Every /create-issue command MUST end with updating SESSION_CONTEXT.md - this is not optional!**

Example usage:
```
Human: /create-issue
Claude: [proposes issue or accepts user proposal, then creates it]
Issue #15 created successfully.

✅ MANDATORY STEP: Updating session context with issue details...
Session context updated with new issue information.
```
