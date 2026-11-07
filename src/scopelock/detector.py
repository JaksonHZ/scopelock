"""Detector de duplicação funcional e similaridade estrutural."""

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import List, Optional
from .parser import FunctionSignature


@dataclass
class DuplicateMatch:
    """Representa uma duplicata ou semelhança identificada."""

    new_func: FunctionSignature
    existing_func: FunctionSignature
    similarity_score: float
    reason: str


def _clean_name(name: str) -> str:
    """Normaliza nome de função (snake_case/camelCase para tokens)."""
    # Converte camelCase para snake_case
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    return s2.replace("_", "")


def calculate_similarity(f1: FunctionSignature, f2: FunctionSignature) -> tuple[float, str]:
    """
    Compara duas funções por:
    1. Nome exato ou normalizado (ex: format_date vs formatDate)
    2. Correspondência de parâmetros e estrutura AST
    3. Docstrings similares
    """
    if f1.file_path == f2.file_path and f1.line_number == f2.line_number:
        return 0.0, ""

    reasons = []
    score = 0.0

    # 1. Correspondência de Nome
    if f1.name == f2.name:
        score += 0.6
        reasons.append(f"Mesmo nome exato '{f1.name}'")
    elif _clean_name(f1.name) == _clean_name(f2.name):
        score += 0.5
        reasons.append(f"Nomes semanticamente idênticos ('{f1.name}' e '{f2.name}')")
    else:
        name_ratio = SequenceMatcher(None, f1.name, f2.name).ratio()
        if name_ratio > 0.75:
            score += 0.35 * name_ratio
            reasons.append(f"Nomes muito próximos ({int(name_ratio * 100)}% de similaridade)")

    # 2. Correspondência de Parâmetros
    if f1.params and f2.params:
        if f1.params == f2.params:
            score += 0.25
            reasons.append("Mesma lista de parâmetros")
        else:
            shared = set(f1.params).intersection(set(f2.params))
            if len(shared) >= min(len(f1.params), len(f2.params)):
                score += 0.15
                reasons.append(f"Parâmetros coincidentes ({', '.join(shared)})")

    # 3. Correspondência Estrutural da AST
    if f1.normalized_body and f2.normalized_body:
        if f1.normalized_body == f2.normalized_body:
            score += 0.2
            reasons.append("Mesmo fluxo de instruções sintáticas (AST)")

    # 4. Docstring similaridade
    if f1.docstring and f2.docstring:
        doc_ratio = SequenceMatcher(None, f1.docstring.strip(), f2.docstring.strip()).ratio()
        if doc_ratio > 0.6:
            score += 0.2
            reasons.append(f"Docstrings com {int(doc_ratio*100)}% de semelhança")

    total_score = min(score, 1.0)
    return total_score, " + ".join(reasons)


def find_duplicates(
    new_functions: List[FunctionSignature],
    existing_functions: List[FunctionSignature],
    threshold: float = 0.65,
) -> List[DuplicateMatch]:
    """Identifica novas funções que duplicam ou reimplementam utilitários já existentes."""
    matches = []

    for new_f in new_functions:
        best_match: Optional[DuplicateMatch] = None
        max_score = 0.0

        for exist_f in existing_functions:
            # Não compara com a própria função
            if new_f.file_path == exist_f.file_path and new_f.line_number == exist_f.line_number:
                continue

            score, reason = calculate_similarity(new_f, exist_f)
            if score >= threshold and score > max_score:
                max_score = score
                best_match = DuplicateMatch(
                    new_func=new_f,
                    existing_func=exist_f,
                    similarity_score=score,
                    reason=reason,
                )

        if best_match:
            matches.append(best_match)

    return matches
