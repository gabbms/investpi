"""Checagens de qualidade C01–C12.

Mesmas regras da medida DAX `Problemas Checagem` (página Qualidade dos Dados
do Power BI v3) e mesmos textos da aba dChecagens. Geram avisos, não bloqueiam.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

from app.planilha.leitura import Base


@dataclass
class ResultadoChecagem:
    id: str
    checagem: str
    tabela: str
    regra: str
    problemas: int

    def dict(self) -> dict:
        return asdict(self)


TEXTOS: list[tuple[str, str, str, str]] = [
    ("C01", "Projetos sem empresa cadastrada", "dProjeto × dEmpresa",
     "Todo projeto deve ter um Código Empresa existente em dEmpresa."),
    ("C02", "Códigos de projeto repetidos", "dProjeto",
     "O Código Projeto (PROJ###) não pode se repetir."),
    ("C03", "Projetos sem dados ambientais", "fAmbiental",
     "Todo projeto deve ter uma linha em fAmbiental."),
    ("C04", "Projetos sem dados sociais", "fSocial",
     "Todo projeto deve ter uma linha em fSocial."),
    ("C05", "Projetos sem execução financeira", "fFinanceiro",
     "Todo projeto deve ter execução financeira informada."),
    ("C06", "Projetos sem dados de transparência", "fTransparencia",
     "Todo projeto deve ter uma linha em fTransparencia."),
    ("C07", "Investimento realizado maior que o previsto", "dProjeto",
     "Investimento Realizado não deve passar o Investimento Previsto sem justificativa."),
    ("C08", "Empregos de mulheres/locais/PCD acima do total gerado", "fSocial",
     "Subgrupos não podem ser maiores que o total de empregos diretos gerados."),
    ("C09", "Valor pago maior que o empenhado", "fFinanceiro",
     "Pago ≤ Liquidado ≤ Empenhado em cada lançamento."),
    ("C10", "Campos obrigatórios vazios em projetos", "dProjeto",
     "Município, status, investimento previsto e custo de manutenção devem estar preenchidos."),
    ("C11", "Percentuais fora da faixa 0% a 100%", "fHidrogenio",
     "% Renovável Eletrolisador deve estar entre 0 e 1."),
    ("C12", "Contratos com data de fim antes do início", "fContratos",
     "Data Fim deve ser posterior à Data Início."),
]


def _sem_linha_em(projetos: pd.DataFrame, fato: pd.DataFrame) -> int:
    return int((~projetos["Código Projeto"].isin(set(fato["Código Projeto"]))).sum())


def _contar(mascara: pd.Series) -> int:
    # comparações com vazio dão False, como em DAX
    return int(mascara.fillna(False).astype(bool).sum())


def rodar_checagens(base: Base) -> list[ResultadoChecagem]:
    p = base["dProjeto"]
    s = base["fSocial"]
    f = base["fFinanceiro"]
    h = base["fHidrogenio"]
    c = base["fContratos"]
    gerados = s["Empregos Diretos Gerados"]

    contagens = {
        "C01": _contar(~p["Código Empresa"].isin(set(base["dEmpresa"]["Código Empresa"]))),
        "C02": len(p) - p["Código Projeto"].nunique(),
        "C03": _sem_linha_em(p, base["fAmbiental"]),
        "C04": _sem_linha_em(p, s),
        "C05": _sem_linha_em(p, f),
        "C06": _sem_linha_em(p, base["fTransparencia"]),
        "C07": _contar(p["Investimento Realizado"] > p["Investimento Previsto"]),
        "C08": _contar(
            (s["Empregos Mulheres"] > gerados)
            | (s["Empregos População Local"] > gerados)
            | (s["Empregos PCD"] > gerados)
        ),
        "C09": _contar((f["Valor Pago"] > f["Valor Liquidado"]) | (f["Valor Liquidado"] > f["Valor Empenhado"])),
        "C10": _contar(
            p["Município"].isna()
            | p["Status Projeto"].isna()
            | p["Investimento Previsto"].isna()
            | p["Custo Manutenção Anual"].isna()
        ),
        "C11": _contar((h["% Renovável Eletrolisador"] < 0) | (h["% Renovável Eletrolisador"] > 1)),
        "C12": _contar(c["Data Fim"] < c["Data Início"]),
    }
    return [ResultadoChecagem(i, nome, tabela, regra, contagens[i]) for i, nome, tabela, regra in TEXTOS]
