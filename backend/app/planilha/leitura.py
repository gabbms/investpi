"""Leitura da planilha .xlsx para um `Base` (um DataFrame por aba conhecida).

A leitura só normaliza (cabeçalhos e textos sem espaços nas pontas, linhas
totalmente vazias descartadas, "Sim/Não" padronizado). Os valores ficam como
vieram para que `validacao.validar_estrutura` possa apontar tipos inválidos;
`aplicar_tipos` converte depois que a validação passa.
"""
from __future__ import annotations

import math
import re
import warnings
from datetime import date, datetime
from io import BytesIO

import pandas as pd

from app.planilha.esquema import ABAS

Base = dict[str, pd.DataFrame]


class PlanilhaInvalida(Exception):
    def __init__(self, mensagem: str):
        super().__init__(mensagem)
        self.mensagem = mensagem


class _Invalido:
    """Marca um valor que não pôde ser convertido ao tipo da coluna."""


INVALIDO = _Invalido()


def vazio(v) -> bool:
    if v is None or v is pd.NaT:
        return True
    if isinstance(v, float) and math.isnan(v):
        return True
    try:
        return bool(pd.isna(v))
    except (TypeError, ValueError):
        return False


def _limpar_texto(v):
    if isinstance(v, str):
        v = v.strip()
        return None if v == "" else v
    return v


def para_simnao(v):
    if vazio(v):
        return None
    if isinstance(v, str):
        t = v.strip().casefold()
        if t == "sim":
            return "Sim"
        if t in ("não", "nao"):
            return "Não"
    return INVALIDO


_NUM_BR = re.compile(r"^-?\d{1,3}(\.\d{3})+(,\d+)?$")


def para_numero(v):
    if vazio(v):
        return None
    if isinstance(v, bool):
        return INVALIDO
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        t = v.strip().replace("R$", "").replace(" ", "")
        if _NUM_BR.match(t):
            t = t.replace(".", "").replace(",", ".")
        elif "," in t and "." not in t:
            t = t.replace(",", ".")
        try:
            return float(t)
        except ValueError:
            return INVALIDO
    try:
        return float(v)
    except (TypeError, ValueError):
        return INVALIDO


def para_inteiro(v):
    n = para_numero(v)
    if n is None or n is INVALIDO:
        return n
    return n if float(n).is_integer() else INVALIDO


def para_data(v):
    if vazio(v):
        return None
    if isinstance(v, (datetime, date, pd.Timestamp)):
        return pd.Timestamp(v)
    if isinstance(v, str):
        t = v.strip()
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M"):
            try:
                return pd.Timestamp(datetime.strptime(t, fmt))
            except ValueError:
                continue
    return INVALIDO


def para_texto(v):
    if vazio(v):
        return None
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    if isinstance(v, (datetime, pd.Timestamp)):
        return v.strftime("%d/%m/%Y")
    return str(v).strip() or None


CONVERSORES = {
    "texto": para_texto,
    "numero": para_numero,
    "inteiro": para_inteiro,
    "data": para_data,
    "simnao": para_simnao,
}


def ler_planilha(conteudo: bytes) -> Base:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            arquivo = pd.ExcelFile(BytesIO(conteudo), engine="openpyxl")
            nomes = [n for n in arquivo.sheet_names if n in ABAS]
            brutas = {n: arquivo.parse(n, dtype=object) for n in nomes}
    except Exception as exc:  # noqa: BLE001 - qualquer falha de leitura vira mensagem ao usuário
        raise PlanilhaInvalida("Arquivo não é uma planilha .xlsx válida") from exc

    base: Base = {}
    for nome, df in brutas.items():
        df = df.rename(columns=lambda c: str(c).strip())
        df = df.loc[:, ~df.columns.str.startswith("Unnamed:")]
        df = df.map(_limpar_texto)
        df = df.dropna(how="all")
        espec = ABAS[nome]
        for col, tipo in espec.tipos.items():
            if col not in df.columns:
                continue
            if tipo == "simnao":
                df[col] = df[col].map(lambda v: v if (r := para_simnao(v)) is INVALIDO else r)
            elif tipo == "texto":
                df[col] = df[col].map(para_texto)
        base[nome] = df
    return base


def aplicar_tipos(base: Base) -> Base:
    """Converte as colunas do esquema para os tipos usados nos cálculos.

    Só deve ser chamado depois de `validar_estrutura` não ter encontrado erros
    (valores inválidos viram vazio aqui).
    """
    tipada: Base = {}
    for nome, df in base.items():
        df = df.copy()
        espec = ABAS.get(nome)
        if espec:
            for col, tipo in espec.tipos.items():
                if col not in df.columns:
                    continue
                conv = CONVERSORES[tipo]
                valores = [None if (r := conv(v)) is INVALIDO else r for v in df[col]]
                if tipo in ("numero", "inteiro"):
                    df[col] = pd.Series(valores, index=df.index, dtype="float64")
                elif tipo == "data":
                    df[col] = pd.to_datetime(pd.Series(valores, index=df.index, dtype=object))
                else:
                    df[col] = pd.Series(valores, index=df.index, dtype=object)
        tipada[nome] = df.reset_index(drop=True)
    return tipada
