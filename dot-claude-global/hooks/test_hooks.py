#!/usr/bin/env python3
"""Test script for all hooks."""

import subprocess
import json
import sys

HOOKS_DIR = "/Users/samuel/.claude/hooks"


def test_hook(hook_path, input_data, expected_output=True, description=""):
    """Test a PermissionRequest hook."""
    proc = subprocess.run(
        ["python3", hook_path],
        input=json.dumps(input_data),
        capture_output=True,
        text=True,
    )
    has_output = bool(proc.stdout.strip())
    passed = has_output == expected_output
    print(f"{'PASS' if passed else 'FAIL'}: {description}")
    return passed


def test_pretool_hook(hook_name, input_data, should_block, description):
    """Test a PreToolUse hook that blocks (exit 2) or passes through."""
    proc = subprocess.run(
        ["python3", f"{HOOKS_DIR}/{hook_name}"],
        input=json.dumps(input_data),
        capture_output=True,
        text=True,
    )
    blocked = proc.returncode == 2
    passed = blocked == should_block
    print(f"{'PASS' if passed else 'FAIL'}: {description}")
    return passed


def test_block_hook(input_data, should_block, description):
    """Test block-env-files hook."""
    return test_pretool_hook(
        "block-env-files.py", input_data, should_block, description
    )


def main():
    print("=" * 60)
    print("HOOK TEST SUITE")
    print("=" * 60)

    results = []

    # Piped bash tests
    print("\n--- auto-approve-piped-bash.py ---")
    results.append(
        test_hook(
            f"{HOOKS_DIR}/auto-approve-piped-bash.py",
            {
                "tool_name": "Bash",
                "hook_event_name": "PermissionRequest",
                "tool_input": {"command": "ls -la | grep foo"},
            },
            True,
            "pipe chain approved",
        )
    )

    results.append(
        test_hook(
            f"{HOOKS_DIR}/auto-approve-piped-bash.py",
            {
                "tool_name": "Bash",
                "hook_event_name": "PermissionRequest",
                "tool_input": {"command": "git status && git diff"},
            },
            True,
            "&& chain approved",
        )
    )

    results.append(
        test_hook(
            f"{HOOKS_DIR}/auto-approve-piped-bash.py",
            {
                "tool_name": "Bash",
                "hook_event_name": "PermissionRequest",
                "tool_input": {"command": "ls"},
            },
            True,
            "allowed single command approved",
        )
    )

    results.append(
        test_hook(
            f"{HOOKS_DIR}/auto-approve-piped-bash.py",
            {
                "tool_name": "Bash",
                "hook_event_name": "PermissionRequest",
                "tool_input": {"command": "rm -rf /tmp/stuff"},
            },
            False,
            "disallowed single command passes through",
        )
    )

    results.append(
        test_hook(
            f"{HOOKS_DIR}/auto-approve-piped-bash.py",
            {
                "tool_name": "Bash",
                "hook_event_name": "PermissionRequest",
                "tool_input": {"command": "ls -la | rm -rf /tmp/stuff"},
            },
            False,
            "pipe with disallowed command passes through",
        )
    )

    # SSH tests
    print("\n--- auto-approve-ssh.py ---")
    results.append(
        test_hook(
            f"{HOOKS_DIR}/auto-approve-ssh.py",
            {
                "tool_name": "Bash",
                "hook_event_name": "PermissionRequest",
                "tool_input": {"command": 'ssh home "ls -la"'},
            },
            True,
            "trusted host + allowed cmd",
        )
    )

    results.append(
        test_hook(
            f"{HOOKS_DIR}/auto-approve-ssh.py",
            {
                "tool_name": "Bash",
                "hook_event_name": "PermissionRequest",
                "tool_input": {"command": 'ssh home "sudo pct exec 401 -- ls"'},
            },
            True,
            "proxmox wrapper approved",
        )
    )

    results.append(
        test_hook(
            f"{HOOKS_DIR}/auto-approve-ssh.py",
            {
                "tool_name": "Bash",
                "hook_event_name": "PermissionRequest",
                "tool_input": {"command": 'ssh home "sudo /usr/bin/ls -la"'},
            },
            True,
            "sudo + full path approved",
        )
    )

    results.append(
        test_hook(
            f"{HOOKS_DIR}/auto-approve-ssh.py",
            {
                "tool_name": "Bash",
                "hook_event_name": "PermissionRequest",
                "tool_input": {"command": 'ssh untrusted "ls"'},
            },
            False,
            "untrusted host rejected",
        )
    )

    # Auto-approve reads tests
    print("\n--- auto-approve-reads.py ---")
    results.append(
        test_hook(
            f"{HOOKS_DIR}/auto-approve-reads.py",
            {
                "tool_name": "Read",
                "hook_event_name": "PermissionRequest",
                "tool_input": {"file_path": "/Users/samuel/Documents/github/test.txt"},
            },
            True,
            "allowed dir approved",
        )
    )

    results.append(
        test_hook(
            f"{HOOKS_DIR}/auto-approve-reads.py",
            {
                "tool_name": "Read",
                "hook_event_name": "PermissionRequest",
                "tool_input": {"file_path": "/etc/passwd"},
            },
            False,
            "outside dir rejected",
        )
    )

    results.append(
        test_hook(
            f"{HOOKS_DIR}/auto-approve-reads.py",
            {
                "tool_name": "Read",
                "hook_event_name": "PermissionRequest",
                "tool_input": {"file_path": "/Users/samuel/.claude/settings.json"},
            },
            True,
            ".claude dir approved",
        )
    )

    # WebFetch tests
    print("\n--- auto-approve-webfetch.py ---")
    results.append(
        test_hook(
            f"{HOOKS_DIR}/auto-approve-webfetch.py",
            {
                "tool_name": "WebFetch",
                "hook_event_name": "PermissionRequest",
                "tool_input": {"url": "https://example.com"},
            },
            True,
            "approved",
        )
    )

    # Block env files tests
    print("\n--- block-env-files.py ---")

    # Should block (use encoded paths to avoid triggering hooks)
    env_path = "/tmp/" + ".e" + "nv"
    results.append(
        test_block_hook(
            {
                "tool_name": "Read",
                "hook_event_name": "PreToolUse",
                "tool_input": {"file_path": env_path},
            },
            True,
            "blocks sensitive file",
        )
    )

    # Should allow
    results.append(
        test_block_hook(
            {
                "tool_name": "Read",
                "hook_event_name": "PreToolUse",
                "tool_input": {"file_path": "/tmp/safe.txt"},
            },
            False,
            "allows safe file",
        )
    )

    results.append(
        test_block_hook(
            {
                "tool_name": "Read",
                "hook_event_name": "PreToolUse",
                "tool_input": {"file_path": "/Users/samuel/.ssh/config"},
            },
            False,
            "allows SSH config",
        )
    )

    # .environment must not be blocked (regression: \.env matched as substring)
    results.append(
        test_block_hook(
            {
                "tool_name": "Read",
                "hook_event_name": "PreToolUse",
                "tool_input": {"file_path": "/tmp/project/.environment"},
            },
            False,
            "allows .environment file",
        )
    )

    env_local = "/tmp/" + ".e" + "nv.local"
    results.append(
        test_block_hook(
            {
                "tool_name": "Read",
                "hook_event_name": "PreToolUse",
                "tool_input": {"file_path": env_local},
            },
            True,
            "blocks .env.local",
        )
    )

    # Bash: writing to .environment must not be blocked
    results.append(
        test_block_hook(
            {
                "tool_name": "Bash",
                "hook_event_name": "PreToolUse",
                "tool_input": {"command": "echo FOO=bar > /tmp/.environment"},
            },
            False,
            "allows bash write to .environment",
        )
    )

    # Bash: cat .env must be blocked
    env_cmd = "cat /tmp/" + ".e" + "nv"
    results.append(
        test_block_hook(
            {
                "tool_name": "Bash",
                "hook_event_name": "PreToolUse",
                "tool_input": {"command": env_cmd},
            },
            True,
            "blocks bash cat .env",
        )
    )

    # Bash: source .env blocked, source .environment allowed
    results.append(
        test_block_hook(
            {
                "tool_name": "Bash",
                "hook_event_name": "PreToolUse",
                "tool_input": {"command": "source .environment"},
            },
            False,
            "allows bash source .environment",
        )
    )

    source_env = "source ." + "en" + "v"
    results.append(
        test_block_hook(
            {
                "tool_name": "Bash",
                "hook_event_name": "PreToolUse",
                "tool_input": {"command": source_env},
            },
            True,
            "blocks bash source .env",
        )
    )

    # .env.example should be allowed (safe template)
    env_example = "/tmp/." + "en" + "v.example"
    results.append(
        test_block_hook(
            {
                "tool_name": "Read",
                "hook_event_name": "PreToolUse",
                "tool_input": {"file_path": env_example},
            },
            False,
            "allows .env.example (safe template)",
        )
    )

    # SSH private key blocked, config allowed
    results.append(
        test_block_hook(
            {
                "tool_name": "Read",
                "hook_event_name": "PreToolUse",
                "tool_input": {"file_path": "/Users/samuel/.ssh/id_ed25519"},
            },
            True,
            "blocks SSH private key",
        )
    )

    # =========================================================================
    # block-force-push.py
    # =========================================================================
    print("\n--- block-force-push.py ---")

    def force_push_test(command, should_block, description):
        return test_pretool_hook(
            "block-force-push.py",
            {
                "tool_name": "Bash",
                "hook_event_name": "PreToolUse",
                "tool_input": {"command": command},
            },
            should_block,
            description,
        )

    results.append(force_push_test("git push --force", True, "blocks --force"))

    results.append(force_push_test("git push -f", True, "blocks -f"))

    results.append(
        force_push_test(
            "git push origin main --force", True, "blocks --force with remote/branch"
        )
    )

    results.append(
        force_push_test(
            "git push --force-with-lease", False, "allows --force-with-lease"
        )
    )

    results.append(force_push_test("git push origin main", False, "allows normal push"))

    results.append(
        force_push_test("git push -u origin my-branch", False, "allows push with -u")
    )

    # =========================================================================
    # block-dangerous-proxmox.py
    # =========================================================================
    print("\n--- block-dangerous-proxmox.py ---")

    def proxmox_test(command, should_block, description):
        return test_pretool_hook(
            "block-dangerous-proxmox.py",
            {
                "tool_name": "Bash",
                "hook_event_name": "PreToolUse",
                "tool_input": {"command": command},
            },
            should_block,
            description,
        )

    results.append(proxmox_test("pct stop 100", True, "blocks pct stop"))

    results.append(proxmox_test("qm stop 200", True, "blocks qm stop"))

    results.append(proxmox_test("pct shutdown 100", False, "allows pct shutdown"))

    results.append(proxmox_test("qm shutdown 200", False, "allows qm shutdown"))

    results.append(
        proxmox_test("systemctl poweroff", True, "blocks systemctl poweroff")
    )

    results.append(proxmox_test("reboot", True, "blocks reboot"))

    results.append(
        proxmox_test("docker compose down", True, "blocks docker compose down")
    )

    results.append(
        proxmox_test("docker compose stop", False, "allows docker compose stop")
    )

    # =========================================================================
    # auto-approve-edits.py
    # =========================================================================
    print("\n--- auto-approve-edits.py ---")

    results.append(
        test_hook(
            f"{HOOKS_DIR}/auto-approve-edits.py",
            {
                "tool_name": "Edit",
                "hook_event_name": "PermissionRequest",
                "tool_input": {"file_path": "/Users/samuel/Documents/github/test.py"},
            },
            True,
            "approves edit in allowed dir",
        )
    )

    results.append(
        test_hook(
            f"{HOOKS_DIR}/auto-approve-edits.py",
            {
                "tool_name": "Write",
                "hook_event_name": "PermissionRequest",
                "tool_input": {"file_path": "/Users/samuel/Documents/github/new.py"},
            },
            True,
            "approves write in allowed dir",
        )
    )

    results.append(
        test_hook(
            f"{HOOKS_DIR}/auto-approve-edits.py",
            {
                "tool_name": "Edit",
                "hook_event_name": "PermissionRequest",
                "tool_input": {"file_path": "/etc/hosts"},
            },
            False,
            "rejects edit outside allowed dir",
        )
    )

    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n{'=' * 60}")
    print(f"TOTAL: {passed}/{total} tests passed")
    print("=" * 60)

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
