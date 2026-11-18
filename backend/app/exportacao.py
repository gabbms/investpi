"""Exporta uma `Pagina` do painel para Excel: o mesmo conteúdo que a tela recebe."""
from datetime import datetime
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from app.calculos.filtros import Filtros
from app.models import Versao
from app.paginas.comum import FUSO, data_local
from app.paginas.tipos import Card, Pagina

FORMATOS = {"brl": '"R$" #,##0.00', "pct": "0.0%", "num": "#,##0", "dec": "0.00", "idx": "0"}
COLUNAS_TEXTO = {"texto", "status", "simnao"}
STATUS = {"verde": "Verde", "amarelo": "Amarelo", "vermelho": "Vermelho"}
PROIBIDOS = set("[]:*?/\\")
LARGURA_MAX = 60
NEGRITO = Font(bold=True)


def _nome_aba(titulo: str, usados: set[str]) -> str:
    """Nome válido no Excel: sem []:*?/\\, até 31 caracteres e sem repetir (sem diferenciar caixa)."""
    limpo = "".join(" " if c in PROIBIDOS else c for c in titulo)
    limpo = " ".join(limpo.split()).strip("'") or "Tabela"
    nome, n = limpo[:31], 2
    while nome.lower() in usados:
        sufixo = f" ({n})"
        nome, n = limpo[: 31 - len(sufixo)].rstrip() + sufixo, n + 1
    usados.add(nome.lower())
    return nome


def _ajustar(ws: Worksheet, congelar: bool = True) -> None:
    larguras: dict[int, int] = {}
    for linha in ws.iter_rows():
        for celula in linha:
            if celula.value is not None:
                larguras[celula.column] = max(larguras.get(celula.column, 0), len(str(celula.value)))
    for col, largura in larguras.items():
        ws.column_dimensions[get_column_letter(col)].width = min(largura + 2, LARGURA_MAX)
    if congelar:
        ws.freeze_panes = "A2"


def _escrever(ws: Worksheet, linha: int, coluna: int, valor, formato: str | None) -> None:
    celula = ws.cell(row=linha, column=coluna, value=valor)
    if formato in FORMATOS and isinstance(valor, (int, float)):
        celula.number_format = FORMATOS[formato]


def _cabecalho(ws: Worksheet, linha: int, rotulos: list[str]) -> None:
    for i, rotulo in enumerate(rotulos, start=1):
        ws.cell(row=linha, column=i, value=rotulo).font = NEGRITO


def _contexto(wb: Workbook, pagina: Pagina, filtros: Filtros, versao: Versao) -> None:
    ws = wb.active
    ws.title = "Contexto"
    linhas = [
        ("Página", pagina.titulo),
        ("Gerado em", data_local(datetime.now(FUSO))),
        ("Versão dos dados", f"nº {versao.numero} · {versao.nome_arquivo} · enviada em {data_local(versao.criado_em, com_hora=False)}"),
        ("Setor", filtros.setores),
        ("Vice-Presidência", filtros.vps),
        ("Status do projeto", filtros.status),
        ("Município", filtros.municipios),
    ]
    for rotulo, valor in linhas:
        if isinstance(valor, list):
            valor = ", ".join(valor) or "Todos"
        ws.append([rotulo, valor])
        ws.cell(row=ws.max_row, column=1).font = NEGRITO
    _ajustar(ws, congelar=False)


def _indicadores(wb: Workbook, pagina: Pagina) -> None:
    ws = wb.create_sheet("Indicadores")
    _cabecalho(ws, 1, ["Indicador", "Valor", "Status"])
    cards: list[Card] = ([pagina.indice] if pagina.indice else []) + pagina.cards
    for i, card in enumerate(cards, start=2):
        ws.cell(row=i, column=1, value=card.titulo)
        _escrever(ws, i, 2, card.valor, card.formato)
        ws.cell(row=i, column=3, value=STATUS.get(card.status or "", None))
    _ajustar(ws)


def _graficos(wb: Workbook, pagina: Pagina) -> None:
    ws = wb.create_sheet("Gráficos")
    linha = 1
    for g in pagina.graficos:
        ws.cell(row=linha, column=1, value=g.titulo).font = NEGRITO
        _cabecalho(ws, linha + 1, ["Categoria"] + [s.nome for s in g.series])
        linha += 2
        for k, categoria in enumerate(g.categorias):
            ws.cell(row=linha, column=1, value=categoria)
            for j, serie in enumerate(g.series, start=2):
                valor = serie.valores[k] if k < len(serie.valores) else None
                _escrever(ws, linha, j, valor, g.formato)
            linha += 1
        linha += 1  # linha vazia entre os blocos
    _ajustar(ws, congelar=False)


def _texto(valor):
    if valor is None:
        return None
    if isinstance(valor, bool):
        return "Sim" if valor else "Não"
    return str(valor)


def _tabelas(wb: Workbook, pagina: Pagina) -> None:
    usados = {n.lower() for n in wb.sheetnames}
    for t in pagina.tabelas:
        ws = wb.create_sheet(_nome_aba(t.titulo, usados))
        _cabecalho(ws, 1, [c.rotulo for c in t.colunas])
        for i, registro in enumerate(t.linhas, start=2):
            for j, col in enumerate(t.colunas, start=1):
                valor = registro.get(col.chave)
                if col.formato in COLUNAS_TEXTO:
                    ws.cell(row=i, column=j, value=_texto(valor)).number_format = "@"
                else:
                    _escrever(ws, i, j, valor, col.formato)
        _ajustar(ws)


def pagina_para_xlsx(pagina: Pagina, filtros: Filtros, versao: Versao) -> bytes:
    wb = Workbook()
    _contexto(wb, pagina, filtros, versao)
    _indicadores(wb, pagina)
    _graficos(wb, pagina)
    _tabelas(wb, pagina)
    saida = BytesIO()
    wb.save(saida)
    return saida.getvalue()
