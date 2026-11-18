"""Carga inicial idempotente (spec §7 e §8)."""
from sqlalchemy import select

from app import cli, repositorio
from app.auth import verificar_senha
from app.config import settings
from app.models import Usuario


def test_inicializar_idempotente(sessao_teste):
    criados = cli.inicializar(sessao_teste)
    assert criados == {"usuarios": 2, "versao": 1}
    usuarios = {u.email: u for u in sessao_teste.scalars(select(Usuario))}
    assert usuarios[settings.ADMIN_EMAIL].perfil == "admin"
    assert usuarios[settings.LEITOR_EMAIL].perfil == "leitor"
    assert verificar_senha(settings.ADMIN_SENHA, usuarios[settings.ADMIN_EMAIL].senha_hash)
    assert usuarios[settings.ADMIN_EMAIL].senha_hash != settings.ADMIN_SENHA

    assert cli.inicializar(sessao_teste) == {"usuarios": 0, "versao": 0}
    assert [v.numero for v in repositorio.listar_versoes(sessao_teste)] == [1]
