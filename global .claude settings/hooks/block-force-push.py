#!/usr/bin/env python3
"""
PreToolUse hook to block dangerous git force pushes.

Blocks:
  - git push --force / -f: Can overwrite others' work without checking
  - git push origin <branch> --force: Same issue

Safe alternative:
  - git push --force-with-lease: Only force pushes if remote hasn't changed
"""
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).parent))

from hook_utils import parse_hook_input, deny, pass_through


def is_dangerous_force_push(command: str) -> bool:
    """Check if command is a dangerous force push (not force-with-lease)."""
    if not command:
        return False

    # Must be a git push command
    if not re.search(r'\bgit\s+push\b', command):
        return False

    # Check for --force-with-lease (the safe option) - if present, allow it
    if re.search(r'--force-with-lease\b', command):
        return False

    # Check for dangerous --force or -f flags
    # Match --force but not --force-with-lease (already handled above)
    if re.search(r'--force\b', command):
        return True

    # Match -f flag (but be careful not to match other flags)
    # -f can appear as: -f, -af, -fa, etc.
    if re.search(r'\s-[a-zA-Z]*f[a-zA-Z]*\b', command):
        return True

    return False


def main():
    hook = parse_hook_input()
    if not hook:
        pass_through()

    if not hook.is_pre_tool_use:
        pass_through()

    if hook.tool_name != "Bash":
        pass_through()

    command = hook.get_input("command")

    if is_dangerous_force_push(command):
        deny(
            "Blocked: 'git push --force' can overwrite others' work. "
            "Use 'git push --force-with-lease' instead - it only force pushes "
            "if the remote branch hasn't been updated by someone else."
        )

    pass_through()


if __name__ == "__main__":
    main()
