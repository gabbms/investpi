import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.db import Base, get_session
from app.main import app

engine_teste = create_engine(settings.TEST_DATABASE_URL)
SessaoTeste = sessionmaker(bind=engine_teste, expire_on_commit=False)


@pytest.fixture
def sessao_teste():
    import app.models  # noqa: F401  (registra as tabelas)

    Base.metadata.drop_all(engine_teste)
    Base.metadata.create_all(engine_teste)
    s = SessaoTeste()
    try:
        yield s
    finally:
        s.close()
        Base.metadata.drop_all(engine_teste)


@pytest.fixture
def cliente(sessao_teste):
    def _sessao():
        yield sessao_teste

    app.dependency_overrides[get_session] = _sessao
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


ADMIN = ("admin@teste.local", "Senha-Admin-1")
LEITOR = ("leitor@teste.local", "Senha-Leitor-1")


@pytest.fixture
def usuarios(sessao_teste):
    from app.auth import hash_senha
    from app.models import Usuario

    admin = Usuario(email=ADMIN[0], nome="Admin Teste", senha_hash=hash_senha(ADMIN[1]), perfil="admin")
    leitor = Usuario(email=LEITOR[0], nome="Leitor Teste", senha_hash=hash_senha(LEITOR[1]), perfil="leitor")
    sessao_teste.add_all([admin, leitor])
    sessao_teste.commit()
    return {"admin": admin, "leitor": leitor}


def _cabecalho(cliente, credenciais) -> dict:
    r = cliente.post("/api/auth/login", json={"email": credenciais[0], "senha": credenciais[1]})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


@pytest.fixture
def h_admin(cliente, usuarios):
    return _cabecalho(cliente, ADMIN)


@pytest.fixture
def h_leitor(cliente, usuarios):
    return _cabecalho(cliente, LEITOR)
