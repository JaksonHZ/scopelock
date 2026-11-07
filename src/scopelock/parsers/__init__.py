"""Roteador e registro unificado de parsers por extensão de arquivo."""

from pathlib import Path
from typing import Dict, List, Set
from .base import BaseParser, FunctionSignature
from .python_parser import PythonParser
from .typescript_parser import TypeScriptParser


class ParserRegistry:
    """Registra parsers por extensão e direciona os arquivos automaticamente."""

    def __init__(self):
        self._parsers: Dict[str, BaseParser] = {}
        # Registra parsers padrão
        self.register(PythonParser())
        self.register(TypeScriptParser())

    def register(self, parser: BaseParser) -> None:
        """Registra um parser para suas respectivas extensões."""
        for ext in parser.supported_extensions:
            self._parsers[ext.lower()] = parser

    @property
    def supported_extensions(self) -> Set[str]:
        return set(self._parsers.keys())

    def parse_file(self, file_path: Path) -> List[FunctionSignature]:
        ext = file_path.suffix.lower()
        parser = self._parsers.get(ext)
        if not parser:
            return []
        return parser.parse_file(file_path)


# Instância global padrão
default_registry = ParserRegistry()
