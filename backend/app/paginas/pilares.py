"""Telas Ambiental, Social, Governança e Metas ASG — espelham as páginas do Power BI v3."""
from __future__ import annotations

from app.calculos.medidas import calcular
from app.calculos.metas import ResultadoMeta
from app.paginas.comum import (
    COR_PILAR,
    Contexto,
    fmt_meta,
    linha_valor,
    ordenar_desc,
    por_categoria_fato,
    por_categoria_projeto,
    por_projeto,
    por_setor,
    texto_meta,
)
from app.paginas.tipos import Coluna, Grafico, Pagina, Serie, Tabela
from app.planilha.leitura import Base

CINZA = "#7B8794"
AZUL_AGUA = "#0277BD"


def _series_por_setor(base: Base, medidas: list[tuple[str, str, str | None]]):
    setores, _, valores = por_setor(base, [m for m, _, _ in medidas])
    return setores, [Serie(nome=nome, valores=valores[m], cor=cor) for m, nome, cor in medidas]


def _projetos(base: Base) -> list[tuple[str, dict, Base]]:
    """(código, linha de dProjeto, base só do projeto), em ordem de nome."""
    p = base["dProjeto"].sort_values("Nome Projeto")
    return [(r["Código Projeto"], r, por_projeto(base, r["Código Projeto"])) for _, r in p.iterrows()]


def _valor_fato(b: Base, tabela: str, coluna: str):
    df = b[tabela]
    return linha_valor(df[coluna].iloc[0]) if len(df) else None


# --------------------------------------------------------------------------- Ambiental


def ambiental(base: Base) -> Pagina:
    ctx = Contexto(base)
    setores, emissoes = _series_por_setor(base, [
        ("Emissões CO2 tCO2e", "Emissões geradas", CINZA),
        ("Emissões Evitadas tCO2e", "Emissões evitadas", COR_PILAR["Ambiental"]),
    ])
    _, agua = _series_por_setor(base, [
        ("% Água Reutilizada", "Água reutilizada", AZUL_AGUA),
        ("% Resíduos Reciclados", "Resíduos reciclados", "#6D9F3A"),
        ("% Resíduos Destinados Corretamente", "Resíduos destinados corretamente", COR_PILAR["Ambiental"]),
    ])
    _, licencas = _series_por_setor(base, [
        ("% Licença Válida", "Licença válida", COR_PILAR["Ambiental"]),
        ("% Avaliação Impacto Ambiental", "Avaliação de impacto ambiental", "#0E6B3B"),
        ("% Projetos Tecnologia Limpa", "Tecnologia limpa", "#7BC08F"),
    ])
    tipos, areas = por_categoria_fato(base, "fSustentabilidade", "Tipo Iniciativa", "Área Intervenção ha")
    tipos, areas = ordenar_desc(tipos, areas)

    return Pagina(
        titulo="Ambiental",
        subtitulo="Emissões, licenciamento, água e resíduos dos projetos",
        indice=ctx.card_indice("Índice Ambiental", "Índice Ambiental"),
        cards=[
            ctx.card("Emissões CO2 tCO2e", "Emissões de CO2 (tCO2e)", "num"),
            ctx.card("Emissões Evitadas tCO2e", "Emissões evitadas (tCO2e)", "num"),
            ctx.card("Remoção Carbono tCO2e", "Remoção de carbono (tCO2e)", "num"),
            ctx.card("Créditos Carbono tCO2e", "Créditos de carbono (tCO2e)", "num"),
            ctx.card("Área Preservada ha", "Área preservada (ha)", "num"),
            ctx.card("% Licença Válida", "Projetos com licença válida", "pct"),
        ],
        graficos=[
            Grafico(id="emissoes_setor", titulo="Emissões geradas e evitadas por setor (tCO2e)", tipo="colunas",
                    categorias=setores, series=emissoes, formato="num"),
            Grafico(id="agua_residuos_setor", titulo="Água e resíduos por setor", tipo="barra_h",
                    categorias=setores, series=agua, formato="pct"),
            Grafico(id="licencas_setor", titulo="Licenciamento, avaliação de impacto e tecnologia limpa por setor",
                    tipo="colunas", categorias=setores, series=licencas, formato="pct"),
            Grafico(id="area_iniciativa", titulo="Área de intervenção por tipo de iniciativa (ha)", tipo="barra_h",
                    categorias=tipos, series=[Serie(nome="Área de intervenção", valores=areas,
                                                     cor=COR_PILAR["Ambiental"])], formato="num"),
        ],
    )


# --------------------------------------------------------------------------- Social


def social(base: Base) -> Pagina:
    ctx = Contexto(base)
    setores, empregos = _series_por_setor(base, [
        ("Empregos Diretos Previstos", "Previstos", "#E8B07F"),
        ("Empregos Diretos Gerados", "Gerados", COR_PILAR["Social"]),
    ])
    municipios, benef = por_categoria_projeto(base, "Município", "Beneficiários Programas Sociais")
    municipios, benef = ordenar_desc(municipios, benef)

    linhas = []
    for _, proj, b in _projetos(base):
        linhas.append({
            "projeto": proj["Nome Projeto"],
            "setor": proj["Setor Investe"],
            "consulta": _valor_fato(b, "fSocial", "Consulta Comunidades"),
            "distribuicao": _valor_fato(b, "fSocial", "Distribuição Territorial"),
            "empregos": calcular(b, "Empregos Diretos Gerados") if len(b["fSocial"]) else None,
            "pct_mulheres": calcular(b, "% Empregos Mulheres"),
            "acidentes": calcular(b, "Acidentes de Trabalho"),
            "reclamacoes": calcular(b, "Reclamações Sociais"),
        })

    return Pagina(
        titulo="Social",
        subtitulo="Empregos, inclusão, comunidades e segurança no trabalho",
        indice=ctx.card_indice("Índice Social", "Índice Social"),
        cards=[
            ctx.card("Empregos Diretos Gerados", "Empregos diretos gerados", "num"),
            ctx.card("% Empregos Gerados vs Previstos", "Empregos gerados sobre previstos", "pct"),
            ctx.card("% Empregos População Local", "Empregos da população local", "pct"),
            ctx.card("% Empregos Mulheres", "Empregos de mulheres", "pct"),
            ctx.card("Beneficiários Programas Sociais", "Beneficiários de programas sociais", "num"),
            ctx.card("Taxa Frequência Acidentes", "Taxa de frequência de acidentes", "dec"),
        ],
        graficos=[
            Grafico(id="empregos_setor", titulo="Empregos diretos previstos e gerados por setor", tipo="colunas",
                    categorias=setores, series=empregos, formato="num"),
            Grafico(id="beneficiarios_municipio", titulo="Beneficiários de programas sociais por município",
                    tipo="barra_h", categorias=municipios,
                    series=[Serie(nome="Beneficiários", valores=benef, cor=COR_PILAR["Social"])], formato="num"),
        ],
        tabelas=[
            Tabela(id="sociais_projeto", titulo="Indicadores sociais por projeto", colunas=[
                Coluna(chave="projeto", rotulo="Projeto", formato="texto"),
                Coluna(chave="setor", rotulo="Setor", formato="texto"),
                Coluna(chave="consulta", rotulo="Consulta às comunidades", formato="simnao"),
                Coluna(chave="distribuicao", rotulo="Distribuição territorial", formato="texto"),
                Coluna(chave="empregos", rotulo="Empregos diretos", formato="num"),
                Coluna(chave="pct_mulheres", rotulo="% mulheres", formato="pct"),
                Coluna(chave="acidentes", rotulo="Acidentes", formato="num"),
                Coluna(chave="reclamacoes", rotulo="Reclamações", formato="num"),
            ], linhas=linhas),
        ],
    )


# --------------------------------------------------------------------------- Governança

LIMITE_TRANSPARENCIA = 15


def governanca(base: Base) -> Pagina:
    ctx = Contexto(base)
    setores, execucao = _series_por_setor(base, [
        ("% Execução Orçamentária", "Empenhado", "#8FA8D6"),
        ("% Liquidado do Orçamento", "Liquidado", "#4A6FB5"),
        ("% Pago do Orçamento", "Pago", COR_PILAR["Governança"]),
    ])

    transp = []
    for _, proj, b in _projetos(base):
        v = calcular(b, "Índice Transparência Médio")
        if v is not None:
            transp.append((proj["Nome Projeto"], v))
    transp.sort(key=lambda x: x[1])
    transp = transp[:LIMITE_TRANSPARENCIA]

    nomes = dict(zip(base["dProjeto"]["Código Projeto"], base["dProjeto"]["Nome Projeto"]))
    contratos = base["fContratos"].sort_values(["Código Projeto", "ID Processo"])
    linhas = [{
        "projeto": nomes.get(r["Código Projeto"]),
        "objeto": linha_valor(r["Objeto"]),
        "empresa": linha_valor(r["Empresa Contratada"]),
        "status": linha_valor(r["Status Contrato"]),
        "fiscalizado": linha_valor(r["Contrato Fiscalizado"]),
        "valor": linha_valor(r["Valor Contratado"]),
    } for _, r in contratos.iterrows()]

    return Pagina(
        titulo="Governança",
        subtitulo="Execução orçamentária, contratos, integridade e transparência",
        indice=ctx.card_indice("Índice Governança", "Índice Governança"),
        cards=[
            ctx.card("% Execução Orçamentária", "Execução orçamentária (empenhado)", "pct"),
            ctx.card("Índice Execução Financeira", "Execução financeira (pago sobre empenhado)", "pct"),
            ctx.card("% Contratos Fiscalizados", "Contratos fiscalizados", "pct"),
            ctx.card("% Recomendações Atendidas", "Recomendações atendidas", "pct"),
            ctx.card("% Riscos Críticos Mitigados", "Riscos críticos mitigados", "pct"),
            ctx.card("Casos Fraude ou Corrupção", "Casos de fraude ou corrupção", "num"),
            ctx.card("Orçamento Previsto", "Orçamento previsto", "brl"),
            ctx.card("% Liquidado do Orçamento", "Liquidado (% do orçamento)", "pct"),
            ctx.card("% Pago do Orçamento", "Pago (% do orçamento)", "pct"),
        ],
        graficos=[
            Grafico(id="execucao_setor", titulo="Empenhado, liquidado e pago por setor (% do orçamento)",
                    tipo="colunas", categorias=setores, series=execucao, formato="pct"),
            Grafico(id="transparencia_projeto",
                    titulo=f"Índice de transparência: os {LIMITE_TRANSPARENCIA} projetos com menor índice",
                    tipo="barra_h", categorias=[n for n, _ in transp],
                    series=[Serie(nome="Índice de transparência", valores=[v for _, v in transp],
                                  cor=COR_PILAR["Governança"])], formato="dec"),
        ],
        tabelas=[
            Tabela(id="contratos", titulo="Contratos", colunas=[
                Coluna(chave="projeto", rotulo="Projeto", formato="texto"),
                Coluna(chave="objeto", rotulo="Objeto", formato="texto"),
                Coluna(chave="empresa", rotulo="Empresa contratada", formato="texto"),
                Coluna(chave="status", rotulo="Situação", formato="texto"),
                Coluna(chave="fiscalizado", rotulo="Fiscalizado", formato="simnao"),
                Coluna(chave="valor", rotulo="Valor contratado", formato="brl"),
            ], linhas=linhas),
        ],
    )


# --------------------------------------------------------------------------- Metas ASG


def valor_atual(r: ResultadoMeta) -> str | None:
    """Medida DAX `Valor Atual`: "%" → 0,0% · "idx" → 0,00 · "dec" → 0,0 · senão inteiro."""
    if r.valor is None:
        return None
    if r.formato == "%":
        return f"{r.valor * 100:.1f}%".replace(".", ",")
    return fmt_meta(r.valor, r.formato)


def metas(base: Base) -> Pagina:
    ctx = Contexto(base)
    tabelas = []
    for pilar in ("Ambiental", "Social", "Governança"):
        linhas = [{
            "indicador": r.indicador,
            "peso": r.peso,
            "atual": valor_atual(r),
            "meta": texto_meta(r),
            "status": r.status,
        } for r in ctx.metas if r.pilar == pilar]
        tabelas.append(Tabela(id=f"metas_{pilar.lower()}", titulo=f"Pilar {pilar}", colunas=[
            Coluna(chave="indicador", rotulo="Indicador", formato="texto"),
            Coluna(chave="peso", rotulo="Peso", formato="num"),
            Coluna(chave="atual", rotulo="Atual", formato="texto"),
            Coluna(chave="meta", rotulo="Meta", formato="texto"),
            Coluna(chave="status", rotulo="Status", formato="status"),
        ], linhas=linhas))

    return Pagina(
        titulo="Metas ASG",
        subtitulo="Situação de cada indicador frente à meta proposta pelo grupo",
        cards=[
            ctx.card("% Metas Atingidas", "Metas atingidas (%)", "pct"),
            ctx.card("Metas Atingidas", "Atingidas", "num"),
            ctx.card("Metas em Atenção", "Em atenção", "num"),
            ctx.card("Metas Abaixo", "Abaixo do limite", "num"),
        ],
        tabelas=tabelas,
    )
