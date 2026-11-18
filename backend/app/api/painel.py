"""Dados das telas do painel, com os filtros da barra superior (spec §9 e §10)."""
from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import repositorio
from app.auth import usuario_atual
from app.calculos.filtros import Filtros, aplicar_filtros
from app.db import get_session
from app.models import Usuario
from app.paginas import pilares, setores, visao_geral
from app.paginas.tipos import Pagina
from app.planilha.leitura import Base, vazio

router = APIRouter(prefix="/api/painel", tags=["painel"])

PAGINAS: dict[str, Callable[[Base], Pagina]] = {
    "visao-geral": visao_geral.montar,
    "ambiental": pilares.ambiental,
    "social": pilares.social,
    "governanca": pilares.governanca,
    "metas": pilares.metas,
}


def base_ativa(s: Session = Depends(get_session), _: Usuario = Depends(usuario_atual)) -> Base:
    base = repositorio.carregar_base_ativa(s)
    if base is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Nenhuma versão de dados carregada")
    return base


def filtros(
    setor: list[str] = Query(default=[]),
    vp: list[str] = Query(default=[]),
    status_: list[str] = Query(default=[], alias="status"),
    municipio: list[str] = Query(default=[]),
) -> Filtros:
    return Filtros(setores=setor, vps=vp, status=status_, municipios=municipio)


def _unicos(valores) -> list[str]:
    vistos: list[str] = []
    for v in valores:
        if not vazio(v) and v not in vistos:
            vistos.append(v)
    return vistos


@router.get("/opcoes")
def opcoes(base: Base = Depends(base_ativa)):
    s = base["dSetor"].sort_values("Ordem")
    p = base["dProjeto"]
    return {
        "setores": _unicos(s["Setor Investe"]),
        "vps": _unicos(s["Vice-Presidência"]),
        "status": sorted(_unicos(p["Status Projeto"])),
        "municipios": sorted(_unicos(p["Município"])),
    }


@router.get("/setor/{slug}", response_model=Pagina)
def pagina_setor(slug: str, base: Base = Depends(base_ativa), f: Filtros = Depends(filtros)):
    if slug not in setores.SETORES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Setor não encontrado")
    return setores.montar(aplicar_filtros(base, f), slug)


@router.get("/{pagina}", response_model=Pagina)
def pagina(pagina: str, base: Base = Depends(base_ativa), f: Filtros = Depends(filtros)):
    montar = PAGINAS.get(pagina)
    if montar is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Página não encontrada")
    return montar(aplicar_filtros(base, f))
