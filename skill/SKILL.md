---
name: scopelock
description: Architectural guardrail preventing functional duplication and code bloat by inspecting syntax trees across Python, TypeScript, Java, and Ruby.
---

# ScopeLock — Architectural Guardrail for AI Agents

ScopeLock empowers AI coding agents to proactively verify whether a utility function already exists before writing redundant code from scratch.

## Guiding Principle: Advisory First, Never Block Blindly

ScopeLock acts as an **architectural advisor**, not a blind roadblock. 

- **Confidence Tiers:**
  - `⛔ CRITICAL DUPLICATE` ($\ge 90\%$ similarity): High-confidence duplicate (identical names/parameters/AST flow). You should almost certainly remove your function and import the existing one.
  - `💡 ADVISORY / WARNING` ($< 90\%$ similarity): A similar utility exists, but verify whether your domain logic is actually distinct. If your business requirements differ, you are permitted to proceed.

## How to Execute

### 1. Inspect a specific file you just modified (Recommended)
Before proposing or finalizing changes:

```bash
python3 -m scopelock.cli . --file path/to/changed_file.py
```

### 2. Inspect in Non-Blocking Mode (Advisory Only)
If you want suggestions without blocking exit codes:

```bash
python3 -m scopelock.cli . --warn-only
```

### 3. Allow Specific Intentional Functions
If a function intentionally shares an interface with another domain module:

```bash
python3 -m scopelock.cli . --allow function_name_to_keep
```

## What to Do When Duplicates Are Detected

If ScopeLock outputs:
```
[1] ⛔ CRITICAL DUPLICATE (99% similarity)
    ❌ Candidate:  'format_currency_brl' in agent_code.py:13
    💡 Already in: 'format_currency_br' in utils/finance.py:6
    👉 Recommendation: Reuse by importing:
       from utils.finance import format_currency_br
```

**Standard Action:**
1. Check if the existing utility (`format_currency_br`) satisfies your requirements.
2. If yes: delete your duplicate function and add the suggested import statement.
3. If no (business logic genuinely differs): re-run with `--warn-only` or `--allow <func>` and document why the separation is intentional.
