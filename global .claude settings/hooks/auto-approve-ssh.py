#!/usr/bin/env python3
"""
Auto-approve SSH commands to trusted hosts when remote commands match allow patterns.

Trusted hosts are read from ~/.ssh/config. Remote commands are validated against
the same settings.json patterns used for local commands, with support for
trusted wrapper patterns like 'sudo pct exec <id> --'.

Security model:
- Trusted hosts: Only hosts explicitly configured in ~/.ssh/config (no wildcards)
- Wrapper unwrapping: Proxmox pct/qm, Docker exec, bash -c are unwrapped
- Remote command validation: Inner commands must match allow patterns
- Dangerous SSH options: Blocked (ProxyCommand, LocalCommand, etc.)
- Fail-safe: Any uncertainty falls through to manual approval

WARNING: This is friction-reduction, not security. SSH crosses trust boundaries
and remote environments are opaque.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os
import shlex
import sys

sys.path.insert(0, str(Path(__file__).parent))

from hook_utils import (
    parse_hook_input, approve, pass_through,
    CommandValidator, ValidationResult
)


# =============================================================================
# SSH Configuration
# =============================================================================

DANGEROUS_SSH_OPTIONS = frozenset({
    '-o', '--option', '-F', '-S', '-W', '-J', '--jump',
})

DANGEROUS_O_VALUES = frozenset({
    'proxycommand', 'localcommand', 'permitlocalcommand',
    'proxyusefirewall', 'remotecommand',
})

SSH_OPTIONS_WITH_ARGS = frozenset({
    '-o', '-F', '-i', '-l', '-p', '-J', '-S', '-W',
    '-b', '-c', '-D', '-E', '-e', '-I', '-L', '-m',
    '-O', '-Q', '-R', '-w', '-B',
})


# =============================================================================
# SSH Config Parser
# =============================================================================

class SSHConfigParser:
    """Parses ~/.ssh/config to extract trusted host names."""

    def __init__(self, config_path: str = "~/.ssh/config"):
        self._path = os.path.expanduser(config_path)
        self._hosts: Optional[frozenset[str]] = None

    def get_trusted_hosts(self) -> frozenset[str]:
        if self._hosts is not None:
            return self._hosts

        hosts: set[str] = set()
        try:
            with open(self._path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if line.lower().startswith('host '):
                        for host in line[5:].split():
                            if not any(c in host for c in '*?!'):
                                hosts.add(host)
        except (OSError, IOError):
            pass

        self._hosts = frozenset(hosts)
        return self._hosts


# =============================================================================
# SSH Command Parser
# =============================================================================

@dataclass
class SSHCommand:
    host: str
    options: list[str]
    remote_command: str


class SSHCommandParser:
    """Parses SSH commands to extract host, options, and remote command."""

    def parse(self, command: str) -> Optional[SSHCommand]:
        try:
            parts = shlex.split(command)
        except ValueError:
            return None

        if not parts or parts[0] != 'ssh':
            return None

        options: list[str] = []
        host: Optional[str] = None
        remote_cmd_start: Optional[int] = None

        i = 1
        while i < len(parts):
            part = parts[i]
            if part.startswith('-'):
                options.append(part)
                if part in SSH_OPTIONS_WITH_ARGS and i + 1 < len(parts):
                    i += 1
                    options.append(parts[i])
                i += 1
                continue
            host = part
            remote_cmd_start = i + 1
            break

        if host is None:
            return None

        # Strip username from user@host syntax
        if '@' in host:
            host = host.split('@', 1)[1]

        remote_cmd = ''
        if remote_cmd_start and remote_cmd_start < len(parts):
            remote_cmd = ' '.join(parts[remote_cmd_start:])

        return SSHCommand(host=host, options=options, remote_command=remote_cmd)

    def has_dangerous_options(self, options: list[str]) -> bool:
        for i, opt in enumerate(options):
            if opt in DANGEROUS_SSH_OPTIONS:
                return True
            if opt == '-o' and i + 1 < len(options):
                o_value = options[i + 1].lower()
                if any(o_value.startswith(d) for d in DANGEROUS_O_VALUES):
                    return True
        return False


# =============================================================================
# SSH Approver
# =============================================================================

class SSHApprover:
    """Orchestrates SSH command validation."""

    def __init__(self):
        self._ssh_config = SSHConfigParser()
        self._ssh_parser = SSHCommandParser()
        self._cmd_validator = CommandValidator()

    def should_approve(self, command: str) -> tuple[bool, str]:
        parsed = self._ssh_parser.parse(command)
        if parsed is None:
            return False, "Not a valid SSH command"

        if parsed.host not in self._ssh_config.get_trusted_hosts():
            return False, f"Host '{parsed.host}' not in ~/.ssh/config"

        if self._ssh_parser.has_dangerous_options(parsed.options):
            return False, "Dangerous SSH options detected"

        if not parsed.remote_command:
            return True, f"SSH session to trusted host '{parsed.host}'"

        result = self._cmd_validator.validate(parsed.remote_command)
        return result.approved, result.reason


# =============================================================================
# Main
# =============================================================================

def main():
    hook = parse_hook_input()
    if not hook:
        pass_through()

    if not hook.is_permission_request or hook.tool_name != "Bash":
        pass_through()

    command = hook.get_input("command")
    if not command.strip().startswith('ssh '):
        pass_through()

    approved, _ = SSHApprover().should_approve(command)
    if approved:
        approve()

    pass_through()


if __name__ == "__main__":
    main()
