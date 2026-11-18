"""Visão Geral — espelha a página "Visão Executiva" do Power BI v3.

O mapa de bolhas do Power BI vira barras de investimento por município,
empilhadas por setor (spec §10).
"""
from app.calculos.filtros import restringir_projetos
from app.calculos.medidas import calcular, do_setor
from app.calculos.metas import indice_pilar
from app.paginas.comum import (
    COR_PILAR,
    Contexto,
    ordenar_desc,
    por_categoria_projeto,
    por_setor,
    setores_ordenados,
)
from app.paginas.tipos import Grafico, Pagina, Serie
from app.planilha.leitura import Base


def _investimento_por_municipio(base: Base) -> Grafico:
    p = base["dProjeto"]
    municipios, totais = por_categoria_projeto(base, "Município", "Investimento Previsto")
    municipios, _ = ordenar_desc(municipios, totais)
    series = []
    for setor, cor in setores_ordenados(base):
        valores = []
        for mun in municipios:
            sel = p.loc[(p["Município"] == mun) & (p["Setor Investe"] == setor), "Código Projeto"]
            valores.append(calcular(restringir_projetos(base, sel), "Investimento Previsto") if len(sel) else None)
        series.append(Serie(nome=setor, valores=valores, cor=cor))
    return Grafico(id="investimento_municipio", titulo="Investimento previsto por município",
                   tipo="barra_h_empilhada", categorias=municipios, series=series, formato="brl")


def montar(base: Base) -> Pagina:
    ctx = Contexto(base)
    setores, cores, valores = por_setor(base, ["Investimento Previsto"])

    indices = [
        Serie(nome=pilar, valores=[indice_pilar(do_setor(base, s), pilar) for s in setores], cor=COR_PILAR[pilar])
        for pilar in ("Ambiental", "Social", "Governança")
    ]
    status, qtd = por_categoria_projeto(base, "Status Projeto", "Qtd Projetos")

    return Pagina(
        titulo="Visão Geral",
        subtitulo="Carteira de projetos ASG acompanhados pela Investe Piauí",
        indice=ctx.card_indice("Índice ASG Geral", "Índice ASG Geral"),
        cards=[
            ctx.card("Investimento Previsto", "Investimento previsto", "brl"),
            ctx.card("Qtd Projetos", "Projetos", "num"),
            ctx.card("Empresas Confirmadas", "Empresas confirmadas", "num"),
            ctx.card("Empregos Diretos Gerados", "Empregos diretos gerados", "num"),
            ctx.card("Emissões Evitadas tCO2e", "Emissões evitadas (tCO2e)", "num"),
        ],
        graficos=[
            Grafico(id="investimento_setor", titulo="Investimento previsto por setor", tipo="barra_h",
                    categorias=setores,
                    series=[Serie(nome="Investimento previsto", valores=valores["Investimento Previsto"])],
                    formato="brl", cores_categorias=cores),
            _investimento_por_municipio(base),
            Grafico(id="indice_pilar_setor", titulo="Índice ASG por pilar e setor (0 a 100)", tipo="colunas",
                    categorias=setores, series=indices, formato="idx"),
            Grafico(id="projetos_status", titulo="Projetos por status", tipo="rosca",
                    categorias=status, series=[Serie(nome="Projetos", valores=qtd)], formato="num"),
        ],
    )
