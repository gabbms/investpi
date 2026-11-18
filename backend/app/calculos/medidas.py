"""Medidas do painel, portadas literalmente das medidas DAX do Power BI v3.

Fonte: PowerBI/Painel_ASG_v3/.../tables/_Medidas.tmdl. Cada medida tem o mesmo
nome da medida DAX.

Semântica de BLANK: internamente `None` faz o papel do BLANK do DAX —
SUM/COUNTROWS de conjunto vazio dão BLANK, BLANK propaga em DIVIDE e em
multiplicação, e é 0 em somas. Isso importa para o Índice ASG: uma meta cujo
valor é BLANK fica fora do índice. Na saída pública (`calcular`), somas e
contagens simples vazias viram 0 (o card mostra 0); razões, médias e medidas
com `IF(ISEMPTY(...), BLANK(), ...)` continuam `None` (o card mostra "—").
"""
from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from app.planilha.leitura import Base

Valor = float | None

# --------------------------------------------------------------------------- helpers DAX


def soma(s: pd.Series) -> Valor:
    s = s.dropna()
    return None if s.empty else float(s.sum())


def contar(n: int) -> Valor:
    return None if n == 0 else float(n)


def contar_sim(df: pd.DataFrame, coluna: str) -> Valor:
    return contar(int((df[coluna] == "Sim").sum()))


def distintos(s: pd.Series) -> Valor:
    return contar(int(s.nunique(dropna=True)))


def media(s: pd.Series) -> Valor:
    s = s.dropna()
    return None if s.empty else float(s.mean())


def dividir(a: Valor, b: Valor) -> Valor:
    if a is None or b is None or b == 0:
        return None
    return a / b


def mais(*vs: Valor) -> Valor:
    """Soma DAX: BLANK conta como 0; tudo BLANK dá BLANK."""
    reais = [v for v in vs if v is not None]
    return None if not reais else float(sum(reais))


def vezes(a: Valor, k: float) -> Valor:
    return None if a is None else a * k


def soma_mais_zero(df: pd.DataFrame, coluna: str) -> Valor:
    """IF ( ISEMPTY ( t ), BLANK (), SUM ( t[coluna] ) + 0 )"""
    return None if df.empty else (soma(df[coluna]) or 0.0)


def do_setor(base: Base, setor: str) -> Base:
    """KEEPFILTERS ( dProjeto[Setor Investe] = setor ) dentro do filtro atual."""
    from app.calculos.filtros import restringir_projetos

    p = base["dProjeto"]
    return restringir_projetos(base, p.loc[p["Setor Investe"] == setor, "Código Projeto"])


def ultimo_mes(fin: pd.DataFrame) -> pd.DataFrame:
    """LASTDATE ( fFinanceiro[Data Referência] ) no filtro atual."""
    if fin.empty:
        return fin
    return fin[fin["Data Referência"] == fin["Data Referência"].max()]


# --------------------------------------------------------------------------- registro

MEDIDAS: dict[str, Callable[[Base], Valor]] = {}
# Medidas que são SUM/COUNTROWS/DISTINCTCOUNT simples: vazio vira 0 na saída.
ADITIVAS: set[str] = set()


def medida(nome: str, aditiva: bool = False):
    def registrar(fn):
        MEDIDAS[nome] = fn
        if aditiva:
            ADITIVAS.add(nome)
        return fn

    return registrar


def m(base: Base, nome: str) -> Valor:
    """Valor DAX interno (com BLANK), para compor medidas."""
    return MEDIDAS[nome](base)


def calcular(base: Base, nome: str) -> Valor:
    if nome not in MEDIDAS:
        raise KeyError(f"Medida desconhecida: {nome}")
    v = MEDIDAS[nome](base)
    if v is None and nome in ADITIVAS:
        return 0.0
    return v


def _reg_soma(nome: str, tabela: str, coluna: str):
    medida(nome, aditiva=True)(lambda b: soma(b[tabela][coluna]))


# --------------------------------------------------------------------------- 1. Visão geral

medida("Qtd Projetos", aditiva=True)(lambda b: contar(len(b["dProjeto"])))
medida("Qtd Empresas", aditiva=True)(lambda b: distintos(b["dProjeto"]["Código Empresa"]))
medida("Qtd Municípios", aditiva=True)(lambda b: distintos(b["dProjeto"]["Município"]))
_reg_soma("Investimento Previsto", "dProjeto", "Investimento Previsto")
_reg_soma("Investimento Realizado", "dProjeto", "Investimento Realizado")


@medida("Empresas Confirmadas", aditiva=True)
def _empresas_confirmadas(b: Base) -> Valor:
    emp = b["dEmpresa"]
    confirmadas = set(emp.loc[emp["Status Relação"] == "Confirmado", "Código Empresa"])
    p = b["dProjeto"]
    return distintos(p.loc[p["Código Empresa"].isin(confirmadas), "Código Empresa"])


@medida("Qtd Países", aditiva=True)
def _qtd_paises(b: Base) -> Valor:
    emp = b["dEmpresa"]
    return distintos(emp.loc[emp["Código Empresa"].isin(set(b["dProjeto"]["Código Empresa"])), "País"])


medida("% Investimento Realizado")(lambda b: dividir(m(b, "Investimento Realizado"), m(b, "Investimento Previsto")))


@medida("% Atingimento Médio da Meta")
def _atingimento_medio(b: Base) -> Valor:
    p = b["dProjeto"]
    razoes = [dividir(r, mt) for r, mt in zip(p["Valor Realizado"], p["Valor Meta"])]
    razoes = [x for x in razoes if x is not None]
    return None if not razoes else sum(razoes) / len(razoes)


for _nome, _setor in [
    ("Investimento Energia Renovável", "Energia Renovável"),
    ("Investimento Hidrogênio Verde", "Hidrogênio Verde"),
    ("Investimento Mineração", "Mineração"),
    ("Investimento Sustentabilidade", "Sustentabilidade Ambiental"),
]:
    medida(_nome, aditiva=True)(lambda b, s=_setor: m(do_setor(b, s), "Investimento Previsto"))

# --------------------------------------------------------------------------- 2–5. Setores

_reg_soma("Capacidade Instalada MW", "fEnergia", "Capacidade Instalada (MW)")
_reg_soma("Geração Anual MWh", "fEnergia", "Geração Anual (MWh)")
medida("Fator de Capacidade Médio")(
    lambda b: dividir(m(b, "Geração Anual MWh"), vezes(m(b, "Capacidade Instalada MW"), 8760))
)
medida("% Energia Renovável no Consumo")(
    lambda b: dividir(
        soma(do_setor(b, "Energia Renovável")["fAmbiental"]["Energia Renovável Consumida (MWh)"]),
        vezes(soma(b["fEnergia"]["Consumo Médio Mensal (MWh)"]), 12),
    )
)

_reg_soma("Capacidade Eletrólise MW", "fHidrogenio", "Capacidade Eletrolisador (MW)")
_reg_soma("Produção H2 t", "fHidrogenio", "Produção H2 (t)")
medida("Intensidade Energética H2 kWh/kg")(
    lambda b: dividir(soma(b["fHidrogenio"]["Consumo Energia Eletrolisador (MWh)"]), m(b, "Produção H2 t"))
)


@medida("% Renovável nos Eletrolisadores")
def _renovavel_eletrolisadores(b: Base) -> Valor:
    h = b["fHidrogenio"]
    ponderado = soma(h["Consumo Energia Eletrolisador (MWh)"] * h["% Renovável Eletrolisador"])
    return dividir(ponderado, soma(h["Consumo Energia Eletrolisador (MWh)"]))


medida("Intensidade Hídrica H2 m3/t")(
    lambda b: dividir(soma(do_setor(b, "Hidrogênio Verde")["fAmbiental"]["Consumo Água (m3)"]), m(b, "Produção H2 t"))
)

_reg_soma("Produção ROM t", "fMineracao", "Produção ROM (t)")
_reg_soma("Quantidade Contido", "fMineracao", "Quantidade Contido")
_reg_soma("Faturamento Mineração", "fMineracao", "Faturamento Previsto")
_reg_soma("Valor de Venda Mineração", "fMineracao", "Valor Venda")
medida("Intensidade Hídrica Mineração m3/t")(
    lambda b: dividir(soma(do_setor(b, "Mineração")["fAmbiental"]["Consumo Água (m3)"]), m(b, "Produção ROM t"))
)
medida("% Mineração com Tecnologia Limpa")(lambda b: m(do_setor(b, "Mineração"), "% Projetos Tecnologia Limpa"))

_reg_soma("Área Intervenção ha", "fSustentabilidade", "Área Intervenção (ha)")
_reg_soma("Remoção Carbono tCO2e", "fSustentabilidade", "Remoção Carbono (tCO2e)")
_reg_soma("Créditos Carbono tCO2e", "fSustentabilidade", "Créditos Carbono (tCO2e)")
_reg_soma("Capacidade Processamento Anual", "fSustentabilidade", "Capacidade Processamento Anual")

# --------------------------------------------------------------------------- 6. Ambiental comum


def _pct_sim(tabela: str, coluna: str):
    return lambda b: dividir(contar_sim(b[tabela], coluna), contar(len(b[tabela])))


_reg_soma("Emissões CO2 tCO2e", "fAmbiental", "Emissões CO2 (tCO2e)")
_reg_soma("Emissões Evitadas tCO2e", "fAmbiental", "Emissões Evitadas (tCO2e)")
medida("Saldo Climático tCO2e")(
    lambda b: mais(m(b, "Emissões Evitadas tCO2e"), vezes(m(b, "Emissões CO2 tCO2e"), -1))
)
medida("Intensidade Emissões tCO2e/R$ mi")(
    lambda b: dividir(m(b, "Emissões CO2 tCO2e"), vezes(m(b, "Investimento Previsto"), 1 / 1_000_000))
)
medida("% Projetos Tecnologia Limpa")(_pct_sim("fAmbiental", "Tecnologia Limpa"))
_reg_soma("Consumo Água m3", "fAmbiental", "Consumo Água (m3)")
medida("% Água Reutilizada")(
    lambda b: dividir(soma(b["fAmbiental"]["Água Reutilizada (m3)"]), m(b, "Consumo Água m3"))
)
_reg_soma("Resíduos Gerados t", "fAmbiental", "Resíduos Gerados (t)")
medida("% Resíduos Reciclados")(
    lambda b: dividir(soma(b["fAmbiental"]["Resíduos Reciclados (t)"]), m(b, "Resíduos Gerados t"))
)
medida("% Resíduos Destinados Corretamente")(
    lambda b: dividir(soma(b["fAmbiental"]["Resíduos Destinados Corretamente (t)"]), m(b, "Resíduos Gerados t"))
)
medida("Projetos com Licenciamento", aditiva=True)(lambda b: contar_sim(b["fAmbiental"], "Licenciamento Ambiental"))
medida("% Licença Válida")(_pct_sim("fAmbiental", "Licença Válida"))
medida("Projetos com Plano de Recuperação", aditiva=True)(
    lambda b: contar_sim(b["fAmbiental"], "Plano Recuperação Ambiental")
)
_reg_soma("Área Recuperada ha", "fAmbiental", "Área Recuperada (ha)")
_reg_soma("Área Preservada ha", "fAmbiental", "Área Preservada (ha)")
medida("% Avaliação Impacto Ambiental")(_pct_sim("fAmbiental", "Avaliação Impacto Ambiental"))
medida("Incidentes Ambientais")(lambda b: soma_mais_zero(b["fAmbiental"], "Incidentes Ambientais"))

# --------------------------------------------------------------------------- 7. Social

_reg_soma("Empregos Diretos Previstos", "fSocial", "Empregos Diretos Previstos")
_reg_soma("Empregos Diretos Gerados", "fSocial", "Empregos Diretos Gerados")
_reg_soma("Empregos Indiretos Gerados", "fSocial", "Empregos Indiretos Gerados")
medida("% Empregos Gerados vs Previstos")(
    lambda b: dividir(m(b, "Empregos Diretos Gerados"), m(b, "Empregos Diretos Previstos"))
)
medida("Empregos por R$ milhão")(
    lambda b: dividir(m(b, "Empregos Diretos Previstos"), vezes(m(b, "Investimento Previsto"), 1 / 1_000_000))
)
for _nome, _col in [
    ("% Empregos População Local", "Empregos População Local"),
    ("% Empregos Mulheres", "Empregos Mulheres"),
    ("% Empregos PCD", "Empregos PCD"),
]:
    medida(_nome)(lambda b, c=_col: dividir(soma(b["fSocial"][c]), m(b, "Empregos Diretos Gerados")))
_reg_soma("Trabalhadores Capacitados", "fSocial", "Trabalhadores Capacitados")
medida("Horas Treinamento por Trabalhador")(
    lambda b: dividir(soma(b["fSocial"]["Horas Treinamento (h)"]), m(b, "Trabalhadores Capacitados"))
)
_reg_soma("Investimento Capacitação", "fSocial", "Investimento Capacitação")
_reg_soma("Programas Sociais", "fSocial", "Programas Sociais Apoiados")
_reg_soma("Beneficiários Programas Sociais", "fSocial", "Beneficiários Programas Sociais")
_reg_soma("Comunidades Beneficiadas", "fSocial", "Comunidades Beneficiadas")
_reg_soma("Investimento Social", "fSocial", "Investimento Social")
medida("% Consulta Comunidades")(_pct_sim("fSocial", "Consulta Comunidades"))
medida("% Avaliação Impacto Social")(_pct_sim("fSocial", "Avaliação Impacto Social"))
medida("Acidentes de Trabalho")(lambda b: soma_mais_zero(b["fSocial"], "Acidentes Trabalho"))
medida("Taxa Frequência Acidentes")(
    lambda b: dividir(vezes(m(b, "Acidentes de Trabalho"), 1_000_000), soma(b["fSocial"]["Horas Trabalhadas (h)"]))
)
_reg_soma("Ações SST", "fSocial", "Ações SST")
medida("% Fornecedores Locais")(
    lambda b: dividir(soma(b["fSocial"]["Valor Fornecedores Locais"]), m(b, "Orçamento Previsto"))
)
medida("Reclamações Sociais")(lambda b: soma_mais_zero(b["fSocial"], "Reclamações Sociais"))

# --------------------------------------------------------------------------- 8. Governança

medida("Orçamento Previsto", aditiva=True)(lambda b: soma(ultimo_mes(b["fFinanceiro"])["Orçamento Previsto"]))
_reg_soma("Valor Empenhado", "fFinanceiro", "Valor Empenhado")
_reg_soma("Valor Liquidado", "fFinanceiro", "Valor Liquidado")
_reg_soma("Valor Pago", "fFinanceiro", "Valor Pago")
medida("% Execução Orçamentária")(lambda b: dividir(m(b, "Valor Empenhado"), m(b, "Orçamento Previsto")))
medida("% Liquidado do Orçamento")(lambda b: dividir(m(b, "Valor Liquidado"), m(b, "Orçamento Previsto")))
medida("% Pago do Orçamento")(lambda b: dividir(m(b, "Valor Pago"), m(b, "Orçamento Previsto")))
medida("Saldo Orçamentário")(
    lambda b: mais(m(b, "Orçamento Previsto"), vezes(m(b, "Valor Empenhado"), -1))
)
medida("Índice Execução Financeira")(lambda b: dividir(m(b, "Valor Pago"), m(b, "Valor Empenhado")))


@medida("% Prestação de Contas Atualizada")
def _prestacao_contas(b: Base) -> Valor:
    u = ultimo_mes(b["fFinanceiro"])
    return dividir(contar_sim(u, "Prestação Contas Atualizada"), contar(len(u)))


_reg_soma("Valor Contratado", "fContratos", "Valor Contratado")
medida("Qtd Contratos", aditiva=True)(lambda b: contar(len(b["fContratos"])))


def _pct_contratos(coluna: str, valor: str = "Sim"):
    return lambda b: dividir(
        contar(int((b["fContratos"][coluna] == valor).sum())), m(b, "Qtd Contratos")
    )


medida("% Contratos em Execução")(_pct_contratos("Status Contrato", "Em execução"))
medida("% Contratos Documentação Completa")(_pct_contratos("Documentação Completa"))
medida("% Contratos Fiscalizados")(_pct_contratos("Contrato Fiscalizado"))
medida("% Irregularidades Corrigidas")(
    lambda b: dividir(soma(b["fContratos"]["Irregularidades Corrigidas"]), soma(b["fContratos"]["Irregularidades Identificadas"]))
)
medida("Auditorias Realizadas")(
    lambda b: None if b["fContratos"].empty else (contar_sim(b["fContratos"], "Auditoria Realizada") or 0.0)
)
medida("% Recomendações Atendidas")(
    lambda b: dividir(soma(b["fContratos"]["Recomendações Atendidas"]), soma(b["fContratos"]["Recomendações Emitidas"]))
)
medida("Denúncias Recebidas")(lambda b: soma_mais_zero(b["fContratos"], "Denúncias Recebidas"))
medida("% Denúncias Apuradas")(
    lambda b: dividir(soma(b["fContratos"]["Denúncias Apuradas"]), m(b, "Denúncias Recebidas"))
)
medida("Casos Fraude ou Corrupção")(
    lambda b: None if b["fContratos"].empty else (contar_sim(b["fContratos"], "Fraude ou Corrupção") or 0.0)
)
medida("% Colaboradores Treinados Integridade")(
    lambda b: dividir(soma(b["fEquipe"]["Colaboradores Treinados Integridade"]), soma(b["fEquipe"]["Colaboradores Totais"]))
)
_reg_soma("Treinamentos Integridade", "fEquipe", "Treinamentos Integridade")


@medida("% Projetos com Análise de Riscos")
def _analise_riscos(b: Base) -> Valor:
    c = b["fContratos"]
    return dividir(distintos(c.loc[c["Análise de Riscos"] == "Sim", "Código Projeto"]), m(b, "Qtd Projetos"))


medida("% Riscos Críticos Mitigados")(
    lambda b: dividir(soma(b["fContratos"]["Riscos Críticos Mitigados"]), soma(b["fContratos"]["Riscos Críticos"]))
)
medida("Tempo Médio Resposta dias")(lambda b: media(b["fTransparencia"]["Tempo Médio Resposta (dias)"]))
medida("% Informações Públicas Atualizadas")(_pct_sim("fTransparencia", "Informações Públicas Atualizadas"))
medida("% Dados Públicos Disponíveis")(_pct_sim("fTransparencia", "Dados Públicos Disponíveis"))
medida("Índice Transparência Médio")(lambda b: media(b["fTransparencia"]["Índice Transparência"]))
medida("% Custo Manutenção Realizado vs Previsto")(
    lambda b: dividir(soma(b["fManutencao"]["Custo Realizado"]), soma(b["fManutencao"]["Custo Previsto"]))
)

# --------------------------------------------------------------------------- 9–10. Índice ASG e metas


def _de_metas(fn_nome: str, *args):
    def calc(b: Base) -> Valor:
        from app.calculos import metas

        return getattr(metas, fn_nome)(b, *args)

    return calc


medida("Índice Ambiental")(_de_metas("indice_pilar", "Ambiental"))
medida("Índice Social")(_de_metas("indice_pilar", "Social"))
medida("Índice Governança")(_de_metas("indice_pilar", "Governança"))
medida("Índice ASG Geral")(_de_metas("indice_geral"))
medida("Metas Atingidas")(_de_metas("contar_status", "Atingida"))
medida("Metas em Atenção")(_de_metas("contar_status", "Atenção"))
medida("Metas Abaixo")(_de_metas("contar_status", "Abaixo"))
medida("% Metas Atingidas")(_de_metas("pct_metas_atingidas"))
