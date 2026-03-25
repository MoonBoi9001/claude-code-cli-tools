---
name: land-pr
description: Merge the current PR (squash by default, or rebase if specified), delete the branch, checkout main, fetch and pull. Use when the user says "land", "land the PR", "merge the PR", "merge and clean up", "land it", or wants to finish/complete a PR.
argument-hint: [squash|rebase]
disable-model-invocation: true
allowed-tools: Bash
---

Merge the current branch's PR, clean up, and return to main.

## Merge strategy

Use `` if provided. If not, default to `--squash`. Valid values: `squash`, `rebase`.

## Steps

1. Merge the PR and delete the remote branch:
   ```
   gh pr merge --<strategy> --delete-branch
   ```

2. Switch to main and pull:
   ```
   git checkout main && git fetch --prune && git pull
   ```

3. Clean up the local branch if it still exists:
   ```
   git branch -d <branch-name>
   ```

If any step fails, stop and report the error rather than continuing.
