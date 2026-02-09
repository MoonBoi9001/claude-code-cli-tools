# Subagent Prompting Guide

## Critical Context Principle

Subagents start with ZERO context about the current project, problem, or conversation. They cannot ask clarifying questions - they work with what you provide. The quality of their output directly correlates with the completeness of your prompt. If you want them to do something specific, you need to tell them exactly what to do. For example, if you want them to return information to you after finishing their task, you must explicity tell them in your initial prompt this is what you expect from them or they will not do it.

**Golden Rule**: In your initial prompt, include everything a brand new team member would need to understand, independently research, and get to work solving the problem you will not get another opportunity to tell them later, you must make sure your initial prompt is comprehensive and detailed.

## Critical Thinking Requirement

Before implementing any solution, subagents must evaluate whether the proposed approach makes logical sense in the problem domain. Specifications and issue descriptions may contain flawed assumptions or contradictory requirements.

**Sanity Check Directive**: If requirements seem economically irrational, technically contradictory, or counterproductive to the stated goal, flag the concern and explain your reasoning rather than blindly implementing. Ask yourself: "Does this actually solve the user's problem, or does it create new ones?"

**Domain Awareness**: When working in a specific domain (finance, protocol economics, distributed systems), apply domain knowledge to validate that the solution aligns with how things actually work. A feature that sounds reasonable in isolation may be nonsensical when you understand the underlying economics or technical constraints.

**Example**: If asked to "enforce a higher minimum allocation for zero-signal subgraphs" in a protocol where zero-signal means zero rewards, the agent should flag: "This doesn't make economic sense - why would we force larger allocations to assets that generate no returns?"

## Model Selection

Always use the latest available Opus model for subagents. Never use Sonnet or Haiku.

## Coding standards

Subagents should adhere to all coding standards as defined in CODING-STANDARDS.md unless otherwise specified.

