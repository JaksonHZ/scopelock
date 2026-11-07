"""Definições e contratos base para parsers agnósticos de linguagem."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Set


@dataclass(frozen=True)
class FunctionSignature:
    """Representação unificada de uma função, agnóstica de linguagem."""

    name: str
    file_path: Path
    line_number: int
    params: tuple[str, ...]
    docstring: Optional[str]
    body_node_count: int
    normalized_body: str
    language: str  # ex: "python", "typescript", "javascript", "go"


class BaseParser(ABC):
    """Contrato base para qualquer parser de linguagem no ScopeLock."""

    @property
    @abstractmethod
    def supported_extensions(self) -> Set[str]:
        """Extensões suportadas por este parser (ex: {'.py'} ou {'.ts', '.tsx', '.js'})."""
        pass

    @abstractmethod
    def parse_file(self, file_path: Path) -> list[FunctionSignature]:
        """Lê e extrai funções e métodos do arquivo."""
        pass
