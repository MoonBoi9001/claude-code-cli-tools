#!/usr/bin/env bash
# Robust Claude wrapper with installation protection

set -euo pipefail

BASE="$HOME/.claude/local"
LOCK_FILE="/tmp/claude-exec.lock"

# Function to check if Claude is healthy
is_healthy() {
    [ -x "$BASE/node_modules/.bin/claude" ] || \
    [ -x "$BASE/node_modules/.bin/claude-code" ] || \
    [ -f "$BASE/node_modules/@anthropic-ai/claude-code/cli.js" ]
}

# Acquire lock to prevent concurrent npm operations
exec 200>"$LOCK_FILE"
if ! flock -n 200; then
    # Wait up to 5 seconds for lock
    flock -w 5 200 || {
        echo "Warning: Another Claude operation is in progress. Proceeding anyway..." >&2
    }
fi

# Check health and run
if ! is_healthy; then
    echo "Claude installation appears broken. Running health check..." >&2
    "$BASE/claude-health-check.sh" || exit 1
fi

# Execute Claude with fallback options
if [ -x "$BASE/node_modules/.bin/claude" ]; then
    exec "$BASE/node_modules/.bin/claude" "$@"
elif [ -x "$BASE/node_modules/.bin/claude-code" ]; then
    exec "$BASE/node_modules/.bin/claude-code" "$@"
elif [ -f "$BASE/node_modules/@anthropic-ai/claude-code/cli.js" ]; then
    exec node "$BASE/node_modules/@anthropic-ai/claude-code/cli.js" "$@"
else
    echo "Claude CLI not found. Please run: $BASE/claude-health-check.sh" >&2
    exit 1
fi