"""Filtros do painel (Setor, Vice-Presidência, Status, Município) — spec §9.

Os filtros valem em dProjeto (e em dSetor para a Vice-Presidência); as tabelas
f* ficam só com os projetos que restaram e dEmpresa só com as empresas desses
projetos. dSetor, dMetas, dPremissas e dIndicador passam sem filtro.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from app.planilha.leitura import Base

TABELAS_SEM_FILTRO = {"dSetor", "dMetas", "dPremissas", "dIndicador"}


@dataclass
class Filtros:
    setores: list[str] = field(default_factory=list)
    vps: list[str] = field(default_factory=list)
    status: list[str] = field(default_factory=list)
    municipios: list[str] = field(default_factory=list)


def restringir_projetos(base: Base, codigos: Iterable[str]) -> Base:
    """Mantém só os projetos `codigos` em dProjeto, nas f* e em dEmpresa."""
    codigos = set(codigos)
    nova: Base = {}
    for nome, df in base.items():
        if nome in TABELAS_SEM_FILTRO:
            nova[nome] = df
        elif nome == "dProjeto" or "Código Projeto" in df.columns:
            nova[nome] = df[df["Código Projeto"].isin(codigos)]
        else:
            nova[nome] = df
    if "dEmpresa" in base:
        empresas = set(nova["dProjeto"]["Código Empresa"])
        emp = base["dEmpresa"]
        nova["dEmpresa"] = emp[emp["Código Empresa"].isin(empresas)]
    return nova


def aplicar_filtros(base: Base, f: Filtros) -> Base:
    p = base["dProjeto"]
    mascara = p["Código Projeto"].notna()
    if f.setores:
        mascara &= p["Setor Investe"].isin(f.setores)
    if f.status:
        mascara &= p["Status Projeto"].isin(f.status)
    if f.municipios:
        mascara &= p["Município"].isin(f.municipios)
    if f.vps:
        s = base["dSetor"]
        setores_vp = set(s.loc[s["Vice-Presidência"].isin(f.vps), "Setor Investe"])
        mascara &= p["Setor Investe"].isin(setores_vp)
    return restringir_projetos(base, p.loc[mascara, "Código Projeto"])
