"""Unified parser registry routing files by extension."""

from pathlib import Path
from typing import Dict, List, Set
from .base import BaseParser, FunctionSignature
from .java_parser import JavaParser
from .python_parser import PythonParser
from .ruby_parser import RubyParser
from .typescript_parser import TypeScriptParser


class ParserRegistry:
    """Registers language parsers by extension and directs files automatically."""

    def __init__(self):
        self._parsers: Dict[str, BaseParser] = {}
        self.register(PythonParser())
        self.register(TypeScriptParser())
        self.register(JavaParser())
        self.register(RubyParser())

    def register(self, parser: BaseParser) -> None:
        """Registers a parser for its supported file extensions."""
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


# Default global registry instance
default_registry = ParserRegistry()
