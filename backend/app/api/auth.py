from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import criar_token, usuario_atual, verificar_senha
from app.db import get_session
from app.models import Usuario

router = APIRouter(prefix="/api/auth", tags=["auth"])


class Login(BaseModel):
    email: str
    senha: str


class UsuarioPublico(BaseModel):
    id: int
    email: str
    nome: str
    perfil: str

    @classmethod
    def de(cls, u: Usuario) -> "UsuarioPublico":
        return cls(id=u.id, email=u.email, nome=u.nome, perfil=u.perfil)


class RespostaLogin(BaseModel):
    token: str
    usuario: UsuarioPublico


@router.post("/login", response_model=RespostaLogin)
def login(dados: Login, s: Session = Depends(get_session)):
    u = s.scalar(select(Usuario).where(func.lower(Usuario.email) == dados.email.strip().lower()))
    if u is None or not u.ativo or not verificar_senha(dados.senha, u.senha_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha incorretos.")
    return RespostaLogin(token=criar_token(u.id), usuario=UsuarioPublico.de(u))


@router.get("/eu", response_model=UsuarioPublico)
def eu(u: Usuario = Depends(usuario_atual)):
    return UsuarioPublico.de(u)
