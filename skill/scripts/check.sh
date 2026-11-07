#!/usr/bin/env bash
# Quick automated inspection script for AI agents
set -euo pipefail

TARGET_FILE="${1:-}"

if [ -n "$TARGET_FILE" ]; then
    python3 -m scopelock.cli . --file "$TARGET_FILE"
else
    python3 -m scopelock.cli .
fi
