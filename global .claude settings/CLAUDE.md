# Global Claude Configuration

## Coding Standards

@CODING-STANDARDS.md

## Rules

- Every fix should address both the immediate symptom and the underlying pattern that caused it — don't just patch the surface, make the system robust against the same class of issue recurring
- Never use emojis
- Markdown documents, where possiblem should read like a narrative, not a checklist
- The narrative flow (engaging) structure is typically best and usually suits our writing objectives better. We should make sure never to make unverified claims, or state facts that are disproportinate to the truth. We always focusing on sergical accuracy, not overblown hype.
- Keep ALL data/numbers (surgical accuracy)
  - Remove robotic formatting
  - Use transitional phrases between ideas
  - Write like explaining to a colleague, not filling a form
  - Keep technical detail, but in prose form
  - Prefer minimalist language e.g. instead of "carefully adapted" use adapted. Instead of "where Parquet files are organized" use "Parquet files were organised"
  - Avoid overusing the same word over and over.
  - Prefer scientific write up style
- If I ask you a question and you are not 100% sure, please let me know that you're not sure rather than stating something that could be wrong

## PR Body Guidance

- Always have a Motivation section at the top of the PR body, before the PR summary
  - The motivation section explains to a non technical audience, in laymans terms, why the PR exists, what it acomplishes, and sets the tone for an easy review this helps to give context to a reviewer that might not be familiar with the codebase
  - The motivation section doesnt overstate anything. It's humble, non technical, easily approachable. We never make unverified claims in the PR body, or anywhere else for that matter.
- Dont end a PR with a ## Test plan section. We dont need those in our PR body's.
