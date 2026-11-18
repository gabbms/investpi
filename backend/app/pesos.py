"""Simulador de pesos das metas: validação dos pesos propostos e comparação oficial × simulado."""
from __future__ import annotations

from dataclasses import replace
from typing import Any

from app.calculos.metas import PILARES, avaliar_metas, indice_geral, indice_pilar
from app.planilha.leitura import Base, vazio

PESO_MAXIMO = 5


def validar_pesos(base: Base, pesos: dict[str, Any]) -> None:
    """Levanta ValueError (mensagem para o usuário) se algum peso proposto não puder ser usado."""
    metas = base["dMetas"]
    ids = set(metas["ID Meta"])
    for id_meta, peso in pesos.items():
        if id_meta not in ids:
            raise ValueError(f"Meta {id_meta} não existe na versão em uso.")
        if isinstance(peso, bool) or not isinstance(peso, int) or not 0 <= peso <= PESO_MAXIMO:
            raise ValueError(f"O peso de {id_meta} deve ser um número inteiro de 0 a {PESO_MAXIMO}.")
    # Pesos efetivos direto de dMetas (sem calcular as medidas). Só vale para os pilares que a
    # proposta mexe: um pilar que a planilha oficial já trouxe zerado não trava o simulador.
    efetivo: dict[str, list[int]] = {}
    tocados = set()
    for id_meta, pilar, peso in zip(metas["ID Meta"], metas["Pilar"], metas["Peso"]):
        oficial = 0 if vazio(peso) else int(float(peso))
        efetivo.setdefault(pilar, []).append(pesos.get(id_meta, oficial))
        if id_meta in pesos:
            tocados.add(pilar)
    for pilar in PILARES:
        if pilar in tocados and not any(efetivo.get(pilar, [])):
            raise ValueError(f"O pilar {pilar} precisa de pelo menos uma meta com peso maior que zero.")


def _indices(base: Base, resultados) -> dict[str, float | None]:
    return {"geral": indice_geral(base, resultados), **{p: indice_pilar(base, p, resultados) for p in PILARES}}


def simular(base: Base, pesos: dict[str, int]) -> dict:
    validar_pesos(base, pesos)
    oficial = avaliar_metas(base)
    simulado = [replace(r, peso=pesos[r.id_meta]) if r.id_meta in pesos else r for r in oficial]
    return {
        "oficial": _indices(base, oficial),
        "simulado": _indices(base, simulado),
        "metas": [
            {"id_meta": s.id_meta, "pilar": s.pilar, "indicador": s.indicador, "atingimento": s.atingimento,
             "status": s.status, "peso_oficial": o.peso, "peso": s.peso}
            for o, s in zip(oficial, simulado)
        ],
    }


def base_com_pesos(base: Base, pesos: dict[str, int]) -> Base:
    """Cópia da base com o Peso de dMetas trocado (a base em uso fica num cache compartilhado)."""
    validar_pesos(base, pesos)
    nova = dict(base)
    metas = base["dMetas"].copy()
    for id_meta, peso in pesos.items():
        metas.loc[metas["ID Meta"] == id_meta, "Peso"] = peso
    nova["dMetas"] = metas
    return nova
