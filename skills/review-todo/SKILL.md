---
name: review-todo
description: Convert the most recent code review in the conversation into a grouped numbered checklist (Decisions needed / Fixes / Polish) of issues to fix. Use this skill whenever the user wants to extract, list, summarize, or triage the issues a reviewer raised — including phrasings like "list the issues from that review", "make me a todo from the review", "turn the review into a checklist", "what did the review flag", "summarize that review as a list", "give me every nit from above", or "/review-todo". Trigger especially as a natural follow-up to /review, /review-pr, /security-review, /ultrareview, or any pasted PR / inline review the user wants to act on. The output is a numbered list of every concrete issue the review raised, grouped under bold section headings, with file:line references appended in parentheses, and decision items rendered with a `→` arrow callout below the description posing the specific question — and lettered choices below that when the reviewer named discrete alternatives.
---

# Review Todo

Convert the most recent code review in the conversation into a tight grouped checklist the user can work straight through. The review will usually come from a `/review`, `/review-pr`, `/security-review`, or pasted PR review, but any block of feedback that names concrete issues is in scope.

The user is going to fix things off this list. Two failure modes ruin it: missing an issue (they will not fix what they cannot see), and burying decisions inside otherwise-actionable items (they cannot fix something that needs their input until they have made the call). Both are addressed below.

## What to extract

Pull every concrete concern the review raised — bugs, correctness issues, nits, naming, style, perf, security gaps, missing tests, doc fixes, typos, suggestions. Items the reviewer labeled "minor", "consider", or "nit" stay in. If the reviewer said "you might want to think about X," it goes in the list. Be exhaustive: the user is asking for *every* issue, not the ones you would prioritize.

If a single review paragraph names three distinct concerns, that is three list items. Do not merge them just because they appear together. The user works through the list one item at a time, and bundled items get half-fixed.

If a section is praise or a high-level summary with no concrete asks, skip it — there is nothing to fix there.

## Format

Group items into three sections, in this order, each as a bold top-level heading separated by a blank line:

- **Decisions needed** — items where the user must choose something before the fix can be applied (see "Items that need a decision" below).
- **Fixes** — concrete, actionable items where the path forward is clear.
- **Polish** — cosmetic issues, nits, perf hints, doc fixes, stale numbers, anything low-stakes.

Decisions go first so the user can answer the questions in one pass, then work straight through the rest. If a section has no items, omit the heading entirely rather than leave it empty.

Number items continuously across sections (1, 2, 3, … — do not restart at each heading). Within each section, keep the review's original order. One short sentence per item description, soft cap of about 20 words. **Fixes** and **Polish** items are description-only — no sub-bullets, no nesting. **Decisions needed** items carry an additional `→ Question?` block (and optionally lettered choices) below the description, as detailed in the next section. No preamble before the first heading, no closing remarks.

**Lead each item with prose, not metadata.** The first few words are what the user's eye lands on when skimming, so they should describe the problem, not the location. Start with a natural article or verb — "The retry loop…", "Each source file…", "Add a test…" — never with a bare file path or a bare noun phrase. "Retry loop has no cap" is one word away from "The retry loop has no cap" and the second is meaningfully easier to read.

**Put file:line references at the end, in parentheses.** They are navigation metadata, useful once the user has decided to act on the item but distracting before that. If the reviewer named a file but no line, put just the filename. If they named neither, omit the parenthetical and let the prose stand alone.

```
**Fixes**
3. Add a test for the `--dry-run --daemon` combo so a future guard change can't silently break it (compact.py).
4. The `safe=False` cast invariant is only doc-pinned — add a guard or test that fails if a non-null promotion path is added (compact.py:`_resolve_field_type`).

**Polish**
6. Each source file is opened twice (schema read, then table read) — cache schemas if first-backfill latency matters (compact.py:`_unify_schemas`).
7. The verify step trusts non-timestamp columns blindly — only timestamp min/max round-trips (compact.py:`_verify_compacted`).
```

## Items that need a decision before they can be fixed

Some review findings cannot be acted on until the user picks something. Architectural tradeoffs the reviewer flagged but did not resolve, "consider X or Y" without a recommendation, fixes that change product behavior, fixes that pick between incompatible approaches — all need input. These go in the **Decisions needed** section.

Render the question on its own line below the item description, prefixed with `→ ` and capitalised as a sentence ending in `?`. The arrow is the visual anchor — every decision point in the document should be findable by it in one scan. Stating the actual question matters: a bare flag tells the user "something is up" but not what they need to think about.

When the reviewer named two or more discrete alternatives, list them as lettered sub-options (`a.`, `b.`, `c.`…) indented two spaces under the question. Lettered, not numbered, so they cannot be confused with the parent item number. When the reviewer's framing or the surrounding context implies a clear lean, annotate one choice with `  *(recommended)*` (two spaces, then the italic-and-parens marker) as a suffix — a hint, not a verdict. Skip the marker when both options are genuinely a judgement call; leaving it off is itself a signal. When the decision is open-ended with no enumerated alternatives, the `→ Question?` line stands alone with nothing below it.

```
**Decisions needed**
1. The retry loop has no cap or escalation — one bad date logs WARNING hourly forever (compact.py:`_run_sweep_safely`).

   → Cap with backoff, escalate to ERROR for ntfy, or quarantine the bad date?
     a. cap retries with exponential backoff  *(recommended)*
     b. escalate to ERROR and route to ntfy
     c. quarantine the bad date and continue

2. The compactor's 4 AM ET wake-up time is documented in three places (compact.py + docker-compose.yml + SKILL.md).

   → Pass `--target-hour` from compose for a single source of truth, or accept the duplication?
     a. plumb `--target-hour` through compose
     b. accept the duplication and add a comment in each place

3. The new `GRT_MIN_STAKE` env var landed in the gateway config but reviewer thinks it's misplaced (config/gateway.yaml:31).

   → Which service owns this setting?
```

A finding where the reviewer already recommended a specific fix is *not* a decision item, even if it touches architecture — the decision is made, the user just has to apply it. Those go in **Fixes**.

## What not to do

- Do not invent issues the review did not raise. The list must be a faithful extraction, not a fresh review.
- Do not paraphrase so loosely that the original meaning shifts. Tight is good; misleading is not.
- Do not merge two distinct issues even if they touch the same file or component.
- Do not include praise, summary preamble, or any commentary outside the sections themselves.
- Do not lead an item with a file path or a bare noun. Add a natural article or verb so the eye lands on the problem.
- Do not inline the question on the same line as the item description — drop to a new line and lead with `→ `.
- Do not number the lettered choices (`1.`, `2.`) — use letters (`a.`, `b.`) so they cannot be confused with the parent item number.

## Edge cases

If the review raised zero issues (e.g., the reviewer signed off without any concerns), output exactly:

```
No issues raised.
```

If there is no code review present in the conversation to extract from, say so in one sentence and stop. The user can then paste a review and reinvoke.
