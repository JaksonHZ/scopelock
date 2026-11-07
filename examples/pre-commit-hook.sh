#!/usr/bin/env bash
# ScopeLock pre-commit hook
# Prevents AI agents or human commits from introducing functional duplication

set -e

# Gather staged files across supported extensions
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|ts|tsx|js|jsx|mjs|java|rb)$' || true)

if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

echo "🔒 ScopeLock: Checking for functional duplication across staged files..."

for file in $STAGED_FILES; do
    if [ -f "$file" ]; then
        python3 -m scopelock.cli . --file "$file"
    fi
done

echo "✅ ScopeLock: Codebase is clean and free of duplicate utilities!"
exit 0
