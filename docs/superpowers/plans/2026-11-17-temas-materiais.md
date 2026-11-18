# Temas Materiais (T4, T6, T7) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three pages — one per material theme T4, T6 and T7 — that show how each theme appears across the four sectors, without changing sectors, pillars or the Índice ASG.

**Architecture:** A new page module `backend/app/paginas/temas.py` builds a `Pagina` for each theme from measures that already exist in `app.calculos.medidas`. It is served by `GET /api/painel/tema/{slug}`. The frontend adds a `TEMAS` menu group, rendered by the existing generic `PaginaPainel`. The theme index uses the same method as the pillar index, applied to the dMetas rows whose `Tema Material` equals the theme code.

**Tech Stack:** same as the main plan (FastAPI, pandas, pytest; React + Vite + TS).

**Spec:** `docs/superpowers/specs/2026-11-17-sistema-asg-web-design.md` (§9 cálculos, §10 telas). This plan is an addendum to `docs/superpowers/plans/2026-11-17-sistema-asg-web.md`, which is already fully implemented.

## Global Constraints

- **Do not change dMetas, weights, `avaliar_metas`, `indice_pilar` or `indice_geral`.** Índice ASG Geral must stay 68, pillars 75/67/62, and every existing test must stay green.
- No new measure formulas. Use only measures already registered in `app/calculos/medidas.py`.
- Theme codes and titles (exact copy):
  - `T4` — "T4 Riscos climáticos e resiliência", slug `riscos-climaticos`, subtitle "Gestão de riscos climáticos e resiliência do portfólio", color `#0277BD`
  - `T6` — "T6 Energia limpa", slug `energia-limpa`, subtitle "Eficiência energética e energia limpa", color `#00A19A`
  - `T7` — "T7 Licença social", slug `licenca-social`, subtitle "Engajamento comunitário e licença social para operar", color `#D9730D`
- Filters work exactly as on the sector pages (the user's filters apply before the page is built).
- pt-BR copy throughout.

## Review Focus

- A filter that leaves the theme with no measurable meta (for example, a sector with no electrolyzers for T6) → the theme index card shows "—", not 0, and nothing crashes.
- T6 shows 100 even though one of its metas is "Atenção" (94,8% against a 95% meta; achievement 0,998). The index card's `ajuda` text must say that the index rounds achievement, and the metas table shows the "Atenção" status.
- `Tema Material` with stray spaces (" T4") → still matched (compare after `.strip()`).
- An unknown slug → 404 "Tema não encontrado".
- The route `/tema/{slug}` must be registered **before** `/{pagina}` in `api/painel.py`, or it is swallowed.

---

### Task 13: Theme pages (T4, T6, T7)

**Files:**
- Create: `backend/app/paginas/temas.py`
- Modify: `backend/app/calculos/metas.py` (add `indice_tema`)
- Modify: `backend/app/api/painel.py` (route before `/{pagina}`)
- Modify: `frontend/src/menu.ts`, `frontend/src/App.tsx`, `frontend/src/layout/Shell.tsx`
- Test: `backend/tests/test_paginas_temas.py`, `backend/tests/test_calculos.py`

**Interfaces:**
- Consumes:
  - `avaliar_metas(base) -> list[ResultadoMeta]` and `_indice(resultados) -> float | None` (metas.py)
  - `Contexto(base)` with `.card(medida, titulo, formato)`, `.metas` and `.status(medida)` (paginas/comum.py)
  - `por_setor(base, medidas)` (comum.py), `_series_por_setor`, `_projetos`, `_valor_fato` and `valor_atual` (paginas/pilares.py; import them, don't copy them)
  - `texto_meta(r)` (comum.py), `cor_indice(v)` (metas.py)
  - `Card`, `Grafico`, `Serie`, `Tabela`, `Coluna`, `Pagina` (paginas/tipos.py); `Pagina.indice` is the big index card, as on the Visão Geral
- Produces:
  - `indice_tema(base: Base, tema: str, resultados: list[ResultadoMeta] | None = None) -> float | None` in `metas.py`
  - `TEMAS: dict[str, Tema]` and `montar(base: Base, slug: str) -> Pagina` in `paginas/temas.py`
  - `GET /api/painel/tema/{slug}` → `Pagina`
  - `TEMAS: ItemMenu[]` in `menu.ts`, with routes `/tema/<slug>`

#### Page layout (identical across the three themes)

1. `indice`: `Card(id="Índice do Tema", titulo="Índice do tema", valor=indice_tema(...), formato="idx", status=cor_indice(v), ajuda=...)`. The `ajuda` text: "Média ponderada pelo peso do atingimento das metas deste tema (dMetas, coluna Tema Material). Mesmo método do índice de pilar."
2. `cards`: the theme's KPIs, listed below.
3. `graficos`: the theme's charts, listed below. Each has one value per sector, built with `por_setor` / `_series_por_setor`, using `tipo="colunas"`.
4. `tabelas[0]`: "Metas do tema", id `metas_tema`, with the same columns as the Metas ASG page (indicador, peso, atual, meta, status) and only the rows of this theme.
5. `tabelas[1]`: one row per project, with the columns listed below.

#### Content per theme (card ids are the existing measure names)

| | Cards (id → título, formato) | Gráficos por setor | Tabela por projeto |
|---|---|---|---|
| **T4** | `Emissões CO2 tCO2e` → "Emissões de CO2 (tCO2e)", num · `Emissões Evitadas tCO2e` → "Emissões evitadas (tCO2e)", num · `Saldo Climático tCO2e` → "Saldo climático (tCO2e)", num · `Intensidade Emissões tCO2e/R$ mi` → "Intensidade de emissões (tCO2e/R$ mi)", dec · `% Projetos com Análise de Riscos` → "Projetos com análise de riscos", pct · `% Riscos Críticos Mitigados` → "Riscos críticos mitigados", pct · `Incidentes Ambientais` → "Incidentes ambientais", num | `emissoes_setor`: two series, Emissões CO2 and Emissões evitadas · `incidentes_setor`: Incidentes Ambientais | Projeto, Setor, Emissões (tCO2e), Evitadas (tCO2e), Incidentes |
| **T6** | `Capacidade Instalada MW` → "Capacidade instalada (MW)", num · `Geração Anual MWh` → "Geração anual (MWh)", num · `% Energia Renovável no Consumo` → "Energia renovável no consumo", pct · `% Renovável nos Eletrolisadores` → "Renovável nos eletrolisadores", pct · `% Projetos Tecnologia Limpa` → "Projetos com tecnologia limpa", pct | `tecnologia_setor`: % Projetos Tecnologia Limpa · `renovavel_setor`: % Energia Renovável no Consumo | Projeto, Setor, Tecnologia limpa (simnao, from fAmbiental), Energia renovável consumida (MWh) |
| **T7** | `% Empregos População Local` → "Empregos para a população local", pct · `% Consulta Comunidades` → "Projetos com consulta às comunidades", pct · `% Avaliação Impacto Social` → "Projetos com avaliação de impacto social", pct · `Comunidades Beneficiadas` → "Comunidades beneficiadas", num · `Investimento Social` → "Investimento social", brl · `Reclamações Sociais` → "Reclamações sociais", num | `consulta_setor`: two series, % Consulta Comunidades and % Avaliação Impacto Social · `reclamacoes_setor`: Reclamações Sociais | Title "Projetos sem consulta às comunidades": **only** the projects whose `Consulta Comunidades` is not "Sim". Columns: Projeto, Setor, Município, Avaliação de impacto social (simnao), Reclamações |

`% Fornecedores Locais` is deliberately left out of T7: it is 0,97% on the current base and would draw questions the group can't answer in time.

- [ ] **Step 1: Write the failing tests for `indice_tema`** (in `tests/test_calculos.py`, using the same `base_modelo()` fixture as the existing index tests)

```python
def test_indice_tema_base_completa():
    b = base_modelo()
    assert indice_tema(b, "T4") == pytest.approx(50.0, abs=0.01)
    assert indice_tema(b, "T6") == pytest.approx(99.87, abs=0.01)
    assert indice_tema(b, "T7") == pytest.approx(71.53, abs=0.01)

def test_indice_tema_com_filtro_mineracao():
    b = aplicar_filtros(base_modelo(), Filtros(setores=["Mineração"], vps=[], status=[], municipios=[]))
    assert indice_tema(b, "T4") == pytest.approx(75.0, abs=0.01)
    assert indice_tema(b, "T6") == pytest.approx(92.59, abs=0.01)
    assert indice_tema(b, "T7") == pytest.approx(63.89, abs=0.01)

def test_indice_tema_inexistente_e_none():
    assert indice_tema(base_modelo(), "T99") is None

def test_indice_geral_nao_muda():
    assert round(indice_geral(base_modelo())) == 68
```

- [ ] **Step 2: Run** `.venv\Scripts\python -m pytest tests/test_calculos.py -k indice_tema -v`. Expected: FAIL (`indice_tema` not defined).

- [ ] **Step 3: Implement `indice_tema(base, tema, resultados=None)` in `metas.py`.** Map `ID Meta` → `Tema Material` from `base["dMetas"]`, comparing `str(v).strip() == tema`. Keep the theme's `ResultadoMeta`s and return `_indice(selecionados)`.

- [ ] **Step 4: Run the Step 2 command again.** Expected: PASS. Then run the whole suite (`.venv\Scripts\python -m pytest -q`); it must stay all green.

- [ ] **Step 5: Write the failing page tests** in `tests/test_paginas_temas.py`, reusing the `com_versao` fixture pattern from `test_paginas_setores.py`

```python
def tema(cliente, h, slug, query=""):
    r = cliente.get(f"/api/painel/tema/{slug}{query}", headers=h)
    assert r.status_code == 200, r.text
    p = r.json()
    return p, {c["id"]: c for c in p["cards"]}

def test_t4(cliente, com_versao, h_leitor):
    p, c = tema(cliente, h_leitor, "riscos-climaticos")
    assert p["titulo"] == "T4 Riscos climáticos e resiliência"
    assert p["indice"]["valor"] == pytest.approx(50.0, abs=0.01)
    assert c["Emissões CO2 tCO2e"]["valor"] == 291160
    assert c["Saldo Climático tCO2e"]["valor"] == pytest.approx(3186729, abs=1)
    assert c["Intensidade Emissões tCO2e/R$ mi"]["valor"] == pytest.approx(6.80, abs=0.01)
    assert c["% Projetos com Análise de Riscos"]["valor"] == pytest.approx(0.854, abs=1e-3)
    assert c["Incidentes Ambientais"]["valor"] == 13
    metas = p["tabelas"][0]["linhas"]
    assert [m["status"] for m in metas] == ["Atingida", "Abaixo"]
    assert len(p["tabelas"][1]["linhas"]) == 48

def test_t6(cliente, com_versao, h_leitor):
    p, c = tema(cliente, h_leitor, "energia-limpa")
    assert p["indice"]["valor"] == pytest.approx(99.87, abs=0.01)
    assert c["Capacidade Instalada MW"]["valor"] == 1905
    assert c["% Renovável nos Eletrolisadores"]["status"] == "amarelo"
    assert c["% Projetos Tecnologia Limpa"]["valor"] == pytest.approx(0.958, abs=1e-3)
    assert "Atenção" in [m["status"] for m in p["tabelas"][0]["linhas"]]

def test_t7(cliente, com_versao, h_leitor):
    p, c = tema(cliente, h_leitor, "licenca-social")
    assert p["indice"]["valor"] == pytest.approx(71.53, abs=0.01)
    assert c["% Consulta Comunidades"]["valor"] == pytest.approx(0.625, abs=1e-3)
    assert c["Comunidades Beneficiadas"]["valor"] == 152
    assert c["Investimento Social"]["valor"] == pytest.approx(52.73e6, abs=1e3)
    assert "% Fornecedores Locais" not in c
    assert len(p["tabelas"][1]["linhas"]) == 18   # projetos sem consulta

def test_tema_com_filtro(cliente, com_versao, h_leitor):
    p, _ = tema(cliente, h_leitor, "riscos-climaticos", "?setor=Mineração")
    assert p["indice"]["valor"] == pytest.approx(75.0, abs=0.01)

def test_graficos_tem_um_valor_por_setor(cliente, com_versao, h_leitor):
    p, _ = tema(cliente, h_leitor, "energia-limpa")
    for g in p["graficos"]:
        assert len(g["categorias"]) == 4
        assert all(len(s["valores"]) == 4 for s in g["series"])

def test_tema_inexistente(cliente, com_versao, h_leitor):
    r = cliente.get("/api/painel/tema/xyz", headers=h_leitor)
    assert r.status_code == 404

def test_tema_exige_login(cliente, com_versao):
    assert cliente.get("/api/painel/tema/energia-limpa").status_code == 401
```

Add `indice_tema` to the existing `from app.calculos.metas import ...` line in `test_calculos.py`.

- [ ] **Step 6: Run** `.venv\Scripts\python -m pytest tests/test_paginas_temas.py -v`. Expected: FAIL (404 for every slug).

- [ ] **Step 7: Implement `paginas/temas.py` and the route.** Follow the shape of `paginas/setores.py`: a frozen dataclass `Tema(codigo, nome, subtitulo, cor, montar)` and a `TEMAS` dict keyed by slug. `montar(base, slug)` builds one `Contexto(base)`, passes `ctx.metas` to `indice_tema`, and returns `Pagina(titulo=..., subtitulo=..., indice=..., cards=..., graficos=..., tabelas=...)`. Add `GET /tema/{slug}` in `api/painel.py` next to `/setor/{slug}` and above `/{pagina}`; it raises 404 "Tema não encontrado" for an unknown slug.

- [ ] **Step 8: Run** the Step 6 command, then the full suite. Expected: all PASS.

- [ ] **Step 9: Frontend menu.** In `menu.ts`, export `TEMAS: ItemMenu[]` with the three themes: `rota: '/tema/<slug>'`, `rotulo` = the title, `cor` from Global Constraints, `pronto: true`, `painel: true`, `endpoint: '/api/painel/tema/<slug>'`. In `App.tsx`, add `...TEMAS` to the routed list. In `Shell.tsx`, render a "Temas Materiais" group **between the pillars and "Setores"**, the same way the Setores group is rendered. Run `npm run build` and `npm test` in `frontend/`. Expected: no errors.

- [ ] **Step 10: Check in the browser** (launch configs `api` and `web`). Log in as the reader user, then open each theme page:
  - the index card shows 50 (T4), 100 (T6) and 72 (T7);
  - the charts have the 4 sectors;
  - the T7 table lists 18 projects;
  - with Setor = Mineração, T4 shows 75.

  Then open the Visão Geral and confirm it still shows 68.

- [ ] **Step 11: Commit**

```bash
git add backend/app/calculos/metas.py backend/app/paginas/temas.py backend/app/api/painel.py backend/tests/test_calculos.py backend/tests/test_paginas_temas.py frontend/src/menu.ts frontend/src/App.tsx frontend/src/layout/Shell.tsx docs/superpowers/plans/2026-11-17-temas-materiais.md
git commit -m "feat: material theme pages T4, T6, T7"
```
