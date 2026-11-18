"""Checagens de qualidade C01–C12 (medida DAX `Problemas Checagem`)."""
import pandas as pd
import pytest

from app.calculos.checagens import rodar_checagens
from tests.apoio import base_modelo


def problemas(base) -> dict[str, int]:
    return {r.id: r.problemas for r in rodar_checagens(base)}


def test_base_sem_problemas():
    res = rodar_checagens(base_modelo())
    assert [r.id for r in res] == [f"C{i:02d}" for i in range(1, 13)]
    assert all(r.problemas == 0 for r in res)
    assert res[0].checagem == "Projetos sem empresa cadastrada"


def test_c01_projeto_sem_empresa():
    b = base_modelo()
    b["dProjeto"].loc[0, "Código Empresa"] = "EMP999"
    assert problemas(b)["C01"] == 1


def test_c02_codigo_repetido():
    b = base_modelo()
    b["dProjeto"] = pd.concat([b["dProjeto"], b["dProjeto"].iloc[[0]]], ignore_index=True)
    assert problemas(b)["C02"] == 1


@pytest.mark.parametrize("aba,cid", [("fAmbiental", "C03"), ("fSocial", "C04"), ("fTransparencia", "C06")])
def test_projeto_sem_linha(aba, cid):
    b = base_modelo()
    b[aba] = b[aba].iloc[1:]
    assert problemas(b)[cid] == 1


def test_c05_sem_financeiro():
    b = base_modelo()
    f = b["fFinanceiro"]
    b["fFinanceiro"] = f[f["Código Projeto"] != "PROJ001"]
    assert problemas(b)["C05"] == 1


def test_c07_realizado_maior_que_previsto():
    b = base_modelo()
    p = b["dProjeto"]
    p.loc[0, "Investimento Realizado"] = p.loc[0, "Investimento Previsto"] + 1
    assert problemas(b)["C07"] == 1


def test_c08_subgrupo_maior_que_total():
    b = base_modelo()
    s = b["fSocial"]
    s.loc[0, "Empregos Mulheres"] = s.loc[0, "Empregos Diretos Gerados"] + 1
    s.loc[1, "Empregos PCD"] = s.loc[1, "Empregos Diretos Gerados"] + 1
    assert problemas(b)["C08"] == 2


def test_c09_pago_maior_que_empenhado():
    b = base_modelo()
    f = b["fFinanceiro"]
    f.loc[0, "Valor Pago"] = f.loc[0, "Valor Empenhado"] + 1
    assert problemas(b)["C09"] == 1


def test_c10_campo_obrigatorio_vazio():
    b = base_modelo()
    b["dProjeto"].loc[0, "Município"] = None
    b["dProjeto"].loc[1, "Custo Manutenção Anual"] = float("nan")
    assert problemas(b)["C10"] == 2


def test_c11_percentual_fora_da_faixa():
    b = base_modelo()
    b["fHidrogenio"].loc[0, "% Renovável Eletrolisador"] = 1.2
    assert problemas(b)["C11"] == 1


def test_c12_fim_antes_do_inicio():
    b = base_modelo()
    c = b["fContratos"]
    c.loc[0, "Data Fim"] = c.loc[0, "Data Início"] - pd.Timedelta(days=1)
    assert problemas(b)["C12"] == 1


def ocorrencias(base, cid):
    return next(r for r in rodar_checagens(base) if r.id == cid).ocorrencias


def test_c01_ocorrencia():
    b = base_modelo()
    b["dProjeto"].loc[0, "Código Empresa"] = "EMP999"
    [o] = ocorrencias(b, "C01")
    assert (o.aba, o.linha, o.identificador) == ("dProjeto", 2, "PROJ001")
    assert o.detalhe == "Código Empresa EMP999 não existe em dEmpresa"


def test_c07_ocorrencia():
    b = base_modelo()
    b["dProjeto"].loc[0, "Investimento Realizado"] = 10 * b["dProjeto"].loc[0, "Investimento Previsto"]
    [o] = ocorrencias(b, "C07")
    assert (o.aba, o.linha, o.identificador) == ("dProjeto", 2, "PROJ001")
    assert o.detalhe == "Investimento Realizado R$ 7,8 bi > Investimento Previsto R$ 780 mi"


def test_c12_ocorrencia():
    b = base_modelo()
    b["fContratos"].loc[0, "Data Fim"] = pd.Timestamp("2025-12-01")
    [o] = ocorrencias(b, "C12")
    assert (o.aba, o.identificador) == ("fContratos", "LIC001")
    assert o.detalhe == "Data Início 12/01/2026 > Data Fim 01/12/2025"


def test_c02_lista_so_as_repeticoes():
    b = base_modelo()
    b["dProjeto"] = pd.concat([b["dProjeto"], b["dProjeto"].iloc[[0]]], ignore_index=True)
    [o] = ocorrencias(b, "C02")
    assert o.identificador == "PROJ001" and o.detalhe == "Código repetido; primeira ocorrência na linha 2"


def test_c02_codigos_vazios_contam_como_repeticao():
    b = base_modelo()
    b["dProjeto"].loc[[0, 1], "Código Projeto"] = None
    p = b["dProjeto"]
    c02 = next(r for r in rodar_checagens(b) if r.id == "C02")
    assert c02.problemas == len(c02.ocorrencias) == len(p) - p["Código Projeto"].nunique()
    assert c02.problemas >= 2
    assert {o.detalhe for o in c02.ocorrencias} >= {"Código Projeto vazio"}


def test_c03_ocorrencia():
    b = base_modelo()
    b["fAmbiental"] = b["fAmbiental"].iloc[1:]
    [o] = ocorrencias(b, "C03")
    assert o.identificador == "PROJ001" and o.detalhe.endswith(" sem linha em fAmbiental")


def test_c08_ocorrencia():
    b = base_modelo()
    b["fSocial"].loc[0, "Empregos Mulheres"] = 600
    [o] = ocorrencias(b, "C08")
    assert (o.aba, o.linha) == ("fSocial", 2)
    assert o.detalhe == "Empregos Mulheres 600 > Empregos Diretos Gerados 520"


def test_c09_ocorrencia():
    b = base_modelo()
    b["fFinanceiro"].loc[0, "Valor Pago"] = 63_400_000
    [o] = ocorrencias(b, "C09")
    assert o.identificador == "FIN001-01"
    assert o.detalhe == "01/01/2026: Empenhado R$ 31,7 mi · Liquidado R$ 29,1 mi · Pago R$ 63,4 mi"


def test_c10_lista_os_campos_vazios():
    b = base_modelo()
    b["dProjeto"].loc[0, ["Município", "Custo Manutenção Anual"]] = None
    [o] = ocorrencias(b, "C10")
    assert o.detalhe == "Vazios: Município, Custo Manutenção Anual"


def test_c11_ocorrencia():
    b = base_modelo()
    b["fHidrogenio"].loc[0, "% Renovável Eletrolisador"] = 1.2
    [o] = ocorrencias(b, "C11")
    assert o.detalhe == "% Renovável Eletrolisador 120,0%"


def test_versao_antiga_sem_linha():
    b = base_modelo()
    b["dProjeto"] = b["dProjeto"].drop(columns="_linha_planilha")
    b["dProjeto"].loc[0, "Município"] = None
    [o] = ocorrencias(b, "C10")
    assert o.linha is None


def _m01(b): b["dProjeto"].loc[0, "Código Empresa"] = "EMP999"
def _m02(b): b["dProjeto"] = pd.concat([b["dProjeto"], b["dProjeto"].iloc[[0]]], ignore_index=True)
def _m03(b): b["fAmbiental"] = b["fAmbiental"].iloc[1:]
def _m04(b): b["fSocial"] = b["fSocial"].iloc[1:]
def _m05(b): b["fFinanceiro"] = b["fFinanceiro"][b["fFinanceiro"]["Código Projeto"] != "PROJ001"]
def _m06(b): b["fTransparencia"] = b["fTransparencia"].iloc[1:]
def _m07(b): b["dProjeto"].loc[0, "Investimento Realizado"] = b["dProjeto"].loc[0, "Investimento Previsto"] + 1
def _m08(b): b["fSocial"].loc[0, "Empregos Mulheres"] = b["fSocial"].loc[0, "Empregos Diretos Gerados"] + 1
def _m09(b): b["fFinanceiro"].loc[0, "Valor Pago"] = b["fFinanceiro"].loc[0, "Valor Empenhado"] + 1
def _m10(b): b["dProjeto"].loc[0, "Município"] = None
def _m11(b): b["fHidrogenio"].loc[0, "% Renovável Eletrolisador"] = 1.2
def _m12(b): b["fContratos"].loc[0, "Data Fim"] = b["fContratos"].loc[0, "Data Início"] - pd.Timedelta(days=1)


MUTACOES = [_m01, _m02, _m03, _m04, _m05, _m06, _m07, _m08, _m09, _m10, _m11, _m12]


@pytest.mark.parametrize("mutacao", MUTACOES)
def test_contagem_igual_a_lista(mutacao):
    b = base_modelo()
    mutacao(b)
    res = rodar_checagens(b)
    assert any(r.problemas for r in res)
    assert all(r.problemas == len(r.ocorrencias) for r in res)


def test_com_ocorrencias_corta_em_50():
    b = base_modelo()
    b["fFinanceiro"]["Valor Pago"] = 2 * b["fFinanceiro"]["Valor Empenhado"]
    c09 = next(r for r in rodar_checagens(b) if r.id == "C09")
    cortado = c09.com_ocorrencias()
    assert cortado["problemas"] == 432 and len(cortado["ocorrencias"]) == 50 and cortado["mais"] == 382
    assert len(c09.com_ocorrencias(None)["ocorrencias"]) == 432
    assert set(c09.dict()) == {"id", "checagem", "tabela", "regra", "problemas"}
