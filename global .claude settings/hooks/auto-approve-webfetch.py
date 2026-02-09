#!/usr/bin/env python3
"""Auto-approve all WebFetch tool requests."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from hook_utils import parse_hook_input, approve, pass_through


def main():
    hook = parse_hook_input()
    if not hook:
        pass_through()

    if hook.is_permission_request and hook.tool_name == "WebFetch":
        approve()

    pass_through()


if __name__ == "__main__":
    main()
