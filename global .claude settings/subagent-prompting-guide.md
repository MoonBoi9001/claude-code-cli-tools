# Subagent Prompting Guide

## Critical Context Principle

Subagents start with ZERO context about the current project, problem, or conversation. They cannot ask clarifying questions - they work with what you provide. The quality of their output directly correlates with the completeness of your prompt. If you want them to do something specific, you need to tell them exactly what to do. For example, if you want them to return information to you after finishing their task, you must explicity tell them in your initial prompt this is what you expect from them or they will not do it.

**Golden Rule**: In your initial prompt, include everything a brand new team member would need to understand, independently research, and get to work solving the problem you will not get another opportunity to tell them later, you must make sure your initial prompt is comprehensive and detailed.
