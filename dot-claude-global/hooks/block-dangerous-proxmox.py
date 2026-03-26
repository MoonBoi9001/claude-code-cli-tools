#!/usr/bin/env python3
"""
PreToolUse hook to block dangerous Proxmox commands that don't allow graceful shutdown.

Blocks:
  - pct stop: Forcefully terminates LXC container (like pulling power cord)
  - qm stop: Forcefully terminates VM (like pulling power cord)

Safe alternatives:
  - pct shutdown: Sends shutdown signal, allows graceful termination
  - qm shutdown: Sends ACPI shutdown, allows graceful termination
"""
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).parent))

from hook_utils import parse_hook_input, deny, pass_through


DANGEROUS_PATTERNS = [
    (r'\bpct\s+stop\b', "Use 'pct shutdown' for graceful container shutdown"),
    (r'\bqm\s+stop\b', "Use 'qm shutdown' for graceful VM shutdown"),
    (r'\bpoweroff\b', "Host poweroff blocked - can cause data corruption"),
    (r'\bshutdown\s+-h\b', "Host shutdown blocked - can cause data corruption"),
    (r'\bshutdown\s+now\b', "Host shutdown blocked - can cause data corruption"),
    (r'\binit\s+0\b', "Host poweroff blocked - can cause data corruption"),
    (r'\bsystemctl\s+poweroff\b', "Host poweroff blocked - can cause data corruption"),
    (r'\breboot\b', "Host reboot blocked - can cause data corruption"),
    (r'\bdocker[-\s]compose\s+down\b', "Use 'docker compose stop' to preserve containers and volumes"),
]


def check_dangerous_command(command: str) -> tuple[bool, str]:
    """Check if command contains dangerous Proxmox operations."""
    if not command:
        return False, ""

    for pattern, suggestion in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True, suggestion

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
    dangerous, suggestion = check_dangerous_command(command)

    if dangerous:
        deny(f"Blocked: Forceful stop can corrupt data. {suggestion}")

    pass_through()


if __name__ == "__main__":
    main()
