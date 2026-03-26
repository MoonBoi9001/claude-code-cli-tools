#!/usr/bin/env python3
"""
Auto-approve Edit/Write operations on files within allowed directories.

Works alongside block-env-files.py which runs first as a PreToolUse hook
to block sensitive files.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from hook_utils import (
    parse_hook_input, approve, pass_through,
    resolve_path, is_path_within
)

# =============================================================================
# Configuration: Add directories to auto-approve for Edit/Write
# =============================================================================

ALLOWED_DIRS = [
    "~/Documents/github",
]

# =============================================================================

# Resolve paths at import time
_RESOLVED_DIRS = tuple(
    resolved for d in ALLOWED_DIRS
    if (resolved := resolve_path(d))
)

# Tool name -> input key mapping
PATH_KEYS = {
    "Edit": "file_path",
    "Write": "file_path",
}


def main():
    hook = parse_hook_input()
    if not hook:
        pass_through()

    if not hook.is_permission_request:
        pass_through()

    path_key = PATH_KEYS.get(hook.tool_name)
    if not path_key:
        pass_through()

    path = hook.get_input(path_key)
    if path and is_path_within(path, _RESOLVED_DIRS):
        approve()

    pass_through()


if __name__ == "__main__":
    main()
