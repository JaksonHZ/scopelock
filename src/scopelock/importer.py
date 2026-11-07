"""Calculador de statements de importação canônicos e relativos."""

from pathlib import Path


def calculate_import_statement(
    source_file: Path,
    target_file: Path,
    function_name: str,
    root_dir: Path,
) -> str:
    """
    Calcula o statement de importação adequado para a linguagem:
    - Python: from module.path import func
    - TypeScript/JavaScript: import { func } from './relative/path';
    """
    ext = target_file.suffix.lower()

    if ext in (".ts", ".tsx", ".js", ".jsx", ".mjs"):
        # Import relativo para JS/TS
        try:
            rel = target_file.resolve().relative_to(source_file.parent.resolve())
            rel_str = str(rel.with_suffix(""))
            if not rel_str.startswith("."):
                rel_str = f"./{rel_str}"
        except ValueError:
            rel_str = f"./{target_file.stem}"
        return f"import {{ {function_name} }} from '{rel_str}';"

    # Padrão Python
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
