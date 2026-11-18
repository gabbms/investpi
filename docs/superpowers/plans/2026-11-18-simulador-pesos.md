# Simulador de pesos — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A "Simulador de pesos" page where anyone edits the 24 goal weights and sees official × simulated ASG indices live, and the admin saves the weights as a new data version.

**Architecture:** `avaliar_metas` gets an optional weight override; a POST endpoint returns official and simulated indices for the current filters; an admin POST copies the active base, rewrites `dMetas.Peso` and saves it with the existing `salvar_versao`. The frontend page is a dedicated component (not the generic dashboard page).

**Tech Stack:** FastAPI, SQLAlchemy, pandas, pytest; React + Vite, Vitest.

**Spec:** `docs/superpowers/specs/2026-11-18-simulador-pesos-design.md`

## Global Constraints

- Weight: integer 0–5; 0 removes the goal; every pillar keeps ≥ 1 goal with weight > 0, else HTTP 400 with a pt-BR message.
- Without changes the simulator returns exactly the official values: Geral 68.15, Ambiental 75.4, Social 66.8, Governança 62.2 (reference base).
- No official screen ever shows simulated numbers; the page shows the banner "Simulação — não altera os números oficiais".
- Saving is admin-only (403 for leitor); the saved version's `nome_arquivo` is `pesos ajustados (a partir da versão N)`; all other sheets identical to the active version.
- Index method unchanged (weighted mean × 100; geral = sum of 3 pillars ÷ 3).
- Menu entry "Simulador de pesos" right after "Qualidade dos dados", for every user.

## Review Focus

1. Unknown goal IDs or non-integer / out-of-range weights in the request → 400, not a 500 — Task 27 test `test_pesos_invalidos_400`.
2. Simulation with filters that leave a pillar without data must not crash (pillar index None) — Task 27 test `test_simular_com_filtro_sem_projetos`.
3. Saving while the active version changed meanwhile must still copy the *current* active base — Task 27 implementation reads the active base inside the save request; test `test_salvar_cria_versao_com_pesos`.
4. Fast typing must not show results out of order (older response arriving last) — Task 28 Step 3 (ignore stale responses).
5. Leitor must not see the save button and the server must refuse anyway — Task 27 `test_leitor_nao_salva` + Task 28 browser check.

---

### Task 27: Backend — weight override, simulate and save

**Files:**
- Modify: `backend/app/calculos/metas.py`, `backend/app/api/painel.py`, `backend/app/api/versoes.py`
- Create: `backend/app/pesos.py` (validation + simulation result builder)
- Test: `backend/tests/test_pesos.py`

**Interfaces:**
- `avaliar_metas(base: Base, pesos: dict[str, int] | None = None) -> list[ResultadoMeta]` — `pesos[id_meta]` replaces the sheet's `Peso`.
- `validar_pesos(base: Base, pesos: dict[str, int]) -> None` in `app/pesos.py` — raises `ValueError(msg)` for unknown ID, weight not int in 0..5, or a pillar left with all weights 0.
- `simular(base: Base, pesos: dict[str, int]) -> dict` — `{"oficial": {"geral", "Ambiental", "Social", "Governança"}, "simulado": {...same keys...}, "metas": [{"id_meta", "pilar", "indicador", "atingimento", "status", "peso_oficial", "peso"}]}`; index values are floats or `None`.
- `POST /api/painel/simular-pesos` (any logged user; filters as the usual query params) body `{"pesos": {id: int}}` → `simular(...)`; `ValueError` → 400.
- `POST /api/versoes/pesos` (admin) body `{"pesos": {id: int}}` → 201 `VersaoOut` of the new active version.

- [ ] **Step 1: Write the failing tests** (`com_versao`/`usuarios` fixtures as in `test_exportacao.py`)

```python
def test_sem_mudanca_igual_ao_oficial(...):   # POST {} → simulado == oficial; geral≈68.15, Ambiental≈75.4, Social≈66.8, Governança≈62.2 (abs 0.05)
def test_peso_da_fraude_muda_governanca(...): # {"META24": 5} → simulado Governança≈57.39, geral≈66.56; oficial unchanged
def test_peso_zero_tira_a_meta(...):          # {"META24": 0} → Governança simulado > oficial
def test_pesos_invalidos_400(...):            # {"META99": 2}, {"META24": 6}, {"META24": -1}, {"META24": 2.5} → 400 each
def test_pilar_sem_peso_400(...):             # all Governança IDs → 0 → 400 mentioning "Governança"
def test_simular_com_filtro_sem_projetos(...):# ?municipio=Inexistente → 200
def test_leitor_nao_salva(...):               # leitor POST /api/versoes/pesos → 403
def test_salvar_cria_versao_com_pesos(...):   # admin {"META24": 5} → 201, numero == old+1, ativa, nome "pesos ajustados (a partir da versão 1)";
                                              # loaded active base: dMetas Peso of META24 == 5, others unchanged; linhas_por_aba equal to v1
```

- [ ] **Step 2: Run** `.venv\Scripts\python -m pytest tests/test_pesos.py -v`. Expected: FAIL (404/ImportError).
- [ ] **Step 3: Implement** the interfaces above. Save copies `carregar_base_ativa`, sets `Peso` per ID on a copy of `dMetas`, calls `salvar_versao(s, base, admin.id, nome, avisos)` with the same `avisos` rule as `confirmar`.
- [ ] **Step 4: Run** the Step 2 command, then the full suite. Expected: all PASS.
- [ ] **Step 5: Commit** — `feat: simulate goal weights and save them as a new version`

---

### Task 28: Frontend — Simulador de pesos page

**Files:**
- Create: `frontend/src/pages/Simulador.tsx`, `frontend/src/simulador.ts`, `frontend/src/simulador.test.ts`
- Modify: `frontend/src/menu.ts`, `frontend/src/App.tsx`, `frontend/src/api.ts` (types), `frontend/src/estilo.css`

**Interfaces:**
- Consumes: the two endpoints of Task 27.
- `simulador.ts`: `pesoValido(texto: string): number | null` (integer 0–5 else null); `alterados(oficial: Record<string, number>, atual: Record<string, number>): Record<string, number>` (only changed IDs — the request body).

- [ ] **Step 1: Write the failing tests**

```ts
pesoValido('3') === 3; pesoValido('0') === 0; pesoValido('6') === null; pesoValido('2.5') === null; pesoValido('') === null
alterados({A: 3, B: 2}, {A: 5, B: 2}) deep-equals {A: 5}; alterados({A: 3}, {A: 3}) deep-equals {}
```

- [ ] **Step 2: Run** `npx vitest run`. Expected: FAIL.
- [ ] **Step 3: Implement.** Page per the spec: banner; top row of four comparisons "oficial → simulado" with each index's color (`cor_indice` bands: ≥75 verde, ≥50 amarelo, else vermelho) and "—" for None; one table per pillar (indicador, atingimento with status seal, peso oficial, `<input type=number min=0 max=5 step=1>`), changed rows highlighted; request debounced ~300 ms with a sequence number so stale responses are ignored; server 400 message shown above the tables; "Restaurar pesos oficiais"; admin-only "Salvar como nova versão" with `confirm()` text "Isso cria a versão nova e passa a valer para todos. Continuar?", then success message with the version number. Uses the top filters like the dashboard pages. Menu item per Global Constraints (`painel: true` so filters show; route `/simulador`).
- [ ] **Step 4: Run** `npx vitest run`, `npm run build`. Expected: PASS, no TS errors.
- [ ] **Step 5: Check in the browser** (Opera test profile, local dev, CDP script as before): as leitor — page shows 68/75/67/62 both sides, no save button; set META24 to 5 → Governança ≈57 and Geral ≈67 simulated, Visão Geral still 68; set every Governança weight to 0 → error message. As admin — save → Histórico shows the new version "pesos ajustados (a partir da versão 1)" active; then reactivate version 1 so the local data is as before. Light and dark screenshots.
- [ ] **Step 6: Commit** — `feat: Simulador de pesos page`

## Final check

- Full backend suite, `npx vitest run`, `npm run build` green.
- PR opened; Actions `backend` + `frontend` pass; user merges.
