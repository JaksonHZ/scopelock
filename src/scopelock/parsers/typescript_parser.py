"""Parser para TypeScript e JavaScript (.ts, .tsx, .js, .jsx)."""

import re
from pathlib import Path
from typing import List, Set
from .base import BaseParser, FunctionSignature


class TypeScriptParser(BaseParser):
    """
    Parser robusto para ecossistema JS/TS sem dependências externas:
    - Funções nomeadas (function name(a, b))
    - Arrow functions e function expressions (const name = (a, b) => ...)
    - Métodos de classes (name(a, b) { ... })
    """

    @property
    def supported_extensions(self) -> Set[str]:
        return {".ts", ".tsx", ".js", ".jsx", ".mjs"}

    def parse_file(self, file_path: Path) -> List[FunctionSignature]:
        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return []

        functions: List[FunctionSignature] = []
        lines = content.splitlines()

        # Regex para capturar declarações de funções e arrow functions
        func_patterns = [
            # 1. function name(params)
            re.compile(
                r"^(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_$]+)\s*(?:<[^>]*>)?\s*\(([^)]*)\)"
            ),
            # 2. const/let/var name = (params) => ou function(...)
            re.compile(
                r"^(?:export\s+)?(?:const|let|var)\s+([A-Za-z0-9_$]+)\s*=\s*(?:async\s*)?(?:\(([^)]*)\)|([A-Za-z0-9_$]+))\s*(?::\s*[^=]+)?\s*=>"
            ),
            # 3. Métodos: name(params): returnType {
            re.compile(
                r"^\s*(?:(?:public|private|protected|static|async)\s+)*([A-Za-z0-9_$]+)\s*(?:<[^>]*>)?\s*\(([^)]*)\)\s*(?::\s*[^{]+)?\s*\{"
            ),
        ]

        for line_idx, line in enumerate(lines):
            clean_line = line.strip()
            if not clean_line or clean_line.startswith("//") or clean_line.startswith("/*"):
                continue

            for pattern in func_patterns:
                match = pattern.match(clean_line)
                if match:
                    func_name = match.group(1)
                    raw_params = match.group(2) if match.lastindex >= 2 and match.group(2) else ""

                    # Ignora palavras reservadas ou construtores de teste
                    if func_name in ("if", "for", "while", "switch", "catch", "describe", "it", "test"):
                        continue

                    # Extrai os nomes dos parâmetros limpando tipos do TS
                    params = []
                    if raw_params:
                        for p in raw_params.split(","):
                            clean_p = p.strip().split(":")[0].strip().split("=")[0].strip()
                            if clean_p and clean_p != "...args":
                                params.append(clean_p)

                    # Tenta capturar JSDoc nas linhas anteriores
                    docstring = None
                    if line_idx > 0:
                        prev_line = lines[line_idx - 1].strip()
                        if "*/" in prev_line or prev_line.startswith("*"):
                            docstring = prev_line.replace("*/", "").replace("*", "").strip()

                    # Estimativa de fluxo sintático
                    body_tokens = []
                    if "return" in clean_line:
                        body_tokens.append("Return")
                    if ".map(" in clean_line or ".filter(" in clean_line or "for (" in clean_line:
                        body_tokens.append("IterationPattern")
                    if "?" in clean_line or "if (" in clean_line:
                        body_tokens.append("BranchPattern")

                    functions.append(
                        FunctionSignature(
                            name=func_name,
                            file_path=file_path,
                            line_number=line_idx + 1,
                            params=tuple(params),
                            docstring=docstring,
                            body_node_count=len(clean_line),
                            normalized_body="-".join(body_tokens) if body_tokens else "Block",
                            language="typescript" if file_path.suffix in (".ts", ".tsx") else "javascript",
                        )
                    )
                    break

        return functions
