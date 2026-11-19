"""Indicadores ASG da própria Investe Piauí (aba opcional dInstitucional).

Cada linha é um indicador da sede com o valor do ano de referência, o do ano anterior e a meta.
O farol segue a mesma regra das metas de dMetas (Status Indicador). A aba não depende de projeto,
então os filtros do painel não a alteram.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.calculos.metas import _status
from app.paginas.tipos import FormatoValor, Semaforo
from app.planilha.leitura import Base, vazio

FORMATOS: dict[str, FormatoValor] = {"%": "pct", "n": "num", "dec": "dec", "R$": "brl"}
SEMAFORO: dict[str, Semaforo] = {"Atingida": "verde", "Atenção": "amarelo", "Abaixo": "vermelho"}


@dataclass
class ItemInstitucional:
    id: str
    pilar: str
    indicador: str
    unidade: str | None
    formato: FormatoValor
    valor: float | None
    anterior: float | None
    ano: int | None
    meta: float | None
    status: Semaforo | None
    demonstracao: bool


def _num(v) -> float | None:
    return None if vazio(v) else float(v)


def _texto(v) -> str | None:
    return None if vazio(v) else str(v).strip()


def avaliar_institucional(base: Base) -> list[ItemInstitucional]:
    """Indicadores da sede, ordenados por ID Institucional; [] quando a planilha não tem a aba."""
    if "dInstitucional" not in base:
        return []
    itens = []
    for _, r in base["dInstitucional"].sort_values("ID Institucional").iterrows():
        valor, meta = _num(r["Valor Atual"]), _num(r["Meta"])
        status = _status(valor, meta, _num(r["Limite Atenção"]), r["Polaridade"] != "Menor melhor")
        ano = _num(r["Ano Referência"])
        itens.append(ItemInstitucional(
            id=str(r["ID Institucional"]).strip(),
            pilar=_texto(r["Pilar"]) or "Outros",
            indicador=_texto(r["Indicador"]) or str(r["ID Institucional"]).strip(),
            unidade=_texto(r["Unidade"]),
            formato=FORMATOS.get(_texto(r["Formato"]) or "", "num"),
            valor=valor,
            anterior=_num(r["Valor Anterior"]),
            ano=None if ano is None else int(ano),
            meta=meta,
            status=SEMAFORO.get(status) if status else None,
            demonstracao=(_texto(r["Fonte"]) or "").startswith("Demonstração"),
        ))
    return itens
