"""Exportar qualquer tela do painel para Excel (plano exportar-indicadores-qualidade, Tarefa 14)."""
from io import BytesIO

import pytest
from openpyxl import load_workbook

from app import repositorio
from tests.apoio import base_modelo


@pytest.fixture
def com_versao(sessao_teste, usuarios):
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, base_modelo(), usuarios["admin"].id, "base.xlsx", [])
    yield
    repositorio.limpar_cache()


def baixar(cliente, h, caminho, query=""):
    r = cliente.get(f"/api/painel/exportar/{caminho}{query}", headers=h)
    assert r.status_code == 200, r.text
    assert "attachment" in r.headers["content-disposition"]
    return load_workbook(BytesIO(r.content))


def test_visao_geral_bate_com_a_tela(cliente, com_versao, h_leitor):
    tela = cliente.get("/api/painel/visao-geral", headers=h_leitor).json()
    wb = baixar(cliente, h_leitor, "visao-geral")
    assert wb.sheetnames[:3] == ["Contexto", "Indicadores", "Gráficos"]
    linhas = {r[0]: r[1] for r in wb["Indicadores"].iter_rows(min_row=2, values_only=True)}
    assert linhas["Índice ASG Geral"] == pytest.approx(tela["indice"]["valor"])
    assert linhas["Investimento previsto"] == pytest.approx(42.83e9, rel=1e-3)
    assert linhas["Projetos"] == 48


def test_filtros_vao_para_o_contexto(cliente, com_versao, h_leitor):
    wb = baixar(cliente, h_leitor, "setor/mineracao", "?setor=Mineração")
    ctx = {r[0]: r[1] for r in wb["Contexto"].iter_rows(values_only=True)}
    assert ctx["Setor"] == "Mineração"
    assert ctx["Município"] == "Todos"
    assert ctx["Versão dos dados"].startswith("nº 1")
    # o título "Conformidade ambiental dos projetos minerários" passa do limite de 31 caracteres do Excel
    assert "Conformidade ambiental dos proj" in wb.sheetnames


def test_tabela_vira_aba_com_todas_as_linhas(cliente, com_versao, h_leitor):
    wb = baixar(cliente, h_leitor, "tema/licenca-social")
    aba = [n for n in wb.sheetnames if n.startswith("Projetos sem consulta")][0]
    assert wb[aba].max_row == 1 + 18


def test_nomes_de_aba_validos_e_unicos(cliente, com_versao, h_leitor):
    for caminho in ["ambiental", "social", "governanca", "metas", "setor/sustentabilidade", "tema/riscos-climaticos"]:
        wb = baixar(cliente, h_leitor, caminho)
        assert len(set(wb.sheetnames)) == len(wb.sheetnames)
        assert all(len(n) <= 31 and not set(n) & set("[]:*?/\\") for n in wb.sheetnames)


def test_filtro_sem_projetos_ainda_gera_arquivo(cliente, com_versao, h_leitor):
    tela = cliente.get("/api/painel/tema/licenca-social?municipio=Inexistente", headers=h_leitor).json()
    wb = baixar(cliente, h_leitor, "tema/licenca-social", "?municipio=Inexistente")
    assert wb.sheetnames[:3] == ["Contexto", "Indicadores", "Gráficos"]
    ctx = {r[0]: r[1] for r in wb["Contexto"].iter_rows(values_only=True)}
    assert ctx["Município"] == "Inexistente"
    # cada tabela vira uma aba com as mesmas linhas da tela; a de projetos fica só com o cabeçalho
    # (a de metas continua cheia: dMetas não é filtrada)
    abas = wb.sheetnames[3:]
    assert len(abas) == len(tela["tabelas"])
    for aba, t in zip(abas, tela["tabelas"]):
        assert wb[aba].max_row == 1 + len(t["linhas"]) and wb[aba]["A1"].value
    assert any(len(t["linhas"]) == 0 for t in tela["tabelas"])


def test_nome_do_arquivo_tem_a_data_do_piaui(cliente, com_versao, h_leitor):
    from datetime import datetime

    from app.paginas.comum import FUSO

    r = cliente.get("/api/painel/exportar/setor/mineracao", headers=h_leitor)
    hoje = datetime.now(FUSO).date().isoformat()
    assert f'filename="ASG_setor_mineracao_{hoje}.xlsx"' in r.headers["content-disposition"]


def test_exportar_pagina_inexistente(cliente, com_versao, h_leitor):
    assert cliente.get("/api/painel/exportar/xyz", headers=h_leitor).status_code == 404


def test_exportar_exige_login(cliente, com_versao):
    assert cliente.get("/api/painel/exportar/visao-geral").status_code == 401
