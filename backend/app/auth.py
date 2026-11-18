"""Senhas (bcrypt), tokens de sessão (JWT HS256) e permissões (spec §8)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_session
from app.models import Usuario

_bearer = HTTPBearer(auto_error=False)


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("ascii"))
    except ValueError:
        return False


def criar_token(usuario_id: int, horas: float | None = None) -> str:
    agora = datetime.now(timezone.utc)
    validade = timedelta(hours=settings.JWT_HORAS if horas is None else horas)
    return jwt.encode({"sub": str(usuario_id), "iat": agora, "exp": agora + validade},
                      settings.JWT_SEGREDO, algorithm="HS256")


def _nao_autenticado(detalhe: str = "Sessão expirada ou inválida. Entre novamente.") -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, detalhe, headers={"WWW-Authenticate": "Bearer"})


def usuario_atual(
    cred: HTTPAuthorizationCredentials | None = Depends(_bearer),
    s: Session = Depends(get_session),
) -> Usuario:
    if cred is None:
        raise _nao_autenticado("Login necessário.")
    try:
        dados = jwt.decode(cred.credentials, settings.JWT_SEGREDO, algorithms=["HS256"])
        usuario_id = int(dados["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise _nao_autenticado() from None
    usuario = s.get(Usuario, usuario_id)
    if usuario is None or not usuario.ativo:
        raise _nao_autenticado()
    return usuario


def exigir_admin(usuario: Usuario = Depends(usuario_atual)) -> Usuario:
    if usuario.perfil != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Apenas administradores podem fazer isso.")
    return usuario
