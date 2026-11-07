#!/usr/bin/env bash
# ScopeLock pre-commit hook
# Impede que agentes ou commits humanos introduzam duplicação funcional

set -e

# Obtém arquivos Python em staged
STAGED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)

if [ -z "$STAGED_PY_FILES" ]; then
    exit 0
fi

echo "🔒 ScopeLock: Verificando duplicação e overengineering nos arquivos alterados..."

for file in $STAGED_PY_FILES; do
    if [ -f "$file" ]; then
        python3 -m scopelock.cli . --file "$file"
    fi
done

echo "✅ ScopeLock: Código limpo e sem duplicação de utilitários!"
exit 0
