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
- Proactively ask the user questions (via the AskUserQuestion tool) — don't wait for a dead end to check in. If there's any ambiguity about approach, scope, or intent, ask rather than assume

## PR Body Guidance

- Always have a Motivation section at the top of the PR body, before the summary
- Don't end a PR with a ## Test plan section

### Motivation section

The motivation orients the reader before they look at any code. Write it as if explaining to yourself on a day you haven't touched this area — clear enough to anchor what the PR does and why, without needing to read the diff first.

**Structure**: Open with what the system does today (the normal behaviour or current state), then introduce what's wrong or missing, then connect that to the impact. The reader should understand the "before" picture before seeing the "after."

**Tone**: Use the natural domain language of the project (contracts, escrow, receipts, signers) but avoid implementation internals (actor mailboxes, HashMap semantics, trait impls). If a term wouldn't come up in a conversation about what the system does — only in how the code works — it belongs in the summary or code comments, not the motivation. Don't overstate the impact or make unverified claims — if something "may" cause an issue, say "may."

**Specificity**: Name the actual components and services involved. "The network subgraph" not "a subgraph." Vague references force the reader to guess.

**Cause and effect**: When the PR addresses a problem, trace the chain of consequences as a connected narrative. Each step should follow from the previous one, building toward the impact. Don't list effects in parallel — connect them.

### Summary and Changes sections

The summary is a concise list of what the PR actually does. Keep it to bullet points — the narrative belongs in the motivation, not here.

## Memories

- Do not write new memories without first asking the user.
