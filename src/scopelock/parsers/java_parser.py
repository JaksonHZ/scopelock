"""Parser para código Java (.java)."""

import re
from pathlib import Path
from typing import List, Set
from .base import BaseParser, FunctionSignature


class JavaParser(BaseParser):
    """
    Parser para arquivos Java (.java):
    - Captura declarações de métodos: [modificadores] [tipo_retorno] nomeMetodo([parametros]) {
    - Captura o nome da classe ou package para imports canônicos
    - Extrai comentários Javadoc prévios
    """

    @property
    def supported_extensions(self) -> Set[str]:
        return {".java"}

    def parse_file(self, file_path: Path) -> List[FunctionSignature]:
        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return []

        functions: List[FunctionSignature] = []
        lines = content.splitlines()

        # Regex para declaração de métodos em Java
        # Ex: public static String slugifyText(String text, boolean strict) {
        # Ex: private List<User> getActiveUsers() throws Exception {
        method_pattern = re.compile(
            r"^\s*(?:(?:public|protected|private|static|final|synchronized|abstract|default)\s+)+"
            r"(?:<[^>]+>\s+)?"  # genéricos ex: <T>
            r"([A-Za-z0-9_<>\[\],\s?]+)\s+"  # tipo de retorno
            r"([A-Za-z0-9_]+)\s*"  # nome do método
            r"\(([^)]*)\)"  # parâmetros
            r"(?:\s*throws\s+[A-Za-z0-9_,\s]+)?"  # throws
            r"\s*\{?"
        )

        # Palavras reservadas que não são métodos
        keywords_blacklist = {"if", "for", "while", "switch", "catch", "synchronized"}

        for line_idx, line in enumerate(lines):
            clean_line = line.strip()
            if not clean_line or clean_line.startswith("//") or clean_line.startswith("/*"):
                continue

            match = method_pattern.match(clean_line)
            if match:
                return_type = match.group(1).strip()
                method_name = match.group(2).strip()
                raw_params = match.group(3).strip()

                if method_name in keywords_blacklist or return_type in ("class", "interface", "enum", "record"):
                    continue

                # Extrai apenas os nomes das variáveis nos parâmetros Java (ex: "String text, int limit" -> ("text", "limit"))
                params = []
                if raw_params:
                    for p in raw_params.split(","):
                        parts = p.strip().split()
                        if parts:
                            # O último token é o nome do parâmetro
                            param_name = parts[-1].replace("...", "")
                            if param_name:
                                params.append(param_name)

                # Captura Javadoc imediatamente anterior se existir
                docstring = None
                if line_idx > 0:
                    prev_line = lines[line_idx - 1].strip()
                    if "*/" in prev_line or prev_line.startswith("*"):
                        docstring = prev_line.replace("*/", "").replace("*", "").strip()

                # Estimativa de fluxo sintático
                body_tokens = []
                if "return" in clean_line:
                    body_tokens.append("Return")
                if "for (" in clean_line or ".forEach(" in clean_line or ".stream(" in clean_line:
                    body_tokens.append("IterationPattern")
                if "if (" in clean_line or "?" in clean_line:
                    body_tokens.append("BranchPattern")

                functions.append(
                    FunctionSignature(
                        name=method_name,
                        file_path=file_path,
                        line_number=line_idx + 1,
                        params=tuple(params),
                        docstring=docstring,
                        body_node_count=len(clean_line),
                        normalized_body="-".join(body_tokens) if body_tokens else "Block",
                        language="java",
                    )
                )

        return functions
