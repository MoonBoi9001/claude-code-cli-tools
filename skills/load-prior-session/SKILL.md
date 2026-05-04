---
name: load-prior-session
description: Load a high-fidelity recap of a prior Claude Code session into the current session's context. The goal is to be LESS lossy than running /compact would be — the user is invoking this skill precisely because /compact discards detail they need. Use this when the user wants to "resume", "pick up", "continue", or "load context from" a previous session — especially a long one (hundreds of thousands of tokens) where actually resuming the session would be prohibitively expensive, or where the session was auto-compacted mid-flow and a lot of detailed work happened after the last compaction that another /compact pass would crush. Also trigger on phrases like "recap the last session", "what was I working on yesterday", "load the prior chat", or "/load-prior-session". The skill extracts via a subagent so the full transcript never enters the current session's context.
---

# Load Prior Session

## What this does

Claude Code's built-in `/compact` summarises the *current* conversation in place. This skill does the same job for a *prior* session — but with higher fidelity than running `/compact` again would give. The user is invoking it precisely because `/compact`'s output is too lossy for what they need. The trick: extract via a subagent so the raw transcript (which can be 80MB+) never enters the main session's context.

## How sessions are stored

Claude Code persists every session as a JSONL file at `~/.claude/projects/<encoded-cwd>/<session-uuid>.jsonl`, where `<encoded-cwd>` is the working directory with `/` replaced by `-`.

Each line is one record. The `type` field discriminates: `user`, `assistant`, plus metadata types (`system`, `attachment`, `custom-title`, etc.). User and assistant entries carry `timestamp`, `sessionId`, `parentUuid`, `uuid`, `cwd`, `gitBranch`, `isSidechain`, `isMeta`. `isSidechain: true` marks subagent traffic — exclude it from the main thread.

The **compaction summary** record is the key one: a `user` record with `isCompactSummary: true` whose `message.content` starts with `"This session is being continued from a previous conversation that ran out of context."`. It's `/compact`'s own output — a 9-section structured snapshot. They appear inline in the same JSONL each time `/compact` runs (manually or auto). Each `/compact` re-summarises everything before it, so the **latest** compaction summary already supersedes all earlier ones — earlier ones are not useful to read directly. The strategy below uses the latest one as a historical anchor and applies high-fidelity extraction to everything that came after it.

Older sessions encrypted with `.jsonl.age` need a passphrase the skill doesn't have — skip them.

## Workflow

### Step 1 — pick the session

If the invocation includes a session UUID, prefix, or absolute `.jsonl` path, use it directly. Otherwise list the 10 most recent `.jsonl` files (mtime descending) under `$HOME/.claude/projects/$(pwd | sed 's|/|-|g')/`, with UUID, mtime, size, line count, and a snippet of the first user message — and `AskUserQuestion` to pick. The active session is in the list; trust the user not to pick it.

### Step 2 — parse the focus argument

If the user supplied text after the slash command (e.g. `/load-prior-session focus on the DIPs work`), capture it as a focus hint and pass to the subagent. Otherwise produce a balanced recap.

### Step 3 — spawn the summariser subagent

Spawn a `general-purpose` subagent with the brief below. **Do not read the JSONL inline** — that puts the full transcript into this session's context, defeating the entire point.

```text
You are summarising a Claude Code session JSONL for handoff into a fresh session.

File: <absolute path to .jsonl>
Focus area (optional): <focus arg, or "balanced">

Goal: produce a recap with HIGHER FIDELITY than another /compact pass would give. The user is invoking this precisely because /compact discards detail they need — so be generous with detail in the post-compact range. Do not re-summarise material that's already a summary.

EXTRACTION STRATEGY — the file may be 50MB+, naively reading it will burn your context for no benefit. Phases below are numbered Phase 1-8 to avoid collision with the outer skill's Step 1-4.

Phase 0 (hygiene) — clear stale artifacts so this run's outputs don't blend with a previous invocation:
    rm -f /tmp/recap-*.jsonl /tmp/recap-*.txt

Phase 1 — Skeleton:
    wc -l <file>
    jq 'select(.isCompactSummary == true)' <file> | wc -l

Phase 2 — If compaction summaries exist (count > 0):
    a. Find the line of the LAST compaction record:
         LAST=$(awk '/"isCompactSummary":true/ {n=NR} END {print n}' <file>)
    b. Read THAT record in full — this is your historical anchor (= /compact's view of everything before). Use it verbatim in the recap; don't re-summarise. **Verbatim means EVERY section, EVERY word.** Do NOT abbreviate, do NOT replace any section with `[list of N items — see transcript]`, do NOT condense long sections like "All user messages" into bullets. If the anchor is 15k characters, the verbatim quote in your recap is 15k characters. Length is not a problem; eliding the anchor is — section 6 ("All user messages") is the densest user-intent signal in the file and abbreviating it defeats the entire point of preserving the anchor.
    c. Slice everything after it:
         tail -n +$((LAST + 1)) <file> > /tmp/recap-post-compact.jsonl
    d. Apply Phases 3-6 below to /tmp/recap-post-compact.jsonl, NOT the original file.
    e. Ignore earlier compaction summaries — they're superseded by the latest one.

If no compaction summaries (count == 0): apply Phases 3-6 directly to the original file.

Phase 3 — Pull every user message verbatim. Cheap, dense, intent-carrying. Filter to string content to drop tool_result echoes, and skip operational noise types:
    jq -c 'select(.type=="user" and .isSidechain==false and (.isMeta // false)==false and (.isCompactSummary // false)==false and (.message.content | type) == "string") | {ts: .timestamp, content: .message.content}' <working-file> > /tmp/recap-users.jsonl

Noise types to skip wholesale (don't carry signal): `progress`, `queue-operation`, `api_error`, `turn_duration`, `stop_hook_summary`, `file-history-snapshot`, `permission-mode`, `last-prompt`, `pr-link`, `agent-name`, `custom-title`. `attachment` is usually noise but can occasionally be load-bearing user input (pasted Slack threads, error logs the user dropped in) — skip by default but inspect if the user explicitly references one. Strip `<task-notification>` and `<system-reminder>` blocks from any user-message text you do extract — these are harness chatter, not user intent.

Phase 4 — Pull all assistant text blocks (skip tool_use):
    jq -c 'select(.type=="assistant" and .isSidechain==false) | {ts: .timestamp, text: ([.message.content[]? | select(.type=="text") | .text] | join("\n"))} | select(.text != "")' <working-file> > /tmp/recap-assistant.jsonl

Phase 5 — Pull tool calls (names + inputs only, no results). For very large ranges, grep down to git/docker/cargo/build/test:
    jq -c 'select(.type=="assistant" and .isSidechain==false) | .message.content[]? | select(.type=="tool_use") | {name, input}' <working-file> > /tmp/recap-tools.jsonl

Phase 6 — Read the last ~30 records of <working-file> in full. This gives you the "I was about to..." state AND the session-end-reason: clean exit (assistant text was the last meaningful record), interrupted (an unresolved tool_use with no following tool_result), error cascade (multiple recent api_error records), or abandoned (user message with no following assistant response). Note the end reason in the recap so the new session knows whether to retry, resume, or proceed fresh.

Phase 7 — Sample tool results only on demand, when a specific gap requires it. Do NOT bulk-read tool results.

Phase 8 — Capture current workspace state. The recap describes what the prior session believed was true; the live repo may have moved. Run from the session's `cwd` (or the user's current cwd if matching):

    git -C <cwd> rev-parse --abbrev-ref HEAD
    git -C <cwd> status --short
    git -C <cwd> log --oneline -10
    git -C <cwd> stash list

Include the output as a "Current workspace state (at recap time)" section in the recap. The new session uses this to spot-check the recap before acting — e.g. if the recap says "5 commits unpushed on branch X" but `git log` shows they were pushed since, the new session knows to trust git over the recap.

Budget: the skill's purpose is fidelity, not minimum cost. Don't sacrifice detail in the post-compact range to hit a tight number. But do keep raw transcripts out of context — work through jq filters to /tmp files, not wholesale Reads. Realistic cost for a heavily-loaded post-compact range: 200-300k tokens of subagent context. That's correct; the user is paying for fidelity.

THREAD ASSIGNMENT (do this BEFORE writing any of the recap) — read /tmp/recap-users.jsonl in chronological order and decide on thread boundaries. Signals that mark a boundary:
- A timestamp gap of >30 minutes between consecutive user messages (strong signal of context shift).
- An "actually let's...", "next thing...", "switching to...", "instead of that..." preamble.
- A change in primary repo or file focus (cross-check against /tmp/recap-tools.jsonl tool inputs).
- A distinct command family (debugging vs editing vs deploy vs config).
Write down the thread→message-index ranges as your plan before composing the recap. A long session typically has 2-5 threads.

OUTPUT — structure the recap by workstream, not by topic taxonomy. The new session does not yet know which thread the user wants to continue, so the recap must NOT collapse them into one narrative — that's exactly what /compact does and why it's lossy. For EACH thread, produce a section containing:

  1. **Short name** for the thread.
  2. **Every user message in this thread, verbatim, chronological.** Yes, every one — "yes", "sure", "okay", "nice" are approval signals; do NOT editorialise that they're "routine" and drop them. The test is "did the user type this?", not "do I think it's important?". Pull these from /tmp/recap-users.jsonl filtered to this thread's time range.
  3. **What was done in this thread.** Pull from /tmp/recap-assistant.jsonl (key reasoning excerpts) and /tmp/recap-tools.jsonl (tool calls). Embed bash commands and Edit/Write file paths verbatim — describing what code does in prose is the laziness pattern; quote the code instead.
  4. **Errors + fixes** as an enumerated list (not narrative prose). Each entry: what went wrong, what the fix was, who caught it.
  5. **State left in** — exact end-of-thread state.

Then close with:
  - **"Session ended on thread X, in state Y"** pointer (single line).
  - **"Current workspace state"** section containing the Phase 8 git output verbatim, plus a one-sentence reconciliation note ("the X commits the recap claims unpushed are present locally as Y, Z, W — confirms the recap").
  - When Phase 2 produced an anchor, a **"Pre-compaction history (verbatim /compact output)"** section at the end containing the anchor verbatim — every section, every word.

Do not editorialise about which thread was "the main one" — the user picks. If a focus arg was given, give that thread extra depth. Aim for dense and useful; the reader is a fresh Claude session that needs to be productive on whichever thread the user names next.

ANTI-LAZINESS, RESTATED: deterministic preservation beats model judgment on raw signal. /compact's section 6 dumps every user message regardless of importance — that's its strongest wins-on-volume feature. Our skill must do the same per thread, plus include code snippets verbatim when a load-bearing code change is described, plus include error→fix pairs as enumerated items rather than narrative prose. If you find yourself thinking "this user message is routine, I'll skip it" or "I'll just describe what the code does instead of quoting it" — stop. That's the laziness pattern. Quote it.
```

### Step 4 — confirm and stop

Give the user a one-line confirmation: "Loaded recap of session `<uuid>`. Ready to pick up." Do not start working on anything from the recap automatically — wait for direction.

## Why this shape

- **The whole point is to be LESS lossy than `/compact`.** The user wouldn't be invoking this skill if `/compact` were good enough — they'd just have run `/compact` themselves. Every design choice flows from that.
- **Subagent over inline read.** Transcripts can be 80MB+; an inline read defeats the cost goal. Subagent context is independent and discarded on return.
- **Latest compaction summary as anchor, not deliverable.** Each `/compact` re-summarises everything before it, so the latest supersedes all earlier ones. Use it verbatim — no point re-summarising what was already summarised.
- **Post-compaction range gets the high-fidelity extraction.** This is the heart of the skill. On a long session, 90%+ of the tokens typically live after the most recent compaction, and that's the material `/compact` would compress away. We pull every user message verbatim, all assistant text, and all tool calls — fidelity comes from preserving this material, not from rewriting it.
- **Final segment in full.** The last ~30 records capture the exact "I was about to..." state and the session-end-reason (clean / interrupted / error / abandoned) — the new session needs this to pick up cleanly.
- **By-workstream structure, not single-narrative.** A long session often contains multiple distinct threads. The new session doesn't know which one the user wants to continue, so collapsing them loses the choice. Present each thread separately so the user can name which to resume.

**Caveat:** the anchor summary is itself lossy. If a commit SHA, file path, or measurement from before the last compaction is load-bearing for a downstream decision, flag it in the recap so the user knows to verify against the live repo or raw JSONL.

## Non-interactive invocation

If `AskUserQuestion` isn't available (the skill was invoked in a scripted or subagent context), require an explicit session UUID or path — don't run the picker.

If you're already running as a subagent and have no Agent tool available (verify with `ToolSearch` for `select:Agent`), do NOT fabricate a subagent spawn. Execute the extraction strategy inline in your own context. The discipline is what matters — keeping the raw transcript out of the *outer* session via `jq` filtering to `/tmp/` files. Expect 1.5-2x the token cost vs true subagent isolation since you absorb both orchestration and extraction overhead. Note this in your final response.
