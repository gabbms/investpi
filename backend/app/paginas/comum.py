"""Peças comuns para montar as telas: contexto, cards, séries por categoria."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from zoneinfo import ZoneInfo

import pandas as pd

from app.calculos.filtros import restringir_projetos
from app.calculos.medidas import Valor, calcular, do_setor
from app.calculos.metas import ResultadoMeta, avaliar_metas, cor_indice
from app.paginas.ajuda import AJUDA_PADRAO
from app.paginas.tipos import Card, FormatoValor, Semaforo
from app.planilha.leitura import Base, vazio

COR_PILAR = {
    "Ambiental": "#1B8A4C",
    "Social": "#D9730D",
    "Governança": "#0B3D91",
    "Metas": "#5B2C83",
    "Visão Geral": "#4B5563",
}
SEMAFORO: dict[str, Semaforo] = {"Atingida": "verde", "Atenção": "amarelo", "Abaixo": "vermelho"}
FUSO = ZoneInfo("America/Fortaleza")  # horário do Piauí (UTC−3)


def data_local(d: datetime, com_hora: bool = True) -> str:
    """dd/mm/aaaa [hh:mm] no horário do Piauí."""
    if d.tzinfo is not None:
        d = d.astimezone(FUSO)
    return d.strftime("%d/%m/%Y %H:%M" if com_hora else "%d/%m/%Y")


def _milhar(texto: str) -> str:
    """Troca separadores do formato en-US (1,234.5) para pt-BR (1.234,5)."""
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_meta(valor: float, formato: str) -> str:
    """Formato da medida DAX `Meta Texto` (sem o sinal), em pt-BR."""
    if formato == "%":
        return f"{valor * 100:.0f}%"
    if formato == "idx":
        return _milhar(f"{valor:.2f}")
    if formato == "dec":
        return _milhar(f"{valor:,.1f}")
    return _milhar(f"{valor:,.0f}")


def texto_meta(r: ResultadoMeta) -> str | None:
    if r.meta is None:
        return None
    sinal = "≥ " if r.polaridade == "Maior melhor" else "≤ "
    return sinal + fmt_meta(r.meta, r.formato)


def _casas(x: float, casas: int, fixo: bool) -> str:
    """Número pt-BR com `casas` decimais (fixas, ou até `casas` sem zeros à direita).

    Arredonda o meio para cima sobre o valor exato do número, como o Intl.NumberFormat do
    navegador (0,125 → "0,13"; o f-string do Python daria "0,12").
    """
    d = Decimal(x).quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP)
    t = f"{d:,.{casas}f}"
    if not fixo and "." in t:
        t = t.rstrip("0").rstrip(".")
    return _milhar(t)


def _reais(v: float) -> str:
    for base, sufixo in ((1e9, "bi"), (1e6, "mi"), (1e3, "mil")):
        if abs(v) >= base:
            x = v / base
            casas = 1 if sufixo != "mil" and abs(x) < 100 else 0
            return f"R$ {_casas(x, casas, fixo=True)} {sufixo}"
    return f"R$ {_casas(v, 0, fixo=False)}"


def texto_reais_completo(v: float) -> str:
    """Valor em reais por extenso, pt-BR, sempre com 2 casas: R$ 720.072.000,00."""
    return f"R$ {_casas(v, 2, fixo=True)}"


def texto_valor(v: float | None, formato: str) -> str:
    """Mesmo texto de `valor()` em frontend/src/format.ts: R$ 42,8 bi · 54,2% · 7.236 · 2,12."""
    if v is None or v != v:  # None ou NaN
        return "—"
    if formato == "brl":
        return _reais(v)
    if formato == "pct":
        return f"{_casas(v * 100, 1, fixo=True)}%"
    if formato == "dec":
        return _casas(v, 2, fixo=False)
    if formato == "idx":
        return _casas(v, 0, fixo=False)
    return _casas(v, 0, fixo=False)


@dataclass
class Contexto:
    """Base filtrada de uma requisição + resultados das metas calculados uma vez."""

    base: Base
    metas: list[ResultadoMeta] = field(default_factory=list)

    def __post_init__(self):
        if not self.metas:
            self.metas = avaliar_metas(self.base)
        self._por_medida = {r.medida: r for r in self.metas}
        self._ajuda = self._carregar_ajuda()

    def _carregar_ajuda(self) -> dict[str, str]:
        ind = self.base.get("dIndicador")
        if ind is None or not {"Medida DAX", "Descrição", "Cálculo"} <= set(ind.columns):
            return {}
        ajuda: dict[str, str] = {}
        for _, r in ind.iterrows():
            medida = r["Medida DAX"]
            if vazio(medida) or medida in ajuda:
                continue
            partes = []
            if not vazio(r["Descrição"]):
                partes.append(str(r["Descrição"]))
            if not vazio(r["Cálculo"]):
                partes.append(f"Cálculo: {r['Cálculo']}.")
            ajuda[medida] = " ".join(partes)
        return ajuda

    def ajuda(self, medida: str) -> str | None:
        if not self._ajuda:
            return None  # sem dIndicador, os cards ficam sem explicação (spec §6)
        texto = self._ajuda.get(medida) or AJUDA_PADRAO.get(medida)
        if texto is None:
            return None
        meta = self._por_medida.get(medida)
        if meta is not None and (t := texto_meta(meta)):
            texto += f" Meta: {t}"
        return texto

    def status(self, medida: str) -> Semaforo | None:
        r = self._por_medida.get(medida)
        return SEMAFORO.get(r.status) if r and r.status else None

    def valor(self, medida: str) -> Valor:
        return calcular(self.base, medida)

    def card(self, medida: str, titulo: str, formato: FormatoValor) -> Card:
        return Card(id=medida, titulo=titulo, valor=self.valor(medida), formato=formato,
                    status=self.status(medida), ajuda=self.ajuda(medida))

    def card_indice(self, medida: str, titulo: str) -> Card:
        v = self.valor(medida)
        return Card(id=medida, titulo=titulo, valor=v, formato="idx", status=cor_indice(v),
                    ajuda=self.ajuda(medida))


def setores_ordenados(base: Base) -> list[tuple[str, str | None]]:
    """(setor, cor) na ordem de dSetor[Ordem], só setores com projetos no filtro."""
    s = base["dSetor"].sort_values("Ordem")
    presentes = set(base["dProjeto"]["Setor Investe"])
    return [
        (r["Setor Investe"], None if vazio(r.get("Cor")) else r.get("Cor"))
        for _, r in s.iterrows()
        if r["Setor Investe"] in presentes
    ]


def por_setor(base: Base, medidas: Iterable[str]) -> tuple[list[str], list[str | None], dict[str, list[Valor]]]:
    setores = setores_ordenados(base)
    valores = {m: [calcular(do_setor(base, s), m) for s, _ in setores] for m in medidas}
    return [s for s, _ in setores], [c for _, c in setores], valores


def grupos(df: pd.DataFrame, coluna: str) -> list[str]:
    return sorted({v for v in df[coluna] if not vazio(v)})


def por_categoria_projeto(base: Base, coluna: str, medida: str) -> tuple[list[str], list[Valor]]:
    """Medida por uma coluna de dProjeto (ex.: Município, Status Projeto)."""
    p = base["dProjeto"]
    cats = grupos(p, coluna)
    vals = [calcular(restringir_projetos(base, p.loc[p[coluna] == c, "Código Projeto"]), medida) for c in cats]
    return cats, vals


def por_categoria_fato(base: Base, tabela: str, coluna: str, medida: str) -> tuple[list[str], list[Valor]]:
    """Medida por uma coluna de uma tabela f* (ex.: fEnergia[Fonte])."""
    df = base[tabela]
    cats = grupos(df, coluna)
    vals = []
    for c in cats:
        sub = dict(base)
        sub[tabela] = df[df[coluna] == c]
        vals.append(calcular(sub, medida))
    return cats, vals


def ordenar_desc(cats: list[str], vals: list[Valor], *extras: list) -> tuple:
    ordem = sorted(range(len(cats)), key=lambda i: -(vals[i] or 0))
    return ([cats[i] for i in ordem], [vals[i] for i in ordem], *[[e[i] for i in ordem] for e in extras])


def linha_valor(v):
    """Valor de célula de tabela serializável em JSON."""
    if vazio(v):
        return None
    if isinstance(v, pd.Timestamp):
        return v.strftime("%d/%m/%Y")
    if hasattr(v, "item"):
        return v.item()
    return v


def por_projeto(base: Base, codigo: str) -> Base:
    return restringir_projetos(base, [codigo])
