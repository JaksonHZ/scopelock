"""Backward compatibility entry point for function signatures and parsing."""

from .parsers.base import BaseParser, FunctionSignature
from .parsers.python_parser import PythonParser
from .parsers.typescript_parser import TypeScriptParser
from .parsers.java_parser import JavaParser
from .parsers.ruby_parser import RubyParser
from .parsers import default_registry


def parse_python_file(file_path):
    """Backward compatibility helper for parsing Python files."""
    return default_registry.parse_file(file_path)
