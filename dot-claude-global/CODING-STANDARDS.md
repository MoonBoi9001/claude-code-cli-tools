# Coding Standards (coding-standards.md / CODING-STANDARDS.md)

Follow these coding standards when writing code, to ensure that the quality of the code passes what is expected from you.

## Core Principles

### DRY (Don't Repeat Yourself)

Abstract when you'd need to change multiple places for one logical change.

**Keep repetition when:**

- Each instance is simple and self-documenting
- The abstraction costs more to understand than the duplication
- The "duplicates" serve different purposes and may diverge

Prefer simple code that repeats over clever code that doesn't.

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

Before removing significant code or refactoring architecture:

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

## No Silent Failures

Code that swallows errors and continues is code that can be broken for weeks without anyone knowing.

**Never swallow errors.** `except Exception: pass` and `except Exception: return default` without logging are forbidden. Log with enough context to diagnose. Prefer re-raising.

**Fallbacks must be observable.** If code catches an error and continues with reduced functionality, surface it through metrics, structured log fields, or health endpoint status.

**Distinguish expected absence from unexpected failure.** A missing optional config is a DEBUG log. A crashed dependency is a WARNING or ERROR.

## Code Review Checklist

Before submitting code, verify:

- [ ] Repetition justified or abstracted (DRY)
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
- [ ] Fallback paths are observable (metrics, structured logs, health status)

## When to Break Rules

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
- Comments that contradict code
- Silent fallbacks (`except: return default` without logging or metrics)
- Degradation paths with no observability

## Git Workflow

### Commit Messages

- Title: conventional commit format, under 72 characters
- Body: 1-5 lines max, wrap at 125 characters. State what changed and why, not a full essay. Save detailed context for the PR body.
- Never restate the title in the body

### Branch Strategy

- **Never push directly to main unless explicitly asked** - All changes must go through pull requests
- Branch names MUST use the `mb9/` prefix: `mb9/<laymens-description>`
  - Descriptions should be readable without codebase context — prefer slightly verbose plain English over terse developer shorthand (e.g. `add-login-authentication` not `add-auth`, `fix-dashboard-loading-crash` not `fix-null-pointer`)
  - e.g. `mb9/add-login-authentication`, `mb9/fix-dashboard-loading-crash`
- Use conventional commit messages with issue references

### PR Sizing

Prefer small, incremental PRs over large feature-complete ones. A PR that touches 5+ files or introduces a full feature in one shot is hard to review — split it into smaller logical changesets that each make sense on their own. Each PR should represent one coherent step: a new type, a migration, a single behaviour change. Reviewers can move faster through a stack of focused PRs than one sprawling diff.

When working with coding agents, this matters even more — agents can produce large changesets quickly, but the review bottleneck remains human. Structure the work so each PR is reviewable in a single sitting.
