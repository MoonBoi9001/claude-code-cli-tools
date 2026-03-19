#!/usr/bin/env python3
"""
PostToolUse hook: format and lint files after Edit/Write.

Formats the file silently, then runs a linter. If lint errors are found,
reports them back to Claude via exit code 2 so it sees the feedback and
self-corrects.

Supported languages:
  Python  — ruff format + ruff check
  TS/JS   — prettier/biome format + eslint/biome lint
  Rust    — rustfmt (edition-aware via Cargo.toml)
  Shell   — shfmt format + shellcheck
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from hook_utils import parse_hook_input, deny, pass_through

SKIP_DIRS = frozenset(
    {
        "node_modules",
        ".git",
        "target",
        "dist",
        "build",
        "__pycache__",
        ".venv",
        "venv",
        ".next",
        ".turbo",
    }
)

TOOL_TIMEOUT = 10


def should_skip(file_path: str) -> bool:
    """Skip generated/vendored paths."""
    return any(part in SKIP_DIRS for part in Path(file_path).parts)


def has_tool(name: str) -> bool:
    """Check if a CLI tool is available on PATH."""
    return shutil.which(name) is not None


def run_tool(args: list[str]) -> subprocess.CompletedProcess:
    """Run a tool with timeout. Returns a zero-exit result on failure."""
    try:
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=TOOL_TIMEOUT,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return subprocess.CompletedProcess(args, 0, "", "")


def get_rustfmt_cmd() -> list[str]:
    """Get the rustfmt command, preferring nightly when available."""
    if has_tool("rustup"):
        result = run_tool(["rustup", "which", "--toolchain", "nightly", "rustfmt"])
        if result.returncode == 0 and result.stdout.strip():
            return [result.stdout.strip()]
    if has_tool("rustfmt"):
        return ["rustfmt"]
    return []


def find_rust_edition(file_path: str) -> str | None:
    """Walk up from file to find the Rust edition in Cargo.toml."""
    directory = Path(file_path).parent
    while directory != directory.parent:
        cargo_toml = directory / "Cargo.toml"
        if cargo_toml.is_file():
            try:
                for line in cargo_toml.read_text().splitlines():
                    key, _, value = line.strip().partition("=")
                    if key.strip() == "edition":
                        value = value.strip().strip('"').strip("'")
                        if value and value[0].isdigit():
                            return value
            except OSError:
                pass
        directory = directory.parent
    return None


def format_and_lint(file_path: str) -> str | None:
    """
    Format the file in place, then lint it.

    Returns lint error output if issues found, None otherwise.
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".py":
        if has_tool("ruff"):
            run_tool(["ruff", "format", "--quiet", file_path])
            result = run_tool(
                ["ruff", "check", "--output-format", "concise", file_path]
            )
            if result.returncode != 0 and result.stdout.strip():
                return result.stdout.strip()

    elif ext in {".ts", ".tsx", ".js", ".jsx"}:
        if has_tool("prettier"):
            run_tool(["prettier", "--write", "--log-level", "silent", file_path])
        elif has_tool("biome"):
            run_tool(["biome", "format", "--write", file_path])

        if has_tool("eslint"):
            result = run_tool(["eslint", "--no-warn-ignored", file_path])
            # eslint exits 1 for lint errors, 2 for config/fatal errors — only report lint
            if result.returncode == 1:
                output = (result.stdout or "").strip()
                if output:
                    return output
        elif has_tool("biome"):
            result = run_tool(["biome", "lint", file_path])
            if result.returncode != 0:
                output = (result.stdout or result.stderr or "").strip()
                if output:
                    return output

    elif ext == ".rs":
        rustfmt = get_rustfmt_cmd()
        if rustfmt:
            cmd = [*rustfmt, "--quiet"]
            edition = find_rust_edition(file_path)
            if edition:
                cmd.extend(["--edition", edition])
            cmd.append(file_path)
            run_tool(cmd)

    elif ext in {".sh", ".bash", ".zsh"}:
        if has_tool("shfmt"):
            run_tool(["shfmt", "-w", file_path])

        if has_tool("shellcheck"):
            result = run_tool(["shellcheck", "--format", "gcc", file_path])
            if result.returncode != 0 and result.stdout.strip():
                return result.stdout.strip()

    return None


def main():
    hook = parse_hook_input()
    if not hook:
        pass_through()

    if not hook.is_post_tool_use:
        pass_through()

    if hook.tool_name not in ("Edit", "Write"):
        pass_through()

    file_path = hook.get_input("file_path")
    if not file_path or not os.path.isfile(file_path):
        pass_through()

    if should_skip(file_path):
        pass_through()

    errors = format_and_lint(file_path)
    if errors:
        deny(f"Lint errors in {file_path}:\n{errors}")

    pass_through()


if __name__ == "__main__":
    main()
