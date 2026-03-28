#!/usr/bin/env bash
# claude-agile Hub launcher
# Sources API keys and starts the orchestrator

KEYS_FILE="${CLAUDE_AGILE_KEYS:-$HOME/lifeos-keys.sh}"

if [ -f "$KEYS_FILE" ]; then
    echo "  Loading keys from $KEYS_FILE"
    source "$KEYS_FILE"
fi

exec python3 "$(dirname "$0")/orchestrator.py" "$@"
