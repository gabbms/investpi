"""API: envio, versões, modelo, opções e Visão Geral (spec §7, §8, §10)."""
import pytest

from app import repositorio
from tests.apoio import base_modelo, bytes_modelo, mutar

XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@pytest.fixture
def com_versao(sessao_teste, usuarios):
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, base_modelo(), usuarios["admin"].id, "base_modelo.xlsx", [])
    yield
    repositorio.limpar_cache()


def arquivo(conteudo: bytes, nome: str = "base.xlsx"):
    return {"arquivo": (nome, conteudo, XLSX)}


def cards(pagina: dict) -> dict:
    return {c["id"]: c for c in pagina["cards"]}


def test_sem_token(cliente, com_versao):
    assert cliente.get("/api/painel/visao-geral").status_code == 401
    assert cliente.get("/api/versoes").status_code == 401


def test_leitor_nao_envia(cliente, com_versao, h_leitor):
    assert cliente.post("/api/importacao/previa", files=arquivo(bytes_modelo()), headers=h_leitor).status_code == 403
    assert cliente.post("/api/importacao/confirmar", files=arquivo(bytes_modelo()), headers=h_leitor).status_code == 403
    assert cliente.post("/api/versoes/1/ativar", headers=h_leitor).status_code == 403
    assert cliente.get("/api/versoes", headers=h_leitor).status_code == 403


def test_previa_base_valida(cliente, com_versao, h_admin):
    r = cliente.post("/api/importacao/previa", files=arquivo(bytes_modelo()), headers=h_admin)
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["pode_confirmar"] is True
    assert corpo["erros"] == []
    assert corpo["linhas_por_aba"]["dProjeto"] == 48
    assert len(corpo["checagens"]) == 12
    assert all(c["problemas"] == 0 for c in corpo["checagens"])


def test_previa_com_erro(cliente, com_versao, h_admin):
    conteudo = mutar(lambda wb: wb.remove(wb["fSocial"]))
    corpo = cliente.post("/api/importacao/previa", files=arquivo(conteudo), headers=h_admin).json()
    assert corpo["pode_confirmar"] is False
    assert corpo["erros"][0]["aba"] == "fSocial"


def test_confirmar_cria_versao(cliente, com_versao, h_admin):
    r = cliente.post("/api/importacao/confirmar", files=arquivo(bytes_modelo(), "nova.xlsx"), headers=h_admin)
    assert r.status_code == 201, r.text
    assert r.json()["versao"]["numero"] == 2
    versoes = cliente.get("/api/versoes", headers=h_admin).json()
    assert versoes[0]["numero"] == 2 and versoes[0]["status"] == "ativa"
    assert versoes[0]["nome_arquivo"] == "nova.xlsx"
    assert versoes[0]["enviado_por"] == "Admin Teste"
    assert versoes[1]["status"] == "inativa"


def test_confirmar_com_erro_nao_muda_ativa(cliente, com_versao, h_admin):
    conteudo = mutar(lambda wb: wb.remove(wb["fSocial"]))
    r = cliente.post("/api/importacao/confirmar", files=arquivo(conteudo), headers=h_admin)
    assert r.status_code == 422
    assert r.json()["detail"]["erros"][0]["aba"] == "fSocial"
    versoes = cliente.get("/api/versoes", headers=h_admin).json()
    ativa = [v for v in versoes if v["status"] == "ativa"]
    assert [v["numero"] for v in ativa] == [1]
    assert versoes[0]["status"] == "rejeitada"


def test_arquivo_invalido(cliente, com_versao, h_admin):
    for rota in ("previa", "confirmar"):
        r = cliente.post(f"/api/importacao/{rota}", files=arquivo(b"x", "a.xlsx"), headers=h_admin)
        assert r.status_code == 400
        assert r.json() == {"detail": "Arquivo não é uma planilha .xlsx válida"}
    corpo = cliente.get("/api/painel/visao-geral", headers=h_admin).json()
    assert cards(corpo)["Qtd Projetos"]["valor"] == 48


def test_ativar_versao(cliente, com_versao, h_admin):
    cliente.post("/api/importacao/confirmar", files=arquivo(bytes_modelo()), headers=h_admin)
    versoes = cliente.get("/api/versoes", headers=h_admin).json()
    v1 = next(v for v in versoes if v["numero"] == 1)
    r = cliente.post(f"/api/versoes/{v1['id']}/ativar", headers=h_admin)
    assert r.status_code == 200
    assert r.json()["status"] == "ativa"
    assert cliente.post("/api/versoes/9999/ativar", headers=h_admin).status_code == 404


def test_modelo(cliente, com_versao, h_leitor):
    r = cliente.get("/api/importacao/modelo", headers=h_leitor)
    assert r.status_code == 200
    assert r.content == bytes_modelo()
    assert "attachment" in r.headers["content-disposition"]


def test_opcoes(cliente, com_versao, h_leitor):
    corpo = cliente.get("/api/painel/opcoes", headers=h_leitor).json()
    assert corpo["setores"] == ["Energia Renovável", "Hidrogênio Verde", "Mineração", "Sustentabilidade Ambiental"]
    assert len(corpo["vps"]) == 3
    assert "Concluído" in corpo["status"]
    assert "Luís Correia" in corpo["municipios"]


def test_painel_sem_versao(cliente, usuarios, h_leitor):
    repositorio.limpar_cache()
    r = cliente.get("/api/painel/visao-geral", headers=h_leitor)
    assert r.status_code == 409
    assert r.json() == {"detail": "Nenhuma versão de dados carregada"}


def test_visao_geral_valores(cliente, com_versao, h_leitor):
    pagina = cliente.get("/api/painel/visao-geral", headers=h_leitor).json()
    c = cards(pagina)
    assert c["Investimento Previsto"]["valor"] == pytest.approx(42_829_000_000)
    assert c["Investimento Previsto"]["formato"] == "brl"
    assert c["Qtd Projetos"]["valor"] == 48
    assert c["Empresas Confirmadas"]["valor"] == 17
    assert c["Empregos Diretos Gerados"]["valor"] == 7236
    assert c["Emissões Evitadas tCO2e"]["valor"] == pytest.approx(3_477_889, abs=1)
    assert c["Investimento Previsto"]["ajuda"]
    indice = pagina["indice"]
    assert indice["id"] == "Índice ASG Geral"
    assert round(indice["valor"]) == 68
    assert indice["status"] == "amarelo"
    graficos = {g["id"]: g for g in pagina["graficos"]}
    assert set(graficos) == {"investimento_setor", "investimento_municipio", "indice_pilar_setor", "projetos_status"}
    setor = graficos["investimento_setor"]
    assert sum(setor["series"][0]["valores"]) == pytest.approx(42_829_000_000)
    assert sum(graficos["projetos_status"]["series"][0]["valores"]) == 48
    mun = graficos["investimento_municipio"]
    totais = [sum(v or 0 for v in vals) for vals in zip(*[s["valores"] for s in mun["series"]])]
    assert totais == sorted(totais, reverse=True)


def test_visao_geral_filtro_mineracao(cliente, com_versao, h_leitor):
    pagina = cliente.get("/api/painel/visao-geral?setor=Mineração", headers=h_leitor).json()
    assert cards(pagina)["Qtd Projetos"]["valor"] == 12


def test_visao_geral_filtros_repetidos(cliente, com_versao, h_leitor):
    url = "/api/painel/visao-geral?setor=Mineração&setor=Hidrogênio Verde"
    assert cards(cliente.get(url, headers=h_leitor).json())["Qtd Projetos"]["valor"] == 24


def test_visao_geral_filtro_sem_projetos(cliente, com_versao, h_leitor):
    r = cliente.get("/api/painel/visao-geral?municipio=Inexistente", headers=h_leitor)
    assert r.status_code == 200
    pagina = r.json()
    assert cards(pagina)["Qtd Projetos"]["valor"] == 0
    assert pagina["indice"]["valor"] is None
