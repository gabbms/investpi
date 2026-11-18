"""Versões dos dados no PostgreSQL (spec §7).

Cada envio confirmado vira uma `Versao` com todas as linhas da planilha em
`LinhaDado` (uma linha da aba = um JSONB). A gravação é uma única transação:
ou a versão entra inteira e passa a ser a ativa, ou nada muda.
"""
from __future__ import annotations

import math
from datetime import date, datetime

import pandas as pd
from sqlalchemy import func, insert, select, update
from sqlalchemy.orm import Session

from app.models import LinhaDado, Versao
from app.planilha.esquema import ABAS
from app.planilha.leitura import Base, aplicar_tipos

# chave = (id, criado_em): um id reaproveitado (banco recriado) não devolve dados antigos
_cache: dict[tuple, Base] = {}
_CACHE_MAX = 3


def limpar_cache() -> None:
    _cache.clear()


def _valor_json(v):
    if v is None or v is pd.NaT:
        return None
    if isinstance(v, (pd.Timestamp, datetime, date)):
        return v.isoformat()
    if hasattr(v, "item"):  # escalares numpy
        v = v.item()
    if isinstance(v, float) and math.isnan(v):
        return None
    return v


def _serializar_linha(linha: dict) -> dict:
    return {k: _valor_json(v) for k, v in linha.items()}


def _proximo_numero(s: Session) -> int:
    return (s.scalar(select(func.max(Versao.numero))) or 0) + 1


def salvar_versao(
    s: Session, base: Base, usuario_id: int | None, nome_arquivo: str, avisos: list[dict]
) -> Versao:
    try:
        s.execute(update(Versao).where(Versao.status == "ativa").values(status="inativa"))
        linhas_por_aba = {aba: len(df) for aba, df in base.items() if aba in ABAS}
        versao = Versao(
            numero=_proximo_numero(s),
            enviado_por_id=usuario_id,
            nome_arquivo=nome_arquivo,
            status="ativa",
            linhas_por_aba=linhas_por_aba,
            avisos=avisos,
            erros=[],
        )
        s.add(versao)
        s.flush()

        registros = []
        for aba, df in base.items():
            if aba not in ABAS:
                continue
            colunas = [c for c in ABAS[aba].colunas if c in df.columns]
            for linha in df[colunas].to_dict(orient="records"):
                registros.append({"versao_id": versao.id, "aba": aba, "dados": _serializar_linha(linha)})
        if registros:
            s.execute(insert(LinhaDado), registros)
        s.commit()
    except Exception:
        s.rollback()
        raise
    return versao


def registrar_rejeicao(s: Session, nome_arquivo: str, usuario_id: int | None, erros: list[dict]) -> Versao:
    try:
        versao = Versao(
            numero=_proximo_numero(s),
            enviado_por_id=usuario_id,
            nome_arquivo=nome_arquivo,
            status="rejeitada",
            linhas_por_aba={},
            avisos=[],
            erros=erros,
        )
        s.add(versao)
        s.commit()
    except Exception:
        s.rollback()
        raise
    return versao


def ativar_versao(s: Session, versao_id: int) -> Versao:
    versao = s.get(Versao, versao_id)
    if versao is None:
        raise LookupError("Versão não encontrada")
    if versao.status == "rejeitada":
        raise ValueError("Uma versão rejeitada não pode ser ativada")
    try:
        s.execute(update(Versao).where(Versao.status == "ativa").values(status="inativa"))
        versao.status = "ativa"
        s.commit()
    except Exception:
        s.rollback()
        raise
    return versao


def listar_versoes(s: Session) -> list[Versao]:
    return list(s.scalars(select(Versao).order_by(Versao.numero.desc())))


def versao_ativa(s: Session) -> Versao | None:
    return s.scalar(select(Versao).where(Versao.status == "ativa"))


def _carregar(s: Session, versao_id: int) -> Base:
    linhas = s.execute(
        select(LinhaDado.aba, LinhaDado.dados).where(LinhaDado.versao_id == versao_id).order_by(LinhaDado.id)
    ).all()
    por_aba: dict[str, list[dict]] = {}
    for aba, dados in linhas:
        por_aba.setdefault(aba, []).append(dados)
    versao = s.get(Versao, versao_id)
    abas = set(por_aba) | set((versao.linhas_por_aba or {}).keys())
    base: Base = {}
    for aba in abas:
        if aba not in ABAS:
            continue
        base[aba] = pd.DataFrame(por_aba.get(aba, []), columns=ABAS[aba].colunas)
    return aplicar_tipos(base)


def carregar_base_ativa(s: Session) -> Base | None:
    ativa = s.execute(select(Versao.id, Versao.criado_em).where(Versao.status == "ativa")).first()
    if ativa is None:
        return None
    chave = (ativa.id, ativa.criado_em)
    if chave not in _cache:
        if len(_cache) >= _CACHE_MAX:
            _cache.pop(next(iter(_cache)))
        _cache[chave] = _carregar(s, ativa.id)
    return _cache[chave]
