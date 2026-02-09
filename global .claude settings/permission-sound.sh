#!/bin/bash
# Play sound in background
afplay ~/.claude/claude_sound.mp3 &
# Output proper decision structure to show dialog to user
cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "ask"
    }
  }
}
EOF
