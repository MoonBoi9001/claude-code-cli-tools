---
name: agent-teams
description: Use when creating agent teams (or agent squads), spawning teammates, or coordinating parallel work that benefits from inter-agent communication. Applies when the user asks for a "agent team" or "agent squad", or when the task involves competing hypotheses, parallel review, cross-layer coordination, or multi-component features where agents need to discuss findings. Do not use for subagents or background agents.
user-invocable: false
---

# Agent Teams Guide

## When to Use Agent Teams

Agent teams are the right choice when teammates need to communicate with each other — sharing findings, challenging assumptions, or coordinating across components. The strongest use cases are:

- **Research and review**: multiple teammates investigate different aspects simultaneously, then share and challenge each other's findings
- **Competing hypotheses**: teammates test different theories in parallel and debate toward the answer
- **Cross-layer coordination**: changes spanning frontend, backend, and tests, each owned by a different teammate
- **New modules or features**: teammates each own a separate piece without stepping on each other

If the subtasks are independent and only the result matters, use subagents instead — they're cheaper and simpler.

## Team Sizing

Start with 3-5 teammates. More than that increases coordination overhead with diminishing returns. Aim for 5-6 tasks per teammate to keep everyone productive without excessive context switching.

## Teammate Context

Teammates load project context automatically (CLAUDE.md, MCP servers, skills) but do not inherit the lead's conversation history. Include task-specific details in the spawn prompt — the same principle as subagents: provide everything a brand new team member would need.

## Critical Thinking

Teammates should evaluate whether the proposed approach makes logical sense before implementing. If requirements seem contradictory or counterproductive, teammates should flag concerns and explain their reasoning rather than blindly implementing.

## Task Design

- **Too small**: coordination overhead exceeds the benefit
- **Too large**: teammates work too long without check-ins, increasing risk of wasted effort
- **Right size**: self-contained units that produce a clear deliverable — a function, a test file, a review

Break work so each teammate owns a different set of files. Two teammates editing the same file leads to overwrites.

## Model Selection

Always use the latest available Opus model for teammates. Never use Sonnet or Haiku.

## Plan Approval

For complex or risky tasks, require teammates to plan before implementing. The teammate works in read-only plan mode until the lead approves their approach. Give the lead criteria for approval, such as "only approve plans that include test coverage."

## Cleanup

Always shut down teammates before cleaning up the team. Only the lead should run cleanup — teammates may leave resources in an inconsistent state if they attempt it.
