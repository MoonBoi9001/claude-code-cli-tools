#!/usr/bin/env python3
"""
Auto-approve chained bash commands when all individual commands are in the allow list.

Solves the problem where `ls | grep foo` or `cd /path && make` requires approval
even though all individual commands are allowed.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from hook_utils import (
    parse_hook_input, approve, pass_through,
    CommandValidator, ChainSplitter
)


def main():
    hook = parse_hook_input()
    if not hook:
        pass_through()

    # Only handle Bash permission requests
    if not hook.is_permission_request or hook.tool_name != "Bash":
        pass_through()

    command = hook.get_input("command")

    # Skip single commands without operators (let standard allow list handle)
    if not ChainSplitter().has_operators(command):
        pass_through()

    # Validate the command chain
    result = CommandValidator().validate(command)
    if result.approved:
        approve()

    pass_through()


if __name__ == "__main__":
    main()
