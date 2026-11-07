"""Extrator de assinaturas e nós de funções usando AST padrão do Python."""

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class FunctionSignature:
    """Representação estruturada de uma função encontrada no código."""

    name: str
    file_path: Path
    line_number: int
    params: List[str]
    docstring: Optional[str]
    body_node_count: int
    normalized_body: str


class ASTParser(ast.NodeVisitor):
    """Varre a AST de um arquivo Python coletando funções e métodos."""

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
        params = [arg.arg for arg in node.args.args if arg.arg not in ("self", "cls")]
        docstring = ast.get_docstring(node)

        # Contagem de nós AST dentro do corpo da função (mede complexidade/tamanho estrutural)
        node_count = sum(1 for _ in ast.walk(node))

        # Cria uma representação normalizada da árvore AST do corpo (ignorando docstring)
        body_stmts = [
            s for s in node.body
            if not (isinstance(s, ast.Expr) and isinstance(getattr(s, "value", None), ast.Constant) and isinstance(s.value.value, str))
        ]
        normalized_repr = "-".join(type(stmt).__name__ for stmt in body_stmts)

        self.functions.append(
            FunctionSignature(
                name=node.name,
                file_path=self.file_path,
                line_number=node.lineno,
                params=params,
                docstring=docstring,
                body_node_count=node_count,
                normalized_body=normalized_repr,
            )
        )


def parse_python_file(file_path: Path) -> List[FunctionSignature]:
    """Lê e analisa um arquivo Python retornando as assinaturas encontradas."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
        parser = ASTParser(file_path)
        parser.visit(tree)
        return parser.functions
    except (SyntaxError, UnicodeDecodeError):
        # Ignora arquivos com erros de sintaxe ou codificação não-UTF8
        return []
