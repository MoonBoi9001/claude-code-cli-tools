---
name: subagent-guide
description: MUST invoke before ANY use of the Agent tool — whether the user requests it or you decide independently to delegate work to (parallel) subagents. Applies when spawning subagents, launching background agents, writing prompts for subagents, choosing between foreground and background execution, or deciding how many subagents to spawn. Do not use for agent teams or agent squads.
user-invocable: false
---

# Subagent Prompting Guide

## Critical Context Principle

Subagents start with zero context about the current project, problem, or conversation. They cannot ask clarifying questions — they work with what you provide. The quality of their output directly correlates with the completeness of your prompt.

**Golden Rule**: Include everything a brand new team member would need to understand, independently research, and complete the task. You will not get another opportunity to clarify — the initial prompt must be comprehensive and detailed. If you want the subagent to return specific information after finishing, you must explicitly say so in the prompt.

## Critical Thinking Requirement

Before implementing any solution, subagents must evaluate whether the proposed approach makes logical sense in the problem domain. Specifications and issue descriptions may contain flawed assumptions or contradictory requirements.

**Sanity Check Directive**: If requirements seem economically irrational, technically contradictory, or counterproductive to the stated goal, flag the concern and explain your reasoning rather than blindly implementing. Ask: "Does this actually solve the user's problem, or does it create new ones?"

**Domain Awareness**: Apply domain knowledge to validate that the solution aligns with how things actually work. A feature that sounds reasonable in isolation may be nonsensical given underlying economic or technical constraints.

**Example**: If asked to "enforce a higher minimum allocation for zero-signal subgraphs" in a protocol where zero-signal means zero rewards, the agent should flag: "This doesn't make economic sense — why would we force larger allocations to assets that generate no returns?"

## Model Selection

Always use the latest available Opus model for subagents. Never use Sonnet or Haiku.

## Coding Standards

Subagents should adhere to all coding standards as defined in CODING-STANDARDS.md unless otherwise specified.
