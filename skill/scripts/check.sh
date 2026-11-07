#!/usr/bin/env bash
# Script de auto-checagem rápida para agentes
set -euo pipefail

TARGET_FILE="${1:-}"

if [ -n "$TARGET_FILE" ]; then
    python3 -m scopelock.cli . --file "$TARGET_FILE"
else
    python3 -m scopelock.cli .
fi
