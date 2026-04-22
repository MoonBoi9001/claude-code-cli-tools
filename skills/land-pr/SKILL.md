---
name: land-pr
description: Merge the current PR (squash by default, or rebase if specified), delete the branch, checkout main, fetch and pull. Use when the user says "land", "land the PR", "merge the PR", "merge and clean up", "land it", or wants to finish/complete a PR.
argument-hint: [squash|rebase]
allowed-tools: Bash
---

Merge the current branch's PR, clean up, and return to the base branch.

## Merge strategy

Use `<arg1>` if provided. If not, default to `--squash`. Valid values: `squash`, `rebase`.

## Steps

1. Check for chained PRs that depend on this branch:
   ```
   gh pr list --base <current-branch> --state open
   ```
   If any open PRs target this branch, warn the user and stop. Deleting the branch would close those PRs. The user needs to retarget them first (e.g. `gh pr edit <number> --base main`).

2. Check CI status on the PR:
   ```
   gh pr checks
   ```
   Inspect the exit code:
   - **0** — all checks passed. Continue.
   - **8** — checks are still pending. Warn the user that CI hasn't finished and stop. Don't merge on top of incomplete CI.
   - **any other non-zero** — one or more checks failed. Report which ones and stop.

   If the repo has no CI configured, `gh pr checks` exits 0 with no output — treat that as "nothing to check" and continue.

3. Identify the base branch this PR targets:
   ```
   gh pr view --json baseRefName --jq '.baseRefName'
   ```

4. Merge the PR, delete branches, and switch to the base branch:
   ```
   gh pr merge --<strategy> --delete-branch
   ```
   `gh pr merge --delete-branch` handles: merging, deleting the remote branch, switching to the base branch, fetching, pulling, and deleting the local branch.

5. Prune stale remote-tracking references:
   ```
   git fetch --prune
   ```
   `gh pr merge` does not prune remote-tracking refs for the deleted branch, so this cleans up the orphaned `origin/<branch>` ref.

If any step fails, stop and report the error rather than continuing.
