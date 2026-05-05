# Global Claude Configuration

## Coding Standards

@CODING-STANDARDS.md

@pre-existing-error-guidance.md

## Rules

- **Never merge or land a PR unless I have explicitly told you to in the current turn.** Never assume a PR is approved when I have not approved it. This applies to `gh pr merge`, the `/land-pr` skill, squash/rebase/merge commits, auto-merge flags, and any equivalent action. If you think a PR is ready, say so and wait — do not merge.
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

## Git Workflow

### Commit Messages

- Title: conventional commit format `type(scope): subject`, under 72 characters. Scope is required: exactly 1 word, no hyphens or slashes, specific enough to point at the right area, scope should not be ambiguous.
- Body: 1-4 lines max, wrap at 72 characters. State what the commit *does* and *why*, not a full essay. Save detailed context for the PR body. If the change can't be explained in 4 lines, split it into multiple commits.
- Build the body from context to action: open with the situation (what exists, what's broken or missing), then describe what the commit changes. Each sentence should set up the next, so a reader without prior context — think 3 a.m., unfamiliar repo — can follow without needing to look anything up.
- Trailers (e.g. `Co-Authored-By:`) live below a blank line after the body and don't count against the 4-line limit
- Never restate the title in the body

### Branch Strategy

- **Never push directly to main unless explicitly asked** - All changes must go through pull requests
- Branch names MUST use the `mb9/` prefix: `mb9/<laymens-description>`
  - Descriptions should be readable without codebase context — prefer slightly verbose plain English over terse developer shorthand (e.g. `add-login-authentication` not `add-auth`, `fix-dashboard-loading-crash` not `fix-null-pointer`)
  - e.g. `mb9/add-login-authentication`, `mb9/fix-dashboard-loading-crash`

### PR Titles

- Keep PR titles under 64 characters. Conventional commit format (`type: subject`) still applies. Do not use `type(scope): subject` for the PR title, as we only have 64 characters to work with.
- Readable without codebase context. A non-engineer (PM, designer, executive) skimming the PR list should be able to tell what the PR does without opening the diff. Avoid file paths, function names, internal acronyms, engineering specific lingo and library-specific jargon — describe the change in plain english terms, not the implementation details.

### PR Sizing

Prefer small, incremental PRs over large feature-complete ones. A PR that touches 5+ files or introduces a full feature in one shot is hard to review — split it into smaller logical changesets that each make sense on their own. Each PR should represent one coherent step: a new type, a migration, a single behaviour change. Reviewers can move faster through a stack of focused PRs than one sprawling diff.

When working with coding agents, this matters even more — agents can produce large changesets quickly, but the review bottleneck remains human. Structure the work so each PR is easily reviewable in a single sitting.

### PR Body

- The PR body should contain only three parts. TL;DR, Motivation and Summary.
  1. TL;DR explains the PR for someone that doesnt even have 30 seconds of time to review and approve.
  2. Motivation follows TL;DR section at the top of the PR body, before the summary
  3. Summary finalises the PR body.

#### TL;DR

The TL;DR is the one-glance answer to "what does this PR do, and is it safe to approve?" Written for a reader who has fewer than 30 seconds to look at this PR.

**Length**: 3 sentences max. If it doesn't fit, the PR is probably too broad and should be split.

**Tone**: same as the rest of the body. Readable by a non-engineer; no jargon, no file paths, no function names.

#### Motivation section

The motivation orients the reader before they look at any code. Write it for two audiences at once: yourself on a day you haven't touched this area, and a colleague landing on the PR cold — no prior context on the change, the surrounding code, or sibling PRs in a stacked series. Both should understand the point without reading the diff, related PRs, or external docs.

**Structure**: Open with what the system does today (the normal behaviour or current state), then introduce what's wrong or missing, then connect that to the impact. The reader should understand the "before" picture before seeing the "after."

**Stakes**: Make the cost of the status quo explicit. Who is hurt by the current state — users, operators, on-call, future maintainers? What breaks, gets missed, or gets harder if this PR doesn't land? A motivation that ends at "X causes Y" without answering "and so what?" leaves the reader unable to judge how much the PR matters. Stakes should be concrete (named systems, named consequences), not vague gestures like "this is bad for users."

**Tone**: Write at a level a non-engineer collaborator (PM, designer, a reviewer of your work who isn't deep in this codebase) could follow. Use the natural domain language of the project (contracts, escrow, receipts, signers) but avoid implementation internals (actor mailboxes, HashMap semantics, trait impls). If a term wouldn't come up in a conversation about what the system does — only in how the code works — it belongs in the summary or code comments, not the motivation. When a domain term is unavoidable but likely opaque to a non-technical reader, gloss it in one short clause the first time it appears. Don't overstate the impact or make unverified claims — if something "may" cause an issue, say "may."

**Specificity**: Name the actual components and services involved. "The network subgraph" not "a subgraph." Vague references force the reader to guess.

**Cause and effect**: When the PR addresses a problem, trace the chain of consequences as a connected narrative. Each step should follow from the previous one, building toward the impact. Don't list effects in parallel — connect them.

**Size**: No more than 5 sentences. No more than 2 paragraphs. If you cannot explain the motivation in less than 5 sentences across 2 paragraphs max, then the PR is too big and should be split into logical changesets.

#### Summary and Changes sections

The summary is a concise list of what the PR actually does. Keep it to bullet points — the narrative belongs in the motivation, not here. Each bullet point should contain a sentence with less than 100 characters.

## Memories

- Never write, overwrite, or delete any memory file without explicitly confirming with the user first via AskUserQuestion. This is imperative — no exceptions.
