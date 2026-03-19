#!/usr/bin/env python3
"""
Stop hook: detect effort level changes from /effort and /model commands
in the session JSONL, and write to ~/.claude/effort_level for the statusline.

Sources detected (most recent wins):
  - /effort <level> commands via <command-args> tags
  - /model output "with <level> effort" via <local-command-stdout> tags
"""

import json
import os
import re
import sys

EFFORT_FILE = os.path.expanduser("~/.claude/effort_level")
VALID_LEVELS = {"low", "medium", "high", "max"}

# /effort command: <command-args>low</command-args>
EFFORT_CMD_RE = re.compile(
    r"<command-name>/effort</command-name>.*?"
    r"<command-args>\s*(low|medium|high|max)\s*</command-args>",
    re.DOTALL,
)

# Strip ANSI escape sequences (both real ESC bytes and literal \x1b strings)
ANSI_RE = re.compile(r"(?:\\x1b|\x1b)\[\d*(?:;\d*)*m")

# After ANSI stripping: "with max effort"
MODEL_EFFORT_RE = re.compile(
    r"with\s+(low|medium|high|max)\s+effort",
)


def tail_bytes(filepath, nbytes=262144):
    """Read the last nbytes of a file and return as lines."""
    try:
        with open(filepath, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            chunk = min(size, nbytes)
            f.seek(size - chunk)
            data = f.read().decode("utf-8", errors="replace")
            return data.splitlines()
    except (OSError, ValueError):
        return []


def find_effort(lines):
    """
    Search backwards through JSONL lines for the most recent effort change.
    Only checks user-type messages with string content.
    """
    for raw_line in reversed(lines):
        try:
            entry = json.loads(raw_line)
        except (json.JSONDecodeError, ValueError):
            continue

        if entry.get("type") != "user":
            continue

        msg = entry.get("message", "")
        # Messages can be strings, dicts with "content", or lists (tool results)
        if isinstance(msg, dict):
            msg = msg.get("content", "")
        if not isinstance(msg, str):
            continue

        # /effort command
        if "command-name" in msg and "/effort" in msg:
            m = EFFORT_CMD_RE.search(msg)
            if m:
                return m.group(1)

        # /model stdout with effort level - strip ANSI then match
        if "local-command-stdout" in msg and "effort" in msg:
            clean = ANSI_RE.sub("", msg)
            m = MODEL_EFFORT_RE.search(clean)
            if m:
                return m.group(1)

    return None


def get_settings_effort():
    """Read default effort level from settings.json."""
    settings_path = os.path.expanduser("~/.claude/settings.json")
    try:
        with open(settings_path) as f:
            settings = json.load(f)
        level = settings.get("effortLevel", "")
        return level if level in VALID_LEVELS else None
    except (OSError, json.JSONDecodeError):
        return None


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    transcript = data.get("transcript_path", "")
    if not transcript or not os.path.isfile(transcript):
        return

    lines = tail_bytes(transcript)
    effort = find_effort(lines)

    # Fall back to settings.json default when no explicit command found
    if not effort:
        effort = get_settings_effort()

    if effort:
        try:
            with open(EFFORT_FILE) as f:
                if f.read().strip() == effort:
                    return
        except FileNotFoundError:
            pass
        with open(EFFORT_FILE, "w") as f:
            f.write(effort + "\n")


if __name__ == "__main__":
    main()
