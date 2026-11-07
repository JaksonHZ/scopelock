"""Exemplo de utilitário existente na base de código."""

import re


def slugify(text: str) -> str:
    """Converte uma string em um slug legível para URL."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "-", text)


def format_currency_br(val: float) -> str:
    """Formata valor float em moeda BRL (R$)."""
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
