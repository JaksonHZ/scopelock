"""Calculador de statements de importação canônicos e relativos."""

from pathlib import Path


def calculate_import_statement(
    source_file: Path,
    target_file: Path,
    function_name: str,
    root_dir: Path,
) -> str:
    """
    Calcula a declaração de import recomendada:
    1. Tenta import canônico absoluto baseado na raiz do projeto (ex: from utils.strings import slugify)
    2. Se os arquivos estiverem na mesma pasta: from .strings import slugify
    """
    try:
        rel_target = target_file.resolve().relative_to(root_dir.resolve())
    except ValueError:
        # Fora da raiz, usa nome do arquivo
        module_name = target_file.stem
        return f"from {module_name} import {function_name}"

    # Remove extensão .py
    parts = list(rel_target.with_suffix("").parts)

    # Se for __init__.py, o módulo é o nome do diretório pai
    if parts and parts[-1] == "__init__":
        parts.pop()

    if not parts:
        return f"from . import {function_name}"

    module_path = ".".join(parts)
    return f"from {module_path} import {function_name}"
