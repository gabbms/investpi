"""Qualidade dos dados: checagens C01–C12 e linhas por aba da versão ativa, sem filtros."""
from __future__ import annotations

from app.calculos.checagens import rodar_checagens
from app.models import Versao
from app.paginas.comum import data_local
from app.paginas.tipos import Card, Coluna, Pagina, Tabela
from app.planilha.esquema import ABAS
from app.planilha.leitura import Base


def _subtitulo(versao: Versao) -> str:
    autor = f" por {versao.enviado_por.nome}" if versao.enviado_por else ""
    return (
        f"Versão nº {versao.numero} · {versao.nome_arquivo} · enviada{autor} em {data_local(versao.criado_em)}. "
        "As checagens usam a versão inteira, sem os filtros."
    )


def _linhas_por_aba(versao: Versao) -> list[tuple[str, int]]:
    """Na ordem do esquema: o JSONB do Postgres não guarda a ordem das chaves."""
    contagem = versao.linhas_por_aba or {}
    ordem = [a for a in ABAS if a in contagem] + sorted(a for a in contagem if a not in ABAS)
    return [(a, int(contagem[a])) for a in ordem]


def montar(base: Base, versao: Versao) -> Pagina:
    checagens = rodar_checagens(base)
    abas = _linhas_por_aba(versao)
    problemas = sum(c.problemas for c in checagens)
    cor = "verde" if problemas == 0 else "amarelo"
    cards = [
        ("Checagens sem problema", sum(c.problemas == 0 for c in checagens), None),
        ("Problemas encontrados", problemas, cor),
        ("Abas carregadas", len(abas), None),
        ("Linhas carregadas", sum(n for _, n in abas), None),
    ]
    return Pagina(
        titulo="Qualidade dos dados",
        subtitulo=_subtitulo(versao),
        cards=[Card(id=t, titulo=t, valor=float(v), formato="num", status=s) for t, v, s in cards],
        tabelas=[
            Tabela(
                id="checagens",
                titulo="Checagens de qualidade (C01–C12)",
                colunas=[
                    Coluna(chave="id", rotulo="ID", formato="texto"),
                    Coluna(chave="checagem", rotulo="Checagem", formato="texto"),
                    Coluna(chave="tabela", rotulo="Tabelas", formato="texto"),
                    Coluna(chave="regra", rotulo="Regra", formato="texto"),
                    Coluna(chave="problemas", rotulo="Problemas", formato="num"),
                    Coluna(chave="situacao", rotulo="Situação", formato="status"),
                ],
                linhas=[
                    {"id": c.id, "checagem": c.checagem, "tabela": c.tabela, "regra": c.regra,
                     "problemas": c.problemas, "situacao": "Atingida" if c.problemas == 0 else "Atenção"}
                    for c in checagens
                ],
            ),
            Tabela(
                id="abas",
                titulo="Linhas por aba",
                colunas=[
                    Coluna(chave="aba", rotulo="Aba", formato="texto"),
                    Coluna(chave="linhas", rotulo="Linhas", formato="num"),
                ],
                linhas=[{"aba": a, "linhas": n} for a, n in abas],
            ),
        ],
    )
