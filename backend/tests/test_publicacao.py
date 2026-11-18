"""Publicação na Vercel: entrada da função, rotas e endereço do banco da Neon."""
import importlib.util
import json

from fastapi.testclient import TestClient

from app.config import RAIZ_PROJETO, normalizar_url_banco


def test_url_postgres_vira_psycopg():
    assert normalizar_url_banco("postgres://u:s@h/db") == "postgresql+psycopg://u:s@h/db"
    assert normalizar_url_banco("postgresql://u:s@h/db") == "postgresql+psycopg://u:s@h/db"


def test_url_local_nao_muda():
    url = "postgresql+psycopg://asg:asg@localhost:5433/asg"
    assert normalizar_url_banco(url) == url


def test_url_neon_mantem_parametros():
    url = "postgres://u:s@ep-x.neon.tech/neondb?sslmode=require&channel_binding=require"
    assert normalizar_url_banco(url) == (
        "postgresql+psycopg://u:s@ep-x.neon.tech/neondb?sslmode=require&channel_binding=require"
    )


def test_entrada_da_vercel_expoe_a_api():
    spec = importlib.util.spec_from_file_location("entrada_vercel", RAIZ_PROJETO / "api" / "index.py")
    entrada = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(entrada)
    assert TestClient(entrada.app).get("/api/saude").json() == {"ok": True}


def test_vercel_json_rotas():
    cfg = json.loads((RAIZ_PROJETO / "vercel.json").read_text(encoding="utf-8"))
    assert cfg["rewrites"][0] == {"source": "/api/(.*)", "destination": "/api/index"}
    assert cfg["rewrites"][-1]["destination"] == "/index.html"
    assert "backend/**" in cfg["functions"]["api/index.py"]["includeFiles"]
    assert cfg["outputDirectory"] == "frontend/dist"


# --- Revisão final: proteções para o site publicado ---------------------------

import pytest  # noqa: E402

from app import cli  # noqa: E402
from app.config import SEGREDO_PADRAO, Settings, validar_producao  # noqa: E402
from app.db import argumentos_engine  # noqa: E402


def _cfg(**kw) -> Settings:
    return Settings(_env_file=None, **kw)


def test_producao_recusa_segredo_padrao():
    with pytest.raises(RuntimeError, match="JWT_SEGREDO"):
        validar_producao(_cfg(), {"VERCEL": "1"})


def test_producao_recusa_segredo_curto():
    with pytest.raises(RuntimeError, match="JWT_SEGREDO"):
        validar_producao(_cfg(JWT_SEGREDO="curto"), {"VERCEL": "1"})


def test_producao_aceita_segredo_longo_e_local_aceita_padrao():
    validar_producao(_cfg(JWT_SEGREDO="x" * 40), {"VERCEL": "1"})
    validar_producao(_cfg(), {})  # fora da Vercel, o padrão continua valendo
    assert _cfg().JWT_SEGREDO == SEGREDO_PADRAO


def test_carga_na_nuvem_recusa_senha_de_demonstracao():
    nuvem = "postgres://u:s@ep-x.neon.tech/neondb?sslmode=require"
    with pytest.raises(SystemExit, match="LEITOR_SENHA"):
        cli.checar_destino(_cfg(DATABASE_URL=nuvem, ADMIN_SENHA="Forte#2026xyzAB", LEITOR_SENHA="Leitor@2026"))
    with pytest.raises(SystemExit, match="ADMIN_SENHA"):
        cli.checar_destino(_cfg(DATABASE_URL=nuvem, ADMIN_SENHA="Admin@2026", LEITOR_SENHA="Outra#2026xyzAB"))


def test_carga_local_aceita_senha_de_demonstracao():
    cli.checar_destino(_cfg(ADMIN_SENHA="Admin@2026", LEITOR_SENHA="Leitor@2026"))
    nuvem = "postgres://u:s@ep-x.neon.tech/neondb"
    cli.checar_destino(_cfg(DATABASE_URL=nuvem, ADMIN_SENHA="Forte#2026xyzAB", LEITOR_SENHA="Outra#2026xyzAB"))


def test_engine_sem_prepared_statements():
    args = argumentos_engine()
    assert args["pool_pre_ping"] is True
    assert args["connect_args"] == {"prepare_threshold": None}


def test_vercel_json_exclui_o_que_a_api_nao_usa():
    cfg = json.loads((RAIZ_PROJETO / "vercel.json").read_text(encoding="utf-8"))
    excl = cfg["functions"]["api/index.py"]["excludeFiles"]
    for pasta in ("frontend/**", "docs/**", "backend/tests/**"):
        assert pasta in excl
    assert cfg["framework"] is None
