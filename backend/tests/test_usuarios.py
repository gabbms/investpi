"""Cadastro de usuários pelo administrador (spec §8)."""
from tests.conftest import ADMIN


def criar(cliente, h, **dados):
    corpo = {"email": "novo@teste.local", "nome": "Nova Pessoa", "senha": "Senha-Nova-1", "perfil": "leitor"}
    corpo.update(dados)
    return cliente.post("/api/usuarios", json=corpo, headers=h)


def login(cliente, email, senha):
    return cliente.post("/api/auth/login", json={"email": email, "senha": senha})


def test_criar_leitor_e_entrar(cliente, h_admin):
    r = criar(cliente, h_admin)
    assert r.status_code == 201, r.text
    corpo = r.json()
    assert corpo["perfil"] == "leitor" and corpo["ativo"] is True
    assert "senha_hash" not in corpo and "senha" not in corpo
    assert login(cliente, "novo@teste.local", "Senha-Nova-1").status_code == 200


def test_listar_sem_hash(cliente, h_admin):
    lista = cliente.get("/api/usuarios", headers=h_admin).json()
    assert {u["email"] for u in lista} >= {ADMIN[0]}
    assert all("senha_hash" not in u for u in lista)


def test_email_duplicado(cliente, h_admin):
    assert criar(cliente, h_admin).status_code == 201
    assert criar(cliente, h_admin, email="NOVO@teste.local").status_code == 409


def test_senha_curta(cliente, h_admin):
    assert criar(cliente, h_admin, senha="123").status_code == 422


def test_perfil_invalido(cliente, h_admin):
    assert criar(cliente, h_admin, perfil="dono").status_code == 422


def test_leitor_nao_gerencia(cliente, h_leitor, usuarios):
    assert cliente.get("/api/usuarios", headers=h_leitor).status_code == 403
    assert criar(cliente, h_leitor).status_code == 403
    assert cliente.patch(f"/api/usuarios/{usuarios['leitor'].id}", json={"perfil": "admin"},
                         headers=h_leitor).status_code == 403


def test_admin_nao_se_desativa_nem_se_rebaixa(cliente, h_admin, usuarios):
    eu = usuarios["admin"].id
    assert cliente.patch(f"/api/usuarios/{eu}", json={"ativo": False}, headers=h_admin).status_code == 400
    assert cliente.patch(f"/api/usuarios/{eu}", json={"perfil": "leitor"}, headers=h_admin).status_code == 400


def test_desativar_e_redefinir_senha(cliente, h_admin, usuarios):
    leitor = usuarios["leitor"].id
    r = cliente.patch(f"/api/usuarios/{leitor}", json={"ativo": False}, headers=h_admin)
    assert r.status_code == 200 and r.json()["ativo"] is False
    assert login(cliente, "leitor@teste.local", "Senha-Leitor-1").status_code == 401

    r = cliente.patch(f"/api/usuarios/{leitor}", json={"ativo": True, "senha": "Outra-Senha-2", "nome": "Renomeado"},
                      headers=h_admin)
    assert r.json()["nome"] == "Renomeado"
    assert login(cliente, "leitor@teste.local", "Senha-Leitor-1").status_code == 401
    assert login(cliente, "leitor@teste.local", "Outra-Senha-2").status_code == 200


def test_promover_a_admin(cliente, h_admin, usuarios):
    r = cliente.patch(f"/api/usuarios/{usuarios['leitor'].id}", json={"perfil": "admin"}, headers=h_admin)
    assert r.json()["perfil"] == "admin"


def test_usuario_inexistente(cliente, h_admin):
    assert cliente.patch("/api/usuarios/9999", json={"nome": "x"}, headers=h_admin).status_code == 404


def test_senha_longa_demais_e_recusada_sem_erro_interno(cliente, h_admin, usuarios):
    longa = "á" * 40  # 80 bytes em UTF-8: acima do limite de 72 bytes do bcrypt
    assert criar(cliente, h_admin, senha=longa).status_code == 422
    r = cliente.patch(f"/api/usuarios/{usuarios['leitor'].id}", json={"senha": longa}, headers=h_admin)
    assert r.status_code == 422
