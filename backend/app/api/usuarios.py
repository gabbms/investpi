"""Cadastro de usuários pelo administrador (spec §8). Não há cadastro aberto."""
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import exigir_admin, hash_senha
from app.db import get_session
from app.models import Usuario

router = APIRouter(prefix="/api/usuarios", tags=["usuários"])

Perfil = Literal["admin", "leitor"]
SENHA_MINIMA = 8
SENHA_MAXIMA_BYTES = 72  # limite do bcrypt


def _senha_cabe_no_bcrypt(senha: str | None) -> str | None:
    if senha is not None and len(senha.encode("utf-8")) > SENHA_MAXIMA_BYTES:
        raise ValueError("A senha deve ter no máximo 72 bytes (cerca de 72 caracteres sem acento).")
    return senha


class UsuarioOut(BaseModel):
    id: int
    email: str
    nome: str
    perfil: str
    ativo: bool
    criado_em: datetime

    @classmethod
    def de(cls, u: Usuario) -> "UsuarioOut":
        return cls(id=u.id, email=u.email, nome=u.nome, perfil=u.perfil, ativo=u.ativo, criado_em=u.criado_em)


class NovoUsuario(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+$")
    nome: str = Field(min_length=1, max_length=255)
    senha: str = Field(min_length=SENHA_MINIMA)
    perfil: Perfil

    _senha = field_validator("senha")(_senha_cabe_no_bcrypt)


class AlteracaoUsuario(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=255)
    perfil: Perfil | None = None
    ativo: bool | None = None
    senha: str | None = Field(default=None, min_length=SENHA_MINIMA)

    _senha = field_validator("senha")(_senha_cabe_no_bcrypt)


@router.get("", response_model=list[UsuarioOut])
def listar(_: Usuario = Depends(exigir_admin), s: Session = Depends(get_session)):
    return [UsuarioOut.de(u) for u in s.scalars(select(Usuario).order_by(Usuario.nome))]


@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def criar(dados: NovoUsuario, _: Usuario = Depends(exigir_admin), s: Session = Depends(get_session)):
    email = dados.email.strip().lower()
    if s.scalar(select(Usuario).where(func.lower(Usuario.email) == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe um usuário com este e-mail.")
    u = Usuario(email=email, nome=dados.nome.strip(), senha_hash=hash_senha(dados.senha), perfil=dados.perfil,
                ativo=True)
    s.add(u)
    s.commit()
    return UsuarioOut.de(u)


@router.patch("/{usuario_id}", response_model=UsuarioOut)
def alterar(
    usuario_id: int,
    dados: AlteracaoUsuario,
    admin: Usuario = Depends(exigir_admin),
    s: Session = Depends(get_session),
):
    u = s.get(Usuario, usuario_id)
    if u is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuário não encontrado.")
    if u.id == admin.id and (dados.ativo is False or dados.perfil == "leitor"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Você não pode desativar nem tirar o perfil de administrador da sua própria conta.")
    if dados.nome is not None:
        u.nome = dados.nome.strip()
    if dados.perfil is not None:
        u.perfil = dados.perfil
    if dados.ativo is not None:
        u.ativo = dados.ativo
    if dados.senha is not None:
        u.senha_hash = hash_senha(dados.senha)
    s.commit()
    return UsuarioOut.de(u)
