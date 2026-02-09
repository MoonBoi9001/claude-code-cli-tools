# Coding Standards (coding-standards.md / CODING-STANDARDS.md)

Remember to follow these standards when writing code.
If the user explicitly asks you to follow coding standards, these are the standards you should follow.
If the user does not explicitly ask you to follow coding standards, you should still follow these standards, unless the user explicitly asks you to not follow them.

## Core Principles

### DRY (Don't Repeat Yourself)

Extract repeated logic into functions, classes, or utilities. If the same code appears twice, it should be abstracted.

### KISS (Keep It Simple, Stupid)

Choose the simplest solution that solves the problem. Avoid premature optimization and over-engineering.

### SOLID

**S - Single Responsibility**: One class = one reason to change.

**O - Open/Closed**: Open for extension, closed for modification.

**L - Liskov Substitution**: Subtypes must be substitutable for base types.

**I - Interface Segregation**: Many specific interfaces > one general interface.

**D - Dependency Inversion**: Depend on abstractions, not concretions.

## Testing Standards

### TDD (Test-Driven Development)

Write tests BEFORE implementation, following red-green-refactor cycle:

1. Write failing test
2. Write minimal code to pass the test
3. Refactor the code to make it better

### AAA (Arrange, Act, Assert)

Structure every test with three clear sections:

1. Arrange - Set up test data and dependencies
2. Act - Execute the code under test
3. Assert - Verify the results

### FIRST Principles

**Fast**: Tests run in milliseconds. Mock external dependencies.

**Independent**: Tests don't depend on each other. Each test has its own setup.

**Repeatable**: Same result every time. Mock time-dependent and random behavior.

**Self-validating**: Pass/fail with no manual checks. Use assertions, not print statements.

**Timely**: Write tests when they're needed (ideally before code).

### FF (Fail Fast)

Validate inputs immediately. Don't let invalid data propagate through the system.

## Code Review Checklist

Before submitting code, verify:

- [ ] No repeated code (DRY)
- [ ] Simplest solution chosen (KISS)
- [ ] Single responsibility per class/function (SOLID-S)
- [ ] Tests written first or alongside code (TDD)
- [ ] All tests follow AAA structure
- [ ] Tests are FIRST compliant
- [ ] Input validation fails fast (FF)
- [ ] Dependencies injected, not hardcoded (SOLID-D)

## When to Break Rules

**DRY**: Repeat code if abstraction would be more complex than duplication.
**KISS**: Add complexity when simplicity creates bugs or performance issues.
**SOLID**: Small scripts don't need full SOLID architecture.
**TDD**: Exploratory prototypes can defer tests until design stabilizes.

## Red Flags

- High cyclomatic complexity (>10 per function)
- Deep nesting (>3 levels of indentation)
- Test files without AAA structure
- Missing error handling
- Hardcoded configuration values
- No type hints (Python) or types (TypeScript)
- God objects (classes doing too many unrelated things)
- Tight coupling (dependencies on concrete implementations)

## Git Workflow

### Branch Strategy

- **Never push directly to main unless explicitly asked** - All changes must go through pull requests
- Branch names follow conventional commit types: `<type>/<issue>-description`
  - `feat/`, `fix/`, `chore/`, `docs/`, `refactor/`, `test/`
- Use conventional commit messages with issue references

### Pull Request Process

1. Create branch from main
2. Make commits on branch
3. Push branch and create PR
4. Wait for review/approval before merging
