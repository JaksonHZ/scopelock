"""Ponto de entrada de compatibilidade para assinaturas e parsing."""

from .parsers.base import BaseParser, FunctionSignature
from .parsers.python_parser import PythonParser
from .parsers.typescript_parser import TypeScriptParser
from .parsers import default_registry


def parse_python_file(file_path):
    """Wrapper de compatibilidade para arquivos Python."""
    return default_registry.parse_file(file_path)

