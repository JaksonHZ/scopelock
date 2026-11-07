"""Base definitions and contracts for language-agnostic parsers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Set


@dataclass(frozen=True)
class FunctionSignature:
    """Unified, language-agnostic representation of a function or method."""

    name: str
    file_path: Path
    line_number: int
    params: tuple[str, ...]
    docstring: Optional[str]
    body_node_count: int
    normalized_body: str
    language: str  # e.g., "python", "typescript", "javascript", "java", "ruby"


class BaseParser(ABC):
    """Abstract contract for all language parsers in ScopeLock."""

    @property
    @abstractmethod
    def supported_extensions(self) -> Set[str]:
        """Supported file extensions (e.g. {'.py'} or {'.ts', '.tsx'})."""
        pass

    @abstractmethod
    def parse_file(self, file_path: Path) -> list[FunctionSignature]:
        """Reads and extracts function signatures from the given file."""
        pass
