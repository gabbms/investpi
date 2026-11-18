"""Formato genérico das telas do painel: o frontend desenha qualquer `Pagina`."""
from typing import Literal

from pydantic import BaseModel

FormatoValor = Literal["brl", "num", "pct", "dec", "idx"]
Semaforo = Literal["verde", "amarelo", "vermelho"]


class Card(BaseModel):
    id: str
    titulo: str
    valor: float | None
    formato: FormatoValor
    status: Semaforo | None = None
    ajuda: str | None = None


class Serie(BaseModel):
    nome: str
    valores: list[float | None]
    cor: str | None = None


class Grafico(BaseModel):
    id: str
    titulo: str
    tipo: Literal["barra_h", "barra_h_empilhada", "colunas", "rosca"]
    categorias: list[str]
    series: list[Serie]
    formato: FormatoValor
    # cor de cada categoria (barras de uma série só, rosca); opcional
    cores_categorias: list[str | None] | None = None
    # fração da largura da grade de gráficos que o gráfico ocupa
    largura: Literal["terco", "metade", "inteira"] = "metade"


class Coluna(BaseModel):
    chave: str
    rotulo: str
    formato: Literal["texto", "brl", "num", "pct", "dec", "idx", "status", "simnao"]


class Tabela(BaseModel):
    id: str
    titulo: str
    colunas: list[Coluna]
    linhas: list[dict]
    # caixa de busca acima da tabela (filtra no navegador)
    busca: bool = False
    # linhas podem abrir uma lista (`ocorrencias`, `mais`); essas chaves não são colunas
    expansivel: bool = False


class Pagina(BaseModel):
    titulo: str
    subtitulo: str | None = None
    indice: Card | None = None
    cards: list[Card] = []
    graficos: list[Grafico] = []
    tabelas: list[Tabela] = []
