#!/usr/bin/env python3
"""Auto-approve all WebFetch tool requests."""
from datetime import datetime
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent))

from hook_utils import parse_hook_input, approve, pass_through

LOG_FILE = Path.home() / ".claude" / "logs" / "webfetch-hook.log"


def log(message: str, data: dict = None):
    """Append timestamped log entry."""
    timestamp = datetime.now().isoformat()
    entry = f"[{timestamp}] {message}"
    if data:
        entry += f"\n  {json.dumps(data, indent=2, default=str)}"
    entry += "\n"
    with open(LOG_FILE, "a") as f:
        f.write(entry)


def main():
    log("Hook invoked")

    hook = parse_hook_input()
    if not hook:
        log("Failed to parse input - passing through")
        pass_through()

    log("Parsed input", {
        "tool_name": hook.tool_name,
        "hook_event": hook.hook_event,
        "is_permission_request": hook.is_permission_request,
        "tool_input": hook.tool_input,
    })

    if hook.is_permission_request and hook.tool_name == "WebFetch":
        log("Approving WebFetch request")
        approve()

    log("Not a WebFetch PermissionRequest - passing through")
    pass_through()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log("Exception occurred", {"error": str(e), "type": type(e).__name__})
        raise
