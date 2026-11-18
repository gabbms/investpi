"""Qualidade dos dados (plano exportar-indicadores-qualidade, Tarefa 16)."""
from io import BytesIO

import pytest
from openpyxl import load_workbook

from app import repositorio
from app.planilha.esquema import ABAS
from tests.apoio import base_modelo


@pytest.fixture
def com_versao(sessao_teste, usuarios):
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, base_modelo(), usuarios["admin"].id, "base.xlsx", [])
    yield
    repositorio.limpar_cache()


def test_qualidade_base_limpa(cliente, com_versao, h_leitor):
    p = cliente.get("/api/painel/qualidade", headers=h_leitor).json()
    c = {x["id"]: x for x in p["cards"]}
    assert c["Checagens sem problema"]["valor"] == 12
    assert c["Problemas encontrados"]["valor"] == 0
    assert c["Problemas encontrados"]["status"] == "verde"
    assert p["subtitulo"].startswith("Versão nº 1")
    assert [l["id"] for l in p["tabelas"][0]["linhas"]] == [f"C{i:02d}" for i in range(1, 13)]
    assert len(p["tabelas"][1]["linhas"]) >= 17   # ABAS tem 17 abas obrigatórias
    assert {l["situacao"] for l in p["tabelas"][0]["linhas"]} == {"OK"}


def test_qualidade_aponta_problema(cliente, sessao_teste, usuarios, h_leitor):
    b = base_modelo()
    b["dProjeto"].loc[0, "Investimento Realizado"] = 10 * b["dProjeto"].loc[0, "Investimento Previsto"]  # C07
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, b, usuarios["admin"].id, "x.xlsx", [])
    p = cliente.get("/api/painel/qualidade", headers=h_leitor).json()
    c07 = next(l for l in p["tabelas"][0]["linhas"] if l["id"] == "C07")
    assert c07["problemas"] == 1 and c07["situacao"] == "Verificar"
    assert {x["id"]: x for x in p["cards"]}["Problemas encontrados"]["status"] == "amarelo"
    repositorio.limpar_cache()


def test_qualidade_ignora_filtros(cliente, com_versao, h_leitor):
    a = cliente.get("/api/painel/qualidade", headers=h_leitor).json()
    b = cliente.get("/api/painel/qualidade?setor=Mineração", headers=h_leitor).json()
    assert a["cards"] == b["cards"]


def test_qualidade_exige_login(cliente, com_versao):
    assert cliente.get("/api/painel/qualidade").status_code == 401


def test_abas_na_ordem_do_esquema(cliente, sessao_teste, com_versao, h_leitor):
    sessao_teste.expire_all()  # relê linhas_por_aba do JSONB, que não guarda a ordem das chaves
    p = cliente.get("/api/painel/qualidade", headers=h_leitor).json()
    assert [l["aba"] for l in p["tabelas"][1]["linhas"]] == list(ABAS)


def test_exportar_qualidade_ignora_filtros(cliente, com_versao, h_leitor):
    r = cliente.get("/api/painel/exportar/qualidade?setor=Mineração", headers=h_leitor)
    assert r.status_code == 200
    wb = load_workbook(BytesIO(r.content))
    ctx = {l[0]: l[1] for l in wb["Contexto"].iter_rows(values_only=True)}
    assert ctx["Setor"] == "Todos"          # a página não usa os filtros, e o arquivo diz isso
    assert "Checagens de qualidade (C01–C" in " ".join(wb.sheetnames)


def test_qualidade_mostra_ocorrencias(cliente, sessao_teste, usuarios, h_leitor):
    b = base_modelo()
    b["fFinanceiro"]["Valor Pago"] = 2 * b["fFinanceiro"]["Valor Empenhado"]   # C09 em todas as 432 linhas
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, b, usuarios["admin"].id, "x.xlsx", [])
    t = cliente.get("/api/painel/qualidade", headers=h_leitor).json()["tabelas"][0]
    assert t["expansivel"] is True
    c09 = next(l for l in t["linhas"] if l["id"] == "C09")
    assert len(c09["ocorrencias"]) == 50 and c09["mais"] == 382
    assert c09["ocorrencias"][0]["identificador"] == "FIN001-01"
    r = cliente.get("/api/painel/exportar/qualidade", headers=h_leitor)
    wb = load_workbook(BytesIO(r.content))
    assert "Problemas" in wb.sheetnames and wb["Problemas"].max_row == 1 + 432
    repositorio.limpar_cache()
