"""Envio da planilha: prévia (validação sem gravar), confirmação e modelo (spec §7)."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import repositorio
from app.api.versoes import VersaoOut
from app.auth import exigir_admin, usuario_atual
from app.calculos.checagens import rodar_checagens
from app.config import settings
from app.db import get_session
from app.models import Usuario
from app.planilha.esquema import ABAS
from app.planilha.leitura import PlanilhaInvalida, aplicar_tipos, ler_planilha
from app.planilha.validacao import validar_estrutura

router = APIRouter(prefix="/api/importacao", tags=["importação"])

TAMANHO_MAXIMO = 20 * 1024 * 1024
MSG_INVALIDA = "Arquivo não é uma planilha .xlsx válida"


async def _ler(arquivo: UploadFile):
    conteudo = await arquivo.read(TAMANHO_MAXIMO + 1)
    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Arquivo maior que 20 MB")
    try:
        base = ler_planilha(conteudo)
    except PlanilhaInvalida as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exc.mensagem) from None
    erros = validar_estrutura(base)
    linhas = {aba: len(base[aba]) for aba in ABAS if aba in base}
    return base, erros, linhas


@router.post("/previa")
async def previa(arquivo: UploadFile, _: Usuario = Depends(exigir_admin)):
    base, erros, linhas = await _ler(arquivo)
    checagens = [] if erros else [c.com_ocorrencias() for c in rodar_checagens(aplicar_tipos(base))]
    return {
        "linhas_por_aba": linhas,
        "erros": [e.dict() for e in erros],
        "checagens": checagens,
        "pode_confirmar": not erros,
    }


@router.post("/confirmar", status_code=status.HTTP_201_CREATED)
async def confirmar(
    arquivo: UploadFile,
    usuario: Usuario = Depends(exigir_admin),
    s: Session = Depends(get_session),
):
    nome = arquivo.filename or "planilha.xlsx"
    try:
        base, erros, _ = await _ler(arquivo)
    except HTTPException as exc:
        if exc.status_code == status.HTTP_400_BAD_REQUEST:
            repositorio.registrar_rejeicao(s, nome, usuario.id, [{"aba": None, "linha": None, "coluna": None,
                                                                   "mensagem": MSG_INVALIDA}])
        raise
    if erros:
        repositorio.registrar_rejeicao(s, nome, usuario.id, [e.dict() for e in erros])
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            {"mensagem": "A planilha tem erros estruturais e não foi gravada.", "erros": [e.dict() for e in erros]},
        )
    tipada = aplicar_tipos(base)
    avisos = [c.dict() for c in rodar_checagens(tipada) if c.problemas]
    versao = repositorio.salvar_versao(s, tipada, usuario.id, nome, avisos)
    s.refresh(versao)
    return {"versao": VersaoOut.de(versao)}


@router.get("/modelo")
def modelo(_: Usuario = Depends(usuario_atual)):
    return FileResponse(
        settings.caminho_modelo,
        filename="planilha_modelo_ASG.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
