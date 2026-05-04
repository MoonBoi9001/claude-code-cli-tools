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

1. Check CI status on the PR:
   ```
   gh pr checks
   ```
   Inspect the exit code:
   - **0** — all checks passed. Continue.
   - **8** — checks are still pending. Warn the user that CI hasn't finished and stop. Don't merge on top of incomplete CI.
   - **any other non-zero** — one or more checks failed. Report which ones and stop.

   If the repo has no CI configured, `gh pr checks` exits 0 with no output — treat that as "nothing to check" and continue.

2. Capture the head and base branches before merging:
   ```
   gh pr view --json headRefName,baseRefName
   ```

3. Merge the PR — **without `--delete-branch`**:
   ```
   gh pr merge --<strategy>
   ```
   The repo has `delete_branch_on_merge` enabled at the GitHub level, so GitHub deletes the remote head branch and auto-retargets any chained PRs onto the base branch. Passing `--delete-branch` would instead **close** those chained PRs, so we deliberately omit it.

4. Switch to the base branch, pull, and delete the local head branch:
   ```
   git checkout <base>
   git pull
   git branch -D <head>
   ```
   Use `-D` (force) — after a squash or rebase merge, the local branch tip won't match the new commit on base, so `-d` would refuse.

5. Prune stale remote-tracking references:
   ```
   git fetch --prune
   ```
   Cleans up the orphaned `origin/<head>` ref left behind by GitHub's remote deletion.

If any step fails, stop and report the error rather than continuing.
