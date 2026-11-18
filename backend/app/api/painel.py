"""Dados das telas do painel, com os filtros da barra superior (spec §9 e §10)."""
from collections.abc import Callable

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import repositorio
from app.auth import usuario_atual
from app.calculos.filtros import Filtros, aplicar_filtros
from app.db import get_session
from app.exportacao import pagina_para_xlsx
from app.models import Usuario
from app.paginas import indicadores, pilares, setores, temas, visao_geral
from app.paginas.tipos import Pagina
from app.planilha.leitura import Base, vazio

router = APIRouter(prefix="/api/painel", tags=["painel"])

PAGINAS: dict[str, Callable[[Base], Pagina]] = {
    "visao-geral": visao_geral.montar,
    "ambiental": pilares.ambiental,
    "social": pilares.social,
    "governanca": pilares.governanca,
    "metas": pilares.metas,
    "indicadores": indicadores.montar,
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


def montar_tela(base: Base, caminho: str) -> Pagina:
    """Monta a tela `caminho` ("ambiental", "setor/mineracao", "tema/energia-limpa"...).

    Levanta KeyError se o caminho não corresponde a nenhuma tela.
    """
    grupo, _, slug = caminho.partition("/")
    if grupo == "setor" and slug in setores.SETORES:
        return setores.montar(base, slug)
    if grupo == "tema" and slug in temas.TEMAS:
        return temas.montar(base, slug)
    if not slug and caminho in PAGINAS:
        return PAGINAS[caminho](base)
    raise KeyError(caminho)


def _tela(base: Base, f: Filtros, caminho: str, nao_encontrada: str) -> Pagina:
    try:
        return montar_tela(aplicar_filtros(base, f), caminho)
    except KeyError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, nao_encontrada) from None


XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/exportar/{caminho:path}")
def exportar(
    caminho: str,
    base: Base = Depends(base_ativa),
    f: Filtros = Depends(filtros),
    s: Session = Depends(get_session),
):
    pagina = _tela(base, f, caminho, "Página não encontrada")
    conteudo = pagina_para_xlsx(pagina, f, repositorio.versao_ativa(s))
    nome = f"ASG_{caminho.replace('/', '_')}_{date.today().isoformat()}.xlsx"
    return Response(conteudo, media_type=XLSX, headers={"Content-Disposition": f'attachment; filename="{nome}"'})


@router.get("/setor/{slug}", response_model=Pagina)
def pagina_setor(slug: str, base: Base = Depends(base_ativa), f: Filtros = Depends(filtros)):
    return _tela(base, f, f"setor/{slug}", "Setor não encontrado")


@router.get("/tema/{slug}", response_model=Pagina)
def pagina_tema(slug: str, base: Base = Depends(base_ativa), f: Filtros = Depends(filtros)):
    return _tela(base, f, f"tema/{slug}", "Tema não encontrado")


@router.get("/{pagina}", response_model=Pagina)
def pagina(pagina: str, base: Base = Depends(base_ativa), f: Filtros = Depends(filtros)):
    return _tela(base, f, pagina, "Página não encontrada")
