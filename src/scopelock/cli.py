"""Interface de Linha de Comando (CLI) para o ScopeLock."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional
from .cache import CacheManager
from .detector import find_duplicates
from .importer import calculate_import_statement
from .parser import FunctionSignature, parse_python_file


# Diretórios padrão que devem ser ignorados na varredura
DEFAULT_IGNORED_DIRS = {
    ".git",
    ".scopelock",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "build",
    "dist",
    "openpost",
}


def scan_directory(target_dir: Path, cache_manager: Optional[CacheManager] = None) -> List[FunctionSignature]:
    """Varre recursivamente uma pasta usando cache incremental para arquivos não modificados."""
    functions: List[FunctionSignature] = []

    for path in target_dir.rglob("*.py"):
        if any(ignored in path.parts for ignored in DEFAULT_IGNORED_DIRS):
            continue

        if cache_manager:
            cached = cache_manager.get_functions_for_file(path)
            if cached is not None:
                functions.extend(cached)
                continue

        parsed = parse_python_file(path)
        functions.extend(parsed)

        if cache_manager:
            cache_manager.update_file_cache(path, parsed)

    if cache_manager:
        cache_manager.save_cache()

    return functions


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ScopeLock — Guardrail anti-overengineering e anti-duplicação para Agentes de IA."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Diretório raiz do projeto a ser analisado (padrão: diretório atual)",
    )
    parser.add_argument(
        "--threshold",
        "-t",
        type=float,
        default=0.65,
        help="Limiar de similaridade para considerar duplicata (0.0 a 1.0, padrão 0.65)",
    )
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        default=None,
        help="Arquivo específico que acabou de ser alterado/criado pelo agente",
    )

    args = parser.parse_args()
    root_path = Path(args.target).resolve()

    if not root_path.exists():
        print(f"Erro: O caminho '{root_path}' não existe.")
        sys.exit(1)

    cache_manager = CacheManager(root_path)
    all_functions = scan_directory(root_path, cache_manager=cache_manager)

    if not all_functions:
        print(f"Nenhum arquivo Python válido encontrado em {root_path}.")
        sys.exit(0)

    if args.file:
        target_file = Path(args.file).resolve()
        new_functions = parse_python_file(target_file)
        # Compara apenas as funções do arquivo contra o restante da base
        other_functions = [f for f in all_functions if f.file_path != target_file]
    else:
        new_functions = all_functions
        other_functions = all_functions

    duplicates = find_duplicates(new_functions, other_functions, threshold=args.threshold)

    # Remove duplicatas espelhadas (A duplica B e B duplica A)
    unique_matches = []
    seen_pairs = set()

    for d in duplicates:
        pair_key = tuple(
            sorted(
                [
                    f"{d.new_func.file_path}:{d.new_func.line_number}",
                    f"{d.existing_func.file_path}:{d.existing_func.line_number}",
                ]
            )
        )
        if pair_key not in seen_pairs:
            seen_pairs.add(pair_key)
            unique_matches.append(d)

    print("\n🔍 ScopeLock: Varredura de AST e Duplicação Funcional")
    print(f"📁 Diretório: {root_path}")
    print(f"📊 Funções analisadas no inventário: {len(all_functions)}")

    if not unique_matches:
        print("\n✅ Nenhuma duplicação funcional ou overengineering detectado!")
        print("O código respeita o princípio de reaproveitamento.\n")
        sys.exit(0)

    print(f"\n⚠️  Atenção: {len(unique_matches)} potencial(is) duplicação(ões) encontrada(s):\n")

    for i, match in enumerate(unique_matches, 1):
        rel_new = match.new_func.file_path.relative_to(root_path)
        rel_exist = match.existing_func.file_path.relative_to(root_path)

        import_stmt = calculate_import_statement(
            source_file=match.new_func.file_path,
            target_file=match.existing_func.file_path,
            function_name=match.existing_func.name,
            root_dir=root_path,
        )

        pct = int(match.similarity_score * 100)
        print(f"[{i}] {pct}% similaridade — {match.reason}")
        print(f"    ❌ Função:   '{match.new_func.name}' em {rel_new}:{match.new_func.line_number}")
        print(f"    💡 Já existe: '{match.existing_func.name}' em {rel_exist}:{match.existing_func.line_number}")
        print(f"    👉 Sugestão: Reaproveite importando:")
        print(f"       {import_stmt}\n")

    sys.exit(1)


if __name__ == "__main__":
    main()
