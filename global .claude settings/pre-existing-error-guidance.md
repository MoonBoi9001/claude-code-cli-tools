# Pre-existing Error Guidance

**Pre-existing issues are not invisible.** When you encounter warnings, lint errors, test failures, or other issues during your work, do not reflexively classify them as "pre-existing" and move on. "Pre-existing" describes when something was introduced, not whether it matters.

If you can fix it in a few minutes -- a lint warning, a dead import, a type hint, a shellcheck issue -- fix it. You're already in the code. If it's larger than that, flag it clearly rather than burying it in a reassuring "all pre-existing" dismissal. Never use "pre-existing" as a reason to ignore a problem; use it only as factual context when explaining what a change did and didn't introduce.
