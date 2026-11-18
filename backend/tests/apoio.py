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


def bytes_modelo() -> bytes:
    return MODELO.read_bytes()


def mutar(alterar) -> bytes:
    """Abre o modelo com openpyxl, aplica `alterar(wb)` e devolve os bytes."""
    from io import BytesIO

    import openpyxl

    wb = openpyxl.load_workbook(BytesIO(bytes_modelo()))
    alterar(wb)
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
