### 4. Fix Issue

Analyze a GitHub issue and propose code solutions to address the requirements:

`/fix-issue <issue-number>`

Claude will:

1. Fetch issue details (title, description, requirements, labels)
2. Analyze the codebase to understand relevant files and architecture
3. Identify the specific changes needed to address the issue
4. Propose concrete code implementations with:
   - File modifications or new file creation
   - Implementation details and technical approach
   - Integration with existing codebase patterns
   - Testing considerations and validation steps
5. Present the proposed solution for review and approval
6. Optionally implement the changes if approved

Example usage:

```text
Human: /fix-issue 10
Claude: Analyzing issue #10: "Add user authentication system"

Issue analysis:
- Type: New feature implementation
- Scope: Backend authentication with JWT tokens
- Requirements: Login, registration, password reset

Proposed solution:
1. Create authentication middleware
2. Add user model and database schema
3. Implement JWT token generation

Would you like me to implement these changes?
```

Analysis approach:

- **Issue classification**: Determine if it's a bug fix, feature, or improvement
- **Codebase impact**: Identify which files and modules need changes
- **Technical feasibility**: Assess complexity and implementation approach
- **Architecture alignment**: Ensure solution fits existing patterns
- **Testing strategy**: Propose validation and testing approaches
