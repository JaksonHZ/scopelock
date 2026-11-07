"""Gerenciador de cache incremental para varredura ultra-rápida de AST."""

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional
from .parser import FunctionSignature


CACHE_DIR_NAME = ".scopelock"
CACHE_FILE_NAME = "index.json"


def get_file_hash(path: Path) -> str:
    """Calcula hash sha256 simples e mtime do arquivo para detecção rápida de alteração."""
    stat = path.stat()
    hasher = hashlib.sha256()
    hasher.update(f"{stat.st_mtime}-{stat.st_size}".encode("utf-8"))
    return hasher.hexdigest()


class CacheManager:
    """Armazena assinaturas de funções parseadas e invalida apenas arquivos modificados."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.cache_dir = root_dir / CACHE_DIR_NAME
        self.cache_file = self.cache_dir / CACHE_FILE_NAME
        self.data: Dict[str, dict] = self._load_cache()

    def _load_cache(self) -> Dict[str, dict]:
        if not self.cache_file.exists():
            return {}
        try:
            return json.loads(self.cache_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save_cache(self) -> None:
        """Persiste o índice no disco."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        # Salva o arquivo de cache ignorando se falhar
        try:
            self.cache_file.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
        except Exception:
            pass

    def get_functions_for_file(self, file_path: Path) -> Optional[List[FunctionSignature]]:
        """Retorna funções do cache se o arquivo não tiver sido modificado."""
        rel_path = str(file_path.relative_to(self.root_dir))
        entry = self.data.get(rel_path)
        if not entry:
            return None

        current_hash = get_file_hash(file_path)
        if entry.get("hash") != current_hash:
            return None  # Arquivo modificado, precisa de re-parse

        cached_funcs = []
        for f in entry.get("functions", []):
            cached_funcs.append(
                FunctionSignature(
                    name=f["name"],
                    file_path=file_path,
                    line_number=f["line_number"],
                    params=tuple(f["params"]),
                    docstring=f.get("docstring"),
                    body_node_count=f.get("body_node_count", 0),
                    normalized_body=f.get("normalized_body", ""),
                    language=f.get("language", "python"),
                )
            )
        return cached_funcs

    def update_file_cache(self, file_path: Path, functions: List[FunctionSignature]) -> None:
        """Atualiza a entrada de cache de um arquivo."""
        rel_path = str(file_path.relative_to(self.root_dir))
        serialized_funcs = []
        for f in functions:
            d = asdict(f)
            d["file_path"] = str(file_path)
            serialized_funcs.append(d)

        self.data[rel_path] = {
            "hash": get_file_hash(file_path),
            "functions": serialized_funcs,
        }
