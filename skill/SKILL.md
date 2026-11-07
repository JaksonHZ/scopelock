---
name: scopelock
description: Prevents overengineering, functional duplication, and code bloat by inspecting the syntax tree before writing new utilities.
---

# ScopeLock — Anti-Overengineering Guardrail for AI Agents

This skill empowers coding agents to proactively verify whether a function or utility they plan to create already exists in the codebase, preventing unnecessary duplication.

## When to Use This Skill

Activate and use ScopeLock whenever:
1. You are about to author a new helper or utility function (e.g. string formatting, mathematical calculations, validators, date helpers, API wrappers).
2. You are preparing to save or propose changes across new or modified files.
3. You want to verify that the repository stays clean before finalizing a coding task.

## How to Execute

### 1. Inspect a specific file you just created or modified
Before completing your task, run:

```bash
python3 -m scopelock.cli . --file path/to/changed_file.py
```

### 2. Inspect the entire project
```bash
python3 -m scopelock.cli .
```

### 3. What to do when duplicates are found?
If ScopeLock reports:
```
⚠️  Warning: 1 potential duplicate detected:
    ❌ Function:   'format_date' in new_module.py
    💡 Already in: 'format_timestamp' in utils/dates.py
    👉 Recommendation: Reuse by importing:
       from utils.dates import format_timestamp
```

**Required Action:**
- Delete the redundant function you just created.
- Import the existing function: `from utils.dates import format_timestamp`.
- Update your code to call the imported helper.
