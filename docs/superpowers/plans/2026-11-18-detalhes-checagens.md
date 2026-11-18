# Detalhes das checagens (C01–C12) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Each check C01–C12 with problems lists the failing records (aba, spreadsheet row, identifier, offending values) in the upload preview and on the Qualidade dos dados page, and the Qualidade export gets a "Problemas" sheet with all of them.

**Architecture:** The spreadsheet row number is captured at read time in an internal column and stored with the version. `rodar_checagens` builds one `Ocorrencia` per failing record from the same masks that count today, so the count is the length of the list. Pages and the preview cut the list at 50.

**Tech Stack:** FastAPI, pandas, openpyxl, pytest; React + Vite + TS, vitest. No new dependency.

**Spec:** `docs/superpowers/specs/2026-11-18-detalhes-checagens-design.md`

## Global Constraints

- `problemas` of every check must equal the length of its full occurrence list, and must not change for any input compared with today.
- On screen (upload preview and Qualidade): at most **50** occurrences per check (`LIMITE_OCORRENCIAS = 50`), plus `mais` = how many were left out. The Excel "Problemas" sheet has all of them.
- `versao.avisos` (Histórico de versões) stays count-only: no occurrences are stored there.
- Versions saved before this feature have no row number: `linha` is `None`, and everything else works.
- The internal row column never shows up as a page column and is never reported by `validar_estrutura`.
- No change to measures, metas or weights: the Índice ASG Geral stays 68. The whole existing suite stays green.
- pt-BR copy; money and percentages through `texto_valor` (`app/paginas/comum.py`), dates as `dd/mm/aaaa`.
- Frontend tests: `npx vitest run` (there is no `npm test`).

## Review Focus

- **Blank rows in the middle of an aba.** `ler_planilha` drops them; the row shown must still match the Excel row (Task 17 test).
- **A version saved before this feature.** Its stored rows have no row number: `linha` is `None`, the Qualidade page still loads (Task 17 test).
- **More than 50 problems in one check.** Screen shows 50 and "e mais N"; the Excel sheet has all (Tasks 18 and 19 tests).
- **C02 duplicates.** The count is "extra occurrences" (`len - nunique`); the list must have the same size, so it lists the repetitions and points to the first one (Task 18 test).
- **Histórico de versões.** Confirming an upload with problems must keep `avisos` count-only (Task 18 test).

---

### Task 17: Número da linha da planilha

**Files:**
- Modify: `backend/app/planilha/leitura.py` (`ler_planilha`), `backend/app/repositorio.py` (`salvar_versao`, `_carregar`)
- Test: `backend/tests/test_planilha.py`, `backend/tests/test_repositorio.py`

**Interfaces:**
- Produces: `COLUNA_LINHA = "_linha_planilha"` in `app/planilha/leitura.py`. Every DataFrame returned by `ler_planilha` has it: the Excel row of that record (`int`, header is row 1, so first data row is 2), computed **after** `dropna(how="all")` from the preserved index and before any `reset_index`. `aplicar_tipos` keeps it untouched. `salvar_versao` stores it in `LinhaDado.dados`; `_carregar` restores it, as `None` for rows saved without it.

- [ ] **Step 1: Write the failing tests**

```python
# test_planilha.py
from app.planilha.leitura import COLUNA_LINHA, aplicar_tipos, ler_planilha
from tests.apoio import bytes_modelo, mutar

def test_linha_da_planilha_sem_lacunas():
    b = aplicar_tipos(ler_planilha(bytes_modelo()))
    assert list(b["dProjeto"][COLUNA_LINHA][:3]) == [2, 3, 4]

def test_linha_da_planilha_pula_linhas_em_branco():
    conteudo = mutar(lambda wb: wb["dProjeto"].insert_rows(3))   # linha 3 do Excel fica vazia
    b = aplicar_tipos(ler_planilha(conteudo))
    p = b["dProjeto"]
    assert p.loc[p["Código Projeto"] == "PROJ002", COLUNA_LINHA].item() == 4
    assert validar_estrutura(ler_planilha(conteudo)) == []

# test_repositorio.py
def test_versao_guarda_a_linha(sessao_teste, usuarios):
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, base_modelo(), usuarios["admin"].id, "b.xlsx", [])
    b = repositorio.carregar_base_ativa(sessao_teste)
    assert b["fContratos"][COLUNA_LINHA].iloc[0] == 2

def test_versao_antiga_sem_linha(sessao_teste, usuarios):
    repositorio.limpar_cache()
    v = repositorio.salvar_versao(sessao_teste, base_modelo(), usuarios["admin"].id, "b.xlsx", [])
    sessao_teste.execute(text("update linha_dado set dados = dados - '_linha_planilha' where versao_id = :v"), {"v": v.id})
    sessao_teste.commit()
    repositorio.limpar_cache()
    b = repositorio.carregar_base_ativa(sessao_teste)
    assert b["dProjeto"][COLUNA_LINHA].isna().all()
    assert len(b["dProjeto"]) == 48
```

(Imports: `validar_estrutura` from `app.planilha.validacao`, `text` from `sqlalchemy`, `repositorio` and `base_modelo` as the files already do.)

- [ ] **Step 2: Run** `.venv\Scripts\python -m pytest tests/test_planilha.py tests/test_repositorio.py -k linha -v`. Expected: FAIL (ImportError on `COLUNA_LINHA`).
- [ ] **Step 3: Implement** `COLUNA_LINHA` in `ler_planilha`, its storage in `salvar_versao` (as a plain `int`, JSON-safe) and its restore in `_carregar` (columns = the aba's `ABAS` columns plus `COLUNA_LINHA`).
- [ ] **Step 4: Run** the Step 2 command, then the full suite `.venv\Scripts\python -m pytest -q`. Expected: all PASS. If an existing test asserts the exact column list of a read aba, it now must account for `COLUNA_LINHA`; record that as a ruling.
- [ ] **Step 5: Commit** — `git commit -m "feat: keep the spreadsheet row of every record"`

---

### Task 18: Ocorrências nas checagens e na prévia do envio

**Files:**
- Modify: `backend/app/calculos/checagens.py`, `backend/app/api/importacao.py` (`previa`)
- Test: `backend/tests/test_checagens.py`, `backend/tests/test_api.py` (or the file that already tests `/api/importacao`)

**Interfaces:**
- Consumes: `COLUNA_LINHA` (Task 17), `texto_valor(v, formato)` from `app/paginas/comum.py`
- Produces, in `app/calculos/checagens.py`:
  - `LIMITE_OCORRENCIAS = 50`
  - `@dataclass Ocorrencia(aba: str, linha: int | None, identificador: str, detalhe: str)`
  - `ResultadoChecagem.ocorrencias: list[Ocorrencia]` (full list); `problemas == len(ocorrencias)`
  - `ResultadoChecagem.dict()` unchanged (count only — it feeds `versao.avisos`)
  - `ResultadoChecagem.com_ocorrencias(limite: int | None = LIMITE_OCORRENCIAS) -> dict`: `dict()` plus `"ocorrencias"` (the first `limite`, as dicts; all when `None`) and `"mais"` (`problemas - len(shown)`)
  - `POST /api/importacao/previa` returns each check through `com_ocorrencias()`

**Occurrence per check** (aba · identificador · detalhe; `linha` is the record's `COLUNA_LINHA`):

| Check | aba | identificador | detalhe |
|---|---|---|---|
| C01 | dProjeto | Código Projeto | `Código Empresa EMP999 não existe em dEmpresa` |
| C02 | dProjeto | Código Projeto | `Código repetido; primeira ocorrência na linha 2` (`Código repetido` when the first has no row). Only the repetitions are listed, the first occurrence is not, so the size equals today's count. |
| C03–C06 | dProjeto | Código Projeto | `<Nome Projeto> sem linha em fAmbiental` (the check's aba) |
| C07 | dProjeto | Código Projeto | `Investimento Realizado R$ 7,8 bi > Investimento Previsto R$ 780 mi` |
| C08 | fSocial | Código Projeto | each subgroup above the total, joined by `; `: `Empregos Mulheres 600 > Empregos Diretos Gerados 520` |
| C09 | fFinanceiro | ID Execução | `01/01/2026: Empenhado R$ 31,7 mi · Liquidado R$ 29,1 mi · Pago R$ 63,4 mi` |
| C10 | dProjeto | Código Projeto | `Vazios: Município, Custo Manutenção Anual` (in the rule's column order) |
| C11 | fHidrogenio | Código Projeto | `% Renovável Eletrolisador 120,0%` |
| C12 | fContratos | ID Processo | `Data Início 12/01/2026 > Data Fim 01/12/2025` |

Restructure `rodar_checagens` so each check yields its failing rows once; the count comes from that list, never from a second computation.

- [ ] **Step 1: Write the failing tests** (in `test_checagens.py`, reusing its `base_modelo` mutations)

```python
def ocorrencias(base, cid):
    return next(r for r in rodar_checagens(base) if r.id == cid).ocorrencias

def test_c07_ocorrencia():
    b = base_modelo()
    b["dProjeto"].loc[0, "Investimento Realizado"] = 10 * b["dProjeto"].loc[0, "Investimento Previsto"]
    [o] = ocorrencias(b, "C07")
    assert (o.aba, o.linha, o.identificador) == ("dProjeto", 2, "PROJ001")
    assert o.detalhe == "Investimento Realizado R$ 7,8 bi > Investimento Previsto R$ 780 mi"

def test_c12_ocorrencia():
    b = base_modelo()
    b["fContratos"].loc[0, "Data Fim"] = pd.Timestamp("2025-12-01")
    [o] = ocorrencias(b, "C12")
    assert (o.aba, o.identificador) == ("fContratos", "LIC001")
    assert o.detalhe == "Data Início 12/01/2026 > Data Fim 01/12/2025"

def test_c02_lista_so_as_repeticoes():
    b = base_modelo()
    b["dProjeto"] = pd.concat([b["dProjeto"], b["dProjeto"].iloc[[0]]], ignore_index=True)
    [o] = ocorrencias(b, "C02")
    assert o.identificador == "PROJ001" and o.detalhe == "Código repetido; primeira ocorrência na linha 2"

def test_c10_lista_os_campos_vazios():
    b = base_modelo()
    b["dProjeto"].loc[0, ["Município", "Custo Manutenção Anual"]] = None
    [o] = ocorrencias(b, "C10")
    assert o.detalhe == "Vazios: Município, Custo Manutenção Anual"

# MUTACOES: lift the 12 mutations already used by test_c01 … test_c12 of this file into a
# module-level list of functions (one per check, base -> None), and reuse them there.
@pytest.mark.parametrize("mutacao", MUTACOES)
def test_contagem_igual_a_lista(mutacao):
    b = base_modelo(); mutacao(b)
    assert all(r.problemas == len(r.ocorrencias) for r in rodar_checagens(b))

def test_com_ocorrencias_corta_em_50():
    b = base_modelo()
    b["fFinanceiro"]["Valor Pago"] = 2 * b["fFinanceiro"]["Valor Empenhado"]
    c09 = next(r for r in rodar_checagens(b) if r.id == "C09").com_ocorrencias()
    assert c09["problemas"] == 432 and len(c09["ocorrencias"]) == 50 and c09["mais"] == 382
    assert "ocorrencias" not in next(r for r in rodar_checagens(b) if r.id == "C09").dict()
```

API tests (with the admin client, as the existing `/api/importacao` tests do):
- `test_previa_traz_ocorrencias`: upload `mutar(...)` with C07 broken → the C07 entry has one occurrence with `linha == 2` and `mais == 0`.
- `test_confirmar_guarda_so_contagens`: confirm the same file → `versao.avisos` entries have no `"ocorrencias"` key.

- [ ] **Step 2: Run** `.venv\Scripts\python -m pytest tests/test_checagens.py tests/test_api.py -k "ocorrencia or repeticoes or vazios or contagem or corta or previa_traz or so_contagens" -v`. Expected: FAIL.
- [ ] **Step 3: Implement** `Ocorrencia`, the restructured `rodar_checagens`, `com_ocorrencias` and the `previa` change.
- [ ] **Step 4: Run** the Step 2 command, then the full suite. Expected: all PASS, including every existing count test in `test_checagens.py` unchanged.
- [ ] **Step 5: Commit** — `git commit -m "feat: list the records behind each data check"`

---

### Task 19: Listas na Qualidade, na tela de envio e no Excel

**Files:**
- Modify: `backend/app/paginas/qualidade.py`, `backend/app/paginas/tipos.py`, `backend/app/api/painel.py` (export case of `"qualidade"`)
- Modify: `frontend/src/api.ts`, `frontend/src/format.ts`, `frontend/src/components/Tabela.tsx`, `frontend/src/pages/Envio.tsx`, `frontend/src/estilo.css`
- Create: `frontend/src/components/ListaOcorrencias.tsx`
- Test: `backend/tests/test_paginas_qualidade.py`, `frontend/src/format.test.ts`

**Interfaces:**
- Consumes: `ResultadoChecagem.com_ocorrencias`, `Ocorrencia` (Task 18)
- Produces:
  - `Tabela.expansivel: bool = False` (backend) / `expansivel?: boolean` (TS). In an expandable table a row may carry `ocorrencias: Ocorrencia[]` and `mais: number`; they are not columns.
  - `qualidade.montar(base, versao, completo: bool = False) -> Pagina`. The `checagens` table is `expansivel=True` and each row carries `ocorrencias` (≤ 50) and `mais`. With `completo=True` (used only by the export route) a third table is added: id `problemas`, title "Problemas", columns Checagem · Aba · Linha (`num`) · Identificador · Detalhe, one row per occurrence, no limit.
  - TS: `interface Ocorrencia { aba: string; linha: number | null; identificador: string; detalhe: string }`; `Checagem` gains `ocorrencias?: Ocorrencia[]` and `mais?: number`.
  - `textoOcorrencia(o: Ocorrencia): string` in `format.ts`: `"dProjeto · linha 2 · PROJ001"`, or `"dProjeto · PROJ001"` when `linha` is null.
  - `<ListaOcorrencias ocorrencias mais />`: one line per occurrence, `textoOcorrencia` in bold then `detalhe`; a last line "e mais N" when `mais > 0`.

**Screen:** in both Tabela (expandable rows) and Envio (check rows), a check with occurrences shows a toggle button (`aria-expanded`, ▸ closed / ▾ open) and starts **closed**; open, the next row spans all columns with `<ListaOcorrencias>`. Checks with 0 problems show no toggle.

- [ ] **Step 1: Write the failing tests**

```python
# test_paginas_qualidade.py
def test_qualidade_mostra_ocorrencias(cliente, sessao_teste, usuarios, h_leitor):
    b = base_modelo()
    b["fFinanceiro"]["Valor Pago"] = 2 * b["fFinanceiro"]["Valor Empenhado"]   # C09 em todas as 432 linhas
    repositorio.limpar_cache()
    repositorio.salvar_versao(sessao_teste, b, usuarios["admin"].id, "x.xlsx", [])
    t = cliente.get("/api/painel/qualidade", headers=h_leitor).json()["tabelas"][0]
    assert t["expansivel"] is True
    c09 = next(l for l in t["linhas"] if l["id"] == "C09")
    assert len(c09["ocorrencias"]) == 50 and c09["mais"] == 382
    assert c09["ocorrencias"][0]["identificador"] == "FIN001-01"
    r = cliente.get("/api/painel/exportar/qualidade", headers=h_leitor)
    wb = load_workbook(BytesIO(r.content))
    assert "Problemas" in wb.sheetnames and wb["Problemas"].max_row == 1 + 432
    repositorio.limpar_cache()
```

```ts
// format.test.ts
describe('textoOcorrencia', () => {
  it('mostra aba, linha e identificador', () => {
    expect(textoOcorrencia({ aba: 'dProjeto', linha: 2, identificador: 'PROJ001', detalhe: '' })).toBe('dProjeto · linha 2 · PROJ001')
    expect(textoOcorrencia({ aba: 'fContratos', linha: null, identificador: 'LIC001', detalhe: '' })).toBe('fContratos · LIC001')
  })
})
```

- [ ] **Step 2: Run** `.venv\Scripts\python -m pytest tests/test_paginas_qualidade.py -v` and `npx vitest run` in `frontend/`. Expected: both FAIL.
- [ ] **Step 3: Implement** the backend (`expansivel`, `montar(..., completo)`, the export route passing `completo=True`), then the frontend (types, `textoOcorrencia`, `ListaOcorrencias`, toggles in `Tabela.tsx` and `Envio.tsx`).
- [ ] **Step 4: Run** the Step 2 commands, the full backend suite, and `npm run build`. Expected: all PASS, no TS errors.
- [ ] **Step 5: Check in the browser.**
  1. As admin, upload a copy of the model spreadsheet with one project's Investimento Realizado set above the Previsto. The preview shows C07 "Verificar: 1"; opening it shows `dProjeto · linha N · PROJ…` and the two values. Cancel without confirming.
  2. As leitor, on Qualidade dos dados all checks are "OK" and show no toggle.
- [ ] **Step 6: Commit** — `git commit -m "feat: show the failing records in Qualidade and the upload preview"`

---

## Final check (after Task 19)

- Full suite green: `.venv\Scripts\python -m pytest -q`, plus `npx vitest run` and `npm run build` in `frontend/`.
- Visão Geral still shows 68; the Histórico de versões looks as before.
