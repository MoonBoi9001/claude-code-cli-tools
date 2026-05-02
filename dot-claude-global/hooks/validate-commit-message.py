#!/usr/bin/env python3
"""
PreToolUse hook to validate git commit messages against project standards.

Enforces:
  - Title under 72 characters
  - Title in conventional-commits format (`type(scope)?: subject`)
  - Body 1-4 non-empty non-trailer lines max
  - Body lines wrap at 72 characters
  - Trailers (e.g. `Co-Authored-By:`) at the end after a blank line don't count

Coverage:
  - `-m "..."`, `-m '...'`, `--message=...`, `--message ...`
  - heredoc body forms (`<<EOF`, `<<'EOF'`, `<<"EOF"`, `<<-EOF`)
  - `-F path` and `-F "path with spaces"`
  - `--amend -m "..."` (validates), `--amend --no-edit` (passes through)
  - Editor-based commits are unreachable; the hook can't see them.

Known limitations (lean-allow):
  - Pathological shell escaping or nested heredocs fall through.
  - `git c` (alias) isn't recognised — only literal `git commit` is matched.
  - Body lines that look like trailers (`Fixes: x`) after a blank line ARE
    stripped as trailers, matching git's own trailer semantics.

Override: run the commit manually outside Claude Code.
"""

from pathlib import Path
import os
import re
import shlex
import sys

sys.path.insert(0, str(Path(__file__).parent))

from hook_utils import parse_hook_input, deny, pass_through


CONVENTIONAL_TYPES = (
    "feat",
    "fix",
    "chore",
    "docs",
    "refactor",
    "test",
    "perf",
    "build",
    "ci",
    "style",
    "revert",
)
CONVENTIONAL_TITLE_RE = re.compile(
    r"^(" + "|".join(CONVENTIONAL_TYPES) + r")(\([^)]+\))?!?: .+$"
)

# A git trailer is a `Token: value` pair where Token uses Title-Case-With-Hyphens.
# Examples: Co-Authored-By, Signed-off-by, Reviewed-by, Fixes.
TRAILER_RE = re.compile(r"^[A-Z][A-Za-z]*(-[A-Za-z]+)*:\s.+$")

MAX_TITLE = 72
MAX_BODY_LINES = 4
MAX_BODY_LINE = 72


def extract_message(cmd: str) -> str | None:
    """Pull the commit message out of a `git commit ...` invocation.

    Returns the message string, or None if no recognised form was found
    (caller should fall through to allow when this returns None).
    """
    # Heredoc form: -m "$(cat <<EOF ... EOF)" with optional ' or " around
    # the tag, and optional - for indent-stripping. Heredocs are checked
    # first so the outer `-m "..."` doesn't grab `$(cat <<` as the message.
    heredoc = re.search(
        r"<<-?\s*['\"]?(\w+)['\"]?\s*\n(.*?)\n\1\b",
        cmd,
        re.DOTALL,
    )
    if heredoc:
        return heredoc.group(2)

    # -m or --message with double-quoted value (escapes processed).
    m_dq = re.search(
        r'(?:-m|--message)(?:\s+|=)"((?:[^"\\]|\\.)*)"',
        cmd,
        re.DOTALL,
    )
    if m_dq:
        return m_dq.group(1).replace('\\"', '"').replace("\\\\", "\\")

    # -m or --message with single-quoted value (literal, no escapes).
    m_sq = re.search(
        r"(?:-m|--message)(?:\s+|=)'([^']*)'",
        cmd,
        re.DOTALL,
    )
    if m_sq:
        return m_sq.group(1)

    # -F path / -F "path with spaces" / -F 'path with spaces'
    f_arg = re.search(
        r"-F\s+(?:\"([^\"]+)\"|'([^']+)'|(\S+))",
        cmd,
    )
    if f_arg:
        path = f_arg.group(1) or f_arg.group(2) or f_arg.group(3)
        try:
            return Path(os.path.expanduser(path)).read_text()
        except OSError:
            return None

    return None


def is_amend_no_edit(cmd: str) -> bool:
    """Return True if the invocation is `git commit --amend --no-edit`.

    Substring matching `"--no-edit" in cmd` would falsely trigger on a
    message body containing the literal string '--no-edit'. Tokenize via
    shlex so we only match the flags as distinct argv tokens. Fall back
    to a whitespace-delimited regex if tokenization fails (e.g. heredocs
    confuse shlex).
    """
    try:
        tokens = shlex.split(cmd, posix=True)
        return "--amend" in tokens and "--no-edit" in tokens
    except ValueError:
        return bool(re.search(r"(?<!\S)--amend(?!\S)", cmd)) and bool(
            re.search(r"(?<!\S)--no-edit(?!\S)", cmd)
        )


def split_message(msg: str) -> tuple[str, list[str]]:
    """Return (title, body_lines) with trailers stripped.

    body_lines includes blank-line paragraph separators if present, so the
    caller can decide whether to count them. Trailers at the end (after a
    blank line) are removed entirely.
    """
    # Normalise CRLF and stray CR so length checks count visible characters.
    lines = msg.replace("\r\n", "\n").replace("\r", "").split("\n")
    if not lines:
        return ("", [])
    title = lines[0]
    rest = lines[1:]

    # Trim trailing empty lines to find the real end.
    while rest and rest[-1] == "":
        rest.pop()

    # Strip trailer block: last contiguous trailer-formatted lines preceded
    # by a blank line. Repeat in case multiple blank-separated trailer
    # blocks were written (uncommon but cheap to handle).
    while rest:
        try:
            last_blank = max(i for i, line in enumerate(rest) if line == "")
        except ValueError:
            break
        candidates = rest[last_blank + 1 :]
        if candidates and all(TRAILER_RE.match(line) for line in candidates):
            rest = rest[:last_blank]
            while rest and rest[-1] == "":
                rest.pop()
        else:
            break

    # Drop the leading blank that separates title from body, if present.
    if rest and rest[0] == "":
        rest = rest[1:]

    return (title, rest)


def validate(msg: str) -> list[str]:
    """Return a list of human-readable rule violations (empty = passes)."""
    title, body = split_message(msg)
    errors: list[str] = []

    if len(title) > MAX_TITLE:
        errors.append(f"Title is {len(title)} characters; max is {MAX_TITLE}.")
    if not CONVENTIONAL_TITLE_RE.match(title):
        errors.append(
            "Title is not in conventional-commits format. Expected "
            "`type(scope)?: subject` where type is one of: "
            + ", ".join(CONVENTIONAL_TYPES)
            + "."
        )

    body_content = [line for line in body if line.strip()]
    if len(body_content) > MAX_BODY_LINES:
        errors.append(
            f"Body has {len(body_content)} non-empty lines (trailers like "
            f"Co-Authored-By: are already excluded from this count); max is "
            f"{MAX_BODY_LINES}. If the change can't fit in {MAX_BODY_LINES} "
            "lines, split the commit."
        )

    over = [i for i, line in enumerate(body, 1) if len(line) > MAX_BODY_LINE]
    if over:
        label = "line" if len(over) == 1 else "lines"
        nums = ", ".join(str(i) for i in over)
        errors.append(f"Body {label} {nums} over {MAX_BODY_LINE} characters.")

    return errors


def main() -> None:
    inp = parse_hook_input()
    if inp is None or not inp.is_pre_tool_use or inp.tool_name != "Bash":
        pass_through()

    cmd = inp.get_input("command", "")
    # Only inspect the invocation line itself; `git commit` substrings inside
    # a heredoc body (e.g. test scripts piping Python with git references)
    # would otherwise self-trigger.
    invocation = cmd.split("\n", 1)[0]
    if not re.search(r"\bgit\s+commit\b", invocation):
        pass_through()
    # --amend --no-edit reuses the prior message; nothing to validate.
    if is_amend_no_edit(cmd):
        pass_through()

    msg = extract_message(cmd)
    if msg is None:
        # Couldn't parse; lean allow rather than block on false positives.
        pass_through()

    errors = validate(msg)
    if errors:
        bullet = "\n  - ".join(errors)
        deny("Commit message rejected:\n  - " + bullet)

    pass_through()


if __name__ == "__main__":
    main()
