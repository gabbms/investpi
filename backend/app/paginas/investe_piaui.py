"""Tela "Investe Piauí": os indicadores ASG da própria instituição, em três blocos.

1. Nossa gestão: a Governança da carteira (contratos, orçamento, servidores, transparência),
   que na prática é a gestão feita pela Investe Piauí.
2. Nossa operação: a sede, pela aba opcional dInstitucional (não muda com os filtros).
3. Nosso impacto: o que a instituição ajudou a atrair.
"""
from __future__ import annotations

from app.calculos.institucional import ItemInstitucional, avaliar_institucional
from app.paginas.comum import Contexto
from app.paginas.tipos import Card, FormatoValor, Pagina, Secao
from app.planilha.leitura import Base

AVISO_SEM_ABA = "A planilha ainda não tem a aba dInstitucional."
AVISO_ABA_VAZIA = "A aba dInstitucional está vazia: preencha uma linha por indicador da sede."
SELO_DEMONSTRACAO = "Dados de demonstração"
ORDEM_PILARES = ("Ambiental", "Social", "Governança")

GESTAO: list[tuple[str, str, FormatoValor]] = [
    ("% Contratos Fiscalizados", "Contratos fiscalizados", "pct"),
    ("% Recomendações Atendidas", "Recomendações de auditoria atendidas", "pct"),
    ("% Execução Orçamentária", "Execução orçamentária", "pct"),
    ("% Prestação de Contas Atualizada", "Prestação de contas atualizada", "pct"),
    ("% Colaboradores Treinados Integridade", "Colaboradores treinados em integridade", "pct"),
    ("Tempo Médio Resposta dias", "Tempo médio de resposta (dias)", "dec"),
    ("Casos Fraude ou Corrupção", "Casos de fraude ou corrupção", "num"),
]

IMPACTO: list[tuple[str, str, FormatoValor]] = [
    ("Investimento Previsto", "Investimento previsto atraído", "brl"),
    ("Empresas Confirmadas", "Empresas confirmadas", "num"),
    ("Empregos Diretos Gerados", "Empregos diretos gerados", "num"),
    ("Emissões Evitadas tCO2e", "Emissões evitadas (tCO2e)", "num"),
]


def _card(item: ItemInstitucional) -> Card:
    # "%" já aparece no valor (48,0%); as outras unidades (MWh, m³, nº) vão no título
    titulo = f"{item.indicador} ({item.unidade})" if item.unidade and item.unidade != "%" else item.indicador
    return Card(
        id=item.id, titulo=titulo, valor=item.valor, formato=item.formato, status=item.status,
        anterior=item.anterior,
        rotulo_anterior=None if item.anterior is None or item.ano is None else str(item.ano - 1),
    )


def _referencia(itens: list[ItemInstitucional]) -> str:
    anos = sorted({i.ano for i in itens if i.ano is not None})
    if not anos:
        return ""
    if len(anos) == 1:
        return f" Ano de referência: {anos[0]}."
    return f" Anos de referência: {anos[0]} a {anos[-1]} (cada card mostra o seu)."


def _operacao(base: Base, itens: list[ItemInstitucional]) -> Secao:
    titulo = "Nossa operação"
    if not itens:
        aviso = AVISO_ABA_VAZIA if "dInstitucional" in base else AVISO_SEM_ABA
        return Secao(id="operacao", titulo=titulo, descricao=aviso)
    pilares = list(ORDEM_PILARES) + sorted({i.pilar for i in itens} - set(ORDEM_PILARES))
    subsecoes = [
        Secao(id=f"operacao-{p.lower()}", titulo=p, cards=[_card(i) for i in itens if i.pilar == p])
        for p in pilares
        if any(i.pilar == p for i in itens)
    ]
    return Secao(
        id="operacao", titulo=titulo,
        descricao="Indicadores da sede, informados na aba dInstitucional. Não mudam com os filtros." + _referencia(itens),
        selo=SELO_DEMONSTRACAO if any(i.demonstracao for i in itens) else None,
        subsecoes=subsecoes,
    )


def montar(base: Base) -> Pagina:
    ctx = Contexto(base)
    return Pagina(
        titulo="Investe Piauí",
        subtitulo="Indicadores ASG da própria instituição: como ela gere, como opera e o que ajuda a atrair",
        secoes=[
            Secao(id="gestao", titulo="Nossa gestão",
                  descricao="Contratos, orçamento, servidores e transparência dos projetos acompanhados.",
                  cards=[ctx.card(m, t, f) for m, t, f in GESTAO]),
            _operacao(base, avaliar_institucional(base)),
            Secao(id="impacto", titulo="Nosso impacto",
                  descricao="O que a carteira de projetos atraída pela Investe Piauí entrega.",
                  cards=[ctx.card(m, t, f) for m, t, f in IMPACTO]),
        ],
    )
