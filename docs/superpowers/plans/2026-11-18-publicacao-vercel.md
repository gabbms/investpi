# Publicação na Vercel + Neon — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the whole panel (React screens + FastAPI API) at a free `https://<nome>.vercel.app` link backed by a free Neon Postgres, auto-deployed on every merge to `main`.

**Architecture:** One Vercel project at the repo root. Vercel builds `frontend/` into static files; `api/index.py` exposes the existing FastAPI `app` as a Python function; `vercel.json` routes `/api/*` to it and every other path to `index.html`. The database URL Neon provides is normalized to the project's psycopg driver in `config.py`.

**Tech Stack:** Vercel (static + Python runtime), Neon Postgres (Vercel Marketplace integration), FastAPI, SQLAlchemy 2 + psycopg 3, Vite/React.

**Spec:** `docs/superpowers/specs/2026-11-18-publicacao-vercel-design.md`

## Global Constraints

- Local run (Docker on port 5433 + `uvicorn` + `npm run dev`) and the test suite keep working unchanged; tests never touch Neon.
- The README demo passwords (`Admin@2026`, `Leitor@2026`) must NOT work on the published site.
- Production secrets (`ADMIN_SENHA`, `LEITOR_SENHA`, `JWT_SEGREDO`) live only in Vercel environment variables and are handed to the user in chat — never committed.
- Logins keep the e-mails `admin@asg.local` and `leitor@asg.local`.
- Interface copy stays in Portuguese (pt-BR).
- Free tier only: no paid Vercel or Neon features.

## Review Focus

1. Reloading or opening a deep link (`/indicadores`, `/setor/mineracao`) on the published site must show the page, not a Vercel 404 — Task 24 Step 4.
2. Neon URLs carry query parameters (`?sslmode=require&channel_binding=require`); normalization must keep them — Task 22 test `test_url_neon_mantem_parametros`.
3. Uploading `base_modelo.xlsx` as admin must finish within the function time limit — Task 24 Step 5.
4. "Baixar planilha modelo" reads `backend/dados/base_modelo.xlsx` from disk; the file must ship inside the function — Task 22 `includeFiles` + Task 24 Step 5.
5. Logging in online with a README demo password must fail with "E-mail ou senha incorretos" — Task 24 Step 4.

---

### Task 22: Vercel entry point, routing and database URL

**Files:**
- Create: `api/index.py`, `vercel.json`, `requirements.txt` (repo root)
- Modify: `backend/requirements.txt`, `backend/app/config.py`
- Test: `backend/tests/test_publicacao.py`

**Interfaces:**
- Produces: `normalizar_url_banco(url: str) -> str` in `app/config.py`; `Settings.DATABASE_URL` passes through it (pydantic `field_validator`). `api/index.py` module exposes `app` (the FastAPI instance from `app.main`).

- [ ] **Step 1: Write the failing tests** in `backend/tests/test_publicacao.py`

```python
from app.config import normalizar_url_banco

def test_url_postgres_vira_psycopg():
    assert normalizar_url_banco("postgres://u:s@h/db") == "postgresql+psycopg://u:s@h/db"
    assert normalizar_url_banco("postgresql://u:s@h/db") == "postgresql+psycopg://u:s@h/db"

def test_url_local_nao_muda():
    url = "postgresql+psycopg://asg:asg@localhost:5433/asg"
    assert normalizar_url_banco(url) == url

def test_url_neon_mantem_parametros():
    url = "postgres://u:s@ep-x.neon.tech/neondb?sslmode=require&channel_binding=require"
    assert normalizar_url_banco(url) == "postgresql+psycopg://u:s@ep-x.neon.tech/neondb?sslmode=require&channel_binding=require"

def test_entrada_da_vercel_expoe_a_api():
    # loads <repo>/api/index.py by path (importlib.util.spec_from_file_location) and calls it with TestClient
    assert TestClient(entrada.app).get("/api/saude").json() == {"ok": True}

def test_vercel_json_rotas():
    # parses <repo>/vercel.json
    assert {"source": "/api/(.*)", "destination": "/api/index"} == cfg["rewrites"][0]
    assert cfg["rewrites"][-1]["destination"] == "/index.html"
    assert "backend/**" in cfg["functions"]["api/index.py"]["includeFiles"]
    assert cfg["outputDirectory"] == "frontend/dist"
```

- [ ] **Step 2: Run** `backend\.venv\Scripts\python -m pytest backend/tests/test_publicacao.py -v`. Expected: FAIL (ImportError on `normalizar_url_banco`).

- [ ] **Step 3: Implement.**
  - `normalizar_url_banco`: replace only the scheme prefix `postgres://` or `postgresql://` with `postgresql+psycopg://`; everything else unchanged.
  - `api/index.py`: insert `<repo>/backend` at the front of `sys.path`, then `from app.main import app`.
  - `vercel.json`: `"buildCommand": "cd frontend && npm ci && npm run build"`, `"outputDirectory": "frontend/dist"`, `"functions": {"api/index.py": {"maxDuration": 60, "includeFiles": "backend/**"}}`, rewrites `/api/(.*)` → `/api/index`, then `/(.*)` → `/index.html`.
  - Root `requirements.txt`: the runtime packages now in `backend/requirements.txt` (everything except `pytest` and `httpx`). `backend/requirements.txt` becomes `-r ../requirements.txt` plus `pytest` and `httpx`.

- [ ] **Step 4: Run** the Step 2 command, then the full suite `cd backend && .venv\Scripts\python -m pytest -q`, then `cd frontend && npx vitest run && npm run build`. Expected: all PASS, no TS errors. Also `.venv\Scripts\pip install -r requirements.txt` in `backend/` still resolves (proves the `-r` include works).

- [ ] **Step 5: Commit** — `git commit -m "feat: Vercel entry point, routing and Neon database URL"`

---

### Task 23: README "Site publicado"

**Files:**
- Modify: `README.md`

- [ ] **Step 1:** Add a section **"Site publicado"** right after the run instructions: the link (placeholder `https://<nome>.vercel.app` until Task 24 fills it), that every merge to `main` republishes it, that the published logins use the same e-mails but **other passwords** (ask the administrator), and a short "Como publicar do zero" list mirroring Task 24 Steps 1–3. Next to the demo-users table, one line: "Valem só no computador local."
- [ ] **Step 2:** Commit — `git commit -m "docs: published site section in the README"`. Open the PR, merge to `main` once the user approves.

---

### Task 24: Publish and check (with the user)

Steps marked **(usuário)** need the user's accounts; Claude writes the exact clicks in chat.

- [ ] **Step 1 (usuário):** On vercel.com, sign up with GitHub, "Add New → Project", import `gabbms/investpi`, root directory = repo root, keep the build settings from `vercel.json`. Do not deploy yet if Vercel allows; otherwise the first deploy may fail for lack of a database. That is expected.
- [ ] **Step 2 (usuário):** In the project, Storage → "Create / Connect Database" → Neon (free plan) → connect it to all environments. Confirm `DATABASE_URL` appears under Settings → Environment Variables.
- [ ] **Step 3:** Claude generates `JWT_SEGREDO` (48 random bytes, URL-safe), `ADMIN_SENHA` and `LEITOR_SENHA` (16 random chars each, letters+digits+one symbol); the user adds them plus `ADMIN_EMAIL=admin@asg.local`, `LEITOR_EMAIL=leitor@asg.local`, `JWT_HORAS=8` in Vercel, then redeploys. Claude runs the one-time load from the notebook with the Neon URL and the same e-mails and passwords in the shell environment (never in `.env`): `cd backend && .venv\Scripts\python -m app.cli inicializar`. Expected: "Usuários criados: 2 · Versões importadas: 1". Running it again reports 0 and 0.
- [ ] **Step 4: Check in the browser** (Opera test profile, as earlier): opening `/` redirects to login; the README password `Leitor@2026` → "E-mail ou senha incorretos"; the new reader password → Visão Geral shows R$ 42,8 bi, 48 projetos and Índice 68; filter Mineração → 12 projetos; a direct visit to `/indicadores` and a reload of it show the page; Exportar Excel downloads.
- [ ] **Step 5: Check as admin:** "Baixar planilha modelo" downloads; uploading `backend/dados/base_modelo.xlsx` shows the preview with 0 errors and 12 OK, and confirming creates version 2 in under the time limit; Histórico de versões lists versions 1 and 2. Then reactivate version 1, so the site is left as delivered.
- [ ] **Step 6:** Put the real link in the README (Task 23 placeholder), commit `docs: published site link`, merge. Give the user the link and both passwords in chat.

## Final check

- Full backend suite and `npx vitest run` / `npm run build` green.
- Local run still works: `/api/saude` on :8000 and Visão Geral 68 on :5173.
- Published site passes Task 24 Steps 4–5.
