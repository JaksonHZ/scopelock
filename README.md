# ScopeLock 🔒

> **Zero-dependency, multi-language anti-overengineering and code deduplication guardrail for AI coding agents.**

Autonomous coding agents (Claude Code, Cursor, Aider, Copilot Workspace) share a common habit: **they love reinventing the wheel**. Whenever they need a utility helper (such as string slugification, currency formatting, or date normalization), most models generate a brand-new function from scratch instead of reusing existing helpers in `utils/` or `helpers/`, bloating the repository with redundant code.

**ScopeLock** analyzes your project's syntax tree and serves as a pre-commit guardrail. It supports multiple ecosystems (**Python, TypeScript, JavaScript, Java, and Ruby**) without external configuration files or heavy dependencies. When an agent attempts to reimplement an existing utility, ScopeLock blocks the change and generates the exact canonical import statement required to reuse it.

---

## 🎯 Key Features

1. **Zero External Dependencies:** Built with pure Python standard libraries. Lightweight, instant execution (< 50ms).
2. **Multi-Language Support:** Analyzes Python (`.py`), TypeScript (`.ts`, `.tsx`), JavaScript (`.js`, `.jsx`), Java (`.java`), and Ruby (`.rb`).
3. **Language-Specific Canonical Imports:** Automatically formats imports in the target language's idiomatic style:
   - Python: `from module.utils import func`
   - TypeScript/JavaScript: `import { func } from './utils';`
   - Java: `import com.example.utils.StringUtils;`
   - Ruby: `require_relative 'format_utils'`
4. **AST Normalization:** Canonicalizes functional equivalents (e.g. comprehensions vs for-loops with appends) to catch semantically identical implementations.
5. **Incremental Cache:** Persists a lightweight signature index in `.scopelock/index.json` to scan massive codebases incrementally without re-parsing unchanged files.
6. **Agent Skill Ready:** Includes an out-of-the-box `SKILL.md` manifest so coding agents can self-inspect code before proposing changes.

---

## 🚀 Getting Started

### 1. Scan the Entire Repository

```bash
# Scan the current directory
python3 -m scopelock.cli .

# Adjust the similarity sensitivity threshold (0.0 to 1.0, default: 0.65)
python3 -m scopelock.cli . --threshold 0.75
```

### 2. Inspect Changed Files Only (Targeted Scan)

```bash
python3 -m scopelock.cli . --file src/new_module.py
```

### 3. As an AI Agent Skill

ScopeLock includes a standard skill definition (`skill/SKILL.md`) compatible with agent harnesses (Antigravity, Claude Code, Cursor, OpenCode):

- Agents can execute `skill/scripts/check.sh` to self-inspect their work before finalizing tasks.
- If redundant functions are detected, the agent is instructed to remove the duplicate and insert the recommended import.

### 4. As a Git Pre-commit Hook

Copy the sample hook to your `.git/hooks` directory:

```bash
cp examples/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

---

## 🧪 Real-World Example

Suppose your repository already has `existing_utils.py` containing `slugify()`. An AI agent then creates `agent_duplicated_code.py` with `slugify_text()`:

```bash
$ python3 -m scopelock.cli examples/

🔍 ScopeLock: AST & Functional Deduplication Scan
📁 Target directory: /home/jakson/pessoal/scopelock/examples
📊 Functions analyzed in inventory: 14

⚠️  Warning: 4 potential duplicate(s) detected:

[1] 99% similarity — Very close names (97% match) + Identical parameters + Matching AST flow
    ❌ Function:   'format_currency_br' in existing_utils.py:13
    💡 Already in: 'format_currency_brl' in agent_duplicated_code.py:13
    👉 Recommendation: Reuse by importing:
       from agent_duplicated_code import format_currency_brl

[2] 76% similarity — Close names (90% match) + Identical parameters + Matching AST flow
    ❌ Function:   'formatCurrencyBRL' in existing_utils.ts:4
    💡 Already in: 'formatCurrency' in agent_duplicated_code.ts:4
    👉 Recommendation: Reuse by importing:
       import { formatCurrency } from './agent_duplicated_code';
```

---

## 📄 License

MIT License — feel free to use, modify, and distribute.
