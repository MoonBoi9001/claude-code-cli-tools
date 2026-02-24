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
# Deny Message (instructs agent not to attempt bypasses)
# =============================================================================

DENY_MSG = """BLOCKED: Access to sensitive file denied.

This file contains secrets/credentials and is protected by security policy.
DO NOT attempt to:
- Use alternative commands (head, tail, less, sed, awk, grep, base64, xxd, etc.)
- Copy the file to another location
- Create symlinks to the file
- Use programming languages to read the file
- Access the file through any other means

If you need values from this file, ask the user to provide them directly."""


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
    # Cloud provider credentials
    r'/\.azure/', r'\.azure/accessTokens\.json$',
    r'/\.config/gcloud/', r'application_default_credentials\.json$',
    r'/\.kube/config$',
    r'/\.docker/config\.json$',
    # Package manager tokens
    r'/\.npmrc$', r'\.npmrc$',
    r'/\.pypirc$', r'\.pypirc$',
    r'/\.gem/credentials$',
    r'/\.composer/auth\.json$',
    # Database credentials
    r'/\.pgpass$', r'\.pgpass$',
    r'/\.my\.cnf$', r'\.my\.cnf$',
    # Git credentials
    r'/\.git-credentials$', r'\.git-credentials$',
    # Certificates with private keys
    r'\.keystore$', r'\.jks$', r'\.p12$', r'\.pfx$',
    # Infrastructure secrets
    r'terraform\.tfvars$', r'\.tfstate$',
    r'vault-token$', r'\.vault-token$',
    r'\.htpasswd$',
    # GPG/PGP private keys
    r'/\.gnupg/private-keys', r'\.gpg$', r'secring\.gpg$',
    # Password managers
    r'/\.password-store/', r'\.kdbx$',  # pass, keepass
    # Generic secret file names
    r'/api[_-]?key$', r'/apikey$', r'/token$',
    # History files (can contain secrets)
    r'\.bash_history$', r'\.zsh_history$', r'\.python_history$',
]

SAFE_PATTERNS = [
    r'\.env\.example$', r'\.env\.sample$', r'\.env\.template$',
]

# Commands that can read file contents
FILE_READ_COMMANDS = [
    'cat', 'head', 'tail', 'less', 'more', 'view',
    'sed', 'awk', 'grep', 'egrep', 'fgrep', 'rg',
    'base64', 'xxd', 'od', 'hexdump', 'strings',
    'dd', 'tr', 'cut', 'paste', 'sort', 'uniq',
    'python', 'python3', 'node', 'ruby', 'perl', 'php',
    'vim', 'nvim', 'nano', 'emacs',
    'bat', 'batcat',  # modern cat alternatives
    'jq', 'yq',  # JSON/YAML processors
    'xargs',  # can be used to read files
]

# Sensitive file basenames/patterns for bash detection
SENSITIVE_BASENAMES = [
    r'\.env', r'\.pem', r'\.key', r'id_rsa', r'id_ed25519', r'id_dsa', r'id_ecdsa',
    r'credentials', r'secrets\.', r'sasl_passwd', r'\.netrc', r'\.pgpass',
    r'\.npmrc', r'\.pypirc', r'\.my\.cnf', r'\.git-credentials', r'config\.json',
    r'auth\.json', r'\.keystore', r'\.jks', r'\.p12', r'\.pfx', r'\.tfvars',
    r'\.tfstate', r'vault-token', r'\.htpasswd', r'api[_-]?key', r'apikey',
    r'application_default_credentials', r'accessTokens',
    r'/token$', r'[/_]token\.', r'\.token$',  # token files but not tokenizer.py etc
]

BASH_SENSITIVE_PATTERNS = [
    # Source/eval .env
    r'source\s+[^\s]*\.env', r'\.\s+[^\s]*\.env',
    r'eval\s+.*\.env', r'export\s+.*\.env',
    # File copy/link to sensitive files (bypass attempts)
    r'\bcp\s+[^\s]*(' + '|'.join(SENSITIVE_BASENAMES) + r')',
    r'\bln\s+[^\s]*(' + '|'.join(SENSITIVE_BASENAMES) + r')',
    r'\bmv\s+[^\s]*(' + '|'.join(SENSITIVE_BASENAMES) + r')',
]

# Build patterns for each file-reading command + sensitive basename
for cmd in FILE_READ_COMMANDS:
    for basename in SENSITIVE_BASENAMES:
        # Match: cmd ... basename (with optional flags/paths in between)
        BASH_SENSITIVE_PATTERNS.append(rf'\b{cmd}\b[^|;]*{basename}')


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
            deny(f"{DENY_MSG}\n\nFile: {os.path.basename(path)}")

    elif hook.tool_name == "Glob":
        pattern = hook.get_input("pattern")
        if is_sensitive_file(pattern):
            deny(f"{DENY_MSG}\n\nPattern: {pattern}")

    elif hook.tool_name == "Grep":
        path = hook.get_input("path")
        if is_sensitive_file(path):
            deny(f"{DENY_MSG}\n\nPath: {path}")

    elif hook.tool_name == "Bash":
        command = hook.get_input("command")
        if is_sensitive_bash(command):
            deny(f"{DENY_MSG}\n\nCommand blocked.")

    pass_through()


if __name__ == "__main__":
    main()
