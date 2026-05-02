#!/usr/bin/env python3
"""
PreToolUse hook to validate PR titles and bodies for `gh pr create` /
`gh pr edit` invocations against the rules in ~/.claude/CLAUDE.md
(Git Workflow > PR Titles, PR Body).

Title rules:
  - Under 64 characters
  - Conventional commit format `type: subject` — NO scope (`(scope)` rejected)

Body rules:
  - Exactly three top-level (H2) sections: TL;DR, Motivation, Summary.
    Any other H2 heading is rejected.
  - TL;DR: <= 3 sentences
  - Motivation: <= 5 sentences AND <= 2 paragraphs
  - Summary: each bullet line < 100 characters

Coverage:
  - `gh pr create --title ... --body ...` (and `-t`/`-b` short forms)
  - `--body-file path` / `-F path` (body content read from file)
  - heredoc body via `--body "$(cat <<'EOF' ... EOF)"`
  - `gh pr edit <NUMBER> --title ... --body ...`
  - Editor-based body (no `--body` flag) is unreachable — the hook can't see it.

Sentence counting is approximate. Common abbreviations
(e.g., i.e., vs., etc., a.m., p.m., U.S., Mr., Dr.) are stripped of their
trailing dot before counting; decimals and version strings are tolerated by
requiring a sentence terminator to be followed by whitespace + capital letter
or end-of-text. Edge cases will miscount — the deny message reports the
counted value so you can spot a false positive.

Override: run `gh pr create` outside Claude Code.
"""

from pathlib import Path
import os
import re
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
# PR title: type: subject (NO scope)
PR_TITLE_RE = re.compile(r"^(" + "|".join(CONVENTIONAL_TYPES) + r")!?: .+$")
# Reject scope: type(scope): subject — different rule from commit titles
SCOPE_PATTERN = re.compile(r"^(" + "|".join(CONVENTIONAL_TYPES) + r")\(.+\)!?: ")

MAX_TITLE = 64
MAX_TLDR_SENTENCES = 3
MAX_MOTIVATION_SENTENCES = 5
MAX_MOTIVATION_PARAGRAPHS = 2
MAX_SUMMARY_BULLET_CHARS = 100

# Permitted H2 sections (case-insensitive, allow flexible heading suffixes)
H2_TLDR = re.compile(r"^##\s+TL[;:]?DR\b", re.IGNORECASE)
H2_MOTIVATION = re.compile(r"^##\s+Motivation\b", re.IGNORECASE)
H2_SUMMARY = re.compile(r"^##\s+Summary\b", re.IGNORECASE)

# Common abbreviations whose trailing dot must NOT count as a sentence end.
ABBREVIATIONS = (
    "e.g.",
    "i.e.",
    "vs.",
    "etc.",
    "et al.",
    "a.m.",
    "p.m.",
    "U.S.",
    "U.K.",
    "U.S.A.",
    "Mr.",
    "Mrs.",
    "Ms.",
    "Dr.",
    "Prof.",
    "Inc.",
    "Ltd.",
    "Co.",
    "St.",
    "Ave.",
    "No.",
    "vol.",
)


def extract_title(cmd: str) -> str | None:
    """Pull `--title` / `-t` value out of a `gh pr create/edit` invocation."""
    m = re.search(
        r'(?:--title|(?<!\S)-t)(?:\s+|=)"((?:[^"\\]|\\.)*)"',
        cmd,
        re.DOTALL,
    )
    if m:
        return m.group(1).replace('\\"', '"').replace("\\\\", "\\")
    m = re.search(
        r"(?:--title|(?<!\S)-t)(?:\s+|=)'([^']*)'",
        cmd,
        re.DOTALL,
    )
    if m:
        return m.group(1)
    return None


def extract_body(cmd: str) -> str | None:
    """Pull `--body` / `-b` value, or read `--body-file` / `-F` path."""
    # Heredoc form first so an outer `--body "..."` doesn't grab `$(cat <<...`.
    heredoc = re.search(
        r"<<-?\s*['\"]?(\w+)['\"]?\s*\n(.*?)\n\1\b",
        cmd,
        re.DOTALL,
    )
    if heredoc:
        return heredoc.group(2)

    m = re.search(
        r'(?:--body|(?<!\S)-b)(?:\s+|=)"((?:[^"\\]|\\.)*)"',
        cmd,
        re.DOTALL,
    )
    if m:
        return m.group(1).replace('\\"', '"').replace("\\\\", "\\")
    m = re.search(
        r"(?:--body|(?<!\S)-b)(?:\s+|=)'([^']*)'",
        cmd,
        re.DOTALL,
    )
    if m:
        return m.group(1)

    f_arg = re.search(
        r"(?:--body-file|(?<!\S)-F)\s+(?:\"([^\"]+)\"|'([^']+)'|(\S+))",
        cmd,
    )
    if f_arg:
        path = f_arg.group(1) or f_arg.group(2) or f_arg.group(3)
        try:
            return Path(os.path.expanduser(path)).read_text()
        except OSError:
            return None

    return None


def split_sections(body: str) -> tuple[list[tuple[str, str]], list[str]]:
    """Split body into (heading, content) pairs and return any pre-section preamble.

    Returns ([(heading, content), ...], preamble_lines). Tracks fenced code blocks
    so `## Foo` inside a code block isn't treated as a heading.
    """
    lines = body.replace("\r\n", "\n").replace("\r", "").split("\n")
    sections: list[tuple[str, str]] = []
    preamble: list[str] = []
    current_heading: str | None = None
    current_content: list[str] = []
    in_code = False

    for line in lines:
        if re.match(r"^\s*(```|~~~)", line):
            in_code = not in_code
            if current_heading is not None:
                current_content.append(line)
            else:
                preamble.append(line)
            continue

        if not in_code and re.match(r"^##\s+", line):
            if current_heading is not None:
                sections.append((current_heading, "\n".join(current_content)))
            current_heading = line.rstrip()
            current_content = []
        elif current_heading is not None:
            current_content.append(line)
        else:
            preamble.append(line)

    if current_heading is not None:
        sections.append((current_heading, "\n".join(current_content)))

    return sections, preamble


def count_sentences(text: str) -> int:
    """Approximate sentence count. Strips code, neutralises common abbreviations,
    and only counts terminators followed by whitespace+capital or end-of-text."""
    text = re.sub(r"(```|~~~).*?\1", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", "", text)
    for abbr in ABBREVIATIONS:
        text = text.replace(abbr, abbr.replace(".", ""))
    matches = re.findall(r"[.!?]+(?=\s+[A-Z]|\s*$)", text.strip())
    return len(matches)


def count_paragraphs(text: str) -> int:
    """Paragraph = block separated by blank lines. Code blocks count as one."""
    text = re.sub(r"(```|~~~).*?\1", "CODEBLOCK", text, flags=re.DOTALL)
    paragraphs = re.split(r"\n\s*\n", text.strip())
    return len([p for p in paragraphs if p.strip()])


def find_long_bullets(section: str) -> list[tuple[int, int, str]]:
    """Return (line_number, char_count, snippet) for bullets > MAX_SUMMARY_BULLET_CHARS."""
    long_bullets = []
    for i, line in enumerate(section.split("\n"), 1):
        stripped = line.lstrip()
        if (stripped.startswith("- ") or stripped.startswith("* ")) and len(
            line
        ) > MAX_SUMMARY_BULLET_CHARS:
            snippet = line[:60] + "..." if len(line) > 60 else line
            long_bullets.append((i, len(line), snippet))
    return long_bullets


def validate_title(title: str) -> list[str]:
    errors: list[str] = []
    if len(title) > MAX_TITLE:
        errors.append(f"Title is {len(title)} characters; max is {MAX_TITLE}.")
    if SCOPE_PATTERN.match(title):
        errors.append(
            "Title contains a scope `(...)`. PR titles must use `type: subject` "
            "without scope — drop the parenthesised group. Scope is for commits, "
            "not PR titles (PR titles only have 64 chars to work with)."
        )
    elif not PR_TITLE_RE.match(title):
        errors.append(
            "Title is not in conventional-commits format. Expected "
            "`type: subject` where type is one of: "
            + ", ".join(CONVENTIONAL_TYPES)
            + "."
        )
    return errors


def _classify(heading: str) -> str | None:
    if H2_TLDR.match(heading):
        return "tldr"
    if H2_MOTIVATION.match(heading):
        return "motivation"
    if H2_SUMMARY.match(heading):
        return "summary"
    return None


def validate_body(body: str) -> list[str]:
    errors: list[str] = []
    sections, _preamble = split_sections(body)

    if not sections:
        errors.append(
            "Body has no H2 sections. Expected exactly three: "
            "`## TL;DR`, `## Motivation`, `## Summary`."
        )
        return errors

    contents: dict[str, str] = {}
    bad_headings: list[str] = []
    for heading, content in sections:
        key = _classify(heading)
        if key is None:
            bad_headings.append(heading.strip())
            continue
        if key in contents:
            errors.append(f"Duplicate `{heading.strip()}` section — keep only one.")
        else:
            contents[key] = content

    if bad_headings:
        errors.append(
            "Body contains disallowed H2 sections: "
            + ", ".join(f"`{h}`" for h in bad_headings)
            + ". Only `## TL;DR`, `## Motivation`, `## Summary` are permitted."
        )

    required = {
        "tldr": "## TL;DR",
        "motivation": "## Motivation",
        "summary": "## Summary",
    }
    missing = [name for key, name in required.items() if key not in contents]
    if missing:
        errors.append("Body is missing required sections: " + ", ".join(missing) + ".")

    for key, name in required.items():
        if key in contents and not contents[key].strip():
            errors.append(f"`{name}` section is empty.")

    if "tldr" in contents:
        n = count_sentences(contents["tldr"])
        if n > MAX_TLDR_SENTENCES:
            errors.append(
                f"TL;DR has {n} sentences; max is {MAX_TLDR_SENTENCES}. "
                "If the count looks wrong the counter may have miscounted around "
                "abbreviations or decimals — re-check the prose is genuinely concise."
            )

    if "motivation" in contents:
        n_sentences = count_sentences(contents["motivation"])
        n_paragraphs = count_paragraphs(contents["motivation"])
        if n_sentences > MAX_MOTIVATION_SENTENCES:
            errors.append(
                f"Motivation has {n_sentences} sentences; max is "
                f"{MAX_MOTIVATION_SENTENCES}. If the PR can't be motivated in "
                f"{MAX_MOTIVATION_SENTENCES} sentences it's too big — split it."
            )
        if n_paragraphs > MAX_MOTIVATION_PARAGRAPHS:
            errors.append(
                f"Motivation has {n_paragraphs} paragraphs; max is "
                f"{MAX_MOTIVATION_PARAGRAPHS}."
            )

    if "summary" in contents:
        for lineno, chars, snippet in find_long_bullets(contents["summary"])[:3]:
            errors.append(
                f"Summary bullet (line {lineno} within section) is {chars} "
                f"chars (max {MAX_SUMMARY_BULLET_CHARS}): {snippet!r}"
            )

    return errors


REMINDER = (
    "\n\nUnenforceable rules to also self-check before retrying:\n"
    "  - Title readable by a non-engineer (PM, designer, executive) without "
    "opening the diff. No file paths, function names, internal acronyms, "
    "engineering-specific lingo or library jargon — describe the change in "
    "plain English, not implementation.\n"
    "  - TL;DR is the one-glance answer to 'what does this PR do, and is it "
    "safe to approve?' for a reader with under 30 seconds.\n"
    "  - Motivation: open with what the system does today, then what's wrong "
    "or missing, then the impact. Name actual components ('the network "
    "subgraph' not 'a subgraph'). Trace cause and effect as a connected "
    "narrative, not a parallel list. Don't overstate — say 'may' when "
    "uncertain.\n"
    "  - Summary: bullet points of what the PR does. No prose narrative — "
    "that belongs in motivation."
)


def main() -> None:
    inp = parse_hook_input()
    if inp is None or not inp.is_pre_tool_use or inp.tool_name != "Bash":
        pass_through()

    cmd = inp.get_input("command", "")
    invocation = cmd.split("\n", 1)[0]
    if not re.search(r"\bgh\s+pr\s+(create|edit)\b", invocation):
        pass_through()

    title = extract_title(cmd)
    body = extract_body(cmd)

    errors: list[str] = []
    if title is not None:
        errors.extend(validate_title(title))
    if body is not None:
        errors.extend(validate_body(body))

    if errors:
        bullet = "\n  - ".join(errors)
        deny("PR rejected:\n  - " + bullet + REMINDER)

    pass_through()


if __name__ == "__main__":
    main()
