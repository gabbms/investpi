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
