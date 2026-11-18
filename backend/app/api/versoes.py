"""Histórico de versões e reativação (spec §7)."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import repositorio
from app.auth import exigir_admin
from app.calculos.checagens import rodar_checagens
from app.pesos import PedidoPesos, base_com_pesos
from app.db import get_session
from app.models import Usuario, Versao

router = APIRouter(prefix="/api/versoes", tags=["versões"])


class VersaoOut(BaseModel):
    id: int
    numero: int
    criado_em: datetime
    enviado_por: str | None
    nome_arquivo: str
    status: str
    linhas_por_aba: dict
    avisos: list
    erros: list

    @classmethod
    def de(cls, v: Versao) -> "VersaoOut":
        return cls(
            id=v.id, numero=v.numero, criado_em=v.criado_em,
            enviado_por=v.enviado_por.nome if v.enviado_por else None,
            nome_arquivo=v.nome_arquivo, status=v.status,
            linhas_por_aba=v.linhas_por_aba or {}, avisos=v.avisos or [], erros=v.erros or [],
        )


@router.post("/pesos", response_model=VersaoOut, status_code=status.HTTP_201_CREATED)
def salvar_pesos(pedido: PedidoPesos, admin: Usuario = Depends(exigir_admin), s: Session = Depends(get_session)):
    """Cria uma versão igual à ativa, só com o Peso das metas trocado (simulador de pesos)."""
    ativa = repositorio.versao_ativa(s)  # uma consulta só: o nome e os dados copiados são da mesma versão
    if ativa is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ainda não há dados carregados.")
    base = repositorio.carregar_base_da_versao(s, ativa.id, ativa.criado_em)
    try:
        nova = base_com_pesos(base, pedido.pesos)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from None
    avisos = [c.dict() for c in rodar_checagens(nova) if c.problemas]
    v = repositorio.salvar_versao(s, nova, admin.id, f"pesos ajustados (a partir da versão {ativa.numero})", avisos)
    s.refresh(v)
    return VersaoOut.de(v)


@router.get("", response_model=list[VersaoOut])
def listar(_: Usuario = Depends(exigir_admin), s: Session = Depends(get_session)):
    return [VersaoOut.de(v) for v in repositorio.listar_versoes(s)]


@router.post("/{versao_id}/ativar", response_model=VersaoOut)
def ativar(versao_id: int, _: Usuario = Depends(exigir_admin), s: Session = Depends(get_session)):
    try:
        v = repositorio.ativar_versao(s, versao_id)
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Versão não encontrada") from None
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from None
    return VersaoOut.de(v)
