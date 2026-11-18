"""Utilitários compartilhados pelos testes."""
from functools import lru_cache
from pathlib import Path

from app.planilha.leitura import aplicar_tipos, ler_planilha

MODELO = Path(__file__).resolve().parent.parent / "dados" / "base_modelo.xlsx"


@lru_cache(maxsize=1)
def _base_modelo():
    return aplicar_tipos(ler_planilha(MODELO.read_bytes()))


def base_modelo():
    """Cópia nova da base de referência (pode ser alterada pelo teste)."""
    return {k: v.copy() for k, v in _base_modelo().items()}
