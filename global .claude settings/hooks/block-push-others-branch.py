#!/usr/bin/env python3
"""
PreToolUse hook to block pushing to branches created by others.

When Claude runs `git push`, this hook checks whether the current branch
has existing commits on the remote authored by other GitHub users. If the
current user has no commits on the remote branch, the push is blocked
with a suggestion to create a separate branch and open a PR instead.
"""
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).parent))

from hook_utils import parse_hook_input, deny, pass_through


SHARED_BRANCHES = {"main", "master", "develop", "staging", "production", "release"}


def run(cmd: list[str], timeout: int = 15) -> str:
    """Run a command and return stdout, or empty string on failure."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip() if result.returncode == 0 else ""
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def run_checked(cmd: list[str], timeout: int = 15) -> tuple[bool, str]:
    """Run a command, distinguishing failure from empty output.

    Returns (True, stdout) on success, (False, "") on failure.
    """
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, ""
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False, ""


def main():
    hook = parse_hook_input()
    if not hook:
        pass_through()

    if not hook.is_pre_tool_use:
        pass_through()

    if hook.tool_name != "Bash":
        pass_through()

    command = hook.get_input("command")
    if not re.search(r'\bgit\s+push\b', command):
        pass_through()

    branch = run(["git", "symbolic-ref", "--short", "HEAD"])
    if not branch or branch in SHARED_BRANCHES:
        pass_through()

    # New branch (not on remote yet) is safe to push.
    # Fail open here: if the remote is unreachable, the push itself will also fail.
    if not run(["git", "ls-remote", "--heads", "origin", branch]):
        pass_through()

    # From here the remote branch exists, so we must verify ownership.
    # Fail closed on gh API errors — a transient network glitch should not
    # silently bypass the check.

    ok, gh_user = run_checked(["gh", "api", "user", "-q", ".login"])
    if not ok:
        deny(
            f"Cannot verify branch ownership for '{branch}': "
            f"failed to determine your GitHub username (gh api error). "
            f"This may be a transient network issue — retry the push."
        )
    if not gh_user:
        pass_through()

    default_branch = (
        run(["gh", "api", "repos/{owner}/{repo}", "-q", ".default_branch"])
        or "main"
    )

    ok, authors_raw = run_checked([
        "gh", "api",
        f"repos/{{owner}}/{{repo}}/compare/{default_branch}...{branch}",
        "-q", ".commits[].author.login",
    ])
    if not ok:
        deny(
            f"Cannot verify branch ownership for '{branch}': "
            f"failed to fetch commit authors (gh api error). "
            f"This may be a transient network issue — retry the push."
        )
    if not authors_raw:
        pass_through()  # No divergent commits, can't determine ownership

    authors = {a for a in authors_raw.splitlines() if a}
    if not authors or gh_user in authors:
        pass_through()

    author_list = ", ".join(sorted(authors))
    deny(
        f"Blocked: Branch '{branch}' belongs to {author_list}. "
        f"You ({gh_user}) have no commits on this remote branch. "
        f"Create your own branch and open a PR to '{branch}' instead."
    )


if __name__ == "__main__":
    main()
