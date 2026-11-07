"""Command Line Interface (CLI) for ScopeLock."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional
from .cache import CacheManager
from .detector import find_duplicates
from .importer import calculate_import_statement
from .parsers import default_registry
from .parsers.base import FunctionSignature


# Directories ignored during repository scans by default
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
    "target",
    "openpost",
}


def scan_directory(target_dir: Path, cache_manager: Optional[CacheManager] = None) -> List[FunctionSignature]:
    """Recursively scans directory across supported languages using incremental caching."""
    functions: List[FunctionSignature] = []
    supported_extensions = default_registry.supported_extensions

    for path in target_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in supported_extensions:
            continue
        if any(ignored in path.parts for ignored in DEFAULT_IGNORED_DIRS):
            continue

        if cache_manager:
            cached = cache_manager.get_functions_for_file(path)
            if cached is not None:
                functions.extend(cached)
                continue

        parsed = default_registry.parse_file(path)
        functions.extend(parsed)

        if cache_manager:
            cache_manager.update_file_cache(path, parsed)

    if cache_manager:
        cache_manager.save_cache()

    return functions


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ScopeLock — Anti-overengineering and code deduplication guardrail for AI coding agents."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Root directory of the project to analyze (default: current directory)",
    )
    parser.add_argument(
        "--threshold",
        "-t",
        type=float,
        default=0.65,
        help="Similarity sensitivity threshold (0.0 to 1.0, default: 0.65)",
    )
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        default=None,
        help="Target file to inspect (e.g. file modified by an AI agent)",
    )

    args = parser.parse_args()
    root_path = Path(args.target).resolve()

    if not root_path.exists():
        print(f"Error: Path '{root_path}' does not exist.")
        sys.exit(1)

    cache_manager = CacheManager(root_path)
    all_functions = scan_directory(root_path, cache_manager=cache_manager)

    if not all_functions:
        print(f"No supported source files found in {root_path}.")
        sys.exit(0)

    if args.file:
        target_file = Path(args.file).resolve()
        new_functions = default_registry.parse_file(target_file)
        other_functions = [f for f in all_functions if f.file_path != target_file]
    else:
        new_functions = all_functions
        other_functions = all_functions

    duplicates = find_duplicates(new_functions, other_functions, threshold=args.threshold)

    # Filter mirrored duplicates (A -> B and B -> A)
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

    print("\n🔍 ScopeLock: AST & Functional Deduplication Scan")
    print(f"📁 Target directory: {root_path}")
    print(f"📊 Functions analyzed in inventory: {len(all_functions)}")

    if not unique_matches:
        print("\n✅ Clean! No functional duplication or overengineering detected.")
        print("Codebase adheres to reuse principles.\n")
        sys.exit(0)

    print(f"\n⚠️  Warning: {len(unique_matches)} potential duplicate(s) detected:\n")

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
        print(f"[{i}] {pct}% similarity — {match.reason}")
        print(f"    ❌ Function:   '{match.new_func.name}' in {rel_new}:{match.new_func.line_number}")
        print(f"    💡 Already in: '{match.existing_func.name}' in {rel_exist}:{match.existing_func.line_number}")
        print(f"    👉 Recommendation: Reuse by importing:")
        print(f"       {import_stmt}\n")

    sys.exit(1)


if __name__ == "__main__":
    main()
