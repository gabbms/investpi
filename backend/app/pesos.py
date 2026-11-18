"""Simulador de pesos das metas: validação dos pesos propostos e comparação oficial × simulado."""
from __future__ import annotations

from typing import Any

from app.calculos.metas import PILARES, avaliar_metas, indice_geral, indice_pilar
from app.planilha.leitura import Base

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
    for pilar in PILARES:
        r = [x for x in avaliar_metas(base, pesos) if x.pilar == pilar]
        if r and all(x.peso == 0 for x in r):
            raise ValueError(f"O pilar {pilar} precisa de pelo menos uma meta com peso maior que zero.")


def _indices(base: Base, resultados) -> dict[str, float | None]:
    return {"geral": indice_geral(base, resultados), **{p: indice_pilar(base, p, resultados) for p in PILARES}}


def simular(base: Base, pesos: dict[str, int]) -> dict:
    validar_pesos(base, pesos)
    oficial, simulado = avaliar_metas(base), avaliar_metas(base, pesos)
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
