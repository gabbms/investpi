"""Catálogo de Indicadores: os indicadores de dIndicador com GRI, ODS e valor atual."""
from __future__ import annotations

from app.calculos.medidas import MEDIDAS
from app.paginas.comum import Contexto, linha_valor, texto_valor
from app.paginas.tipos import Card, Coluna, FormatoValor, Pagina, Tabela
from app.planilha.leitura import Base, vazio

# Formato de dMetas → formato de valor. "idx" (Índice Transparência Médio, de 0 a 1) usa
# duas casas, como `fmt_meta`; o formato `idx` dos cards arredondaria 0,58 para 1.
FORMATO_META: dict[str, FormatoValor] = {"%": "pct", "n": "num", "dec": "dec", "idx": "dec"}
MOEDA = ("Investimento", "Valor", "Orçamento", "Custo", "Faturamento", "Saldo Orçamentário")
# " por " cobre razões como "Empregos por R$ milhão" (0,43), que como inteiro virariam 0
DECIMAL = ("Intensidade", "Fator", "Horas", " por ")


def _formatos_meta(base: Base) -> dict[str, str]:
    metas = base.get("dMetas")
    if metas is None:
        return {}
    return {r["Medida"]: r["Formato"] for _, r in metas.iterrows() if not vazio(r["Medida"])}


def formato_da_medida(nome: str, formatos_meta: dict[str, str] | None = None) -> FormatoValor:
    """Formato de exibição de uma medida: o de dMetas, senão deduzido do nome."""
    formato = (formatos_meta or {}).get(nome)
    if formato is not None:
        return FORMATO_META.get(str(formato).strip(), "num")
    if nome.startswith("%"):
        return "pct"
    if any(p in nome for p in MOEDA):
        return "brl"
    if nome.startswith(("Índice", "Taxa")) or any(p in nome for p in DECIMAL):
        return "dec"
    return "num"


def _texto(v) -> str | None:
    v = linha_valor(v)
    return None if v is None else str(v)


def _tem_gri(v) -> bool:
    return not vazio(v) and str(v).strip() != "-"


def valores_e_formatos(base: Base, ctx: Contexto | None = None) -> dict[str, tuple[float | None, FormatoValor]]:
    """ID Indicador → (valor atual, formato), respeitando a base filtrada.

    Medida que o sistema ainda não calcula (ex.: planilha nova) vale None. Um erro *dentro* de uma
    medida conhecida não é escondido.
    """
    ctx = ctx or Contexto(base)
    formatos = _formatos_meta(base)
    valores: dict[str, tuple[float | None, FormatoValor]] = {}
    for _, r in base["dIndicador"].iterrows():
        medida = r["Medida DAX"]
        conhecida = not vazio(medida) and medida in MEDIDAS
        valor = ctx.valor(medida) if conhecida else None
        valores[_texto(r["ID Indicador"])] = (valor, formato_da_medida(medida, formatos) if conhecida else "num")
    return valores


def valores_atuais(base: Base, ctx: Contexto | None = None) -> dict[str, str]:
    """ID Indicador → o texto da coluna "Valor atual" do catálogo (respeita a base filtrada)."""
    return {i: texto_valor(v, f) for i, (v, f) in valores_e_formatos(base, ctx).items()}


def montar(base: Base) -> Pagina:
    ctx = Contexto(base)
    ind = base["dIndicador"].sort_values("ID Indicador")
    por_medida = {r.medida: r for r in ctx.metas}
    numeros = valores_e_formatos(base, ctx)

    linhas = []
    for _, r in ind.iterrows():
        medida = r["Medida DAX"]
        valor, formato = numeros[_texto(r["ID Indicador"])]
        meta = None if vazio(medida) else por_medida.get(medida)
        linhas.append({
            "id": _texto(r["ID Indicador"]),
            "indicador": _texto(r["Indicador"]),
            "pilar": _texto(r["Pilar"]),
            "tema": _texto(r["Tema Material"]),
            "ods": _texto(r["ODS"]),
            "gri": _texto(r["Referência GRI"]),
            "valor": texto_valor(valor, formato),
            # para o Excel: o número em si e o formato (a tela usa só o texto acima)
            "valor_num": valor,
            "valor_formato": formato,
            "status": meta.status if meta else None,
            "calculo": _texto(r["Cálculo"]),
            "origem": _texto(r["Tabela de Origem"]),
        })

    pilares = list(ind["Pilar"])
    metas = base.get("dMetas")
    contagens = [
        ("Indicadores", len(ind)),
        ("Ambiental", pilares.count("Ambiental")),
        ("Social", pilares.count("Social")),
        ("Governança", pilares.count("Governança")),
        ("Com meta ASG", 0 if metas is None else len(metas)),
        ("Com referência GRI", sum(_tem_gri(g) for g in ind["Referência GRI"])),
    ]
    return Pagina(
        titulo="Indicadores",
        subtitulo=(f"Catálogo dos {len(ind)} indicadores ASG com cálculo, origem, ODS e referência GRI. "
                   "Os valores respeitam os filtros."),
        cards=[Card(id=t, titulo=t, valor=float(n), formato="num") for t, n in contagens],
        tabelas=[
            Tabela(
                id="catalogo",
                titulo="Catálogo de indicadores",
                busca=True,
                colunas=[
                    Coluna(chave="id", rotulo="ID", formato="texto"),
                    Coluna(chave="indicador", rotulo="Indicador", formato="texto"),
                    Coluna(chave="pilar", rotulo="Pilar", formato="texto"),
                    Coluna(chave="tema", rotulo="Tema", formato="texto"),
                    Coluna(chave="ods", rotulo="ODS", formato="texto"),
                    Coluna(chave="gri", rotulo="GRI", formato="texto"),
                    Coluna(chave="valor", rotulo="Valor atual", formato="texto"),
                    Coluna(chave="status", rotulo="Status", formato="status"),
                    Coluna(chave="calculo", rotulo="Cálculo", formato="texto"),
                    Coluna(chave="origem", rotulo="Origem", formato="texto"),
                ],
                linhas=linhas,
            )
        ],
    )
