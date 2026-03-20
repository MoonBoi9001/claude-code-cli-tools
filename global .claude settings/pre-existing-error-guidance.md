# Pre-existing Error Guidance

When a lint hook, test run, or build step reports errors, handle every error — not just the ones your edit introduced.

- **Fixable in ~2 minutes** (unused imports, sort order, dead variables, type hints, shellcheck issues): fix them immediately. You are already in the code.
- **Larger issues**: flag each one explicitly to the user with enough context to act on later. Do not group them under a blanket "pre-existing" dismissal.
- **Never say "pre-existing" and move on.** "Pre-existing" describes when something was introduced, not whether it matters. Use the word only as factual context when explaining what your change did and did not introduce — never as a reason to ignore a problem.
