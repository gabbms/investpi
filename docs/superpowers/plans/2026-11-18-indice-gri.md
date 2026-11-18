# Índice de conteúdo GRI exportável — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A button "Exportar índice GRI" on the Indicadores page downloads `ASG_indice_gri_<AAAA-MM-DD>.xlsx`: the indicators grouped by GRI standard and disclosure with their current values (filters applied), ready to go into the sustainability report.

**Architecture:** A new module `app/gri.py` holds the official Portuguese names (with source) and the supersession dates, and builds the index from `dIndicador` plus the catalog's current values. `app/exportacao.py` writes it in report layout. A route `/api/painel/exportar-gri` and a second export button on the Indicadores page.

**Tech Stack:** FastAPI, pandas, openpyxl, pytest; React + Vite + TS, vitest. No new dependency.

**Spec:** `docs/superpowers/specs/2026-11-18-indice-gri-design.md`

## Global Constraints

- The file goes straight into the report: no internal columns; nothing in it claims the report is "de acordo com" the GRI Standards; the title is exactly "Índice de conteúdo GRI — indicadores quantitativos".
- Values respect the filters and are the same text as the catalog's "Valor atual" (`texto_valor`); a measure the system doesn't compute is "—".
- Names come only from the table below (official GRI Portuguese translations). A reference outside the table, or of a standard already superseded on the export date (America/Fortaleza), goes to "Referências a revisar" — never into the index.
- Any logged-in user; without login → 401.
- No change to measures, metas or weights: the Índice ASG Geral stays 68. The whole existing suite stays green (188 backend, 10 vitest).
- Frontend tests: `npx vitest run`; `npm run build` must pass.

## Official names (verified)

Standard titles: GRI's list "GRI Standards Portuguese Translations" (globalreporting.org/how-to-use-the-gri-standards/gri-standards-portuguese-translations/). Disclosure titles: the headings "Conteúdo X-Y …" in GRI's Portuguese PDFs — GRI 2: Conteúdos Gerais 2021 (pdf.ashx?id=13899); GRI 201, 203, 204, 205 and 302 (their own Portuguese PDFs); for 303, 304, 305, 306, 403, 404, 405 and 413, the Portuguese edition of GRI 11: Setor de Petróleo e Gás 2021, which reproduces the topic disclosures. Record this source text in a comment at the top of the table.

| Standard (as written) | Superseded |
|---|---|
| GRI 2: Conteúdos Gerais 2021 | — |
| GRI 201: Desempenho Econômico 2016 | — |
| GRI 203: Impactos Econômicos Indiretos 2016 | — |
| GRI 204: Práticas de Compra 2016 | — |
| GRI 205: Combate à Corrupção 2016 | — |
| GRI 302: Energia 2016 | by "GRI 103: Energy 2025" on 2027-01-01 |
| GRI 303: Água e Efluentes 2018 | — |
| GRI 304: Biodiversidade 2016 | by "GRI 101: Biodiversity 2024" on 2026-01-01 (no longer in GRI's Portuguese list; this title is never displayed after that date — its disclosures always go to "a revisar") |
| GRI 305: Emissões 2016 | — |
| GRI 306: Resíduos 2020 | — |
| GRI 403: Saúde e Segurança do Trabalho 2018 | — |
| GRI 404: Capacitação e Educação 2016 | — |
| GRI 405: Diversidade e Igualdade de Oportunidades 2016 | — |
| GRI 413: Comunidades Locais 2016 | — |

| Disclosure | Title |
|---|---|
| 2-5 | Verificação externa |
| 2-6 | Atividades, cadeia de valor e outras relações de negócios |
| 2-12 | Papel desempenhado pelo mais alto órgão de governança na supervisão da gestão dos impactos |
| 2-25 | Processos para reparar impactos negativos |
| 2-26 | Mecanismos para aconselhamento e apresentação de preocupações |
| 2-27 | Conformidade com leis e regulamentos |
| 2-29 | Abordagem para engajamento de stakeholders |
| 201-1 | Valor econômico direto gerado e distribuído |
| 203-1 | Investimentos em infraestrutura e apoio a serviços |
| 203-2 | Impactos econômicos indiretos significativos |
| 204-1 | Proporção de gastos com fornecedores locais |
| 205-2 | Comunicação e capacitação em políticas e procedimentos de combate à corrupção |
| 205-3 | Casos confirmados de corrupção e medidas tomadas |
| 302-1 | Consumo de energia dentro da organização |
| 302-3 | Intensidade energética |
| 303-3 | Captação de água |
| 303-5 | Consumo de água |
| 304-3 | Habitats protegidos ou restaurados |
| 305-1 | Emissões diretas (Escopo 1) de gases de efeito estufa (GEE) |
| 305-4 | Intensidade de emissões de gases de efeito estufa (GEE) |
| 305-5 | Redução de emissões de gases de efeito estufa (GEE) |
| 306-2 | Gestão de impactos significativos relacionados a resíduos |
| 306-3 | Resíduos gerados |
| 306-4 | Resíduos não destinados para disposição final |
| 306-5 | Resíduos destinados para disposição final |
| 403-5 | Capacitação de trabalhadores em saúde e segurança do trabalho |
| 403-9 | Acidentes de trabalho |
| 404-1 | Média de horas de capacitação por ano, por empregado |
| 404-2 | Programas para o aperfeiçoamento de competências dos empregados e de assistência para transição de carreira |
| 405-1 | Diversidade em órgãos de governança e empregados |
| 413-1 | Operações com engajamento, avaliações de impacto e programas de desenvolvimento voltados à comunidade local |

Motives for "Referências a revisar" (exact text):
- `GRI-G4 …` → `Divulgação do modelo GRI-G4, anterior às Normas GRI`
- `GRI 14 (Mineração)` (a standard with no disclosure number) → `Norma setorial sem divulgação específica`
- superseded on the export date → `Norma substituída por GRI 101: Biodiversity 2024 em 01/01/2026` (the standard's replacement and date)
- anything else not in the table → `Divulgação não reconhecida`

## Review Focus

- **Export on or after 2027-01-01.** 302-1 and 302-3 must leave the index for "a revisar" without a code change (Task 20 test with `hoje=date(2027, 1, 1)`).
- **A reference with stray spaces or another case** ("gri  403-9 ") must still find its name (Task 20 test).
- **Filters that leave zero projects.** The file is still produced, values read "R$ 0"/"0"/"—", the context line lists the filters (Task 20 test).
- **A future spreadsheet with an unknown reference** ("GRI 999-9") goes to "a revisar", not to an error (Task 20 test).
- **The `/exportar-gri` route registered after `/{pagina}`** would be swallowed by the page route and return 404 (Task 20 API test).

---

### Task 20: Montar e exportar o índice GRI

**Files:**
- Create: `backend/app/gri.py`
- Modify: `backend/app/paginas/indicadores.py` (extract the current-value computation), `backend/app/exportacao.py` (report-layout writer; make the Contexto writer reusable with a title), `backend/app/api/painel.py` (route)
- Test: `backend/tests/test_gri.py`

**Interfaces:**
- Produces, in `app/paginas/indicadores.py`: `valores_atuais(base: Base) -> dict[str, str]` — ID Indicador → the catalog's "Valor atual" text. `montar` uses it (no second copy of the try/except).
- Produces, in `app/gri.py`:
  - `normalizar_referencia(texto: str) -> str` — trims, collapses inner spaces, upper-cases the `GRI` prefix (`" gri  403-9 "` → `"GRI 403-9"`)
  - `@dataclass LinhaGri(indicador: str, valor: str)` — `indicador` is `"<ID> <Indicador>"`
  - `@dataclass DivulgacaoGri(titulo: str, linhas: list[LinhaGri])` — `titulo` is `"403-9 Acidentes de trabalho"`
  - `@dataclass NormaGri(titulo: str, divulgacoes: list[DivulgacaoGri])`
  - `@dataclass RevisarGri(referencia: str, motivo: str, indicador: str, valor: str)`
  - `@dataclass IndiceGri(normas: list[NormaGri], revisar: list[RevisarGri])`
  - `montar_indice_gri(base: Base, hoje: date) -> IndiceGri` — base already filtered; rows whose reference is `-` or empty are skipped; order by standard number, then disclosure number, then ID Indicador; `revisar` in ID Indicador order.
- Produces, in `app/exportacao.py`: `indice_gri_para_xlsx(indice: IndiceGri, filtros: Filtros, versao: Versao) -> bytes`. Sheets, in order: "Índice GRI", "Contexto".
  - "Índice GRI": A1 = the title (bold); A2 = `Versão nº <n> · <nome_arquivo> · filtros: <resumo>` where `<resumo>` is `carteira inteira` without filters, else the chosen fields as `Setor: Mineração · Município: Teresina` (field labels as in the Contexto sheet); row 4 = header Norma GRI · Divulgação · Indicador · Valor · Localização no relatório; then the rows, the standard only on its first row and the disclosure only on its first row; then an empty row, a bold "Referências a revisar", a header Referência · Motivo · Indicador · Valor and its rows. Localização stays empty. Freeze below row 4; widths fitted (cap 60).
  - "Contexto": the same rows as the dashboard export, with Página = "Índice de conteúdo GRI".
- Produces: `GET /api/painel/exportar-gri?<filters>` → the file, `Content-Disposition: attachment; filename="ASG_indice_gri_<AAAA-MM-DD>.xlsx"` (date in America/Fortaleza). Register it before `@router.get("/{pagina}")`.

- [ ] **Step 1: Write the failing tests** (`tests/test_gri.py`; the API tests reuse the `com_versao` fixture pattern of `test_exportacao.py`). Imports: `date`, `datetime` from `datetime`; `BytesIO`; `load_workbook`; `FUSO` from `app.paginas.comum`; `Filtros`, `aplicar_filtros` from `app.calculos.filtros`; `montar_indice_gri`, `normalizar_referencia` from `app.gri`; `base_modelo` from `tests.apoio`.

```python
HOJE = date(2026, 11, 18)

def todas_linhas(ind):
    return [(n.titulo, d.titulo, l.indicador, l.valor) for n in ind.normas for d in n.divulgacoes for l in d.linhas]

def test_normalizar_referencia():
    assert normalizar_referencia(" gri  403-9 ") == "GRI 403-9"

def test_indice_na_base_atual():
    ind = montar_indice_gri(base_modelo(), HOJE)
    linhas = todas_linhas(ind)
    assert len(linhas) == 65 and sum(len(n.divulgacoes) for n in ind.normas) == 30
    assert linhas[0] == ("GRI 2: Conteúdos Gerais 2021", "2-5 Verificação externa", "IND69 Número de auditorias realizadas", linhas[0][3])
    n403 = next(n for n in ind.normas if n.titulo == "GRI 403: Saúde e Segurança do Trabalho 2018")
    assert [d.titulo for d in n403.divulgacoes] == ["403-5 Capacitação de trabalhadores em saúde e segurança do trabalho", "403-9 Acidentes de trabalho"]
    assert [(l.indicador, l.valor) for l in n403.divulgacoes[1].linhas] == [
        ("IND54 Número de acidentes de trabalho", "23"), ("IND55 Taxa de frequência de acidentes", "2,12")]

def test_referencias_a_revisar():
    rev = {r.indicador.split()[0]: r for r in montar_indice_gri(base_modelo(), HOJE).revisar}
    assert list(rev) == ["IND03", "IND04", "IND13", "IND14", "IND17", "IND32", "IND33", "IND34"]
    assert rev["IND03"].motivo == "Divulgação do modelo GRI-G4, anterior às Normas GRI" and rev["IND03"].valor == "1.905"
    assert rev["IND13"].motivo == "Norma setorial sem divulgação específica"
    assert rev["IND17"].motivo == "Norma substituída por GRI 101: Biodiversity 2024 em 01/01/2026"

def test_302_sai_do_indice_em_2027():
    ind = montar_indice_gri(base_modelo(), date(2027, 1, 1))
    assert len(todas_linhas(ind)) == 62
    rev = {r.indicador.split()[0]: r.motivo for r in ind.revisar}
    assert rev["IND06"] == rev["IND10"] == rev["IND11"] == "Norma substituída por GRI 103: Energy 2025 em 01/01/2027"

def test_referencia_desconhecida_e_espacos():
    b = base_modelo()
    b["dIndicador"].loc[0, "Referência GRI"] = "GRI 999-9"      # IND01
    b["dIndicador"].loc[1, "Referência GRI"] = " gri  403-9 "   # IND02
    ind = montar_indice_gri(b, HOJE)
    assert {r.indicador.split()[0]: r.motivo for r in ind.revisar}["IND01"] == "Divulgação não reconhecida"
    assert any(l[2].startswith("IND02") and l[1] == "403-9 Acidentes de trabalho" for l in todas_linhas(ind))

def test_valores_respeitam_o_filtro():
    b = aplicar_filtros(base_modelo(), Filtros(setores=["Mineração"]))
    ind = montar_indice_gri(b, HOJE)
    assert next(l for l in todas_linhas(ind) if l[2].startswith("IND01"))[3] == "R$ 0"

def test_exportar_gri(cliente, com_versao, h_leitor):
    r = cliente.get("/api/painel/exportar-gri?setor=Mineração", headers=h_leitor)
    assert r.status_code == 200
    hoje = datetime.now(FUSO).date().isoformat()
    assert f'filename="ASG_indice_gri_{hoje}.xlsx"' in r.headers["content-disposition"]
    wb = load_workbook(BytesIO(r.content))
    assert wb.sheetnames == ["Índice GRI", "Contexto"]
    ws = wb["Índice GRI"]
    assert ws["A1"].value == "Índice de conteúdo GRI — indicadores quantitativos"
    assert ws["A2"].value.startswith("Versão nº 1 · base.xlsx · filtros: Setor: Mineração")
    assert [c.value for c in ws[4]] == ["Norma GRI", "Divulgação", "Indicador", "Valor", "Localização no relatório"]
    textos = [str(c.value) for row in ws.iter_rows() for c in row if c.value]
    assert "Referências a revisar" in textos
    assert not any("de acordo com" in t.lower() for t in textos)

def test_exportar_gri_sem_filtro_e_sem_login(cliente, com_versao, h_leitor):
    wb = load_workbook(BytesIO(cliente.get("/api/painel/exportar-gri", headers=h_leitor).content))
    assert wb["Índice GRI"]["A2"].value.endswith("filtros: carteira inteira")
    assert cliente.get("/api/painel/exportar-gri").status_code == 401
```

- [ ] **Step 2: Run** `.venv\Scripts\python -m pytest tests/test_gri.py -v`. Expected: FAIL (ImportError on `app.gri`).
- [ ] **Step 3: Implement** `valores_atuais`, `app/gri.py` with the tables above, `indice_gri_para_xlsx` and the route.
- [ ] **Step 4: Run** the Step 2 command, then the full suite. Expected: all PASS (catalog tests unchanged).
- [ ] **Step 5: Commit** — `git commit -m "feat: build and export the GRI content index"`

---

### Task 21: Botão "Exportar índice GRI" na página Indicadores

**Files:**
- Modify: `frontend/src/menu.ts`, `frontend/src/App.tsx`, `frontend/src/components/PaginaPainel.tsx`

**Interfaces:**
- Consumes: `GET /api/painel/exportar-gri` (Task 20); `api.baixar(caminho, nome, params)`; `nomeExportacao(caminho)` in `format.ts` (`nomeExportacao('indice_gri')` → `ASG_indice_gri_<data>.xlsx`, already tested).
- Produces: `ItemMenu.exportacaoExtra?: { rotulo: string; endpoint: string; nome: string }`; the Indicadores item gets `{ rotulo: 'Exportar índice GRI', endpoint: '/api/painel/exportar-gri', nome: 'indice_gri' }`. `PaginaPainel` takes an optional `exportacaoExtra` prop (App passes the item's) and renders a second `botao secundario` next to "Exportar Excel", with the same "Gerando…" / disabled / error behavior and the current filters.

- [ ] **Step 1:** Implement the prop, the menu field and the button. Only the Indicadores page shows it.
- [ ] **Step 2: Run** `npx vitest run` and `npm run build` in `frontend/`. Expected: 10 passed, no TS errors.
- [ ] **Step 3: Check through the API** with a temporary uvicorn on port 8001 (demo leitor from the README), not on 8000/5173: `GET /api/painel/exportar-gri` returns the file. State in the report that the button itself was not clicked in a browser.
- [ ] **Step 4: Commit** — `git commit -m "feat: GRI index export button on the Indicadores page"`

---

## Final check (after Task 21)

- Full suite green: `.venv\Scripts\python -m pytest -q`, plus `npx vitest run` and `npm run build` in `frontend/`.
- Visão Geral still shows 68; the catalog's "Valor atual" column is unchanged.
