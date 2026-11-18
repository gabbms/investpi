"""Catálogo de Indicadores (plano exportar-indicadores-qualidade, Tarefa 15)."""
import pytest

from app import repositorio
from app.paginas.comum import texto_valor
from tests.apoio import base_modelo


@pytest.fixture
def com_versao(sessao_teste, usuarios):
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, base_modelo(), usuarios["admin"].id, "base.xlsx", [])
    yield
    repositorio.limpar_cache()


@pytest.mark.parametrize("v,f,esperado", [
    (0.5417, "pct", "54,2%"), (9.012e9, "brl", "R$ 9,0 bi"), (52.73e6, "brl", "R$ 52,7 mi"),
    (7236, "num", "7.236"), (2.119, "dec", "2,12"), (None, "num", "—"), (0, "brl", "R$ 0")])
def test_texto_valor(v, f, esperado):
    assert texto_valor(v, f) == esperado


def test_catalogo(cliente, com_versao, h_leitor):
    p = cliente.get("/api/painel/indicadores", headers=h_leitor).json()
    c = {x["id"]: x["valor"] for x in p["cards"]}
    assert c == {"Indicadores": 82, "Ambiental": 36, "Social": 22, "Governança": 24,
                 "Com meta ASG": 24, "Com referência GRI": 73}
    t = p["tabelas"][0]
    assert t["busca"] is True and len(t["linhas"]) == 82
    por_id = {l["id"]: l for l in t["linhas"]}
    assert por_id["IND01"]["valor"] == "R$ 9,0 bi"
    assert por_id["IND31"]["valor"] == "54,2%"
    assert por_id["IND55"]["valor"] == "2,12"
    assert por_id["IND62"]["valor"] == "10,4%"
    assert por_id["IND01"]["gri"] == "GRI 203-1" and por_id["IND01"]["ods"] == "ODS 7"
    assert por_id["IND31"]["status"] in {"Atingida", "Atenção", "Abaixo"}


def test_catalogo_respeita_filtro(cliente, com_versao, h_leitor):
    p = cliente.get("/api/painel/indicadores?setor=Mineração", headers=h_leitor).json()
    por_id = {l["id"]: l for l in p["tabelas"][0]["linhas"]}
    assert por_id["IND01"]["valor"] == "R$ 0"  # Mineração não tem energia renovável


def test_medida_desconhecida_vira_traco(cliente, sessao_teste, usuarios, h_leitor):
    b = base_modelo()
    b["dIndicador"].loc[0, "Medida DAX"] = "Medida Que Nao Existe"
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, b, usuarios["admin"].id, "x.xlsx", [])
    p = cliente.get("/api/painel/indicadores", headers=h_leitor).json()
    assert p["tabelas"][0]["linhas"][0]["valor"] == "—"
    repositorio.limpar_cache()


def test_subtitulo_conta_os_indicadores_da_versao(cliente, sessao_teste, usuarios, h_leitor):
    b = base_modelo()
    b["dIndicador"] = b["dIndicador"].iloc[:-1]
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, b, usuarios["admin"].id, "x.xlsx", [])
    p = cliente.get("/api/painel/indicadores", headers=h_leitor).json()
    assert p["subtitulo"].startswith("Catálogo dos 81 indicadores ASG")
    repositorio.limpar_cache()


def test_razao_por_milhao_tem_casas_decimais(cliente, com_versao, h_leitor):
    # "Empregos por R$ milhão" vale 0,43; como número inteiro apareceria "0"
    p = cliente.get("/api/painel/indicadores", headers=h_leitor).json()
    por_id = {l["id"]: l for l in p["tabelas"][0]["linhas"]}
    assert por_id["IND40"]["valor"] == "0,43"
