"""Telas de temas materiais T4, T6 e T7 (adendo ao plano principal)."""
import pytest

from app import repositorio
from tests.apoio import base_modelo


@pytest.fixture
def com_versao(sessao_teste, usuarios):
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, base_modelo(), usuarios["admin"].id, "base.xlsx", [])
    yield
    repositorio.limpar_cache()


def tema(cliente, h, slug, query=""):
    r = cliente.get(f"/api/painel/tema/{slug}{query}", headers=h)
    assert r.status_code == 200, r.text
    p = r.json()
    return p, {c["id"]: c for c in p["cards"]}


def test_t4(cliente, com_versao, h_leitor):
    p, c = tema(cliente, h_leitor, "riscos-climaticos")
    assert p["titulo"] == "T4 Riscos climáticos e resiliência"
    assert p["indice"]["valor"] == pytest.approx(50.0, abs=0.01)
    assert c["Emissões CO2 tCO2e"]["valor"] == 291160
    assert c["Saldo Climático tCO2e"]["valor"] == pytest.approx(3186729, abs=1)
    assert c["Intensidade Emissões tCO2e/R$ mi"]["valor"] == pytest.approx(6.80, abs=0.01)
    assert c["% Projetos com Análise de Riscos"]["valor"] == pytest.approx(0.854, abs=1e-3)
    assert c["Incidentes Ambientais"]["valor"] == 13
    metas = p["tabelas"][0]["linhas"]
    assert [m["status"] for m in metas] == ["Atingida", "Abaixo"]
    assert len(p["tabelas"][1]["linhas"]) == 48


def test_t6(cliente, com_versao, h_leitor):
    p, c = tema(cliente, h_leitor, "energia-limpa")
    assert p["indice"]["valor"] == pytest.approx(99.87, abs=0.01)
    assert c["Capacidade Instalada MW"]["valor"] == 1905
    assert c["% Renovável nos Eletrolisadores"]["status"] == "amarelo"
    assert c["% Projetos Tecnologia Limpa"]["valor"] == pytest.approx(0.958, abs=1e-3)
    assert "Atenção" in [m["status"] for m in p["tabelas"][0]["linhas"]]


def test_t6_ajuda_explica_arredondamento(cliente, com_versao, h_leitor):
    p, _ = tema(cliente, h_leitor, "energia-limpa")
    assert "Tema Material" in p["indice"]["ajuda"]
    assert "arredondado" in p["indice"]["ajuda"]


def test_t7(cliente, com_versao, h_leitor):
    p, c = tema(cliente, h_leitor, "licenca-social")
    assert p["indice"]["valor"] == pytest.approx(71.53, abs=0.01)
    assert c["% Consulta Comunidades"]["valor"] == pytest.approx(0.625, abs=1e-3)
    assert c["Comunidades Beneficiadas"]["valor"] == 152
    assert c["Investimento Social"]["valor"] == pytest.approx(52.73e6, abs=1e3)
    assert "% Fornecedores Locais" not in c
    assert len(p["tabelas"][1]["linhas"]) == 18   # projetos sem consulta


def test_tema_com_filtro(cliente, com_versao, h_leitor):
    p, _ = tema(cliente, h_leitor, "riscos-climaticos", "?setor=Mineração")
    assert p["indice"]["valor"] == pytest.approx(75.0, abs=0.01)


@pytest.mark.parametrize("slug", ["riscos-climaticos", "energia-limpa", "licenca-social"])
def test_tema_sem_metas_mensuraveis(cliente, com_versao, h_leitor, slug):
    p, _ = tema(cliente, h_leitor, slug, "?municipio=Inexistente")
    assert p["indice"]["valor"] is None
    assert p["indice"]["status"] is None


def test_graficos_tem_um_valor_por_setor(cliente, com_versao, h_leitor):
    p, _ = tema(cliente, h_leitor, "energia-limpa")
    for g in p["graficos"]:
        assert len(g["categorias"]) == 4
        assert all(len(s["valores"]) == 4 for s in g["series"])


def test_tema_inexistente(cliente, com_versao, h_leitor):
    r = cliente.get("/api/painel/tema/xyz", headers=h_leitor)
    assert r.status_code == 404
    assert r.json() == {"detail": "Tema não encontrado"}


def test_tema_exige_login(cliente, com_versao):
    assert cliente.get("/api/painel/tema/energia-limpa").status_code == 401
