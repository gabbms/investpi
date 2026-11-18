"""Medidas, metas e Índice ASG — valores de aceitação da spec §9 (iguais ao Power BI v3)."""
from collections import Counter

import pytest

from app.calculos.filtros import Filtros, aplicar_filtros
from app.calculos.medidas import calcular
from app.calculos.metas import avaliar_metas, cor_indice, indice_geral, indice_pilar, indice_tema, status_medida
from app.planilha.esquema import MEDIDAS_META
from tests.apoio import base_modelo


@pytest.fixture(scope="module")
def base():
    return base_modelo()


@pytest.mark.parametrize(
    "nome,esperado,tol",
    [
        ("Investimento Previsto", 42_829_000_000, 1),
        ("Qtd Projetos", 48, 0),
        ("Empresas Confirmadas", 17, 0),
        ("Empregos Diretos Gerados", 7236, 0),
        ("Emissões Evitadas tCO2e", 3_477_889, 1),
        ("% Contratos Fiscalizados", 0.55, 1e-9),
        ("% Licença Válida", 0.5417, 1e-4),
        ("% Execução Orçamentária", 0.2482, 1e-4),
        ("Taxa Frequência Acidentes", 2.119, 1e-3),
    ],
)
def test_valores_de_aceitacao(base, nome, esperado, tol):
    assert calcular(base, nome) == pytest.approx(esperado, abs=tol)


def test_todas_as_medidas_de_meta_calculam(base):
    for medida in MEDIDAS_META:
        calcular(base, medida)  # não pode lançar KeyError


def test_medida_desconhecida(base):
    with pytest.raises(KeyError):
        calcular(base, "Medida Inventada")


def test_orcamento_usa_ultimo_mes(base):
    fin = base["fFinanceiro"]
    ultimo = fin["Data Referência"].max()
    esperado = fin.loc[fin["Data Referência"] == ultimo, "Orçamento Previsto"].sum()
    assert calcular(base, "Orçamento Previsto") == pytest.approx(esperado)
    assert calcular(base, "Valor Empenhado") == pytest.approx(fin["Valor Empenhado"].sum())


def test_indices(base):
    assert round(indice_pilar(base, "Ambiental")) == 75
    assert round(indice_pilar(base, "Social")) == 67
    assert round(indice_pilar(base, "Governança")) == 62
    assert round(indice_geral(base)) == 68
    assert round(calcular(base, "Índice ASG Geral")) == 68


def test_status_das_metas(base):
    res = avaliar_metas(base)
    assert len(res) == 24
    assert Counter(r.status for r in res) == {"Atingida": 6, "Atenção": 6, "Abaixo": 12}
    assert calcular(base, "Metas Atingidas") == 6
    assert calcular(base, "Metas em Atenção") == 6
    assert calcular(base, "Metas Abaixo") == 12
    assert calcular(base, "% Metas Atingidas") == pytest.approx(0.25)


def test_status_medida(base):
    assert status_medida(base, "% Licença Válida") == "Abaixo"
    assert status_medida(base, "Investimento Previsto") is None


def test_cor_indice():
    assert cor_indice(75) == "verde"
    assert cor_indice(68) == "amarelo"
    assert cor_indice(49.9) == "vermelho"
    assert cor_indice(None) is None


def test_filtro_mineracao(base):
    b = aplicar_filtros(base, Filtros(setores=["Mineração"]))
    assert calcular(b, "Qtd Projetos") == 12
    assert calcular(b, "Investimento Previsto") == pytest.approx(5_330_000_000, abs=1e7)
    assert set(b["fAmbiental"]["Código Projeto"]) == set(b["dProjeto"]["Código Projeto"])
    assert set(b["dEmpresa"]["Código Empresa"]) == set(b["dProjeto"]["Código Empresa"])


def test_filtro_por_vice_presidencia(base):
    b = aplicar_filtros(base, Filtros(vps=["VP de Energias Renováveis e Hidrogênio Verde"]))
    assert set(b["dProjeto"]["Setor Investe"]) == {"Energia Renovável", "Hidrogênio Verde"}


def test_filtro_por_empresa(base):
    b = aplicar_filtros(base, Filtros(empresas=["Lusitana EcoEnergias S.A."]))
    assert set(b["dProjeto"]["Código Empresa"]) == {"EMP002"}
    assert calcular(b, "Qtd Projetos") == 2
    assert set(b["dEmpresa"]["Código Empresa"]) == {"EMP002"}


def test_filtro_vazio(base):
    b = aplicar_filtros(base, Filtros(municipios=["Inexistente"]))
    assert calcular(b, "Qtd Projetos") == 0
    assert calcular(b, "Investimento Previsto") == 0
    assert calcular(b, "% Licença Válida") is None
    assert indice_geral(b) is None
    for medida in MEDIDAS_META:
        calcular(b, medida)


def test_indice_tema_base_completa():
    b = base_modelo()
    assert indice_tema(b, "T4") == pytest.approx(50.0, abs=0.01)
    assert indice_tema(b, "T6") == pytest.approx(99.87, abs=0.01)
    assert indice_tema(b, "T7") == pytest.approx(71.53, abs=0.01)


def test_indice_tema_com_filtro_mineracao():
    b = aplicar_filtros(base_modelo(), Filtros(setores=["Mineração"], vps=[], status=[], municipios=[]))
    assert indice_tema(b, "T4") == pytest.approx(75.0, abs=0.01)
    assert indice_tema(b, "T6") == pytest.approx(92.59, abs=0.01)
    assert indice_tema(b, "T7") == pytest.approx(63.89, abs=0.01)


def test_indice_tema_inexistente_e_none():
    assert indice_tema(base_modelo(), "T99") is None


def test_indice_tema_ignora_espacos_no_codigo():
    b = base_modelo()
    b["dMetas"]["Tema Material"] = b["dMetas"]["Tema Material"].map(lambda v: f" {v} ")
    assert indice_tema(b, "T4") == pytest.approx(50.0, abs=0.01)


def test_indice_geral_nao_muda():
    assert round(indice_geral(base_modelo())) == 68


def test_pct_projetos_concluidos():
    assert calcular(base_modelo(), "% Projetos Concluídos") == pytest.approx(5 / 48)
