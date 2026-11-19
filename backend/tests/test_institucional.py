"""Aba opcional dInstitucional: indicadores ASG da própria Investe Piauí (sede)."""
from app.calculos.filtros import Filtros, aplicar_filtros
from app.calculos.institucional import avaliar_institucional
from app.planilha.validacao import validar_estrutura
from tests.apoio import base_modelo


def _item(itens, ident):
    return next(i for i in itens if i.id == ident)


def test_modelo_tem_15_indicadores():
    itens = avaliar_institucional(base_modelo())
    assert len(itens) == 15
    assert [i.id for i in itens] == sorted(i.id for i in itens)


def test_farol_menor_melhor():
    i = _item(avaliar_institucional(base_modelo()), "INS01")
    assert i.valor == 162
    assert i.anterior == 184
    assert i.ano == 2026
    assert i.status == "amarelo"
    assert i.formato == "num"
    assert i.demonstracao is True


def test_farol_maior_melhor():
    itens = avaliar_institucional(base_modelo())
    ins07 = _item(itens, "INS07")
    assert ins07.status == "amarelo"
    assert ins07.formato == "pct"
    assert _item(itens, "INS13").status == "verde"


def test_sem_aba():
    b = base_modelo()
    del b["dInstitucional"]
    assert avaliar_institucional(b) == []


def test_anterior_vazio():
    b = base_modelo()
    d = b["dInstitucional"]
    d.loc[d["ID Institucional"] == "INS01", "Valor Anterior"] = None
    assert _item(avaliar_institucional(b), "INS01").anterior is None


def test_sem_meta():
    b = base_modelo()
    d = b["dInstitucional"]
    d.loc[d["ID Institucional"] == "INS01", "Meta"] = None
    assert _item(avaliar_institucional(b), "INS01").status is None


def test_planilha_sem_aba_e_aceita():
    b = base_modelo()
    del b["dInstitucional"]
    assert [e for e in validar_estrutura(b) if e.aba == "dInstitucional"] == []
    assert validar_estrutura(b) == validar_estrutura(base_modelo())


def test_filtro_nao_altera():
    b = aplicar_filtros(base_modelo(), Filtros(municipios=["Inexistente"]))
    assert len(b["dInstitucional"]) == 15
