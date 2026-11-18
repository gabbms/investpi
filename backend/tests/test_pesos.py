"""Simulador de pesos das metas (plano simulador-pesos, Tarefa 27)."""
import pytest

from app import repositorio
from tests.apoio import base_modelo

GOVERNANCA = [f"META{n:02d}" for n in range(16, 25)]  # as 9 metas de Governança da base modelo


@pytest.fixture
def com_versao(sessao_teste, usuarios):
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, base_modelo(), usuarios["admin"].id, "base.xlsx", [])
    yield
    repositorio.limpar_cache()


def simular(cliente, h, pesos, query=""):
    return cliente.post(f"/api/painel/simular-pesos{query}", json={"pesos": pesos}, headers=h)


def test_sem_mudanca_igual_ao_oficial(cliente, com_versao, h_leitor):
    r = simular(cliente, h_leitor, {})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["simulado"] == d["oficial"]
    assert d["oficial"]["geral"] == pytest.approx(68.15, abs=0.05)
    assert d["oficial"]["Ambiental"] == pytest.approx(75.4, abs=0.05)
    assert d["oficial"]["Social"] == pytest.approx(66.8, abs=0.05)
    assert d["oficial"]["Governança"] == pytest.approx(62.2, abs=0.05)
    assert len(d["metas"]) == 24
    fraude = next(m for m in d["metas"] if m["id_meta"] == "META24")
    assert fraude["pilar"] == "Governança" and fraude["peso_oficial"] == 3 and fraude["peso"] == 3


def test_peso_da_fraude_muda_governanca(cliente, com_versao, h_leitor):
    d = simular(cliente, h_leitor, {"META24": 5}).json()
    assert d["simulado"]["Governança"] == pytest.approx(57.39, abs=0.01)
    assert d["simulado"]["geral"] == pytest.approx(66.56, abs=0.01)
    assert d["oficial"]["Governança"] == pytest.approx(62.2, abs=0.05)
    assert next(m for m in d["metas"] if m["id_meta"] == "META24")["peso"] == 5


def test_peso_zero_tira_a_meta(cliente, com_versao, h_leitor):
    d = simular(cliente, h_leitor, {"META24": 0}).json()
    assert d["simulado"]["Governança"] > d["oficial"]["Governança"]


@pytest.mark.parametrize("pesos", [{"META99": 2}, {"META24": 6}, {"META24": -1}, {"META24": 2.5}])
def test_pesos_invalidos_400(cliente, com_versao, h_leitor, pesos):
    r = simular(cliente, h_leitor, pesos)
    assert r.status_code == 400, r.text


def test_pilar_sem_peso_400(cliente, com_versao, h_leitor):
    r = simular(cliente, h_leitor, {i: 0 for i in GOVERNANCA})
    assert r.status_code == 400
    assert "Governança" in r.json()["detail"]


def test_simular_com_filtro_sem_projetos(cliente, com_versao, h_leitor):
    r = simular(cliente, h_leitor, {"META24": 5}, "?municipio=Inexistente")
    assert r.status_code == 200, r.text


def test_leitor_nao_salva(cliente, com_versao, h_leitor):
    r = cliente.post("/api/versoes/pesos", json={"pesos": {"META24": 5}}, headers=h_leitor)
    assert r.status_code == 403


def test_salvar_cria_versao_com_pesos(cliente, com_versao, h_admin, sessao_teste):
    v1 = repositorio.listar_versoes(sessao_teste)[0]
    r = cliente.post("/api/versoes/pesos", json={"pesos": {"META24": 5}}, headers=h_admin)
    assert r.status_code == 201, r.text
    nova = r.json()
    assert nova["numero"] == v1.numero + 1
    assert nova["status"] == "ativa"
    assert nova["nome_arquivo"] == f"pesos ajustados (a partir da versão {v1.numero})"
    assert nova["linhas_por_aba"] == v1.linhas_por_aba
    repositorio.limpar_cache()
    metas = repositorio.carregar_base_ativa(sessao_teste)["dMetas"].set_index("ID Meta")["Peso"]
    original = base_modelo()["dMetas"].set_index("ID Meta")["Peso"]
    assert int(metas["META24"]) == 5
    assert all(int(metas[i]) == int(original[i]) for i in original.index if i != "META24")
    # a tela oficial passa a refletir o peso salvo
    vg = cliente.get("/api/painel/visao-geral", headers=h_admin).json()
    assert vg["indice"]["valor"] == pytest.approx(66.56, abs=0.01)


# --- Revisão final ---------------------------------------------------------------------------------

def test_simular_avalia_as_metas_uma_vez(monkeypatch):
    from app import pesos as modulo
    chamadas = []
    original = modulo.avaliar_metas
    monkeypatch.setattr(modulo, "avaliar_metas", lambda *a, **k: chamadas.append(1) or original(*a, **k))
    d = modulo.simular(base_modelo(), {"META24": 5})
    assert len(chamadas) == 1
    assert d["simulado"]["Governança"] == pytest.approx(57.39, abs=0.01)


def test_pilar_zerado_na_planilha_nao_trava_o_simulador():
    from app.pesos import simular
    b = base_modelo()
    gov = b["dMetas"]["Pilar"] == "Governança"
    b["dMetas"].loc[gov, "Peso"] = 0  # a planilha oficial já veio com o pilar todo em 0
    d = simular(b, {"META01": 3})  # mexer em outro pilar continua funcionando
    assert d["simulado"]["Governança"] is None


# --- Detalhes da revisão (corpo estranho, cache, versão de origem, modelo único) -----------------

@pytest.mark.parametrize("peso", [True, "3", None, 10**20])
def test_corpo_estranho_400(cliente, com_versao, h_leitor, peso):
    assert simular(cliente, h_leitor, {"META24": peso}).status_code == 400


def test_salvar_nao_mexe_na_base_em_cache(cliente, com_versao, h_admin, sessao_teste):
    antes = repositorio.carregar_base_ativa(sessao_teste)["dMetas"].copy(deep=True)
    em_cache = repositorio.carregar_base_ativa(sessao_teste)
    assert cliente.post("/api/versoes/pesos", json={"pesos": {"META24": 5}}, headers=h_admin).status_code == 201
    assert em_cache["dMetas"].equals(antes)


def test_salvar_depois_de_reativar_copia_a_base_nova(cliente, com_versao, h_admin, sessao_teste):
    assert cliente.post("/api/versoes/pesos", json={"pesos": {"META24": 5}}, headers=h_admin).status_code == 201
    v1 = [v for v in repositorio.listar_versoes(sessao_teste) if v.numero == 1][0]
    assert cliente.post(f"/api/versoes/{v1.id}/ativar", headers=h_admin).status_code == 200
    r = cliente.post("/api/versoes/pesos", json={"pesos": {"META01": 1}}, headers=h_admin)
    assert r.status_code == 201 and r.json()["nome_arquivo"] == "pesos ajustados (a partir da versão 1)"
    repositorio.limpar_cache()
    pesos = repositorio.carregar_base_ativa(sessao_teste)["dMetas"].set_index("ID Meta")["Peso"]
    assert int(pesos["META01"]) == 1 and int(pesos["META24"]) == 3  # o 5 da versão 2 não veio junto


def test_salvar_copia_exatamente_a_versao_do_nome(cliente, com_versao, h_admin, monkeypatch):
    # nome e dados vêm da mesma consulta: a rota não pode buscar "a ativa" duas vezes
    def proibido(*a, **k):
        raise AssertionError("carregar_base_ativa faz uma segunda consulta à versão ativa")
    monkeypatch.setattr(repositorio, "carregar_base_ativa", proibido)
    r = cliente.post("/api/versoes/pesos", json={"pesos": {"META24": 5}}, headers=h_admin)
    assert r.status_code == 201, r.text


def test_um_modelo_de_pedido_so():
    from app import pesos
    from app.api import painel, versoes
    assert painel.PedidoPesos is pesos.PedidoPesos and versoes.PedidoPesos is pesos.PedidoPesos
