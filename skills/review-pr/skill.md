---
name: review-pr
description: "Review a GitHub PR with a team of specialized agents covering architecture, correctness, security, tests, code quality, and integration. Use when the user asks to 'review a PR', 'review this PR', 'code review PR 1234', 'review PR #1234', 'what do you think of this PR', or pastes a GitHub PR URL and asks for feedback. Also trigger when the user says 'review' followed by a PR number."
argument-hint: "<PR number or URL>"
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Agent
  - Write
  - Edit
---

# Review PR

Review a GitHub PR using 6 specialized agents in parallel, then consolidate and verify findings before presenting to the user.

## Why this skill exists

Review agents are good at pattern-matching — finding code that looks like a potential bug, a missing null check, an unused parameter. What they're bad at is impact assessment: determining whether a pattern actually matters in context. A null dereference in a function with zero callers is dead code, not a vulnerability. Two systems that can theoretically race but are prevented from causing harm by a smart contract aren't a critical bug — they're a minor cleanup.

This skill compensates for that gap by requiring agents to prove impact, then verifying their claims before presenting findings to the user.

## Working directory

Run all commands from the repo root. Detect it via `git rev-parse --show-toplevel`.

## Input

The argument is a PR number (e.g., `1172`) or a GitHub PR URL. If a URL, extract the number. If no argument, ask the user which PR to review.

## Steps

### 1. Fetch PR metadata and diff

```bash
gh pr view <number> --json title,body,baseRefName,headRefName,additions,deletions,files,author
gh pr diff <number> > /tmp/pr-<number>.diff
gh pr diff <number> --name-only
```

Report to the user: PR title, base/head branches, size (additions/deletions), and file count. If the PR is very large (>5000 additions), warn the user it may take a while.

Check if this PR is part of a stack (base branch is not `main`/`master`/`develop`). If so:
- Note this for the agents — some patterns in the code may come from the base branch rather than this PR. The agents should focus on what this PR changes, not what the base branch already had.
- **Map the PR chain.** Use `gh pr list --head <headRefName>` and `gh pr list --base <headRefName>` to find downstream PRs that build on this one. For each PR number in the chain, fetch its head via `git fetch origin refs/pull/<n>/head:pr/<n>` — this works uniformly whether the PR head lives in the base repo or in a fork, because GitHub exposes `refs/pull/<n>/head` on the base repo for every PR. Record the chain (e.g., "#1172 -> #1174 -> #1175 -> #1181") for reference. This is critical because stacked PRs often introduce functions in one PR and wire them up in the next — a function with zero callers in the current PR may have callers in the next PR in the chain.

Infer domain context from the PR title, body, and file paths. Before launching agents, add a one-line domain summary to the shared context (e.g., "This is a blockchain indexing agent that manages on-chain allocations and payment collection" or "This is a REST API for user management"). This helps agents assess severity more accurately — knowing that "collect" means "call a smart contract" changes how you evaluate error handling.

### 2. Launch 6 review agents in parallel

Spawn all 6 in a single message. Each agent gets the same context block, plus its specific focus area.

**Shared context for every agent:**

```
You are reviewing PR #<number> on <owner>/<repo>: "<title>".
Size: <additions> additions, <deletions> deletions, <file_count> files.
Base: <baseRefName>, Head: <headRefName>.

The PR diff is at /tmp/pr-<number>.diff. The full repo is at <repo_path>.

Read the diff AND the source files it touches. Do not review based on the diff alone.
```

**Severity rules for every agent:**

```
Severity rules — these determine whether your review is useful or noise:

BEFORE reporting any finding:
1. Check callers. Search for who calls the function/method. If zero callers,
   it's dead code — report it as "dead code" under Minor, not as a bug.
   IMPORTANT: For stacked PRs, zero callers in the current checkout does NOT
   mean dead code. The caller may be in a downstream PR. Flag it as "no
   callers in this PR — may be wired up downstream" rather than "dead code."
2. Check runtime reachability. Trace the code path from an entry point (API
   handler, timer, reconciliation loop) to the flagged code. If you can't
   trace a path, the code may not execute.
3. Check external guards. If the finding involves on-chain calls, check whether
   the smart contract prevents the bad outcome (e.g., double-spend prevented
   by balance tracking). If an external system prevents harm, the finding is
   Minor at most.

SEVERITY DEFINITIONS:
- Critical: Data loss, fund loss, or security breach that CAN happen in
  production through a concrete sequence of events you can describe.
- Significant: Bug that causes incorrect behavior in a reachable code path,
  but doesn't lose data/funds. Or a security issue with a viable attack
  scenario.
- Moderate: A real bug or behavioral issue that requires unusual conditions
  to trigger, or whose blast radius is limited to diagnostics/logging/retries.
  Code quality observations (circular dependencies, commented-out code,
  partial feature flags) belong in Minor unless they cause runtime bugs.
- Minor: Code quality, dead code, style, unused plumbing, architectural
  observations, theoretical issues prevented by external systems.

For any finding ranked Significant or above, you MUST include:
- WHO calls this code (the entry point)
- WHAT input triggers the bug (the concrete scenario)
- WHAT happens as a result (the actual consequence)
If you can't fill in all three, downgrade the finding.
```

**The 6 agents and their focus areas:**

1. **Architecture & Design**: Focus on system-level structure, not line-level code style. Stay in your lane — don't flag dead exports, naming, or duplicate imports (that's Code Quality's job). Hunt for:
   - Two classes or loops doing the same conceptual operation (parallel systems). Do they share deduplication? Could they conflict?
   - Code that writes to model/table A but a different path reads model/table B for the same logical concept (data model inconsistency)
   - Bidirectional dependencies between classes (A creates B, B calls back into A)
   - Classes with too many responsibilities that should be split

2. **Correctness & Logic**: Focus on runtime behavior and data flow, not code style. Stay in your lane — don't flag naming or migration SQL (that's Code Quality's job). Hunt for:
   - `findOne` where multiple records can match (should be `findAll` or filtered more narrowly)
   - `Set` or `Map` used for deduplication on objects (reference equality fails for class instances)
   - Fields assigned conditionally in a constructor but accessed unconditionally in methods
   - Status/state transitions where an intermediate state is skipped or a terminal state isn't checked
   - Unreachable code paths (dead branches that look intentional but aren't)

3. **Security**: Focus on trust boundaries and error handling, not code style. Stay in your lane — don't flag dead code or naming (that's Code Quality's job). Hunt for:
   - Catch blocks that return a default value instead of propagating (`catch { return false }`, `catch { return [] }`) — these are fail-open patterns that silently convert errors into wrong answers
   - Handlers receiving external messages without validating the message is addressed to this node (identity/address validation)
   - External input used directly as database keys or identifiers without validation
   - Unbounded queries or loops driven by external input
   - Unencrypted transport for sensitive data

4. **Test Coverage**: What's tested, what's missing, mock quality, edge cases. Report gaps, not bugs — the other agents handle bugs. Focus on which code paths have NO test coverage at all, especially complex methods with multiple branches.

5. **Code Quality**: Focus on code hygiene and configuration correctness. Stay in your lane — don't flag architectural issues or runtime bugs (those belong to other agents). Check:
   - Database migrations: is `down()` valid SQL for the target database? (e.g., PostgreSQL doesn't support `ALTER TYPE ... DROP VALUE`)
   - CLI/config: is every config value read from argv actually registered as a CLI option?
   - Dead exports: are new exported functions actually imported anywhere?
   - Duplicate imports/exports
   - Variable shadowing, dead code blocks, commented-out code

6. **Integration & Compatibility**: Focus on how this PR interacts with existing code. Stay in your lane — don't flag internal code quality issues (that's Code Quality's job). Hunt for:
   - Return type changes on existing functions — callers may check for `undefined`/`null` that no longer occurs
   - Feature flags that gate some code paths but not all related code (partially gated features)
   - New dependencies between services that aren't reflected in startup ordering or health checks
   - Changes that affect APIs consumed by external systems

Each agent should keep its report under 400 words as a bullet list: issues first (with severity tag), then positives.

### 3. Consolidate findings

After all 6 agents complete, merge their findings into a single list. Deduplicate findings reported by multiple agents — note the count as a confidence signal, but don't treat it as an importance signal. A finding from 1 agent can be the most important finding in the review if it identifies a real-world bug. Consensus means "multiple angles see the same thing" (high confidence), not "this matters more than a single-agent finding."

### 4. Severity challenge (this is the most important step)

Go through every finding ranked Significant or above and personally verify it:

1. **Verify attribution** — if a finding claims something is "new," "introduced by," or "added in" this PR, check the diff. If the code predates this PR, correct the attribution. Observations about unchanged code are valid findings but must be labeled accurately — don't claim the PR introduced something it didn't.
2. **Read the actual code** at the file and line cited. IMPORTANT: Use `gh pr diff <n>` when you only need the change, or fetch the PR's head ref via `git fetch origin refs/pull/<n>/head:pr/<n>` and then `git show pr/<n>:path/to/file` when you need surrounding context. This works for same-repo and forked PRs. Never use bare branch names — local branches may have extra commits from the user or other contributors that aren't part of the PR. `origin/<branch>` refs only work when the PR head lives in the base repo; for forks, the branch isn't on `origin` and you'll get a confusing error or silently read the wrong tree.
3. **Search for callers** — `grep` for the function name. If zero callers in the current checkout, and this is a stacked PR, **fetch and search the downstream PR refs** identified in Step 1 (after `git fetch origin refs/pull/<n>/head:pr/<n>`, use `git show pr/<n>:<file> | grep <function>`). A function introduced in PR N with zero local callers but called in PR N+1 is not dead code — it's staged for the next PR. Downgrade to Minor ("dead code") only after confirming zero callers across the entire chain.
4. **Trace the entry point** — can you get from a timer, API handler, or user action to this code? If not, downgrade.
5. **Trace the consumer** — for "wrong data returned" findings (missing filter, wrong query, stale cache), don't stop at "this could return the wrong record." Check what the caller does with the result. Does the caller branch on it? Is the result used in a path that's actually reachable given normal control flow? A query that could match the wrong row but whose result is never used in the relevant code path is Minor at most.
6. **Check external guards** — for on-chain interactions, does the contract prevent the bad outcome? If yes, downgrade.
7. **Ask "so what?"** — if this bug fires in production, what actually happens? If the answer is "a log line" or "wasted gas" or "a retry", it's not Significant.

Be aggressive about downgrading. A finding that "sounds scary" but can't cause harm in practice is noise. Presenting noise erodes the user's trust in the review.

### 4b. Gap check

Agents tend to review what's visible in the diff and miss structural issues. After the severity challenge, run these targeted searches across the files touched by the PR. These are the patterns most commonly missed by review agents.

**Fail-open error handling** — search the changed files for catch blocks that swallow errors:
```bash
grep -n "catch.*{" <changed-files> | # then read surrounding lines
```
Look for catches that `return false`, `return []`, `return null`, `return undefined`, or `return 0` without logging. These turn errors into silent wrong answers. A function that returns `false` on error when `false` means "no match found" will cause callers to proceed as if the check passed.

**Unconditional class field access after conditional initialization** — if a constructor conditionally assigns fields (behind an `if` or config check), grep for those field names in methods to check if they're accessed without guards.

**Parallel implementations** — scan for pairs of methods/classes that do the same conceptual operation (collect, validate, sync, reconcile). Check: do they share state or deduplication? Could they race or produce conflicting results?

**Data model reads vs writes** — if the PR adds writes to a model/table, search for where that model is read. If a different model is read for the same concept, that's a gap. Conversely, if the PR reads from a model, check who writes to it.

**Identity/address validation** — for any handler that receives external messages containing an address, ID, or identity field, check if the code validates it matches the local node. Missing validation means a misdirected message burns resources before failing at a deeper layer.

**Inverse findings** — for each agent finding, ask: "what's the related thing nobody checked?" Examples:
- If an agent found "function X writes to model A" → check who READS from model A and whether they see the data
- If an agent found "proposals are never marked accepted" → check what depends on the accepted status downstream
- If an agent found "no validation on field X" → check what other fields in the same message are also unvalidated

This step catches the second-order consequences that agents miss because they only look at the code in isolation.

Add any findings from the gap check to the report with appropriate severity. These often surface real issues the agents missed.

### 5. Write the report

Save to `pr-reviews/pr-<number>-review.md` in the repo root.

Structure:

```markdown
# PR #<number> Review: <title>

**PR**: <url>
**Author**: <author>
**Branch**: <head> -> <base>
**Size**: <additions> additions, <deletions> deletions, <file_count> files
**Reviewed**: <date>

## Critical
(Only if there are genuinely critical findings after the severity challenge.)

## Significant
### <N>. <Title>
**In short**: <1-2 sentence non-technical summary of what's wrong and what to do about it. No function names or code — write it so someone skimming the review gets the point immediately.>
<Description with entry point, trigger, and consequence. When a finding involves multiple steps or behavior over time, include a short concrete example showing what happens rather than describing the problem abstractly. Use tables to show state (e.g., DB rows before/after, cache entries, queue items) — visual reporting is easier to follow than prose for stateful bugs.>
**Fix**: <Concrete recommendation — what to change, where, and why. If there are multiple options, list them with trade-offs.>
**Status**: [ ] Reviewed

## Moderate
### <N>. <Title>
**In short**: <1-2 sentence non-technical summary.>
<Description.>
**Fix**: <Concrete recommendation.>
**Status**: [ ] Reviewed

## Minor
...

## Test Gaps
<Bullet list of untested paths identified by the test coverage agent.>

## Positives
<Bullet list of things done well.>
```

Omit empty severity sections. Number findings sequentially across all sections.

### 6. Present to the user

Show a short summary: how many findings at each severity, the most notable ones, and the path to the full report. Do not dump the entire report into the conversation — the user can read the file.

## Constraints

- Requires `gh` CLI authenticated with access to the repo
- Requires the Agent tool for spawning review agents
- Always run from the repo the PR belongs to (for source file access)
- Do not leave the /tmp diff file around — clean up after writing the report
