"""Telas Ambiental, Social, Governança e Metas ASG (spec §10)."""
import pytest

from app import repositorio
from tests.apoio import base_modelo


@pytest.fixture
def com_versao(sessao_teste, usuarios):
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, base_modelo(), usuarios["admin"].id, "base.xlsx", [])
    yield
    repositorio.limpar_cache()


def pagina(cliente, h, nome, query=""):
    r = cliente.get(f"/api/painel/{nome}{query}", headers=h)
    assert r.status_code == 200, r.text
    return r.json()


def cards(p):
    return {c["id"]: c for c in p["cards"]}


def test_ambiental(cliente, com_versao, h_leitor):
    p = pagina(cliente, h_leitor, "ambiental")
    assert p["indice"]["id"] == "Índice Ambiental"
    assert round(p["indice"]["valor"]) == 75
    c = cards(p)
    assert list(c) == [
        "Emissões CO2 tCO2e", "Emissões Evitadas tCO2e", "Remoção Carbono tCO2e",
        "Créditos Carbono tCO2e", "Área Preservada ha", "% Licença Válida",
    ]
    assert c["% Licença Válida"]["valor"] == pytest.approx(0.5417, abs=1e-4)
    assert c["% Licença Válida"]["status"] == "vermelho"
    assert c["% Licença Válida"]["formato"] == "pct"
    assert len(p["graficos"]) == 4


def test_social(cliente, com_versao, h_leitor):
    p = pagina(cliente, h_leitor, "social")
    assert round(p["indice"]["valor"]) == 67
    c = cards(p)
    assert c["Empregos Diretos Gerados"]["valor"] == 7236
    assert c["% Empregos Mulheres"]["valor"] == pytest.approx(0.25, abs=1e-3)
    assert c["% Empregos Mulheres"]["status"] == "amarelo"
    assert c["Taxa Frequência Acidentes"]["formato"] == "dec"
    tabela = p["tabelas"][0]
    assert len(tabela["linhas"]) == 48
    assert {col["chave"] for col in tabela["colunas"]} >= {"projeto", "setor", "empregos", "pct_mulheres"}


def test_governanca(cliente, com_versao, h_leitor):
    p = pagina(cliente, h_leitor, "governanca")
    assert round(p["indice"]["valor"]) == 62
    c = cards(p)
    assert c["% Contratos Fiscalizados"]["status"] == "vermelho"
    assert c["Casos Fraude ou Corrupção"]["valor"] == 4
    assert c["% Execução Orçamentária"]["valor"] == pytest.approx(0.2482, abs=1e-4)
    for medida in ("Orçamento Previsto", "% Liquidado do Orçamento", "% Pago do Orçamento"):
        assert medida in c
    assert len(p["tabelas"][0]["linhas"]) == 60


def test_metas(cliente, com_versao, h_leitor):
    p = pagina(cliente, h_leitor, "metas")
    c = cards(p)
    assert c["% Metas Atingidas"]["valor"] == pytest.approx(0.25)
    assert c["Metas Atingidas"]["valor"] == 6
    assert c["Metas em Atenção"]["valor"] == 6
    assert c["Metas Abaixo"]["valor"] == 12
    assert [len(t["linhas"]) for t in p["tabelas"]] == [8, 7, 9]
    primeira = p["tabelas"][0]["linhas"][0]
    assert primeira == {
        "indicador": "Projetos com licença ambiental válida",
        "peso": 2,
        "atual": "54,2%",
        "meta": "≥ 100%",
        "status": "Abaixo",
    }
    taxa = next(l for l in p["tabelas"][1]["linhas"] if l["indicador"].startswith("Taxa"))
    assert taxa["atual"] == "2,1"
    assert taxa["meta"] == "≤ 2,0"


@pytest.mark.parametrize("nome", ["visao-geral", "ambiental", "social", "governanca", "metas"])
def test_filtro_sem_projetos(cliente, com_versao, h_leitor, nome):
    p = pagina(cliente, h_leitor, nome, "?municipio=Inexistente")
    assert p["titulo"]


def test_pagina_inexistente(cliente, com_versao, h_leitor):
    assert cliente.get("/api/painel/nao-existe", headers=h_leitor).status_code == 404
