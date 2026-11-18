"""Telas por tema material (T4, T6, T7): como cada tema aparece nos quatro setores.

Usam só medidas que já existem. O índice do tema aplica o método do índice de
pilar às metas de dMetas daquele tema; ele não entra no Índice ASG Geral.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.calculos.medidas import calcular
from app.calculos.metas import cor_indice, indice_tema
from app.paginas.comum import Contexto, texto_meta
from app.paginas.pilares import _projetos, _series_por_setor, _valor_fato, valor_atual
from app.paginas.tipos import Card, Coluna, Grafico, Pagina, Tabela
from app.planilha.leitura import Base

AJUDA_INDICE = (
    "Média ponderada pelo peso do atingimento das metas deste tema (dMetas, coluna Tema Material). "
    "Mesmo método do índice de pilar. "
    "O valor exibido é arredondado: um tema pode mostrar 100 mesmo com uma meta em atenção."
)
CINZA = "#7B8794"

PROJETO = Coluna(chave="projeto", rotulo="Projeto", formato="texto")
SETOR = Coluna(chave="setor", rotulo="Setor", formato="texto")


@dataclass(frozen=True)
class Tema:
    codigo: str
    nome: str
    subtitulo: str
    cor: str
    montar: Callable[[Base, Contexto, str], tuple[list[Card], list[Grafico], Tabela]]


def _grafico(base: Base, gid: str, titulo: str, formato: str, medidas: list[tuple[str, str, str | None]]) -> Grafico:
    setores, series = _series_por_setor(base, medidas)
    return Grafico(id=gid, titulo=titulo, tipo="colunas", categorias=setores, series=series, formato=formato)


def _tabela_metas(ctx: Contexto, codigo: str) -> Tabela:
    metas = ctx.base["dMetas"]
    ids = {i for i, t in zip(metas["ID Meta"], metas["Tema Material"]) if str(t).strip() == codigo}
    linhas = [{
        "indicador": r.indicador,
        "peso": r.peso,
        "atual": valor_atual(r),
        "meta": texto_meta(r),
        "status": r.status,
    } for r in ctx.metas if r.id_meta in ids]
    return Tabela(id="metas_tema", titulo="Metas do tema", colunas=[
        Coluna(chave="indicador", rotulo="Indicador", formato="texto"),
        Coluna(chave="peso", rotulo="Peso", formato="num"),
        Coluna(chave="atual", rotulo="Atual", formato="texto"),
        Coluna(chave="meta", rotulo="Meta", formato="texto"),
        Coluna(chave="status", rotulo="Status", formato="status"),
    ], linhas=linhas)


# --------------------------------------------------------------------------- T4


def _t4(base: Base, ctx: Contexto, cor: str):
    cards = [
        ctx.card("Emissões CO2 tCO2e", "Emissões de CO2 (tCO2e)", "num"),
        ctx.card("Emissões Evitadas tCO2e", "Emissões evitadas (tCO2e)", "num"),
        ctx.card("Saldo Climático tCO2e", "Saldo climático (tCO2e)", "num"),
        ctx.card("Intensidade Emissões tCO2e/R$ mi", "Intensidade de emissões (tCO2e/R$ mi)", "dec"),
        ctx.card("% Projetos com Análise de Riscos", "Projetos com análise de riscos", "pct"),
        ctx.card("% Riscos Críticos Mitigados", "Riscos críticos mitigados", "pct"),
        ctx.card("Incidentes Ambientais", "Incidentes ambientais", "num"),
    ]
    graficos = [
        _grafico(base, "emissoes_setor", "Emissões geradas e evitadas por setor (tCO2e)", "num", [
            ("Emissões CO2 tCO2e", "Emissões de CO2", CINZA),
            ("Emissões Evitadas tCO2e", "Emissões evitadas", cor),
        ]),
        _grafico(base, "incidentes_setor", "Incidentes ambientais por setor", "num", [
            ("Incidentes Ambientais", "Incidentes ambientais", cor),
        ]),
    ]
    linhas = [{
        "projeto": proj["Nome Projeto"],
        "setor": proj["Setor Investe"],
        "emissoes": calcular(b, "Emissões CO2 tCO2e") if len(b["fAmbiental"]) else None,
        "evitadas": calcular(b, "Emissões Evitadas tCO2e") if len(b["fAmbiental"]) else None,
        "incidentes": calcular(b, "Incidentes Ambientais"),
    } for _, proj, b in _projetos(base)]
    tabela = Tabela(id="projetos_tema", titulo="Emissões e incidentes por projeto", colunas=[
        PROJETO, SETOR,
        Coluna(chave="emissoes", rotulo="Emissões (tCO2e)", formato="num"),
        Coluna(chave="evitadas", rotulo="Evitadas (tCO2e)", formato="num"),
        Coluna(chave="incidentes", rotulo="Incidentes", formato="num"),
    ], linhas=linhas)
    return cards, graficos, tabela


# --------------------------------------------------------------------------- T6


def _t6(base: Base, ctx: Contexto, cor: str):
    cards = [
        ctx.card("Capacidade Instalada MW", "Capacidade instalada (MW)", "num"),
        ctx.card("Geração Anual MWh", "Geração anual (MWh)", "num"),
        ctx.card("% Energia Renovável no Consumo", "Energia renovável no consumo", "pct"),
        ctx.card("% Renovável nos Eletrolisadores", "Renovável nos eletrolisadores", "pct"),
        ctx.card("% Projetos Tecnologia Limpa", "Projetos com tecnologia limpa", "pct"),
    ]
    graficos = [
        _grafico(base, "tecnologia_setor", "Projetos com tecnologia limpa por setor", "pct", [
            ("% Projetos Tecnologia Limpa", "Projetos com tecnologia limpa", cor),
        ]),
        _grafico(base, "renovavel_setor", "Energia renovável no consumo por setor", "pct", [
            ("% Energia Renovável no Consumo", "Energia renovável no consumo", cor),
        ]),
    ]
    linhas = [{
        "projeto": proj["Nome Projeto"],
        "setor": proj["Setor Investe"],
        "tecnologia": _valor_fato(b, "fAmbiental", "Tecnologia Limpa"),
        "renovavel": _valor_fato(b, "fAmbiental", "Energia Renovável Consumida (MWh)"),
    } for _, proj, b in _projetos(base)]
    tabela = Tabela(id="projetos_tema", titulo="Tecnologia limpa e energia renovável por projeto", colunas=[
        PROJETO, SETOR,
        Coluna(chave="tecnologia", rotulo="Tecnologia limpa", formato="simnao"),
        Coluna(chave="renovavel", rotulo="Energia renovável consumida (MWh)", formato="num"),
    ], linhas=linhas)
    return cards, graficos, tabela


# --------------------------------------------------------------------------- T7


def _t7(base: Base, ctx: Contexto, cor: str):
    cards = [
        ctx.card("% Empregos População Local", "Empregos para a população local", "pct"),
        ctx.card("% Consulta Comunidades", "Projetos com consulta às comunidades", "pct"),
        ctx.card("% Avaliação Impacto Social", "Projetos com avaliação de impacto social", "pct"),
        ctx.card("Comunidades Beneficiadas", "Comunidades beneficiadas", "num"),
        ctx.card("Investimento Social", "Investimento social", "brl"),
        ctx.card("Reclamações Sociais", "Reclamações sociais", "num"),
    ]
    graficos = [
        _grafico(base, "consulta_setor", "Consulta às comunidades e avaliação de impacto social por setor", "pct", [
            ("% Consulta Comunidades", "Consulta às comunidades", cor),
            ("% Avaliação Impacto Social", "Avaliação de impacto social", "#E8B07F"),
        ]),
        _grafico(base, "reclamacoes_setor", "Reclamações sociais por setor", "num", [
            ("Reclamações Sociais", "Reclamações sociais", cor),
        ]),
    ]
    linhas = [{
        "projeto": proj["Nome Projeto"],
        "setor": proj["Setor Investe"],
        "municipio": proj["Município"],
        "avaliacao": _valor_fato(b, "fSocial", "Avaliação Impacto Social"),
        "reclamacoes": calcular(b, "Reclamações Sociais"),
    } for _, proj, b in _projetos(base) if _valor_fato(b, "fSocial", "Consulta Comunidades") != "Sim"]
    tabela = Tabela(id="projetos_tema", titulo="Projetos sem consulta às comunidades", colunas=[
        PROJETO, SETOR,
        Coluna(chave="municipio", rotulo="Município", formato="texto"),
        Coluna(chave="avaliacao", rotulo="Avaliação de impacto social", formato="simnao"),
        Coluna(chave="reclamacoes", rotulo="Reclamações", formato="num"),
    ], linhas=linhas)
    return cards, graficos, tabela


TEMAS: dict[str, Tema] = {
    "riscos-climaticos": Tema("T4", "T4 Riscos climáticos e resiliência",
                              "Gestão de riscos climáticos e resiliência do portfólio", "#0277BD", _t4),
    "energia-limpa": Tema("T6", "T6 Energia limpa", "Eficiência energética e energia limpa", "#00A19A", _t6),
    "licenca-social": Tema("T7", "T7 Licença social",
                           "Engajamento comunitário e licença social para operar", "#D9730D", _t7),
}


def montar(base: Base, slug: str) -> Pagina:
    tema = TEMAS[slug]
    ctx = Contexto(base)
    v = indice_tema(base, tema.codigo, ctx.metas)
    indice = Card(id="Índice do Tema", titulo="Índice do tema", valor=v, formato="idx",
                  status=cor_indice(v), ajuda=AJUDA_INDICE)
    cards, graficos, tabela_projetos = tema.montar(base, ctx, tema.cor)
    return Pagina(
        titulo=tema.nome,
        subtitulo=tema.subtitulo,
        indice=indice,
        cards=cards,
        graficos=graficos,
        tabelas=[_tabela_metas(ctx, tema.codigo), tabela_projetos],
    )
