#!/usr/bin/env python3
"""
Stop hook: block Claude from stopping when its response dismisses errors
as "pre-existing" without fixing or flagging them.

Reads the session transcript to find the last assistant message and checks
for the word "pre-existing" (or "preexisting"). If found, blocks the stop
and quotes each offending sentence back to Claude with the trigger phrase
highlighted, so Claude can see exactly what was flagged.

Uses stop_hook_active to prevent infinite loops — if this hook already
triggered a continuation, allow the next stop unconditionally.
"""

import json
import os
import sys

NEEDLES = ("pre-existing", "preexisting")
SENTENCE_DELIMS = (". ", "! ", "? ", "\n")
MAX_QUOTES = 5

BLOCK_PREAMBLE = (
    "Your response contains the dismissal phrase in these passages "
    "(the trigger is wrapped in >>>...<<<):"
)

BLOCK_TRAILER = (
    "This likely means you dismissed errors without addressing them. "
    "Per project rules: if the error is small (lint, unused import, "
    "type hint, sort order), fix it now. If larger, flag each one "
    "explicitly to the user. Do not move on without either fixing or "
    "flagging. The word may only appear as factual context — never as "
    "a reason to ignore a problem."
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


def find_code_ranges(text):
    """Return (start, end) ranges covering inline and fenced backtick code spans.

    Treats any run of N backticks as opening a code span that closes at the
    next run of exactly N backticks. Covers `inline`, ``with`backticks``, and
    ```fenced``` blocks alike.
    """
    ranges = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] != "`":
            i += 1
            continue
        j = i
        while j < n and text[j] == "`":
            j += 1
        tick_count = j - i
        k = j
        closed = False
        while k < n:
            if text[k] != "`":
                k += 1
                continue
            m = k
            while m < n and text[m] == "`":
                m += 1
            if m - k == tick_count:
                ranges.append((i, m))
                i = m
                closed = True
                break
            k = m
        if not closed:
            i = j
    return ranges


def find_match_spans(text):
    """Return sorted, deduplicated (start, end) spans for every needle hit
    that falls outside any code span."""
    code_ranges = find_code_ranges(text)

    def in_code(pos):
        for s, e in code_ranges:
            if s <= pos < e:
                return True
        return False

    text_lower = text.lower()
    spans = set()
    for needle in NEEDLES:
        start = 0
        while True:
            idx = text_lower.find(needle, start)
            if idx == -1:
                break
            if not in_code(idx):
                spans.add((idx, idx + len(needle)))
            start = idx + 1
    return sorted(spans)


def sentence_bounds(text, start, end):
    """Return (sent_start, sent_end) bracketing the sentence around [start, end)."""
    sent_start = 0
    for delim in SENTENCE_DELIMS:
        idx = text.rfind(delim, 0, start)
        if idx != -1 and idx + len(delim) > sent_start:
            sent_start = idx + len(delim)

    sent_end = len(text)
    for delim in SENTENCE_DELIMS:
        idx = text.find(delim, end)
        if idx != -1:
            # Include the terminating punctuation, drop the trailing space/newline.
            cand = idx + len(delim) - 1
            if cand < sent_end:
                sent_end = cand
    return sent_start, sent_end


def extract_quotes(text):
    """Return a list of sentences containing matches, with each match highlighted."""
    spans = find_match_spans(text)
    if not spans:
        return []

    quotes = []
    seen = set()
    for span in spans:
        sent_start, sent_end = sentence_bounds(text, span[0], span[1])
        key = (sent_start, sent_end)
        if key in seen:
            continue
        seen.add(key)

        # Highlight every match that falls inside this sentence.
        pieces = []
        cursor = sent_start
        for s, e in spans:
            if s < sent_start or e > sent_end:
                continue
            pieces.append(text[cursor:s])
            pieces.append(">>>" + text[s:e] + "<<<")
            cursor = e
        pieces.append(text[cursor:sent_end])

        # Collapse newlines so each quote sits on one line in the block reason.
        quote = "".join(pieces).strip()
        quote = " ".join(quote.split())
        quotes.append(quote)

    return quotes


def build_reason(quotes):
    shown = quotes[:MAX_QUOTES]
    omitted = len(quotes) - len(shown)
    numbered = "\n".join(f'  {i + 1}. "{q}"' for i, q in enumerate(shown))
    if omitted > 0:
        numbered += f"\n  ... and {omitted} more"
    return f"{BLOCK_PREAMBLE}\n\n{numbered}\n\n{BLOCK_TRAILER}"


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
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

    quotes = extract_quotes(message)
    if not quotes:
        return

    output = {"decision": "block", "reason": build_reason(quotes)}
    print(json.dumps(output))


if __name__ == "__main__":
    main()
