"""Gravação transacional de versões (spec §7)."""
import pytest
from sqlalchemy import func, select

from app import repositorio
from app.calculos.medidas import calcular
from app.models import LinhaDado, Versao
from tests.apoio import base_modelo


@pytest.fixture(autouse=True)
def limpar_cache():
    repositorio.limpar_cache()
    yield
    repositorio.limpar_cache()


def ativas(s) -> list[int]:
    return [v.numero for v in s.scalars(select(Versao).where(Versao.status == "ativa"))]


def test_salvar_e_carregar(sessao_teste):
    base = base_modelo()
    v = repositorio.salvar_versao(sessao_teste, base, None, "base.xlsx", [])
    assert v.numero == 1 and v.status == "ativa"
    assert v.linhas_por_aba["dProjeto"] == 48

    repositorio.limpar_cache()
    carregada = repositorio.carregar_base_ativa(sessao_teste)
    assert set(carregada) == set(base)
    for aba in base:
        assert len(carregada[aba]) == len(base[aba]), aba
    for nome in ["Investimento Previsto", "Orçamento Previsto", "% Licença Válida", "Taxa Frequência Acidentes"]:
        assert calcular(carregada, nome) == pytest.approx(calcular(base, nome))
    assert str(carregada["fFinanceiro"]["Data Referência"].dtype).startswith("datetime64")


def test_sem_versao(sessao_teste):
    assert repositorio.carregar_base_ativa(sessao_teste) is None


def test_nova_versao_desativa_anterior(sessao_teste):
    repositorio.salvar_versao(sessao_teste, base_modelo(), None, "a.xlsx", [])
    repositorio.salvar_versao(sessao_teste, base_modelo(), None, "b.xlsx", [])
    assert ativas(sessao_teste) == [2]
    assert [v.numero for v in repositorio.listar_versoes(sessao_teste)] == [2, 1]


def test_ativar_versao_anterior(sessao_teste):
    v1 = repositorio.salvar_versao(sessao_teste, base_modelo(), None, "a.xlsx", [])
    b2 = base_modelo()
    b2["dProjeto"] = b2["dProjeto"].iloc[:10]
    repositorio.salvar_versao(sessao_teste, b2, None, "b.xlsx", [])
    assert len(repositorio.carregar_base_ativa(sessao_teste)["dProjeto"]) == 10

    repositorio.ativar_versao(sessao_teste, v1.id)
    assert ativas(sessao_teste) == [1]
    assert len(repositorio.carregar_base_ativa(sessao_teste)["dProjeto"]) == 48


def test_ativar_rejeitada_falha(sessao_teste):
    rej = repositorio.registrar_rejeicao(sessao_teste, "ruim.xlsx", None, [{"mensagem": "x"}])
    with pytest.raises(ValueError):
        repositorio.ativar_versao(sessao_teste, rej.id)


def test_falha_no_meio_nao_grava(sessao_teste, monkeypatch):
    repositorio.salvar_versao(sessao_teste, base_modelo(), None, "a.xlsx", [])
    linhas_antes = sessao_teste.scalar(select(func.count()).select_from(LinhaDado))

    original = repositorio._serializar_linha
    chamadas = {"n": 0}

    def quebrar(linha):
        chamadas["n"] += 1
        if chamadas["n"] > 500:
            raise RuntimeError("falha simulada")
        return original(linha)

    monkeypatch.setattr(repositorio, "_serializar_linha", quebrar)
    with pytest.raises(RuntimeError):
        repositorio.salvar_versao(sessao_teste, base_modelo(), None, "b.xlsx", [])

    assert [v.numero for v in repositorio.listar_versoes(sessao_teste)] == [1]
    assert ativas(sessao_teste) == [1]
    assert sessao_teste.scalar(select(func.count()).select_from(LinhaDado)) == linhas_antes


def test_rejeicao_nao_muda_ativa(sessao_teste):
    repositorio.salvar_versao(sessao_teste, base_modelo(), None, "a.xlsx", [])
    rej = repositorio.registrar_rejeicao(sessao_teste, "ruim.xlsx", None, [{"mensagem": "Aba ausente"}])
    assert rej.status == "rejeitada"
    assert rej.erros == [{"mensagem": "Aba ausente"}]
    assert ativas(sessao_teste) == [1]
    assert len(repositorio.carregar_base_ativa(sessao_teste)["dProjeto"]) == 48
