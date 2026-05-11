#!/usr/bin/env python3
"""
PreToolUse hook to validate git commit messages against project standards.

Enforces:
  - Title under 72 characters
  - Title in conventional-commits format (`type(scope): subject`, scope mandatory and exactly one lowercase word)
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
  - `git c` (aliases) aren't recognised — `git commit` (with optional
    global flags like `-C <path>`, `-c name=val`, `--no-pager`, etc.)
    is what we match.
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
    r"^(" + "|".join(CONVENTIONAL_TYPES) + r")\([a-z0-9]+\)!?: .+$"
)

# Detect `git [global flags] commit`. The earlier `\bgit\s+commit\b` form
# missed `git -C <path> commit` (and other global-flag prefixes) entirely,
# silently letting any commit invoked that way bypass validation. Allows
# zero or more flag tokens between `git` and `commit`:
#   - `-C <path>` / `-c <name>=<value>`           (`-[Cc]\s+\S+`)
#   - bundled or single-letter flags like `-p`    (`-[A-Za-z]+`)
#   - long flags `--name`, `--name=value`         (`--[\w-]+(?:=\S+)?`)
GIT_COMMIT_RE = re.compile(
    r"\bgit"
    r"(?:\s+(?:-[Cc]\s+\S+|-[A-Za-z]+|--[\w-]+(?:=\S+)?))*"
    r"\s+commit\b"
)

# A git trailer is a `Token: value` pair where Token uses Title-Case-With-Hyphens.
# Examples: Co-Authored-By, Signed-off-by, Reviewed-by, Fixes.
TRAILER_RE = re.compile(r"^[A-Z][A-Za-z]*(-[A-Za-z]+)*:\s.+$")

# Match a heredoc block (the `<<TAG ... TAG` form with all four opening
# variants: `<<TAG`, `<<'TAG'`, `<<"TAG"`, `<<-TAG`). Used to strip heredoc
# bodies before searching for `git commit`: a test script body containing
# the literal string `git commit` must not self-trigger, but a real
# `git commit` invocation on a line after a heredoc must still be caught.
HEREDOC_BODY_RE = re.compile(
    r"<<-?\s*['\"]?(\w+)['\"]?\s*\n.*?\n\1\b",
    re.DOTALL,
)

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
            "`type(scope): subject`. Scope is mandatory: exactly one "
            "lowercase word, no hyphens or slashes, specific enough to "
            "point at the right area. `fix(skill):` is right; "
            "`fix(add-indexers-skill):` is too many words; "
            "`fix(indexers):` is too generic. Type must be one of: "
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
    # Strip heredoc bodies before searching: a `git commit` substring inside
    # a heredoc body (e.g. a test script being cat'd to disk) must not
    # self-trigger, but a real `git commit` invocation on a line other than
    # the first must. The earlier `cmd.split("\n", 1)[0]` defense missed the
    # very common `cat > /tmp/msg <<EOF ... EOF \n git commit -F /tmp/msg`
    # pattern entirely — line 1 was just the heredoc opener.
    sanitized = HEREDOC_BODY_RE.sub("", cmd)
    if not GIT_COMMIT_RE.search(sanitized):
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
        reminders = (
            "\n\nReminders for the rewrite (~/.claude/CLAUDE.md):\n"
            '  - Title reads as completing "If applied, this commit '
            'will…" — lead with an imperative verb (extract, simplify, '
            "prevent), not the type itself. Plain English, not jargon "
            '("prevent" over "gate", "rename" over "alias").\n'
            '  - Body stands on its own. No references to "the original '
            'X bug" or "after the Y refactor" without inlining the '
            "context; no function names or internal jargon. A reader who "
            "has never seen this codebase should be able to follow.\n"
            "  - Don't restate the title in the body."
        )
        deny("Commit message rejected:\n  - " + bullet + reminders)

    pass_through()


if __name__ == "__main__":
    main()
