---
name: land-pr
description: Merge the current PR (squash by default, or rebase if specified), delete the branch, checkout main, fetch and pull. Use when the user says "land", "land the PR", "merge the PR", "merge and clean up", "land it", or wants to finish/complete a PR.
argument-hint: [squash|rebase]
disable-model-invocation: true
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

2. Identify the base branch this PR targets:
   ```
   gh pr view --json baseRefName --jq '.baseRefName'
   ```

3. Merge the PR and delete the remote branch:
   ```
   gh pr merge --<strategy> --delete-branch
   ```

4. Switch to the base branch and pull:
   ```
   git checkout <base-branch> && git fetch --prune && git pull
   ```

5. Clean up the local branch if it still exists:
   ```
   git branch -d <branch-name>
   ```

If any step fails, stop and report the error rather than continuing.
