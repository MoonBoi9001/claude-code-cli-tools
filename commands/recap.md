### 1. Recap
Quick load context into new claude session and get an overview of current work state and suggested next actions:

`/recap`

Claude will:
1. Review the current repository and form a deep understanding of it
2. Review CLAUDE.md
3. Review SESSION_CONTEXT.md
4. Review current branch and commit status
5. Review recent commits and changes
6. Review open issues
7. Review uncommitted changes if any
8. Suggest logical next actions based on context

Example usage:
```
Human: /recap
Claude: [reviews everything as per instructions above and then gives next action suggestions]
```

Example output:
```
## 1. Repository Overview
- **Project**: E-commerce platform with React frontend and Node.js backend
- **Structure**: Monorepo with packages for frontend, backend, and shared utilities
- **Key Technologies**: TypeScript, React, Express, PostgreSQL, Redis

## 2. Project Configuration (from CLAUDE.md)
- TypeScript with strict mode enabled
- Jest for testing, ESLint + Prettier for code quality
- Conventional commits required for all changes

## 3. Session Context (from SESSION_CONTEXT.md)
- **Current Work**: Implementing payment processing with Stripe
- **Technical Decisions**: Using webhook handlers for async payment events
- **Recent Discovery**: Need to handle idempotency for payment retries
- **Next Steps**: Add integration tests for payment flow

## 4. Current Branch Status
- **Branch**: feature/payment-processing (5 commits ahead of main)
- **Remote**: origin/feature/payment-processing (up to date)

## 5. Recent Commits
- abc123: feat: Add Stripe payment integration
- def456: test: Add payment service unit tests  
- ghi789: refactor: Extract payment validation logic
- jkl012: docs: Update API docs with payment endpoints
- mno345: fix: Handle payment webhook timeouts

## 6. Open Issues
**High Priority:**
- #10: Implement payment processing (in progress)
- #11: Add user dashboard
- #13: Set up monitoring for payment failures

**Medium Priority:**
- #15: Improve error handling across services
- #18: Add rate limiting to API endpoints

## 7. Uncommitted Changes
- Modified: src/services/payment.service.ts (added retry logic)
- Modified: src/controllers/checkout.controller.ts (webhook handler)
- New file: src/utils/idempotency.ts

## 8. Suggested Next Actions
1. Commit current payment service changes with retry logic
2. Implement remaining webhook handlers for payment events
3. Write integration tests for complete payment flow
4. Update environment variables documentation for Stripe keys
5. Create PR once tests are passing
```
