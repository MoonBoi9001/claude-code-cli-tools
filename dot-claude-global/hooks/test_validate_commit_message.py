#!/usr/bin/env python3
"""Tests for validate-commit-message.py hook.

Pinned focus: the hook must recognise `git commit` even when global flags
like `-C <path>`, `-c <name>=<value>`, or `--no-pager` sit between `git`
and `commit`. A regression where the recognition regex required the
literal substring `git commit` allowed every commit issued via
`git -C /path commit ...` to silently bypass validation.
"""

import json
import subprocess
import unittest
from pathlib import Path

HOOK_PATH = str(Path(__file__).resolve().parent / "validate-commit-message.py")


def run_hook(command: str) -> subprocess.CompletedProcess:
    """Invoke the hook with a Bash PreToolUse payload and given command."""
    payload = {
        "tool_name": "Bash",
        "hook_event_name": "PreToolUse",
        "tool_input": {"command": command},
    }
    return subprocess.run(
        ["python3", HOOK_PATH],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


# A 6-line body — three rules' worth of content above the 4-line cap.
# Used wherever a test wants to confirm the hook caught the body length.
SIX_LINE_BAD_BODY = (
    "fix(scope): too long\n\nLine 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6"
)


class TestGitCommitDetection(unittest.TestCase):
    """The hook must recognise every shape of `git commit` it gets called on."""

    def test_plain_git_commit_is_recognised(self):
        proc = run_hook(f'git commit -m "{SIX_LINE_BAD_BODY}"')
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("Body has 6 non-empty lines", proc.stderr)

    def test_git_dash_C_is_recognised(self):
        proc = run_hook(f'git -C /tmp/repo commit -m "{SIX_LINE_BAD_BODY}"')
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("Body has 6 non-empty lines", proc.stderr)

    def test_git_dash_C_absolute_path_is_recognised(self):
        proc = run_hook(
            f'git -C /Users/sam/Documents/github/repo commit -m "{SIX_LINE_BAD_BODY}"'
        )
        self.assertEqual(proc.returncode, 2, proc.stderr)

    def test_git_dash_c_config_is_recognised(self):
        proc = run_hook(f'git -c user.name=foo commit -m "{SIX_LINE_BAD_BODY}"')
        self.assertEqual(proc.returncode, 2, proc.stderr)

    def test_git_no_pager_is_recognised(self):
        proc = run_hook(f'git --no-pager commit -m "{SIX_LINE_BAD_BODY}"')
        self.assertEqual(proc.returncode, 2, proc.stderr)

    def test_git_long_flag_with_equals_is_recognised(self):
        proc = run_hook(f'git --git-dir=/tmp/.git commit -m "{SIX_LINE_BAD_BODY}"')
        self.assertEqual(proc.returncode, 2, proc.stderr)

    def test_git_multiple_global_flags_recognised(self):
        proc = run_hook(
            f'git -C /tmp --no-pager -c user.email=x commit -m "{SIX_LINE_BAD_BODY}"'
        )
        self.assertEqual(proc.returncode, 2, proc.stderr)

    def test_chained_with_double_ampersand_recognised(self):
        # `git add ... && git -C /path commit ...` — the form the agent
        # actually uses. The hook splits on newline only, so the whole
        # invocation is one line; the regex must still find `commit`.
        proc = run_hook(
            f'git add file && git -C /tmp/repo commit -m "{SIX_LINE_BAD_BODY}"'
        )
        self.assertEqual(proc.returncode, 2, proc.stderr)


class TestHeredocPatterns(unittest.TestCase):
    """Multi-line commands with heredocs.

    The agent's standard pattern for long commit messages is:
        cat > /tmp/msg.txt <<EOF
        <message>
        EOF
        git commit -F /tmp/msg.txt

    Line 1 is the heredoc opener, not `git commit`. The earlier hook
    inspected only line 1 and silently passed through every commit issued
    this way. The new hook strips heredoc bodies and searches the rest.
    """

    def test_heredoc_to_file_then_commit_F_is_recognised(self):
        # Real-world bypass: heredoc writes the message to disk, git
        # commit reads it back. `git commit` lives on line 5.
        bad = "fix(scope): too long\n\nLine 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6"
        cmd = f"cat > /tmp/msg.txt <<'EOF'\n{bad}\nEOF\ngit commit -F /tmp/msg.txt"
        proc = run_hook(cmd)
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("Body has 6 non-empty lines", proc.stderr)

    def test_setup_chain_then_commit_on_later_line_recognised(self):
        # `git status` first, real commit on line 2. No heredoc.
        proc = run_hook(f'git status\ngit commit -m "{SIX_LINE_BAD_BODY}"')
        self.assertEqual(proc.returncode, 2, proc.stderr)

    def test_git_commit_inside_heredoc_body_passes_through(self):
        # The defense the original line-1 restriction was protecting:
        # writing a shell script that contains the literal `git commit`
        # must not trigger validation, because no commit is happening.
        cmd = (
            "cat > /tmp/script.sh <<'EOF'\n"
            'git commit -m "this is a test fixture, not a real commit"\n'
            "EOF\n"
            "echo wrote script"
        )
        proc = run_hook(cmd)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_heredoc_substitution_form_message_is_extracted(self):
        # The CLAUDE.md canonical pattern: heredoc inside -m "$(cat <<EOF
        # ... EOF)". The heredoc IS the message; extraction must find it.
        cmd = (
            "git commit -m \"$(cat <<'EOF'\n"
            "fix(scope): too long\n\n"
            "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\n"
            "EOF\n"
            ')"'
        )
        proc = run_hook(cmd)
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("Body has 6 non-empty lines", proc.stderr)

    def test_indented_heredoc_dash_form_recognised(self):
        # `<<-EOF` strips leading tabs; still a heredoc.
        bad = "fix(scope): too long\n\nLine 1\nLine 2\nLine 3\nLine 4\nLine 5"
        cmd = f"cat > /tmp/msg.txt <<-EOF\n{bad}\nEOF\ngit commit -F /tmp/msg.txt"
        proc = run_hook(cmd)
        self.assertEqual(proc.returncode, 2, proc.stderr)


class TestNonCommitInvocations(unittest.TestCase):
    """Anything that isn't `git commit` must pass through (exit 0)."""

    def test_git_status(self):
        proc = run_hook("git status")
        self.assertEqual(proc.returncode, 0)

    def test_git_dash_C_checkout(self):
        proc = run_hook("git -C /tmp/repo checkout main")
        self.assertEqual(proc.returncode, 0)

    def test_git_dash_C_log(self):
        proc = run_hook("git -C /tmp/repo log --oneline")
        self.assertEqual(proc.returncode, 0)

    def test_non_git_command(self):
        proc = run_hook("ls -la")
        self.assertEqual(proc.returncode, 0)

    def test_amend_no_edit_passes_through(self):
        # Reusing the prior message — nothing to validate.
        proc = run_hook("git commit --amend --no-edit")
        self.assertEqual(proc.returncode, 0)

    def test_amend_no_edit_with_dash_C_passes_through(self):
        proc = run_hook("git -C /tmp/repo commit --amend --no-edit")
        self.assertEqual(proc.returncode, 0)


class TestValidMessages(unittest.TestCase):
    """Well-formed messages must pass."""

    def test_minimal_valid_message(self):
        proc = run_hook('git commit -m "fix(scope): do the thing"')
        self.assertEqual(proc.returncode, 0)

    def test_valid_message_with_dash_C(self):
        proc = run_hook('git -C /tmp/repo commit -m "fix(scope): do the thing"')
        self.assertEqual(proc.returncode, 0)

    def test_valid_message_with_4_line_body(self):
        body = "fix(scope): do the thing\n\nLine 1\nLine 2\nLine 3\nLine 4"
        proc = run_hook(f'git -C /tmp/repo commit -m "{body}"')
        self.assertEqual(proc.returncode, 0)


class TestRejectionMessageQuality(unittest.TestCase):
    """The rejection block must include CLAUDE.md reminders."""

    def test_reminders_block_present_on_failure(self):
        proc = run_hook(f'git -C /tmp/repo commit -m "{SIX_LINE_BAD_BODY}"')
        self.assertEqual(proc.returncode, 2)
        self.assertIn("Reminders for the rewrite", proc.stderr)
        self.assertIn("Body stands on its own", proc.stderr)
        self.assertIn("imperative verb", proc.stderr)


if __name__ == "__main__":
    unittest.main()
