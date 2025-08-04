### Update Session Context Document

#### Description:
Persist session context to `SESSION_CONTEXT.md`. The session context document is to be treated like a lossless external memory. Claude can use and refer to this document at any time.

#### Use:
`/update-session`

#### Claude will:
1. Think back about what has happened in the current session (commits, issues, PRs, technical discoveries, plans, etc.)
2. Remember key decisions, implementations, and discussion context.
3. Update the `SESSION_CONTEXT.md` document to persist all recalled memories for future Claude instances.
4. Use language that avoids unnecessary articles and prepositions while preserving full meaning, rather than truncating or removing important information.
5. Ensure there is no conflicting information in the document.
6. Ensure that `SESSION_CONTEXT.md` is never longer than 750 lines
