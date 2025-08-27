#!/usr/bin/env bash
# Claude Installation Health Check & Repair Script

set -euo pipefail

CLAUDE_HOME="$HOME/.claude/local"
PACKAGE_NAME="@anthropic-ai/claude-code"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_installation() {
    echo -e "${YELLOW}Checking Claude installation...${NC}"
    
    # Check if CLI exists and is executable
    if [ -x "$CLAUDE_HOME/node_modules/.bin/claude" ]; then
        echo -e "${GREEN}✓ Claude binary found${NC}"
        return 0
    elif [ -f "$CLAUDE_HOME/node_modules/$PACKAGE_NAME/cli.js" ]; then
        echo -e "${YELLOW}⚠ Claude CLI found but not linked${NC}"
        return 1
    else
        echo -e "${RED}✗ Claude not installed${NC}"
        return 2
    fi
}

fix_installation() {
    echo -e "${YELLOW}Fixing Claude installation...${NC}"
    
    cd "$CLAUDE_HOME"
    
    # Clean any partial installations
    if [ -d "node_modules/@anthropic-ai" ]; then
        echo "Cleaning partial installations..."
        find "node_modules/@anthropic-ai" -name ".claude-code-*" -type d -exec rm -rf {} + 2>/dev/null || true
    fi
    
    # Lock file to prevent concurrent npm operations
    LOCK_FILE="/tmp/claude-install.lock"
    exec 200>"$LOCK_FILE"
    
    if ! flock -n 200; then
        echo -e "${RED}Another npm operation is in progress. Please wait and try again.${NC}"
        exit 1
    fi
    
    # Install with exact version from package.json
    echo "Installing Claude..."
    npm install --no-audit --no-fund --loglevel=error
    
    # Verify installation
    if [ -x "$CLAUDE_HOME/node_modules/.bin/claude" ]; then
        VERSION=$("$CLAUDE_HOME/node_modules/.bin/claude" --version 2>/dev/null || echo "unknown")
        echo -e "${GREEN}✓ Claude installed successfully (version: $VERSION)${NC}"
    else
        echo -e "${RED}Installation failed. Please check npm logs.${NC}"
        exit 1
    fi
}

# Main
if check_installation; then
    VERSION=$("$CLAUDE_HOME/node_modules/.bin/claude" --version 2>/dev/null || echo "unknown")
    echo -e "${GREEN}Claude is healthy (version: $VERSION)${NC}"
else
    fix_installation
fi