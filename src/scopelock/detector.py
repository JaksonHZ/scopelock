"""Similarity and functional deduplication detector."""

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import List, Optional
from .parsers.base import FunctionSignature


@dataclass
class DuplicateMatch:
    """Represents an identified function duplicate or close match."""

    new_func: FunctionSignature
    existing_func: FunctionSignature
    similarity_score: float
    reason: str


def _clean_name(name: str) -> str:
    """Normalizes function identifiers (camelCase/snake_case to normalized token)."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    return s2.replace("_", "")


def calculate_similarity(f1: FunctionSignature, f2: FunctionSignature) -> tuple[float, str]:
    """
    Compares two functions across:
    1. Exact or normalized names (e.g. format_date vs formatDate)
    2. Parameters and AST instruction structure
    3. Docstring similarity
    """
    if f1.file_path == f2.file_path and f1.line_number == f2.line_number:
        return 0.0, ""

    reasons = []
    score = 0.0

    # 1. Name Match
    if f1.name == f2.name:
        score += 0.6
        reasons.append(f"Exact name match '{f1.name}'")
    elif _clean_name(f1.name) == _clean_name(f2.name):
        score += 0.5
        reasons.append(f"Semantically identical names ('{f1.name}' and '{f2.name}')")
    else:
        name_ratio = SequenceMatcher(None, f1.name, f2.name).ratio()
        if name_ratio > 0.75:
            score += 0.35 * name_ratio
            reasons.append(f"Very close names ({int(name_ratio * 100)}% match)")

    # 2. Parameter Match
    if f1.params and f2.params:
        if f1.params == f2.params:
            score += 0.25
            reasons.append("Identical parameter list")
        else:
            shared = set(f1.params).intersection(set(f2.params))
            if len(shared) >= min(len(f1.params), len(f2.params)):
                score += 0.15
                reasons.append(f"Overlapping parameters ({', '.join(shared)})")

    # 3. Structural AST / Flow Match
    if f1.normalized_body and f2.normalized_body:
        if f1.normalized_body == f2.normalized_body:
            score += 0.2
            reasons.append("Matching AST statement flow")

    # 4. Docstring Similarity
    if f1.docstring and f2.docstring:
        doc_ratio = SequenceMatcher(None, f1.docstring.strip(), f2.docstring.strip()).ratio()
        if doc_ratio > 0.6:
            score += 0.2
            reasons.append(f"Docstrings with {int(doc_ratio * 100)}% match")

    total_score = min(score, 1.0)
    return total_score, " + ".join(reasons)


def find_duplicates(
    new_functions: List[FunctionSignature],
    existing_functions: List[FunctionSignature],
    threshold: float = 0.65,
) -> List[DuplicateMatch]:
    """
    Identifies functions that duplicate or reimplement existing utilities.
    Uses an inverted token index for fast O(1) candidate pruning in large codebases.
    """
    matches = []

    token_index = {}
    for exist_f in existing_functions:
        tokens = set(re.findall(r"\w+", _clean_name(exist_f.name)))
        if exist_f.params:
            tokens.update(exist_f.params)
        for token in tokens:
            if len(token) > 2:
                token_index.setdefault(token, []).append(exist_f)

    for new_f in new_functions:
        best_match: Optional[DuplicateMatch] = None
        max_score = 0.0

        new_tokens = set(re.findall(r"\w+", _clean_name(new_f.name)))
        if new_f.params:
            new_tokens.update(new_f.params)

        candidates = set()
        for token in new_tokens:
            if token in token_index:
                candidates.update(token_index[token])

        if len(existing_functions) < 100:
            target_pool = existing_functions
        else:
            target_pool = candidates

        for exist_f in target_pool:
            if new_f.file_path == exist_f.file_path and new_f.line_number == exist_f.line_number:
                continue

            # Strict language boundary isolation
            if new_f.language != exist_f.language:
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
