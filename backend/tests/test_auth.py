"""Login, token e perfis (spec §8)."""
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth import criar_token, exigir_admin
from app.db import get_session
from tests.conftest import ADMIN, LEITOR


def login(cliente, email, senha):
    return cliente.post("/api/auth/login", json={"email": email, "senha": senha})


def test_login_ok(cliente, usuarios):
    r = login(cliente, *ADMIN)
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["token"]
    assert corpo["usuario"] == {
        "id": usuarios["admin"].id, "email": ADMIN[0], "nome": "Admin Teste", "perfil": "admin",
    }


def test_login_email_maiusculo(cliente, usuarios):
    assert login(cliente, ADMIN[0].upper(), ADMIN[1]).status_code == 200


def test_senha_errada_e_email_desconhecido_mesma_mensagem(cliente, usuarios):
    a = login(cliente, ADMIN[0], "errada")
    b = login(cliente, "ninguem@teste.local", "errada")
    assert a.status_code == b.status_code == 401
    assert a.json() == b.json()


def test_usuario_inativo(cliente, usuarios, sessao_teste):
    usuarios["leitor"].ativo = False
    sessao_teste.commit()
    assert login(cliente, *LEITOR).status_code == 401


def test_eu(cliente, h_leitor):
    r = cliente.get("/api/auth/eu", headers=h_leitor)
    assert r.status_code == 200
    assert r.json()["perfil"] == "leitor"


def test_eu_sem_token(cliente):
    assert cliente.get("/api/auth/eu").status_code == 401


def test_token_invalido(cliente, usuarios):
    assert cliente.get("/api/auth/eu", headers={"Authorization": "Bearer xyz"}).status_code == 401


def test_token_expirado(cliente, usuarios):
    token = criar_token(usuarios["admin"].id, horas=-1)
    r = cliente.get("/api/auth/eu", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_usuario_desativado_depois_do_login(cliente, usuarios, h_leitor, sessao_teste):
    usuarios["leitor"].ativo = False
    sessao_teste.commit()
    assert cliente.get("/api/auth/eu", headers=h_leitor).status_code == 401


def test_exigir_admin(sessao_teste, usuarios):
    mini = FastAPI()

    @mini.get("/so-admin")
    def so_admin(u=Depends(exigir_admin)):
        return {"ok": u.email}

    def _sessao():
        yield sessao_teste

    mini.dependency_overrides[get_session] = _sessao
    c = TestClient(mini)
    leitor = {"Authorization": f"Bearer {criar_token(usuarios['leitor'].id)}"}
    admin = {"Authorization": f"Bearer {criar_token(usuarios['admin'].id)}"}
    assert c.get("/so-admin", headers=leitor).status_code == 403
    assert c.get("/so-admin", headers=admin).json() == {"ok": ADMIN[0]}
