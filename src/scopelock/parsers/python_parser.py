"""Native Python parser based on standard AST."""

import ast
from pathlib import Path
from typing import List, Set
from .base import BaseParser, FunctionSignature


def normalize_statement_type(stmt: ast.stmt) -> str:
    """Normalizes functionally equivalent statements."""
    if isinstance(stmt, (ast.For, ast.AsyncFor)):
        return "IterationPattern"
    if isinstance(stmt, ast.If):
        return "BranchPattern"
    if isinstance(stmt, ast.Return):
        val = getattr(stmt, "value", None)
        if isinstance(val, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
            return "IterationPattern"
        if isinstance(val, ast.IfExp):
            return "BranchPattern"
        return "Return"
    return type(stmt).__name__


class _ASTVisitor(ast.NodeVisitor):
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.functions: List[FunctionSignature] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record_function(node)
        self.generic_visit(node)

    def _record_function(self, node) -> None:
        params = tuple(arg.arg for arg in node.args.args if arg.arg not in ("self", "cls"))
        docstring = ast.get_docstring(node)
        node_count = sum(1 for _ in ast.walk(node))

        body_stmts = [
            s for s in node.body
            if not (isinstance(s, ast.Expr) and isinstance(getattr(s, "value", None), ast.Constant) and isinstance(s.value.value, str))
        ]
        normalized_repr = "-".join(normalize_statement_type(stmt) for stmt in body_stmts)

        self.functions.append(
            FunctionSignature(
                name=node.name,
                file_path=self.file_path,
                line_number=node.lineno,
                params=params,
                docstring=docstring,
                body_node_count=node_count,
                normalized_body=normalized_repr,
                language="python",
            )
        )


class PythonParser(BaseParser):
    """Parser for Python source files (.py)."""

    @property
    def supported_extensions(self) -> Set[str]:
        return {".py"}

    def parse_file(self, file_path: Path) -> List[FunctionSignature]:
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            visitor = _ASTVisitor(file_path)
            visitor.visit(tree)
            return visitor.functions
        except (SyntaxError, UnicodeDecodeError):
            return []
