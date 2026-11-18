"""Leitura e validação estrutural da planilha (spec §6 e §7)."""
import pytest
from openpyxl.styles import PatternFill

from app.planilha.leitura import COLUNA_LINHA, PlanilhaInvalida, aplicar_tipos, ler_planilha
from app.planilha.validacao import validar_estrutura
from tests.apoio import bytes_modelo, mutar


def coluna(ws, nome: str) -> int:
    for c in ws[1]:
        if c.value == nome:
            return c.column
    raise KeyError(nome)


def test_base_modelo_valida():
    base = ler_planilha(bytes_modelo())
    assert validar_estrutura(base) == []
    assert len(base["dProjeto"]) == 48
    assert len(base["fFinanceiro"]) == 432
    assert len(base["fContratos"]) == 60
    assert len(base["fEquipe"]) == 62
    assert len(base["dMetas"]) == 24


def test_abas_nao_listadas_ignoradas():
    base = ler_planilha(bytes_modelo())
    assert "fUsinasPI" not in base
    assert "LEIA-ME" not in base


def test_aba_obrigatoria_ausente():
    conteudo = mutar(lambda wb: wb.remove(wb["fSocial"]))
    erros = validar_estrutura(ler_planilha(conteudo))
    assert len(erros) == 1
    assert erros[0].aba == "fSocial"


def test_aba_opcional_ausente_nao_bloqueia():
    conteudo = mutar(lambda wb: wb.remove(wb["dIndicador"]))
    assert validar_estrutura(ler_planilha(conteudo)) == []


def test_coluna_ausente():
    def alterar(wb):
        ws = wb["fAmbiental"]
        ws.delete_cols(coluna(ws, "Licença Válida"))

    erros = validar_estrutura(ler_planilha(mutar(alterar)))
    assert any(e.aba == "fAmbiental" and e.coluna == "Licença Válida" for e in erros)


def test_chave_repetida():
    def alterar(wb):
        ws = wb["dProjeto"]
        ws.append([c.value for c in ws[2]])

    erros = validar_estrutura(ler_planilha(mutar(alterar)))
    assert any(e.aba == "dProjeto" and e.coluna == "Código Projeto" for e in erros)


def test_chave_vazia():
    def alterar(wb):
        ws = wb["dProjeto"]
        ws.cell(row=3, column=coluna(ws, "Código Projeto")).value = None

    erros = validar_estrutura(ler_planilha(mutar(alterar)))
    assert any(e.aba == "dProjeto" and e.linha == 3 for e in erros)


def test_referencia_inexistente():
    def alterar(wb):
        ws = wb["fAmbiental"]
        ws.cell(row=2, column=coluna(ws, "Código Projeto")).value = "PROJ999"

    erros = validar_estrutura(ler_planilha(mutar(alterar)))
    assert any(e.aba == "fAmbiental" and e.linha == 2 and "PROJ999" in e.mensagem for e in erros)


def test_empresa_inexistente():
    def alterar(wb):
        ws = wb["dProjeto"]
        ws.cell(row=2, column=coluna(ws, "Código Empresa")).value = "EMP999"

    erros = validar_estrutura(ler_planilha(mutar(alterar)))
    assert any(e.aba == "dProjeto" and e.coluna == "Código Empresa" for e in erros)


def test_medida_meta_desconhecida():
    def alterar(wb):
        ws = wb["dMetas"]
        ws.cell(row=2, column=coluna(ws, "Medida")).value = "Medida Inventada"

    erros = validar_estrutura(ler_planilha(mutar(alterar)))
    assert any(e.aba == "dMetas" and "Medida Inventada" in e.mensagem for e in erros)


def test_texto_em_coluna_numerica():
    def alterar(wb):
        ws = wb["dProjeto"]
        ws.cell(row=2, column=coluna(ws, "Investimento Previsto")).value = "abc"

    erros = validar_estrutura(ler_planilha(mutar(alterar)))
    assert any(
        e.aba == "dProjeto" and e.coluna == "Investimento Previsto" and e.linha == 2 for e in erros
    )


def test_data_invalida():
    def alterar(wb):
        ws = wb["fContratos"]
        ws.cell(row=2, column=coluna(ws, "Data Fim")).value = "amanhã"

    erros = validar_estrutura(ler_planilha(mutar(alterar)))
    assert any(e.aba == "fContratos" and e.coluna == "Data Fim" for e in erros)


def test_linhas_vazias_ignoradas():
    def alterar(wb):
        ws = wb["dProjeto"]
        amarelo = PatternFill("solid", fgColor="FFFF00")
        ultima = ws.max_row
        for r in range(ultima + 1, ultima + 6):
            for c in range(1, ws.max_column + 1):
                ws.cell(row=r, column=c).fill = amarelo

    base = ler_planilha(mutar(alterar))
    assert validar_estrutura(base) == []
    assert len(base["dProjeto"]) == 48


def test_simnao_normalizado():
    def alterar(wb):
        ws = wb["fAmbiental"]
        c = coluna(ws, "Licença Válida")
        ws.cell(row=2, column=c).value = " sim "
        ws.cell(row=3, column=c).value = "NÃO"

    base = ler_planilha(mutar(alterar))
    assert validar_estrutura(base) == []
    col = base["fAmbiental"]["Licença Válida"]
    assert col.iloc[0] == "Sim"
    assert col.iloc[1] == "Não"


def test_simnao_invalido():
    def alterar(wb):
        ws = wb["fAmbiental"]
        ws.cell(row=2, column=coluna(ws, "Licença Válida")).value = "Talvez"

    erros = validar_estrutura(ler_planilha(mutar(alterar)))
    assert any(e.aba == "fAmbiental" and e.coluna == "Licença Válida" for e in erros)


def test_arquivo_nao_xlsx():
    with pytest.raises(PlanilhaInvalida):
        ler_planilha(b"a,b\n1,2")


def test_linha_da_planilha_sem_lacunas():
    b = aplicar_tipos(ler_planilha(bytes_modelo()))
    assert list(b["dProjeto"][COLUNA_LINHA][:3]) == [2, 3, 4]


def test_linha_da_planilha_pula_linhas_em_branco():
    conteudo = mutar(lambda wb: wb["dProjeto"].insert_rows(3))  # linha 3 do Excel fica vazia
    b = aplicar_tipos(ler_planilha(conteudo))
    p = b["dProjeto"]
    assert p.loc[p["Código Projeto"] == "PROJ002", COLUNA_LINHA].item() == 4
    assert validar_estrutura(ler_planilha(conteudo)) == []
