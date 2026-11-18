"""Índice de conteúdo GRI exportável (plano indice-gri, Tarefa 20)."""
from datetime import date, datetime
from io import BytesIO

import pytest
from openpyxl import load_workbook

from app import repositorio
from app.calculos.filtros import Filtros, aplicar_filtros
from app.gri import montar_indice_gri, normalizar_referencia
from app.paginas.comum import FUSO
from tests.apoio import base_modelo

HOJE = date(2026, 11, 18)


@pytest.fixture
def com_versao(sessao_teste, usuarios):
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, base_modelo(), usuarios["admin"].id, "base.xlsx", [])
    yield
    repositorio.limpar_cache()


def todas_linhas(ind):
    return [(n.titulo, d.titulo, l.indicador, l.valor) for n in ind.normas for d in n.divulgacoes for l in d.linhas]


def test_normalizar_referencia():
    assert normalizar_referencia(" gri  403-9 ") == "GRI 403-9"


def test_indice_na_base_atual():
    ind = montar_indice_gri(base_modelo(), HOJE)
    linhas = todas_linhas(ind)
    assert len(linhas) == 65 and sum(len(n.divulgacoes) for n in ind.normas) == 30
    assert linhas[0][:3] == ("GRI 2: Conteúdos Gerais 2021", "2-5 Verificação externa",
                             "IND69 Número de auditorias realizadas")
    n403 = next(n for n in ind.normas if n.titulo == "GRI 403: Saúde e Segurança do Trabalho 2018")
    assert [d.titulo for d in n403.divulgacoes] == [
        "403-5 Capacitação de trabalhadores em saúde e segurança do trabalho", "403-9 Acidentes de trabalho"]
    assert [(l.indicador, l.valor) for l in n403.divulgacoes[1].linhas] == [
        ("IND54 Número de acidentes de trabalho", "23"), ("IND55 Taxa de frequência de acidentes", "2,12")]


def test_referencias_a_revisar():
    rev = {r.indicador.split()[0]: r for r in montar_indice_gri(base_modelo(), HOJE).revisar}
    assert list(rev) == ["IND03", "IND04", "IND13", "IND14", "IND17", "IND32", "IND33", "IND34"]
    assert rev["IND03"].motivo == "Divulgação do modelo GRI-G4, anterior às Normas GRI" and rev["IND03"].valor == "1.905"
    assert rev["IND13"].motivo == "Norma setorial sem divulgação específica"
    assert rev["IND17"].motivo == "Norma substituída por GRI 101: Biodiversity 2024 em 01/01/2026"


def test_302_sai_do_indice_em_2027():
    ind = montar_indice_gri(base_modelo(), date(2027, 1, 1))
    assert len(todas_linhas(ind)) == 62
    rev = {r.indicador.split()[0]: r.motivo for r in ind.revisar}
    assert rev["IND06"] == rev["IND10"] == rev["IND11"] == "Norma substituída por GRI 103: Energy 2025 em 01/01/2027"


def test_referencia_desconhecida_e_espacos():
    b = base_modelo()
    b["dIndicador"].loc[0, "Referência GRI"] = "GRI 999-9"      # IND01
    b["dIndicador"].loc[1, "Referência GRI"] = " gri  403-9 "   # IND02
    ind = montar_indice_gri(b, HOJE)
    assert {r.indicador.split()[0]: r.motivo for r in ind.revisar}["IND01"] == "Divulgação não reconhecida"
    assert any(l[2].startswith("IND02") and l[1] == "403-9 Acidentes de trabalho" for l in todas_linhas(ind))


def test_valores_respeitam_o_filtro():
    b = aplicar_filtros(base_modelo(), Filtros(setores=["Mineração"]))
    ind = montar_indice_gri(b, HOJE)
    assert next(l for l in todas_linhas(ind) if l[2].startswith("IND01"))[3] == "R$ 0"


def test_exportar_gri(cliente, com_versao, h_leitor):
    r = cliente.get("/api/painel/exportar-gri?setor=Mineração", headers=h_leitor)
    assert r.status_code == 200, r.text
    hoje = datetime.now(FUSO).date().isoformat()
    assert f'filename="ASG_indice_gri_{hoje}.xlsx"' in r.headers["content-disposition"]
    wb = load_workbook(BytesIO(r.content))
    assert wb.sheetnames == ["Índice GRI", "Contexto"]
    ws = wb["Índice GRI"]
    assert ws["A1"].value == "Índice de conteúdo GRI — indicadores quantitativos"
    assert ws["A2"].value.startswith("Versão nº 1 · base.xlsx · filtros: Setor: Mineração")
    assert [c.value for c in ws[4]] == ["Norma GRI", "Divulgação", "Indicador", "Valor", "Localização no relatório"]
    textos = [str(c.value) for row in ws.iter_rows() for c in row if c.value]
    assert "Referências a revisar" in textos
    assert not any("de acordo com" in t.lower() for t in textos)


def test_exportar_gri_sem_filtro_e_sem_login(cliente, com_versao, h_leitor):
    wb = load_workbook(BytesIO(cliente.get("/api/painel/exportar-gri", headers=h_leitor).content))
    assert wb["Índice GRI"]["A2"].value.endswith("filtros: carteira inteira")
    assert cliente.get("/api/painel/exportar-gri").status_code == 401


def test_exportar_gri_com_filtro_sem_projetos(cliente, com_versao, h_leitor):
    r = cliente.get("/api/painel/exportar-gri?municipio=Inexistente", headers=h_leitor)
    assert r.status_code == 200
    ws = load_workbook(BytesIO(r.content))["Índice GRI"]
    assert ws["A2"].value.endswith("filtros: Município: Inexistente")
    valores = {row[2]: row[3] for row in ws.iter_rows(min_row=5, values_only=True) if row[2]}
    assert valores["IND01 Investimento em energias renováveis"] == "R$ 0"
