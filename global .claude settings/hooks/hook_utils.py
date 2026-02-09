#!/usr/bin/env python3
"""
Shared utilities for Claude Code permission hooks.

This module provides reusable components for command validation,
following SOLID principles:
- Single Responsibility: Each class has one focused purpose
- Open/Closed: New patterns can be added via configuration
- Dependency Inversion: High-level validators depend on abstractions

Components:
    Hook Helpers:
        HookInput: Parsed hook input data
        parse_hook_input(): Parse JSON from stdin
        approve(): Output approval and exit
        deny(): Output denial and exit
        pass_through(): Exit without decision

    Path Utilities:
        resolve_path(): Resolve path with expansion
        is_path_within(): Check if path is within allowed directories

    Command Validation:
        SettingsReader: Reads Bash allow patterns from settings files
        PatternMatcher: Matches commands against allow patterns
        DangerousPatternChecker: Detects dangerous command patterns
        ChainSplitter: Splits command chains on operators
        WrapperUnwrapper: Unwraps trusted command wrapper patterns
        CommandValidator: Orchestrates full command validation
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Protocol, NoReturn
import fnmatch
import json
import os
import re
import sys


# =============================================================================
# Hook Input/Output Helpers (DRY: Common boilerplate for all hooks)
# =============================================================================

@dataclass
class HookInput:
    """Parsed hook input data."""
    tool_name: str
    hook_event: str
    tool_input: dict
    raw_data: dict

    @property
    def is_permission_request(self) -> bool:
        """Check if this is a PermissionRequest event."""
        return self.hook_event == "PermissionRequest"

    @property
    def is_pre_tool_use(self) -> bool:
        """Check if this is a PreToolUse event."""
        return self.hook_event == "PreToolUse"

    def get_input(self, key: str, default: str = "") -> str:
        """Get a value from tool_input."""
        return self.tool_input.get(key, default)


def parse_hook_input() -> Optional[HookInput]:
    """
    Parse hook input from stdin.

    Returns:
        HookInput if parsing succeeds, None on JSON error.
    """
    try:
        data = json.load(sys.stdin)
        return HookInput(
            tool_name=data.get("tool_name", ""),
            hook_event=data.get("hook_event_name", ""),
            tool_input=data.get("tool_input", {}),
            raw_data=data
        )
    except json.JSONDecodeError:
        return None


def approve() -> NoReturn:
    """Output approval decision and exit."""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "decision": {"behavior": "allow"}
        }
    }
    print(json.dumps(output))
    sys.exit(0)


def deny(reason: str) -> NoReturn:
    """Output denial reason to stderr and exit with code 2."""
    print(reason, file=sys.stderr)
    sys.exit(2)


def pass_through() -> NoReturn:
    """Exit without making a decision (let other hooks or user decide)."""
    sys.exit(0)


# =============================================================================
# Path Utilities (DRY: Common path operations)
# =============================================================================

def resolve_path(path: str) -> Optional[str]:
    """
    Resolve a path by expanding ~ and following symlinks.

    Returns:
        Resolved absolute path, or None if resolution fails.
    """
    if not path:
        return None
    try:
        return os.path.realpath(os.path.expanduser(path))
    except (OSError, ValueError):
        return None


def is_path_within(path: str, allowed_dirs: tuple[str, ...]) -> bool:
    """
    Check if path is within any of the allowed directories.

    Uses exact match or directory prefix check to prevent path traversal
    attacks (e.g., 'github-evil' matching 'github').

    Args:
        path: Path to check (will be resolved)
        allowed_dirs: Tuple of allowed directory paths (should be pre-resolved)

    Returns:
        True if path is within an allowed directory.
    """
    resolved = resolve_path(path)
    if not resolved:
        return False

    return any(
        resolved == allowed or resolved.startswith(allowed + os.sep)
        for allowed in allowed_dirs
    )


# =============================================================================
# Protocols (Interfaces for Dependency Inversion)
# =============================================================================

class IPatternMatcher(Protocol):
    """Interface for pattern matching."""
    def matches(self, command: str, pattern: str) -> bool: ...


class ISettingsReader(Protocol):
    """Interface for reading settings."""
    def get_bash_patterns(self) -> list[str]: ...


# =============================================================================
# Settings Reader (Single Responsibility: Read patterns from settings files)
# =============================================================================

class SettingsReader:
    """Reads and caches Bash allow patterns from global and project settings."""

    def __init__(self):
        self._patterns: Optional[list[str]] = None

    def get_bash_patterns(self) -> list[str]:
        """Return list of Bash allow patterns from all settings files."""
        if self._patterns is not None:
            return self._patterns

        self._patterns = []
        self._read_patterns_from(os.path.expanduser("~/.claude/settings.json"))

        project_settings = self._find_project_settings()
        if project_settings:
            self._read_patterns_from(project_settings)

        return self._patterns

    def _find_project_settings(self) -> Optional[str]:
        """Walk up from cwd to find .claude/settings.local.json."""
        try:
            current = os.getcwd()
            for _ in range(20):
                candidate = os.path.join(current, ".claude", "settings.local.json")
                if os.path.isfile(candidate):
                    return candidate
                parent = os.path.dirname(current)
                if parent == current:
                    break
                current = parent
        except OSError:
            pass
        return None

    def _read_patterns_from(self, path: str) -> None:
        """Extract Bash patterns from a settings file."""
        try:
            with open(path) as f:
                settings = json.load(f)
            for entry in settings.get("permissions", {}).get("allow", []):
                if entry.startswith("Bash(") and entry.endswith(")"):
                    pattern = entry[5:-1]
                    if pattern not in self._patterns:
                        self._patterns.append(pattern)
        except (OSError, json.JSONDecodeError):
            pass


# =============================================================================
# Pattern Matcher (Single Responsibility: Match commands against patterns)
# =============================================================================

class PatternMatcher:
    """Matches commands against settings.json Bash patterns."""

    def matches(self, command: str, pattern: str) -> bool:
        """
        Check if command matches a Bash pattern from settings.json.

        Pattern formats:
        - "ls:*"           -> matches "ls", "ls -la", "ls /path"
        - "git status:*"   -> matches "git status", "git status -s"
        - "npm:--version"  -> matches "npm --version" exactly
        - "curl:-s :*"     -> matches "curl -s ..." (flag must be present)

        Also handles full paths: "/usr/bin/ls -la" matches "ls:*"
        """
        # Try matching with original command first
        if self._matches_internal(command, pattern):
            return True

        # Try matching with normalized command (basename of first token)
        normalized = self._normalize_command(command)
        if normalized != command:
            return self._matches_internal(normalized, pattern)

        return False

    def _normalize_command(self, command: str) -> str:
        """Normalize command by replacing full path with basename."""
        if not command:
            return command
        parts = command.split(None, 1)
        if not parts:
            return command
        first_token = parts[0]
        if '/' in first_token:
            basename = os.path.basename(first_token)
            if len(parts) > 1:
                return f"{basename} {parts[1]}"
            return basename
        return command

    def _matches_internal(self, command: str, pattern: str) -> bool:
        """Internal matching logic."""
        if ":" not in pattern:
            return self._match_bare_command(command, pattern)

        cmd_part, args_pattern = pattern.split(":", 1)
        return self._match_with_args(command, cmd_part.strip(), args_pattern)

    def _match_bare_command(self, command: str, pattern: str) -> bool:
        """Match pattern without colon (just command name)."""
        cmd_base = command.split()[0] if command else ""
        return cmd_base == pattern

    def _match_with_args(self, command: str, cmd_part: str, args_pattern: str) -> bool:
        """Match pattern with command:args format."""
        if command == cmd_part:
            rest = ""
        elif command.startswith(cmd_part + " "):
            rest = command[len(cmd_part):].strip()
        else:
            return False

        if args_pattern == "*":
            return True

        if args_pattern.endswith(":*"):
            required_prefix = args_pattern[:-2]
            return rest.startswith(required_prefix)

        if " :*" in args_pattern:
            required_flag = args_pattern.replace(" :*", "").strip()
            return required_flag in rest

        if args_pattern.endswith("*"):
            return fnmatch.fnmatch(rest, args_pattern)

        return rest == args_pattern or rest.startswith(args_pattern + " ")


# =============================================================================
# Dangerous Pattern Checker (Single Responsibility: Detect dangerous patterns)
# =============================================================================

@dataclass
class DangerousPatternConfig:
    """Configuration for dangerous pattern detection."""
    # Patterns dangerous even inside quotes (command substitution)
    always_dangerous: tuple[re.Pattern, ...] = field(default_factory=lambda: tuple(
        re.compile(p) for p in [
            r'\$\(',           # Command substitution $(...)
            r'`[^`]*`',        # Backtick command substitution
        ]
    ))
    # Patterns dangerous only when unquoted
    unquoted_dangerous: tuple[re.Pattern, ...] = field(default_factory=lambda: tuple(
        re.compile(p) for p in [
            r'\beval\b',       # eval command
            r'\bsource\b',     # source command
            r'^\s*\.',         # . (source) at start
            # Redirect to absolute path (but allow /dev/null and fd redirects like 2>/dev/null)
            r'(?<!\d)>\s*/(?!dev/null)',
            r'(?<!\d)>>\s*/(?!dev/null)',
            r'<\(',            # Process substitution <(...)
            r'>\(',            # Process substitution >(...)
            r'\n',             # Newline (command separator)
        ]
    ))


class DangerousPatternChecker:
    """Checks commands for dangerous patterns."""

    def __init__(self, config: Optional[DangerousPatternConfig] = None):
        self._config = config or DangerousPatternConfig()

    def is_dangerous(self, command: str) -> bool:
        """Return True if command contains dangerous patterns."""
        # Always-dangerous patterns apply everywhere
        if any(p.search(command) for p in self._config.always_dangerous):
            return True

        # Unquoted-dangerous patterns only apply outside quotes
        stripped = self._strip_quoted_content(command)
        return any(p.search(stripped) for p in self._config.unquoted_dangerous)

    def _strip_quoted_content(self, s: str) -> str:
        """Remove content inside quotes, preserving structure outside."""
        result = []
        in_single = False
        in_double = False
        i = 0

        while i < len(s):
            c = s[i]

            if c == '\\' and i + 1 < len(s) and (in_single or in_double):
                i += 2
                continue

            if c == "'" and not in_double:
                in_single = not in_single
                i += 1
                continue

            if c == '"' and not in_single:
                in_double = not in_double
                i += 1
                continue

            if not in_single and not in_double:
                result.append(c)
            i += 1

        return ''.join(result)


# =============================================================================
# Chain Splitter (Single Responsibility: Split commands on operators)
# =============================================================================

class ChainSplitter:
    """Splits shell command chains into individual commands."""

    OPERATORS = ('&&', '||', '|', ';')

    def has_operators(self, command: str) -> bool:
        """Check if command contains chain operators outside quotes."""
        stripped = self._strip_quoted_content(command)
        return any(op in stripped for op in self.OPERATORS)

    def split(self, command: str) -> Optional[list[str]]:
        """
        Split command on chain operators, respecting quotes.
        Returns None if parsing fails (unclosed quotes, etc.)
        """
        segments = []
        current: list[str] = []
        in_single_quote = False
        in_double_quote = False
        i = 0

        while i < len(command):
            char = command[i]

            # Handle quote toggling
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
                current.append(char)
                i += 1
                continue
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
                current.append(char)
                i += 1
                continue

            # Handle escapes
            if char == '\\' and i + 1 < len(command):
                current.append(char)
                current.append(command[i + 1])
                i += 2
                continue

            # Check for operators only outside quotes
            if not in_single_quote and not in_double_quote:
                matched_op = None
                for op in self.OPERATORS:
                    if command[i:i+len(op)] == op:
                        matched_op = op
                        break

                if matched_op:
                    segment = ''.join(current).strip()
                    if segment:
                        segments.append(segment)
                    current = []
                    i += len(matched_op)
                    continue

            current.append(char)
            i += 1

        # Append final segment
        segment = ''.join(current).strip()
        if segment:
            segments.append(segment)

        return segments if segments else None

    def _strip_quoted_content(self, s: str) -> str:
        """Remove content inside quotes for operator detection."""
        result = []
        in_single = False
        in_double = False
        i = 0

        while i < len(s):
            c = s[i]
            if c == '\\' and i + 1 < len(s):
                i += 2
                continue
            if c == "'" and not in_double:
                in_single = not in_single
                i += 1
                continue
            if c == '"' and not in_single:
                in_double = not in_double
                i += 1
                continue
            if not in_single and not in_double:
                result.append(c)
            i += 1

        return ''.join(result)


# =============================================================================
# Wrapper Unwrapper (Single Responsibility: Unwrap trusted command wrappers)
# =============================================================================

@dataclass
class WrapperPattern:
    """Defines a trusted command wrapper pattern."""
    name: str
    regex: re.Pattern
    inner_group: int = 1  # Capture group containing the inner command

    @classmethod
    def create(cls, name: str, pattern: str, inner_group: int = 1) -> 'WrapperPattern':
        """Factory method to create a WrapperPattern."""
        return cls(name=name, regex=re.compile(pattern), inner_group=inner_group)


class WrapperUnwrapper:
    """Unwraps trusted command wrapper patterns to extract inner commands."""

    # Default trusted wrapper patterns
    DEFAULT_PATTERNS: tuple[WrapperPattern, ...] = (
        # Proxmox LXC: sudo pct exec <container_id> -- <command>
        WrapperPattern.create('proxmox_pct', r'^sudo\s+pct\s+exec\s+(\d+)\s+--\s+(.+)$', 2),
        # Proxmox VM: sudo qm guest exec <vmid> -- <command>
        WrapperPattern.create('proxmox_qm', r'^sudo\s+qm\s+guest\s+exec\s+(\d+)\s+--\s+(.+)$', 2),
        # Docker: sudo docker exec <container> <command>
        WrapperPattern.create('docker', r'^sudo\s+docker\s+exec\s+([a-zA-Z0-9_.-]+)\s+(.+)$', 2),
        # bash -c with single quotes
        WrapperPattern.create('bash_single', r"^bash\s+-c\s+'(.+)'$", 1),
        # bash -c with double quotes
        WrapperPattern.create('bash_double', r'^bash\s+-c\s+"(.+)"$', 1),
        # sh -c with single quotes
        WrapperPattern.create('sh_single', r"^sh\s+-c\s+'(.+)'$", 1),
        # sh -c with double quotes
        WrapperPattern.create('sh_double', r'^sh\s+-c\s+"(.+)"$', 1),
        # Generic sudo: sudo <command> (must be last to let specific sudo patterns match first)
        WrapperPattern.create('sudo', r'^sudo\s+(.+)$', 1),
    )

    def __init__(self, patterns: Optional[tuple[WrapperPattern, ...]] = None):
        self._patterns = patterns or self.DEFAULT_PATTERNS

    def unwrap(self, command: str) -> tuple[str, list[str]]:
        """
        Recursively unwrap command wrappers.

        Returns:
            (inner_command, wrapper_chain): The innermost command and list of
            wrapper names that were unwrapped.
        """
        wrapper_chain: list[str] = []
        current = command.strip()

        while True:
            unwrapped, wrapper_name = self._unwrap_once(current)
            if wrapper_name is None:
                break
            wrapper_chain.append(wrapper_name)
            current = unwrapped.strip()

        return current, wrapper_chain

    def _unwrap_once(self, command: str) -> tuple[str, Optional[str]]:
        """
        Try to unwrap one layer of wrapper.

        Returns:
            (inner_command, wrapper_name) or (command, None) if no match.
        """
        for pattern in self._patterns:
            match = pattern.regex.match(command.strip())
            if match:
                try:
                    inner = match.group(pattern.inner_group)
                    return inner, pattern.name
                except IndexError:
                    continue
        return command, None

    def is_wrapped(self, command: str) -> bool:
        """Check if command matches any wrapper pattern."""
        _, wrapper_name = self._unwrap_once(command)
        return wrapper_name is not None


# =============================================================================
# Command Validator (Facade: Orchestrates full command validation)
# =============================================================================

@dataclass
class ValidationResult:
    """Result of command validation."""
    approved: bool
    reason: str
    unwrapped_command: Optional[str] = None
    wrapper_chain: list[str] = field(default_factory=list)


class CommandValidator:
    """
    Orchestrates command validation using composition.

    This is a Facade that coordinates:
    - Dangerous pattern checking
    - Wrapper unwrapping
    - Chain splitting
    - Pattern matching against allow list
    """

    def __init__(
        self,
        settings_reader: Optional[ISettingsReader] = None,
        pattern_matcher: Optional[IPatternMatcher] = None,
        dangerous_checker: Optional[DangerousPatternChecker] = None,
        chain_splitter: Optional[ChainSplitter] = None,
        wrapper_unwrapper: Optional[WrapperUnwrapper] = None,
    ):
        self._settings = settings_reader or SettingsReader()
        self._matcher = pattern_matcher or PatternMatcher()
        self._dangerous = dangerous_checker or DangerousPatternChecker()
        self._splitter = chain_splitter or ChainSplitter()
        self._unwrapper = wrapper_unwrapper or WrapperUnwrapper()

    def validate(self, command: str) -> ValidationResult:
        """
        Validate a command, handling wrappers and chains.

        Flow:
        1. Check for dangerous patterns
        2. Split on chain operators
        3. For each segment:
           a. Unwrap any wrappers
           b. Recursively validate the inner command
        4. All segments must be approved
        """
        # Fast fail on dangerous patterns
        if self._dangerous.is_dangerous(command):
            return ValidationResult(False, "Command contains dangerous patterns")

        # Split into chain segments
        segments = self._splitter.split(command)
        if segments is None:
            return ValidationResult(False, "Failed to parse command")

        patterns = self._settings.get_bash_patterns()
        all_wrappers: list[str] = []

        for segment in segments:
            result = self._validate_segment(segment, patterns)
            if not result.approved:
                return result
            all_wrappers.extend(result.wrapper_chain)

        return ValidationResult(
            True,
            f"All {len(segments)} command(s) approved",
            wrapper_chain=all_wrappers
        )

    def _validate_segment(self, segment: str, patterns: list[str]) -> ValidationResult:
        """Validate a single command segment (may contain wrappers)."""
        # Try to unwrap
        inner_cmd, wrapper_chain = self._unwrapper.unwrap(segment)

        if wrapper_chain:
            # Command was wrapped - validate the inner command
            return self._validate_inner_command(inner_cmd, patterns, wrapper_chain)

        # No wrapper - validate directly against patterns
        if self._matches_any_pattern(segment, patterns):
            return ValidationResult(True, "Command matches allow pattern")

        base_cmd = segment.split()[0] if segment else segment
        return ValidationResult(False, f"Command '{base_cmd}' not in allow list")

    def _validate_inner_command(
        self,
        inner_cmd: str,
        patterns: list[str],
        wrapper_chain: list[str]
    ) -> ValidationResult:
        """Validate the inner command extracted from wrappers."""
        # Check for dangerous patterns in inner command
        if self._dangerous.is_dangerous(inner_cmd):
            return ValidationResult(
                False,
                "Inner command contains dangerous patterns",
                wrapper_chain=wrapper_chain
            )

        # If inner command has chain operators, split and validate each
        if self._splitter.has_operators(inner_cmd):
            segments = self._splitter.split(inner_cmd)
            if segments is None:
                return ValidationResult(False, "Failed to parse inner command")

            for seg in segments:
                # Recursively validate - inner segments might have wrappers too
                result = self._validate_segment(seg, patterns)
                if not result.approved:
                    return ValidationResult(
                        False,
                        result.reason,
                        wrapper_chain=wrapper_chain + result.wrapper_chain
                    )

            return ValidationResult(
                True,
                f"All {len(segments)} inner command(s) approved",
                unwrapped_command=inner_cmd,
                wrapper_chain=wrapper_chain
            )

        # Single inner command - validate against patterns
        if self._matches_any_pattern(inner_cmd, patterns):
            return ValidationResult(
                True,
                "Inner command matches allow pattern",
                unwrapped_command=inner_cmd,
                wrapper_chain=wrapper_chain
            )

        base_cmd = inner_cmd.split()[0] if inner_cmd else inner_cmd
        return ValidationResult(
            False,
            f"Inner command '{base_cmd}' not in allow list",
            wrapper_chain=wrapper_chain
        )

    def _matches_any_pattern(self, command: str, patterns: list[str]) -> bool:
        """Check if command matches any allow pattern."""
        return any(self._matcher.matches(command, p) for p in patterns)
