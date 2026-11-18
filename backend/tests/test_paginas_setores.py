"""Telas por setor (spec §10)."""
import pytest

from app import repositorio
from tests.apoio import base_modelo


@pytest.fixture
def com_versao(sessao_teste, usuarios):
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, base_modelo(), usuarios["admin"].id, "base.xlsx", [])
    yield
    repositorio.limpar_cache()


def setor(cliente, h, slug, query=""):
    r = cliente.get(f"/api/painel/setor/{slug}{query}", headers=h)
    assert r.status_code == 200, r.text
    p = r.json()
    return p, {c["id"]: c for c in p["cards"]}


def test_energia(cliente, com_versao, h_leitor):
    p, c = setor(cliente, h_leitor, "energia-renovavel")
    assert p["titulo"] == "Energia Renovável"
    assert c["Capacidade Instalada MW"]["valor"] == 1905
    assert c["Fator de Capacidade Médio"]["valor"] == pytest.approx(0.341, abs=1e-3)
    assert "% Energia Renovável no Consumo" in c
    assert len(p["tabelas"][0]["linhas"]) == 13


def test_hidrogenio(cliente, com_versao, h_leitor):
    p, c = setor(cliente, h_leitor, "hidrogenio-verde")
    assert c["Intensidade Energética H2 kWh/kg"]["valor"] == pytest.approx(54.3, abs=0.05)
    assert c["% Renovável nos Eletrolisadores"]["valor"] == pytest.approx(0.948, abs=1e-3)
    assert c["% Renovável nos Eletrolisadores"]["status"] == "amarelo"
    assert len(p["tabelas"][0]["linhas"]) == 12


def test_mineracao(cliente, com_versao, h_leitor):
    p, c = setor(cliente, h_leitor, "mineracao")
    assert c["Investimento Previsto"]["valor"] == pytest.approx(5.33e9, abs=1e7)
    assert {"Produção ROM t", "Faturamento Mineração", "Intensidade Hídrica Mineração m3/t",
            "% Mineração com Tecnologia Limpa"} <= set(c)
    assert len(p["tabelas"][0]["linhas"]) == 12


def test_sustentabilidade(cliente, com_versao, h_leitor):
    p, c = setor(cliente, h_leitor, "sustentabilidade")
    assert list(c) == ["Investimento Previsto", "Área Intervenção ha", "Remoção Carbono tCO2e", "Créditos Carbono tCO2e"]
    assert len(p["tabelas"][0]["linhas"]) == 11


def test_setor_soma_com_filtro_do_usuario(cliente, com_versao, h_leitor):
    _, c = setor(cliente, h_leitor, "energia-renovavel", "?setor=Mineração")
    assert c["Investimento Previsto"]["valor"] == 0
    assert c["Fator de Capacidade Médio"]["valor"] is None


def test_setor_inexistente(cliente, com_versao, h_leitor):
    assert cliente.get("/api/painel/setor/agricultura", headers=h_leitor).status_code == 404
