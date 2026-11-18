# Sistema ASG Web — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A web version of the Grupo 3 ASG dashboard: an admin uploads the Excel base, the system validates and stores it as a version, and logged-in users see the same numbers as the Power BI v3, with filters, cards and charts.

**Architecture:** FastAPI backend reads the workbook with pandas, validates it, stores each sheet row as JSONB in PostgreSQL under a `versao` (one transaction per upload), and computes every measure in pure-Python modules over a `Base = dict[str, pd.DataFrame]`. Each dashboard page is one endpoint returning a generic payload (cards, charts, tables); the React frontend renders any payload with one generic page component.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2, psycopg 3, pandas, openpyxl, bcrypt, PyJWT, pytest · React 18 + Vite + TypeScript, react-router-dom, echarts + echarts-for-react · PostgreSQL 17 in Docker.

**Spec:** `docs/superpowers/specs/2026-11-17-sistema-asg-web-design.md` (read it first; section numbers below refer to it).

## Global Constraints

- Project root: `C:\Users\Gabriel\Desktop\investepi\SistemaWeb` (all paths below are relative to it). Git repository.
- PostgreSQL runs in Docker on host port **5433** (5432 is taken by the machine's own PostgreSQL). Never use the machine's own PostgreSQL install.
- API on `http://localhost:8000`, frontend on `http://localhost:5173` (Vite proxies `/api` to 8000).
- Python virtualenv at `backend/.venv`; run Python with that interpreter.
- Source of truth for every number: the DAX measures in `C:\Users\Gabriel\Desktop\investepi\PowerBI\Painel_ASG_v3\Painel_ASG_Investe_PI_v3.SemanticModel\definition\tables\_Medidas.tmdl`. A measure here is named exactly as its DAX measure name (e.g. `"% Licença Válida"`), and that name is also the card `id`.
- Reference workbook: `C:\Users\Gabriel\Desktop\investepi\PowerBI\Base_ASG_Grupo3_PowerBI.xlsx`. Copy it to `backend/dados/base_modelo.xlsx` in Task 1; tests and seed use the copy.
- UI text in Brazilian Portuguese; numbers formatted pt-BR in the frontend (API returns raw numbers).
- Colors: Ambiental `#1B8A4C`, Social `#D9730D`, Governança `#0B3D91`, Metas `#5B2C83`, Visão Geral `#4B5563`; semáforo verde `#1B8A4C`, amarelo `#E0A100`, vermelho `#C62828`.
- Session token expires after 8 hours. Passwords hashed with bcrypt. Only admins upload, activate versions, manage users.
- Demo credentials live only in `.env.example` and README (`ADMIN_EMAIL=admin@asg.local`, `ADMIN_SENHA=Admin@2026`, `LEITOR_EMAIL=leitor@asg.local`, `LEITOR_SENHA=Leitor@2026`), never hard-coded.
- Build order follows spec §2 "Prioridade de construção": Tasks 1–8 are priority 1; 9 is priority 2; 10 is priority 3; 11 is priority 4.

## Review Focus

1. **Excel rows that look empty** (formatting left on blank rows after the last record) — fully empty rows are dropped before validation, so they never count as "chave vazia". Test in Task 2.
2. **"Sim/Não" written differently** (`"sim"`, `" SIM "`) — normalized by trim + case-insensitive before any count. Test in Task 2.
3. **A filter combination with zero projects** — every page still returns 200; ratios with zero denominator return `null`, sums return 0; the frontend shows "—". Test in Task 4 and Task 9.
4. **A file that is not a valid .xlsx** (renamed .csv, corrupted) — 400 with a Portuguese message; the active version is untouched. Test in Task 7.
5. **Expired or missing token while a page is open** — API answers 401 and the frontend returns to the login screen instead of a blank page. Test in Task 7 (API) and checked manually in Task 8.

---

### Task 1: Repository, Docker database and backend skeleton

**Files:**
- Create: `.gitignore`, `docker-compose.yml`, `.env.example`, `backend/requirements.txt`, `backend/app/__init__.py`, `backend/app/config.py`, `backend/app/db.py`, `backend/app/models.py`, `backend/app/main.py`, `backend/tests/conftest.py`, `backend/tests/test_saude.py`, `backend/dados/base_modelo.xlsx` (copy)

**Interfaces:**
- Produces: `config.settings` (pydantic-settings, reads `.env` at repo root) with `DATABASE_URL`, `JWT_SEGREDO`, `JWT_HORAS=8`, `ADMIN_EMAIL`, `ADMIN_SENHA`, `LEITOR_EMAIL`, `LEITOR_SENHA`, `CAMINHO_MODELO="dados/base_modelo.xlsx"`.
- Produces: `db.engine`, `db.SessionLocal`, `db.Base`, `db.get_session()` (FastAPI dependency yielding a session).
- Produces models: `Usuario(id, email unique, nome, senha_hash, perfil in {"admin","leitor"}, ativo bool, criado_em)`; `Versao(id, numero int unique, criado_em, enviado_por_id FK usuario nullable, nome_arquivo, status in {"ativa","inativa","rejeitada"}, linhas_por_aba JSONB, avisos JSONB, erros JSONB)`; `LinhaDado(id, versao_id FK, aba str indexed, dados JSONB)`.
- Produces: `GET /api/saude -> {"ok": true}`.

- [ ] **Step 1:** `git init`; `.gitignore` ignores `.env`, `backend/.venv`, `__pycache__`, `node_modules`, `frontend/dist`. `docker-compose.yml`: service `db` image `postgres:17`, env `POSTGRES_USER=asg`, `POSTGRES_PASSWORD=asg`, `POSTGRES_DB=asg`, port `5433:5432`, named volume, and an init SQL that also creates database `asg_test`. `.env.example` with `DATABASE_URL=postgresql+psycopg://asg:asg@localhost:5433/asg`, `TEST_DATABASE_URL=postgresql+psycopg://asg:asg@localhost:5433/asg_test`, `JWT_SEGREDO=troque-este-segredo`, and the demo credentials from Global Constraints. Copy `.env.example` to `.env`.
- [ ] **Step 2:** `docker compose up -d db`; expected: `docker compose ps` shows `db` healthy/running.
- [ ] **Step 3:** Create venv, `requirements.txt` (fastapi, uvicorn[standard], sqlalchemy>=2, psycopg[binary], pandas, openpyxl, bcrypt, pyjwt, python-multipart, pydantic-settings, pytest, httpx), install.
- [ ] **Step 4: Failing test** `tests/test_saude.py::test_saude` — `TestClient(app).get("/api/saude").json() == {"ok": True}`. `conftest.py` provides fixture `sessao_teste` that creates all tables on `TEST_DATABASE_URL`, yields a session, drops tables after; and fixture `cliente` overriding `get_session`.
- [ ] **Step 5:** Implement config, db, models, `main.py` (app, CORS for 5173, router include point, `/api/saude`). Run `pytest -q` → PASS.
- [ ] **Step 6:** Commit `chore: project skeleton, docker db, models` (include the spec and this plan).

---

### Task 2: Workbook schema, reading and structural validation

**Files:**
- Create: `backend/app/planilha/esquema.py`, `backend/app/planilha/leitura.py`, `backend/app/planilha/validacao.py`
- Test: `backend/tests/test_planilha.py`

**Interfaces:**
- Produces: `esquema.ABAS: dict[str, EspecAba]` with `EspecAba(colunas: list[str], chave: str | None, obrigatoria: bool, tipos: dict[str, Literal["texto","numero","inteiro","data","simnao"]], referencias: dict[str, tuple[str, str]])`. Required sheets and their columns = spec §6 (copy the headers exactly from the reference workbook; `dIndicador` optional). Keys per spec §6 table (`fAmbiental`, `fSocial`, `fTransparencia`, `fEnergia`, `fHidrogenio`, `fMineracao`, `fSustentabilidade` keyed by `Código Projeto`). References: every f* `Código Projeto` → `dProjeto.Código Projeto`; `dProjeto.Código Empresa` → `dEmpresa.Código Empresa`; `dProjeto.Setor Investe` → `dSetor.Setor Investe`.
- Produces: `esquema.MEDIDAS_META: frozenset[str]` = the 24 `dMetas.Medida` values of the reference workbook.
- Produces: `leitura.ler_planilha(conteudo: bytes) -> Base` where `Base = dict[str, pd.DataFrame]` (only sheets in `ABAS`; header row 1; fully empty rows dropped; text trimmed; "Sim/Não" columns normalized to exactly `"Sim"`/`"Não"`). Raises `PlanilhaInvalida(mensagem: str)` if bytes are not a readable xlsx.
- Produces: `validacao.validar_estrutura(base: Base) -> list[ErroEstrutura]`, `ErroEstrutura(aba: str, linha: int | None, coluna: str | None, mensagem: str)`; checks: missing required sheet, missing column, type mismatch, empty/duplicate key, broken reference, `dMetas.Medida` not in `MEDIDAS_META`.

- [ ] **Step 1: Failing tests** in `test_planilha.py` (build mutated workbooks in-memory with openpyxl from `dados/base_modelo.xlsx`):
  - `test_base_modelo_valida`: `validar_estrutura(ler_planilha(base)) == []`; row counts `dProjeto 48, fFinanceiro 432, fContratos 60, fEquipe 62, dMetas 24`.
  - `test_aba_obrigatoria_ausente`: delete `fSocial` → one error with `aba == "fSocial"`.
  - `test_coluna_ausente`: delete column `Licença Válida` in `fAmbiental` → error naming that column.
  - `test_chave_repetida`: duplicate a `dProjeto` row → error `aba == "dProjeto"`.
  - `test_referencia_inexistente`: set a `fAmbiental` `Código Projeto` to `"PROJ999"` → error.
  - `test_medida_meta_desconhecida`: set a `dMetas.Medida` to `"Medida Inventada"` → error.
  - `test_texto_em_coluna_numerica`: `dProjeto.Investimento Previsto = "abc"` → error.
  - `test_linhas_vazias_ignoradas` (Review Focus 1): append 5 rows with only cell formatting → no error, 48 projects.
  - `test_simnao_normalizado` (Review Focus 2): write `" sim "` and `"NÃO"` into `fAmbiental.Licença Válida` → read back as `"Sim"`/`"Não"`.
  - `test_arquivo_nao_xlsx`: `ler_planilha(b"a,b\n1,2")` raises `PlanilhaInvalida`.
- [ ] **Step 2:** Run `pytest tests/test_planilha.py -q` → FAIL (module missing).
- [ ] **Step 3:** Implement the three modules.
- [ ] **Step 4:** Run → PASS. Commit `feat: workbook schema, reading and structural validation`.

---

### Task 3: Quality checks C01–C12

**Files:**
- Create: `backend/app/calculos/checagens.py`
- Test: `backend/tests/test_checagens.py`

**Interfaces:**
- Consumes: `Base`.
- Produces: `rodar_checagens(base: Base) -> list[ResultadoChecagem]`, `ResultadoChecagem(id: str, checagem: str, tabela: str, regra: str, problemas: int)`, ids `C01`…`C12` with the texts of sheet `dChecagens` (spec §7). Rules = DAX measure `Problemas Checagem` in `_Medidas.tmdl` (C09: `Pago > Liquidado or Liquidado > Empenhado` per row; C10: blank Município, Status Projeto, Investimento Previsto or Custo Manutenção Anual).

- [ ] **Step 1: Failing tests:** `test_base_sem_problemas` (all 12 have `problemas == 0`); one mutation test per check proving it counts (e.g. C07: set one `Investimento Realizado` above `Investimento Previsto` → C07 == 1; C09: one row Pago > Empenhado → 1; C11: `% Renovável Eletrolisador = 1.2` → 1; C12: `Data Fim` before `Data Início` → 1; C03: drop one `fAmbiental` row → 1).
- [ ] **Step 2:** Run → FAIL. **Step 3:** implement. **Step 4:** Run → PASS. Commit `feat: quality checks C01-C12`.

---

### Task 4: Filters, measures, goals and ASG index (Visão Geral)

**Files:**
- Create: `backend/app/calculos/filtros.py`, `backend/app/calculos/medidas.py`, `backend/app/calculos/metas.py`
- Test: `backend/tests/test_calculos.py`

**Interfaces:**
- Produces: `Filtros(setores: list[str] = [], vps: list[str] = [], status: list[str] = [], municipios: list[str] = [])`; `aplicar_filtros(base: Base, f: Filtros) -> Base` — filters `dProjeto` (Setor Investe, Status Projeto, Município; VP via `dSetor`), then every f* to the remaining `Código Projeto`, and `dEmpresa` to the companies of remaining projects. Unfiltered tables (dMetas, dPremissas, dIndicador, dSetor) pass through.
- Produces: `medidas.calcular(base: Base, nome: str) -> float | None` — dispatch by DAX measure name; returns `None` where DAX would DIVIDE by zero. Must cover at least every measure used by any page in Tasks 7, 9, 11 and all 24 `MEDIDAS_META`. Financial rule (spec §9): `Orçamento Previsto` and `% Prestação de Contas Atualizada` use only the latest `Data Referência`.
- Produces: `metas.avaliar_metas(base: Base) -> list[ResultadoMeta]`, `ResultadoMeta(id_meta, pilar, indicador, medida, peso: int, valor: float | None, meta: float, limite: float, formato: str, polaridade: str, status: Literal["Atingida","Atenção","Abaixo"] | None, atingimento: float | None)`; `metas.indice_pilar(base, pilar: str) -> float | None`; `metas.indice_geral(base) -> float | None`; `metas.status_medida(base, medida: str) -> str | None` (status of the meta whose Medida is that name, else None). Rules = spec §9.
- Produces: `metas.cor_indice(valor) -> "verde"|"amarelo"|"vermelho"` (≥75, ≥50, else).

- [ ] **Step 1: Failing tests** with the reference workbook (fixture `base` read once per module), all values from spec §9:
  - `calcular(base,"Investimento Previsto") == pytest.approx(42_829_000_000)`; `"Qtd Projetos" == 48`; `"Empresas Confirmadas" == 17`; `"Empregos Diretos Gerados" == 7236`; `"Emissões Evitadas tCO2e" == pytest.approx(3_477_889, abs=1)`; `"% Contratos Fiscalizados" == pytest.approx(0.55)`; `"% Licença Válida" == pytest.approx(0.5417, abs=1e-4)`; `"% Execução Orçamentária" == pytest.approx(0.2482, abs=1e-4)`; `"Taxa Frequência Acidentes" == pytest.approx(2.119, abs=1e-3)`.
  - `round(indice_pilar(base,"Ambiental")) == 75`, `"Social" == 67`, `"Governança" == 62`, `round(indice_geral(base)) == 68`.
  - status counts from `avaliar_metas`: Atingida 6, Atenção 6, Abaixo 12.
  - `test_filtro_mineracao`: `aplicar_filtros(base, Filtros(setores=["Mineração"]))` → Qtd Projetos 12, Investimento Previsto ≈ 5_330_000_000 (abs 1e7).
  - `test_filtro_vazio` (Review Focus 3): `Filtros(municipios=["Inexistente"])` → Qtd Projetos 0, `% Licença Válida is None`, `indice_geral` is None, no exception.
- [ ] **Step 2:** Run → FAIL. **Step 3:** implement (port each needed DAX measure literally; `KEEPFILTERS(dProjeto[Setor Investe]="X")` = restrict to projects of sector X within the current filter). **Step 4:** Run → PASS. Commit `feat: filters, measures, goals and ASG index`.

---

### Task 5: Version storage and initial load command

**Files:**
- Create: `backend/app/repositorio.py`, `backend/app/cli.py`
- Test: `backend/tests/test_repositorio.py`

**Interfaces:**
- Consumes: `Base`, `rodar_checagens`, models.
- Produces: `salvar_versao(s: Session, base: Base, usuario_id: int | None, nome_arquivo: str, avisos: list[dict]) -> Versao` — one transaction: inserts `Versao(numero = max+1, status="ativa")`, all `LinhaDado` rows (dates as ISO strings, NaN as null), sets the previous active version to `"inativa"`. `carregar_base_ativa(s) -> Base | None` (rebuilds DataFrames with the schema dtypes; cached in-process by version id). `ativar_versao(s, versao_id) -> Versao`. `listar_versoes(s) -> list[Versao]` newest first. `registrar_rejeicao(s, nome_arquivo, usuario_id, erros) -> Versao` (status `"rejeitada"`, no rows).
- Produces CLI: `python -m app.cli inicializar` — creates tables, creates admin and leitor from settings if absent, imports `CAMINHO_MODELO` as version 1 if no version exists. Idempotent.

- [ ] **Step 1: Failing tests:** `test_salvar_e_carregar` (save reference base, load, `calcular(...,"Investimento Previsto")` unchanged and row counts equal); `test_nova_versao_desativa_anterior` (two saves → only numero 2 ativa); `test_ativar_versao_anterior`; `test_falha_no_meio_nao_grava` (monkeypatch to raise after half the rows → no new Versao, previous still ativa); `test_rejeicao_nao_muda_ativa`.
- [ ] **Step 2:** Run → FAIL. **Step 3:** implement. **Step 4:** Run → PASS. Run `python -m app.cli inicializar` twice → second run reports nothing created. Commit `feat: versioned storage and initial load`.

---

### Task 6: Authentication and permissions

**Files:**
- Create: `backend/app/auth.py`, `backend/app/api/auth.py`
- Test: `backend/tests/test_auth.py`

**Interfaces:**
- Produces: `hash_senha(s) -> str`, `verificar_senha(s, h) -> bool`, `criar_token(usuario_id: int) -> str` (JWT HS256, exp = `JWT_HORAS`), dependencies `usuario_atual` (401 if missing/invalid/expired token or inactive user) and `exigir_admin` (403 if perfil != admin).
- Produces: `POST /api/auth/login {email, senha} -> {token, usuario: {id, email, nome, perfil}}` (401 on wrong credentials, same message for unknown email and wrong password); `GET /api/auth/eu -> usuario`.

- [ ] **Step 1: Failing tests:** login ok returns token; wrong password 401; inactive user 401; `GET /api/auth/eu` without token 401; with expired token (create with negative hours) 401 (Review Focus 5); `exigir_admin` on a leitor → 403 (via a tiny test route or Task 7 routes).
- [ ] **Step 2–4:** FAIL → implement → PASS. Commit `feat: login, JWT and roles`.

---

### Task 7: API — upload, versions, template, filter options, Visão Geral page

**Files:**
- Create: `backend/app/api/importacao.py`, `backend/app/api/versoes.py`, `backend/app/api/painel.py`, `backend/app/paginas/__init__.py`, `backend/app/paginas/tipos.py`, `backend/app/paginas/visao_geral.py`
- Test: `backend/tests/test_api.py`

**Interfaces:**
- Produces payload types in `paginas/tipos.py` (pydantic): `Card(id: str, titulo: str, valor: float | None, formato: Literal["brl","num","pct","dec","idx"], status: Literal["verde","amarelo","vermelho"] | None, ajuda: str | None)`; `Serie(nome: str, valores: list[float | None], cor: str | None)`; `Grafico(id, titulo, tipo: Literal["barra_h","barra_h_empilhada","colunas","rosca"], categorias: list[str], series: list[Serie], formato)`; `Coluna(chave, rotulo, formato: Literal["texto","brl","num","pct","dec","status"])`; `Tabela(id, titulo, colunas: list[Coluna], linhas: list[dict])`; `Pagina(titulo, subtitulo, indice: Card | None, cards: list[Card], graficos: list[Grafico], tabelas: list[Tabela])`.
- Card rule: `status` = `metas.status_medida` mapped Atingida→verde, Atenção→amarelo, Abaixo→vermelho; for index cards use `cor_indice`. `ajuda` = `dIndicador` Descrição + Cálculo for that `Medida DAX` (+ " Meta: ≥/≤ X" when it has a meta); None if dIndicador absent.
- Produces endpoints (all require `usuario_atual`; marked ones `exigir_admin`):
  - `POST /api/importacao/previa` (admin, multipart `arquivo`) → `{linhas_por_aba, erros: [ErroEstrutura], checagens: [ResultadoChecagem], pode_confirmar: bool}`; 400 `{"detail": "Arquivo não é uma planilha .xlsx válida"}` on `PlanilhaInvalida`.
  - `POST /api/importacao/confirmar` (admin, same multipart; re-reads and re-validates) → 201 `{versao}`; 422 with erros if structural errors (also `registrar_rejeicao`).
  - `GET /api/importacao/modelo` → the template xlsx download.
  - `GET /api/versoes` (admin) → list; `POST /api/versoes/{id}/ativar` (admin).
  - `GET /api/painel/opcoes` → `{setores, vps, status, municipios}` from the active version.
  - `GET /api/painel/visao-geral?setor=..&vp=..&status=..&municipio=..` (each repeatable) → `Pagina`. 409 `{"detail": "Nenhuma versão de dados carregada"}` if none.
- Visão Geral content = spec §10 row "Visão Geral": cards `Investimento Previsto`(brl), `Qtd Projetos`(num), `Empresas Confirmadas`(num), `Empregos Diretos Gerados`(num), `Emissões Evitadas tCO2e`(num), index card `Índice ASG Geral`(idx); charts: investimento por setor (barra_h), investimento por município empilhado por setor sorted by total desc (barra_h_empilhada, one Serie per sector with the sector color), índice por pilar e setor (colunas, 3 series with pillar colors), projetos por status (rosca).

- [ ] **Step 1: Failing tests** (`cliente` + users created in fixture, reference base saved as active version):
  - `test_leitor_nao_envia`: leitor POST previa → 403; leitor POST ativar → 403.
  - `test_previa_base_valida`: admin → `pode_confirmar is True`, `erros == []`, 12 checagens all 0.
  - `test_confirmar_cria_versao`: → 201, `GET /api/versoes` first item numero 2 status ativa.
  - `test_confirmar_com_erro_nao_muda_ativa`: workbook without `fSocial` → 422; active version still numero 1.
  - `test_arquivo_invalido` (Review Focus 4): upload bytes `b"x"` named `a.xlsx` → 400 with the Portuguese detail.
  - `test_visao_geral_valores`: cards by id match spec §9 values; index card `valor` rounds to 68 with `status == "amarelo"`.
  - `test_visao_geral_filtro_mineracao`: `?setor=Mineração` → Qtd Projetos 12.
  - `test_sem_token` → 401.
- [ ] **Step 2–4:** FAIL → implement → PASS. Commit `feat: upload, versions and Visão Geral API`.

---

### Task 8: Frontend foundation — login, shell, filters, generic page, Visão Geral, upload

**Files:**
- Create: `frontend/` (Vite React TS), `frontend/vite.config.ts` (proxy `/api` → 8000), `src/api.ts`, `src/auth.tsx`, `src/filtros.tsx`, `src/format.ts`, `src/layout/Shell.tsx`, `src/components/{CardKpi,Grafico,Tabela,PaginaPainel}.tsx`, `src/pages/{Login,VisaoGeral,Envio}.tsx`, `src/App.tsx`, `src/estilo.css`, `.claude/launch.json` (configs `api`: `backend/.venv/Scripts/python -m uvicorn app.main:app --port 8000` in `backend`; `web`: `npm run dev` in `frontend`, port 5173)
- Test: `frontend/src/format.test.ts` (vitest)

**Interfaces:**
- Consumes: endpoints of Tasks 6–7 and the payload types (mirror them in `src/api.ts` as TS types).
- Produces: `api.get<T>(path, params?)`, `api.post`, `api.upload(path, file)` — attach `Authorization: Bearer`, on 401 clear token and navigate to `/login` (Review Focus 5); `useAuth()` → `{usuario, entrar(email, senha), sair()}`; `<RequireAuth>`, `<RequireAdmin>`; `useFiltros()` → `{filtros, setFiltros, query}` shared across pages (state kept in URL search params); `<PaginaPainel endpoint="/api/painel/visao-geral" />` fetches with current filters and renders `indice`, cards grid, charts grid, tables; `format.valor(v: number | null, formato) -> string`.
- Routes: `/login`, `/` (Visão Geral), `/admin/envio`. Shell: sidebar with menu items in the spec colors (items for pages built later may be present but disabled until their task), top filter bar (4 multi-selects from `/api/painel/opcoes`), user name + "Sair".

- [ ] **Step 1: Failing test** `format.test.ts`: `valor(42829000000,"brl") === "R$ 42,8 bi"`, `valor(5330000000,"brl") === "R$ 5,3 bi"`, `valor(283000000,"brl") === "R$ 283 mi"`, `valor(0.5417,"pct") === "54,2%"`, `valor(7236,"num") === "7.236"`, `valor(2.119,"dec") === "2,12"`, `valor(67.9,"idx") === "68"`, `valor(null,"pct") === "—"`.
- [ ] **Step 2:** `npx vitest run` → FAIL. **Step 3:** implement everything in Files. Card: big value, title, colored value per `status`, "?" icon showing `ajuda` on hover. Grafico: ECharts with pt-BR axis labels via `format.valor`. Envio page: choose file → `previa` → show linhas por aba, erros (blocking, red) and checagens (OK green / Verificar red) → "Confirmar envio" enabled only if `pode_confirmar` → `confirmar` → success message; link "Baixar planilha modelo".
- [ ] **Step 4:** `npx vitest run` → PASS; `npm run build` → no TS errors.
- [ ] **Step 5: Manual check** (start both via `.claude/launch.json` with the browser preview tools): log in as leitor → Visão Geral shows R$ 42,8 bi, 48, 17, 7.236, Índice 68 amarelo; filter Setor = Mineração → 12 projetos; leitor has no Envio menu and `/admin/envio` redirects. Log in as admin → upload the reference workbook → preview shows 0 errors, 12 OK → confirm → Visão Geral unchanged. Delete the token in localStorage while on a page and click a filter → back to login.
- [ ] **Step 6:** Commit `feat: frontend foundation, Visão Geral and upload`. **Priority 1 complete.**

---

### Task 9: Ambiental, Social, Governança and Metas ASG pages

**Files:**
- Create: `backend/app/paginas/{ambiental,social,governanca,metas}.py`; modify `backend/app/api/painel.py`; create `frontend/src/pages/{Ambiental,Social,Governanca,Metas}.tsx`; modify `src/App.tsx`, `src/layout/Shell.tsx`
- Test: `backend/tests/test_paginas_pilares.py`

**Interfaces:**
- Consumes: `calcular`, `metas.*`, payload types, `<PaginaPainel>`.
- Produces: `GET /api/painel/{ambiental|social|governanca|metas}` → `Pagina`. Contents = spec §10 rows (card ids = DAX names: Ambiental `Emissões CO2 tCO2e`, `Emissões Evitadas tCO2e`, `Remoção Carbono tCO2e`, `Créditos Carbono tCO2e`, `Área Preservada ha`, `% Licença Válida`; Social `Empregos Diretos Gerados`, `% Empregos Gerados vs Previstos`, `% Empregos População Local`, `% Empregos Mulheres`, `Beneficiários Programas Sociais`, `Taxa Frequência Acidentes`; Governança `% Execução Orçamentária`, `Índice Execução Financeira`, `% Contratos Fiscalizados`, `% Recomendações Atendidas`, `% Riscos Críticos Mitigados`, `Casos Fraude ou Corrupção`, plus `Orçamento Previsto`, `% Liquidado do Orçamento`, `% Pago do Orçamento`). Each pillar page `indice` = `Índice {Pilar}`. Metas page: cards `% Metas Atingidas`, `Metas Atingidas`, `Metas em Atenção`, `Metas Abaixo`; three `Tabela`s (one per pillar, ordered by `id_meta`) with columns Indicador(texto), Peso(num), Atual(formato from dMetas.Formato), Meta(texto, e.g. "≥ 100%"), Status(status).
- Chart and table contents: as in the equivalent Power BI v3 pages (spec §10), each series in the pillar/sector colors.

- [ ] **Step 1: Failing tests:** ambiental index 75 and `% Licença Válida` status vermelho; social index 67, `% Empregos Mulheres` ≈ 0.25 status amarelo; governanca index 62, `% Contratos Fiscalizados` vermelho, `Casos Fraude ou Corrupção == 4`; metas `% Metas Atingidas` ≈ 0.25 and the three tables have 8, 7, 9 rows; every page with `?municipio=Inexistente` → 200 (Review Focus 3).
- [ ] **Step 2–4:** FAIL → implement → PASS. **Step 5:** frontend routes `/ambiental`, `/social`, `/governanca`, `/metas`, menu items enabled; Metas status cells colored. Manual check each page against the Power BI v3 numbers. Commit `feat: pillar pages and Metas ASG`.

---

### Task 10: Version history and user management

**Files:**
- Create: `backend/app/api/usuarios.py`; `frontend/src/pages/{Versoes,Usuarios}.tsx`; modify `App.tsx`, `Shell.tsx`
- Test: `backend/tests/test_usuarios.py`

**Interfaces:**
- Produces: `GET /api/usuarios` (admin) → list without hashes; `POST /api/usuarios {email, nome, senha, perfil}` (admin) → 201, 409 if email exists; `PATCH /api/usuarios/{id} {nome?, perfil?, ativo?, senha?}` (admin); an admin cannot deactivate or demote themself (400).
- Frontend: `/admin/versoes` table (número, data/hora pt-BR, enviado por, arquivo, linhas, avisos, status) with "Ativar" on inactive rows (confirm dialog); `/admin/usuarios` list + create form + toggle ativo + reset senha.

- [ ] **Step 1: Failing tests:** create leitor then log in with it; duplicate email 409; leitor calling `GET /api/usuarios` → 403; admin deactivating self → 400; deactivated user login → 401.
- [ ] **Step 2–4:** FAIL → implement → PASS. **Step 5:** manual: upload a second version, activate version 1 from history, Visão Geral reflects it. Commit `feat: version history and user management`.

---

### Task 11: Sector pages

**Files:**
- Create: `backend/app/paginas/setores.py`; modify `api/painel.py`; create `frontend/src/pages/Setor.tsx`; modify `App.tsx`, `Shell.tsx`
- Test: `backend/tests/test_paginas_setores.py`

**Interfaces:**
- Produces: `GET /api/painel/setor/{slug}` with slug in `energia-renovavel|hidrogenio-verde|mineracao|sustentabilidade` → `Pagina` computed on the base restricted to that sector (on top of the user filters). Contents = spec §10 sector rows (Energia: `Investimento Previsto`, `Capacidade Instalada MW`, `Geração Anual MWh`, `Fator de Capacidade Médio`, `% Energia Renovável no Consumo`; Hidrogênio: `Investimento Previsto`, `Capacidade Eletrólise MW`, `Produção H2 t`, `Intensidade Energética H2 kWh/kg`, `% Renovável nos Eletrolisadores`; Mineração: `Investimento Previsto`, `Produção ROM t`, `Faturamento Mineração`, `Intensidade Hídrica Mineração m3/t`, `% Mineração com Tecnologia Limpa`; Sustentabilidade: `Investimento Previsto`, `Área Intervenção ha`, `Remoção Carbono tCO2e`, `Créditos Carbono tCO2e`). Unknown slug → 404.

- [ ] **Step 1: Failing tests:** energia `Capacidade Instalada MW == 1905`, `Fator de Capacidade Médio` ≈ 0.341; hidrogênio `Intensidade Energética H2 kWh/kg` ≈ 54.3 and `% Renovável nos Eletrolisadores` ≈ 0.948; mineração `Investimento Previsto` ≈ 5.33e9; unknown slug 404.
- [ ] **Step 2–4:** FAIL → implement → PASS. **Step 5:** route `/setor/:slug`, four menu items; manual check. Commit `feat: sector pages`.

---

### Task 12: README and final verification

**Files:**
- Create: `README.md`

- [ ] **Step 1:** README in Portuguese: what it is; prerequisites (Docker, Node, Python); first run (`docker compose up -d db`, venv + `pip install -r requirements.txt`, copy `.env.example` → `.env`, `python -m app.cli inicializar`, `uvicorn`, `npm install`, `npm run dev`); demo users (from `.env.example`); how to upload a spreadsheet and what errors vs warnings mean; how to run tests; what is out of the MVP (spec §2).
- [ ] **Step 2:** From a clean state (`docker compose down -v`, delete `.env`), follow the README literally; all steps work; `pytest -q` and `npx vitest run` pass.
- [ ] **Step 3:** Manual walkthrough of every page as leitor and admin, comparing with Power BI v3 values (spec §9).
- [ ] **Step 4:** Commit `docs: README and run instructions`.
