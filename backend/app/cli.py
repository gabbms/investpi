"""Comandos de linha de comando.

    python -m app.cli inicializar

Cria as tabelas, os usuários de demonstração (administrador e leitor, a partir
do .env) e importa a planilha modelo como versão 1 se ainda não houver versão.
Pode ser executado várias vezes: só cria o que falta.
"""
from __future__ import annotations

import sys

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import repositorio
from app.auth import hash_senha
from app.calculos.checagens import rodar_checagens
from app.config import settings
from app.db import Base, SessionLocal, engine
from app.models import Usuario, Versao
from app.planilha.leitura import aplicar_tipos, ler_planilha
from app.planilha.validacao import validar_estrutura


def _criar_usuario(s: Session, email: str | None, senha: str | None, nome: str, perfil: str) -> int:
    if not email or not senha:
        return 0
    if s.scalar(select(Usuario).where(Usuario.email == email)):
        return 0
    s.add(Usuario(email=email, nome=nome, senha_hash=hash_senha(senha), perfil=perfil, ativo=True))
    s.commit()
    return 1


def inicializar(s: Session) -> dict[str, int]:
    usuarios = _criar_usuario(s, settings.ADMIN_EMAIL, settings.ADMIN_SENHA, "Administrador", "admin")
    usuarios += _criar_usuario(s, settings.LEITOR_EMAIL, settings.LEITOR_SENHA, "Leitor", "leitor")

    versao = 0
    if s.scalar(select(Versao.id).limit(1)) is None:
        caminho = settings.caminho_modelo
        base = ler_planilha(caminho.read_bytes())
        erros = validar_estrutura(base)
        if erros:
            raise SystemExit(f"A planilha modelo {caminho} tem erros estruturais: {erros[:3]}")
        base = aplicar_tipos(base)
        avisos = [c.dict() for c in rodar_checagens(base) if c.problemas]
        admin_id = s.scalar(select(Usuario.id).where(Usuario.email == settings.ADMIN_EMAIL))
        repositorio.salvar_versao(s, base, admin_id, caminho.name, avisos)
        versao = 1
    return {"usuarios": usuarios, "versao": versao}


def main(argv: list[str]) -> int:
    if argv[:1] != ["inicializar"]:
        print(__doc__)
        return 2
    import app.models  # noqa: F401

    Base.metadata.create_all(engine)
    with SessionLocal() as s:
        criados = inicializar(s)
    print(f"Usuários criados: {criados['usuarios']} · Versões importadas: {criados['versao']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
