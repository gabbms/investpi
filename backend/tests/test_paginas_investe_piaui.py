"""Tela "Investe Piauí": indicadores ASG da própria instituição (gestão, operação, impacto)."""
import pytest

from app import repositorio
from tests.apoio import base_modelo

AVISO_SEM_ABA = "A planilha ainda não tem a aba dInstitucional."


def _salvar(sessao, usuarios, base):
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao, base, usuarios["admin"].id, "base.xlsx", [])


@pytest.fixture
def com_versao(sessao_teste, usuarios):
    _salvar(sessao_teste, usuarios, base_modelo())
    yield
    repositorio.limpar_cache()


def pagina(cliente, h, nome="investe-piaui", query=""):
    r = cliente.get(f"/api/painel/{nome}{query}", headers=h)
    assert r.status_code == 200, r.text
    return r.json()


def secoes(p):
    return {s["id"]: s for s in p["secoes"]}


def cards_operacao(p):
    return {c["id"]: c for sub in secoes(p)["operacao"]["subsecoes"] for c in sub["cards"]}


def test_tres_secoes(cliente, com_versao, h_leitor):
    p = pagina(cliente, h_leitor)
    assert p["titulo"] == "Investe Piauí"
    assert p["cards"] == []
    assert [s["id"] for s in p["secoes"]] == ["gestao", "operacao", "impacto"]
    op = secoes(p)["operacao"]
    assert op["selo"] == "Dados de demonstração"
    assert [s["titulo"] for s in op["subsecoes"]] == ["Ambiental", "Social", "Governança"]
    assert len(cards_operacao(p)) == 15


def test_card_institucional(cliente, com_versao, h_leitor):
    c = cards_operacao(pagina(cliente, h_leitor))["INS01"]
    assert c["titulo"] == "Consumo de energia da sede (MWh)"
    assert c["valor"] == 162
    assert c["anterior"] == 184
    assert c["rotulo_anterior"] == "2025"
    assert c["status"] == "amarelo"


def test_gestao_usa_carteira(cliente, com_versao, h_leitor):
    gestao = {c["id"]: c for c in secoes(pagina(cliente, h_leitor))["gestao"]["cards"]}
    assert list(gestao) == [
        "% Contratos Fiscalizados", "% Recomendações Atendidas", "% Execução Orçamentária",
        "% Prestação de Contas Atualizada", "% Colaboradores Treinados Integridade",
        "Tempo Médio Resposta dias", "Casos Fraude ou Corrupção",
    ]
    governanca = {c["id"]: c for c in pagina(cliente, h_leitor, "governanca")["cards"]}
    assert gestao["% Contratos Fiscalizados"]["valor"] == governanca["% Contratos Fiscalizados"]["valor"]
    assert gestao["% Contratos Fiscalizados"]["status"] == "vermelho"


def test_impacto(cliente, com_versao, h_leitor):
    impacto = {c["id"]: c for c in secoes(pagina(cliente, h_leitor))["impacto"]["cards"]}
    assert list(impacto) == [
        "Investimento Previsto", "Empresas Confirmadas", "Empregos Diretos Gerados", "Emissões Evitadas tCO2e",
    ]
    assert impacto["Empresas Confirmadas"]["valor"] == 17


def test_sem_aba_institucional(cliente, sessao_teste, usuarios, h_leitor):
    b = base_modelo()
    del b["dInstitucional"]
    _salvar(sessao_teste, usuarios, b)
    try:
        op = secoes(pagina(cliente, h_leitor))["operacao"]
    finally:
        repositorio.limpar_cache()
    assert op["descricao"] == AVISO_SEM_ABA
    assert op["subsecoes"] == [] and op["cards"] == []
    assert op["selo"] is None


def test_outras_telas_sem_secoes(cliente, com_versao, h_leitor):
    assert pagina(cliente, h_leitor, "visao-geral")["secoes"] == []
