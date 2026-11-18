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
