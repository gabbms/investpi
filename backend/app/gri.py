"""Índice de conteúdo GRI: liga cada indicador de dIndicador à divulgação GRI que ele atende.

Fonte dos nomes (tradução oficial das Normas GRI para o português, publicada pela GRI):
- títulos das normas: lista "GRI Standards Portuguese Translations" em globalreporting.org
  (how-to-use-the-gri-standards/gri-standards-portuguese-translations);
- títulos das divulgações: cabeçalhos "Conteúdo X-Y …" dos PDFs em português — GRI 2: Conteúdos
  Gerais 2021 (pdf.ashx?id=13899); GRI 201, 203, 204, 205 e 302 (PDFs próprios); para 303, 304, 305,
  306, 403, 404, 405 e 413, a edição em português da GRI 11: Setor de Petróleo e Gás 2021, que
  reproduz essas divulgações.
Datas de substituição: notas da própria GRI (GRI 302 → GRI 103: Energy 2025 em 01/01/2027;
GRI 304 → GRI 101: Biodiversity 2024 em 01/01/2026).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from app.paginas.indicadores import valores_atuais
from app.planilha.leitura import Base, vazio


@dataclass(frozen=True)
class Norma:
    titulo: str
    substituida_por: str | None = None
    substituida_em: date | None = None


NORMAS: dict[str, Norma] = {
    "2": Norma("GRI 2: Conteúdos Gerais 2021"),
    "201": Norma("GRI 201: Desempenho Econômico 2016"),
    "203": Norma("GRI 203: Impactos Econômicos Indiretos 2016"),
    "204": Norma("GRI 204: Práticas de Compra 2016"),
    "205": Norma("GRI 205: Combate à Corrupção 2016"),
    "302": Norma("GRI 302: Energia 2016", "GRI 103: Energy 2025", date(2027, 1, 1)),
    "303": Norma("GRI 303: Água e Efluentes 2018"),
    # fora da lista atual de traduções; nunca exibida depois de 01/01/2026 (vai para "a revisar")
    "304": Norma("GRI 304: Biodiversidade 2016", "GRI 101: Biodiversity 2024", date(2026, 1, 1)),
    "305": Norma("GRI 305: Emissões 2016"),
    "306": Norma("GRI 306: Resíduos 2020"),
    "403": Norma("GRI 403: Saúde e Segurança do Trabalho 2018"),
    "404": Norma("GRI 404: Capacitação e Educação 2016"),
    "405": Norma("GRI 405: Diversidade e Igualdade de Oportunidades 2016"),
    "413": Norma("GRI 413: Comunidades Locais 2016"),
}

DIVULGACOES: dict[str, str] = {
    "2-5": "Verificação externa",
    "2-6": "Atividades, cadeia de valor e outras relações de negócios",
    "2-12": "Papel desempenhado pelo mais alto órgão de governança na supervisão da gestão dos impactos",
    "2-25": "Processos para reparar impactos negativos",
    "2-26": "Mecanismos para aconselhamento e apresentação de preocupações",
    "2-27": "Conformidade com leis e regulamentos",
    "2-29": "Abordagem para engajamento de stakeholders",
    "201-1": "Valor econômico direto gerado e distribuído",
    "203-1": "Investimentos em infraestrutura e apoio a serviços",
    "203-2": "Impactos econômicos indiretos significativos",
    "204-1": "Proporção de gastos com fornecedores locais",
    "205-2": "Comunicação e capacitação em políticas e procedimentos de combate à corrupção",
    "205-3": "Casos confirmados de corrupção e medidas tomadas",
    "302-1": "Consumo de energia dentro da organização",
    "302-3": "Intensidade energética",
    "303-3": "Captação de água",
    "303-5": "Consumo de água",
    "304-3": "Habitats protegidos ou restaurados",
    "305-1": "Emissões diretas (Escopo 1) de gases de efeito estufa (GEE)",
    "305-4": "Intensidade de emissões de gases de efeito estufa (GEE)",
    "305-5": "Redução de emissões de gases de efeito estufa (GEE)",
    "306-2": "Gestão de impactos significativos relacionados a resíduos",
    "306-3": "Resíduos gerados",
    "306-4": "Resíduos não destinados para disposição final",
    "306-5": "Resíduos destinados para disposição final",
    "403-5": "Capacitação de trabalhadores em saúde e segurança do trabalho",
    "403-9": "Acidentes de trabalho",
    "404-1": "Média de horas de capacitação por ano, por empregado",
    "404-2": "Programas para o aperfeiçoamento de competências dos empregados e de assistência "
             "para transição de carreira",
    "405-1": "Diversidade em órgãos de governança e empregados",
    "413-1": "Operações com engajamento, avaliações de impacto e programas de desenvolvimento "
             "voltados à comunidade local",
}

MOTIVO_G4 = "Divulgação do modelo GRI-G4, anterior às Normas GRI"
MOTIVO_SETORIAL = "Norma setorial sem divulgação específica"
MOTIVO_DESCONHECIDA = "Divulgação não reconhecida"

_DIVULGACAO = re.compile(r"^GRI (\d+)-(\d+)$")
_G4 = re.compile(r"^GRI[- ]G4\b", re.IGNORECASE)  # "GRI-G4 EU1" ou "GRI G4 EU1"
_SETORIAL = re.compile(r"^GRI 1[1-9]\b(?!-)")  # GRI 11 a 19: normas setoriais, sem número de divulgação


@dataclass
class LinhaGri:
    indicador: str
    valor: str


@dataclass
class DivulgacaoGri:
    titulo: str
    linhas: list[LinhaGri]


@dataclass
class NormaGri:
    titulo: str
    divulgacoes: list[DivulgacaoGri]


@dataclass
class RevisarGri:
    referencia: str
    motivo: str
    indicador: str
    valor: str


@dataclass
class IndiceGri:
    normas: list[NormaGri]
    revisar: list[RevisarGri]


def normalizar_referencia(texto: str) -> str:
    """Ex.: " gri  403-9 " → "GRI 403-9": sem espaços sobrando e com o prefixo GRI em maiúsculas."""
    t = " ".join(str(texto).split())
    return re.sub(r"^gri\b", "GRI", t, flags=re.IGNORECASE)


def _classificar(ref: str, hoje: date) -> tuple[str, str] | str:
    """(norma, divulgação) quando a referência entra no índice; senão, o motivo para revisar."""
    if _G4.match(ref):
        return MOTIVO_G4
    if _SETORIAL.match(ref):
        return MOTIVO_SETORIAL
    m = _DIVULGACAO.match(ref)
    cod = f"{m.group(1)}-{m.group(2)}" if m else None
    if not m or m.group(1) not in NORMAS or cod not in DIVULGACOES:
        return MOTIVO_DESCONHECIDA
    norma = NORMAS[m.group(1)]
    if norma.substituida_em and hoje >= norma.substituida_em:
        return f"Norma substituída por {norma.substituida_por} em {norma.substituida_em:%d/%m/%Y}"
    return m.group(1), cod


def _ordem(cod: str) -> tuple[int, int]:
    norma, item = cod.split("-")
    return int(norma), int(item)


def montar_indice_gri(base: Base, hoje: date) -> IndiceGri:
    """Índice da base já filtrada: os indicadores com referência GRI, agrupados por norma e divulgação."""
    valores = valores_atuais(base)
    por_divulgacao: dict[str, list[LinhaGri]] = {}
    revisar: list[RevisarGri] = []
    for _, r in base["dIndicador"].sort_values("ID Indicador").iterrows():
        bruta = r["Referência GRI"]
        if vazio(bruta) or str(bruta).strip() in ("", "-"):
            continue
        ref = normalizar_referencia(bruta)
        ident = str(r["ID Indicador"]).strip()
        nome = r["Indicador"]
        indicador = ident if vazio(nome) else f"{ident} {str(nome).strip()}"
        valor = valores.get(ident, "—")
        destino = _classificar(ref, hoje)
        if isinstance(destino, str):
            revisar.append(RevisarGri(ref, destino, indicador, valor))
        else:
            por_divulgacao.setdefault(destino[1], []).append(LinhaGri(indicador, valor))

    normas: list[NormaGri] = []
    for cod in sorted(por_divulgacao, key=_ordem):
        titulo_norma = NORMAS[cod.split("-")[0]].titulo
        if not normas or normas[-1].titulo != titulo_norma:
            normas.append(NormaGri(titulo_norma, []))
        normas[-1].divulgacoes.append(DivulgacaoGri(f"{cod} {DIVULGACOES[cod]}", por_divulgacao[cod]))
    return IndiceGri(normas, revisar)
