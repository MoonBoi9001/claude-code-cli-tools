# Coding Standards (coding-standards.md / CODING-STANDARDS.md)

Remember to follow these coding standards when writing code.

## Core Principles

### DRY (Don't Repeat Yourself)

Extract repeated logic into functions, classes, or utilities. If the same code appears twice, it should be abstracted.

### KISS (Keep It Simple, Stupid)

Choose the simplest solution that solves the problem. Avoid premature optimization and over-engineering.

### SOLID

**S - Single Responsibility**: One class = one reason to change.

**O - Open/Closed**: Open for extension, closed for modification.

**L - Liskov Substitution**: Subtypes must be substitutable for base types.

**I - Interface Segregation**: Specific interfaces > general interface.

**D - Dependency Inversion**: Depend on abstractions, not concretions.

## Async & Concurrency

**No blocking in async contexts.**

**Shared state needs synchronization.**

**Avoid hold-across-await.**

## Security

**Validate at boundaries.** All external input (user input, API responses, config files) must be validated before use. Internal code can trust internal data.

**No secrets in code.**

**Parameterize queries.** Use parameterized queries or ORMs. Never interpolate user input into SQL or shell commands.

## Critical Thinking

Question assumptions before implementing major changes. Specifications may contain flawed logic or contradictory requirements.

### Sanity Check Before Changes

Before removing significant code (>500 lines) or refactoring architecture:

**Trace responsibility flow**: Where does this logic move? Does the target component have necessary context? If configuration becomes orphaned (defined but unused), the design is broken.

**Verify with code, not logic**: Check actual implementation in affected systems. Assumptions about "another system handles this" often fail when you read that system's code.

**Consider performance**: Distinguish cheap operations (in-memory checks) from expensive ones (network I/O, database queries).

### Warning Signs

Stop and reconsider when:

- User questions the approach - Don't defend. Reconsider from first principles.
- Removing code without verified replacement implementation
- Cross-system impacts not traced end-to-end
- Assumptions not validated by examining actual code

### Domain Awareness

Apply domain knowledge to validate solutions. A feature that sounds reasonable may be nonsensical given underlying constraints.

## Testing Standards

### TDD (Test-Driven Development)

Ideally, write tests BEFORE implementation, following red-green-refactor.

### AAA (Arrange, Act, Assert)

Structure every test with three clear sections:
1. Arrange
2. Act
3. Assert

### FIRST Principles

**Fast**: Tests run in milliseconds.

**Independent**: Tests don't depend on each other.

**Repeatable**: Same result every time.

**Self-validating**: Pass/fail with no manual checks.

**Timely**: Write tests when they're needed.

### FF (Fail Fast)

Validate inputs immediately.

## Code Review Checklist

Before submitting code, verify:

- [ ] No repeated code (DRY)
- [ ] Simplest solution chosen (KISS)
- [ ] Single responsibility per class/function
- [ ] Tests written first or alongside code
- [ ] All tests follow AAA structure
- [ ] Tests are FIRST compliant
- [ ] Input validation fails fast
- [ ] Dependencies injected, not hardcoded
- [ ] No blocking calls in async code
- [ ] No secrets hardcoded
- [ ] External input validated at boundaries

## When to Break Rules

**DRY**: Repeat code if abstraction would be more complex.
**KISS**: Add complexity when simplicity creates bugs or performance issues.

## Red Flags

- High cyclomatic complexity
- Deep nesting
- Test files without AAA
- Missing error handling
- Hardcoded config
- No type hints/types
- Classes doing too many unrelated things
- Tight coupling
- Dead code
- Blocking calls in async functions
- Loops that issue one query per iteration
- Comments that contradict the code

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
