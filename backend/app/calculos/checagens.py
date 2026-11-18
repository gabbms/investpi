"""Checagens de qualidade C01–C12.

Mesmas regras da medida DAX `Problemas Checagem` (página Qualidade dos Dados
do Power BI v3) e mesmos textos da aba dChecagens. Geram avisos, não bloqueiam.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass, field

import pandas as pd

from app.paginas.comum import texto_valor
from app.planilha.leitura import COLUNA_LINHA, Base

LIMITE_OCORRENCIAS = 50  # máximo de ocorrências mostradas por checagem na tela


@dataclass
class Ocorrencia:
    aba: str
    linha: int | None  # linha do Excel; None em versões salvas antes de guardá-la
    identificador: str
    detalhe: str


@dataclass
class ResultadoChecagem:
    id: str
    checagem: str
    tabela: str
    regra: str
    problemas: int
    ocorrencias: list[Ocorrencia] = field(default_factory=list)

    def dict(self) -> dict:
        """Só a contagem: é o que vai para `versao.avisos`."""
        return {k: v for k, v in asdict(self).items() if k != "ocorrencias"}

    def com_ocorrencias(self, limite: int | None = LIMITE_OCORRENCIAS) -> dict:
        mostradas = self.ocorrencias if limite is None else self.ocorrencias[:limite]
        return {**self.dict(), "ocorrencias": [asdict(o) for o in mostradas], "mais": self.problemas - len(mostradas)}


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


def _mascara(mascara: pd.Series) -> pd.Series:
    # comparações com vazio dão False, como em DAX
    return mascara.fillna(False).astype(bool)


def _linha(registro: pd.Series) -> int | None:
    v = registro.get(COLUNA_LINHA)
    return None if v is None or v != v else int(v)


def _ocorrencias(
    aba: str, df: pd.DataFrame, mascara: pd.Series, chave: str, detalhe: Callable[[pd.Series], str]
) -> list[Ocorrencia]:
    return [
        Ocorrencia(aba, _linha(r), str(r[chave]), detalhe(r))
        for _, r in df[_mascara(mascara)].iterrows()
    ]


def _data(v) -> str:
    return "—" if pd.isna(v) else pd.Timestamp(v).strftime("%d/%m/%Y")


def _sem_linha_em(projetos: pd.DataFrame, fato: pd.DataFrame, tabela: str) -> list[Ocorrencia]:
    return _ocorrencias(
        "dProjeto", projetos, ~projetos["Código Projeto"].isin(set(fato["Código Projeto"])), "Código Projeto",
        lambda r: f"{r['Nome Projeto']} sem linha em {tabela}",
    )


def _repeticoes(p: pd.DataFrame) -> list[Ocorrencia]:
    primeira: dict[str, int | None] = {}
    saida = []
    for _, r in p.iterrows():
        cod = r["Código Projeto"]
        if pd.isna(cod):  # como `nunique`, que ignora vazios: cada código vazio conta como repetição
            saida.append(Ocorrencia("dProjeto", _linha(r), "", "Código Projeto vazio"))
            continue
        if cod not in primeira:
            primeira[cod] = _linha(r)
            continue
        origem = primeira[cod]
        detalhe = "Código repetido" if origem is None else f"Código repetido; primeira ocorrência na linha {origem}"
        saida.append(Ocorrencia("dProjeto", _linha(r), str(cod), detalhe))
    return saida


def _subgrupos_acima(r: pd.Series) -> str:
    total = r["Empregos Diretos Gerados"]
    return "; ".join(
        f"{col} {texto_valor(r[col], 'num')} > Empregos Diretos Gerados {texto_valor(total, 'num')}"
        for col in ("Empregos Mulheres", "Empregos População Local", "Empregos PCD")
        if r[col] > total
    )


CAMPOS_OBRIGATORIOS = ("Município", "Status Projeto", "Investimento Previsto", "Custo Manutenção Anual")


def rodar_checagens(base: Base) -> list[ResultadoChecagem]:
    p = base["dProjeto"]
    s = base["fSocial"]
    f = base["fFinanceiro"]
    h = base["fHidrogenio"]
    c = base["fContratos"]
    gerados = s["Empregos Diretos Gerados"]
    pct = h["% Renovável Eletrolisador"]

    listas = {
        "C01": _ocorrencias(
            "dProjeto", p, ~p["Código Empresa"].isin(set(base["dEmpresa"]["Código Empresa"])), "Código Projeto",
            lambda r: f"Código Empresa {r['Código Empresa']} não existe em dEmpresa",
        ),
        "C02": _repeticoes(p),
        "C03": _sem_linha_em(p, base["fAmbiental"], "fAmbiental"),
        "C04": _sem_linha_em(p, s, "fSocial"),
        "C05": _sem_linha_em(p, f, "fFinanceiro"),
        "C06": _sem_linha_em(p, base["fTransparencia"], "fTransparencia"),
        "C07": _ocorrencias(
            "dProjeto", p, p["Investimento Realizado"] > p["Investimento Previsto"], "Código Projeto",
            lambda r: (
                f"Investimento Realizado {texto_valor(r['Investimento Realizado'], 'brl')} > "
                f"Investimento Previsto {texto_valor(r['Investimento Previsto'], 'brl')}"
            ),
        ),
        "C08": _ocorrencias(
            "fSocial", s,
            (s["Empregos Mulheres"] > gerados) | (s["Empregos População Local"] > gerados) | (s["Empregos PCD"] > gerados),
            "Código Projeto", _subgrupos_acima,
        ),
        "C09": _ocorrencias(
            "fFinanceiro", f,
            (f["Valor Pago"] > f["Valor Liquidado"]) | (f["Valor Liquidado"] > f["Valor Empenhado"]), "ID Execução",
            lambda r: (
                f"{_data(r['Data Referência'])}: Empenhado {texto_valor(r['Valor Empenhado'], 'brl')} · "
                f"Liquidado {texto_valor(r['Valor Liquidado'], 'brl')} · Pago {texto_valor(r['Valor Pago'], 'brl')}"
            ),
        ),
        "C10": _ocorrencias(
            "dProjeto", p, p[list(CAMPOS_OBRIGATORIOS)].isna().any(axis=1), "Código Projeto",
            lambda r: "Vazios: " + ", ".join(col for col in CAMPOS_OBRIGATORIOS if pd.isna(r[col])),
        ),
        "C11": _ocorrencias(
            "fHidrogenio", h, (pct < 0) | (pct > 1), "Código Projeto",
            lambda r: f"% Renovável Eletrolisador {texto_valor(r['% Renovável Eletrolisador'], 'pct')}",
        ),
        "C12": _ocorrencias(
            "fContratos", c, c["Data Fim"] < c["Data Início"], "ID Processo",
            lambda r: f"Data Início {_data(r['Data Início'])} > Data Fim {_data(r['Data Fim'])}",
        ),
    }
    return [ResultadoChecagem(i, nome, tabela, regra, len(listas[i]), listas[i]) for i, nome, tabela, regra in TEXTOS]
