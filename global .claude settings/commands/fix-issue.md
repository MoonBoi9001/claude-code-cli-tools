# (Required Flags: --<issue-number>)

## Flags

**Required flags:**

- `--<issue-number>`: The GitHub issue we want to fix

## Description

Analyze a GitHub issue based on the issue number flag and propose code solutions to address the issue:

## Use

`/fix-issue [flags]`

## Claude will

1. Fetch issue details (title, description, requirements, labels)
2. Analyze the codebase to understand relevant files and architecture
3. Identify the specific changes needed to address the issue
4. Formulate a plan/TODO to address the issue
5. Check the plan for any potential issues and take a moment to refine the plan where appropriate
   - The plan/TODO could detail which files/functions/methods/classes need modification
   - The plan/TODO may give specific implementation details or technical approach
   - The plan/TODO may say how we will ensure integration with existing codebase patterns
   - The plan/TODO may give testing considerations and additional validation steps
6. Present the proposed plan for review and approval
7. Implement the plan changes if approved
