"""Detalhes pendentes das revisões anteriores: catálogo, arredondamento, exportação, publicação."""
from io import BytesIO

import pytest
from openpyxl import load_workbook

from app import repositorio
from app.calculos import medidas
from app.exportacao import _nome_aba
from app.paginas import indicadores
from app.paginas.comum import texto_valor
from tests.apoio import base_modelo


@pytest.fixture
def com_versao(sessao_teste, usuarios):
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, base_modelo(), usuarios["admin"].id, "base.xlsx", [])
    yield
    repositorio.limpar_cache()


# --- Catálogo: erro dentro de uma medida não vira "—" --------------------------------------------

def test_medida_desconhecida_vira_traco():
    b = base_modelo()
    b["dIndicador"].loc[0, "Medida DAX"] = "Medida Que Nao Existe"
    assert indicadores.valores_atuais(b)[str(b["dIndicador"].loc[0, "ID Indicador"])] == "—"


def test_keyerror_dentro_de_uma_medida_nao_e_escondido(monkeypatch):
    b = base_modelo()
    nome = b["dIndicador"].loc[0, "Medida DAX"]

    def quebrada(_base):
        raise KeyError("coluna que sumiu")

    monkeypatch.setitem(medidas.MEDIDAS, nome, quebrada)
    with pytest.raises(KeyError, match="coluna que sumiu"):
        indicadores.valores_atuais(b)


# --- Arredondamento igual ao do navegador (meio para cima) ---------------------------------------

@pytest.mark.parametrize("v, formato, esperado", [
    (0.125, "dec", "0,13"),
    (2.5, "num", "3"),
    (0.0005, "pct", "0,1%"),
    (1.005, "dec", "1"),  # 1,005 em binário é 1,00499…: o navegador também mostra "1"
])
def test_arredonda_meio_para_cima(v, formato, esperado):
    assert texto_valor(v, formato) == esperado


# --- Nome das abas do Excel ----------------------------------------------------------------------

def test_nome_aba_tira_caracteres_proibidos_e_limita():
    assert _nome_aba("Água [m³]: reuso/total?", set()) == "Água m³ reuso total"
    assert len(_nome_aba("x" * 50, set())) == 31


def test_nome_aba_repetido_ganha_numero():
    usados: set[str] = set()
    assert _nome_aba("Pilar Social", usados) == "Pilar Social"
    assert _nome_aba("pilar social", usados) == "pilar social (2)"
    longo = "y" * 40
    assert _nome_aba(longo, usados) == "y" * 31
    assert _nome_aba(longo, usados) == "y" * 27 + " (2)"


# --- Catálogo exportado: "Valor atual" como número -----------------------------------------------

def test_catalogo_exporta_valor_como_numero(cliente, com_versao, h_leitor):
    r = cliente.get("/api/painel/exportar/indicadores", headers=h_leitor)
    wb = load_workbook(BytesIO(r.content))
    ws = next(wb[n] for n in wb.sheetnames if n.startswith("Catálogo"))
    cab = [c.value for c in ws[1]]
    col = cab.index("Valor atual") + 1
    por_id = {ws.cell(row=i, column=1).value: ws.cell(row=i, column=col) for i in range(2, ws.max_row + 1)}
    assert por_id["IND01"].value == pytest.approx(9.0e9, rel=1e-2)
    assert por_id["IND01"].number_format == '"R$" #,##0.00'
    assert por_id["IND02"].value == 48
    assert isinstance(por_id["IND26"].value, float) and por_id["IND26"].number_format == "0.0%"
