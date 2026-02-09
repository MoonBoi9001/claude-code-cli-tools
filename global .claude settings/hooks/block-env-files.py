#!/usr/bin/env python3
"""
PreToolUse hook to block read/write/edit operations on sensitive files.
Catches both file tools (Read, Write, Edit) and Bash commands.
"""
from pathlib import Path
import os
import re
import sys

sys.path.insert(0, str(Path(__file__).parent))

from hook_utils import parse_hook_input, deny, pass_through, resolve_path


# =============================================================================
# Sensitive File Patterns
# =============================================================================

SENSITIVE_FILE_PATTERNS = [
    # .env files
    r'\.env$', r'\.env\.', r'/\.env$', r'/\.env\.', r'^\.env$', r'^\.env\.',
    # Secrets
    r'\.pem$', r'\.key$', r'credentials\.json$', r'secrets\.json$',
    r'secrets\.yaml$', r'secrets\.yml$', r'\.secret$',
    r'/\.aws/credentials$', r'\.netrc$',
    # SSH private keys (but NOT config, known_hosts, authorized_keys)
    r'/\.ssh/id_rsa', r'/\.ssh/id_ed25519', r'/\.ssh/id_dsa',
    r'/\.ssh/id_ecdsa', r'\.ssh/.*\.pem$', r'\.ssh/.*\.key$',
    # Postfix SASL credentials
    r'sasl_passwd$', r'sasl_passwd\.db$',
]

SAFE_PATTERNS = [
    r'\.env\.example$', r'\.env\.sample$', r'\.env\.template$',
]

BASH_SENSITIVE_PATTERNS = [
    # .env access
    r'\.env\b', r'\.env\.', r'\.env["\']',
    r'source\s+[^\s]*\.env', r'\.\s+[^\s]*\.env',
    r'cat\s+[^|]*\.env', r'cat\s*<\s*[^\s]*\.env',
    r'eval\s+.*\.env', r'export\s+.*\.env',
    # SSH keys
    r'cat\s+[^|]*id_rsa', r'cat\s+[^|]*id_ed25519',
    r'cat\s+[^|]*\.pem', r'cat\s+[^|]*\.key',
    # Credentials
    r'cat\s+[^|]*credentials', r'cat\s+[^|]*secrets\.',
    # Postfix SASL
    r'cat\s+[^|]*sasl_passwd',
]


# =============================================================================
# Sensitivity Checkers
# =============================================================================

def is_sensitive_file(path: str) -> bool:
    """Check if a path refers to a sensitive file."""
    if not path:
        return False

    # Allow safe template files
    for pattern in SAFE_PATTERNS:
        if re.search(pattern, path, re.IGNORECASE):
            return False

    # Check all path variants
    resolved = resolve_path(path) or path
    normalized = os.path.normpath(path)

    for check_path in [path, normalized, resolved]:
        for pattern in SENSITIVE_FILE_PATTERNS:
            if re.search(pattern, check_path, re.IGNORECASE):
                return True

    return False


def is_sensitive_bash(command: str) -> bool:
    """Check if a bash command accesses sensitive files."""
    if not command:
        return False

    for pattern in BASH_SENSITIVE_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True

    return False


# =============================================================================
# Main
# =============================================================================

def main():
    hook = parse_hook_input()
    if not hook:
        pass_through()

    if not hook.is_pre_tool_use:
        pass_through()

    # Check file-based tools
    if hook.tool_name in ("Read", "Write", "Edit"):
        path = hook.get_input("file_path")
        if is_sensitive_file(path):
            deny(f"Blocked: {hook.tool_name} on sensitive file '{os.path.basename(path)}'")

    elif hook.tool_name == "Glob":
        pattern = hook.get_input("pattern")
        if is_sensitive_file(pattern):
            deny("Blocked: Glob pattern matches sensitive files")

    elif hook.tool_name == "Grep":
        path = hook.get_input("path")
        if is_sensitive_file(path):
            deny("Blocked: Grep on sensitive file")

    elif hook.tool_name == "Bash":
        command = hook.get_input("command")
        if is_sensitive_bash(command):
            deny("Blocked: Bash command accesses sensitive file")

    pass_through()


if __name__ == "__main__":
    main()
