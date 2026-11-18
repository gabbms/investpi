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
