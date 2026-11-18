"""Exporta uma `Pagina` do painel para Excel: o mesmo conteúdo que a tela recebe."""
from datetime import datetime
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from app.calculos.filtros import Filtros
from app.gri import IndiceGri
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


def _campos_filtro(filtros: Filtros) -> list[tuple[str, list[str]]]:
    return [
        ("Setor", filtros.setores),
        ("Vice-Presidência", filtros.vps),
        ("Status do projeto", filtros.status),
        ("Município", filtros.municipios),
    ]


def _contexto(ws: Worksheet, titulo: str, filtros: Filtros, versao: Versao) -> None:
    ws.title = "Contexto"
    linhas = [
        ("Página", titulo),
        ("Gerado em", data_local(datetime.now(FUSO))),
        ("Versão dos dados", f"nº {versao.numero} · {versao.nome_arquivo} · enviada em {data_local(versao.criado_em, com_hora=False)}"),
        *_campos_filtro(filtros),
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
    _contexto(wb.active, pagina.titulo, filtros, versao)
    _indicadores(wb, pagina)
    _graficos(wb, pagina)
    _tabelas(wb, pagina)
    saida = BytesIO()
    wb.save(saida)
    return saida.getvalue()


TITULO_GRI = "Índice de conteúdo GRI — indicadores quantitativos"
CABECALHO_GRI = ["Norma GRI", "Divulgação", "Indicador", "Valor", "Localização no relatório"]
CABECALHO_REVISAR = ["Referência", "Motivo", "Indicador", "Valor"]


def _resumo_filtros(filtros: Filtros) -> str:
    escolhidos = [f"{rotulo}: {', '.join(valores)}" for rotulo, valores in _campos_filtro(filtros) if valores]
    return " · ".join(escolhidos) or "carteira inteira"


def indice_gri_para_xlsx(indice: IndiceGri, filtros: Filtros, versao: Versao) -> bytes:
    """Anexo do relatório: o índice agrupado por norma e divulgação, e as referências a revisar."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Índice GRI"
    ws["A1"] = TITULO_GRI
    ws["A1"].font = Font(bold=True, size=13)
    ws["A2"] = f"Versão nº {versao.numero} · {versao.nome_arquivo} · filtros: {_resumo_filtros(filtros)}"
    _cabecalho(ws, 4, CABECALHO_GRI)
    linha = 5
    for norma in indice.normas:
        primeira_da_norma = True
        for div in norma.divulgacoes:
            for k, item in enumerate(div.linhas):
                ws.cell(row=linha, column=1, value=norma.titulo if primeira_da_norma else None)
                ws.cell(row=linha, column=2, value=div.titulo if k == 0 else None)
                ws.cell(row=linha, column=3, value=item.indicador)
                ws.cell(row=linha, column=4, value=item.valor)
                primeira_da_norma = False
                linha += 1
    linha += 1
    ws.cell(row=linha, column=1, value="Referências a revisar").font = NEGRITO
    _cabecalho(ws, linha + 1, CABECALHO_REVISAR)
    for k, r in enumerate(indice.revisar, start=linha + 2):
        for col, valor in enumerate([r.referencia, r.motivo, r.indicador, r.valor], start=1):
            ws.cell(row=k, column=col, value=valor)
    _ajustar(ws, congelar=False)
    ws.column_dimensions["A"].width = min(max(len(n.titulo) for n in indice.normas) + 2, LARGURA_MAX) if indice.normas else 20
    ws.freeze_panes = "A5"
    _contexto(wb.create_sheet("Contexto"), "Índice de conteúdo GRI", filtros, versao)
    saida = BytesIO()
    wb.save(saida)
    return saida.getvalue()
