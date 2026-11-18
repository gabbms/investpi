"""Metas ASG, semáforo e Índice ASG (medidas DAX das pastas 9 e 10; spec §9)."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from app.calculos.medidas import Valor, m
from app.planilha.leitura import Base, vazio

Status = Literal["Atingida", "Atenção", "Abaixo"]
PILARES = ("Ambiental", "Social", "Governança")


@dataclass
class ResultadoMeta:
    id_meta: str
    pilar: str
    indicador: str
    medida: str
    peso: int
    valor: float | None
    meta: float | None
    limite: float | None
    formato: str
    polaridade: str
    status: Status | None
    atingimento: float | None

    def dict(self) -> dict:
        return asdict(self)


def _num(v) -> float | None:
    return None if vazio(v) else float(v)


def _status(v: Valor, meta: float | None, limite: float | None, maior: bool) -> Status | None:
    """Medida DAX `Status Indicador`."""
    if v is None or meta is None:
        return None
    lim = limite if limite is not None else 0.0
    if maior:
        return "Atingida" if v >= meta else ("Atenção" if v >= lim else "Abaixo")
    return "Atingida" if v <= meta else ("Atenção" if v <= lim else "Abaixo")


def _atingimento(v: Valor, meta: float | None, limite: float | None, maior: bool) -> float | None:
    """Medida DAX `Atingimento Meta` (BLANK em meta/limite vale 0, como no DAX)."""
    if v is None:
        return None
    mt = meta or 0.0
    lim = limite or 0.0
    if maior:
        return 1.0 if mt == 0 else min(v / mt, 1.0)
    return 1.0 if v <= mt else (0.5 if v <= lim else 0.0)


def avaliar_metas(base: Base, pesos: dict[str, int] | None = None) -> list[ResultadoMeta]:
    """Avalia as metas de dMetas. `pesos` (opcional) substitui o Peso da planilha por ID Meta (simulador)."""
    metas = base["dMetas"].sort_values("ID Meta")
    res = []
    for _, r in metas.iterrows():
        maior = r["Polaridade"] == "Maior melhor"
        meta, limite = _num(r["Meta"]), _num(r["Limite Atenção"])
        v = m(base, r["Medida"])
        res.append(
            ResultadoMeta(
                id_meta=r["ID Meta"],
                pilar=r["Pilar"],
                indicador=r["Indicador"],
                medida=r["Medida"],
                peso=pesos[r["ID Meta"]] if pesos and r["ID Meta"] in pesos else int(_num(r["Peso"]) or 0),
                valor=v,
                meta=meta,
                limite=limite,
                formato=r["Formato"] or "n",
                polaridade=r["Polaridade"],
                status=_status(v, meta, limite, maior),
                atingimento=_atingimento(v, meta, limite, maior),
            )
        )
    return res


def _indice(resultados: list[ResultadoMeta]) -> float | None:
    numerador = [r.peso * r.atingimento for r in resultados if r.atingimento is not None]
    denominador = sum(r.peso for r in resultados if r.atingimento is not None)
    if not numerador or denominador == 0:
        return None
    return 100 * sum(numerador) / denominador


def indice_pilar(base: Base, pilar: str, resultados: list[ResultadoMeta] | None = None) -> float | None:
    resultados = resultados if resultados is not None else avaliar_metas(base)
    return _indice([r for r in resultados if r.pilar == pilar])


def indice_geral(base: Base, resultados: list[ResultadoMeta] | None = None) -> float | None:
    """DIVIDE ( [Índice Ambiental] + [Índice Social] + [Índice Governança], 3 )."""
    resultados = resultados if resultados is not None else avaliar_metas(base)
    pilares = [indice_pilar(base, p, resultados) for p in PILARES]
    reais = [v for v in pilares if v is not None]
    return None if not reais else sum(reais) / 3


def indice_tema(base: Base, tema: str, resultados: list[ResultadoMeta] | None = None) -> float | None:
    """Índice de um tema material (T4, T6, T7…): mesmo método do índice de pilar,
    sobre as metas de dMetas cuja coluna `Tema Material` é `tema`.

    Não entra no Índice ASG Geral.
    """
    resultados = resultados if resultados is not None else avaliar_metas(base)
    metas = base["dMetas"]
    if "Tema Material" not in metas.columns:
        return None
    ids_do_tema = {
        id_meta
        for id_meta, codigo in zip(metas["ID Meta"], metas["Tema Material"])
        if not vazio(codigo) and str(codigo).strip() == tema
    }
    return _indice([r for r in resultados if r.id_meta in ids_do_tema])


def contar_status(base: Base, status: Status) -> float:
    return float(sum(1 for r in avaliar_metas(base) if r.status == status))


def pct_metas_atingidas(base: Base) -> float | None:
    res = avaliar_metas(base)
    com_status = sum(1 for r in res if r.status is not None)
    if com_status == 0:
        return None
    return sum(1 for r in res if r.status == "Atingida") / com_status


def status_medida(base: Base, medida: str) -> Status | None:
    metas = base["dMetas"]
    if medida not in set(metas["Medida"]):
        return None
    for r in avaliar_metas(base):
        if r.medida == medida:
            return r.status
    return None


def cor_indice(valor: float | None) -> Literal["verde", "amarelo", "vermelho"] | None:
    """Medida DAX `Cor Índice ASG`: ≥ 75 verde, ≥ 50 amarelo, senão vermelho."""
    if valor is None:
        return None
    return "verde" if valor >= 75 else ("amarelo" if valor >= 50 else "vermelho")
