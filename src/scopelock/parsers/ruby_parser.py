"""Parser for Ruby source code (.rb)."""

import re
from pathlib import Path
from typing import List, Set
from .base import BaseParser, FunctionSignature


class RubyParser(BaseParser):
    """
    Parser for Ruby files (.rb):
    - Captures instance and class method declarations: def method_name or def self.method_name
    - Extracts preceding Ruby comments (# ...)
    """

    @property
    def supported_extensions(self) -> Set[str]:
        return {".rb"}

    def parse_file(self, file_path: Path) -> List[FunctionSignature]:
        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return []

        functions: List[FunctionSignature] = []
        lines = content.splitlines()

        method_pattern = re.compile(
            r"^\s*def\s+(?:self\.)?([A-Za-z0-9_!?]+)(?:\s*\(([^)]*)\)|\s+([A-Za-z0-9_,\s=:]+))?"
        )

        for line_idx, line in enumerate(lines):
            clean_line = line.strip()
            if not clean_line or clean_line.startswith("#"):
                continue

            match = method_pattern.match(clean_line)
            if match:
                method_name = match.group(1).strip()
                raw_params = match.group(2) or match.group(3) or ""

                params = []
                if raw_params:
                    for p in raw_params.split(","):
                        param_name = p.strip().split("=")[0].split(":")[0].strip()
                        if param_name and not param_name.startswith("&") and not param_name.startswith("*"):
                            params.append(param_name)

                docstring = None
                if line_idx > 0:
                    prev_line = lines[line_idx - 1].strip()
                    if prev_line.startswith("#"):
                        docstring = prev_line.lstrip("#").strip()

                body_tokens = []
                if ".each" in clean_line or ".map" in clean_line or "for " in clean_line:
                    body_tokens.append("IterationPattern")
                if "if " in clean_line or "unless " in clean_line or "?" in clean_line:
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
                        language="ruby",
                    )
                )

        return functions
