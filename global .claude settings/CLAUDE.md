# Global Claude Configuration

## Coding Standards

@CODING-STANDARDS.md

@pre-existing-error-guidance.md

## Rules

- Every fix should address both the immediate symptom and the underlying pattern that caused it — don't just patch the surface, make the system robust against the same class of issue recurring
- Never use emojis
- Markdown documents, where possible, should read like a narrative, not a checklist
- The narrative flow (engaging) structure is typically best and usually suits our writing objectives better. We should make sure never to make unverified claims, or state facts that are disproportionate to the truth. We always focus on surgical accuracy, not overblown hype.
- Keep ALL data/numbers (surgical accuracy)
  - Remove robotic formatting
  - Use transitional phrases between ideas
  - Write like explaining to a colleague, not filling a form
  - Keep technical detail, but in prose form
  - Prefer minimalist language e.g. instead of "carefully adapted" use adapted. Instead of "where Parquet files are organized" use "Parquet files were organised"
  - Avoid overusing the same word over and over.
  - Prefer scientific write up style
- If I ask you a question and you are not 100% sure, please let me know that you're not sure rather than stating something that could be wrong
- When working with git operations, always confirm the current working directory before running commands, especially after subshell operations or package installs
- When analyzing systems or services, be exhaustive — list ALL relevant components. Do not omit services unless explicitly told to scope down

## PR Body Guidance

- Always have a Motivation section at the top of the PR body, before the PR summary
  - The motivation section explains to a non technical audience, in layman's terms, why the PR exists, what it accomplishes, and sets the tone for an easy review this helps to give context to a reviewer that might not be familiar with the codebase
  - The motivation section doesnt overstate anything. It's humble, non technical, easily approachable. We never make unverified claims in the PR body, or anywhere else for that matter.
- Don't end a PR with a ## Test plan section. We don't need those in our PR bodies.

## Memories

- Do not write new memories without first asking the user.
