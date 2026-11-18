"""Telas por setor — espelham as páginas de setor do Power BI v3.

Cada tela calcula sobre a base restrita ao setor, por cima dos filtros do
usuário (como o filtro de página do Power BI somado aos segmentadores).
O Power BI não tem página de Sustentabilidade Ambiental; esta segue a spec §10.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.calculos.medidas import calcular, do_setor
from app.paginas.comum import Contexto, linha_valor, ordenar_desc, por_categoria_fato, por_projeto
from app.paginas.tipos import Coluna, Grafico, Pagina, Serie, Tabela
from app.planilha.leitura import Base


@dataclass(frozen=True)
class Setor:
    nome: str
    subtitulo: str
    montar: Callable[[Base, Contexto, str], tuple[list, list, list]]


def _cor(base: Base, setor: str) -> str | None:
    s = base["dSetor"]
    cor = s.loc[s["Setor Investe"] == setor, "Cor"]
    return cor.iloc[0] if len(cor) else None


def _primeiro(b: Base, tabela: str, coluna: str):
    df = b[tabela]
    return linha_valor(df[coluna].iloc[0]) if len(df) else None


def _linhas(base: Base, colunas: dict[str, Callable[[dict, Base], object]]) -> list[dict]:
    p = base["dProjeto"].sort_values("Nome Projeto")
    linhas = []
    for _, proj in p.iterrows():
        b = por_projeto(base, proj["Código Projeto"])
        linhas.append({chave: fn(proj, b) for chave, fn in colunas.items()})
    return linhas


def _barra(base, tabela, coluna, medida, titulo, gid, cor, formato, tipo="barra_h"):
    cats, vals = por_categoria_fato(base, tabela, coluna, medida)
    cats, vals = ordenar_desc(cats, vals)
    return Grafico(id=gid, titulo=titulo, tipo=tipo, categorias=cats,
                   series=[Serie(nome=titulo, valores=vals, cor=cor)], formato=formato)


PROJETO = Coluna(chave="projeto", rotulo="Projeto", formato="texto")
MUNICIPIO = Coluna(chave="municipio", rotulo="Município", formato="texto")
STATUS = Coluna(chave="status", rotulo="Status", formato="texto")
ETAPA = Coluna(chave="etapa", rotulo="Etapa", formato="texto")
BASICAS = {
    "projeto": lambda p, b: p["Nome Projeto"],
    "municipio": lambda p, b: p["Município"],
    "status": lambda p, b: p["Status Projeto"],
    "etapa": lambda p, b: p["Etapa"],
}


def _energia(base: Base, ctx: Contexto, cor: str):
    cards = [
        ctx.card("Investimento Previsto", "Investimento previsto", "brl"),
        ctx.card("Capacidade Instalada MW", "Capacidade instalada (MW)", "num"),
        ctx.card("Geração Anual MWh", "Geração anual (MWh)", "num"),
        ctx.card("Fator de Capacidade Médio", "Fator de capacidade médio", "pct"),
        ctx.card("% Energia Renovável no Consumo", "Energia renovável no consumo", "pct"),
    ]
    graficos = [_barra(base, "fEnergia", "Fonte", "Capacidade Instalada MW", "Capacidade instalada por fonte (MW)",
                       "capacidade_fonte", cor, "num", tipo="colunas")]
    colunas = {**BASICAS,
               "capacidade": lambda p, b: calcular(b, "Capacidade Instalada MW"),
               "geracao": lambda p, b: calcular(b, "Geração Anual MWh"),
               "fator": lambda p, b: calcular(b, "Fator de Capacidade Médio"),
               "evitadas": lambda p, b: calcular(b, "Emissões Evitadas tCO2e")}
    tabela = Tabela(id="projetos_energia", titulo="Projetos de energia renovável", colunas=[
        PROJETO, MUNICIPIO, STATUS, ETAPA,
        Coluna(chave="capacidade", rotulo="Capacidade (MW)", formato="num"),
        Coluna(chave="geracao", rotulo="Geração anual (MWh)", formato="num"),
        Coluna(chave="fator", rotulo="Fator de capacidade", formato="pct"),
        Coluna(chave="evitadas", rotulo="Emissões evitadas (tCO2e)", formato="num"),
    ], linhas=_linhas(base, colunas))
    return cards, graficos, [tabela]


def _hidrogenio(base: Base, ctx: Contexto, cor: str):
    cards = [
        ctx.card("Investimento Previsto", "Investimento previsto", "brl"),
        ctx.card("Capacidade Eletrólise MW", "Capacidade de eletrólise (MW)", "num"),
        ctx.card("Produção H2 t", "Produção de H2 (t/ano)", "num"),
        ctx.card("Intensidade Energética H2 kWh/kg", "Intensidade energética (kWh/kg H2)", "dec"),
        ctx.card("% Renovável nos Eletrolisadores", "Energia renovável nos eletrolisadores", "pct"),
    ]
    graficos = [
        _barra(base, "fHidrogenio", "Produto Final", "Produção H2 t", "Produção anual por produto final (t)",
               "producao_produto", cor, "num"),
        _barra(base, "fHidrogenio", "Destino Produção", "Produção H2 t", "Destino da produção",
               "destino_producao", None, "num", tipo="rosca"),
    ]
    colunas = {**BASICAS,
               "licenca": lambda p, b: _primeiro(b, "fAmbiental", "Licença Válida"),
               "eletrolise": lambda p, b: calcular(b, "Capacidade Eletrólise MW"),
               "producao": lambda p, b: calcular(b, "Produção H2 t"),
               "investimento": lambda p, b: calcular(b, "Investimento Previsto")}
    tabela = Tabela(id="projetos_hidrogenio", titulo="Projetos de hidrogênio verde", colunas=[
        PROJETO, MUNICIPIO, STATUS, ETAPA,
        Coluna(chave="licenca", rotulo="Licença válida", formato="simnao"),
        Coluna(chave="eletrolise", rotulo="Eletrólise (MW)", formato="num"),
        Coluna(chave="producao", rotulo="Produção H2 (t)", formato="num"),
        Coluna(chave="investimento", rotulo="Investimento previsto", formato="brl"),
    ], linhas=_linhas(base, colunas))
    return cards, graficos, [tabela]


def _mineracao(base: Base, ctx: Contexto, cor: str):
    cards = [
        ctx.card("Investimento Previsto", "Investimento previsto", "brl"),
        ctx.card("Produção ROM t", "Produção ROM (t)", "num"),
        ctx.card("Faturamento Mineração", "Faturamento previsto", "brl"),
        ctx.card("Intensidade Hídrica Mineração m3/t", "Intensidade hídrica (m³/t)", "dec"),
        ctx.card("% Mineração com Tecnologia Limpa", "Projetos com tecnologia limpa", "pct"),
    ]
    graficos = [
        _barra(base, "fMineracao", "Substância", "Valor de Venda Mineração", "Valor de venda previsto por substância",
               "venda_substancia", cor, "brl"),
        _barra(base, "fMineracao", "Classe Substância", "Faturamento Mineração", "Faturamento previsto por classe",
               "faturamento_classe", None, "brl", tipo="rosca"),
    ]
    sim = lambda col: (lambda p, b: _primeiro(b, "fAmbiental", col))  # noqa: E731
    colunas = {"projeto": BASICAS["projeto"], "municipio": BASICAS["municipio"],
               "licenciamento": sim("Licenciamento Ambiental"), "licenca": sim("Licença Válida"),
               "recuperacao": sim("Plano Recuperação Ambiental"), "aia": sim("Avaliação Impacto Ambiental"),
               "incidentes": lambda p, b: calcular(b, "Incidentes Ambientais")}
    tabela = Tabela(id="conformidade_mineracao", titulo="Conformidade ambiental dos projetos minerários", colunas=[
        PROJETO, MUNICIPIO,
        Coluna(chave="licenciamento", rotulo="Licenciamento", formato="simnao"),
        Coluna(chave="licenca", rotulo="Licença válida", formato="simnao"),
        Coluna(chave="recuperacao", rotulo="Plano de recuperação", formato="simnao"),
        Coluna(chave="aia", rotulo="Avaliação de impacto", formato="simnao"),
        Coluna(chave="incidentes", rotulo="Incidentes ambientais", formato="num"),
    ], linhas=_linhas(base, colunas))
    return cards, graficos, [tabela]


def _sustentabilidade(base: Base, ctx: Contexto, cor: str):
    cards = [
        ctx.card("Investimento Previsto", "Investimento previsto", "brl"),
        ctx.card("Área Intervenção ha", "Área de intervenção (ha)", "num"),
        ctx.card("Remoção Carbono tCO2e", "Remoção de carbono (tCO2e)", "num"),
        ctx.card("Créditos Carbono tCO2e", "Créditos de carbono (tCO2e)", "num"),
    ]
    graficos = [_barra(base, "fSustentabilidade", "Tipo Iniciativa", "Área Intervenção ha",
                       "Área de intervenção por tipo de iniciativa (ha)", "area_iniciativa", cor, "num")]
    tipos, remocao = por_categoria_fato(base, "fSustentabilidade", "Tipo Iniciativa", "Remoção Carbono tCO2e")
    _, creditos = por_categoria_fato(base, "fSustentabilidade", "Tipo Iniciativa", "Créditos Carbono tCO2e")
    graficos.append(Grafico(id="carbono_iniciativa", titulo="Remoção e créditos de carbono por tipo de iniciativa (tCO2e)",
                            tipo="barra_h", categorias=tipos, formato="num", series=[
                                Serie(nome="Remoção de carbono", valores=remocao, cor=cor),
                                Serie(nome="Créditos de carbono", valores=creditos, cor="#7BC08F")]))
    colunas = {**BASICAS,
               "tipo": lambda p, b: _primeiro(b, "fSustentabilidade", "Tipo Iniciativa"),
               "area": lambda p, b: calcular(b, "Área Intervenção ha"),
               "remocao": lambda p, b: calcular(b, "Remoção Carbono tCO2e"),
               "creditos": lambda p, b: calcular(b, "Créditos Carbono tCO2e"),
               "certificacao": lambda p, b: _primeiro(b, "fSustentabilidade", "Certificação Ambiental")}
    tabela = Tabela(id="projetos_sustentabilidade", titulo="Projetos de sustentabilidade ambiental", colunas=[
        PROJETO, MUNICIPIO, STATUS,
        Coluna(chave="tipo", rotulo="Tipo de iniciativa", formato="texto"),
        Coluna(chave="area", rotulo="Área (ha)", formato="num"),
        Coluna(chave="remocao", rotulo="Remoção (tCO2e)", formato="num"),
        Coluna(chave="creditos", rotulo="Créditos (tCO2e)", formato="num"),
        Coluna(chave="certificacao", rotulo="Certificação", formato="simnao"),
    ], linhas=_linhas(base, colunas))
    return cards, graficos, [tabela]


SETORES: dict[str, Setor] = {
    "energia-renovavel": Setor("Energia Renovável", "Capacidade, geração e emissões evitadas dos parques", _energia),
    "hidrogenio-verde": Setor("Hidrogênio Verde", "Eletrólise, produção e origem da energia", _hidrogenio),
    "mineracao": Setor("Mineração", "Produção, faturamento e conformidade ambiental", _mineracao),
    "sustentabilidade": Setor("Sustentabilidade Ambiental", "Áreas de intervenção, remoção e créditos de carbono",
                              _sustentabilidade),
}


def montar(base: Base, slug: str) -> Pagina:
    setor = SETORES[slug]
    b = do_setor(base, setor.nome)
    ctx = Contexto(b)
    cards, graficos, tabelas = setor.montar(b, ctx, _cor(base, setor.nome))
    return Pagina(titulo=setor.nome, subtitulo=setor.subtitulo, cards=cards, graficos=graficos, tabelas=tabelas)
