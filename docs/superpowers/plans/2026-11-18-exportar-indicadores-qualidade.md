# Exportar Excel, Catálogo de Indicadores e Qualidade dos Dados — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Three features for the delivery on 18/11:
1. Every dashboard page can be exported to Excel, with its filters applied.
2. An indicator catalog shows the 82 indicators of `dIndicador`, with GRI, ODS and their current values.
3. A "Qualidade dos dados" page shows the C01–C12 checks of the active version to every logged-in user.

**Architecture:** The two new pages are ordinary `Pagina` payloads, drawn by the existing `PaginaPainel`. Export runs on the backend: openpyxl takes the same `Pagina` the screen receives and writes it to an `.xlsx`, so the Excel and the screen cannot disagree.

**Tech Stack:** same as the main plan (FastAPI, pandas, openpyxl, pytest; React + Vite + TS).

**Spec:** `docs/superpowers/specs/2026-11-17-sistema-asg-web-design.md`. This plan is an addendum to `2026-11-17-sistema-asg-web.md` (Tasks 1–12) and `2026-11-17-temas-materiais.md` (Task 13), all already implemented.

## Global Constraints

- **Do not change** dMetas, weights, the index functions or any existing measure. The Índice ASG Geral must stay 68, and the whole existing suite must stay green.
- Every user who is logged in can use all three features, admin and leitor alike. Without login, every request returns 401.
- No new dependency. openpyxl is already in `backend/requirements.txt`.
- The tasks are independent. Do them in order (14, 15, 16) and commit each one separately.
- Menu: add "Indicadores" and "Qualidade dos dados" to `PILARES` in `menu.ts`, right after "Metas ASG", with `cor: COR.geral`.
- pt-BR copy throughout.

## Review Focus

- **Export with filters that leave zero projects.** The file is still produced: cards show empty cells, tables are written with their headers only, and the Contexto sheet lists the filters.
- **Sheet names.** Excel caps them at 31 characters, forbids `[]:*?/\` and requires them to be unique. Table titles such as "Projetos de sustentabilidade ambiental" must be cleaned up, truncated and de-duplicated, or openpyxl raises an error.
- **An indicator whose `Medida DAX` is not registered.** The catalog shows "—" for that indicator and keeps going. Today every one is registered once Task 15 adds `% Projetos Concluídos`, but a future upload can bring a new name.
- **The catalog has 82 rows.** The search box filters them on the client without a new request. Upper/lower case and accents must not matter: "agua" finds "Água".
- **The Qualidade page ignores the filters.** It always shows the whole active version, and its subtitle says so.

---

### Task 14: Exportar Excel em todas as páginas do painel

**Files:**
- Create: `backend/app/exportacao.py`
- Modify: `backend/app/api/painel.py` (resolver + route `/exportar/{caminho:path}`, registered **before** `/{pagina}`)
- Modify: `frontend/src/api.ts` (`baixar` accepts query params), `frontend/src/components/PaginaPainel.tsx` (button)
- Test: `backend/tests/test_exportacao.py`

**Interfaces:**
- Consumes: `PAGINAS`, `setores.montar(base, slug)`, `temas.montar(base, slug)`, `aplicar_filtros`, the `filtros` dependency, `repositorio.versao_ativa(s)` (`numero`, `nome_arquivo`, `criado_em`), and the models in `paginas/tipos.py`
- Produces:
  - `montar_tela(base: Base, caminho: str) -> Pagina` in `api/painel.py`. It maps `"ambiental"`, `"setor/mineracao"`, `"tema/energia-limpa"` and so on to their builder, and raises `KeyError` for an unknown path. The existing routes `/setor/{slug}`, `/tema/{slug}` and `/{pagina}` must use it too, so there is a single map.
  - `pagina_para_xlsx(pagina: Pagina, filtros: Filtros, versao: Versao) -> bytes` in `exportacao.py`
  - `GET /api/painel/exportar/{caminho:path}?<same filters>` → the `.xlsx` file, with `Content-Disposition: attachment; filename="ASG_<caminho com / trocado por _>_<AAAA-MM-DD>.xlsx"`. An unknown `caminho` returns 404 "Página não encontrada".

**Workbook layout:**

1. **Sheet "Contexto"**, one label/value pair per row:
   - Página — the page title
   - Gerado em — `dd/mm/aaaa hh:mm`
   - Versão dos dados — `nº <numero> · <nome_arquivo> · enviada em dd/mm/aaaa`
   - Then one row per filter field: Setor, Vice-Presidência, Status do projeto, Município. Each value is the chosen items joined with ", ", or "Todos".
2. **Sheet "Indicadores"**: columns Indicador | Valor | Status. The page's `indice`, if there is one, comes first, then each card in order.
   - Valor is the raw number, with a number format taken from the card's `formato`: `brl` → `"R$" #,##0.00` · `pct` → `0.0%` · `num` → `#,##0` · `dec` → `0.00` · `idx` → `0`.
   - Status is "Verde", "Amarelo", "Vermelho" or empty.
3. **Sheet "Gráficos"**: one block per chart. The first row holds the chart title in bold. The next row is a header: "Categoria", then one column per series name. Then one row per category. Leave an empty row between blocks.
4. **One sheet per table**, named after the table title as described in Review Focus. The header row uses the column labels.
   - Numeric columns keep raw numbers with the format mapping above.
   - `simnao`, `status` and `texto` columns are written as text.

Freeze the header row and auto-fit the column widths (cap at 60).

- [ ] **Step 1: Write the failing tests** (in `tests/test_exportacao.py`, reusing the `com_versao` fixture pattern of `test_paginas_setores.py`)

```python
from io import BytesIO
from openpyxl import load_workbook

def baixar(cliente, h, caminho, query=""):
    r = cliente.get(f"/api/painel/exportar/{caminho}{query}", headers=h)
    assert r.status_code == 200, r.text
    assert "attachment" in r.headers["content-disposition"]
    return load_workbook(BytesIO(r.content))

def test_visao_geral_bate_com_a_tela(cliente, com_versao, h_leitor):
    tela = cliente.get("/api/painel/visao-geral", headers=h_leitor).json()
    wb = baixar(cliente, h_leitor, "visao-geral")
    assert wb.sheetnames[:3] == ["Contexto", "Indicadores", "Gráficos"]
    linhas = {r[0]: r[1] for r in wb["Indicadores"].iter_rows(min_row=2, values_only=True)}
    assert linhas["Índice ASG Geral"] == pytest.approx(tela["indice"]["valor"])
    assert linhas["Investimento previsto"] == pytest.approx(42.83e9, rel=1e-3)
    assert linhas["Projetos"] == 48

def test_filtros_vao_para_o_contexto(cliente, com_versao, h_leitor):
    wb = baixar(cliente, h_leitor, "setor/mineracao", "?setor=Mineração")
    ctx = {r[0]: r[1] for r in wb["Contexto"].iter_rows(values_only=True)}
    assert ctx["Setor"] == "Mineração"
    assert ctx["Município"] == "Todos"
    assert ctx["Versão dos dados"].startswith("nº 1")
    # o título "Conformidade ambiental dos projetos minerários" passa do limite de 31 caracteres do Excel
    assert "Conformidade ambiental dos proj" in wb.sheetnames

def test_tabela_vira_aba_com_todas_as_linhas(cliente, com_versao, h_leitor):
    wb = baixar(cliente, h_leitor, "tema/licenca-social")
    aba = [n for n in wb.sheetnames if n.startswith("Projetos sem consulta")][0]
    assert wb[aba].max_row == 1 + 18

def test_nomes_de_aba_validos_e_unicos(cliente, com_versao, h_leitor):
    for caminho in ["ambiental", "social", "governanca", "metas", "setor/sustentabilidade", "tema/riscos-climaticos"]:
        wb = baixar(cliente, h_leitor, caminho)
        assert len(set(wb.sheetnames)) == len(wb.sheetnames)
        assert all(len(n) <= 31 and not set(n) & set("[]:*?/\\") for n in wb.sheetnames)

def test_filtro_sem_projetos_ainda_gera_arquivo(cliente, com_versao, h_leitor):
    wb = baixar(cliente, h_leitor, "ambiental", "?municipio=Inexistente")
    assert "Indicadores" in wb.sheetnames

def test_exportar_pagina_inexistente(cliente, com_versao, h_leitor):
    assert cliente.get("/api/painel/exportar/xyz", headers=h_leitor).status_code == 404

def test_exportar_exige_login(cliente, com_versao):
    assert cliente.get("/api/painel/exportar/visao-geral").status_code == 401
```


- [ ] **Step 2: Run** `.venv\Scripts\python -m pytest tests/test_exportacao.py -v`. Expected: FAIL (404).
- [ ] **Step 3: Implement** `montar_tela`, `pagina_para_xlsx` and the route. Then make `/setor/{slug}`, `/tema/{slug}` and `/{pagina}` delegate to `montar_tela`, converting `KeyError` into their existing 404 messages.
- [ ] **Step 4: Run** the Step 2 command, then the full suite. Expected: all PASS.
- [ ] **Step 5: Frontend.**
  - In `api.ts`, change the signature to `baixar(caminho: string, nome: string, params?: URLSearchParams)`, appending `?<params>` when present. Envio's existing call keeps working.
  - In `PaginaPainel.tsx`, add a "Exportar Excel" button on the right of `pagina-cabecalho`. It calls `api.baixar('/api/painel/exportar/' + endpoint.replace('/api/painel/', ''), nome, query)`, where `nome` is `nomeExportacao(caminho)` from `format.ts`: `ASG_<that path with / → _>_<AAAA-MM-DD>.xlsx`, the same name the server sends (the `download` attribute overrides Content-Disposition, so the date must be added on the client too). The server's date is taken in America/Fortaleza.
  - While the download runs, the button reads "Gerando…" and is disabled. A failed download shows the error message next to the button.
  - Run `npm run build` and `npx vitest run` in `frontend/`. Expected: no errors.
- [ ] **Step 6: Check in the browser.**
  1. Open Visão Geral and click Exportar Excel. The file opens in Excel with the 3 sheets (Contexto, Indicadores, Gráficos) plus one per table, and the "Índice ASG Geral" row shows 68.
  2. Choose Setor = Mineração, open the Mineração page and export again. The Contexto sheet shows "Setor: Mineração".
- [ ] **Step 7: Commit** — `git commit -m "feat: export any dashboard page to Excel"`

---

### Task 15: Catálogo de Indicadores

**Files:**
- Create: `backend/app/paginas/indicadores.py`
- Modify:
  - `backend/app/calculos/medidas.py` — add the missing `% Projetos Concluídos`
  - `backend/app/paginas/comum.py` — add `texto_valor`
  - `backend/app/paginas/tipos.py` and `frontend/src/api.ts` — `Tabela.busca`
  - `backend/app/api/painel.py` — register `"indicadores"` in `PAGINAS`, which also makes it exportable through `montar_tela`
  - `frontend/src/components/Tabela.tsx`, `frontend/src/menu.ts`
- Test: `backend/tests/test_paginas_indicadores.py`, `backend/tests/test_calculos.py`

**Interfaces:**
- Consumes:
  - `Contexto(base)`, with `.valor(medida)` (raises `KeyError` for an unknown measure) and `.status(medida)`
  - `base["dIndicador"]`, with columns ID Indicador, Indicador, Pilar, Descrição, Cálculo, Tabela de Origem, Medida DAX, Tema Material, ODS, Referência GRI, Polaridade, Página do Painel
- Produces:
  - measure `% Projetos Concluídos`, ported from the Power BI: `DIVIDE(CALCULATE([Qtd Projetos], dProjeto[Status Projeto] = "Concluído"), [Qtd Projetos])`
  - `texto_valor(v: float | None, formato: str) -> str` in `comum.py`
  - `formato_da_medida(nome: str) -> str` in `indicadores.py`
  - `indicadores.montar(base: Base) -> Pagina`
  - `Tabela.busca: bool = False` in the backend model and `busca?: boolean` in TS

**Rules:**
- `formato_da_medida`:
  - if the measure is in dMetas, use its `Formato`: `"%"` → `pct`, `"n"` → `num`, `"dec"` → `dec`, `"idx"` → `dec` (Índice Transparência Médio is 0,58, which the `idx` card format would round to 1; two decimals match `fmt_meta`);
  - else, a name starting with `%` → `pct`;
  - else, a name containing "Investimento", "Valor", "Orçamento", "Custo", "Faturamento" or "Saldo Orçamentário" → `brl`;
  - else, a name starting with "Índice" or "Taxa", or containing "Intensidade", "Fator", "Horas" or " por " → `dec` (" por " covers "Empregos por R$ milhão", 0,43, which `num` would show as "0");
  - else `num`.
- `texto_valor` gives the same text as `valor()` in `frontend/src/format.ts`, so the catalog matches the cards (`brl`: one decimal in bi/mi below 100, none above or in mil). Examples, written as tests:

  | Call | Result |
  |---|---|
  | `(0.5417, "pct")` | `"54,2%"` |
  | `(9.012e9, "brl")` | `"R$ 9,0 bi"` |
  | `(52.73e6, "brl")` | `"R$ 52,7 mi"` |
  | `(7236, "num")` | `"7.236"` |
  | `(2.119, "dec")` | `"2,12"` |
  | `(None, any)` | `"—"` |

- **Page:**
  - title "Indicadores";
  - subtitle "Catálogo dos <N> indicadores ASG com cálculo, origem, ODS e referência GRI. Os valores respeitam os filtros.", where N is the number of dIndicador rows (82 today), so a new upload never contradicts the "Indicadores" card. When a search matches nothing, the table says "Nenhum resultado para a busca." instead of blaming the filters;
  - no `indice`, no charts.
  - Cards, each with formato `num` and an id equal to its title:

    | Card | Value on the current base |
    |---|---|
    | "Indicadores" | 82 |
    | "Ambiental" | 36 |
    | "Social" | 22 |
    | "Governança" | 24 |
    | "Com meta ASG" | 24 (the number of dMetas rows) |
    | "Com referência GRI" | 73 (`Referência GRI` not empty and not "-") |

- **One table**, id `catalogo`, titled "Catálogo de indicadores", with `busca=True` and the rows sorted by ID Indicador:
  - Columns: ID · Indicador · Pilar · Tema · ODS · GRI · Valor atual (`texto`, from `texto_valor`) · Status (`status`: the `ResultadoMeta.status` of that measure, empty if the measure has no meta) · Cálculo · Origem (Tabela de Origem).
  - A `Medida DAX` that is not registered gives Valor atual "—" instead of an exception.

- [ ] **Step 1: Write the failing tests**

```python
# test_calculos.py
def test_pct_projetos_concluidos():
    assert calcular(base_modelo(), "% Projetos Concluídos") == pytest.approx(5 / 48)

# test_paginas_indicadores.py
@pytest.mark.parametrize("v,f,esperado", [
    (0.5417, "pct", "54,2%"), (9.012e9, "brl", "R$ 9,0 bi"), (52.73e6, "brl", "R$ 52,7 mi"),
    (7236, "num", "7.236"), (2.119, "dec", "2,12"), (None, "num", "—"), (0, "brl", "R$ 0")])
def test_texto_valor(v, f, esperado):
    assert texto_valor(v, f) == esperado

def test_catalogo(cliente, com_versao, h_leitor):
    p = cliente.get("/api/painel/indicadores", headers=h_leitor).json()
    c = {x["id"]: x["valor"] for x in p["cards"]}
    assert c == {"Indicadores": 82, "Ambiental": 36, "Social": 22, "Governança": 24,
                 "Com meta ASG": 24, "Com referência GRI": 73}
    t = p["tabelas"][0]
    assert t["busca"] is True and len(t["linhas"]) == 82
    por_id = {l["id"]: l for l in t["linhas"]}
    assert por_id["IND01"]["valor"] == "R$ 9,0 bi"
    assert por_id["IND31"]["valor"] == "54,2%"
    assert por_id["IND55"]["valor"] == "2,12"
    assert por_id["IND62"]["valor"] == "10,4%"
    assert por_id["IND01"]["gri"] == "GRI 203-1" and por_id["IND01"]["ods"] == "ODS 7"
    assert por_id["IND31"]["status"] in {"Atingida", "Atenção", "Abaixo"}
    assert por_id["IND40"]["valor"] == "0,43"

def test_catalogo_respeita_filtro(cliente, com_versao, h_leitor):
    p = cliente.get("/api/painel/indicadores?setor=Mineração", headers=h_leitor).json()
    por_id = {l["id"]: l for l in p["tabelas"][0]["linhas"]}
    assert por_id["IND01"]["valor"] == "R$ 0"          # Mineração não tem energia renovável

def test_medida_desconhecida_vira_traco(cliente, sessao_teste, usuarios, h_leitor):
    b = base_modelo()
    b["dIndicador"].loc[0, "Medida DAX"] = "Medida Que Nao Existe"
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, b, usuarios["admin"].id, "x.xlsx", [])
    p = cliente.get("/api/painel/indicadores", headers=h_leitor).json()
    assert p["tabelas"][0]["linhas"][0]["valor"] == "—"
    repositorio.limpar_cache()
```

`texto_valor(0, "brl")` must give `"R$ 0"`, as `test_catalogo_respeita_filtro` expects. If an additive measure returns 0 under a filter, that is the value. If `salvar_versao` needs the base to be typed first, call `aplicar_tipos(b)` in the last test.

- [ ] **Step 2: Run** `.venv\Scripts\python -m pytest tests/test_paginas_indicadores.py tests/test_calculos.py -k "concluidos or texto_valor or catalogo or desconhecida" -v`. Expected: FAIL.
- [ ] **Step 3: Implement** the measure, `texto_valor`, `formato_da_medida`, `indicadores.montar`, the `busca` field and the `PAGINAS` entry.
- [ ] **Step 4: Run** the Step 2 command, then the full suite. Expected: all PASS.
- [ ] **Step 5: Frontend.**
  - When `tabela.busca` is true, `Tabela.tsx` shows a search input above the table, with placeholder "Buscar por nome, código, tema, ODS ou GRI".
  - It filters the rows whose cells, joined, contain the query. Compare after `normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()`, so "agua" finds "Água".
  - It shows "N de M indicadores" under the input.
  - Add the menu item `{ rota: '/indicadores', rotulo: 'Indicadores', cor: COR.geral, pronto: true, painel: true, endpoint: '/api/painel/indicadores' }`.
  - Run `npm run build` and `npx vitest run`. Expected: no errors.
- [ ] **Step 6: Check in the browser.** The page lists 82 indicators. Typing "GRI 403" leaves the occupational-safety rows, and "agua" finds the water indicators. Exportar Excel works on this page too.
- [ ] **Step 7: Commit** — `git commit -m "feat: indicator catalog with GRI, ODS and current values"`

---

### Task 16: Qualidade dos Dados

**Files:**
- Create: `backend/app/paginas/qualidade.py`
- Modify:
  - `backend/app/api/painel.py` — route `/qualidade` before `/{pagina}`. It needs the `Session` for the version data, so it does not go in `PAGINAS`. `montar_tela` gets a `versao` argument, or the export route special-cases `"qualidade"`; implementer's choice.
  - `frontend/src/menu.ts`
- Test: `backend/tests/test_paginas_qualidade.py`

**Interfaces:**
- Consumes:
  - `rodar_checagens(base) -> list[ResultadoChecagem]`, with `id`, `checagem`, `tabela`, `regra` and `problemas`
  - `repositorio.versao_ativa(s)`, with `numero`, `nome_arquivo`, `criado_em`, `enviado_por.nome` and `linhas_por_aba`
- Produces: `qualidade.montar(base: Base, versao: Versao) -> Pagina` and `GET /api/painel/qualidade`. Filters are accepted but ignored.

**Page:**
- title "Qualidade dos dados";
- subtitle `"Versão nº <numero> · <nome_arquivo> · enviada por <nome> em dd/mm/aaaa hh:mm. As checagens usam a versão inteira, sem os filtros."`. Time in America/Fortaleza, as in the export. `enviado_por` is nullable, so without it the subtitle reads `"… · enviada em dd/mm/aaaa hh:mm. …"`.
- Cards, each with formato `num`:
  - "Checagens sem problema" — how many of the 12 checks report 0 problems;
  - "Problemas encontrados" — the sum of `problemas`;
  - "Abas carregadas" — the size of `linhas_por_aba`;
  - "Linhas carregadas" — the sum of `linhas_por_aba`.

  Set the card status to `verde` when "Problemas encontrados" is 0, else `amarelo`.
- **Table 1**, id `checagens`, "Checagens de qualidade (C01–C12)":
  - columns ID · Checagem · Tabelas · Regra · Problemas (`num`) · Situação (`status`);
  - Situação is "OK" when there are 0 problems, else "Verificar". `corDoStatus` in `format.ts` maps OK → verde and Verificar → amarelo, next to the metas words (Atingida/Atenção/Abaixo), which stay as they are. The upload screen (Envio) shows "Verificar: N" in yellow too, since the checks are warnings that do not block saving.
- **Table 2**, id `abas`, "Linhas por aba": columns Aba · Linhas (`num`), in the order of `ABAS` in `planilha/esquema.py` (dEmpresa, dSetor, dProjeto…), then any other key. `linhas_por_aba` is stored as JSONB, and Postgres does not keep key order, so its own order cannot be used.

- [ ] **Step 1: Write the failing tests**

```python
def test_qualidade_base_limpa(cliente, com_versao, h_leitor):
    p = cliente.get("/api/painel/qualidade", headers=h_leitor).json()
    c = {x["id"]: x for x in p["cards"]}
    assert c["Checagens sem problema"]["valor"] == 12
    assert c["Problemas encontrados"]["valor"] == 0
    assert c["Problemas encontrados"]["status"] == "verde"
    assert p["subtitulo"].startswith("Versão nº 1")
    assert [l["id"] for l in p["tabelas"][0]["linhas"]] == [f"C{i:02d}" for i in range(1, 13)]
    assert len(p["tabelas"][1]["linhas"]) >= 17   # ABAS tem 17 abas obrigatórias

def test_qualidade_aponta_problema(cliente, sessao_teste, usuarios, h_leitor):
    b = base_modelo()
    b["dProjeto"].loc[0, "Investimento Realizado"] = 10 * b["dProjeto"].loc[0, "Investimento Previsto"]  # C07
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, b, usuarios["admin"].id, "x.xlsx", [])
    p = cliente.get("/api/painel/qualidade", headers=h_leitor).json()
    c07 = next(l for l in p["tabelas"][0]["linhas"] if l["id"] == "C07")
    assert c07["problemas"] == 1 and c07["situacao"] == "Verificar"
    assert {x["id"]: x for x in p["cards"]}["Problemas encontrados"]["status"] == "amarelo"
    repositorio.limpar_cache()

def test_qualidade_ignora_filtros(cliente, com_versao, h_leitor):
    a = cliente.get("/api/painel/qualidade", headers=h_leitor).json()
    b = cliente.get("/api/painel/qualidade?setor=Mineração", headers=h_leitor).json()
    assert a["cards"] == b["cards"]

def test_qualidade_exige_login(cliente, com_versao):
    assert cliente.get("/api/painel/qualidade").status_code == 401

def test_abas_na_ordem_do_esquema(cliente, sessao_teste, com_versao, h_leitor):
    sessao_teste.expire_all()  # relê linhas_por_aba do JSONB, que não guarda a ordem das chaves
    p = cliente.get("/api/painel/qualidade", headers=h_leitor).json()
    assert [l["aba"] for l in p["tabelas"][1]["linhas"]] == list(ABAS)

def test_exportar_qualidade_ignora_filtros(cliente, com_versao, h_leitor):
    r = cliente.get("/api/painel/exportar/qualidade?setor=Mineração", headers=h_leitor)
    assert r.status_code == 200
    wb = load_workbook(BytesIO(r.content))
    ctx = {l[0]: l[1] for l in wb["Contexto"].iter_rows(values_only=True)}
    assert ctx["Setor"] == "Todos"          # a página não usa os filtros, e o arquivo diz isso
    assert "Checagens de qualidade (C01–C" in " ".join(wb.sheetnames)
```

The export route special-cases `"qualidade"`: it builds the page from the unfiltered base and the active version, and writes empty filters to the Contexto sheet.


- [ ] **Step 2: Run** `.venv\Scripts\python -m pytest tests/test_paginas_qualidade.py -v`. Expected: FAIL.
- [ ] **Step 3: Implement** `qualidade.montar` and the route, and make the page exportable.
- [ ] **Step 4: Run** the Step 2 command, then the full suite. Expected: all PASS.
- [ ] **Step 5: Frontend.** Add the menu item `{ rota: '/qualidade', rotulo: 'Qualidade dos dados', cor: COR.geral, pronto: true, painel: true, endpoint: '/api/painel/qualidade' }`. Run `npm run build` and `npx vitest run`.
- [ ] **Step 6: Check in the browser.** As leitor, the page shows 12 green seals, 0 problems and the version line. As admin, the same.
- [ ] **Step 7: Commit** — `git commit -m "feat: data quality page for all users"`

---

## Final check (after Task 16)

- Full suite green: `.venv\Scripts\python -m pytest -q`, plus `npx vitest run` and `npm run build` in `frontend/`.
- In the browser, the Visão Geral still shows 68, and all three features work as leitor.
