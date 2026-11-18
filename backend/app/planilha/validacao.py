"""Validação estrutural (spec §7): erros que impedem a gravação da versão."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass

from app.planilha.esquema import ABAS, MEDIDAS_META
from app.planilha.leitura import CONVERSORES, INVALIDO, Base, vazio

# Quantas linhas listar por problema antes de resumir ("… e mais N linhas").
LIMITE_POR_PROBLEMA = 10

NOME_TIPO = {
    "numero": "um número",
    "inteiro": "um número inteiro",
    "data": "uma data",
    "simnao": '"Sim" ou "Não"',
}

PILARES = {"Ambiental", "Social", "Governança"}
POLARIDADES = {"Maior melhor", "Menor melhor"}


@dataclass
class ErroEstrutura:
    aba: str
    linha: int | None
    coluna: str | None
    mensagem: str

    def dict(self) -> dict:
        return asdict(self)


def _linha_excel(indice) -> int:
    # índice 0 do DataFrame = linha 2 do Excel (linha 1 é o cabeçalho)
    return int(indice) + 2


class _Coletor:
    def __init__(self):
        self.erros: list[ErroEstrutura] = []
        self._contagem: dict[tuple, int] = defaultdict(int)

    def add(self, aba, linha, coluna, mensagem, grupo: str | None = None):
        chave = (aba, coluna, grupo or mensagem)
        self._contagem[chave] += 1
        if self._contagem[chave] <= LIMITE_POR_PROBLEMA:
            self.erros.append(ErroEstrutura(aba, linha, coluna, mensagem))

    def resumir(self) -> list[ErroEstrutura]:
        for (aba, coluna, grupo), n in self._contagem.items():
            if n > LIMITE_POR_PROBLEMA:
                self.erros.append(
                    ErroEstrutura(aba, None, coluna, f"{grupo}: e mais {n - LIMITE_POR_PROBLEMA} linhas")
                )
        return self.erros


def validar_estrutura(base: Base) -> list[ErroEstrutura]:
    c = _Coletor()

    for nome, espec in ABAS.items():
        if nome not in base:
            if espec.obrigatoria:
                c.add(nome, None, None, f"Aba obrigatória ausente: {nome}")
            continue
        df = base[nome]
        ausentes = [col for col in espec.colunas if col not in df.columns]
        if ausentes and not espec.obrigatoria:
            continue  # aba opcional incompleta é ignorada pelo painel
        for col in ausentes:
            c.add(nome, None, col, f"Coluna obrigatória ausente: {col}")

        for col, tipo in espec.tipos.items():
            if tipo == "texto" or col not in df.columns:
                continue
            conv = CONVERSORES[tipo]
            for idx, v in df[col].items():
                if conv(v) is INVALIDO:
                    c.add(
                        nome, _linha_excel(idx), col,
                        f"Valor inválido em {col}: {v!r} (esperado {NOME_TIPO[tipo]})",
                        grupo=f"Valores inválidos em {col}",
                    )

        if espec.chave and espec.chave in df.columns:
            vistos: set = set()
            for idx, v in df[espec.chave].items():
                if vazio(v):
                    c.add(nome, _linha_excel(idx), espec.chave, f"Chave vazia: {espec.chave}",
                          grupo="Chave vazia")
                elif v in vistos:
                    c.add(nome, _linha_excel(idx), espec.chave, f"Chave repetida: {v}",
                          grupo="Chave repetida")
                else:
                    vistos.add(v)

        for col, (aba_ref, col_ref) in espec.referencias.items():
            if col not in df.columns or aba_ref not in base or col_ref not in base[aba_ref].columns:
                continue
            validos = set(base[aba_ref][col_ref].dropna())
            for idx, v in df[col].items():
                if not vazio(v) and v not in validos:
                    c.add(nome, _linha_excel(idx), col, f"{col} {v} não existe em {aba_ref}",
                          grupo=f"{col} inexistente em {aba_ref}")

    metas = base.get("dMetas")
    if metas is not None:
        regras = [
            ("Medida", MEDIDAS_META, "Medida que o sistema não sabe calcular"),
            ("Pilar", PILARES, "Pilar deve ser Ambiental, Social ou Governança"),
            ("Polaridade", POLARIDADES, 'Polaridade deve ser "Maior melhor" ou "Menor melhor"'),
        ]
        for col, permitidos, texto in regras:
            if col not in metas.columns:
                continue
            for idx, v in metas[col].items():
                if v not in permitidos:
                    c.add("dMetas", _linha_excel(idx), col, f"{texto}: {v!r}", grupo=texto)

    return c.resumir()
