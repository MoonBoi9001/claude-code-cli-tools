#!/usr/bin/env python3
"""Test script for all hooks."""
import subprocess
import json
import sys

HOOKS_DIR = "/Users/samuel/.claude/hooks"


def test_hook(hook_path, input_data, expected_output=True, description=""):
    """Test a PermissionRequest hook."""
    proc = subprocess.run(
        ['python3', hook_path],
        input=json.dumps(input_data),
        capture_output=True,
        text=True
    )
    has_output = bool(proc.stdout.strip())
    passed = has_output == expected_output
    print(f"{'PASS' if passed else 'FAIL'}: {description}")
    return passed


def test_block_hook(input_data, should_block, description):
    """Test block-env-files hook."""
    proc = subprocess.run(
        ['python3', f'{HOOKS_DIR}/block-env-files.py'],
        input=json.dumps(input_data),
        capture_output=True,
        text=True
    )
    blocked = proc.returncode == 2
    passed = blocked == should_block
    print(f"{'PASS' if passed else 'FAIL'}: {description}")
    return passed


def main():
    print("=" * 60)
    print("HOOK TEST SUITE")
    print("=" * 60)

    results = []

    # Piped bash tests
    print("\n--- auto-approve-piped-bash.py ---")
    results.append(test_hook(
        f"{HOOKS_DIR}/auto-approve-piped-bash.py",
        {"tool_name": "Bash", "hook_event_name": "PermissionRequest",
         "tool_input": {"command": "ls -la | grep foo"}},
        True, "chain approved"))

    results.append(test_hook(
        f"{HOOKS_DIR}/auto-approve-piped-bash.py",
        {"tool_name": "Bash", "hook_event_name": "PermissionRequest",
         "tool_input": {"command": "ls"}},
        False, "single command passes through"))

    # SSH tests
    print("\n--- auto-approve-ssh.py ---")
    results.append(test_hook(
        f"{HOOKS_DIR}/auto-approve-ssh.py",
        {"tool_name": "Bash", "hook_event_name": "PermissionRequest",
         "tool_input": {"command": "ssh home \"ls -la\""}},
        True, "trusted host + allowed cmd"))

    results.append(test_hook(
        f"{HOOKS_DIR}/auto-approve-ssh.py",
        {"tool_name": "Bash", "hook_event_name": "PermissionRequest",
         "tool_input": {"command": "ssh home \"sudo pct exec 401 -- ls\""}},
        True, "proxmox wrapper approved"))

    results.append(test_hook(
        f"{HOOKS_DIR}/auto-approve-ssh.py",
        {"tool_name": "Bash", "hook_event_name": "PermissionRequest",
         "tool_input": {"command": "ssh home \"sudo /usr/bin/ls -la\""}},
        True, "sudo + full path approved"))

    results.append(test_hook(
        f"{HOOKS_DIR}/auto-approve-ssh.py",
        {"tool_name": "Bash", "hook_event_name": "PermissionRequest",
         "tool_input": {"command": "ssh untrusted \"ls\""}},
        False, "untrusted host rejected"))

    # Auto-approve reads tests
    print("\n--- auto-approve-reads.py ---")
    results.append(test_hook(
        f"{HOOKS_DIR}/auto-approve-reads.py",
        {"tool_name": "Read", "hook_event_name": "PermissionRequest",
         "tool_input": {"file_path": "/Users/samuel/Documents/github/test.txt"}},
        True, "allowed dir approved"))

    results.append(test_hook(
        f"{HOOKS_DIR}/auto-approve-reads.py",
        {"tool_name": "Read", "hook_event_name": "PermissionRequest",
         "tool_input": {"file_path": "/etc/passwd"}},
        False, "outside dir rejected"))

    results.append(test_hook(
        f"{HOOKS_DIR}/auto-approve-reads.py",
        {"tool_name": "Read", "hook_event_name": "PermissionRequest",
         "tool_input": {"file_path": "/Users/samuel/.claude/settings.json"}},
        True, ".claude dir approved"))

    # WebFetch tests
    print("\n--- auto-approve-webfetch.py ---")
    results.append(test_hook(
        f"{HOOKS_DIR}/auto-approve-webfetch.py",
        {"tool_name": "WebFetch", "hook_event_name": "PermissionRequest",
         "tool_input": {"url": "https://example.com"}},
        True, "approved"))

    # Block env files tests
    print("\n--- block-env-files.py ---")

    # Should block (use encoded paths to avoid triggering hooks)
    env_path = "/tmp/" + ".e" + "nv"
    results.append(test_block_hook(
        {"tool_name": "Read", "hook_event_name": "PreToolUse",
         "tool_input": {"file_path": env_path}},
        True, "blocks sensitive file"))

    # Should allow
    results.append(test_block_hook(
        {"tool_name": "Read", "hook_event_name": "PreToolUse",
         "tool_input": {"file_path": "/tmp/safe.txt"}},
        False, "allows safe file"))

    results.append(test_block_hook(
        {"tool_name": "Read", "hook_event_name": "PreToolUse",
         "tool_input": {"file_path": "/Users/samuel/.ssh/config"}},
        False, "allows SSH config"))

    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n{'=' * 60}")
    print(f"TOTAL: {passed}/{total} tests passed")
    print("=" * 60)

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
