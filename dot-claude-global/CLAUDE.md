# Global Claude Configuration

## Coding Standards

@CODING-STANDARDS.md

@pre-existing-error-guidance.md

## Rules

- Every fix should address the immediate symptom and the underlying pattern — make the system robust against the same class of issue recurring
- Never use emojis
- Markdown documents, where possible, should read like a narrative, not a checklist
- Never make unverified claims or state facts disproportionate to the truth. Surgical accuracy, not overblown hype.
- Keep ALL data and numbers intact when rewriting or summarising.
- Write like explaining to a colleague: use transitional phrases, keep technical detail in prose form, prefer minimalist language (e.g. "adapted" not "carefully adapted"). Avoid robotic formatting and repetitive word choices.
- If I ask you a question and you are not 100% sure, please let me know that you're not sure rather than stating something that could be wrong
- When working with git operations, always confirm the current working directory before running commands, especially after subshell operations or package installs
- When analyzing systems or services, be exhaustive — list ALL relevant components. Do not omit services unless explicitly told to scope down
- Default to asking over assuming. Aggressively use AskUserQuestion early and often — before choosing an approach, before scoping work, before making judgment calls. For features or significant changes, propose various approaches with trade-offs and ask which I prefer. Do not start coding until we've agreed on direction.

## Implementation Approach
- Before claiming work is complete, run the relevant tests/build/lint commands and show the output. No "should pass" or "looks correct" -- evidence before assertions.
- When debugging, find the root cause before proposing fixes. Read the error, trace the data flow, check recent changes. Do not guess-and-check.

## PR Body Guidance

- Always have a Motivation section at the top of the PR body, before the summary
- Don't end a PR with a ## Test plan section

### Motivation section

The motivation orients the reader before they look at any code. Write it for two audiences at once: yourself on a day you haven't touched this area, and a colleague landing on the PR cold — no prior context on the change, the surrounding code, or sibling PRs in a stacked series. Both should understand the point without reading the diff, related PRs, or external docs.

**Structure**: Open with what the system does today (the normal behaviour or current state), then introduce what's wrong or missing, then connect that to the impact. The reader should understand the "before" picture before seeing the "after."

**Stakes**: Make the cost of the status quo explicit. Who is hurt by the current state — users, operators, on-call, future maintainers? What breaks, gets missed, or gets harder if this PR doesn't land? A motivation that ends at "X causes Y" without answering "and so what?" leaves the reader unable to judge how much the PR matters. Stakes should be concrete (named systems, named consequences), not vague gestures like "this is bad for users."

**Tone**: Write at a level a non-engineer collaborator (PM, designer, a reviewer of your work who isn't deep in this codebase) could follow. Use the natural domain language of the project (contracts, escrow, receipts, signers) but avoid implementation internals (actor mailboxes, HashMap semantics, trait impls). If a term wouldn't come up in a conversation about what the system does — only in how the code works — it belongs in the summary or code comments, not the motivation. When a domain term is unavoidable but likely opaque to a non-technical reader, gloss it in one short clause the first time it appears. Don't overstate the impact or make unverified claims — if something "may" cause an issue, say "may."

**Specificity**: Name the actual components and services involved. "The network subgraph" not "a subgraph." Vague references force the reader to guess.

**Cause and effect**: When the PR addresses a problem, trace the chain of consequences as a connected narrative. Each step should follow from the previous one, building toward the impact. Don't list effects in parallel — connect them.

### Summary and Changes sections

The summary is a concise list of what the PR actually does. Keep it to bullet points — the narrative belongs in the motivation, not here.

## Memories

- Never write, overwrite, or delete any memory file without explicitly confirming with the user first via AskUserQuestion. This is imperative — no exceptions.
