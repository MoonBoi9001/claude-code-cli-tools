#!/usr/bin/env python3
"""
Stop hook: block Claude from stopping when its response dismisses errors
as "pre-existing" without fixing or flagging them.

Reads the session transcript to find the last assistant message and checks
for the word "pre-existing" (or "preexisting"). If found, blocks the stop
and instructs Claude to address the errors.

Uses stop_hook_active to prevent infinite loops — if this hook already
triggered a continuation, allow the next stop unconditionally.
"""

import json
import os
import re
import sys

PATTERN = re.compile(r"pre-?existing", re.IGNORECASE)

BLOCK_REASON = (
    'Your response contains "pre-existing" — this likely means you dismissed '
    "errors without addressing them. Per project rules: if the error is small "
    "(lint, unused import, type hint, sort order), fix it now. If larger, flag "
    "each one explicitly to the user. Do not move on without either fixing or "
    "flagging."
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


def find_last_assistant_message(lines):
    """
    Walk backwards through JSONL lines to find the last assistant message
    with string content.
    """
    for raw_line in reversed(lines):
        try:
            entry = json.loads(raw_line)
        except (json.JSONDecodeError, ValueError):
            continue

        if entry.get("type") != "assistant":
            continue

        msg = entry.get("message", "")
        if isinstance(msg, dict):
            content = msg.get("content", "")
            if isinstance(content, list):
                # content blocks — extract text from text blocks
                parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        parts.append(block.get("text", ""))
                msg = " ".join(parts)
            else:
                msg = content
        if isinstance(msg, str) and msg.strip():
            return msg

    return None


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    if data.get("stop_hook_active", False):
        return

    transcript = data.get("transcript_path", "")
    if not transcript or not os.path.isfile(transcript):
        return

    lines = tail_bytes(transcript)
    message = find_last_assistant_message(lines)
    if not message:
        return

    if PATTERN.search(message):
        output = {"decision": "block", "reason": BLOCK_REASON}
        print(json.dumps(output))


if __name__ == "__main__":
    main()
