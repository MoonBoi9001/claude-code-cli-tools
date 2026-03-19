#!/usr/bin/env python3
"""Tests for block-push-others-branch.py hook."""

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest

HOOKS_DIR = str(Path(__file__).resolve().parent)
HOOK_PATH = str(Path(HOOKS_DIR) / "block-push-others-branch.py")


def run_hook(input_data, env=None):
    """Run the hook as a subprocess, returning the CompletedProcess."""
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    return subprocess.run(
        ["python3", HOOK_PATH],
        input=json.dumps(input_data) if isinstance(input_data, dict) else input_data,
        capture_output=True,
        text=True,
        env=run_env,
    )


def make_input(command="git push", tool_name="Bash", event="PreToolUse"):
    return {
        "tool_name": tool_name,
        "hook_event_name": event,
        "tool_input": {"command": command},
    }


class TestPassThrough(unittest.TestCase):
    """Cases that should always exit 0 (pass through) without calling git/gh."""

    def test_non_bash_tool(self):
        proc = run_hook(
            {
                "tool_name": "Write",
                "hook_event_name": "PreToolUse",
                "tool_input": {"file_path": "/tmp/test"},
            }
        )
        self.assertEqual(proc.returncode, 0)

    def test_wrong_event_type(self):
        proc = run_hook(make_input("git push", event="PostToolUse"))
        self.assertEqual(proc.returncode, 0)

    def test_non_push_command(self):
        proc = run_hook(make_input("git status"))
        self.assertEqual(proc.returncode, 0)

    def test_non_git_command(self):
        proc = run_hook(make_input("ls -la"))
        self.assertEqual(proc.returncode, 0)

    def test_empty_command(self):
        proc = run_hook(make_input(""))
        self.assertEqual(proc.returncode, 0)

    def test_invalid_json(self):
        proc = run_hook("not json")
        self.assertEqual(proc.returncode, 0)


class TestBlockingWithMocks(unittest.TestCase):
    """Tests using mock git/gh executables to verify ownership checking."""

    def setUp(self):
        self.mock_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.mock_dir, ignore_errors=True)

    def _write_script(self, name, content):
        path = os.path.join(self.mock_dir, name)
        with open(path, "w") as f:
            f.write(content)
        os.chmod(path, stat.S_IRWXU)

    def _setup_mocks(
        self,
        branch="feat/their-feature",
        remote_exists=True,
        username="samuel",
        default_branch="main",
        authors="other-user",
    ):
        ls_remote = f"abc123\trefs/heads/{branch}" if remote_exists else ""
        self._write_script(
            "git",
            f"""#!/usr/bin/env bash
if [[ "$1" == "symbolic-ref" ]]; then
    echo "{branch}"
elif [[ "$1" == "ls-remote" ]]; then
    {"echo '" + ls_remote + "'" if remote_exists else "true"}
fi
exit 0
""",
        )
        self._write_script(
            "gh",
            f"""#!/usr/bin/env bash
if [[ "$2" == "user" ]]; then
    echo "{username}"
elif [[ "$2" == *"compare"* ]]; then
    echo "{authors}"
else
    echo "{default_branch}"
fi
exit 0
""",
        )

    def _run(self, input_data=None):
        env = {"PATH": f"{self.mock_dir}:{os.environ.get('PATH', '')}"}
        return run_hook(input_data or make_input("git push"), env=env)

    # -- should block --

    def test_blocks_push_to_others_branch(self):
        self._setup_mocks(branch="feat/their-feature", authors="other-user")
        proc = self._run()
        self.assertEqual(proc.returncode, 2)
        self.assertIn("Blocked", proc.stderr)
        self.assertIn("other-user", proc.stderr)

    def test_blocks_push_in_chained_command(self):
        self._setup_mocks(branch="feat/their-feature", authors="other-user")
        proc = self._run(make_input("git add . && git commit -m 'fix' && git push"))
        self.assertEqual(proc.returncode, 2)

    def test_blocks_push_with_flags(self):
        self._setup_mocks(branch="feat/their-feature", authors="other-user")
        proc = self._run(make_input("git push -u origin feat/their-feature"))
        self.assertEqual(proc.returncode, 2)

    def test_deny_message_suggests_pr(self):
        self._setup_mocks(branch="feat/their-feature", authors="other-user")
        proc = self._run()
        self.assertIn("PR", proc.stderr)
        self.assertIn("feat/their-feature", proc.stderr)

    def test_deny_lists_branch_owner(self):
        self._setup_mocks(branch="feat/their-feature", authors="alice")
        proc = self._run()
        self.assertEqual(proc.returncode, 2)
        self.assertIn("alice", proc.stderr)

    # -- should allow --

    def test_allows_push_to_own_branch(self):
        self._setup_mocks(branch="feat/my-feature", authors="samuel")
        proc = self._run()
        self.assertEqual(proc.returncode, 0)

    def test_allows_when_user_among_multiple_authors(self):
        self._setup_mocks(
            branch="feat/collab", authors="other-user\nsamuel\nthird-user"
        )
        proc = self._run()
        self.assertEqual(proc.returncode, 0)

    def test_allows_new_branch(self):
        self._setup_mocks(branch="feat/new-feature", remote_exists=False)
        proc = self._run()
        self.assertEqual(proc.returncode, 0)

    def test_allows_shared_branches(self):
        for branch in ("main", "master", "develop", "staging", "production", "release"):
            self._setup_mocks(branch=branch, authors="other-user")
            proc = self._run()
            self.assertEqual(proc.returncode, 0, f"Should allow push to {branch}")

    def test_blocks_when_gh_user_fails(self):
        """Fails closed when gh can't determine username (e.g. network glitch)."""
        self._setup_mocks(branch="feat/their-feature", authors="other-user")
        self._write_script("gh", "#!/usr/bin/env bash\nexit 1\n")
        proc = self._run()
        self.assertEqual(proc.returncode, 2)
        self.assertIn("failed to determine your GitHub username", proc.stderr)
        self.assertIn("retry", proc.stderr)

    def test_blocks_when_compare_api_fails(self):
        """Fails closed when gh can't fetch branch authors (e.g. network glitch)."""
        self._setup_mocks(branch="feat/their-feature", authors="other-user")
        # gh succeeds for user lookup but fails for compare
        self._write_script(
            "gh",
            """#!/usr/bin/env bash
if [[ "$2" == "user" ]]; then
    echo "samuel"
    exit 0
fi
exit 1
""",
        )
        proc = self._run()
        self.assertEqual(proc.returncode, 2)
        self.assertIn("failed to fetch commit authors", proc.stderr)
        self.assertIn("retry", proc.stderr)

    def test_allows_when_remote_unreachable(self):
        """Fails open when git ls-remote fails — push will also fail."""
        self._setup_mocks(branch="feat/their-feature", authors="other-user")
        # Overwrite git mock so ls-remote fails (simulating unreachable remote)
        self._write_script(
            "git",
            """#!/usr/bin/env bash
if [[ "$1" == "symbolic-ref" ]]; then
    echo "feat/their-feature"
elif [[ "$1" == "ls-remote" ]]; then
    exit 1
fi
exit 0
""",
        )
        proc = self._run()
        self.assertEqual(proc.returncode, 0)

    def test_allows_when_no_divergent_commits(self):
        """Passes through when compare API returns no authors."""
        self._setup_mocks(branch="feat/empty-branch", authors="")
        proc = self._run()
        self.assertEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
