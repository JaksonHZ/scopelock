"""Canonical import statement calculator across supported languages."""

from pathlib import Path


def calculate_import_statement(
    source_file: Path,
    target_file: Path,
    function_name: str,
    root_dir: Path,
) -> str:
    """
    Calculates the recommended import statement according to the language convention:
    - Python: from module.path import func
    - TypeScript/JavaScript: import { func } from './relative/path';
    - Java: import com.package.ClassName;
    - Ruby: require_relative 'relative/path'
    """
    ext = target_file.suffix.lower()

    if ext in (".ts", ".tsx", ".js", ".jsx", ".mjs"):
        try:
            rel = target_file.resolve().relative_to(source_file.parent.resolve())
            rel_str = str(rel.with_suffix(""))
            if not rel_str.startswith("."):
                rel_str = f"./{rel_str}"
        except ValueError:
            rel_str = f"./{target_file.stem}"
        return f"import {{ {function_name} }} from '{rel_str}';"

    if ext == ".java":
        try:
            for line in target_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("package ") and line.endswith(";"):
                    pkg = line.replace("package ", "").replace(";", "").strip()
                    class_name = target_file.stem
                    return f"import {pkg}.{class_name};"
        except Exception:
            pass
        return f"import {target_file.stem}; // or static import {function_name}"

    if ext == ".rb":
        try:
            rel = target_file.resolve().relative_to(source_file.parent.resolve())
            rel_str = str(rel.with_suffix(""))
        except ValueError:
            rel_str = target_file.stem
        return f"require_relative '{rel_str}'"

    # Default Python style
    try:
        rel_target = target_file.resolve().relative_to(root_dir.resolve())
    except ValueError:
        module_name = target_file.stem
        return f"from {module_name} import {function_name}"

    parts = list(rel_target.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()

    if not parts:
        return f"from . import {function_name}"

    module_path = ".".join(parts)
    return f"from {module_path} import {function_name}"
