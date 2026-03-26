#!/usr/bin/env python3
"""
Auto-approve bash commands when they match patterns in the allow list.

Handles both single commands and chained commands (pipes, &&, ||, ;).
Bypasses Claude Code's built-in permission matching which has issues with
commands containing shell-like characters (|, >, &) even when quoted/escaped.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from hook_utils import (
    parse_hook_input, approve, pass_through,
    CommandValidator
)


def main():
    hook = parse_hook_input()
    if not hook:
        pass_through()

    # Only handle Bash permission requests
    if not hook.is_permission_request or hook.tool_name != "Bash":
        pass_through()

    command = hook.get_input("command")

    # Validate all commands (single or chained) against allow patterns
    result = CommandValidator().validate(command)
    if result.approved:
        approve()

    pass_through()


if __name__ == "__main__":
    main()
