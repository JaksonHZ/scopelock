"""Exemplo de código gerado por um agente de IA desatento."""

import re


def slugify_text(text: str) -> str:
    """Converte uma string em um slug legível para URL."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "-", text)


def format_currency_brl(val: float) -> str:
    """Formata valor em Real."""
    return f"R$ {val:.2f}"
